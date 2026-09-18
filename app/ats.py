import re
from typing import List, Tuple
from pydantic import BaseModel


from app.schemas import ATSCheck


def compute_ats_score(resume_text: str) -> Tuple[float, List[ATSCheck]]:
    """
    Scores a resume for ATS (Applicant Tracking System) friendliness.
    Returns an overall score (0-100) and a list of individual checks.
    """
    checks: List[ATSCheck] = []

    # ── 1. Parseable Text ──
    text_stripped = resume_text.strip()
    is_parseable = len(text_stripped) > 50
    checks.append(ATSCheck(
        name="Parseable Content",
        passed=is_parseable,
        detail="Resume text was extracted successfully." if is_parseable
        else "Resume appears empty or too short — it may be a scanned image."
    ))

    # ── 2. Contact Info: Email ──
    has_email = bool(re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', resume_text))
    checks.append(ATSCheck(
        name="Email Address",
        passed=has_email,
        detail="Email address found." if has_email
        else "No email address detected — add your email so recruiters can reach you."
    ))

    # ── 3. Contact Info: Phone ──
    has_phone = bool(re.search(
        r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}',
        resume_text
    ))
    checks.append(ATSCheck(
        name="Phone Number",
        passed=has_phone,
        detail="Phone number found." if has_phone
        else "No phone number detected — consider adding one."
    ))

    # ── 4. Standard Section Headers ──
    standard_headers = [
        ("Experience", r'\b(experience|work\s*history|employment)\b'),
        ("Education", r'\b(education|academic|qualification)\b'),
        ("Skills", r'\b(skills|technologies|technical\s*skills|competencies)\b'),
    ]

    found_headers = []
    for header_name, pattern in standard_headers:
        if re.search(pattern, resume_text, re.IGNORECASE):
            found_headers.append(header_name)

    has_headers = len(found_headers) >= 2
    checks.append(ATSCheck(
        name="Standard Section Headers",
        passed=has_headers,
        detail=f"Found sections: {', '.join(found_headers)}." if found_headers
        else "No standard section headers found (Experience, Education, Skills). ATS bots look for these."
    ))

    # ── 5. Reasonable Length ──
    word_count = len(resume_text.split())
    good_length = 150 <= word_count <= 2500
    checks.append(ATSCheck(
        name="Resume Length",
        passed=good_length,
        detail=f"Word count: {word_count} — looks good!" if good_length
        else f"Word count: {word_count} — {'too short, add more detail.' if word_count < 150 else 'very long, consider trimming to 1-2 pages.'}"
    ))

    # ── 6. No Excessive Special Characters ──
    special_chars = len(re.findall(r'[^\w\s.,;:!?\'\"()\-/@#&+]', resume_text))
    char_ratio = special_chars / max(len(resume_text), 1)
    clean_formatting = char_ratio < 0.03
    checks.append(ATSCheck(
        name="Clean Formatting",
        passed=clean_formatting,
        detail="Formatting looks clean and ATS-friendly." if clean_formatting
        else "High density of special characters detected — ATS bots may struggle to parse fancy formatting."
    ))

    # ── 7. No long lines of repeated characters (table/graphic indicators) ──
    has_graphics = bool(re.search(r'[─━═│┃|]{5,}|[■□▪▫●○◆◇★☆]{3,}', resume_text))
    checks.append(ATSCheck(
        name="No Graphics/Tables",
        passed=not has_graphics,
        detail="No graphic elements detected." if not has_graphics
        else "Possible tables or graphics detected — these often break ATS parsing."
    ))

    # ── Calculate overall score ──
    passed_count = sum(1 for c in checks if c.passed)
    ats_score = round((passed_count / len(checks)) * 100, 1)

    return ats_score, checks
