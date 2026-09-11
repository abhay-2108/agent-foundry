-- ============================================================================
-- PostgreSQL + pgvector Production Schema Template
-- Multi-Tenant Partitioning, HNSW Indexing, and Hybrid Search
-- ============================================================================

-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Production Document Chunks Table
CREATE TABLE IF NOT EXISTS rag_document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(64) NOT NULL,
    document_id VARCHAR(128) NOT NULL,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    -- 1536 dimensions for text-embedding-3-small or similar
    embedding vector(1536) NOT NULL,
    tsv_content tsvector GENERATED ALWAYS AS (to_tsvector('english', chunk_text)) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Composite & Filtering Indexes
CREATE INDEX IF NOT EXISTS idx_chunks_tenant_doc 
ON rag_document_chunks (tenant_id, document_id);

CREATE INDEX IF NOT EXISTS idx_chunks_metadata_gin 
ON rag_document_chunks USING GIN (metadata);

CREATE INDEX IF NOT EXISTS idx_chunks_tsv 
ON rag_document_chunks USING GIN (tsv_content);

-- 4. Production HNSW Index for Cosine Similarity
-- M = 16 (good balance of memory and recall)
-- ef_construction = 128 (high build-time accuracy)
CREATE INDEX IF NOT EXISTS idx_chunks_hnsw_cosine 
ON rag_document_chunks 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 128);

-- 5. Hybrid Search Function (Dense Vector + BM25 Full-Text with Reciprocal Rank Fusion)
CREATE OR REPLACE FUNCTION match_documents_hybrid(
    query_text TEXT,
    query_embedding vector(1536),
    match_tenant_id VARCHAR(64),
    match_count INT DEFAULT 10,
    rrf_k INT DEFAULT 60
)
RETURNS TABLE (
    id UUID,
    document_id VARCHAR(128),
    chunk_text TEXT,
    metadata JSONB,
    dense_score FLOAT,
    fulltext_score FLOAT,
    combined_rrf_score FLOAT
)
LANGUAGE sql
STABLE
AS $$
WITH dense_search AS (
    SELECT 
        c.id,
        c.document_id,
        c.chunk_text,
        c.metadata,
        (1 - (c.embedding <=> query_embedding)) AS dense_score,
        ROW_NUMBER() OVER (ORDER BY c.embedding <=> query_embedding) AS dense_rank
    FROM rag_document_chunks c
    WHERE c.tenant_id = match_tenant_id
    ORDER BY c.embedding <=> query_embedding
    LIMIT match_count * 2
),
fulltext_search AS (
    SELECT 
        c.id,
        c.document_id,
        c.chunk_text,
        c.metadata,
        ts_rank(c.tsv_content, plainto_tsquery('english', query_text)) AS fulltext_score,
        ROW_NUMBER() OVER (ORDER BY ts_rank(c.tsv_content, plainto_tsquery('english', query_text)) DESC) AS ft_rank
    FROM rag_document_chunks c
    WHERE c.tenant_id = match_tenant_id 
      AND c.tsv_content @@ plainto_tsquery('english', query_text)
    ORDER BY fulltext_score DESC
    LIMIT match_count * 2
)
SELECT 
    COALESCE(d.id, f.id) AS id,
    COALESCE(d.document_id, f.document_id) AS document_id,
    COALESCE(d.chunk_text, f.chunk_text) AS chunk_text,
    COALESCE(d.metadata, f.metadata) AS metadata,
    COALESCE(d.dense_score, 0.0)::FLOAT AS dense_score,
    COALESCE(f.fulltext_score, 0.0)::FLOAT AS fulltext_score,
    (
        COALESCE(1.0 / (rrf_k + d.dense_rank), 0.0) +
        COALESCE(1.0 / (rrf_k + f.ft_rank), 0.0)
    )::FLOAT AS combined_rrf_score
FROM dense_search d
FULL OUTER JOIN fulltext_search f ON d.id = f.id
ORDER BY combined_rrf_score DESC
LIMIT match_count;
$$;
