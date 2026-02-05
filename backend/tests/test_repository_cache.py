"""Tests for RepositoryCacheRepository.

These tests require a running MongoDB instance.
"""

import pytest
from datetime import datetime
from app.database.repositories.repository_cache import RepositoryCacheRepository


@pytest.fixture
def repo_cache():
    """Fixture for RepositoryCacheRepository instance."""
    return RepositoryCacheRepository()


@pytest.fixture
def sample_repo_data():
    """Fixture for sample repository data."""
    return [
        {
            "id": 1,
            "name": "repo1",
            "full_name": "owner/repo1",
            "private": False,
            "html_url": "https://github.com/owner/repo1",
        },
        {
            "id": 2,
            "name": "repo2",
            "full_name": "owner/repo2",
            "private": True,
            "html_url": "https://github.com/owner/repo2",
        },
    ]


@pytest.mark.asyncio
class TestRepositoryCacheRepository:
    """Test suite for RepositoryCacheRepository."""

    async def test_set_and_get_user_repos(self, repo_cache, sample_repo_data):
        """Test setting and getting user repositories."""
        user_id = "test_user_123"

        # Clear any existing cache
        await repo_cache.clear_user_repos(user_id)

        # Set repos
        await repo_cache.set_user_repos(user_id, sample_repo_data)

        # Get repos
        repos = await repo_cache.get_user_repos(user_id)

        assert repos is not None
        assert len(repos) == 2
        assert repos[0]["name"] in ["repo1", "repo2"]
        assert repos[0]["user_id"] == user_id
        assert "cached_at" in repos[0]

    async def test_clear_user_repos(self, repo_cache, sample_repo_data):
        """Test clearing user repository cache."""
        user_id = "test_user_456"

        # Set repos
        await repo_cache.set_user_repos(user_id, sample_repo_data)

        # Verify repos exist
        repos = await repo_cache.get_user_repos(user_id)
        assert repos is not None

        # Clear repos
        deleted_count = await repo_cache.clear_user_repos(user_id)
        assert deleted_count == 2

        # Verify repos are gone
        repos = await repo_cache.get_user_repos(user_id)
        assert repos is None

    async def test_is_cache_valid(self, repo_cache, sample_repo_data):
        """Test cache validity check."""
        user_id = "test_user_789"

        # Initially no cache
        assert await repo_cache.is_cache_valid(user_id) is False

        # Set repos
        await repo_cache.set_user_repos(user_id, sample_repo_data)

        # Cache should be valid
        assert await repo_cache.is_cache_valid(user_id) is True

        # Clear cache
        await repo_cache.clear_user_repos(user_id)

        # Cache should be invalid
        assert await repo_cache.is_cache_valid(user_id) is False

    async def test_get_cache_timestamp(self, repo_cache, sample_repo_data):
        """Test getting cache timestamp."""
        user_id = "test_user_abc"

        # No cache initially
        timestamp = await repo_cache.get_cache_timestamp(user_id)
        assert timestamp is None

        # Set repos
        before = datetime.utcnow()
        await repo_cache.set_user_repos(user_id, sample_repo_data)
        after = datetime.utcnow()

        # Get timestamp
        timestamp = await repo_cache.get_cache_timestamp(user_id)
        assert timestamp is not None
        assert before <= timestamp <= after

    async def test_set_user_repos_overwrites_existing(self, repo_cache, sample_repo_data):
        """Test that set_user_repos overwrites existing cache."""
        user_id = "test_user_def"

        # Set initial repos
        await repo_cache.set_user_repos(user_id, sample_repo_data)

        # Set new repos
        new_repos = [
            {
                "id": 3,
                "name": "repo3",
                "full_name": "owner/repo3",
                "private": False,
                "html_url": "https://github.com/owner/repo3",
            }
        ]
        await repo_cache.set_user_repos(user_id, new_repos)

        # Should only have the new repo
        repos = await repo_cache.get_user_repos(user_id)
        assert len(repos) == 1
        assert repos[0]["name"] == "repo3"

    async def test_ensure_ttl_index(self, repo_cache):
        """Test TTL index creation."""
        # Create index
        await repo_cache.ensure_ttl_index()

        # Get indexes
        indexes = await repo_cache.collection.list_indexes().to_list(length=None)
        index_names = [idx["name"] for idx in indexes]

        # Check TTL index exists
        assert "cached_at_ttl" in index_names

        # Find TTL index
        ttl_index = next((idx for idx in indexes if idx["name"] == "cached_at_ttl"), None)
        assert ttl_index is not None
        assert ttl_index.get("expireAfterSeconds") == 3600

    async def test_empty_repos_list(self, repo_cache):
        """Test setting empty repos list."""
        user_id = "test_user_empty"

        # Set empty list
        await repo_cache.set_user_repos(user_id, [])

        # Should return None (no documents inserted)
        repos = await repo_cache.get_user_repos(user_id)
        assert repos is None
