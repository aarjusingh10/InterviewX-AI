import re
from statistics import mean
from app.services.ai_provider import ai_provider
from app.services.knowledge_base import knowledge_base

PERSONALITIES = {
    "Friendly Recruiter": "warm, encouraging, conversational, explains transitions clearly",
    "Startup Founder": "fast-paced, product-minded, asks about ownership, ambiguity, and business impact",
    "Senior Engineer": "practical, systems-oriented, probes tradeoffs and implementation quality",
    "FAANG Interviewer": "structured, rigorous, expects complexity analysis and edge cases",
    "HR Manager": "behavioral, values clarity, motivation, teamwork, and communication",
}

ROLE_KEYWORD_MAP = {
    "engineering": ["api", "database", "deploy", "test", "architecture", "latency", "scalable", "cache", "security", "monitoring", "docker", "cloud"],
    "ai": ["model", "algorithm", "dataset", "accuracy", "precision", "recall", "overfitting", "features", "training", "inference", "rag", "embedding"],
    "marketing": ["campaign", "conversion", "funnel", "seo", "cac", "roi", "segment", "channel", "brand", "creative", "lead", "retention"],
    "sales": ["lead", "pipeline", "discovery", "objection", "crm", "quota", "close", "demo", "prospect", "follow-up", "negotiation"],
    "product": ["user", "roadmap", "prioritize", "metric", "experiment", "activation", "retention", "feedback", "mvp", "stakeholder"],
    "design": ["user", "prototype", "accessibility", "wireframe", "usability", "research", "design system", "interaction", "handoff"],
    "business": ["kpi", "revenue", "cost", "forecast", "dashboard", "process", "stakeholder", "risk", "operations", "analysis"],
}


def _clamp(value: float, minimum: int = 0, maximum: int = 100) -> int:
    return max(minimum, min(maximum, round(value)))


def _role_family(role: str) -> str:
    lower = role.lower()
    if "ai" in lower or "ml" in lower or "data scientist" in lower:
        return "ai"
    if "marketing" in lower:
        return "marketing"
    if "sales" in lower:
        return "sales"
    if "product" in lower:
        return "product"
    if "design" in lower or "ui/ux" in lower or "graphic" in lower:
        return "design"
    if "finance" in lower or "business" in lower or "operations" in lower:
        return "business"
    return "engineering"


def _count_matches(text: str, terms: list[str]) -> int:
    lower = text.lower()
    return sum(1 for term in terms if term in lower)


def _signal_score(answer: str, role: str) -> dict:
    lower = answer.lower()
    token_count = len(re.findall(r"[a-z0-9+#.%-]+", lower))
    family = _role_family(role)
    role_hits = _count_matches(lower, ROLE_KEYWORD_MAP[family])
    universal_hits = _count_matches(lower, ["because", "tradeoff", "measured", "result", "impact", "challenge", "improved", "learned", "customer", "user"])
    metrics = len(re.findall(r"\b\d+%|\b\d+x|\b\d+\+|\b\d{2,}\b", lower))
    star = _count_matches(lower, ["situation", "task", "action", "result", "problem", "solution", "outcome"])
    filler = _count_matches(lower, ["maybe", "kind of", "sort of", "stuff", "things", "basically"])
    return {
        "token_count": token_count,
        "role_hits": role_hits,
        "universal_hits": universal_hits,
        "metrics": metrics,
        "star": star,
        "filler": filler,
        "length_score": _clamp((token_count / 75) * 100),
        "specificity": _clamp(role_hits * 12 + universal_hits * 5 + metrics * 10 + star * 4 - filler * 8),
    }


def _question_bank(role: str, difficulty: str, resume: dict | None, context: list[str]) -> list[dict]:
    skills = ", ".join((resume or {}).get("skills", [])[:8]) or "the candidate's strongest listed skills"
    projects = (resume or {}).get("projects", [])
    project_ref = projects[0] if projects else "a recent technical project"
    diff = difficulty.lower()
    role_name = role.strip()
    hardener = "Include tradeoffs, failure modes, and measurable impact." if diff in {"advanced", "faang"} else "Explain your reasoning clearly."
    role_lower = role.lower()
    if "marketing" in role_lower:
        prompts = [
            "Walk me through a campaign you would plan from audience research to conversion reporting.",
            "How would you reduce customer acquisition cost without lowering lead quality?",
            "Which channels would you test first for a new startup product and why?",
            "How do you measure brand awareness, demand generation, and campaign ROI?",
            "Tell me about a failed campaign and what you changed after reading the data.",
            "How would you use AI tools in content, SEO, segmentation, and reporting?",
            "Pitch a 30-day launch plan for InterviewX AI.",
            "How do you align marketing work with sales and product teams?",
        ]
        return [{"id": f"q{i+1}", "text": text, "type": "core"} for i, text in enumerate(prompts)]
    if "sales" in role_lower:
        prompts = [
            "How would you qualify a lead and decide whether to continue the sales cycle?",
            "Give me your discovery call structure for a B2B SaaS product.",
            "How do you handle pricing objections without discounting too early?",
            "What metrics do you track daily and weekly as a sales professional?",
            "Role-play a pitch for InterviewX AI to a college placement cell.",
            "Tell me about a deal you lost and what you learned.",
            "How would you build trust with a skeptical buyer?",
            "How do you use CRM data to improve follow-ups?",
        ]
        return [{"id": f"q{i+1}", "text": text, "type": "core"} for i, text in enumerate(prompts)]
    if "product" in role_lower:
        prompts = [
            "How would you prioritize features for InterviewX AI with limited engineering time?",
            "Define success metrics for resume analysis, mock interviews, and paid conversion.",
            "How would you collect customer feedback and turn it into a roadmap?",
            "Explain a product tradeoff between user delight and technical complexity.",
            "How would you run an experiment to improve activation?",
            "What would you build for recruiters versus candidates?",
            "Tell me about a time you influenced without authority.",
            "How would you handle a feature request from a large customer that hurts the core product?",
        ]
        return [{"id": f"q{i+1}", "text": text, "type": "core"} for i, text in enumerate(prompts)]
    if "designer" in role_lower or "ui/ux" in role_lower:
        prompts = [
            "Walk me through your design process from problem discovery to shipped interface.",
            "How do you make a dashboard usable for first-time and power users?",
            "How would you improve the InterviewX AI onboarding screen?",
            "What signals tell you a design is working beyond visual polish?",
            "Tell me about a design decision you defended with user evidence.",
            "How do you handle accessibility, empty states, and responsive layouts?",
            "How do you collaborate with engineers during handoff?",
            "What would you change if conversion improved but user trust decreased?",
        ]
        return [{"id": f"q{i+1}", "text": text, "type": "core"} for i, text in enumerate(prompts)]
    if "finance" in role_lower or "business analyst" in role_lower or "operations" in role_lower:
        prompts = [
            "How do you break down an ambiguous business problem into measurable drivers?",
            "Which KPIs would you track for a SaaS interview platform?",
            "Explain a time you used data to influence a decision.",
            "How would you forecast revenue for a freemium AI product?",
            "What dashboard would you build for founders and why?",
            "How do you check whether a dataset or report is trustworthy?",
            "Tell me about a process you improved and the impact it created.",
            "How would you balance growth, cost, and customer experience?",
        ]
        return [{"id": f"q{i+1}", "text": text, "type": "core"} for i, text in enumerate(prompts)]
    prompts = [
        f"Walk me through your background for a {role_name} role, focusing on {skills}.",
        f"Pick {project_ref}. What problem did it solve, and how did you design the architecture?",
        f"What technical decision in your resume would you defend under production constraints? {hardener}",
        f"How would you debug a production issue where latency increases after a release?",
        f"Describe a time you learned a difficult concept quickly and applied it.",
        f"Use the retrieved topic context to answer: {context[0] if context else 'system design and fundamentals'}.",
        "Tell me about a mistake in a project and how you corrected it.",
        "What would you improve in your strongest project if you had two more weeks?",
    ]
    if "ml" in role.lower() or "ai" in role.lower() or "data scientist" in role.lower():
        prompts.extend(
            [
                "How do you choose evaluation metrics for an ML model, and when can accuracy be misleading?",
                "How would you prevent overfitting and monitor model quality after deployment?",
            ]
        )
    if "frontend" in role.lower():
        prompts.extend(["How do you make a React interface fast and accessible?", "Explain a state management tradeoff you have made."])
    if "backend" in role.lower() or "software" in role.lower() or "full stack" in role.lower():
        prompts.extend(["Design an authenticated API for interview history at scale.", "How do you choose between SQL and NoSQL for a new feature?"])
    return [{"id": f"q{i+1}", "text": text, "type": "core"} for i, text in enumerate(prompts[:10])]


async def generate_questions(role: str, difficulty: str, personality: str, resume: dict | None) -> list[dict]:
    retrieved = knowledge_base.retrieve(f"{role} {difficulty} {resume or {}}", limit=5)
    context = [item.content for item in retrieved]
    fallback = {"questions": _question_bank(role, difficulty, resume, context)}
    prompt = (
        f"Generate 10 dynamic interview questions for role={role}, difficulty={difficulty}, "
        f"interviewer personality={personality} ({PERSONALITIES.get(personality, 'professional')}). "
        f"Resume profile={resume}. Retrieved knowledge={context}. Return JSON with questions array of id,text,type."
    )
    result = await ai_provider.json_task(prompt, fallback)
    return result.get("questions", fallback["questions"])


def generate_follow_up(answer: str, role: str) -> str:
    lower = answer.lower()
    if any(term in lower for term in ["campaign", "seo", "conversion", "brand"]):
        return "Which metric would prove that campaign worked, and how would you improve it after week one?"
    if any(term in lower for term in ["customer", "sales", "lead", "deal"]):
        return "How would you qualify that customer and handle the strongest objection?"
    if any(term in lower for term in ["roadmap", "feature", "user", "product"]):
        return "How would you prioritize that against other user needs and business goals?"
    if any(term in lower for term in ["design", "ux", "interface", "prototype"]):
        return "What user evidence would validate that design decision?"
    if any(term in lower for term in ["flask", "django", "fastapi"]):
        return "Why did you choose that web framework, and how did routing, validation, and deployment work?"
    if any(term in lower for term in ["model", "algorithm", "accuracy", "overfit", "regression", "classification"]):
        return "Why was that algorithm appropriate, what metrics did you use, and how did you avoid overfitting?"
    if any(term in lower for term in ["database", "postgres", "sql", "mongodb"]):
        return "How did you design the schema, indexes, and consistency guarantees for that data layer?"
    if any(term in lower for term in ["deploy", "docker", "aws", "vercel", "render"]):
        return "What did your deployment pipeline look like, and how would you roll back a bad release?"
    if any(term in lower for term in ["team", "lead", "conflict", "mentor"]):
        return "What was your exact role, and how did your decision change the team outcome?"
    if "frontend" in role.lower() or "react" in lower:
        return "How did you handle state, performance, accessibility, and edge-case UI states?"
    return "What tradeoff did you make there, and what evidence tells you it was the right choice?"


async def score_interview(role: str, difficulty: str, transcript: list[dict]) -> dict:
    answers = [turn.get("answer", "") for turn in transcript if turn.get("answer")]
    combined = " ".join(answers)
    signals = [_signal_score(answer, role) for answer in answers]
    avg_length = mean([signal["length_score"] for signal in signals] or [0])
    avg_specificity = mean([signal["specificity"] for signal in signals] or [0])
    role_coverage = _clamp(mean([signal["role_hits"] for signal in signals] or [0]) * 18)
    metric_coverage = _clamp(mean([signal["metrics"] for signal in signals] or [0]) * 22)
    structure_coverage = _clamp(mean([signal["star"] for signal in signals] or [0]) * 14)
    filler_penalty = _clamp(mean([signal["filler"] for signal in signals] or [0]) * 9, 0, 35)
    confidence_signal = mean([(turn.get("confidence_signal") or 0.55) * 100 for turn in transcript] or [55])
    leadership_hits = _count_matches(combined, ["led", "owned", "managed", "collaborated", "stakeholder", "mentored", "negotiated", "aligned"])
    reasoning_hits = _count_matches(combined, ["because", "therefore", "tradeoff", "constraint", "risk", "alternative", "measured"])
    technical = _clamp(28 + role_coverage * 0.55 + avg_specificity * 0.32 + metric_coverage * 0.2 - filler_penalty * 0.35)
    communication = _clamp(34 + avg_length * 0.34 + structure_coverage * 0.28 + confidence_signal * 0.22 - filler_penalty * 0.5)
    clarity = _clamp(36 + structure_coverage * 0.42 + reasoning_hits * 5 + metric_coverage * 0.18 - filler_penalty * 0.6)
    confidence = _clamp(30 + confidence_signal * 0.48 + avg_length * 0.18 + len(transcript) * 3 - filler_penalty * 0.35)
    problem = _clamp(30 + reasoning_hits * 7 + metric_coverage * 0.26 + role_coverage * 0.24 + structure_coverage * 0.2)
    leadership = _clamp(35 + leadership_hits * 9 + _count_matches(combined, ["customer", "user", "team", "business", "impact"]) * 4 + structure_coverage * 0.18)
    breakdown = {
        "technical_knowledge": technical,
        "communication": communication,
        "confidence": confidence,
        "clarity": clarity,
        "problem_solving": problem,
        "leadership": leadership,
    }
    difficulty_multiplier = 0.92 if difficulty == "FAANG" else 0.96 if difficulty == "Advanced" else 1.04 if difficulty == "Beginner" else 1
    overall = _clamp(mean(breakdown.values()) * difficulty_multiplier)
    fallback = {
        "overall": overall,
        "breakdown": breakdown,
        "formula": {
            "role_keyword_coverage": role_coverage,
            "metric_coverage": metric_coverage,
            "answer_depth": round(avg_length),
            "structure_coverage": structure_coverage,
            "filler_penalty": filler_penalty,
            "difficulty_multiplier": difficulty_multiplier,
        },
        "feedback": "Score is calculated from role keyword coverage, measurable evidence, answer depth, STAR structure, reasoning, confidence, and filler-word penalty.",
    }
    return fallback


def detect_weaknesses(transcript: list[dict], scores: dict) -> list[dict]:
    breakdown = scores.get("breakdown", {})
    weaknesses = []
    combined = " ".join(turn.get("answer", "") for turn in transcript if turn.get("answer")).lower()
    answer_lengths = [len(turn.get("answer", "").split()) for turn in transcript if turn.get("answer")]
    avg_words = round(mean(answer_lengths or [0]))

    def add(area: str, severity: str, explanation: str) -> None:
        if not any(item["area"] == area for item in weaknesses):
            weaknesses.append({"area": area, "severity": severity, "explanation": explanation})

    if avg_words < 22:
        add("Answer Depth", "High", f"Average answer length is {avg_words} words. Use a complete example with context, action, result, and lesson.")
    if not re.search(r"\b\d+%|\b\d+x|\b\d+\+|\b\d{2,}\b", combined):
        add("Missing Metrics", "High", "Answers do not include measurable proof. Add numbers such as revenue, users, conversion, latency, accuracy, cost, or time saved.")
    if not re.search(r"\btradeoff|because|therefore|instead|alternative|risk|constraint\b", combined):
        add("Decision Reasoning", "Medium", "Answers need clearer reasoning. Compare alternatives and explain the constraint behind each decision.")
    if not re.search(r"\bdeployed|launched|shipped|published|production|campaign|customer|stakeholder|user\b", combined):
        add("Real-World Impact", "Medium", "Answers need stronger real-world context. Mention who used the work, what changed, and how success was checked.")
    if re.search(r"\bmaybe|kind of|sort of|basically|stuff|things\b", combined):
        add("Communication Precision", "Medium", "Some wording sounds vague. Replace filler with concrete nouns, exact actions, and outcome statements.")

    for key, value in breakdown.items():
        if value < 72:
            add(key.replace("_", " ").title(), "High" if value < 60 else "Medium", f"Score is {value}/100. Add a specific example, measurable result, and clearer structure for this dimension.")
    if not weaknesses:
        weaknesses.append(
            {
                "area": "Depth Under Follow-Up",
                "severity": "Low",
                "explanation": "Performance is solid; next improvement is answering deeper follow-ups with metrics and tradeoffs faster.",
            }
        )
    return weaknesses


def generate_roadmap(role: str, weaknesses: list[dict]) -> dict:
    focus = [item["area"] for item in weaknesses[:4]]
    return {
        "title": f"30-Day {role} Interview Upgrade Plan",
        "focus_areas": focus,
        "weekly_goals": [
            "Week 1: repair fundamentals and rewrite resume stories using STAR plus technical tradeoffs.",
            "Week 2: build one production-style project feature with tests, deployment, and observability.",
            "Week 3: practice role-specific system, coding, ML, or behavioral interviews daily.",
            "Week 4: simulate full interviews, review recordings, and optimize weak score dimensions.",
        ],
        "daily_tasks": [
            "45 minutes fundamentals review",
            "45 minutes project or coding practice",
            "20 minutes spoken answer rehearsal",
            "10 minutes reflection with one measurable improvement",
        ],
        "projects_to_build": [
            "Role-specific analytics dashboard with authentication and PostgreSQL",
            "RAG assistant or scalable API service with monitoring",
            "Deployment-ready portfolio project with tests and CI",
        ],
        "technologies_to_learn": ["Docker", "PostgreSQL", "Testing", "System Design", "Cloud Deployment"],
        "recommended_courses": ["DeepLearning.AI short courses", "FastAPI production patterns", "NeetCode roadmap", "System Design Primer"],
        "leetcode": ["Two Sum", "Valid Parentheses", "Binary Search", "LRU Cache", "Number of Islands", "Top K Frequent Elements"],
    }


def premium_metrics(scores: dict, role: str, transcript: list[dict]) -> dict:
    overall = scores.get("overall", 0)
    salary_base = {
        "AI Engineer": 135000,
        "ML Engineer": 132000,
        "Data Scientist": 125000,
        "Backend Developer": 118000,
        "Frontend Developer": 112000,
        "Full Stack Developer": 120000,
        "Software Engineer": 122000,
    }.get(role, 105000)
    multiplier = 0.72 + overall / 250
    return {
        "hiring_probability": min(96, max(12, round(overall * 0.92))),
        "salary_prediction_usd": {"low": round(salary_base * (multiplier - 0.12)), "mid": round(salary_base * multiplier), "high": round(salary_base * (multiplier + 0.18))},
        "skill_ranking": sorted(scores.get("breakdown", {}).items(), key=lambda item: item[1], reverse=True),
        "confidence_detection": round(mean([(turn.get("confidence_signal") or 0.72) * 100 for turn in transcript] or [72])),
        "eye_contact_analysis": round(mean([(turn.get("eye_contact_signal") or 0.68) * 100 for turn in transcript] or [68])),
        "body_language_analysis": "Stable" if overall >= 75 else "Needs more controlled pacing and posture during complex explanations",
    }
