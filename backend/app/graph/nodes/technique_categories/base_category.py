import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from langchain_core.runnables import RunnableConfig
from app.graph.state import EvaluationState
from app.techniques.router import TechniqueRouter
from app.techniques.schema import TechniqueCategory
from app.services.event_channel import create_sommelier_event, get_event_channel

logger = logging.getLogger(__name__)

CATEGORY_PROGRESS = {
    "aroma": {"start": 10, "complete": 20},
    "palate": {"start": 20, "complete": 30},
    "body": {"start": 30, "complete": 40},
    "finish": {"start": 40, "complete": 50},
    "balance": {"start": 50, "complete": 60},
    "vintage": {"start": 60, "complete": 70},
    "terroir": {"start": 70, "complete": 80},
    "cellar": {"start": 80, "complete": 90},
}


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
        evaluation_id = state.get("evaluation_id", "")
        progress_config = CATEGORY_PROGRESS.get(
            self.category.value, {"start": 0, "complete": 100}
        )
        event_channel = get_event_channel()

        if evaluation_id:
            event_channel.emit_sync(
                evaluation_id,
                create_sommelier_event(
                    evaluation_id=evaluation_id,
                    sommelier=self.category.value,
                    event_type="sommelier_start",
                    progress_percent=progress_config["start"],
                    message=f"{self.display_name} analysis starting...",
                ),
            )

        technique_ids = self.router.select_techniques(
            mode="full_techniques", category=self.category.value
        )

        if not technique_ids:
            logger.warning(f"{self.category.value}: no techniques available")
            if evaluation_id:
                event_channel.emit_sync(
                    evaluation_id,
                    create_sommelier_event(
                        evaluation_id=evaluation_id,
                        sommelier=self.category.value,
                        event_type="sommelier_complete",
                        progress_percent=progress_config["complete"],
                        message=f"{self.display_name} complete (no techniques)",
                    ),
                )
            return self._empty_result(started_at)

        logger.info(f"{self.category.value}: running {len(technique_ids)} techniques")

        try:
            results = await self.router.execute_techniques(technique_ids, dict(state))
            aggregated = self.router.aggregate_results(results)
        except Exception as e:
            logger.error(f"{self.category.value}: execution failed - {e}")
            if evaluation_id:
                event_channel.emit_sync(
                    evaluation_id,
                    create_sommelier_event(
                        evaluation_id=evaluation_id,
                        sommelier=self.category.value,
                        event_type="sommelier_error",
                        progress_percent=progress_config["start"],
                        message=f"{self.display_name} failed",
                    ),
                )
            return {
                "errors": [f"{self.category.value}: {str(e)}"],
                "completed_sommeliers": [self.category.value],
                "token_usage": {self.category.value: {}},
                "cost_usage": {self.category.value: 0.0},
                "trace_metadata": {
                    self.category.value: {
                        "started_at": started_at,
                        "completed_at": datetime.now(timezone.utc).isoformat(),
                        "error": str(e),
                    }
                },
            }

        if evaluation_id:
            event_channel.emit_sync(
                evaluation_id,
                create_sommelier_event(
                    evaluation_id=evaluation_id,
                    sommelier=self.category.value,
                    event_type="sommelier_complete",
                    progress_percent=progress_config["complete"],
                    message=f"{self.display_name} complete",
                    tokens_used=aggregated.total_token_usage.get("total_tokens", 0),
                ),
            )

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
