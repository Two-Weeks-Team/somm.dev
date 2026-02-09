from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from langchain_core.runnables import RunnableConfig
from app.graph.state import EvaluationState
from app.models.graph import ItemScore

CONFLICT_SCORE_RANGE_THRESHOLD = 2.0


async def deep_synthesis(
    state: EvaluationState, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:
    item_scores = dict(state.get("item_scores", {}))

    conflicts = []
    methodology_trace = list(state.get("methodology_trace", []))

    if methodology_trace:
        item_score_variants = {}
        for event in methodology_trace:
            if event.item_id and event.score_delta is not None:
                if event.item_id not in item_score_variants:
                    item_score_variants[event.item_id] = []
                item_score_variants[event.item_id].append(event.score_delta)

        for item_id, scores in item_score_variants.items():
            if len(scores) > 1:
                score_range = max(scores) - min(scores)
                if score_range > CONFLICT_SCORE_RANGE_THRESHOLD:
                    conflicts.append(
                        {
                            "item_id": item_id,
                            "score_range": score_range,
                            "min_score": min(scores),
                            "max_score": max(scores),
                        }
                    )

    return {
        "trace_metadata": {
            "deep_synthesis": {
                "total_items_scored": len(item_scores),
                "conflicts_detected": len(conflicts),
                "conflict_details": conflicts,
                "completed_at": datetime.now(timezone.utc).isoformat(),
            }
        },
        "completed_sommeliers": ["deep_synthesis"],
    }
