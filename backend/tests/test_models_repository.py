"""Tests for Repository models."""

from datetime import datetime, timezone
from app.models.repository import (
    RepositoryBase,
    RepositoryCache,
    RepositoryListResponse,
)


class TestRepositoryBaseModel:
    """Test suite for RepositoryBase model."""

    def test_repository_base_model_fields(self):
        """Test that RepositoryBase has all required fields."""
        repo_data = {
            "id": 123,
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "description": "A test repository",
            "private": False,
            "html_url": "https://github.com/owner/test-repo",
            "default_branch": "main",
            "stars": 42,
            "forks": 10,
            "language": "Python",
            "updated_at": datetime.now(timezone.utc),
            "pushed_at": datetime.now(timezone.utc),
        }

        repo = RepositoryBase(**repo_data)

        assert repo.id == 123
        assert repo.name == "test-repo"
        assert repo.full_name == "owner/test-repo"
        assert repo.private is False
        assert repo.html_url == "https://github.com/owner/test-repo"
        assert repo.stars == 42
        assert repo.forks == 10
        assert repo.language == "Python"

    def test_repository_base_optional_fields(self):
        """Test that optional fields have default values."""
        repo_data = {
            "id": 123,
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "private": True,
            "html_url": "https://github.com/owner/test-repo",
        }

        repo = RepositoryBase(**repo_data)

        assert repo.description is None
        assert repo.default_branch == "main"
        assert repo.stars == 0
        assert repo.forks == 0
        assert repo.language is None


class TestRepositoryCacheModel:
    """Test suite for RepositoryCache model."""

    def test_repository_cache_includes_user_id_and_cached_at(self):
        """Test that RepositoryCache has user_id and cached_at fields."""
        now = datetime.now(timezone.utc)
        repo_data = {
            "id": 123,
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "private": False,
            "html_url": "https://github.com/owner/test-repo",
            "user_id": "507f1f77bcf86cd799439011",
            "cached_at": now,
        }

        repo = RepositoryCache(**repo_data)

        assert repo.user_id == "507f1f77bcf86cd799439011"
        assert repo.cached_at == now

    def test_repository_cache_auto_sets_cached_at(self):
        """Test that cached_at is auto-set to current time."""
        repo_data = {
            "id": 123,
            "name": "test-repo",
            "full_name": "owner/test-repo",
            "private": False,
            "html_url": "https://github.com/owner/test-repo",
            "user_id": "507f1f77bcf86cd799439011",
        }

        before = datetime.now(timezone.utc)
        repo = RepositoryCache(**repo_data)
        after = datetime.now(timezone.utc)

        assert before <= repo.cached_at <= after


class TestRepositoryListResponse:
    """Test suite for RepositoryListResponse model."""

    def test_repository_list_response_structure(self):
        """Test RepositoryListResponse has correct structure."""
        repos = [
            RepositoryBase(
                id=1,
                name="repo1",
                full_name="owner/repo1",
                private=False,
                html_url="https://github.com/owner/repo1",
            ),
            RepositoryBase(
                id=2,
                name="repo2",
                full_name="owner/repo2",
                private=True,
                html_url="https://github.com/owner/repo2",
            ),
        ]

        response = RepositoryListResponse(
            repositories=repos,
            total=2,
            cached_at=datetime.utcnow(),
        )

        assert len(response.repositories) == 2
        assert response.total == 2
        assert response.cached_at is not None
