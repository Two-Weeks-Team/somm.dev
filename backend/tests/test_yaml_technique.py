import pytest
from app.techniques.yaml_technique import YAMLTechnique
from app.techniques.schema import TechniqueDefinition, TechniqueCategory
from app.models.graph import ItemScore, TraceEvent


@pytest.fixture
def five_whys_definition():
    """Load real five-whys YAML technique."""
    from app.techniques.loader import load_techniques

    techs, _ = load_techniques()
    for t in techs:
        if t.id == "five-whys":
            return t
    pytest.fail("five-whys technique not found")


@pytest.fixture
def simple_definition():
    return TechniqueDefinition(
        id="test-yaml-tech",
        name="Test YAML Technique",
        category=TechniqueCategory.AROMA,
        promptTemplate="Evaluate the following item: {item_id}",
    )


@pytest.fixture
def sample_state():
    return {
        "repo_context": {
            "repo_url": "https://github.com/test/repo",
            "readme": "# Test Project\nThis is a test.",
            "file_structure": "src/\n  main.py\n  utils.py",
        },
        "evaluation_mode": "six_sommeliers",
    }


@pytest.fixture
def mock_llm_response():
    return {
        "score": 5,
        "rationale": "Well-defined problem with clear scope",
        "evidence": ["README clearly states the problem", "Issue tracker organized"],
        "confidence": "high",
        "token_usage": {"prompt_tokens": 200, "completion_tokens": 100},
        "cost_usd": 0.002,
    }


class TestBuildPrompt:
    def test_prompt_includes_technique_name(self, simple_definition, sample_state):
        tech = YAMLTechnique(simple_definition)
        prompt = tech.build_prompt(sample_state, "A1")
        assert "Test YAML Technique" in prompt

    def test_prompt_includes_bmad_rubric(self, simple_definition, sample_state):
        tech = YAMLTechnique(simple_definition)
        prompt = tech.build_prompt(sample_state, "A1")
        assert "Problem Clarity" in prompt
        assert "Maximum Score: 7" in prompt

    def test_prompt_includes_repo_context(self, simple_definition, sample_state):
        tech = YAMLTechnique(simple_definition)
        prompt = tech.build_prompt(sample_state, "A1")
        assert "github.com/test/repo" in prompt
        assert "Test Project" in prompt

    def test_prompt_includes_output_format(self, simple_definition, sample_state):
        tech = YAMLTechnique(simple_definition)
        prompt = tech.build_prompt(sample_state, "A1")
        assert "Required Output Format" in prompt
        assert "JSON" in prompt

    def test_prompt_with_real_yaml(self, five_whys_definition, sample_state):
        tech = YAMLTechnique(five_whys_definition)
        prompt = tech.build_prompt(sample_state, "A1")
        assert "Five Whys" in prompt or "five" in prompt.lower()
        assert "A1" in prompt


class TestParseResponse:
    def test_valid_response_produces_item_score(
        self, simple_definition, mock_llm_response
    ):
        tech = YAMLTechnique(simple_definition)
        result = tech._parse_response(mock_llm_response, "A1")
        assert "A1" in result["item_scores"]
        score = result["item_scores"]["A1"]
        assert isinstance(score, ItemScore)
        assert score.score == 5
        assert score.confidence == "high"
        assert score.status == "evaluated"

    def test_score_clamped_to_max(self, simple_definition):
        tech = YAMLTechnique(simple_definition)
        response = {"score": 99, "rationale": "test"}
        result = tech._parse_response(response, "A1")
        # A1 max_score is 7, so score should be clamped
        assert result["item_scores"]["A1"].score == 7

    def test_trace_event_emitted(self, simple_definition, mock_llm_response):
        tech = YAMLTechnique(simple_definition)
        result = tech._parse_response(mock_llm_response, "A1")
        assert len(result["trace_events"]) == 1
        event = result["trace_events"][0]
        assert isinstance(event, TraceEvent)
        assert event.technique_id == "test-yaml-tech"
        assert event.item_id == "A1"
        assert event.action == "evaluate"

    def test_token_usage_captured(self, simple_definition, mock_llm_response):
        tech = YAMLTechnique(simple_definition)
        result = tech._parse_response(mock_llm_response, "A1")
        assert result["token_usage"]["prompt_tokens"] == 200


class TestMultiItem:
    def test_evaluate_multiple_items(self, simple_definition):
        tech = YAMLTechnique(simple_definition)
        response = {
            "A1": {"score": 5, "rationale": "good", "confidence": "high"},
            "A2": {"score": 4, "rationale": "ok", "confidence": "medium"},
        }
        result = tech.evaluate_multiple_items(response, ["A1", "A2"])
        assert "A1" in result["item_scores"]
        assert "A2" in result["item_scores"]
        assert len(result["trace_events"]) == 2


class TestGracefulDegradation:
    def test_invalid_response_handled(self, simple_definition):
        tech = YAMLTechnique(simple_definition)
        result = tech._parse_response({}, "A1")
        assert result["item_scores"]["A1"].score == 0
        assert result["item_scores"]["A1"].confidence == "medium"
