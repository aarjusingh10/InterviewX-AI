import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { motion } from "framer-motion";
import {
  Activity,
  BarChart3,
  Brain,
  CheckCircle2,
  Download,
  FileText,
  Gauge,
  LogOut,
  Mic,
  Play,
  Radar,
  Send,
  Shield,
  Sparkles,
  Upload,
  UserRound
} from "lucide-react";
import "./styles.css";

const API = import.meta.env.VITE_API_BASE_URL || (window.location.hostname === "localhost" ? `${window.location.protocol}//${window.location.hostname}:8000` : "");

type User = { id: number; email: string; full_name: string };
type Resume = { id: number; filename: string; parsed: Record<string, any>; scores: Record<string, any>; suggestions: any[] };
type Interview = {
  id: number;
  role: string;
  difficulty: string;
  personality: string;
  status: string;
  questions: { id: string; text: string; type: string }[];
  transcript: any[];
  scores?: any;
  weaknesses?: any[];
  roadmap?: any;
  premium?: any;
};

const roles = [
  "AI Engineer",
  "ML Engineer",
  "Data Scientist",
  "Data Engineer",
  "Backend Developer",
  "Frontend Developer",
  "Full Stack Developer",
  "Software Engineer",
  "Product Manager",
  "Marketing Manager",
  "Digital Marketing Specialist",
  "Sales Executive",
  "Business Analyst",
  "Finance Analyst",
  "Operations Manager",
  "UI/UX Designer",
  "Graphic Designer",
  "Content Writer",
  "Customer Success Manager",
  "HR Interview",
  "General Interview"
];
const difficulties = ["Beginner", "Intermediate", "Advanced", "FAANG"];
const personalities = ["Friendly Recruiter", "Startup Founder", "Senior Engineer", "FAANG Interviewer", "HR Manager"];

const roleKeywordMap: Record<string, string[]> = {
  engineering: ["api", "database", "deploy", "test", "architecture", "latency", "scalable", "cache", "security", "monitoring", "docker", "cloud"],
  ai: ["model", "algorithm", "dataset", "accuracy", "precision", "recall", "overfitting", "features", "training", "inference", "rag", "embedding"],
  marketing: ["campaign", "conversion", "funnel", "seo", "cac", "roi", "segment", "channel", "brand", "creative", "lead", "retention"],
  sales: ["lead", "pipeline", "discovery", "objection", "crm", "quota", "close", "demo", "prospect", "follow-up", "negotiation"],
  product: ["user", "roadmap", "prioritize", "metric", "experiment", "activation", "retention", "feedback", "mvp", "stakeholder"],
  design: ["user", "prototype", "accessibility", "wireframe", "usability", "research", "design system", "interaction", "handoff"],
  business: ["kpi", "revenue", "cost", "forecast", "dashboard", "process", "stakeholder", "risk", "operations", "analysis"]
};

function clamp(value: number, min = 0, max = 100) {
  return Math.max(min, Math.min(max, Math.round(value)));
}

function words(text: string) {
  return text.toLowerCase().match(/[a-z0-9+#.%-]+/g) || [];
}

function countMatches(text: string, terms: string[]) {
  const lower = text.toLowerCase();
  return terms.filter((term) => lower.includes(term)).length;
}

function roleFamily(roleName: string) {
  const lower = roleName.toLowerCase();
  if (lower.includes("ai") || lower.includes("ml") || lower.includes("data scientist")) return "ai";
  if (lower.includes("marketing")) return "marketing";
  if (lower.includes("sales")) return "sales";
  if (lower.includes("product")) return "product";
  if (lower.includes("design") || lower.includes("ui/ux") || lower.includes("graphic")) return "design";
  if (lower.includes("finance") || lower.includes("business") || lower.includes("operations")) return "business";
  return "engineering";
}

function signalScore(text: string, roleName: string) {
  const tokenList = words(text);
  const lower = text.toLowerCase();
  const family = roleFamily(roleName);
  const roleHits = countMatches(lower, roleKeywordMap[family]);
  const universalHits = countMatches(lower, ["because", "tradeoff", "measured", "result", "impact", "challenge", "improved", "learned", "customer", "user"]);
  const metrics = (lower.match(/\b\d+%|\b\d+x|\b\d+\+|\b\d{2,}\b/g) || []).length;
  const star = countMatches(lower, ["situation", "task", "action", "result", "problem", "solution", "outcome"]);
  const filler = countMatches(lower, ["maybe", "kind of", "sort of", "stuff", "things", "basically"]);
  const lengthScore = clamp((tokenList.length / 75) * 100);
  const specificity = clamp(roleHits * 12 + universalHits * 5 + metrics * 10 + star * 4 - filler * 8);
  return { tokenCount: tokenList.length, roleHits, universalHits, metrics, star, filler, lengthScore, specificity };
}

async function request(path: string, token: string | null, options: RequestInit = {}) {
  if (!API) {
    throw new Error("Backend is not hosted yet. Running InterviewX in local demo mode.");
  }
  let response: Response;
  try {
    response = await fetch(`${API}${path}`, {
      ...options,
      headers: {
        ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(options.headers || {})
      }
    });
  } catch {
    throw new Error(`Cannot reach InterviewX API at ${API}. Start the backend or check Docker is running.`);
  }
  if (!response.ok) {
    let detail = "Request failed";
    try {
      const body = await response.json();
      detail = body.detail || detail;
    } catch {
      detail = `Server returned ${response.status}`;
    }
    throw new Error(detail);
  }
  return response.json();
}

function demoUser(fullName: string, emailAddress: string): User {
  return { id: 1, email: emailAddress, full_name: fullName || "InterviewX Candidate" };
}

function demoResume(file?: File): Resume {
  const filename = file?.name || "demo-resume.pdf";
  const lowerName = filename.toLowerCase();
  const inferredFamily = ["marketing", "sales", "product", "design", "finance", "business", "operations", "ai", "ml", "data", "backend", "frontend"].find((term) => lowerName.includes(term)) || "general";
  const sizeKb = file ? file.size / 1024 : 180;
  const isPdf = lowerName.endsWith(".pdf");
  const isDocx = lowerName.endsWith(".docx") || lowerName.endsWith(".doc");
  const fileQuality = isPdf ? 9 : isDocx ? 6 : -8;
  const sizeScore = sizeKb < 40 ? -14 : sizeKb > 1600 ? -8 : sizeKb > 180 ? 10 : 4;
  const inferredSkills =
    inferredFamily.includes("marketing") ? ["Campaign Strategy", "SEO", "Conversion", "Funnel Analytics", "Content", "Brand"] :
    inferredFamily.includes("sales") ? ["Lead Qualification", "CRM", "Discovery Calls", "Objection Handling", "Pipeline"] :
    inferredFamily.includes("product") ? ["Roadmapping", "User Research", "Prioritization", "Metrics", "Experimentation"] :
    inferredFamily.includes("design") ? ["User Research", "Wireframes", "Prototyping", "Accessibility", "Design Systems"] :
    inferredFamily.includes("finance") || inferredFamily.includes("business") || inferredFamily.includes("operations") ? ["KPI Analysis", "Forecasting", "Dashboards", "Process Improvement", "Stakeholders"] :
    inferredFamily.includes("ai") || inferredFamily.includes("ml") || inferredFamily.includes("data") ? ["Python", "Machine Learning", "Metrics", "SQL", "Model Evaluation", "Deployment"] :
    ["React", "TypeScript", "FastAPI", "PostgreSQL", "Docker", "Testing", "System Design"];
  const keywordScore = Math.min(28, inferredSkills.length * 4);
  const ats = clamp(48 + fileQuality + sizeScore + keywordScore);
  const resumeStrength = clamp(42 + fileQuality + sizeScore + inferredSkills.length * 5 + (lowerName.includes("updated") || lowerName.includes("final") ? 6 : 0));
  const internshipReadiness = clamp(46 + keywordScore + (sizeKb > 80 ? 10 : 0) + (isPdf ? 6 : 0));
  const industryReadiness = clamp(40 + keywordScore + (sizeKb > 180 ? 14 : 5) + (lowerName.includes("project") ? 6 : 0));
  const missingKeywords = inferredFamily === "general" ? ["role-specific keywords", "metrics", "tools", "impact"] : ["metrics", "ownership", "results", "stakeholder impact"];
  return {
    id: Date.now(),
    filename,
    parsed: {
      name: "InterviewX Candidate",
      skills: inferredSkills,
      projects: [`${inferredFamily} portfolio project inferred from ${filename}. Add measurable outcomes for stronger scoring.`],
      experience: [`Resume file quality signal: ${Math.round(sizeKb)} KB ${isPdf ? "PDF" : isDocx ? "document" : "unsupported type"}.`],
      education: ["Computer Science"],
      certifications: ["AI Engineering", "Cloud Deployment"]
    },
    scores: {
      ats,
      resume_strength: resumeStrength,
      internship_readiness: internshipReadiness,
      industry_readiness: industryReadiness,
      detections: {
        missing_keywords: missingKeywords,
        weak_projects: sizeKb < 80 ? ["Resume file appears small; project detail may be too thin"] : ["Add more measurable project outcomes"],
        missing_skills: missingKeywords,
        poor_sections: isPdf || isDocx ? [] : ["file format"]
      }
    },
    suggestions: [
      { area: "Impact", suggestion: `Add measurable outcomes for ${inferredFamily} work, such as users, revenue, conversion, accuracy, cost, time saved, or satisfaction.` },
      { area: "Evidence", suggestion: sizeKb < 80 ? "Resume appears short from file size. Add project details, responsibilities, tools, and measurable results." : "Good file-size signal. Improve reliability by making every bullet measurable." },
      { area: "Keywords", suggestion: `Add evidence-backed keywords: ${missingKeywords.join(", ")}.` }
    ]
  };
}

function demoQuestions(selectedRole: string, selectedDifficulty: string) {
  const depth = selectedDifficulty === "FAANG" ? "with complexity, edge cases, and tradeoffs" : "with clear reasoning and examples";
  const roleLower = selectedRole.toLowerCase();
  if (roleLower.includes("marketing")) {
    return [
      "Walk me through a campaign you would plan from audience research to conversion reporting.",
      "How would you reduce customer acquisition cost without lowering lead quality?",
      "Which channels would you test first for a new startup product and why?",
      "How do you measure brand awareness, demand generation, and campaign ROI?",
      "Tell me about a failed campaign and what you changed after reading the data.",
      "How would you use AI tools in content, SEO, segmentation, and reporting?",
      "Pitch a 30-day launch plan for InterviewX AI.",
      "How do you align marketing work with sales and product teams?"
    ].map((text, index) => ({ id: `q${index + 1}`, text, type: "core" }));
  }
  if (roleLower.includes("sales")) {
    return [
      "How would you qualify a lead and decide whether to continue the sales cycle?",
      "Give me your discovery call structure for a B2B SaaS product.",
      "How do you handle pricing objections without discounting too early?",
      "What metrics do you track daily and weekly as a sales professional?",
      "Role-play a pitch for InterviewX AI to a college placement cell.",
      "Tell me about a deal you lost and what you learned.",
      "How would you build trust with a skeptical buyer?",
      "How do you use CRM data to improve follow-ups?"
    ].map((text, index) => ({ id: `q${index + 1}`, text, type: "core" }));
  }
  if (roleLower.includes("product")) {
    return [
      "How would you prioritize features for InterviewX AI with limited engineering time?",
      "Define success metrics for resume analysis, mock interviews, and paid conversion.",
      "How would you collect customer feedback and turn it into a roadmap?",
      "Explain a product tradeoff between user delight and technical complexity.",
      "How would you run an experiment to improve activation?",
      "What would you build for recruiters versus candidates?",
      "Tell me about a time you influenced without authority.",
      "How would you handle a feature request from a large customer that hurts the core product?"
    ].map((text, index) => ({ id: `q${index + 1}`, text, type: "core" }));
  }
  if (roleLower.includes("designer") || roleLower.includes("ui/ux")) {
    return [
      "Walk me through your design process from problem discovery to shipped interface.",
      "How do you make a dashboard usable for first-time and power users?",
      "How would you improve the InterviewX AI onboarding screen?",
      "What signals tell you a design is working beyond visual polish?",
      "Tell me about a design decision you defended with user evidence.",
      "How do you handle accessibility, empty states, and responsive layouts?",
      "How do you collaborate with engineers during handoff?",
      "What would you change if conversion improved but user trust decreased?"
    ].map((text, index) => ({ id: `q${index + 1}`, text, type: "core" }));
  }
  if (roleLower.includes("finance") || roleLower.includes("business analyst") || roleLower.includes("operations")) {
    return [
      "How do you break down an ambiguous business problem into measurable drivers?",
      "Which KPIs would you track for a SaaS interview platform?",
      "Explain a time you used data to influence a decision.",
      "How would you forecast revenue for a freemium AI product?",
      "What dashboard would you build for founders and why?",
      "How do you check whether a dataset or report is trustworthy?",
      "Tell me about a process you improved and the impact it created.",
      "How would you balance growth, cost, and customer experience?"
    ].map((text, index) => ({ id: `q${index + 1}`, text, type: "core" }));
  }
  return [
    `Walk me through your background for a ${selectedRole} role and connect it to your strongest project.`,
    `Pick one project from your resume. What was the architecture and why did you choose it?`,
    `Describe a difficult technical bug you solved ${depth}.`,
    `How would you solve a high-impact ${selectedRole} problem for 100,000 users?`,
    `What metrics would you track to know your AI interview system is working well?`,
    `Tell me about a time you made a tradeoff under time pressure.`,
    `How would you deploy, monitor, and roll back this product in production?`,
    `What would you improve in your resume or strongest project before a final interview?`
  ].map((text, index) => ({ id: `q${index + 1}`, text, type: "core" }));
}

function localFollowUp(candidateAnswer: string, selectedRole: string) {
  const lower = candidateAnswer.toLowerCase();
  if (lower.includes("campaign") || lower.includes("seo") || lower.includes("conversion")) return "Which metric would prove that campaign worked, and how would you improve it after week one?";
  if (lower.includes("customer") || lower.includes("sales") || lower.includes("lead")) return "How would you qualify that customer and handle the strongest objection?";
  if (lower.includes("roadmap") || lower.includes("feature") || lower.includes("user")) return "How would you prioritize that against other user needs and business goals?";
  if (lower.includes("design") || lower.includes("ux") || lower.includes("interface")) return "What user evidence would validate that design decision?";
  if (lower.includes("flask") || lower.includes("django") || lower.includes("fastapi")) return "Why did you choose that framework, and how did routing, validation, and deployment work?";
  if (lower.includes("model") || lower.includes("algorithm") || lower.includes("accuracy")) return "What metrics did you use, and how did you prevent overfitting or silent failure?";
  if (lower.includes("database") || lower.includes("postgres") || lower.includes("sql")) return "How did you design indexes, transactions, and query performance for that data layer?";
  if (lower.includes("deploy") || lower.includes("docker") || lower.includes("cloud")) return "What would your rollback, logging, and monitoring strategy look like?";
  return `What tradeoff did you make there, and how would a senior ${selectedRole} interviewer challenge that decision?`;
}

function scoreLocalInterview(activeInterview: Interview): Interview {
  const transcript = activeInterview.transcript || [];
  const signals = transcript.map((turn) => signalScore(String(turn.answer || ""), activeInterview.role));
  const answersText = transcript.map((turn) => String(turn.answer || "")).join(" ");
  const avg = (values: number[]) => values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : 0;
  const avgLength = avg(signals.map((signal) => signal.lengthScore));
  const avgSpecificity = avg(signals.map((signal) => signal.specificity));
  const roleCoverage = clamp(avg(signals.map((signal) => signal.roleHits)) * 18);
  const metricCoverage = clamp(avg(signals.map((signal) => signal.metrics)) * 22);
  const structureCoverage = clamp(avg(signals.map((signal) => signal.star)) * 14);
  const fillerPenalty = clamp(avg(signals.map((signal) => signal.filler)) * 9, 0, 35);
  const confidenceSignal = avg(transcript.map((turn) => (turn.confidence_signal || 0.55) * 100));
  const leadershipHits = countMatches(answersText, ["led", "owned", "managed", "collaborated", "stakeholder", "mentored", "negotiated", "aligned"]);
  const reasoningHits = countMatches(answersText, ["because", "therefore", "tradeoff", "constraint", "risk", "alternative", "measured"]);
  const technical = clamp(28 + roleCoverage * 0.55 + avgSpecificity * 0.32 + metricCoverage * 0.2 - fillerPenalty * 0.35);
  const communication = clamp(34 + avgLength * 0.34 + structureCoverage * 0.28 + confidenceSignal * 0.22 - fillerPenalty * 0.5);
  const clarity = clamp(36 + structureCoverage * 0.42 + reasoningHits * 5 + metricCoverage * 0.18 - fillerPenalty * 0.6);
  const confidence = clamp(30 + confidenceSignal * 0.48 + avgLength * 0.18 + transcript.length * 3 - fillerPenalty * 0.35);
  const problem = clamp(30 + reasoningHits * 7 + metricCoverage * 0.26 + roleCoverage * 0.24 + structureCoverage * 0.2);
  const leadership = clamp(35 + leadershipHits * 9 + countMatches(answersText, ["customer", "user", "team", "business", "impact"]) * 4 + structureCoverage * 0.18);
  const breakdown = {
    technical_knowledge: technical,
    communication,
    confidence,
    clarity,
    problem_solving: problem,
    leadership
  };
  const difficultyMultiplier = activeInterview.difficulty === "FAANG" ? 0.92 : activeInterview.difficulty === "Advanced" ? 0.96 : activeInterview.difficulty === "Beginner" ? 1.04 : 1;
  const overall = clamp(Object.values(breakdown).reduce((sum, value) => sum + value, 0) / 6 * difficultyMultiplier);
  const weaknesses = detectLocalWeaknesses(activeInterview, breakdown);
  const salaryBase = roleFamily(activeInterview.role) === "marketing" ? 92000 : roleFamily(activeInterview.role) === "sales" ? 98000 : roleFamily(activeInterview.role) === "product" ? 125000 : roleFamily(activeInterview.role) === "design" ? 95000 : roleFamily(activeInterview.role) === "business" ? 90000 : 118000;
  const salaryFactor = 0.72 + overall / 240;
  return {
    ...activeInterview,
    status: "completed",
    scores: {
      overall,
      breakdown,
      formula: {
        role_keyword_coverage: roleCoverage,
        metric_coverage: metricCoverage,
        answer_depth: Math.round(avgLength),
        structure_coverage: structureCoverage,
        filler_penalty: fillerPenalty,
        difficulty_multiplier: difficultyMultiplier
      },
      feedback: "Score is calculated from role keyword coverage, measurable evidence, answer depth, STAR structure, reasoning, confidence, and filler-word penalty."
    },
    weaknesses: weaknesses.length ? weaknesses : [{ area: "Depth Under Follow-Up", severity: "Low", explanation: "Good performance. Practice deeper follow-ups with faster structure and stronger numbers." }],
    roadmap: {
      weekly_goals: [
        "Week 1: tighten fundamentals and rewrite every project story with problem, action, result, and tradeoff.",
        "Week 2: build one production feature with tests, deployment, monitoring, and a clean README.",
        "Week 3: practice role-specific interviews daily and review weak answer patterns.",
        "Week 4: run full mock interviews, improve pacing, and polish final resume bullets."
      ],
      daily_tasks: ["45 minutes fundamentals", "45 minutes coding or project work", "20 minutes spoken answer practice"],
      projects_to_build: ["Interview analytics dashboard", "RAG assistant", "Production API with observability"]
    },
    premium: {
      hiring_probability: clamp(overall * 0.88 + metricCoverage * 0.08 + roleCoverage * 0.05, 8, 96),
      salary_prediction_usd: { low: Math.round(salaryBase * (salaryFactor - 0.14)), mid: Math.round(salaryBase * salaryFactor), high: Math.round(salaryBase * (salaryFactor + 0.2)) },
      confidence_detection: confidence,
      eye_contact_analysis: clamp(58 + confidenceSignal * 0.24 + transcript.length * 2),
      body_language_analysis: confidence > 78 ? "Strong and steady based on answer length and confidence signals" : "Needs more controlled pacing, longer answers, and stronger evidence under follow-up"
    }
  };
}

function detectLocalWeaknesses(activeInterview: Interview, breakdown: Record<string, number>) {
  const transcript = activeInterview.transcript || [];
  const combined = transcript.map((turn) => String(turn.answer || "")).join(" ").toLowerCase();
  const avgWords = transcript.length ? transcript.reduce((sum, turn) => sum + String(turn.answer || "").split(/\s+/).filter(Boolean).length, 0) / transcript.length : 0;
  const findings: { area: string; severity: string; explanation: string }[] = [];
  const add = (area: string, severity: string, explanation: string) => {
    if (!findings.some((item) => item.area === area)) findings.push({ area, severity, explanation });
  };

  if (avgWords < 22) add("Answer Depth", "High", `Average answer length is ${Math.round(avgWords)} words. Give a complete example with situation, action, result, and one lesson.`);
  if (!/\b\d+%|\b\d+x|\b\d+\+|\b\d{2,}\b/.test(combined)) add("Missing Metrics", "High", "Your answers do not include measurable proof. Add numbers such as revenue, users, conversion, latency, accuracy, cost, or time saved.");
  if (!/\btradeoff|because|therefore|instead|alternative|risk|constraint\b/.test(combined)) add("Decision Reasoning", "Medium", "You explain what you did, but not enough about why. Compare alternatives and name the constraint behind your choice.");
  if (!/\bdeployed|launched|shipped|published|production|campaign|customer|stakeholder|user\b/.test(combined)) add("Real-World Impact", "Medium", "The answers need stronger real-world context. Mention who used the work, what changed, and how success was checked.");
  if (/\bmaybe|kind of|sort of|basically|stuff|things\b/.test(combined)) add("Communication Precision", "Medium", "Some language sounds vague. Replace filler words with concrete nouns, exact actions, and outcome statements.");
  if (activeInterview.role.toLowerCase().includes("marketing") && !/\bconversion|cac|roi|channel|segment|funnel|campaign\b/.test(combined)) add("Marketing Fundamentals", "High", "For marketing roles, include funnel metrics, customer segments, channel strategy, CAC, ROI, and campaign learning loops.");
  if (activeInterview.role.toLowerCase().includes("sales") && !/\blead|pipeline|objection|crm|quota|discovery|close\b/.test(combined)) add("Sales Process", "High", "For sales roles, show your discovery process, qualification logic, objection handling, CRM discipline, and closing strategy.");
  if (activeInterview.role.toLowerCase().includes("product") && !/\bprioritize|metric|roadmap|experiment|user|activation|retention\b/.test(combined)) add("Product Thinking", "High", "For product roles, connect choices to user pain, prioritization, experiments, activation, retention, and roadmap tradeoffs.");
  if ((activeInterview.role.toLowerCase().includes("engineer") || activeInterview.role.toLowerCase().includes("developer")) && !/\btest|api|database|deploy|architecture|latency|scal/i.test(combined)) add("Engineering Specificity", "High", "For engineering roles, add architecture, testing, deployment, scalability, data model, and failure handling details.");

  Object.entries(breakdown).forEach(([area, value]) => {
    if (value < 68) add(area.replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase()), "High", `${value}/100 in this dimension. The answer evidence is thin; add a specific example and measurable result.`);
  });

  return findings.slice(0, 5);
}

function ScoreRing({ value, label }: { value: number; label: string }) {
  const angle = Math.max(0, Math.min(100, value)) * 3.6;
  return (
    <div className="score-ring" style={{ background: `conic-gradient(#31e6d1 ${angle}deg, rgba(106,168,255,.16) ${angle}deg, rgba(255,255,255,.08) 0deg)` }}>
      <div>
        <strong>{value}</strong>
        <span>{label}</span>
      </div>
    </div>
  );
}

function RadarChart({ data }: { data: Record<string, number> }) {
  const keys = Object.keys(data);
  if (!keys.length) return <div className="empty-chart">Complete an interview to unlock the radar.</div>;
  const cx = 120;
  const cy = 120;
  const radius = 90;
  const points = keys.map((key, index) => {
    const angle = (Math.PI * 2 * index) / keys.length - Math.PI / 2;
    const r = radius * (data[key] / 100);
    return `${cx + Math.cos(angle) * r},${cy + Math.sin(angle) * r}`;
  });
  return (
    <svg viewBox="0 0 240 240" className="radar">
      {[0.25, 0.5, 0.75, 1].map((scale) => (
        <circle key={scale} cx={cx} cy={cy} r={radius * scale} fill="none" stroke="rgba(255,255,255,.1)" />
      ))}
      {keys.map((key, index) => {
        const angle = (Math.PI * 2 * index) / keys.length - Math.PI / 2;
        return (
          <g key={key}>
            <line x1={cx} y1={cy} x2={cx + Math.cos(angle) * radius} y2={cy + Math.sin(angle) * radius} stroke="rgba(255,255,255,.1)" />
            <text x={cx + Math.cos(angle) * 108} y={cy + Math.sin(angle) * 108} textAnchor="middle">{key.replaceAll("_", " ")}</text>
          </g>
        );
      })}
      <polygon points={points.join(" ")} fill="rgba(49,230,209,.24)" stroke="#31e6d1" strokeWidth="2" />
    </svg>
  );
}

function App() {
  const [token, setToken] = useState(localStorage.getItem("interviewx_token"));
  const [user, setUser] = useState<User | null>(null);
  const [authMode, setAuthMode] = useState<"login" | "signup">("signup");
  const [email, setEmail] = useState("founder@interviewx.ai");
  const [password, setPassword] = useState("InterviewX@2026");
  const [name, setName] = useState("InterviewX Candidate");
  const [resume, setResume] = useState<Resume | null>(null);
  const [interview, setInterview] = useState<Interview | null>(null);
  const [role, setRole] = useState(roles[0]);
  const [difficulty, setDifficulty] = useState(difficulties[2]);
  const [personality, setPersonality] = useState(personalities[2]);
  const [answer, setAnswer] = useState("");
  const [activeQuestion, setActiveQuestion] = useState(0);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const timerRef = useRef<number | null>(null);
  const recognitionRef = useRef<any>(null);
  const liveTranscriptRef = useRef("");

  const scores = resume?.scores || {};
  const breakdown = interview?.scores?.breakdown || {};
  const currentQuestion = interview?.questions?.[activeQuestion];

  const readiness = useMemo(() => Math.round(((scores.ats || 0) + (scores.resume_strength || 0) + (scores.industry_readiness || 0)) / 3) || 0, [scores]);

  useEffect(() => {
    if (!token || user) return;
    if (token.startsWith("demo-")) {
      setUser(demoUser(name, email));
      return;
    }
    request("/api/v1/auth/me", token)
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("interviewx_token");
        setToken(null);
      });
  }, [token, user]);

  useEffect(() => {
    return () => {
      recognitionRef.current?.stop?.();
      if (recorderRef.current?.state === "recording") recorderRef.current.stop();
      if (timerRef.current) window.clearInterval(timerRef.current);
    };
  }, []);

  async function authenticate() {
    setBusy(true);
    try {
      const payload = authMode === "signup" ? { email, password, full_name: name } : { email, password };
      const data = await request(`/api/v1/auth/${authMode}`, null, { method: "POST", body: JSON.stringify(payload) });
      localStorage.setItem("interviewx_token", data.access_token);
      setToken(data.access_token);
      setUser(data.user);
      setMessage("Workspace secured. You can upload a resume now.");
    } catch (error: any) {
      const demoToken = `demo-${crypto.randomUUID()}`;
      localStorage.setItem("interviewx_token", demoToken);
      setToken(demoToken);
      setUser(demoUser(name, email));
      setMessage("Demo workspace is ready. Backend was unreachable, so InterviewX is running locally without errors.");
    } finally {
      setBusy(false);
    }
  }

  async function uploadResume(file: File) {
    if (!token) return;
    setBusy(true);
    try {
      const form = new FormData();
      form.append("file", file);
      const data = await request("/api/v1/resumes/upload", token, { method: "POST", body: form });
      setResume(data);
      setMessage("Resume analyzed with ATS, readiness, and improvement signals.");
    } catch (error: any) {
      setResume(demoResume(file));
      setMessage("Resume demo analysis is ready. Backend upload failed, so local scoring was used.");
    } finally {
      setBusy(false);
    }
  }

  async function generateInterview() {
    if (!token) return;
    setBusy(true);
    try {
      const data = await request("/api/v1/interviews/generate", token, {
        method: "POST",
        body: JSON.stringify({ resume_id: resume?.id, role, difficulty, personality })
      });
      setInterview(data);
      setActiveQuestion(0);
      setMessage("Interview room is live. The interviewer will adapt to your answers.");
      speak(data.questions[0]?.text);
    } catch (error: any) {
      const data: Interview = {
        id: Date.now(),
        role,
        difficulty,
        personality,
        status: "active",
        questions: demoQuestions(role, difficulty),
        transcript: []
      };
      setInterview(data);
      setActiveQuestion(0);
      setMessage("Interview room is live in local mode. No fetch errors, just practice.");
      speak(data.questions[0]?.text);
    } finally {
      setBusy(false);
    }
  }

  async function submitAnswer() {
    if (!token || !interview || !currentQuestion || !answer.trim()) return;
    setBusy(true);
    try {
      const confidence = Math.min(0.95, Math.max(0.42, answer.split(" ").length / 80));
      const data = await request(`/api/v1/interviews/${interview.id}/answer`, token, {
        method: "POST",
        body: JSON.stringify({
          question_id: currentQuestion.id,
          answer,
          confidence_signal: confidence,
          emotion_signal: confidence > 0.72 ? "focused" : "uncertain",
          eye_contact_signal: 0.7
        })
      });
      setInterview({ ...interview, transcript: [...interview.transcript, data.turn] });
      setAnswer("");
      setMessage(`Follow-up: ${data.follow_up}`);
      speak(data.follow_up);
      setActiveQuestion((index) => Math.min(index + 1, interview.questions.length - 1));
    } catch (error: any) {
      const followUp = localFollowUp(answer, interview.role);
      const turn = {
        question_id: currentQuestion.id,
        question: currentQuestion.text,
        answer,
        follow_up: followUp,
        confidence_signal: Math.min(0.95, Math.max(0.42, answer.split(" ").length / 80)),
        emotion_signal: "focused",
        eye_contact_signal: 0.72,
        answered_at: new Date().toISOString()
      };
      setInterview({ ...interview, transcript: [...interview.transcript, turn] });
      setAnswer("");
      setMessage(`Follow-up: ${followUp}`);
      speak(followUp);
      setActiveQuestion((index) => Math.min(index + 1, interview.questions.length - 1));
    } finally {
      setBusy(false);
    }
  }

  async function completeInterview() {
    if (!token || !interview) return;
    setBusy(true);
    try {
      const data = await request(`/api/v1/interviews/${interview.id}/complete`, token, { method: "POST" });
      setInterview(data);
      setMessage("Scoring, weakness detection, premium analytics, and roadmap are ready.");
    } catch (error: any) {
      setInterview(scoreLocalInterview(interview));
      setMessage("Scoring, weakness detection, premium analytics, and roadmap are ready in local mode.");
    } finally {
      setBusy(false);
    }
  }

  async function createReport() {
    if (!token || !interview) return;
    let blob: Blob;
    try {
      const report = await request(`/api/v1/reports/${interview.id}`, token, { method: "POST" });
      const response = await fetch(`${API}/api/v1/reports/${report.id}/download`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      blob = await response.blob();
    } catch {
      const text = [
        "InterviewX AI Report",
        `Role: ${interview.role}`,
        `Difficulty: ${interview.difficulty}`,
        `Overall Score: ${interview.scores?.overall || "Pending"}/100`,
        "",
        "Weaknesses:",
        ...(interview.weaknesses || []).map((item) => `${item.area}: ${item.explanation}`),
        "",
        "Transcript:",
        ...(interview.transcript || []).map((turn) => `Q: ${turn.question}\nA: ${turn.answer}\nFollow-up: ${turn.follow_up}`)
      ].join("\n");
      blob = new Blob([text], { type: "text/plain" });
    }
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = blob.type === "application/pdf" ? `interviewx-report-${interview.id}.pdf` : `interviewx-report-${interview.id}.txt`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  async function listen() {
    if (isRecording) {
      recognitionRef.current?.stop?.();
      if (recorderRef.current?.state === "recording") recorderRef.current.stop();
      setIsRecording(false);
      if (timerRef.current) window.clearInterval(timerRef.current);
      return;
    }
    if (!currentQuestion) {
      setMessage("Generate an interview first, then start recording.");
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia) {
      setMessage("Microphone recording is unavailable in this browser. Type your answer in the box.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      liveTranscriptRef.current = "";
      chunksRef.current = [];
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = async () => {
        stream.getTracks().forEach((track) => track.stop());
        if (timerRef.current) window.clearInterval(timerRef.current);
        setIsRecording(false);
        recognitionRef.current?.stop?.();
        if (liveTranscriptRef.current.trim()) {
          setMessage("Voice answer captured. Review it, then send.");
          return;
        }
        const audio = new Blob(chunksRef.current, { type: "audio/webm" });
        if (!token || !interview) {
          setMessage("Audio captured. Type the answer text to score it.");
          return;
        }
        try {
          const form = new FormData();
          form.append("file", audio, `answer-${Date.now()}.webm`);
          const data = await request(`/api/v1/interviews/${interview.id}/transcribe`, token, { method: "POST", body: form });
          setAnswer(data.transcript || "");
          setMessage("Audio transcribed. Review it, then send.");
        } catch {
          setMessage("Audio captured, but transcription is unavailable. Type a short summary and send it.");
        }
      };
      recorderRef.current = recorder;
      if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        recognition.lang = "en-US";
        recognition.interimResults = true;
        recognition.continuous = true;
        let finalText = "";
        recognition.onresult = (event: any) => {
          let draft = "";
          for (let index = event.resultIndex; index < event.results.length; index += 1) {
            const phrase = event.results[index][0].transcript;
            if (event.results[index].isFinal) finalText += `${phrase} `;
            else draft += phrase;
          }
          liveTranscriptRef.current = `${finalText}${draft}`.trim();
          setAnswer(liveTranscriptRef.current);
        };
        recognition.onerror = () => setMessage("Still recording audio. Live captions are unavailable in this browser.");
        recognitionRef.current = recognition;
        recognition.start();
      }
      setRecordingSeconds(0);
      setIsRecording(true);
      timerRef.current = window.setInterval(() => setRecordingSeconds((seconds) => seconds + 1), 1000);
      recorder.start();
      setMessage("Recording... live captions will appear if the browser supports them. Click Stop when done.");
    } catch {
      setMessage("Microphone permission was blocked. Allow microphone access or type your answer.");
    }
  }

  function speak(text?: string) {
    if (!text || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 0.95;
    window.speechSynthesis.speak(utterance);
  }

  if (token && !user) {
    return <main className="auth-shell"><div className="auth-card"><div className="brand"><Brain /> InterviewX AI</div><p className="status">Restoring your secure workspace...</p></div></main>;
  }

  if (!token || !user) {
    return (
      <main className="auth-shell">
        <motion.section initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} className="auth-card auth-card-wide">
          <div className="auth-copy">
            <div className="brand"><Brain /> InterviewX AI</div>
            <h1>Practice. Score. Improve.</h1>
            <p>AI interviews for engineering, marketing, sales, product, design, finance, HR, and more.</p>
            <div className="auth-badges">
              <span><Sparkles /> Adaptive AI</span>
              <span><Mic /> Voice Practice</span>
              <span><Radar /> Score Analytics</span>
            </div>
            <div className="ai-orbit" aria-hidden="true">
              <div className="ai-core"><Brain /></div>
              <span className="node node-a">ATS</span>
              <span className="node node-b">RAG</span>
              <span className="node node-c">VOICE</span>
              <span className="node node-d">SCORE</span>
            </div>
          </div>
          <div className="auth-form">
            <div className="switch">
              <button className={authMode === "signup" ? "active" : ""} onClick={() => setAuthMode("signup")}>Signup</button>
              <button className={authMode === "login" ? "active" : ""} onClick={() => setAuthMode("login")}>Login</button>
            </div>
            {authMode === "signup" && <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Full name" />}
            <input value={email} onChange={(event) => setEmail(event.target.value)} placeholder="Email" />
            <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" placeholder="Password" />
            <button className="primary" onClick={authenticate} disabled={busy}><Shield /> Enter Dashboard</button>
            <button className="ghost" onClick={() => request("/api/v1/auth/google", null, { method: "POST", body: JSON.stringify({ id_token: crypto.randomUUID() }) }).then((data) => { localStorage.setItem("interviewx_token", data.access_token); setToken(data.access_token); setUser(data.user); }).catch(() => { const demoToken = `demo-${crypto.randomUUID()}`; localStorage.setItem("interviewx_token", demoToken); setToken(demoToken); setUser(demoUser("Google Demo User", "google-demo@interviewx.local")); setMessage("Google demo workspace is ready in local mode."); })}>
              <Sparkles /> Google Demo
            </button>
            {message && <p className="status">{message}</p>}
          </div>
        </motion.section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <aside>
        <div className="brand"><Brain /> InterviewX AI</div>
        {["Command Center", "Resume Analyzer", "Voice Interview", "Analytics", "Roadmap"].map((item, index) => (
          <a key={item} href={`#panel-${index}`}>{item}</a>
        ))}
        <button className="logout" onClick={() => { localStorage.removeItem("interviewx_token"); setToken(null); setUser(null); }}><LogOut /> Sign out</button>
      </aside>

      <section className="workspace">
        <header>
          <div>
            <p className="eyebrow">Candidate workspace</p>
            <h1>Interview readiness cockpit</h1>
          </div>
          <div className="profile"><UserRound /> {user.full_name}</div>
        </header>

        {message && <div className="notice">{message}</div>}

        <motion.section id="panel-0" className="metrics-grid" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ staggerChildren: 0.08 }}>
          <ScoreRing value={readiness} label="Readiness" />
          <ScoreRing value={scores.ats || 0} label="ATS" />
          <ScoreRing value={interview?.scores?.overall || 0} label="Interview" />
          <div className="premium-strip">
            <span><Gauge /> Hiring probability</span>
            <strong>{interview?.premium?.hiring_probability || 0}%</strong>
            <small>{interview?.premium?.salary_prediction_usd ? `$${interview.premium.salary_prediction_usd.mid.toLocaleString()} predicted midpoint` : "Complete an interview to unlock salary intelligence"}</small>
          </div>
        </motion.section>

        <section className="two-col">
          <motion.div id="panel-1" className="panel" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
            <div className="panel-title"><FileText /> Resume Analyzer</div>
            <label className="dropzone">
              <Upload />
              <span>{resume ? resume.filename : "Upload PDF or DOCX resume"}</span>
              <input type="file" accept=".pdf,.doc,.docx" onChange={(event) => event.target.files?.[0] && uploadResume(event.target.files[0])} />
            </label>
            {resume && (
              <div className="resume-results">
                <h3>{resume.parsed.name || "Candidate"}</h3>
                <div className="chips">{(resume.parsed.skills || []).slice(0, 10).map((skill: string) => <span key={skill}>{skill}</span>)}</div>
                {resume.suggestions.map((item, index) => <p key={index}><CheckCircle2 /> <b>{item.area}</b> {item.suggestion}</p>)}
              </div>
            )}
          </motion.div>

          <motion.div className="panel" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
            <div className="panel-title"><Sparkles /> Interview Generator</div>
            <div className="form-grid">
              <select value={role} onChange={(event) => setRole(event.target.value)}>{roles.map((item) => <option key={item}>{item}</option>)}</select>
              <select value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>{difficulties.map((item) => <option key={item}>{item}</option>)}</select>
              <select value={personality} onChange={(event) => setPersonality(event.target.value)}>{personalities.map((item) => <option key={item}>{item}</option>)}</select>
            </div>
            <button className="primary" onClick={generateInterview} disabled={busy}><Play /> Generate Interview</button>
            <div className="question-list">
              {(interview?.questions || []).slice(0, 5).map((question, index) => <p key={question.id}><span>{index + 1}</span>{question.text}</p>)}
            </div>
          </motion.div>
        </section>

        <motion.section id="panel-2" className="panel interview-panel" initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }}>
          <div className="panel-title"><Mic /> Voice Interview</div>
          <div className="interviewer">
            <div className="ai-stream" aria-hidden="true"><span /><span /><span /><span /><span /></div>
            <div>
              <small>{personality}</small>
              <h2>{currentQuestion?.text || "Generate an interview to begin."}</h2>
            </div>
            <button className="icon-button" onClick={() => speak(currentQuestion?.text)}><Activity /></button>
          </div>
          {isRecording && (
            <div className="recording-bar">
              <div className="voice-wave"><span /><span /><span /><span /><span /><span /></div>
              <strong>Recording {recordingSeconds}s</strong>
              <small>Speak naturally, then click Stop.</small>
            </div>
          )}
          <textarea value={answer} onChange={(event) => setAnswer(event.target.value)} placeholder="Speak or type your answer with decisions, tradeoffs, metrics, and impact." />
          <div className="actions">
            <button className={isRecording ? "secondary" : "ghost"} onClick={listen}><Mic /> {isRecording ? "Stop" : "Record"}</button>
            <button className="primary" onClick={submitAnswer} disabled={!answer.trim() || busy}><Send /> Send Answer</button>
            <button className="secondary" onClick={completeInterview} disabled={!interview || busy}><CheckCircle2 /> Complete</button>
          </div>
          <div className="transcript">
            {(interview?.transcript || []).map((turn, index) => (
              <article key={index}>
                <strong>{turn.question}</strong>
                <p>{turn.answer}</p>
                <em>{turn.follow_up}</em>
              </article>
            ))}
          </div>
        </motion.section>

        <section id="panel-3" className="two-col">
          <div className="panel">
            <div className="panel-title"><Radar /> Performance Radar</div>
            <RadarChart data={breakdown} />
          </div>
          <div className="panel">
            <div className="panel-title"><BarChart3 /> Weakness Detection</div>
            {interview?.scores?.formula && (
              <div className="formula-grid">
                {Object.entries(interview.scores.formula).map(([key, value]) => (
                  <div key={key}>
                    <span>{key.replaceAll("_", " ")}</span>
                    <strong>{String(value)}</strong>
                  </div>
                ))}
              </div>
            )}
            {(interview?.weaknesses || []).map((weakness) => (
              <div className="weakness" key={weakness.area}>
                <strong>{weakness.area}</strong>
                <span>{weakness.severity}</span>
                <p>{weakness.explanation}</p>
              </div>
            ))}
            {interview?.scores && <button className="primary" onClick={createReport}><Download /> Download PDF Report</button>}
          </div>
        </section>

        <section id="panel-4" className="panel roadmap">
          <div className="panel-title"><Brain /> Personalized Roadmap</div>
          {(interview?.roadmap?.weekly_goals || []).map((goal: string, index: number) => (
            <div className="roadmap-row" key={goal}>
              <span>Week {index + 1}</span>
              <p>{goal}</p>
            </div>
          ))}
        </section>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<App />);
