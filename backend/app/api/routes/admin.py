"""Admin API routes for user role/plan management.

Only accessible by users with role='admin' or listed in VERTEX_ADMIN_USER_IDS/EMAILS.
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import User, get_current_user
from app.database.repositories.user import UserRepository
from app.services.provider_routing import _is_admin

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

VALID_ROLES = {"user", "admin"}
VALID_PLANS = {"free", "premium", "pro", "enterprise"}


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Dependency that requires the current user to be an admin."""
    user_repo = UserRepository()
    user_doc = await user_repo.get_by_id(user.id)
    if not _is_admin(user_doc):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


class UserRoleUpdate(BaseModel):
    role: str | None = Field(None, description="User role (user, admin)")
    plan: str | None = Field(
        None, description="User plan (free, premium, pro, enterprise)"
    )


class AdminUserResponse(BaseModel):
    id: str
    username: str
    email: str | None = None
    github_id: str | None = None
    avatar_url: str | None = None
    role: str = "user"
    plan: str = "free"
    created_at: str | None = None


@router.get("/users", response_model=list[AdminUserResponse])
async def list_users(
    _admin: User = Depends(require_admin),
) -> list[AdminUserResponse]:
    """List all users with their roles and plans."""
    user_repo = UserRepository()
    users = await user_repo.list(limit=500)

    return [
        AdminUserResponse(
            id=str(u["_id"]),
            username=u.get("username", ""),
            email=u.get("email"),
            github_id=str(u.get("github_id", "")),
            avatar_url=u.get("avatar_url"),
            role=u.get("role", "user"),
            plan=u.get("plan", "free"),
            created_at=str(u.get("created_at", "")),
        )
        for u in users
    ]


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
async def update_user_role(
    user_id: str,
    update: UserRoleUpdate,
    _admin: User = Depends(require_admin),
) -> AdminUserResponse:
    """Update a user's role and/or plan."""
    update_data: dict[str, Any] = {}

    if update.role is not None:
        if update.role not in VALID_ROLES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid role: {update.role}. Must be one of {VALID_ROLES}",
            )
        update_data["role"] = update.role

    if update.plan is not None:
        if update.plan not in VALID_PLANS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid plan: {update.plan}. Must be one of {VALID_PLANS}",
            )
        update_data["plan"] = update.plan

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    user_repo = UserRepository()
    updated = await user_repo.update_user(user_id, update_data)

    if not updated:
        raise HTTPException(status_code=404, detail="User not found")

    logger.info(f"[Admin] User {user_id} updated: {update_data} by admin {_admin.id}")

    return AdminUserResponse(
        id=str(updated["_id"]),
        username=updated.get("username", ""),
        email=updated.get("email"),
        github_id=str(updated.get("github_id", "")),
        avatar_url=updated.get("avatar_url"),
        role=updated.get("role", "user"),
        plan=updated.get("plan", "free"),
        created_at=str(updated.get("created_at", "")),
    )
