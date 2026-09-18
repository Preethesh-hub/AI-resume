from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.schemas import (
    AnalyzeResponse, CompareResponse, CompareResult, UserResponse, UserCreate, Token,
    StatusUpdate, CoverLetterRequest, LinkedInOptimizeRequest, LinkedInOptimizeResponse
)
from app.parser import parse_file
from app.nlp import analyze_resume_vs_jd, extract_skills
from app.scorer import compute_score, generate_suggestions
from app.llm import (
    generate_summary, generate_rewrite_suggestions, generate_interview_questions,
    generate_cover_letter, optimize_linkedin_profile
)
from app.ats import compute_ats_score
from app.database import engine, get_db
import app.models as models
from app.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_current_user_optional,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from typing import List
from datetime import timedelta
import json
import os
import io
from fpdf import FPDF

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Resume Analyzer API")

# Use a relative path to templates to ensure it works anywhere
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    """Serves the frontend testing UI."""
    user = get_current_user_optional(request, db)
    return templates.TemplateResponse(request=request, name="index.html", context={"user": user})

@app.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/login", response_class=HTMLResponse)
async def read_login(request: Request, db: Session = Depends(get_db)):
    """Serves the login page."""
    user = get_current_user_optional(request, db)
    if user:
        return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="login.html")

@app.post("/api/login", response_model=Token)
async def login_for_access_token(
    user: UserCreate, 
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/logout")
async def logout():
    # Frontend will handle this by deleting the cookie/token
    return {"message": "Logged out successfully"}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Endpoint to analyze a resume against a job description.
    Now includes ATS score and AI rewrite suggestions.
    """
    try:
        # 1. Parse Resume
        file_bytes = await resume.read()
        resume_text = parse_file(file_bytes, resume.filename)
        
        # 2. NLP / Extraction
        matched_skills, missing_skills, experience_years, has_education = analyze_resume_vs_jd(
            resume_text, job_description
        )
        jd_skills = extract_skills(job_description)
        jd_skills_count = len(jd_skills)
        
        # 3. Scoring
        total_score, skill_score, exp_score, edu_score = compute_score(
            matched_skills, jd_skills_count, experience_years, has_education
        )
        
        # 4. Suggestions
        suggestions = generate_suggestions(skill_score, exp_score, edu_score, missing_skills)
        
        # 5. Optional LLM Summary
        llm_summary = generate_summary(resume_text, job_description)

        # 6. ATS Friendliness Score
        ats_score, ats_checks = compute_ats_score(resume_text)

        # 7. AI Rewrite Suggestions
        rewrite_suggestions = generate_rewrite_suggestions(
            resume_text, job_description, list(missing_skills)
        )
        
        # 7b. AI Interview Questions
        interview_questions = generate_interview_questions(
            resume_text, job_description, list(missing_skills)
        )
        
        # 7c. Red Flag Scanning
        RED_FLAGS = {
            "wear many hats": "Warning: Expect to do the work of 2-3 people.",
            "fast-paced": "Warning: High risk of burnout and poor work-life balance.",
            "work hard play hard": "Warning: Often a culture of overworking.",
            "we are a family": "Warning: Poor boundaries, guilt-tripping for working overtime.",
            "self-starter": "Warning: Lack of training or onboarding process."
        }
        red_flags = []
        jd_lower = job_description.lower()
        for flag, warning in RED_FLAGS.items():
            if flag in jd_lower:
                red_flags.append({"phrase": flag, "warning": warning})
        
        # 8. Save to DB
        db_candidate = models.Candidate(
            filename=resume.filename,
            job_description=job_description,
            match_score=round(total_score, 2),
            skill_score=round(skill_score, 2),
            experience_score=round(exp_score, 2),
            education_score=round(edu_score, 2),
            ats_score=ats_score,
            matched_skills=",".join(list(matched_skills)),
            missing_skills=",".join(list(missing_skills)),
            user_id=current_user.id
        )
        db.add(db_candidate)
        db.commit()

        return AnalyzeResponse(
            match_score=round(total_score, 2),
            matched_skills=list(matched_skills),
            missing_skills=list(missing_skills),
            experience_score=round(exp_score, 2),
            education_score=round(edu_score, 2),
            skill_score=round(skill_score, 2),
            suggestions=suggestions,
            llm_summary=llm_summary,
            ats_score=ats_score,
            ats_checks=ats_checks,
            rewrite_suggestions=rewrite_suggestions,
            interview_questions=interview_questions,
            red_flags=red_flags,
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard", response_class=HTMLResponse)
async def read_dashboard(request: Request, db: Session = Depends(get_db)):
    """Serves the Recruiter Dashboard UI."""
    user = get_current_user_optional(request, db)
    return templates.TemplateResponse(request=request, name="dashboard.html", context={"user": user})

@app.get("/api/candidates")
def get_candidates(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    candidates = db.query(models.Candidate).filter(models.Candidate.user_id == current_user.id).order_by(models.Candidate.created_at.desc()).all()
    return [{
        "id": c.id,
        "filename": c.filename,
        "match_score": c.match_score,
        "skill_score": c.skill_score,
        "experience_score": c.experience_score,
        "education_score": c.education_score,
        "ats_score": c.ats_score,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "matched_skills": c.matched_skills.split(",") if c.matched_skills else [],
        "missing_skills": c.missing_skills.split(",") if c.missing_skills else [],
        "status": c.status,
    } for c in candidates]

@app.get("/api/dashboard/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    candidates = db.query(models.Candidate).filter(models.Candidate.user_id == current_user.id).order_by(models.Candidate.created_at.asc()).all()
    
    if not candidates:
        return {"total_analyzed": 0, "avg_match_score": 0, "score_history": [], "top_missing_skills": []}
    
    total_analyzed = len(candidates)
    avg_match_score = round(sum(c.match_score for c in candidates) / total_analyzed, 1)
    
    # Chart 1: Score over time (last 10)
    score_history = [{"date": c.created_at.strftime("%b %d"), "score": c.match_score} for c in candidates[-10:] if c.created_at] 
    
    # Chart 2: Top Missing Skills
    missing_counts = {}
    for c in candidates:
        if c.missing_skills:
            for skill in c.missing_skills.split(","):
                skill = skill.strip()
                if skill:
                    missing_counts[skill] = missing_counts.get(skill, 0) + 1
                    
    # Sort dict and take top 5
    top_missing = sorted(missing_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    top_missing_formatted = [{"skill": k, "count": v} for k, v in top_missing]

    return {
        "total_analyzed": total_analyzed,
        "avg_match_score": avg_match_score,
        "score_history": score_history,
        "top_missing_skills": top_missing_formatted
    }

@app.patch("/api/candidates/{candidate_id}/status")
def update_candidate_status(
    candidate_id: int,
    status_update: StatusUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == candidate_id,
        models.Candidate.user_id == current_user.id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    candidate.status = status_update.status
    db.commit()
    return {"message": "Status updated successfully"}

@app.post("/api/cover-letter")
def api_generate_cover_letter(
    req: CoverLetterRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    candidate = db.query(models.Candidate).filter(
        models.Candidate.id == req.candidate_id,
        models.Candidate.user_id == current_user.id
    ).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    # We don't have the original resume text stored easily, so we might need it passed in?
    # Actually, we can just say this requires the resume text to be parsed again, or we can just accept text.
    # Let's change this to accept resume_text and jd_text directly for simplicity.
    raise HTTPException(status_code=400, detail="Use the text-based endpoint")

@app.post("/api/generate-cover-letter")
async def text_generate_cover_letter(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    current_user: models.User = Depends(get_current_user)
):
    file_bytes = await resume.read()
    resume_text = parse_file(file_bytes, resume.filename)
    
    cover_letter = generate_cover_letter(resume_text, job_description)
    if not cover_letter:
        raise HTTPException(status_code=500, detail="Could not generate cover letter")
    return {"cover_letter": cover_letter}

@app.post("/api/export-resume")
async def export_resume(
    resume_content: str = Form(...),
    current_user: models.User = Depends(get_current_user)
):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=11)
    
    # Handle multi-line (fpdf2 handles utf8 better, but fallback to latin-1 encoding approach if needed)
    try:
        # replace smart quotes etc if they exist
        text = resume_content.replace('“', '"').replace('”', '"').replace("'", "'").replace("'", "'")
        for line in text.split('\n'):
            pdf.multi_cell(0, 7, text=line)
    except Exception as e:
        pdf.multi_cell(0, 7, text=resume_content.encode('latin-1', 'replace').decode('latin-1'))

    pdf_bytes = pdf.output(dest='S')
    # Depending on fpdf version, output('S') is string or bytearray. Let's make sure it's bytes
    if isinstance(pdf_bytes, str):
        pdf_bytes = pdf_bytes.encode('latin-1')
        
    return Response(
        content=pdf_bytes, 
        media_type="application/pdf", 
        headers={"Content-Disposition": "attachment; filename=resume_optimized.pdf"}
    )

@app.post("/api/linkedin-optimize", response_model=LinkedInOptimizeResponse)
async def api_linkedin_optimize(
    req: LinkedInOptimizeRequest,
    current_user: models.User = Depends(get_current_user)
):
    result = optimize_linkedin_profile(req.profile_text, req.target_role)
    if not result:
        raise HTTPException(status_code=500, detail="Could not optimize profile")
    return result



@app.post("/compare", response_model=CompareResponse)
async def compare_resume(
    resume: UploadFile = File(...),
    job_descriptions: str = Form(...),
    current_user: models.User = Depends(get_current_user)
):
    """
    Compare a single resume against multiple job descriptions.
    Accepts job_descriptions as a JSON string: [{"label": "...", "job_description": "..."}]
    """
    try:
        # 1. Parse Resume
        file_bytes = await resume.read()
        resume_text = parse_file(file_bytes, resume.filename)

        # 2. Parse the JD list
        jd_list = json.loads(job_descriptions)

        results: List[CompareResult] = []

        for jd_item in jd_list:
            label = jd_item.get("label", "Untitled")
            jd_text = jd_item.get("job_description", "")

            if not jd_text.strip():
                continue

            # Run analysis pipeline
            matched_skills, missing_skills, experience_years, has_education = analyze_resume_vs_jd(
                resume_text, jd_text
            )
            jd_skills = extract_skills(jd_text)
            jd_skills_count = len(jd_skills)

            total_score, skill_score, exp_score, edu_score = compute_score(
                matched_skills, jd_skills_count, experience_years, has_education
            )

            results.append(CompareResult(
                label=label,
                match_score=round(total_score, 2),
                skill_score=round(skill_score, 2),
                experience_score=round(exp_score, 2),
                education_score=round(edu_score, 2),
                matched_skills=list(matched_skills),
                missing_skills=list(missing_skills),
            ))

        # Sort by match score descending
        results.sort(key=lambda r: r.match_score, reverse=True)

        return CompareResponse(results=results)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid job_descriptions JSON format.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel

class URLRequest(BaseModel):
    url: str

from app.scraper import scrape_job_description

@app.post("/api/scrape-jd")
def scrape_jd(request: URLRequest):
    try:
        text = scrape_job_description(request.url)
        return {"text": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
