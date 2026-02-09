"""Application settings and configuration"""

import secrets
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


_DEFAULT_JWT_SECRET = secrets.token_urlsafe(32)


class Settings(BaseSettings):
    """Application settings loaded from environment variables

    Security Note: JWT_SECRET_KEY MUST be set via environment variable in production.
    The default random value is only for development convenience.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "Somm.dev API"
    API_V1_STR: str = "/api"

    ENVIRONMENT: str = "development"

    JWT_SECRET_KEY: str = _DEFAULT_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 7

    # GitHub OAuth (required for production, optional for testing)
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: str = ""

    # URLs
    FRONTEND_URL: str = "https://www.somm.dev"
    BACKEND_URL: str = "http://localhost:8000"

    # Database
    MONGODB_URI: str = "mongodb://localhost:27017/somm_db"
    MONGO_DB: str = "somm"

    # LLM API (Vertex AI Express only)
    VERTEX_API_KEY: str = ""
    GOOGLE_CLOUD_PROJECT: str = ""
    VERTEX_PREMIUM_USER_IDS: str = ""
    VERTEX_ADMIN_USER_IDS: str = ""
    VERTEX_PREMIUM_EMAILS: str = ""
    VERTEX_ADMIN_EMAILS: str = ""

    # LangSmith Tracing (optional - enables LangGraph monitoring)
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_TRACING: bool = False
    LANGCHAIN_PROJECT: str = "somm-dev"

    # GitHub
    GITHUB_TOKEN: str = ""

    # Optional: Error Tracking
    SENTRY_DSN: str = ""

    # Optional: Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # RAG Enrichment (Gemini embeddings + Google Search grounding)
    RAG_ENABLED: bool = True
    RAG_TOP_K: int = 4
    RAG_EMBEDDING_MODEL: str = "gemini-embedding-001"

    # Technique Execution Settings
    MAX_CONCURRENT_TECHNIQUES: int = 5
    TECHNIQUE_TIMEOUT_SECONDS: int = 60

    # Technique Cache Settings
    TECHNIQUE_CACHE_TTL_HOURS: int = 24
    TECHNIQUE_CACHE_ENABLED: bool = True

    @field_validator("MAX_CONCURRENT_TECHNIQUES")
    @classmethod
    def validate_max_concurrent(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("MAX_CONCURRENT_TECHNIQUES must be positive (> 0)")
        return v

    @field_validator("TECHNIQUE_TIMEOUT_SECONDS")
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("TECHNIQUE_TIMEOUT_SECONDS must be positive (> 0)")
        return v

    # Server settings
    PORT: int = 8000
    DEBUG: bool = False

    # Proxy settings (for IP-based rate limiting)
    # Set to True when running behind a trusted reverse proxy (e.g., nginx, Cloudflare)
    TRUSTED_PROXY: bool = False

    @property
    def CORS_ORIGINS(self) -> List[str]:
        origins = [self.FRONTEND_URL]
        if self.FRONTEND_URL.startswith("https://www."):
            origins.append(self.FRONTEND_URL.replace("https://www.", "https://", 1))
        return origins


settings = Settings()
