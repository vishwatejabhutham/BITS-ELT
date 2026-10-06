-- ============================================================
-- SUPABASE CLOUD DATABASE SCHEMA SETUP
-- Paste and Run this script in your Supabase SQL Editor:
-- https://supabase.com/dashboard/project/bntwuoqenwmvtqosmijo/sql/new
-- ============================================================

-- 1. Raw Landing Table
CREATE TABLE IF NOT EXISTS public.raw_orders_landing (
    order_id VARCHAR(50),
    order_date VARCHAR(20),
    customer_id VARCHAR(50),
    customer_name VARCHAR(100),
    customer_segment VARCHAR(50),
    country VARCHAR(50),
    product_id VARCHAR(50),
    product_name VARCHAR(150),
    category VARCHAR(50),
    unit_price REAL,
    quantity INTEGER,
    discount_pct REAL,
    gross_item_total REAL,
    discount_amount REAL,
    net_item_total REAL,
    shipping_cost REAL,
    total_order_amount REAL,
    order_status VARCHAR(50),
    extracted_at VARCHAR(50),
    loaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enable Row Level Security and allow API access
ALTER TABLE public.raw_orders_landing ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow full access raw_orders_landing" ON public.raw_orders_landing;
CREATE POLICY "Allow full access raw_orders_landing" ON public.raw_orders_landing FOR ALL USING (true) WITH CHECK (true);

-- Grant permissions to anon and service_role
GRANT ALL ON public.raw_orders_landing TO anon, service_role, postgres;
