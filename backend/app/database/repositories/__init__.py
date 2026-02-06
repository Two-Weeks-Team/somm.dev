"""Repositories package

This package contains all repository classes for database operations:
- base: Generic BaseRepository class
- user: UserRepository for user CRUD operations
- evaluation: EvaluationRepository for evaluation CRUD operations
- result: ResultRepository for result CRUD operations
"""

from app.database.repositories.base import BaseRepository
from app.database.repositories.user import UserRepository
from app.database.repositories.evaluation import EvaluationRepository
from app.database.repositories.result import ResultRepository
from app.database.repositories.graph_cache import GraphCacheRepository, create_indexes

__all__ = [
    "BaseRepository",
    "UserRepository",
    "EvaluationRepository",
    "ResultRepository",
    "GraphCacheRepository",
    "create_indexes",
]
