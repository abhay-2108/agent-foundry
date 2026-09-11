#!/usr/bin/env python3
"""
Data Pipeline & Modern ELT Toolkit
====================================
Zero-dependency toolkit for:
- DAG topological dependency sorting & cycle detection (Airflow/Dagster)
- dbt SQL model linting & architectural anti-pattern detection
- In-memory incremental merge & lookback window simulation
- Data quality assertion testing (Uniqueness, Non-null, Referential integrity)
"""

import argparse
import json
import re
import sys
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# 1. DAG Dependency Sorter & Cycle Detection
# ---------------------------------------------------------------------------

class DAGDependencyError(Exception):
    pass


def topological_sort(tasks: List[str], dependencies: Dict[str, List[str]]) -> List[str]:
    """
    Sorts DAG tasks using Kahn's algorithm.
    dependencies: dict where key depends on values, e.g. {'marts': ['int'], 'int': ['stg']}
    Returns ordered execution list. Raises DAGDependencyError if cycles exist.
    """
    in_degree = {t: 0 for t in tasks}
    adjacency = defaultdict(list)

    # Validate all referenced nodes exist
    for task, upstreams in dependencies.items():
        if task not in in_degree:
            in_degree[task] = 0
        for upstream in upstreams:
            if upstream not in in_degree:
                in_degree[upstream] = 0
            adjacency[upstream].append(task)
            in_degree[task] += 1

    queue = deque([node for node, deg in in_degree.items() if deg == 0])
    ordered = []

    while queue:
        node = queue.popleft()
        ordered.append(node)
        for downstream in adjacency[node]:
            in_degree[downstream] -= 1
            if in_degree[downstream] == 0:
                queue.append(downstream)

    if len(ordered) != len(in_degree):
        unresolved = [node for node, deg in in_degree.items() if deg > 0]
        raise DAGDependencyError(f"Cycle detected in DAG. Unresolved nodes: {unresolved}")

    return ordered


# ---------------------------------------------------------------------------
# 2. dbt SQL Model Linter & Contract Checker
# ---------------------------------------------------------------------------

@dataclass
class LintIssue:
    line_number: int
    rule_id: str
    severity: str  # 'ERROR' or 'WARNING'
    message: str


def lint_dbt_sql(sql_content: str) -> List[LintIssue]:
    """
    Inspects SQL for common dbt & dimensional modeling anti-patterns.
    """
    issues = []
    lines = sql_content.splitlines()

    has_config_block = "{{ config(" in sql_content or "{{config(" in sql_content
    is_incremental = "materialized='incremental'" in sql_content or 'materialized="incremental"' in sql_content
    has_unique_key = "unique_key=" in sql_content

    if is_incremental and not has_unique_key:
        issues.append(LintIssue(
            line_number=1,
            rule_id="DBT-001",
            severity="ERROR",
            message="Incremental model is missing 'unique_key' configuration."
        ))

    if is_incremental and "is_incremental()" not in sql_content:
        issues.append(LintIssue(
            line_number=1,
            rule_id="DBT-002",
            severity="ERROR",
            message="Incremental model config declared but no 'is_incremental()' filter block found in SQL."
        ))

    raw_table_regex = re.compile(r'\bFROM\s+([a-zA-Z0-9_]+)\b', re.IGNORECASE)

    for idx, line in enumerate(lines, start=1):
        clean_line = line.strip()

        # Check for raw table references without ref() or source()
        match = raw_table_regex.search(clean_line)
        if match:
            table_ref = match.group(1).lower()
            if table_ref not in {"source_data", "final", "filtered", "staged", "joined", "base", "unnested"}:
                if "{{" not in line and "}}" not in line and not clean_line.startswith("--"):
                    issues.append(LintIssue(
                        line_number=idx,
                        rule_id="DBT-003",
                        severity="WARNING",
                        message=f"Possible raw table reference 'FROM {table_ref}'. Use {{{{ ref(...) }}}} or {{{{ source(...) }}}}."
                    ))

        # Check for select * in final queries without alias
        if clean_line.upper().startswith("SELECT *") and idx > 10 and not any(kw in clean_line.upper() for kw in ["FROM {{", "FROM SOURCE_DATA"]):
            issues.append(LintIssue(
                line_number=idx,
                rule_id="DBT-004",
                severity="WARNING",
                message="Unbounded 'SELECT *' detected in projection. Explicitly list columns to preserve schema contracts."
            ))

    return issues


# ---------------------------------------------------------------------------
# 3. Incremental Merge Simulation Engine
# ---------------------------------------------------------------------------

def simulate_incremental_merge(
    target_table: List[Dict],
    incoming_batch: List[Dict],
    unique_key: str,
    timestamp_col: str,
    lookback_seconds: int = 86400 * 3
) -> Tuple[List[Dict], Dict[str, int]]:
    """
    Simulates a production dbt/warehouse incremental MERGE operation with a lookback window.
    """
    table_map = {row[unique_key]: row.copy() for row in target_table}
    max_target_ts = max((row[timestamp_col] for row in target_table), default=0)
    lookback_threshold = max_target_ts - lookback_seconds

    inserted = 0
    updated = 0
    filtered_out = 0

    for row in incoming_batch:
        row_ts = row.get(timestamp_col, 0)
        # Apply lookback filter
        if target_table and row_ts < lookback_threshold:
            filtered_out += 1
            continue

        key = row[unique_key]
        if key in table_map:
            # Overwrite existing record with newer data
            table_map[key] = row.copy()
            updated += 1
        else:
            table_map[key] = row.copy()
            inserted += 1

    result = sorted(list(table_map.values()), key=lambda x: x.get(timestamp_col, 0))
    stats = {
        "inserted": inserted,
        "updated": updated,
        "filtered_out_by_lookback": filtered_out,
        "final_total_rows": len(result)
    }
    return result, stats


# ---------------------------------------------------------------------------
# 4. Data Quality Assertion Engine
# ---------------------------------------------------------------------------

def test_data_quality(
    dataset: List[Dict],
    unique_cols: List[str],
    not_null_cols: List[str],
    accepted_values: Optional[Dict[str, Set]] = None,
    referential_keys: Optional[Dict[str, Set]] = None
) -> Dict[str, List[str]]:
    """
    Runs automated schema & value assertions across in-memory rows.
    """
    failures = defaultdict(list)
    seen_unique = {col: set() for col in unique_cols}

    for row_idx, row in enumerate(dataset):
        # 1. Uniqueness
        for col in unique_cols:
            val = row.get(col)
            if val in seen_unique[col]:
                failures[f"unique_{col}"].append(f"Row {row_idx}: duplicate value '{val}'")
            else:
                seen_unique[col].add(val)

        # 2. Not Null
        for col in not_null_cols:
            val = row.get(col)
            if val is None or str(val).strip() == "":
                failures[f"not_null_{col}"].append(f"Row {row_idx}: null or empty value found")

        # 3. Accepted Values
        if accepted_values:
            for col, allowed in accepted_values.items():
                val = row.get(col)
                if val is not None and val not in allowed:
                    failures[f"accepted_values_{col}"].append(f"Row {row_idx}: unexpected value '{val}' not in {allowed}")

        # 4. Referential Integrity
        if referential_keys:
            for col, parent_keys in referential_keys.items():
                val = row.get(col)
                if val is not None and val not in parent_keys:
                    failures[f"foreign_key_{col}"].append(f"Row {row_idx}: orphan foreign key '{val}'")

    return dict(failures)


# ---------------------------------------------------------------------------
# CLI & Self-Test Suite
# ---------------------------------------------------------------------------

def run_self_test():
    print("=================================================================")
    print("Running Data Pipeline Toolkit Self-Tests...")
    print("=================================================================")

    # Test 1: Topological Sort
    tasks = ["extract", "stg_orders", "int_order_items", "fct_orders", "dq_check"]
    deps = {
        "stg_orders": ["extract"],
        "int_order_items": ["stg_orders"],
        "fct_orders": ["int_order_items"],
        "dq_check": ["fct_orders"]
    }
    sorted_tasks = topological_sort(tasks, deps)
    assert sorted_tasks == tasks, f"Expected {tasks}, got {sorted_tasks}"
    print("[PASS] Topological sort passed")

    # Test 2: Cycle Detection
    cycle_deps = {
        "task_a": ["task_b"],
        "task_b": ["task_c"],
        "task_c": ["task_a"]
    }
    cycle_caught = False
    try:
        topological_sort(["task_a", "task_b", "task_c"], cycle_deps)
    except DAGDependencyError:
        cycle_caught = True
    assert cycle_caught, "Failed to catch dependency cycle"
    print("[PASS] Cycle detection passed")

    # Test 3: dbt SQL Linter
    bad_sql = """
    {{ config(materialized='incremental') }}
    SELECT * FROM raw_orders
    """
    issues = lint_dbt_sql(bad_sql)
    rule_ids = {i.rule_id for i in issues}
    assert "DBT-001" in rule_ids, "Failed to catch missing unique_key"
    assert "DBT-002" in rule_ids, "Failed to catch missing is_incremental() block"
    assert "DBT-003" in rule_ids, "Failed to catch raw table reference"
    print("[PASS] dbt SQL linter rules passed")

    # Test 4: Incremental Merge Simulation
    target = [
        {"order_id": 1, "status": "PENDING", "ts": 1000},
        {"order_id": 2, "status": "COMPLETED", "ts": 1050},
    ]
    batch = [
        {"order_id": 1, "status": "COMPLETED", "ts": 1100},  # Update
        {"order_id": 3, "status": "PENDING", "ts": 1150},    # Insert
        {"order_id": 4, "status": "FAILED", "ts": 100},      # Outdated (before lookback)
    ]
    merged, stats = simulate_incremental_merge(target, batch, unique_key="order_id", timestamp_col="ts", lookback_seconds=200)
    assert stats["inserted"] == 1
    assert stats["updated"] == 1
    assert stats["filtered_out_by_lookback"] == 1
    assert len(merged) == 3
    updated_order_1 = next(r for r in merged if r["order_id"] == 1)
    assert updated_order_1["status"] == "COMPLETED"
    print("[PASS] Incremental merge simulation passed")

    # Test 5: Data Quality Assertions
    data = [
        {"id": 101, "status": "ACTIVE", "customer_id": "C1"},
        {"id": 102, "status": "INVALID", "customer_id": "C2"},
        {"id": 101, "status": "ACTIVE", "customer_id": "C99"},  # Duplicate ID & orphan customer
    ]
    valid_customers = {"C1", "C2"}
    dq_results = test_data_quality(
        dataset=data,
        unique_cols=["id"],
        not_null_cols=["status"],
        accepted_values={"status": {"ACTIVE", "INACTIVE"}},
        referential_keys={"customer_id": valid_customers}
    )
    assert "unique_id" in dq_results
    assert "accepted_values_status" in dq_results
    assert "foreign_key_customer_id" in dq_results
    print("[PASS] Data quality assertion tests passed")

    print("\nALL DATA PIPELINE TOOLKIT TESTS PASSED (5/5) [OK]\n")


def main():
    parser = argparse.ArgumentParser(description="Data Pipeline & ELT Toolkit")
    parser.add_argument("--test", action="store_true", help="Run comprehensive test suite")
    parser.add_argument("--lint", type=str, help="Lint a dbt SQL model file")

    args = parser.parse_args()

    if args.test:
        run_self_test()
        sys.exit(0)
    elif args.lint:
        with open(args.lint, "r", encoding="utf-8") as f:
            content = f.read()
        issues = lint_dbt_sql(content)
        if not issues:
            print(f"✅ No issues found in {args.lint}")
        else:
            print(f"Found {len(issues)} issue(s) in {args.lint}:")
            for iss in issues:
                print(f"  [{iss.severity}] Line {iss.line_number} ({iss.rule_id}): {iss.message}")
            sys.exit(1 if any(i.severity == "ERROR" for i in issues) else 0)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
