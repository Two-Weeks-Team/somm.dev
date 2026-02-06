"""Tests for SofiaNode (Vineyard Scout) - Issue #16."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from app.graph.nodes.sofia import SofiaNode
from app.graph.nodes.base import BaseSommelierNode
from app.graph.state import EvaluationState


class TestSofiaNode:
    """Test cases for SofiaNode (Vineyard Scout)."""

    def test_sofia_node_instantiation(self):
        """Test that SofiaNode can be instantiated."""
        node = SofiaNode()
        assert node is not None

    def test_sofia_node_name(self):
        """Test that SofiaNode has correct name."""
        node = SofiaNode()
        assert node.name == "sofia"

    def test_sofia_node_role(self):
        """Test that SofiaNode has correct role."""
        node = SofiaNode()
        assert node.role == "Vineyard Scout"

    def test_sofia_node_has_llm(self):
        """Test that SofiaNode uses build_llm in evaluate."""
        node = SofiaNode()
        assert node is not None

    def test_sofia_node_has_parser(self):
        """Test that SofiaNode has parser configured."""
        node = SofiaNode()
        assert hasattr(node, "parser")

    def test_sofia_get_prompt_returns_chat_prompt_template(self):
        """Test that get_prompt returns ChatPromptTemplate."""
        node = SofiaNode()
        prompt = node.get_prompt("basic")
        assert prompt is not None
        from langchain_core.prompts import ChatPromptTemplate

        assert isinstance(prompt, ChatPromptTemplate)

    def test_sofia_inherits_from_base_sommelier_node(self):
        """Test that SofiaNode inherits from BaseSommelierNode."""
        node = SofiaNode()
        assert isinstance(node, BaseSommelierNode)

    @pytest.mark.asyncio
    async def test_sofia_evaluate_returns_correct_keys(self):
        """Test that evaluate returns correct dictionary keys."""
        mock_response = MagicMock()
        mock_response.content = '{"score": 88, "notes": "Promising vintage with great potential", "confidence": 0.87, "techniques_used": ["innovation_scan", "tech_analysis"], "aspects": {"innovation": 90, "modernity": 85}}'
        mock_response.usage_metadata = {
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150,
        }

        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        with patch("app.graph.nodes.base.build_llm", return_value=mock_llm):
            node = SofiaNode()
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

            assert "sofia_result" in result
            assert "completed_sommeliers" in result
            assert "sofia" in result["completed_sommeliers"]

    @pytest.mark.asyncio
    async def test_sofia_evaluate_handles_errors(self):
        """Test that evaluate handles errors correctly."""
        mock_llm = MagicMock()
        mock_llm.ainvoke = AsyncMock(side_effect=Exception("API error"))

        with patch("app.graph.nodes.base.build_llm", return_value=mock_llm):
            node = SofiaNode()
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
            assert "sofia evaluation failed" in result["errors"][0]
            assert result["sofia_result"] is None


class TestSofiaPrompt:
    """Test cases for Sofia's prompt template."""

    def test_sofia_prompt_contains_vineyard_scout_theme(self):
        """Test that Sofia's prompt contains vineyard scout themes."""
        node = SofiaNode()
        prompt = node.get_prompt("basic")
        prompt_messages = prompt.messages

        assert len(prompt_messages) >= 2

        system_message = str(prompt_messages[0])
        assert "Vineyard Scout" in system_message or "scout" in system_message.lower()

    def test_sofia_prompt_focuses_on_innovation(self):
        """Test that Sofia's prompt focuses on innovation and growth."""
        node = SofiaNode()
        prompt = node.get_prompt("basic")
        prompt_messages = prompt.messages

        system_message = str(prompt_messages[0])
        assert (
            "innovation" in system_message.lower() or "growth" in system_message.lower()
        )
