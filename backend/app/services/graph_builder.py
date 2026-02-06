"""Graph builder service for creating ReactFlow graph structures.

This module provides functions to build ReactFlow-compatible graph
structures for visualization of the evaluation pipeline.
"""

from app.models.graph import ReactFlowGraph, ReactFlowNode, ReactFlowEdge, EvaluationMode

# Sommelier node configurations
SOMMELIER_CONFIG = {
    "marcel": {"name": "Marcel", "role": "Cellar Master", "color": "#8B7355"},
    "isabella": {"name": "Isabella", "role": "Wine Critic", "color": "#C41E3A"},
    "heinrich": {"name": "Heinrich", "role": "Quality Inspector", "color": "#2F4F4F"},
    "sofia": {"name": "Sofia", "role": "Vineyard Scout", "color": "#DAA520"},
    "laurent": {"name": "Laurent", "role": "Winemaker", "color": "#228B22"},
    "jeanpierre": {"name": "Jean-Pierre", "role": "Master Sommelier", "color": "#4169E1"},
}

# Technique group configurations for full_techniques mode
TECHNIQUE_GROUPS = {
    "structure": {"name": "Structure Analysis", "color": "#8B7355"},
    "quality": {"name": "Quality Assessment", "color": "#C41E3A"},
    "security": {"name": "Security Review", "color": "#2F4F4F"},
    "innovation": {"name": "Innovation Scan", "color": "#DAA520"},
    "implementation": {"name": "Implementation Check", "color": "#228B22"},
    "documentation": {"name": "Documentation Review", "color": "#9370DB"},
    "testing": {"name": "Testing Analysis", "color": "#FF6347"},
    "performance": {"name": "Performance Audit", "color": "#20B2AA"},
}


def build_six_hats_topology() -> ReactFlowGraph:
    """Build ReactFlow graph for six_hats mode.

    Topology: Start -> 6 parallel agents -> Synthesis -> End

    Returns:
        ReactFlowGraph with nodes and edges for the six_hats evaluation pipeline.
    """
    nodes: list[ReactFlowNode] = []
    edges: list[ReactFlowEdge] = []

    # Start node
    nodes.append(
        ReactFlowNode(
            id="start",
            type="start",
            position={"x": 400, "y": 0},
            data={"label": "Start", "description": "Evaluation begins"},
        )
    )

    # Parallel sommelier agents (5 in parallel)
    sommelier_ids = ["marcel", "isabella", "heinrich", "sofia", "laurent"]
    spacing = 160
    start_x = 80

    for i, sommelier_id in enumerate(sommelier_ids):
        config = SOMMELIER_CONFIG[sommelier_id]
        x_pos = start_x + (i * spacing)
        nodes.append(
            ReactFlowNode(
                id=sommelier_id,
                type="agent",
                position={"x": x_pos, "y": 120},
                data={
                    "label": config["name"],
                    "role": config["role"],
                    "color": config["color"],
                },
            )
        )
        # Edge from start to each sommelier
        edges.append(
            ReactFlowEdge(
                id=f"edge-start-{sommelier_id}",
                source="start",
                target=sommelier_id,
                animated=True,
            )
        )

    # Synthesis node (Jean-Pierre)
    nodes.append(
        ReactFlowNode(
            id="jeanpierre",
            type="synthesis",
            position={"x": 400, "y": 280},
            data={
                "label": "Jean-Pierre",
                "role": "Master Sommelier",
                "color": "#4169E1",
                "description": "Final synthesis and verdict",
            },
        )
    )

    # Edges from each sommelier to synthesis
    for sommelier_id in sommelier_ids:
        edges.append(
            ReactFlowEdge(
                id=f"edge-{sommelier_id}-jeanpierre",
                source=sommelier_id,
                target="jeanpierre",
                animated=True,
            )
        )

    # End node
    nodes.append(
        ReactFlowNode(
            id="end",
            type="end",
            position={"x": 400, "y": 420},
            data={"label": "End", "description": "Evaluation complete"},
        )
    )

    # Edge from synthesis to end
    edges.append(
        ReactFlowEdge(
            id="edge-jeanpierre-end",
            source="jeanpierre",
            target="end",
            animated=True,
        )
    )

    return ReactFlowGraph(
        mode=EvaluationMode.SIX_HATS.value,
        nodes=nodes,
        edges=edges,
        description="Six sommeliers evaluate in parallel, then Jean-Pierre synthesizes",
        meta={
            "parallel_agents": 5,
            "synthesis_agent": "jeanpierre",
            "total_nodes": len(nodes),
            "total_edges": len(edges),
        },
    )


def build_full_techniques_topology() -> ReactFlowGraph:
    """Build ReactFlow graph for full_techniques mode.

    Topology: Start -> 8 technique groups -> Synthesis -> End

    Returns:
        ReactFlowGraph with nodes and edges for the full_techniques evaluation pipeline.
    """
    nodes: list[ReactFlowNode] = []
    edges: list[ReactFlowEdge] = []

    # Start node
    nodes.append(
        ReactFlowNode(
            id="start",
            type="start",
            position={"x": 500, "y": 0},
            data={"label": "Start", "description": "Evaluation begins"},
        )
    )

    # Technique groups (8 groups in two rows)
    group_ids = list(TECHNIQUE_GROUPS.keys())
    spacing_x = 120
    start_x = 140

    # First row (4 groups)
    for i, group_id in enumerate(group_ids[:4]):
        config = TECHNIQUE_GROUPS[group_id]
        x_pos = start_x + (i * spacing_x)
        nodes.append(
            ReactFlowNode(
                id=group_id,
                type="technique_group",
                position={"x": x_pos, "y": 100},
                data={
                    "label": config["name"],
                    "color": config["color"],
                    "group": group_id,
                },
            )
        )
        # Edge from start to each group
        edges.append(
            ReactFlowEdge(
                id=f"edge-start-{group_id}",
                source="start",
                target=group_id,
                animated=True,
            )
        )

    # Second row (4 groups)
    for i, group_id in enumerate(group_ids[4:]):
        config = TECHNIQUE_GROUPS[group_id]
        x_pos = start_x + (i * spacing_x)
        nodes.append(
            ReactFlowNode(
                id=group_id,
                type="technique_group",
                position={"x": x_pos, "y": 220},
                data={
                    "label": config["name"],
                    "color": config["color"],
                    "group": group_id,
                },
            )
        )
        # Edge from start to each group
        edges.append(
            ReactFlowEdge(
                id=f"edge-start-{group_id}",
                source="start",
                target=group_id,
                animated=True,
            )
        )

    # Synthesis node
    nodes.append(
        ReactFlowNode(
            id="synthesis",
            type="synthesis",
            position={"x": 500, "y": 360},
            data={
                "label": "Synthesis",
                "description": "Aggregate all technique analyses",
                "color": "#4169E1",
            },
        )
    )

    # Edges from each technique group to synthesis
    for group_id in group_ids:
        edges.append(
            ReactFlowEdge(
                id=f"edge-{group_id}-synthesis",
                source=group_id,
                target="synthesis",
                animated=True,
            )
        )

    # End node
    nodes.append(
        ReactFlowNode(
            id="end",
            type="end",
            position={"x": 500, "y": 480},
            data={"label": "End", "description": "Evaluation complete"},
        )
    )

    # Edge from synthesis to end
    edges.append(
        ReactFlowEdge(
            id="edge-synthesis-end",
            source="synthesis",
            target="end",
            animated=True,
        )
    )

    return ReactFlowGraph(
        mode=EvaluationMode.FULL_TECHNIQUES.value,
        nodes=nodes,
        edges=edges,
        description="8 technique groups analyze in parallel, then synthesize results",
        meta={
            "technique_groups": 8,
            "total_nodes": len(nodes),
            "total_edges": len(edges),
        },
    )
