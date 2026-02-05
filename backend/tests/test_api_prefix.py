"""Tests for API prefix centralization (#59)

Verifies that all API routes use centralized prefix management via settings.API_V1_STR.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings


client = TestClient(app, raise_server_exceptions=False)


class TestApiPrefixConfiguration:
    def test_api_v1_prefix_configured(self):
        assert settings.API_V1_STR == "/api/v1"

    def test_evaluate_endpoint_uses_v1_prefix(self):
        response = client.post("/api/v1/evaluate")
        assert response.status_code != 404, (
            "Evaluate endpoint should exist under /api/v1"
        )

    def test_history_endpoint_uses_v1_prefix(self):
        response = client.get("/api/v1/history")
        assert response.status_code != 404, (
            "History endpoint should exist under /api/v1"
        )

    def test_repositories_endpoint_uses_v1_prefix(self):
        response = client.get("/api/v1/repositories")
        assert response.status_code != 404, (
            "Repositories endpoint should exist under /api/v1"
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
    def test_old_evaluate_prefix_removed(self):
        response = client.post("/api/evaluate")
        assert response.status_code == 404, "Old /api/evaluate should not exist"

    def test_old_history_prefix_removed(self):
        response = client.get("/api/history")
        assert response.status_code == 404, "Old /api/history should not exist"

    def test_old_repositories_prefix_removed(self):
        response = client.get("/repositories")
        assert response.status_code == 404, "Old /repositories should not exist"
