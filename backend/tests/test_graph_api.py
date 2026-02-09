"""Test suite for Graph Visualization API v1.

Tests cover:
- Authentication and authorization
- Graph topology endpoints
- Timeline endpoint
- Mode endpoint
- Response schema validation
- Snapshot stability
"""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock

from fastapi.testclient import TestClient

from app.main import app
from app.graph.graph_factory import EvaluationMode
from app.models.graph import (
    GRAPH_SCHEMA_VERSION,
    ReactFlowGraph,
    TraceEvent,
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
def mock_evaluation_six_sommeliers():
    """Mock evaluation document for six_sommeliers mode."""
    return {
        "_id": "eval123",
        "user_id": "user123",
        "repo_context": {"repo_url": "https://github.com/test/repo"},
        "criteria": "basic",
        "status": "completed",
        "mode": "six_sommeliers",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def mock_evaluation_full_techniques():
    """Mock evaluation document for full_techniques mode."""
    return {
        "_id": "eval456",
        "user_id": "user123",
        "repo_context": {"repo_url": "https://github.com/test/repo"},
        "criteria": "hackathon",
        "status": "completed",
        "mode": "full_techniques",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def auth_headers(mock_token):
    """Authorization headers with Bearer token."""
    return {"Authorization": f"Bearer {mock_token}"}


# Authentication Tests


class TestAuthentication:
    """Test authentication requirements for graph endpoints.

    Note: graph, timeline, and mode endpoints use get_optional_user
    (not get_current_user) to support public demo evaluations.
    For non-public evaluations, _check_ownership raises CorkedError
    when user is None.
    """

    def test_check_ownership_requires_auth_for_non_public(self):
        """Test that _check_ownership raises CorkedError when user is None for non-public evaluations."""
        from app.api.routes.graph import _check_ownership

        evaluation = {"user_id": "some_user"}
        with pytest.raises(CorkedError) as exc_info:
            _check_ownership(evaluation, None, "non_public_eval_id")
        assert "Authentication required" in str(exc_info.value.detail)

    def test_check_ownership_allows_public_demo_without_auth(self):
        """Test that public demo evaluations can be accessed without authentication."""
        from app.api.routes.graph import _check_ownership, PUBLIC_DEMO_EVALUATIONS

        evaluation = {"user_id": "some_user"}
        demo_id = next(iter(PUBLIC_DEMO_EVALUATIONS))
        _check_ownership(evaluation, None, demo_id)

    def test_check_ownership_allows_authenticated_owner(self):
        """Test that authenticated owner can access their evaluation."""
        from app.api.routes.graph import _check_ownership

        user = MagicMock(id="user123")
        evaluation = {"user_id": "user123"}
        _check_ownership(evaluation, user, "any_eval_id")


# Authorization Tests


class TestAuthorization:
    """Test authorization checks for graph endpoints."""

    def test_wrong_user_returns_403(self):
        """Test that accessing another user's evaluation returns 403."""
        from app.api.routes.graph import _check_ownership

        evaluation = {"user_id": "different_user"}
        user = MagicMock(id="current_user")

        with pytest.raises(CorkedError) as exc_info:
            _check_ownership(evaluation, user, "eval123")

        assert "Access denied" in str(exc_info.value.detail)

    def test_unauthenticated_non_public_returns_auth_error(self):
        """Test that unauthenticated access to non-public evaluation raises CorkedError."""
        from app.api.routes.graph import _check_ownership

        evaluation = {"user_id": "some_user"}

        with pytest.raises(CorkedError) as exc_info:
            _check_ownership(evaluation, None, "non_public_eval")

        assert "Authentication required" in str(exc_info.value.detail)


# 404 Not Found Tests


class TestNotFound:
    """Test 404 responses for non-existent evaluations."""

    @pytest.mark.asyncio
    async def test_get_graph_unknown_evaluation_raises_empty_cellar(self):
        """Test that unknown evaluation raises EmptyCellarError (404)."""
        from app.api.routes.graph import _get_evaluation

        with patch("app.api.routes.graph.EvaluationRepository") as mock_repo:
            mock_instance = MagicMock()
            mock_instance.get_by_id = AsyncMock(return_value=None)
            mock_repo.return_value = mock_instance

            result = await _get_evaluation("unknown_eval")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_timeline_unknown_evaluation_raises_empty_cellar(self):
        """Test that timeline raises EmptyCellarError for unknown evaluation."""
        from app.api.routes.graph import _get_evaluation

        with patch("app.api.routes.graph.EvaluationRepository") as mock_repo:
            mock_instance = MagicMock()
            mock_instance.get_by_id = AsyncMock(return_value=None)
            mock_repo.return_value = mock_instance

            result = await _get_evaluation("unknown_eval")
            assert result is None

    @pytest.mark.asyncio
    async def test_get_mode_unknown_evaluation_raises_empty_cellar(self):
        """Test that mode raises EmptyCellarError for unknown evaluation."""
        from app.api.routes.graph import _get_evaluation

        with patch("app.api.routes.graph.EvaluationRepository") as mock_repo:
            mock_instance = MagicMock()
            mock_instance.get_by_id = AsyncMock(return_value=None)
            mock_repo.return_value = mock_instance

            result = await _get_evaluation("unknown_eval")
            assert result is None


# Schema Validation Tests


class TestSchemaValidation:
    """Test response schema validation."""

    def test_react_flow_graph_model_has_required_fields(self):
        """Test that ReactFlowGraph model has all required fields."""
        graph = ReactFlowGraph(
            mode=EvaluationMode.SIX_SOMMELIERS.value,
            nodes=[],
            edges=[],
        )

        assert graph.graph_schema_version == GRAPH_SCHEMA_VERSION
        assert graph.mode == EvaluationMode.SIX_SOMMELIERS.value
        assert isinstance(graph.nodes, list)
        assert isinstance(graph.edges, list)

    def test_trace_event_model_has_required_fields(self):
        """Test that TraceEvent model has all required fields."""
        event = TraceEvent(
            step=1,
            timestamp="2025-01-15T10:00:00Z",
            agent="marcel",
            technique_id="test-technique",
            action="analyze",
        )

        assert event.step == 1
        assert event.timestamp == "2025-01-15T10:00:00Z"
        assert event.agent == "marcel"
        assert event.technique_id == "test-technique"
        assert event.action == "analyze"

    def test_mode_response_model_has_required_fields(self):
        """Test that ModeResponse model has all required fields."""
        response = ModeResponse(
            mode=EvaluationMode.SIX_SOMMELIERS.value,
            evaluation_id="eval123",
        )

        assert response.mode == EvaluationMode.SIX_SOMMELIERS.value
        assert response.evaluation_id == "eval123"


# Graph Builder Service Tests


class TestGraphBuilder:
    """Test graph builder service functions."""

    def test_build_six_sommeliers_topology_returns_valid_graph(self):
        """Test that six_sommeliers topology builder returns valid ReactFlowGraph."""
        from app.services.graph_builder import build_six_sommeliers_topology

        graph = build_six_sommeliers_topology()

        assert isinstance(graph, ReactFlowGraph)
        assert graph.mode == EvaluationMode.SIX_SOMMELIERS.value
        assert graph.graph_schema_version == GRAPH_SCHEMA_VERSION
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0

        # Check for required node types
        node_types = {node.type for node in graph.nodes}
        assert "start" in node_types
        assert "agent" in node_types or "synthesis" in node_types
        assert "end" in node_types

    def test_build_full_techniques_topology_returns_valid_graph(self):
        """Test that full_techniques topology builder returns valid ReactFlowGraph."""
        from app.services.graph_builder import build_full_techniques_topology

        graph = build_full_techniques_topology()

        assert isinstance(graph, ReactFlowGraph)
        assert graph.mode == EvaluationMode.FULL_TECHNIQUES.value
        assert graph.graph_schema_version == GRAPH_SCHEMA_VERSION
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0

        # Check for required node types
        node_types = {node.type for node in graph.nodes}
        assert "start" in node_types
        assert "technique_group" in node_types or "synthesis" in node_types
        assert "end" in node_types

    def test_six_sommeliers_has_expected_sommelier_nodes(self):
        """Test that six_sommeliers topology includes all expected sommelier nodes."""
        from app.services.graph_builder import (
            build_six_sommeliers_topology,
            SOMMELIER_CONFIG,
        )

        graph = build_six_sommeliers_topology()
        node_ids = {node.id for node in graph.nodes}

        # Check all sommeliers are present
        for sommelier_id in SOMMELIER_CONFIG.keys():
            assert sommelier_id in node_ids, f"Missing sommelier: {sommelier_id}"

    def test_full_techniques_has_expected_technique_groups(self):
        """Test that full_techniques topology includes all expected technique groups."""
        from app.services.graph_builder import (
            build_full_techniques_topology,
            TECHNIQUE_GROUPS,
        )

        graph = build_full_techniques_topology()
        node_ids = {node.id for node in graph.nodes}

        # Check all technique groups are present
        for group_id in TECHNIQUE_GROUPS.keys():
            assert group_id in node_ids, f"Missing technique group: {group_id}"


# Snapshot Stability Tests


class TestSnapshotStability:
    """Test that topology structure is consistent across calls."""

    def test_six_sommeliers_topology_structure_is_stable(self):
        """Test that six_sommeliers topology produces consistent structure."""
        from app.services.graph_builder import build_six_sommeliers_topology

        # Build multiple graphs
        graphs = [build_six_sommeliers_topology() for _ in range(3)]

        # All graphs should have same structure
        first = graphs[0]
        for graph in graphs[1:]:
            assert graph.mode == first.mode
            assert len(graph.nodes) == len(first.nodes)
            assert len(graph.edges) == len(first.edges)
            # Check node IDs are consistent
            assert sorted([n.id for n in graph.nodes]) == sorted(
                [n.id for n in first.nodes]
            )

    def test_full_techniques_topology_structure_is_stable(self):
        """Test that full_techniques topology produces consistent structure."""
        from app.services.graph_builder import build_full_techniques_topology

        # Build multiple graphs
        graphs = [build_full_techniques_topology() for _ in range(3)]

        # All graphs should have same structure
        first = graphs[0]
        for graph in graphs[1:]:
            assert graph.mode == first.mode
            assert len(graph.nodes) == len(first.nodes)
            assert len(graph.edges) == len(first.edges)
            # Check node IDs are consistent
            assert sorted([n.id for n in graph.nodes]) == sorted(
                [n.id for n in first.nodes]
            )


# Mode Detection Tests


class TestModeDetection:
    """Test evaluation mode detection."""

    def test_determine_mode_returns_six_sommeliers_for_six_sommeliers_mode(self):
        """Test that _determine_mode returns SIX_SOMMELIERS for six_sommeliers mode."""
        from app.api.routes.graph import _determine_mode

        evaluation = {"mode": "six_sommeliers"}
        mode = _determine_mode(evaluation)

        assert mode == EvaluationMode.SIX_SOMMELIERS

    def test_determine_mode_returns_six_sommeliers_for_evaluation_mode_field(self):
        """Test that _determine_mode checks evaluation_mode field first."""
        from app.api.routes.graph import _determine_mode

        evaluation = {"evaluation_mode": "six_sommeliers", "mode": "full_techniques"}
        mode = _determine_mode(evaluation)

        assert mode == EvaluationMode.SIX_SOMMELIERS

    def test_determine_mode_returns_full_techniques_for_full_techniques_mode(self):
        """Test that _determine_mode returns FULL_TECHNIQUES for full_techniques mode."""
        from app.api.routes.graph import _determine_mode

        evaluation = {"mode": "full_techniques"}
        mode = _determine_mode(evaluation)

        assert mode == EvaluationMode.FULL_TECHNIQUES

    def test_determine_mode_defaults_to_six_sommeliers(self):
        """Test that _determine_mode defaults to SIX_SOMMELIERS when mode not specified."""
        from app.api.routes.graph import _determine_mode

        evaluation = {}
        mode = _determine_mode(evaluation)

        assert mode == EvaluationMode.SIX_SOMMELIERS
