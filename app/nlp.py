import re
from typing import List, Set, Tuple, Dict
from rapidfuzz import fuzz
from collections import Counter

try:
    from sentence_transformers import SentenceTransformer, util
    import torch
    print("Loading Semantic Model (all-MiniLM-L6-v2)...")
    semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Semantic Model loaded.")
except ImportError:
    print("Warning: sentence-transformers not installed. Falling back to fuzzy match.")
    semantic_model = None
except Exception as e:
    print(f"Warning: Could not load semantic model: {e}")
    semantic_model = None

# A default taxonomy of common tech skills
TAXONOMY = [
    "AWS", "Azure", "GCP", "Kubernetes", "Docker", "FastAPI", "PostgreSQL",
    "Python", "Java", "JavaScript", "TypeScript", "React", "Angular", "Vue",
    "Machine Learning", "Deep Learning", "NLP", "SQL", "NoSQL", "MongoDB",
    "Redis", "Kafka", "RabbitMQ", "CI/CD", "Git", "Terraform", "Ansible",
    "Linux", "C++", "C#", "Ruby", "PHP", "Go", "Rust", "Swift", "Kotlin",
    "Android", "iOS", "HTML", "CSS", "REST", "GraphQL", "PyTorch", "TensorFlow",
    "Scikit-Learn", "Pandas", "NumPy", "Spark", "Hadoop", "Snowflake", "BigQuery",
    "Airflow", "dbt", "Tableau", "Power BI", "Excel", "Agile", "Scrum",
    "Jira", "Confluence", "Figma", "Sketch", "Photoshop", "Illustrator",
    "Data Analysis", "Data Engineering", "Data Science", "Software Engineering",
    "System Design", "Microservices", "Serverless", "WebSockets",
    "Node.js", "Next.js", "Flask", "Django", "Spring Boot", "Express",
    ".NET", "Elasticsearch", "Grafana", "Prometheus", "Jenkins", "GitHub Actions",
    "AWS Lambda", "S3", "EC2", "DynamoDB", "CloudFormation",
]

# ── Synonym Mapping for Semantic Matching ──
# Maps common abbreviations/aliases to their canonical taxonomy form
SYNONYMS: Dict[str, str] = {
    "k8s": "Kubernetes",
    "kube": "Kubernetes",
    "container orchestration": "Kubernetes",
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "py": "Python",
    "python3": "Python",
    "ml": "Machine Learning",
    "machine learning": "Machine Learning",
    "dl": "Deep Learning",
    "deep learning": "Deep Learning",
    "natural language processing": "NLP",
    "nlp": "NLP",
    "ai": "Machine Learning",
    "artificial intelligence": "Machine Learning",
    "postgres": "PostgreSQL",
    "psql": "PostgreSQL",
    "mongo": "MongoDB",
    "mongodb": "MongoDB",
    "react.js": "React",
    "reactjs": "React",
    "vue.js": "Vue",
    "vuejs": "Vue",
    "angular.js": "Angular",
    "angularjs": "Angular",
    "node": "Node.js",
    "nodejs": "Node.js",
    "nextjs": "Next.js",
    "next.js": "Next.js",
    "scikit learn": "Scikit-Learn",
    "sklearn": "Scikit-Learn",
    "tf": "TensorFlow",
    "tensorflow": "TensorFlow",
    "ci cd": "CI/CD",
    "ci/cd": "CI/CD",
    "continuous integration": "CI/CD",
    "continuous deployment": "CI/CD",
    "amazon web services": "AWS",
    "aws": "AWS",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "microsoft azure": "Azure",
    "power bi": "Power BI",
    "powerbi": "Power BI",
    "elastic search": "Elasticsearch",
    "elastic": "Elasticsearch",
    "github actions": "GitHub Actions",
    "gh actions": "GitHub Actions",
    "lambda": "AWS Lambda",
    "spring": "Spring Boot",
    "springboot": "Spring Boot",
    "expressjs": "Express",
    "express.js": "Express",
    ".net core": ".NET",
    "dotnet": ".NET",
    "c sharp": "C#",
    "csharp": "C#",
    "cpp": "C++",
    "system design": "System Design",
    "distributed systems": "System Design",
}

if semantic_model is not None:
    # Precompute embeddings for the taxonomy to save time during requests
    TAXONOMY_EMBEDDINGS = semantic_model.encode(TAXONOMY, convert_to_tensor=True)
else:
    TAXONOMY_EMBEDDINGS = None

# Minimum fuzzy match score to consider a match
FUZZY_THRESHOLD = 85


def extract_skills(text: str) -> Set[str]:
    """Extracts skills from text using exact matching, synonym resolution, and fuzzy matching."""
    extracted = set()
    text_lower = text.lower()

    for skill in TAXONOMY:
        # 1. Exact match
        if skill.lower() in text_lower:
            extracted.add(skill)
            continue

    # 2. Synonym resolution
    for alias, canonical in SYNONYMS.items():
        if alias in text_lower and canonical in TAXONOMY:
            extracted.add(canonical)

    # 3. Fuzzy/Semantic matching for close variations
    words = text_lower.split()
    # Build n-grams (1, 2, 3 word chunks) for fuzzy matching
    ngrams = []
    for n in range(1, 4):
        for i in range(len(words) - n + 1):
            ngrams.append(" ".join(words[i:i + n]))

    if semantic_model is not None and ngrams:
        # Semantic Matching
        # We only consider a subset of ngrams to avoid extreme overhead on huge resumes,
        # but 1000-2000 ngrams is perfectly fine for MiniLM.
        try:
            ngram_embeddings = semantic_model.encode(ngrams, convert_to_tensor=True)
            cosine_scores = util.cos_sim(ngram_embeddings, TAXONOMY_EMBEDDINGS)
            
            # Find any pairs with score > 0.8
            # cosine_scores is shape (len(ngrams), len(TAXONOMY))
            for i in range(len(ngrams)):
                for j in range(len(TAXONOMY)):
                    if cosine_scores[i][j] > 0.8:
                        extracted.add(TAXONOMY[j])
        except Exception as e:
            print(f"Error during semantic matching: {e}")
            # Fallback to fuzzy
            for skill in TAXONOMY:
                if skill in extracted: continue
                skill_lower = skill.lower()
                for ngram in ngrams:
                    if fuzz.ratio(ngram, skill_lower) >= FUZZY_THRESHOLD:
                        extracted.add(skill)
                        break
    else:
        # Fallback to fuzzy matching
        for skill in TAXONOMY:
            if skill in extracted:
                continue
            skill_lower = skill.lower()
            for ngram in ngrams:
                score = fuzz.ratio(ngram, skill_lower)
                if score >= FUZZY_THRESHOLD:
                    extracted.add(skill)
                    break

    return extracted


def extract_keyword_frequency(text: str, skills: Set[str]) -> Dict[str, int]:
    """Count how many times each skill appears in the text."""
    text_lower = text.lower()
    freq: Dict[str, int] = {}
    for skill in skills:
        count = text_lower.count(skill.lower())
        if count > 0:
            freq[skill] = count
    # Sort by frequency descending
    return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True))


def extract_experience_years(text: str) -> float:
    """Extracts total years of experience from text using regex."""
    # Look for patterns like "5 years of experience", "10+ years", "3 yrs"
    pattern = r'(\d+)(?:\+| years?| yrs?)(?: of)? experience'
    matches = re.findall(pattern, text, re.IGNORECASE)

    if not matches:
        return 0.0

    years = [float(match) for match in matches]
    return max(years) if years else 0.0

def has_degree(text: str) -> bool:
    """Checks for education credentials."""
    patterns = [
        r'\bB\.?S\.?\b', r'\bB\.?A\.?\b', r'\bBachelor(?:s)?\b',
        r'\bM\.?S\.?\b', r'\bM\.?A\.?\b', r'\bMaster(?:s)?\b',
        r'\bPh\.?D\.?\b', r'\bDoctorate\b', r'\bB\.?Tech\b', r'\bM\.?Tech\b'
    ]
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def analyze_resume_vs_jd(resume_text: str, jd_text: str) -> Tuple[Set[str], Set[str], float, bool]:
    """Analyzes a resume against a job description."""
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    matched_skills = resume_skills.intersection(jd_skills)
    missing_skills = jd_skills - resume_skills

    experience = extract_experience_years(resume_text)
    education = has_degree(resume_text)

    return matched_skills, missing_skills, experience, education
