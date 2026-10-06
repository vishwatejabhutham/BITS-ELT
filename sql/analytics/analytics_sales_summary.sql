-- Analytics Model: Sales Performance Aggregations by Category & Country
CREATE TABLE IF NOT EXISTS analytics_sales_summary AS
SELECT
    category,
    country,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(gross_item_total), 2) AS gross_sales_usd,
    ROUND(SUM(discount_amount), 2) AS total_discounts_usd,
    ROUND(SUM(net_item_total), 2) AS net_sales_usd,
    ROUND(AVG(total_order_amount), 2) AS average_order_value_usd,
    ROUND(SUM(estimated_profit_usd), 2) AS total_estimated_profit_usd,
    ROUND((COUNT(CASE WHEN order_status = 'Returned' THEN 1 END) * 100.0) / COUNT(*), 2) AS return_rate_pct
FROM fact_orders
GROUP BY category, country;
