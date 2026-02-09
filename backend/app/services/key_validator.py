import logging
from dataclasses import dataclass, field
from typing import List, Optional

import httpx

logger = logging.getLogger(__name__)

GOOGLE_MODELS_URL = "https://generativelanguage.googleapis.com/v1/models"
VERTEX_TEST_URL = "https://aiplatform.googleapis.com/v1/projects/vertex-ai-express/locations/us-central1/publishers/google/models"
VALIDATION_TIMEOUT = 10.0


@dataclass
class ValidationResult:
    valid: bool
    error: Optional[str] = None
    models_available: List[str] = field(default_factory=list)


async def validate_google_key(api_key: str) -> ValidationResult:
    try:
        async with httpx.AsyncClient(timeout=VALIDATION_TIMEOUT) as client:
            response = await client.get(
                GOOGLE_MODELS_URL, headers={"x-goog-api-key": api_key}
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
        return ValidationResult(valid=False, error="Network error during validation")


async def validate_vertex_key(api_key: str) -> ValidationResult:
    try:
        async with httpx.AsyncClient(timeout=VALIDATION_TIMEOUT) as client:
            response = await client.get(
                VERTEX_TEST_URL, headers={"x-goog-api-key": api_key}
            )
            if response.status_code == 200:
                return ValidationResult(valid=True, models_available=["vertex-ai"])
            if response.status_code in (401, 403):
                return ValidationResult(valid=False, error="Invalid Vertex AI API key")
            return ValidationResult(
                valid=False, error=f"Unexpected status: {response.status_code}"
            )
    except httpx.TimeoutException:
        return ValidationResult(valid=False, error="Validation timed out")
    except httpx.HTTPError:
        return ValidationResult(valid=False, error="Network error during validation")


async def validate_api_key(api_key: str, provider: str) -> ValidationResult:
    if provider == "google":
        return await validate_google_key(api_key)
    elif provider == "vertex":
        return await validate_vertex_key(api_key)
    else:
        return ValidationResult(valid=False, error=f"Unknown provider: {provider}")
