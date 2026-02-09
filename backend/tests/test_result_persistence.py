# backend/tests/test_result_persistence.py
"""Tests for FullTechniqueResult model and persistence."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch


class TestFullTechniqueResultModel:
    """Test FullTechniqueResult Pydantic model validation and defaults."""

    def test_model_validates_correctly(self):
        """FullTechniqueResult model validates correctly with required fields."""
        from app.models.evaluation import FullTechniqueResult

        result = FullTechniqueResult(
            evaluation_id="eval_123",
            repo_url="https://github.com/test/repo",
        )

        assert result.evaluation_id == "eval_123"
        assert result.repo_url == "https://github.com/test/repo"

    def test_model_defaults_applied(self):
        """FullTechniqueResult defaults applied (quality_gate='INCOMPLETE')."""
        from app.models.evaluation import FullTechniqueResult

        result = FullTechniqueResult(
            evaluation_id="eval_123",
            repo_url="https://github.com/test/repo",
        )

        assert result.quality_gate == "INCOMPLETE"
        assert result.evaluation_mode == "full_techniques"
        assert result.total_score == 0.0
        assert result.normalized_score == 0.0
        assert result.coverage == 0.0
        assert result.item_scores == {}
        assert result.dimension_scores == {}
        assert result.techniques_used == []
        assert result.failed_techniques == []
        assert result.hat_contributions == {}
        assert result.methodology_trace == []
        assert result.api_key_source == "system"
        assert result.cost_summary == {}
        assert result.duration_ms == 0

    def test_model_serialization_round_trip(self):
        """Model serialization round-trip preserves data."""
        from app.models.evaluation import FullTechniqueResult

        original = FullTechniqueResult(
            evaluation_id="eval_456",
            repo_url="https://github.com/test/repo",
            evaluation_mode="full_techniques",
            item_scores={"item_1": {"score": 85, "max": 100}},
            dimension_scores={"A": {"score": 80, "max": 100}},
            total_score=450.0,
            normalized_score=75.0,
            quality_gate="PASS",
            coverage=0.85,
            techniques_used=["tech_1", "tech_2"],
            failed_techniques=[{"id": "tech_3", "error": "timeout"}],
            hat_contributions={"marcel": ["tech_1"]},
            methodology_trace=[{"step": 1, "action": "start"}],
            api_key_source="user",
            cost_summary={"total": 0.05},
            duration_ms=5000,
        )

        serialized = original.model_dump()
        deserialized = FullTechniqueResult(**serialized)

        assert deserialized.evaluation_id == original.evaluation_id
        assert deserialized.repo_url == original.repo_url
        assert deserialized.quality_gate == original.quality_gate
        assert deserialized.total_score == original.total_score
        assert deserialized.item_scores == original.item_scores

    def test_model_all_17_item_scores_persisted(self):
        """All 17 item_scores fields are persisted correctly."""
        from app.models.evaluation import FullTechniqueResult

        item_scores = {f"item_{i}": {"score": i * 5, "max": 100} for i in range(1, 18)}

        result = FullTechniqueResult(
            evaluation_id="eval_789",
            repo_url="https://github.com/test/repo",
            item_scores=item_scores,
        )

        assert len(result.item_scores) == 17
        for i in range(1, 18):
            assert f"item_{i}" in result.item_scores
            assert result.item_scores[f"item_{i}"]["score"] == i * 5

    def test_model_evaluation_mode_field_present(self):
        """evaluation_mode field is present and defaults to 'full_techniques'."""
        from app.models.evaluation import FullTechniqueResult

        result = FullTechniqueResult(
            evaluation_id="eval_abc",
            repo_url="https://github.com/test/repo",
        )

        assert hasattr(result, "evaluation_mode")
        assert result.evaluation_mode == "full_techniques"

        result_custom = FullTechniqueResult(
            evaluation_id="eval_def",
            repo_url="https://github.com/test/repo",
            evaluation_mode="custom_mode",
        )
        assert result_custom.evaluation_mode == "custom_mode"

    def test_model_cost_summary_stored_correctly(self):
        """cost_summary is stored correctly with nested structure."""
        from app.models.evaluation import FullTechniqueResult

        cost_summary = {
            "total": 0.1234,
            "breakdown": {
                "marcel": 0.02,
                "isabella": 0.03,
            },
            "currency": "USD",
        }

        result = FullTechniqueResult(
            evaluation_id="eval_cost",
            repo_url="https://github.com/test/repo",
            cost_summary=cost_summary,
        )

        assert result.cost_summary == cost_summary
        assert result.cost_summary["total"] == 0.1234
        assert result.cost_summary["breakdown"]["marcel"] == 0.02


class TestEvaluationRepositoryFullTechniques:
    """Test EvaluationRepository extended methods for full_techniques."""

    @pytest.mark.asyncio
    async def test_save_full_technique_result_success(self):
        """Save and retrieve works with mock MongoDB."""
        from app.database.repositories.evaluation import EvaluationRepository

        repo = EvaluationRepository()

        mock_collection = AsyncMock()
        mock_collection.insert_one = AsyncMock(
            return_value=MagicMock(inserted_id="doc_123")
        )

        mock_db = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_collection.database = mock_db

        repo._collection = mock_collection

        result_data = {
            "evaluation_id": "eval_save_001",
            "repo_url": "https://github.com/test/repo",
            "evaluation_mode": "full_techniques",
            "total_score": 85.0,
        }

        result_id = await repo.save_full_technique_result(result_data)

        assert result_id == "doc_123"
        mock_collection.insert_one.assert_called_once()
        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["evaluation_id"] == "eval_save_001"
        assert "_id" in call_args
        assert "created_at" in call_args

    @pytest.mark.asyncio
    async def test_save_full_technique_result_missing_evaluation_id_raises(self):
        """Save raises ValueError when evaluation_id is missing."""
        from app.database.repositories.evaluation import EvaluationRepository

        repo = EvaluationRepository()

        result_data = {
            "repo_url": "https://github.com/test/repo",
        }

        with pytest.raises(ValueError, match="evaluation_id is required"):
            await repo.save_full_technique_result(result_data)

    @pytest.mark.asyncio
    async def test_save_full_technique_result_missing_repo_url_raises(self):
        """Save raises ValueError when repo_url is missing."""
        from app.database.repositories.evaluation import EvaluationRepository

        repo = EvaluationRepository()

        result_data = {
            "evaluation_id": "eval_001",
        }

        with pytest.raises(ValueError, match="repo_url is required"):
            await repo.save_full_technique_result(result_data)

    @pytest.mark.asyncio
    async def test_get_full_technique_result_found(self):
        """Get returns result document when found."""
        from app.database.repositories.evaluation import EvaluationRepository

        repo = EvaluationRepository()

        expected_doc = {
            "_id": "doc_456",
            "evaluation_id": "eval_get_001",
            "repo_url": "https://github.com/test/repo",
            "quality_gate": "PASS",
        }

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=expected_doc)

        mock_db = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_collection.database = mock_db

        repo._collection = mock_collection

        result = await repo.get_full_technique_result("eval_get_001")

        assert result == expected_doc
        mock_collection.find_one.assert_called_once_with(
            {"evaluation_id": "eval_get_001"}
        )

    @pytest.mark.asyncio
    async def test_get_full_technique_result_not_found(self):
        """Get returns None when result not found."""
        from app.database.repositories.evaluation import EvaluationRepository

        repo = EvaluationRepository()

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=None)

        mock_db = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_collection.database = mock_db

        repo._collection = mock_collection

        result = await repo.get_full_technique_result("non_existent_eval")

        assert result is None

    @pytest.mark.asyncio
    async def test_old_results_without_evaluation_mode_treated_as_six_sommeliers(self):
        """Old results without evaluation_mode field treated as 'six_sommeliers'."""
        from app.database.repositories.evaluation import EvaluationRepository

        repo = EvaluationRepository()

        old_doc = {
            "_id": "doc_old",
            "evaluation_id": "eval_old_001",
            "repo_url": "https://github.com/test/repo",
            "quality_gate": "PASS",
        }

        mock_collection = AsyncMock()
        mock_collection.find_one = AsyncMock(return_value=old_doc)

        mock_db = MagicMock()
        mock_db.__getitem__ = MagicMock(return_value=mock_collection)
        mock_collection.database = mock_db

        repo._collection = mock_collection

        result = await repo.get_full_technique_result("eval_old_001")

        assert result is not None
        assert "evaluation_mode" not in result
