import asyncio
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock
from langchain_core.messages import AIMessage

MOCK_SOMMELIER_OUTPUT = {
    "sommelier_name": "mock_sommelier",
    "score": 85,
    "confidence": 0.9,
    "notes": "A well-structured repository with clear organization.",
    "summary": "Good overall quality.",
    "recommendations": ["Add more tests", "Improve documentation"],
    "aspects": {
        "code_quality": 85,
        "documentation": 80,
        "testing": 75,
    },
    "techniques_used": ["static_analysis", "metric_extraction"],
}


def create_mock_sommelier_response(
    sommelier_name: str = "mock",
    score: int = 85,
    confidence: float = 0.9,
) -> str:
    import json

    output = {
        "sommelier_name": sommelier_name,
        "score": score,
        "confidence": confidence,
        "notes": f"Evaluation by {sommelier_name}",
        "summary": "Test evaluation",
        "recommendations": [],
        "aspects": {},
        "techniques_used": [],
    }
    return json.dumps(output)


class MockLLM:
    def __init__(
        self,
        response: Optional[str] = None,
        sommelier_name: str = "mock",
        delay: float = 0.0,
    ):
        self.response = response or create_mock_sommelier_response(sommelier_name)
        self.delay = delay
        self.call_count = 0
        self.last_messages: List[Any] = []

    async def ainvoke(
        self, messages: List[Any], config: Optional[Dict] = None
    ) -> AIMessage:
        self.call_count += 1
        self.last_messages = messages

        if self.delay > 0:
            await asyncio.sleep(self.delay)

        return AIMessage(
            content=self.response,
            usage_metadata={
                "input_tokens": 100,
                "output_tokens": 50,
                "total_tokens": 150,
            },
        )

    def invoke(self, messages: List[Any], config: Optional[Dict] = None) -> AIMessage:
        self.call_count += 1
        self.last_messages = messages
        return AIMessage(
            content=self.response,
            usage_metadata={
                "input_tokens": 100,
                "output_tokens": 50,
                "total_tokens": 150,
            },
        )


class MockLLMWithError(MockLLM):
    def __init__(
        self, error_message: str = "LLM API error", error_type: type = Exception
    ):
        super().__init__()
        self.error_message = error_message
        self.error_type = error_type

    async def ainvoke(
        self, messages: List[Any], config: Optional[Dict] = None
    ) -> AIMessage:
        self.call_count += 1
        self.last_messages = messages
        raise self.error_type(self.error_message)

    def invoke(self, messages: List[Any], config: Optional[Dict] = None) -> AIMessage:
        self.call_count += 1
        self.last_messages = messages
        raise self.error_type(self.error_message)


class MockLLMWithTimeout(MockLLM):
    def __init__(self, timeout_seconds: float = 30.0):
        super().__init__()
        self.timeout_seconds = timeout_seconds

    async def ainvoke(
        self, messages: List[Any], config: Optional[Dict] = None
    ) -> AIMessage:
        self.call_count += 1
        self.last_messages = messages
        await asyncio.sleep(self.timeout_seconds)
        raise asyncio.TimeoutError(f"LLM call timed out after {self.timeout_seconds}s")


def create_mock_checkpointer():
    from langgraph.checkpoint.base import BaseCheckpointSaver

    mock = MagicMock(spec=BaseCheckpointSaver)
    return mock
