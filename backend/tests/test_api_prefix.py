"""Tests for API prefix centralization (#59)

Verifies that all API routes use centralized prefix management via settings.API_V1_STR.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings


client = TestClient(app, raise_server_exceptions=False)


class TestApiPrefixConfiguration:
    def test_api_prefix_configured(self):
        assert settings.API_V1_STR == "/api"

    def test_evaluate_endpoint_uses_api_prefix(self):
        response = client.post("/api/evaluate")
        assert response.status_code != 404, "Evaluate endpoint should exist under /api"

    def test_history_endpoint_uses_api_prefix(self):
        response = client.get("/api/history")
        assert response.status_code != 404, "History endpoint should exist under /api"

    def test_repositories_endpoint_at_root(self):
        response = client.get("/repositories")
        assert response.status_code != 404, (
            "Repositories endpoint should exist at /repositories"
        )


class TestAuthEndpointNotUnderV1:
    def test_auth_github_at_root(self):
        response = client.get("/auth/github", follow_redirects=False)
        assert response.status_code in (307, 302), (
            "Auth github should redirect (not 404)"
        )

    def test_auth_me_at_root(self):
        response = client.get("/auth/me")
        assert response.status_code != 404, "Auth me should be at /auth/me"


class TestHealthCheckAtRoot:
    def test_health_check_at_root(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200


class TestOldEndpointsRemoved:
    def test_old_v1_evaluate_prefix_removed(self):
        response = client.post("/api/v1/evaluate")
        assert response.status_code == 404, "/api/v1/evaluate should not exist"

    def test_old_v1_history_prefix_removed(self):
        response = client.get("/api/v1/history")
        assert response.status_code == 404, "/api/v1/history should not exist"

    def test_old_v1_repositories_prefix_removed(self):
        response = client.get("/api/v1/repositories")
        assert response.status_code == 404, (
            "/api/v1/repositories should not exist (route is at /repositories)"
        )
