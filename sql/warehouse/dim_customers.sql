-- Dimension Model: E-Commerce Customers Catalog
CREATE TABLE IF NOT EXISTS dim_customers AS
SELECT
    customer_id,
    customer_name,
    customer_segment,
    country,
    MIN(order_date) AS first_order_date,
    MAX(order_date) AS latest_order_date,
    COUNT(DISTINCT order_id) AS total_orders_count,
    ROUND(SUM(total_order_amount), 2) AS lifetime_value_usd
FROM stg_raw_orders
GROUP BY customer_id, customer_name, customer_segment, country;
