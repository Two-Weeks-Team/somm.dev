"""Integration tests for all API endpoints with auth bypass.

Tests verify:
- Response status codes
- Response schema validation
- Auth requirements (protected vs public)
- Basic functionality
"""

from unittest.mock import patch, AsyncMock, MagicMock


class TestHealthEndpoints:
    def test_root_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_echo_returns_message(self, client):
        response = client.post("/api/echo", json={"message": "test"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["echo"] == "test"


class TestTechniquesEndpoints:
    def test_techniques_stats_returns_200(self, client):
        response = client.get("/api/techniques/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_category" in data
        assert "by_priority" in data
        assert "by_mode" in data
        assert data["total"] > 0

    def test_techniques_list_returns_200(self, client):
        response = client.get("/api/techniques")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        first = data[0]
        assert "id" in first
        assert "name" in first
        assert "category" in first

    def test_techniques_filter_by_category(self, client):
        response = client.get("/api/techniques?category=aroma")
        assert response.status_code == 200
        data = response.json()
        for tech in data:
            assert tech["category"] == "aroma"

    def test_techniques_filter_by_mode(self, client):
        response = client.get("/api/techniques?mode=grand_tasting")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_techniques_invalid_category_returns_400(self, client):
        response = client.get("/api/techniques?category=invalid")
        assert response.status_code == 400

    def test_technique_detail_returns_200(self, client):
        list_response = client.get("/api/techniques")
        techniques = list_response.json()
        technique_id = techniques[0]["id"]

        response = client.get(f"/api/techniques/{technique_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == technique_id
        assert "description" in data
        assert "prompt_template" in data

    def test_technique_detail_not_found_returns_404(self, client):
        response = client.get("/api/techniques/nonexistent-technique")
        assert response.status_code == 404


class TestAuthEndpoints:
    def test_auth_github_redirects(self, client):
        response = client.get("/auth/github", follow_redirects=False)
        assert response.status_code == 307
        assert "github.com/login/oauth/authorize" in response.headers.get(
            "location", ""
        )

    def test_auth_me_without_token_returns_401(self, client):
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_auth_me_with_token_returns_user(self, client, test_jwt_token, mock_user):
        with patch("app.api.routes.auth.UserRepository") as MockRepo:
            mock_instance = MagicMock()
            mock_instance.get_by_id = AsyncMock(
                return_value={
                    "_id": mock_user.id,
                    "github_id": mock_user.github_id,
                    "username": mock_user.username,
                    "email": mock_user.email,
                    "avatar_url": mock_user.avatar_url,
                    "created_at": "2025-01-01T00:00:00Z",
                }
            )
            MockRepo.return_value = mock_instance

            response = client.get(
                "/auth/me", headers={"Authorization": f"Bearer {test_jwt_token}"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "username" in data

    def test_auth_logout_returns_200(self, auth_client):
        response = auth_client.post("/auth/logout")
        assert response.status_code == 200


class TestRepositoriesEndpoints:
    def test_repositories_without_auth_returns_401(self, client):
        response = client.get("/repositories")
        assert response.status_code == 401

    def test_repositories_with_auth_returns_list(
        self, auth_client, mock_repository_data
    ):
        with (
            patch("app.api.routes.repositories.RepositoryCacheRepository") as MockCache,
            patch("app.api.routes.repositories.GitHubService") as MockGH,
        ):
            mock_cache = MagicMock()
            mock_cache.get_user_repos = AsyncMock(return_value=None)
            mock_cache.set_user_repos = AsyncMock(return_value=True)
            MockCache.return_value = mock_cache

            mock_gh = MagicMock()
            mock_gh.list_user_repositories = AsyncMock(
                return_value=mock_repository_data
            )
            MockGH.return_value = mock_gh

            response = auth_client.get("/repositories")
            assert response.status_code == 200
            data = response.json()
            assert "repositories" in data
            assert "total" in data

    def test_repositories_refresh_without_auth_returns_401(self, client):
        response = client.post("/repositories/refresh")
        assert response.status_code == 401


class TestQuotaEndpoints:
    def test_quota_status_without_auth_returns_401(self, client):
        response = client.get("/api/quota/status")
        assert response.status_code == 401

    def test_quota_status_with_auth_returns_quotas(self, auth_client):
        with (
            patch("app.api.routes.quota.APIKeyRepository") as MockRepo,
            patch("app.api.routes.quota.check_quota") as mock_check,
        ):
            mock_instance = MagicMock()
            mock_instance.get_status = AsyncMock(return_value=[])
            MockRepo.return_value = mock_instance

            from app.services.quota import QuotaResult

            mock_check.return_value = QuotaResult(
                allowed=True,
                reason="OK",
                remaining=5,
                daily_limit=10,
                used_today=5,
            )

            response = auth_client.get("/api/quota/status")
            assert response.status_code == 200
            data = response.json()
            assert "quotas" in data
            assert "plan" in data

    def test_quota_limits_returns_rules(self, auth_client):
        response = auth_client.get("/api/quota/limits")
        assert response.status_code == 200
        data = response.json()
        assert "rules" in data
        assert "current_plan" in data


class TestAPIKeysEndpoints:
    def test_api_keys_status_without_auth_returns_401(self, client):
        response = client.get("/api/api/keys/status")
        assert response.status_code == 401

    def test_api_keys_status_with_auth_returns_list(self, auth_client):
        with patch("app.api.routes.api_keys.APIKeyRepository") as MockRepo:
            mock_instance = MagicMock()
            mock_instance.get_status = AsyncMock(return_value=[])
            MockRepo.return_value = mock_instance

            response = auth_client.get("/api/api/keys/status")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_api_keys_validate_without_auth_returns_401(self, client):
        response = client.post(
            "/api/api/keys/validate", json={"provider": "google", "api_key": "test_key"}
        )
        assert response.status_code == 401


class TestHistoryEndpoints:
    def test_history_without_auth_returns_401(self, client):
        response = client.get("/api/history")
        assert response.status_code == 401

    def test_history_with_auth_returns_list(self, auth_client):
        with patch("app.api.routes.history.get_user_history") as mock_history:
            mock_history.return_value = []

            response = auth_client.get("/api/history")
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert "total" in data


class TestEvaluateEndpoints:
    def test_evaluate_without_auth_returns_401(self, client):
        response = client.post(
            "/api/evaluate",
            json={
                "repo_url": "https://github.com/test/repo",
                "criteria": "basic",
            },
        )
        assert response.status_code == 401

    def test_evaluate_result_public_demo_returns_200(self, client):
        from app.api.routes.evaluate import PUBLIC_DEMO_EVALUATIONS

        demo_id = next(iter(PUBLIC_DEMO_EVALUATIONS))

        with patch("app.api.routes.evaluate.get_evaluation_result") as mock_result:
            mock_result.return_value = {
                "evaluation_id": demo_id,
                "final_evaluation": {"score": 85},
                "created_at": "2025-01-01T00:00:00Z",
            }

            response = client.get(f"/api/evaluate/{demo_id}/result")
            assert response.status_code == 200


class TestGraphEndpoints:
    def test_graph_public_demo_returns_200(self, client):
        from app.api.routes.graph import PUBLIC_DEMO_EVALUATIONS

        demo_id = next(iter(PUBLIC_DEMO_EVALUATIONS))

        with patch("app.api.routes.graph.EvaluationRepository") as MockRepo:
            mock_instance = MagicMock()
            mock_instance.get_by_id = AsyncMock(
                return_value={
                    "_id": demo_id,
                    "user_id": "some_user",
                    "evaluation_mode": "six_sommeliers",
                }
            )
            MockRepo.return_value = mock_instance

            response = client.get(f"/api/evaluate/{demo_id}/graph")
            assert response.status_code == 200
            data = response.json()
            assert "nodes" in data
            assert "edges" in data

    def test_graph_timeline_public_demo_returns_200(self, client):
        from app.api.routes.graph import PUBLIC_DEMO_EVALUATIONS

        demo_id = next(iter(PUBLIC_DEMO_EVALUATIONS))

        with patch("app.api.routes.graph.EvaluationRepository") as MockRepo:
            mock_instance = MagicMock()
            mock_instance.get_by_id = AsyncMock(
                return_value={
                    "_id": demo_id,
                    "user_id": "some_user",
                    "evaluation_mode": "six_sommeliers",
                    "methodology_trace": [],
                }
            )
            MockRepo.return_value = mock_instance

            response = client.get(f"/api/evaluate/{demo_id}/graph/timeline")
            assert response.status_code == 200

    def test_graph_mode_public_demo_returns_200(self, client):
        from app.api.routes.graph import PUBLIC_DEMO_EVALUATIONS

        demo_id = next(iter(PUBLIC_DEMO_EVALUATIONS))

        with patch("app.api.routes.graph.EvaluationRepository") as MockRepo:
            mock_instance = MagicMock()
            mock_instance.get_by_id = AsyncMock(
                return_value={
                    "_id": demo_id,
                    "user_id": "some_user",
                    "evaluation_mode": "six_sommeliers",
                }
            )
            MockRepo.return_value = mock_instance

            response = client.get(f"/api/evaluate/{demo_id}/graph/mode")
            assert response.status_code == 200
            data = response.json()
            assert "mode" in data

    def test_graph_3d_public_demo_returns_200(self, client):
        from app.api.routes.graph import PUBLIC_DEMO_EVALUATIONS

        demo_id = next(iter(PUBLIC_DEMO_EVALUATIONS))

        with patch("app.api.routes.graph.EvaluationRepository") as MockRepo:
            mock_instance = MagicMock()
            mock_instance.get_by_id = AsyncMock(
                return_value={
                    "_id": demo_id,
                    "user_id": "some_user",
                    "evaluation_mode": "six_sommeliers",
                    "methodology_trace": [],
                }
            )
            MockRepo.return_value = mock_instance

            response = client.get(f"/api/evaluate/{demo_id}/graph-3d")
            assert response.status_code == 200
            data = response.json()
            assert "nodes" in data
            assert "edges" in data


class TestAdminEndpoints:
    def test_admin_users_without_auth_returns_401(self, client):
        response = client.get("/api/admin/users")
        assert response.status_code == 401

    def test_admin_users_with_regular_user_returns_403(self, auth_client):
        with (
            patch("app.api.routes.admin.UserRepository") as MockRepo,
            patch("app.api.routes.admin._is_admin") as mock_is_admin,
        ):
            mock_is_admin.return_value = False
            mock_instance = MagicMock()
            mock_instance.get_by_id = AsyncMock(return_value={"role": "user"})
            MockRepo.return_value = mock_instance

            response = auth_client.get("/api/admin/users")
            assert response.status_code == 403

    def test_admin_users_with_admin_returns_list(self, admin_client):
        with patch("app.api.routes.admin.UserRepository") as MockRepo:
            mock_instance = MagicMock()
            mock_instance.list = AsyncMock(
                return_value=[
                    {
                        "_id": "user1",
                        "username": "testuser",
                        "role": "user",
                        "plan": "free",
                    }
                ]
            )
            MockRepo.return_value = mock_instance

            response = admin_client.get("/api/admin/users")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)

    def test_admin_update_user_without_auth_returns_401(self, client):
        response = client.patch("/api/admin/users/some_user_id", json={"role": "admin"})
        assert response.status_code == 401


class TestEvaluateWithAuth:
    def test_evaluate_creates_evaluation(self, auth_client, mock_user):
        with (
            patch("app.api.routes.evaluate.APIKeyRepository") as MockAPIKey,
            patch("app.api.routes.evaluate.check_quota") as mock_quota,
            patch("app.api.routes.evaluate.start_evaluation") as mock_start,
            patch("app.api.routes.evaluate.get_event_channel") as mock_channel,
            patch("app.api.routes.evaluate.register_task") as mock_register,
        ):
            mock_api_key = MagicMock()
            mock_api_key.get_status = AsyncMock(return_value=[])
            MockAPIKey.return_value = mock_api_key

            from app.services.quota import QuotaResult

            mock_quota.return_value = QuotaResult(
                allowed=True,
                reason="OK",
                remaining=5,
                daily_limit=10,
                used_today=5,
            )

            mock_start.return_value = "test_eval_123"

            mock_event = MagicMock()
            mock_event.create_channel = AsyncMock()
            mock_event.close_channel = AsyncMock()
            mock_channel.return_value = mock_event

            mock_register.return_value = None

            response = auth_client.post(
                "/api/evaluate",
                json={
                    "repo_url": "https://github.com/test/repo",
                    "criteria": "basic",
                    "evaluation_mode": "six_sommeliers",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["evaluation_id"] == "test_eval_123"
            assert data["status"] == "pending"

    def test_evaluate_quota_exceeded_returns_error(self, auth_client):
        with (
            patch("app.api.routes.evaluate.APIKeyRepository") as MockAPIKey,
            patch("app.api.routes.evaluate.check_quota") as mock_quota,
        ):
            mock_api_key = MagicMock()
            mock_api_key.get_status = AsyncMock(return_value=[])
            MockAPIKey.return_value = mock_api_key

            from app.services.quota import QuotaResult

            mock_quota.return_value = QuotaResult(
                allowed=False,
                reason="Daily limit exceeded",
                remaining=0,
                daily_limit=5,
                used_today=5,
                suggestion="Upgrade to premium",
            )

            response = auth_client.post(
                "/api/evaluate",
                json={
                    "repo_url": "https://github.com/test/repo",
                    "criteria": "basic",
                },
            )

            assert response.status_code == 400


class TestRepositoriesWithAuth:
    def test_repositories_returns_cached_data(self, auth_client, mock_repository_data):
        cached_repos = [
            {
                **repo,
                "user_id": "507f1f77bcf86cd799439011",
                "cached_at": "2025-01-01T00:00:00Z",
            }
            for repo in mock_repository_data
        ]

        with patch(
            "app.api.routes.repositories.RepositoryCacheRepository"
        ) as MockCache:
            mock_cache = MagicMock()
            mock_cache.get_user_repos = AsyncMock(return_value=cached_repos)
            MockCache.return_value = mock_cache

            response = auth_client.get("/repositories")
            assert response.status_code == 200
            data = response.json()
            assert data["total"] == 2
            assert len(data["repositories"]) == 2

    def test_repositories_refresh_clears_cache(self, auth_client, mock_repository_data):
        with (
            patch("app.api.routes.repositories.RepositoryCacheRepository") as MockCache,
            patch("app.api.routes.repositories.GitHubService") as MockGH,
        ):
            mock_cache = MagicMock()
            mock_cache.clear_user_repos = AsyncMock(return_value=True)
            mock_cache.set_user_repos = AsyncMock(return_value=True)
            MockCache.return_value = mock_cache

            mock_gh = MagicMock()
            mock_gh.list_user_repositories = AsyncMock(
                return_value=mock_repository_data
            )
            MockGH.return_value = mock_gh

            response = auth_client.post("/repositories/refresh")
            assert response.status_code == 200
            mock_cache.clear_user_repos.assert_called_once()


class TestHistoryWithAuth:
    def test_history_returns_paginated_results(self, auth_client, mock_evaluation_data):
        with patch("app.api.routes.history.get_user_history") as mock_history:
            mock_history.return_value = [
                {
                    "id": mock_evaluation_data["evaluation_id"],
                    "repo_context": mock_evaluation_data["repo_context"],
                    "criteria": mock_evaluation_data["criteria"],
                    "status": mock_evaluation_data["status"],
                    "created_at": mock_evaluation_data["created_at"],
                    "score": 85,
                    "rating_tier": "Premier Cru",
                }
            ]

            response = auth_client.get("/api/history?skip=0&limit=10")
            assert response.status_code == 200
            data = response.json()
            assert "items" in data
            assert len(data["items"]) == 1
            assert data["skip"] == 0
            assert data["limit"] == 10
