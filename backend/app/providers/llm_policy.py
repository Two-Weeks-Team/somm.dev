"""Rate-limiting policy and concurrency control for LLM invocations."""

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from langchain_core.language_models.chat_models import BaseChatModel

from app.providers.llm_errors import classify_error, ErrorCategory

logger = logging.getLogger(__name__)

T = TypeVar("T")

LLM_INVOKE_TIMEOUT_SECONDS = 90.0


@dataclass
class RetryConfig:
    """Configuration for retry behavior with jittered exponential backoff."""

    max_attempts: int = 3
    base_delay: float = 5.0
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


class RpmLimiter:
    """Simple in-process RPM limiter to prevent burst requests."""

    def __init__(self, rpm: int):
        if rpm <= 0:
            raise ValueError(f"RPM must be positive, got {rpm}")
        self._min_interval = 60.0 / rpm
        self._lock = asyncio.Lock()
        self._next_ts = 0.0

    async def wait(self) -> None:
        async with self._lock:
            now = time.monotonic()
            if now < self._next_ts:
                delay = self._next_ts - now
                logger.debug(f"RPM limiter: waiting {delay:.2f}s")
                await asyncio.sleep(delay)
            self._next_ts = max(time.monotonic(), self._next_ts) + self._min_interval


_provider_semaphores: dict[str, asyncio.Semaphore] = {}
_provider_rpm_limiters: dict[str, RpmLimiter] = {}
_semaphore_lock = asyncio.Lock()

PROVIDER_CONCURRENCY_LIMITS = {
    "google": 3,
    "vertex": 3,
}

PROVIDER_RPM_LIMITS = {
    "google": 10,
    "vertex": 10,
}


async def _get_provider_semaphore(provider: str) -> asyncio.Semaphore:
    async with _semaphore_lock:
        if provider not in _provider_semaphores:
            limit = PROVIDER_CONCURRENCY_LIMITS.get(provider, 3)
            _provider_semaphores[provider] = asyncio.Semaphore(limit)
        return _provider_semaphores[provider]


async def _get_provider_rpm_limiter(provider: str) -> RpmLimiter:
    async with _semaphore_lock:
        if provider not in _provider_rpm_limiters:
            rpm = PROVIDER_RPM_LIMITS.get(provider, 10)
            _provider_rpm_limiters[provider] = RpmLimiter(rpm)
        return _provider_rpm_limiters[provider]


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
        provider: Provider name (gemini, vertex)
        config: Retry configuration (defaults to RetryConfig())
        langchain_config: Optional config to pass to llm.ainvoke()
        on_retry: Optional callback(attempt, delay, message) for logging

    Returns:
        InvocationResult with success/failure status and details
    """
    config = config or RetryConfig()
    semaphore = await _get_provider_semaphore(provider)
    rpm_limiter = await _get_provider_rpm_limiter(provider)

    attempts = 0
    total_wait = 0.0
    last_error = None
    last_category = None

    while attempts < config.max_attempts:
        attempts += 1

        await rpm_limiter.wait()

        async with semaphore:
            try:
                response = await asyncio.wait_for(
                    llm.ainvoke(messages, config=langchain_config),
                    timeout=LLM_INVOKE_TIMEOUT_SECONDS,
                )
                return InvocationResult(
                    success=True,
                    response=response,
                    attempts=attempts,
                    total_wait_seconds=total_wait,
                )
            except asyncio.TimeoutError:
                last_error = TimeoutError(
                    f"LLM call timed out after {LLM_INVOKE_TIMEOUT_SECONDS}s"
                )
                last_category = ErrorCategory.TRANSIENT
                msg = (
                    f"Attempt {attempts}/{config.max_attempts} "
                    f"timed out after {LLM_INVOKE_TIMEOUT_SECONDS}s"
                )
                logger.warning(msg)
                if attempts >= config.max_attempts:
                    break
                delay = _calculate_delay_with_jitter(attempts - 1, config)
                if on_retry:
                    on_retry(attempts, delay, msg)
                await asyncio.sleep(delay)
                total_wait += delay
                continue
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
    global _provider_semaphores, _provider_rpm_limiters
    _provider_semaphores = {}
    _provider_rpm_limiters = {}
