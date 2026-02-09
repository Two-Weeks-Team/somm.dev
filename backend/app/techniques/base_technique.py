import abc
import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.models.graph import ItemScore, TraceEvent
from app.techniques.schema import TechniqueDefinition

logger = logging.getLogger(__name__)

RETRY_DELAYS = [1.0, 2.0, 4.0]  # exponential backoff


@dataclass
class TechniqueResult:
    technique_id: str
    item_scores: Dict[str, ItemScore] = field(default_factory=dict)
    trace_events: List[TraceEvent] = field(default_factory=list)
    token_usage: Dict[str, int] = field(
        default_factory=dict
    )  # {"prompt_tokens": N, "completion_tokens": N}
    cost_usd: float = 0.0
    success: bool = True
    error: Optional[str] = None


class BaseTechnique(abc.ABC):
    def __init__(self, definition: TechniqueDefinition):
        self.definition = definition
        self.id = definition.id
        self.name = definition.name

    async def evaluate(self, state: dict, item_id: str) -> TechniqueResult:
        """Execute the technique evaluation with retry logic."""
        result = TechniqueResult(technique_id=self.id)
        last_error = None

        for attempt, delay in enumerate(RETRY_DELAYS):
            try:
                raw_response = await self._call_llm(state, item_id)
                parsed = self._parse_response(raw_response, item_id)
                result.item_scores = parsed["item_scores"]
                result.trace_events = parsed["trace_events"]
                result.token_usage = parsed.get("token_usage", {})
                result.cost_usd = parsed.get("cost_usd", 0.0)
                result.success = True
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"Technique {self.id} attempt {attempt + 1} failed: {e}")
                if attempt < len(RETRY_DELAYS) - 1:
                    await asyncio.sleep(delay)

        # All retries exhausted — return error result
        logger.error(
            f"Technique {self.id} failed after {len(RETRY_DELAYS)} retries: {last_error}"
        )
        result.success = False
        result.error = str(last_error)
        result.item_scores = {
            item_id: ItemScore(
                item_id=item_id,
                score=0,
                evaluated_by=self.id,
                technique_id=self.id,
                timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                status="error",
                unevaluated_reason=str(last_error),
            )
        }
        return result

    @abc.abstractmethod
    async def _call_llm(self, state: dict, item_id: str) -> dict:
        """Call LLM and return raw response dict. Subclasses must implement."""
        ...

    @abc.abstractmethod
    def _parse_response(self, response: dict, item_id: str) -> dict:
        """Parse LLM response into item_scores, trace_events, token_usage.
        Must return: {"item_scores": {}, "trace_events": [], "token_usage": {}, "cost_usd": 0.0}
        """
        ...

    def _get_api_key(self, state: dict) -> Optional[str]:
        """Get API key from state (BYOK support)."""
        return state.get("user_api_key")

    def _get_api_key_source(self, state: dict) -> str:
        """Get API key source from state."""
        return state.get("api_key_source", "system")
