"""Tests for repositories API endpoints."""

import os
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# Set required env vars before imports
os.environ["JWT_SECRET_KEY"] = "test_secret_key"
os.environ["GITHUB_CLIENT_ID"] = "test_client_id"
os.environ["GITHUB_CLIENT_SECRET"] = "test_client_secret"
os.environ["FRONTEND_URL"] = "http://localhost:3000"

from fastapi.testclient import TestClient
from jose import jwt

from app.main import app


client = TestClient(app)


def create_test_token(user_id: str = "test_user_id", github_id: str = "12345") -> str:
    """Create a test JWT token."""
    from app.api.deps import JWT_SECRET, JWT_ALGORITHM
    payload = {
        "sub": user_id,
        "github_id": github_id,
        "username": "testuser",
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


class TestGetRepositories:
    """Test suite for GET /api/repositories endpoint."""

    def test_get_repositories_requires_auth(self):
        """Test that endpoint requires authentication."""
        response = client.get("/repositories")

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_get_repositories_returns_list(self):
        """Test that endpoint returns list of repositories."""
        token = create_test_token()

        # Mock cache to return no data (will fetch from GitHub)
        mock_repos = [
            {
                "id": 1,
                "name": "repo1",
                "full_name": "owner/repo1",
                "private": False,
                "html_url": "https://github.com/owner/repo1",
            }
        ]

        with patch("app.api.routes.repositories.RepositoryCacheRepository") as MockCache:
            mock_cache_instance = MagicMock()
            mock_cache_instance.get_user_repos = AsyncMock(return_value=None)
            mock_cache_instance.set_user_repos = AsyncMock()
            MockCache.return_value = mock_cache_instance

            with patch("app.api.routes.repositories.GitHubService") as MockGitHub:
                mock_github_instance = MagicMock()
                mock_github_instance.list_user_repositories = AsyncMock(return_value=mock_repos)
                MockGitHub.return_value = mock_github_instance

                response = client.get(
                    "/repositories",
                    headers={"Authorization": f"Bearer {token}"}
                )

                assert response.status_code == 200
                data = response.json()
                assert "repositories" in data
                assert data["total"] == 1
                assert data["repositories"][0]["name"] == "repo1"

    @pytest.mark.asyncio
    async def test_get_repositories_uses_cache(self):
        """Test that endpoint uses cached data when available."""
        token = create_test_token()

        mock_cached_repos = [
            {
                "_id": "doc_id",
                "id": 1,
                "name": "cached_repo",
                "full_name": "owner/cached_repo",
                "private": False,
                "html_url": "https://github.com/owner/cached_repo",
                "user_id": "test_user_id",
                "cached_at": datetime.utcnow().isoformat(),
            }
        ]

        with patch("app.api.routes.repositories.RepositoryCacheRepository") as MockCache:
            mock_cache_instance = MagicMock()
            mock_cache_instance.get_user_repos = AsyncMock(return_value=mock_cached_repos)
            MockCache.return_value = mock_cache_instance

            response = client.get(
                "/repositories",
                headers={"Authorization": f"Bearer {token}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["repositories"][0]["name"] == "cached_repo"
            assert data["cached_at"] is not None


class TestRefreshRepositories:
    """Test suite for POST /api/repositories/refresh endpoint."""

    def test_refresh_repositories_requires_auth(self):
        """Test that refresh endpoint requires authentication."""
        response = client.post("/repositories/refresh")

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_clears_cache_and_fetches_fresh(self):
        """Test that refresh clears cache and fetches fresh data."""
        token = create_test_token()

        mock_repos = [
            {
                "id": 1,
                "name": "fresh_repo",
                "full_name": "owner/fresh_repo",
                "private": False,
                "html_url": "https://github.com/owner/fresh_repo",
            }
        ]

        with patch("app.api.routes.repositories.RepositoryCacheRepository") as MockCache:
            mock_cache_instance = MagicMock()
            mock_cache_instance.clear_user_repos = AsyncMock(return_value=1)
            mock_cache_instance.set_user_repos = AsyncMock()
            MockCache.return_value = mock_cache_instance

            with patch("app.api.routes.repositories.GitHubService") as MockGitHub:
                mock_github_instance = MagicMock()
                mock_github_instance.list_user_repositories = AsyncMock(return_value=mock_repos)
                MockGitHub.return_value = mock_github_instance

                response = client.post(
                    "/repositories/refresh",
                    headers={"Authorization": f"Bearer {token}"}
                )

                assert response.status_code == 200
                data = response.json()
                assert data["repositories"][0]["name"] == "fresh_repo"
                assert data["cached_at"] is None

                # Verify cache was cleared
                mock_cache_instance.clear_user_repos.assert_called_once()
