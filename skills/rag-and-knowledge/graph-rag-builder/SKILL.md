---
name: graph-rag-builder
description: >-
  Use this skill when designing, building, or querying Knowledge Graph-enhanced RAG (GraphRAG) systems.
  Extracts entities, relations, and communities from unstructured text, constructs queryable graphs
  (Neo4j, NetworkX, Graphiti), and enables multi-hop relational reasoning across documents.
---

# Graph RAG Builder & Knowledge Graph Architect

## Overview

Builds, extracts, and queries Knowledge Graph-enhanced RAG (GraphRAG) systems using Neo4j, NetworkX, and Graphiti. Extracts entities, relations, and communities from unstructured text to enable multi-hop relational reasoning across complex corpora.

## When to Use

- When questions require tracing multi-step connections between people, companies, software modules, or concepts (`"Which services depend on the authentication gateway through indirect calls?"`).
- When vector search fails because relevant facts are scattered across hundreds of separate pages.
- When building hierarchical knowledge graphs, community summaries, or entity catalogs.
- Trigger phrases: `"GraphRAG"`, `"knowledge graph"`, `"Neo4j agent"`, `"entity extraction"`, `"multi-hop reasoning"`.

---
- **When NOT to use**: Flat vector-only chunk retrieval (use `agentic-rag-engineer`) or relational SQL database modeling (use `backend-architecture`).

## Core Process & Knowledge Graph Construction

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

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| *"Standard RAG is good enough; Knowledge Graphs add too much complexity."* | Standard RAG cannot perform multi-hop reasoning (e.g. connecting Entity A -> Entity B -> Entity C across disparate documents). |
| *"We can extract entities using regex without an LLM."* | Regex cannot resolve entity coreferences ('it', 'the company', 'the CEO') or infer nuanced relationship predicates. |
| *"Entity deduplication can be done by simple lowercase string matching."* | Acronyms, aliases, and misspellings require embedding-based clustering or canonical entity resolution. |
| *"Graph queries can replace vector search entirely."* | Graph traversal requires seed entities; optimal retrieval combines vector search to find seed nodes with graph walks to explore context. |

## Red Flags

- Knowledge graph with disconnected orphan nodes due to missing coreference resolution.
- Unbounded Cypher/graph traversal queries that cause exponential graph walk timeouts.
- Extracting generic, low-information relation predicates (`RELATED_TO`, `HAS_THING`).
- Failing to persist source chunk provenance on graph edges.

## Verification

After completing the workflow, confirm:
- [ ] Entity extraction extracts typed nodes (Person, Org, Service, Concept) with canonical IDs.
- [ ] Relation predicates are explicit, directed, and grounded in source text.
- [ ] Multi-hop queries successfully traverse 2-3 hops to answer complex relational questions.
- [ ] Graph queries return both structured subgraphs and cited provenance references.
