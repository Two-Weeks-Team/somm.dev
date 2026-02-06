from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

from app.core.config import settings


def resolve_byok(api_key: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    if api_key is None:
        return None, None
    if not api_key.strip():
        return None, "invalid_api_key"
    return api_key, None


def build_llm(
    provider: str,
    api_key: Optional[str],
    model: Optional[str],
    temperature: Optional[float],
    max_output_tokens: Optional[int],
):
    provider_key = (provider or "gemini").lower()
    resolved_key, _ = resolve_byok(api_key)

    if provider_key == "gemini":
        return ChatGoogleGenerativeAI(
            model=model or "gemini-1.5-flash",
            temperature=temperature if temperature is not None else 0.3,
            max_output_tokens=max_output_tokens or 2048,
            google_api_key=resolved_key or settings.GEMINI_API_KEY,
            convert_system_message_to_human=True,
        )

    if provider_key == "openai":
        return ChatOpenAI(
            model=model or "gpt-4o-mini",
            temperature=temperature if temperature is not None else 0.3,
            api_key=resolved_key or settings.OPENAI_API_KEY,
        )

    if provider_key == "anthropic":
        return ChatAnthropic(
            model=model or "claude-3-5-sonnet-20241022",
            temperature=temperature if temperature is not None else 0.3,
            api_key=resolved_key or settings.ANTHROPIC_API_KEY,
        )

    raise ValueError(f"Unsupported provider: {provider_key}")
