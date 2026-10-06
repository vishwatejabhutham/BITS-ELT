import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as gg
import streamlit as st
from datetime import datetime

from pipeline.db_manager import get_db_connection, get_supabase_credentials
from pipeline.extract import extract_all_data
from pipeline.load import load_latest_raw_data
from pipeline.transform import execute_transformations
from pipeline.pipeline_runner import run_full_elt_pipeline

# Page Configuration
st.set_page_config(
    page_title="Supabase E-Commerce ELT Pipeline",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #f0f4f8;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #064e3b 0%, #0f172a 50%, #1e1b4b 100%);
        padding: 1.8rem 2rem;
        border-radius: 16px;
        border: 1px solid rgba(52, 211, 153, 0.2);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #34d399, #38bdf8, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 0.4rem 0;
    }
    
    .main-header p {
        color: #94a3b8;
        font-size: 1.05rem;
        margin: 0;
    }

    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.2rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(52, 211, 153, 0.15);
        border-color: rgba(52, 211, 153, 0.3);
    }
    .metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0.3rem 0;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #34d399;
    }

    .badge-supabase {
        background: rgba(52, 211, 153, 0.2);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.4);
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-local {
        background: rgba(251, 191, 36, 0.2);
        color: #fbbf24;
        border: 1px solid rgba(251, 191, 36, 0.4);
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .terminal-box {
        background-color: #030712;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 1rem;
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        color: #34d399;
        font-size: 0.9rem;
        line-height: 1.5;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to run query and get DataFrame
def fetch_df(query):
    conn, engine_type = get_db_connection()
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df, engine_type
    except Exception as e:
        conn.close()
        raise e

# Navigation Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/color/96/supabase.png", width=64)
    st.title("Supabase E-Commerce ELT")
    st.caption("Extract ➔ Load ➔ Transform in Supabase")
    st.markdown("---")
    
    page = st.radio(
        "Navigation Menu",
        [
            "🛒 E-Commerce & Customer Analytics",
            "⚡ Supabase Pipeline Control",
            "🔍 SQL Data Warehouse Explorer",
            "📐 Architecture & Lineage"
        ]
    )
    
    st.markdown("---")
    st.subheader("⚡ Supabase Connection")
    creds = get_supabase_credentials()
    
    if creds["is_configured"]:
        st.markdown("<span class='badge-supabase'>Connected to Supabase Postgres</span>", unsafe_allow_html=True)
    else:
        st.markdown("<span class='badge-local'>Local Engine (SQLite Fallback)</span>", unsafe_allow_html=True)
        st.caption("To connect live Supabase, enter connection URL below:")
        
    with st.expander("⚙️ Connection Settings"):
        sup_url_input = st.text_input("Supabase Project URL", value=creds["supabase_url"] or "", placeholder="https://xyzproject.supabase.co")
        sup_key_input = st.text_input("Supabase Anon/Service Key", value=creds["supabase_key"] or "", type="password", placeholder="eyJhbGciOi...")
        pg_url_input = st.text_input("Supabase Postgres URL (Optional)", value=creds["postgres_url"] or "", placeholder="postgresql://postgres:pass@db.ref.supabase.co:5432/postgres")
        
        if st.button("Save Supabase Credentials"):
            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
            with open(env_path, "w") as f:
                f.write(f"SUPABASE_URL={sup_url_input.strip()}\n")
                f.write(f"SUPABASE_KEY={sup_key_input.strip()}\n")
                if pg_url_input.strip():
                    f.write(f"POSTGRES_URL={pg_url_input.strip()}\n")
            st.success("Saved to .env! Refresh page.")

# App Header
st.markdown("""
<div class="main-header">
    <h1>⚡ Supabase E-Commerce ELT Pipeline & Dashboard</h1>
    <p>Automated Extraction, Direct Landing Storage in Supabase/Postgres, and SQL RFM Customer Analytics</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# PAGE 1: E-COMMERCE & CUSTOMER ANALYTICS
# ==========================================
if page == "🛒 E-Commerce & Customer Analytics":
    st.header("🛒 E-Commerce Sales & Customer RFM Analytics")
    
    try:
        fact_df, engine = fetch_df("SELECT * FROM fact_orders;")
        summary_df, _ = fetch_df("SELECT * FROM analytics_sales_summary;")
        rfm_df, _ = fetch_df("SELECT * FROM analytics_customer_rfm;")
        
        # Metric Cards Row
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        total_revenue = fact_df["net_item_total"].sum()
        total_orders = len(fact_df["order_id"].unique())
        avg_order_value = fact_df["total_order_amount"].mean() if not fact_df.empty else 0
        total_customers = len(rfm_df)
        
        with kpi1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Net Revenue</div>
                <div class="metric-value">${total_revenue:,.2f}</div>
                <div class="metric-sub">Processed in Database</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Completed Orders</div>
                <div class="metric-value">{total_orders:,}</div>
                <div class="metric-sub">{len(fact_df):,} Order Items</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Average Order Value (AOV)</div>
                <div class="metric-value">${avg_order_value:.2f}</div>
                <div class="metric-sub">Including Shipping</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Unique Active Customers</div>
                <div class="metric-value">{total_customers}</div>
                <div class="metric-sub">Segmented via RFM</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Interactive Charts Row 1: RFM Segmentation & Category Revenue
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.subheader("🎯 Customer RFM Segmentation Breakdown")
            rfm_counts = rfm_df["rfm_segment"].value_counts().reset_index()
            rfm_counts.columns = ["RFM Segment", "Customer Count"]
            
            fig_rfm = px.pie(
                rfm_counts,
                names="RFM Segment",
                values="Customer Count",
                hole=0.45,
                color="RFM Segment",
                color_discrete_map={
                    "Champions": "#10b981",
                    "Loyal Customers": "#38bdf8",
                    "New Customers": "#a78bfa",
                    "At Risk": "#f59e0b",
                    "Hibernating": "#ef4444"
                }
            )
            fig_rfm.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(15, 23, 42, 0.6)",
                plot_bgcolor="rgba(15, 23, 42, 0.6)",
                height=350
            )
            st.plotly_chart(fig_rfm, use_container_width=True)
            
        with c2:
            st.subheader("📦 Product Category Sales & Estimated Profit")
            cat_summary = summary_df.groupby("category")[["net_sales_usd", "total_estimated_profit_usd"]].sum().reset_index()
            
            fig_cat = px.bar(
                cat_summary,
                x="category",
                y=["net_sales_usd", "total_estimated_profit_usd"],
                barmode="group",
                labels={"value": "Amount ($)", "variable": "Metric"},
                color_discrete_sequence=["#34d399", "#38bdf8"]
            )
            fig_cat.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(15, 23, 42, 0.6)",
                plot_bgcolor="rgba(15, 23, 42, 0.6)",
                height=350
            )
            st.plotly_chart(fig_cat, use_container_width=True)
            
        # Interactive Row 2: Sales Over Time & Geographic Heatmap
        st.subheader("📈 Revenue Growth & Regional Performance")
        
        c3, c4 = st.columns([2, 1])
        
        with c3:
            fact_df["order_date"] = pd.to_datetime(fact_df["order_date"])
            daily_sales = fact_df.groupby("order_date")["net_item_total"].sum().reset_index()
            
            fig_trend = px.area(
                daily_sales,
                x="order_date",
                y="net_item_total",
                title="Daily Net Sales Revenue ($)",
                color_discrete_sequence=["#34d399"]
            )
            fig_trend.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(15, 23, 42, 0.6)",
                plot_bgcolor="rgba(15, 23, 42, 0.6)",
                height=320
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
        with c4:
            country_summary = summary_df.groupby("country")["net_sales_usd"].sum().reset_index()
            fig_country = px.bar(
                country_summary.sort_values(by="net_sales_usd", ascending=True),
                x="net_sales_usd",
                y="country",
                orientation="h",
                title="Sales by Country ($)",
                color_discrete_sequence=["#818cf8"]
            )
            fig_country.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(15, 23, 42, 0.6)",
                plot_bgcolor="rgba(15, 23, 42, 0.6)",
                height=320
            )
            st.plotly_chart(fig_country, use_container_width=True)
            
        # Table Preview
        st.subheader("📋 Top RFM Champions & High-Value Customers")
        st.dataframe(
            rfm_df.sort_values(by="monetary_value", ascending=False).head(20).style.format({
                "monetary_value": "${:,.2f}",
                "recency_days": "{:,} days",
                "frequency": "{:,} orders"
            }),
            use_container_width=True
        )
        
    except Exception as e:
        st.warning("⚠️ Database is empty. Go to **'⚡ Supabase Pipeline Control'** and click **Run Full Pipeline**.")


# ==========================================
# PAGE 2: PIPELINE CONTROL CENTER
# ==========================================
elif page == "⚡ Supabase Pipeline Control":
    st.header("⚡ Supabase ELT Pipeline Control Center")
    st.markdown("Trigger E-Commerce extraction, landing loading into Supabase/Postgres, and SQL analytics compilation.")
    
    col_ctrl, col_stats = st.columns([1, 1])
    
    with col_ctrl:
        st.subheader("🎛️ Execution Controls")
        
        order_count_input = st.slider("Number of Order Transactions", min_value=50, max_value=5000, value=500, step=50)
        days_input = st.slider("Timeframe (Days)", min_value=30, max_value=730, value=365, step=30)
        
        btn_full = st.button("🚀 Run Full ELT Pipeline (Extract + Load to Supabase + Transform)", type="primary", use_container_width=True)
        
        st.markdown("<hr style='margin: 1rem 0; border-color: #334155;'>", unsafe_allow_html=True)
        st.markdown("**Stage-by-Stage Control:**")
        
        c_e, c_l, c_t = st.columns(3)
        btn_extract = c_e.button("📥 1. Extract", use_container_width=True)
        btn_load = c_l.button("💾 2. Load", use_container_width=True)
        btn_transform = c_t.button("⚙️ 3. Transform", use_container_width=True)
        
    with col_stats:
        st.subheader("📊 Engine & Database Status")
        creds = get_supabase_credentials()
        st.markdown(f"**Supabase Configured:** `{'YES' if creds['is_configured'] else 'NO'}`")
        if creds['postgres_url']:
            st.markdown(f"**Target Host:** `{creds['postgres_url'].split('@')[-1] if '@' in creds['postgres_url'] else 'Supabase'}`")
            
        try:
            conn, engine_type = get_db_connection()
            st.markdown(f"**Active Database Engine:** `<span class='badge-supabase'>{engine_type}</span>`", unsafe_allow_html=True)
            cursor = conn.cursor()
            
            if engine_type == "POSTGRESQL":
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
            else:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                
            tables = [row[0] for row in cursor.fetchall()]
            st.markdown(f"**Total Tables Built:** `{len(tables)}` ({', '.join(tables)})")
            conn.close()
        except Exception as e:
            st.error(f"DB Error: {e}")
            
    st.markdown("---")
    st.subheader("💻 Execution Terminal Logs")
    
    log_container = st.empty()
    log_container.markdown("""
    <div class="terminal-box">
    [SYSTEM] Supabase ELT Engine initialized. Select an action button above.
    </div>
    """, unsafe_allow_html=True)
    
    if btn_full:
        with st.spinner("Running complete Supabase ELT pipeline..."):
            summary = run_full_elt_pipeline(order_count=order_count_input, days=days_input)
            
            formatted_logs = "<br>".join(summary["logs"])
            log_container.markdown(f"""
            <div class="terminal-box">
            {formatted_logs}
            </div>
            """, unsafe_allow_html=True)
            st.success(f"✅ Full ELT Pipeline executed successfully in {summary['total_duration_seconds']}s on {summary['engine']}!")
            
    elif btn_extract:
        with st.spinner("Extracting raw E-Commerce order transactions..."):
            res = extract_all_data(order_count=order_count_input, days=days_input)
            log_container.markdown(f"""
            <div class="terminal-box">
            [EXTRACT] Extracted {res['total_orders']} orders (${res['total_sales_usd']:,} USD).<br>
            [EXTRACT] Output File: {res['filename']}<br>
            [EXTRACT] Duration: {res['duration_seconds']}s
            </div>
            """, unsafe_allow_html=True)
            st.success(f"✅ Extraction complete: {res['total_orders']} raw JSON order items created!")
            
    elif btn_load:
        with st.spinner("Loading raw order data into Supabase/Postgres landing..."):
            try:
                res = load_latest_raw_data()
                log_container.markdown(f"""
                <div class="terminal-box">
                [LOAD] Source File: {res['filename']}<br>
                [LOAD] Target Table: {res['target_table']}<br>
                [LOAD] Engine: {res['engine']} | Rows Loaded: {res['rows_loaded']}<br>
                [LOAD] Duration: {res['duration_seconds']}s
                </div>
                """, unsafe_allow_html=True)
                st.success(f"✅ Load complete: {res['rows_loaded']} rows inserted into target landing table!")
            except Exception as e:
                st.error(f"Load failed: {e}")
                
    elif btn_transform:
        with st.spinner("Running SQL transformation models..."):
            try:
                res = execute_transformations()
                if res["status"] == "SUCCESS":
                    log_lines = [f"[TRANSFORM] Executing SQL models in database ({res['engine']}):"]
                    for m in res["models"]:
                        log_lines.append(f"  └─ Built [{m['layer']}] model '{m['model']}': {m['rows']} rows ({m['duration_seconds']}s)")
                    log_lines.append(f"[TRANSFORM] Total Duration: {res['total_duration_seconds']}s")
                    
                    log_container.markdown(f"""
                    <div class="terminal-box">
                    {"<br>".join(log_lines)}
                    </div>
                    """, unsafe_allow_html=True)
                    st.success(f"✅ Transformation complete: {res['total_models']} SQL models built!")
                else:
                    st.error(f"Transform failed: {res.get('error')}")
            except Exception as e:
                st.error(f"Transform failed: {e}")


# ==========================================
# PAGE 3: SQL DATA WAREHOUSE EXPLORER
# ==========================================
elif page == "🔍 SQL Data Warehouse Explorer":
    st.header("🔍 SQL Data Warehouse & Supabase Explorer")
    st.markdown("Browse tables, inspect column schemas, or execute raw SQL queries against your database engine.")
    
    try:
        conn, engine_type = get_db_connection()
        cursor = conn.cursor()
        
        if engine_type == "POSTGRESQL":
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        tab_browser, tab_query = st.tabs(["📂 Data Warehouse Models Browser", "⚡ Custom SQL Query Console"])
        
        with tab_browser:
            selected_table = st.selectbox("Select Table", tables)
            
            if selected_table:
                data_df, _ = fetch_df(f"SELECT * FROM {selected_table} LIMIT 100;")
                count_df, _ = fetch_df(f"SELECT COUNT(*) as total FROM {selected_table};")
                total_rows = count_df["total"].iloc[0]
                
                col_s1, col_s2 = st.columns([1, 2])
                with col_s1:
                    st.markdown(f"**Table:** `{selected_table}`")
                    st.markdown(f"**Total Rows:** `{total_rows:,}`")
                    st.markdown("**Columns:**")
                    st.write(list(data_df.columns))
                    
                with col_s2:
                    st.markdown("**Data Preview (Top 100 Rows):**")
                    st.dataframe(data_df, use_container_width=True)
                    
                    csv_bytes = data_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📥 Download {selected_table}.csv",
                        data=csv_bytes,
                        file_name=f"{selected_table}.csv",
                        mime="text/csv"
                    )
                    
        with tab_query:
            st.markdown("Execute SQL queries against database:")
            
            default_query = """-- Custom E-Commerce Analytics Query
SELECT 
    customer_segment,
    COUNT(DISTINCT customer_id) as total_customers,
    ROUND(SUM(lifetime_value_usd), 2) as total_segment_revenue,
    ROUND(AVG(lifetime_value_usd), 2) as avg_customer_ltv
FROM dim_customers
GROUP BY customer_segment
ORDER BY total_segment_revenue DESC;"""

            sql_input = st.text_area("SQL Query Editor", value=default_query, height=180)
            
            if st.button("▶️ Execute SQL Query", type="primary"):
                try:
                    q_start = datetime.now()
                    res_df, eng = fetch_df(sql_input)
                    q_duration = (datetime.now() - q_start).total_seconds()
                    
                    st.success(f"Query returned {len(res_df)} rows in {q_duration:.4f}s on {eng}!")
                    st.dataframe(res_df, use_container_width=True)
                except Exception as e:
                    st.error(f"SQL Error: {e}")
                    
    except Exception as e:
        st.error(f"Database error: {e}")


# ==========================================
# PAGE 4: ARCHITECTURE & LINEAGE
# ==========================================
elif page == "📐 Architecture & Lineage":
    st.header("📐 Supabase E-Commerce ELT Architecture")
    
    st.markdown("""
    ### Why Supabase for ELT Pipelines?
    **Supabase** provides an open-source **PostgreSQL** database environment with native REST, Realtime, and direct SQL execution engines.
    
    1. **Extract (E)**: Pull raw E-Commerce customer orders, product details, and items.
    2. **Load (L)**: Store raw JSON directly into Supabase PostgreSQL landing table `raw_orders_landing`.
    3. **Transform (T)**: Execute SQL transformations inside PostgreSQL/Supabase database engine (**Staging ➔ Warehouse Facts/Dims ➔ RFM Customer Analytics**).
    """)
    
    st.markdown("---")
    st.code("""
BITS-ELT/
├── app.py                         # Streamlit Dashboard & Web UI
├── pipeline/
│   ├── extract.py                 # E: Raw E-Commerce Orders Extractor
│   ├── load.py                    # L: Ingest Raw Payload into Supabase Landing Storage
│   ├── transform.py               # T: Execute SQL Models in Supabase / Postgres
│   ├── db_manager.py              # Supabase & SQLite Database Connector
│   └── pipeline_runner.py         # End-to-End Pipeline Orchestrator
├── sql/
│   ├── staging/
│   │   └── stg_raw_orders.sql     # Staging & Data Cleaning Model
│   ├── warehouse/
│   │   ├── dim_customers.sql      # Customer Dimension Model
│   │   ├── dim_products.sql       # Product Dimension Model
│   │   └── fact_orders.sql        # Transactional Orders Fact Model
│   └── analytics/
│       ├── analytics_customer_rfm.sql # Customer RFM Segmentation Model
│       └── analytics_sales_summary.sql # Sales Aggregation & AOV Model
├── data/
│   └── raw/                       # Raw JSON file landings
└── requirements.txt
""", language="text")
