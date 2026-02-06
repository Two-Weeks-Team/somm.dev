"""Graph visualization models for somm.dev backend.

This module contains all Pydantic models for graph visualization as defined in ADR-002:
- EvaluationMode: Enum for canonical evaluation modes
- ReactFlowNode: 2D graph node for ReactFlow visualization
- ReactFlowEdge: 2D graph edge for ReactFlow visualization
- ReactFlowGraph: Complete 2D graph payload
- Position3D: 3D coordinate position
- Graph3DNode: 3D graph node
- Graph3DEdge: 3D graph edge with bundling support
- Graph3DMetadata: Metadata for 3D graph
- Graph3DPayload: Complete 3D graph payload

Graph Schema Versioning:
    - Current version: 2 (matching Fairthon)
    - graph_schema_version field included in all payloads
    - Breaking changes increment major version
    - Cached graphs invalidated on version mismatch
"""

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field

# GRAPH_SCHEMA_VERSION: Current graph schema version (matching Fairthon)
# Increment on breaking changes. Cached graphs are invalidated on version mismatch.
GRAPH_SCHEMA_VERSION = 2


class EvaluationMode(str, Enum):
    """Canonical evaluation modes with machine IDs.

    Attributes:
        SIX_HATS: Six Hats mode - 6 parallel agents, ~90s duration
        FULL_TECHNIQUES: Full Techniques mode - 75 techniques in 8 groups, ~3min duration
    """

    SIX_HATS = "six_hats"
    FULL_TECHNIQUES = "full_techniques"


class ReactFlowNode(BaseModel):
    """2D graph node for ReactFlow visualization.

    Represents a single node in a ReactFlow-compatible 2D graph.
    Used for visualizing evaluation workflows and agent interactions.

    Attributes:
        id: Unique identifier for the node
        type: Node type - "start" | "end" | "agent" | "technique" | "synthesis" | "process"
        position: 2D coordinates {"x": float, "y": float}
        data: Node data including label, status, progress, color, etc.
    """

    id: str = Field(..., description="Unique identifier for the node")
    type: str = Field(
        ...,
        description='Node type: "start" | "end" | "agent" | "technique" | "synthesis" | "process"',
    )
    position: dict[str, float] = Field(
        ..., description='2D coordinates {"x": float, "y": float}'
    )
    data: dict[str, Any] = Field(
        ..., description="Node data including label, status, progress, color, etc."
    )


class ReactFlowEdge(BaseModel):
    """2D graph edge for ReactFlow visualization.

    Represents a connection between two nodes in a ReactFlow graph.
    Supports animation and custom styling.

    Attributes:
        id: Unique identifier for the edge
        source: ID of the source node
        target: ID of the target node
        animated: Whether the edge should be animated (default: True)
        style: Optional custom styling properties
    """

    id: str = Field(..., description="Unique identifier for the edge")
    source: str = Field(..., description="ID of the source node")
    target: str = Field(..., description="ID of the target node")
    animated: bool = Field(
        default=True, description="Whether the edge should be animated"
    )
    style: Optional[dict[str, Any]] = Field(
        default=None, description="Optional custom styling properties"
    )


class ReactFlowGraph(BaseModel):
    """Complete 2D graph payload for ReactFlow visualization.

    This model represents the full graph structure for 2D visualization.
    Includes graph schema version for cache invalidation and backward compatibility.

    Attributes:
        graph_schema_version: Schema version for backward compatibility (default: 2)
        mode: Evaluation mode - "six_hats" | "full_techniques"
        nodes: List of ReactFlowNode objects
        edges: List of ReactFlowEdge objects
        description: Optional graph description
        meta: Optional metadata dictionary

    Versioning:
        - graph_schema_version is required for cache key generation
        - Increment version on breaking schema changes
        - Cached graphs are automatically invalidated when version changes
    """

    graph_schema_version: int = Field(
        default=GRAPH_SCHEMA_VERSION,
        description="Schema version for backward compatibility and cache invalidation",
    )
    mode: str = Field(
        ..., description='Evaluation mode: "six_hats" | "full_techniques"'
    )
    nodes: list[ReactFlowNode] = Field(..., description="List of graph nodes")
    edges: list[ReactFlowEdge] = Field(..., description="List of graph edges")
    description: Optional[str] = Field(
        default=None, description="Optional graph description"
    )
    meta: Optional[dict[str, Any]] = Field(
        default=None, description="Optional metadata"
    )


class Position3D(BaseModel):
    """3D coordinate position.

    Represents a point in 3D space for graph visualization.

    Attributes:
        x: X-coordinate (horizontal)
        y: Y-coordinate (vertical)
        z: Z-coordinate (depth)
    """

    x: float = Field(..., description="X-coordinate (horizontal)")
    y: float = Field(..., description="Y-coordinate (vertical)")
    z: float = Field(..., description="Z-coordinate (depth)")


class Graph3DNode(BaseModel):
    """3D graph node for layered visualization.

    Represents a single node in a 3D graph with layered layout.
    Includes step_number for animation sequencing.

    Attributes:
        node_id: Unique identifier for the node
        node_type: Type of node (e.g., "agent", "technique", "synthesis")
        label: Display label for the node
        position: 3D coordinates
        color: Optional color for the node
        step_number: Animation step number for sequencing
        hat_type: Optional hat type for Six Hats mode
        technique_id: Optional technique identifier
        category: Optional category classification
        item_count: Optional count of items
    """

    node_id: str = Field(..., description="Unique identifier for the node")
    node_type: str = Field(
        ..., description="Type of node (e.g., 'agent', 'technique', 'synthesis')"
    )
    label: str = Field(..., description="Display label for the node")
    position: Position3D = Field(..., description="3D coordinates")
    color: Optional[str] = Field(
        default=None, description="Optional color for the node"
    )
    step_number: int = Field(..., description="Animation step number for sequencing")
    hat_type: Optional[str] = Field(
        default=None, description="Optional hat type for Six Hats mode"
    )
    technique_id: Optional[str] = Field(
        default=None, description="Optional technique identifier"
    )
    category: Optional[str] = Field(
        default=None, description="Optional category classification"
    )
    item_count: Optional[int] = Field(
        default=None, description="Optional count of items"
    )


class Graph3DEdge(BaseModel):
    """3D graph edge with bundling support.

    Represents a connection between two nodes in a 3D graph.
    Supports edge bundling for cleaner visualization of parallel edges.

    Attributes:
        edge_id: Unique identifier for the edge
        source: ID of the source node
        target: ID of the target node
        edge_type: Edge type - "flow" | "parallel" | "data" | "excluded"
        color: Optional color for the edge
        width: Edge width (default: 1.0)
        step_number: Animation step number for sequencing
        bundle_id: Optional bundle identifier for grouped edges
        bundled_path: Optional path points for bundled edges
        dasharray: Optional dash pattern for the edge
    """

    edge_id: str = Field(..., description="Unique identifier for the edge")
    source: str = Field(..., description="ID of the source node")
    target: str = Field(..., description="ID of the target node")
    edge_type: str = Field(
        ..., description='Edge type: "flow" | "parallel" | "data" | "excluded"'
    )
    color: Optional[str] = Field(
        default=None, description="Optional color for the edge"
    )
    width: float = Field(default=1.0, description="Edge width")
    step_number: int = Field(..., description="Animation step number for sequencing")
    bundle_id: Optional[str] = Field(
        default=None, description="Optional bundle identifier for grouped edges"
    )
    bundled_path: Optional[list[Position3D]] = Field(
        default=None, description="Optional path points for bundled edges"
    )
    dasharray: Optional[str] = Field(default=None, description="Optional dash pattern")


class Graph3DMetadata(BaseModel):
    """Metadata for 3D graph.

    Contains bounds and statistics for the 3D graph visualization.
    Used for camera positioning and progress indicators.

    Attributes:
        x_range: Min and max X coordinates
        y_range: Min and max Y coordinates
        z_range: Min and max Z coordinates
        total_nodes: Total number of nodes
        total_edges: Total number of edges
        total_steps: Total animation steps
        max_step_number: Maximum step number
        graph_schema_version: Schema version (default: 2)
        generated_at: ISO timestamp when graph was generated

    Versioning:
        - graph_schema_version must match the payload version
        - Used for cache validation and backward compatibility
    """

    x_range: tuple[float, float] = Field(..., description="Min and max X coordinates")
    y_range: tuple[float, float] = Field(..., description="Min and max Y coordinates")
    z_range: tuple[float, float] = Field(..., description="Min and max Z coordinates")
    total_nodes: int = Field(..., description="Total number of nodes")
    total_edges: int = Field(..., description="Total number of edges")
    total_steps: int = Field(..., description="Total animation steps")
    max_step_number: int = Field(..., description="Maximum step number")
    graph_schema_version: int = Field(
        default=GRAPH_SCHEMA_VERSION,
        description="Schema version for backward compatibility",
    )
    generated_at: str = Field(..., description="ISO timestamp when graph was generated")


class Graph3DPayload(BaseModel):
    """Complete 3D graph payload for visualization.

    This model represents the full graph structure for 3D visualization
    with layered layout and edge bundling support.

    Attributes:
        graph_schema_version: Schema version for backward compatibility (default: 2)
        evaluation_id: Reference to the evaluation
        mode: Evaluation mode - "six_hats" | "full_techniques"
        nodes: List of Graph3DNode objects
        edges: List of Graph3DEdge objects (bundled)
        edges_raw: Optional list of edges before bundling
        excluded_techniques: Optional list of excluded technique info
        metadata: Graph3DMetadata with bounds and statistics

    Versioning:
        - graph_schema_version is required for cache key generation
        - Must match metadata.graph_schema_version
        - Increment version on breaking schema changes
        - Cached graphs are automatically invalidated when version changes

    Cache Invalidation:
        Cache keys include the graph schema version: "{evaluation_id}:{mode}:{layout_hash}:{version}"
        When version changes, old cache entries are ignored and graphs are regenerated.
    """

    graph_schema_version: int = Field(
        default=GRAPH_SCHEMA_VERSION,
        description="Schema version for backward compatibility and cache invalidation",
    )
    evaluation_id: str = Field(..., description="Reference to the evaluation")
    mode: str = Field(
        ..., description='Evaluation mode: "six_hats" | "full_techniques"'
    )
    nodes: list[Graph3DNode] = Field(..., description="List of graph nodes")
    edges: list[Graph3DEdge] = Field(..., description="List of graph edges (bundled)")
    edges_raw: Optional[list[Graph3DEdge]] = Field(
        default=None, description="Optional list of edges before bundling"
    )
    excluded_techniques: Optional[list[dict]] = Field(
        default=None, description="Optional list of excluded technique info"
    )
    metadata: Graph3DMetadata = Field(..., description="Graph bounds and statistics")
