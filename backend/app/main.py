import logging
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import analytics, auth, interviews, reports, resumes
from app.core.config import get_settings
from app.db.session import Base, engine

settings = get_settings()
logger = logging.getLogger("interviewx")


def initialize_database() -> None:
    last_error: Exception | None = None
    for attempt in range(1, 8):
        try:
            Base.metadata.create_all(bind=engine)
            return
        except Exception as exc:
            last_error = exc
            logger.warning("Database initialization attempt %s failed: %s", attempt, exc)
            time.sleep(min(attempt * 2, 10))
    raise RuntimeError("Database initialization failed") from last_error

app = FastAPI(
    title="InterviewX AI API",
    version="1.0.0",
    description="AI interview intelligence platform API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        str(settings.frontend_origin),
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://0.0.0.0:5173",
    ],
    allow_origin_regex=r"(http://(localhost|127\.0\.0\.1|0\.0\.0\.0|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+):5173|https://.*\.(onrender\.com|vercel\.app|netlify\.app|github\.io))",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    initialize_database()

app.include_router(auth.router, prefix="/api/v1")
app.include_router(resumes.router, prefix="/api/v1")
app.include_router(interviews.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "service": "interviewx-ai"}
