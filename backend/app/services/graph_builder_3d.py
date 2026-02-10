"""3D graph builder service with deterministic layered layout.

This module provides deterministic 3D graph visualization building:
- Layered z-axis layout (0-400) for different node types
- Step tracking from methodology_trace for animation
- Stable, reproducible coordinates for identical inputs
- FDEB edge bundling for cleaner visualization (Phase G4)
- Graph3DBuilder class for fluent graph construction (Phase G4)
"""

from typing import Optional

from app.models.graph import (
    Graph3DPayload,
    Graph3DNode,
    Graph3DEdge,
    Position3D,
    ExcludedVisualization,
    ExcludedTechnique,
)
from app.techniques.registry import get_registry


LAYER_START = 0
LAYER_RAG = 100
LAYER_AGENTS = 200
LAYER_SYNTHESIS = 300
LAYER_END = 400

AGENT_SPACING = 120
CENTER_X = 0

EDGE_TYPE_STYLES = {
    "flow": {"color": "#722F37", "width": 2.0, "dasharray": None},
    "parallel": {"color": "#4169E1", "width": 1.5, "dasharray": None},
    "data": {"color": "#DAA520", "width": 1.0, "dasharray": "4,4"},
    "excluded": {"color": "#888888", "width": 1.0, "dasharray": "4,4"},
}

SOMMELIER_AGENTS = [
    ("marcel", "Marcel", "#8B7355"),
    ("isabella", "Isabella", "#C41E3A"),
    ("heinrich", "Heinrich", "#2F4F4F"),
    ("sofia", "Sofia", "#DAA520"),
    ("laurent", "Laurent", "#228B22"),
]

TASTING_NOTE_CATEGORIES = [
    ("aroma", "Aroma", "#9B59B6", 11),
    ("palate", "Palate", "#E74C3C", 13),
    ("body", "Body", "#F39C12", 8),
    ("finish", "Finish", "#1ABC9C", 12),
    ("balance", "Balance", "#3498DB", 8),
    ("vintage", "Vintage", "#27AE60", 10),
    ("terroir", "Terroir", "#E67E22", 5),
    ("cellar", "Cellar", "#34495E", 8),
]

ENRICHMENT_STEPS = [
    ("code_analysis", "Code Analysis", "#9370DB"),
    ("rag", "RAG Context", "#6C3483"),
    ("web_search", "Web Search", "#8E44AD"),
]

DEFAULT_TECHNIQUES: list[tuple[str, str, str]] = []


def _get_category_counts() -> dict[str, int]:
    """Get technique counts per category from registry, with fallback to static values."""
    try:
        registry = get_registry()
        return registry.count_by_category()
    except Exception:
        return {cat_id: total for cat_id, _, _, total in TASTING_NOTE_CATEGORIES}


def _build_start_node(step_number: int = 0) -> Graph3DNode:
    """Build the start node at layer 0."""
    return Graph3DNode(
        node_id="start",
        node_type="start",
        label="Start",
        position=Position3D(x=CENTER_X, y=0, z=LAYER_START),
        color="#4169E1",
        step_number=step_number,
    )


def _build_rag_node(step_number: int = 1) -> Graph3DNode:
    """Build the RAG enrichment node at layer 100 (legacy single node)."""
    return Graph3DNode(
        node_id="rag_enrich",
        node_type="rag",
        label="RAG Enrichment",
        position=Position3D(x=CENTER_X, y=0, z=LAYER_RAG),
        color="#9370DB",
        step_number=step_number,
    )


def _build_enrichment_nodes(start_step: int = 1) -> list[Graph3DNode]:
    """Build 3 enrichment nodes (code_analysis, rag, web_search) at layer 100."""
    nodes = []
    num_steps = len(ENRICHMENT_STEPS)
    spacing = 100
    start_x = CENTER_X - (num_steps - 1) * spacing / 2

    for i, (step_id, label, color) in enumerate(ENRICHMENT_STEPS):
        x_pos = start_x + i * spacing
        nodes.append(
            Graph3DNode(
                node_id=step_id,
                node_type="enrichment",
                label=label,
                position=Position3D(x=x_pos, y=0, z=LAYER_RAG),
                color=color,
                step_number=start_step + i,
            )
        )
    return nodes


def _build_agent_nodes(
    start_step: int = 2, use_techniques: bool = True
) -> list[Graph3DNode]:
    """Build sommelier agent nodes at layer 200 with horizontal spread.

    Agents are spread evenly on the x-axis for parallel visualization.
    """
    nodes = []
    num_agents = len(SOMMELIER_AGENTS)
    total_width = (num_agents - 1) * AGENT_SPACING
    start_x = CENTER_X - total_width / 2

    for i, (agent_id, label, color) in enumerate(SOMMELIER_AGENTS):
        x_pos = start_x + i * AGENT_SPACING
        nodes.append(
            Graph3DNode(
                node_id=agent_id,
                node_type="agent",
                label=label,
                position=Position3D(x=x_pos, y=0, z=LAYER_AGENTS),
                color=color,
                step_number=start_step + i,
                hat_type=agent_id,
            )
        )

        if use_techniques:
            for j, (tech_id, tech_label, category) in enumerate(DEFAULT_TECHNIQUES):
                tech_node_id = f"{agent_id}_{tech_id}"
                nodes.append(
                    Graph3DNode(
                        node_id=tech_node_id,
                        node_type="technique",
                        label=tech_label,
                        position=Position3D(
                            x=x_pos, y=(j + 1) * 30, z=LAYER_AGENTS + 20
                        ),
                        color=color,
                        step_number=start_step + i,
                        technique_id=tech_id,
                        category=category,
                    )
                )

    return nodes


def _build_category_nodes(start_step: int = 4) -> list[Graph3DNode]:
    """Build 8 tasting note category nodes at layer 200 for full_techniques mode."""
    nodes = []
    num_categories = len(TASTING_NOTE_CATEGORIES)
    total_width = (num_categories - 1) * AGENT_SPACING
    start_x = CENTER_X - total_width / 2

    dynamic_counts = _get_category_counts()

    for i, (cat_id, label, color, static_total) in enumerate(TASTING_NOTE_CATEGORIES):
        x_pos = start_x + i * AGENT_SPACING
        technique_count = dynamic_counts.get(cat_id, static_total)
        nodes.append(
            Graph3DNode(
                node_id=cat_id,
                node_type="category",
                label=label,
                position=Position3D(x=x_pos, y=0, z=LAYER_AGENTS),
                color=color,
                step_number=start_step + i,
                category=cat_id,
                metadata={"total_techniques": technique_count},
            )
        )
    return nodes


def _build_synthesis_node(step_number: int = 7) -> Graph3DNode:
    """Build the synthesis node at layer 300."""
    return Graph3DNode(
        node_id="synthesis",
        node_type="synthesis",
        label="Synthesis",
        position=Position3D(x=CENTER_X, y=0, z=LAYER_SYNTHESIS),
        color="#4169E1",
        step_number=step_number,
    )


def _build_end_node(step_number: int = 8) -> Graph3DNode:
    """Build the end node at layer 400."""
    return Graph3DNode(
        node_id="end",
        node_type="end",
        label="End",
        position=Position3D(x=CENTER_X, y=0, z=LAYER_END),
        color="#32CD32",
        step_number=step_number,
    )


def _create_styled_edge(
    edge_id: str,
    source: str,
    target: str,
    edge_type: str,
    step_number: int,
) -> Graph3DEdge:
    """Create an edge with styling based on edge_type."""
    style = EDGE_TYPE_STYLES.get(edge_type, EDGE_TYPE_STYLES["flow"])
    return Graph3DEdge(
        edge_id=edge_id,
        source=source,
        target=target,
        edge_type=edge_type,
        step_number=step_number,
        color=style["color"],
        width=style["width"],
        dasharray=style["dasharray"],
    )


def _build_edges(nodes: list[Graph3DNode]) -> list[Graph3DEdge]:
    """Build edges connecting nodes in the graph with styling.

    Creates deterministic edges with edge-type-based styling:
    - flow: burgundy, solid, 2.0 width
    - parallel: blue, solid, 1.5 width
    - data: gold, dashed, 1.0 width
    - excluded: gray, dashed, 1.0 width
    """
    edges = []
    edge_id = 0

    node_map = {n.node_id: n for n in nodes}

    has_rag = "rag_enrich" in node_map
    has_synthesis = "synthesis" in node_map
    has_end = "end" in node_map

    if has_rag:
        edges.append(
            _create_styled_edge(f"edge_{edge_id}", "start", "rag_enrich", "flow", 0)
        )
        edge_id += 1

    agents = [n for n in nodes if n.node_type == "agent"]
    if agents:
        source_layer = "rag_enrich" if has_rag else "start"
        for agent in agents:
            edges.append(
                _create_styled_edge(
                    f"edge_{edge_id}",
                    source_layer,
                    agent.node_id,
                    "parallel",
                    agent.step_number,
                )
            )
            edge_id += 1

            techniques = [n for n in nodes if n.node_id.startswith(agent.node_id + "_")]
            for tech in techniques:
                edges.append(
                    _create_styled_edge(
                        f"edge_{edge_id}",
                        agent.node_id,
                        tech.node_id,
                        "data",
                        agent.step_number,
                    )
                )
                edge_id += 1

    if has_synthesis and agents:
        for agent in agents:
            edges.append(
                _create_styled_edge(
                    f"edge_{edge_id}",
                    agent.node_id,
                    "synthesis",
                    "flow",
                    agent.step_number + 1,
                )
            )
            edge_id += 1

    if has_end and has_synthesis:
        edges.append(
            _create_styled_edge(f"edge_{edge_id}", "synthesis", "end", "flow", 8)
        )
        edge_id += 1

    return edges


def assign_step_numbers(
    nodes: list[Graph3DNode], edges: list[Graph3DEdge], trace: list | None
) -> None:
    """Assign step numbers based on methodology_trace ordering.

    Rules:
    - Step 0: Start node
    - Steps 1-N: Based on trace events (agent order)
    - Final step: End node
    - Missing trace: Use default sequential ordering
    """
    if not trace:
        return

    trace_order = []
    seen_agents = set()
    for event in trace:
        if isinstance(event, dict):
            agent = event.get("agent") or event.get("sommelier")
            if agent and agent not in seen_agents:
                trace_order.append(agent)
                seen_agents.add(agent)

    if not trace_order:
        return

    step_map = {"start": 0}
    for i, agent in enumerate(trace_order, start=1):
        step_map[agent] = i

    step_map["synthesis"] = len(trace_order) + 1
    step_map["end"] = len(trace_order) + 2

    for node in nodes:
        node_type = node.node_type
        hat = node.hat_type or ""

        if node.node_id == "start":
            node.step_number = step_map.get("start", 0)
        elif node.node_id == "end":
            node.step_number = step_map.get("end", len(trace_order) + 2)
        elif node.node_id == "synthesis":
            node.step_number = step_map.get("synthesis", len(trace_order) + 1)
        elif node.node_id == "rag_enrich":
            node.step_number = 1
        elif node_type == "agent" and hat in step_map:
            node.step_number = step_map[hat]
        elif node_type == "technique" and hat in step_map:
            node.step_number = step_map[hat]

    node_map = {node.node_id: node for node in nodes}
    for edge in edges:
        if source_node := node_map.get(edge.source):
            edge.step_number = source_node.step_number


def build_3d_graph(
    evaluation_id: str,
    mode: str,
    methodology_trace: list | None = None,
    include_rag: bool = True,
    include_techniques: bool = True,
) -> Graph3DPayload:
    """Build deterministic 3D graph payload.

    Layered layout (z-axis):
    - Layer 0 (z=0): Start node
    - Layer 1 (z=100): RAG enrichment (optional)
    - Layer 2 (z=200): Sommelier agents (parallel, spread on x-axis)
    - Layer 3 (z=300): Synthesis node
    - Layer 4 (z=400): End node

    Determinism: Same inputs always produce identical coordinates.

    Args:
        evaluation_id: The evaluation identifier
        mode: Evaluation criteria mode
        methodology_trace: Optional trace events for step ordering
        include_rag: Whether to include RAG enrichment layer
        include_techniques: Whether to include technique nodes

    Returns:
        Graph3DPayload with deterministic 3D layout
    """
    nodes = []

    nodes.append(_build_start_node(step_number=0))

    if include_rag:
        nodes.append(_build_rag_node(step_number=1))

    agent_nodes = _build_agent_nodes(
        start_step=2 if include_rag else 1,
        use_techniques=include_techniques,
    )
    nodes.extend(agent_nodes)

    nodes.append(_build_synthesis_node(step_number=7 if include_rag else 6))
    nodes.append(_build_end_node(step_number=8 if include_rag else 7))

    edges = _build_edges(nodes)

    if methodology_trace:
        assign_step_numbers(nodes, edges, methodology_trace)

    return Graph3DPayload.create(
        evaluation_id=evaluation_id,
        mode=mode,
        nodes=nodes,
        edges=edges,
    )


def build_3d_graph_full_techniques(
    evaluation_id: str,
    methodology_trace: list | None = None,
) -> Graph3DPayload:
    """Build 3D graph for full_techniques mode with 8 categories and 3 enrichment steps.

    Layered layout (z-axis):
    - Layer 0 (z=0): Start node
    - Layer 1 (z=100): 3 enrichment nodes (code_analysis, rag, web_search)
    - Layer 2 (z=200): 8 tasting note categories
    - Layer 3 (z=300): Synthesis node
    - Layer 4 (z=400): End node
    """
    nodes: list[Graph3DNode] = []
    edges: list[Graph3DEdge] = []

    nodes.append(_build_start_node(step_number=0))

    enrichment_nodes = _build_enrichment_nodes(start_step=1)
    nodes.extend(enrichment_nodes)

    category_nodes = _build_category_nodes(start_step=4)
    nodes.extend(category_nodes)

    nodes.append(_build_synthesis_node(step_number=12))
    nodes.append(_build_end_node(step_number=13))

    edge_id = 0
    for enrich in enrichment_nodes:
        edges.append(
            _create_styled_edge(f"edge_{edge_id}", "start", enrich.node_id, "flow", 0)
        )
        edge_id += 1

    last_enrich = enrichment_nodes[-1]
    for cat in category_nodes:
        edges.append(
            _create_styled_edge(
                f"edge_{edge_id}", last_enrich.node_id, cat.node_id, "parallel", 3
            )
        )
        edge_id += 1

    for cat in category_nodes:
        edges.append(
            _create_styled_edge(
                f"edge_{edge_id}", cat.node_id, "synthesis", "flow", cat.step_number
            )
        )
        edge_id += 1

    edges.append(_create_styled_edge(f"edge_{edge_id}", "synthesis", "end", "flow", 12))

    if methodology_trace:
        assign_step_numbers(nodes, edges, methodology_trace)

    return Graph3DPayload.create(
        evaluation_id=evaluation_id,
        mode="full_techniques",
        nodes=nodes,
        edges=edges,
    )


# =============================================================================
# Phase G4: FDEB Edge Bundling and Graph3DBuilder
# =============================================================================

NUMERICAL_STABILITY_EPSILON = 1e-10

LAYER_Z = {
    1: 0,
    2: 200,
    3: 250,
    4: 300,
    5: 400,
}

AGENT_LAYER = 2
TECHNIQUE_LAYER = 3
ITEM_LAYER = 4
SYNTHESIS_LAYER = 5


def generate_step_number(parent_step: str, child_index: int) -> str:
    """Generate hierarchical step number (e.g., '1.1', '1.1.1')."""
    return f"{parent_step}.{child_index + 1}"


def compute_fdeb_bundling(
    edges: list[Graph3DEdge],
    nodes: dict[str, Graph3DNode],
    iterations: int = 20,
    compatibility_threshold: float = 0.6,
) -> list[Graph3DEdge]:
    """Apply Force-Directed Edge Bundling (FDEB) algorithm.

    FDEB algorithm (Holten & van Wijk 2009) bundles similar edges together
    for cleaner visualization of parallel connections.
    """
    iterations = max(1, min(iterations, 100))
    compatibility_threshold = max(0.0, min(compatibility_threshold, 1.0))

    for edge in edges:
        source = nodes.get(edge.source)
        target = nodes.get(edge.target)
        if source and target:
            edge.bundled_path = [source.position, target.position]
            edge.control_points = edge.bundled_path

    if not edges or len(edges) < 2:
        return edges

    def compute_compatibility(e1: Graph3DEdge, e2: Graph3DEdge) -> float:
        s1, t1 = nodes.get(e1.source), nodes.get(e1.target)
        s2, t2 = nodes.get(e2.source), nodes.get(e2.target)

        if not all([s1, t1, s2, t2]):
            return 0.0

        v1 = t1.position - s1.position
        v2 = t2.position - s2.position

        len1, len2 = v1.magnitude(), v2.magnitude()
        if len1 < NUMERICAL_STABILITY_EPSILON or len2 < NUMERICAL_STABILITY_EPSILON:
            return 0.0

        cos_angle = (v1.dot(v2)) / (len1 * len2)
        angle_compat = abs(cos_angle)

        scale_compat = 2 / (
            1 + max(len1, len2) / (min(len1, len2) + NUMERICAL_STABILITY_EPSILON)
        )

        mid1 = (s1.position + t1.position) * 0.5
        mid2 = (s2.position + t2.position) * 0.5
        mid_dist = (mid1 - mid2).magnitude()
        avg_len = (len1 + len2) * 0.5
        pos_compat = 1 / (1 + mid_dist / (avg_len + NUMERICAL_STABILITY_EPSILON))

        return angle_compat * scale_compat * pos_compat

    n_edges = len(edges)
    compatible_pairs = []
    for i in range(n_edges):
        for j in range(i + 1, n_edges):
            compat = compute_compatibility(edges[i], edges[j])
            if compat >= compatibility_threshold:
                compatible_pairs.append((i, j, compat))

    for iteration in range(iterations):
        n_subdivisions = min(8, 1 + iteration // 10)

        for edge_idx, edge in enumerate(edges):
            source = nodes.get(edge.source)
            target = nodes.get(edge.target)
            if not source or not target:
                continue

            points = []
            for i in range(n_subdivisions + 2):
                t = i / (n_subdivisions + 1)
                point = source.position + (target.position - source.position) * t
                points.append(point)

            bundled_points = [points[0]]

            for i in range(1, len(points) - 1):
                point = points[i]
                force = Position3D(x=0, y=0, z=0)

                for other_idx, other_compat, compat in compatible_pairs:
                    if edge_idx not in (other_idx, other_compat):
                        continue

                    other_edge = edges[
                        other_idx if edge_idx == other_compat else other_compat
                    ]
                    other_source = nodes.get(other_edge.source)
                    other_target = nodes.get(other_edge.target)

                    if not other_source or not other_target:
                        continue

                    other_point = other_source.position + (
                        other_target.position - other_source.position
                    ) * (i / (n_subdivisions + 1))

                    diff = other_point - point
                    force_mag = compat * 0.1
                    force = force + diff * force_mag

                for node in nodes.values():
                    diff = point - node.position
                    dist = diff.magnitude()
                    if dist > NUMERICAL_STABILITY_EPSILON and dist < 100:
                        repulsion = diff.normalize() * (500 / (dist * dist + 1))
                        force = force + repulsion

                damping = 0.5 * (1 - iteration / iterations)
                new_point = point + force * damping

                new_point = Position3D(
                    x=max(-1000, min(1000, new_point.x)),
                    y=max(-1000, min(1000, new_point.y)),
                    z=max(0, min(500, new_point.z)),
                )

                bundled_points.append(new_point)

            bundled_points.append(points[-1])

            for p in bundled_points:
                import math

                if not (
                    math.isfinite(p.x) and math.isfinite(p.y) and math.isfinite(p.z)
                ):
                    edge.bundled_path = [source.position, target.position]
                    edge.control_points = edge.bundled_path
                    break
            else:
                edge.bundled_path = bundled_points
                edge.control_points = bundled_points

    return edges


class Graph3DBuilder:
    """Fluent builder for constructing 3D graphs with multi-layer topology."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.nodes: dict[str, Graph3DNode] = {}
        self.edges: list[Graph3DEdge] = []
        self.excluded: list[ExcludedVisualization] = []
        self.node_counter = 0
        self.edge_counter = 0

    def _generate_id(self, prefix: str) -> str:
        self.node_counter += 1
        return f"{prefix}_{self.node_counter}"

    def _generate_position(
        self, layer: int, parent_pos: Optional[Position3D] = None
    ) -> Position3D:
        import random

        random.seed(self.seed + self.node_counter)
        offset_x = random.uniform(-50, 50)
        offset_y = random.uniform(-50, 50)

        if parent_pos:
            return Position3D(
                x=parent_pos.x + offset_x,
                y=parent_pos.y + offset_y,
                z=LAYER_Z[layer],
            )
        return Position3D(x=offset_x, y=offset_y, z=LAYER_Z[layer])

    def add_agent_node(
        self,
        agent_name: str,
        step_number: str,
        metadata: Optional[dict] = None,
    ) -> Graph3DNode:
        node_id = self._generate_id(f"agent_{agent_name.lower()}")
        position = self._generate_position(AGENT_LAYER)

        node = Graph3DNode(
            node_id=node_id,
            label=agent_name,
            node_type="agent",
            position=position,
            step_number=int(step_number) if step_number.isdigit() else 0,
        )
        self.nodes[node_id] = node
        return node

    def add_technique_node(
        self,
        technique_name: str,
        parent_agent: Graph3DNode,
        child_index: int,
        metadata: Optional[dict] = None,
    ) -> Graph3DNode:
        node_id = self._generate_id(f"tech_{technique_name.lower()}")
        position = self._generate_position(TECHNIQUE_LAYER, parent_agent.position)

        node = Graph3DNode(
            node_id=node_id,
            label=technique_name,
            node_type="technique",
            position=position,
            step_number=parent_agent.step_number,
        )
        self.nodes[node_id] = node

        self._add_edge(parent_agent.node_id, node_id, "default")

        return node

    def add_item_node(
        self,
        item_name: str,
        parent_technique: Graph3DNode,
        child_index: int,
        metadata: Optional[dict] = None,
    ) -> Graph3DNode:
        node_id = self._generate_id(f"item_{item_name.lower()}")
        position = self._generate_position(ITEM_LAYER, parent_technique.position)

        node = Graph3DNode(
            node_id=node_id,
            label=item_name,
            node_type="item",
            position=position,
            step_number=parent_technique.step_number,
        )
        self.nodes[node_id] = node

        self._add_edge(parent_technique.node_id, node_id, "default")

        return node

    def add_excluded_technique(
        self,
        technique_name: str,
        parent_agent: Graph3DNode,
        reason: str,
        child_index: int,
    ) -> Graph3DNode:
        node_id = self._generate_id(f"excluded_{technique_name.lower()}")
        position = self._generate_position(TECHNIQUE_LAYER, parent_agent.position)

        node = Graph3DNode(
            node_id=node_id,
            label=f"{technique_name} (excluded)",
            node_type="excluded",
            position=position,
            step_number=parent_agent.step_number,
        )
        self.nodes[node_id] = node

        self._add_edge(parent_agent.node_id, node_id, "excluded")

        excluded_viz = ExcludedVisualization(
            technique_id=node_id,
            reason=reason,
        )
        self.excluded.append(excluded_viz)

        return node

    def add_synthesis_node(
        self,
        synthesis_name: str = "Synthesis",
        metadata: Optional[dict] = None,
    ) -> Graph3DNode:
        node_id = self._generate_id("synthesis")
        position = Position3D(x=0, y=0, z=LAYER_Z[SYNTHESIS_LAYER])

        node = Graph3DNode(
            node_id=node_id,
            label=synthesis_name,
            node_type="synthesis",
            position=position,
            step_number=99,
        )
        self.nodes[node_id] = node
        return node

    def _add_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str = "default",
    ) -> Graph3DEdge:
        self.edge_counter += 1
        edge_id = f"edge_{self.edge_counter}"

        edge = Graph3DEdge(
            edge_id=edge_id,
            source=source_id,
            target=target_id,
            edge_type=edge_type,
            step_number=0,
        )
        self.edges.append(edge)
        return edge

    def connect_to_synthesis(
        self, node: Graph3DNode, synthesis: Graph3DNode
    ) -> Graph3DEdge:
        return self._add_edge(node.node_id, synthesis.node_id, "default")

    def apply_edge_bundling(
        self,
        iterations: int = 20,
        compatibility_threshold: float = 0.6,
    ) -> "Graph3DBuilder":
        self.edges = compute_fdeb_bundling(
            self.edges,
            self.nodes,
            iterations=iterations,
            compatibility_threshold=compatibility_threshold,
        )
        return self

    def build(self, apply_bundling: bool = True) -> Graph3DPayload:
        if apply_bundling and self.edges:
            self.apply_edge_bundling()

        nodes_list = list(self.nodes.values())
        return Graph3DPayload.create(
            evaluation_id="builder",
            mode="builder",
            nodes=nodes_list,
            edges=self.edges,
            excluded_techniques=[
                ExcludedTechnique(technique_id=e.technique_id, reason=e.reason)
                for e in self.excluded
            ]
            if self.excluded
            else None,
        )


def build_sample_3d_graph(seed: int = 42) -> Graph3DPayload:
    """Build a sample 3D graph for testing."""
    builder = Graph3DBuilder(seed=seed)

    agents = [
        builder.add_agent_node("Marcel", "1", {"role": "cellar_master"}),
        builder.add_agent_node("Isabella", "2", {"role": "wine_critic"}),
        builder.add_agent_node("Heinrich", "3", {"role": "quality_inspector"}),
    ]

    synthesis = builder.add_synthesis_node("Final Synthesis")

    for agent in agents:
        for t_idx in range(2):
            tech = builder.add_technique_node(
                f"Tech_{agent.label}_{t_idx + 1}",
                agent,
                t_idx,
                {"technique_type": "analysis"},
            )

            for i_idx in range(2):
                item = builder.add_item_node(
                    f"Item_{tech.label}_{i_idx + 1}",
                    tech,
                    i_idx,
                    {"item_data": "sample"},
                )
                builder.connect_to_synthesis(item, synthesis)

        builder.add_excluded_technique(
            f"Excluded_{agent.label}",
            agent,
            reason="Incompatible with current criteria",
            child_index=2,
        )

    return builder.build(apply_bundling=True)
