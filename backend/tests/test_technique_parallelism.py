"""Tests for technique parallelism with concurrency limiting in BaseCategoryNode"""

import asyncio
import time
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone

from app.graph.nodes.technique_categories.base_category import BaseCategoryNode
from app.techniques.schema import TechniqueCategory
from app.techniques.base_technique import TechniqueResult
from app.models.graph import ItemScore


class MockCategoryNode(BaseCategoryNode):
    """Concrete implementation for testing"""

    @property
    def category(self) -> TechniqueCategory:
        return TechniqueCategory.AROMA

    @property
    def display_name(self) -> str:
        return "Test Category"


@pytest.fixture
def mock_state():
    return {
        "repo_url": "https://github.com/test/repo",
        "repo_context": {},
        "evaluation_criteria": "basic",
        "user_id": "user123",
    }


def create_mock_technique_result(
    technique_id: str, success: bool = True
) -> TechniqueResult:
    """Create a mock TechniqueResult for testing."""
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if success:
        return TechniqueResult(
            technique_id=technique_id,
            item_scores={
                "A1": ItemScore(
                    item_id="A1",
                    score=80,
                    evaluated_by=technique_id,
                    technique_id=technique_id,
                    timestamp=timestamp,
                )
            },
            trace_events=[],
            token_usage={"prompt_tokens": 10, "completion_tokens": 5},
            cost_usd=0.001,
            success=True,
        )
    else:
        return TechniqueResult(
            technique_id=technique_id,
            success=False,
            error="Simulated failure",
        )


class TestConcurrentExecution:
    """Test that techniques execute concurrently (in parallel)."""

    @pytest.mark.asyncio
    async def test_techniques_execute_concurrently(self, mock_state):
        """Verify multiple techniques run in parallel by checking total time."""
        node = MockCategoryNode()
        execution_times = []

        async def timed_execute(technique_id: str, state: dict):
            start = time.monotonic()
            await asyncio.sleep(0.1)
            execution_times.append(time.monotonic() - start)
            return create_mock_technique_result(technique_id)

        mock_router = MagicMock()
        mock_router.select_techniques.return_value = ["tech1", "tech2", "tech3"]

        async def mock_execute_single(technique_id, state):
            return await timed_execute(technique_id, state)

        mock_router.execute_single_technique = mock_execute_single

        mock_aggregated = MagicMock()
        mock_aggregated.item_scores = {"A1": MagicMock()}
        mock_aggregated.techniques_used = ["tech1", "tech2", "tech3"]
        mock_aggregated.methodology_trace = []
        mock_aggregated.failed_techniques = []
        mock_aggregated.total_token_usage = {
            "prompt_tokens": 30,
            "completion_tokens": 15,
        }
        mock_aggregated.total_cost_usd = 0.003
        mock_router.aggregate_results.return_value = mock_aggregated

        node.router = mock_router

        with patch(
            "app.graph.nodes.technique_categories.base_category.settings"
        ) as mock_settings:
            mock_settings.MAX_CONCURRENT_TECHNIQUES = 5
            mock_settings.TECHNIQUE_TIMEOUT_SECONDS = 60

            start_time = time.monotonic()
            result = await node.evaluate(mock_state)
            total_time = time.monotonic() - start_time

        assert total_time < 0.25, (
            f"Expected parallel execution (< 0.25s), but took {total_time}s"
        )
        assert len(execution_times) == 3
        assert result["techniques_used"] == ["tech1", "tech2", "tech3"]

    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrency(self, mock_state):
        """Verify MAX_CONCURRENT_TECHNIQUES limits the number of concurrent executions."""
        node = MockCategoryNode()
        concurrent_count = 0
        max_concurrent_observed = 0

        async def tracked_execute(technique_id: str, state: dict):
            nonlocal concurrent_count, max_concurrent_observed
            concurrent_count += 1
            max_concurrent_observed = max(max_concurrent_observed, concurrent_count)
            await asyncio.sleep(0.05)
            concurrent_count -= 1
            return create_mock_technique_result(technique_id)

        mock_router = MagicMock()
        mock_router.select_techniques.return_value = [
            "tech1",
            "tech2",
            "tech3",
            "tech4",
            "tech5",
        ]

        async def mock_execute_single(technique_id, state):
            return await tracked_execute(technique_id, state)

        mock_router.execute_single_technique = mock_execute_single

        mock_aggregated = MagicMock()
        mock_aggregated.item_scores = {}
        mock_aggregated.techniques_used = []
        mock_aggregated.methodology_trace = []
        mock_aggregated.failed_techniques = []
        mock_aggregated.total_token_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        mock_aggregated.total_cost_usd = 0.0
        mock_router.aggregate_results.return_value = mock_aggregated

        node.router = mock_router

        with patch(
            "app.graph.nodes.technique_categories.base_category.settings"
        ) as mock_settings:
            mock_settings.MAX_CONCURRENT_TECHNIQUES = 2
            mock_settings.TECHNIQUE_TIMEOUT_SECONDS = 60

            await node.evaluate(mock_state)

        assert max_concurrent_observed <= 2, (
            f"Max concurrent {max_concurrent_observed} exceeded limit of 2"
        )
        assert max_concurrent_observed == 2, (
            f"Expected max concurrent of 2, got {max_concurrent_observed}"
        )


class TestPerTechniqueTimeout:
    """Test that individual techniques can timeout without affecting others."""

    @pytest.mark.asyncio
    async def test_slow_technique_times_out(self, mock_state):
        """Verify a slow technique gets timeout error while others complete."""
        node = MockCategoryNode()

        async def variable_speed_execute(technique_id: str, state: dict):
            if technique_id == "slow_tech":
                await asyncio.sleep(10)
            else:
                await asyncio.sleep(0.01)
            return create_mock_technique_result(technique_id)

        mock_router = MagicMock()
        mock_router.select_techniques.return_value = ["fast1", "slow_tech", "fast2"]

        async def mock_execute_single(technique_id, state):
            return await variable_speed_execute(technique_id, state)

        mock_router.execute_single_technique = mock_execute_single

        mock_aggregated = MagicMock()
        mock_aggregated.item_scores = {"A1": MagicMock()}
        mock_aggregated.techniques_used = ["fast1", "fast2"]
        mock_aggregated.methodology_trace = []
        mock_aggregated.failed_techniques = []
        mock_aggregated.total_token_usage = {
            "prompt_tokens": 20,
            "completion_tokens": 10,
        }
        mock_aggregated.total_cost_usd = 0.002
        mock_router.aggregate_results.return_value = mock_aggregated

        node.router = mock_router

        with patch(
            "app.graph.nodes.technique_categories.base_category.settings"
        ) as mock_settings:
            mock_settings.MAX_CONCURRENT_TECHNIQUES = 5
            mock_settings.TECHNIQUE_TIMEOUT_SECONDS = 0.1

            result = await node.evaluate(mock_state)

        trace_meta = result["trace_metadata"]["aroma"]
        assert trace_meta["techniques_failed"] == 1
        assert len(trace_meta["failed_techniques"]) == 1
        assert trace_meta["failed_techniques"][0]["technique_id"] == "slow_tech"
        assert "timeout" in trace_meta["failed_techniques"][0]["error"]

    @pytest.mark.asyncio
    async def test_timeout_value_respected(self, mock_state):
        """Verify the timeout value from settings is used correctly."""
        node = MockCategoryNode()

        async def slow_execute(technique_id: str, state: dict):
            await asyncio.sleep(5)
            return create_mock_technique_result(technique_id)

        mock_router = MagicMock()
        mock_router.select_techniques.return_value = ["tech1"]

        async def mock_execute_single(technique_id, state):
            return await slow_execute(technique_id, state)

        mock_router.execute_single_technique = mock_execute_single

        mock_aggregated = MagicMock()
        mock_aggregated.item_scores = {}
        mock_aggregated.techniques_used = []
        mock_aggregated.methodology_trace = []
        mock_aggregated.failed_techniques = []
        mock_aggregated.total_token_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        mock_aggregated.total_cost_usd = 0.0
        mock_router.aggregate_results.return_value = mock_aggregated

        node.router = mock_router

        with patch(
            "app.graph.nodes.technique_categories.base_category.settings"
        ) as mock_settings:
            mock_settings.MAX_CONCURRENT_TECHNIQUES = 5
            mock_settings.TECHNIQUE_TIMEOUT_SECONDS = 0.05

            start = time.monotonic()
            result = await node.evaluate(mock_state)
            elapsed = time.monotonic() - start

        assert elapsed < 0.2, f"Should have timed out quickly, but took {elapsed}s"
        assert result["trace_metadata"]["aroma"]["techniques_failed"] == 1


class TestErrorIsolation:
    """Test that one failing technique doesn't affect others."""

    @pytest.mark.asyncio
    async def test_one_failure_others_succeed(self, mock_state):
        """Verify when one technique fails, others still complete successfully."""
        node = MockCategoryNode()

        async def mixed_execute(technique_id: str, state: dict):
            if technique_id == "failing_tech":
                raise ValueError("Simulated error")
            return create_mock_technique_result(technique_id)

        mock_router = MagicMock()
        mock_router.select_techniques.return_value = ["good1", "failing_tech", "good2"]

        async def mock_execute_single(technique_id, state):
            return await mixed_execute(technique_id, state)

        mock_router.execute_single_technique = mock_execute_single

        mock_aggregated = MagicMock()
        mock_aggregated.item_scores = {"A1": MagicMock()}
        mock_aggregated.techniques_used = ["good1", "good2"]
        mock_aggregated.methodology_trace = []
        mock_aggregated.failed_techniques = []
        mock_aggregated.total_token_usage = {
            "prompt_tokens": 20,
            "completion_tokens": 10,
        }
        mock_aggregated.total_cost_usd = 0.002
        mock_router.aggregate_results.return_value = mock_aggregated

        node.router = mock_router

        with patch(
            "app.graph.nodes.technique_categories.base_category.settings"
        ) as mock_settings:
            mock_settings.MAX_CONCURRENT_TECHNIQUES = 5
            mock_settings.TECHNIQUE_TIMEOUT_SECONDS = 60

            result = await node.evaluate(mock_state)

        trace_meta = result["trace_metadata"]["aroma"]
        assert trace_meta["techniques_succeeded"] == 2
        assert trace_meta["techniques_failed"] == 1
        assert len(trace_meta["failed_techniques"]) == 1
        assert trace_meta["failed_techniques"][0]["technique_id"] == "failing_tech"
        assert "Simulated error" in trace_meta["failed_techniques"][0]["error"]

    @pytest.mark.asyncio
    async def test_all_techniques_can_fail(self, mock_state):
        """Verify graceful handling when all techniques fail."""
        node = MockCategoryNode()

        async def always_fail(technique_id: str, state: dict):
            raise RuntimeError(f"Error in {technique_id}")

        mock_router = MagicMock()
        mock_router.select_techniques.return_value = ["tech1", "tech2"]

        async def mock_execute_single(technique_id, state):
            return await always_fail(technique_id, state)

        mock_router.execute_single_technique = mock_execute_single

        mock_aggregated = MagicMock()
        mock_aggregated.item_scores = {}
        mock_aggregated.techniques_used = []
        mock_aggregated.methodology_trace = []
        mock_aggregated.failed_techniques = []
        mock_aggregated.total_token_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        mock_aggregated.total_cost_usd = 0.0
        mock_router.aggregate_results.return_value = mock_aggregated

        node.router = mock_router

        with patch(
            "app.graph.nodes.technique_categories.base_category.settings"
        ) as mock_settings:
            mock_settings.MAX_CONCURRENT_TECHNIQUES = 5
            mock_settings.TECHNIQUE_TIMEOUT_SECONDS = 60

            result = await node.evaluate(mock_state)

        trace_meta = result["trace_metadata"]["aroma"]
        assert trace_meta["techniques_succeeded"] == 0
        assert trace_meta["techniques_failed"] == 2
        assert len(trace_meta["failed_techniques"]) == 2


class TestResultsAggregation:
    """Test that results from all successful techniques are properly aggregated."""

    @pytest.mark.asyncio
    async def test_all_successful_results_collected(self, mock_state):
        """Verify all successful technique results are included in aggregation."""
        node = MockCategoryNode()
        results_created = []

        async def create_result(technique_id: str, state: dict):
            result = create_mock_technique_result(technique_id)
            results_created.append(result)
            return result

        mock_router = MagicMock()
        mock_router.select_techniques.return_value = ["tech1", "tech2", "tech3"]

        async def mock_execute_single(technique_id, state):
            return await create_result(technique_id, state)

        mock_router.execute_single_technique = mock_execute_single

        mock_aggregated = MagicMock()
        mock_aggregated.item_scores = {"A1": MagicMock(), "A2": MagicMock()}
        mock_aggregated.techniques_used = ["tech1", "tech2", "tech3"]
        mock_aggregated.methodology_trace = [
            {"technique_id": "tech1", "event": "evaluated"},
            {"technique_id": "tech2", "event": "evaluated"},
            {"technique_id": "tech3", "event": "evaluated"},
        ]
        mock_aggregated.failed_techniques = []
        mock_aggregated.total_token_usage = {
            "prompt_tokens": 30,
            "completion_tokens": 15,
        }
        mock_aggregated.total_cost_usd = 0.003
        mock_router.aggregate_results.return_value = mock_aggregated

        node.router = mock_router

        with patch(
            "app.graph.nodes.technique_categories.base_category.settings"
        ) as mock_settings:
            mock_settings.MAX_CONCURRENT_TECHNIQUES = 5
            mock_settings.TECHNIQUE_TIMEOUT_SECONDS = 60

            result = await node.evaluate(mock_state)

        call_args = mock_router.aggregate_results.call_args[0][0]
        assert len(call_args) == 3
        assert all(isinstance(r, TechniqueResult) for r in call_args)
        assert result["techniques_used"] == ["tech1", "tech2", "tech3"]
        assert len(result["methodology_trace"]) == 3
        assert result["trace_metadata"]["aroma"]["techniques_succeeded"] == 3
        assert result["trace_metadata"]["aroma"]["techniques_failed"] == 0


class TestEmptyTechniqueList:
    """Test handling of empty technique lists."""

    @pytest.mark.asyncio
    async def test_empty_technique_list_returns_empty_result(self, mock_state):
        """Verify graceful handling when no techniques are selected."""
        node = MockCategoryNode()

        mock_router = MagicMock()
        mock_router.select_techniques.return_value = []
        node.router = mock_router

        with patch(
            "app.graph.nodes.technique_categories.base_category.settings"
        ) as mock_settings:
            mock_settings.MAX_CONCURRENT_TECHNIQUES = 5
            mock_settings.TECHNIQUE_TIMEOUT_SECONDS = 60

            result = await node.evaluate(mock_state)

        assert "errors" in result
        assert result["errors"][0] == "aroma: no techniques available"
        assert result["completed_sommeliers"] == ["aroma"]
        assert result["trace_metadata"]["aroma"]["techniques_count"] == 0


class TestConfigurationIntegration:
    """Test that configuration values are properly integrated."""

    @pytest.mark.asyncio
    async def test_settings_values_used(self, mock_state):
        """Verify that MAX_CONCURRENT_TECHNIQUES and TECHNIQUE_TIMEOUT_SECONDS from settings are used."""
        node = MockCategoryNode()

        sem_value_captured = None
        timeout_value_captured = None

        original_init = asyncio.Semaphore.__init__

        def capture_semaphore_init(self, value):
            nonlocal sem_value_captured
            sem_value_captured = value
            return original_init(self, value)

        mock_router = MagicMock()
        mock_router.select_techniques.return_value = ["tech1"]
        mock_router.execute_single_technique = AsyncMock(
            return_value=create_mock_technique_result("tech1")
        )

        mock_aggregated = MagicMock()
        mock_aggregated.item_scores = {}
        mock_aggregated.techniques_used = ["tech1"]
        mock_aggregated.methodology_trace = []
        mock_aggregated.failed_techniques = []
        mock_aggregated.total_token_usage = {"prompt_tokens": 0, "completion_tokens": 0}
        mock_aggregated.total_cost_usd = 0.0
        mock_router.aggregate_results.return_value = mock_aggregated

        node.router = mock_router

        with patch(
            "app.graph.nodes.technique_categories.base_category.settings"
        ) as mock_settings:
            mock_settings.MAX_CONCURRENT_TECHNIQUES = 7
            mock_settings.TECHNIQUE_TIMEOUT_SECONDS = 120

            with patch.object(asyncio.Semaphore, "__init__", capture_semaphore_init):
                with patch(
                    "app.graph.nodes.technique_categories.base_category.asyncio.wait_for"
                ) as mock_wait_for:

                    async def capture_wait_for(coro, timeout):
                        nonlocal timeout_value_captured
                        timeout_value_captured = timeout
                        return await coro

                    mock_wait_for.side_effect = capture_wait_for
                    await node.evaluate(mock_state)

        assert sem_value_captured == 7
        assert timeout_value_captured == 120
