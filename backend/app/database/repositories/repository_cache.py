"""Repository cache module for storing user GitHub repositories with TTL.

This module provides the RepositoryCacheRepository class for caching
user repository data with automatic expiration (TTL) support.
"""

from datetime import datetime, timedelta
from typing import List, Optional

from app.database.repositories.base import BaseRepository
from app.models.repository import RepositoryCache


class RepositoryCacheRepository(BaseRepository[RepositoryCache]):
    """Repository for caching user GitHub repositories with TTL.

    This repository stores user repository data in MongoDB with a TTL index
    that automatically removes expired cache entries after 1 hour.

    Attributes:
        collection_name: Name of the MongoDB collection
        model_cls: The RepositoryCache model class
        CACHE_TTL_SECONDS: Time-to-live in seconds (3600 = 1 hour)
    """

    collection_name: str = "user_repositories"
    model_cls = RepositoryCache
    CACHE_TTL_SECONDS: int = 3600  # 1 hour

    async def ensure_ttl_index(self):
        """Ensure TTL index exists on cached_at field.

        This method creates a TTL index if it doesn't exist.
        Should be called during application startup.
        """
        # Create TTL index on cached_at field
        # MongoDB will automatically delete documents after CACHE_TTL_SECONDS
        await self.collection.create_index(
            "cached_at",
            expireAfterSeconds=self.CACHE_TTL_SECONDS,
            name="cached_at_ttl"
        )

    async def get_user_repos(self, user_id: str) -> Optional[List[dict]]:
        """Get cached repositories for a user.

        Args:
            user_id: The MongoDB user ID.

        Returns:
            List of repository dictionaries or None if no cache exists.
        """
        cursor = self.collection.find({"user_id": user_id}).sort("cached_at", -1)
        repos = await cursor.to_list(length=None)

        if not repos:
            return None

        return repos

    async def set_user_repos(
        self, user_id: str, repos: List[dict]
    ) -> None:
        """Cache repositories for a user.

        This method:
        1. Clears existing cache for the user
        2. Inserts new repository documents with current timestamp

        Args:
            user_id: The MongoDB user ID.
            repos: List of repository data dictionaries.
        """
        # Clear existing cache for this user
        await self.clear_user_repos(user_id)

        if not repos:
            return

        # Prepare documents with user_id and cached_at
        now = datetime.utcnow()
        documents = []
        for repo in repos:
            doc = {
                **repo,
                "user_id": user_id,
                "cached_at": now,
            }
            documents.append(doc)

        # Insert all repositories
        if documents:
            await self.collection.insert_many(documents)

    async def clear_user_repos(self, user_id: str) -> int:
        """Clear cached repositories for a user.

        Args:
            user_id: The MongoDB user ID.

        Returns:
            Number of documents deleted.
        """
        result = await self.collection.delete_many({"user_id": user_id})
        return result.deleted_count

    async def is_cache_valid(self, user_id: str) -> bool:
        """Check if valid (non-expired) cache exists for user.

        Args:
            user_id: The MongoDB user ID.

        Returns:
            True if cache exists and is not expired, False otherwise.
        """
        # Since TTL index automatically removes expired documents,
        # we just need to check if any documents exist
        count = await self.collection.count_documents({"user_id": user_id})
        return count > 0

    async def get_cache_timestamp(self, user_id: str) -> Optional[datetime]:
        """Get the timestamp of the most recent cache entry for a user.

        Args:
            user_id: The MongoDB user ID.

        Returns:
            Timestamp of the most recent cache entry or None.
        """
        repo = await self.collection.find_one(
            {"user_id": user_id},
            sort=[("cached_at", -1)]
        )
        if repo:
            return repo.get("cached_at")
        return None
