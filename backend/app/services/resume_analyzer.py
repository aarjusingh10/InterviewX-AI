import re
from collections import Counter
from statistics import mean
from app.services.ai_provider import ai_provider

ROLE_KEYWORDS = {
    "ai": {"python", "pytorch", "tensorflow", "rag", "llm", "vector", "ml", "nlp", "deployment"},
    "backend": {"api", "database", "postgresql", "redis", "docker", "auth", "microservices", "testing"},
    "frontend": {"react", "typescript", "accessibility", "state", "performance", "design", "testing"},
    "data": {"sql", "spark", "airflow", "warehouse", "etl", "python", "dbt", "pipeline"},
}


def _clamp(value: float, minimum: int = 0, maximum: int = 100) -> int:
    return max(minimum, min(maximum, round(value)))


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
    bullet_count = len(re.findall(r"(?m)^\s*[-*•]", text))
    contact_signal = 1 if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text) else 0
    link_signal = len(re.findall(r"github|linkedin|portfolio|kaggle|behance|dribbble", text.lower()))
    section_count = sum(1 for section in [skills, projects, experience, education, certifications] if section)
    keyword_density = len(keywords) / max(1, word_count / 120)
    project_depth = mean([len(project.split()) for project in projects] or [0])
    weak_language = len(re.findall(r"\b(responsible for|helped|worked on|basic|familiar|some)\b", text.lower()))

    ats = _clamp(
        28
        + section_count * 7
        + min(keyword_density, 10) * 3.2
        + min(quantified, 8) * 2.8
        + contact_signal * 5
        + min(link_signal, 3) * 2
        - max(0, 350 - word_count) * 0.035
        - weak_language * 1.8
    )
    strength = _clamp(
        25
        + min(len(projects), 4) * 8
        + min(len(experience), 5) * 7
        + min(len(action_verbs), 10) * 2.6
        + min(project_depth, 45) * 0.45
        + min(quantified, 10) * 2.5
        - weak_language * 2
    )
    internship = _clamp(
        30
        + min(len(skills), 14) * 2.4
        + min(len(projects), 3) * 9
        + (8 if education else 0)
        + (6 if certifications else 0)
        + min(bullet_count, 10) * 1.3
    )
    industry = _clamp(
        24
        + min(len(experience), 5) * 9
        + min(len(projects), 4) * 6
        + min(len(keywords), 14) * 2.5
        + min(quantified, 10) * 3
        + min(link_signal, 3) * 2
        - weak_language * 2
    )

    missing = sorted({"docker", "testing", "deployment", "metrics", "sql", "system design"} - set(keywords))
    weak_projects = [p for p in projects if len(p.split()) < 12 or not re.search(r"\d|deployed|users|latency|accuracy", p, re.I)]
    suggestions = [
        {"area": "Impact", "suggestion": f"Detected {quantified} quantified signals. Add numbers to every project and experience bullet for more reliable scoring."},
        {"area": "Keywords", "suggestion": f"Keyword density is {keyword_density:.1f} per 120 words. Add evidence-backed keywords: {', '.join(missing[:5])}."},
        {"area": "Projects", "suggestion": f"Average project depth is {round(project_depth)} words. Strong projects should include problem, architecture, tradeoffs, deployment, and measurable result."},
        {"area": "Readability", "suggestion": f"Detected {weak_language} weak phrasing signals. Replace vague verbs with built, shipped, improved, automated, led, or measured."},
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
    return fallback
