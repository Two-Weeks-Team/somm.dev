import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime, timezone

from app.graph.nodes.technique_categories import (
    BaseCategoryNode,
    AromaCategoryNode,
    PalateCategoryNode,
    BodyCategoryNode,
    FinishCategoryNode,
    BalanceCategoryNode,
    VintageCategoryNode,
    TerroirCategoryNode,
    CellarCategoryNode,
)
from app.techniques.schema import TechniqueCategory


class TestBaseCategoryNode:
    def test_base_category_node_is_abstract(self):
        with pytest.raises(TypeError):
            BaseCategoryNode()


class TestCategoryNodeInstances:
    def test_aroma_category_node(self):
        node = AromaCategoryNode()
        assert node.category == TechniqueCategory.AROMA
        assert node.display_name == "Problem Analysis"

    def test_palate_category_node(self):
        node = PalateCategoryNode()
        assert node.category == TechniqueCategory.PALATE
        assert node.display_name == "Innovation"

    def test_body_category_node(self):
        node = BodyCategoryNode()
        assert node.category == TechniqueCategory.BODY
        assert node.display_name == "Risk Analysis"

    def test_finish_category_node(self):
        node = FinishCategoryNode()
        assert node.category == TechniqueCategory.FINISH
        assert node.display_name == "User-Centricity"

    def test_balance_category_node(self):
        node = BalanceCategoryNode()
        assert node.category == TechniqueCategory.BALANCE
        assert node.display_name == "Feasibility"

    def test_vintage_category_node(self):
        node = VintageCategoryNode()
        assert node.category == TechniqueCategory.VINTAGE
        assert node.display_name == "Opportunity"

    def test_terroir_category_node(self):
        node = TerroirCategoryNode()
        assert node.category == TechniqueCategory.TERROIR
        assert node.display_name == "Presentation"

    def test_cellar_category_node(self):
        node = CellarCategoryNode()
        assert node.category == TechniqueCategory.CELLAR
        assert node.display_name == "Synthesis"


class TestCategoryNodeEvaluate:
    @pytest.mark.asyncio
    async def test_evaluate_returns_proper_state_shape(self):
        node = AromaCategoryNode()

        mock_router = MagicMock()
        mock_router.select_techniques.return_value = ["tech1", "tech2"]

        mock_result = MagicMock()
        mock_result.item_scores = {"A1": MagicMock()}
        mock_result.techniques_used = ["tech1", "tech2"]
        mock_result.methodology_trace = []
        mock_result.failed_techniques = []
        mock_result.total_token_usage = {"prompt_tokens": 100, "completion_tokens": 50}
        mock_result.total_cost_usd = 0.001

        mock_router.execute_techniques = AsyncMock(return_value=[])
        mock_router.aggregate_results.return_value = mock_result

        node.router = mock_router

        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user123",
        }

        result = await node.evaluate(state)

        assert "item_scores" in result
        assert "techniques_used" in result
        assert "methodology_trace" in result
        assert "completed_sommeliers" in result
        assert "token_usage" in result
        assert "cost_usage" in result
        assert "trace_metadata" in result

        assert result["completed_sommeliers"] == ["aroma"]
        assert result["techniques_used"] == ["tech1", "tech2"]

    @pytest.mark.asyncio
    async def test_evaluate_empty_techniques_returns_empty_result(self):
        node = AromaCategoryNode()

        mock_router = MagicMock()
        mock_router.select_techniques.return_value = []
        node.router = mock_router

        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user123",
        }

        result = await node.evaluate(state)

        assert "errors" in result
        assert result["completed_sommeliers"] == ["aroma"]
        assert result["errors"][0] == "aroma: no techniques available"

    @pytest.mark.asyncio
    async def test_evaluate_handles_failed_techniques(self):
        node = AromaCategoryNode()

        mock_router = MagicMock()
        mock_router.select_techniques.return_value = ["tech1", "tech2"]

        mock_result = MagicMock()
        mock_result.item_scores = {"A1": MagicMock()}
        mock_result.techniques_used = ["tech1"]
        mock_result.methodology_trace = []
        mock_result.failed_techniques = [{"technique_id": "tech2", "error": "Failed"}]
        mock_result.total_token_usage = {"prompt_tokens": 100, "completion_tokens": 50}
        mock_result.total_cost_usd = 0.001

        mock_router.execute_techniques = AsyncMock(return_value=[])
        mock_router.aggregate_results.return_value = mock_result

        node.router = mock_router

        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user123",
        }

        result = await node.evaluate(state)

        assert result["techniques_used"] == ["tech1"]
        trace_meta = result["trace_metadata"]["aroma"]
        assert trace_meta["techniques_succeeded"] == 1
        assert trace_meta["techniques_failed"] == 1


class TestAllCategoryNodes:
    @pytest.mark.asyncio
    async def test_all_nodes_have_correct_enum_values(self):
        nodes = [
            (AromaCategoryNode(), TechniqueCategory.AROMA),
            (PalateCategoryNode(), TechniqueCategory.PALATE),
            (BodyCategoryNode(), TechniqueCategory.BODY),
            (FinishCategoryNode(), TechniqueCategory.FINISH),
            (BalanceCategoryNode(), TechniqueCategory.BALANCE),
            (VintageCategoryNode(), TechniqueCategory.VINTAGE),
            (TerroirCategoryNode(), TechniqueCategory.TERROIR),
            (CellarCategoryNode(), TechniqueCategory.CELLAR),
        ]

        for node, expected_category in nodes:
            assert node.category == expected_category
            assert isinstance(node.display_name, str)
            assert len(node.display_name) > 0
