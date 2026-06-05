from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from app.core.config import get_settings
from app.models import Interview


def _para(text: str):
    styles = getSampleStyleSheet()
    return Paragraph(str(text).replace("\n", "<br/>"), styles["BodyText"])


def create_interview_report(interview: Interview) -> str:
    settings = get_settings()
    out_dir = Path(settings.report_storage_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"interviewx-report-{interview.id}.pdf"
    doc = SimpleDocTemplate(str(path), pagesize=letter, title=f"InterviewX Report {interview.id}")
    styles = getSampleStyleSheet()
    story = [Paragraph("InterviewX AI Interview Report", styles["Title"]), Spacer(1, 16)]
    story.append(Paragraph(f"{interview.role} / {interview.difficulty} / {interview.personality}", styles["Heading2"]))
    story.append(Spacer(1, 12))

    scores = interview.scores or {}
    breakdown = scores.get("breakdown", {})
    story.append(Paragraph(f"Overall Score: {scores.get('overall', 'Pending')}/100", styles["Heading2"]))
    if breakdown:
        data = [["Dimension", "Score"]] + [[key.replace("_", " ").title(), value] for key, value in breakdown.items()]
        table = Table(data, hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#9CA3AF")),
                    ("PADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.extend([table, Spacer(1, 14)])

    story.append(Paragraph("Weaknesses", styles["Heading2"]))
    for weakness in interview.weaknesses or []:
        story.append(_para(f"{weakness.get('area')}: {weakness.get('explanation')}"))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Transcript", styles["Heading2"]))
    for turn in interview.transcript or []:
        story.append(_para(f"Q: {turn.get('question')}"))
        story.append(_para(f"A: {turn.get('answer')}"))
        if turn.get("follow_up"):
            story.append(_para(f"Follow-up: {turn.get('follow_up')}"))
        story.append(Spacer(1, 8))

    roadmap = interview.roadmap or {}
    story.append(Paragraph("30-Day Improvement Roadmap", styles["Heading2"]))
    for key in ["weekly_goals", "daily_tasks", "projects_to_build", "technologies_to_learn", "recommended_courses", "leetcode"]:
        if roadmap.get(key):
            story.append(Paragraph(key.replace("_", " ").title(), styles["Heading3"]))
            for item in roadmap[key]:
                story.append(_para(f"- {item}"))
    doc.build(story)
    return str(path)
