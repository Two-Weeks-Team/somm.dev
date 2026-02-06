"""Contract tests for graph visualization models.

This module contains tests for the graph visualization contracts defined in ADR-002:
- ReactFlowGraph validation (2D)
- Graph3DPayload validation (3D)
- EvaluationMode enum values
- Graph schema versioning
- Failure cases: missing fields, invalid types, version mismatch
"""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.graph import (
    GRAPH_SCHEMA_VERSION,
    EvaluationMode,
    ReactFlowNode,
    ReactFlowEdge,
    ReactFlowGraph,
    Position3D,
    Graph3DNode,
    Graph3DEdge,
    Graph3DMetadata,
    Graph3DPayload,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures" / "graph"


class TestEvaluationMode:
    """Tests for EvaluationMode enum."""

    def test_enum_values(self):
        """Test that EvaluationMode has correct canonical values."""
        assert EvaluationMode.SIX_HATS.value == "six_hats"
        assert EvaluationMode.FULL_TECHNIQUES.value == "full_techniques"

    def test_enum_comparison(self):
        """Test enum value comparison."""
        assert EvaluationMode.SIX_HATS == EvaluationMode("six_hats")
        assert EvaluationMode.FULL_TECHNIQUES == EvaluationMode("full_techniques")

    def test_enum_from_string(self):
        """Test creating enum from string values."""
        mode1 = EvaluationMode("six_hats")
        mode2 = EvaluationMode("full_techniques")
        assert mode1 == EvaluationMode.SIX_HATS
        assert mode2 == EvaluationMode.FULL_TECHNIQUES

    def test_invalid_enum_value(self):
        """Test that invalid enum values raise ValueError."""
        with pytest.raises(ValueError):
            EvaluationMode("invalid_mode")


class TestReactFlowGraph:
    """Tests for ReactFlowGraph 2D models."""

    def test_valid_reactflow_node(self):
        """Test creating a valid ReactFlowNode."""
        node = ReactFlowNode(
            id="node-1",
            type="agent",
            position={"x": 100.0, "y": 200.0},
            data={"label": "Test Node", "status": "complete"},
        )
        assert node.id == "node-1"
        assert node.type == "agent"
        assert node.position == {"x": 100.0, "y": 200.0}
        assert node.data["label"] == "Test Node"

    def test_valid_reactflow_edge(self):
        """Test creating a valid ReactFlowEdge."""
        edge = ReactFlowEdge(
            id="edge-1",
            source="node-1",
            target="node-2",
            animated=True,
            style={"stroke": "#722F37"},
        )
        assert edge.id == "edge-1"
        assert edge.source == "node-1"
        assert edge.target == "node-2"
        assert edge.animated is True
        assert edge.style == {"stroke": "#722F37"}

    def test_reactflow_edge_defaults(self):
        """Test ReactFlowEdge default values."""
        edge = ReactFlowEdge(
            id="edge-1",
            source="node-1",
            target="node-2",
        )
        assert edge.animated is True
        assert edge.style is None

    def test_valid_reactflow_graph(self):
        """Test creating a valid ReactFlowGraph."""
        node = ReactFlowNode(
            id="node-1",
            type="start",
            position={"x": 0.0, "y": 0.0},
            data={"label": "Start"},
        )
        edge = ReactFlowEdge(
            id="edge-1",
            source="node-1",
            target="node-2",
        )
        graph = ReactFlowGraph(
            mode="six_hats",
            nodes=[node],
            edges=[edge],
            description="Test graph",
        )
        assert graph.graph_schema_version == GRAPH_SCHEMA_VERSION
        assert graph.mode == "six_hats"
        assert len(graph.nodes) == 1
        assert len(graph.edges) == 1
        assert graph.description == "Test graph"

    def test_reactflow_graph_from_fixture(self):
        """Test loading valid ReactFlowGraph from golden fixture."""
        fixture_path = FIXTURES_DIR / "valid_reactflow_graph.json"
        with open(fixture_path, encoding="utf-8") as f:
            data = json.load(f)

        graph = ReactFlowGraph(**data)
        assert graph.graph_schema_version == 2
        assert graph.mode == "six_hats"
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 2
        assert graph.description == "Test ReactFlow graph for six_hats mode"

    def test_reactflow_node_missing_id(self):
        """Test ReactFlowNode fails without id."""
        with pytest.raises(ValidationError):
            ReactFlowNode(
                type="agent",
                position={"x": 0.0, "y": 0.0},
                data={},
            )

    def test_reactflow_edge_missing_source(self):
        """Test ReactFlowEdge fails without source."""
        with pytest.raises(ValidationError):
            ReactFlowEdge(
                id="edge-1",
                target="node-2",
            )

    def test_reactflow_invalid_position_type(self):
        """Test validation fails with invalid position type."""
        with pytest.raises(ValidationError):
            ReactFlowNode(
                id="node-1",
                type="agent",
                position="invalid",
                data={},
            )


class TestPosition3D:
    """Tests for Position3D model."""

    def test_valid_position(self):
        """Test creating a valid Position3D."""
        pos = Position3D(x=1.0, y=2.0, z=3.0)
        assert pos.x == 1.0
        assert pos.y == 2.0
        assert pos.z == 3.0

    def test_position_requires_all_coordinates(self):
        """Test that all coordinates are required."""
        with pytest.raises(ValidationError):
            Position3D(x=1.0, y=2.0)


class TestGraph3DNode:
    """Tests for Graph3DNode model."""

    def test_valid_node(self):
        """Test creating a valid Graph3DNode."""
        pos = Position3D(x=1.0, y=2.0, z=3.0)
        node = Graph3DNode(
            node_id="node-1",
            node_type="agent",
            label="Test Node",
            position=pos,
            step_number=0,
        )
        assert node.node_id == "node-1"
        assert node.step_number == 0
        assert node.color is None

    def test_node_with_optional_fields(self):
        """Test Graph3DNode with all optional fields."""
        pos = Position3D(x=1.0, y=2.0, z=3.0)
        node = Graph3DNode(
            node_id="node-1",
            node_type="technique",
            label="Technique Node",
            position=pos,
            color="#722F37",
            step_number=1,
            hat_type="white",
            technique_id="tech_001",
            category="quality",
            item_count=5,
        )
        assert node.color == "#722F37"
        assert node.hat_type == "white"
        assert node.technique_id == "tech_001"
        assert node.item_count == 5


class TestGraph3DEdge:
    """Tests for Graph3DEdge model."""

    def test_valid_edge(self):
        """Test creating a valid Graph3DEdge."""
        edge = Graph3DEdge(
            edge_id="edge-1",
            source="node-1",
            target="node-2",
            edge_type="flow",
            step_number=1,
        )
        assert edge.edge_id == "edge-1"
        assert edge.width == 1.0
        assert edge.bundle_id is None

    def test_edge_with_bundled_path(self):
        """Test Graph3DEdge with bundled path."""
        path = [
            Position3D(x=0.0, y=0.0, z=0.0),
            Position3D(x=1.0, y=1.0, z=1.0),
        ]
        edge = Graph3DEdge(
            edge_id="edge-1",
            source="node-1",
            target="node-2",
            edge_type="parallel",
            step_number=1,
            bundle_id="bundle-1",
            bundled_path=path,
            dasharray="5,5",
        )
        assert edge.bundle_id == "bundle-1"
        assert len(edge.bundled_path) == 2
        assert edge.dasharray == "5,5"


class TestGraph3DMetadata:
    """Tests for Graph3DMetadata model."""

    def test_valid_metadata(self):
        """Test creating valid Graph3DMetadata."""
        metadata = Graph3DMetadata(
            x_range=(0.0, 100.0),
            y_range=(0.0, 50.0),
            z_range=(0.0, 20.0),
            total_nodes=10,
            total_edges=15,
            total_steps=5,
            max_step_number=4,
            generated_at="2026-02-06T10:00:00Z",
        )
        assert metadata.graph_schema_version == GRAPH_SCHEMA_VERSION
        assert metadata.total_nodes == 10
        assert metadata.x_range == (0.0, 100.0)


class TestGraph3DPayload:
    """Tests for Graph3DPayload model."""

    def test_valid_payload(self):
        """Test creating a valid Graph3DPayload."""
        node = Graph3DNode(
            node_id="node-1",
            node_type="start",
            label="Start",
            position=Position3D(x=0.0, y=0.0, z=0.0),
            step_number=0,
        )
        edge = Graph3DEdge(
            edge_id="edge-1",
            source="node-1",
            target="node-2",
            edge_type="flow",
            step_number=1,
        )
        metadata = Graph3DMetadata(
            x_range=(0.0, 100.0),
            y_range=(0.0, 50.0),
            z_range=(0.0, 20.0),
            total_nodes=1,
            total_edges=1,
            total_steps=2,
            max_step_number=1,
            generated_at="2026-02-06T10:00:00Z",
        )

        payload = Graph3DPayload(
            evaluation_id="eval_123",
            mode="six_hats",
            nodes=[node],
            edges=[edge],
            metadata=metadata,
        )
        assert payload.graph_schema_version == GRAPH_SCHEMA_VERSION
        assert payload.evaluation_id == "eval_123"
        assert payload.mode == "six_hats"

    def test_payload_from_fixture(self):
        """Test loading valid Graph3DPayload from golden fixture."""
        fixture_path = FIXTURES_DIR / "valid_graph_3d.json"
        with open(fixture_path, encoding="utf-8") as f:
            data = json.load(f)

        payload = Graph3DPayload(**data)
        assert payload.graph_schema_version == 2
        assert payload.evaluation_id == "eval_test_123"
        assert payload.mode == "full_techniques"
        assert len(payload.nodes) == 3
        assert len(payload.edges) == 2
        assert payload.metadata.total_nodes == 3

    def test_payload_with_excluded_techniques(self):
        """Test Graph3DPayload with excluded techniques."""
        node = Graph3DNode(
            node_id="node-1",
            node_type="start",
            label="Start",
            position=Position3D(x=0.0, y=0.0, z=0.0),
            step_number=0,
        )
        edge = Graph3DEdge(
            edge_id="edge-1",
            source="node-1",
            target="node-2",
            edge_type="flow",
            step_number=1,
        )
        metadata = Graph3DMetadata(
            x_range=(0.0, 100.0),
            y_range=(0.0, 50.0),
            z_range=(0.0, 20.0),
            total_nodes=1,
            total_edges=1,
            total_steps=2,
            max_step_number=1,
            generated_at="2026-02-06T10:00:00Z",
        )

        payload = Graph3DPayload(
            evaluation_id="eval_123",
            mode="full_techniques",
            nodes=[node],
            edges=[edge],
            excluded_techniques=[
                {"technique_id": "tech_001", "reason": "not_applicable"}
            ],
            metadata=metadata,
        )
        assert payload.excluded_techniques is not None
        assert len(payload.excluded_techniques) == 1

    def test_payload_missing_evaluation_id(self):
        """Test Graph3DPayload fails without evaluation_id."""
        node = Graph3DNode(
            node_id="node-1",
            node_type="start",
            label="Start",
            position=Position3D(x=0.0, y=0.0, z=0.0),
            step_number=0,
        )
        metadata = Graph3DMetadata(
            x_range=(0.0, 100.0),
            y_range=(0.0, 50.0),
            z_range=(0.0, 20.0),
            total_nodes=1,
            total_edges=0,
            total_steps=1,
            max_step_number=0,
            generated_at="2026-02-06T10:00:00Z",
        )

        with pytest.raises(ValidationError):
            Graph3DPayload(
                mode="six_hats",
                nodes=[node],
                edges=[],
                metadata=metadata,
            )


class TestGraphSchemaVersion:
    """Tests for graph schema versioning."""

    def test_constant_value(self):
        """Test GRAPH_SCHEMA_VERSION constant."""
        assert GRAPH_SCHEMA_VERSION == 2

    def test_reactflow_default_version(self):
        """Test ReactFlowGraph has correct default version."""
        node = ReactFlowNode(
            id="node-1",
            type="start",
            position={"x": 0.0, "y": 0.0},
            data={},
        )
        graph = ReactFlowGraph(
            mode="six_hats",
            nodes=[node],
            edges=[],
        )
        assert graph.graph_schema_version == 2

    def test_3d_payload_default_version(self):
        """Test Graph3DPayload has correct default version."""
        node = Graph3DNode(
            node_id="node-1",
            node_type="start",
            label="Start",
            position=Position3D(x=0.0, y=0.0, z=0.0),
            step_number=0,
        )
        edge = Graph3DEdge(
            edge_id="edge-1",
            source="node-1",
            target="node-2",
            edge_type="flow",
            step_number=1,
        )
        metadata = Graph3DMetadata(
            x_range=(0.0, 100.0),
            y_range=(0.0, 50.0),
            z_range=(0.0, 20.0),
            total_nodes=1,
            total_edges=1,
            total_steps=2,
            max_step_number=1,
            generated_at="2026-02-06T10:00:00Z",
        )

        payload = Graph3DPayload(
            evaluation_id="eval_123",
            mode="six_hats",
            nodes=[node],
            edges=[edge],
            metadata=metadata,
        )
        assert payload.graph_schema_version == 2

    def test_explicit_version_override(self):
        """Test that explicit version values are accepted."""
        node = ReactFlowNode(
            id="node-1",
            type="start",
            position={"x": 0.0, "y": 0.0},
            data={},
        )
        graph = ReactFlowGraph(
            graph_schema_version=3,
            mode="six_hats",
            nodes=[node],
            edges=[],
        )
        assert graph.graph_schema_version == 3

    def test_version_mismatch_payload_vs_metadata(self):
        """Test that mismatched versions between payload and metadata raise error."""
        node = Graph3DNode(
            node_id="node-1",
            node_type="start",
            label="Start",
            position=Position3D(x=0.0, y=0.0, z=0.0),
            step_number=0,
        )
        metadata = Graph3DMetadata(
            x_range=(0.0, 100.0),
            y_range=(0.0, 50.0),
            z_range=(0.0, 20.0),
            total_nodes=1,
            total_edges=0,
            total_steps=1,
            max_step_number=0,
            graph_schema_version=2,
            generated_at="2026-02-06T10:00:00Z",
        )
        with pytest.raises(ValidationError) as exc_info:
            Graph3DPayload(
                graph_schema_version=3,
                evaluation_id="eval_123",
                mode="six_hats",
                nodes=[node],
                edges=[],
                metadata=metadata,
            )
        assert "graph_schema_version" in str(exc_info.value)


class TestInvalidModeValidation:
    """Tests for invalid mode string rejection."""

    def test_reactflow_graph_invalid_mode(self):
        """Test ReactFlowGraph fails with invalid mode."""
        node = ReactFlowNode(
            id="node-1",
            type="start",
            position={"x": 0.0, "y": 0.0},
            data={},
        )
        with pytest.raises(ValidationError) as exc_info:
            ReactFlowGraph(
                mode="invalid_mode",
                nodes=[node],
                edges=[],
            )
        assert "mode" in str(exc_info.value).lower()

    def test_graph_3d_payload_accepts_any_mode(self):
        """Test Graph3DPayload accepts any mode string (criteria-based)."""
        node = Graph3DNode(
            node_id="node-1",
            node_type="start",
            label="Start",
            position=Position3D(x=0.0, y=0.0, z=0.0),
            step_number=0,
        )
        metadata = Graph3DMetadata(
            x_range=(0.0, 100.0),
            y_range=(0.0, 50.0),
            z_range=(0.0, 20.0),
            total_nodes=1,
            total_edges=0,
            total_steps=1,
            max_step_number=0,
            generated_at="2026-02-06T10:00:00Z",
        )
        payload = Graph3DPayload(
            evaluation_id="eval_123",
            mode="hackathon",
            nodes=[node],
            edges=[],
            metadata=metadata,
        )
        assert payload.mode == "hackathon"
