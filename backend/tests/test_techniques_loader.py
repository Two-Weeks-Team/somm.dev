from pathlib import Path

from app.techniques.loader import load_techniques
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
