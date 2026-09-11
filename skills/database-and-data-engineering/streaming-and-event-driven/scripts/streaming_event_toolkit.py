#!/usr/bin/env python3
"""
Streaming & Event-Driven Systems Toolkit
=========================================
Zero-dependency toolkit for:
- Consistent partition key hashing (Kafka/Redpanda simulation)
- Transactional Outbox pattern simulation & atomic state drain
- Idempotent consumer engine with deduplication windows
- Non-blocking retry topics & Dead Letter Queue (DLQ) router
- CloudEvents v1.0 JSON schema validation
"""

import argparse
import hashlib
import json
import sys
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# 1. Consistent Partition Key Router
# ---------------------------------------------------------------------------

def compute_partition(key: str, num_partitions: int) -> int:
    """
    Deterministically routes a business entity key to a partition index (0 to num_partitions - 1).
    Uses SHA256 truncated integer hashing to ensure uniform distribution and ordering consistency.
    """
    if num_partitions <= 0:
        raise ValueError("num_partitions must be > 0")
    if not key:
        raise ValueError("partition key cannot be empty")

    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    hash_int = int(digest[:8], 16)
    return hash_int % num_partitions


# ---------------------------------------------------------------------------
# 2. CloudEvents v1.0 Schema Validator
# ---------------------------------------------------------------------------

REQUIRED_CLOUDEVENTS_FIELDS = {"specversion", "id", "source", "type"}


def validate_cloudevent(event: Dict) -> Tuple[bool, List[str]]:
    """
    Validates that a JSON event dictionary conforms to the CloudEvents v1.0 specification.
    """
    errors = []
    for f in REQUIRED_CLOUDEVENTS_FIELDS:
        if f not in event or not str(event[f]).strip():
            errors.append(f"Missing required CloudEvent attribute: '{f}'")

    if event.get("specversion") != "1.0":
        errors.append(f"Invalid specversion '{event.get('specversion')}'; must be '1.0'")

    if "data" not in event:
        errors.append("CloudEvent must include a 'data' payload attribute")

    return (len(errors) == 0, errors)


# ---------------------------------------------------------------------------
# 3. Transactional Outbox Pattern Simulator
# ---------------------------------------------------------------------------

@dataclass
class OutboxRecord:
    id: str
    aggregate_type: str
    aggregate_id: str
    event_type: str
    payload: Dict
    status: str = "PENDING"  # PENDING, PUBLISHED, FAILED


class TransactionalOutboxEngine:
    def __init__(self):
        self.database_entities: Dict[str, Dict] = {}
        self.outbox_table: List[OutboxRecord] = []
        self.published_events: List[Dict] = []

    def commit_transaction(
        self,
        entity_id: str,
        entity_data: Dict,
        event_type: str,
        aggregate_type: str
    ) -> OutboxRecord:
        """
        Simulates an atomic database transaction writing both entity state AND outbox event.
        """
        # Step 1: Write business entity
        self.database_entities[entity_id] = entity_data

        # Step 2: Write outbox event
        outbox_entry = OutboxRecord(
            id=f"evt_{len(self.outbox_table) + 1:04d}",
            aggregate_type=aggregate_type,
            aggregate_id=entity_id,
            event_type=event_type,
            payload=entity_data,
            status="PENDING"
        )
        self.outbox_table.append(outbox_entry)
        return outbox_entry

    def drain_outbox(self, max_batch: int = 10) -> int:
        """
        Simulates the asynchronous outbox publisher / CDC process.
        """
        drained_count = 0
        for entry in self.outbox_table:
            if entry.status == "PENDING" and drained_count < max_batch:
                # Simulate successful Kafka message publication
                self.published_events.append({
                    "event_id": entry.id,
                    "topic": f"{entry.aggregate_type}.events",
                    "key": entry.aggregate_id,
                    "data": entry.payload
                })
                entry.status = "PUBLISHED"
                drained_count += 1
        return drained_count


# ---------------------------------------------------------------------------
# 4. Resilient Consumer, Deduplication & DLQ Engine
# ---------------------------------------------------------------------------

@dataclass
class ConsumerResult:
    event_id: str
    status: str  # 'PROCESSED', 'SKIPPED_DUPLICATE', 'SENT_TO_RETRY', 'SENT_TO_DLQ'
    attempt_count: int
    destination_topic: str


class ResilientEventConsumer:
    def __init__(self, main_topic: str, max_retries: int = 3):
        self.main_topic = main_topic
        self.max_retries = max_retries
        self.processed_event_ids: Set[str] = set()
        self.retry_queues: Dict[int, List[Dict]] = {1: [], 2: []}
        self.dead_letter_queue: List[Dict] = []
        self.business_state: Dict[str, Dict] = {}

    def process_message(
        self,
        event: Dict,
        should_fail: bool = False
    ) -> ConsumerResult:
        """
        Consumes an incoming message with idempotency check, retry escalation, and DLQ routing.
        """
        event_id = event["id"]
        attempt = event.get("retry_count", 0)

        # 1. Idempotency Gate (Deduplication)
        if event_id in self.processed_event_ids:
            return ConsumerResult(
                event_id=event_id,
                status="SKIPPED_DUPLICATE",
                attempt_count=attempt,
                destination_topic=self.main_topic
            )

        # 2. Simulated Processing Failure (Poison Pill)
        if should_fail:
            next_attempt = attempt + 1
            if next_attempt > self.max_retries:
                # Exceeded retries -> Route to Dead Letter Queue
                event_copy = event.copy()
                event_copy["error"] = "Exceeded maximum retry threshold"
                self.dead_letter_queue.append(event_copy)
                return ConsumerResult(
                    event_id=event_id,
                    status="SENT_TO_DLQ",
                    attempt_count=next_attempt,
                    destination_topic=f"{self.main_topic}.dlq"
                )
            else:
                # Route to appropriate non-blocking retry topic
                retry_topic_num = min(next_attempt, 2)
                event_copy = event.copy()
                event_copy["retry_count"] = next_attempt
                self.retry_queues[retry_topic_num].append(event_copy)
                return ConsumerResult(
                    event_id=event_id,
                    status="SENT_TO_RETRY",
                    attempt_count=next_attempt,
                    destination_topic=f"{self.main_topic}.retry-{retry_topic_num}"
                )

        # 3. Successful Processing & State Mutate
        self.processed_event_ids.add(event_id)
        self.business_state[event_id] = event.get("data", {})

        return ConsumerResult(
            event_id=event_id,
            status="PROCESSED",
            attempt_count=attempt,
            destination_topic=self.main_topic
        )


# ---------------------------------------------------------------------------
# CLI & Self-Test Suite
# ---------------------------------------------------------------------------

def run_self_test():
    print("=================================================================")
    print("Running Streaming & Event-Driven Toolkit Self-Tests...")
    print("=================================================================")

    # Test 1: Deterministic Partition Key Hashing
    key_a = "customer_1001"
    key_b = "customer_1002"
    p1 = compute_partition(key_a, 16)
    p2 = compute_partition(key_a, 16)
    assert p1 == p2, "Same key must deterministically yield identical partition"
    assert 0 <= p1 < 16, "Partition must be within range [0, num_partitions-1]"
    p3 = compute_partition(key_b, 16)
    print(f"[PASS] Partition key hashing passed ('{key_a}' -> partition {p1}, '{key_b}' -> partition {p3})")

    # Test 2: CloudEvents Schema Validation
    valid_ce = {
        "specversion": "1.0",
        "id": "evt-abc-123",
        "source": "https://api.myapp.com/orders",
        "type": "com.myapp.order.created",
        "data": {"order_id": "ORD-99", "amount": 149.50}
    }
    is_valid, errors = validate_cloudevent(valid_ce)
    assert is_valid, f"Expected valid CloudEvent, got errors: {errors}"

    invalid_ce = {"specversion": "0.3", "id": "123"}
    is_valid, errors = validate_cloudevent(invalid_ce)
    assert not is_valid and len(errors) >= 3, "Failed to catch invalid CloudEvent specification"
    print("[PASS] CloudEvents v1.0 schema validator passed")

    # Test 3: Transactional Outbox Pattern
    outbox_engine = TransactionalOutboxEngine()
    record = outbox_engine.commit_transaction(
        entity_id="order_500",
        entity_data={"status": "PAID", "total": 99.0},
        event_type="OrderPaid",
        aggregate_type="orders"
    )
    assert record.status == "PENDING"
    assert len(outbox_engine.outbox_table) == 1
    assert "order_500" in outbox_engine.database_entities

    drained = outbox_engine.drain_outbox()
    assert drained == 1
    assert record.status == "PUBLISHED"
    assert len(outbox_engine.published_events) == 1
    print("[PASS] Transactional Outbox commit & drain passed")

    # Test 4: Idempotent Consumer & DLQ Routing
    consumer = ResilientEventConsumer(main_topic="orders.v1", max_retries=2)
    sample_event = {
        "id": "event_uuid_100",
        "data": {"user": "alice", "action": "login"}
    }

    # First pass: normal processing
    r1 = consumer.process_message(sample_event)
    assert r1.status == "PROCESSED"
    assert "event_uuid_100" in consumer.processed_event_ids

    # Second pass: duplicate delivery (should skip without error)
    r2 = consumer.process_message(sample_event)
    assert r2.status == "SKIPPED_DUPLICATE"

    # Poison pill pass: fails and escalates to retry, then DLQ
    poison_pill = {"id": "bad_event_999", "data": {"corrupt": True}}
    res_retry1 = consumer.process_message(poison_pill, should_fail=True)
    assert res_retry1.status == "SENT_TO_RETRY" and res_retry1.attempt_count == 1

    poison_pill["retry_count"] = 1
    res_retry2 = consumer.process_message(poison_pill, should_fail=True)
    assert res_retry2.status == "SENT_TO_RETRY" and res_retry2.attempt_count == 2

    poison_pill["retry_count"] = 2
    res_dlq = consumer.process_message(poison_pill, should_fail=True)
    assert res_dlq.status == "SENT_TO_DLQ" and res_dlq.attempt_count == 3
    assert len(consumer.dead_letter_queue) == 1
    print("[PASS] Idempotent consumer, retry backoff & DLQ routing passed")

    print("\nALL STREAMING & EVENT TOOLKIT TESTS PASSED (4/4) [OK]\n")


def main():
    parser = argparse.ArgumentParser(description="Streaming & Event-Driven Systems Toolkit")
    parser.add_argument("--test", action="store_true", help="Run self-test suite")
    subparsers = parser.add_subparsers(dest="command")

    hash_p = subparsers.add_parser("hash-key", help="Calculate partition for a key")
    hash_p.add_argument("--key", type=str, required=True, help="Entity partition key")
    hash_p.add_argument("--partitions", type=int, default=16, help="Total number of partitions")

    args = parser.parse_args()

    if args.test:
        run_self_test()
        sys.exit(0)
    elif args.command == "hash-key":
        p = compute_partition(args.key, args.partitions)
        print(f"Key '{args.key}' -> Partition {p} (of {args.partitions} partitions)")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
