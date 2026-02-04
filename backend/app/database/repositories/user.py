"""User repository module.

This module provides the UserRepository class for user-related
database operations on MongoDB.
"""

from datetime import datetime
from typing import Optional

from app.database.repositories.base import BaseRepository
from app.models.user import UserCreate, UserInDB


class UserRepository(BaseRepository[UserInDB]):
    """Repository for user-related database operations.

    This class extends BaseRepository with user-specific operations.
    """

    collection_name: str = "users"
    model_cls = UserInDB

    async def get_by_github_id(self, github_id: int) -> Optional[dict]:
        """Find a user by their GitHub ID.

        Args:
            github_id: The GitHub user ID to search for.

        Returns:
            The user document or None if not found.
        """
        return await self.collection.find_one({"github_id": github_id})

    async def create_user(self, user_data: UserCreate) -> str:
        """Create a new user in the database.

        Args:
            user_data: The user data to create.

        Returns:
            The created user ID as a string.
        """
        from bson import ObjectId

        now = datetime.utcnow()
        document = {
            "_id": ObjectId(),
            **user_data.model_dump(),
            "created_at": now,
        }
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def update_user(self, user_id: str, update_data: dict) -> Optional[dict]:
        """Update a user by their ID.

        Args:
            user_id: The user ID to update.
            update_data: Dictionary of fields to update.

        Returns:
            The updated user document or None if not found.
        """
        from bson import ObjectId

        update_data["updated_at"] = datetime.utcnow()
        return await self.collection.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": update_data},
            return_document=True,
        )
