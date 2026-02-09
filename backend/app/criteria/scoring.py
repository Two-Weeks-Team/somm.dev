"""Scoring aggregation module for BMAD evaluation system."""

from enum import Enum
from typing import Literal

# Constants
NEUTRAL_SCORE_RATIO = 0.5
CONFIDENCE_MULTIPLIERS = {"high": 1.0, "medium": 0.85, "low": 0.7}

# Absence keywords for detecting missing information
ABSENCE_KEYWORDS = [
    "no information",
    "not found",
    "not available",
    "cannot determine",
    "insufficient data",
    "no evidence",
    "unable to assess",
    "not provided",
    "absent",
    "missing",
]


class ItemStatus(str, Enum):
    EVALUATED = "evaluated"
    EXCLUDED = "excluded"
    DATA_MISSING = "data_missing"
    EVALUATION_FAILED = "evaluation_failed"


ConfidenceLevel = Literal["high", "medium", "low"]


def adjust_score_by_confidence(
    raw_score: float, max_score: float, confidence: ConfidenceLevel
) -> float:
    """Adjust a raw score based on confidence level.

    Args:
        raw_score: The original score value
        max_score: The maximum possible score for this item
        confidence: Confidence level - "high", "medium", or "low"

    Returns:
        Adjusted score clamped to [0, max_score]

    Behavior:
        - HIGH: raw_score * 1.0 (no change)
        - MEDIUM: raw_score * 0.85
        - LOW: weighted average toward neutral (0.3 * raw_score + 0.7 * (max_score * 0.5))
    """
    if confidence == "high":
        adjusted = raw_score * CONFIDENCE_MULTIPLIERS["high"]
    elif confidence == "medium":
        adjusted = raw_score * CONFIDENCE_MULTIPLIERS["medium"]
    elif confidence == "low":
        neutral_score = max_score * NEUTRAL_SCORE_RATIO
        adjusted = 0.3 * raw_score + 0.7 * neutral_score
    else:
        adjusted = raw_score

    # Clamp to [0, max_score]
    return max(0.0, min(adjusted, max_score))


def calculate_exclusion_normalized_score(item_scores: dict) -> dict:
    """Calculate normalized score accounting for excluded items.

    Args:
        item_scores: Dict[str, dict] where each value has keys:
            - score: float
            - max_score: float
            - status: str (one of ItemStatus values)

    Returns:
        Dictionary with:
            - raw_score: Sum of all evaluated item scores
            - max_possible: Sum of max scores for evaluated items
            - normalized_score: Percentage (0-100) of max_possible achieved
            - evaluated_items: List of item_ids that were evaluated
            - excluded_items: List of item_ids that were not evaluated
            - coverage_rate: Ratio of evaluated items to total BMAD items (17)
            - summary: Human-readable summary string
    """
    total_bmad_items = 17

    evaluated_items = []
    excluded_items = []
    raw_score = 0.0
    max_possible = 0.0

    for item_id, item_data in item_scores.items():
        status = item_data.get("status", ItemStatus.DATA_MISSING)
        if status == ItemStatus.EVALUATED:
            evaluated_items.append(item_id)
            raw_score += item_data.get("score", 0.0)
            max_possible += item_data.get("max_score", 0.0)
        else:
            excluded_items.append(item_id)

    # Calculate normalized score
    if max_possible > 0:
        normalized_score = (raw_score / max_possible) * 100
    else:
        normalized_score = 0.0

    # Calculate coverage rate
    coverage_rate = len(evaluated_items) / total_bmad_items

    # Generate summary
    summary = (
        f"Evaluated {len(evaluated_items)}/{total_bmad_items} items "
        f"({coverage_rate:.1%} coverage), "
        f"score: {normalized_score:.1f}%"
    )

    return {
        "raw_score": raw_score,
        "max_possible": max_possible,
        "normalized_score": normalized_score,
        "evaluated_items": evaluated_items,
        "excluded_items": excluded_items,
        "coverage_rate": coverage_rate,
        "summary": summary,
    }


def apply_confidence_adjustment_to_scores(item_scores: dict) -> dict:
    """Apply confidence adjustment to all items in the scores dictionary.

    Args:
        item_scores: Dict[str, dict] where each value has keys:
            - score: float
            - confidence: ConfidenceLevel
            - status: str (optional)

    Returns:
        New dictionary with adjusted scores (input is not mutated)
    """
    from app.criteria.bmad_items import get_item

    adjusted_scores = {}

    for item_id, item_data in item_scores.items():
        # Create a copy to avoid mutating input
        adjusted_item = dict(item_data)

        # Only adjust evaluated items
        status = item_data.get("status", ItemStatus.EVALUATED)
        if status == ItemStatus.EVALUATED:
            raw_score = item_data.get("score", 0.0)
            confidence = item_data.get("confidence", "medium")

            # Get max_score from bmad_items
            try:
                bmad_item = get_item(item_id)
                max_score = float(bmad_item.max_score)
            except KeyError:
                # Fallback to item_data max_score if item not found
                max_score = item_data.get("max_score", 100.0)

            adjusted_score = adjust_score_by_confidence(
                raw_score, max_score, confidence
            )
            adjusted_item["score"] = adjusted_score

        adjusted_scores[item_id] = adjusted_item

    return adjusted_scores


def is_information_absent(evidence: list[str] | None, rationale: str | None) -> bool:
    """Check if information is absent based on evidence and rationale.

    Args:
        evidence: List of evidence strings, or None
        rationale: Explanation string, or None

    Returns:
        True if information is absent (no evidence or absence keywords in rationale)
    """
    # Check if evidence is None or empty
    if evidence is None or len(evidence) == 0:
        return True

    # Check if rationale contains absence keywords
    if rationale is not None:
        rationale_lower = rationale.lower()
        for keyword in ABSENCE_KEYWORDS:
            if keyword in rationale_lower:
                return True

    return False
