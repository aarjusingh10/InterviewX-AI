import re
from collections import Counter
from app.services.ai_provider import ai_provider

ROLE_KEYWORDS = {
    "ai": {"python", "pytorch", "tensorflow", "rag", "llm", "vector", "ml", "nlp", "deployment"},
    "backend": {"api", "database", "postgresql", "redis", "docker", "auth", "microservices", "testing"},
    "frontend": {"react", "typescript", "accessibility", "state", "performance", "design", "testing"},
    "data": {"sql", "spark", "airflow", "warehouse", "etl", "python", "dbt", "pipeline"},
}


def _lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def _extract_name(lines: list[str]) -> str:
    for line in lines[:8]:
        if 2 <= len(line.split()) <= 4 and not any(token in line.lower() for token in ["email", "phone", "@"]):
            return line
    return "Candidate"


def _extract_section(text: str, names: list[str]) -> list[str]:
    pattern = "|".join(re.escape(name) for name in names)
    match = re.search(rf"(?is)({pattern})\s*[:\n](.*?)(\n[A-Z][A-Za-z ]{{2,25}}\s*[:\n]|$)", text)
    if not match:
        return []
    return [item.strip(" -•\t") for item in re.split(r"[\n;]", match.group(2)) if item.strip()]


def _keyword_hits(text: str) -> list[str]:
    words = set(re.findall(r"[a-zA-Z][a-zA-Z+#.]{1,}", text.lower()))
    known = sorted(set().union(*ROLE_KEYWORDS.values()))
    return [word for word in known if word.lower() in words]


async def analyze_resume(text: str) -> dict:
    lines = _lines(text)
    keywords = _keyword_hits(text)
    projects = _extract_section(text, ["Projects", "Project Experience", "Personal Projects"])
    experience = _extract_section(text, ["Experience", "Work Experience", "Internships"])
    education = _extract_section(text, ["Education", "Academics"])
    certifications = _extract_section(text, ["Certifications", "Courses", "Achievements"])
    skills = _extract_section(text, ["Skills", "Technical Skills"]) or keywords
    word_count = len(re.findall(r"\w+", text))
    quantified = len(re.findall(r"\b\d+%|\b\d+x|\b\d+\+|\b\d{2,}\b", text))
    action_verbs = Counter(re.findall(r"\b(built|designed|deployed|optimized|led|created|implemented|automated|trained|scaled)\b", text.lower()))

    ats = min(98, 45 + len(keywords) * 4 + min(quantified, 8) * 3 + (10 if education else 0))
    strength = min(97, 40 + len(projects) * 8 + len(experience) * 7 + len(action_verbs) * 3)
    internship = min(96, 35 + len(skills) * 3 + len(projects) * 10 + (10 if certifications else 0))
    industry = min(95, 30 + len(experience) * 12 + len(projects) * 7 + min(len(keywords), 12) * 3)

    missing = sorted({"docker", "testing", "deployment", "metrics", "sql", "system design"} - set(keywords))
    weak_projects = [p for p in projects if len(p.split()) < 12 or not re.search(r"\d|deployed|users|latency|accuracy", p, re.I)]
    suggestions = [
        {"area": "Impact", "suggestion": "Add quantified outcomes to each major project and internship bullet."},
        {"area": "Keywords", "suggestion": f"Add evidence-backed keywords: {', '.join(missing[:5])}."},
        {"area": "Projects", "suggestion": "For every project, include problem, architecture, tradeoffs, deployment, and measurable result."},
        {"area": "Readability", "suggestion": "Keep bullets action-led and compress low-signal coursework into one line."},
    ]
    fallback = {
        "parsed": {
            "name": _extract_name(lines),
            "skills": skills[:24],
            "projects": projects[:8],
            "experience": experience[:8],
            "education": education[:4],
            "certifications": certifications[:8],
        },
        "scores": {
            "ats": ats,
            "resume_strength": strength,
            "internship_readiness": internship,
            "industry_readiness": industry,
        },
        "detections": {
            "missing_keywords": missing,
            "weak_projects": weak_projects[:5],
            "missing_skills": missing[:6],
            "poor_sections": [name for name, value in {"experience": experience, "projects": projects, "education": education}.items() if not value],
        },
        "suggestions": suggestions,
    }
    prompt = f"Analyze this resume for InterviewX AI. Extract profile fields, scores, detections, and suggestions.\n{text[:12000]}"
    return await ai_provider.json_task(prompt, fallback)

