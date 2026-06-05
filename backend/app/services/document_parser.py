from pathlib import Path
from docx import Document
from pypdf import PdfReader


def extract_text(path: str) -> str:
    file_path = Path(path)
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(str(file_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if suffix in {".docx", ".doc"}:
        doc = Document(str(file_path))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs).strip()
    raise ValueError("Only PDF and DOCX resumes are supported")

