"""Tests for evaluate API routes."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.core.exceptions import CorkedError, EmptyCellarError


class TestPOSTEvaluate:
    """Test cases for POST /api/evaluate endpoint."""

    def test_post_evaluate_success(self):
        """Test successful evaluation request."""
        from app.api.routes.evaluate import router

        with patch(
            "app.services.evaluation_service.run_full_evaluation",
            new_callable=AsyncMock,
        ) as mock_start:
            mock_start.return_value = {
                "evaluation_id": "eval_123456",
                "status": "pending",
            }

            with TestClient(router) as client:
                response = client.post(
                    "/evaluate",
                    json={
                        "repo_url": "https://github.com/owner/repo",
                        "criteria": "basic",
                    },
                )

                assert response.status_code == 200
                data = response.json()
                assert data["evaluation_id"] == "eval_123456"
                assert data["status"] == "pending"

    def test_post_evaluate_with_custom_criteria(self):
        """Test evaluation with custom criteria."""
        from app.api.routes.evaluate import router

        with patch(
            "app.services.evaluation_service.run_full_evaluation",
            new_callable=AsyncMock,
        ) as mock_start:
            mock_start.return_value = {
                "evaluation_id": "eval_custom",
                "status": "pending",
            }

            with TestClient(router) as client:
                response = client.post(
                    "/evaluate",
                    json={
                        "repo_url": "https://github.com/owner/repo",
                        "criteria": "custom",
                        "custom_criteria": ["readability", "performance", "security"],
                    },
                )

                assert response.status_code == 200
                assert response.json()["evaluation_id"] == "eval_custom"

    def test_post_evaluate_invalid_url(self):
        """Test evaluation with invalid GitHub URL."""
        from app.api.routes.evaluate import router

        with TestClient(router) as client:
            response = client.post(
                "/evaluate",
                json={
                    "repo_url": "https://gitlab.com/owner/repo",
                    "criteria": "basic",
                },
            )

            assert response.status_code == 400
            assert "corked" in response.json()["detail"].lower()

    def test_post_evaluate_invalid_criteria(self):
        """Test evaluation with invalid criteria enum."""
        from app.api.routes.evaluate import router

        with TestClient(router) as client:
            response = client.post(
                "/evaluate",
                json={
                    "repo_url": "https://github.com/owner/repo",
                    "criteria": "invalid_mode",
                },
            )

            assert response.status_code == 422

    def test_post_evaluate_missing_repo_url(self):
        """Test evaluation without repo_url."""
        from app.api.routes.evaluate import router

        with TestClient(router) as client:
            response = client.post(
                "/evaluate",
                json={"criteria": "basic"},
            )

            assert response.status_code == 422

    def test_post_evaluate_missing_criteria(self):
        """Test evaluation without criteria."""
        from app.api.routes.evaluate import router

        with TestClient(router) as client:
            response = client.post(
                "/evaluate",
                json={"repo_url": "https://github.com/owner/repo"},
            )

            assert response.status_code == 422

    def test_post_evaluate_hackathon_criteria(self):
        """Test evaluation with hackathon criteria."""
        from app.api.routes.evaluate import router

        with patch(
            "app.services.evaluation_service.run_full_evaluation",
            new_callable=AsyncMock,
        ) as mock_start:
            mock_start.return_value = {
                "evaluation_id": "eval_hackathon",
                "status": "pending",
            }

            with TestClient(router) as client:
                response = client.post(
                    "/evaluate",
                    json={
                        "repo_url": "https://github.com/hackathon/project",
                        "criteria": "hackathon",
                    },
                )

                assert response.status_code == 200
                assert response.json()["evaluation_id"] == "eval_hackathon"

    def test_post_evaluate_academic_criteria(self):
        """Test evaluation with academic criteria."""
        from app.api.routes.evaluate import router

        with patch(
            "app.services.evaluation_service.run_full_evaluation",
            new_callable=AsyncMock,
        ) as mock_start:
            mock_start.return_value = {
                "evaluation_id": "eval_academic",
                "status": "pending",
            }

            with TestClient(router) as client:
                response = client.post(
                    "/evaluate",
                    json={
                        "repo_url": "https://github.com/research/project",
                        "criteria": "academic",
                    },
                )

                assert response.status_code == 200
                assert response.json()["evaluation_id"] == "eval_academic"


class TestGETEvaluateStream:
    """Test cases for GET /{id}/stream endpoint."""

    def test_get_evaluate_stream_success(self):
        """Test successful SSE stream connection."""
        from app.api.routes.evaluate import router

        with patch("app.api.routes.evaluate.SSEManager") as mock_sse_class:
            mock_sse = MagicMock()
            mock_sse.subscribe = MagicMock()
            mock_sse_class.return_value = mock_sse

            with TestClient(router) as client:
                response = client.get("/evaluate/eval_123/stream")

                assert response.status_code == 200
                assert (
                    response.headers["content-type"]
                    == "text/event-stream; charset=utf-8"
                )


class TestGETEvaluateResult:
    """Test cases for GET /{id}/result endpoint."""

    def test_get_evaluate_result_success(self):
        """Test getting evaluation result successfully."""
        from app.api.routes.evaluate import router
        from datetime import datetime

        mock_result = {
            "evaluation_id": "eval_123",
            "final_evaluation": {
                "overall_score": 85,
                "rating_tier": "Premier Cru",
                "summary": "Excellent work!",
                "sommelier_outputs": [],
            },
            "created_at": datetime.utcnow(),
        }

        with patch(
            "app.services.evaluation_service.get_evaluation_result",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_result

            with TestClient(router) as client:
                response = client.get("/evaluate/eval_123/result")

                assert response.status_code == 200
                data = response.json()
                assert data["evaluation_id"] == "eval_123"
                assert data["final_evaluation"]["overall_score"] == 85

    def test_get_evaluate_result_not_found(self):
        """Test getting result for non-existent evaluation."""
        from app.api.routes.evaluate import router

        with patch(
            "app.services.evaluation_service.get_evaluation_result",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = None

            with TestClient(router) as client:
                response = client.get("/evaluate/nonexistent/result")

                assert response.status_code == 404

    def test_get_evaluate_result_pending(self):
        """Test getting result for pending evaluation returns error."""
        from app.api.routes.evaluate import router

        with patch(
            "app.services.evaluation_service.get_evaluation_result",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.side_effect = CorkedError("Evaluation is still pending")

            with TestClient(router) as client:
                response = client.get("/evaluate/eval_pending/result")

                assert response.status_code == 400

    def test_get_evaluate_result_contains_all_sommeliers(self):
        """Test that result contains all sommelier outputs."""
        from app.api.routes.evaluate import router
        from datetime import datetime

        mock_result = {
            "evaluation_id": "eval_full",
            "final_evaluation": {
                "overall_score": 88,
                "rating_tier": "Premier Cru",
                "summary": "Outstanding",
                "sommelier_outputs": [
                    {
                        "sommelier_name": "marcel",
                        "score": 85,
                        "summary": "Good structure",
                    },
                    {
                        "sommelier_name": "isabella",
                        "score": 90,
                        "summary": "Clean code",
                    },
                    {
                        "sommelier_name": "heinrich",
                        "score": 87,
                        "summary": "Well tested",
                    },
                    {
                        "sommelier_name": "sofia",
                        "score": 85,
                        "summary": "Good innovation",
                    },
                    {
                        "sommelier_name": "laurent",
                        "score": 88,
                        "summary": "Solid implementation",
                    },
                ],
            },
            "created_at": datetime.utcnow(),
        }

        with patch(
            "app.services.evaluation_service.get_evaluation_result",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_result

            with TestClient(router) as client:
                response = client.get("/evaluate/eval_full/result")

                assert response.status_code == 200
                sommeliers = response.json()["final_evaluation"]["sommelier_outputs"]
                assert len(sommeliers) == 5


class TestEvaluateEndpointValidation:
    """Validation tests for evaluate endpoints."""

    def test_post_evaluate_validates_github_url_format(self):
        """Test that GitHub URL format is validated."""
        from app.api.routes.evaluate import router

        invalid_urls = [
            "not-a-url",
            "https://example.com/repo",
            "github.com/owner/repo",
            "git@github.com:owner/repo.git",
        ]

        with TestClient(router) as client:
            for url in invalid_urls:
                response = client.post(
                    "/evaluate",
                    json={"repo_url": url, "criteria": "basic"},
                )
                assert response.status_code in [400, 422], (
                    f"URL {url} should be rejected"
                )

    def test_post_evaluate_validates_criteria_enum(self):
        """Test that criteria enum is validated."""
        from app.api.routes.evaluate import router

        invalid_criteria = ["basic_mode", "default", "strict", "loose"]

        with TestClient(router) as client:
            for criteria in invalid_criteria:
                response = client.post(
                    "/evaluate",
                    json={
                        "repo_url": "https://github.com/owner/repo",
                        "criteria": criteria,
                    },
                )
                assert response.status_code == 422, (
                    f"Criteria {criteria} should be rejected"
                )


class TestEvaluateEndpointIntegration:
    """Integration tests for evaluate endpoints."""

    def test_full_evaluation_workflow(self):
        """Test complete evaluation workflow from start to result."""
        from app.api.routes.evaluate import router
        from datetime import datetime

        mock_evaluation_id = "eval_workflow_123"
        mock_result = {
            "evaluation_id": mock_evaluation_id,
            "final_evaluation": {
                "overall_score": 92,
                "rating_tier": "Grand Cru",
                "summary": "Outstanding project!",
                "sommelier_outputs": [],
            },
            "created_at": datetime.utcnow(),
        }

        with patch(
            "app.services.evaluation_service.run_full_evaluation",
            new_callable=AsyncMock,
        ) as mock_start:
            mock_start.return_value = {
                "evaluation_id": mock_evaluation_id,
                "status": "pending",
            }

            with patch(
                "app.services.evaluation_service.get_evaluation_result",
                new_callable=AsyncMock,
            ) as mock_get:
                mock_get.return_value = mock_result

                with TestClient(router) as client:
                    start_response = client.post(
                        "/evaluate",
                        json={
                            "repo_url": "https://github.com/owner/repo",
                            "criteria": "basic",
                        },
                    )
                    assert start_response.status_code == 200
                    assert start_response.json()["evaluation_id"] == mock_evaluation_id

                    result_response = client.get(
                        f"/evaluate/{mock_evaluation_id}/result"
                    )
                    assert result_response.status_code == 200
                    assert (
                        result_response.json()["final_evaluation"]["overall_score"]
                        == 92
                    )

    def test_evaluation_with_all_criteria_types(self):
        """Test evaluations with all supported criteria types."""
        from app.api.routes.evaluate import router

        criteria_types = ["basic", "hackathon", "academic", "custom"]

        with patch(
            "app.services.evaluation_service.run_full_evaluation",
            new_callable=AsyncMock,
        ) as mock_start:
            mock_start.return_value = {
                "evaluation_id": "eval_criteria",
                "status": "pending",
            }

            with TestClient(router) as client:
                for criteria in criteria_types:
                    response = client.post(
                        "/evaluate",
                        json={
                            "repo_url": "https://github.com/owner/repo",
                            "criteria": criteria,
                        },
                    )
                    assert response.status_code == 200, (
                        f"Criteria {criteria} should be accepted"
                    )

    def test_get_evaluate_stream_sends_events(self):
        """Test that stream sends evaluation events."""
        from app.api.routes.evaluate import router
        import asyncio

        received_events = []

        def capture_events():
            with patch("app.api.routes.evaluate.SSEManager") as mock_sse_class:
                mock_queue = asyncio.Queue()

                async def mock_subscribe(eval_id, queue):
                    await queue.put({"type": "status", "data": "started"})
                    await queue.put({"type": "status", "data": "marcel_completed"})
                    await queue.put({"type": "close"})

                mock_sse = MagicMock()
                mock_sse.subscribe = mock_subscribe
                mock_sse_class.return_value = mock_sse

                with TestClient(router) as client:
                    with client.stream(
                        "GET", "/api/evaluate/eval_123/stream"
                    ) as stream:
                        for chunk in stream.iter_content(chunk_size=1024):
                            if chunk:
                                received_events.append(chunk)

        capture_events()

        assert len(received_events) > 0


class TestGETEvaluateResult:
    """Test cases for GET /api/evaluate/{id}/result endpoint."""

    def test_get_evaluate_result_success(self):
        """Test getting evaluation result successfully."""
        from app.api.routes.evaluate import router
        from datetime import datetime

        mock_result = {
            "evaluation_id": "eval_123",
            "final_evaluation": {
                "overall_score": 85,
                "rating_tier": "Premier Cru",
                "summary": "Excellent work!",
                "sommelier_outputs": [],
            },
            "created_at": datetime.utcnow(),
        }

        with patch(
            "app.services.evaluation_service.get_evaluation_result",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_result

            with TestClient(router) as client:
                response = client.get("/api/evaluate/eval_123/result")

                assert response.status_code == 200
                data = response.json()
                assert data["evaluation_id"] == "eval_123"
                assert data["final_evaluation"]["overall_score"] == 85

    def test_get_evaluate_result_not_found(self):
        """Test getting result for non-existent evaluation."""
        from app.api.routes.evaluate import router

        with patch(
            "app.services.evaluation_service.get_evaluation_result",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = None

            with TestClient(router) as client:
                response = client.get("/api/evaluate/nonexistent/result")

                assert response.status_code == 404

    def test_get_evaluate_result_pending(self):
        """Test getting result for pending evaluation returns error."""
        from app.api.routes.evaluate import router

        with patch(
            "app.services.evaluation_service.get_evaluation_result",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.side_effect = CorkedError("Evaluation is still pending")

            with TestClient(router) as client:
                response = client.get("/api/evaluate/eval_pending/result")

                assert response.status_code == 400

    def test_get_evaluate_result_contains_all_sommeliers(self):
        """Test that result contains all sommelier outputs."""
        from app.api.routes.evaluate import router
        from datetime import datetime

        mock_result = {
            "evaluation_id": "eval_full",
            "final_evaluation": {
                "overall_score": 88,
                "rating_tier": "Premier Cru",
                "summary": "Outstanding",
                "sommelier_outputs": [
                    {
                        "sommelier_name": "marcel",
                        "score": 85,
                        "summary": "Good structure",
                    },
                    {
                        "sommelier_name": "isabella",
                        "score": 90,
                        "summary": "Clean code",
                    },
                    {
                        "sommelier_name": "heinrich",
                        "score": 87,
                        "summary": "Well tested",
                    },
                    {
                        "sommelier_name": "sofia",
                        "score": 85,
                        "summary": "Good innovation",
                    },
                    {
                        "sommelier_name": "laurent",
                        "score": 88,
                        "summary": "Solid implementation",
                    },
                ],
            },
            "created_at": datetime.utcnow(),
        }

        with patch(
            "app.services.evaluation_service.get_evaluation_result",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_result

            with TestClient(router) as client:
                response = client.get("/api/evaluate/eval_full/result")

                assert response.status_code == 200
                sommeliers = response.json()["final_evaluation"]["sommelier_outputs"]
                assert len(sommeliers) == 5


class TestEvaluateEndpointValidation:
    """Validation tests for evaluate endpoints."""

    def test_post_evaluate_validates_github_url_format(self):
        """Test that GitHub URL format is validated."""
        from app.api.routes.evaluate import router

        invalid_urls = [
            "not-a-url",
            "https://example.com/repo",
            "github.com/owner/repo",
            "git@github.com:owner/repo.git",
        ]

        with TestClient(router) as client:
            for url in invalid_urls:
                response = client.post(
                    "/api/evaluate",
                    json={"repo_url": url, "criteria": "basic"},
                )
                assert response.status_code in [400, 422], (
                    f"URL {url} should be rejected"
                )

    def test_post_evaluate_validates_criteria_enum(self):
        """Test that criteria enum is validated."""
        from app.api.routes.evaluate import router

        invalid_criteria = ["basic_mode", "default", "strict", "loose"]

        with TestClient(router) as client:
            for criteria in invalid_criteria:
                response = client.post(
                    "/api/evaluate",
                    json={
                        "repo_url": "https://github.com/owner/repo",
                        "criteria": criteria,
                    },
                )
                assert response.status_code == 422, (
                    f"Criteria {criteria} should be rejected"
                )

    def test_get_evaluate_result_validates_evaluation_id(self):
        """Test that evaluation ID format is validated."""
        from app.api.routes.evaluate import router

        with TestClient(router) as client:
            response = client.get("/api/evaluate/invalid-id/result")
            assert response.status_code == 422


class TestEvaluateEndpointIntegration:
    """Integration tests for evaluate endpoints."""

    def test_full_evaluation_workflow(self):
        """Test complete evaluation workflow from start to result."""
        from app.api.routes.evaluate import router
        from datetime import datetime

        mock_evaluation_id = "eval_workflow_123"
        mock_result = {
            "evaluation_id": mock_evaluation_id,
            "final_evaluation": {
                "overall_score": 92,
                "rating_tier": "Grand Cru",
                "summary": "Outstanding project!",
                "sommelier_outputs": [],
            },
            "created_at": datetime.utcnow(),
        }

        with patch(
            "app.services.evaluation_service.run_full_evaluation",
            new_callable=AsyncMock,
        ) as mock_start:
            mock_start.return_value = {
                "evaluation_id": mock_evaluation_id,
                "status": "pending",
            }

            with patch(
                "app.services.evaluation_service.get_evaluation_result",
                new_callable=AsyncMock,
            ) as mock_get:
                mock_get.return_value = mock_result

                with TestClient(router) as client:
                    start_response = client.post(
                        "/api/evaluate",
                        json={
                            "repo_url": "https://github.com/owner/repo",
                            "criteria": "basic",
                        },
                    )
                    assert start_response.status_code == 200
                    assert start_response.json()["evaluation_id"] == mock_evaluation_id

                    result_response = client.get(
                        f"/api/evaluate/{mock_evaluation_id}/result"
                    )
                    assert result_response.status_code == 200
                    assert (
                        result_response.json()["final_evaluation"]["overall_score"]
                        == 92
                    )

    def test_evaluation_with_all_criteria_types(self):
        """Test evaluations with all supported criteria types."""
        from app.api.routes.evaluate import router

        criteria_types = ["basic", "hackathon", "academic", "custom"]

        with patch(
            "app.services.evaluation_service.run_full_evaluation",
            new_callable=AsyncMock,
        ) as mock_start:
            mock_start.return_value = {
                "evaluation_id": "eval_criteria",
                "status": "pending",
            }

            with TestClient(router) as client:
                for criteria in criteria_types:
                    response = client.post(
                        "/api/evaluate",
                        json={
                            "repo_url": "https://github.com/owner/repo",
                            "criteria": criteria,
                        },
                    )
                    assert response.status_code == 200, (
                        f"Criteria {criteria} should be accepted"
                    )
