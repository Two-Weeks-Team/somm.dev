"""Repository models for somm.dev backend.

This module contains all Pydantic models related to GitHub repositories:
- RepositoryBase: Base repository model with common fields
- RepositoryCache: Model for cached repository data with TTL
- RepositoryListResponse: Response model for repository list endpoint
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class RepositoryBase(BaseModel):
    """Base repository model with common fields.

    This model represents a GitHub repository with essential metadata.
    """

    id: int = Field(..., description="GitHub repository ID")
    name: str = Field(..., description="Repository name")
    full_name: str = Field(..., description="Full repository name (owner/repo)")
    description: Optional[str] = Field(default=None, description="Repository description")
    private: bool = Field(..., description="Whether the repository is private")
    html_url: str = Field(..., description="Repository URL on GitHub")
    default_branch: Optional[str] = Field(default="main", description="Default branch name")
    stars: int = Field(default=0, description="Number of stars")
    forks: int = Field(default=0, description="Number of forks")
    language: Optional[str] = Field(default=None, description="Primary programming language")
    updated_at: Optional[datetime] = Field(default=None, description="Last updated timestamp")
    pushed_at: Optional[datetime] = Field(default=None, description="Last pushed timestamp")


class RepositoryCache(RepositoryBase):
    """Model for cached repository data with user association and TTL.

    This model extends RepositoryBase with caching-specific fields.
    """

    user_id: str = Field(..., description="MongoDB user ID who owns this cache entry")
    cached_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when this cache entry was created"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RepositoryListResponse(BaseModel):
    """Response model for repository list endpoint.

    Returns a list of repositories with metadata about the response.
    """

    repositories: List[RepositoryBase] = Field(..., description="List of repositories")
    total: int = Field(..., description="Total number of repositories")
    cached_at: Optional[datetime] = Field(
        default=None,
        description="Timestamp when data was cached (null if fresh from GitHub)"
    )
