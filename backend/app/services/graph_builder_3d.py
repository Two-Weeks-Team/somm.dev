"""3D graph builder service with deterministic layered layout.

This module provides deterministic 3D graph visualization building:
- Layered z-axis layout (0-400) for different node types
- Step tracking from methodology_trace for animation
- Stable, reproducible coordinates for identical inputs
"""

from app.models.graph import (
    Graph3DPayload,
    Graph3DNode,
    Graph3DEdge,
    Position3D,
)


LAYER_START = 0
LAYER_RAG = 100
LAYER_AGENTS = 200
LAYER_SYNTHESIS = 300
LAYER_END = 400

AGENT_SPACING = 120
CENTER_X = 0

SOMMELIER_AGENTS = [
    ("marcel", "Marcel", "#8B7355"),
    ("isabella", "Isabella", "#C41E3A"),
    ("heinrich", "Heinrich", "#2F4F4F"),
    ("sofia", "Sofia", "#DAA520"),
    ("laurent", "Laurent", "#228B22"),
]

DEFAULT_TECHNIQUES = [
    ("tech_1", "Code Structure Analysis", "structure"),
    ("tech_2", "Quality Assessment", "quality"),
    ("tech_3", "Security Scan", "security"),
    ("tech_4", "Innovation Check", "innovation"),
    ("tech_5", "Implementation Review", "implementation"),
]


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
    """Build the RAG enrichment node at layer 100."""
    return Graph3DNode(
        node_id="rag_enrich",
        node_type="rag",
        label="RAG Enrichment",
        position=Position3D(x=CENTER_X, y=0, z=LAYER_RAG),
        color="#9370DB",
        step_number=step_number,
    )


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


def _build_edges(nodes: list[Graph3DNode]) -> list[Graph3DEdge]:
    """Build edges connecting nodes in the graph.

    Creates deterministic edges:
    - Start -> RAG (if RAG exists)
    - RAG -> Agents or Start -> Agents
    - Agents -> Synthesis
    - Synthesis -> End
    """
    edges = []
    edge_id = 0

    node_map = {n.node_id: n for n in nodes}

    has_rag = "rag_enrich" in node_map
    has_synthesis = "synthesis" in node_map
    has_end = "end" in node_map

    if has_rag:
        edges.append(
            Graph3DEdge(
                edge_id=f"edge_{edge_id}",
                source="start",
                target="rag_enrich",
                edge_type="flow",
                step_number=0,
            )
        )
        edge_id += 1

    agents = [n for n in nodes if n.node_type == "agent"]
    if agents:
        source_layer = "rag_enrich" if has_rag else "start"
        for agent in agents:
            edges.append(
                Graph3DEdge(
                    edge_id=f"edge_{edge_id}",
                    source=source_layer,
                    target=agent.node_id,
                    edge_type="parallel",
                    step_number=agent.step_number,
                )
            )
            edge_id += 1

            techniques = [n for n in nodes if n.node_id.startswith(agent.node_id + "_")]
            for tech in techniques:
                edges.append(
                    Graph3DEdge(
                        edge_id=f"edge_{edge_id}",
                        source=agent.node_id,
                        target=tech.node_id,
                        edge_type="data",
                        step_number=agent.step_number,
                    )
                )
                edge_id += 1

    if has_synthesis and agents:
        for agent in agents:
            edges.append(
                Graph3DEdge(
                    edge_id=f"edge_{edge_id}",
                    source=agent.node_id,
                    target="synthesis",
                    edge_type="flow",
                    step_number=agent.step_number + 1,
                )
            )
            edge_id += 1

    if has_end and has_synthesis:
        edges.append(
            Graph3DEdge(
                edge_id=f"edge_{edge_id}",
                source="synthesis",
                target="end",
                edge_type="flow",
                step_number=8,
            )
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
