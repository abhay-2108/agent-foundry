-- ============================================================================
-- Template 1: Staging Model (models/staging/ecommerce/stg_ecommerce__orders.sql)
-- Grain: One record per raw ecommerce order
-- ============================================================================

{{ config(
    materialized='view',
    tags=['staging', 'ecommerce']
) }}

WITH source AS (
    SELECT * FROM {{ source('raw_ecommerce', 'orders') }}
),

renamed_and_cast AS (
    SELECT
        -- Identifiers
        CAST(id AS VARCHAR(64)) AS order_id,
        CAST(user_id AS VARCHAR(64)) AS customer_id,
        CAST(store_id AS VARCHAR(64)) AS store_id,

        -- Attributes & Status Normalization
        UPPER(TRIM(order_status)) AS order_status,
        LOWER(TRIM(payment_method)) AS payment_method,

        -- Financial Amounts (Converted to Cents/USD numeric)
        CAST(subtotal_cents AS NUMERIC(18, 2)) / 100.0 AS subtotal_usd,
        CAST(tax_cents AS NUMERIC(18, 2)) / 100.0 AS tax_usd,
        CAST(discount_cents AS NUMERIC(18, 2)) / 100.0 AS discount_usd,
        CAST(total_cents AS NUMERIC(18, 2)) / 100.0 AS total_amount_usd,

        -- Timestamps
        CAST(ordered_at AS TIMESTAMP_NTZ) AS ordered_at,
        CAST(updated_at AS TIMESTAMP_NTZ) AS updated_at

    FROM source
)

SELECT * FROM renamed_and_cast;


-- ============================================================================
-- Template 2: Marts Fact Table (models/marts/fct_orders.sql)
-- Grain: One record per order, incremental merge with lookback buffer
-- ============================================================================

{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge',
    on_schema_change='sync_all_columns',
    tags=['marts', 'core', 'financials']
) }}

WITH orders AS (
    SELECT * FROM {{ ref('stg_ecommerce__orders') }}
    {% if is_incremental() %}
        -- 3-day safety lookback buffer prevents dropping late-arriving event replays
        WHERE updated_at >= (
            SELECT DATEADD('day', -3, MAX(updated_at)) 
            FROM {{ this }}
        )
    {% endif %}
),

customers AS (
    SELECT customer_id, customer_segment, country_code 
    FROM {{ ref('dim_customers') }}
),

final AS (
    SELECT
        -- Primary Key
        o.order_id,

        -- Foreign Keys
        o.customer_id,
        o.store_id,

        -- Degenerate Dimensions
        o.order_status,
        o.payment_method,
        c.customer_segment,
        c.country_code,

        -- Financial Measures
        o.subtotal_usd,
        o.tax_usd,
        o.discount_usd,
        o.total_amount_usd,
        (o.total_amount_usd - o.discount_usd) AS net_revenue_usd,

        -- Timestamps & Lineage
        o.ordered_at,
        o.updated_at,
        CURRENT_TIMESTAMP() AS dbt_loaded_at

    FROM orders o
    LEFT JOIN customers c ON o.customer_id = c.customer_id
)

SELECT * FROM final;
