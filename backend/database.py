import os
import sqlite3
from typing import Dict, Any
from dotenv import load_dotenv
load_dotenv()

DATABASE_FILE = os.getenv("DATABASE_FILE", "app.db")

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

def create_table():
    """
    Creates the necessary tables in the database,
    as defined in the schema.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # We will create 'issues' table for now.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        github_issue_id INTEGER UNIQUE NOT NULL,
        repo_name TEXT NOT NULL,
        title TEXT NOT NULL,
        body_text TEXT,
        github_url TEXT NOT NULL,
        labels TEXT
    )
    """)
    
    conn.commit()
    conn.close()