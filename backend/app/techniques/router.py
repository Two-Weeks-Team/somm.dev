import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from app.criteria.technique_mappings import (
    get_techniques_for_mode,
    TECHNIQUE_TO_ITEMS,
)
from app.models.graph import ItemScore
from app.techniques.base_technique import BaseTechnique, TechniqueResult
from app.techniques.registry import get_registry

logger = logging.getLogger(__name__)


@dataclass
class AggregatedResult:
    item_scores: Dict[str, ItemScore] = field(default_factory=dict)
    techniques_used: List[str] = field(default_factory=list)
    failed_techniques: List[Dict[str, str]] = field(default_factory=list)
    methodology_trace: list = field(default_factory=list)
    hat_contributions: Dict[str, Dict] = field(default_factory=dict)
    total_token_usage: Dict[str, int] = field(
        default_factory=lambda: {"prompt_tokens": 0, "completion_tokens": 0}
    )
    total_cost_usd: float = 0.0


class TechniqueRouter:
    def __init__(self, technique_factory: Optional[Callable] = None):
        """Initialize router. technique_factory creates BaseTechnique from TechniqueDefinition."""
        self._factory = technique_factory

    def select_techniques(
        self,
        mode: str,
        category: Optional[str] = None,
        hat: Optional[str] = None,
    ) -> List[str]:
        """Select technique IDs based on mode and optional filters."""
        technique_ids = get_techniques_for_mode(mode)

        if category:
            registry = get_registry()
            category_techs = set()
            for tech in registry.list_techniques():
                cat_val = (
                    tech.category.value
                    if hasattr(tech.category, "value")
                    else str(tech.category)
                )
                if cat_val == category:
                    category_techs.add(tech.id)
            technique_ids = [t for t in technique_ids if t in category_techs]

        if hat:
            from app.criteria.hat_mappings import HAT_TO_ITEMS

            hat_items = set(HAT_TO_ITEMS.get(hat, []))
            hat_techs = set()
            for t_id in technique_ids:
                t_items = set(TECHNIQUE_TO_ITEMS.get(t_id, []))
                if t_items & hat_items:
                    hat_techs.add(t_id)
            technique_ids = [t for t in technique_ids if t in hat_techs]

        return sorted(technique_ids)

    async def execute_techniques(
        self,
        technique_ids: List[str],
        state: dict,
        on_progress: Optional[Callable] = None,
    ) -> List[TechniqueResult]:
        """Execute techniques sequentially. Returns list of results."""
        registry = get_registry()
        results = []

        for i, tech_id in enumerate(technique_ids):
            definition = registry.get_technique(tech_id)
            if not definition:
                logger.warning(f"Technique {tech_id} not found in registry, skipping")
                continue

            try:
                technique = self._create_technique(definition)
                items = TECHNIQUE_TO_ITEMS.get(tech_id, [])
                primary_item = items[0] if items else "A1"
                result = await technique.evaluate(state, primary_item)
                results.append(result)

                if on_progress:
                    on_progress(i + 1, len(technique_ids), tech_id, result.success)

            except Exception as e:
                logger.error(f"Technique {tech_id} execution failed: {e}")
                results.append(
                    TechniqueResult(
                        technique_id=tech_id,
                        success=False,
                        error=str(e),
                    )
                )

        return results

    def aggregate_results(self, results: List[TechniqueResult]) -> AggregatedResult:
        """Aggregate technique results into final scores."""
        aggregated = AggregatedResult()

        for result in results:
            if result.success:
                aggregated.techniques_used.append(result.technique_id)
                aggregated.methodology_trace.extend(result.trace_events)
                aggregated.total_token_usage["prompt_tokens"] += result.token_usage.get(
                    "prompt_tokens", 0
                )
                aggregated.total_token_usage["completion_tokens"] += (
                    result.token_usage.get("completion_tokens", 0)
                )
                aggregated.total_cost_usd += result.cost_usd

                for item_id, score in result.item_scores.items():
                    self._merge_score(aggregated.item_scores, item_id, score)

                # Track hat contributions
                for item_id, score in result.item_scores.items():
                    hat = score.hat_used
                    if hat:
                        if hat not in aggregated.hat_contributions:
                            aggregated.hat_contributions[hat] = {
                                "techniques": [],
                                "items": [],
                            }
                        if (
                            result.technique_id
                            not in aggregated.hat_contributions[hat]["techniques"]
                        ):
                            aggregated.hat_contributions[hat]["techniques"].append(
                                result.technique_id
                            )
                        if item_id not in aggregated.hat_contributions[hat]["items"]:
                            aggregated.hat_contributions[hat]["items"].append(item_id)
            else:
                aggregated.failed_techniques.append(
                    {
                        "technique_id": result.technique_id,
                        "error": result.error or "Unknown error",
                    }
                )

        return aggregated

    def _merge_score(
        self, scores: Dict[str, ItemScore], item_id: str, new_score: ItemScore
    ) -> None:
        """Merge a new score with existing, preferring higher confidence."""
        if item_id not in scores:
            scores[item_id] = new_score
            return

        existing = scores[item_id]
        confidence_order = {"high": 3, "medium": 2, "low": 1, None: 0}
        existing_conf = confidence_order.get(existing.confidence, 0)
        new_conf = confidence_order.get(new_score.confidence, 0)

        if new_conf > existing_conf:
            scores[item_id] = new_score

    def _create_technique(self, definition) -> BaseTechnique:
        """Create a technique instance from definition."""
        if self._factory:
            return self._factory(definition)
        # Default: try YAMLTechnique, fallback to placeholder
        try:
            from app.techniques.yaml_technique import YAMLTechnique

            return YAMLTechnique(definition)
        except ImportError:
            # YAMLTechnique doesn't exist yet - use placeholder
            logger.warning(
                f"YAMLTechnique not available, using placeholder for {definition.id}"
            )
            return _PlaceholderTechnique(definition)


class _PlaceholderTechnique(BaseTechnique):
    """Placeholder technique for when YAMLTechnique is not available."""

    async def _call_llm(self, state: dict, item_id: str) -> dict:
        """Return empty response as placeholder."""
        return {
            "item_scores": {},
            "trace_events": [],
            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0},
            "cost_usd": 0.0,
        }

    def _parse_response(self, response: dict, item_id: str) -> dict:
        """Return response as-is."""
        return response
