"""Base class for all sommelier nodes."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from langchain_core.runnables import RunnableConfig
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.graph.state import EvaluationState
from app.graph.schemas import SommelierOutput
from app.providers.llm import build_llm, extract_text_content
from app.providers.llm_policy import invoke_with_policy, RetryConfig
from app.providers.llm_errors import ErrorCategory
from app.services.event_channel import create_sommelier_event, get_event_channel
from app.services.llm_context import render_repo_context, get_context_budget

logger = logging.getLogger(__name__)

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

        context_budget = get_context_budget(provider, model)
        rendered_context, context_meta = render_repo_context(
            state["repo_context"], max_tokens=context_budget
        )

        rag_context = state.get("rag_context", {})
        rag_chunks = rag_context.get("chunks", [])
        if rag_chunks:
            rag_section = "\n\n## Retrieved Context (RAG)\n"
            for chunk in rag_chunks:
                rag_section += f"\n### [{chunk['source']}]\n{chunk['text']}\n"
            rendered_context += rag_section

        web_context = state.get("web_search_context", {})
        web_content = web_context.get("content", "")
        if web_content:
            web_section = "\n\n## Latest Industry Context (Web Search)\n"
            web_section += web_content[:3000]
            web_sources = web_context.get("sources", [])
            if web_sources:
                web_section += "\n\n**Sources:**\n"
                for src in web_sources[:5]:
                    web_section += f"- [{src.get('title', '')}]({src.get('uri', '')})\n"
            rendered_context += web_section

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
                    "estimated_input_tokens": context_meta["estimated_tokens"],
                    "context_truncated": context_meta["truncated"],
                }
            },
        }
        prompt = self.get_prompt(state["evaluation_criteria"])
        prompt_inputs = {
            "repo_context": rendered_context,
            "criteria": state["evaluation_criteria"],
            "format_instructions": self.parser.get_format_instructions(),
        }
        messages = prompt.format_messages(**prompt_inputs)

        def on_retry(attempt: int, delay: float, msg: str) -> None:
            logger.info(f"{self.name}: {msg}")
            if evaluation_id:
                event_channel.emit_sync(
                    evaluation_id,
                    create_sommelier_event(
                        evaluation_id=evaluation_id,
                        sommelier=self.name,
                        event_type="sommelier_retry",
                        progress_percent=progress_config["start"],
                        message=f"{self.name} retrying ({attempt}/3)...",
                    ),
                )

        invocation_result = await invoke_with_policy(
            llm=llm,
            messages=messages,
            provider=provider,
            config=RetryConfig(max_attempts=3, base_delay=2.0, max_delay=60.0),
            langchain_config=config,
            on_retry=on_retry,
        )

        observability["trace_metadata"][self.name]["completed_at"] = datetime.now(
            timezone.utc
        ).isoformat()
        observability["trace_metadata"][self.name]["attempts"] = (
            invocation_result.attempts
        )
        observability["trace_metadata"][self.name]["total_wait_seconds"] = (
            invocation_result.total_wait_seconds
        )

        if invocation_result.success:
            response = invocation_result.response
            usage = getattr(response, "usage_metadata", {}) or {}
            observability["token_usage"] = {
                self.name: {
                    "input_tokens": usage.get("input_tokens"),
                    "output_tokens": usage.get("output_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                }
            }
            observability["cost_usage"] = {self.name: usage.get("total_cost")}

            try:
                text_content = extract_text_content(response.content)
                result = self.parser.parse(text_content)
            except Exception as parse_error:
                logger.error(f"{self.name} failed to parse response: {parse_error!s}")
                if evaluation_id:
                    event_channel.emit_sync(
                        evaluation_id,
                        create_sommelier_event(
                            evaluation_id=evaluation_id,
                            sommelier=self.name,
                            event_type="sommelier_error",
                            progress_percent=progress_config["start"],
                            message=f"{self.name} analysis failed (parse error)",
                        ),
                    )
                return {
                    "errors": [f"{self.name} parse error: {parse_error!s}"],
                    f"{self.name}_result": None,
                    **observability,
                }

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

        error_category = invocation_result.error_category
        error_msg = (
            f"{self.name} evaluation failed after {invocation_result.attempts} attempts"
        )
        if error_category:
            error_msg += f" ({error_category.value})"
        if invocation_result.final_error:
            error_msg += f": {invocation_result.final_error!s}"

        logger.error(error_msg)

        if evaluation_id:
            event_channel.emit_sync(
                evaluation_id,
                create_sommelier_event(
                    evaluation_id=evaluation_id,
                    sommelier=self.name,
                    event_type="sommelier_error",
                    progress_percent=progress_config["start"],
                    message=f"{self.name} analysis failed",
                ),
            )

        return {
            "errors": [error_msg],
            f"{self.name}_result": None,
            **observability,
        }
