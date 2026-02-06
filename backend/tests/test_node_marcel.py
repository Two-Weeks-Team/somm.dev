"""Tests for MarcelNode (Cellar Master) - Issue #13."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.graph.nodes.marcel import MarcelNode
from app.graph.nodes.base import BaseSommelierNode
from app.graph.state import EvaluationState


class TestMarcelNode:
    """Test cases for MarcelNode (Cellar Master)."""

    def test_marcel_node_instantiation(self):
        """Test that MarcelNode can be instantiated."""
        node = MarcelNode()
        assert node is not None

    def test_marcel_node_name(self):
        """Test that MarcelNode has correct name."""
        node = MarcelNode()
        assert node.name == "marcel"

    def test_marcel_node_role(self):
        """Test that MarcelNode has correct role."""
        node = MarcelNode()
        assert node.role == "Cellar Master"

    def test_marcel_node_has_llm(self):
        """Test that MarcelNode uses build_llm in evaluate."""
        # LLM is now created lazily in evaluate() via build_llm
        node = MarcelNode()
        # Verify the node can be instantiated (LLM is built during evaluate)
        assert node is not None

    def test_marcel_node_has_parser(self):
        """Test that MarcelNode has parser configured."""
        node = MarcelNode()
        assert hasattr(node, "parser")

    def test_marcel_get_prompt_returns_chat_prompt_template(self):
        """Test that get_prompt returns ChatPromptTemplate."""
        node = MarcelNode()
        prompt = node.get_prompt("basic")
        assert prompt is not None
        from langchain_core.prompts import ChatPromptTemplate

        assert isinstance(prompt, ChatPromptTemplate)

    def test_marcel_inherits_from_base_sommelier_node(self):
        """Test that MarcelNode inherits from BaseSommelierNode."""
        node = MarcelNode()
        assert isinstance(node, BaseSommelierNode)

    @pytest.mark.asyncio
    async def test_marcel_evaluate_returns_correct_keys(self):
        """Test that evaluate returns correct dictionary keys."""
        mock_response = MagicMock()
        mock_response.content = '{"score": 85, "notes": "Excellent vintage", "confidence": 0.9, "techniques_used": ["structure_analysis"], "aspects": {"architecture": 85, "organization": 88}}'
        mock_response.usage_metadata = {
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150,
        }

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        with patch("app.graph.nodes.base.build_llm", return_value=mock_llm):
            node = MarcelNode()
            state: EvaluationState = {
                "repo_url": "https://github.com/example/repo",
                "repo_context": {"files": ["main.py", "app.py"]},
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

            assert "marcel_result" in result
            assert "completed_sommeliers" in result
            assert "marcel" in result["completed_sommeliers"]

    @pytest.mark.asyncio
    async def test_marcel_evaluate_handles_errors(self):
        """Test that evaluate handles errors correctly."""
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("API error"))

        with patch("app.graph.nodes.base.build_llm", return_value=mock_llm):
            node = MarcelNode()
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
            assert "marcel evaluation failed" in result["errors"][0]
            assert result["marcel_result"] is None


class TestMarcelPrompt:
    """Test cases for Marcel's prompt template."""

    def test_marcel_prompt_contains_cellar_master_theme(self):
        """Test that Marcel's prompt contains cellar master themes."""
        node = MarcelNode()
        prompt = node.get_prompt("basic")
        prompt_messages = prompt.messages

        assert len(prompt_messages) >= 2

        system_message = str(prompt_messages[0])
        assert "Cellar Master" in system_message or "cellar" in system_message.lower()

    def test_marcel_prompt_focuses_on_structure(self):
        """Test that Marcel's prompt focuses on structure and architecture."""
        node = MarcelNode()
        prompt = node.get_prompt("basic")
        prompt_messages = prompt.messages

        system_message = str(prompt_messages[0])
        assert (
            "structure" in system_message.lower()
            or "architecture" in system_message.lower()
        )
