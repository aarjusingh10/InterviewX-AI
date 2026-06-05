from pathlib import Path


def transcribe_audio(path: str) -> str:
    try:
        from faster_whisper import WhisperModel

        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(path)
        return " ".join(segment.text.strip() for segment in segments).strip()
    except Exception:
        return f"Audio uploaded successfully as {Path(path).name}. Configure Whisper runtime for full transcription."

