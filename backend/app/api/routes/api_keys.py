"""API routes for managing user API keys.

This module provides endpoints for registering, validating, and managing
encrypted API keys for external providers like Google Gemini.
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.api.deps import get_current_user, User
from app.database.repositories.api_key import APIKeyRepository
from app.services.encryption import EncryptionService
from app.services.key_validator import validate_api_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/keys", tags=["API Keys"])


class RegisterKeyRequest(BaseModel):
    """Request model for registering a new API key."""

    provider: str = "google"
    api_key: str


class KeyStatusResponse(BaseModel):
    """Response model for API key status."""

    provider: str
    key_hint: str
    registered_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    usage_count: int = 0


class RegisterKeyResponse(BaseModel):
    """Response model for successful key registration."""

    valid: bool
    key_hint: str
    provider: str
    expires_at: Optional[datetime] = None


class ValidateKeyRequest(BaseModel):
    """Request model for validating an API key."""

    provider: str = "google"
    api_key: str


class ValidateKeyResponse(BaseModel):
    """Response model for key validation."""

    valid: bool
    error: Optional[str] = None
    models_available: List[str] = []


@router.post("/register", response_model=RegisterKeyResponse)
async def register_key(
    request: RegisterKeyRequest, user: User = Depends(get_current_user)
):
    """Register a new API key for the current user.

    Validates the key with the provider, encrypts it, and stores it.

    Args:
        request: The registration request containing provider and API key.
        user: The authenticated user.

    Returns:
        Registration response with key hint and expiration.

    Raises:
        HTTPException: If the key is invalid.
    """
    validation = await validate_api_key(request.api_key, request.provider)
    if not validation.valid:
        raise HTTPException(
            status_code=400, detail=f"Invalid API key: {validation.error}"
        )

    enc = EncryptionService()
    encrypted = enc.encrypt(request.api_key)
    key_hint = f"...{request.api_key[-4:]}"

    repo = APIKeyRepository()
    doc = await repo.save_key(
        user_id=user.id,
        provider=request.provider,
        encrypted_key=encrypted,
        key_hint=key_hint,
    )
    return RegisterKeyResponse(
        valid=True,
        key_hint=key_hint,
        provider=request.provider,
        expires_at=doc.get("expires_at"),
    )


@router.get("/status", response_model=List[KeyStatusResponse])
async def get_key_status(user: User = Depends(get_current_user)):
    """Get status of all API keys for the current user.

    Args:
        user: The authenticated user.

    Returns:
        List of key status responses.
    """
    repo = APIKeyRepository()
    keys = await repo.get_status(user.id)
    return [
        KeyStatusResponse(
            provider=k.get("provider", "unknown"),
            key_hint=k.get("key_hint", "****"),
            registered_at=k.get("registered_at"),
            expires_at=k.get("expires_at"),
            last_used_at=k.get("last_used_at"),
            usage_count=k.get("usage_count", 0),
        )
        for k in keys
    ]


@router.delete("/{provider}")
async def delete_key(provider: str, user: User = Depends(get_current_user)):
    """Delete an API key for the current user.

    Args:
        provider: The API provider.
        user: The authenticated user.

    Returns:
        Deletion confirmation.

    Raises:
        HTTPException: If no key is found for the provider.
    """
    repo = APIKeyRepository()
    deleted = await repo.delete_key(user.id, provider)
    if not deleted:
        raise HTTPException(
            status_code=404, detail=f"No key found for provider: {provider}"
        )
    return {"deleted": True, "provider": provider}


@router.post("/validate", response_model=ValidateKeyResponse)
async def validate_key(
    request: ValidateKeyRequest, user: User = Depends(get_current_user)
):
    """Validate an API key without storing it.

    Args:
        request: The validation request containing provider and API key.
        user: The authenticated user.

    Returns:
        Validation response with status and available models.
    """
    result = await validate_api_key(request.api_key, request.provider)
    return ValidateKeyResponse(
        valid=result.valid,
        error=result.error,
        models_available=result.models_available,
    )


@router.post("/{provider}/refresh")
async def refresh_key(provider: str, user: User = Depends(get_current_user)):
    """Refresh the expiration of an existing API key.

    Re-validates the key with the provider and extends its expiration.

    Args:
        provider: The API provider.
        user: The authenticated user.

    Returns:
        Refresh confirmation with new expiration date.

    Raises:
        HTTPException: If no key is found or key is no longer valid.
    """
    repo = APIKeyRepository()
    doc = await repo.get_key(user.id, provider)
    if not doc:
        raise HTTPException(
            status_code=404, detail=f"No key found for provider: {provider}"
        )

    enc = EncryptionService()
    decrypted = enc.decrypt(doc["encrypted_key"])
    validation = await validate_api_key(decrypted, provider)
    if not validation.valid:
        raise HTTPException(
            status_code=400, detail=f"Key no longer valid: {validation.error}"
        )

    updated = await repo.refresh_expiry(user.id, provider)
    return {
        "refreshed": True,
        "provider": provider,
        "expires_at": updated.get("expires_at") if updated else None,
    }
