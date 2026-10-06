"""
Transform Module: T in ELT Pipeline (Supabase / Postgres Target)
Executes SQL models inside Supabase/Postgres database engine.
Models executed:
  1. Staging: stg_raw_orders
  2. Warehouse: dim_customers, dim_products, fact_orders
  3. Analytics: analytics_customer_rfm, analytics_sales_summary
"""

import os
import time
import json
from datetime import datetime
from pipeline.db_manager import get_db_connection

SQL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sql")

MODEL_SEQUENCE = [
    ("staging", "stg_raw_orders.sql"),
    ("warehouse", "dim_customers.sql"),
    ("warehouse", "dim_products.sql"),
    ("warehouse", "fact_orders.sql"),
    ("analytics", "analytics_customer_rfm.sql"),
    ("analytics", "analytics_sales_summary.sql"),
]

def execute_transformations():
    """
    Executes the Transformation phase: Runs SQL scripts in dependency order.
    """
    start_total_time = time.time()
    
    conn, engine_type = get_db_connection()
    cursor = conn.cursor()
    model_results = []
    
    print("\n==================================================")
    print(" ⚙️ STEP 3: TRANSFORM (In-Database SQL Models)")
    print("==================================================")
    print(f"[*] Target Database Engine: {engine_type}")
    print(f"[*] Total Models to Execute: {len(MODEL_SEQUENCE)}")
    print("[*] Status: Compiling and executing dbt-style SQL models...\n")
    
    for layer, sql_file in MODEL_SEQUENCE:
        file_path = os.path.join(SQL_DIR, layer, sql_file)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"SQL file not found: {file_path}")
            
        with open(file_path, "r") as f:
            sql_content = f.read()
            
        model_start = time.time()
        table_name = sql_file.replace(".sql", "")
        
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            cursor.execute(sql_content)
            conn.commit()
            
            model_duration = round(time.time() - model_start, 4)
            
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            row_count = cursor.fetchone()[0]
            
            print(f"  [✔] Layer: {layer:<10} | Model: {table_name:<26} | Rows: {row_count:<6} | Duration: {model_duration:.4f}s")
            
            model_results.append({
                "model": table_name,
                "layer": layer,
                "status": "SUCCESS",
                "rows": row_count,
                "duration_seconds": model_duration
            })
        except Exception as e:
            conn.rollback()
            model_duration = round(time.time() - model_start, 4)
            print(f"  [✖] Layer: {layer:<10} | Model: {table_name:<26} | FAILED: {str(e)}")
            model_results.append({
                "model": table_name,
                "layer": layer,
                "status": "FAILED",
                "error": str(e),
                "duration_seconds": model_duration
            })
            conn.close()
            return {
                "status": "FAILED",
                "error": f"Error running model {table_name}: {str(e)}",
                "models": model_results,
                "engine": engine_type
            }
            
    conn.close()
    total_duration = round(time.time() - start_total_time, 3)
    
    print("\n--------------------------------------------------")
    print(f"[✔] Transformations Finished Successfully!")
    print(f" ├─ Models Built : {len(model_results)} SQL models")
    print(f" └─ Duration     : {total_duration:.3f} seconds")
    print("--------------------------------------------------")
    
    return {
        "status": "SUCCESS",
        "total_models": len(model_results),
        "total_duration_seconds": total_duration,
        "engine": engine_type,
        "transformed_at": datetime.now().isoformat(),
        "models": model_results
    }

if __name__ == "__main__":
    execute_transformations()
