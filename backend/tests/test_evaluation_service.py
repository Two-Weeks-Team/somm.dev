"""Tests for evaluation service module."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.exceptions import CorkedError, EmptyCellarError


class TestStartEvaluation:
    """Test cases for start_evaluation function."""

    @pytest.mark.asyncio
    async def test_start_evaluation_success(self):
        """Test starting evaluation successfully."""
        from app.services.evaluation_service import start_evaluation

        mock_evaluation_id = "eval_123456"
        mock_graph_result = {
            "repo_url": "https://github.com/owner/repo",
            "jeanpierre_result": {
                "overall_score": 85,
                "rating_tier": "Premier Cru",
                "summary": "Excellent work!",
            },
        }

        with patch(
            "app.services.evaluation_service.EvaluationRepository"
        ) as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.create_evaluation = AsyncMock(return_value=mock_evaluation_id)
            mock_repo_class.return_value = mock_repo

            with patch(
                "app.services.evaluation_service.get_evaluation_graph"
            ) as mock_graph:
                mock_graph.return_value.ainvoke = AsyncMock(
                    return_value=mock_graph_result
                )

                with patch(
                    "app.services.evaluation_service.GitHubService"
                ) as mock_github_class:
                    mock_github = MagicMock()
                    mock_github.get_full_repo_context = AsyncMock(return_value={})
                    mock_github_class.return_value = mock_github

                    result = await start_evaluation(
                        repo_url="https://github.com/owner/repo",
                        criteria="basic",
                        user_id="user_123",
                    )

                    assert result == mock_evaluation_id
                    mock_repo.create_evaluation.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_evaluation_invalid_url(self):
        """Test starting evaluation with invalid URL raises error."""
        from app.services.evaluation_service import start_evaluation

        with pytest.raises(CorkedError):
            await start_evaluation(
                repo_url="https://invalid-url.com/owner/repo",
                criteria="basic",
                user_id="user_123",
            )

    @pytest.mark.asyncio
    async def test_start_evaluation_invalid_criteria(self):
        """Test starting evaluation with invalid criteria raises error."""
        from app.services.evaluation_service import start_evaluation

        with pytest.raises(CorkedError):
            await start_evaluation(
                repo_url="https://github.com/owner/repo",
                criteria="invalid_criteria",
                user_id="user_123",
            )


class TestRunEvaluationPipeline:
    """Test cases for running the evaluation pipeline."""

    @pytest.mark.asyncio
    async def test_run_evaluation_pipeline_success(self):
        """Test running full evaluation pipeline successfully."""
        from app.services.evaluation_service import run_evaluation_pipeline

        mock_graph_result = {
            "repo_url": "https://github.com/owner/repo",
            "marcel_result": {"score": 80, "summary": "Good structure"},
            "isabella_result": {"score": 85, "summary": "Clean code"},
            "heinrich_result": {"score": 90, "summary": "Well tested"},
            "sofia_result": {"score": 75, "summary": "Some innovation"},
            "laurent_result": {"score": 82, "summary": "Good implementation"},
            "jeanpierre_result": {
                "overall_score": 82,
                "rating_tier": "Village",
                "summary": "Solid work",
                "sommelier_outputs": [],
            },
            "completed_sommeliers": [
                "marcel",
                "isabella",
                "heinrich",
                "sofia",
                "laurent",
            ],
        }

        with patch(
            "app.services.evaluation_service.get_evaluation_graph"
        ) as mock_graph:
            mock_graph.return_value.ainvoke = AsyncMock(return_value=mock_graph_result)

            result = await run_evaluation_pipeline(
                repo_url="https://github.com/owner/repo",
                criteria="basic",
            )

            assert "jeanpierre_result" in result
            assert result["jeanpierre_result"]["overall_score"] == 82

    @pytest.mark.asyncio
    async def test_run_evaluation_pipeline_with_sse(self):
        """Test running evaluation pipeline with SSE progress updates."""
        from app.services.evaluation_service import run_evaluation_pipeline

        mock_graph_result = {
            "repo_url": "https://github.com/owner/repo",
            "jeanpierre_result": {
                "overall_score": 90,
                "rating_tier": "Grand Cru",
                "summary": "Excellent",
                "sommelier_outputs": [],
            },
            "completed_sommeliers": [],
        }

        with patch(
            "app.services.evaluation_service.get_evaluation_graph"
        ) as mock_graph:
            mock_graph.return_value.ainvoke = AsyncMock(return_value=mock_graph_result)

            mock_queue = MagicMock()

            result = await run_evaluation_pipeline(
                repo_url="https://github.com/owner/repo",
                criteria="basic",
                progress_queue=mock_queue,
            )

            assert "jeanpierre_result" in result


class TestSaveEvaluationResults:
    """Test cases for saving evaluation results."""

    @pytest.mark.asyncio
    async def test_save_evaluation_results_success(self):
        """Test saving evaluation results successfully."""
        from app.services.evaluation_service import save_evaluation_results

        mock_evaluation_data = {
            "repo_url": "https://github.com/owner/repo",
            "jeanpierre_result": {
                "overall_score": 85,
                "rating_tier": "Premier Cru",
                "summary": "Excellent",
                "sommelier_outputs": [],
            },
        }

        with patch(
            "app.services.evaluation_service.ResultRepository"
        ) as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.create_result = AsyncMock(return_value="result_123")
            mock_repo_class.return_value = mock_repo

            result_id = await save_evaluation_results(
                evaluation_id="eval_123",
                evaluation_data=mock_evaluation_data,
            )

            assert result_id == "result_123"
            mock_repo.create_result.assert_called_once()

    @pytest.mark.asyncio
    async def test_save_evaluation_results_calculates_tier(self):
        """Test that saving results correctly calculates rating tier."""
        from app.services.evaluation_service import save_evaluation_results
        from app.models.results import RatingTier

        mock_evaluation_data = {
            "repo_url": "https://github.com/owner/repo",
            "jeanpierre_result": {
                "overall_score": 95,
                "rating_tier": "Legendary",
                "summary": "Exceptional",
                "sommelier_outputs": [],
            },
        }

        with patch(
            "app.services.evaluation_service.ResultRepository"
        ) as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.create_result = AsyncMock(return_value="result_456")
            mock_repo_class.return_value = mock_repo

            await save_evaluation_results(
                evaluation_id="eval_123",
                evaluation_data=mock_evaluation_data,
            )

            call_args = mock_repo.create_result.call_args[1]["result_data"]
            assert call_args["final_evaluation"]["overall_score"] == 95


class TestHandleEvaluationError:
    """Test cases for handling evaluation errors."""

    @pytest.mark.asyncio
    async def test_handle_evaluation_error_updates_status(self):
        """Test that evaluation errors update the status correctly."""
        from app.services.evaluation_service import handle_evaluation_error

        with patch(
            "app.services.evaluation_service.EvaluationRepository"
        ) as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.update_status = AsyncMock()
            mock_repo_class.return_value = mock_repo

            await handle_evaluation_error(
                evaluation_id="eval_123",
                error_message="GitHub API rate limit exceeded",
            )

            mock_repo.update_status.assert_called_once_with(
                "eval_123", "failed", "GitHub API rate limit exceeded"
            )

    @pytest.mark.asyncio
    async def test_handle_evaluation_error_logs_error(self):
        """Test that evaluation errors are logged."""
        from app.services.evaluation_service import handle_evaluation_error

        with patch("app.services.evaluation_service.logger") as mock_logger:
            await handle_evaluation_error(
                evaluation_id="eval_123",
                error_message="Connection timeout",
            )

            mock_logger.error.assert_called_once()


class TestGetEvaluationProgress:
    """Test cases for getting evaluation progress."""

    @pytest.mark.asyncio
    async def test_get_evaluation_progress_pending(self):
        """Test getting progress for pending evaluation."""
        from app.services.evaluation_service import get_evaluation_progress

        with patch(
            "app.services.evaluation_service.EvaluationRepository"
        ) as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_id = AsyncMock(return_value={"status": "pending"})
            mock_repo_class.return_value = mock_repo

            progress = await get_evaluation_progress("eval_123")

            assert progress["status"] == "pending"
            assert progress["completed_steps"] == 0
            assert progress["total_steps"] == 6

    @pytest.mark.asyncio
    async def test_get_evaluation_progress_partial(self):
        """Test getting progress for partially complete evaluation."""
        from app.services.evaluation_service import get_evaluation_progress

        with patch(
            "app.services.evaluation_service.EvaluationRepository"
        ) as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_id = AsyncMock(
                return_value={
                    "status": "running",
                    "completed_sommeliers": ["marcel", "isabella"],
                }
            )
            mock_repo_class.return_value = mock_repo

            progress = await get_evaluation_progress("eval_123")

            assert progress["status"] == "running"
            assert progress["completed_steps"] == 2
            assert progress["remaining_steps"] == 4

    @pytest.mark.asyncio
    async def test_get_evaluation_progress_completed(self):
        """Test getting progress for completed evaluation."""
        from app.services.evaluation_service import get_evaluation_progress

        with patch(
            "app.services.evaluation_service.EvaluationRepository"
        ) as mock_repo_class:
            mock_repo = MagicMock()
            mock_repo.get_by_id = AsyncMock(
                return_value={
                    "status": "completed",
                    "completed_sommeliers": [
                        "marcel",
                        "isabella",
                        "heinrich",
                        "sofia",
                        "laurent",
                    ],
                }
            )
            mock_repo_class.return_value = mock_repo

            progress = await get_evaluation_progress("eval_123")

            assert progress["status"] == "completed"
            assert progress["completed_steps"] == 6


class TestEvaluationServiceIntegration:
    """Integration tests for evaluation service."""

    @pytest.mark.asyncio
    async def test_full_evaluation_flow(self):
        """Test complete evaluation flow from start to finish."""
        from app.services.evaluation_service import run_full_evaluation

        mock_graph_result = {
            "repo_url": "https://github.com/owner/repo",
            "jeanpierre_result": {
                "overall_score": 88,
                "rating_tier": "Premier Cru",
                "summary": "Excellent code quality",
                "sommelier_outputs": [],
            },
            "completed_sommeliers": [
                "marcel",
                "isabella",
                "heinrich",
                "sofia",
                "laurent",
            ],
        }

        with patch(
            "app.services.evaluation_service.EvaluationRepository"
        ) as mock_eval_repo_class:
            mock_eval_repo = MagicMock()
            mock_eval_repo.create_evaluation = AsyncMock(return_value="eval_789")
            mock_eval_repo.update_status = AsyncMock()
            mock_eval_repo_class.return_value = mock_eval_repo

            with patch(
                "app.services.evaluation_service.ResultRepository"
            ) as mock_result_repo_class:
                mock_result_repo = MagicMock()
                mock_result_repo.create_result = AsyncMock(return_value="result_789")
                mock_result_repo_class.return_value = mock_result_repo

                with patch(
                    "app.services.evaluation_service.get_evaluation_graph"
                ) as mock_graph:
                    mock_graph.return_value.ainvoke = AsyncMock(
                        return_value=mock_graph_result
                    )

                    with patch(
                        "app.services.evaluation_service.GitHubService"
                    ) as mock_github_class:
                        mock_github = MagicMock()
                        mock_github.get_full_repo_context = AsyncMock(return_value={})
                        mock_github_class.return_value = mock_github

                        result = await run_full_evaluation(
                            repo_url="https://github.com/owner/repo",
                            criteria="basic",
                            user_id="user_123",
                        )

                        assert result["evaluation_id"] == "eval_789"
                        assert result["status"] == "completed"
                        assert result["score"] == 88

    @pytest.mark.asyncio
    async def test_evaluation_flow_with_hackathon_criteria(self):
        """Test evaluation flow with hackathon criteria."""
        from app.services.evaluation_service import run_full_evaluation

        mock_graph_result = {
            "repo_url": "https://github.com/hackathon/project",
            "jeanpierre_result": {
                "overall_score": 92,
                "rating_tier": "Grand Cru",
                "summary": "Outstanding hackathon project",
                "sommelier_outputs": [],
            },
            "completed_sommeliers": [
                "marcel",
                "isabella",
                "heinrich",
                "sofia",
                "laurent",
            ],
        }

        with patch(
            "app.services.evaluation_service.EvaluationRepository"
        ) as mock_eval_repo_class:
            mock_eval_repo = MagicMock()
            mock_eval_repo.create_evaluation = AsyncMock(return_value="eval_hack")
            mock_eval_repo_class.return_value = mock_eval_repo

            with patch(
                "app.services.evaluation_service.ResultRepository"
            ) as mock_result_repo_class:
                mock_result_repo = MagicMock()
                mock_result_repo.create_result = AsyncMock(return_value="result_hack")
                mock_result_repo_class.return_value = mock_result_repo

                with patch(
                    "app.services.evaluation_service.get_evaluation_graph"
                ) as mock_graph:
                    mock_graph.return_value.ainvoke = AsyncMock(
                        return_value=mock_graph_result
                    )

                    with patch(
                        "app.services.evaluation_service.GitHubService"
                    ) as mock_github_class:
                        mock_github = MagicMock()
                        mock_github.get_full_repo_context = AsyncMock(return_value={})
                        mock_github_class.return_value = mock_github

                        result = await run_full_evaluation(
                            repo_url="https://github.com/hackathon/project",
                            criteria="hackathon",
                            user_id="user_456",
                        )

                        assert result["evaluation_id"] == "eval_hack"
                        assert result["criteria"] == "hackathon"
