from typing import List
from pydantic import BaseModel, Field



class MatchRequest(BaseModel):
    user_profile: str = Field(
        ...,
        description="The Uses's skill profile as text.",
        example="I am a new Python Developer. I have Used pandas and sckit-learn."
    )

    repos_to_scan: List[str] =Field(
        ...,
        description="A list of 'owner/repo' strings to scan.",
        example=["pandas-dev/pandas", "scikit-learn/scikit-learn", "kubeflow/sdk"]
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