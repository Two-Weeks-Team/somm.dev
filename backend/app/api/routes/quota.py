"""Quota API routes for checking user usage limits.

This module provides endpoints for:
- Checking quota status for evaluation modes (GET /api/quota/status)
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from app.api.deps import get_current_user, User
from app.database.repositories.api_key import APIKeyRepository
from app.services.quota import check_quota, QUOTA_RULES

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/quota", tags=["quota"])


class QuotaStatusResponse(BaseModel):
    """Response model for quota status."""

    evaluation_mode: str = Field(description="The evaluation mode checked")
    allowed: bool = Field(description="Whether user can start this evaluation")
    reason: str = Field(description="Human-readable explanation")
    remaining: int = Field(description="Remaining evaluations today (-1 = unlimited)")
    daily_limit: int = Field(description="Daily limit for this mode (-1 = unlimited)")
    used_today: int = Field(description="Evaluations used today")
    suggestion: Optional[str] = Field(
        default=None, description="Suggestion for when quota is exceeded"
    )
    has_byok: bool = Field(description="Whether user has BYOK configured")
    plan: str = Field(description="User's current plan")


class AllQuotaStatusResponse(BaseModel):
    """Response model for all quota statuses."""

    user_id: str
    plan: str
    role: str
    has_byok: bool
    quotas: dict[str, QuotaStatusResponse]


@router.get("/status", response_model=AllQuotaStatusResponse)
async def get_quota_status(
    user: User = Depends(get_current_user),
    evaluation_mode: Optional[str] = Query(
        default=None,
        description="Specific evaluation mode to check (six_sommeliers, grand_tasting, full_techniques)",
    ),
) -> AllQuotaStatusResponse:
    """Get quota status for the current user.

    Returns quota information for all evaluation modes, or a specific mode
    if the evaluation_mode query parameter is provided.

    Args:
        user: The authenticated user.
        evaluation_mode: Optional specific mode to check.

    Returns:
        Quota status for all modes or the specified mode.
    """
    api_key_repo = APIKeyRepository()
    user_keys = await api_key_repo.get_status(user.id)
    has_byok = any(
        k.get("provider") == "google" and k.get("encrypted_key") for k in user_keys
    )

    modes = (
        [evaluation_mode]
        if evaluation_mode
        else ["six_sommeliers", "grand_tasting", "full_techniques"]
    )

    quotas = {}
    for mode in modes:
        result = await check_quota(
            user_id=user.id,
            role=user.role,
            plan=user.plan,
            evaluation_mode=mode,
            has_byok=has_byok,
        )
        quotas[mode] = QuotaStatusResponse(
            evaluation_mode=mode,
            allowed=result.allowed,
            reason=result.reason,
            remaining=result.remaining,
            daily_limit=result.daily_limit,
            used_today=result.used_today,
            suggestion=result.suggestion,
            has_byok=has_byok,
            plan=user.plan,
        )

    return AllQuotaStatusResponse(
        user_id=user.id,
        plan=user.plan,
        role=user.role,
        has_byok=has_byok,
        quotas=quotas,
    )


@router.get("/limits")
async def get_quota_limits(
    user: User = Depends(get_current_user),
) -> dict:
    """Get quota limits configuration for reference.

    Returns the quota rules for all plans and modes.

    Args:
        user: The authenticated user.

    Returns:
        Dictionary of quota rules by plan.
    """
    return {
        "current_plan": user.plan,
        "current_role": user.role,
        "rules": QUOTA_RULES,
        "notes": {
            "-1": "Unlimited evaluations",
            "0": "Requires BYOK or plan upgrade",
        },
    }
