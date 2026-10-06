"""
Pipeline Orchestrator Module (E-Commerce & Supabase)
Runs full end-to-end ELT pipeline: Extract -> Load to Supabase -> Transform in Supabase
Includes interactive next step prompts for CLI execution.
"""

import time
import json
from datetime import datetime
from pipeline.extract import extract_all_data
from pipeline.load import load_latest_raw_data
from pipeline.transform import execute_transformations

def run_full_elt_pipeline(order_count=500, days=365):
    """
    Runs complete E-Commerce ELT execution flow to Supabase/Postgres.
    """
    pipeline_start = time.time()
    logs = []
    
    print("\n" + "="*60)
    print(" 🚀 SUPABASE E-COMMERCE ELT PIPELINE ORCHESTRATOR")
    print("="*60)
    print(f" Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(" Workflow  : Extract ➔ Load to Supabase/Postgres ➔ SQL Transform")
    print("="*60)
    
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Starting E-Commerce ELT Pipeline Execution...")
    
    # 1. Extract
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Step 1/3: Extracting raw E-Commerce orders ({order_count} transactions)...")
    extract_res = extract_all_data(order_count=order_count, days=days)
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Extract Complete: {extract_res['total_orders']} orders (${extract_res['total_sales_usd']:,} USD) written to {extract_res['filename']} in {extract_res['duration_seconds']}s.")
    
    # 2. Load
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Step 2/3: Loading raw data into Supabase/Postgres target database...")
    load_res = load_latest_raw_data(extract_res['output_file'])
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Load Complete: {load_res['rows_loaded']} rows inserted into '{load_res['target_table']}' (Engine: {load_res['engine']}) in {load_res['duration_seconds']}s.")
    
    # 3. Transform
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Step 3/3: Running SQL Transformations inside Supabase database engine...")
    transform_res = execute_transformations()
    if transform_res["status"] == "SUCCESS":
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Transform Complete: {transform_res['total_models']} SQL models built in {transform_res['total_duration_seconds']}s.")
        for m in transform_res["models"]:
            logs.append(f"  └─ Model [{m['layer']}] {m['model']}.sql: {m['rows']} rows ({m['duration_seconds']}s)")
    else:
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Transform FAILED: {transform_res.get('error')}")
        
    total_time = round(time.time() - pipeline_start, 3)
    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] E-Commerce ELT Pipeline Execution finished in {total_time} seconds.")
    
    print("\n" + "="*60)
    print(" 🎉 PIPELINE EXECUTION SUMMARY")
    print("="*60)
    print(f" Status               : {transform_res['status']}")
    print(f" Database Engine Used : {load_res['engine']}")
    print(f" Orders Extracted     : {extract_res['total_orders']:,} orders")
    print(f" Gross Revenue Value  : ${extract_res['total_sales_usd']:,.2f} USD")
    print(f" Rows Loaded Landing  : {load_res['rows_loaded']:,} rows")
    print(f" SQL Models Built     : {transform_res.get('total_models', 0)} models")
    print(f" Total Duration       : {total_time} seconds")
    print("="*60 + "\n")
    
    return {
        "status": "SUCCESS" if transform_res["status"] == "SUCCESS" else "FAILED",
        "total_duration_seconds": total_time,
        "extracted_orders": extract_res["total_orders"],
        "loaded_rows": load_res["rows_loaded"],
        "models_built": transform_res.get("total_models", 0),
        "engine": load_res["engine"],
        "extract_details": extract_res,
        "load_details": load_res,
        "transform_details": transform_res,
        "logs": logs
    }

def interactive_cli():
    """
    CLI runner with formatted outputs and interactive prompts.
    """
    res = run_full_elt_pipeline(order_count=300, days=180)
    
    print("--------------------------------------------------")
    print(" ❓ NEXT STEPS DECISION PROMPT")
    print("--------------------------------------------------")
    print(" Next Step Option 1: Open Streamlit Web Dashboard (http://localhost:8501)")
    print(" Next Step Option 2: Inspect Database Tables via SQL Console")
    print("--------------------------------------------------")

if __name__ == "__main__":
    interactive_cli()
