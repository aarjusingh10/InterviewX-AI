from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class SignupRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    id_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    avatar_url: str | None = None
    provider: str

    model_config = {"from_attributes": True}


class ResumeOut(BaseModel):
    id: int
    filename: str
    parsed: dict
    scores: dict
    suggestions: list
    created_at: datetime

    model_config = {"from_attributes": True}


class GenerateInterviewRequest(BaseModel):
    resume_id: int | None = None
    role: str
    difficulty: str
    personality: str = "Senior Engineer"


class AnswerRequest(BaseModel):
    question_id: str
    answer: str
    confidence_signal: float | None = Field(default=None, ge=0, le=1)
    emotion_signal: str | None = None
    eye_contact_signal: float | None = Field(default=None, ge=0, le=1)


class InterviewOut(BaseModel):
    id: int
    role: str
    difficulty: str
    personality: str
    status: str
    questions: list
    transcript: list
    scores: dict | None = None
    weaknesses: list | None = None
    roadmap: dict | None = None
    premium: dict | None = None
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


class ReportOut(BaseModel):
    id: int
    interview_id: int
    file_path: str
    created_at: datetime

    model_config = {"from_attributes": True}


TokenResponse.model_rebuild()

