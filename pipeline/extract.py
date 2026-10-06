"""
Extract Module: E in ELT Pipeline (E-Commerce Domain)
Fetches raw E-Commerce customer order transactions and writes raw JSON payload files.
"""

import os
import json
import random
import time
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")

CATEGORIES = {
    "Electronics": [
        ("PROD-101", "Wireless Ergonomic Mouse", 49.99),
        ("PROD-102", "4K Ultra-HD Monitor 27inch", 349.99),
        ("PROD-103", "Mechanical RGB Keyboard", 119.99),
        ("PROD-104", "USB-C Multiport Docking Station", 79.99),
        ("PROD-105", "Noise-Canceling Wireless Headphones", 199.99)
    ],
    "Office Furniture": [
        ("PROD-201", "Ergonomic Mesh Executive Chair", 289.99),
        ("PROD-202", "Electric Standing Desk 55inch", 429.99),
        ("PROD-203", "LED Task Desk Lamp with Wireless Charger", 39.99),
        ("PROD-204", "Dual Monitor Adjustable Arm", 64.99)
    ],
    "Accessories": [
        ("PROD-301", "Full Grain Leather Laptop Sleeve", 59.99),
        ("PROD-302", "Aluminum Laptop Cooling Stand", 34.99),
        ("PROD-303", "Anti-Glare Screen Protector 15inch", 19.99),
        ("PROD-304", "Braided High-Speed Cable 6ft", 14.99)
    ],
    "Apparel": [
        ("PROD-401", "Water-Resistant Tech Backpack", 89.99),
        ("PROD-402", "Merino Wool Zip Sweater", 109.99),
        ("PROD-403", "Blue-Light Blocking Glasses", 29.99)
    ]
}

COUNTRIES = ["United States", "United Kingdom", "Germany", "Japan", "Canada", "India", "France", "Australia"]
SEGMENTS = ["Consumer", "Corporate", "Home Office"]
ORDER_STATUSES = ["Completed", "Completed", "Completed", "Completed", "Pending", "Shipped", "Returned"]

FIRST_NAMES = ["Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Riley", "Casey", "Dakota", "Avery", "Reese"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]

def ensure_directories():
    os.makedirs(RAW_DIR, exist_ok=True)

def generate_mock_ecommerce_orders(order_count=500, days=365):
    """
    Generates realistic historical E-Commerce order transactions.
    """
    orders = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    customer_pool = []
    for i in range(1, 81):
        c_id = f"CUST-{1000 + i}"
        c_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        c_segment = random.choice(SEGMENTS)
        c_country = random.choice(COUNTRIES)
        customer_pool.append((c_id, c_name, c_segment, c_country))
        
    for i in range(1, order_count + 1):
        order_id = f"ORD-{10000 + i}"
        customer = random.choice(customer_pool)
        
        category = random.choice(list(CATEGORIES.keys()))
        product_info = random.choice(CATEGORIES[category])
        prod_id, prod_name, unit_price = product_info
        
        quantity = random.choices([1, 2, 3, 4, 5], weights=[60, 25, 10, 3, 2])[0]
        discount_pct = random.choice([0.0, 0.0, 0.0, 0.05, 0.10, 0.15, 0.20])
        shipping_cost = round(random.uniform(4.99, 19.99), 2)
        order_status = random.choice(ORDER_STATUSES)
        
        random_days = random.randint(0, days)
        order_date = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
        
        gross_item_total = round(unit_price * quantity, 2)
        discount_amount = round(gross_item_total * discount_pct, 2)
        net_item_total = round(gross_item_total - discount_amount, 2)
        total_order_amount = round(net_item_total + shipping_cost, 2)
        
        orders.append({
            "order_id": order_id,
            "order_date": order_date,
            "customer_id": customer[0],
            "customer_name": customer[1],
            "customer_segment": customer[2],
            "country": customer[3],
            "product_id": prod_id,
            "product_name": prod_name,
            "category": category,
            "unit_price": unit_price,
            "quantity": quantity,
            "discount_pct": discount_pct,
            "gross_item_total": gross_item_total,
            "discount_amount": discount_amount,
            "net_item_total": net_item_total,
            "shipping_cost": shipping_cost,
            "total_order_amount": total_order_amount,
            "order_status": order_status,
            "extracted_at": datetime.now().isoformat()
        })
        
    orders.sort(key=lambda x: x["order_date"])
    return orders

def extract_all_data(order_count=500, days=365):
    """
    Executes E-Commerce Extract step and dumps raw JSON to disk.
    """
    start_time = time.time()
    ensure_directories()
    
    print("\n==================================================")
    print(" 📥 STEP 1: EXTRACT (E-Commerce Raw Ingestion)")
    print("==================================================")
    print(f"[*] Target Order Transactions Count: {order_count}")
    print(f"[*] Historical Timeframe Span      : {days} days")
    print("[*] Status: Extracting data from source...")
    
    orders = generate_mock_ecommerce_orders(order_count=order_count, days=days)
    
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"raw_ecommerce_orders_{timestamp_str}.json"
    output_path = os.path.join(RAW_DIR, output_filename)
    
    with open(output_path, "w") as f:
        json.dump(orders, f, indent=2)
        
    duration = time.time() - start_time
    total_sales_value = sum(o["total_order_amount"] for o in orders)
    
    print(f"[✔] Extraction Finished Successfully!")
    print(f" ├─ Saved File  : {output_filename}")
    print(f" ├─ Orders Count: {len(orders):,} transactions")
    print(f" ├─ Gross Value : ${total_sales_value:,.2f} USD")
    print(f" └─ Duration    : {duration:.3f} seconds")
    print("--------------------------------------------------")
    
    return {
        "status": "SUCCESS",
        "output_file": output_path,
        "filename": output_filename,
        "total_orders": len(orders),
        "total_sales_usd": round(total_sales_value, 2),
        "duration_seconds": round(duration, 3),
        "extracted_at": datetime.now().isoformat()
    }

if __name__ == "__main__":
    extract_all_data(order_count=200, days=30)
