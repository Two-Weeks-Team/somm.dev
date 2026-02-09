import pytest
from unittest.mock import MagicMock, patch
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END


def create_mock_checkpointer():
    mock = MagicMock(spec=BaseCheckpointSaver)
    return mock


class TestFullTechniquesGraph:
    def test_create_full_techniques_graph_exists(self):
        from app.graph.full_techniques_graph import create_full_techniques_graph

        assert callable(create_full_techniques_graph)

    def test_graph_compiles_without_error(self):
        from app.graph.full_techniques_graph import create_full_techniques_graph

        with patch(
            "app.graph.full_techniques_graph.get_checkpointer"
        ) as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            graph = create_full_techniques_graph()

            assert graph is not None
            assert hasattr(graph, "invoke")
            assert hasattr(graph, "ainvoke")

    def test_graph_has_all_category_nodes(self):
        from app.graph.full_techniques_graph import create_full_techniques_graph

        with patch(
            "app.graph.full_techniques_graph.get_checkpointer"
        ) as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            graph = create_full_techniques_graph()

            nodes = graph.nodes
            expected_nodes = [
                "aroma",
                "palate",
                "body",
                "finish",
                "balance",
                "vintage",
                "terroir",
                "cellar",
                "deep_synthesis",
                "finalize",
            ]
            for node_name in expected_nodes:
                assert node_name in nodes, f"Node '{node_name}' not found in graph"

    def test_graph_has_deep_synthesis_and_finalize(self):
        from app.graph.full_techniques_graph import create_full_techniques_graph

        with patch(
            "app.graph.full_techniques_graph.get_checkpointer"
        ) as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            graph = create_full_techniques_graph()

            nodes = graph.nodes
            assert "deep_synthesis" in nodes
            assert "finalize" in nodes

    def test_graph_has_enrichment_nodes(self):
        from app.graph.full_techniques_graph import create_full_techniques_graph

        with patch(
            "app.graph.full_techniques_graph.get_checkpointer"
        ) as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.full_techniques_graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = True

                graph = create_full_techniques_graph()

                nodes = graph.nodes
                assert "rag_enrich" in nodes
                assert "web_search_enrich" in nodes
                assert "code_analysis_enrich" in nodes

    def test_graph_fan_out_from_enrichment_to_categories(self):
        from app.graph.full_techniques_graph import create_full_techniques_graph

        with patch(
            "app.graph.full_techniques_graph.get_checkpointer"
        ) as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            with patch("app.graph.full_techniques_graph.settings") as mock_settings:
                mock_settings.RAG_ENABLED = False

                graph = create_full_techniques_graph()

                builder = getattr(graph, "builder", None)
                assert builder is not None

                all_edges = builder.edges
                category_nodes = [
                    "aroma",
                    "palate",
                    "body",
                    "finish",
                    "balance",
                    "vintage",
                    "terroir",
                    "cellar",
                ]

                for enrich_node in ["web_search_enrich", "code_analysis_enrich"]:
                    for cat_node in category_nodes:
                        edge_exists = any(
                            e[0] == enrich_node and e[1] == cat_node for e in all_edges
                        )
                        assert edge_exists, (
                            f"Expected edge from {enrich_node} to {cat_node}"
                        )

    def test_graph_fan_in_from_categories_to_deep_synthesis(self):
        from app.graph.full_techniques_graph import create_full_techniques_graph

        with patch(
            "app.graph.full_techniques_graph.get_checkpointer"
        ) as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            graph = create_full_techniques_graph()

            builder = getattr(graph, "builder", None)
            assert builder is not None

            all_edges = builder.edges
            category_nodes = [
                "aroma",
                "palate",
                "body",
                "finish",
                "balance",
                "vintage",
                "terroir",
                "cellar",
            ]

            for cat_node in category_nodes:
                edge_exists = any(
                    e[0] == cat_node and e[1] == "deep_synthesis" for e in all_edges
                )
                assert edge_exists, f"Expected edge from {cat_node} to deep_synthesis"

    def test_graph_flows_to_finalize_and_end(self):
        from app.graph.full_techniques_graph import create_full_techniques_graph

        with patch(
            "app.graph.full_techniques_graph.get_checkpointer"
        ) as mock_checkpointer:
            mock_checkpointer.return_value = create_mock_checkpointer()

            graph = create_full_techniques_graph()

            builder = getattr(graph, "builder", None)
            assert builder is not None

            all_edges = builder.edges

            deep_to_finalize = [
                e for e in all_edges if e[0] == "deep_synthesis" and e[1] == "finalize"
            ]
            assert len(deep_to_finalize) == 1

            finalize_to_end = [
                e for e in all_edges if e[0] == "finalize" and e[1] == END
            ]
            assert len(finalize_to_end) == 1


class TestGraphFactoryRegistration:
    def test_full_techniques_registered_in_factory(self):
        from app.graph.graph_factory import (
            get_evaluation_graph,
            list_available_modes,
            is_valid_mode,
            _graph_builders,
        )

        _graph_builders.clear()

        modes = list_available_modes()
        assert "full_techniques" in modes
        assert is_valid_mode("full_techniques") is True

    def test_factory_raises_invalid_mode_error(self):
        from app.graph.graph_factory import (
            get_evaluation_graph,
            InvalidEvaluationModeError,
            _graph_builders,
        )

        _graph_builders.clear()

        with pytest.raises(InvalidEvaluationModeError) as exc_info:
            get_evaluation_graph("invalid_mode_xyz")

        assert "invalid_mode_xyz" in str(exc_info.value)
        assert "full_techniques" in str(exc_info.value)
