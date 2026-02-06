"""Evaluate API routes for starting and monitoring evaluations.

This module provides endpoints for:
- Starting new evaluations (POST /api/evaluate)
- Streaming evaluation progress (GET /api/evaluate/{evaluation_id}/stream)
- Getting evaluation results (GET /api/evaluate/{evaluation_id}/result)
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.api.deps import get_current_user, get_current_user_token
from app.core.exceptions import CorkedError, EmptyCellarError
from app.services.evaluation_service import (
    get_evaluation_progress,
    get_evaluation_result,
    handle_evaluation_error,
    run_evaluation_pipeline_with_events,
    start_evaluation,
)
from app.services.event_channel import (
    get_event_channel,
    EventType,
    SommelierProgressEvent,
    create_sommelier_event,
)
from app.services.task_registry import register_task

logger = logging.getLogger(__name__)

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
    evaluation_mode: str = Field(
        default="six_sommeliers",
        description="Evaluation mode: six_sommeliers (default) or grand_tasting",
        examples=["six_sommeliers", "grand_tasting"],
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
    evaluation_mode: str = Field(
        default="six_sommeliers",
        description="Evaluation mode used",
    )
    estimated_time: int = Field(
        default=30,
        description="Estimated time in seconds",
    )


class ResultResponse(BaseModel):
    """Response model for evaluation result."""

    evaluation_id: str
    final_evaluation: dict[str, Any]
    created_at: str


@router.post("", response_model=EvaluateResponse)
async def create_evaluation(
    request: EvaluateRequest,
    user=Depends(get_current_user),
    github_token: str = Depends(get_current_user_token),
) -> EvaluateResponse:
    """Start a new code evaluation for a GitHub repository.

    The evaluation runs as a background task, allowing immediate response.
    Use the /stream endpoint to receive real-time progress updates.
    """
    logger.info(
        f"[Evaluate] Request received: repo_url={request.repo_url}, "
        f"criteria={request.criteria}, evaluation_mode={request.evaluation_mode}, user={user.id}"
    )

    try:
        eval_id = await start_evaluation(
            repo_url=request.repo_url,
            criteria=request.criteria,
            user_id=user.id,
            evaluation_mode=request.evaluation_mode,
        )

        event_channel = get_event_channel()
        await event_channel.create_channel(eval_id)

        async def run_in_background():
            try:
                await run_evaluation_pipeline_with_events(
                    evaluation_id=eval_id,
                    repo_url=request.repo_url,
                    criteria=request.criteria,
                    user_id=user.id,
                    evaluation_mode=request.evaluation_mode,
                    provider=request.provider,
                    model=request.model,
                    temperature=request.temperature,
                    api_key=request.api_key,
                    github_token=github_token,
                )
            except Exception as e:
                logger.exception(f"Background evaluation failed: {eval_id}")
                error_msg = str(e)
                if "Resource not found" in error_msg or "404" in error_msg:
                    user_message = "Repository not found or is private. Please check the URL and try again."
                elif "rate limit" in error_msg.lower():
                    user_message = (
                        "GitHub API rate limit exceeded. Please try again later."
                    )
                else:
                    user_message = f"Evaluation failed: {error_msg}"
                await event_channel.emit(
                    eval_id,
                    create_sommelier_event(
                        evaluation_id=eval_id,
                        sommelier="system",
                        event_type=EventType.EVALUATION_ERROR.value,
                        progress_percent=-1,
                        message=user_message,
                    ),
                )
                await handle_evaluation_error(eval_id, error_msg)
            finally:
                await event_channel.close_channel(eval_id)

        try:
            task = asyncio.create_task(run_in_background())
            await register_task(eval_id, task)
        except Exception as e:
            await event_channel.close_channel(eval_id)
            raise CorkedError(f"Failed to start background task: {e!s}") from e

        logger.info(f"[Evaluate] Background task started: {eval_id}")

        estimated = 30 if request.evaluation_mode == "six_sommeliers" else 60
        return EvaluateResponse(
            evaluation_id=eval_id,
            status="pending",
            evaluation_mode=request.evaluation_mode,
            estimated_time=estimated,
        )
    except CorkedError as e:
        logger.error(f"[Evaluate] CorkedError: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"[Evaluate] Exception: {type(e).__name__}: {str(e)}")
        import traceback

        logger.error(f"[Evaluate] Traceback: {traceback.format_exc()}")
        raise CorkedError(f"Failed to start evaluation: {e!s}") from e


@router.get("/{evaluation_id}/stream")
async def stream_evaluation(
    evaluation_id: str,
    user=Depends(get_current_user),
) -> Any:
    """Stream evaluation progress via Server-Sent Events.

    This endpoint provides real-time updates about the evaluation progress,
    including:
    - sommelier_start: When a sommelier begins analysis
    - sommelier_complete: When a sommelier finishes analysis
    - sommelier_error: When a sommelier encounters an error
    - evaluation_complete: When the entire evaluation is finished
    - evaluation_error: When the entire evaluation fails
    - heartbeat: Keep-alive signal (every 30 seconds)
    """
    try:
        progress = await get_evaluation_progress(evaluation_id)
    except EmptyCellarError:
        raise EmptyCellarError(f"Evaluation not found: {evaluation_id}") from None

    if progress.get("user_id") != user.id:
        raise CorkedError("Access denied: evaluation belongs to another user")

    event_channel = get_event_channel()
    await event_channel.create_channel(evaluation_id)

    async def generate():
        try:
            status = progress.get("status")
            if status in ("completed", "failed"):
                event_type = (
                    EventType.EVALUATION_COMPLETE
                    if status == "completed"
                    else EventType.EVALUATION_ERROR
                )
                fallback_event = SommelierProgressEvent(
                    evaluation_id=evaluation_id,
                    event_type=event_type,
                    sommelier="system",
                    message=f"Evaluation already {status}",
                    progress_percent=100 if status == "completed" else -1,
                )
                yield f"data: {json.dumps(fallback_event.to_dict())}\n\n"
                return

            async for event in event_channel.subscribe(evaluation_id):
                yield f"data: {json.dumps(event.to_dict())}\n\n"

                if event.event_type in (
                    EventType.EVALUATION_COMPLETE,
                    EventType.EVALUATION_ERROR,
                ):
                    break
        except asyncio.CancelledError:
            logger.info(f"SSE stream cancelled for {evaluation_id}")
        finally:
            await event_channel.close_channel(evaluation_id)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


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
        raise EmptyCellarError(f"Evaluation not found: {evaluation_id}") from None
    except CorkedError:
        raise

    if result is None:
        raise EmptyCellarError(f"Evaluation result not found: {evaluation_id}")

    return ResultResponse(
        evaluation_id=result["evaluation_id"],
        final_evaluation=result["final_evaluation"],
        created_at=str(result["created_at"]),
    )
