from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.providers.llm import build_llm, resolve_byok


def test_resolve_byok_invalid_key():
    key, error = resolve_byok("   ")
    assert key is None
    assert error == "invalid_api_key"


def test_build_llm_gemini():
    llm = build_llm("gemini", "test", None, 0.1, 128)
    assert isinstance(llm, ChatGoogleGenerativeAI)


def test_build_llm_openai():
    llm = build_llm("openai", "test", "gpt-4o-mini", 0.1, 128)
    assert isinstance(llm, ChatOpenAI)


def test_build_llm_anthropic():
    llm = build_llm("anthropic", "test", "claude-3-5-sonnet-20241022", 0.1, 128)
    assert isinstance(llm, ChatAnthropic)
