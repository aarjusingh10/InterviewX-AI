from pathlib import Path
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.core.config import get_settings
from app.db.session import get_db
from app.models import Resume, User
from app.schemas import ResumeOut
from app.services.document_parser import extract_text
from app.services.resume_analyzer import analyze_resume

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("/upload", response_model=ResumeOut)
async def upload_resume(file: UploadFile = File(...), user: User = Depends(current_user), db: Session = Depends(get_db)):
    if not file.filename or Path(file.filename).suffix.lower() not in {".pdf", ".docx", ".doc"}:
        raise HTTPException(status_code=400, detail="Upload a PDF or DOCX resume")
    settings = get_settings()
    upload_dir = Path(settings.upload_storage_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    path = upload_dir / f"user-{user.id}-{file.filename}"
    path.write_bytes(await file.read())
    text = extract_text(str(path))
    if len(text) < 80:
        raise HTTPException(status_code=400, detail="Resume text is too short to analyze")
    analysis = await analyze_resume(text)
    resume = Resume(
        user_id=user.id,
        filename=file.filename,
        text=text,
        parsed=analysis["parsed"],
        scores=analysis["scores"] | {"detections": analysis.get("detections", {})},
        suggestions=analysis["suggestions"],
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("", response_model=list[ResumeOut])
def list_resumes(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return db.query(Resume).filter(Resume.user_id == user.id).order_by(Resume.created_at.desc()).all()


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(resume_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if not resume or resume.user_id != user.id:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

