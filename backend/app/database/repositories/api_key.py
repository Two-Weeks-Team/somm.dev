"""API key repository for managing user API keys.

This module provides repository methods for storing, retrieving, and managing
encrypted API keys for external providers like Google Gemini.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional

from app.database.repositories.base import BaseRepository


class APIKeyRepository(BaseRepository):
    """Repository for API key storage and management.

    Handles CRUD operations for user API keys with automatic encryption
    and expiration tracking.
    """

    collection_name = "api_keys"

    async def save_key(
        self,
        user_id: str,
        provider: str,
        encrypted_key: str,
        key_hint: str,
        expires_at: Optional[datetime] = None,
    ) -> dict:
        """Save or update an API key for a user.

        Args:
            user_id: The user's unique identifier.
            provider: The API provider (e.g., 'google', 'openai').
            encrypted_key: The encrypted API key.
            key_hint: A hint showing the last 4 characters of the original key.
            expires_at: Optional expiration datetime (defaults to 90 days).

        Returns:
            The saved document as a dictionary.
        """
        if expires_at is None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=90)
        doc = {
            "user_id": user_id,
            "provider": provider,
            "encrypted_key": encrypted_key,
            "key_hint": key_hint,
            "expires_at": expires_at,
            "registered_at": datetime.now(timezone.utc),
            "last_used_at": None,
            "usage_count": 0,
        }
        await self.collection.update_one(
            {"user_id": user_id, "provider": provider},
            {"$set": doc},
            upsert=True,
        )
        return doc

    async def get_key(self, user_id: str, provider: str) -> Optional[dict]:
        """Retrieve a user's API key for a specific provider.

        Args:
            user_id: The user's unique identifier.
            provider: The API provider.

        Returns:
            The key document if found and not expired, None otherwise.
        """
        doc = await self.collection.find_one({"user_id": user_id, "provider": provider})
        if doc and doc.get("expires_at"):
            if doc["expires_at"] < datetime.now(timezone.utc):
                return None  # Expired
        return doc

    async def delete_key(self, user_id: str, provider: str) -> bool:
        """Delete a user's API key for a specific provider.

        Args:
            user_id: The user's unique identifier.
            provider: The API provider.

        Returns:
            True if a key was deleted, False otherwise.
        """
        result = await self.collection.delete_one(
            {"user_id": user_id, "provider": provider}
        )
        return result.deleted_count > 0

    async def get_status(self, user_id: str) -> list:
        """Get status of all API keys for a user.

        Args:
            user_id: The user's unique identifier.

        Returns:
            List of key documents for the user.
        """
        cursor = self.collection.find({"user_id": user_id})
        return await cursor.to_list(length=100)

    async def record_usage(self, user_id: str, provider: str) -> None:
        """Record usage of an API key.

        Updates the last_used_at timestamp and increments usage_count.

        Args:
            user_id: The user's unique identifier.
            provider: The API provider.
        """
        await self.collection.update_one(
            {"user_id": user_id, "provider": provider},
            {
                "$set": {"last_used_at": datetime.now(timezone.utc)},
                "$inc": {"usage_count": 1},
            },
        )

    async def refresh_expiry(
        self, user_id: str, provider: str, days: int = 90
    ) -> Optional[dict]:
        """Refresh the expiration date of an API key.

        Args:
            user_id: The user's unique identifier.
            provider: The API provider.
            days: Number of days to extend (default 90).

        Returns:
            The updated document or None if not found.
        """
        new_expiry = datetime.now(timezone.utc) + timedelta(days=days)
        result = await self.collection.find_one_and_update(
            {"user_id": user_id, "provider": provider},
            {"$set": {"expires_at": new_expiry}},
            return_document=True,
        )
        return result
