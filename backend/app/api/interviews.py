from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models import Interview, Resume, User
from app.schemas import AnswerRequest, GenerateInterviewRequest, InterviewOut
from app.services.interview_engine import detect_weaknesses, generate_follow_up, generate_questions, generate_roadmap, premium_metrics, score_interview
from app.services.speech_service import transcribe_audio

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.post("/generate", response_model=InterviewOut)
async def generate(payload: GenerateInterviewRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    resume = db.get(Resume, payload.resume_id) if payload.resume_id else None
    if payload.resume_id and (not resume or resume.user_id != user.id):
        raise HTTPException(status_code=404, detail="Resume not found")
    questions = await generate_questions(payload.role, payload.difficulty, payload.personality, resume.parsed if resume else None)
    interview = Interview(
        user_id=user.id,
        resume_id=resume.id if resume else None,
        role=payload.role,
        difficulty=payload.difficulty,
        personality=payload.personality,
        questions=questions,
        transcript=[],
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return interview


@router.get("", response_model=list[InterviewOut])
def list_interviews(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.query(Interview).filter(Interview.user_id == user.id).order_by(Interview.created_at.desc()).all()


@router.get("/{interview_id}", response_model=InterviewOut)
def get_interview(interview_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    interview = db.get(Interview, interview_id)
    if not interview or interview.user_id != user.id:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview


@router.post("/{interview_id}/answer")
def answer(interview_id: int, payload: AnswerRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    interview = db.get(Interview, interview_id)
    if not interview or interview.user_id != user.id:
        raise HTTPException(status_code=404, detail="Interview not found")
    question = next((q for q in interview.questions if q["id"] == payload.question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    follow_up = generate_follow_up(payload.answer, interview.role)
    turn = {
        "question_id": payload.question_id,
        "question": question["text"],
        "answer": payload.answer,
        "follow_up": follow_up,
        "confidence_signal": payload.confidence_signal,
        "emotion_signal": payload.emotion_signal,
        "eye_contact_signal": payload.eye_contact_signal,
        "answered_at": datetime.now(timezone.utc).isoformat(),
    }
    interview.transcript = [*(interview.transcript or []), turn]
    db.commit()
    return {"follow_up": follow_up, "turn": turn}


@router.post("/{interview_id}/transcribe")
async def transcribe(interview_id: int, file: UploadFile = File(...), user: User = Depends(current_user), db: Session = Depends(get_db)):
    interview = db.get(Interview, interview_id)
    if not interview or interview.user_id != user.id:
        raise HTTPException(status_code=404, detail="Interview not found")
    settings = get_settings()
    upload_dir = Path(settings.upload_storage_dir) / "audio"
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / f"interview-{interview.id}-{file.filename}"
    path.write_bytes(await file.read())
    return {"transcript": transcribe_audio(str(path))}


@router.post("/{interview_id}/complete", response_model=InterviewOut)
async def complete(interview_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    interview = db.get(Interview, interview_id)
    if not interview or interview.user_id != user.id:
        raise HTTPException(status_code=404, detail="Interview not found")
    scores = await score_interview(interview.role, interview.difficulty, interview.transcript or [])
    weaknesses = detect_weaknesses(interview.transcript or [], scores)
    roadmap = generate_roadmap(interview.role, weaknesses)
    premium = premium_metrics(scores, interview.role, interview.transcript or [])
    interview.scores = scores
    interview.weaknesses = weaknesses
    interview.roadmap = roadmap
    interview.premium = premium
    interview.status = "completed"
    interview.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(interview)
    return interview

