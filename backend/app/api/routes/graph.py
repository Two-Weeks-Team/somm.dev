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
from app.models.graph import ReactFlowGraph, TraceEvent, ModeResponse, EvaluationMode
from app.services.graph_builder import (
    build_six_hats_topology,
    build_full_techniques_topology,
)

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
        raise CorkedError("Access denied: evaluation belongs to another user")


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

    # Convert to TraceEvent models and sort by step
    events = [
        TraceEvent(
            step=event.get("step", 0),
            timestamp=event.get("timestamp", ""),
            agent=event.get("agent", ""),
            technique_id=event.get("technique_id", ""),
            item_id=event.get("item_id"),
            action=event.get("action", ""),
            score_delta=event.get("score_delta"),
            evidence_ref=event.get("evidence_ref"),
        )
        for event in methodology_trace
    ]

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
