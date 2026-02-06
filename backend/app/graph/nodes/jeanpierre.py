"""Jean-Pierre (Master Sommelier) node implementation.

Focus: Final synthesis, weighted verdict.
Color: #4169E1
Style: Wise, synthesizing, final verdict.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableConfig

from app.graph.nodes.base import (
    BaseSommelierNode,
    SOMMELIER_PROGRESS,
    MAX_RETRIES,
    RETRY_DELAYS,
)

logger = logging.getLogger(__name__)
from app.graph.schemas import FinalEvaluation
from app.graph.state import EvaluationState
from app.prompts.jeanpierre import get_jeanpierre_prompt
from app.providers.llm import build_llm
from app.services.event_channel import create_sommelier_event, get_event_channel


class JeanPierreNode(BaseSommelierNode):
    """Jean-Pierre - Master Sommelier focused on final synthesis.

    Synthesizes all sommelier evaluations into a final weighted verdict
    with the wisdom of a master sommelier.
    """

    name = "jeanpierre"
    role = "Master Sommelier"

    def __init__(self):
        """Initialize with FinalEvaluation schema instead of SommelierOutput."""
        self.parser = PydanticOutputParser(pydantic_object=FinalEvaluation)

    def get_prompt(self, criteria: str):
        """Return Jean-Pierre's synthesis prompt template."""
        return get_jeanpierre_prompt()

    async def evaluate(
        self, state: EvaluationState, config: Optional[RunnableConfig] = None
    ) -> Dict[str, Any]:
        """Execute the synthesis evaluation with all sommelier results.

        Unlike other sommeliers, Jean-Pierre needs access to all previous
        sommelier results for synthesis.
        """
        evaluation_id = state.get("evaluation_id", "")
        progress_config = SOMMELIER_PROGRESS.get(
            self.name, {"start": 85, "complete": 100}
        )
        event_channel = get_event_channel()

        if evaluation_id:
            event_channel.emit_sync(
                evaluation_id,
                create_sommelier_event(
                    evaluation_id=evaluation_id,
                    sommelier=self.name,
                    event_type="sommelier_start",
                    progress_percent=progress_config["start"],
                    message=f"{self.name} synthesis starting...",
                ),
            )

        started_at = datetime.now(timezone.utc).isoformat()
        configurable = (config or {}).get("configurable", {})
        provider = configurable.get("provider", "gemini")
        api_key = configurable.get("api_key")
        model = configurable.get("model")
        temperature = configurable.get("temperature")
        max_output_tokens = configurable.get("max_output_tokens", 2048)
        llm = build_llm(
            provider=provider,
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )
        model_name = model or getattr(
            llm, "model", getattr(llm, "model_name", "unknown")
        )
        observability = {
            "completed_sommeliers": [self.name],
            "token_usage": {self.name: {}},
            "cost_usage": {self.name: None},
            "trace_metadata": {
                self.name: {
                    "started_at": started_at,
                    "completed_at": None,
                    "model": model_name,
                    "provider": provider,
                }
            },
        }
        prompt = self.get_prompt(state["evaluation_criteria"])
        prompt_inputs = {
            "repo_context": state["repo_context"],
            "criteria": state["evaluation_criteria"],
            "format_instructions": self.parser.get_format_instructions(),
            "marcel_result": state.get("marcel_result") or "Not available",
            "isabella_result": state.get("isabella_result") or "Not available",
            "heinrich_result": state.get("heinrich_result") or "Not available",
            "sofia_result": state.get("sofia_result") or "Not available",
            "laurent_result": state.get("laurent_result") or "Not available",
        }
        messages = prompt.format_messages(**prompt_inputs)

        last_error: Optional[Exception] = None
        for attempt in range(MAX_RETRIES):
            try:
                response = await llm.ainvoke(messages, config=config)
                usage = getattr(response, "usage_metadata", {}) or {}
                observability["token_usage"] = {
                    self.name: {
                        "input_tokens": usage.get("input_tokens"),
                        "output_tokens": usage.get("output_tokens"),
                        "total_tokens": usage.get("total_tokens"),
                    }
                }
                observability["cost_usage"] = {self.name: usage.get("total_cost")}
                observability["trace_metadata"][self.name]["completed_at"] = (
                    datetime.now(timezone.utc).isoformat()
                )
                result = self.parser.parse(response.content)

                if evaluation_id:
                    event_channel.emit_sync(
                        evaluation_id,
                        create_sommelier_event(
                            evaluation_id=evaluation_id,
                            sommelier=self.name,
                            event_type="sommelier_complete",
                            progress_percent=progress_config["complete"],
                            message=f"{self.name} synthesis complete",
                            tokens_used=usage.get("total_tokens", 0),
                        ),
                    )
                    event_channel.emit_sync(
                        evaluation_id,
                        create_sommelier_event(
                            evaluation_id=evaluation_id,
                            sommelier=self.name,
                            event_type="evaluation_complete",
                            progress_percent=100,
                            message="Evaluation complete!",
                        ),
                    )

                return {
                    f"{self.name}_result": result.dict(),
                    **observability,
                }
            except Exception as e:
                last_error = e
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAYS[attempt]
                    logger.warning(
                        f"{self.name} attempt {attempt + 1} failed: {e!s}. "
                        f"Retrying in {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"{self.name} failed after {MAX_RETRIES} attempts: {e!s}"
                    )

        observability["trace_metadata"][self.name]["completed_at"] = datetime.now(
            timezone.utc
        ).isoformat()

        if evaluation_id:
            event_channel.emit_sync(
                evaluation_id,
                create_sommelier_event(
                    evaluation_id=evaluation_id,
                    sommelier=self.name,
                    event_type="sommelier_error",
                    progress_percent=progress_config["start"],
                    message=f"{self.name} synthesis encountered an error",
                ),
            )

        return {
            "errors": [f"{self.name} evaluation failed: {last_error!s}"],
            f"{self.name}_result": None,
            **observability,
        }
