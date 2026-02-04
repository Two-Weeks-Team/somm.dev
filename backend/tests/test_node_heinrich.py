"""Tests for HeinrichNode (Quality Inspector) - Issue #15."""

import pytest
from unittest.mock import MagicMock, patch
from app.graph.nodes.heinrich import HeinrichNode
from app.graph.nodes.base import BaseSommelierNode
from app.graph.state import EvaluationState


class TestHeinrichNode:
    """Test cases for HeinrichNode (Quality Inspector)."""

    def test_heinrich_node_instantiation(self):
        """Test that HeinrichNode can be instantiated."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = HeinrichNode()
            assert node is not None

    def test_heinrich_node_name(self):
        """Test that HeinrichNode has correct name."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = HeinrichNode()
            assert node.name == "heinrich"

    def test_heinrich_node_role(self):
        """Test that HeinrichNode has correct role."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = HeinrichNode()
            assert node.role == "Quality Inspector"

    def test_heinrich_node_has_llm(self):
        """Test that HeinrichNode has LLM configured."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI") as mock_llm:
            HeinrichNode()
            mock_llm.assert_called_once()

    def test_heinrich_node_has_parser(self):
        """Test that HeinrichNode has parser configured."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = HeinrichNode()
            assert hasattr(node, "parser")

    def test_heinrich_get_prompt_returns_chat_prompt_template(self):
        """Test that get_prompt returns ChatPromptTemplate."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = HeinrichNode()
            prompt = node.get_prompt("basic")
            assert prompt is not None
            from langchain_core.prompts import ChatPromptTemplate

            assert isinstance(prompt, ChatPromptTemplate)

    def test_heinrich_inherits_from_base_sommelier_node(self):
        """Test that HeinrichNode inherits from BaseSommelierNode."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = HeinrichNode()
            assert isinstance(node, BaseSommelierNode)

    @pytest.mark.asyncio
    async def test_heinrich_evaluate_returns_correct_keys(self):
        """Test that evaluate returns correct dictionary keys."""
        mock_result = MagicMock()
        mock_result.dict.return_value = {
            "score": 78,
            "notes": "Requires more testing",
            "confidence": 0.85,
            "techniques_used": ["security_scan", "test_coverage"],
            "aspects": {"test_coverage": 75, "security": 80},
        }

        with patch.object(HeinrichNode, "get_prompt") as mock_get_prompt:
            mock_chain = MagicMock()
            mock_chain.ainvoke = MagicMock(return_value=mock_result)

            mock_prompt = MagicMock()
            mock_prompt.__or__ = MagicMock(return_value=mock_chain)

            mock_get_prompt.return_value = mock_prompt

            with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
                node = HeinrichNode()
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

                assert "heinrich_result" in result
                assert "completed_sommeliers" in result
                assert "heinrich" in result["completed_sommeliers"]

    @pytest.mark.asyncio
    async def test_heinrich_evaluate_handles_errors(self):
        """Test that evaluate handles errors correctly."""
        with patch.object(HeinrichNode, "get_prompt") as mock_get_prompt:
            mock_chain = MagicMock()
            mock_chain.ainvoke = MagicMock(side_effect=Exception("API error"))
            mock_prompt = MagicMock()
            mock_prompt.__or__ = MagicMock(return_value=mock_chain)
            mock_get_prompt.return_value = mock_prompt

            with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
                node = HeinrichNode()
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
                assert "heinrich evaluation failed" in result["errors"][0]
                assert result["heinrich_result"] is None


class TestHeinrichPrompt:
    """Test cases for Heinrich's prompt template."""

    def test_heinrich_prompt_contains_quality_inspector_theme(self):
        """Test that Heinrich's prompt contains quality inspector themes."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = HeinrichNode()
            prompt = node.get_prompt("basic")
            prompt_messages = prompt.messages

            # Check that prompt has system and human messages
            assert len(prompt_messages) >= 2

            # Verify system message contains quality inspector references
            system_message = str(prompt_messages[0])
            assert (
                "Quality Inspector" in system_message
                or "quality" in system_message.lower()
            )

    def test_heinrich_prompt_focuses_on_testing_and_security(self):
        """Test that Heinrich's prompt focuses on testing and security."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = HeinrichNode()
            prompt = node.get_prompt("basic")
            prompt_messages = prompt.messages

            system_message = str(prompt_messages[0])
            assert (
                "test" in system_message.lower() or "security" in system_message.lower()
            )
