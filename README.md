# InterviewX AI

InterviewX AI is a production-oriented AI interview intelligence platform for resume analysis, adaptive interviews, scoring, analytics, weakness detection, and personalized improvement plans.

## What Is Included

- React + TypeScript + Tailwind + Framer Motion frontend
- FastAPI backend with JWT auth, Google login hook, password reset flow, resume ingestion, RAG-backed interview generation, adaptive follow-ups, scoring, analytics, roadmap generation, and PDF reports
- PostgreSQL schema through SQLAlchemy models
- ChromaDB vector knowledge base integration with an in-memory fallback for local demos
- Gemini 2.5 Pro integration with deterministic local intelligence fallback
- Whisper-compatible speech endpoint for uploaded audio
- Docker Compose for frontend, backend, Postgres, and Chroma

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API Routes](docs/API.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [Deployment](docs/DEPLOYMENT.md)

## Quick Start

1. Copy `.env.example` to `.env`.
2. Set `JWT_SECRET_KEY` and optionally `GEMINI_API_KEY`.
3. Start the stack:

```bash
docker compose up --build
```

Frontend: http://localhost:5173  
Backend API: http://localhost:8000/docs

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Resume-Ready Description

Built InterviewX AI, a full-stack AI interview intelligence platform using React, TypeScript, FastAPI, PostgreSQL, ChromaDB, Gemini 2.5 Pro, JWT authentication, and Docker. The platform analyzes resumes, generates role-specific adaptive interview questions, conducts voice-based mock interviews, detects weaknesses, scores candidates across technical and communication dimensions, visualizes analytics, and produces personalized 30-day improvement roadmaps and PDF reports.
