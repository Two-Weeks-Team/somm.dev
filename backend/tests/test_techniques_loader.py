from pathlib import Path

from app.techniques.loader import (
    determine_available_inputs,
    filter_techniques,
    load_techniques,
)
from app.techniques.schema import TechniqueDefinition


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def test_load_techniques_invalid_yaml_returns_error(tmp_path: Path):
    invalid = tmp_path / "bad.yaml"
    _write(invalid, "not: [valid")

    techniques, errors = load_techniques(tmp_path)
    assert techniques == []
    assert errors


def test_load_techniques_schema_validation_error(tmp_path: Path):
    invalid = tmp_path / "missing.yaml"
    _write(invalid, "id: only-id")

    techniques, errors = load_techniques(tmp_path)
    assert techniques == []
    assert errors


def test_filter_techniques_by_input_source():
    from app.techniques.schema import ScoringCriteria

    techniques = [
        TechniqueDefinition(
            id="t1",
            name="Test Technique 1",
            category="structure",
            input_source="github",
            scoring=ScoringCriteria(min=1, max=5, criteria={}, weight=1.0),
            output_schema={"score": "integer"},
            prompt_template="x",
        ),
        TechniqueDefinition(
            id="t2",
            name="Test Technique 2",
            category="structure",
            input_source="both",
            scoring=ScoringCriteria(min=1, max=5, criteria={}, weight=1.0),
            output_schema={"score": "integer"},
            prompt_template="y",
        ),
    ]

    github_only = filter_techniques(techniques, ["github"])
    assert [t.id for t in github_only] == ["t1"]

    both_inputs = filter_techniques(techniques, ["github", "pdf"])
    assert [t.id for t in both_inputs] == ["t1", "t2"]


def test_determine_available_inputs_from_repo_context():
    assert determine_available_inputs({}) == ["github"]
    assert determine_available_inputs({"pdf_context": "x"}) == ["github", "pdf"]
