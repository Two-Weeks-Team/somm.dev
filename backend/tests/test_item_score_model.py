import pytest
from pydantic import ValidationError
from app.models.graph import ItemScore


class TestItemScoreModel:
    def test_old_style_item_score(self):
        score = ItemScore(
            item_id="test-item-1",
            score=85.0,
            evaluated_by="test-agent",
            technique_id="tech-1",
            timestamp="2026-02-09T10:00:00Z",
            notes="Test notes",
        )
        assert score.item_id == "test-item-1"
        assert score.score == 85.0
        assert score.evaluated_by == "test-agent"
        assert score.technique_id == "tech-1"
        assert score.timestamp == "2026-02-09T10:00:00Z"
        assert score.notes == "Test notes"
        assert score.item_name is None
        assert score.max_score is None

    def test_new_style_item_score_all_fields(self):
        score = ItemScore(
            item_id="test-item-2",
            score=7.0,
            evaluated_by="marcel",
            technique_id="bmad-1",
            timestamp="2026-02-09T10:00:00Z",
            notes="Detailed evaluation",
            item_name="Architecture Quality",
            max_score=7.0,
            status="evaluated",
            unevaluated_reason=None,
            hat_used="cellar_master",
            evidence=["ref1", "ref2"],
            rationale="Well structured codebase",
            confidence="high",
        )
        assert score.score == 7.0
        assert score.max_score == 7.0
        assert score.item_name == "Architecture Quality"
        assert score.hat_used == "cellar_master"
        assert score.evidence == ["ref1", "ref2"]

    def test_bmad_scale_score_valid(self):
        score = ItemScore(
            item_id="bmad-item",
            score=7.0,
            max_score=7.0,
            evaluated_by="agent",
            technique_id="bmad-tech",
            timestamp="2026-02-09T10:00:00Z",
        )
        assert score.score == 7.0
        assert score.max_score == 7.0

    def test_score_below_zero_fails(self):
        with pytest.raises(ValidationError) as exc_info:
            ItemScore(
                item_id="test-item",
                score=-1.0,
                evaluated_by="agent",
                technique_id="tech",
                timestamp="2026-02-09T10:00:00Z",
            )
        assert "score" in str(exc_info.value)

    def test_score_at_zero_valid(self):
        score = ItemScore(
            item_id="test-item",
            score=0.0,
            evaluated_by="agent",
            technique_id="tech",
            timestamp="2026-02-09T10:00:00Z",
        )
        assert score.score == 0.0

    def test_score_above_100_valid(self):
        score = ItemScore(
            item_id="test-item",
            score=150.0,
            evaluated_by="agent",
            technique_id="tech",
            timestamp="2026-02-09T10:00:00Z",
        )
        assert score.score == 150.0

    def test_partial_new_fields(self):
        score = ItemScore(
            item_id="test-item",
            score=5.0,
            evaluated_by="agent",
            technique_id="tech",
            timestamp="2026-02-09T10:00:00Z",
            item_name="Partial Test",
            confidence="medium",
        )
        assert score.item_name == "Partial Test"
        assert score.confidence == "medium"
        assert score.max_score is None
        assert score.evidence is None
