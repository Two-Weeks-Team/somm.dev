"""Base class for all sommelier nodes."""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from langchain_core.runnables import RunnableConfig
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import EvaluationState
from app.graph.schemas import SommelierOutput
from app.providers.llm import build_llm
from app.services.event_channel import create_sommelier_event, get_event_channel

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]

SOMMELIER_PROGRESS = {
    "marcel": {"start": 10, "complete": 25},
    "isabella": {"start": 25, "complete": 40},
    "heinrich": {"start": 40, "complete": 55},
    "sofia": {"start": 55, "complete": 70},
    "laurent": {"start": 70, "complete": 85},
    "jeanpierre": {"start": 85, "complete": 100},
}


class BaseSommelierNode(ABC):
    """Abstract base class for all sommelier evaluation nodes.

    Provides common LLM configuration, output parsing, and evaluation logic
    that can be inherited by specific sommelier implementations.
    """

    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=SommelierOutput)

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name identifier for this sommelier."""
        pass

    @property
    @abstractmethod
    def role(self) -> str:
        """Return the role description for this sommelier."""
        pass

    @abstractmethod
    def get_prompt(self, criteria: str) -> ChatPromptTemplate:
        """Return the evaluation prompt template for this sommelier."""
        pass

    async def evaluate(
        self, state: EvaluationState, config: Optional[RunnableConfig] = None
    ) -> Dict[str, Any]:
        """Execute the evaluation for this sommelier.

        Args:
            state: The current evaluation state containing repo context and criteria.
            config: Optional RunnableConfig for the LLM chain.

        Returns:
            Dictionary containing the sommelier result and completion status.
        """
        evaluation_id = state.get("evaluation_id", "")
        progress_config = SOMMELIER_PROGRESS.get(
            self.name, {"start": 0, "complete": 100}
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
                    message=f"{self.name} analysis starting...",
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
                            message=f"{self.name} analysis complete",
                            tokens_used=usage.get("total_tokens", 0),
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
                    message=f"{self.name} analysis encountered an error",
                ),
            )

        return {
            "errors": [f"{self.name} evaluation failed: {last_error!s}"],
            f"{self.name}_result": None,
            **observability,
        }
