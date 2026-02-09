"""Technique to Hat/Item/Mode mappings.

Maps techniques to their primary BMAD evaluation items and provides
filtering by evaluation mode (grand_tasting, six_sommeliers, full_techniques).
"""

from typing import Dict, List, Optional

from app.techniques.mappings import TECHNIQUE_PRIORITY, Priority
from app.techniques.registry import get_registry


# Technique → BMAD item mappings (primary evaluations)
# Each technique has primary items it evaluates
TECHNIQUE_TO_ITEMS: Dict[str, List[str]] = {
    # Aroma (problem-analysis) techniques
    "five-whys": ["A1", "A2"],
    "5w1h": ["A1", "A2", "A3"],
    "question-storming": ["A1", "A3"],
    "failure-analysis": ["A4", "B4"],
    "assumption-reversal": ["A3", "A4"],
    "data-mining": ["A2", "A3"],
    "fact-checking": ["A1", "D1"],
    "morphological-analysis": ["A3", "B2"],
    "pestle-analysis": ["A3", "A4"],
    "mind-mapping": ["A1", "B1"],
    "constraint-mapping": ["A4", "B3"],
    # Palate (innovation) techniques
    "first-principles-thinking": ["B1", "B2"],
    "scamper": ["B1", "B2"],
    "design-thinking": ["B1", "A2"],
    "triz": ["B2", "B3"],
    "cross-pollination": ["B1", "B2"],
    "concept-blending": ["B1", "B2"],
    "lateral-thinking": ["B1", "B3"],
    "random-stimulation": ["B1"],
    "biomimicry": ["B2", "B3"],
    "analogical-thinking": ["B1", "B2"],
    "reversal-inversion": ["B1", "B3"],
    "provocation-technique": ["B1"],
    "quantum-superposition": ["B1", "B2"],
    # Body (risk-analysis) techniques
    "reverse-brainstorming": ["B4", "C3"],
    "pre-mortem": ["B4", "C3"],
    "swot-analysis": ["B3", "B4"],
    "fmea": ["B4", "C3"],
    "risk-matrix": ["B4", "C4"],
    "anti-solution": ["B4", "C3"],
    "devil-advocate": ["B4", "C3"],
    "zombie-apocalypse": ["B4"],
    # Finish (user-centricity) techniques
    "empathy-mapping": ["A2", "A3"],
    "jobs-to-be-done": ["A2", "A3"],
    "kano-model": ["A2", "A4"],
    "persona-journey": ["A2", "A3"],
    "role-playing": ["A2"],
    "emotional-journey": ["A2", "A3"],
    "sensory-exploration": ["A2"],
    "gut-check": ["A1"],
    "body-wisdom-dialogue": ["A2"],
    "inner-child-conference": ["A2"],
    "alien-anthropologist": ["A2", "A3"],
    "first-impression-analysis": ["A1", "D1"],
    # Balance (feasibility) techniques
    "technology-readiness-level": ["B2", "B3"],
    "porters-five-forces": ["A4", "B3"],
    "ecosystem-thinking": ["B3", "C5"],
    "chaos-engineering": ["C3", "C4"],
    "resource-constraints": ["B3", "C4"],
    "evolutionary-pressure": ["B3"],
    "trait-transfer": ["B2"],
    "decision-tree-mapping": ["B3", "C4"],
    # Vintage (opportunity) techniques
    "scenario-planning": ["A4", "B3"],
    "okr": ["A1", "A3"],
    "opportunity-spotting": ["A3", "A4"],
    "what-if-scenarios": ["A4", "B3"],
    "value-mapping": ["A3", "A4"],
    "strength-analysis": ["A3", "B1"],
    "plus-points": ["A3"],
    "yes-and-building": ["A3", "B1"],
    "future-self-interview": ["A4"],
    "permission-giving": ["A3"],
    # Terroir (presentation) techniques
    "metaphor-mapping": ["D1", "D3"],
    "mythic-frameworks": ["D1", "D3"],
    "emotion-orchestra": ["D1"],
    "time-travel-talk-show": ["D1", "D4"],
    "drunk-history-retelling": ["D1"],
    # Cellar (synthesis) techniques
    "business-model-canvas": ["A4", "B1"],
    "balanced-scorecard": ["A3", "B1"],
    "meta-analysis": ["C1", "C2"],
    "six-thinking-hats": ["A1", "B1"],
    "synthesis-framework": ["C1", "D3"],
    "priority-matrix": ["B3", "C4"],
    "consensus-building": ["D3", "D4"],
    "indigenous-wisdom": ["A3"],
}


def get_techniques_for_hat(hat: str) -> List[str]:
    """Get technique IDs that are applicable to a given hat.

    Args:
        hat: The hat color (white, red, black, yellow, green, blue).

    Returns:
        Sorted list of technique IDs applicable to this hat.
    """
    registry = get_registry()
    all_techs = registry.list_techniques()
    result = []
    for tech in all_techs:
        if hat in tech.applicable_hats:
            result.append(tech.id)
    return sorted(result)


def get_techniques_for_item(item_code: str) -> List[str]:
    """Get technique IDs that evaluate a specific BMAD item.

    Args:
        item_code: The BMAD item ID (e.g., "A1", "B2").

    Returns:
        Sorted list of technique IDs that evaluate this item.
    """
    return sorted(
        [tech_id for tech_id, items in TECHNIQUE_TO_ITEMS.items() if item_code in items]
    )


def get_techniques_for_mode(mode: str) -> List[str]:
    """Get technique IDs filtered by evaluation mode and priority.

    Args:
        mode: The evaluation mode ("full_techniques", "grand_tasting", "six_sommeliers").

    Returns:
        Sorted list of technique IDs matching the mode criteria.
    """
    registry = get_registry()
    all_techs = registry.list_techniques()
    all_ids = [t.id for t in all_techs]

    if mode == "full_techniques":
        return sorted(all_ids)

    if mode == "grand_tasting":
        return sorted(
            [
                t_id
                for t_id in all_ids
                if TECHNIQUE_PRIORITY.get(t_id, Priority.P2) == Priority.P0
            ]
        )

    if mode == "six_sommeliers":
        return sorted(
            [
                t_id
                for t_id in all_ids
                if TECHNIQUE_PRIORITY.get(t_id, Priority.P2)
                in (Priority.P0, Priority.P1)
            ]
        )

    return sorted(all_ids)


def get_primary_technique_for_item(item_code: str) -> Optional[str]:
    """Get the highest priority technique for a BMAD item.

    Args:
        item_code: The BMAD item ID (e.g., "A1", "B2").

    Returns:
        The highest priority technique ID, or None if no techniques evaluate this item.
    """
    tech_ids = get_techniques_for_item(item_code)
    if not tech_ids:
        return None
    best = None
    best_priority = Priority.P2.value + 1
    for t_id in tech_ids:
        p = TECHNIQUE_PRIORITY.get(t_id, Priority.P2).value
        if p < best_priority:
            best_priority = p
            best = t_id
    return best
