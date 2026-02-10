"""Evaluate API routes for starting and monitoring evaluations.

This module provides endpoints for:
- Starting new evaluations (POST /api/evaluate)
- Starting anonymous public evaluations (POST /api/evaluate/public)
- Streaming evaluation progress (GET /api/evaluate/{evaluation_id}/stream)
- Getting evaluation results (GET /api/evaluate/{evaluation_id}/result)
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
import traceback
from typing import Any

from cachetools import TTLCache
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.api.deps import get_current_user, get_current_user_token, get_optional_user
from app.core.config import settings
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
from app.services.github_service import verify_public_repo
from app.services.task_registry import register_task
from app.services.quota import check_quota
from app.database.repositories.api_key import APIKeyRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/evaluate", tags=["evaluate"])

_ANONYMOUS_RATE_LIMIT = 5
_ANONYMOUS_RATE_WINDOW = 3600
# TTL cache with max 10000 entries, auto-expiring after 2x window to handle edge cases
_anonymous_rate_limit_store: TTLCache = TTLCache(
    maxsize=10000, ttl=_ANONYMOUS_RATE_WINDOW * 2
)


def _check_anonymous_rate_limit(client_ip: str) -> bool:
    """Check if the client IP has exceeded the anonymous evaluation rate limit.

    Uses a TTL-based cache to prevent unbounded memory growth.

    Args:
        client_ip: The client's IP address.

    Returns:
        True if the request is allowed, False if rate limited.
    """
    now = time.time()
    window_start = now - _ANONYMOUS_RATE_WINDOW
    timestamps = _anonymous_rate_limit_store.get(client_ip, [])
    timestamps = [ts for ts in timestamps if ts > window_start]

    if len(timestamps) >= _ANONYMOUS_RATE_LIMIT:
        _anonymous_rate_limit_store[client_ip] = timestamps
        return False

    timestamps.append(now)
    _anonymous_rate_limit_store[client_ip] = timestamps
    return True


def _get_client_ip(request: Request) -> str:
    """Extract the client IP address from the request.

    Only trusts X-Forwarded-For header when TRUSTED_PROXY is enabled in settings.
    This prevents IP spoofing attacks to bypass rate limiting.

    Args:
        request: The FastAPI request object.

    Returns:
        The client's IP address.
    """
    # Only trust X-Forwarded-For when running behind a trusted proxy
    if getattr(settings, "TRUSTED_PROXY", False):
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


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
        description="LLM provider (gemini, vertex)",
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

    has_byok = bool(request.api_key)
    if not has_byok:
        api_key_repo = APIKeyRepository()
        user_keys = await api_key_repo.get_status(user.id)
        has_byok = any(
            k.get("provider") == "google" and k.get("encrypted_key") for k in user_keys
        )

    quota_result = await check_quota(
        user_id=user.id,
        role=user.role,
        plan=user.plan,
        evaluation_mode=request.evaluation_mode,
        has_byok=has_byok,
    )

    if not quota_result.allowed:
        error_msg = quota_result.reason
        if quota_result.suggestion:
            error_msg = f"{error_msg}. {quota_result.suggestion}"
        raise CorkedError(error_msg)

    try:
        eval_id = await start_evaluation(
            repo_url=request.repo_url,
            criteria=request.criteria,
            user_id=user.id,
            custom_criteria=request.custom_criteria,
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

        ETA_SECONDS = {
            "six_sommeliers": 30,
            "grand_tasting": 60,
            "full_techniques": 600,
        }
        estimated = ETA_SECONDS.get(request.evaluation_mode, 60)
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
        logger.error(f"[Evaluate] Traceback: {traceback.format_exc()}")
        raise CorkedError(f"Failed to start evaluation: {e!s}") from e


@router.post("/public", response_model=EvaluateResponse)
async def create_public_evaluation(
    request: EvaluateRequest,
    req: Request,
) -> EvaluateResponse:
    """Start anonymous evaluation for public repositories.

    This endpoint allows unauthenticated users to evaluate public GitHub repositories.
    Constraints:
    - Only six_sommeliers mode allowed
    - Only public GitHub repos (verified server-side)
    - Forced model: gemini-3-flash-preview
    - No BYOK/provider/model/temperature overrides
    - Rate limited by IP (5 evaluations per hour)

    Args:
        request: The evaluation request containing repo_url and criteria.
        req: The FastAPI request object for IP-based rate limiting.

    Returns:
        EvaluateResponse with evaluation_id and status.

    Raises:
        CorkedError: If rate limit exceeded, repo is private, or evaluation fails.
    """
    client_ip = _get_client_ip(req)
    logger.info(
        f"[Evaluate Public] Request from {client_ip}: repo_url={request.repo_url}"
    )

    if not _check_anonymous_rate_limit(client_ip):
        logger.warning(f"[Evaluate Public] Rate limit exceeded for IP: {client_ip}")
        raise CorkedError(
            "Rate limit exceeded. Please try again later or login for unlimited access."
        )

    await verify_public_repo(request.repo_url)

    try:
        eval_id = await start_evaluation(
            repo_url=request.repo_url,
            criteria=request.criteria,
            user_id="anonymous",
            custom_criteria=None,  # Anonymous users cannot use custom criteria
            evaluation_mode="six_sommeliers",
        )

        event_channel = get_event_channel()
        await event_channel.create_channel(eval_id)

        async def run_in_background():
            try:
                await run_evaluation_pipeline_with_events(
                    evaluation_id=eval_id,
                    repo_url=request.repo_url,
                    criteria=request.criteria,
                    user_id="anonymous",
                    evaluation_mode="six_sommeliers",
                    provider="gemini",
                    model="gemini-3-flash-preview",
                    temperature=None,
                    api_key=None,
                    github_token=None,
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

        logger.info(f"[Evaluate Public] Background task started: {eval_id}")

        return EvaluateResponse(
            evaluation_id=eval_id,
            status="pending",
            evaluation_mode="six_sommeliers",
            estimated_time=30,
        )
    except CorkedError as e:
        logger.error(f"[Evaluate Public] CorkedError: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"[Evaluate Public] Exception: {type(e).__name__}: {str(e)}")
        logger.error(f"[Evaluate Public] Traceback: {traceback.format_exc()}")
        raise CorkedError(f"Failed to start evaluation: {e!s}") from e


@router.get("/{evaluation_id}/stream")
async def stream_evaluation(
    evaluation_id: str,
    user=Depends(get_optional_user),
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

    Anonymous evaluations (user_id == "anonymous") can be accessed without
    authentication. Authenticated users can only access their own evaluations.
    """
    try:
        progress = await get_evaluation_progress(evaluation_id)
    except EmptyCellarError:
        raise EmptyCellarError(f"Evaluation not found: {evaluation_id}") from None

    eval_user_id = progress.get("user_id")

    # Access control logic:
    # 1. Anonymous evaluations are publicly accessible (no auth required)
    # 2. Authenticated users can access their own evaluations
    # 3. Authenticated users can also view anonymous evaluations
    if eval_user_id == "anonymous":
        pass  # Public access allowed
    elif user is None:
        raise CorkedError("Authentication required to view this evaluation")
    elif user.id != eval_user_id:
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

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# Demo evaluation IDs that can be accessed without authentication
PUBLIC_DEMO_EVALUATIONS = {
    "6986e6d6650de8503772babf",  # ai/nanoid evaluation
}


@router.get("/{evaluation_id}/result", response_model=ResultResponse)
async def get_result(
    evaluation_id: str,
    user=Depends(get_optional_user),
) -> ResultResponse:
    """Get the results of a completed evaluation.

    This endpoint returns the complete evaluation results including
    the final verdict from Jean-Pierre and all sommelier outputs.

    Public demo evaluations (in PUBLIC_DEMO_EVALUATIONS) and anonymous
    evaluations (user_id == "anonymous") can be accessed without authentication.

    Args:
        evaluation_id: The evaluation ID.
        user: The authenticated user (optional for public access).

    Returns:
        The evaluation results.

    Raises:
        EmptyCellarError: If the evaluation is not found.
        CorkedError: If the evaluation is still in progress.
    """
    is_public_demo = evaluation_id in PUBLIC_DEMO_EVALUATIONS

    if is_public_demo:
        result = await get_evaluation_result(evaluation_id)
        if result is None:
            raise EmptyCellarError(f"Evaluation result not found: {evaluation_id}")
        return ResultResponse(
            evaluation_id=result["evaluation_id"],
            final_evaluation=result["final_evaluation"],
            created_at=str(result["created_at"]),
        )

    try:
        progress = await get_evaluation_progress(evaluation_id)
    except EmptyCellarError:
        raise EmptyCellarError(f"Evaluation not found: {evaluation_id}") from None

    eval_user_id = progress.get("user_id")

    # Access control: same logic as stream_evaluation
    if eval_user_id == "anonymous":
        pass  # Public access allowed
    elif user is None:
        raise CorkedError("Authentication required to view this evaluation")
    elif user.id != eval_user_id:
        raise CorkedError("Access denied: evaluation belongs to another user")

    result = await get_evaluation_result(evaluation_id)

    if result is None:
        raise EmptyCellarError(f"Evaluation result not found: {evaluation_id}")

    return ResultResponse(
        evaluation_id=result["evaluation_id"],
        final_evaluation=result["final_evaluation"],
        created_at=str(result["created_at"]),
    )
