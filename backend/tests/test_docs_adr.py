from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
ADR_DIR = DOCS / "adr"
ADR_SECTIONS = ["Context", "Decision", "Alternatives", "Consequences", "Links"]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_sections(content: str, sections: list[str]) -> None:
    for section in sections:
        assert f"## {section}" in content


@pytest.mark.parametrize(
    "adr_file",
    [
        "ADR_TEMPLATE.md",
        "ADR-001-fairthon-alignment.md",
    ],
)
def test_adr_sections_exist(adr_file: str):
    content = _read(ADR_DIR / adr_file)
    _assert_sections(content, ADR_SECTIONS)


def test_docs_index_references_adrs():
    content = _read(DOCS / "README.md")
    assert "ADR_TEMPLATE.md" in content
    assert "ADR-001-fairthon-alignment.md" in content
    assert "DECISION_LOG.md" in content


def test_plan_checklist_exists():
    content = _read(DOCS / "FAIRTHON_ALIGNMENT_PLAN.md")
    assert "Plan Execution Checklist" in content
