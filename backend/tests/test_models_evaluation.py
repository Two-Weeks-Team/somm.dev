# backend/tests/test_models_evaluation.py
"""
Tests for Evaluation models.
RED Phase: These tests should FAIL initially because the evaluation model doesn't exist yet.
"""

import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))


class TestEvaluationModelImports:
    """Test that evaluation models can be imported correctly"""

    def test_import_evaluation_status_enum(self):
        """Test that EvaluationStatus enum can be imported"""
        from app.models.evaluation import EvaluationStatus

        assert EvaluationStatus is not None

    def test_import_evaluation_criteria_enum(self):
        """Test that EvaluationCriteria enum can be imported"""
        from app.models.evaluation import EvaluationCriteria

        assert EvaluationCriteria is not None

    def test_import_repo_context(self):
        """Test that RepoContext can be imported"""
        from app.models.evaluation import RepoContext

        assert RepoContext is not None

    def test_import_evaluation_create(self):
        """Test that EvaluationCreate can be imported"""
        from app.models.evaluation import EvaluationCreate

        assert EvaluationCreate is not None

    def test_import_evaluation_in_db(self):
        """Test that EvaluationInDB can be imported"""
        from app.models.evaluation import EvaluationInDB

        assert EvaluationInDB is not None

    def test_import_evaluation_response(self):
        """Test that EvaluationResponse can be imported"""
        from app.models.evaluation import EvaluationResponse

        assert EvaluationResponse is not None


class TestEvaluationStatusEnum:
    """Test EvaluationStatus enum values"""

    def test_evaluation_status_has_pending(self):
        """Test that EvaluationStatus has 'pending' value"""
        from app.models.evaluation import EvaluationStatus

        assert hasattr(EvaluationStatus, "pending")

    def test_evaluation_status_has_running(self):
        """Test that EvaluationStatus has 'running' value"""
        from app.models.evaluation import EvaluationStatus

        assert hasattr(EvaluationStatus, "running")

    def test_evaluation_status_has_completed(self):
        """Test that EvaluationStatus has 'completed' value"""
        from app.models.evaluation import EvaluationStatus

        assert hasattr(EvaluationStatus, "completed")

    def test_evaluation_status_has_failed(self):
        """Test that EvaluationStatus has 'failed' value"""
        from app.models.evaluation import EvaluationStatus

        assert hasattr(EvaluationStatus, "failed")


class TestEvaluationCriteriaEnum:
    """Test EvaluationCriteria enum values"""

    def test_evaluation_criteria_has_basic(self):
        """Test that EvaluationCriteria has 'basic' value"""
        from app.models.evaluation import EvaluationCriteria

        assert hasattr(EvaluationCriteria, "basic")

    def test_evaluation_criteria_has_hackathon(self):
        """Test that EvaluationCriteria has 'hackathon' value"""
        from app.models.evaluation import EvaluationCriteria

        assert hasattr(EvaluationCriteria, "hackathon")

    def test_evaluation_criteria_has_academic(self):
        """Test that EvaluationCriteria has 'academic' value"""
        from app.models.evaluation import EvaluationCriteria

        assert hasattr(EvaluationCriteria, "academic")

    def test_evaluation_criteria_has_custom(self):
        """Test that EvaluationCriteria has 'custom' value"""
        from app.models.evaluation import EvaluationCriteria

        assert hasattr(EvaluationCriteria, "custom")


class TestRepoContextModel:
    """Test RepoContext model"""

    def test_repo_context_has_repo_url(self):
        """Test that RepoContext has repo_url field"""
        from app.models.evaluation import RepoContext

        assert "repo_url" in RepoContext.__fields__

    def test_repo_context_has_branch(self):
        """Test that RepoContext has branch field"""
        from app.models.evaluation import RepoContext

        assert "branch" in RepoContext.__fields__

    def test_repo_context_has_commit_sha(self):
        """Test that RepoContext has commit_sha field"""
        from app.models.evaluation import RepoContext

        assert "commit_sha" in RepoContext.__fields__

    def test_repo_context_optional_fields(self):
        """Test that some fields in RepoContext are optional"""
        from app.models.evaluation import RepoContext

        # branch and commit_sha should be optional
        ctx = RepoContext(repo_url="https://github.com/user/repo")
        assert ctx.repo_url == "https://github.com/user/repo"
        assert ctx.branch is None
        assert ctx.commit_sha is None

    def test_repo_context_with_all_fields(self):
        """Test creating RepoContext with all fields"""
        from app.models.evaluation import RepoContext

        ctx = RepoContext(
            repo_url="https://github.com/user/repo",
            branch="main",
            commit_sha="abc123def456",
        )

        assert ctx.repo_url == "https://github.com/user/repo"
        assert ctx.branch == "main"
        assert ctx.commit_sha == "abc123def456"


class TestEvaluationCreateModel:
    """Test EvaluationCreate model"""

    def test_evaluation_create_has_repo_context(self):
        """Test that EvaluationCreate has repo_context field"""
        from app.models.evaluation import EvaluationCreate, RepoContext

        assert "repo_context" in EvaluationCreate.__fields__

    def test_evaluation_create_has_criteria(self):
        """Test that EvaluationCreate has criteria field"""
        from app.models.evaluation import EvaluationCreate

        assert "criteria" in EvaluationCreate.__fields__

    def test_evaluation_create_has_user_id(self):
        """Test that EvaluationCreate has user_id field"""
        from app.models.evaluation import EvaluationCreate

        assert "user_id" in EvaluationCreate.__fields__

    def test_evaluation_create_optional_custom_criteria(self):
        """Test that EvaluationCreate has optional custom_criteria field"""
        from app.models.evaluation import EvaluationCreate

        assert "custom_criteria" in EvaluationCreate.__fields__

    def test_evaluation_create_instance(self):
        """Test creating EvaluationCreate instance"""
        from app.models.evaluation import (
            EvaluationCreate,
            RepoContext,
            EvaluationCriteria,
        )

        create = EvaluationCreate(
            repo_context=RepoContext(repo_url="https://github.com/user/repo"),
            criteria=EvaluationCriteria.basic,
            user_id="user123",
        )

        assert create.repo_context.repo_url == "https://github.com/user/repo"
        assert create.criteria == EvaluationCriteria.basic
        assert create.user_id == "user123"


class TestEvaluationInDBModel:
    """Test EvaluationInDB model"""

    def test_evaluation_in_db_inherits_from_evaluation_create(self):
        """Test that EvaluationInDB inherits from EvaluationCreate"""
        from app.models.evaluation import EvaluationCreate, EvaluationInDB

        # Should have all EvaluationCreate fields
        assert "repo_context" in EvaluationInDB.__fields__
        assert "criteria" in EvaluationInDB.__fields__
        assert "user_id" in EvaluationInDB.__fields__

    def test_evaluation_in_db_has_id(self):
        """Test that EvaluationInDB has id field"""
        from app.models.evaluation import EvaluationInDB

        assert "id" in EvaluationInDB.__fields__

    def test_evaluation_in_db_has_status(self):
        """Test that EvaluationInDB has status field"""
        from app.models.evaluation import EvaluationInDB

        assert "status" in EvaluationInDB.__fields__

    def test_evaluation_in_db_has_created_at(self):
        """Test that EvaluationInDB has created_at field"""
        from app.models.evaluation import EvaluationInDB

        assert "created_at" in EvaluationInDB.__fields__

    def test_evaluation_in_db_has_updated_at(self):
        """Test that EvaluationInDB has updated_at field"""
        from app.models.evaluation import EvaluationInDB

        assert "updated_at" in EvaluationInDB.__fields__

    def test_evaluation_in_db_optional_error_message(self):
        """Test that EvaluationInDB has optional error_message field"""
        from app.models.evaluation import EvaluationInDB

        assert "error_message" in EvaluationInDB.__fields__


class TestEvaluationResponseModel:
    """Test EvaluationResponse model"""

    def test_evaluation_response_has_id(self):
        """Test that EvaluationResponse has id field"""
        from app.models.evaluation import EvaluationResponse

        assert "id" in EvaluationResponse.__fields__

    def test_evaluation_response_has_status(self):
        """Test that EvaluationResponse has status field"""
        from app.models.evaluation import EvaluationResponse

        assert "status" in EvaluationResponse.__fields__

    def test_evaluation_response_has_created_at(self):
        """Test that EvaluationResponse has created_at field"""
        from app.models.evaluation import EvaluationResponse

        assert "created_at" in EvaluationResponse.__fields__

    def test_evaluation_response_excludes_internal_fields(self):
        """Test that EvaluationResponse excludes sensitive internal fields"""
        from app.models.evaluation import EvaluationResponse

        # error_message should not be in response
        assert (
            "error_message" not in EvaluationResponse.__fields__
            or EvaluationResponse.__fields__["error_message"].is_required() == False
        )
