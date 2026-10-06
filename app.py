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
    page_title="BITS Enterprise Data Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Corporate Dark Theme Styling
st.markdown("""
<style>
    /* Global Reset & Dark Palette */
    .stApp {
        background-color: #090d16;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Hide Default Streamlit Branding Elements for Official Look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Header Gradient Banner */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
        padding: 1.6rem 2rem;
        border-radius: 14px;
        border: 1px solid #334155;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.6);
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        font-size: 2rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #f8fafc;
        margin: 0 0 0.3rem 0;
    }
    
    .main-header p {
        color: #94a3b8;
        font-size: 0.98rem;
        margin: 0;
    }

    /* Executive KPI Cards */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.25rem 1.4rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #38bdf8;
    }
    .metric-label {
        font-size: 0.8rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0.3rem 0;
        letter-spacing: -0.02em;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #38bdf8;
        font-weight: 500;
    }

    /* Status Badges */
    .badge-active {
        background: rgba(56, 189, 248, 0.12);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    
    /* Terminal Console Box */
    .terminal-box {
        background-color: #020617;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 1.2rem;
        font-family: "JetBrains Mono", "Fira Code", Monaco, monospace;
        color: #38bdf8;
        font-size: 0.88rem;
        line-height: 1.6;
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
    st.markdown("### 📊 Enterprise Data Platform")
    st.caption("E-Commerce Data Pipeline & Analytics Engine")
    st.markdown("---")
    
    page = st.radio(
        "Platform Navigation",
        [
            "📊 Executive Overview & Analytics",
            "⚡ Data Pipeline Orchestrator",
            "🔍 Data Warehouse Console",
            "📐 System Lineage & Architecture"
        ]
    )
    
    st.markdown("---")
    creds = get_supabase_credentials()
    engine_label = "Cloud Database" if creds["is_configured"] else "Local Engine"
    st.markdown(f"**Database:** `<span class='badge-active'>{engine_label}</span>`", unsafe_allow_html=True)
    
    with st.expander("⚙️ Connection Settings"):
        sup_url_input = st.text_input("Supabase Project URL", value=creds["supabase_url"] or "", placeholder="https://xyzproject.supabase.co")
        sup_key_input = st.text_input("Supabase Secret Key", value=creds["supabase_key"] or "", type="password", placeholder="sb_secret_...")
        pg_url_input = st.text_input("Postgres URL (Optional)", value=creds["postgres_url"] or "", placeholder="postgresql://...")
        
        if st.button("Save Credentials"):
            env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
            with open(env_path, "w") as f:
                f.write(f"SUPABASE_URL={sup_url_input.strip()}\n")
                f.write(f"SUPABASE_KEY={sup_key_input.strip()}\n")
                if pg_url_input.strip():
                    f.write(f"POSTGRES_URL={pg_url_input.strip()}\n")
            st.success("Credentials saved to .env!")

# Official Executive Header
st.markdown("""
<div class="main-header">
    <h1>BITS Enterprise Data Pipeline & Analytics Platform</h1>
    <p>Automated Data Extraction, Landing Lake Storage, and In-Database Analytics Modeling</p>
</div>
""", unsafe_allow_html=True)


# ==========================================
# PAGE 1: EXECUTIVE OVERVIEW & ANALYTICS
# ==========================================
if page == "📊 Executive Overview & Analytics":
    st.subheader("📊 Sales Performance & Customer RFM Intelligence")
    
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
                <div class="metric-label">Net Sales Revenue</div>
                <div class="metric-value">${total_revenue:,.2f}</div>
                <div class="metric-sub">Processed in Warehouse</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Completed Transactions</div>
                <div class="metric-value">{total_orders:,}</div>
                <div class="metric-sub">{len(fact_df):,} Total Items</div>
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
                <div class="metric-label">Active Customer Base</div>
                <div class="metric-value">{total_customers}</div>
                <div class="metric-sub">Segmented via RFM</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Row 1: RFM Segmentation & Category Revenue
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.markdown("##### 🎯 Customer RFM Segmentation Distribution")
            rfm_counts = rfm_df["rfm_segment"].value_counts().reset_index()
            rfm_counts.columns = ["RFM Segment", "Customer Count"]
            
            fig_rfm = px.pie(
                rfm_counts,
                names="RFM Segment",
                values="Customer Count",
                hole=0.5,
                color="RFM Segment",
                color_discrete_map={
                    "Champions": "#10b981",
                    "Loyal Customers": "#38bdf8",
                    "New Customers": "#818cf8",
                    "At Risk": "#f59e0b",
                    "Hibernating": "#ef4444"
                }
            )
            fig_rfm.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(15, 23, 42, 0.4)",
                plot_bgcolor="rgba(15, 23, 42, 0.4)",
                height=340,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_rfm, width="stretch")
            
        with c2:
            st.markdown("##### 📦 Category Revenue & Net Profit Margins")
            cat_summary = summary_df.groupby("category")[["net_sales_usd", "total_estimated_profit_usd"]].sum().reset_index()
            
            fig_cat = px.bar(
                cat_summary,
                x="category",
                y=["net_sales_usd", "total_estimated_profit_usd"],
                barmode="group",
                labels={"value": "Amount ($)", "variable": "Metric", "category": "Product Category"},
                color_discrete_sequence=["#38bdf8", "#10b981"]
            )
            fig_cat.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(15, 23, 42, 0.4)",
                plot_bgcolor="rgba(15, 23, 42, 0.4)",
                height=340,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_cat, width="stretch")
            
        # Row 2: Sales Over Time & Geographic Heatmap
        c3, c4 = st.columns([2, 1])
        
        with c3:
            st.markdown("##### 📈 Daily Revenue Growth Trajectory")
            fact_df["order_date"] = pd.to_datetime(fact_df["order_date"])
            daily_sales = fact_df.groupby("order_date")["net_item_total"].sum().reset_index()
            
            fig_trend = px.area(
                daily_sales,
                x="order_date",
                y="net_item_total",
                labels={"net_item_total": "Sales Revenue ($)", "order_date": "Date"},
                color_discrete_sequence=["#38bdf8"]
            )
            fig_trend.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(15, 23, 42, 0.4)",
                plot_bgcolor="rgba(15, 23, 42, 0.4)",
                height=320,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_trend, width="stretch")
            
        with c4:
            st.markdown("##### 🌍 Sales Volume by Country")
            country_summary = summary_df.groupby("country")["net_sales_usd"].sum().reset_index()
            fig_country = px.bar(
                country_summary.sort_values(by="net_sales_usd", ascending=True),
                x="net_sales_usd",
                y="country",
                orientation="h",
                labels={"net_sales_usd": "Net Sales ($)", "country": "Country"},
                color_discrete_sequence=["#818cf8"]
            )
            fig_country.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(15, 23, 42, 0.4)",
                plot_bgcolor="rgba(15, 23, 42, 0.4)",
                height=320,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_country, width="stretch")
            
        # High-Value Customers Data Table
        st.markdown("##### 📋 Customer Lifetime Value (LTV) Matrix")
        st.dataframe(
            rfm_df.sort_values(by="monetary_value", ascending=False).head(20).style.format({
                "monetary_value": "${:,.2f}",
                "recency_days": "{:,} days",
                "frequency": "{:,} orders"
            }),
            width="stretch"
        )
        
    except Exception as e:
        st.warning("⚠️ Warehouse database is unpopulated. Please go to **'⚡ Data Pipeline Orchestrator'** and click **Run Pipeline**.")


# ==========================================
# PAGE 2: DATA PIPELINE ORCHESTRATOR
# ==========================================
elif page == "⚡ Data Pipeline Orchestrator":
    st.subheader("⚡ ELT Pipeline Execution & Task Management")
    st.markdown("Orchestrate raw data extraction, landing lake loading, and in-database transformation models.")
    
    col_ctrl, col_stats = st.columns([1, 1])
    
    with col_ctrl:
        st.markdown("##### 🎛️ Execution Controls")
        
        order_count_input = st.slider("Order Transactions Volume", min_value=50, max_value=5000, value=500, step=50)
        days_input = st.slider("Timeframe Span (Days)", min_value=30, max_value=730, value=365, step=30)
        
        btn_full = st.button("🚀 Trigger Full ELT Execution Pipeline", type="primary", width="stretch")
        
        st.markdown("<hr style='margin: 1rem 0; border-color: #334155;'>", unsafe_allow_html=True)
        st.markdown("**Stage-by-Stage Execution:**")
        
        c_e, c_l, c_t = st.columns(3)
        btn_extract = c_e.button("📥 1. Extract", width="stretch")
        btn_load = c_l.button("💾 2. Load", width="stretch")
        btn_transform = c_t.button("⚙️ 3. Transform", width="stretch")
        
    with col_stats:
        st.markdown("##### 📊 Storage & Infrastructure Metrics")
        creds = get_supabase_credentials()
        st.markdown(f"**Target Engine:** `{'Supabase Cloud Database' if creds['is_configured'] else 'Local SQLite Engine'}`")
        
        try:
            conn, engine_type = get_db_connection()
            cursor = conn.cursor()
            
            if engine_type == "POSTGRESQL":
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
            else:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                
            tables = [row[0] for row in cursor.fetchall()]
            st.markdown(f"**Built Models Count:** `{len(tables)}` tables")
            st.markdown(f"**Active Tables:** `{', '.join(tables)}`")
            conn.close()
        except Exception as e:
            st.error(f"DB Metric Error: {e}")
            
    st.markdown("---")
    st.markdown("##### 💻 Real-Time Pipeline Terminal Logs")
    
    log_container = st.empty()
    log_container.markdown("""
    <div class="terminal-box">
    [SYSTEM] Data Pipeline Orchestrator Idle. Ready for command input.
    </div>
    """, unsafe_allow_html=True)
    
    if btn_full:
        with st.spinner("Executing full data pipeline..."):
            summary = run_full_elt_pipeline(order_count=order_count_input, days=days_input)
            formatted_logs = "<br>".join(summary["logs"])
            log_container.markdown(f"""
            <div class="terminal-box">
            {formatted_logs}
            </div>
            """, unsafe_allow_html=True)
            st.success(f"✅ Pipeline executed successfully in {summary['total_duration_seconds']}s!")
            
    elif btn_extract:
        with st.spinner("Extracting raw order transactions..."):
            res = extract_all_data(order_count=order_count_input, days=days_input)
            log_container.markdown(f"""
            <div class="terminal-box">
            [EXTRACT] Extracted {res['total_orders']} raw order items (${res['total_sales_usd']:,} USD).<br>
            [EXTRACT] Output File: {res['filename']}<br>
            [EXTRACT] Duration: {res['duration_seconds']}s
            </div>
            """, unsafe_allow_html=True)
            st.success("✅ Extraction phase completed!")
            
    elif btn_load:
        with st.spinner("Loading raw data into database..."):
            try:
                res = load_latest_raw_data()
                log_container.markdown(f"""
                <div class="terminal-box">
                [LOAD] Source File: {res['filename']}<br>
                [LOAD] Target Table: {res['target_table']}<br>
                [LOAD] Engine: {res['engine']} | Rows Ingested: {res['rows_loaded']}<br>
                [LOAD] Duration: {res['duration_seconds']}s
                </div>
                """, unsafe_allow_html=True)
                st.success("✅ Load phase completed!")
            except Exception as e:
                st.error(f"Load Error: {e}")
                
    elif btn_transform:
        with st.spinner("Executing SQL transformation models..."):
            try:
                res = execute_transformations()
                if res["status"] == "SUCCESS":
                    log_lines = [f"[TRANSFORM] Executed SQL models in database ({res['engine']}):"]
                    for m in res["models"]:
                        log_lines.append(f"  └─ Built [{m['layer']}] table '{m['model']}': {m['rows']} rows ({m['duration_seconds']}s)")
                    log_lines.append(f"[TRANSFORM] Total Duration: {res['total_duration_seconds']}s")
                    
                    log_container.markdown(f"""
                    <div class="terminal-box">
                    {"<br>".join(log_lines)}
                    </div>
                    """, unsafe_allow_html=True)
                    st.success("✅ Transformation phase completed!")
                else:
                    st.error(f"Transform Error: {res.get('error')}")
            except Exception as e:
                st.error(f"Transform Error: {e}")


# ==========================================
# PAGE 3: DATA WAREHOUSE CONSOLE
# ==========================================
elif page == "🔍 Data Warehouse Console":
    st.subheader("🔍 Data Warehouse Explorer & SQL Console")
    st.markdown("Inspect database schemas, browse transformed models, or execute raw SQL analytical queries.")
    
    try:
        conn, engine_type = get_db_connection()
        cursor = conn.cursor()
        
        if engine_type == "POSTGRESQL":
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        tab_browser, tab_query = st.tabs(["📂 Warehouse Model Browser", "⚡ Custom SQL Query Runner"])
        
        with tab_browser:
            selected_table = st.selectbox("Select Model Table", tables)
            
            if selected_table:
                data_df, _ = fetch_df(f"SELECT * FROM {selected_table} LIMIT 100;")
                count_df, _ = fetch_df(f"SELECT COUNT(*) as total FROM {selected_table};")
                total_rows = count_df["total"].iloc[0]
                
                col_s1, col_s2 = st.columns([1, 2])
                with col_s1:
                    st.markdown(f"**Model Table:** `{selected_table}`")
                    st.markdown(f"**Total Record Count:** `{total_rows:,}` rows")
                    st.markdown("**Columns:**")
                    st.write(list(data_df.columns))
                    
                with col_s2:
                    st.markdown("**Data Preview (First 100 Rows):**")
                    st.dataframe(data_df, width="stretch")
                    
                    csv_bytes = data_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📥 Download {selected_table}.csv",
                        data=csv_bytes,
                        file_name=f"{selected_table}.csv",
                        mime="text/csv"
                    )
                    
        with tab_query:
            st.markdown("Execute custom SQL queries against the database:")
            
            default_query = """-- Customer Segment Performance Analysis Query
SELECT 
    customer_segment,
    COUNT(DISTINCT customer_id) as total_customers,
    ROUND(SUM(lifetime_value_usd), 2) as total_segment_sales,
    ROUND(AVG(lifetime_value_usd), 2) as avg_customer_value
FROM dim_customers
GROUP BY customer_segment
ORDER BY total_segment_sales DESC;"""

            sql_input = st.text_area("SQL Query Editor", value=default_query, height=180)
            
            if st.button("▶️ Run SQL Query", type="primary"):
                try:
                    q_start = datetime.now()
                    res_df, eng = fetch_df(sql_input)
                    q_duration = (datetime.now() - q_start).total_seconds()
                    
                    st.success(f"Query returned {len(res_df)} rows in {q_duration:.4f}s on {eng}!")
                    st.dataframe(res_df, width="stretch")
                except Exception as e:
                    st.error(f"SQL Execution Error: {e}")
                    
    except Exception as e:
        st.error(f"Warehouse database connection error: {e}")


# ==========================================
# PAGE 4: SYSTEM LINEAGE & ARCHITECTURE
# ==========================================
elif page == "📐 System Lineage & Architecture":
    st.subheader("📐 System Architecture & Data Model Lineage")
    
    st.markdown("""
    ### Enterprise ELT Architecture Principles
    
    This platform separates data pipeline execution into **Extract**, **Load**, and **Transform**:
    
    1. **Extract (E)**: Pull raw E-Commerce order payload JSON without modification.
    2. **Load (L)**: Bulk insert raw payload into target lake storage `raw_orders_landing`.
    3. **Transform (T)**: Execute SQL transformations inside the target database (**Staging ➔ Warehouse Facts/Dims ➔ RFM Customer Analytics**).
    """)
    
    st.markdown("---")
    st.code("""
BITS-ELT Architecture Map:

  [Source API / Generator]
            │
            ▼ (Extract)
  [data/raw/raw_ecommerce_orders_*.json]
            │
            ▼ (Load)
  [Landing Lake Table: raw_orders_landing]
            │
            ▼ (Transform SQL Models)
   ├── staging/stg_raw_orders.sql
   ├── warehouse/dim_customers.sql
   ├── warehouse/dim_products.sql
   ├── warehouse/fact_orders.sql
   ├── analytics/analytics_customer_rfm.sql
   └── analytics/analytics_sales_summary.sql
            │
            ▼ (Consumption Layer)
  [Streamlit Enterprise Web Dashboard]
""", language="text")
