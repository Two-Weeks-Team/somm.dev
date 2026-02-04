"""Base repository module for MongoDB operations.

This module provides a generic BaseRepository class for CRUD operations
on MongoDB collections using Motor async driver.
"""

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

from app.database.connection import get_database


T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """Generic base repository for MongoDB CRUD operations.

    This class provides common CRUD operations for any Pydantic model.
    Subclass this with a specific model to create a repository.

    Attributes:
        collection_name: Name of the MongoDB collection
        model_cls: The Pydantic model class for this repository
    """

    collection_name: str = ""
    model_cls: type[T]

    def __init__(self):
        """Initialize the repository with database connection."""
        self._collection = None

    @property
    def collection(self):
        """Get the MongoDB collection."""
        if self._collection is None:
            db = get_database()
            self._collection = db[self.collection_name]
        return self._collection

    async def create(self, document: dict) -> str:
        """Insert a new document into the collection.

        Args:
            document: Dictionary representation of the document to insert.

        Returns:
            The inserted document ID as a string.
        """
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def get_by_id(self, doc_id: str) -> Optional[dict]:
        """Retrieve a document by its ID.

        Args:
            doc_id: The document ID to search for.

        Returns:
            The document dictionary or None if not found.
        """
        from bson import ObjectId

        return await self.collection.find_one({"_id": ObjectId(doc_id)})

    async def update(self, doc_id: str, update_data: dict) -> Optional[dict]:
        """Update a document by its ID.

        Args:
            doc_id: The document ID to update.
            update_data: Dictionary of fields to update.

        Returns:
            The updated document dictionary or None if not found.
        """
        from bson import ObjectId

        result = await self.collection.find_one_and_update(
            {"_id": ObjectId(doc_id)},
            {"$set": update_data},
            return_document=True,
        )
        return result

    async def delete(self, doc_id: str) -> bool:
        """Delete a document by its ID.

        Args:
            doc_id: The document ID to delete.

        Returns:
            True if the document was deleted, False otherwise.
        """
        from bson import ObjectId

        result = await self.collection.delete_one({"_id": ObjectId(doc_id)})
        return result.deleted_count > 0

    async def list(
        self, query: Optional[dict] = None, limit: int = 100, skip: int = 0
    ) -> List[dict]:
        """List documents with optional filtering.

        Args:
            query: Optional filter query.
            limit: Maximum number of documents to return.
            skip: Number of documents to skip.

        Returns:
            List of document dictionaries.
        """
        query = query or {}
        cursor = self.collection.find(query).skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def find_one(self, query: dict) -> Optional[dict]:
        """Find a single document matching the query.

        Args:
            query: Filter query.

        Returns:
            The document dictionary or None if not found.
        """
        return await self.collection.find_one(query)
