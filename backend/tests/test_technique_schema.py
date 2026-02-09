import pytest
from app.techniques.schema import (
    TechniqueCategory,
    EvaluationDimension,
    TechniqueDefinition,
)


class TestTechniqueCategory:
    def test_eight_categories(self):
        assert len(TechniqueCategory) == 8

    def test_all_wine_themed(self):
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
        assert {c.value for c in TechniqueCategory} == expected

    def test_string_coercion(self):
        assert TechniqueCategory("aroma") == TechniqueCategory.AROMA


class TestEvaluationDimension:
    def test_17_dimensions(self):
        assert len(EvaluationDimension) == 17

    def test_all_bmad_items(self):
        expected = {
            "A1",
            "A2",
            "A3",
            "A4",
            "B1",
            "B2",
            "B3",
            "B4",
            "C1",
            "C2",
            "C3",
            "C4",
            "C5",
            "D1",
            "D2",
            "D3",
            "D4",
        }
        assert {d.value for d in EvaluationDimension} == expected


class TestTechniqueDefinitionParsing:
    def test_valid_category_parses(self):
        data = {
            "id": "test-tech",
            "name": "Test",
            "category": "aroma",
            "promptTemplate": "test prompt",
        }
        tech = TechniqueDefinition(**data)
        assert tech.category == TechniqueCategory.AROMA

    def test_invalid_category_raises(self):
        data = {
            "id": "test-tech",
            "name": "Test",
            "category": "invalid_category",
            "promptTemplate": "test prompt",
        }
        with pytest.raises(Exception):
            TechniqueDefinition(**data)

    def test_evaluation_dimensions_parse(self):
        data = {
            "id": "test-tech",
            "name": "Test",
            "category": "body",
            "promptTemplate": "test prompt",
            "evaluationDimensions": ["A1", "B2", "C3"],
        }
        tech = TechniqueDefinition(**data)
        assert tech.evaluation_dimensions == [
            EvaluationDimension.A1,
            EvaluationDimension.B2,
            EvaluationDimension.C3,
        ]

    def test_fairthon_source_preserved(self):
        data = {
            "id": "test-tech",
            "name": "Test",
            "category": "aroma",
            "promptTemplate": "test prompt",
            "requiredSources": "pdf_only",
        }
        tech = TechniqueDefinition(**data)
        assert tech.fairthon_source == "pdf_only"


class TestAllYAMLsLoad:
    def test_all_75_yaml_load_with_typed_enums(self):
        from app.techniques.loader import load_techniques

        techs, errors = load_techniques()
        assert len(techs) == 75, f"Expected 75, got {len(techs)}, errors: {errors}"
        assert len(errors) == 0
        for tech in techs:
            assert isinstance(tech.category, TechniqueCategory)
