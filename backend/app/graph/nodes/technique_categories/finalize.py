from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from langchain_core.runnables import RunnableConfig
from app.graph.state import EvaluationState
from app.criteria.bmad_items import list_items, get_category, get_category_max
from app.constants import get_quality_gate
from app.models.graph import ItemScore


async def finalize(
    state: EvaluationState, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:
    item_scores = state.get("item_scores", {})

    category_scores = {
        "A": {"score": 0.0, "max": 25},
        "B": {"score": 0.0, "max": 25},
        "C": {"score": 0.0, "max": 30},
        "D": {"score": 0.0, "max": 20},
    }

    evaluated_count = 0
    max_possible = 0
    total_score = 0.0

    for item in list_items():
        cat_id = item.item_id[0]
        score_obj = item_scores.get(item.item_id)

        if score_obj is None:
            continue

        score_value = (
            score_obj.score
            if isinstance(score_obj, ItemScore)
            else float(score_obj)
            if isinstance(score_obj, (int, float))
            else 0.0
        )
        status = score_obj.status if isinstance(score_obj, ItemScore) else "evaluated"

        if status == "evaluated":
            evaluated_count += 1
            max_possible += item.max_score
            total_score += min(score_value, item.max_score)
            if cat_id in category_scores:
                category_scores[cat_id]["score"] += min(score_value, item.max_score)

    coverage = evaluated_count / 17 if evaluated_count > 0 else 0.0
    normalized = (total_score / max_possible * 100) if max_possible > 0 else 0.0

    quality_gate = get_quality_gate(normalized, coverage)

    return {
        "trace_metadata": {
            "finalize": {
                "total_score": round(total_score, 2),
                "max_possible": max_possible,
                "normalized_score": round(normalized, 2),
                "coverage_rate": round(coverage, 4),
                "quality_gate": quality_gate,
                "category_scores": category_scores,
                "evaluated_count": evaluated_count,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        },
        "completed_sommeliers": ["finalize"],
        "total_score": round(total_score, 2),
        "normalized_score": round(normalized, 2),
        "coverage_rate": round(coverage, 4),
        "quality_gate": quality_gate,
        "category_scores": category_scores,
    }
