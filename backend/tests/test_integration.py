"""Integration tests for repository selection flow.

These tests verify the end-to-end flow of repository selection.
"""

import os
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

# Set required env vars
os.environ["JWT_SECRET_KEY"] = "test_secret_key_integration"
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


class TestAuthFlowIntegration:
    """Integration tests for authentication flow."""

    def test_oauth_redirect_url_structure(self):
        """Test that OAuth redirect URL has correct structure with repo scope."""
        response = client.get("/auth/github", follow_redirects=False)

        assert response.status_code == 307
        redirect_url = response.headers["location"]
        assert "github.com/login/oauth/authorize" in redirect_url
        assert "scope=repo" in redirect_url
        assert "client_id=test_client_id" in redirect_url
        assert "state=" in redirect_url

    def test_protected_endpoint_requires_auth(self):
        """Test that protected endpoints require authentication."""
        response = client.get("/repositories")
        assert response.status_code == 401

    def test_protected_endpoint_with_invalid_token(self):
        """Test that invalid token returns 401."""
        response = client.get(
            "/repositories", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


class TestRepositoryEndpointsIntegration:
    """Integration tests for repository endpoints."""

    @pytest.mark.asyncio
    async def test_get_repositories_with_mocked_github(self):
        """Test getting repositories with mocked GitHub API."""
        token = create_test_token()

        mock_github_repos = [
            {
                "id": 1,
                "name": "test-repo",
                "full_name": "owner/test-repo",
                "description": "Test repository",
                "private": False,
                "html_url": "https://github.com/owner/test-repo",
                "default_branch": "main",
                "stargazers_count": 10,
                "forks_count": 5,
                "language": "Python",
                "updated_at": "2024-01-01T00:00:00Z",
                "pushed_at": "2024-01-01T00:00:00Z",
            }
        ]

        with patch("app.api.routes.repositories.GitHubService") as MockGitHub:
            mock_github = MagicMock()
            mock_github.list_user_repositories = AsyncMock(
                return_value=mock_github_repos
            )
            MockGitHub.return_value = mock_github

            with patch(
                "app.api.routes.repositories.RepositoryCacheRepository"
            ) as MockCache:
                mock_cache = MagicMock()
                mock_cache.get_user_repos = AsyncMock(return_value=None)
                mock_cache.set_user_repos = AsyncMock()
                MockCache.return_value = mock_cache

                response = client.get(
                    "/repositories", headers={"Authorization": f"Bearer {token}"}
                )

                assert response.status_code == 200
                data = response.json()
                assert "repositories" in data
                assert data["total"] == 1
                assert data["repositories"][0]["name"] == "test-repo"


class TestCacheIntegration:
    """Integration tests for repository caching."""

    @pytest.mark.asyncio
    async def test_cache_is_used_when_available(self):
        """Test that cached data is returned when available."""
        token = create_test_token()

        cached_repos = [
            {
                "_id": "doc1",
                "id": 1,
                "name": "cached-repo",
                "full_name": "owner/cached-repo",
                "description": "Cached repository",
                "private": False,
                "html_url": "https://github.com/owner/cached-repo",
                "default_branch": "main",
                "stars": 100,
                "forks": 10,
                "language": "TypeScript",
                "updated_at": "2024-01-15T00:00:00Z",
                "pushed_at": "2024-01-15T00:00:00Z",
                "user_id": "test_user_id",
                "cached_at": datetime.utcnow().isoformat(),
            }
        ]

        with patch(
            "app.api.routes.repositories.RepositoryCacheRepository"
        ) as MockCache:
            mock_cache = MagicMock()
            mock_cache.get_user_repos = AsyncMock(return_value=cached_repos)
            MockCache.return_value = mock_cache

            response = client.get(
                "/repositories", headers={"Authorization": f"Bearer {token}"}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["cached_at"] is not None
            assert data["repositories"][0]["name"] == "cached-repo"
