from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.db.session import get_db
from app.models import Interview, User

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
def overview(user: User = Depends(current_user), db: Session = Depends(get_db)):
    interviews = db.query(Interview).filter(Interview.user_id == user.id).order_by(Interview.created_at.asc()).all()
    completed = [item for item in interviews if item.scores]
    scores = [item.scores.get("overall", 0) for item in completed]
    latest = completed[-1] if completed else None
    breakdown = latest.scores.get("breakdown", {}) if latest else {}
    heatmap = [{"skill": key.replace("_", " ").title(), "score": value} for key, value in breakdown.items()]
    return {
        "total_interviews": len(interviews),
        "completed_interviews": len(completed),
        "average_score": round(sum(scores) / len(scores), 1) if scores else 0,
        "trend": [{"date": item.created_at.isoformat(), "score": item.scores.get("overall", 0)} for item in completed],
        "radar": breakdown,
        "skill_heatmap": heatmap,
        "history": [
            {
                "id": item.id,
                "role": item.role,
                "difficulty": item.difficulty,
                "score": item.scores.get("overall") if item.scores else None,
                "created_at": item.created_at.isoformat(),
            }
            for item in interviews[-10:]
        ],
    }


@router.get("/interviews/{interview_id}")
def interview_analytics(interview_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    interview = db.get(Interview, interview_id)
    if not interview or interview.user_id != user.id:
        raise HTTPException(status_code=404, detail="Interview not found")
    return {
        "scores": interview.scores,
        "weaknesses": interview.weaknesses,
        "premium": interview.premium,
        "transcript_depth": len(interview.transcript or []),
        "progress_tracking": interview.roadmap,
    }

