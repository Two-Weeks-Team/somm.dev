"""Tests for app/graph/nodes/base.py - BaseSommelierNode abstract class"""

import pytest
from unittest.mock import MagicMock, patch
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


class TestBaseSommelierNode:
    """Test cases for BaseSommelierNode abstract class"""

    def test_base_sommelier_node_can_be_instantiated(self):
        """Test that we can create a concrete implementation"""
        node = ConcreteSommelierNode()
        assert node is not None
        assert node.name == "test_sommelier"
        assert node.role == "Test Sommelier"

    def test_base_sommelier_has_llm(self):
        """Test that BaseSommelierNode initializes LLM"""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI") as mock_llm:
            mock_instance = MagicMock()
            mock_llm.return_value = mock_instance
            node = ConcreteSommelierNode()
            assert hasattr(node, "llm")
            assert mock_llm.called

    def test_base_sommelier_has_parser(self):
        """Test that BaseSommelierNode initializes PydanticOutputParser"""
        node = ConcreteSommelierNode()
        assert hasattr(node, "parser")

    def test_base_sommelier_node_properties(self):
        """Test that name and role properties are implemented"""
        node = ConcreteSommelierNode()
        assert isinstance(node.name, str)
        assert isinstance(node.role, str)
        assert len(node.name) > 0
        assert len(node.role) > 0

    def test_base_sommelier_has_get_prompt(self):
        """Test that get_prompt method exists and returns ChatPromptTemplate"""
        node = ConcreteSommelierNode()
        prompt = node.get_prompt("basic")
        assert prompt is not None

    def test_base_sommelier_has_evaluate_method(self):
        """Test that evaluate method exists"""
        node = ConcreteSommelierNode()
        assert hasattr(node, "evaluate")
        assert callable(node.evaluate)

    @pytest.mark.asyncio
    async def test_evaluate_success(self):
        """Test successful evaluation flow"""
        mock_result = SommelierOutput(
            score=85,
            notes="Excellent vintage",
            confidence=0.9,
            techniques_used=["analysis"],
            aspects={},
        )

        with patch.object(ConcreteSommelierNode, "get_prompt") as mock_get_prompt:
            mock_chain = MagicMock()
            mock_chain.ainvoke = MagicMock(return_value=mock_result)

            mock_prompt = MagicMock()
            mock_prompt.__or__ = MagicMock(return_value=mock_chain)

            mock_get_prompt.return_value = mock_prompt

            node = ConcreteSommelierNode()
            state: EvaluationState = {
                "repo_url": "https://github.com/example/repo",
                "repo_context": {"files": ["main.py"]},
                "evaluation_criteria": "basic",
                "user_id": "user123",
                "marcel_result": None,
                "isabella_result": None,
                "heinrich_result": None,
                "sofia_result": None,
                "laurent_result": None,
                "jeanpierre_result": None,
                "completed_sommeliers": [],
                "errors": [],
                "started_at": "2024-01-01T00:00:00",
                "completed_at": None,
            }

            result = await node.evaluate(state)

            assert f"{node.name}_result" in result
            assert "completed_sommeliers" in result
            assert node.name in result["completed_sommeliers"]

    @pytest.mark.asyncio
    async def test_evaluate_error_handling(self):
        """Test error handling in evaluate method"""
        with patch.object(ConcreteSommelierNode, "get_prompt") as mock_get_prompt:
            mock_chain = MagicMock()
            mock_chain.ainvoke = MagicMock(side_effect=Exception("API error"))
            mock_prompt = MagicMock()
            mock_prompt.__or__ = MagicMock(return_value=mock_chain)
            mock_get_prompt.return_value = mock_prompt

            node = ConcreteSommelierNode()
            state: EvaluationState = {
                "repo_url": "https://github.com/example/repo",
                "repo_context": {"files": ["main.py"]},
                "evaluation_criteria": "basic",
                "user_id": "user123",
                "marcel_result": None,
                "isabella_result": None,
                "heinrich_result": None,
                "sofia_result": None,
                "laurent_result": None,
                "jeanpierre_result": None,
                "completed_sommeliers": [],
                "errors": [],
                "started_at": "2024-01-01T00:00:00",
                "completed_at": None,
            }

            result = await node.evaluate(state)

            assert "errors" in result
            assert len(result["errors"]) > 0
            assert f"{node.name} evaluation failed" in result["errors"][0]
            assert f"{node.name}_result" in result
            assert result[f"{node.name}_result"] is None

    def test_base_sommelier_is_abstract(self):
        """Test that BaseSommelierNode cannot be instantiated directly"""
        with pytest.raises(TypeError):
            BaseSommelierNode()


class TestBaseSommelierNodeLLMConfig:
    """Test LLM configuration"""

    def test_llm_uses_gemini_model(self):
        """Test that LLM is configured for Gemini"""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI") as mock_llm:
            ConcreteSommelierNode()
            mock_llm.assert_called_once()
            call_kwargs = mock_llm.call_args[1]
            assert "gemini-1.5-flash" in call_kwargs.get("model", "")

    def test_llm_has_temperature(self):
        """Test that LLM has temperature configured"""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI") as mock_llm:
            ConcreteSommelierNode()
            call_kwargs = mock_llm.call_args[1]
            assert "temperature" in call_kwargs
            assert call_kwargs["temperature"] == 0.3

    def test_llm_has_max_output_tokens(self):
        """Test that LLM has max_output_tokens configured"""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI") as mock_llm:
            ConcreteSommelierNode()
            call_kwargs = mock_llm.call_args[1]
            assert "max_output_tokens" in call_kwargs
            assert call_kwargs["max_output_tokens"] == 2048

    def test_llm_uses_settings_api_key(self):
        """Test that LLM uses settings for API key"""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI") as mock_llm:
            with patch("app.graph.nodes.base.settings") as mock_settings:
                mock_settings.GEMINI_API_KEY = "test_api_key"
                ConcreteSommelierNode()
                call_kwargs = mock_llm.call_args[1]
                assert call_kwargs.get("google_api_key") == "test_api_key"


class TestBaseSommelierNodeParser:
    """Test parser configuration"""

    def test_parser_uses_sommelier_output(self):
        """Test that parser is configured for SommelierOutput"""
        with patch("app.graph.nodes.base.PydanticOutputParser") as mock_parser:
            mock_parser_instance = MagicMock()
            mock_parser.return_value = mock_parser_instance
            ConcreteSommelierNode()
            mock_parser.assert_called_once_with(pydantic_object=SommelierOutput)

    def test_parser_has_get_format_instructions(self):
        """Test that parser has get_format_instructions method"""
        with patch("app.graph.nodes.base.PydanticOutputParser"):
            node = ConcreteSommelierNode()
            assert hasattr(node.parser, "get_format_instructions")
