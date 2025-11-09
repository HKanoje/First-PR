from typing import List, Dict, Any
from backend.models.models import *
import os
import json
import requests
import sqlite3
from fastapi import HTTPException
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
from backend.database import get_db_connection

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if GITHUB_TOKEN is None:
    print("="*80)
    print("WARNING: GITHUB_TOKEN environment variable not set.")
    print("="*80)

print("Loading AI Model..")

try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model loaded successfully.")

except Exception as e:
    print(f"FATAL: Could not load SentenceTransformer model: {e}")

if model is None:
    raise HTTPException(status_code=500, detail="AI model not loaded.")

def fetch_issues_for_repo(repo_name: str) -> List[Dict[str, Any]]:
    """
    Fetches "Truly Available" issues for a *single* repository.
    """
    print(f"Fetching issues for repo: {repo_name}")
    
    # Construct the query with proper syntax
    query_parts = [
        f"repo:{repo_name}",
        "state:open",
        "is:issue",
        "label:\"good first issue\"",
        "no:assignee"
    ]
    query = " ".join(query_parts)
    
    # Use requests' built-in URL parameter encoding
    params = {
        "q": query,
        "per_page": 50
    }
    
    # Set up headers with API version and authentication
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-Github-Api-Version": "2022-11-28",
    }

    #use GITHUB_TOKEN if available
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    try:
        response = requests.get(
            "https://api.github.com/search/issues",
            params=params,
            headers=headers
        )
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    
    except Exception as e:
        print(f"Error fetching {repo_name}: {e}")
        return []
    

def get_ai_matches(user_profile: str, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes a user profile and a list of issues.
    and retturn a sorted list of matches.
    """

    if not issues:
        return []
    
    if model is None:
        print("AI model not loaded.")
        return []
    
    #Create issue documents
    issue_docs = []
    issue_data_for_output = []

    for issue in issues:
        # Get the body content safely, using empty string if not present
        body = issue.get('body', '') or ''
        # Truncate body to 500 chars if it exists
        truncated_body = body[:500] + ('...' if len(body) > 500 else '')
        
        # Safely get all required fields with defaults
        title = issue.get('title', 'No title available')
        url = issue.get('html_url', issue.get('url', '#'))  # Try html_url first, then url, then default to #
        labels = issue.get('labels', [])
        
        issue_text = f"Title: {title}\n\nBody: {truncated_body}"
        issue_docs.append(issue_text)
        issue_data_for_output.append({
            "title": title,
            "url": url,
            "labels": [label.get('name', '') for label in labels if isinstance(label, dict)]
        })

    #generate embeddings
    issue_embeddings = model.encode(issue_docs)
    user_embedding = model.encode([user_profile]).reshape(1, -1)

    #calculate cosine similarities
    similarities = cosine_similarity(user_embedding, issue_embeddings)[0]


    #combine and sort
    results = []
    for i, issue_data in enumerate(issue_data_for_output):
        results.append({
            "score": similarities[i],
            **issue_data
        })
    
    return sorted(results, key=lambda x: x['score'], reverse=True)

def fetch_issues_from_db() -> List[Dict[str, Any]]:
    """
    Fetches all available issues from the local database.
    """
    print("Fetching issues from local database...")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM issues")
        issues = cursor.fetchall()
        conn.close()

        # Convert sqlite3.Row objects to dicts and reconstruct the data structure
        formatted_issues = []
        for row in issues:
            issue_dict = dict(row)
            
            # Convert stored labels string back to list of label objects
            try:
                labels_str = issue_dict.get('labels', '[]')
                labels_list = json.loads(labels_str) if labels_str else []
            except:
                labels_list = []
            
            formatted_issue = {
                'title': issue_dict['title'],
                'body': issue_dict['body_text'],
                'html_url': issue_dict['github_url'],
                'labels': [{'name': label} for label in labels_list]
            }
            formatted_issues.append(formatted_issue)
            
        return formatted_issues
    
    except sqlite3.OperationalError as e:
        print(f"DATABASE ERROR: {e}")
        print(f"Did you run 'python backend/scanner.py' first?")
        return []
    
    except Exception as e:
        print(f"Error fetching from DB: {e}")
        return []
    