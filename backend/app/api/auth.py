import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.api.deps import current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import PasswordResetToken, User
from app.schemas import ForgotPasswordRequest, GoogleLoginRequest, LoginRequest, ResetPasswordRequest, SignupRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])


def _token_for(user: User) -> TokenResponse:
    return TokenResponse(access_token=create_access_token(str(user.id)), user=UserOut.model_validate(user))


@router.post("/signup", response_model=TokenResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(email=payload.email.lower(), full_name=payload.full_name, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_for(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return _token_for(user)


@router.post("/google", response_model=TokenResponse)
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    full_name = "Google User"
    avatar_url = None
    if settings.google_client_id:
        try:
            from google.auth.transport import requests
            from google.oauth2 import id_token

            info = id_token.verify_oauth2_token(payload.id_token, requests.Request(), settings.google_client_id)
            email = info["email"].lower()
            full_name = info.get("name") or email.split("@")[0]
            avatar_url = info.get("picture")
        except Exception as exc:
            raise HTTPException(status_code=401, detail="Invalid Google token") from exc
    else:
        digest = hashlib.sha256(payload.id_token.encode()).hexdigest()[:12]
        email = f"google-{digest}@interviewx.local"
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email, full_name=full_name, provider="google", password_hash=None, avatar_url=avatar_url)
        db.add(user)
        db.commit()
        db.refresh(user)
    return _token_for(user)


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user:
        raw = secrets.token_urlsafe(32)
        token = PasswordResetToken(
            user_id=user.id,
            token_hash=hashlib.sha256(raw.encode()).hexdigest(),
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
        )
        db.add(token)
        db.commit()
        return {"message": "Password reset token generated", "reset_token": raw}
    return {"message": "If an account exists, reset instructions were generated"}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    token_hash = hashlib.sha256(payload.token.encode()).hexdigest()
    token = db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).first()
    if not token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    expires_at = token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if token.used_at or expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    user = db.get(User, token.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = hash_password(payload.password)
    token.used_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Password updated"}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user
