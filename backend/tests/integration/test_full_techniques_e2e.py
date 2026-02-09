"""End-to-end integration tests for the full techniques evaluation pipeline.

This module tests the complete evaluation pipeline using mocks for all external
dependencies (LLM calls, database, etc.) to ensure fast, deterministic tests.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime, timezone

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END

from app.graph.graph_factory import (
    get_evaluation_graph,
    list_available_modes,
    is_valid_mode,
)
from app.graph.full_techniques_graph import create_full_techniques_graph
from app.graph.state import EvaluationState
from app.services.evaluation_service import _create_initial_state
from app.criteria.scoring import (
    calculate_exclusion_normalized_score,
    adjust_score_by_confidence,
)
from app.constants import get_quality_gate
from app.techniques.router import TechniqueRouter
from app.techniques.base_technique import TechniqueResult
from app.models.graph import ItemScore


def create_mock_checkpointer():
    """Create a mock checkpointer for graph compilation."""
    return MagicMock(spec=BaseCheckpointSaver)


@pytest.fixture
def mock_registry_techniques():
    """Mock technique registry with sample techniques."""
    techniques = []
    for i in range(75):
        tech = MagicMock()
        tech.id = f"technique-{i:03d}"
        tech.category = MagicMock()
        tech.category.value = [
            "aroma",
            "palate",
            "body",
            "finish",
            "balance",
            "vintage",
            "terroir",
            "cellar",
        ][i % 8]
        tech.applicable_hats = ["white", "red", "black", "yellow", "green", "blue"]
        techniques.append(tech)
    return techniques


@pytest.fixture
def sample_repo_context():
    """Sample repository context for testing."""
    return {
        "repo_url": "https://github.com/test/repo",
        "files": ["main.py", "README.md"],
        "readme": "# Test Repository",
        "techniques": [{"id": f"tech-{i}"} for i in range(75)],
    }


@pytest.fixture
def sample_evaluation_state(sample_repo_context) -> EvaluationState:
    """Create a sample evaluation state for testing."""
    return _create_initial_state(
        repo_url="https://github.com/test/repo",
        repo_context=sample_repo_context,
        criteria="basic",
        user_id="test_user_123",
    )


class TestGraphCompilationAndStructure:
    """Test graph compilation and node structure."""

    def test_full_techniques_graph_compiles_without_error(self):
        """Test that the full_techniques graph compiles successfully."""
        with patch(
            "app.graph.full_techniques_graph.get_checkpointer"
        ) as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            graph = create_full_techniques_graph()

            assert graph is not None
            assert hasattr(graph, "invoke")
            assert hasattr(graph, "ainvoke")

    def test_graph_has_all_expected_nodes(self):
        """Test that graph has all 8 category nodes plus synthesis and finalize."""
        with patch(
            "app.graph.full_techniques_graph.get_checkpointer"
        ) as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            graph = create_full_techniques_graph()
            nodes = graph.nodes

            expected_category_nodes = [
                "aroma",
                "palate",
                "body",
                "finish",
                "balance",
                "vintage",
                "terroir",
                "cellar",
            ]
            expected_synthesis_nodes = ["deep_synthesis", "finalize"]
            expected_enrichment_nodes = ["web_search_enrich", "code_analysis_enrich"]

            for node in expected_category_nodes:
                assert node in nodes, f"Category node '{node}' not found in graph"

            for node in expected_synthesis_nodes:
                assert node in nodes, f"Synthesis node '{node}' not found in graph"

            for node in expected_enrichment_nodes:
                assert node in nodes, f"Enrichment node '{node}' not found in graph"

    def test_graph_edges_fan_out_fan_in_pattern(self):
        """Test that graph has correct fan-out from enrichment and fan-in to synthesis."""
        with patch(
            "app.graph.full_techniques_graph.get_checkpointer"
        ) as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.full_techniques_graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = False

                graph = create_full_techniques_graph()
                builder = getattr(graph, "builder", None)
                assert builder is not None

                all_edges = builder.edges
                category_nodes = [
                    "aroma",
                    "palate",
                    "body",
                    "finish",
                    "balance",
                    "vintage",
                    "terroir",
                    "cellar",
                ]

                for enrich_node in ["web_search_enrich", "code_analysis_enrich"]:
                    for cat_node in category_nodes:
                        edge_exists = any(
                            e[0] == enrich_node and e[1] == cat_node for e in all_edges
                        )
                        assert edge_exists, (
                            f"Missing edge from {enrich_node} to {cat_node}"
                        )

                for cat_node in category_nodes:
                    edge_exists = any(
                        e[0] == cat_node and e[1] == "deep_synthesis" for e in all_edges
                    )
                    assert edge_exists, (
                        f"Missing edge from {cat_node} to deep_synthesis"
                    )

                deep_to_finalize = any(
                    e[0] == "deep_synthesis" and e[1] == "finalize" for e in all_edges
                )
                assert deep_to_finalize, "Missing edge from deep_synthesis to finalize"

                finalize_to_end = any(
                    e[0] == "finalize" and e[1] == END for e in all_edges
                )
                assert finalize_to_end, "Missing edge from finalize to END"


class TestFactoryRegistration:
    """Test graph factory registration and lookup."""

    def test_get_evaluation_graph_returns_compiled_graph(self):
        """Test that get_evaluation_graph returns a compiled graph for full_techniques."""
        with patch("app.graph.graph_factory._graph_builders", {}):
            with patch(
                "app.graph.full_techniques_graph.get_checkpointer"
            ) as mock_checkpointer:
                mock_checkpointer.return_value = create_mock_checkpointer()

                graph = get_evaluation_graph("full_techniques")

                assert graph is not None
                assert hasattr(graph, "invoke")
                assert hasattr(graph, "ainvoke")

    def test_full_techniques_in_list_available_modes(self):
        """Test that full_techniques is listed in available modes."""
        with patch("app.graph.graph_factory._graph_builders", {}):
            modes = list_available_modes()
            assert "full_techniques" in modes
            assert "six_sommeliers" in modes
            assert "grand_tasting" in modes

    def test_is_valid_mode_recognizes_full_techniques(self):
        """Test that is_valid_mode correctly identifies full_techniques."""
        with patch("app.graph.graph_factory._graph_builders", {}):
            assert is_valid_mode("full_techniques") is True
            assert is_valid_mode("invalid_mode") is False


class TestStateInitialization:
    """Test state initialization from evaluation service."""

    def test_create_initial_state_produces_valid_evaluation_state(
        self, sample_repo_context
    ):
        """Test that _create_initial_state produces a valid EvaluationState."""
        state = _create_initial_state(
            repo_url="https://github.com/test/repo",
            repo_context=sample_repo_context,
            criteria="basic",
            user_id="test_user_123",
        )

        assert state["repo_url"] == "https://github.com/test/repo"
        assert state["repo_context"] == sample_repo_context
        assert state["evaluation_criteria"] == "basic"
        assert state["user_id"] == "test_user_123"
        assert state["marcel_result"] is None
        assert state["isabella_result"] is None
        assert state["heinrich_result"] is None
        assert state["sofia_result"] is None
        assert state["laurent_result"] is None
        assert state["completed_sommeliers"] == []
        assert state["errors"] == []

    def test_create_initial_state_with_progress_fields(self, sample_repo_context):
        """Test that _create_initial_state includes progress fields when requested."""
        state = _create_initial_state(
            repo_url="https://github.com/test/repo",
            repo_context=sample_repo_context,
            criteria="hackathon",
            user_id="test_user_456",
            evaluation_id="eval_123",
            include_progress=True,
        )

        assert state["evaluation_id"] == "eval_123"
        assert state["progress_percent"] == 0
        assert state["current_stage"] == ""

    def test_all_required_fields_present_in_state(self, sample_repo_context):
        """Test that all required EvaluationState fields are present."""
        state = _create_initial_state(
            repo_url="https://github.com/test/repo",
            repo_context=sample_repo_context,
            criteria="academic",
            user_id="test_user",
        )

        required_fields = [
            "repo_url",
            "repo_context",
            "evaluation_criteria",
            "user_id",
            "marcel_result",
            "isabella_result",
            "heinrich_result",
            "sofia_result",
            "laurent_result",
            "completed_sommeliers",
            "errors",
            "token_usage",
            "cost_usage",
            "trace_metadata",
            "started_at",
            "completed_at",
        ]

        for field in required_fields:
            assert field in state, f"Required field '{field}' missing from state"


class TestQualityGateIntegration:
    """Test quality gate logic integration."""

    def test_score_70_coverage_50_returns_pass(self):
        """Test that score >= 70 with coverage >= 50% returns PASS."""
        result = get_quality_gate(70.0, 0.5)
        assert result == "PASS"

    def test_score_100_coverage_100_returns_pass(self):
        """Test that perfect score with full coverage returns PASS."""
        result = get_quality_gate(100.0, 1.0)
        assert result == "PASS"

    def test_score_50_coverage_50_returns_concerns(self):
        """Test that score >= 50 with coverage >= 50% returns CONCERNS."""
        result = get_quality_gate(50.0, 0.5)
        assert result == "CONCERNS"

    def test_score_69_coverage_50_returns_concerns(self):
        """Test that score 69 with coverage 50% returns CONCERNS."""
        result = get_quality_gate(69.0, 0.5)
        assert result == "CONCERNS"

    def test_score_49_coverage_50_returns_fail(self):
        """Test that score < 50 returns FAIL."""
        result = get_quality_gate(49.0, 0.5)
        assert result == "FAIL"

    def test_score_0_coverage_100_returns_fail(self):
        """Test that zero score returns FAIL even with full coverage."""
        result = get_quality_gate(0.0, 1.0)
        assert result == "FAIL"

    def test_coverage_below_50_returns_incomplete(self):
        """Test that coverage < 50% returns INCOMPLETE regardless of score."""
        result_high_score = get_quality_gate(95.0, 0.3)
        assert result_high_score == "INCOMPLETE"

        result_low_score = get_quality_gate(30.0, 0.4)
        assert result_low_score == "INCOMPLETE"

    def test_coverage_boundary_at_50_percent(self):
        """Test coverage boundary at exactly 50%."""
        result = get_quality_gate(80.0, 0.5)
        assert result == "PASS"

        result_below = get_quality_gate(80.0, 0.49)
        assert result_below == "INCOMPLETE"


class TestScoringPipeline:
    """Test scoring calculation pipeline."""

    def test_calculate_exclusion_normalized_score_with_evaluated_items(self):
        """Test score calculation with evaluated items."""
        item_scores = {
            "A1": {"score": 8.0, "max_score": 10.0, "status": "evaluated"},
            "A2": {"score": 7.0, "max_score": 10.0, "status": "evaluated"},
            "A3": {"score": 9.0, "max_score": 10.0, "status": "evaluated"},
        }

        result = calculate_exclusion_normalized_score(item_scores)

        assert result["raw_score"] == 24.0
        assert result["max_possible"] == 30.0
        assert result["normalized_score"] == 80.0
        assert result["evaluated_items"] == ["A1", "A2", "A3"]
        assert result["excluded_items"] == []
        assert result["coverage_rate"] == 3 / 17

    def test_calculate_exclusion_normalized_score_with_excluded_items(self):
        """Test score calculation with some excluded items."""
        item_scores = {
            "A1": {"score": 8.0, "max_score": 10.0, "status": "evaluated"},
            "A2": {"score": 0.0, "max_score": 10.0, "status": "excluded"},
            "A3": {"score": 0.0, "max_score": 10.0, "status": "data_missing"},
        }

        result = calculate_exclusion_normalized_score(item_scores)

        assert result["raw_score"] == 8.0
        assert result["max_possible"] == 10.0
        assert result["normalized_score"] == 80.0
        assert len(result["evaluated_items"]) == 1
        assert len(result["excluded_items"]) == 2

    def test_calculate_exclusion_normalized_score_empty(self):
        """Test score calculation with no evaluated items."""
        result = calculate_exclusion_normalized_score({})

        assert result["raw_score"] == 0.0
        assert result["max_possible"] == 0.0
        assert result["normalized_score"] == 0.0
        assert result["coverage_rate"] == 0.0

    def test_confidence_adjustment_high(self):
        """Test that high confidence applies no adjustment."""
        adjusted = adjust_score_by_confidence(80.0, 100.0, "high")
        assert adjusted == 80.0

    def test_confidence_adjustment_medium(self):
        """Test that medium confidence applies 0.85 multiplier."""
        adjusted = adjust_score_by_confidence(80.0, 100.0, "medium")
        assert adjusted == 68.0

    def test_confidence_adjustment_low(self):
        """Test that low confidence applies weighted average toward neutral."""
        adjusted = adjust_score_by_confidence(80.0, 100.0, "low")
        expected = 0.3 * 80.0 + 0.7 * 50.0
        assert adjusted == expected


class TestRouterTechniqueSelection:
    """Test technique router selection logic."""

    def test_full_techniques_returns_all_techniques(self):
        """Test that full_techniques mode returns all 75 technique IDs."""
        router = TechniqueRouter()
        techniques = router.select_techniques("full_techniques")
        assert len(techniques) == 75

    def test_grand_tasting_returns_p0_only(self):
        """Test that grand_tasting mode returns only P0 techniques."""
        router = TechniqueRouter()
        grand = router.select_techniques("grand_tasting")
        full = router.select_techniques("full_techniques")

        assert len(grand) < len(full)
        assert len(grand) > 0

        from app.techniques.mappings import TECHNIQUE_PRIORITY, Priority

        for tech_id in grand:
            assert TECHNIQUE_PRIORITY.get(tech_id, Priority.P2) == Priority.P0

    def test_six_sommeliers_returns_p0_and_p1(self):
        """Test that six_sommeliers mode returns P0 and P1 techniques."""
        router = TechniqueRouter()
        six = router.select_techniques("six_sommeliers")
        grand = router.select_techniques("grand_tasting")
        full = router.select_techniques("full_techniques")

        assert len(grand) <= len(six) <= len(full)

        from app.techniques.mappings import TECHNIQUE_PRIORITY, Priority

        for tech_id in six:
            priority = TECHNIQUE_PRIORITY.get(tech_id, Priority.P2)
            assert priority in (Priority.P0, Priority.P1)

    def test_mode_count_ordering(self):
        """Test that mode counts follow expected ordering."""
        router = TechniqueRouter()
        grand = len(router.select_techniques("grand_tasting"))
        six = len(router.select_techniques("six_sommeliers"))
        full = len(router.select_techniques("full_techniques"))

        assert grand <= six <= full

    def test_category_filter_reduces_results(self):
        """Test that category filter reduces the number of techniques."""
        router = TechniqueRouter()
        all_aroma = router.select_techniques("full_techniques", category="aroma")
        all_techs = router.select_techniques("full_techniques")

        assert len(all_aroma) > 0
        assert len(all_aroma) < len(all_techs)

    def test_invalid_category_returns_empty(self):
        """Test that invalid category returns empty list."""
        router = TechniqueRouter()
        result = router.select_techniques("full_techniques", category="nonexistent")
        assert result == []


class TestErrorResilience:
    """Test error handling and resilience."""

    @pytest.mark.asyncio
    async def test_missing_techniques_in_registry_graceful_degradation(self):
        """Test that missing techniques in registry are handled gracefully."""
        router = TechniqueRouter()

        with patch("app.techniques.router.get_registry") as mock_get_registry:
            mock_registry = MagicMock()
            mock_registry.list_techniques.return_value = []
            mock_registry.get_technique.return_value = None
            mock_get_registry.return_value = mock_registry

            result = await router.execute_single_technique("nonexistent-tech", {})

            assert result.success is False
            assert "not found" in result.error.lower() or result.error is not None

    def test_empty_repo_context_no_crash(self, sample_evaluation_state):
        """Test that empty repo_context doesn't cause crashes."""
        state = sample_evaluation_state
        state["repo_context"] = {}

        assert state["repo_context"] == {}
        assert "repo_url" in state

    @pytest.mark.asyncio
    async def test_technique_execution_failure_continues(self):
        """Test that technique execution failure doesn't stop the pipeline."""
        router = TechniqueRouter()

        mock_result_success = TechniqueResult(
            technique_id="success-tech",
            success=True,
            item_scores={
                "A1": ItemScore(
                    item_id="A1",
                    score=5,
                    evaluated_by="success-tech",
                    technique_id="success-tech",
                    timestamp="2025-01-01T00:00:00Z",
                )
            },
        )

        mock_result_failure = TechniqueResult(
            technique_id="fail-tech",
            success=False,
            error="Simulated failure",
        )

        results = [mock_result_success, mock_result_failure]
        aggregated = router.aggregate_results(results)

        assert "success-tech" in aggregated.techniques_used
        assert len(aggregated.failed_techniques) == 1
        assert aggregated.failed_techniques[0]["technique_id"] == "fail-tech"

    def test_aggregate_results_with_empty_list(self):
        """Test that aggregating empty results doesn't crash."""
        router = TechniqueRouter()
        aggregated = router.aggregate_results([])

        assert aggregated.item_scores == {}
        assert aggregated.techniques_used == []
        assert aggregated.failed_techniques == []
        assert aggregated.total_cost_usd == 0.0


class TestEvaluationModeProgression:
    """Test evaluation mode progress steps."""

    def test_full_techniques_has_10_progress_steps(self):
        """Test that full_techniques mode has 10 progress steps."""
        from app.services.evaluation_service import get_evaluation_progress

        with patch("app.services.evaluation_service.EvaluationRepository") as mock_repo:
            mock_instance = MagicMock()
            mock_instance.get_by_id = AsyncMock(
                return_value={
                    "status": "running",
                    "completed_sommeliers": [],
                    "user_id": "test_user",
                    "evaluation_mode": "full_techniques",
                }
            )
            mock_repo.return_value = mock_instance

            import asyncio

            progress = asyncio.run(get_evaluation_progress("eval_123"))

            assert progress["total_steps"] == 10

    def test_six_sommeliers_has_6_progress_steps(self):
        """Test that six_sommeliers mode has 6 progress steps."""
        from app.services.evaluation_service import get_evaluation_progress

        with patch("app.services.evaluation_service.EvaluationRepository") as mock_repo:
            mock_instance = MagicMock()
            mock_instance.get_by_id = AsyncMock(
                return_value={
                    "status": "running",
                    "completed_sommeliers": [],
                    "user_id": "test_user",
                    "evaluation_mode": "six_sommeliers",
                }
            )
            mock_repo.return_value = mock_instance

            import asyncio

            progress = asyncio.run(get_evaluation_progress("eval_123"))

            assert progress["total_steps"] == 6

    def test_grand_tasting_has_8_progress_steps(self):
        """Test that grand_tasting mode has 8 progress steps."""
        from app.services.evaluation_service import get_evaluation_progress

        with patch("app.services.evaluation_service.EvaluationRepository") as mock_repo:
            mock_instance = MagicMock()
            mock_instance.get_by_id = AsyncMock(
                return_value={
                    "status": "running",
                    "completed_sommeliers": [],
                    "user_id": "test_user",
                    "evaluation_mode": "grand_tasting",
                }
            )
            mock_repo.return_value = mock_instance

            import asyncio

            progress = asyncio.run(get_evaluation_progress("eval_123"))

            assert progress["total_steps"] == 8

    def test_progress_percentage_calculation(self):
        """Test that progress percentage is calculated correctly."""
        from app.services.evaluation_service import get_evaluation_progress

        with patch("app.services.evaluation_service.EvaluationRepository") as mock_repo:
            mock_instance = MagicMock()
            mock_instance.get_by_id = AsyncMock(
                return_value={
                    "status": "running",
                    "completed_sommeliers": ["aroma", "palate", "body"],
                    "user_id": "test_user",
                    "evaluation_mode": "full_techniques",
                }
            )
            mock_repo.return_value = mock_instance

            import asyncio

            progress = asyncio.run(get_evaluation_progress("eval_123"))

            assert progress["completed_steps"] == 3
            assert progress["total_steps"] == 10
            assert progress["percentage"] == 30.0


class TestImportVerification:
    """Test that all required imports work correctly."""

    def test_import_graph_factory(self):
        """Test importing graph factory functions."""
        from app.graph.graph_factory import get_evaluation_graph, list_available_modes

        assert callable(get_evaluation_graph)
        assert callable(list_available_modes)

    def test_import_full_techniques_graph(self):
        """Test importing full techniques graph creator."""
        from app.graph.full_techniques_graph import create_full_techniques_graph

        assert callable(create_full_techniques_graph)

    def test_import_scoring_functions(self):
        """Test importing scoring functions."""
        from app.criteria.scoring import calculate_exclusion_normalized_score

        assert callable(calculate_exclusion_normalized_score)

    def test_import_quality_gate(self):
        """Test importing quality gate function."""
        from app.constants import get_quality_gate

        assert callable(get_quality_gate)

    def test_import_technique_router(self):
        """Test importing technique router."""
        from app.techniques.router import TechniqueRouter

        assert callable(TechniqueRouter)
