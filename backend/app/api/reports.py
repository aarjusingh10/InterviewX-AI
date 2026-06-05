from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import current_user
from app.db.session import get_db
from app.models import Interview, Report, User
from app.schemas import ReportOut
from app.services.report_service import create_interview_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/{interview_id}", response_model=ReportOut)
def create_report(interview_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    interview = db.get(Interview, interview_id)
    if not interview or interview.user_id != user.id:
        raise HTTPException(status_code=404, detail="Interview not found")
    if not interview.scores:
        raise HTTPException(status_code=400, detail="Complete the interview before generating a report")
    report = db.query(Report).filter(Report.interview_id == interview.id).first()
    if not report:
        file_path = create_interview_report(interview)
        report = Report(interview_id=interview.id, user_id=user.id, file_path=file_path)
        db.add(report)
        db.commit()
        db.refresh(report)
    return report


@router.get("/{report_id}/download")
def download_report(report_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    report = db.get(Report, report_id)
    if not report or report.user_id != user.id:
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(report.file_path, media_type="application/pdf", filename=f"interviewx-report-{report.interview_id}.pdf")

