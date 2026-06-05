# InterviewX AI Architecture

## System Overview

InterviewX AI uses a modular monorepo:

- `frontend`: React SPA for candidate workflows, live voice interview UI, dashboards, analytics, and reports.
- `backend`: FastAPI application exposing authenticated REST APIs.
- `postgres`: durable transactional storage for users, resumes, interviews, answers, analytics, and reports.
- `chroma`: semantic retrieval store for DSA, ML, NLP, data engineering, system design, and behavioral knowledge.
- `Gemini 2.5 Pro`: production AI provider for extraction, question generation, scoring, weakness detection, and roadmaps.
- `Whisper`: speech-to-text compatible endpoint for uploaded interview answers.

## Core Flow

1. User signs up or logs in through JWT or Google.
2. Candidate uploads a resume file.
3. Backend extracts text, parses structured profile data, computes readiness scores, and stores analysis.
4. User selects role, difficulty, and interviewer personality.
5. RAG retrieves relevant interview topics from Chroma.
6. Gemini generates tailored questions using resume profile plus retrieved context.
7. Voice interview collects answers through browser speech recognition or uploaded audio transcription.
8. Adaptive follow-up engine inspects answer content and asks deeper project, ML, system, or behavioral questions.
9. Scoring engine evaluates technical knowledge, communication, confidence, clarity, problem solving, and leadership.
10. Analytics, weaknesses, hiring probability, salary estimate, and roadmap are generated.
11. PDF report is created with transcript, scores, weaknesses, analytics, and action plan.

## Scaling Notes

- Stateless backend containers can be horizontally scaled behind a load balancer.
- PostgreSQL owns source-of-truth transactional data.
- Chroma collection can be replaced with managed vector databases without API changes.
- Long-running AI/report jobs can be moved to Celery or Cloud Tasks using the existing service boundaries.
- Audio/video analysis is isolated under interview services so it can move to GPU workers.

