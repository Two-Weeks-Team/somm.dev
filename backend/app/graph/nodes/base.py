"""Base class for all sommelier nodes."""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from langchain_core.runnables import RunnableConfig
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import EvaluationState
from app.graph.schemas import SommelierOutput
from app.providers.llm import build_llm


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
        try:
            prompt = self.get_prompt(state["evaluation_criteria"])
            prompt_inputs = {
                "repo_context": state["repo_context"],
                "criteria": state["evaluation_criteria"],
                "format_instructions": self.parser.get_format_instructions(),
            }
            messages = prompt.format_messages(**prompt_inputs)
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
            observability["trace_metadata"][self.name]["completed_at"] = datetime.now(
                timezone.utc
            ).isoformat()
            result = self.parser.parse(response.content)
            return {
                f"{self.name}_result": result.dict(),
                **observability,
            }
        except Exception as e:
            observability["trace_metadata"][self.name]["completed_at"] = datetime.now(
                timezone.utc
            ).isoformat()
            return {
                "errors": [f"{self.name} evaluation failed: {e!s}"],
                f"{self.name}_result": None,
                **observability,
            }
