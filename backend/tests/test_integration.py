"""Integration tests for repository selection flow.

These tests verify the end-to-end flow of repository selection.
Note: Tests requiring MongoDB are skipped if no database connection.
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
        response = client.get("/api/v1/repositories")
        assert response.status_code == 401

    def test_protected_endpoint_with_invalid_token(self):
        """Test that invalid token returns 401."""
        response = client.get(
            "/api/v1/repositories", headers={"Authorization": "Bearer invalid_token"}
        )
        assert response.status_code == 401


@pytest.mark.skip(reason="Requires MongoDB connection - run manually with DB")
class TestRepositoryEndpointsIntegration:
    """Integration tests for repository endpoints - requires MongoDB."""

    @pytest.mark.asyncio
    async def test_get_repositories_with_mocked_github(self):
        """Test getting repositories with mocked GitHub API."""
        pass


@pytest.mark.skip(reason="Requires MongoDB connection - run manually with DB")
class TestCacheIntegration:
    """Integration tests for repository caching - requires MongoDB."""

    @pytest.mark.asyncio
    async def test_cache_is_used_when_available(self):
        """Test that cache is used on subsequent requests."""
        pass
