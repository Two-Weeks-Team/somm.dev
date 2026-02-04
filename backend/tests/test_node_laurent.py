"""Tests for LaurentNode (Winemaker) - Issue #17."""

import pytest
from unittest.mock import MagicMock, patch
from app.graph.nodes.laurent import LaurentNode
from app.graph.nodes.base import BaseSommelierNode
from app.graph.state import EvaluationState


class TestLaurentNode:
    """Test cases for LaurentNode (Winemaker)."""

    def test_laurent_node_instantiation(self):
        """Test that LaurentNode can be instantiated."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = LaurentNode()
            assert node is not None

    def test_laurent_node_name(self):
        """Test that LaurentNode has correct name."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = LaurentNode()
            assert node.name == "laurent"

    def test_laurent_node_role(self):
        """Test that LaurentNode has correct role."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = LaurentNode()
            assert node.role == "Winemaker"

    def test_laurent_node_has_llm(self):
        """Test that LaurentNode has LLM configured."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI") as mock_llm:
            LaurentNode()
            mock_llm.assert_called_once()

    def test_laurent_node_has_parser(self):
        """Test that LaurentNode has parser configured."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = LaurentNode()
            assert hasattr(node, "parser")

    def test_laurent_get_prompt_returns_chat_prompt_template(self):
        """Test that get_prompt returns ChatPromptTemplate."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = LaurentNode()
            prompt = node.get_prompt("basic")
            assert prompt is not None
            from langchain_core.prompts import ChatPromptTemplate

            assert isinstance(prompt, ChatPromptTemplate)

    def test_laurent_inherits_from_base_sommelier_node(self):
        """Test that LaurentNode inherits from BaseSommelierNode."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = LaurentNode()
            assert isinstance(node, BaseSommelierNode)

    @pytest.mark.asyncio
    async def test_laurent_evaluate_returns_correct_keys(self):
        """Test that evaluate returns correct dictionary keys."""
        mock_result = MagicMock()
        mock_result.dict.return_value = {
            "score": 82,
            "notes": "Well-crafted with careful attention to detail",
            "confidence": 0.91,
            "techniques_used": ["code_review", "algorithm_analysis"],
            "aspects": {"implementation": 85, "performance": 79},
        }

        with patch.object(LaurentNode, "get_prompt") as mock_get_prompt:
            mock_chain = MagicMock()
            mock_chain.ainvoke = MagicMock(return_value=mock_result)

            mock_prompt = MagicMock()
            mock_prompt.__or__ = MagicMock(return_value=mock_chain)

            mock_get_prompt.return_value = mock_prompt

            with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
                node = LaurentNode()
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

                assert "laurent_result" in result
                assert "completed_sommeliers" in result
                assert "laurent" in result["completed_sommeliers"]

    @pytest.mark.asyncio
    async def test_laurent_evaluate_handles_errors(self):
        """Test that evaluate handles errors correctly."""
        with patch.object(LaurentNode, "get_prompt") as mock_get_prompt:
            mock_chain = MagicMock()
            mock_chain.ainvoke = MagicMock(side_effect=Exception("API error"))
            mock_prompt = MagicMock()
            mock_prompt.__or__ = MagicMock(return_value=mock_chain)
            mock_get_prompt.return_value = mock_prompt

            with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
                node = LaurentNode()
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
                assert "laurent evaluation failed" in result["errors"][0]
                assert result["laurent_result"] is None


class TestLaurentPrompt:
    """Test cases for Laurent's prompt template."""

    def test_laurent_prompt_contains_winemaker_theme(self):
        """Test that Laurent's prompt contains winemaker themes."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = LaurentNode()
            prompt = node.get_prompt("basic")
            prompt_messages = prompt.messages

            # Check that prompt has system and human messages
            assert len(prompt_messages) >= 2

            # Verify system message contains winemaker references
            system_message = str(prompt_messages[0])
            assert (
                "Winemaker" in system_message or "winemaker" in system_message.lower()
            )

    def test_laurent_prompt_focuses_on_implementation(self):
        """Test that Laurent's prompt focuses on implementation quality."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = LaurentNode()
            prompt = node.get_prompt("basic")
            prompt_messages = prompt.messages

            system_message = str(prompt_messages[0])
            assert (
                "implementation" in system_message.lower()
                or "algorithm" in system_message.lower()
            )
