"""
FastAPI Backend for somm.dev
Compatible with Python 3.12+ (Python 3.14 ready)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Somm.dev API", description="Backend API for somm.dev", version="1.0.0"
)

# CORS middleware - Next.js frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models
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


# Routes
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


# Run server
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True, log_level="info")
