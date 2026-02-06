import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from langgraph.graph import END

from tests.mocks.providers import create_mock_checkpointer


class TestGraphTrajectory:
    def test_trajectory_rag_disabled_fan_out(self):
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = False

                graph = create_evaluation_graph()
                builder = getattr(graph, "builder", None)
                all_edges = builder.edges

                start_edges = [e for e in all_edges if e[0] == "__start__"]
                sommelier_targets = {e[1] for e in start_edges}

                expected_sommeliers = {
                    "marcel",
                    "isabella",
                    "heinrich",
                    "sofia",
                    "laurent",
                }
                assert sommelier_targets == expected_sommeliers
                assert len(start_edges) == 5

    def test_trajectory_rag_enabled_sequential_then_fan_out(self):
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = True

                graph = create_evaluation_graph()
                builder = getattr(graph, "builder", None)
                all_edges = builder.edges

                start_edges = [e for e in all_edges if e[0] == "__start__"]
                assert len(start_edges) == 1
                assert start_edges[0][1] == "rag_enrich"

                rag_edges = [e for e in all_edges if e[0] == "rag_enrich"]
                rag_targets = {e[1] for e in rag_edges}
                expected_sommeliers = {
                    "marcel",
                    "isabella",
                    "heinrich",
                    "sofia",
                    "laurent",
                }
                assert rag_targets == expected_sommeliers

    def test_trajectory_fan_in_to_jeanpierre(self):
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = False

                graph = create_evaluation_graph()
                builder = getattr(graph, "builder", None)
                all_edges = builder.edges

                jeanpierre_sources = [e[0] for e in all_edges if e[1] == "jeanpierre"]
                expected_sources = {
                    "marcel",
                    "isabella",
                    "heinrich",
                    "sofia",
                    "laurent",
                }
                assert set(jeanpierre_sources) == expected_sources

    def test_trajectory_jeanpierre_to_end(self):
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = False

                graph = create_evaluation_graph()
                builder = getattr(graph, "builder", None)
                all_edges = builder.edges

                end_edges = [e for e in all_edges if e[1] == END]
                assert len(end_edges) == 1
                assert end_edges[0][0] == "jeanpierre"

    def test_complete_trajectory_rag_disabled(self):
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = False

                graph = create_evaluation_graph()
                builder = getattr(graph, "builder", None)
                all_edges = builder.edges

                expected_edge_count = 5 + 5 + 1
                assert len(all_edges) == expected_edge_count

    def test_complete_trajectory_rag_enabled(self):
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = True

                graph = create_evaluation_graph()
                builder = getattr(graph, "builder", None)
                all_edges = builder.edges

                expected_edge_count = 1 + 5 + 5 + 1
                assert len(all_edges) == expected_edge_count


class TestNodeExecutionOrder:
    def test_all_sommelier_nodes_present(self):
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = False

                graph = create_evaluation_graph()
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
                    assert node_name in nodes

    def test_rag_node_present_when_enabled(self):
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = True

                graph = create_evaluation_graph()
                nodes = graph.nodes

                assert "rag_enrich" in nodes

    def test_rag_node_absent_when_disabled(self):
        from app.graph.graph import create_evaluation_graph

        with patch("app.graph.graph.get_checkpointer") as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = False

                graph = create_evaluation_graph()
                nodes = graph.nodes

                assert "rag_enrich" not in nodes
