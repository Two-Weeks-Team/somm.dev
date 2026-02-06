"""Evaluate API routes for starting and monitoring evaluations.

This module provides endpoints for:
- Starting new evaluations (POST /api/evaluate)
- Streaming evaluation progress (GET /api/evaluate/{evaluation_id}/stream)
- Getting evaluation results (GET /api/evaluate/{evaluation_id}/result)
"""

import asyncio
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.core.exceptions import CorkedError, EmptyCellarError
from app.services.evaluation_service import (
    get_evaluation_result,
    run_full_evaluation,
)
from app.services.sse_manager import get_sse_manager

router = APIRouter(prefix="/evaluate", tags=["evaluate"])


class EvaluateRequest(BaseModel):
    """Request model for starting an evaluation."""

    repo_url: str = Field(
        ...,
        description="GitHub repository URL",
        examples=["https://github.com/owner/repo"],
    )
    criteria: str = Field(
        ...,
        description="Evaluation criteria mode",
        examples=["basic", "hackathon", "academic", "custom"],
    )
    custom_criteria: list[str] | None = Field(
        default=None,
        description="Custom criteria for custom mode",
    )
    provider: str | None = Field(
        default=None,
        description="LLM provider (gemini, openai, anthropic)",
    )
    model: str | None = Field(
        default=None,
        description="LLM model name override",
    )
    temperature: float | None = Field(
        default=None,
        description="LLM temperature override",
    )
    api_key: str | None = Field(
        default=None,
        description="BYOK API key for selected provider",
    )


class EvaluateResponse(BaseModel):
    """Response model for evaluation request."""

    evaluation_id: str
    status: str
    estimated_time: int = Field(
        default=30,
        description="Estimated time in seconds",
    )


class ResultResponse(BaseModel):
    """Response model for evaluation result."""

    evaluation_id: str
    final_evaluation: dict[str, Any]
    created_at: str


async def event_generator(
    evaluation_id: str,
    queue: asyncio.Queue,
) -> None:
    """Generate SSE events from the evaluation queue.

    Args:
        evaluation_id: The evaluation ID.
        queue: The asyncio Queue to read from.
    """
    sse_manager = get_sse_manager()

    try:
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {event}\n\n"

                if event.get("type") == "close":
                    break
            except asyncio.TimeoutError:
                yield f"data: {None}\n\n"
    except asyncio.CancelledError:
        pass
    finally:
        sse_manager.unsubscribe(evaluation_id, queue)


@router.post("", response_model=EvaluateResponse)
async def create_evaluation(
    request: EvaluateRequest,
    user=Depends(get_current_user),
) -> EvaluateResponse:
    """Start a new code evaluation for a GitHub repository.

    This endpoint initiates a new evaluation of the specified repository
    using the provided criteria mode. The evaluation runs asynchronously
    and progress can be tracked via the stream endpoint.

    Args:
        request: The evaluation request containing repo URL and criteria.
        user: The authenticated user.

    Returns:
        An evaluation response containing the evaluation ID and status.

    Raises:
        CorkedError: If the request is invalid.
    """
    try:
        evaluation_id = await run_full_evaluation(
            repo_url=request.repo_url,
            criteria=request.criteria,
            user_id=user.id,
            provider=request.provider,
            model=request.model,
            temperature=request.temperature,
            api_key=request.api_key,
        )

        return EvaluateResponse(
            evaluation_id=evaluation_id["evaluation_id"],
            status="pending",
            estimated_time=30,
        )
    except CorkedError as e:
        raise e
    except Exception as e:
        raise CorkedError(f"Failed to start evaluation: {str(e)}")


@router.get("/{evaluation_id}/stream")
async def stream_evaluation(
    evaluation_id: str,
    user=Depends(get_current_user),
) -> Any:
    """Stream evaluation progress via Server-Sent Events.

    This endpoint provides real-time updates about the evaluation progress,
    including:
    - Status changes
    - Sommelier completion events
    - Errors and warnings
    - Final result

    Args:
        evaluation_id: The evaluation ID to stream.
        user: The authenticated user.

    Returns:
        An SSE stream of evaluation events.
    """
    sse_manager = get_sse_manager()
    queue = asyncio.Queue()

    sse_manager.subscribe(evaluation_id, queue)

    async def send_events():
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {event}\n\n"

                    if event.get("type") == "close":
                        break
                except asyncio.TimeoutError:
                    yield f"data: {None}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            sse_manager.unsubscribe(evaluation_id, queue)

    return send_events()


@router.get("/{evaluation_id}/result", response_model=ResultResponse)
async def get_result(
    evaluation_id: str,
    user=Depends(get_current_user),
) -> ResultResponse:
    """Get the results of a completed evaluation.

    This endpoint returns the complete evaluation results including
    the final verdict from Jean-Pierre and all sommelier outputs.

    Args:
        evaluation_id: The evaluation ID.
        user: The authenticated user.

    Returns:
        The evaluation results.

    Raises:
        EmptyCellarError: If the evaluation is not found.
        CorkedError: If the evaluation is still in progress.
    """
    try:
        result = await get_evaluation_result(evaluation_id)
    except EmptyCellarError:
        raise EmptyCellarError(f"Evaluation not found: {evaluation_id}")
    except CorkedError as e:
        raise e

    if result is None:
        raise EmptyCellarError(f"Evaluation result not found: {evaluation_id}")

    return ResultResponse(
        evaluation_id=result["evaluation_id"],
        final_evaluation=result["final_evaluation"],
        created_at=str(result["created_at"]),
    )
