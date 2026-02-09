"""API key validation service for external providers.

This module provides validation services for API keys from various providers
like Google Gemini, OpenAI, etc.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional

import httpx

logger = logging.getLogger(__name__)

GEMINI_MODELS_URL = "https://generativelanguage.googleapis.com/v1/models"
VALIDATION_TIMEOUT = 10.0


@dataclass
class ValidationResult:
    """Result of an API key validation attempt.

    Attributes:
        valid: Whether the key is valid.
        error: Error message if validation failed.
        models_available: List of available models if validation succeeded.
    """

    valid: bool
    error: Optional[str] = None
    models_available: List[str] = field(default_factory=list)


async def validate_gemini_key(api_key: str) -> ValidationResult:
    """Validate a Google Gemini API key.

    Makes a request to the Gemini API to verify the key is valid and
    retrieves the list of available models.

    Args:
        api_key: The Gemini API key to validate.

    Returns:
        ValidationResult containing validation status and available models.
    """
    try:
        async with httpx.AsyncClient(timeout=VALIDATION_TIMEOUT) as client:
            response = await client.get(
                GEMINI_MODELS_URL, headers={"x-goog-api-key": api_key}
            )
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                return ValidationResult(valid=True, models_available=models)
            if response.status_code in (401, 403):
                return ValidationResult(valid=False, error="Invalid API key")
            return ValidationResult(
                valid=False, error=f"Unexpected status: {response.status_code}"
            )
    except httpx.TimeoutException:
        return ValidationResult(valid=False, error="Validation timed out")
    except httpx.HTTPError:
        return ValidationResult(
            valid=False, error="Network error occurred during validation"
        )
