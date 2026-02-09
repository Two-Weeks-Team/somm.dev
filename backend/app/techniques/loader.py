from pathlib import Path
from typing import List, Tuple

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
