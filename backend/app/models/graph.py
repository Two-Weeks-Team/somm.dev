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

Graph State Models (Phase G1):
- TraceEvent: Single trace event for timeline visualization
- ItemScore: Score for a single evaluated item
- ExcludedTechnique: Technique that was excluded from evaluation
- AgentContribution: Contribution from a single agent

Graph Schema Versioning:
    - Current version: 2 (matching Fairthon)
    - graph_schema_version field included in all payloads
    - Breaking changes increment major version
    - Cached graphs invalidated on version mismatch
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field, model_validator

# GRAPH_SCHEMA_VERSION: Current graph schema version (matching Fairthon)
# Increment on breaking changes. Cached graphs are invalidated on version mismatch.
GRAPH_SCHEMA_VERSION = 2


class EvaluationMode(str, Enum):
    """Canonical evaluation modes with machine IDs.

    This is the single source of truth for evaluation modes.
    Imported and re-exported by app.graph.graph_factory for backward compatibility.

    Attributes:
        SIX_SOMMELIERS: Six Sommeliers mode - 6 parallel agents, ~90s duration
        GRAND_TASTING: Grand Tasting mode - comprehensive evaluation
        FULL_TECHNIQUES: Full Techniques mode - 75 techniques in 8 groups, ~3min duration
    """

    SIX_SOMMELIERS = "six_sommeliers"
    GRAND_TASTING = "grand_tasting"
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
        mode: Evaluation mode - "six_sommeliers" | "grand_tasting" | "full_techniques"
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
    mode: EvaluationMode = Field(
        ...,
        description='Evaluation mode: "six_sommeliers" | "grand_tasting" | "full_techniques"',
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
    """3D coordinate position with vector operations.

    Represents a point in 3D space for graph visualization.
    Supports vector arithmetic for FDEB edge bundling calculations.

    Attributes:
        x: X-coordinate (horizontal)
        y: Y-coordinate (vertical)
        z: Z-coordinate (depth)
    """

    x: float = Field(..., description="X-coordinate (horizontal)")
    y: float = Field(..., description="Y-coordinate (vertical)")
    z: float = Field(..., description="Z-coordinate (depth)")

    def __add__(self, other: "Position3D") -> "Position3D":
        """Add two positions component-wise."""
        return Position3D(x=self.x + other.x, y=self.y + other.y, z=self.z + other.z)

    def __sub__(self, other: "Position3D") -> "Position3D":
        """Subtract two positions component-wise."""
        return Position3D(x=self.x - other.x, y=self.y - other.y, z=self.z - other.z)

    def __mul__(self, scalar: float) -> "Position3D":
        """Scale position by a scalar."""
        return Position3D(x=self.x * scalar, y=self.y * scalar, z=self.z * scalar)

    def __truediv__(self, scalar: float) -> "Position3D":
        """Divide position by a scalar."""
        if scalar == 0:
            return Position3D(x=0, y=0, z=0)
        return Position3D(x=self.x / scalar, y=self.y / scalar, z=self.z / scalar)

    def dot(self, other: "Position3D") -> float:
        """Compute dot product with another position."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def magnitude(self) -> float:
        """Compute Euclidean magnitude."""
        import math

        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> "Position3D":
        """Return normalized position (unit vector)."""
        mag = self.magnitude()
        if mag == 0:
            return Position3D(x=0, y=0, z=0)
        return self / mag


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
        hat_type: Optional hat type for Six Sommeliers mode
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
    step_number: int = Field(
        default=0, description="Animation step number for sequencing"
    )
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
    control_points: Optional[list[Position3D]] = Field(
        default=None, description="Alias for bundled_path, used by frontend renderers"
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
    bundle_groups: Optional[dict[str, Any]] = Field(
        default=None, description="Optional bundle group metadata for edge bundling"
    )


class Graph3DPayload(BaseModel):
    """Complete 3D graph payload for visualization.

    This model represents the full graph structure for 3D visualization
    with layered layout and edge bundling support.

    Attributes:
        graph_schema_version: Schema version for backward compatibility (default: 2)
        evaluation_id: Reference to the evaluation
        mode: Evaluation mode - "six_sommeliers" | "grand_tasting" | "full_techniques"
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
        ...,
        description="Evaluation mode (e.g., six_sommeliers, grand_tasting, full_techniques)",
    )
    nodes: list[Graph3DNode] = Field(..., description="List of graph nodes")
    edges: list[Graph3DEdge] = Field(..., description="List of graph edges (bundled)")
    edges_raw: Optional[list[Graph3DEdge]] = Field(
        default=None, description="Optional list of edges before bundling"
    )
    excluded_techniques: Optional[list["ExcludedTechnique"]] = Field(
        default=None, description="Optional list of excluded technique info"
    )
    metadata: Graph3DMetadata = Field(..., description="Graph bounds and statistics")

    @classmethod
    def create(
        cls,
        evaluation_id: str,
        mode: str,
        nodes: list["Graph3DNode"],
        edges: list["Graph3DEdge"],
        edges_raw: Optional[list["Graph3DEdge"]] = None,
        excluded_techniques: Optional[list["ExcludedTechnique"]] = None,
    ) -> "Graph3DPayload":
        """Create Graph3DPayload with computed metadata."""
        all_steps = {n.step_number for n in nodes} | {e.step_number for e in edges}
        total_steps = len(all_steps)
        max_step = max(all_steps) if all_steps else 0

        if nodes:
            x_coords = [n.position.x for n in nodes]
            y_coords = [n.position.y for n in nodes]
            z_coords = [n.position.z for n in nodes]
            x_range = (min(x_coords), max(x_coords))
            y_range = (min(y_coords), max(y_coords))
            z_range = (min(z_coords), max(z_coords))
        else:
            x_range = (0.0, 0.0)
            y_range = (0.0, 0.0)
            z_range = (0.0, 0.0)

        metadata = Graph3DMetadata(
            x_range=x_range,
            y_range=y_range,
            z_range=z_range,
            total_nodes=len(nodes),
            total_edges=len(edges),
            total_steps=total_steps,
            max_step_number=max_step,
            generated_at=datetime.now(timezone.utc).isoformat(),
        )

        return cls(
            evaluation_id=evaluation_id,
            mode=mode,
            nodes=nodes,
            edges=edges,
            edges_raw=edges_raw,
            excluded_techniques=excluded_techniques,
            metadata=metadata,
        )

    @model_validator(mode="after")
    def check_version_consistency(self) -> "Graph3DPayload":
        """Validate that graph_schema_version matches metadata.graph_schema_version."""
        if self.graph_schema_version != self.metadata.graph_schema_version:
            raise ValueError(
                f"Payload graph_schema_version ({self.graph_schema_version}) "
                f"does not match metadata.graph_schema_version "
                f"({self.metadata.graph_schema_version})"
            )
        return self


# =============================================================================
# Phase G1: Graph State Models
# =============================================================================


class TraceEvent(BaseModel):
    """Single trace event for timeline visualization.

    Represents a discrete action in the evaluation pipeline,
    enabling step-by-step animation and debugging.

    Timestamp format: ISO 8601 (e.g., "2026-02-06T10:30:00Z")
    Step semantics: Global ordering per evaluation (0-indexed, monotonic)

    Attributes:
        step: Global step number for ordering
        timestamp: ISO 8601 timestamp
        agent: Agent that performed the action
        technique_id: Technique being applied
        item_id: Item being evaluated, if applicable
        action: Action performed (e.g., 'evaluate', 'score', 'exclude')
        score_delta: Score change, if applicable
        evidence_ref: Reference to evidence, if applicable
    """

    step: int = Field(ge=0, description="Global step number for ordering")
    timestamp: str = Field(description="ISO 8601 timestamp")
    agent: str = Field(description="Agent that performed the action")
    technique_id: str = Field(description="Technique being applied")
    item_id: Optional[str] = Field(
        default=None, description="Item being evaluated, if applicable"
    )
    action: str = Field(
        description="Action performed (e.g., 'evaluate', 'score', 'exclude')"
    )
    score_delta: Optional[float] = Field(
        default=None, description="Score change, if applicable"
    )
    evidence_ref: Optional[str] = Field(
        default=None, description="Reference to evidence, if applicable"
    )


class ItemScore(BaseModel):
    """Score for a single evaluated item.

    Attributes:
        item_id: Unique identifier for the evaluated item
        score: Score value between 0 and 100
        evaluated_by: Name of the agent that performed the evaluation
        technique_id: Technique used for evaluation
        timestamp: ISO 8601 timestamp of when the evaluation occurred
        notes: Optional notes or comments about the evaluation
    """

    item_id: str = Field(description="Unique identifier for the evaluated item")
    score: float = Field(ge=0, description="Score value (0 or greater, no upper limit)")
    evaluated_by: str = Field(
        description="Name of the agent that performed the evaluation"
    )
    technique_id: str = Field(description="Technique used for evaluation")
    timestamp: str = Field(
        description="ISO 8601 timestamp of when the evaluation occurred"
    )
    notes: Optional[str] = Field(
        default=None, description="Optional notes or comments about the evaluation"
    )

    # Extended fields for detailed evaluation (backward compatible)
    item_name: Optional[str] = Field(
        default=None, description="Human-readable name of the item"
    )
    max_score: Optional[float] = Field(
        default=None, description="Maximum possible score for this item"
    )
    status: Optional[str] = Field(
        default=None, description="Evaluation status (e.g., 'evaluated', 'excluded')"
    )
    unevaluated_reason: Optional[str] = Field(
        default=None, description="Reason if item was not evaluated"
    )
    hat_used: Optional[str] = Field(
        default=None, description="Hat/agent type that performed the evaluation"
    )
    evidence: Optional[list[str]] = Field(
        default=None, description="List of evidence references"
    )
    rationale: Optional[str] = Field(
        default=None, description="Explanation for the score"
    )
    confidence: Optional[str] = Field(
        default=None, description="Confidence level in the evaluation"
    )


class ExcludedTechnique(BaseModel):
    """Technique that was excluded from evaluation.

    Attributes:
        technique_id: Unique identifier for the excluded technique
        reason: Reason for exclusion
        excluded_at: Timestamp when the technique was excluded
        excluded_by: Agent that excluded the technique
    """

    technique_id: str = Field(
        description="Unique identifier for the excluded technique"
    )
    reason: str = Field(default="unknown", description="Reason for exclusion")
    excluded_at: Optional[str] = Field(
        default=None, description="Timestamp when the technique was excluded"
    )
    excluded_by: Optional[str] = Field(
        default=None, description="Agent that excluded the technique"
    )


class AgentContribution(BaseModel):
    """Contribution from a single agent.

    Tracks the work performed by a single agent during evaluation,
    including techniques used, items evaluated, and artifacts produced.

    Attributes:
        agent: Name of the agent
        technique_ids: List of technique IDs used by this agent
        item_ids: List of item IDs evaluated by this agent
        artifacts: Dictionary of artifacts produced by this agent
    """

    agent: str = Field(description="Name of the agent")
    technique_ids: List[str] = Field(
        default_factory=list, description="List of technique IDs used by this agent"
    )
    item_ids: List[str] = Field(
        default_factory=list, description="List of item IDs evaluated by this agent"
    )
    artifacts: dict = Field(
        default_factory=dict,
        description="Dictionary of artifacts produced by this agent",
    )


class ModeResponse(BaseModel):
    """Response model for the evaluation mode endpoint."""

    mode: str = Field(
        ...,
        description="Evaluation mode (six_sommeliers, grand_tasting, or full_techniques)",
    )
    evaluation_id: str = Field(..., description="The evaluation ID")


# =============================================================================
# Phase G4: Advanced 3D Graph Models
# =============================================================================


class ExcludedVisualization(BaseModel):
    """Visualization metadata for excluded techniques.

    Provides styling information for techniques that were excluded
    from the main flow but should still be visualized with distinct styling.

    Attributes:
        technique_id: ID of the excluded technique
        reason: Reason for exclusion
        node_style: Visual style for excluded node (opacity, dasharray)
        edge_style: Visual style for edges to excluded node (color, dasharray)
    """

    technique_id: str = Field(..., description="ID of the excluded technique")
    reason: str = Field(..., description="Reason for exclusion")
    node_style: dict = Field(
        default_factory=lambda: {"opacity": 0.5, "dasharray": "5,5"},
        description="Visual style for excluded node",
    )
    edge_style: dict = Field(
        default_factory=lambda: {"color": "#ff0000", "dasharray": "3,3"},
        description="Visual style for edges to excluded node",
    )
