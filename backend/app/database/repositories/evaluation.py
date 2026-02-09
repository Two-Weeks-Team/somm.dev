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

    async def create_evaluation(self, eval_data: dict | EvaluationCreate) -> str:
        """Create a new evaluation in the database.

        Args:
            eval_data: The evaluation data to create.

        Returns:
            The created evaluation ID as a string.
        """
        from bson import ObjectId

        now = datetime.utcnow()
        if isinstance(eval_data, EvaluationCreate):
            document = {
                "_id": ObjectId(),
                **eval_data.model_dump(),
                "status": EvaluationStatus.pending,
                "created_at": now,
                "updated_at": now,
            }
        else:
            document = {
                "_id": ObjectId(),
                **eval_data,
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
        status: EvaluationStatus | str,
        error_message: Optional[str] = None,
    ) -> Optional[dict]:
        """Update the status of an evaluation.

        Args:
            eval_id: The evaluation ID to update.
            status: The new status (enum or string).
            error_message: Optional error message if status is 'failed'.

        Returns:
            The updated evaluation document or None if not found.
        """
        from bson import ObjectId

        # Handle both enum and string status
        status_value = status.value if isinstance(status, EvaluationStatus) else status

        update_data = {
            "status": status_value,
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

    async def save_full_technique_result(self, result: dict) -> str:
        """Save a full_techniques evaluation result.

        Args:
            result: Dictionary containing the full_technique result data.
                   Must include 'evaluation_id' and 'repo_url' fields.

        Returns:
            The ID of the saved result document as a string.

        Raises:
            ValueError: If evaluation_id or repo_url is missing from result.
        """
        from bson import ObjectId

        if not result.get("evaluation_id"):
            raise ValueError("evaluation_id is required")
        if not result.get("repo_url"):
            raise ValueError("repo_url is required")

        now = datetime.utcnow()
        document = {
            "_id": ObjectId(),
            **result,
            "created_at": now,
        }

        result_coll = self.collection.database["full_technique_results"]
        insert_result = await result_coll.insert_one(document)
        return str(insert_result.inserted_id)

    async def get_full_technique_result(self, evaluation_id: str) -> dict | None:
        """Retrieve a full_techniques evaluation result by evaluation ID.

        Args:
            evaluation_id: The evaluation ID to search for.

        Returns:
            The result document as a dictionary, or None if not found.
        """
        result_coll = self.collection.database["full_technique_results"]
        return await result_coll.find_one({"evaluation_id": evaluation_id})
