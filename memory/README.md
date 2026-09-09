# 3-Tier Agentic Memory Engine

A production-grade, zero-dependency Python implementation of the **3-Tier Agent Memory Architecture** conforming to [`agent-memory-architect`](../skills/agent-memory-architect/SKILL.md).

---

## 1. Architectural Model

```
┌────────────────────────────────────────────────────────────────────────┐
│               TIER 1: WORKING MEMORY (Active Context)                  │
│  Transient scratchpad, sliding-window buffer & automatic compaction   │
│                 Token Budget Tracker & System Notes                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (summarize & consolidate)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               TIER 2: EPISODIC MEMORY (Execution Ledger)               │
│      Persistent SQLite relational database (`.memory/agent_memory.db`) │
│     Chronological trace of turns, tool payloads, latencies & tokens    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ (extract durable facts)
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             TIER 3: SEMANTIC MEMORY (Long-Term Fact Store)             │
│        Persistent key-fact vector store with cosine similarity         │
│     Durable architectural decisions, user preferences & conventions     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Memory Tier Details

### Tier 1: Working Memory
- **Purpose**: Tracks active turn history in the current session.
- **Auto-Compaction**: When turns exceed the token budget threshold ($85\%$), older turns are automatically compacted into rolling milestone summary notes while preserving the most recent turns.

### Tier 2: Episodic Memory
- **Storage**: Persistent SQLite relational database at `.memory/agent_memory.db`.
- **Schema**:
  - `session_id`: Unique identifier of the user/agent interaction.
  - `agent_name`: Name of the agent performing the action.
  - `action_type`: Task decomposition, tool invocation, or user interaction.
  - `input_payload` & `output_payload`: Serialized JSON parameters and execution results.
  - `status`, `duration_ms`, `tokens_used`.

### Tier 3: Semantic Memory
- **Storage**: Persistent SQLite table `semantic_facts` with access count and timestamp tracking.
- **Matching Engine**: Normalized subword and root-prefix term frequency vector similarity.
- **Capabilities**:
  - `remember_fact(category, key, fact)`: Stores or updates a durable rule.
  - `recall_facts(query, top_k=3)`: Retrieves the highest-relevance facts matching an agent prompt.

---

## 3. Usage & CLI

### Programmatic Usage in Python:
```python
from memory.memory_engine import AgentMemoryEngine

# Initialize engine with session context
engine = AgentMemoryEngine(session_id="session_dev_01")

# Tier 1: Record working turns
engine.record_turn("fullstack-engineer", "assistant", "Implemented Redis JWT blocklist.")

# Tier 3: Store durable project facts
engine.remember_fact("security", "jwt_policy", "All JWT tokens must use RS256 with 15-minute expiration.")

# Tier 3: Semantic recall
facts = engine.recall_facts("what is the token expiration rule?")
for f in facts:
    print(f"[{f['similarity_score']}] {f['fact_text']}")
```

### Command-Line Interface:
```bash
# Run automated self-test across all 3 tiers
python memory/memory_engine.py --test

# Query semantic long-term memory from the terminal
python memory/memory_engine.py --query "database connection pooling"
```
