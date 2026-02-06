"""FastAPI Backend for somm.dev
Compatible with Python 3.12+ (Python 3.14 ready)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from app.core.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.api.routes import evaluate, history, auth, repositories


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup/shutdown events"""
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for somm.dev",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes - centralized prefix management
app.include_router(evaluate.router, prefix=settings.API_V1_STR)
app.include_router(history.router, prefix=settings.API_V1_STR)

# Repositories route - mounted at root level (frontend expects /repositories, not /api/repositories)
app.include_router(repositories.router)

# Auth routes - kept at root level for OAuth callback compatibility
app.include_router(auth.router)


class HealthResponse(BaseModel):
    status: str
    version: str


class MessageRequest(BaseModel):
    message: str
    user_id: Optional[str] = None


class MessageResponse(BaseModel):
    success: bool
    message: str
    echo: str


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - Health check"""
    return HealthResponse(status="healthy", version="1.0.0")


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", version="1.0.0")


@app.post("/api/echo", response_model=MessageResponse)
async def echo_message(request: MessageRequest):
    """Echo endpoint - Test API connectivity"""
    return MessageResponse(
        success=True, message="Message received successfully", echo=request.message
    )
