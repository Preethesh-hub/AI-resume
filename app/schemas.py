from pydantic import BaseModel
from typing import List, Optional


class ATSCheck(BaseModel):
    """A single ATS friendliness check result."""
    name: str
    passed: bool
    detail: str


class AnalyzeResponse(BaseModel):
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    experience_score: float
    education_score: float
    skill_score: float
    suggestions: List[str]
    llm_summary: Optional[str] = None
    # ── New: ATS Score ──
    ats_score: Optional[float] = None
    ats_checks: Optional[List[ATSCheck]] = None
    # ── New: AI Rewrite Suggestions ──
    rewrite_suggestions: Optional[List[str]] = None
    # ── New: Interview Questions ──
    interview_questions: Optional[List[str]] = None
    # ── New: Red Flags ──
    red_flags: Optional[List[dict]] = None


class CompareItem(BaseModel):
    """A single JD entry for comparison."""
    label: str
    job_description: str


class CompareResult(BaseModel):
    """Result for one JD in a comparison."""
    label: str
    match_score: float
    skill_score: float
    experience_score: float
    education_score: float
    matched_skills: List[str]
    missing_skills: List[str]


class CompareResponse(BaseModel):
    """Response for multi-JD comparison."""
    results: List[CompareResult]

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class StatusUpdate(BaseModel):
    status: str

class CoverLetterRequest(BaseModel):
    candidate_id: int

class LinkedInOptimizeRequest(BaseModel):
    profile_text: str
    target_role: str

class LinkedInOptimizeResponse(BaseModel):
    headline_suggestion: str
    summary_suggestion: str
    tips: List[str]
