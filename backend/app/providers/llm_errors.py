"""LLM error classification and handling for rate limit detection."""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ErrorCategory(Enum):
    """Categories of LLM errors for retry policy decisions."""

    RATE_LIMITED = "rate_limited"  # 429, quota exceeded, RESOURCE_EXHAUSTED
    CONTEXT_OVERFLOW = "context_overflow"  # Input too long, context length exceeded
    AUTH_ERROR = "auth_error"  # Invalid API key, unauthorized
    MODEL_ERROR = "model_error"  # Invalid model, model not found
    TRANSIENT = "transient"  # Network issues, 5xx, timeout
    PERMANENT = "permanent"  # Content blocked, invalid request


@dataclass
class ClassifiedError:
    """Classified LLM error with retry guidance."""

    category: ErrorCategory
    retry_after_seconds: Optional[
        float
    ]  # Suggested wait time (from header or estimate)
    original_error: Exception
    message: str

    @property
    def should_retry(self) -> bool:
        """Whether this error category suggests retry is worthwhile."""
        return self.category in (ErrorCategory.RATE_LIMITED, ErrorCategory.TRANSIENT)

    @property
    def should_reduce_context(self) -> bool:
        """Whether this error suggests context reduction might help."""
        return self.category == ErrorCategory.CONTEXT_OVERFLOW


# Regex patterns for error message classification
RATE_LIMIT_PATTERNS = [
    r"rate.?limit",
    r"quota.?exceed",
    r"too.?many.?requests",
    r"resource.?exhausted",
    r"429",
    r"rate_limit_exceeded",
    r"requests.?per.?minute",
    r"tokens.?per.?minute",
    r"RPM.?limit",
    r"TPM.?limit",
]

CONTEXT_OVERFLOW_PATTERNS = [
    r"context.?length",
    r"maximum.?context",
    r"too.?long",
    r"token.?limit",
    r"max.?tokens",
    r"input.?too.?large",
    r"exceeds.?the.?limit",
    r"prompt.?too.?long",
]

AUTH_ERROR_PATTERNS = [
    r"invalid.?api.?key",
    r"unauthorized",
    r"authentication",
    r"403",
    r"401",
    r"permission.?denied",
]

MODEL_ERROR_PATTERNS = [
    r"model.?not.?found",
    r"invalid.?model",
    r"does.?not.?exist",
    r"unsupported.?model",
]


def _matches_patterns(text: str, patterns: list[str]) -> bool:
    """Check if text matches any of the given regex patterns."""
    text_lower = text.lower()
    return any(re.search(p, text_lower) for p in patterns)


def _extract_retry_after(error: Exception) -> Optional[float]:
    """Try to extract retry-after value from error or response headers."""
    # Check for Retry-After in error attributes
    if hasattr(error, "response") and error.response is not None:
        response = error.response
        if hasattr(response, "headers"):
            retry_after = response.headers.get("Retry-After") or response.headers.get(
                "retry-after"
            )
            if retry_after:
                try:
                    return float(retry_after)
                except (ValueError, TypeError):
                    pass

    # Check for retry_after in error body/message
    error_str = str(error).lower()
    # Look for patterns like "retry after 30 seconds" or "try again in 60s"
    match = re.search(r"(?:retry|wait|try).+?(\d+)\s*(?:s|sec|second)", error_str)
    if match:
        return float(match.group(1))

    return None


def _get_http_status(error: Exception) -> Optional[int]:
    """Extract HTTP status code from error if available."""
    # Check common attribute names for status code
    for attr in ("status_code", "status", "code", "http_status"):
        if hasattr(error, attr):
            val = getattr(error, attr)
            if isinstance(val, int):
                return val

    # Check nested response object
    if (
        hasattr(error, "response")
        and error.response is not None
        and hasattr(error.response, "status_code")
    ):
        return error.response.status_code

    return None


def classify_error(error: Exception) -> ClassifiedError:
    """Classify an LLM error to determine retry strategy.

    Args:
        error: The exception raised during LLM invocation

    Returns:
        ClassifiedError with category and retry guidance
    """
    error_str = str(error)
    status_code = _get_http_status(error)
    retry_after = _extract_retry_after(error)

    # Check HTTP status codes first
    if status_code == 429:
        return ClassifiedError(
            category=ErrorCategory.RATE_LIMITED,
            retry_after_seconds=retry_after or 30.0,  # Default to 30s if no header
            original_error=error,
            message=f"Rate limited (HTTP 429): {error_str[:200]}",
        )

    if status_code in (401, 403):
        return ClassifiedError(
            category=ErrorCategory.AUTH_ERROR,
            retry_after_seconds=None,
            original_error=error,
            message=f"Authentication error (HTTP {status_code}): {error_str[:200]}",
        )

    if status_code and 500 <= status_code < 600:
        return ClassifiedError(
            category=ErrorCategory.TRANSIENT,
            retry_after_seconds=retry_after or 5.0,
            original_error=error,
            message=f"Server error (HTTP {status_code}): {error_str[:200]}",
        )

    # Check error message patterns
    if _matches_patterns(error_str, RATE_LIMIT_PATTERNS):
        return ClassifiedError(
            category=ErrorCategory.RATE_LIMITED,
            retry_after_seconds=retry_after or 30.0,
            original_error=error,
            message=f"Rate limited: {error_str[:200]}",
        )

    if _matches_patterns(error_str, CONTEXT_OVERFLOW_PATTERNS):
        return ClassifiedError(
            category=ErrorCategory.CONTEXT_OVERFLOW,
            retry_after_seconds=None,
            original_error=error,
            message=f"Context overflow: {error_str[:200]}",
        )

    if _matches_patterns(error_str, AUTH_ERROR_PATTERNS):
        return ClassifiedError(
            category=ErrorCategory.AUTH_ERROR,
            retry_after_seconds=None,
            original_error=error,
            message=f"Authentication error: {error_str[:200]}",
        )

    if _matches_patterns(error_str, MODEL_ERROR_PATTERNS):
        return ClassifiedError(
            category=ErrorCategory.MODEL_ERROR,
            retry_after_seconds=None,
            original_error=error,
            message=f"Model error: {error_str[:200]}",
        )

    # Check for common transient error types
    error_type = type(error).__name__.lower()
    transient_types = ("timeout", "connection", "network", "temporary", "unavailable")
    if any(t in error_type for t in transient_types):
        return ClassifiedError(
            category=ErrorCategory.TRANSIENT,
            retry_after_seconds=retry_after or 5.0,
            original_error=error,
            message=f"Transient error: {error_str[:200]}",
        )

    # Default to permanent (don't waste retries on unknown errors)
    return ClassifiedError(
        category=ErrorCategory.PERMANENT,
        retry_after_seconds=None,
        original_error=error,
        message=f"Unknown error: {error_str[:200]}",
    )
