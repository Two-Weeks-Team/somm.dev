"""Base class for all sommelier nodes."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional
from langchain_core.runnables import RunnableConfig
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from app.graph.state import EvaluationState
from app.graph.schemas import SommelierOutput


class BaseSommelierNode(ABC):
    """Abstract base class for all sommelier evaluation nodes.

    Provides common LLM configuration, output parsing, and evaluation logic
    that can be inherited by specific sommelier implementations.
    """

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            max_output_tokens=2048,
            google_api_key=settings.GEMINI_API_KEY,
            convert_system_message_to_human=True,
        )
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
        started_at = datetime.utcnow().isoformat()
        model_name = getattr(self.llm, "model", "gemini-1.5-flash")
        observability = {
            "completed_sommeliers": [self.name],
            "token_usage": {
                self.name: {
                    "input_tokens": None,
                    "output_tokens": None,
                    "total_tokens": None,
                }
            },
            "cost_usage": {self.name: None},
            "trace_metadata": {
                self.name: {
                    "started_at": started_at,
                    "completed_at": datetime.utcnow().isoformat(),
                    "model": model_name,
                    "provider": "gemini",
                }
            },
        }
        try:
            prompt = self.get_prompt(state["evaluation_criteria"])
            chain = prompt | self.llm | self.parser
            result = await chain.ainvoke(
                {
                    "repo_context": state["repo_context"],
                    "criteria": state["evaluation_criteria"],
                    "format_instructions": self.parser.get_format_instructions(),
                },
                config=config,
            )
            return {
                f"{self.name}_result": result.dict(),
                **observability,
            }
        except Exception as e:
            observability["token_usage"] = {self.name: {}}
            return {
                "errors": [f"{self.name} evaluation failed: {str(e)}"],
                f"{self.name}_result": None,
                **observability,
            }
