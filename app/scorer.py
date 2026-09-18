from typing import Set, List, Tuple

def compute_score(
    matched_skills: Set[str],
    jd_skills_count: int,
    experience_years: float,
    has_education: bool,
    required_experience: float = 3.0
) -> Tuple[float, float, float, float]:
    """
    Computes a weighted match score.
    Weights: 65% skills / 20% experience / 15% education
    """
    
    # 1. Skills Score (out of 100)
    if jd_skills_count == 0:
        skill_score = 100.0 # If JD has no specific skills, give full points
    else:
        skill_score = (len(matched_skills) / jd_skills_count) * 100.0
        
    # 2. Experience Score (out of 100)
    # Cap at 100. If they meet or exceed required experience, 100.
    if required_experience <= 0:
        experience_score = 100.0
    else:
        experience_score = min(100.0, (experience_years / required_experience) * 100.0)
        
    # 3. Education Score (out of 100)
    education_score = 100.0 if has_education else 0.0
    
    # Total weighted score
    total_score = (skill_score * 0.65) + (experience_score * 0.20) + (education_score * 0.15)
    
    return total_score, skill_score, experience_score, education_score

def generate_suggestions(
    skill_score: float,
    experience_score: float,
    education_score: float,
    missing_skills: Set[str]
) -> List[str]:
    """Generates actionable suggestions based on scores."""
    suggestions = []
    
    if skill_score < 70:
        suggestions.append(f"Focus on acquiring missing key skills: {', '.join(list(missing_skills)[:5])}")
    
    if experience_score < 100:
        suggestions.append("Highlight more quantifiable achievements in your past roles to emphasize your experience level.")
        
    if education_score == 0:
        suggestions.append("If you have a degree, make sure it's explicitly stated using standard abbreviations (e.g., BS, MS, Bachelor).")
        
    if not suggestions:
        suggestions.append("Your profile looks like a strong match for this role!")
        
    return suggestions
