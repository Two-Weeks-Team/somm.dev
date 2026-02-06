"""Tests for IsabellaNode (Wine Critic) - Issue #14."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.graph.nodes.isabella import IsabellaNode
from app.graph.nodes.base import BaseSommelierNode
from app.graph.state import EvaluationState


class TestIsabellaNode:
    """Test cases for IsabellaNode (Wine Critic)."""

    def test_isabella_node_instantiation(self):
        """Test that IsabellaNode can be instantiated."""
        node = IsabellaNode()
        assert node is not None

    def test_isabella_node_name(self):
        """Test that IsabellaNode has correct name."""
        node = IsabellaNode()
        assert node.name == "isabella"

    def test_isabella_node_role(self):
        """Test that IsabellaNode has correct role."""
        node = IsabellaNode()
        assert node.role == "Wine Critic"

    def test_isabella_node_has_llm(self):
        """Test that IsabellaNode uses build_llm in evaluate."""
        node = IsabellaNode()
        assert node is not None

    def test_isabella_node_has_parser(self):
        """Test that IsabellaNode has parser configured."""
        node = IsabellaNode()
        assert hasattr(node, "parser")

    def test_isabella_get_prompt_returns_chat_prompt_template(self):
        """Test that get_prompt returns ChatPromptTemplate."""
        node = IsabellaNode()
        prompt = node.get_prompt("basic")
        assert prompt is not None
        from langchain_core.prompts import ChatPromptTemplate

        assert isinstance(prompt, ChatPromptTemplate)

    def test_isabella_inherits_from_base_sommelier_node(self):
        """Test that IsabellaNode inherits from BaseSommelierNode."""
        node = IsabellaNode()
        assert isinstance(node, BaseSommelierNode)

    @pytest.mark.asyncio
    async def test_isabella_evaluate_returns_correct_keys(self):
        """Test that evaluate returns correct dictionary keys."""
        mock_response = MagicMock()
        mock_response.content = '{"score": 90, "notes": "A masterpiece of elegance", "confidence": 0.95, "techniques_used": ["aesthetics_review"], "aspects": {"readability": 92, "elegance": 88}}'
        mock_response.usage_metadata = {
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150,
        }

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        with patch("app.graph.nodes.base.build_llm", return_value=mock_llm):
            node = IsabellaNode()
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

            assert "isabella_result" in result
            assert "completed_sommeliers" in result
            assert "isabella" in result["completed_sommeliers"]

    @pytest.mark.asyncio
    async def test_isabella_evaluate_handles_errors(self):
        """Test that evaluate handles errors correctly."""
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("API error"))

        with patch("app.graph.nodes.base.build_llm", return_value=mock_llm):
            node = IsabellaNode()
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
            assert "isabella evaluation failed" in result["errors"][0]
            assert result["isabella_result"] is None


class TestIsabellaPrompt:
    """Test cases for Isabella's prompt template."""

    def test_isabella_prompt_contains_wine_critic_theme(self):
        """Test that Isabella's prompt contains wine critic themes."""
        node = IsabellaNode()
        prompt = node.get_prompt("basic")
        prompt_messages = prompt.messages

        assert len(prompt_messages) >= 2

        system_message = str(prompt_messages[0])
        assert "Wine Critic" in system_message or "critic" in system_message.lower()

    def test_isabella_prompt_focuses_on_aesthetics(self):
        """Test that Isabella's prompt focuses on aesthetics and DX."""
        node = IsabellaNode()
        prompt = node.get_prompt("basic")
        prompt_messages = prompt.messages

        system_message = str(prompt_messages[0])
        assert (
            "aesthetic" in system_message.lower()
            or "elegance" in system_message.lower()
        )
