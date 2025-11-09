
from models.models import *
from fastapi import FastAPI, HTTPException
from services.services import *




app = FastAPI(
    title="First-PR API",
    description="The core AI-based mathcing service for fiding first-time contributors to open source projects.",
    version="0.1.0",
)

@app.get("/")
def get_health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok", "message": "First-PR API is running."}

@app.post("/matches", response_model=MatchResponse)
def get_matches(request: MatchRequest):
    """
    This is the main endpoint for our MVP.
    
    It takes a user's profile and a list of repos,
    scans them live, and returns the best matches.
    
    (Note: This is *not* the final architecture, as scanning
    live is slow. But it's the perfect MVP step.)
    """
    
    print(f"Received match request for {len(request.repos_to_scan)} repos.")

    #fetch all issues from all repos
    all_issues = []
    for repo_name in request.repos_to_scan:
        issues = fetch_issues_for_repo(repo_name)
        all_issues.extend(issues)  # Use extend instead of append to flatten the list

    if not all_issues:
        print("No issues found in all repos.")
        return MatchResponse(matches=[], issues_scanned=0, profile_summary=request.user_profile)
    
    #get AI Ranked Matches
    print(f"Total issues found: {len(all_issues)}. Running AI Matching...")
    matched_issues = get_ai_matches(request.user_profile, all_issues)

    #get top 10 results
    top_10_matches = matched_issues[:10]

    print(f"Returning {len(top_10_matches)} matches.")

    return MatchResponse(
        matches=top_10_matches,
        issues_scanned=len(all_issues),
        profile_summary=request.user_profile
    )