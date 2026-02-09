import pytest
from datetime import datetime, timezone

from app.graph.nodes.technique_categories.finalize import finalize
from app.graph.state import EvaluationState
from app.models.graph import ItemScore


class TestFinalizeNode:
    @pytest.mark.asyncio
    async def test_finalize_calculates_category_scores(self):
        item_scores = {
            "A1": ItemScore(
                item_id="A1",
                score=5.0,
                max_score=7,
                evaluated_by="test",
                technique_id="tech1",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="evaluated",
            ),
            "A2": ItemScore(
                item_id="A2",
                score=4.0,
                max_score=6,
                evaluated_by="test",
                technique_id="tech2",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="evaluated",
            ),
        }

        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user123",
            "item_scores": item_scores,
        }

        result = await finalize(state)

        assert "trace_metadata" in result
        assert "completed_sommeliers" in result
        assert result["completed_sommeliers"] == ["finalize"]

        finalize_meta = result["trace_metadata"]["finalize"]
        assert "category_scores" in finalize_meta
        assert finalize_meta["evaluated_count"] == 2

    @pytest.mark.asyncio
    async def test_finalize_quality_gate_pass(self):
        item_scores = {}
        all_items = [
            "A1",
            "A2",
            "A3",
            "A4",
            "B1",
            "B2",
            "B3",
            "B4",
            "C1",
            "C2",
            "C3",
            "C4",
            "C5",
            "D1",
            "D2",
            "D3",
            "D4",
        ]
        for item_id in all_items:
            item_scores[item_id] = ItemScore(
                item_id=item_id,
                score=6.0,
                max_score=6,
                evaluated_by="test",
                technique_id="tech1",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="evaluated",
            )

        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user123",
            "item_scores": item_scores,
        }

        result = await finalize(state)

        finalize_meta = result["trace_metadata"]["finalize"]
        assert finalize_meta["quality_gate"] == "PASS"
        assert finalize_meta["normalized_score"] >= 70

    @pytest.mark.asyncio
    async def test_finalize_quality_gate_concerns(self):
        item_scores = {}
        all_items = [
            "A1",
            "A2",
            "A3",
            "A4",
            "B1",
            "B2",
            "B3",
            "B4",
            "C1",
            "C2",
            "C3",
            "C4",
            "C5",
            "D1",
            "D2",
            "D3",
            "D4",
        ]
        for item_id in all_items:
            item_scores[item_id] = ItemScore(
                item_id=item_id,
                score=3.5,
                max_score=6,
                evaluated_by="test",
                technique_id="tech1",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="evaluated",
            )

        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user123",
            "item_scores": item_scores,
        }

        result = await finalize(state)

        finalize_meta = result["trace_metadata"]["finalize"]
        assert finalize_meta["quality_gate"] == "CONCERNS"
        assert 50 <= finalize_meta["normalized_score"] < 70

    @pytest.mark.asyncio
    async def test_finalize_quality_gate_fail(self):
        item_scores = {}
        all_items = [
            "A1",
            "A2",
            "A3",
            "A4",
            "B1",
            "B2",
            "B3",
            "B4",
            "C1",
            "C2",
            "C3",
            "C4",
            "C5",
            "D1",
            "D2",
            "D3",
            "D4",
        ]
        for item_id in all_items:
            item_scores[item_id] = ItemScore(
                item_id=item_id,
                score=2.0,
                max_score=6,
                evaluated_by="test",
                technique_id="tech1",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="evaluated",
            )

        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user123",
            "item_scores": item_scores,
        }

        result = await finalize(state)

        finalize_meta = result["trace_metadata"]["finalize"]
        assert finalize_meta["quality_gate"] == "FAIL"
        assert finalize_meta["normalized_score"] < 50

    @pytest.mark.asyncio
    async def test_finalize_quality_gate_incomplete_low_coverage(self):
        item_scores = {
            "A1": ItemScore(
                item_id="A1",
                score=6.0,
                max_score=6,
                evaluated_by="test",
                technique_id="tech1",
                timestamp=datetime.now(timezone.utc).isoformat(),
                status="evaluated",
            ),
        }

        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user123",
            "item_scores": item_scores,
        }

        result = await finalize(state)

        finalize_meta = result["trace_metadata"]["finalize"]
        assert finalize_meta["quality_gate"] == "INCOMPLETE"
        assert finalize_meta["coverage_rate"] < 0.5

    @pytest.mark.asyncio
    async def test_finalize_zero_items(self):
        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user123",
            "item_scores": {},
        }

        result = await finalize(state)

        finalize_meta = result["trace_metadata"]["finalize"]
        assert finalize_meta["total_score"] == 0.0
        assert finalize_meta["max_possible"] == 0
        assert finalize_meta["normalized_score"] == 0.0
        assert finalize_meta["coverage_rate"] == 0.0
        assert finalize_meta["quality_gate"] == "INCOMPLETE"
