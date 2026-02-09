"""Tests for BMAD 17-item evaluation canon."""

import importlib.util
from pathlib import Path

import pytest


def _load_bmad_module():
    """Load the bmad_items module directly without triggering app imports."""
    backend_path = Path(__file__).parent.parent
    module_path = backend_path / "app" / "criteria" / "bmad_items.py"
    spec = importlib.util.spec_from_file_location("bmad_items", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bmad = _load_bmad_module()
BMADItem = bmad.BMADItem
BMADCategory = bmad.BMADCategory
BMAD_ITEMS = bmad.BMAD_ITEMS
BMAD_CATEGORIES = bmad.BMAD_CATEGORIES
get_item = bmad.get_item
list_items = bmad.list_items
get_items_by_category = bmad.get_items_by_category
get_category = bmad.get_category
get_max_total = bmad.get_max_total
get_category_max = bmad.get_category_max


class TestBMADItems:
    def test_total_items_count(self):
        assert len(BMAD_ITEMS) == 17

    def test_total_max_score_is_100(self):
        assert sum(item.max_score for item in BMAD_ITEMS.values()) == 100

    def test_category_a_sum_is_25(self):
        assert get_category_max("A") == 25

    def test_category_b_sum_is_25(self):
        assert get_category_max("B") == 25

    def test_category_c_sum_is_30(self):
        assert get_category_max("C") == 30

    def test_category_d_sum_is_20(self):
        assert get_category_max("D") == 20

    def test_get_item_a1(self):
        item = get_item("A1")
        assert item.item_id == "A1"
        assert item.max_score == 7
        assert item.category == "A"

    def test_all_items_have_rubric(self):
        for item in BMAD_ITEMS.values():
            assert len(item.rubric) > 0, f"{item.item_id} has empty rubric"

    def test_list_items_order(self):
        items = list_items()
        assert len(items) == 17
        assert items[0].item_id == "A1"
        assert items[-1].item_id == "D4"

    def test_get_items_by_category(self):
        a_items = get_items_by_category("A")
        assert len(a_items) == 4
        c_items = get_items_by_category("C")
        assert len(c_items) == 5

    def test_get_max_total(self):
        assert get_max_total() == 100

    def test_invalid_item_raises(self):
        with pytest.raises(KeyError):
            get_item("Z99")

    def test_four_categories(self):
        assert len(BMAD_CATEGORIES) == 4
        assert set(BMAD_CATEGORIES.keys()) == {"A", "B", "C", "D"}
