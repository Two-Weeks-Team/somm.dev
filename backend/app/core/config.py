"""Application settings and configuration"""

import secrets
from pydantic_settings import BaseSettings
from typing import List


_DEFAULT_JWT_SECRET = secrets.token_urlsafe(32)


class Settings(BaseSettings):
    """Application settings loaded from environment variables

    Security Note: JWT_SECRET_KEY MUST be set via environment variable in production.
    The default random value is only for development convenience.
    """

    APP_NAME: str = "Somm.dev API"
    API_V1_STR: str = "/api/v1"

    ENVIRONMENT: str = "development"

    JWT_SECRET_KEY: str = _DEFAULT_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 7

    # CORS settings
    FRONTEND_URL: str = "http://localhost:3000"

    # Database
    MONGODB_URI: str = "mongodb://localhost:27017/somm_db"
    MONGO_DB: str = "somm"

    # LLM APIs
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # GitHub
    GITHUB_TOKEN: str = ""

    # Optional: Error Tracking
    SENTRY_DSN: str = ""

    # Optional: Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Server settings
    PORT: int = 8000
    DEBUG: bool = False

    @property
    def CORS_ORIGINS(self) -> List[str]:
        origins = [self.FRONTEND_URL]
        if self.FRONTEND_URL.startswith("https://www."):
            origins.append(self.FRONTEND_URL.replace("https://www.", "https://", 1))
        return origins

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
