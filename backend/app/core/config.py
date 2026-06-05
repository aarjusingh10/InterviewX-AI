from functools import lru_cache
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./interviewx.db"
    jwt_secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    gemini_api_key: str | None = None
    google_client_id: str | None = None
    google_client_secret: str | None = None
    frontend_origin: str | AnyHttpUrl = "http://localhost:5173"
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    report_storage_dir: str = "storage/reports"
    upload_storage_dir: str = "storage/uploads"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

