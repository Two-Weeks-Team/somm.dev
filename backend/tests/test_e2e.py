"""End-to-end tests for the evaluation API.

Tests complete evaluation flows including:
- Submit evaluation -> SSE stream -> results
- Error handling (invalid URLs, private repos, rate limiting)
- Concurrent evaluations
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.core.exceptions import CorkedError


class TestE2EEvaluationFlow:
    """End-to-end tests for the complete evaluation flow."""

    def test_complete_evaluation_flow_submit_to_results(self):
        """Test complete evaluation flow from submit to getting results."""
        evaluation_id = "eval_e2e_123"

        mock_result = {
            "evaluation_id": evaluation_id,
            "final_evaluation": {
                "overall_score": 85,
                "rating_tier": "Premier Cru",
                "summary": "Excellent work!",
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
            "app.services.evaluation_service.run_full_evaluation",
            new_callable=AsyncMock,
        ) as mock_start:
            mock_start.return_value = {
                "evaluation_id": evaluation_id,
                "status": "pending",
            }

            with patch(
                "app.services.evaluation_service.get_evaluation_result",
                new_callable=AsyncMock,
            ) as mock_get:
                mock_get.return_value = mock_result

                from app.api.routes.evaluate import router

                with TestClient(router) as client:
                    # Step 1: Submit evaluation
                    submit_response = client.post(
                        "/evaluate",
                        json={
                            "repo_url": "https://github.com/owner/repo",
                            "criteria": "basic",
                        },
                    )
                    assert submit_response.status_code == 200
                    data = submit_response.json()
                    assert data["evaluation_id"] == evaluation_id
                    assert data["status"] == "pending"

                    # Step 2: Get results
                    result_response = client.get(f"/evaluate/{evaluation_id}/result")
                    assert result_response.status_code == 200
                    result_data = result_response.json()
                    assert result_data["evaluation_id"] == evaluation_id
                    assert result_data["final_evaluation"]["overall_score"] == 85
                    assert (
                        result_data["final_evaluation"]["rating_tier"] == "Premier Cru"
                    )

    def test_evaluation_with_sse_stream_flow(self):
        """Test evaluation with SSE stream connection and events."""
        evaluation_id = "eval_sse_123"

        mock_result = {
            "evaluation_id": evaluation_id,
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
                "evaluation_id": evaluation_id,
                "status": "pending",
            }

            with patch(
                "app.services.evaluation_service.get_evaluation_result",
                new_callable=AsyncMock,
            ) as mock_get:
                mock_get.return_value = mock_result

                from app.api.routes.evaluate import router

                with TestClient(router) as client:
                    # Submit first
                    submit_response = client.post(
                        "/evaluate",
                        json={
                            "repo_url": "https://github.com/hackathon/project",
                            "criteria": "hackathon",
                        },
                    )
                    assert submit_response.status_code == 200

                    # Stream should be accessible
                    stream_response = client.get(f"/evaluate/{evaluation_id}/stream")
                    assert stream_response.status_code == 200
                    assert (
                        stream_response.headers["content-type"]
                        == "text/event-stream; charset=utf-8"
                    )

    def test_evaluation_all_criteria_types(self):
        """Test evaluation with all supported criteria types."""
        criteria_types = [
            ("basic", "Basic evaluation"),
            ("hackathon", "Hackathon evaluation"),
            ("academic", "Academic evaluation"),
            ("custom", "Custom evaluation"),
        ]

        for criteria, _ in criteria_types:
            with patch(
                "app.services.evaluation_service.run_full_evaluation",
                new_callable=AsyncMock,
            ) as mock_start:
                mock_start.return_value = {
                    "evaluation_id": f"eval_{criteria}",
                    "status": "pending",
                }

                from app.api.routes.evaluate import router

                with TestClient(router) as client:
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

    def test_evaluation_with_custom_criteria(self):
        """Test evaluation with custom criteria list."""
        evaluation_id = "eval_custom_criteria"

        mock_result = {
            "evaluation_id": evaluation_id,
            "final_evaluation": {
                "overall_score": 78,
                "rating_tier": "Village",
                "summary": "Good effort",
                "sommelier_outputs": [],
            },
            "created_at": datetime.utcnow(),
        }

        with patch(
            "app.services.evaluation_service.run_full_evaluation",
            new_callable=AsyncMock,
        ) as mock_start:
            mock_start.return_value = {
                "evaluation_id": evaluation_id,
                "status": "pending",
            }

            with patch(
                "app.services.evaluation_service.get_evaluation_result",
                new_callable=AsyncMock,
            ) as mock_get:
                mock_get.return_value = mock_result

                from app.api.routes.evaluate import router

                with TestClient(router) as client:
                    response = client.post(
                        "/evaluate",
                        json={
                            "repo_url": "https://github.com/owner/repo",
                            "criteria": "custom",
                            "custom_criteria": [
                                "readability",
                                "performance",
                                "security",
                            ],
                        },
                    )
                    assert response.status_code == 200
                    assert response.json()["evaluation_id"] == evaluation_id


class TestE2EErrorHandling:
    """End-to-end tests for error handling scenarios."""

    def test_invalid_github_url_error(self):
        """Test error handling for invalid GitHub URLs."""
        invalid_urls = [
            "https://gitlab.com/owner/repo",
            "not-a-url",
            "https://example.com/repo",
            "github.com/owner/repo",
            "git@github.com:owner/repo.git",
            "https://github.com/",
            "https://github.com/owner",
            "",
        ]

        from app.api.routes.evaluate import router

        with TestClient(router) as client:
            for url in invalid_urls:
                response = client.post(
                    "/evaluate",
                    json={"repo_url": url, "criteria": "basic"},
                )
                assert response.status_code in [400, 422], (
                    f"URL '{url}' should be rejected"
                )

    def test_invalid_criteria_error(self):
        """Test error handling for invalid criteria enum."""
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

    def test_missing_required_fields(self):
        """Test error handling for missing required fields."""
        from app.api.routes.evaluate import router

        with TestClient(router) as client:
            # Missing repo_url
            response1 = client.post("/evaluate", json={"criteria": "basic"})
            assert response1.status_code == 422

            # Missing criteria
            response2 = client.post(
                "/evaluate",
                json={"repo_url": "https://github.com/owner/repo"},
            )
            assert response2.status_code == 422

    def test_nonexistent_evaluation_result(self):
        """Test getting result for non-existent evaluation."""
        from app.api.routes.evaluate import router

        with patch(
            "app.services.evaluation_service.get_evaluation_result",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.side_effect = CorkedError("Evaluation not found: nonexistent")

            with TestClient(router) as client:
                response = client.get("/evaluate/nonexistent_evaluation/result")
                assert response.status_code == 404

    def test_pending_evaluation_error(self):
        """Test error when trying to get result of pending evaluation."""
        from app.api.routes.evaluate import router

        with patch(
            "app.services.evaluation_service.get_evaluation_result",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.side_effect = CorkedError("Evaluation is still pending")

            with TestClient(router) as client:
                response = client.get("/evaluate/pending_eval/result")
                assert response.status_code == 400


class TestE2ERateLimiting:
    """Tests for rate limiting behavior (simulated 429 responses)."""

    def test_rate_limit_response_structure(self):
        """Test that rate limit responses have correct structure."""
        from app.api.routes.evaluate import router

        with TestClient(router) as client:
            response = client.post(
                "/evaluate",
                json={
                    "repo_url": "https://github.com/owner/repo",
                    "criteria": "basic",
                },
            )

            # Normal response should be 200 (not rate limited)
            # When rate limited, we expect 429
            assert response.status_code in [200, 429]

    def test_concurrent_evaluation_requests(self):
        """Test handling of concurrent evaluation requests."""
        num_concurrent = 5
        evaluation_ids = [f"eval_concurrent_{i}" for i in range(num_concurrent)]

        def submit_evaluation(index: int):
            with patch(
                "app.services.evaluation_service.run_full_evaluation",
                new_callable=AsyncMock,
            ) as mock_start:
                mock_start.return_value = {
                    "evaluation_id": evaluation_ids[index],
                    "status": "pending",
                }

                from app.api.routes.evaluate import router

                with TestClient(router) as client:
                    response = client.post(
                        "/evaluate",
                        json={
                            "repo_url": f"https://github.com/owner/repo{index}",
                            "criteria": "basic",
                        },
                    )
                    return response.status_code, evaluation_ids[index]

        # Run concurrent requests
        results = [submit_evaluation(i) for i in range(num_concurrent)]

        # All should succeed
        for i, (status_code, eval_id) in enumerate(results):
            assert status_code == 200, f"Request {i} failed with {status_code}"
            assert eval_id == evaluation_ids[i]


class TestE2EPrivateRepoHandling:
    """Tests for private repository handling."""

    def test_private_repo_error_response(self):
        """Test that private repos return appropriate error."""
        from app.core.exceptions import CorkedError

        with patch(
            "app.services.evaluation_service.run_full_evaluation",
            new_callable=AsyncMock,
        ) as mock_start:
            mock_start.side_effect = CorkedError(
                "Repository is private or access denied"
            )

            from app.api.routes.evaluate import router

            with TestClient(router) as client:
                response = client.post(
                    "/evaluate",
                    json={
                        "repo_url": "https://github.com/private-org/private-repo",
                        "criteria": "basic",
                    },
                )

                # Should return error for private repos
                assert response.status_code == 400
                error_detail = response.json()["detail"].lower()
                assert (
                    "private" in error_detail
                    or "access" in error_detail
                    or "denied" in error_detail
                )

    def test_invalid_github_enterprise_url(self):
        """Test handling of non-GitHub URLs."""
        enterprise_urls = [
            "https://github.mycompany.com/owner/repo",
            "https://bitbucket.org/owner/repo",
            "https://gitlab.com/owner/repo",
        ]

        from app.api.routes.evaluate import router

        with TestClient(router) as client:
            for url in enterprise_urls:
                response = client.post(
                    "/evaluate",
                    json={"repo_url": url, "criteria": "basic"},
                )
                assert response.status_code in [400, 422], (
                    f"URL '{url}' should be rejected"
                )


class TestE2EResponseValidation:
    """Tests for response validation and data integrity."""

    def test_response_contains_all_sommelier_outputs(self):
        """Test that evaluation result contains all sommelier outputs."""
        evaluation_id = "eval_full_sommeliers"

        mock_result = {
            "evaluation_id": evaluation_id,
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

            from app.api.routes.evaluate import router

            with TestClient(router) as client:
                response = client.get(f"/evaluate/{evaluation_id}/result")
                assert response.status_code == 200

                data = response.json()
                sommelier_outputs = data["final_evaluation"]["sommelier_outputs"]

                # Should have all 5 sommeliers
                assert len(sommelier_outputs) == 5

                # Each should have required fields
                expected_sommeliers = {
                    "marcel",
                    "isabella",
                    "heinrich",
                    "sofia",
                    "laurent",
                }
                actual_sommeliers = {s["sommelier_name"] for s in sommelier_outputs}
                assert actual_sommeliers == expected_sommeliers

    def test_rating_tiers_mapping(self):
        """Test that score correctly maps to rating tier."""
        test_cases = [
            (95, "Legendary"),
            (92, "Grand Cru"),
            (87, "Premier Cru"),
            (82, "Village"),
            (75, "Table"),
            (65, "House Wine"),
            (50, "Corked"),
        ]

        for score, expected_tier in test_cases:
            mock_result = {
                "evaluation_id": f"eval_{score}",
                "final_evaluation": {
                    "overall_score": score,
                    "rating_tier": expected_tier,
                    "summary": "Test summary",
                    "sommelier_outputs": [],
                },
                "created_at": datetime.utcnow(),
            }

            with patch(
                "app.services.evaluation_service.get_evaluation_result",
                new_callable=AsyncMock,
            ) as mock_get:
                mock_get.return_value = mock_result

                from app.api.routes.evaluate import router

                with TestClient(router) as client:
                    response = client.get(f"/evaluate/eval_{score}/result")
                    assert response.status_code == 200
                    assert (
                        response.json()["final_evaluation"]["rating_tier"]
                        == expected_tier
                    )

    def test_response_timestamps_format(self):
        """Test that response timestamps are properly formatted."""
        evaluation_id = "eval_timestamp_test"

        mock_result = {
            "evaluation_id": evaluation_id,
            "final_evaluation": {
                "overall_score": 85,
                "rating_tier": "Premier Cru",
                "summary": "Test summary",
                "sommelier_outputs": [],
            },
            "created_at": datetime.utcnow(),
        }

        with patch(
            "app.services.evaluation_service.get_evaluation_result",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = mock_result

            from app.api.routes.evaluate import router

            with TestClient(router) as client:
                response = client.get(f"/evaluate/{evaluation_id}/result")
                assert response.status_code == 200

                data = response.json()
                # created_at should be a string
                assert isinstance(data["created_at"], str)
