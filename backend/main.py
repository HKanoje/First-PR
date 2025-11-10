
from backend.models.models import *
from fastapi import FastAPI, HTTPException
from backend.services.services import *
from fastapi.middleware.cors import CORSMiddleware

# Define the "origins" (frontends) that are allowed to talk to us.
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


app = FastAPI(
    title="First-PR API",
    description="The core AI-based mathcing service for fiding first-time contributors to open source projects.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow our frontend's origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, OPTIONS, etc)
    allow_headers=["*"],  # Allow all headers (like Content-Type)
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
    This is the main endpoint for our V1 System.

    It takes a user's profile, reads issues from the local database,
    and return the best matches.
    """

    #fetch issues from local DB
    all_issues = fetch_issues_from_db()

    if not all_issues:
        print("No issues found in the local database.")
        #this is a crital error this means the scanner has not been run
        raise HTTPException(status_code=503,
                            detail="No issues found in the local database. Please run the scanner first.")
    
    #get AI matches
    print(f"Total issues in DB: {len(all_issues)}. Running AI matching...")
    matched_issue = get_ai_matches(request.user_profile, all_issues)

    #get top 10
    top_10_matches = matched_issue[:10]

    return MatchResponse(
        matches=top_10_matches,
        issues_scanned=len(all_issues),
        profile_summary=request.user_profile
    )