-- Dimension Model: Product Catalog Performance
CREATE TABLE IF NOT EXISTS dim_products AS
SELECT
    product_id,
    product_name,
    category,
    ROUND(AVG(unit_price), 2) AS catalog_unit_price,
    SUM(quantity) AS total_units_sold,
    COUNT(DISTINCT order_id) AS total_orders_featured,
    ROUND(SUM(net_item_total), 2) AS total_gross_revenue_usd
FROM stg_raw_orders
GROUP BY product_id, product_name, category;
