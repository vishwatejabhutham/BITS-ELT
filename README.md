# ⚡ Supabase E-Commerce ELT Pipeline & Streamlit Dashboard

A simple, production-grade **ELT (Extract, Load, Transform)** data pipeline built with **Python**, **Supabase / PostgreSQL**, and **Streamlit**.

This pipeline extracts raw E-Commerce customer order transactions, loads raw JSON payloads directly into **Supabase / PostgreSQL** landing storage (`raw_orders_landing`), executes **in-database SQL transformations** (Staging ➔ Warehouse Facts/Dims ➔ Customer RFM Analytics), and visualizes real-time metrics in a **Streamlit Dashboard**.

---

## 🌟 Key Architecture & Highlights

- **Modern ELT Pattern**: Raw order transactions are ingested into Supabase landing storage *first*, without altering fields. SQL transformations execute inside the Supabase/PostgreSQL query engine.
- **Supabase / PostgreSQL Connector**: Connects to live Supabase cloud PostgreSQL database or runs seamlessly in local Supabase-compatible database mode.
- **Layered SQL Transformations (dbt-style)**:
  - `staging/stg_raw_orders.sql`: Cleans raw order items, parses date fields, calculates item totals & discounts.
  - `warehouse/dim_customers.sql`: Customer dimension table (lifetime orders, first/latest order dates, segment, country).
  - `warehouse/dim_products.sql`: Product dimension table (category, unit price, units sold, revenue).
  - `warehouse/fact_orders.sql`: Transactional orders fact table (gross sales, net sales, estimated profit).
  - `analytics/analytics_customer_rfm.sql`: **RFM Segmentation (Recency, Frequency, Monetary)** dividing customers into segments (`Champions`, `Loyal Customers`, `At Risk`, `New Customers`, `Hibernating`).
  - `analytics/analytics_sales_summary.sql`: Sales aggregations by category & country (Net sales, AOV, Estimated profit, Return rate %).
- **Interactive Streamlit Dashboard**: E-Commerce sales analytics, RFM customer charts, pipeline execution controls, SQL editor, and database model browser.

---

## 📁 Repository Structure

```
BITS-ELT/
├── app.py                         # Streamlit Dashboard & Web UI
├── pipeline/
│   ├── extract.py                 # E: Extract raw E-Commerce order transactions
│   ├── load.py                    # L: Ingest raw payload into Supabase landing storage
│   ├── transform.py               # T: Execute SQL models inside Supabase/Postgres
│   ├── db_manager.py              # Supabase & PostgreSQL Connection Manager
│   └── pipeline_runner.py         # End-to-End Pipeline Orchestrator
├── sql/
│   ├── staging/
│   │   └── stg_raw_orders.sql     # Staging cleaning model
│   ├── warehouse/
│   │   ├── dim_customers.sql      # Customer dimension model
│   │   ├── dim_products.sql       # Product dimension model
│   │   └── fact_orders.sql        # Transactional orders fact table
│   └── analytics/
│       ├── analytics_customer_rfm.sql # Customer RFM Segmentation
│       └── analytics_sales_summary.sql # Category & Country sales aggregations
├── data/
│   └── raw/                       # Raw JSON payload landings
├── .env.example                   # Supabase environment variables template
└── requirements.txt
```

---

## 🚀 Quick Start Guide

### 1. Environment Setup

```bash
# Clone/Open directory
cd BITS-ELT

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies (including Supabase, psycopg2, sqlalchemy)
pip install -r requirements.txt
```

---

### 2. Configure Supabase Connection (Optional)

Copy `.env.example` to `.env` and set your Supabase PostgreSQL connection string:

```bash
cp .env.example .env
```

Edit `.env`:
```env
POSTGRES_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
```

*(If no Supabase credentials are provided, the pipeline automatically runs in local offline engine mode so you can test immediately!)*

---

### 3. Run Pipeline from CLI

```bash
source venv/bin/activate
python3 -m pipeline.pipeline_runner
```

Output:
```text
[08:07:56] Starting E-Commerce ELT Pipeline Execution...
[08:07:56] Step 1/3: Extracting raw E-Commerce orders (500 transactions)...
[08:07:56] Extract Complete: 500 orders written to raw_ecommerce_orders_*.json
[08:07:56] Step 2/3: Loading raw data into Supabase/Postgres target database...
[08:07:56] Load Complete: 500 rows inserted into 'raw_orders_landing'
[08:07:56] Step 3/3: Running SQL Transformations inside Supabase database engine...
[08:07:56] Transform Complete: 6 SQL models built in 0.006s.
  └─ Model [staging] stg_raw_orders.sql: 500 rows
  └─ Model [warehouse] dim_customers.sql: 74 rows
  └─ Model [warehouse] dim_products.sql: 16 rows
  └─ Model [warehouse] fact_orders.sql: 500 rows
  └─ Model [analytics] analytics_customer_rfm.sql: 74 rows
  └─ Model [analytics] analytics_sales_summary.sql: 32 rows
[08:07:56] E-Commerce ELT Pipeline Execution finished in 0.019 seconds.
```

---

### 4. Launch Streamlit Dashboard

```bash
source venv/bin/activate
streamlit run app.py
```

Access the dashboard at **`http://localhost:8501`**.

---

## 📊 Dashboard Features

1. **🛒 E-Commerce & Customer Analytics**: Total Revenue, Completed Orders, Average Order Value (AOV), Customer RFM Segmentation distribution (Champions, Loyal, At Risk), Category Sales & Estimated Profit breakdown.
2. **⚡ Supabase Pipeline Control**: Trigger Extract, Load, or Transform stages individually or run the full pipeline on demand with real-time execution logs.
3. **🔍 SQL Data Warehouse Explorer**: Inspect Supabase/Postgres table schemas, browse live model data, run custom SQL queries, and download dataset CSVs.
4. **📐 Architecture & Lineage**: Visual graph and detailed explanation of the Supabase ELT architecture.
