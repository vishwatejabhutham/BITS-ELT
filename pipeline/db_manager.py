"""
Database Manager Module for Supabase / PostgreSQL Engine.
Supports Supabase Client (REST API via SUPABASE_URL & SUPABASE_KEY),
direct PostgreSQL connection, and local SQLite engine fallback.
"""

import os
import sqlite3
from dotenv import load_dotenv

# Try importing supabase client
try:
    from supabase import create_client, Client
    SUPABASE_PY_AVAILABLE = True
except ImportError:
    SUPABASE_PY_AVAILABLE = False

# Try importing psycopg2 for Supabase PostgreSQL connection
try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

load_dotenv()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
SQLITE_DB_PATH = os.path.join(DATA_DIR, "supabase_elt.db")

def get_supabase_credentials():
    """
    Reads Supabase connection parameters from environment variables.
    """
    postgres_url = os.getenv("POSTGRES_URL") or os.getenv("SUPABASE_DB_URL")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    return {
        "postgres_url": postgres_url,
        "supabase_url": supabase_url,
        "supabase_key": supabase_key,
        "is_configured": bool(postgres_url or (supabase_url and supabase_key))
    }

def get_supabase_client():
    """
    Returns an instance of Supabase Client if SUPABASE_URL and SUPABASE_KEY exist.
    """
    creds = get_supabase_credentials()
    if creds["supabase_url"] and creds["supabase_key"] and SUPABASE_PY_AVAILABLE:
        try:
            client: Client = create_client(creds["supabase_url"], creds["supabase_key"])
            return client
        except Exception as e:
            print(f"Supabase REST Client initialization error: {e}")
    return None

def get_db_connection():
    """
    Returns an active database connection.
    Connects to Supabase PostgreSQL if configured, else local database.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    creds = get_supabase_credentials()
    
    if creds["postgres_url"] and PSYCOPG2_AVAILABLE:
        try:
            conn = psycopg2.connect(creds["postgres_url"])
            return conn, "POSTGRESQL"
        except Exception as e:
            print(f"Supabase PostgreSQL connection failed: {e}. Falling back to SQLite engine.")
            
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn, "SQLITE"
