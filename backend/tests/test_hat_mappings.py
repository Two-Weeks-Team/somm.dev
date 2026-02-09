"""Tests for hat_mappings module."""

from app.criteria.bmad_items import BMAD_ITEMS
from app.criteria.hat_mappings import (
    HAT_TO_ITEMS,
    ITEM_TO_HATS,
    Hat,
    get_all_hats,
    get_hats_for_item,
    get_items_for_hat,
    validate_coverage,
)


class TestHatMappings:
    """Test cases for hat to BMAD item mappings."""

    def test_all_17_bmad_items_have_at_least_one_hat(self):
        """Every item from BMAD_ITEMS has at least one hat."""
        for item_id in BMAD_ITEMS.keys():
            hats = get_hats_for_item(item_id)
            assert len(hats) >= 1, f"BMAD item {item_id} has no hats"

    def test_validate_coverage_returns_empty(self):
        """validate_coverage() returns []."""
        uncovered = validate_coverage()
        assert uncovered == [], f"Uncovered BMAD items: {uncovered}"

    def test_known_hat_item_relationships(self):
        """Known hat→item relationships exist."""
        assert "A1" in get_items_for_hat("white")
        assert "B4" in get_items_for_hat("black")
        assert "B1" in get_items_for_hat("green")
        assert "A3" in get_items_for_hat("yellow")
        assert "D1" in get_items_for_hat("blue")
        assert "C1" in get_items_for_hat("red")

    def test_get_items_for_hat_returns_sorted(self):
        """Results from get_items_for_hat are sorted."""
        items = get_items_for_hat("white")
        assert items == sorted(items)

    def test_six_hats_defined(self):
        """Six hats are defined in the Hat enum."""
        assert len(Hat) == 6

    def test_get_all_hats(self):
        """get_all_hats returns 6 hat values."""
        hats = get_all_hats()
        assert len(hats) == 6
        assert set(hats) == {"white", "red", "black", "yellow", "green", "blue"}

    def test_reverse_mapping_consistency(self):
        """If hat→item exists, then item→hat exists."""
        for hat, items in HAT_TO_ITEMS.items():
            for item in items:
                assert hat in ITEM_TO_HATS[item], (
                    f"{hat}→{item} exists but {item}→{hat} missing"
                )

    def test_all_hat_values_in_mapping(self):
        """All hat enum values have entries in HAT_TO_ITEMS."""
        for hat in Hat:
            assert hat.value in HAT_TO_ITEMS, f"Hat {hat.value} not in HAT_TO_ITEMS"

    def test_no_duplicate_items_per_hat(self):
        """Each hat has unique items (no duplicates)."""
        for hat, items in HAT_TO_ITEMS.items():
            assert len(items) == len(set(items)), f"Hat {hat} has duplicate items"

    def test_item_to_hats_sorted(self):
        """ITEM_TO_HATS values are sorted."""
        for item, hats in ITEM_TO_HATS.items():
            assert hats == sorted(hats), f"Hats for {item} not sorted"
