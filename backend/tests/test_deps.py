"""Tests for API dependencies (deps.py)."""

import os
import pytest
from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import jwt

# Set JWT secret before importing deps
os.environ["JWT_SECRET_KEY"] = "test_secret_key_for_testing"

from app.api.deps import (
    decode_token,
    get_current_user,
    get_optional_user,
    get_current_user_token,
    User,
)


class TestDecodeToken:
    """Test suite for decode_token function."""

    def test_decode_valid_token(self):
        """Test decoding a valid JWT token."""
        from app.api.deps import JWT_SECRET, JWT_ALGORITHM

        payload = {"sub": "user123", "github_id": "456"}
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        decoded = decode_token(token)

        assert decoded["sub"] == "user123"
        assert decoded["github_id"] == "456"

    def test_decode_invalid_token_raises_401(self):
        """Test that invalid token raises HTTPException with 401."""
        with pytest.raises(HTTPException) as exc_info:
            decode_token("invalid_token")

        assert exc_info.value.status_code == 401
        assert "Invalid authentication credentials" in str(exc_info.value.detail)


class TestUserClass:
    """Test suite for User class."""

    def test_user_creation(self):
        """Test creating a User instance."""
        user = User(
            id="507f1f77bcf86cd799439011",
            github_id="12345",
            username="testuser",
            email="test@example.com",
            avatar_url="https://example.com/avatar.png",
        )

        assert user.id == "507f1f77bcf86cd799439011"
        assert user.github_id == "12345"
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.avatar_url == "https://example.com/avatar.png"

    def test_user_optional_fields(self):
        """Test User creation with optional fields as None."""
        user = User(
            id="507f1f77bcf86cd799439011",
            github_id="12345",
            username="testuser",
        )

        assert user.email is None
        assert user.avatar_url is None
