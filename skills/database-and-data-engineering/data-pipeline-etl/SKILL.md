---
name: data-pipeline-etl
description: >-
  Use this skill when designing, building, or orchestrating data pipelines (Airflow, Dagster, Prefect),
  authoring dbt transformation models (Kimball star schemas: staging, intermediate, incremental marts),
  enforcing data quality test assertions (Great Expectations, dbt test), managing data contracts,
  and tracking DAG lineage.
---

# Data Pipeline Engineering & Modern ETL/ELT Architectures

Acts as a Lead Data & Analytics Engineer. Designs, authors, and optimizes end-to-end data pipelines using modern orchestration engines (Apache Airflow, Dagster, Prefect) and transform-in-place tools (dbt, DuckDB, Snowflake, BigQuery). Enforces Kimball dimensional modeling, writes robust incremental materializations, automates data quality assertion gates, and ensures 100% idempotent pipeline execution.

---

## When to Use This Skill

- When designing or writing data orchestration workflows (Airflow DAGs, Dagster software-defined assets, Prefect flows).
- When creating or refactoring dbt projects (`stg_`, `int_`, `fct_`, `dim_` models).
- When implementing incremental table materializations (`merge`, `append`, `delete+insert`) with lookback windows.
- When configuring data quality tests, schema validation, and freshness checks (dbt tests, Great Expectations, Soda Core).
- When diagnosing slow data transformations, warehouse spill-to-disk, or pipeline dependency deadlocks.
- Trigger phrases: `"create dbt model"`, `"author airflow dag"`, `"build ETL pipeline"`, `"data transformation job"`, `"orchestrate data pipeline"`, `"data quality tests"`, `"lineage tracking"`, `"prefect flow"`, `"dagster asset"`.

---

## The Modern Data Pipeline Lifecycle

```
┌────────────────────────────────────────────────────────────────────────┐
│               Modern ELT / Data Orchestration Lifecycle                │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. Ingestion & Raw Staging     │ 2. Dimensional Transformation (dbt)   │
│ (Airflow TaskFlow / CDC / S3)  │ (stg_ -> int_ -> fct_ / dim_ Marts)   │
├────────────────────────────────┼───────────────────────────────────────┤
│ 3. Incremental Materialization │ 4. Automated Quality Gates & Tests    │
│ (Unique Keys, Lookback Window) │ (Uniqueness, Referential, Freshness)  │
├────────────────────────────────┴───────────────────────────────────────┤
│ 5. Lineage Tracking & Slim CI (State-Modified Selective Builds)        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Pipeline Orchestration Standards (Airflow & Dagster)

### 1. Airflow 2.x TaskFlow API Best Practices
- **Never pass large datasets via XCom**: XCom is for metadata (record counts, batch IDs, S3 URIs), never raw dataframes.
- **Enforce Idempotency**: Running a DAG for execution date `T` must yield identical output regardless of how many times it is rerun.
- **Dynamic Task Mapping**: Use `.expand()` for fan-out processing rather than monolithic loops inside a single task.

```python
from datetime import datetime, timedelta
from airflow.decorators import dag, task

@dag(
    dag_id="orders_incremental_elt",
    schedule="0 2 * * *",  # Daily at 02:00 UTC
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "execution_timeout": timedelta(hours=1),
    },
    tags=["elt", "orders", "dbt"],
)
def orders_elt_pipeline():
    @task
    def check_source_freshness() -> bool:
        # Verify upstream CDC or raw landing tables are fresh
        return True

    @task
    def run_dbt_staging(is_fresh: bool):
        # Trigger dbt run --select tag:staging
        pass

    @task
    def run_dbt_marts():
        # Trigger dbt run --select tag:marts
        pass

    @task
    def run_data_quality_gates():
        # dbt test --select state:modified+
        pass

    fresh = check_source_freshness()
    stg = run_dbt_staging(fresh)
    marts = run_dbt_marts()
    dq = run_data_quality_gates()

    stg >> marts >> dq

pipeline = orders_elt_pipeline()
```

---

## Phase 2: dbt Dimensional Modeling & Star Schemas

Structure projects into strict semantic layers according to dbt best practices:

```
models/
├── staging/       # stg_<source>__<entities>.sql (1:1 with source tables, cleanup, casting)
├── intermediate/  # int_<entity>__<transformation>.sql (Complex business logic joins)
└── marts/         # fct_<process>.sql & dim_<entity>.sql (Star schema consumable by BI)
```

### 1. Staging Conventions (`stg_`)
- Rename raw columns to standard snake_case naming conventions (`id` -> `order_id`).
- Explicitly cast data types (`CAST(created_at AS TIMESTAMP)`).
- Strip whitespace, normalize status enums (`UPPER(TRIM(status))`).
- No joins across sources in the staging layer.

### 2. Marts & Kimball Dimensional Modeling (`fct_`, `dim_`)
- **Facts (`fct_`)**: Represent business verbs/events at a defined grain (e.g., `fct_orders`, `fct_daily_customer_metrics`). Contain foreign keys and measurable additive numeric values.
- **Dimensions (`dim_`)**: Represent business nouns/entities (e.g., `dim_customers`, `dim_products`). Include surrogate keys and descriptive attributes.

---

## Phase 3: High-Performance Incremental Models

For high-volume tables ($> 10^7$ rows), full refreshes are prohibitively slow and expensive. Implement dbt incremental materializations with lookback windows to safely capture late-arriving records:

```sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge',
    on_schema_change='sync_all_columns'
) }}

WITH source_data AS (
    SELECT * FROM {{ ref('stg_ecommerce__orders') }}
    {% if is_incremental() %}
        -- 3-day lookback window prevents dropped late-arriving events
        WHERE updated_at >= (
            SELECT DATEADD(day, -3, MAX(updated_at)) 
            FROM {{ this }}
        )
    {% endif %}
),

final AS (
    SELECT
        order_id,
        customer_id,
        order_status,
        order_amount_usd,
        created_at,
        updated_at
    FROM source_data
)

SELECT * FROM final
```

---

## Phase 4: Automated Data Quality Testing

Every production model must have automated test coverage before downstream exposure:

### 1. Core Schema Tests (`schema.yml`)
- **`unique`**: Primary keys and surrogate keys must never duplicate.
- **`not_null`**: Identifiers and critical metrics must not contain nulls.
- **`relationships`**: Foreign keys in facts must resolve to valid dimensions (`dim_customers.customer_id`).
- **`accepted_values`**: Categorical status fields must match finite sets (`['PENDING', 'COMPLETED', 'REFUNDED']`).

### 2. Custom SQL Assertion Tests (`tests/assert_positive_revenue.sql`)
```sql
-- Fails if any order produces negative net revenue
SELECT
    order_id,
    net_revenue_usd
FROM {{ ref('fct_orders') }}
WHERE net_revenue_usd < 0
```

---

## Anti-Patterns & Hard Guardrails

- 🚫 **Never run heavy compute on the orchestrator**: Airflow workers should only orchestrate, never parse millions of rows in memory. Push compute to Snowflake, BigQuery, ClickHouse, or DuckDB.
- 🚫 **Never omit a lookback buffer in incremental models**: Relying strictly on `updated_at > MAX(updated_at)` causes silent data loss from network retries and delayed CDC ingestion.
- 🚫 **Never reference raw tables directly in downstream marts**: All raw tables must pass through a staging model (`{{ ref('stg_...') }}`) to encapsulate schema changes.
- 🚫 **Never write non-idempotent insert jobs**: Direct `INSERT INTO` without unique key deduplication or partition overwriting leads to corrupted duplicate tables on task retry.

---

## Verification & CLI Tooling

Use the companion script [`data_pipeline_toolkit.py`](./scripts/data_pipeline_toolkit.py) to audit DAG dependencies, detect circular references, lint dbt models, and test incremental merge logic.

```bash
# Run self-test suite
python skills/database-and-data-engineering/data-pipeline-etl/scripts/data_pipeline_toolkit.py --test

# Lint a dbt model SQL file
python skills/database-and-data-engineering/data-pipeline-etl/scripts/data_pipeline_toolkit.py lint --file models/fct_orders.sql

# Test DAG topological dependency sort
python skills/database-and-data-engineering/data-pipeline-etl/scripts/data_pipeline_toolkit.py dag-sort --tasks ingest,stg,int,marts,test --deps "stg:ingest,int:stg,marts:int,test:marts"
```
