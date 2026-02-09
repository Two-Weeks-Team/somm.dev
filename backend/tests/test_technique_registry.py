"""Tests for the Technique Registry."""

import pytest

from app.techniques.registry import (
    TechniqueNotFoundError,
    TechniqueRegistry,
    get_registry,
    get_technique,
    get_techniques_by_category,
    list_available_categories,
    list_techniques,
)
from app.techniques.schema import TechniqueCategory


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset singleton before each test."""
    TechniqueRegistry.reset()
    yield
    TechniqueRegistry.reset()


class TestTechniqueRegistry:
    def test_list_techniques_returns_all_75(self):
        registry = TechniqueRegistry()
        techniques = registry.list_techniques()
        assert len(techniques) == 75

    def test_list_techniques_deterministic_order(self):
        registry = TechniqueRegistry()
        first = registry.list_techniques()
        second = registry.list_techniques()
        assert [t.id for t in first] == [t.id for t in second]

    def test_get_technique_valid_id(self):
        registry = TechniqueRegistry()
        technique = registry.get_technique("five-whys")
        assert technique is not None
        assert technique.id == "five-whys"
        assert technique.category == TechniqueCategory.AROMA

    def test_get_technique_unknown_id_returns_none(self):
        registry = TechniqueRegistry()
        technique = registry.get_technique("nonexistent-technique")
        assert technique is None

    def test_get_raises_on_unknown_id(self):
        registry = TechniqueRegistry()
        with pytest.raises(TechniqueNotFoundError) as exc_info:
            registry.get("nonexistent-technique")
        assert "nonexistent-technique" in str(exc_info.value)

    def test_exists_returns_true_for_valid_id(self):
        registry = TechniqueRegistry()
        assert registry.exists("five-whys") is True

    def test_exists_returns_false_for_invalid_id(self):
        registry = TechniqueRegistry()
        assert registry.exists("not-a-technique") is False

    def test_get_techniques_by_category_aroma(self):
        registry = TechniqueRegistry()
        aroma = registry.get_techniques_by_category("aroma")
        assert len(aroma) == 11
        assert all(t.category == TechniqueCategory.AROMA for t in aroma)

    def test_get_techniques_by_category_palate(self):
        registry = TechniqueRegistry()
        palate = registry.get_techniques_by_category("palate")
        assert len(palate) == 13
        assert all(t.category == TechniqueCategory.PALATE for t in palate)

    def test_get_techniques_by_category_body(self):
        registry = TechniqueRegistry()
        body = registry.get_techniques_by_category("body")
        assert len(body) == 8
        assert all(t.category == TechniqueCategory.BODY for t in body)

    def test_get_techniques_by_category_finish(self):
        registry = TechniqueRegistry()
        finish = registry.get_techniques_by_category("finish")
        assert len(finish) == 12
        assert all(t.category == TechniqueCategory.FINISH for t in finish)

    def test_get_techniques_by_category_balance(self):
        registry = TechniqueRegistry()
        balance = registry.get_techniques_by_category("balance")
        assert len(balance) == 8
        assert all(t.category == TechniqueCategory.BALANCE for t in balance)

    def test_get_techniques_by_category_vintage(self):
        registry = TechniqueRegistry()
        vintage = registry.get_techniques_by_category("vintage")
        assert len(vintage) == 10
        assert all(t.category == TechniqueCategory.VINTAGE for t in vintage)

    def test_get_techniques_by_category_terroir(self):
        registry = TechniqueRegistry()
        terroir = registry.get_techniques_by_category("terroir")
        assert len(terroir) == 5
        assert all(t.category == TechniqueCategory.TERROIR for t in terroir)

    def test_get_techniques_by_category_cellar(self):
        registry = TechniqueRegistry()
        cellar = registry.get_techniques_by_category("cellar")
        assert len(cellar) == 8
        assert all(t.category == TechniqueCategory.CELLAR for t in cellar)

    def test_get_techniques_by_unknown_category_returns_empty(self):
        registry = TechniqueRegistry()
        unknown = registry.get_techniques_by_category("nonexistent")
        assert unknown == []

    def test_list_categories_returns_all_8(self):
        registry = TechniqueRegistry()
        categories = registry.list_categories()
        assert len(categories) == 8
        assert set(categories) == {
            TechniqueCategory.AROMA,
            TechniqueCategory.PALATE,
            TechniqueCategory.BODY,
            TechniqueCategory.FINISH,
            TechniqueCategory.BALANCE,
            TechniqueCategory.VINTAGE,
            TechniqueCategory.TERROIR,
            TechniqueCategory.CELLAR,
        }

    def test_count_returns_75(self):
        registry = TechniqueRegistry()
        assert registry.count() == 75

    def test_count_by_category(self):
        registry = TechniqueRegistry()
        counts = registry.count_by_category()
        assert counts["aroma"] == 11
        assert counts["palate"] == 13
        assert counts["body"] == 8
        assert counts["finish"] == 12
        assert counts["balance"] == 8
        assert counts["vintage"] == 10
        assert counts["terroir"] == 5
        assert counts["cellar"] == 8
        assert sum(counts.values()) == 75

    def test_singleton_pattern(self):
        reg1 = TechniqueRegistry()
        reg2 = TechniqueRegistry()
        assert reg1 is reg2

    def test_validate_returns_true(self):
        registry = TechniqueRegistry()
        assert registry.validate() is True


class TestModuleLevelFunctions:
    def test_get_registry_returns_singleton(self):
        reg1 = get_registry()
        reg2 = get_registry()
        assert reg1 is reg2

    def test_list_techniques_function(self):
        techniques = list_techniques()
        assert len(techniques) == 75

    def test_get_technique_function(self):
        technique = get_technique("five-whys")
        assert technique is not None
        assert technique.id == "five-whys"

    def test_get_techniques_by_category_function(self):
        aroma = get_techniques_by_category("aroma")
        assert len(aroma) == 11

    def test_list_available_categories_function(self):
        categories = list_available_categories()
        assert len(categories) == 8


class TestTechniqueNotFoundError:
    def test_error_message_includes_id(self):
        error = TechniqueNotFoundError("missing-tech")
        assert "missing-tech" in str(error)

    def test_error_suggests_similar_ids(self):
        error = TechniqueNotFoundError(
            "five-why",
            available_ids=["five-whys", "5w1h", "swot-analysis"],
        )
        assert "five-whys" in str(error)
        assert "Did you mean" in str(error)
