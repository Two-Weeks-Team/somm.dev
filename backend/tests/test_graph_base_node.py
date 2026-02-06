"""Tests for app/graph/nodes/base.py - BaseSommelierNode abstract class"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.graph.nodes.base import BaseSommelierNode
from app.graph.state import EvaluationState
from app.graph.schemas import SommelierOutput


class ConcreteSommelierNode(BaseSommelierNode):
    """Concrete implementation of BaseSommelierNode for testing"""

    @property
    def name(self):
        return "test_sommelier"

    @property
    def role(self):
        return "Test Sommelier"

    def get_prompt(self, criteria: str):
        from langchain_core.prompts import ChatPromptTemplate

        return ChatPromptTemplate.from_messages(
            [("human", "Evaluate this {criteria}: {repo_context}")]
        )


def _make_state(**overrides) -> EvaluationState:
    base = {
        "repo_url": "https://github.com/example/repo",
        "repo_context": {"files": ["main.py"]},
        "evaluation_criteria": "basic",
        "user_id": "user123",
    }
    base.update(overrides)
    return base


class TestBaseSommelierNode:
    def test_can_be_instantiated(self):
        node = ConcreteSommelierNode()
        assert node is not None
        assert node.name == "test_sommelier"
        assert node.role == "Test Sommelier"

    def test_has_parser(self):
        node = ConcreteSommelierNode()
        assert hasattr(node, "parser")

    def test_does_not_have_llm_attribute(self):
        node = ConcreteSommelierNode()
        assert not hasattr(node, "llm")

    def test_properties_are_strings(self):
        node = ConcreteSommelierNode()
        assert isinstance(node.name, str)
        assert isinstance(node.role, str)
        assert len(node.name) > 0
        assert len(node.role) > 0

    def test_get_prompt_returns_template(self):
        node = ConcreteSommelierNode()
        prompt = node.get_prompt("basic")
        assert prompt is not None

    def test_has_evaluate_method(self):
        node = ConcreteSommelierNode()
        assert hasattr(node, "evaluate")
        assert callable(node.evaluate)

    def test_is_abstract(self):
        with pytest.raises(TypeError):
            BaseSommelierNode()


class TestBuildLlmProviderIntegration:
    @pytest.mark.asyncio
    async def test_evaluate_calls_build_llm(self):
        node = ConcreteSommelierNode()
        state = _make_state()

        mock_llm = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = '{"score": 85, "notes": "Good", "confidence": 0.9, "techniques_used": ["a"], "aspects": {}}'
        mock_response.usage_metadata = {}
        mock_llm.ainvoke.return_value = mock_response

        with patch(
            "app.graph.nodes.base.build_llm", return_value=mock_llm
        ) as mock_build:
            with patch("app.graph.nodes.base.get_event_channel") as mock_ec:
                mock_ec.return_value = MagicMock()
                await node.evaluate(state)
                mock_build.assert_called_once()

    @pytest.mark.asyncio
    async def test_evaluate_default_provider_is_gemini(self):
        node = ConcreteSommelierNode()
        state = _make_state()

        mock_llm = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = '{"score": 85, "notes": "Good", "confidence": 0.9, "techniques_used": ["a"], "aspects": {}}'
        mock_response.usage_metadata = {}
        mock_llm.ainvoke.return_value = mock_response

        with patch(
            "app.graph.nodes.base.build_llm", return_value=mock_llm
        ) as mock_build:
            with patch("app.graph.nodes.base.get_event_channel") as mock_ec:
                mock_ec.return_value = MagicMock()
                await node.evaluate(state)
                call_kwargs = mock_build.call_args[1]
                assert call_kwargs["provider"] == "gemini"

    @pytest.mark.asyncio
    async def test_evaluate_uses_provider_from_config(self):
        node = ConcreteSommelierNode()
        state = _make_state()

        mock_llm = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = '{"score": 85, "notes": "Good", "confidence": 0.9, "techniques_used": ["a"], "aspects": {}}'
        mock_response.usage_metadata = {}
        mock_llm.ainvoke.return_value = mock_response

        config = {"configurable": {"provider": "openai", "api_key": "test-key-123"}}

        with patch(
            "app.graph.nodes.base.build_llm", return_value=mock_llm
        ) as mock_build:
            with patch("app.graph.nodes.base.get_event_channel") as mock_ec:
                mock_ec.return_value = MagicMock()
                await node.evaluate(state, config=config)
                call_kwargs = mock_build.call_args[1]
                assert call_kwargs["provider"] == "openai"
                assert call_kwargs["api_key"] == "test-key-123"

    @pytest.mark.asyncio
    async def test_evaluate_success(self):
        node = ConcreteSommelierNode()
        state = _make_state()

        mock_llm = AsyncMock()
        mock_response = MagicMock()
        mock_response.content = '{"score": 85, "notes": "Excellent vintage", "confidence": 0.9, "techniques_used": ["analysis"], "aspects": {}}'
        mock_response.usage_metadata = {
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150,
        }
        mock_llm.ainvoke.return_value = mock_response

        with patch("app.graph.nodes.base.build_llm", return_value=mock_llm):
            with patch("app.graph.nodes.base.get_event_channel") as mock_ec:
                mock_ec.return_value = MagicMock()
                result = await node.evaluate(state)

                assert f"{node.name}_result" in result
                assert "completed_sommeliers" in result
                assert node.name in result["completed_sommeliers"]

    @pytest.mark.asyncio
    async def test_evaluate_error_handling(self):
        node = ConcreteSommelierNode()
        state = _make_state()

        mock_llm = AsyncMock()
        mock_llm.ainvoke.side_effect = Exception("API error")

        with patch("app.graph.nodes.base.build_llm", return_value=mock_llm):
            with patch("app.graph.nodes.base.get_event_channel") as mock_ec:
                mock_ec.return_value = MagicMock()
                result = await node.evaluate(state)

                assert "errors" in result
                assert len(result["errors"]) > 0
                assert f"{node.name} evaluation failed" in result["errors"][0]
                assert f"{node.name}_result" in result
                assert result[f"{node.name}_result"] is None


class TestBaseSommelierNodeParser:
    def test_parser_uses_sommelier_output(self):
        with patch("app.graph.nodes.base.PydanticOutputParser") as mock_parser:
            mock_parser_instance = MagicMock()
            mock_parser.return_value = mock_parser_instance
            ConcreteSommelierNode()
            mock_parser.assert_called_once_with(pydantic_object=SommelierOutput)

    def test_parser_has_get_format_instructions(self):
        with patch("app.graph.nodes.base.PydanticOutputParser"):
            node = ConcreteSommelierNode()
            assert hasattr(node.parser, "get_format_instructions")
