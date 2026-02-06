import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from tests.mocks.providers import (
    MockLLM,
    create_mock_checkpointer,
    create_mock_sommelier_response,
)


class TestEndToEndSmoke:
    def test_graph_can_be_created_with_rag_enabled(self):
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = True

                graph = create_evaluation_graph()

                assert graph is not None
                assert hasattr(graph, "invoke")
                assert hasattr(graph, "ainvoke")

    def test_graph_can_be_created_with_rag_disabled(self):
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = False

                graph = create_evaluation_graph()

                assert graph is not None
                assert hasattr(graph, "invoke")
                assert hasattr(graph, "ainvoke")

    def test_graph_has_expected_node_count_rag_enabled(self):
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = True

                graph = create_evaluation_graph()
                nodes = graph.nodes

                assert len(nodes) == 8

    def test_graph_has_expected_node_count_rag_disabled(self):
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = False

                graph = create_evaluation_graph()
                nodes = graph.nodes

                assert len(nodes) == 7


class TestNodeInstantiation:
    def test_all_sommelier_nodes_can_be_instantiated(self):
        from app.graph.nodes.marcel import MarcelNode
        from app.graph.nodes.isabella import IsabellaNode
        from app.graph.nodes.heinrich import HeinrichNode
        from app.graph.nodes.sofia import SofiaNode
        from app.graph.nodes.laurent import LaurentNode
        from app.graph.nodes.jeanpierre import JeanPierreNode

        marcel = MarcelNode()
        isabella = IsabellaNode()
        heinrich = HeinrichNode()
        sofia = SofiaNode()
        laurent = LaurentNode()
        jeanpierre = JeanPierreNode()

        assert marcel.name == "marcel"
        assert isabella.name == "isabella"
        assert heinrich.name == "heinrich"
        assert sofia.name == "sofia"
        assert laurent.name == "laurent"
        assert jeanpierre.name == "jeanpierre"

    def test_all_sommelier_nodes_have_parser(self):
        from app.graph.nodes.marcel import MarcelNode
        from app.graph.nodes.isabella import IsabellaNode
        from app.graph.nodes.heinrich import HeinrichNode
        from app.graph.nodes.sofia import SofiaNode
        from app.graph.nodes.laurent import LaurentNode
        from app.graph.nodes.jeanpierre import JeanPierreNode

        nodes = [
            MarcelNode(),
            IsabellaNode(),
            HeinrichNode(),
            SofiaNode(),
            LaurentNode(),
            JeanPierreNode(),
        ]

        for node in nodes:
            assert hasattr(node, "parser")
            assert node.parser is not None


class TestStateValidation:
    def test_evaluation_state_accepts_minimal_input(self):
        from app.graph.state import EvaluationState

        state: EvaluationState = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user1",
        }

        assert state["repo_url"] == "https://github.com/test/repo"
        assert state["evaluation_criteria"] == "basic"

    def test_evaluation_state_accepts_full_input(self):
        from app.graph.state import EvaluationState

        state: EvaluationState = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {"readme": "Test"},
            "evaluation_criteria": "hackathon",
            "user_id": "user1",
            "marcel_result": None,
            "isabella_result": None,
            "heinrich_result": None,
            "sofia_result": None,
            "laurent_result": None,
            "jeanpierre_result": None,
            "completed_sommeliers": [],
            "errors": [],
            "rag_context": None,
            "started_at": "2024-01-01T00:00:00Z",
            "completed_at": None,
        }

        assert state["evaluation_criteria"] == "hackathon"
        assert state["completed_sommeliers"] == []


class TestMockProviderSuite:
    def test_mock_llm_returns_valid_response(self):
        mock_llm = MockLLM(sommelier_name="test")

        response = mock_llm.invoke([])

        assert response.content is not None
        assert "test" in response.content

    @pytest.mark.asyncio
    async def test_mock_llm_async_returns_valid_response(self):
        mock_llm = MockLLM(sommelier_name="test")

        response = await mock_llm.ainvoke([])

        assert response.content is not None
        assert response.usage_metadata is not None
        assert response.usage_metadata["total_tokens"] == 150

    def test_mock_llm_tracks_call_count(self):
        mock_llm = MockLLM()

        assert mock_llm.call_count == 0
        mock_llm.invoke([])
        assert mock_llm.call_count == 1
        mock_llm.invoke([])
        assert mock_llm.call_count == 2

    def test_create_mock_sommelier_response_is_valid_json(self):
        import json

        response = create_mock_sommelier_response("marcel", 90, 0.95)

        parsed = json.loads(response)
        assert parsed["sommelier_name"] == "marcel"
        assert parsed["score"] == 90
        assert parsed["confidence"] == 0.95
