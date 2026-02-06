"""Technique-to-Evaluation Mappings for Grand Tasting mode.

Maps techniques to evaluation axes (Tasting Notes) with priority ordering.
"""

from enum import Enum
from typing import Dict, List, Optional

__all__ = [
    "TastingNote",
    "Priority",
    "InvalidMappingError",
    "get_techniques_for_category",
    "get_primary_technique",
    "get_technique_priority",
    "get_p0_techniques",
    "validate_mappings",
    "get_category_summary",
    "list_all_mappings",
]

from app.techniques.registry import (
    TechniqueNotFoundError,
    TechniqueRegistry,
    get_registry,
)
from app.techniques.schema import TechniqueDefinition


class TastingNote(str, Enum):
    AROMA = "aroma"
    PALATE = "palate"
    BODY = "body"
    FINISH = "finish"
    BALANCE = "balance"
    VINTAGE = "vintage"
    TERROIR = "terroir"
    CELLAR = "cellar"


class Priority(int, Enum):
    P0 = 0
    P1 = 1
    P2 = 2


TECHNIQUE_PRIORITY: Dict[str, Priority] = {
    "five-whys": Priority.P0,
    "5w1h": Priority.P0,
    "question-storming": Priority.P1,
    "failure-analysis": Priority.P1,
    "assumption-reversal": Priority.P1,
    "data-mining": Priority.P1,
    "fact-checking": Priority.P1,
    "morphological-analysis": Priority.P2,
    "pestle-analysis": Priority.P2,
    "mind-mapping": Priority.P2,
    "constraint-mapping": Priority.P2,
    "first-principles-thinking": Priority.P0,
    "scamper": Priority.P0,
    "design-thinking": Priority.P0,
    "triz": Priority.P1,
    "cross-pollination": Priority.P1,
    "concept-blending": Priority.P1,
    "lateral-thinking": Priority.P1,
    "random-stimulation": Priority.P2,
    "biomimicry": Priority.P2,
    "analogical-thinking": Priority.P2,
    "reversal-inversion": Priority.P2,
    "provocation-technique": Priority.P2,
    "quantum-superposition": Priority.P2,
    "reverse-brainstorming": Priority.P0,
    "pre-mortem": Priority.P0,
    "swot-analysis": Priority.P0,
    "fmea": Priority.P1,
    "risk-matrix": Priority.P1,
    "anti-solution": Priority.P1,
    "devil-advocate": Priority.P2,
    "zombie-apocalypse": Priority.P2,
    "empathy-mapping": Priority.P0,
    "jobs-to-be-done": Priority.P0,
    "kano-model": Priority.P0,
    "persona-journey": Priority.P1,
    "role-playing": Priority.P1,
    "emotional-journey": Priority.P1,
    "sensory-exploration": Priority.P2,
    "gut-check": Priority.P2,
    "body-wisdom-dialogue": Priority.P2,
    "inner-child-conference": Priority.P2,
    "alien-anthropologist": Priority.P2,
    "first-impression-analysis": Priority.P2,
    "technology-readiness-level": Priority.P0,
    "porters-five-forces": Priority.P0,
    "ecosystem-thinking": Priority.P1,
    "chaos-engineering": Priority.P1,
    "resource-constraints": Priority.P1,
    "evolutionary-pressure": Priority.P2,
    "trait-transfer": Priority.P2,
    "decision-tree-mapping": Priority.P2,
    "scenario-planning": Priority.P0,
    "okr": Priority.P0,
    "opportunity-spotting": Priority.P0,
    "what-if-scenarios": Priority.P1,
    "value-mapping": Priority.P1,
    "strength-analysis": Priority.P1,
    "plus-points": Priority.P2,
    "yes-and-building": Priority.P2,
    "future-self-interview": Priority.P2,
    "permission-giving": Priority.P2,
    "metaphor-mapping": Priority.P0,
    "mythic-frameworks": Priority.P0,
    "emotion-orchestra": Priority.P1,
    "time-travel-talk-show": Priority.P2,
    "drunk-history-retelling": Priority.P2,
    "business-model-canvas": Priority.P0,
    "balanced-scorecard": Priority.P0,
    "meta-analysis": Priority.P0,
    "six-thinking-hats": Priority.P1,
    "synthesis-framework": Priority.P1,
    "priority-matrix": Priority.P1,
    "consensus-building": Priority.P2,
    "indigenous-wisdom": Priority.P2,
}


class InvalidMappingError(Exception):
    """Raised when a mapping references a non-existent technique."""

    def __init__(self, invalid_ids: List[str]):
        self.invalid_ids = invalid_ids
        msg = f"Invalid technique IDs in mappings: {', '.join(invalid_ids)}"
        super().__init__(msg)


def get_techniques_for_category(
    category: TastingNote | str,
) -> List[TechniqueDefinition]:
    """Get all techniques for a Tasting Note category, sorted by priority.

    Args:
        category: The tasting note category (e.g., TastingNote.AROMA or "aroma").

    Returns:
        List of techniques sorted by priority (P0 first, then P1, then P2).
    """
    if isinstance(category, TastingNote):
        category = category.value

    registry = get_registry()
    techniques = registry.get_techniques_by_category(category)

    def priority_key(t: TechniqueDefinition) -> int:
        return TECHNIQUE_PRIORITY.get(t.id, Priority.P2).value

    return sorted(techniques, key=priority_key)


def get_primary_technique(
    category: TastingNote | str,
) -> Optional[TechniqueDefinition]:
    """Get the highest priority technique for a category.

    Args:
        category: The tasting note category.

    Returns:
        The highest priority technique (may be P0, P1, or P2 depending on
        what's available), or None if category is empty.
    """
    techniques = get_techniques_for_category(category)
    return techniques[0] if techniques else None


def get_technique_priority(technique_id: str) -> Priority:
    """Get the priority level for a technique.

    Args:
        technique_id: The technique identifier.

    Returns:
        Priority level (P0, P1, or P2). Defaults to P2 if not explicitly set.
    """
    return TECHNIQUE_PRIORITY.get(technique_id, Priority.P2)


def get_p0_techniques(category: TastingNote | str) -> List[TechniqueDefinition]:
    """Get all P0 (highest priority) techniques for a category.

    Args:
        category: The tasting note category.

    Returns:
        List of P0 priority techniques.
    """
    return [
        t
        for t in get_techniques_for_category(category)
        if get_technique_priority(t.id) == Priority.P0
    ]


def validate_mappings() -> bool:
    """Validate that all mapped technique IDs exist in the registry.

    Returns:
        True if all mappings are valid.

    Raises:
        InvalidMappingError: If any technique ID in TECHNIQUE_PRIORITY doesn't exist.
    """
    registry = get_registry()
    invalid_ids = [
        tech_id for tech_id in TECHNIQUE_PRIORITY.keys() if not registry.exists(tech_id)
    ]

    if invalid_ids:
        raise InvalidMappingError(invalid_ids)

    return True


def get_category_summary() -> Dict[str, Dict[str, int]]:
    """Get a summary of technique counts by category and priority.

    Returns:
        Dict mapping category to priority counts.
        Example: {"aroma": {"P0": 2, "P1": 4, "P2": 5}}
    """
    summary: Dict[str, Dict[str, int]] = {}

    for note in TastingNote:
        techniques = get_techniques_for_category(note)
        counts = {"P0": 0, "P1": 0, "P2": 0}
        for t in techniques:
            priority = get_technique_priority(t.id)
            counts[f"P{priority.value}"] += 1
        summary[note.value] = counts

    return summary


def list_all_mappings() -> Dict[str, List[str]]:
    """List all technique IDs grouped by category.

    Returns:
        Dict mapping category name to list of technique IDs (sorted by priority).
    """
    return {
        note.value: [t.id for t in get_techniques_for_category(note)]
        for note in TastingNote
    }
