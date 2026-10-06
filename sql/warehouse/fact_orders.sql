-- Fact Model: E-Commerce Transactional Orders Fact Table
CREATE TABLE IF NOT EXISTS fact_orders AS
SELECT
    order_id,
    order_date,
    customer_id,
    product_id,
    category,
    country,
    unit_price,
    quantity,
    discount_pct,
    gross_item_total,
    discount_amount,
    net_item_total,
    shipping_cost,
    total_order_amount,
    order_status,
    -- Estimated Net Profit (assuming ~45% COGS)
    ROUND((net_item_total * 0.55) - shipping_cost, 2) AS estimated_profit_usd
FROM stg_raw_orders;
