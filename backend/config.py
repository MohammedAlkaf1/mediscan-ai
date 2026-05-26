"""
Configuration settings for MediScan AI
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "MediScan AI"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://postgres:12345@localhost:5432/medical"

    # Security — IMPORTANT: Override SECRET_KEY in production!
    # Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # URLs
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    # File storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".pdf"}
    DELETE_FILES_AFTER_PROCESSING: bool = True
    DEFAULT_SAVE_REPORT: bool = False

    # OCR
    OCR_ENGINE: str = "easyocr"  # easyocr
    OCR_LANGUAGE: str = "en"
    MIN_OCR_CONFIDENCE: float = 0.5

    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
    ]

    # AI / Gemini
    AI_PROVIDER: str = "gemini"          # gemini or openai
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash-preview-05-20"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # Feature flags
    ENABLE_AI_EXPLANATIONS: bool = False   # Set true when GEMINI_API_KEY is configured
    ENABLE_PDF_EXPORT: bool = True
    ENABLE_SHARING: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
