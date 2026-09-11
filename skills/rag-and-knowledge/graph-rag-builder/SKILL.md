---
name: graph-rag-builder
description: >-
  Use this skill when designing, building, or querying Knowledge Graph-enhanced RAG (GraphRAG) systems.
  Extracts entities, relations, and communities from unstructured text, constructs queryable graphs
  (Neo4j, NetworkX, Graphiti), and enables multi-hop relational reasoning across documents.
---

# Graph RAG Builder & Knowledge Graph Architect

Enables agents to perform complex, multi-hop reasoning over connected entities and relationships by combining graph databases with semantic language models (GraphRAG).

## When to Use This Skill
- When questions require tracing multi-step connections between people, companies, software modules, or concepts (`"Which services depend on the authentication gateway through indirect calls?"`).
- When vector search fails because relevant facts are scattered across hundreds of separate pages.
- When building hierarchical knowledge graphs, community summaries, or entity catalogs.
- Trigger phrases: `"GraphRAG"`, `"knowledge graph"`, `"Neo4j agent"`, `"entity extraction"`, `"multi-hop reasoning"`.

---

## Vector Search vs. Graph RAG

| Dimension | Vector RAG (Flat Similarity) | Graph RAG (Relational Structure) |
|---|---|---|
| **Best For** | Point-in-time facts, direct similarity | Connected networks, impact analysis, holistic themes |
| **Failure Mode** | Blind to relationships across documents | Requires upfront entity extraction compute |
| **Query Style** | "What is the return policy for item X?" | "How does component A affect component F through B and C?" |

---

## Step-by-Step Graph RAG Architecture

```
┌────────────────────────────────────────────────────────┐
│                   GraphRAG Pipeline                    │
├──────────────┬──────────────┬─────────────┬────────────┤
│ 1. Entity &  │ 2. Graph     │ 3. Community│ 4. Hybrid  │
│    Relation  │    Build     │    Detection│    Graph + │
│    Extract   │   (Triplets) │   (Leiden)  │    Vector  │
└──────────────┴──────────────┴─────────────┴────────────┘
```

### Step 1: Entity & Relationship Extraction
Extract subject-predicate-object triplets from text chunks using structured extraction:
```python
from pydantic import BaseModel, Field
from typing import List

class Entity(BaseModel):
    name: str
    type: str = Field(description="e.g., Service, Database, Team, Protocol")
    description: str

class Relationship(BaseModel):
    source_entity: str
    target_entity: str
    relation_type: str = Field(description="e.g., DEPENDS_ON, WRITES_TO, MAINTAINS")
    strength: float
```

### Step 2: Ingestion into Graph Database (Neo4j / NetworkX)
```cypher
// Cypher query to insert extracted triplet
MERGE (s:Service {name: $source_name})
MERGE (t:Database {name: $target_name})
MERGE (s)-[r:WRITES_TO]->(t)
SET r.updated_at = timestamp();
```

### Step 3: Multi-Hop Cypher Generation & Traversal
When a user asks a relational question, convert natural language into a Cypher query:
```cypher
MATCH (origin:Service {name: 'AuthGateway'})-[:DEPENDS_ON*1..3]->(downstream)
RETURN origin.name, downstream.name, count(*) as hops;
```

### Step 4: Community Summarization (Global Search)
- Use community detection algorithms (e.g. Leiden or Louvain) to cluster related nodes into sub-graphs.
- Pre-generate hierarchical summaries for each community to answer broad thematic questions ("What are the main architecture risks across the entire platform?").

## Anti-Patterns & Traps to Avoid

1. **Unbounded Multi-Hop Graph Traversal**: Executing graph queries without edge depth limits (e.g., `[:DEPENDS_ON*]`). On dense graphs, this triggers combinatorial explosion, database timeouts, and memory crashes. Always enforce explicit hop bounds (e.g., `[:DEPENDS_ON*1..3]`).
2. **Entity Duplication & Canonicalization Failure**: Inserting synonyms as distinct nodes (e.g., "Postgres", "PostgreSQL", and "PG_DB" as 3 separate nodes). This severs relationship paths and breaks multi-hop reasoning. Always run entity resolution prior to graph ingestion.
3. **The Knowledge Graph "Hairball"**: Extracting trivial verbs or unconstrained relationships from conversational text. Without an ontology schema, the graph fills with low-signal edges that drown out causal connections.
4. **Local Traversal for Global Queries**: Attempting to answer high-level thematic queries ("Summarize all security risks across the enterprise") using local node neighborhood searches. Global questions require hierarchical community detection (Leiden/Louvain) summaries.

---

## Quality Checklist

- [ ] Entity resolution normalizes synonyms and aliases into canonical node identifiers before insertion.
- [ ] Triplet extraction is constrained by an explicit entity and relationship ontology.
- [ ] Cypher / Gremlin queries enforce hard depth boundaries (`*1..3`) and pagination limits.
- [ ] Node labels and relationship types use consistent capitalization and snake_case conventions.
- [ ] Hierarchical community detection (Leiden/Louvain) is pre-computed for corpus-wide global queries.
- [ ] Retrieved subgraphs are formatted into clean natural language context strings before passing to LLM generation.
