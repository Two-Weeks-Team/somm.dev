import pytest
from unittest.mock import AsyncMock, MagicMock
from app.techniques.router import TechniqueRouter, AggregatedResult
from app.techniques.base_technique import TechniqueResult
from app.models.graph import ItemScore


@pytest.fixture
def router():
    return TechniqueRouter()


class TestSelectTechniques:
    def test_full_techniques_returns_75(self, router):
        selected = router.select_techniques("full_techniques")
        assert len(selected) == 75

    def test_six_sommeliers_returns_p0_p1(self, router):
        full = router.select_techniques("full_techniques")
        six = router.select_techniques("six_sommeliers")
        assert len(six) < len(full)
        assert len(six) > 0

    def test_grand_tasting_returns_p0(self, router):
        six = router.select_techniques("six_sommeliers")
        grand = router.select_techniques("grand_tasting")
        assert len(grand) <= len(six)
        assert len(grand) > 0

    def test_mode_count_ordering(self, router):
        grand = len(router.select_techniques("grand_tasting"))
        six = len(router.select_techniques("six_sommeliers"))
        full = len(router.select_techniques("full_techniques"))
        assert grand <= six <= full

    def test_category_filter(self, router):
        aroma = router.select_techniques("full_techniques", category="aroma")
        assert len(aroma) == 11
        all_techs = router.select_techniques("full_techniques")
        assert len(aroma) < len(all_techs)

    def test_hat_filter(self, router):
        white = router.select_techniques("full_techniques", hat="white")
        assert len(white) > 0
        full = router.select_techniques("full_techniques")
        assert len(white) < len(full)


class TestAggregateResults:
    def test_successful_results_aggregated(self, router):
        results = [
            TechniqueResult(
                technique_id="tech-1",
                success=True,
                item_scores={
                    "A1": ItemScore(
                        item_id="A1",
                        score=5,
                        evaluated_by="tech-1",
                        technique_id="tech-1",
                        timestamp="2025-01-01T00:00:00Z",
                        confidence="high",
                        status="evaluated",
                    )
                },
                trace_events=[],
                token_usage={"prompt_tokens": 100, "completion_tokens": 50},
                cost_usd=0.001,
            )
        ]
        agg = router.aggregate_results(results)
        assert "A1" in agg.item_scores
        assert agg.item_scores["A1"].score == 5
        assert "tech-1" in agg.techniques_used
        assert agg.total_cost_usd == 0.001

    def test_failed_technique_recorded(self, router):
        results = [
            TechniqueResult(technique_id="tech-fail", success=False, error="LLM error")
        ]
        agg = router.aggregate_results(results)
        assert len(agg.failed_techniques) == 1
        assert agg.failed_techniques[0]["technique_id"] == "tech-fail"

    def test_higher_confidence_wins(self, router):
        results = [
            TechniqueResult(
                technique_id="tech-1",
                success=True,
                item_scores={
                    "A1": ItemScore(
                        item_id="A1",
                        score=3,
                        evaluated_by="tech-1",
                        technique_id="tech-1",
                        timestamp="t1",
                        confidence="low",
                        status="evaluated",
                    )
                },
            ),
            TechniqueResult(
                technique_id="tech-2",
                success=True,
                item_scores={
                    "A1": ItemScore(
                        item_id="A1",
                        score=5,
                        evaluated_by="tech-2",
                        technique_id="tech-2",
                        timestamp="t2",
                        confidence="high",
                        status="evaluated",
                    )
                },
            ),
        ]
        agg = router.aggregate_results(results)
        assert agg.item_scores["A1"].score == 5
        assert agg.item_scores["A1"].confidence == "high"

    def test_mixed_success_failure(self, router):
        results = [
            TechniqueResult(
                technique_id="good",
                success=True,
                item_scores={
                    "A1": ItemScore(
                        item_id="A1",
                        score=5,
                        evaluated_by="good",
                        technique_id="good",
                        timestamp="t1",
                        status="evaluated",
                    )
                },
            ),
            TechniqueResult(technique_id="bad", success=False, error="crash"),
        ]
        agg = router.aggregate_results(results)
        assert "good" in agg.techniques_used
        assert len(agg.failed_techniques) == 1


class TestExecuteTechniques:
    @pytest.mark.asyncio
    async def test_execute_with_mock_factory(self):
        mock_result = TechniqueResult(
            technique_id="five-whys",
            success=True,
            item_scores={
                "A1": ItemScore(
                    item_id="A1",
                    score=5,
                    evaluated_by="five-whys",
                    technique_id="five-whys",
                    timestamp="t1",
                    status="evaluated",
                )
            },
        )
        mock_technique = MagicMock()
        mock_technique.evaluate = AsyncMock(return_value=mock_result)

        def factory(defn):
            return mock_technique

        router = TechniqueRouter(technique_factory=factory)
        results = await router.execute_techniques(["five-whys"], {})
        assert len(results) == 1
        assert results[0].success is True

    @pytest.mark.asyncio
    async def test_execute_failure_continues(self):
        call_count = 0

        async def failing_evaluate(state, item_id):
            nonlocal call_count
            call_count += 1
            raise RuntimeError("LLM error")

        mock_technique = MagicMock()
        mock_technique.evaluate = failing_evaluate

        router = TechniqueRouter(technique_factory=lambda d: mock_technique)
        results = await router.execute_techniques(["five-whys", "5w1h"], {})
        assert len(results) == 2
        assert all(not r.success for r in results)
        assert call_count == 2


class TestAggregatedResult:
    def test_default_values(self):
        agg = AggregatedResult()
        assert agg.item_scores == {}
        assert agg.techniques_used == []
        assert agg.failed_techniques == []
        assert agg.total_cost_usd == 0.0
