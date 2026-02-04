"""Tests for history API routes."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


class TestGETHistory:
    """Test cases for GET /history endpoint."""

    def test_get_history_success(self):
        """Test getting evaluation history successfully."""
        from app.api.routes.history import router

        mock_evaluations = [
            {
                "_id": "eval_1",
                "repo_context": {"repo_url": "https://github.com/owner/repo1"},
                "criteria": "basic",
                "status": "completed",
                "created_at": datetime.utcnow(),
            },
            {
                "_id": "eval_2",
                "repo_context": {"repo_url": "https://github.com/owner/repo2"},
                "criteria": "hackathon",
                "status": "completed",
                "created_at": datetime.utcnow(),
            },
        ]

        with patch(
            "app.services.evaluation_service.get_user_history", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_evaluations

            with TestClient(router) as client:
                response = client.get("/history")

                assert response.status_code == 200
                data = response.json()
                assert len(data["items"]) == 2
                assert data["items"][0]["id"] == "eval_1"
                assert data["items"][1]["id"] == "eval_2"

    def test_get_history_with_pagination(self):
        """Test getting history with pagination parameters."""
        from app.api.routes.history import router

        mock_evaluations = [
            {
                "_id": "eval_page1",
                "repo_context": {"repo_url": "https://github.com/owner/repo1"},
                "criteria": "basic",
                "status": "completed",
                "created_at": datetime.utcnow(),
            },
        ]

        with patch(
            "app.services.evaluation_service.get_user_history", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_evaluations

            with TestClient(router) as client:
                response = client.get("/history?skip=10&limit=5")

                assert response.status_code == 200
                mock_get.assert_called_once_with(skip=10, limit=5)

    def test_get_history_default_pagination(self):
        """Test that default pagination values are applied."""
        from app.api.routes.history import router

        mock_evaluations = []

        with patch(
            "app.services.evaluation_service.get_user_history", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_evaluations

            with TestClient(router) as client:
                response = client.get("/history")

                assert response.status_code == 200
                mock_get.assert_called_once_with(skip=0, limit=50)

    def test_get_history_empty_list(self):
        """Test getting history when user has no evaluations."""
        from app.api.routes.history import router

        with patch(
            "app.services.evaluation_service.get_user_history", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = []

            with TestClient(router) as client:
                response = client.get("/history")

                assert response.status_code == 200
                assert response.json()["items"] == []

    def test_get_history_with_skip_only(self):
        """Test getting history with only skip parameter."""
        from app.api.routes.history import router

        mock_evaluations = []

        with patch(
            "app.services.evaluation_service.get_user_history", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_evaluations

            with TestClient(router) as client:
                response = client.get("/history?skip=20")

                assert response.status_code == 200
                mock_get.assert_called_once_with(skip=20, limit=50)

    def test_get_history_with_limit_only(self):
        """Test getting history with only limit parameter."""
        from app.api.routes.history import router

        mock_evaluations = []

        with patch(
            "app.services.evaluation_service.get_user_history", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_evaluations

            with TestClient(router) as client:
                response = client.get("/history?limit=10")

                assert response.status_code == 200
                mock_get.assert_called_once_with(skip=0, limit=10)

    def test_get_history_limit_max_value(self):
        """Test that limit is capped at maximum value."""
        from app.api.routes.history import router

        mock_evaluations = []

        with patch(
            "app.services.evaluation_service.get_user_history", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_evaluations

            with TestClient(router) as client:
                response = client.get("/history?limit=1000")

                assert response.status_code == 200
                mock_get.assert_called_once_with(skip=0, limit=1000)


class TestHistoryResponseFormat:
    """Test cases for history response format."""

    def test_history_response_contains_expected_fields(self):
        """Test that history response contains all expected fields."""
        from app.api.routes.history import router

        mock_evaluations = [
            {
                "_id": "eval_test",
                "repo_context": {
                    "repo_url": "https://github.com/test/repo",
                    "branch": "main",
                },
                "criteria": "basic",
                "status": "completed",
                "created_at": datetime.utcnow(),
            },
        ]

        with patch(
            "app.services.evaluation_service.get_user_history", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_evaluations

            with TestClient(router) as client:
                response = client.get("/history")

                assert response.status_code == 200
                data = response.json()
                assert "items" in data
                item = data["items"][0]
                assert "id" in item
                assert "repo_context" in item
                assert "criteria" in item
                assert "status" in item
                assert "created_at" in item

    def test_history_response_contains_result_summary(self):
        """Test that completed evaluations include result summary."""
        from app.api.routes.history import router

        mock_evaluations = [
            {
                "_id": "eval_with_result",
                "repo_context": {"repo_url": "https://github.com/owner/repo"},
                "criteria": "basic",
                "status": "completed",
                "score": 85,
                "rating_tier": "Premier Cru",
                "created_at": datetime.utcnow(),
            },
        ]

        with patch(
            "app.services.evaluation_service.get_user_history", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_evaluations

            with TestClient(router) as client:
                response = client.get("/history")

                assert response.status_code == 200
                data = response.json()
                item = data["items"][0]
                assert item["score"] == 85
                assert item["rating_tier"] == "Premier Cru"


class TestHistoryEndpointValidation:
    """Validation tests for history endpoint."""

    def test_history_validates_skip_parameter(self):
        """Test that skip parameter is validated."""
        from app.api.routes.history import router

        with TestClient(router) as client:
            response = client.get("/history?skip=-1")
            assert response.status_code == 422

    def test_history_validates_limit_parameter(self):
        """Test that limit parameter is validated."""
        from app.api.routes.history import router

        with TestClient(router) as client:
            response = client.get("/history?limit=0")
            assert response.status_code == 422

    def test_history_validates_limit_type(self):
        """Test that limit parameter type is validated."""
        from app.api.routes.history import router

        with TestClient(router) as client:
            response = client.get("/history?limit=abc")
            assert response.status_code == 422


class TestHistoryEndpointIntegration:
    """Integration tests for history endpoint."""

    def test_history_sorted_by_created_at_descending(self):
        """Test that history is sorted by created_at in descending order."""
        from app.api.routes.history import router

        now = datetime.utcnow()
        mock_evaluations = [
            {
                "_id": "eval_recent",
                "repo_context": {"repo_url": "https://github.com/owner/repo1"},
                "criteria": "basic",
                "status": "completed",
                "created_at": now,
            },
            {
                "_id": "eval_older",
                "repo_context": {"repo_url": "https://github.com/owner/repo2"},
                "criteria": "basic",
                "status": "completed",
                "created_at": now.replace(day=now.day - 1),
            },
        ]

        with patch(
            "app.services.evaluation_service.get_user_history", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_evaluations

            with TestClient(router) as client:
                response = client.get("/history")

                assert response.status_code == 200
                data = response.json()
                assert data["items"][0]["id"] == "eval_recent"
                assert data["items"][1]["id"] == "eval_older"

    def test_history_mixed_statuses(self):
        """Test history with mixed evaluation statuses."""
        from app.api.routes.history import router

        mock_evaluations = [
            {
                "_id": "eval_completed",
                "repo_context": {"repo_url": "https://github.com/owner/repo1"},
                "criteria": "basic",
                "status": "completed",
                "created_at": datetime.utcnow(),
            },
            {
                "_id": "eval_running",
                "repo_context": {"repo_url": "https://github.com/owner/repo2"},
                "criteria": "hackathon",
                "status": "running",
                "created_at": datetime.utcnow(),
            },
            {
                "_id": "eval_failed",
                "repo_context": {"repo_url": "https://github.com/owner/repo3"},
                "criteria": "academic",
                "status": "failed",
                "created_at": datetime.utcnow(),
            },
        ]

        with patch(
            "app.services.evaluation_service.get_user_history", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_evaluations

            with TestClient(router) as client:
                response = client.get("/history")

                assert response.status_code == 200
                data = response.json()
                assert len(data["items"]) == 3
                assert data["items"][0]["status"] == "completed"
                assert data["items"][1]["status"] == "running"
                assert data["items"][2]["status"] == "failed"

    def test_history_with_different_criteria_types(self):
        """Test history with all different criteria types."""
        from app.api.routes.history import router

        mock_evaluations = [
            {
                "_id": "eval_basic",
                "repo_context": {"repo_url": "https://github.com/owner/repo1"},
                "criteria": "basic",
                "status": "completed",
                "created_at": datetime.utcnow(),
            },
            {
                "_id": "eval_hackathon",
                "repo_context": {"repo_url": "https://github.com/owner/repo2"},
                "criteria": "hackathon",
                "status": "completed",
                "created_at": datetime.utcnow(),
            },
            {
                "_id": "eval_academic",
                "repo_context": {"repo_url": "https://github.com/owner/repo3"},
                "criteria": "academic",
                "status": "completed",
                "created_at": datetime.utcnow(),
            },
            {
                "_id": "eval_custom",
                "repo_context": {"repo_url": "https://github.com/owner/repo4"},
                "criteria": "custom",
                "status": "completed",
                "created_at": datetime.utcnow(),
            },
        ]

        with patch(
            "app.services.evaluation_service.get_user_history", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_evaluations

            with TestClient(router) as client:
                response = client.get("/history")

                assert response.status_code == 200
                data = response.json()
                criteria_types = [e["criteria"] for e in data["items"]]
                assert "basic" in criteria_types
                assert "hackathon" in criteria_types
                assert "academic" in criteria_types
                assert "custom" in criteria_types

    def test_history_large_dataset(self):
        """Test history with large dataset."""
        from app.api.routes.history import router

        mock_evaluations = [
            {
                "_id": f"eval_{i}",
                "repo_context": {"repo_url": f"https://github.com/owner/repo{i}"},
                "criteria": "basic",
                "status": "completed",
                "created_at": datetime.utcnow(),
            }
            for i in range(50)
        ]

        with patch(
            "app.services.evaluation_service.get_user_history", new_callable=AsyncMock
        ) as mock_get:
            mock_get.return_value = mock_evaluations

            with TestClient(router) as client:
                response = client.get("/history?limit=50")

                assert response.status_code == 200
                data = response.json()
                assert len(data["items"]) == 50
