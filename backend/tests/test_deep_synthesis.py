import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.graph.nodes.technique_categories.deep_synthesis import deep_synthesis
from app.graph.state import EvaluationState
from app.models.graph import ItemScore, TraceEvent


class TestDeepSynthesis:
    @pytest.mark.asyncio
    async def test_deep_synthesis_with_item_scores(self):
        item_scores = {
            "A1": ItemScore(
                item_id="A1",
                score=5.0,
                evaluated_by="test",
                technique_id="tech1",
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
            "A2": ItemScore(
                item_id="A2",
                score=4.0,
                evaluated_by="test",
                technique_id="tech2",
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
        }

        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user123",
            "item_scores": item_scores,
            "methodology_trace": [],
        }

        result = await deep_synthesis(state)

        assert "trace_metadata" in result
        assert "completed_sommeliers" in result
        assert result["completed_sommeliers"] == ["deep_synthesis"]

        deep_meta = result["trace_metadata"]["deep_synthesis"]
        assert deep_meta["total_items_scored"] == 2
        assert deep_meta["conflicts_detected"] == 0
        assert "completed_at" in deep_meta

    @pytest.mark.asyncio
    async def test_deep_synthesis_empty_item_scores(self):
        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user123",
            "item_scores": {},
            "methodology_trace": [],
        }

        result = await deep_synthesis(state)

        deep_meta = result["trace_metadata"]["deep_synthesis"]
        assert deep_meta["total_items_scored"] == 0

    @pytest.mark.asyncio
    async def test_deep_synthesis_detects_conflicts(self):
        trace_events = [
            TraceEvent(
                step=1,
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent="test_agent",
                technique_id="tech1",
                item_id="A1",
                action="score",
                score_delta=2.0,
            ),
            TraceEvent(
                step=2,
                timestamp=datetime.now(timezone.utc).isoformat(),
                agent="test_agent",
                technique_id="tech2",
                item_id="A1",
                action="score",
                score_delta=5.0,
            ),
        ]

        item_scores = {
            "A1": ItemScore(
                item_id="A1",
                score=5.0,
                evaluated_by="test",
                technique_id="tech2",
                timestamp=datetime.now(timezone.utc).isoformat(),
            ),
        }

        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user123",
            "item_scores": item_scores,
            "methodology_trace": trace_events,
        }

        result = await deep_synthesis(state)

        deep_meta = result["trace_metadata"]["deep_synthesis"]
        assert deep_meta["conflicts_detected"] == 1
        assert len(deep_meta["conflict_details"]) == 1
        conflict = deep_meta["conflict_details"][0]
        assert conflict["item_id"] == "A1"
        assert conflict["score_range"] == 3.0
