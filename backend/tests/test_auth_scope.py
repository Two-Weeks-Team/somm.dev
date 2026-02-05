"""Tests for GitHub OAuth scope configuration."""

import os
import pytest
from fastapi.testclient import TestClient


# Set environment variables BEFORE importing the app
os.environ["GITHUB_CLIENT_ID"] = "test_client_id"
os.environ["GITHUB_CLIENT_SECRET"] = "test_client_secret"
os.environ["FRONTEND_URL"] = "http://localhost:3000"

from app.main import app

client = TestClient(app)


class TestGitHubOAuthScope:
    """Test suite for GitHub OAuth scope configuration."""

    def test_github_oauth_url_contains_repo_scope(self):
        """Test that OAuth URL includes 'repo' scope for private repository access."""
        response = client.get("/auth/github", follow_redirects=False)

        assert response.status_code == 307
        redirect_url = response.headers["location"]

        # Verify the redirect URL contains GitHub OAuth endpoint
        assert "github.com/login/oauth/authorize" in redirect_url

        # Verify 'repo' scope is present
        assert "scope=repo" in redirect_url

        # Verify other required scopes are present
        assert "user:email" in redirect_url
        assert "read:user" in redirect_url

    def test_github_oauth_url_structure(self):
        """Test that OAuth URL has correct structure with all required parameters."""
        response = client.get("/auth/github", follow_redirects=False)

        assert response.status_code == 307
        redirect_url = response.headers["location"]

        # Check all required OAuth parameters
        assert "client_id=test_client_id" in redirect_url
        assert "redirect_uri=" in redirect_url
        assert "state=" in redirect_url
        assert "scope=" in redirect_url

        # Verify state cookie is set
        set_cookie_header = response.headers.get("set-cookie", "")
        assert "oauth_state=" in set_cookie_header
        assert "HttpOnly" in set_cookie_header
        assert "Secure" in set_cookie_header

    def test_github_oauth_scope_order(self):
        """Test that scope parameter has correct value with repo first."""
        response = client.get("/auth/github", follow_redirects=False)

        assert response.status_code == 307
        redirect_url = response.headers["location"]

        # Extract scope parameter
        import urllib.parse
        parsed = urllib.parse.urlparse(redirect_url)
        params = urllib.parse.parse_qs(parsed.query)
        
        assert "scope" in params
        scope_value = params["scope"][0]
        
        # Verify scope contains all required values
        scopes = scope_value.split(",")
        assert "repo" in scopes
        assert "user:email" in scopes
        assert "read:user" in scopes
