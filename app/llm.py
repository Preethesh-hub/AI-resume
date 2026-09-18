import os
import openai
from typing import Optional, List


def generate_summary(resume_text: str, jd_text: str) -> Optional[str]:
    """
    Generates a qualitative summary of the candidate's fit for the role
    using the OpenAI API if OPENAI_API_KEY is set.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
        
    try:
        client = openai.OpenAI(api_key=api_key)
        
        prompt = f"""
        Act as an expert technical recruiter. Analyze this resume against the job description.
        Provide a concise, 2-3 sentence summary of why the candidate is or isn't a good fit, 
        highlighting their strongest assets and biggest gaps.
        
        Job Description:
        {jd_text[:1000]}...
        
        Resume:
        {resume_text[:1500]}...
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful expert technical recruiter."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Summary Error: {e}")
        return None


def generate_rewrite_suggestions(
    resume_text: str,
    jd_text: str,
    missing_skills: List[str]
) -> Optional[List[str]]:
    """
    Uses the LLM to generate rewritten resume bullet points that better
    incorporate missing keywords from the job description.
    Returns a list of suggested bullet points, or None if no API key.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    if not missing_skills:
        return ["Your resume already covers the key skills — no rewrites needed! 🎉"]

    try:
        client = openai.OpenAI(api_key=api_key)

        skills_str = ", ".join(missing_skills[:8])

        prompt = f"""You are a resume writing expert. The candidate's resume is missing these 
keywords that appear in the job description: {skills_str}

Based on the resume content below, suggest 3-5 improved bullet points the candidate 
could ADD or REWRITE in their resume to naturally incorporate these missing skills.

Each bullet point should:
- Start with a strong action verb
- Be specific and include quantifiable results where possible
- Naturally weave in one or more of the missing keywords
- Sound authentic (not keyword-stuffed)

Format: Return ONLY the bullet points, one per line, each starting with "•"

Resume excerpt:
{resume_text[:1200]}

Job Description excerpt:
{jd_text[:800]}
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert resume writer who helps candidates optimize their resumes for specific job descriptions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400
        )

        raw = response.choices[0].message.content.strip()
        # Split by newline and clean up
        suggestions = [
            line.strip().lstrip("•-").strip()
            for line in raw.split("\n")
            if line.strip() and len(line.strip()) > 10
        ]
        return suggestions[:5] if suggestions else None

    except Exception as e:
        print(f"LLM Rewrite Error: {e}")
        return None

def generate_interview_questions(resume_text: str, jd_text: str, missing_skills: List[str]) -> Optional[List[str]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        client = openai.OpenAI(api_key=api_key)
        skills_str = ", ".join(missing_skills[:5]) if missing_skills else "general role requirements"
        
        prompt = f"""You are an expert technical interviewer. The candidate is interviewing for this role, but their resume lacks explicit experience with: {skills_str}.
        
        Based on the job description and their resume, generate 3-5 specific, challenging interview questions that test their aptitude or transferable skills in these missing areas.

        Format: Return ONLY the questions, one per line, each starting with "•"

        Resume excerpt:
        {resume_text[:1200]}

        Job Description excerpt:
        {jd_text[:800]}
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a tough but fair technical interviewer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        raw = response.choices[0].message.content.strip()
        questions = [line.strip().lstrip("•-").strip() for line in raw.split("\n") if len(line.strip()) > 10]
        return questions[:5] if questions else None
    except Exception as e:
        print(f"LLM Interview Qs Error: {e}")
        return None

def generate_cover_letter(resume_text: str, jd_text: str) -> Optional[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        client = openai.OpenAI(api_key=api_key)
        prompt = f"""Write a professional, compelling, and modern cover letter based on the candidate's resume and the job description.
        Do not use placeholder brackets like [Company Name] if the company is mentioned in the JD. If not mentioned, just write it generically without placeholders.
        Keep it to 3-4 paragraphs. Make it enthusiastic and highlight the alignment between their experience and the role.

        Resume excerpt:
        {resume_text[:2000]}

        Job Description excerpt:
        {jd_text[:1500]}
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert career coach writing a cover letter."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"LLM Cover Letter Error: {e}")
        return None

def optimize_linkedin_profile(profile_text: str, target_role: str) -> Optional[dict]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    try:
        client = openai.OpenAI(api_key=api_key)
        prompt = f"""You are a LinkedIn profile optimization expert. The user wants to optimize their profile for the role of "{target_role}".
        
        Analyze their current profile text (which may be a mix of their summary, headline, and experience).
        Provide:
        1. A suggested highly-optimized Headline (1-2 sentences max).
        2. A suggested engaging Summary/About section (2-3 paragraphs).
        3. 3-4 bullet point tips on what else they should improve on their profile.

        Format the output EXACTLY like this:
        HEADLINE: <your suggested headline>
        ---
        SUMMARY:
        <your suggested summary>
        ---
        TIPS:
        • <tip 1>
        • <tip 2>
        • <tip 3>

        Current Profile Text:
        {profile_text[:2000]}
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a LinkedIn profile optimization expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )
        
        raw = response.choices[0].message.content.strip()
        parts = raw.split("---")
        if len(parts) >= 3:
            headline = parts[0].replace("HEADLINE:", "").strip()
            summary = parts[1].replace("SUMMARY:", "").strip()
            tips_raw = parts[2].replace("TIPS:", "").strip()
            tips = [t.strip().lstrip("•-").strip() for t in tips_raw.split("\n") if len(t.strip()) > 5]
            return {
                "headline_suggestion": headline,
                "summary_suggestion": summary,
                "tips": tips
            }
        return None
    except Exception as e:
        print(f"LLM LinkedIn Error: {e}")
        return None
