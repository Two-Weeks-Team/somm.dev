import pytest
import time
from unittest.mock import AsyncMock, patch
from app.techniques.base_technique import BaseTechnique, TechniqueResult, RETRY_DELAYS
from app.techniques.schema import TechniqueDefinition, TechniqueCategory
from app.models.graph import ItemScore


class MockTechnique(BaseTechnique):
    """Concrete implementation for testing."""

    def __init__(self, definition, call_llm_fn=None, parse_fn=None):
        super().__init__(definition)
        self._call_llm_fn = call_llm_fn
        self._parse_fn = parse_fn

    async def _call_llm(self, state, item_id):
        if self._call_llm_fn:
            return await self._call_llm_fn(state, item_id)
        return {"score": 5, "rationale": "test"}

    def _parse_response(self, response, item_id):
        if self._parse_fn:
            return self._parse_fn(response, item_id)
        return {
            "item_scores": {
                item_id: ItemScore(
                    item_id=item_id,
                    score=response.get("score", 0),
                    evaluated_by=self.id,
                    technique_id=self.id,
                    timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    rationale=response.get("rationale"),
                    status="evaluated",
                )
            },
            "trace_events": [],
            "token_usage": {"prompt_tokens": 100, "completion_tokens": 50},
            "cost_usd": 0.001,
        }


@pytest.fixture
def sample_definition():
    return TechniqueDefinition(
        id="test-technique",
        name="Test Technique",
        category=TechniqueCategory.AROMA,
        promptTemplate="Evaluate {item_id}",
    )


@pytest.fixture
def sample_state():
    return {
        "github_url": "https://github.com/test/repo",
        "evaluation_mode": "six_sommeliers",
    }


class TestBaseTechniqueSuccess:
    @pytest.mark.asyncio
    async def test_successful_evaluation(self, sample_definition, sample_state):
        tech = MockTechnique(sample_definition)
        result = await tech.evaluate(sample_state, "A1")
        assert result.success is True
        assert "A1" in result.item_scores
        assert result.item_scores["A1"].score == 5
        assert result.token_usage == {"prompt_tokens": 100, "completion_tokens": 50}
        assert result.cost_usd == 0.001

    @pytest.mark.asyncio
    async def test_result_item_score_fields(self, sample_definition, sample_state):
        tech = MockTechnique(sample_definition)
        result = await tech.evaluate(sample_state, "A1")
        score = result.item_scores["A1"]
        assert score.evaluated_by == "test-technique"
        assert score.technique_id == "test-technique"
        assert score.status == "evaluated"
        assert score.rationale == "test"


class TestBaseTechniqueRetry:
    @pytest.mark.asyncio
    async def test_transient_failure_retries_then_succeeds(
        self, sample_definition, sample_state
    ):
        call_count = 0

        async def flaky_llm(state, item_id):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Transient error")
            return {"score": 5, "rationale": "recovered"}

        tech = MockTechnique(sample_definition, call_llm_fn=flaky_llm)
        with patch(
            "app.techniques.base_technique.asyncio.sleep", new_callable=AsyncMock
        ):
            result = await tech.evaluate(sample_state, "A1")
        assert result.success is True
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_permanent_failure_returns_error(
        self, sample_definition, sample_state
    ):
        async def always_fail(state, item_id):
            raise RuntimeError("Permanent failure")

        tech = MockTechnique(sample_definition, call_llm_fn=always_fail)
        with patch(
            "app.techniques.base_technique.asyncio.sleep", new_callable=AsyncMock
        ):
            result = await tech.evaluate(sample_state, "A1")
        assert result.success is False
        assert "Permanent failure" in result.error
        assert result.item_scores["A1"].status == "error"

    @pytest.mark.asyncio
    async def test_retry_count_matches_delays(self, sample_definition, sample_state):
        call_count = 0

        async def counting_fail(state, item_id):
            nonlocal call_count
            call_count += 1
            raise RuntimeError("fail")

        tech = MockTechnique(sample_definition, call_llm_fn=counting_fail)
        with patch(
            "app.techniques.base_technique.asyncio.sleep", new_callable=AsyncMock
        ):
            result = await tech.evaluate(sample_state, "A1")
        assert result.success is False
        assert call_count == len(RETRY_DELAYS)


class TestBaseTechniqueBYOK:
    def test_get_api_key_from_state(self, sample_definition):
        tech = MockTechnique(sample_definition)
        state = {"user_api_key": "AIza-test-key"}
        assert tech._get_api_key(state) == "AIza-test-key"

    def test_get_api_key_none_when_missing(self, sample_definition):
        tech = MockTechnique(sample_definition)
        assert tech._get_api_key({}) is None

    def test_get_api_key_source_default(self, sample_definition):
        tech = MockTechnique(sample_definition)
        assert tech._get_api_key_source({}) == "system"

    def test_get_api_key_source_user(self, sample_definition):
        tech = MockTechnique(sample_definition)
        state = {"api_key_source": "user"}
        assert tech._get_api_key_source(state) == "user"


class TestTechniqueResult:
    def test_default_values(self):
        result = TechniqueResult(technique_id="test")
        assert result.success is True
        assert result.error is None
        assert result.item_scores == {}
        assert result.trace_events == []
        assert result.cost_usd == 0.0
