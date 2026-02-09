"""Test suite for graph visualization mode inference.

This module tests the mode inference logic in graph.py to ensure:
- Correct mode detection from evaluation_mode field
- Backward compatibility with legacy mode field
- Proper default fallback behavior
- Correct graph topology generation for each mode
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.main import app
from app.graph.graph_factory import EvaluationMode
from app.models.graph import (
    GRAPH_SCHEMA_VERSION,
    ReactFlowGraph,
    ModeResponse,
)
from app.core.exceptions import EmptyCellarError, CorkedError


client = TestClient(app)


# Fixtures


@pytest.fixture
def mock_user():
    """Mock authenticated user."""
    return MagicMock(
        id="user123",
        github_id="github456",
        username="testuser",
        email="test@example.com",
    )


@pytest.fixture
def mock_token():
    """Mock JWT token for authentication."""
    return "mock_jwt_token"


@pytest.fixture
def auth_headers(mock_token):
    """Authorization headers with Bearer token."""
    return {"Authorization": f"Bearer {mock_token}"}


# Mode Inference Tests


class TestModeInference:
    """Test mode inference from evaluation data.

    Tests cover the _determine_mode function's ability to correctly
    identify the evaluation mode from various field combinations.
    """

    def test_evaluation_mode_six_sommeliers_returns_correct_mode(self):
        """Test that evaluation_mode='six_sommeliers' returns SIX_SOMMELIERS.

        Given: An evaluation document with evaluation_mode='six_sommeliers'
        When: _determine_mode is called
        Then: It returns EvaluationMode.SIX_SOMMELIERS
        """
        from app.api.routes.graph import _determine_mode

        evaluation = {"evaluation_mode": "six_sommeliers"}
        mode = _determine_mode(evaluation)

        assert mode == EvaluationMode.SIX_SOMMELIERS

    def test_evaluation_mode_grand_tasting_returns_correct_mode(self):
        """Test that evaluation_mode='grand_tasting' returns GRAND_TASTING.

        Given: An evaluation document with evaluation_mode='grand_tasting'
        When: _determine_mode is called
        Then: It returns EvaluationMode.GRAND_TASTING
        """
        from app.api.routes.graph import _determine_mode

        evaluation = {"evaluation_mode": "grand_tasting"}
        mode = _determine_mode(evaluation)

        assert mode == EvaluationMode.GRAND_TASTING

    def test_evaluation_mode_full_techniques_returns_correct_mode(self):
        """Test that evaluation_mode='full_techniques' returns FULL_TECHNIQUES.

        Given: An evaluation document with evaluation_mode='full_techniques'
        When: _determine_mode is called
        Then: It returns EvaluationMode.FULL_TECHNIQUES
        """
        from app.api.routes.graph import _determine_mode

        evaluation = {"evaluation_mode": "full_techniques"}
        mode = _determine_mode(evaluation)

        assert mode == EvaluationMode.FULL_TECHNIQUES

    def test_missing_evaluation_mode_defaults_to_six_sommeliers(self):
        """Test that missing evaluation_mode field defaults to SIX_SOMMELIERS.

        Given: An evaluation document without evaluation_mode or mode fields
        When: _determine_mode is called
        Then: It returns EvaluationMode.SIX_SOMMELIERS as default
        """
        from app.api.routes.graph import _determine_mode

        evaluation = {"_id": "eval123", "user_id": "user123"}
        mode = _determine_mode(evaluation)

        assert mode == EvaluationMode.SIX_SOMMELIERS

    def test_legacy_mode_field_only_graceful_fallback(self):
        """Test graceful fallback to legacy 'mode' field when evaluation_mode missing.

        Given: An evaluation document with only the legacy 'mode' field
        When: _determine_mode is called
        Then: It falls back to using 'mode' field for backward compatibility
        """
        from app.api.routes.graph import _determine_mode

        evaluation = {"mode": "full_techniques"}
        mode = _determine_mode(evaluation)

        assert mode == EvaluationMode.FULL_TECHNIQUES

    def test_evaluation_mode_takes_precedence_over_legacy_mode(self):
        """Test that evaluation_mode takes precedence over legacy mode field.

        Given: An evaluation with both evaluation_mode and mode fields
        When: _determine_mode is called
        Then: evaluation_mode value is used, ignoring mode
        """
        from app.api.routes.graph import _determine_mode

        evaluation = {
            "evaluation_mode": "six_sommeliers",
            "mode": "full_techniques",
        }
        mode = _determine_mode(evaluation)

        assert mode == EvaluationMode.SIX_SOMMELIERS

    def test_legacy_mode_grand_tasting_fallback(self):
        """Test that legacy 'mode'='grand_tasting' works correctly.

        Given: An evaluation with only legacy mode='grand_tasting'
        When: _determine_mode is called
        Then: It returns EvaluationMode.GRAND_TASTING
        """
        from app.api.routes.graph import _determine_mode

        evaluation = {"mode": "grand_tasting"}
        mode = _determine_mode(evaluation)

        assert mode == EvaluationMode.GRAND_TASTING

    def test_legacy_mode_six_sommeliers_fallback(self):
        """Test that legacy 'mode'='six_sommeliers' works correctly.

        Given: An evaluation with only legacy mode='six_sommeliers'
        When: _determine_mode is called
        Then: It returns EvaluationMode.SIX_SOMMELIERS
        """
        from app.api.routes.graph import _determine_mode

        evaluation = {"mode": "six_sommeliers"}
        mode = _determine_mode(evaluation)

        assert mode == EvaluationMode.SIX_SOMMELIERS

    def test_empty_evaluation_defaults_to_six_sommeliers(self):
        """Test that completely empty evaluation defaults correctly.

        Given: An empty evaluation document
        When: _determine_mode is called
        Then: It returns EvaluationMode.SIX_SOMMELIERS
        """
        from app.api.routes.graph import _determine_mode

        evaluation = {}
        mode = _determine_mode(evaluation)

        assert mode == EvaluationMode.SIX_SOMMELIERS


# Graph Topology Tests by Mode


class TestGraphTopologyByMode:
    """Test that correct graph topology is returned for each mode."""

    def test_six_sommeliers_graph_has_expected_topology(self):
        """Test that six_sommeliers mode returns correct graph structure.

        Verifies the graph includes:
        - Start node
        - 5 sommelier agent nodes
        - Synthesis node (Jean-Pierre)
        - End node
        - Correct edges connecting all nodes
        """
        from app.services.graph_builder import (
            build_six_sommeliers_topology,
            SOMMELIER_CONFIG,
        )

        graph = build_six_sommeliers_topology()

        assert isinstance(graph, ReactFlowGraph)
        assert graph.mode == EvaluationMode.SIX_SOMMELIERS.value

        # Check for required node types
        node_types = {node.type for node in graph.nodes}
        assert "start" in node_types
        assert "agent" in node_types
        assert "synthesis" in node_types
        assert "end" in node_types

        # Check all sommeliers are present
        node_ids = {node.id for node in graph.nodes}
        for sommelier_id in SOMMELIER_CONFIG.keys():
            assert sommelier_id in node_ids

    def test_grand_tasting_graph_has_expected_topology(self):
        """Test that grand_tasting mode returns correct graph structure.

        Note: grand_tasting uses the same topology as six_sommeliers
        but with different evaluation behavior.
        """
        from app.services.graph_builder import build_six_sommeliers_topology

        # grand_tasting uses six_sommeliers topology
        graph = build_six_sommeliers_topology()

        assert isinstance(graph, ReactFlowGraph)
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0

    def test_full_techniques_graph_has_dimension_clusters(self):
        """Test that full_techniques mode returns correct topology with dimensions.

        Verifies the graph includes:
        - Start node
        - 8 technique group nodes (cluster nodes)
        - Synthesis node
        - End node
        - Correct edges connecting all nodes
        """
        from app.services.graph_builder import (
            build_full_techniques_topology,
            TECHNIQUE_GROUPS,
        )

        graph = build_full_techniques_topology()

        assert isinstance(graph, ReactFlowGraph)
        assert graph.mode == EvaluationMode.FULL_TECHNIQUES.value

        # Check for required node types
        node_types = {node.type for node in graph.nodes}
        assert "start" in node_types
        assert "technique_group" in node_types
        assert "synthesis" in node_types
        assert "end" in node_types

        # Check all technique groups are present
        node_ids = {node.id for node in graph.nodes}
        for group_id in TECHNIQUE_GROUPS.keys():
            assert group_id in node_ids

    def test_full_techniques_has_correct_node_count(self):
        """Test that full_techniques graph has expected node count.

        Expected: 1 start + 8 technique groups + 1 synthesis + 1 end = 11 nodes
        """
        from app.services.graph_builder import build_full_techniques_topology

        graph = build_full_techniques_topology()

        # 1 start + 8 technique groups + 1 synthesis + 1 end
        expected_node_count = 11
        assert len(graph.nodes) == expected_node_count

    def test_six_sommeliers_has_correct_node_count(self):
        """Test that six_sommeliers graph has expected node count.

        Expected: 1 start + 5 sommeliers + 1 synthesis + 1 end = 8 nodes
        """
        from app.services.graph_builder import build_six_sommeliers_topology

        graph = build_six_sommeliers_topology()

        # 1 start + 5 sommeliers + 1 synthesis (jeanpierre) + 1 end
        expected_node_count = 8
        assert len(graph.nodes) == expected_node_count


# API Endpoint Mode Tests


class TestGraphAPIModeEndpoints:
    """Test mode-related API endpoints."""

    @pytest.mark.asyncio
    async def test_get_mode_endpoint_returns_correct_mode(self):
        """Test that /graph/mode endpoint returns correct mode."""
        from app.api.routes.graph import _get_evaluation, _check_ownership

        mock_evaluation = {
            "_id": "eval123",
            "user_id": "user123",
            "evaluation_mode": "full_techniques",
        }

        with patch("app.api.routes.graph.EvaluationRepository") as mock_repo:
            mock_instance = MagicMock()
            mock_instance.get_by_id = AsyncMock(return_value=mock_evaluation)
            mock_repo.return_value = mock_instance

            evaluation = await _get_evaluation("eval123")
            mode = evaluation.get("evaluation_mode")

            assert mode == "full_techniques"

    @pytest.mark.asyncio
    async def test_graph_endpoint_uses_mode_inference(self):
        """Test that graph endpoints use mode inference correctly."""
        from app.api.routes.graph import _determine_mode

        # Test various evaluation configurations
        test_cases = [
            ({"evaluation_mode": "six_sommeliers"}, EvaluationMode.SIX_SOMMELIERS),
            ({"evaluation_mode": "grand_tasting"}, EvaluationMode.GRAND_TASTING),
            ({"evaluation_mode": "full_techniques"}, EvaluationMode.FULL_TECHNIQUES),
            ({"mode": "six_sommeliers"}, EvaluationMode.SIX_SOMMELIERS),
            ({"mode": "grand_tasting"}, EvaluationMode.GRAND_TASTING),
            ({"mode": "full_techniques"}, EvaluationMode.FULL_TECHNIQUES),
            ({}, EvaluationMode.SIX_SOMMELIERS),
        ]

        for eval_data, expected_mode in test_cases:
            result = _determine_mode(eval_data)
            assert result == expected_mode, f"Failed for evaluation: {eval_data}"


# Backward Compatibility Tests


class TestBackwardCompatibility:
    """Test backward compatibility with legacy evaluation data."""

    def test_old_evaluations_without_evaluation_mode_work(self):
        """Test that old evaluations without evaluation_mode field still work.

        Given: Legacy evaluation documents without evaluation_mode
        When: Mode inference is performed
        Then: They gracefully fall back to using 'mode' field or default
        """
        from app.api.routes.graph import _determine_mode

        legacy_evaluations = [
            {"_id": "old1", "mode": "six_sommeliers"},
            {"_id": "old2", "mode": "grand_tasting"},
            {"_id": "old3", "mode": "full_techniques"},
            {"_id": "old4"},  # No mode field at all
        ]

        expected_modes = [
            EvaluationMode.SIX_SOMMELIERS,
            EvaluationMode.GRAND_TASTING,
            EvaluationMode.FULL_TECHNIQUES,
            EvaluationMode.SIX_SOMMELIERS,  # Default
        ]

        for eval_data, expected in zip(legacy_evaluations, expected_modes):
            result = _determine_mode(eval_data)
            assert result == expected, f"Failed for evaluation: {eval_data}"

    def test_new_evaluations_with_evaluation_mode_take_precedence(self):
        """Test that new evaluation_mode field takes precedence.

        Given: Evaluations with both evaluation_mode and legacy mode
        When: Mode inference is performed
        Then: evaluation_mode is used, legacy mode is ignored
        """
        from app.api.routes.graph import _determine_mode

        evaluations = [
            {
                "evaluation_mode": "full_techniques",
                "mode": "six_sommeliers",  # Should be ignored
            },
            {
                "evaluation_mode": "six_sommeliers",
                "mode": "grand_tasting",  # Should be ignored
            },
        ]

        expected_modes = [
            EvaluationMode.FULL_TECHNIQUES,
            EvaluationMode.SIX_SOMMELIERS,
        ]

        for eval_data, expected in zip(evaluations, expected_modes):
            result = _determine_mode(eval_data)
            assert result == expected, f"Failed for evaluation: {eval_data}"


# Graph Schema Version Tests


class TestGraphSchemaConsistency:
    """Test that all graph modes use correct schema version."""

    def test_all_graph_modes_use_correct_schema_version(self):
        """Test that all graph topologies use the correct schema version."""
        from app.services.graph_builder import (
            build_six_sommeliers_topology,
            build_full_techniques_topology,
        )

        six_sommeliers = build_six_sommeliers_topology()
        full_techniques = build_full_techniques_topology()

        assert six_sommeliers.graph_schema_version == GRAPH_SCHEMA_VERSION
        assert full_techniques.graph_schema_version == GRAPH_SCHEMA_VERSION

    def test_graph_modes_are_valid_strings(self):
        """Test that all graph modes use valid mode string values."""
        from app.services.graph_builder import (
            build_six_sommeliers_topology,
            build_full_techniques_topology,
        )

        six_sommeliers = build_six_sommeliers_topology()
        full_techniques = build_full_techniques_topology()

        valid_modes = {m.value for m in EvaluationMode}

        assert six_sommeliers.mode in valid_modes
        assert full_techniques.mode in valid_modes
