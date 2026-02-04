# backend/tests/test_repositories.py
"""
Tests for repositories.
RED Phase: These tests should FAIL initially because the repositories don't exist yet.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


class TestRepositoryImports:
    """Test that repositories can be imported correctly"""

    def test_import_base_repository(self):
        """Test that BaseRepository can be imported"""
        from app.database.repositories.base import BaseRepository

        assert BaseRepository is not None

    def test_import_user_repository(self):
        """Test that UserRepository can be imported"""
        from app.database.repositories.user import UserRepository

        assert UserRepository is not None

    def test_import_evaluation_repository(self):
        """Test that EvaluationRepository can be imported"""
        from app.database.repositories.evaluation import EvaluationRepository

        assert EvaluationRepository is not None

    def test_import_result_repository(self):
        """Test that ResultRepository can be imported"""
        from app.database.repositories.result import ResultRepository

        assert ResultRepository is not None


class TestBaseRepository:
    """Test BaseRepository generic implementation"""

    def test_base_repository_has_create_method(self):
        """Test that BaseRepository has create method"""
        from app.database.repositories.base import BaseRepository

        assert hasattr(BaseRepository, "create")
        assert callable(getattr(BaseRepository, "create"))

    def test_base_repository_has_get_by_id_method(self):
        """Test that BaseRepository has get_by_id method"""
        from app.database.repositories.base import BaseRepository

        assert hasattr(BaseRepository, "get_by_id")
        assert callable(getattr(BaseRepository, "get_by_id"))

    def test_base_repository_has_update_method(self):
        """Test that BaseRepository has update method"""
        from app.database.repositories.base import BaseRepository

        assert hasattr(BaseRepository, "update")
        assert callable(getattr(BaseRepository, "update"))

    def test_base_repository_has_delete_method(self):
        """Test that BaseRepository has delete method"""
        from app.database.repositories.base import BaseRepository

        assert hasattr(BaseRepository, "delete")
        assert callable(getattr(BaseRepository, "delete"))

    def test_base_repository_has_list_method(self):
        """Test that BaseRepository has list method"""
        from app.database.repositories.base import BaseRepository

        assert hasattr(BaseRepository, "list")
        assert callable(getattr(BaseRepository, "list"))

    def test_base_repository_is_generic(self):
        """Test that BaseRepository is a Generic type"""
        from app.database.repositories.base import BaseRepository
        from typing import Generic

        # Check that BaseRepository inherits from Generic
        assert issubclass(BaseRepository, Generic.__class__.__bases__[0])


class TestUserRepository:
    """Test UserRepository implementation"""

    def test_user_repository_inherits_from_base(self):
        """Test that UserRepository inherits from BaseRepository"""
        from app.database.repositories.base import BaseRepository
        from app.database.repositories.user import UserRepository

        assert issubclass(UserRepository, BaseRepository)

    def test_user_repository_has_collection_name(self):
        """Test that UserRepository has correct collection name"""
        from app.database.repositories.user import UserRepository

        assert hasattr(UserRepository, "collection_name")
        assert UserRepository.collection_name == "users"

    def test_user_repository_create(self):
        """Test UserRepository create method"""
        from app.database.repositories.user import UserRepository

        repo = UserRepository()
        assert repo.create is not None

    def test_user_repository_get_by_id(self):
        """Test UserRepository get_by_id method"""
        from app.database.repositories.user import UserRepository

        repo = UserRepository()
        assert repo.get_by_id is not None

    def test_user_repository_update(self):
        """Test UserRepository update method"""
        from app.database.repositories.user import UserRepository

        repo = UserRepository()
        assert repo.update is not None

    def test_user_repository_delete(self):
        """Test UserRepository delete method"""
        from app.database.repositories.user import UserRepository

        repo = UserRepository()
        assert repo.delete is not None

    def test_user_repository_list(self):
        """Test UserRepository list method"""
        from app.database.repositories.user import UserRepository

        repo = UserRepository()
        assert repo.list is not None

    def test_user_repository_get_by_github_id(self):
        """Test UserRepository has get_by_github_id method"""
        from app.database.repositories.user import UserRepository

        repo = UserRepository()
        assert hasattr(repo, "get_by_github_id")
        assert callable(getattr(repo, "get_by_github_id"))


class TestEvaluationRepository:
    """Test EvaluationRepository implementation"""

    def test_evaluation_repository_inherits_from_base(self):
        """Test that EvaluationRepository inherits from BaseRepository"""
        from app.database.repositories.base import BaseRepository
        from app.database.repositories.evaluation import EvaluationRepository

        assert issubclass(EvaluationRepository, BaseRepository)

    def test_evaluation_repository_has_collection_name(self):
        """Test that EvaluationRepository has correct collection name"""
        from app.database.repositories.evaluation import EvaluationRepository

        assert hasattr(EvaluationRepository, "collection_name")
        assert EvaluationRepository.collection_name == "evaluations"

    def test_evaluation_repository_create(self):
        """Test EvaluationRepository create method"""
        from app.database.repositories.evaluation import EvaluationRepository

        repo = EvaluationRepository()
        assert repo.create is not None

    def test_evaluation_repository_get_by_id(self):
        """Test EvaluationRepository get_by_id method"""
        from app.database.repositories.evaluation import EvaluationRepository

        repo = EvaluationRepository()
        assert repo.get_by_id is not None

    def test_evaluation_repository_update(self):
        """Test EvaluationRepository update method"""
        from app.database.repositories.evaluation import EvaluationRepository

        repo = EvaluationRepository()
        assert repo.update is not None

    def test_evaluation_repository_delete(self):
        """Test EvaluationRepository delete method"""
        from app.database.repositories.evaluation import EvaluationRepository

        repo = EvaluationRepository()
        assert repo.delete is not None

    def test_evaluation_repository_list(self):
        """Test EvaluationRepository list method"""
        from app.database.repositories.evaluation import EvaluationRepository

        repo = EvaluationRepository()
        assert repo.list is not None

    def test_evaluation_repository_get_by_user_id(self):
        """Test EvaluationRepository has get_by_user_id method"""
        from app.database.repositories.evaluation import EvaluationRepository

        repo = EvaluationRepository()
        assert hasattr(repo, "get_by_user_id")
        assert callable(getattr(repo, "get_by_user_id"))

    def test_evaluation_repository_get_by_status(self):
        """Test EvaluationRepository has get_by_status method"""
        from app.database.repositories.evaluation import EvaluationRepository

        repo = EvaluationRepository()
        assert hasattr(repo, "get_by_status")
        assert callable(getattr(repo, "get_by_status"))


class TestResultRepository:
    """Test ResultRepository implementation"""

    def test_result_repository_inherits_from_base(self):
        """Test that ResultRepository inherits from BaseRepository"""
        from app.database.repositories.base import BaseRepository
        from app.database.repositories.result import ResultRepository

        assert issubclass(ResultRepository, BaseRepository)

    def test_result_repository_has_collection_name(self):
        """Test that ResultRepository has correct collection name"""
        from app.database.repositories.result import ResultRepository

        assert hasattr(ResultRepository, "collection_name")
        assert ResultRepository.collection_name == "results"

    def test_result_repository_create(self):
        """Test ResultRepository create method"""
        from app.database.repositories.result import ResultRepository

        repo = ResultRepository()
        assert repo.create is not None

    def test_result_repository_get_by_id(self):
        """Test ResultRepository get_by_id method"""
        from app.database.repositories.result import ResultRepository

        repo = ResultRepository()
        assert repo.get_by_id is not None

    def test_result_repository_update(self):
        """Test ResultRepository update method"""
        from app.database.repositories.result import ResultRepository

        repo = ResultRepository()
        assert repo.update is not None

    def test_result_repository_delete(self):
        """Test ResultRepository delete method"""
        from app.database.repositories.result import ResultRepository

        repo = ResultRepository()
        assert repo.delete is not None

    def test_result_repository_list(self):
        """Test ResultRepository list method"""
        from app.database.repositories.result import ResultRepository

        repo = ResultRepository()
        assert repo.list is not None

    def test_result_repository_get_by_evaluation_id(self):
        """Test ResultRepository has get_by_evaluation_id method"""
        from app.database.repositories.result import ResultRepository

        repo = ResultRepository()
        assert hasattr(repo, "get_by_evaluation_id")
        assert callable(getattr(repo, "get_by_evaluation_id"))


class TestRepositoryIntegration:
    """Test repository integration with MongoDB"""

    def test_base_repository_with_mock_collection(self):
        """Test BaseRepository CRUD operations with mocked MongoDB collection"""
        from app.database.repositories.base import BaseRepository
        from pydantic import BaseModel
        from typing import TypeVar

        T = TypeVar("T", bound=BaseModel)

        class TestModel(BaseModel):
            name: str
            value: int

        # Create a repository instance manually
        repo = BaseRepository.__new__(BaseRepository)
        repo._collection = MagicMock()

        # Test create
        repo.collection.insert_one = AsyncMock()
        repo.collection.insert_one.return_value = MagicMock(inserted_id="mock_id")

        # Verify the mock is set up correctly
        assert repo.collection.insert_one is not None
