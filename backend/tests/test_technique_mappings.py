"""Tests for Technique-to-Evaluation Mappings."""

import pytest

from app.techniques.mappings import (
    InvalidMappingError,
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
