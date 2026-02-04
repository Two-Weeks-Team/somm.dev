"""Application settings and configuration"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    APP_NAME: str = "Somm.dev API"
    API_V1_STR: str = "/api/v1"

    # Environment
    ENVIRONMENT: str = "development"

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
        return [self.FRONTEND_URL]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
