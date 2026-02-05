"""Tests for User model with GitHub access token fields."""

from datetime import datetime
from app.models.user import UserInDB, UserResponse


class TestUserInDBModel:
    """Test suite for UserInDB model with token fields."""

    def test_user_in_db_has_github_access_token_field(self):
        """Test that UserInDB has github_access_token field."""
        user_data = {
            "github_id": 12345,
            "username": "testuser",
            "email": "test@example.com",
            "avatar_url": "https://example.com/avatar.png",
            "_id": "507f1f77bcf86cd799439011",
            "github_access_token": "ghp_test_token_123",
            "token_updated_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
        }

        user = UserInDB(**user_data)

        assert user.github_access_token == "ghp_test_token_123"
        assert user.token_updated_at is not None

    def test_user_in_db_token_fields_optional(self):
        """Test that token fields are optional (can be None)."""
        user_data = {
            "github_id": 12345,
            "username": "testuser",
            "email": "test@example.com",
            "avatar_url": "https://example.com/avatar.png",
            "_id": "507f1f77bcf86cd799439011",
            "created_at": datetime.utcnow(),
        }

        user = UserInDB(**user_data)

        assert user.github_access_token is None
        assert user.token_updated_at is None


class TestUserResponseModel:
    """Test suite for UserResponse model security."""

    def test_user_response_excludes_github_access_token(self):
        """Test that UserResponse does NOT include github_access_token field."""
        user_data = {
            "github_id": 12345,
            "username": "testuser",
            "email": "test@example.com",
            "avatar_url": "https://example.com/avatar.png",
            "id": "507f1f77bcf86cd799439011",
            "created_at": datetime.utcnow(),
        }

        user = UserResponse(**user_data)

        # UserResponse should NOT have github_access_token
        assert not hasattr(user, 'github_access_token')
        assert "github_access_token" not in user.model_dump()
