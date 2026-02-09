"""Tests for English YAML technique definitions."""

import re
from pathlib import Path

import pytest
import yaml

KOREAN_PATTERN = re.compile(
    r"[\uac00-\ud7af\u1100-\u11ff\u3130-\u318f\ua960-\ua97f\ud7b0-\ud7ff]"
)

DEFINITIONS_DIR = Path(__file__).parent.parent / "app" / "techniques" / "definitions"
VALID_CATEGORIES = {
    "aroma",
    "palate",
    "body",
    "finish",
    "balance",
    "vintage",
    "terroir",
    "cellar",
}


def load_yaml_files():
    yaml_files = list(DEFINITIONS_DIR.glob("**/*.yaml")) + list(
        DEFINITIONS_DIR.glob("**/*.yml")
    )
    techniques = []
    errors = []

    for path in sorted(yaml_files):
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError(f"Technique file {path.name} must define a mapping")
            techniques.append(raw)
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")

    return techniques, errors


class TestYAMLEnglish:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.techniques, self.errors = load_yaml_files()

    def test_all_75_load(self):
        assert len(self.techniques) == 75, (
            f"Expected 75, got {len(self.techniques)}, errors: {self.errors}"
        )

    def test_no_load_errors(self):
        assert len(self.errors) == 0, f"Load errors: {self.errors}"

    def test_no_korean_in_descriptions(self):
        for tech in self.techniques:
            description = tech.get("description", "")
            assert not KOREAN_PATTERN.search(description), (
                f"{tech.get('id')} has Korean in description"
            )

    def test_no_korean_in_prompts(self):
        for tech in self.techniques:
            prompt = tech.get("promptTemplate", "")
            assert not KOREAN_PATTERN.search(prompt), (
                f"{tech.get('id')} has Korean in promptTemplate"
            )

    def test_no_name_ko_field(self):
        for tech in self.techniques:
            assert "nameKo" not in tech, f"{tech.get('id')} still has nameKo field"

    def test_categories_are_wine_themed(self):
        for tech in self.techniques:
            category = tech.get("category", "")
            assert category in VALID_CATEGORIES, (
                f"{tech.get('id')} has non-wine category: {category}"
            )
