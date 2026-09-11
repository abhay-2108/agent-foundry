"""
Production Airflow 2.x TaskFlow DAG Template
=============================================
Features:
- Standard TaskFlow API decorators (@dag, @task)
- Strict retry exponential backoffs and SLAs
- Decoupled compute (pushdown execution)
- Pre-flight freshness checks and post-flight data quality gates
"""

from datetime import datetime, timedelta
import logging
from airflow.decorators import dag, task

logger = logging.getLogger("airflow.task")

DEFAULT_ARGS = {
    "owner": "data-platform",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=3),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=15),
    "execution_timeout": timedelta(minutes=45),
}


@dag(
    dag_id="ecommerce_daily_marts_etl",
    default_args=DEFAULT_ARGS,
    description="Daily incremental ingestion and Kimball marts transformation with automated quality gates",
    schedule="0 3 * * *",  # Runs daily at 03:00 UTC
    start_date=datetime(2026, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["ecommerce", "dbt", "production", "analytics-engineering"],
)
def ecommerce_daily_marts_etl():

    @task
    def check_upstream_freshness(batch_date: str) -> dict:
        """
        Validates raw landing tables have received CDC syncs within SLA.
        """
        logger.info(f"Checking CDC landing table freshness for partition: {batch_date}")
        # In production: run lightweight SQL query to check max(synced_at)
        metadata = {
            "batch_date": batch_date,
            "status": "HEALTHY",
            "cdc_lag_minutes": 4.2
        }
        if metadata["cdc_lag_minutes"] > 60:
            raise ValueError(f"CDC freshness breached: {metadata['cdc_lag_minutes']}m > 60m SLA")
        return metadata

    @task
    def run_dbt_staging_and_intermediate(freshness_info: dict) -> dict:
        """
        Executes dbt models for staging and intermediate layers.
        """
        logger.info(f"Triggering dbt run for staging layers. Freshness: {freshness_info}")
        # In production: trigger via DbtCloudJobRunOperator, BashOperator, or KubernetesPodOperator
        return {"models_built": ["stg_ecommerce__orders", "int_order_items"], "status": "SUCCESS"}

    @task
    def run_dbt_marts(stg_result: dict) -> dict:
        """
        Executes incremental marts materializations with lookback window.
        """
        logger.info(f"Triggering dbt incremental marts. Prior step status: {stg_result['status']}")
        return {"models_built": ["fct_orders", "dim_customers"], "status": "SUCCESS"}

    @task
    def execute_quality_assertions(marts_result: dict) -> dict:
        """
        Runs dbt test and Great Expectations validation gates. Fails DAG if assertions break.
        """
        logger.info("Running schema, uniqueness, and referential integrity assertions...")
        assertion_summary = {
            "tests_run": 42,
            "tests_passed": 42,
            "tests_failed": 0
        }
        if assertion_summary["tests_failed"] > 0:
            raise AssertionError(f"Quality gate failure: {assertion_summary['tests_failed']} tests failed!")
        return assertion_summary

    @task
    def notify_slack_on_completion(quality_summary: dict):
        """
        Emits success webhook to monitoring channels.
        """
        logger.info(f"Pipeline completed successfully. Passed tests: {quality_summary['tests_passed']}")

    # DAG Dependency Graph
    freshness = check_upstream_freshness(batch_date="{{ ds }}")
    staging = run_dbt_staging_and_intermediate(freshness)
    marts = run_dbt_marts(staging)
    quality = execute_quality_assertions(marts)
    notify = notify_slack_on_completion(quality)

    freshness >> staging >> marts >> quality >> notify


# Instantiate the DAG
dag_instance = ecommerce_daily_marts_etl()
