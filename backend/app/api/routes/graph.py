"""Graph visualization API routes.

This module provides endpoints for:
- Getting ReactFlow graph structure for evaluation visualization
- Getting timeline trace events
- Getting evaluation mode
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.core.exceptions import CorkedError, EmptyCellarError
from app.database.repositories.evaluation import EvaluationRepository
from app.models.graph import (
    ReactFlowGraph,
    TraceEvent,
    ModeResponse,
    EvaluationMode,
    Graph3DPayload,
)
from app.services.graph_builder import (
    build_six_hats_topology,
    build_full_techniques_topology,
)
from app.services.graph_builder_3d import build_3d_graph

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evaluate", tags=["graph"])


async def _get_evaluation(evaluation_id: str) -> dict[str, Any] | None:
    """Fetch evaluation from database.

    Args:
        evaluation_id: The evaluation ID.

    Returns:
        Evaluation document or None if not found.
    """
    repo = EvaluationRepository()
    return await repo.get_by_id(evaluation_id)


def _check_ownership(evaluation: dict[str, Any], user) -> None:
    """Verify user owns the evaluation.

    Args:
        evaluation: The evaluation document.
        user: The current authenticated user.

    Raises:
        CorkedError: If user does not own the evaluation.
    """
    if evaluation.get("user_id") != user.id:
        raise CorkedError(
            "Access denied: evaluation belongs to another user", status_code=403
        )


def _determine_mode(evaluation: dict[str, Any]) -> EvaluationMode:
    """Determine evaluation mode from evaluation data.

    Args:
        evaluation: The evaluation document.

    Returns:
        EvaluationMode (six_hats or full_techniques).
    """
    # Check for explicit mode in evaluation data
    mode = evaluation.get("mode")
    if mode == EvaluationMode.FULL_TECHNIQUES.value:
        return EvaluationMode.FULL_TECHNIQUES
    # Default to six_hats mode
    return EvaluationMode.SIX_HATS


@router.get("/{evaluation_id}/graph", response_model=ReactFlowGraph)
async def get_graph(
    evaluation_id: str,
    user=Depends(get_current_user),
) -> ReactFlowGraph:
    """Get ReactFlow graph for evaluation visualization.

    This endpoint returns the complete ReactFlow graph structure
    (nodes and edges) needed to visualize the evaluation pipeline.

    Args:
        evaluation_id: The evaluation ID.
        user: The authenticated user.

    Returns:
        ReactFlowGraph containing nodes, edges, and metadata.

    Raises:
        EmptyCellarError: If evaluation not found (404).
        CorkedError: If user does not own the evaluation (403).
    """
    logger.info(f"[Graph] Getting graph for evaluation: {evaluation_id}")

    # 1. Verify evaluation exists
    evaluation = await _get_evaluation(evaluation_id)
    if not evaluation:
        raise EmptyCellarError(f"Evaluation not found: {evaluation_id}")

    # 2. Check user owns evaluation
    _check_ownership(evaluation, user)

    # 3. Determine mode and build graph
    mode = _determine_mode(evaluation)

    if mode == EvaluationMode.FULL_TECHNIQUES:
        graph = build_full_techniques_topology()
    else:
        graph = build_six_hats_topology()

    logger.info(f"[Graph] Returning {mode.value} graph for {evaluation_id}")
    return graph


@router.get("/{evaluation_id}/graph/structure", response_model=ReactFlowGraph)
async def get_graph_structure(
    evaluation_id: str,
    user=Depends(get_current_user),
) -> ReactFlowGraph:
    """Get static graph structure (topology only, no execution state).

    Returns the evaluation workflow topology without any runtime state.
    Use this for displaying the graph structure before execution starts.
    """
    logger.info(f"[Graph] Getting structure for evaluation: {evaluation_id}")

    evaluation = await _get_evaluation(evaluation_id)
    if not evaluation:
        raise EmptyCellarError(f"Evaluation not found: {evaluation_id}")
    _check_ownership(evaluation, user)

    mode = _determine_mode(evaluation)
    if mode == EvaluationMode.FULL_TECHNIQUES:
        graph = build_full_techniques_topology()
    else:
        graph = build_six_hats_topology()

    return graph


@router.get("/{evaluation_id}/graph/execution", response_model=ReactFlowGraph)
async def get_graph_execution(
    evaluation_id: str,
    user=Depends(get_current_user),
) -> ReactFlowGraph:
    """Get graph with execution state overlay (status, progress from trace).

    Returns the evaluation workflow with runtime state from methodology_trace.
    Node status reflects the execution progress.
    """
    logger.info(f"[Graph] Getting execution graph for evaluation: {evaluation_id}")

    evaluation = await _get_evaluation(evaluation_id)
    if not evaluation:
        raise EmptyCellarError(f"Evaluation not found: {evaluation_id}")
    _check_ownership(evaluation, user)

    mode = _determine_mode(evaluation)
    if mode == EvaluationMode.FULL_TECHNIQUES:
        graph = build_full_techniques_topology()
    else:
        graph = build_six_hats_topology()

    methodology_trace = evaluation.get("methodology_trace", [])
    if methodology_trace:
        completed_agents = set()
        for event in methodology_trace:
            if isinstance(event, dict):
                agent = event.get("agent") or event.get("sommelier")
                if agent:
                    completed_agents.add(agent.lower())

        for node in graph.nodes:
            node_id_lower = node.id.lower()
            if node_id_lower in completed_agents:
                node.data["status"] = "completed"
            elif node.type == "start":
                node.data["status"] = "completed"
            elif node.type == "end" and len(completed_agents) >= 5:
                node.data["status"] = "completed"
            elif node.type == "synthesis" and len(completed_agents) >= 5:
                node.data["status"] = "completed"
            else:
                node.data["status"] = "pending"

    return graph


@router.get("/{evaluation_id}/graph/timeline", response_model=list[TraceEvent])
async def get_timeline(
    evaluation_id: str,
    user=Depends(get_current_user),
) -> list[TraceEvent]:
    """Get timeline of trace events ordered by step.

    This endpoint returns the methodology trace from the evaluation state,
    ordered by step number.

    Args:
        evaluation_id: The evaluation ID.
        user: The authenticated user.

    Returns:
        List of TraceEvent objects ordered by step.

    Raises:
        EmptyCellarError: If evaluation not found (404).
        CorkedError: If user does not own the evaluation (403).
    """
    logger.info(f"[Graph] Getting timeline for evaluation: {evaluation_id}")

    # Verify evaluation exists and user owns it
    evaluation = await _get_evaluation(evaluation_id)
    if not evaluation:
        raise EmptyCellarError(f"Evaluation not found: {evaluation_id}")
    _check_ownership(evaluation, user)

    # Get methodology_trace from evaluation state
    # For now, return empty list as placeholder
    # In full implementation, this would come from evaluation state or checkpoint
    methodology_trace = evaluation.get("methodology_trace", [])

    if not methodology_trace:
        # Return empty timeline as placeholder
        return []

    events = [TraceEvent.model_validate(event) for event in methodology_trace]

    # Sort by step number
    events.sort(key=lambda e: e.step)

    return events


@router.get("/{evaluation_id}/graph/mode", response_model=ModeResponse)
async def get_mode(
    evaluation_id: str,
    user=Depends(get_current_user),
) -> ModeResponse:
    """Get current evaluation mode.

    Returns the evaluation mode (six_hats or full_techniques)
    for the specified evaluation.

    Args:
        evaluation_id: The evaluation ID.
        user: The authenticated user.

    Returns:
        ModeResponse containing mode and evaluation_id.

    Raises:
        EmptyCellarError: If evaluation not found (404).
        CorkedError: If user does not own the evaluation (403).
    """
    logger.info(f"[Graph] Getting mode for evaluation: {evaluation_id}")

    # Verify evaluation exists and user owns it
    evaluation = await _get_evaluation(evaluation_id)
    if not evaluation:
        raise EmptyCellarError(f"Evaluation not found: {evaluation_id}")
    _check_ownership(evaluation, user)

    # Determine mode
    mode = _determine_mode(evaluation)

    return ModeResponse(
        mode=mode.value,
        evaluation_id=evaluation_id,
    )


@router.get("/{evaluation_id}/graph-3d", response_model=Graph3DPayload)
async def get_graph_3d(
    evaluation_id: str,
    user=Depends(get_current_user),
) -> Graph3DPayload:
    """Get 3D graph payload for evaluation visualization.

    Returns a deterministic 3D graph representation of the evaluation
    pipeline with layered layout and step tracking.
    """
    logger.info(f"[Graph] Getting 3D graph for evaluation: {evaluation_id}")

    evaluation = await _get_evaluation(evaluation_id)
    if not evaluation:
        raise EmptyCellarError(f"Evaluation not found: {evaluation_id}")

    _check_ownership(evaluation, user)

    mode = _determine_mode(evaluation)
    methodology_trace = evaluation.get("methodology_trace") or []

    return build_3d_graph(
        evaluation_id=evaluation_id,
        mode=mode.value,
        methodology_trace=methodology_trace,
    )
