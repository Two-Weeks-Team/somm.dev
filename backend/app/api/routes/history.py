"""History API routes for viewing evaluation history.

This module provides endpoints for:
- Listing user evaluation history (GET /history)
"""

from typing import Any, List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.services.evaluation_service import get_user_history

router = APIRouter(prefix="/history", tags=["history"])


class HistoryItem(BaseModel):
    """Model for a single history item."""

    id: str
    repo_context: dict[str, Any]
    criteria: str
    status: str
    created_at: str
    score: int | None = None
    rating_tier: str | None = None


class HistoryResponse(BaseModel):
    """Response model for history list."""

    items: List[HistoryItem]
    total: int
    skip: int
    limit: int


@router.get("", response_model=HistoryResponse)
async def list_history(
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of records to return",
    ),
    user=Depends(get_current_user),
) -> HistoryResponse:
    """List the user's evaluation history.

    This endpoint returns a paginated list of the user's past evaluations,
    sorted by creation date in descending order (most recent first).

    Args:
        skip: Number of records to skip for pagination.
        limit: Maximum number of records to return.
        user: The authenticated user.

    Returns:
        A paginated list of evaluation history items.
    """
    history = await get_user_history(skip=skip, limit=limit)

    items = []
    for h in history:
        item = HistoryItem(
            id=h["id"],
            repo_context=h.get("repo_context", {}),
            criteria=h["criteria"],
            status=h["status"],
            created_at=str(h["created_at"]),
            score=h.get("score"),
            rating_tier=h.get("rating_tier"),
        )
        items.append(item)

    return HistoryResponse(
        items=items,
        total=len(items),
        skip=skip,
        limit=limit,
    )
