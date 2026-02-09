import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from langchain_core.runnables import RunnableConfig

from app.core.config import settings
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

    async def _execute_technique_with_limit(
        self,
        sem: asyncio.Semaphore,
        technique_id: str,
        state: Dict[str, Any],
    ) -> Dict[str, Any]:
        async with sem:
            try:
                result = await asyncio.wait_for(
                    self.router.execute_single_technique(technique_id, dict(state)),
                    timeout=settings.TECHNIQUE_TIMEOUT_SECONDS,
                )
                return {"result": result, "technique_id": technique_id}
            except asyncio.TimeoutError:
                logger.error(
                    f"Technique {technique_id} timed out after {settings.TECHNIQUE_TIMEOUT_SECONDS}s"
                )
                return {
                    "technique_id": technique_id,
                    "error": f"timeout after {settings.TECHNIQUE_TIMEOUT_SECONDS}s",
                    "failed": True,
                }
            except Exception as e:
                logger.error(f"Technique {technique_id} execution failed: {e}")
                return {
                    "technique_id": technique_id,
                    "error": str(e),
                    "failed": True,
                }

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

        logger.info(
            f"{self.category.value}: running {len(technique_ids)} techniques concurrently (max {settings.MAX_CONCURRENT_TECHNIQUES})"
        )

        sem = asyncio.Semaphore(settings.MAX_CONCURRENT_TECHNIQUES)

        tasks = [
            self._execute_technique_with_limit(sem, tid, dict(state))
            for tid in technique_ids
        ]

        try:
            task_results = await asyncio.gather(*tasks, return_exceptions=False)
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

        successful_results = []
        failed_techniques = []

        for task_result in task_results:
            if task_result.get("failed"):
                failed_techniques.append(
                    {
                        "technique_id": task_result["technique_id"],
                        "error": task_result.get("error", "Unknown error"),
                    }
                )
            elif "result" in task_result:
                successful_results.append(task_result["result"])
            else:
                failed_techniques.append(
                    {
                        "technique_id": task_result.get("technique_id", "unknown"),
                        "error": "Invalid result format",
                    }
                )

        aggregated = self.router.aggregate_results(successful_results)

        all_failed_techniques = (
            list(aggregated.failed_techniques or []) + failed_techniques
        )

        if evaluation_id:
            event_channel.emit_sync(
                evaluation_id,
                create_sommelier_event(
                    evaluation_id=evaluation_id,
                    sommelier=self.category.value,
                    event_type="sommelier_complete",
                    progress_percent=progress_config["complete"],
                    message=f"{self.display_name} complete",
                    tokens_used=aggregated.total_token_usage.get("prompt_tokens", 0)
                    + aggregated.total_token_usage.get("completion_tokens", 0),
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
                    "techniques_failed": len(all_failed_techniques),
                    "failed_techniques": all_failed_techniques,
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
