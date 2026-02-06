"""Phase G4 Advanced 3D Graph Tests.

Tests for:
- Position3D vector operations
- FDEB edge bundling algorithm
- Graph3DBuilder class
- Excluded technique visualization
"""

import math
import time

from app.models.graph import (
    Graph3DPayload,
    Position3D,
    ExcludedVisualization,
)
from app.services.graph_builder_3d import (
    Graph3DBuilder,
    build_sample_3d_graph,
    compute_fdeb_bundling,
    generate_step_number,
    AGENT_LAYER,
    TECHNIQUE_LAYER,
    ITEM_LAYER,
    SYNTHESIS_LAYER,
    LAYER_Z,
    NUMERICAL_STABILITY_EPSILON,
)


class TestPosition3DVectorOps:
    def test_position_creation(self):
        pos = Position3D(x=1.0, y=2.0, z=3.0)
        assert pos.x == 1.0
        assert pos.y == 2.0
        assert pos.z == 3.0

    def test_position_addition(self):
        p1 = Position3D(x=1, y=2, z=3)
        p2 = Position3D(x=4, y=5, z=6)
        result = p1 + p2
        assert result.x == 5
        assert result.y == 7
        assert result.z == 9

    def test_position_subtraction(self):
        p1 = Position3D(x=5, y=7, z=9)
        p2 = Position3D(x=1, y=2, z=3)
        result = p1 - p2
        assert result.x == 4
        assert result.y == 5
        assert result.z == 6

    def test_position_scalar_multiplication(self):
        p = Position3D(x=1, y=2, z=3)
        result = p * 2
        assert result.x == 2
        assert result.y == 4
        assert result.z == 6

    def test_position_scalar_division(self):
        p = Position3D(x=10, y=20, z=30)
        result = p / 2
        assert result.x == 5
        assert result.y == 10
        assert result.z == 15

    def test_position_division_by_zero(self):
        p = Position3D(x=10, y=20, z=30)
        result = p / 0
        assert result.x == 0
        assert result.y == 0
        assert result.z == 0

    def test_dot_product(self):
        p1 = Position3D(x=1, y=2, z=3)
        p2 = Position3D(x=4, y=5, z=6)
        result = p1.dot(p2)
        assert result == 32

    def test_magnitude(self):
        p = Position3D(x=3, y=4, z=0)
        assert p.magnitude() == 5.0

    def test_normalize(self):
        p = Position3D(x=3, y=4, z=0)
        normalized = p.normalize()
        assert abs(normalized.magnitude() - 1.0) < 1e-10
        assert abs(normalized.x - 0.6) < 1e-10
        assert abs(normalized.y - 0.8) < 1e-10

    def test_normalize_zero_vector(self):
        p = Position3D(x=0, y=0, z=0)
        result = p.normalize()
        assert result.x == 0
        assert result.y == 0
        assert result.z == 0


class TestStepNumbering:
    def test_generate_step_number_basic(self):
        assert generate_step_number("1", 0) == "1.1"
        assert generate_step_number("1", 1) == "1.2"
        assert generate_step_number("2", 0) == "2.1"

    def test_generate_step_number_nested(self):
        assert generate_step_number("1.1", 0) == "1.1.1"
        assert generate_step_number("1.1", 1) == "1.1.2"
        assert generate_step_number("1.1.1", 0) == "1.1.1.1"

    def test_generate_step_number_various(self):
        assert generate_step_number("2.3", 4) == "2.3.5"


class TestLayerConstants:
    def test_layer_z_values(self):
        assert LAYER_Z[1] == 0
        assert LAYER_Z[2] == 200
        assert LAYER_Z[3] == 250
        assert LAYER_Z[4] == 300
        assert LAYER_Z[5] == 400

    def test_layer_constants(self):
        assert AGENT_LAYER == 2
        assert TECHNIQUE_LAYER == 3
        assert ITEM_LAYER == 4
        assert SYNTHESIS_LAYER == 5

    def test_numerical_stability_epsilon(self):
        assert NUMERICAL_STABILITY_EPSILON == 1e-10


class TestExcludedVisualization:
    def test_excluded_visualization_defaults(self):
        ev = ExcludedVisualization(technique_id="test_123", reason="Test reason")
        assert ev.technique_id == "test_123"
        assert ev.reason == "Test reason"
        assert ev.node_style["opacity"] == 0.5
        assert ev.node_style["dasharray"] == "5,5"
        assert ev.edge_style["color"] == "#ff0000"
        assert ev.edge_style["dasharray"] == "3,3"

    def test_excluded_visualization_custom_styles(self):
        ev = ExcludedVisualization(
            technique_id="test",
            reason="Custom",
            node_style={"opacity": 0.3},
            edge_style={"color": "#blue"},
        )
        assert ev.node_style["opacity"] == 0.3
        assert ev.edge_style["color"] == "#blue"


class TestGraph3DBuilder:
    def test_builder_initialization(self):
        builder = Graph3DBuilder(seed=42)
        assert builder.seed == 42
        assert len(builder.nodes) == 0
        assert len(builder.edges) == 0
        assert len(builder.excluded) == 0

    def test_add_agent_node(self):
        builder = Graph3DBuilder(seed=42)
        agent = builder.add_agent_node("Marcel", "1")
        assert agent.node_type == "agent"
        assert agent.label == "Marcel"
        assert agent.position.z == LAYER_Z[AGENT_LAYER]

    def test_add_technique_node(self):
        builder = Graph3DBuilder(seed=42)
        agent = builder.add_agent_node("Marcel", "1")
        tech = builder.add_technique_node("Analysis", agent, 0)
        assert tech.node_type == "technique"
        assert tech.label == "Analysis"
        assert tech.position.z == LAYER_Z[TECHNIQUE_LAYER]

    def test_add_item_node(self):
        builder = Graph3DBuilder(seed=42)
        agent = builder.add_agent_node("Marcel", "1")
        tech = builder.add_technique_node("Analysis", agent, 0)
        item = builder.add_item_node("Item1", tech, 0)
        assert item.node_type == "item"
        assert item.label == "Item1"
        assert item.position.z == LAYER_Z[ITEM_LAYER]

    def test_add_synthesis_node(self):
        builder = Graph3DBuilder(seed=42)
        synthesis = builder.add_synthesis_node("Final")
        assert synthesis.node_type == "synthesis"
        assert synthesis.label == "Final"
        assert synthesis.position.z == LAYER_Z[SYNTHESIS_LAYER]

    def test_add_excluded_technique(self):
        builder = Graph3DBuilder(seed=42)
        agent = builder.add_agent_node("Marcel", "1")
        excluded = builder.add_excluded_technique(
            "Excluded", agent, "Not applicable", 0
        )
        assert excluded.node_type == "excluded"
        assert "excluded" in excluded.label.lower()
        assert len(builder.excluded) == 1
        assert builder.excluded[0].reason == "Not applicable"

    def test_connect_to_synthesis(self):
        builder = Graph3DBuilder(seed=42)
        agent = builder.add_agent_node("Marcel", "1")
        synthesis = builder.add_synthesis_node()
        edge = builder.connect_to_synthesis(agent, synthesis)
        assert edge.source == agent.node_id
        assert edge.target == synthesis.node_id

    def test_build_creates_payload(self):
        builder = Graph3DBuilder(seed=42)
        builder.add_agent_node("Marcel", "1")
        result = builder.build(apply_bundling=False)
        assert isinstance(result, Graph3DPayload)
        assert len(result.nodes) == 1


class TestFDEBBundling:
    def test_compute_fdeb_empty_edges(self):
        result = compute_fdeb_bundling([], {})
        assert result == []

    def test_compute_fdeb_single_edge(self):
        builder = Graph3DBuilder(seed=42)
        agent = builder.add_agent_node("Agent", "1")
        synthesis = builder.add_synthesis_node()
        builder.connect_to_synthesis(agent, synthesis)

        result = compute_fdeb_bundling(builder.edges, builder.nodes)
        assert len(result) == 1
        assert result[0].bundled_path is not None
        assert len(result[0].bundled_path) >= 2

    def test_bundled_path_no_nan_inf(self):
        builder = Graph3DBuilder(seed=42)
        for i in range(3):
            builder.add_agent_node(f"Agent{i}", str(i + 1))
        synthesis = builder.add_synthesis_node()
        for node in builder.nodes.values():
            if node.node_type == "agent":
                builder.connect_to_synthesis(node, synthesis)

        result = compute_fdeb_bundling(builder.edges, builder.nodes)

        for edge in result:
            for point in edge.bundled_path:
                assert math.isfinite(point.x)
                assert math.isfinite(point.y)
                assert math.isfinite(point.z)

    def test_fdeb_deterministic(self):
        def build_test_graph(seed):
            builder = Graph3DBuilder(seed=seed)
            builder.add_agent_node("Agent1", "1")
            builder.add_agent_node("Agent2", "2")
            synthesis = builder.add_synthesis_node()
            for node in builder.nodes.values():
                if node.node_type == "agent":
                    builder.connect_to_synthesis(node, synthesis)
            return compute_fdeb_bundling(builder.edges, builder.nodes)

        result1 = build_test_graph(123)
        result2 = build_test_graph(123)

        for e1, e2 in zip(result1, result2):
            assert len(e1.bundled_path) == len(e2.bundled_path)
            for p1, p2 in zip(e1.bundled_path, e2.bundled_path):
                assert abs(p1.x - p2.x) < 1e-10
                assert abs(p1.y - p2.y) < 1e-10
                assert abs(p1.z - p2.z) < 1e-10


class TestEdgePathValidity:
    def test_control_points_within_bounds(self):
        result = build_sample_3d_graph(seed=42)

        for edge in result.edges:
            if edge.bundled_path:
                for point in edge.bundled_path:
                    assert -1000 <= point.x <= 1000
                    assert -1000 <= point.y <= 1000
                    assert 0 <= point.z <= 500


class TestPerformance:
    def test_build_performance(self):
        start_time = time.time()
        result = build_sample_3d_graph(seed=42)
        elapsed_ms = (time.time() - start_time) * 1000

        assert elapsed_ms < 2000
        assert len(result.nodes) > 0
        assert len(result.edges) > 0

    def test_fdeb_performance(self):
        builder = Graph3DBuilder(seed=42)

        for i in range(5):
            agent = builder.add_agent_node(f"Agent{i}", str(i + 1))
            for j in range(3):
                tech = builder.add_technique_node(f"Tech{j}", agent, j)
                for k in range(2):
                    builder.add_item_node(f"Item{k}", tech, k)

        synthesis = builder.add_synthesis_node()
        for node in builder.nodes.values():
            if node.node_type == "item":
                builder.connect_to_synthesis(node, synthesis)

        start_time = time.time()
        builder.apply_edge_bundling(iterations=20)
        elapsed_ms = (time.time() - start_time) * 1000

        assert elapsed_ms < 2000


class TestBuildSampleGraph:
    def test_sample_graph_structure(self):
        result = build_sample_3d_graph(seed=42)

        agents = [n for n in result.nodes if n.node_type == "agent"]
        techniques = [n for n in result.nodes if n.node_type == "technique"]
        items = [n for n in result.nodes if n.node_type == "item"]
        synthesis = [n for n in result.nodes if n.node_type == "synthesis"]
        excluded = [n for n in result.nodes if n.node_type == "excluded"]

        assert len(agents) == 3
        assert len(techniques) == 6
        assert len(items) == 12
        assert len(synthesis) == 1
        assert len(excluded) == 3

    def test_sample_graph_has_excluded_techniques(self):
        result = build_sample_3d_graph(seed=42)
        assert result.excluded_techniques is not None
        assert len(result.excluded_techniques) == 3

    def test_sample_graph_deterministic(self):
        result1 = build_sample_3d_graph(seed=42)
        result2 = build_sample_3d_graph(seed=42)

        assert len(result1.nodes) == len(result2.nodes)
        assert len(result1.edges) == len(result2.edges)

        for n1, n2 in zip(result1.nodes, result2.nodes):
            assert n1.node_id == n2.node_id
            assert abs(n1.position.x - n2.position.x) < 1e-10
            assert abs(n1.position.y - n2.position.y) < 1e-10
            assert abs(n1.position.z - n2.position.z) < 1e-10


class TestNodeAnchoring:
    def test_technique_near_agent(self):
        builder = Graph3DBuilder(seed=42)
        agent = builder.add_agent_node("TestAgent", "1")
        tech = builder.add_technique_node("Tech", agent, 0)

        distance = math.sqrt(
            (tech.position.x - agent.position.x) ** 2
            + (tech.position.y - agent.position.y) ** 2
        )
        assert distance < 200

    def test_item_near_technique(self):
        builder = Graph3DBuilder(seed=42)
        agent = builder.add_agent_node("TestAgent", "1")
        tech = builder.add_technique_node("Tech", agent, 0)
        item = builder.add_item_node("Item", tech, 0)

        distance = math.sqrt(
            (item.position.x - tech.position.x) ** 2
            + (item.position.y - tech.position.y) ** 2
        )
        assert distance < 200
