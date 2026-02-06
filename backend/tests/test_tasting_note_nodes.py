import pytest
from app.techniques.registry import TechniqueRegistry


@pytest.fixture(autouse=True)
def reset_registry():
    TechniqueRegistry.reset()
    yield
    TechniqueRegistry.reset()


class TestTastingNoteNodes:
    def test_aroma_node_category(self):
        from app.graph.nodes.tasting_notes import AromaNotesNode

        node = AromaNotesNode()
        assert node.category.value == "aroma"
        assert node.axis == "problem-analysis"

    def test_palate_node_category(self):
        from app.graph.nodes.tasting_notes import PalateNotesNode

        node = PalateNotesNode()
        assert node.category.value == "palate"
        assert node.axis == "innovation"

    def test_body_node_category(self):
        from app.graph.nodes.tasting_notes import BodyNotesNode

        node = BodyNotesNode()
        assert node.category.value == "body"
        assert node.axis == "risk-analysis"

    def test_finish_node_category(self):
        from app.graph.nodes.tasting_notes import FinishNotesNode

        node = FinishNotesNode()
        assert node.category.value == "finish"
        assert node.axis == "user-centricity"

    def test_balance_node_category(self):
        from app.graph.nodes.tasting_notes import BalanceNotesNode

        node = BalanceNotesNode()
        assert node.category.value == "balance"
        assert node.axis == "feasibility"

    def test_vintage_node_category(self):
        from app.graph.nodes.tasting_notes import VintageNotesNode

        node = VintageNotesNode()
        assert node.category.value == "vintage"
        assert node.axis == "opportunity"

    def test_terroir_node_category(self):
        from app.graph.nodes.tasting_notes import TerroirNotesNode

        node = TerroirNotesNode()
        assert node.category.value == "terroir"
        assert node.axis == "presentation"

    def test_cellar_node_category(self):
        from app.graph.nodes.tasting_notes import CellarNotesNode

        node = CellarNotesNode()
        assert node.category.value == "cellar"
        assert node.axis == "synthesis"

    def test_all_nodes_have_techniques(self):
        from app.graph.nodes.tasting_notes import (
            AromaNotesNode,
            PalateNotesNode,
            BodyNotesNode,
            FinishNotesNode,
            BalanceNotesNode,
            VintageNotesNode,
            TerroirNotesNode,
            CellarNotesNode,
        )

        nodes = [
            AromaNotesNode(),
            PalateNotesNode(),
            BodyNotesNode(),
            FinishNotesNode(),
            BalanceNotesNode(),
            VintageNotesNode(),
            TerroirNotesNode(),
            CellarNotesNode(),
        ]
        for node in nodes:
            techniques = node.get_techniques()
            assert len(techniques) > 0, f"{node.category.value} should have techniques"

    def test_all_nodes_have_p0_techniques(self):
        from app.graph.nodes.tasting_notes import (
            AromaNotesNode,
            PalateNotesNode,
            BodyNotesNode,
            FinishNotesNode,
            BalanceNotesNode,
            VintageNotesNode,
            TerroirNotesNode,
            CellarNotesNode,
        )

        nodes = [
            AromaNotesNode(),
            PalateNotesNode(),
            BodyNotesNode(),
            FinishNotesNode(),
            BalanceNotesNode(),
            VintageNotesNode(),
            TerroirNotesNode(),
            CellarNotesNode(),
        ]
        for node in nodes:
            p0 = node.get_p0_techniques()
            assert len(p0) >= 1, f"{node.category.value} should have P0 techniques"
