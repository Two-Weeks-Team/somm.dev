"""Graph builder service for creating ReactFlow graph structures.

This module provides functions to build ReactFlow-compatible graph
structures for visualization of the evaluation pipeline.
"""

from app.graph.graph_factory import EvaluationMode
from app.models.graph import (
    ReactFlowGraph,
    ReactFlowNode,
    ReactFlowEdge,
)

# Sommelier node configurations
SOMMELIER_CONFIG = {
    "marcel": {"name": "Marcel", "role": "Cellar Master", "color": "#8B7355"},
    "isabella": {"name": "Isabella", "role": "Wine Critic", "color": "#C41E3A"},
    "heinrich": {"name": "Heinrich", "role": "Quality Inspector", "color": "#2F4F4F"},
    "sofia": {"name": "Sofia", "role": "Vineyard Scout", "color": "#DAA520"},
    "laurent": {"name": "Laurent", "role": "Winemaker", "color": "#228B22"},
    "jeanpierre": {
        "name": "Jean-Pierre",
        "role": "Master Sommelier",
        "color": "#4169E1",
    },
}

TECHNIQUE_CATEGORIES = {
    "aroma": {
        "name": "Aroma",
        "description": "Problem Analysis",
        "color": "#9B59B6",
        "total": 11,
        "sommelier_origin": "marcel",
    },
    "palate": {
        "name": "Palate",
        "description": "Innovation",
        "color": "#E74C3C",
        "total": 13,
        "sommelier_origin": "isabella",
    },
    "body": {
        "name": "Body",
        "description": "Risk Analysis",
        "color": "#F39C12",
        "total": 8,
        "sommelier_origin": "heinrich",
    },
    "finish": {
        "name": "Finish",
        "description": "User-Centricity",
        "color": "#1ABC9C",
        "total": 12,
        "sommelier_origin": "sofia",
    },
    "balance": {
        "name": "Balance",
        "description": "Feasibility",
        "color": "#3498DB",
        "total": 8,
        "sommelier_origin": "laurent",
    },
    "vintage": {
        "name": "Vintage",
        "description": "Opportunity",
        "color": "#27AE60",
        "total": 10,
        "sommelier_origin": "laurent",
    },
    "terroir": {
        "name": "Terroir",
        "description": "Presentation",
        "color": "#E67E22",
        "total": 5,
        "sommelier_origin": "jeanpierre",
    },
    "cellar": {
        "name": "Cellar",
        "description": "Synthesis",
        "color": "#34495E",
        "total": 8,
        "sommelier_origin": "jeanpierre",
    },
}

# Backward compatibility alias for tests
TECHNIQUE_GROUPS = TECHNIQUE_CATEGORIES


def build_six_sommeliers_topology() -> ReactFlowGraph:
    """Build ReactFlow graph for six_sommeliers mode.

    Topology: Start -> 6 parallel agents -> Synthesis -> End

    Returns:
        ReactFlowGraph with nodes and edges for the six_sommeliers evaluation pipeline.
    """
    nodes: list[ReactFlowNode] = []
    edges: list[ReactFlowEdge] = []

    # Start node (step 0)
    nodes.append(
        ReactFlowNode(
            id="start",
            type="start",
            position={"x": 400, "y": 0},
            data={"label": "Start", "description": "Evaluation begins", "step": 0},
        )
    )

    # Parallel sommelier agents (5 in parallel, steps 1-5)
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
                    "step": i + 1,
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

    # Synthesis node (Jean-Pierre, step 6)
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
                "step": 6,
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

    # End node (step 7)
    nodes.append(
        ReactFlowNode(
            id="end",
            type="end",
            position={"x": 400, "y": 420},
            data={"label": "End", "description": "Evaluation complete", "step": 7},
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
        mode=EvaluationMode.SIX_SOMMELIERS.value,
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

    # Start node (step 0)
    nodes.append(
        ReactFlowNode(
            id="start",
            type="start",
            position={"x": 500, "y": 0},
            data={"label": "Start", "description": "Evaluation begins", "step": 0},
        )
    )

    category_ids = list(TECHNIQUE_CATEGORIES.keys())
    spacing_x = 120
    start_x = 140

    for i, category_id in enumerate(category_ids[:4]):
        config = TECHNIQUE_CATEGORIES[category_id]
        x_pos = start_x + (i * spacing_x)
        nodes.append(
            ReactFlowNode(
                id=category_id,
                type="technique_group",
                position={"x": x_pos, "y": 100},
                data={
                    "label": config["name"],
                    "description": config["description"],
                    "color": config["color"],
                    "category": category_id,
                    "total": config["total"],
                    "sommelier_origin": config["sommelier_origin"],
                    "step": i + 1,
                },
            )
        )
        edges.append(
            ReactFlowEdge(
                id=f"edge-start-{category_id}",
                source="start",
                target=category_id,
                animated=True,
            )
        )

    for i, category_id in enumerate(category_ids[4:]):
        config = TECHNIQUE_CATEGORIES[category_id]
        x_pos = start_x + (i * spacing_x)
        nodes.append(
            ReactFlowNode(
                id=category_id,
                type="technique_group",
                position={"x": x_pos, "y": 220},
                data={
                    "label": config["name"],
                    "description": config["description"],
                    "color": config["color"],
                    "category": category_id,
                    "total": config["total"],
                    "sommelier_origin": config["sommelier_origin"],
                    "step": i + 5,
                },
            )
        )
        edges.append(
            ReactFlowEdge(
                id=f"edge-start-{category_id}",
                source="start",
                target=category_id,
                animated=True,
            )
        )

    # Synthesis node (step 9)
    nodes.append(
        ReactFlowNode(
            id="synthesis",
            type="synthesis",
            position={"x": 500, "y": 360},
            data={
                "label": "Synthesis",
                "description": "Aggregate all technique analyses",
                "color": "#4169E1",
                "step": 9,
            },
        )
    )

    for category_id in category_ids:
        edges.append(
            ReactFlowEdge(
                id=f"edge-{category_id}-synthesis",
                source=category_id,
                target="synthesis",
                animated=True,
            )
        )

    # End node (step 10)
    nodes.append(
        ReactFlowNode(
            id="end",
            type="end",
            position={"x": 500, "y": 480},
            data={"label": "End", "description": "Evaluation complete", "step": 10},
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
