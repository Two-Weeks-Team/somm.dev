"""Evaluation repository module.

This module provides the EvaluationRepository class for evaluation-related
database operations on MongoDB.
"""

from datetime import datetime
from typing import List, Optional

from app.database.repositories.base import BaseRepository
from app.models.evaluation import EvaluationCreate, EvaluationInDB, EvaluationStatus


class EvaluationRepository(BaseRepository[EvaluationInDB]):
    """Repository for evaluation-related database operations.

    This class extends BaseRepository with evaluation-specific operations.
    """

    collection_name: str = "evaluations"
    model_cls = EvaluationInDB

    async def create_evaluation(self, eval_data: EvaluationCreate) -> str:
        """Create a new evaluation in the database.

        Args:
            eval_data: The evaluation data to create.

        Returns:
            The created evaluation ID as a string.
        """
        from bson import ObjectId

        now = datetime.utcnow()
        document = {
            "_id": ObjectId(),
            **eval_data.model_dump(),
            "status": EvaluationStatus.pending,
            "created_at": now,
            "updated_at": now,
        }
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def get_by_user_id(self, user_id: str) -> List[dict]:
        """Find all evaluations by user ID.

        Args:
            user_id: The user ID to search for.

        Returns:
            List of evaluation documents.
        """
        cursor = self.collection.find({"user_id": user_id}).sort("created_at", -1)
        return await cursor.to_list(length=100)

    async def get_by_status(self, status: EvaluationStatus) -> List[dict]:
        """Find all evaluations with a specific status.

        Args:
            status: The evaluation status to filter by.

        Returns:
            List of evaluation documents.
        """
        cursor = self.collection.find({"status": status.value}).sort("created_at", -1)
        return await cursor.to_list(length=100)

    async def update_status(
        self,
        eval_id: str,
        status: EvaluationStatus,
        error_message: Optional[str] = None,
    ) -> Optional[dict]:
        """Update the status of an evaluation.

        Args:
            eval_id: The evaluation ID to update.
            status: The new status.
            error_message: Optional error message if status is 'failed'.

        Returns:
            The updated evaluation document or None if not found.
        """
        from bson import ObjectId

        update_data = {
            "status": status.value,
            "updated_at": datetime.utcnow(),
        }
        if error_message:
            update_data["error_message"] = error_message

        return await self.collection.find_one_and_update(
            {"_id": ObjectId(eval_id)},
            {"$set": update_data},
            return_document=True,
        )

    async def list_by_user(
        self, user_id: str, limit: int = 50, skip: int = 0
    ) -> List[dict]:
        """List evaluations for a user with pagination.

        Args:
            user_id: The user ID to filter by.
            limit: Maximum number of documents to return.
            skip: Number of documents to skip.

        Returns:
            List of evaluation documents.
        """
        cursor = (
            self.collection.find({"user_id": user_id})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        return await cursor.to_list(length=limit)
