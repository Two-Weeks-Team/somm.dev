# ADR-002: Graph Visualization Contracts

## Status
Accepted

## Context
We need to align somm.dev with Fairthon's graph visualization capabilities. Fairthon provides:
- ReactFlow-compatible 2D graph output
- 3D graph with layered layout and edge bundling
- Multiple evaluation modes (six_hats, full_techniques)
- Graph caching for performance

Before implementing the Graph Track (Phases G0-G6), we need stable API contracts to ensure:
- Backend/frontend compatibility
- Cache key consistency
- Schema versioning for backward compatibility

## Decision

### 1. Evaluation Modes
Support exactly two evaluation modes:

| Mode | ID | Agents/Techniques | Typical Duration |
|------|-----|-------------------|------------------|
| Six Hats | `six_hats` | 6 parallel agents | ~90s |
| Full Techniques | `full_techniques` | 75 techniques in 8 groups | ~3min |

### 2. ReactFlow Graph Schema (2D)
```python
class ReactFlowNode(BaseModel):
    id: str
    type: str  # "start" | "end" | "agent" | "technique" | "synthesis" | "process"
    position: dict[str, float]  # {"x": float, "y": float}
    data: dict[str, Any]  # label, status, progress, color, etc.

class ReactFlowEdge(BaseModel):
    id: str
    source: str
    target: str
    animated: bool = True
    style: dict[str, Any] | None = None

class ReactFlowGraph(BaseModel):
    graph_schema_version: int = 2  # Required for cache invalidation
    mode: str  # "six_hats" | "full_techniques"
    nodes: list[ReactFlowNode]
    edges: list[ReactFlowEdge]
    description: str | None = None
    meta: dict[str, Any] | None = None
```

### 3. 3D Graph Schema
```python
class Position3D(BaseModel):
    x: float
    y: float
    z: float

class Graph3DNode(BaseModel):
    node_id: str
    node_type: str
    label: str
    position: Position3D
    color: str | None = None
    step_number: int  # For animation
    # Type-specific fields
    hat_type: str | None = None
    technique_id: str | None = None
    category: str | None = None
    item_count: int | None = None

class Graph3DEdge(BaseModel):
    edge_id: str
    source: str
    target: str
    edge_type: str  # "flow" | "parallel" | "data" | "excluded"
    color: str | None = None
    width: float = 1.0
    step_number: int
    bundle_id: str | None = None
    bundled_path: list[Position3D] | None = None  # For edge bundling
    dasharray: str | None = None

class Graph3DMetadata(BaseModel):
    x_range: tuple[float, float]
    y_range: tuple[float, float]
    z_range: tuple[float, float]
    total_nodes: int
    total_edges: int
    total_steps: int
    max_step_number: int
    graph_schema_version: int = 2
    generated_at: str

class Graph3DPayload(BaseModel):
    graph_schema_version: int = 2
    evaluation_id: str
    mode: str
    nodes: list[Graph3DNode]
    edges: list[Graph3DEdge]
    edges_raw: list[Graph3DEdge] | None = None  # Before bundling
    excluded_techniques: list[dict] | None = None
    metadata: Graph3DMetadata
```

### 4. API Endpoints
```
GET /api/evaluate/{evaluation_id}/graph
    -> ReactFlowGraph

GET /api/evaluate/{evaluation_id}/graph/timeline
    -> list[TraceEvent]

GET /api/evaluate/{evaluation_id}/graph-3d
    -> Graph3DPayload

Query params:
    ?refresh=true  # Force recompute, bypass cache
    ?bundling=true|false  # Enable/disable edge bundling (3D only)
```

### 5. Cache Key Structure
```python
cache_key = f"{evaluation_id}:{mode}:{layout_hash}:{graph_schema_version}"

# Example:
# "eval_abc123:six_hats:a1b2c3d4:2"
```

### 6. Schema Versioning

**GRAPH_SCHEMA_VERSION Constant:**
```python
GRAPH_SCHEMA_VERSION = 2  # Current version matching Fairthon
```

**Versioning Rules:**
- `graph_schema_version` field required in all payloads (ReactFlowGraph, Graph3DPayload, Graph3DMetadata)
- Current version: **2** (matching Fairthon)
- Breaking changes increment major version
- Cached graphs invalidated on version mismatch

**Cache Invalidation Behavior:**
- Cache key format: `{evaluation_id}:{mode}:{layout_hash}:{graph_schema_version}`
- Example: `"eval_abc123:six_hats:a1b2c3d4:2"`
- When graph_schema_version changes, old cache entries are ignored
- Graphs are automatically regenerated with new schema version
- Backend validates version match between payload and metadata

**Documentation in Models:**
All Pydantic models include docstrings documenting:
- Graph schema version requirements
- Cache invalidation behavior
- Version field descriptions

## Consequences

### Positive
- Clear contracts enable parallel frontend/backend development
- Versioning ensures backward compatibility
- Cache keys prevent stale data issues
- Two modes provide flexibility without complexity

### Negative
- Schema changes require coordination
- Cache invalidation adds complexity
- Two modes mean maintaining two graph definitions

## Links
- [FAIRTHON_ALIGNMENT_PLAN.md](../FAIRTHON_ALIGNMENT_PLAN.md)
- [ADR-001: Fairthon Alignment Baseline](./ADR-001-fairthon-alignment.md)
- Fairthon reference: `backend/app/routers/graph_routes.py`

---

*Created: 2026-02-06*
