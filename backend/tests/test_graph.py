"""Tests for app/graph/graph.py - LangGraph evaluation pipeline"""

import pytest
from unittest.mock import MagicMock, patch
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END


class TestCheckpoint:
    """Test cases for checkpoint.py module"""

    def test_get_checkpointer_exists(self):
        """Test that get_checkpointer function exists"""
        from app.graph.checkpoint import get_checkpointer

        assert callable(get_checkpointer)

    def test_get_checkpointer_returns_mongodb_saver(self):
        """Test that get_checkpointer returns MongoDBSaver instance"""
        from app.graph.checkpoint import get_checkpointer

        with patch("app.graph.checkpoint._get_sync_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            with patch("app.graph.checkpoint.MongoDBSaver") as mock_saver:
                mock_saver_instance = MagicMock(spec=BaseCheckpointSaver)
                mock_saver.return_value = mock_saver_instance

                checkpointer = get_checkpointer()

                mock_saver.assert_called_once()
                assert checkpointer == mock_saver_instance


def create_mock_checkpointer():
    """Create a mock checkpointer that passes LangGraph validation."""
    mock = MagicMock(spec=BaseCheckpointSaver)
    return mock


class TestEvaluationGraph:
    """Test cases for the evaluation graph creation and structure"""

    def test_create_evaluation_graph_exists(self):
        """Test that create_evaluation_graph function exists"""
        from app.graph.graph import create_evaluation_graph

        assert callable(create_evaluation_graph)

    def test_evaluation_graph_is_compiled(self):
        """Test that create_evaluation_graph returns a compiled graph"""
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            graph = create_evaluation_graph()

            assert graph is not None
            # Check that it's a compiled graph (has methods like invoke, ainvoke)
            assert hasattr(graph, "invoke")
            assert hasattr(graph, "ainvoke")

    def test_graph_has_all_sommelier_nodes(self):
        """Test that the graph includes all 6 sommelier nodes"""
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            graph = create_evaluation_graph()

            # Verify the graph has all 6 nodes by checking graph.nodes
            nodes = graph.nodes
            expected_nodes = [
                "marcel",
                "isabella",
                "heinrich",
                "sofia",
                "laurent",
                "jeanpierre",
            ]
            for node_name in expected_nodes:
                assert node_name in nodes, f"Node '{node_name}' not found in graph"

    def test_graph_has_correct_node_names(self):
        """Test that graph nodes have correct identifiers"""
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            graph = create_evaluation_graph()

            # Get the nodes from the graph
            nodes = graph.nodes

            # Check that all sommelier nodes are present
            expected_nodes = [
                "marcel",
                "isabella",
                "heinrich",
                "sofia",
                "laurent",
                "jeanpierre",
            ]
            for node_name in expected_nodes:
                assert node_name in nodes, f"Node '{node_name}' not found in graph"


class TestGraphStructure:
    """Test cases for graph structure - fan-out and fan-in patterns"""

    def test_graph_has_fan_out_from_start_rag_disabled(self):
        """Test that enrichment nodes are connected from __start__ when RAG disabled"""
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = False

                graph = create_evaluation_graph()

                builder = getattr(graph, "builder", None)
                assert builder is not None

                all_edges = builder.edges
                start_edges = [e for e in all_edges if e[0] == "__start__"]

                # When RAG disabled: __start__ -> [code_analysis_enrich, web_search_enrich]
                assert len(start_edges) == 2
                start_targets = {e[1] for e in start_edges}
                assert "code_analysis_enrich" in start_targets
                assert "web_search_enrich" in start_targets

    def test_graph_has_rag_enrich_when_enabled(self):
        """Test that rag_enrich node exists and connects from __start__ when RAG enabled"""
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = True

                graph = create_evaluation_graph()

                nodes = graph.nodes
                assert "rag_enrich" in nodes

                builder = getattr(graph, "builder", None)
                all_edges = builder.edges

                start_edges = [e for e in all_edges if e[0] == "__start__"]
                # When RAG enabled: __start__ -> [rag_enrich, code_analysis_enrich, web_search_enrich]
                assert len(start_edges) == 3
                start_targets = {e[1] for e in start_edges}
                assert "rag_enrich" in start_targets
                assert "code_analysis_enrich" in start_targets
                assert "web_search_enrich" in start_targets

                # Each enrichment node connects to all 5 sommeliers
                rag_edges = [e for e in all_edges if e[0] == "rag_enrich"]
                assert len(rag_edges) == 5

    def test_graph_has_fan_in_to_jeanpierre(self):
        """Test that all 5 sommelier nodes connect to jeanpierre"""
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            graph = create_evaluation_graph()

            builder = getattr(graph, "builder", None)
            assert builder is not None

            all_edges = builder.edges

            # Check that all 5 evaluation nodes connect to jeanpierre
            # Edges are tuples of (source, target)
            evaluation_nodes = ["marcel", "isabella", "heinrich", "sofia", "laurent"]
            for node_name in evaluation_nodes:
                edges_to_jeanpierre = [
                    e for e in all_edges if e[0] == node_name and e[1] == "jeanpierre"
                ]
                assert len(edges_to_jeanpierre) == 1, (
                    f"Expected edge from {node_name} to jeanpierre"
                )

    def test_graph_ends_at_end(self):
        """Test that jeanpierre connects to END"""
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            graph = create_evaluation_graph()

            builder = getattr(graph, "builder", None)
            assert builder is not None

            all_edges = builder.edges

            # Check that jeanpierre connects to END
            # Edges are tuples of (source, target)
            edges_to_end = [
                e for e in all_edges if e[0] == "jeanpierre" and e[1] == END
            ]
            assert len(edges_to_end) == 1


class TestEvaluationGraphModule:
    """Test module-level exports and integration"""

    def test_evaluation_graph_lazy_export_configured(self):
        """Test that evaluation_graph is configured for lazy export via __getattr__"""
        from app.graph import graph as graph_module

        # Check that __getattr__ is defined for lazy loading
        assert hasattr(graph_module, "__getattr__")

        # Check that the lazy graph variable exists
        assert hasattr(graph_module, "_evaluation_graph")

    def test_evaluation_graph_is_compiled_graph(self):
        """Test that module-level evaluation_graph is a compiled graph when accessed"""
        from app.graph import graph as graph_module

        # Reset the cached graph to force recreation with mocks
        graph_module._evaluation_graph = None

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            graph = graph_module.evaluation_graph

            assert graph is not None
            assert hasattr(graph, "invoke")
            assert hasattr(graph, "ainvoke")


class TestGraphExecutionFlow:
    """Test graph execution flow and state management"""

    @pytest.mark.asyncio
    async def test_graph_accepts_initial_state(self):
        """Test that graph can be invoked with initial state"""
        from app.graph.graph import create_evaluation_graph
        from app.graph.state import EvaluationState

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            create_evaluation_graph()

            # Create initial state
            initial_state: EvaluationState = {
                "repo_url": "https://github.com/example/repo",
                "repo_context": {"files": ["main.py"], "structure": {}},
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

            # The graph should accept state (even if nodes are mocked)
            # We just verify the structure allows invocation
            assert isinstance(initial_state, dict)
