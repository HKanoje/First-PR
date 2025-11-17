import os
import sqlite3
from typing import Dict, Any
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_FILE = os.getenv("DATABASE_FILE", "app.db")
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    """
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name
    return conn

def get_db():
    """
    Dependency for FastAPI to get database sessions.
    """
    from sqlalchemy.orm import Session
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_sqlalchemy_tables():
    """
    Creates all SQLAlchemy ORM tables in the database.
    """
    Base.metadata.create_all(bind=engine)

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