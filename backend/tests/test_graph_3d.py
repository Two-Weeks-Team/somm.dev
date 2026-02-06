"""Tests for 3D graph builder functionality.

This module tests:
- Deterministic layout generation
- Bounds validation
- Step ordering
- Missing trace handling
"""

import math

import pytest

from app.models.graph import (
    Graph3DPayload,
    Graph3DNode,
    Graph3DEdge,
    Position3D,
)
from app.services.graph_builder_3d import (
    build_3d_graph,
    assign_step_numbers,
    LAYER_START,
    LAYER_RAG,
    LAYER_AGENTS,
    LAYER_SYNTHESIS,
    LAYER_END,
)


class TestDeterminism:
    """Tests that graph generation is deterministic."""

    def test_same_input_same_output(self):
        """Same inputs must produce identical coordinates."""
        graph1 = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
            methodology_trace=None,
        )
        graph2 = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
            methodology_trace=None,
        )

        assert len(graph1.nodes) == len(graph2.nodes)
        assert len(graph1.edges) == len(graph2.edges)

        for n1, n2 in zip(graph1.nodes, graph2.nodes):
            assert n1.node_id == n2.node_id
            assert n1.position.x == n2.position.x
            assert n1.position.y == n2.position.y
            assert n1.position.z == n2.position.z

    def test_same_input_with_trace(self):
        """Same inputs with trace must produce identical results."""
        trace = [
            {"agent": "marcel", "step": 1},
            {"agent": "isabella", "step": 2},
        ]

        graph1 = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
            methodology_trace=trace,
        )
        graph2 = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
            methodology_trace=trace,
        )

        for n1, n2 in zip(graph1.nodes, graph2.nodes):
            assert n1.node_id == n2.node_id
            assert n1.step_number == n2.step_number


class TestBoundsValidation:
    """Tests for valid bounds and no NaN/inf values."""

    def test_no_nan_in_positions(self):
        """Positions must not contain NaN values."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
        )

        for node in graph.nodes:
            assert not math.isnan(node.position.x)
            assert not math.isnan(node.position.y)
            assert not math.isnan(node.position.z)

    def test_no_inf_in_positions(self):
        """Positions must not contain infinity values."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
        )

        for node in graph.nodes:
            assert not math.isinf(node.position.x)
            assert not math.isinf(node.position.y)
            assert not math.isinf(node.position.z)

    def test_layer_ranges_correct(self):
        """Z coordinates must match expected layer ranges."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
            include_rag=True,
        )

        start_node = next(n for n in graph.nodes if n.node_id == "start")
        rag_node = next(n for n in graph.nodes if n.node_id == "rag_enrich")
        synthesis_node = next(n for n in graph.nodes if n.node_id == "synthesis")
        end_node = next(n for n in graph.nodes if n.node_id == "end")

        assert start_node.position.z == LAYER_START
        assert rag_node.position.z == LAYER_RAG
        assert synthesis_node.position.z == LAYER_SYNTHESIS
        assert end_node.position.z == LAYER_END

    def test_metadata_ranges_match_nodes(self):
        """Metadata ranges must match actual node positions."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
        )

        x_coords = [n.position.x for n in graph.nodes]
        y_coords = [n.position.y for n in graph.nodes]
        z_coords = [n.position.z for n in graph.nodes]

        assert graph.metadata.x_range == (min(x_coords), max(x_coords))
        assert graph.metadata.y_range == (min(y_coords), max(y_coords))
        assert graph.metadata.z_range == (min(z_coords), max(z_coords))


class TestStepOrdering:
    """Tests for monotonically increasing step numbers."""

    def test_step_numbers_increase_monotonically(self):
        """Step numbers must be monotonically increasing."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
        )

        step_numbers = [n.step_number for n in graph.nodes]
        for i in range(len(step_numbers) - 1):
            assert step_numbers[i] <= step_numbers[i + 1]

    def test_start_node_is_step_zero(self):
        """Start node must have step_number 0."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
        )

        start_node = next(n for n in graph.nodes if n.node_id == "start")
        assert start_node.step_number == 0

    def test_end_node_is_final_step(self):
        """End node must have the highest step number."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
        )

        max_step = max(n.step_number for n in graph.nodes)
        end_node = next(n for n in graph.nodes if n.node_id == "end")
        assert end_node.step_number == max_step

    def test_step_numbers_from_trace(self):
        """Step numbers must follow trace ordering."""
        trace = [
            {"agent": "marcel"},
            {"agent": "isabella"},
            {"agent": "heinrich"},
        ]

        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
            methodology_trace=trace,
        )

        marcel = next(n for n in graph.nodes if n.node_id == "marcel")
        isabella = next(n for n in graph.nodes if n.node_id == "isabella")
        heinrich = next(n for n in graph.nodes if n.node_id == "heinrich")

        assert marcel.step_number == 1
        assert isabella.step_number == 2
        assert heinrich.step_number == 3


class TestMissingTrace:
    """Tests for missing methodology_trace handling."""

    def test_none_trace_returns_valid_payload(self):
        """None trace must return valid payload."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
            methodology_trace=None,
        )

        assert graph is not None
        assert len(graph.nodes) > 0
        assert len(graph.edges) > 0
        assert graph.metadata.total_nodes > 0

    def test_empty_list_trace_returns_valid_payload(self):
        """Empty list trace must return valid payload."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
            methodology_trace=[],
        )

        assert graph is not None
        assert len(graph.nodes) > 0
        assert graph.metadata.total_steps >= 0

    def test_default_step_ordering_without_trace(self):
        """Without trace, use default sequential ordering."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
            methodology_trace=None,
        )

        steps = sorted(set(n.step_number for n in graph.nodes))
        for i in range(len(steps) - 1):
            assert steps[i + 1] - steps[i] <= 1


class TestAssignStepNumbers:
    """Tests for assign_step_numbers function."""

    def test_assign_step_numbers_with_trace(self):
        """Step numbers assigned correctly from trace."""
        nodes = [
            Graph3DNode(
                node_id="start",
                node_type="start",
                label="Start",
                position=Position3D(x=0, y=0, z=0),
            ),
            Graph3DNode(
                node_id="marcel",
                node_type="agent",
                label="Marcel",
                position=Position3D(x=0, y=0, z=200),
                hat_type="marcel",
            ),
            Graph3DNode(
                node_id="end",
                node_type="end",
                label="End",
                position=Position3D(x=0, y=0, z=400),
            ),
        ]
        edges = []
        trace = [{"agent": "marcel"}]

        assign_step_numbers(nodes, edges, trace)

        assert nodes[0].step_number == 0
        assert nodes[1].step_number == 1
        assert nodes[2].step_number == 3

    def test_assign_step_numbers_with_none_trace(self):
        """None trace leaves default step numbers."""
        nodes = [
            Graph3DNode(
                node_id="start",
                node_type="start",
                label="Start",
                position=Position3D(x=0, y=0, z=0),
                step_number=0,
            ),
        ]
        edges = []

        assign_step_numbers(nodes, edges, None)

        assert nodes[0].step_number == 0


class TestPayloadStructure:
    """Tests for Graph3DPayload structure and metadata."""

    def test_payload_has_required_fields(self):
        """Payload must have all required fields."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="hackathon",
        )

        assert graph.evaluation_id == "eval_123"
        assert graph.mode == "hackathon"
        assert graph.graph_schema_version == 2
        assert isinstance(graph.nodes, list)
        assert isinstance(graph.edges, list)
        assert graph.metadata is not None

    def test_metadata_has_required_fields(self):
        """Metadata must have all required fields."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
        )

        assert graph.metadata.total_nodes == len(graph.nodes)
        assert graph.metadata.total_edges == len(graph.edges)
        assert graph.metadata.x_range is not None
        assert graph.metadata.y_range is not None
        assert graph.metadata.z_range is not None
        assert graph.metadata.generated_at is not None

    def test_agent_nodes_have_correct_type(self):
        """Agent nodes must have node_type='agent'."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
        )

        agents = [
            n
            for n in graph.nodes
            if n.node_id in ["marcel", "isabella", "heinrich", "sofia", "laurent"]
        ]
        for agent in agents:
            assert agent.node_type == "agent"
            assert agent.color is not None

    def test_technique_nodes_under_agents(self):
        """Technique nodes must be children of agents."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
            include_techniques=True,
        )

        techniques = [n for n in graph.nodes if n.node_type == "technique"]
        for tech in techniques:
            assert tech.technique_id is not None
            parent_id = tech.node_id.split("_")[0]
            assert parent_id in ["marcel", "isabella", "heinrich", "sofia", "laurent"]


class TestEdgeStructure:
    """Tests for graph edge structure."""

    def test_edges_connect_valid_nodes(self):
        """All edges must connect existing nodes."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
        )

        node_ids = {n.node_id for n in graph.nodes}
        for edge in graph.edges:
            assert edge.source in node_ids
            assert edge.target in node_ids

    def test_edge_types_are_valid(self):
        """Edge types must be valid."""
        valid_types = {"flow", "parallel", "data", "excluded"}
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
        )

        for edge in graph.edges:
            assert edge.edge_type in valid_types

    def test_start_to_rag_edge_exists(self):
        """Start to RAG edge must exist when RAG is included."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
            include_rag=True,
        )

        start_to_rag = [
            e for e in graph.edges if e.source == "start" and e.target == "rag_enrich"
        ]
        assert len(start_to_rag) == 1

    def test_agents_connect_to_synthesis(self):
        """All agents must connect to synthesis node."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
        )

        agent_ids = {"marcel", "isabella", "heinrich", "sofia", "laurent"}
        for agent_id in agent_ids:
            agent_to_synth = [
                e
                for e in graph.edges
                if e.source == agent_id and e.target == "synthesis"
            ]
            assert len(agent_to_synth) >= 1


class TestConfiguration:
    """Tests for builder configuration options."""

    def test_without_rag(self):
        """Graph without RAG must skip RAG layer."""
        graph = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
            include_rag=False,
        )

        rag_nodes = [n for n in graph.nodes if n.node_id == "rag_enrich"]
        assert len(rag_nodes) == 0

    def test_without_techniques(self):
        """Graph without techniques must have fewer nodes."""
        graph_with = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
            include_techniques=True,
        )
        graph_without = build_3d_graph(
            evaluation_id="eval_123",
            mode="basic",
            include_techniques=False,
        )

        assert len(graph_without.nodes) < len(graph_with.nodes)

    def test_different_modes(self):
        """Graph must work with different modes."""
        modes = ["basic", "hackathon", "academic", "custom"]
        for mode in modes:
            graph = build_3d_graph(
                evaluation_id="eval_123",
                mode=mode,
            )
            assert graph.mode == mode
            assert len(graph.nodes) > 0
