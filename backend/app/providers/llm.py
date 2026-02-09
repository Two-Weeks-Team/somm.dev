from dataclasses import dataclass
from typing import Optional

from google import genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import settings


DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_OUTPUT_TOKENS = 2048
DEFAULT_REQUEST_TIMEOUT = 60

GEMINI3_THINKING_LEVELS = {
    "flash": "minimal",
    "pro": "low",
}


@dataclass
class BYOKValidationError:
    """Structured error for BYOK (Bring Your Own Key) validation failures."""

    error_code: str
    message: str
    provider: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "error_code": self.error_code,
            "message": self.message,
            "provider": self.provider,
        }


def resolve_byok(
    api_key: Optional[str], provider: Optional[str] = None
) -> tuple[Optional[str], Optional[BYOKValidationError]]:
    """Validate and resolve a BYOK API key.

    Args:
        api_key: User-provided API key (None means use server-side key)
        provider: Provider name for error context

    Returns:
        Tuple of (resolved_key, error). If error is not None, resolved_key is None
        and the caller should fall back to server-side key.
    """
    if api_key is None:
        return None, None
    if not api_key.strip():
        return None, BYOKValidationError(
            error_code="invalid_api_key",
            message="API key is empty or contains only whitespace",
            provider=provider,
        )
    return api_key, None


def _resolve_thinking_level(model_name: str) -> Optional[str]:
    """Flash→minimal, Pro→low. Pro doesn't support minimal/medium."""
    name = model_name.lower()
    if "gemini-3" not in name:
        return None
    if "-pro" in name:
        return GEMINI3_THINKING_LEVELS["pro"]
    return GEMINI3_THINKING_LEVELS["flash"]


PROVIDER_DEFAULTS = {
    "google": "gemini-3-flash-preview",
    "vertex": "gemini-3-flash-preview",
}


def build_llm(
    provider: str,
    api_key: Optional[str],
    model: Optional[str],
    temperature: Optional[float],
    max_output_tokens: Optional[int],
    enable_fallback: bool = False,
) -> BaseChatModel:
    provider_key = (provider or "vertex").lower()
    resolved_key, byok_error = resolve_byok(api_key, provider_key)

    if byok_error:
        resolved_key = None

    resolved_temperature = (
        temperature if temperature is not None else DEFAULT_TEMPERATURE
    )
    resolved_max_tokens = max_output_tokens or DEFAULT_MAX_OUTPUT_TOKENS

    if provider_key not in ("google", "vertex"):
        raise ValueError(
            f"Unsupported provider: {provider_key}. Use 'vertex' or 'google'."
        )

    resolved_model = model or PROVIDER_DEFAULTS[provider_key]

    if resolved_key:
        use_vertex = provider_key == "vertex"
        final_key = resolved_key
    else:
        if not settings.VERTEX_API_KEY:
            raise ValueError("VERTEX_API_KEY is required")
        use_vertex = True
        final_key = settings.VERTEX_API_KEY

    llm_kwargs: dict = {
        "model": resolved_model,
        "temperature": resolved_temperature,
        "max_output_tokens": resolved_max_tokens,
        "timeout": DEFAULT_REQUEST_TIMEOUT,
    }

    if use_vertex:
        # Use pre-configured genai.Client for Vertex AI Express mode
        # This bypasses LangChain's ADC requirement when vertexai=True
        vertex_client = genai.Client(vertexai=True, api_key=final_key)
        llm_kwargs["client"] = vertex_client
    else:
        llm_kwargs["google_api_key"] = final_key

    thinking_level = _resolve_thinking_level(resolved_model)
    if thinking_level:
        llm_kwargs["thinking_level"] = thinking_level

    llm = ChatGoogleGenerativeAI(**llm_kwargs)

    if enable_fallback and model and model != PROVIDER_DEFAULTS.get(provider_key):
        fallback_llm = build_llm(
            provider=provider_key,
            api_key=api_key,
            model=None,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            enable_fallback=False,
        )
        return llm.with_fallbacks([fallback_llm])

    return llm


def extract_text_content(content) -> str:
    """Extract text from LLM response content.

    Gemini 3 with thinking mode returns content as a list of blocks:
      [{'type': 'text', 'text': '...', 'extras': {'signature': '...'}}]
    Other providers return plain strings.
    """
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif isinstance(block, str):
                parts.append(block)
        return "\n".join(parts) if parts else str(content)
    return str(content)
