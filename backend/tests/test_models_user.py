# backend/tests/test_models_user.py
"""
Tests for User models.
RED Phase: These tests should FAIL initially because the user model doesn't exist yet.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


class TestUserModelImports:
    """Test that user models can be imported correctly"""

    def test_import_user_base(self):
        """Test that UserBase can be imported from app.models.user"""
        from app.models.user import UserBase

        assert UserBase is not None

    def test_import_user_create(self):
        """Test that UserCreate can be imported from app.models.user"""
        from app.models.user import UserCreate

        assert UserCreate is not None

    def test_import_user_in_db(self):
        """Test that UserInDB can be imported from app.models.user"""
        from app.models.user import UserInDB

        assert UserInDB is not None

    def test_import_user_response(self):
        """Test that UserResponse can be imported from app.models.user"""
        from app.models.user import UserResponse

        assert UserResponse is not None


class TestUserBaseModel:
    """Test UserBase model fields and validation"""

    def test_user_base_has_github_id(self):
        """Test that UserBase has github_id field"""
        from app.models.user import UserBase

        assert "github_id" in UserBase.__fields__

    def test_user_base_has_username(self):
        """Test that UserBase has username field"""
        from app.models.user import UserBase

        assert "username" in UserBase.__fields__

    def test_user_base_has_email(self):
        """Test that UserBase has email field"""
        from app.models.user import UserBase

        assert "email" in UserBase.__fields__

    def test_user_base_has_avatar_url(self):
        """Test that UserBase has avatar_url field"""
        from app.models.user import UserBase

        assert "avatar_url" in UserBase.__fields__

    def test_user_base_optional_fields(self):
        """Test that UserBase has optional preferences field"""
        from app.models.user import UserBase

        assert "preferences" in UserBase.__fields__


class TestUserCreateModel:
    """Test UserCreate model"""

    def test_user_create_with_required_fields(self):
        """Test that UserCreate can be created with required fields"""
        from app.models.user import UserCreate

        user_data = UserCreate(
            github_id=12345,
            username="testuser",
            email="test@example.com",
            avatar_url="https://github.com/avatars/testuser",
        )

        assert user_data.github_id == 12345
        assert user_data.username == "testuser"
        assert user_data.email == "test@example.com"
        assert user_data.avatar_url == "https://github.com/avatars/testuser"

    def test_user_create_with_preferences(self):
        """Test that UserCreate can include preferences"""
        from app.models.user import UserCreate

        preferences = {"theme": "dark", "notifications": True}
        user_data = UserCreate(
            github_id=12345,
            username="testuser",
            email="test@example.com",
            avatar_url="https://github.com/avatars/testuser",
            preferences=preferences,
        )

        assert user_data.preferences == preferences


class TestUserInDBModel:
    """Test UserInDB model"""

    def test_user_in_db_inherits_from_user_base(self):
        """Test that UserInDB inherits from UserBase"""
        from app.models.user import UserBase, UserInDB

        # UserInDB should have all UserBase fields plus additional fields
        assert "github_id" in UserInDB.__fields__
        assert "username" in UserInDB.__fields__
        assert "email" in UserInDB.__fields__
        assert "avatar_url" in UserInDB.__fields__

    def test_user_in_db_has_id_field(self):
        """Test that UserInDB has id field for MongoDB"""
        from app.models.user import UserInDB

        assert "id" in UserInDB.__fields__

    def test_user_in_db_has_created_at(self):
        """Test that UserInDB has created_at field"""
        from app.models.user import UserInDB

        assert "created_at" in UserInDB.__fields__

    def test_user_in_db_has_hashed_password(self):
        """Test that UserInDB has hashed_password field"""
        from app.models.user import UserInDB

        assert "hashed_password" in UserInDB.__fields__

    def test_user_in_db_create_instance(self):
        """Test creating UserInDB instance"""
        from app.models.user import UserInDB
        from bson import ObjectId

        now = datetime.utcnow()
        user = UserInDB(
            id=str(ObjectId()),
            github_id=12345,
            username="testuser",
            email="test@example.com",
            avatar_url="https://github.com/avatars/testuser",
            hashed_password="hashedpassword123",
            created_at=now,
        )

        assert user.github_id == 12345
        assert user.username == "testuser"
        assert user.hashed_password == "hashedpassword123"


class TestUserResponseModel:
    """Test UserResponse model"""

    def test_user_response_inherits_from_user_base(self):
        """Test that UserResponse inherits from UserBase"""
        from app.models.user import UserBase, UserResponse

        assert "github_id" in UserResponse.__fields__
        assert "username" in UserResponse.__fields__

    def test_user_response_has_id(self):
        """Test that UserResponse has id field"""
        from app.models.user import UserResponse

        assert "id" in UserResponse.__fields__

    def test_user_response_has_created_at(self):
        """Test that UserResponse has created_at field"""
        from app.models.user import UserResponse

        assert "created_at" in UserResponse.__fields__

    def test_user_response_excludes_sensitive_data(self):
        """Test that UserResponse does not include hashed_password"""
        from app.models.user import UserResponse

        assert "hashed_password" not in UserResponse.__fields__


class TestUserModelValidation:
    """Test user model validation"""

    def test_user_create_email_validation(self):
        """Test that UserCreate validates email format"""
        from app.models.user import UserCreate
        from pydantic import ValidationError

        try:
            UserCreate(
                github_id=12345,
                username="testuser",
                email="invalid-email",  # Invalid email format
                avatar_url="https://github.com/avatars/testuser",
            )
            assert False, "Should have raised ValidationError"
        except ValidationError:
            pass  # Expected behavior

    def test_user_create_github_id_required(self):
        """Test that github_id is required"""
        from app.models.user import UserCreate
        from pydantic import ValidationError

        try:
            UserCreate(
                username="testuser",
                email="test@example.com",
                avatar_url="https://github.com/avatars/testuser",
            )
            assert False, "Should have raised ValidationError"
        except ValidationError:
            pass  # Expected behavior
