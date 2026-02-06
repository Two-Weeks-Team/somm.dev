"""Rate-limiting policy and concurrency control for LLM invocations."""

import asyncio
import logging
import random
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

from langchain_core.language_models.chat_models import BaseChatModel

from app.providers.llm_errors import classify_error, ErrorCategory

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior with jittered exponential backoff."""

    max_attempts: int = 3
    base_delay: float = 2.0
    max_delay: float = 60.0
    jitter_factor: float = 0.5


@dataclass
class InvocationResult:
    """Result of an LLM invocation with policy applied."""

    success: bool
    response: Any = None
    attempts: int = 0
    total_wait_seconds: float = 0.0
    final_error: Exception | None = None
    error_category: ErrorCategory | None = None


_provider_semaphores: dict[str, asyncio.Semaphore] = {}
_semaphore_lock = asyncio.Lock()

PROVIDER_CONCURRENCY_LIMITS = {
    "gemini": 5,
    "openai": 10,
    "anthropic": 5,
}


async def _get_provider_semaphore(provider: str) -> asyncio.Semaphore:
    """Get or create a semaphore for the given provider."""
    async with _semaphore_lock:
        if provider not in _provider_semaphores:
            limit = PROVIDER_CONCURRENCY_LIMITS.get(provider, 5)
            _provider_semaphores[provider] = asyncio.Semaphore(limit)
            logger.debug(f"Created semaphore for {provider} with limit {limit}")
        return _provider_semaphores[provider]


def _calculate_delay_with_jitter(
    attempt: int,
    config: RetryConfig,
    suggested_delay: float | None = None,
) -> float:
    """Calculate backoff delay with jitter to prevent thundering herd."""
    if suggested_delay is not None:
        base = suggested_delay
    else:
        base = config.base_delay * (2**attempt)

    base = min(base, config.max_delay)
    jitter = base * config.jitter_factor * random.random()
    return base + jitter


async def invoke_with_policy(
    llm: BaseChatModel,
    messages: list,
    provider: str,
    config: RetryConfig | None = None,
    langchain_config: dict | None = None,
    on_retry: Callable[[int, float, str], None] | None = None,
) -> InvocationResult:
    """Invoke LLM with rate-limiting, concurrency control, and smart retry.

    Applies:
    - Provider-scoped semaphore to limit concurrent requests
    - Error classification to determine retry strategy
    - Jittered exponential backoff for rate limits

    Args:
        llm: The LangChain LLM instance
        messages: Messages to send to the LLM
        provider: Provider name (gemini, openai, anthropic)
        config: Retry configuration (defaults to RetryConfig())
        langchain_config: Optional config to pass to llm.ainvoke()
        on_retry: Optional callback(attempt, delay, message) for logging

    Returns:
        InvocationResult with success/failure status and details
    """
    config = config or RetryConfig()
    semaphore = await _get_provider_semaphore(provider)

    attempts = 0
    total_wait = 0.0
    last_error = None
    last_category = None

    while attempts < config.max_attempts:
        attempts += 1

        async with semaphore:
            try:
                response = await llm.ainvoke(messages, config=langchain_config)
                return InvocationResult(
                    success=True,
                    response=response,
                    attempts=attempts,
                    total_wait_seconds=total_wait,
                )
            except Exception as e:
                classified = classify_error(e)
                last_error = e
                last_category = classified.category

                if not classified.should_retry:
                    logger.warning(
                        f"Non-retryable error ({classified.category.value}): "
                        f"{classified.message}"
                    )
                    return InvocationResult(
                        success=False,
                        attempts=attempts,
                        total_wait_seconds=total_wait,
                        final_error=e,
                        error_category=classified.category,
                    )

                if attempts >= config.max_attempts:
                    break

                delay = _calculate_delay_with_jitter(
                    attempt=attempts - 1,
                    config=config,
                    suggested_delay=classified.retry_after_seconds,
                )

                msg = (
                    f"Attempt {attempts}/{config.max_attempts} failed "
                    f"({classified.category.value}). Retrying in {delay:.1f}s..."
                )
                logger.info(msg)

                if on_retry:
                    on_retry(attempts, delay, msg)

                await asyncio.sleep(delay)
                total_wait += delay

    logger.error(
        f"All {config.max_attempts} attempts failed. "
        f"Last error: {last_category.value if last_category else 'unknown'}"
    )

    return InvocationResult(
        success=False,
        attempts=attempts,
        total_wait_seconds=total_wait,
        final_error=last_error,
        error_category=last_category,
    )


def reset_semaphores() -> None:
    """Reset all provider semaphores. Used for testing."""
    global _provider_semaphores
    _provider_semaphores = {}
