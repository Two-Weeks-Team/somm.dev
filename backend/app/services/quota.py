"""Quota checking service for usage limits.

This module provides quota management for different user tiers and evaluation modes.
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

# Tier/mode daily limits (server-key usage only)
QUOTA_RULES = {
    "free": {"six_sommeliers": 2, "grand_tasting": 2, "full_techniques": 0},
    "premium": {"six_sommeliers": 5, "grand_tasting": 5, "full_techniques": 5},
    "pro": {"six_sommeliers": 5, "grand_tasting": 5, "full_techniques": 5},
    "admin": {
        "six_sommeliers": -1,
        "grand_tasting": -1,
        "full_techniques": -1,
    },  # -1 = unlimited
}


@dataclass
class QuotaResult:
    """Result of a quota check operation."""

    allowed: bool
    reason: str
    remaining: int = 0
    daily_limit: int = 0
    used_today: int = 0
    suggestion: Optional[str] = None


async def check_quota(
    user_id: str,
    role: str,
    plan: str,
    evaluation_mode: str,
    has_byok: bool = False,
) -> QuotaResult:
    """Check if user can start a new evaluation.

    Priority:
    1. Admin → always allowed
    2. BYOK user → always allowed (using their own key)
    3. Check daily limit based on plan + mode

    Args:
        user_id: The user's ID
        role: User role (user, admin)
        plan: Subscription plan (free, premium, pro)
        evaluation_mode: The evaluation mode to check
        has_byok: Whether user has BYOK (Bring Your Own Key) configured

    Returns:
        QuotaResult with check results
    """
    # Admin bypass
    if role == "admin":
        return QuotaResult(
            allowed=True, reason="Admin: unlimited access", remaining=-1, daily_limit=-1
        )

    # BYOK bypass
    if has_byok:
        return QuotaResult(
            allowed=True,
            reason="BYOK: using your own API key",
            remaining=-1,
            daily_limit=-1,
        )

    # Get quota rules for plan
    rules = QUOTA_RULES.get(plan, QUOTA_RULES["free"])
    daily_limit = rules.get(evaluation_mode, 0)

    # full_techniques requires BYOK for free tier
    if daily_limit == 0:
        return QuotaResult(
            allowed=False,
            reason=f"'{evaluation_mode}' requires BYOK or plan upgrade for {plan} tier",
            remaining=0,
            daily_limit=0,
            used_today=0,
            suggestion="Register your Gemini API key at /settings/api-keys or upgrade your plan",
        )

    # Unlimited for paid admins
    if daily_limit == -1:
        return QuotaResult(
            allowed=True,
            reason=f"{plan}: unlimited access",
            remaining=-1,
            daily_limit=-1,
        )

    # Count today's evaluations
    used_today = await _count_today_evaluations(user_id, evaluation_mode)

    remaining = max(0, daily_limit - used_today)
    if used_today >= daily_limit:
        return QuotaResult(
            allowed=False,
            reason=f"Daily limit reached: {used_today}/{daily_limit} for {evaluation_mode}",
            remaining=0,
            daily_limit=daily_limit,
            used_today=used_today,
            suggestion="Register your Gemini API key for unlimited access, or wait until tomorrow (UTC 00:00)",
        )

    return QuotaResult(
        allowed=True,
        reason=f"Quota OK: {used_today}/{daily_limit}",
        remaining=remaining,
        daily_limit=daily_limit,
        used_today=used_today,
    )


async def _count_today_evaluations(user_id: str, evaluation_mode: str) -> int:
    """Count evaluations for the user today (UTC)."""
    from app.database.repositories.evaluation import EvaluationRepository

    repo = EvaluationRepository()
    today_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    count = await repo.collection.count_documents(
        {
            "user_id": user_id,
            "created_at": {"$gte": today_start},
            "$or": [
                {"mode": evaluation_mode},
                {"evaluation_mode": evaluation_mode},
            ],
        }
    )
    return count
