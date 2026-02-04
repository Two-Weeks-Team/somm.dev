"""Result repository module.

This module provides the ResultRepository class for result-related
database operations on MongoDB.
"""

from datetime import datetime
from typing import List, Optional

from app.database.repositories.base import BaseRepository
from app.models.results import ResultInDB


class ResultRepository(BaseRepository[ResultInDB]):
    """Repository for result-related database operations.

    This class extends BaseRepository with result-specific operations.
    """

    collection_name: str = "results"
    model_cls = ResultInDB

    async def create_result(self, result_data: dict) -> str:
        """Create a new result in the database.

        Args:
            result_data: The result data containing evaluation_id and final_evaluation.

        Returns:
            The created result ID as a string.
        """
        from bson import ObjectId

        now = datetime.utcnow()
        document = {
            "_id": ObjectId(),
            **result_data,
            "created_at": now,
        }
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def get_by_evaluation_id(self, evaluation_id: str) -> Optional[dict]:
        """Find a result by evaluation ID.

        Args:
            evaluation_id: The evaluation ID to search for.

        Returns:
            The result document or None if not found.
        """
        return await self.collection.find_one({"evaluation_id": evaluation_id})

    async def list_by_user(
        self, user_id: str, limit: int = 50, skip: int = 0
    ) -> List[dict]:
        """List results for a user by joining with evaluations collection.

        Args:
            user_id: The user ID to filter by.
            limit: Maximum number of documents to return.
            skip: Number of documents to skip.

        Returns:
            List of result documents with evaluation info.
        """
        from app.database.repositories.evaluation import EvaluationRepository

        eval_repo = EvaluationRepository()
        evaluations = await eval_repo.list_by_user(user_id, limit=limit, skip=skip)

        results = []
        for eval_doc in evaluations:
            result = await self.get_by_evaluation_id(str(eval_doc.get("_id")))
            if result:
                results.append(result)

        return results

    async def update_result(self, result_id: str, update_data: dict) -> Optional[dict]:
        """Update a result by its ID.

        Args:
            result_id: The result ID to update.
            update_data: Dictionary of fields to update.

        Returns:
            The updated result document or None if not found.
        """
        from bson import ObjectId

        return await self.collection.find_one_and_update(
            {"_id": ObjectId(result_id)},
            {"$set": update_data},
            return_document=True,
        )

    async def get_latest_for_user(self, user_id: str) -> Optional[dict]:
        """Get the latest result for a user.

        Args:
            user_id: The user ID to search for.

        Returns:
            The latest result document or None if not found.
        """
        from app.database.repositories.evaluation import EvaluationRepository

        eval_repo = EvaluationRepository()
        evaluations = await eval_repo.list_by_user(user_id, limit=1)

        if not evaluations:
            return None

        eval_doc = evaluations[0]
        return await self.get_by_evaluation_id(str(eval_doc.get("_id")))
