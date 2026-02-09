import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from langchain_core.runnables import RunnableConfig
from app.graph.state import EvaluationState
from app.techniques.router import TechniqueRouter
from app.techniques.schema import TechniqueCategory

logger = logging.getLogger(__name__)


class BaseCategoryNode(ABC):
    def __init__(self):
        self.router = TechniqueRouter()

    @property
    @abstractmethod
    def category(self) -> TechniqueCategory:
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        pass

    async def evaluate(
        self, state: EvaluationState, config: Optional[RunnableConfig] = None
    ) -> Dict[str, Any]:
        started_at = datetime.now(timezone.utc).isoformat()

        technique_ids = self.router.select_techniques(
            mode="full_techniques", category=self.category.value
        )

        if not technique_ids:
            logger.warning(f"{self.category.value}: no techniques available")
            return self._empty_result(started_at)

        logger.info(f"{self.category.value}: running {len(technique_ids)} techniques")

        results = await self.router.execute_techniques(technique_ids, dict(state))
        aggregated = self.router.aggregate_results(results)

        return {
            "item_scores": aggregated.item_scores,
            "techniques_used": aggregated.techniques_used,
            "methodology_trace": aggregated.methodology_trace,
            "completed_sommeliers": [self.category.value],
            "token_usage": {self.category.value: aggregated.total_token_usage},
            "cost_usage": {self.category.value: aggregated.total_cost_usd},
            "trace_metadata": {
                self.category.value: {
                    "started_at": started_at,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "techniques_count": len(technique_ids),
                    "techniques_succeeded": len(aggregated.techniques_used),
                    "techniques_failed": len(aggregated.failed_techniques),
                    "failed_techniques": aggregated.failed_techniques,
                }
            },
        }

    def _empty_result(self, started_at: str) -> Dict[str, Any]:
        return {
            "errors": [f"{self.category.value}: no techniques available"],
            "completed_sommeliers": [self.category.value],
            "token_usage": {self.category.value: {}},
            "cost_usage": {self.category.value: 0.0},
            "trace_metadata": {
                self.category.value: {
                    "started_at": started_at,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "techniques_count": 0,
                }
            },
        }
