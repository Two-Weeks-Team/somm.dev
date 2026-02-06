import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from langchain_core.runnables import RunnableConfig
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from app.graph.state import EvaluationState
from app.graph.schemas import TastingNoteOutput, TechniqueResult
from app.providers.llm import build_llm, extract_text_content
from app.providers.llm_policy import invoke_with_policy, RetryConfig
from app.services.llm_context import render_repo_context, get_context_budget
from app.techniques.mappings import (
    TastingNote,
    get_techniques_for_category,
    get_technique_priority,
    Priority,
)
from app.techniques.schema import TechniqueDefinition

logger = logging.getLogger(__name__)

TASTING_NOTE_PROGRESS = {
    "aroma": {"start": 10, "complete": 20},
    "palate": {"start": 20, "complete": 30},
    "body": {"start": 30, "complete": 40},
    "finish": {"start": 40, "complete": 50},
    "balance": {"start": 50, "complete": 60},
    "vintage": {"start": 60, "complete": 70},
    "terroir": {"start": 70, "complete": 80},
    "cellar": {"start": 80, "complete": 90},
}


class BaseTastingNoteNode(ABC):
    def __init__(self):
        self.parser = PydanticOutputParser(pydantic_object=TastingNoteOutput)

    @property
    @abstractmethod
    def category(self) -> TastingNote:
        pass

    @property
    @abstractmethod
    def axis(self) -> str:
        pass

    def get_techniques(self) -> List[TechniqueDefinition]:
        return get_techniques_for_category(self.category)

    def get_p0_techniques(self) -> List[TechniqueDefinition]:
        return [
            t
            for t in self.get_techniques()
            if get_technique_priority(t.id) == Priority.P0
        ]

    def build_evaluation_prompt(
        self, techniques: List[TechniqueDefinition]
    ) -> ChatPromptTemplate:
        technique_prompts = "\n\n".join(
            [f"### {t.name} ({t.id})\n{t.prompt_template}" for t in techniques]
        )

        system = f"""You are an expert evaluator using the {self.axis} lens.
Your role is to apply multiple evaluation techniques systematically.

For each technique, provide:
1. A score (1-5)
2. Key findings
3. Reasoning

{self.parser.get_format_instructions()}"""

        human = f"""## Evaluation Context
{{repo_context}}

## Techniques to Apply
{technique_prompts}

## Instructions
Apply each technique above to evaluate this repository.
Provide structured output with technique results and an aggregate summary."""

        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=system),
                HumanMessagePromptTemplate.from_template(human),
            ]
        )

    async def evaluate(
        self, state: EvaluationState, config: Optional[RunnableConfig] = None
    ) -> Dict[str, Any]:
        started_at = datetime.now(timezone.utc).isoformat()
        configurable = (config or {}).get("configurable", {})
        provider = configurable.get("provider", "gemini")
        api_key = configurable.get("api_key")
        model = configurable.get("model")
        temperature = configurable.get("temperature")

        llm = build_llm(
            provider=provider,
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_output_tokens=4096,
        )

        techniques = self.get_p0_techniques()
        if not techniques:
            techniques = self.get_techniques()[:3]

        context_budget = get_context_budget(provider, model)
        rendered_context, context_meta = render_repo_context(
            state["repo_context"], max_tokens=context_budget
        )

        observability = {
            "completed_sommeliers": [self.category.value],
            "token_usage": {self.category.value: {}},
            "cost_usage": {self.category.value: None},
            "trace_metadata": {
                self.category.value: {
                    "started_at": started_at,
                    "completed_at": None,
                    "model": model or "default",
                    "provider": provider,
                    "techniques_count": len(techniques),
                    "estimated_input_tokens": context_meta["estimated_tokens"],
                    "context_truncated": context_meta["truncated"],
                }
            },
        }

        prompt = self.build_evaluation_prompt(techniques)
        messages = prompt.format_messages(repo_context=rendered_context)

        def on_retry(attempt: int, delay: float, msg: str) -> None:
            logger.info(f"{self.category.value}: {msg}")

        invocation_result = await invoke_with_policy(
            llm=llm,
            messages=messages,
            provider=provider,
            config=RetryConfig(max_attempts=3, base_delay=2.0, max_delay=60.0),
            langchain_config=config,
            on_retry=on_retry,
        )

        observability["trace_metadata"][self.category.value]["completed_at"] = (
            datetime.now(timezone.utc).isoformat()
        )
        observability["trace_metadata"][self.category.value]["attempts"] = (
            invocation_result.attempts
        )
        observability["trace_metadata"][self.category.value]["total_wait_seconds"] = (
            invocation_result.total_wait_seconds
        )

        if invocation_result.success:
            response = invocation_result.response
            usage = getattr(response, "usage_metadata", {}) or {}
            observability["token_usage"] = {
                self.category.value: {
                    "input_tokens": usage.get("input_tokens"),
                    "output_tokens": usage.get("output_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                }
            }

            try:
                text_content = extract_text_content(response.content)
                result = self.parser.parse(text_content)
            except Exception as parse_error:
                logger.error(
                    f"{self.category.value} failed to parse response: {parse_error!s}"
                )
                return {
                    "errors": [f"{self.category.value} parse error: {parse_error!s}"],
                    f"{self.category.value}_result": None,
                    **observability,
                }

            return {
                f"{self.category.value}_result": result.model_dump(),
                **observability,
            }

        error_category = invocation_result.error_category
        error_msg = (
            f"{self.category.value} evaluation failed after "
            f"{invocation_result.attempts} attempts"
        )
        if error_category:
            error_msg += f" ({error_category.value})"
        if invocation_result.final_error:
            error_msg += f": {invocation_result.final_error!s}"

        logger.error(error_msg)

        return {
            "errors": [error_msg],
            f"{self.category.value}_result": None,
            **observability,
        }
