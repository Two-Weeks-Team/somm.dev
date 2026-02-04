"""User models for somm.dev backend.

This module contains all Pydantic models related to users:
- UserBase: Base user model with common fields
- UserCreate: Model for creating new users
- UserInDB: Model for user data stored in database
- UserResponse: Model for user data in API responses
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model with common fields.

    This model contains fields that are common across all user-related models.
    """

    github_id: int = Field(..., description="GitHub user ID")
    username: str = Field(..., description="GitHub username")
    email: EmailStr = Field(..., description="User email address")
    avatar_url: str = Field(..., description="GitHub avatar URL")
    preferences: Optional[Dict[str, Any]] = Field(
        default=None, description="User preferences"
    )


class UserCreate(UserBase):
    """Model for creating a new user.

    This model is used when a user is first authenticated via GitHub OAuth.
    All required fields from UserBase are inherited.
    """

    pass


class UserInDB(UserBase):
    """Model for user data stored in the database.

    This model extends UserBase with database-specific fields like id and timestamps.
    """

    id: str = Field(..., alias="_id", description="MongoDB document ID")
    hashed_password: Optional[str] = Field(
        default=None, description="Hashed password for future authentication"
    )
    created_at: datetime = Field(..., description="User creation timestamp")

    class Config:
        populate_by_name = True


class UserResponse(UserBase):
    """Model for user data in API responses.

    This model is used when returning user data in API responses.
    It excludes sensitive fields like hashed_password.
    """

    id: str = Field(..., description="User ID")
    created_at: datetime = Field(..., description="User creation timestamp")
