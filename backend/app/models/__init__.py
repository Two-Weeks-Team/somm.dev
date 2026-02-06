"""Models package

This package contains all Pydantic models for the somm.dev backend:
- user: User-related models (UserBase, UserCreate, UserInDB, UserResponse)
- evaluation: Evaluation models (EvaluationStatus, EvaluationCriteria, RepoContext, etc.)
- results: Results models (RatingTier, SommelierOutput, FinalEvaluation, etc.)
- graph: Graph visualization models (ReactFlowGraph, Graph3DPayload, EvaluationMode, etc.)
         and graph state models (TraceEvent, ItemScore, ExcludedTechnique, AgentContribution)
"""

from app.models.user import UserBase, UserCreate, UserInDB, UserResponse
from app.models.evaluation import (
    EvaluationStatus,
    EvaluationCriteria,
    RepoContext,
    EvaluationCreate,
    EvaluationInDB,
    EvaluationResponse,
)
from app.models.results import (
    RatingTier,
    get_rating_tier,
    SommelierOutput,
    FinalEvaluation,
    ResultInDB,
    ResultResponse,
)
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
    TraceEvent,
    ItemScore,
    ExcludedTechnique,
    AgentContribution,
    ModeResponse,
    ExcludedVisualization,
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserInDB",
    "UserResponse",
    "EvaluationStatus",
    "EvaluationCriteria",
    "RepoContext",
    "EvaluationCreate",
    "EvaluationInDB",
    "EvaluationResponse",
    "RatingTier",
    "get_rating_tier",
    "SommelierOutput",
    "FinalEvaluation",
    "ResultInDB",
    "ResultResponse",
    "GRAPH_SCHEMA_VERSION",
    "EvaluationMode",
    "ReactFlowNode",
    "ReactFlowEdge",
    "ReactFlowGraph",
    "Position3D",
    "Graph3DNode",
    "Graph3DEdge",
    "Graph3DMetadata",
    "Graph3DPayload",
    "TraceEvent",
    "ItemScore",
    "ExcludedTechnique",
    "AgentContribution",
    "ModeResponse",
    "ExcludedVisualization",
]
