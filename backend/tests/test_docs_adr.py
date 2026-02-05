from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs"
ADR_DIR = DOCS / "adr"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _assert_sections(content: str, sections: list[str]) -> None:
    for section in sections:
        assert f"## {section}" in content


def test_adr_template_sections_exist():
    content = _read(ADR_DIR / "ADR_TEMPLATE.md")
    _assert_sections(
        content,
        ["Context", "Decision", "Alternatives", "Consequences", "Links"],
    )


def test_adr_001_sections_exist():
    content = _read(ADR_DIR / "ADR-001-fairthon-alignment.md")
    _assert_sections(
        content,
        ["Context", "Decision", "Alternatives", "Consequences", "Links"],
    )


def test_docs_index_references_adrs():
    content = _read(DOCS / "README.md")
    assert "ADR_TEMPLATE.md" in content
    assert "ADR-001-fairthon-alignment.md" in content
    assert "DECISION_LOG.md" in content


def test_plan_checklist_exists():
    content = _read(DOCS / "FAIRTHON_ALIGNMENT_PLAN.md")
    assert "Plan Execution Checklist" in content
