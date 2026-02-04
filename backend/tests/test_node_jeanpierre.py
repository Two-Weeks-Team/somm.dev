"""Tests for JeanPierreNode (Master Sommelier) - Issue #18."""

import pytest
from unittest.mock import MagicMock, patch
from app.graph.nodes.jeanpierre import JeanPierreNode
from app.graph.nodes.base import BaseSommelierNode
from app.graph.state import EvaluationState


class TestJeanPierreNode:
    """Test cases for JeanPierreNode (Master Sommelier)."""

    def test_jeanpierre_node_instantiation(self):
        """Test that JeanPierreNode can be instantiated."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = JeanPierreNode()
            assert node is not None

    def test_jeanpierre_node_name(self):
        """Test that JeanPierreNode has correct name."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = JeanPierreNode()
            assert node.name == "jeanpierre"

    def test_jeanpierre_node_role(self):
        """Test that JeanPierreNode has correct role."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = JeanPierreNode()
            assert node.role == "Master Sommelier"

    def test_jeanpierre_node_has_llm(self):
        """Test that JeanPierreNode has LLM configured."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI") as mock_llm:
            JeanPierreNode()
            mock_llm.assert_called_once()

    def test_jeanpierre_node_has_parser(self):
        """Test that JeanPierreNode has parser configured."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = JeanPierreNode()
            assert hasattr(node, "parser")

    def test_jeanpierre_get_prompt_returns_chat_prompt_template(self):
        """Test that get_prompt returns ChatPromptTemplate."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = JeanPierreNode()
            prompt = node.get_prompt("basic")
            assert prompt is not None
            from langchain_core.prompts import ChatPromptTemplate

            assert isinstance(prompt, ChatPromptTemplate)

    def test_jeanpierre_inherits_from_base_sommelier_node(self):
        """Test that JeanPierreNode inherits from BaseSommelierNode."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = JeanPierreNode()
            assert isinstance(node, BaseSommelierNode)

    @pytest.mark.asyncio
    async def test_jeanpierre_evaluate_returns_correct_keys(self):
        """Test that evaluate returns correct dictionary keys."""
        mock_result = MagicMock()
        mock_result.dict.return_value = {
            "score": 85,
            "notes": "An exceptional vintage with perfect balance",
            "confidence": 0.95,
            "techniques_used": ["synthesis", "harmonization"],
            "aspects": {"balance": 90, "complexity": 85, "finish": 80},
        }

        with patch.object(JeanPierreNode, "get_prompt") as mock_get_prompt:
            mock_chain = MagicMock()
            mock_chain.ainvoke = MagicMock(return_value=mock_result)

            mock_prompt = MagicMock()
            mock_prompt.__or__ = MagicMock(return_value=mock_chain)

            mock_get_prompt.return_value = mock_prompt

            with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
                node = JeanPierreNode()
                state: EvaluationState = {
                    "repo_url": "https://github.com/example/repo",
                    "repo_context": {"files": ["main.py", "app.py"]},
                    "evaluation_criteria": "basic",
                    "user_id": "user123",
                    "marcel_result": {"score": 88},
                    "isabella_result": {"score": 90},
                    "heinrich_result": {"score": 78},
                    "sofia_result": {"score": 88},
                    "laurent_result": {"score": 82},
                    "jeanpierre_result": None,
                    "completed_sommeliers": [
                        "marcel",
                        "isabella",
                        "heinrich",
                        "sofia",
                        "laurent",
                    ],
                    "errors": [],
                    "started_at": "2024-01-01T00:00:00",
                    "completed_at": None,
                }

                result = await node.evaluate(state)

                assert "jeanpierre_result" in result
                assert "completed_sommeliers" in result
                assert "jeanpierre" in result["completed_sommeliers"]

    @pytest.mark.asyncio
    async def test_jeanpierre_evaluate_handles_errors(self):
        """Test that evaluate handles errors correctly."""
        with patch.object(JeanPierreNode, "get_prompt") as mock_get_prompt:
            mock_chain = MagicMock()
            mock_chain.ainvoke = MagicMock(side_effect=Exception("API error"))
            mock_prompt = MagicMock()
            mock_prompt.__or__ = MagicMock(return_value=mock_chain)
            mock_get_prompt.return_value = mock_prompt

            with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
                node = JeanPierreNode()
                state: EvaluationState = {
                    "repo_url": "https://github.com/example/repo",
                    "repo_context": {"files": ["main.py"]},
                    "evaluation_criteria": "basic",
                    "user_id": "user123",
                    "marcel_result": {"score": 88},
                    "isabella_result": {"score": 90},
                    "heinrich_result": {"score": 78},
                    "sofia_result": {"score": 88},
                    "laurent_result": {"score": 82},
                    "jeanpierre_result": None,
                    "completed_sommeliers": [
                        "marcel",
                        "isabella",
                        "heinrich",
                        "sofia",
                        "laurent",
                    ],
                    "errors": [],
                    "started_at": "2024-01-01T00:00:00",
                    "completed_at": None,
                }

                result = await node.evaluate(state)

                assert "errors" in result
                assert len(result["errors"]) > 0
                assert "jeanpierre evaluation failed" in result["errors"][0]
                assert result["jeanpierre_result"] is None


class TestJeanPierrePrompt:
    """Test cases for Jean-Pierre's prompt template."""

    def test_jeanpierre_prompt_contains_master_sommelier_theme(self):
        """Test that Jean-Pierre's prompt contains master sommelier themes."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = JeanPierreNode()
            prompt = node.get_prompt("basic")
            prompt_messages = prompt.messages

            # Check that prompt has system and human messages
            assert len(prompt_messages) >= 2

            # Verify system message contains master sommelier references
            system_message = str(prompt_messages[0])
            assert (
                "Master Sommelier" in system_message
                or "sommelier" in system_message.lower()
            )

    def test_jeanpierre_prompt_focuses_on_synthesis(self):
        """Test that Jean-Pierre's prompt focuses on synthesis."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = JeanPierreNode()
            prompt = node.get_prompt("basic")
            prompt_messages = prompt.messages

            system_message = str(prompt_messages[0])
            assert (
                "synthes" in system_message.lower() or "final" in system_message.lower()
            )

    def test_jeanpierre_prompt_includes_all_sommeliers(self):
        """Test that Jean-Pierre's prompt includes references to all sommeliers."""
        with patch("app.graph.nodes.base.ChatGoogleGenerativeAI"):
            node = JeanPierreNode()
            prompt = node.get_prompt("basic")
            prompt_messages = prompt.messages

            system_message = str(prompt_messages[0])
            assert "Marcel" in system_message
            assert "Isabella" in system_message
            assert "Heinrich" in system_message
            assert "Sofia" in system_message
            assert "Laurent" in system_message
