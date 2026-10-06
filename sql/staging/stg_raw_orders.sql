-- Staging Model: Clean and parse raw E-Commerce order transactions
CREATE TABLE IF NOT EXISTS stg_raw_orders AS
SELECT
    TRIM(order_id) AS order_id,
    DATE(order_date) AS order_date,
    TRIM(customer_id) AS customer_id,
    TRIM(customer_name) AS customer_name,
    TRIM(customer_segment) AS customer_segment,
    TRIM(country) AS country,
    TRIM(product_id) AS product_id,
    TRIM(product_name) AS product_name,
    TRIM(category) AS category,
    CAST(unit_price AS REAL) AS unit_price,
    CAST(quantity AS INTEGER) AS quantity,
    CAST(discount_pct AS REAL) AS discount_pct,
    CAST(gross_item_total AS REAL) AS gross_item_total,
    CAST(discount_amount AS REAL) AS discount_amount,
    CAST(net_item_total AS REAL) AS net_item_total,
    CAST(shipping_cost AS REAL) AS shipping_cost,
    CAST(total_order_amount AS REAL) AS total_order_amount,
    TRIM(order_status) AS order_status,
    CAST(extracted_at AS TIMESTAMP) AS extracted_at
FROM raw_orders_landing
WHERE order_id IS NOT NULL 
  AND customer_id IS NOT NULL;
