from typing import List
from pydantic import BaseModel, Field



class MatchRequest(BaseModel):
    user_profile: str = Field(
        ...,
        description="The User's skill profile as text.",
        example="I am a new Python Developer. I have used pandas and scikit-learn."
    )

class MatchedIssue(BaseModel):
    score: float
    title: str
    url: str
    labels: List[str]

class MatchResponse(BaseModel):
    matches: List[MatchedIssue]
    issues_scanned: int
    profile_summary: str = Field(..., example="I am a new Python Developer...")