"""
Load Module: L in ELT Pipeline (Supabase Target Storage)
Bulk loads raw E-Commerce JSON order payloads into Supabase landing table `raw_orders_landing`.
Supports loading via Supabase REST API (SUPABASE_URL & SUPABASE_KEY) or direct Postgres connection.
"""

import os
import json
import time
from datetime import datetime
from pipeline.db_manager import get_db_connection, get_supabase_client, get_supabase_credentials

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")

def load_latest_raw_data(raw_file_path=None):
    """
    Executes the Load step: Ingests raw JSON payload into Supabase `raw_orders_landing` table.
    """
    start_time = time.time()
    
    if not raw_file_path:
        raw_files = [f for f in os.listdir(RAW_DIR) if f.endswith(".json")]
        if not raw_files:
            raise FileNotFoundError("No raw JSON files found in data/raw. Run Extract step first!")
        raw_files.sort(reverse=True)
        raw_file_path = os.path.join(RAW_DIR, raw_files[0])
        
    with open(raw_file_path, "r") as f:
        raw_orders = json.load(f)
        
    creds = get_supabase_credentials()
    supabase_client = get_supabase_client()
    
    print("\n==================================================")
    print(" 💾 STEP 2: LOAD (Raw Storage Ingestion)")
    print("==================================================")
    print(f"[*] Source Payload File   : {os.path.basename(raw_file_path)}")
    print(f"[*] Landing Storage Table : raw_orders_landing")
    
    # Check if we can load via Supabase REST API
    if supabase_client is not None:
        print("[*] Target Database Engine: SUPABASE REST API (Cloud)")
        print("[*] Status: Inserting records into Supabase cloud table...")
        
        try:
            # Upsert/Insert records into Supabase table
            batch_size = 100
            total_inserted = 0
            for i in range(0, len(raw_orders), batch_size):
                batch = raw_orders[i:i + batch_size]
                supabase_client.table("raw_orders_landing").upsert(batch).execute()
                total_inserted += len(batch)
                
            duration = time.time() - start_time
            print(f"[✔] Loading Finished Successfully via Supabase REST API!")
            print(f" ├─ Rows Loaded : {total_inserted:,} records")
            print(f" ├─ Target DB   : Supabase Cloud ({creds['supabase_url']})")
            print(f" └─ Duration    : {duration:.3f} seconds")
            print("--------------------------------------------------")
            
            return {
                "status": "SUCCESS",
                "source_file": raw_file_path,
                "filename": os.path.basename(raw_file_path),
                "target_table": "raw_orders_landing",
                "engine": "SUPABASE_REST_API",
                "supabase_connected": True,
                "rows_loaded": total_inserted,
                "duration_seconds": round(duration, 3),
                "loaded_at": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"[!] Supabase REST API insert note: {e}. Falling back to PostgreSQL/SQLite connection driver.")

    # Fallback / Standard SQL connection driver
    conn, engine_type = get_db_connection()
    cursor = conn.cursor()
    print(f"[*] Target Database Engine: {engine_type}")
    print("[*] Status: Creating table and bulk inserting records...")
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS raw_orders_landing (
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
    """
    cursor.execute(create_table_sql)
    cursor.execute("DELETE FROM raw_orders_landing;")
    
    insert_sql = """
    INSERT INTO raw_orders_landing (
        order_id, order_date, customer_id, customer_name, customer_segment, country,
        product_id, product_name, category, unit_price, quantity, discount_pct,
        gross_item_total, discount_amount, net_item_total, shipping_cost, total_order_amount,
        order_status, extracted_at
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    );
    """ if engine_type == "POSTGRESQL" else """
    INSERT INTO raw_orders_landing (
        order_id, order_date, customer_id, customer_name, customer_segment, country,
        product_id, product_name, category, unit_price, quantity, discount_pct,
        gross_item_total, discount_amount, net_item_total, shipping_cost, total_order_amount,
        order_status, extracted_at
    ) VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
    );
    """
    
    records_to_insert = [
        (
            o["order_id"], o["order_date"], o["customer_id"], o["customer_name"],
            o["customer_segment"], o["country"], o["product_id"], o["product_name"],
            o["category"], o["unit_price"], o["quantity"], o["discount_pct"],
            o["gross_item_total"], o["discount_amount"], o["net_item_total"],
            o["shipping_cost"], o["total_order_amount"], o["order_status"], o["extracted_at"]
        )
        for o in raw_orders
    ]
    
    cursor.executemany(insert_sql, records_to_insert)
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM raw_orders_landing;")
    loaded_count = cursor.fetchone()[0]
    conn.close()
    
    duration = time.time() - start_time
    
    print(f"[✔] Loading Finished Successfully!")
    print(f" ├─ Rows Loaded : {loaded_count:,} records")
    print(f" ├─ Target DB   : {engine_type}")
    print(f" └─ Duration    : {duration:.3f} seconds")
    print("--------------------------------------------------")
    
    return {
        "status": "SUCCESS",
        "source_file": raw_file_path,
        "filename": os.path.basename(raw_file_path),
        "target_table": "raw_orders_landing",
        "engine": engine_type,
        "supabase_connected": creds["is_configured"],
        "rows_loaded": loaded_count,
        "duration_seconds": round(duration, 3),
        "loaded_at": datetime.now().isoformat()
    }

if __name__ == "__main__":
    load_latest_raw_data()
