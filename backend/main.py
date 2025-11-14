import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from models.models import *
from services.services import *
from auth import router as auth_router

load_dotenv()

# Define the "origins" (frontends) that are allowed to talk to us.
origins = [os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")]

app = FastAPI(
    title="First-PR API",
    description="The core AI-based matching service for finding first-time contributors to open source projects.",
    version="0.1.0",
)

# Session middleware required for OAuth (Authlib uses request.session)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET", os.getenv("JWT_SECRET", "dev-session-secret")),
    same_site="lax",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth_router)

@app.get("/healthz")
def healthz():
    """Health check endpoint."""
    return {"ok": True}

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