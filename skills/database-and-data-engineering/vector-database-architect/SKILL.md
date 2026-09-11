---
name: vector-database-architect
description: >-
  Use this skill when designing, sizing, and optimizing vector databases and Approximate Nearest
  Neighbor (ANN) indexes at scale. Covers HNSW and IVFFlat parameter tuning, vector quantization
  (SQ8, PQ, BQ), multi-tenant namespace isolation, hybrid full-text + vector queries, and production
  schemas across pgvector, Qdrant, Pinecone, and Milvus.
---

# Vector Database Architect & ANN Index Optimization

Acts as a Lead Vector Database Architect & Retrieval Systems Engineer. Designs, tunes, and sizes production vector storage engines for semantic search, agentic RAG, and high-dimensional clustering. Masterfully balances the three-way trade-off between **Recall Accuracy**, **Query Latency (QPS)**, and **Memory (RAM) Footprint**.

---

## When to Use This Skill

- When selecting or tuning vector index algorithms (HNSW vs. IVFFlat vs. Flat).
- When configuring index build and search hyperparameters (`M`, `ef_construction`, `ef_search`, `lists`, `probes`).
- When applying vector compression / quantization (SQ8 scalar quantization, Product Quantization PQ, Binary Quantization BQ).
- When architecting multi-tenant vector storage (partitioning, namespaces, metadata pre-filtering vs. post-filtering).
- When deploying PostgreSQL `pgvector`, Qdrant, Milvus, or Pinecone in production.
- When calculating vector database RAM sizing, disk capacity, and hardware budgets.
- Trigger phrases: `"tune vector index"`, `"pgvector setup"`, `"hnsw index optimization"`, `"vector database sizing"`, `"vector search indexing"`, `"qdrant schema"`, `"vector quantization"`, `"multi-tenant vector search"`.

---

## The Vector Indexing Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                   High-Dimensional Vector Architecture                 │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. Vector Normalization & Sim  │ 2. Index Graph Mechanics (HNSW/IVF)   │
│ (Cosine, Inner Product, L2)    │ (M, ef_construction, ef_search)       │
├────────────────────────────────┼───────────────────────────────────────┤
│ 3. Quantization & Compression  │ 4. Single-Stage Filtered Search       │
│ (SQ8 75% RAM Cut, PQ 90% Cut)  │ (Preventing Post-Filter Recall Drops) │
├────────────────────────────────┴───────────────────────────────────────┤
│ 5. Multi-Tenant Schemas & Hybrid Retrieval (BM25 + Dense Re-ranking)   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Distance Metrics & Normalization

Choosing the correct distance metric directly affects query latency and hardware acceleration:

| Metric | Formula | Best Use Case | Performance Note |
| :--- | :--- | :--- | :--- |
| **Cosine Similarity** | $\frac{u \cdot v}{\|u\| \|v\|}$ | Text embeddings (OpenAI, Voyage, Cohere) | Slower than dot product due to dynamic norm calculation. |
| **Inner / Dot Product** | $u \cdot v$ | Unit-normalized vectors ($\|v\| = 1.0$) | **Fastest**. Use SIMD/AVX-512 vector instructions directly. |
| **Euclidean / L2** | $\sqrt{\sum (u_i - v_i)^2}$ | Computer vision, spatial embeddings | Natural distance; scale-sensitive. |

> [!TIP]
> **Performance Trick**: Always pre-normalize your embedding vectors to unit length ($\|v\|_2 = 1.0$) prior to insertion. This allows you to use **Inner Product** indexes instead of Cosine, achieving identical ranking order with up to 2.5x higher query throughput.

---

## Phase 2: HNSW vs. IVFFlat Index Tuning

### 1. HNSW (Hierarchical Navigable Small World)
HNSW builds a multi-layer graph of skip-lists and nearest neighbor links. It is the gold standard for low-latency, high-recall retrieval.

- **`M` (Connections per node)**: Typically 16 to 64.
  - Higher `M` ($M=32$–$64$): Increases recall on high-dimensional vectors ($D > 1024$), but increases RAM usage and index build time.
  - Lower `M` ($M=16$): Ideal for memory-constrained deployments.
- **`ef_construction` (Build search depth)**: Typically 64 to 256.
  - Controls build accuracy. Increasing `ef_construction` increases build time, but does NOT increase query RAM. Set to 128 for production.
- **`ef_search` (Query search depth)**: Typically 20 to 128 (configured per query).
  - Runtime lever: Increase `ef_search` to gain $>99\%$ recall; decrease to achieve sub-5ms latencies.

### 2. IVFFlat (Inverted File Flat)
Partitions vector space into Voronoi cells using k-means clustering.
- **`lists`**: Number of clusters. Rule of thumb: $\text{lists} = 4 \times \sqrt{N}$ (e.g., for 1M vectors, $\approx 4,000$ lists).
- **`probes`**: Number of centroids searched at query time. Rule of thumb: $\text{probes} \approx \sqrt{\text{lists}}$.

---

## Phase 3: Vector Compression & Quantization

High-dimensional vectors consume enormous amounts of memory. Quantization compresses vectors to fit millions of embeddings in RAM:

### 1. Scalar Quantization (SQ8: Float32 $\rightarrow$ Int8)
- Maps 32-bit floats linearly to 8-bit integers: $q = \text{round}\left(\frac{v - v_{\min}}{v_{\max} - v_{\min}} \times 255\right)$.
- **Compression**: **75% RAM reduction** (4 bytes $\rightarrow$ 1 byte per dimension).
- **Recall Impact**: Minimal ($<1.5\%$ recall loss for typical text embeddings).

### 2. Product Quantization (PQ)
- Decomposes a $D$-dimensional vector into $m$ smaller subvectors (e.g. 1536 dim $\rightarrow$ 96 subvectors of 16 dim).
- Clusters each sub-space into 256 centroids using k-means and stores 1-byte centroid indexes.
- **Compression**: **90%–95% RAM reduction**.
- **Recall Impact**: $3\%$–$8\%$ recall degradation; best paired with a 2nd-stage uncompressed float32 reranking pass.

---

## Phase 4: Production Schemas & Multi-Tenancy

### 1. PostgreSQL + `pgvector` Schema
```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Table with tenant partitioning & metadata
CREATE TABLE document_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    document_id VARCHAR(128) NOT NULL,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}',
    embedding vector(1536) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Partial HNSW Index per tenant (or global filtered HNSW)
CREATE INDEX idx_embeddings_hnsw_cosine 
ON document_embeddings 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 128);

-- Single-Stage Filtered Vector Query
SELECT 
    id, 
    document_id, 
    content,
    1 - (embedding <=> $1::vector) AS similarity
FROM document_embeddings
WHERE tenant_id = $2
ORDER BY embedding <=> $1::vector
LIMIT 10;
```

### 2. Guarding Against Post-Filter Recall Collapse
- **Naive Post-Filtering**: Finds top 100 nearest vectors in the entire index, then discards rows where `tenant_id != 'org_123'`. If `org_123` represents 1% of the data, the query returns 0 to 1 results!
- **Single-Stage Filtered ANN**: Uses payload-aware graph traversals (native in Qdrant, Milvus, and pgvector 0.7+) where the graph traversal only visits nodes matching the metadata predicate.

---

## Phase 5: Hardware & Memory Sizing Formulas

To size production vector database instances, calculate:

$$\text{Raw Vectors (bytes)} = N \times D \times 4$$

$$\text{HNSW Graph Overhead (bytes)} \approx N \times M \times 2 \times 8$$

$$\text{Total RAM (with OS & Buffer Margin)} = (\text{Vector RAM} + \text{Graph RAM}) \times 1.30$$

*Example for 1,000,000 vectors of dimension 1536 with $M=32$:*
- Vector Data: $10^6 \times 1536 \times 4 \approx 6.14 \text{ GB}$
- Graph Overhead: $10^6 \times 32 \times 2 \times 8 \approx 0.51 \text{ GB}$
- Total with 30% margin: $(6.14 + 0.51) \times 1.30 \approx \mathbf{8.65 \text{ GB RAM}}$

---

## Anti-Patterns & Hard Guardrails

- 🚫 **Never build HNSW indexes during bulk data ingestion**: Bulk insert without indexes first, then build the HNSW index in a single batch. Building HNSW incrementally row-by-row causes index fragmentation and takes 10x longer.
- 🚫 **Never use Naive Post-Filtering for restrictive metadata**: Always use filtered ANN or separate tenant partitions.
- 🚫 **Never query raw Cosine similarity on non-normalized vectors without cosine ops**: If using inner product ops (`<#>`), vectors must be unit-normalized first.
- 🚫 **Never leave `ef_search` at default (10)**: Tune `ef_search` between 40 and 80 in production to achieve $>98\%$ recall.

---

## Verification & CLI Tooling

Use the companion script [`vector_index_toolkit.py`](./scripts/vector_index_toolkit.py) to calculate RAM sizing, benchmark SQ8 quantization recall, and simulate filtered ANN search:

```bash
# Run self-test suite
python skills/database-and-data-engineering/vector-database-architect/scripts/vector_index_toolkit.py --test

# Calculate hardware & RAM sizing
python skills/database-and-data-engineering/vector-database-architect/scripts/vector_index_toolkit.py size --count 500000 --dim 1536 --m 32 --quantization sq8
```
