from pathlib import Path
from typing import Dict, List, Tuple

import yaml

from app.core.logging import logger
from app.techniques.schema import TechniqueDefinition


DEFAULT_TECHNIQUES_DIR = Path(__file__).parent / "definitions"


def load_techniques(
    definitions_dir: Path = DEFAULT_TECHNIQUES_DIR,
) -> Tuple[List[TechniqueDefinition], List[str]]:
    techniques: List[TechniqueDefinition] = []
    errors: List[str] = []

    if not definitions_dir.exists():
        return techniques, errors

    yaml_files = list(definitions_dir.glob("**/*.yaml")) + list(
        definitions_dir.glob("**/*.yml")
    )

    for path in sorted(yaml_files):
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError(f"Technique file {path.name} must define a mapping")
            techniques.append(TechniqueDefinition(**raw))
        except Exception as exc:
            errors.append(f"{path.name}: {exc}")
            logger.warning(
                "Technique load failed", extra={"file": path.name, "error": str(exc)}
            )

    return techniques, errors


def determine_available_inputs(repo_context: Dict) -> List[str]:
    available = {"github"}
    if (
        repo_context.get("pdf_context")
        or repo_context.get("pdf_text")
        or repo_context.get("pdfs")
    ):
        available.add("pdf")
    return sorted(available)


def filter_techniques(
    techniques: List[TechniqueDefinition], available_inputs: List[str]
) -> List[TechniqueDefinition]:
    available = set(available_inputs)
    filtered: List[TechniqueDefinition] = []

    for technique in techniques:
        if technique.input_source == "both":
            if {"github", "pdf"}.issubset(available):
                filtered.append(technique)
            continue
        if technique.input_source in available:
            filtered.append(technique)

    return filtered
