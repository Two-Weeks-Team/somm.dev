"""Tests for Technique-to-Evaluation Mappings."""

import pytest

from app.techniques.mappings import (
    Priority,
    TastingNote,
    get_category_summary,
    get_p0_techniques,
    get_primary_technique,
    get_technique_priority,
    get_techniques_for_category,
    list_all_mappings,
    validate_mappings,
)
from app.techniques.registry import TechniqueRegistry


@pytest.fixture(autouse=True)
def reset_registry():
    TechniqueRegistry.reset()
    yield
    TechniqueRegistry.reset()


class TestGetTechniquesForCategory:
    def test_aroma_returns_11_techniques(self):
        techniques = get_techniques_for_category(TastingNote.AROMA)
        assert len(techniques) == 11

    def test_aroma_string_arg_works(self):
        techniques = get_techniques_for_category("aroma")
        assert len(techniques) == 11

    def test_palate_returns_13_techniques(self):
        techniques = get_techniques_for_category(TastingNote.PALATE)
        assert len(techniques) == 13

    def test_body_returns_8_techniques(self):
        techniques = get_techniques_for_category(TastingNote.BODY)
        assert len(techniques) == 8

    def test_finish_returns_12_techniques(self):
        techniques = get_techniques_for_category(TastingNote.FINISH)
        assert len(techniques) == 12

    def test_balance_returns_8_techniques(self):
        techniques = get_techniques_for_category(TastingNote.BALANCE)
        assert len(techniques) == 8

    def test_vintage_returns_10_techniques(self):
        techniques = get_techniques_for_category(TastingNote.VINTAGE)
        assert len(techniques) == 10

    def test_terroir_returns_5_techniques(self):
        techniques = get_techniques_for_category(TastingNote.TERROIR)
        assert len(techniques) == 5

    def test_cellar_returns_8_techniques(self):
        techniques = get_techniques_for_category(TastingNote.CELLAR)
        assert len(techniques) == 8

    def test_sorted_by_priority(self):
        techniques = get_techniques_for_category(TastingNote.AROMA)
        priorities = [get_technique_priority(t.id).value for t in techniques]
        assert priorities == sorted(priorities)


class TestGetPrimaryTechnique:
    def test_aroma_primary_is_p0(self):
        primary = get_primary_technique(TastingNote.AROMA)
        assert primary is not None
        assert get_technique_priority(primary.id) == Priority.P0

    def test_palate_primary_is_p0(self):
        primary = get_primary_technique(TastingNote.PALATE)
        assert primary is not None
        assert get_technique_priority(primary.id) == Priority.P0

    def test_body_primary_is_p0(self):
        primary = get_primary_technique(TastingNote.BODY)
        assert primary is not None
        assert get_technique_priority(primary.id) == Priority.P0


class TestGetTechniquePriority:
    def test_five_whys_is_p0(self):
        assert get_technique_priority("five-whys") == Priority.P0

    def test_first_principles_is_p0(self):
        assert get_technique_priority("first-principles-thinking") == Priority.P0

    def test_unknown_technique_defaults_to_p2(self):
        assert get_technique_priority("unknown-tech") == Priority.P2


class TestGetP0Techniques:
    def test_aroma_has_p0_techniques(self):
        p0 = get_p0_techniques(TastingNote.AROMA)
        assert len(p0) >= 1
        assert all(get_technique_priority(t.id) == Priority.P0 for t in p0)

    def test_all_categories_have_p0(self):
        for note in TastingNote:
            p0 = get_p0_techniques(note)
            assert len(p0) >= 1, f"{note.value} should have at least one P0 technique"


class TestValidateMappings:
    def test_all_mappings_valid(self):
        assert validate_mappings() is True


class TestGetCategorySummary:
    def test_returns_all_8_categories(self):
        summary = get_category_summary()
        assert len(summary) == 8
        assert set(summary.keys()) == {n.value for n in TastingNote}

    def test_each_category_has_priority_counts(self):
        summary = get_category_summary()
        for cat, counts in summary.items():
            assert "P0" in counts
            assert "P1" in counts
            assert "P2" in counts

    def test_total_count_is_75(self):
        summary = get_category_summary()
        total = sum(
            counts["P0"] + counts["P1"] + counts["P2"] for counts in summary.values()
        )
        assert total == 75


class TestListAllMappings:
    def test_returns_all_8_categories(self):
        mappings = list_all_mappings()
        assert len(mappings) == 8

    def test_total_techniques_is_75(self):
        mappings = list_all_mappings()
        total = sum(len(ids) for ids in mappings.values())
        assert total == 75


class TestTastingNoteEnum:
    def test_all_8_notes_defined(self):
        assert len(TastingNote) == 8

    def test_values_match_categories(self):
        expected = {
            "aroma",
            "palate",
            "body",
            "finish",
            "balance",
            "vintage",
            "terroir",
            "cellar",
        }
        assert {n.value for n in TastingNote} == expected


class TestPriorityEnum:
    def test_p0_is_highest(self):
        assert Priority.P0.value < Priority.P1.value < Priority.P2.value

    def test_p0_value_is_0(self):
        assert Priority.P0.value == 0


class TestCriteriaTechniqueMappings:
    """Test cases for app.criteria.technique_mappings module."""

    def test_full_techniques_returns_75(self):
        """get_techniques_for_mode('full_techniques') returns 75 techniques."""
        from app.criteria.technique_mappings import get_techniques_for_mode

        techs = get_techniques_for_mode("full_techniques")
        assert len(techs) == 75, f"Expected 75 techniques, got {len(techs)}"

    def test_six_sommeliers_returns_p0_p1(self):
        """six_sommeliers returns fewer than 75, only P0+P1."""
        from app.criteria.technique_mappings import get_techniques_for_mode

        techs = get_techniques_for_mode("six_sommeliers")
        assert len(techs) < 75
        # All should be P0 or P1
        for t_id in techs:
            p = get_technique_priority(t_id)
            assert p in (Priority.P0, Priority.P1), f"{t_id} is not P0 or P1"

    def test_grand_tasting_returns_p0_only(self):
        """grand_tasting returns fewer than six_sommeliers, only P0."""
        from app.criteria.technique_mappings import get_techniques_for_mode

        grand_tasting = get_techniques_for_mode("grand_tasting")
        six_sommeliers = get_techniques_for_mode("six_sommeliers")
        assert len(grand_tasting) < len(six_sommeliers)
        # All should be P0
        for t_id in grand_tasting:
            p = get_technique_priority(t_id)
            assert p == Priority.P0, f"{t_id} is not P0"

    def test_mode_count_ordering(self):
        """grand_tasting < six_sommeliers < full_techniques(75)."""
        from app.criteria.technique_mappings import get_techniques_for_mode

        grand = len(get_techniques_for_mode("grand_tasting"))
        six = len(get_techniques_for_mode("six_sommeliers"))
        full = len(get_techniques_for_mode("full_techniques"))
        assert grand < six < full
        assert full == 75

    def test_five_representative_mappings(self):
        """Verify specific technique→item relationships."""
        from app.criteria.technique_mappings import TECHNIQUE_TO_ITEMS

        assert "A1" in TECHNIQUE_TO_ITEMS["five-whys"]
        assert "A1" in TECHNIQUE_TO_ITEMS["5w1h"]
        assert "A2" in TECHNIQUE_TO_ITEMS["empathy-mapping"]
        assert "B1" in TECHNIQUE_TO_ITEMS["scamper"]
        assert "B4" in TECHNIQUE_TO_ITEMS["pre-mortem"]

    def test_get_primary_technique_for_item_returns_highest_priority(self):
        """get_primary_technique_for_item returns highest priority technique."""
        from app.criteria.technique_mappings import (
            get_primary_technique_for_item,
            get_techniques_for_item,
        )

        # A1 has multiple techniques, should return a P0 one
        primary = get_primary_technique_for_item("A1")
        assert primary is not None
        p = get_technique_priority(primary)
        # Should be the lowest value (highest priority)
        all_a1_techs = get_techniques_for_item("A1")
        min_priority = min(get_technique_priority(t).value for t in all_a1_techs)
        assert p.value == min_priority

    def test_get_techniques_for_item_a1(self):
        """A1 has multiple techniques."""
        from app.criteria.technique_mappings import get_techniques_for_item

        techs = get_techniques_for_item("A1")
        assert len(techs) > 1
        # Should include five-whys, 5w1h, etc.
        assert "five-whys" in techs
        assert "5w1h" in techs

    def test_all_techniques_have_items(self):
        """All techniques in TECHNIQUE_TO_ITEMS have at least one item."""
        from app.criteria.technique_mappings import TECHNIQUE_TO_ITEMS

        for tech_id, items in TECHNIQUE_TO_ITEMS.items():
            assert len(items) >= 1, f"Technique {tech_id} has no items"

    def test_get_techniques_for_item_returns_sorted(self):
        """get_techniques_for_item returns sorted list."""
        from app.criteria.technique_mappings import get_techniques_for_item

        techs = get_techniques_for_item("B1")
        assert techs == sorted(techs)

    def test_get_techniques_for_mode_invalid_returns_all(self):
        """Invalid mode returns all techniques."""
        from app.criteria.technique_mappings import get_techniques_for_mode

        techs = get_techniques_for_mode("invalid_mode")
        assert len(techs) == 75
