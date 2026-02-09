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
    API_V1_STR: str = "/api"

    ENVIRONMENT: str = "development"

    JWT_SECRET_KEY: str = _DEFAULT_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 7

    # GitHub OAuth
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str

    # URLs
    FRONTEND_URL: str = "https://www.somm.dev"
    BACKEND_URL: str = "http://localhost:8000"

    # Database
    MONGODB_URI: str = "mongodb://localhost:27017/somm_db"
    MONGO_DB: str = "somm"

    # LLM APIs
    GEMINI_API_KEY: str = ""

    # Vertex AI Express (API key auth)
    VERTEX_API_KEY: str = ""
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_CLOUD_LOCATION: str = "asia-northeast3"
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

    # RAG Enrichment (adds context retrieval before evaluation)
    RAG_ENABLED: bool = True
    RAG_TOP_K: int = 4
    RAG_EMBEDDING_MODEL: str = "hf:nomic-ai/nomic-embed-text-v1.5"

    # Synthetic API (for embeddings - free tier)
    SYNTHETIC_API_KEY: str = ""
    SYNTHETIC_BASE_URL: str = "https://api.synthetic.new/openai/v1"

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
