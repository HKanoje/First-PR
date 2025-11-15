import os
import sys
import requests
import json
from typing import List, Dict, Any
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from database import get_db_connection
from services.services import fetch_issues_for_repo  # Moving this import lower to avoid circular import

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# This is our MVP version of the "Healthy Repo" list (Section 5.1)
# We will manually hard-code this for now.
REPOS_TO_SCAN = [
    "kubeflow/sdk",
    "pandas-dev/pandas",
    "scikit-learn/scikit-learn",
    "fastapi-users/fastapi-users",
    "tiangolo/fastapi"
]

if GITHUB_TOKEN is None:
    print("=" * 80)
    print(" WARNING: GITHUB_TOKEN environment variable not set.")
    print("=" * 80)

def create_table():
    """
    Creates the nessesary tables in the databse,
    as defined in the schema.
    """

    conn = get_db_connection()
    cursor = conn.cursor()

    #We will create 'issues' table for now.
    #In actual implementation, we'd have 'repos' and 'users' tables too.

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        github_issue_id INTEGER UNIQUE NOT NULL,
        repo_name TEXT NOT NULL,
        title TEXT NOT NULL,
        body_text TEXT,
        github_url TEXT NOT NULL,
        labels TEXT -- Storing lables as a JSON string
    );
    """)

    conn.commit()
    conn.close()
    print("Database tables ensured.")

def populate_database():
    """
    Main fucntion to scan all repos and save issues to the DB.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    print(f"Starting scan for {len(REPOS_TO_SCAN)} repositories...")
    total_issues_found = 0
    total_issues_added = 0

    for repo_name in REPOS_TO_SCAN:
        issues = fetch_issues_for_repo(repo_name)
        total_issues_found += len(issues)

        for issue in issues:
            try:
                #storing labels as JSON string
                labels_json = json.dumps([label['name'] for label in issue['labels']])

                cursor.execute("""
                    INSERT OR IGNORE INTO issues (
                        github_issue_id, repo_name, title, body_text, github_url, labels
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    issue['id'],
                    repo_name,
                    issue['title'],
                    issue.get('body', ''),  # Handle cases where body might be None
                    issue['html_url'],
                    labels_json
                ))

                if cursor.rowcount > 0:
                    total_issues_added += 1
                    
            except Exception as e:
                print(f"Error inserting issue {issue.get('id', 'unknown')}: {e}")
    
    conn.commit()
    conn.close()

    print("\n" + "=" * 80)
    print("Database Scan Complete.")
    print(f"Total Issues Found: {total_issues_found}")
    print(f"Total New Issues Added: {total_issues_added}")
    print("=" * 80)

if __name__ == "__main__":
    print("Initializing database...")
    create_table()
    print("Starting Github Issue scan...")
    populate_database()