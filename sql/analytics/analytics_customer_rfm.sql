-- Analytics Model: Customer RFM (Recency, Frequency, Monetary) Segmentation
CREATE TABLE IF NOT EXISTS analytics_customer_rfm AS
WITH customer_metrics AS (
    SELECT
        customer_id,
        customer_name,
        customer_segment,
        country,
        first_order_date,
        latest_order_date,
        total_orders_count AS frequency,
        lifetime_value_usd AS monetary_value,
        -- Recency in days (difference from latest order in dataset)
        JULIANDAY((SELECT MAX(order_date) FROM fact_orders)) - JULIANDAY(latest_order_date) AS recency_days
    FROM dim_customers
)
SELECT
    customer_id,
    customer_name,
    customer_segment,
    country,
    first_order_date,
    latest_order_date,
    CAST(recency_days AS INTEGER) AS recency_days,
    frequency,
    ROUND(monetary_value, 2) AS monetary_value,
    -- RFM Segmentation Rules
    CASE
        WHEN frequency >= 8 AND monetary_value >= 1500 THEN 'Champions'
        WHEN frequency >= 5 AND monetary_value >= 800 THEN 'Loyal Customers'
        WHEN recency_days <= 45 AND frequency <= 2 THEN 'New Customers'
        WHEN recency_days > 120 AND frequency >= 3 THEN 'At Risk'
        ELSE 'Hibernating'
    END AS rfm_segment
FROM customer_metrics;
