"""Six Thinking Hats to BMAD item mappings.

This module maps Edward de Bono's Six Thinking Hats to the 17 BMAD evaluation items,
enabling multi-perspective code evaluation.
"""

from enum import Enum
from typing import Dict, List


class Hat(str, Enum):
    WHITE = "white"  # Facts & Data
    RED = "red"  # Emotions & Feelings
    BLACK = "black"  # Caution & Risk
    YELLOW = "yellow"  # Optimism & Benefits
    GREEN = "green"  # Creativity & Innovation
    BLUE = "blue"  # Process & Meta-thinking


# Hat → BMAD items mapping
# Each hat evaluates specific BMAD items based on its perspective
HAT_TO_ITEMS: Dict[str, List[str]] = {
    Hat.WHITE.value: ["A1", "A2", "A3", "A4", "C1", "D1", "D2"],
    Hat.RED.value: ["A1", "A3", "B1", "C1", "C3"],
    Hat.BLACK.value: ["B3", "B4", "C3", "C4", "C5"],
    Hat.YELLOW.value: ["A3", "A4", "B1", "B2", "C5"],
    Hat.GREEN.value: ["B1", "B2", "B3", "C1", "C2"],
    Hat.BLUE.value: ["A1", "A2", "B1", "D1", "D2", "D3", "D4"],
}

# Reverse mapping: BMAD item → hats that evaluate it
ITEM_TO_HATS: Dict[str, List[str]] = {}
for hat, items in HAT_TO_ITEMS.items():
    for item in items:
        if item not in ITEM_TO_HATS:
            ITEM_TO_HATS[item] = []
        ITEM_TO_HATS[item].append(hat)
# Sort for deterministic output
for item in ITEM_TO_HATS:
    ITEM_TO_HATS[item] = sorted(ITEM_TO_HATS[item])


def get_items_for_hat(hat: str) -> List[str]:
    """Get BMAD items evaluated by a specific hat.

    Args:
        hat: The hat color (white, red, black, yellow, green, blue).

    Returns:
        Sorted list of BMAD item IDs evaluated by this hat.
    """
    return sorted(HAT_TO_ITEMS.get(hat, []))


def get_hats_for_item(item_id: str) -> List[str]:
    """Get hats that evaluate a specific BMAD item.

    Args:
        item_id: The BMAD item ID (e.g., "A1", "B2").

    Returns:
        Sorted list of hat colors that evaluate this item.
    """
    return ITEM_TO_HATS.get(item_id, [])


def get_all_hats() -> List[str]:
    """Get all hat values.

    Returns:
        List of all six hat color values.
    """
    return [h.value for h in Hat]


def validate_coverage() -> List[str]:
    """Return list of BMAD items NOT covered by any hat (should be empty).

    Returns:
        Sorted list of uncovered BMAD item IDs. Empty list means full coverage.
    """
    from app.criteria.bmad_items import BMAD_ITEMS

    all_items = set(BMAD_ITEMS.keys())
    covered = set(ITEM_TO_HATS.keys())
    return sorted(all_items - covered)
