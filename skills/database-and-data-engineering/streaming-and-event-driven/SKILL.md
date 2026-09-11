---
name: streaming-and-event-driven
description: >-
  Use this skill when designing, building, or troubleshooting event-driven architectures, distributed
  streaming pipelines, and message brokers (Kafka, Redpanda, Redis Streams). Covers topic partitioning,
  idempotent consumers, Transactional Outbox pattern, retry topics with Dead Letter Queues (DLQ),
  and exactly-once processing semantics.
---

# Streaming & Event-Driven Systems Architecture

Acts as a Principal Distributed Systems & Event Streaming Architect. Designs resilient event-driven architectures across Apache Kafka, Redpanda, and Redis Streams. Solves complex distributed systems challenges including the dual-write problem, partition hotspotting, out-of-order event arrivals, consumer rebalancing, poison-pill triage, and end-to-end exactly-once processing semantics.

---

## When to Use This Skill

- When designing Kafka/Redpanda topic schemas, partition strategies, and retention policies.
- When implementing the Transactional Outbox pattern to prevent data loss or dual-write inconsistency.
- When authoring resilient consumer groups with non-blocking retry topics and Dead Letter Queues (DLQ).
- When configuring idempotent consumers to guarantee safe event replays without duplicate processing.
- When implementing Redis Streams for lightweight background pipelines (`XADD`, `XREADGROUP`, `XCLAIM`).
- When defining event envelopes adhering to CloudEvents v1.0 specifications.
- Trigger phrases: `"design kafka topic"`, `"event-driven architecture"`, `"redis streams consumer"`, `"dead letter queue pattern"`, `"transactional outbox"`, `"stream processing"`, `"idempotent consumer"`, `"event schema registry"`.

---

## The Event-Driven Architecture Lifecycle

```
┌────────────────────────────────────────────────────────────────────────┐
│                   Distributed Event Streaming Topology                 │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. Transactional Outbox        │ 2. Topic & Partition Routing          │
│ (Atomic DB Commit + CDC Drain) │ (Consistent Key Hashing, Compaction)  │
├────────────────────────────────┼───────────────────────────────────────┤
│ 3. Consumer Group Offset Mgmt  │ 4. Non-Blocking Retry & DLQ Pipeline  │
│ (Manual Commit, Sticky Assign) │ (Main -> Retry-1 -> Retry-2 -> DLQ)   │
├────────────────────────────────┴───────────────────────────────────────┤
│ 5. Idempotent Processing (Deduplication Cache, Versioned State Store)  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Topic Design & Partitioning Strategy

Partitions are the fundamental unit of parallelism and ordering in distributed streaming:

### 1. Key Selection & Ordering Guarantees
- **Kafka guarantees strict order ONLY within a single partition**, never across partitions.
- Always use the core business entity ID as the partition key (e.g., `user_id`, `account_id`, `order_id`).
- All events for that entity will route to the same partition, guaranteeing chronological processing.
- **Guard against Hotspot Partitions**: Avoid keys with extreme skew (e.g., tenant ID for enterprise accounts). If a single tenant generates 50% of traffic, salt the key (`tenant_id + "_" + (hash(id) % 8)`) to distribute load.

### 2. Partition Sizing Equation
Calculate the minimum number of partitions needed:

$$P = \max\left(\frac{T_{\text{target}}}{T_{\text{producer}}}, \frac{T_{\text{target}}}{T_{\text{consumer}}}\right)$$

Where $T_{\text{consumer}}$ is the sustained throughput of a single consumer worker thread (e.g. 1,000 msgs/sec). For a 20,000 msg/sec target, provision at least 20 partitions.

### 3. Log Compaction vs. Time Retention
- **Time Retention (`cleanup.policy=delete`)**: For transient logs, audit trails, and append-only event streams. Configured with `retention.ms` (e.g., 7 days).
- **Log Compaction (`cleanup.policy=compact`)**: For state changelogs and entity snapshots. Kafka keeps the latest record for each key indefinitely, allowing new consumers to rebuild full state tables.

---

## Phase 2: Solving the Dual-Write Problem (Transactional Outbox)

### The Dual-Write Bug
Attempting to write to a relational database and publish an event to Kafka in the same API handler will inevitably fail:
- If DB commits and Kafka publish fails $\rightarrow$ Event is lost forever.
- If Kafka publish succeeds and DB transaction rolls back $\rightarrow$ Downstream services process phantom data.

### The Solution: Transactional Outbox Pattern
1. Write business entity mutations AND an outbox record (`outbox_events` table) within a single ACID database transaction.
2. An asynchronous publisher or CDC engine (Debezium) reads the outbox table and publishes events to Kafka with `acks=all`.
3. Once acknowledged, the outbox record is marked published or pruned.

```sql
-- Transactional Outbox Table
CREATE TABLE outbox_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type VARCHAR(64) NOT NULL,
    aggregate_id VARCHAR(128) NOT NULL,
    event_type VARCHAR(128) NOT NULL,
    payload JSONB NOT NULL,
    headers JSONB NOT NULL DEFAULT '{}',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP WITH TIME ZONE
);
```

---

## Phase 3: Resilient Consumer Architecture & DLQ Topology

Never block consumer threads or perform infinite synchronous retries on failures. A single poison-pill message will stall the entire partition.

### The Non-Blocking Retry Pipeline

```
[Main Topic: orders.v1] ─── (Failure) ───► [Retry Topic 1: orders.v1.retry-30s]
                                                    │
                                                (Failure)
                                                    ▼
                                           [Retry Topic 2: orders.v1.retry-5m]
                                                    │
                                                (Failure)
                                                    ▼
                                           [Dead Letter Queue: orders.v1.dlq]
```

1. **Main Topic**: Processes events immediately. On transient failure (e.g., network timeout, downstream 503), publish to `orders.v1.retry-30s` with retry count header and commit the offset on the main topic.
2. **Retry Topics**: Consumers configured with scheduled polling or delayed handlers.
3. **Dead Letter Queue (DLQ)**: When `retry_count >= MAX_RETRIES` (e.g., 3), route to `orders.v1.dlq`. Alerts are triggered for engineer inspection.
4. **Main Partition Continues**: No message behind the failed record is blocked.

---

## Phase 4: Idempotent Consumer Implementation

Because distributed streaming offers **at-least-once** delivery under network partitions and consumer crashes, duplicate events will occur. Every consumer must be idempotent:

```python
def process_incoming_event(event: dict, db_conn):
    event_id = event["id"]
    
    # 1. Atomic Deduplication Gate
    # Attempt insert into processed_events table with unique constraint
    with db_conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO processed_events (event_id, processed_at)
            VALUES (%s, CURRENT_TIMESTAMP)
            ON CONFLICT (event_id) DO NOTHING;
            """,
            (event_id,)
        )
        if cur.rowcount == 0:
            # Already processed! Skip duplicate safely.
            return {"status": "SKIPPED_DUPLICATE"}
        
        # 2. Execute business mutation in same transaction
        apply_business_logic(event["data"], cur)
        db_conn.commit()
        
    return {"status": "SUCCESS"}
```

---

## Phase 5: Redis Streams Architecture

For lightweight systems not requiring full Kafka infrastructure:
- **`XADD mystream * sensor_id 101 temp 22.4`**: Appends record with auto-generated millisecond-sequence ID.
- **`XGROUP CREATE mystream mygroup $ MKSTREAM`**: Creates consumer group starting at tail (`$`).
- **`XREADGROUP GROUP mygroup worker1 COUNT 10 BLOCK 2000 STREAMS mystream >`**: Reads unread messages.
- **`XACK mystream mygroup <id>`**: Acknowledges processed message.
- **`XAUTOCLAIM mystream mygroup worker1 60000 0-0 COUNT 10`**: Automatically claims messages pending $>60\text{s}$ from crashed workers.

---

## Anti-Patterns & Hard Guardrails

- 🚫 **Never use auto-commit (`enable.auto.commit=true`) in production consumers**: Auto-commit advances offsets before business logic completes, causing permanent data loss if the worker crashes mid-task.
- 🚫 **Never retry failed messages in an in-memory loop on the consumer thread**: This triggers a consumer heartbeat timeout, causing a rebalance storm across the cluster.
- 🚫 **Never mutate the database and send a message without the Outbox pattern**: Guarantees data drift and silent inconsistencies.
- 🚫 **Never use random or time-only partition keys**: Destroys per-entity ordering guarantees.

---

## Verification & CLI Tooling

Use the companion script [`streaming_event_toolkit.py`](./scripts/streaming_event_toolkit.py) to simulate partition routing, test transactional outbox draining, and benchmark idempotent DLQ consumers:

```bash
# Run self-test suite
python skills/database-and-data-engineering/streaming-and-event-driven/scripts/streaming_event_toolkit.py --test

# Route event to partition
python skills/database-and-data-engineering/streaming-and-event-driven/scripts/streaming_event_toolkit.py hash-key --key "cust_98765" --partitions 16
```
