from unittest.mock import patch

import pytest
from langchain_google_genai import ChatGoogleGenerativeAI

from app.providers.llm import (
    build_llm,
    resolve_byok,
    BYOKValidationError,
    PROVIDER_DEFAULTS,
    _resolve_thinking_level,
)


class TestResolveBYOK:
    def test_resolve_byok_none_returns_none(self):
        key, error = resolve_byok(None)
        assert key is None
        assert error is None

    def test_resolve_byok_valid_key_returns_key(self):
        key, error = resolve_byok("sk-valid-key-123")
        assert key == "sk-valid-key-123"
        assert error is None

    def test_resolve_byok_empty_key_returns_structured_error(self):
        key, error = resolve_byok("   ", provider="openai")
        assert key is None
        assert isinstance(error, BYOKValidationError)
        assert error.error_code == "invalid_api_key"
        assert error.provider == "openai"
        assert "empty" in error.message.lower() or "whitespace" in error.message.lower()

    def test_resolve_byok_error_to_dict(self):
        _, error = resolve_byok("", provider="gemini")
        error_dict = error.to_dict()
        assert error_dict["error_code"] == "invalid_api_key"
        assert error_dict["provider"] == "gemini"
        assert "message" in error_dict


class TestProviderSelection:
    def test_build_llm_gemini_routing(self):
        llm = build_llm("gemini", "test-key", None, 0.1, 128)
        assert isinstance(llm, ChatGoogleGenerativeAI)

    @patch("app.providers.llm.ChatGoogleGenerativeAI")
    @patch("app.providers.llm.settings")
    def test_build_llm_vertex_routing(self, mock_settings, mock_vertex):
        mock_settings.VERTEX_API_KEY = "AQ.test-vertex-key"
        build_llm("vertex", None, None, 0.1, 128)
        mock_vertex.assert_called_once()
        call_kwargs = mock_vertex.call_args.kwargs
        assert call_kwargs["api_key"] == "AQ.test-vertex-key"
        assert call_kwargs["vertexai"] is True
        assert call_kwargs["thinking_level"] == "minimal"

    def test_build_llm_vertex_missing_key_raises(self):
        with patch("app.providers.llm.settings") as mock_settings:
            mock_settings.VERTEX_API_KEY = ""
            with pytest.raises(ValueError, match="VERTEX_API_KEY"):
                build_llm("vertex", None, None, 0.1, 128)

    def test_build_llm_unsupported_provider_raises(self):
        with pytest.raises(ValueError, match="Unsupported provider"):
            build_llm("openai", "test-key", None, 0.1, 128)

    def test_build_llm_default_is_gemini(self):
        llm = build_llm(None, "test-key", None, 0.1, 128)
        assert isinstance(llm, ChatGoogleGenerativeAI)

    def test_build_llm_case_insensitive(self):
        llm = build_llm("GEMINI", "test-key", None, 0.1, 128)
        assert isinstance(llm, ChatGoogleGenerativeAI)


class TestPerNodeModelConfig:
    def test_custom_model_passed_to_gemini(self):
        llm = build_llm("gemini", "test-key", "gemini-2.5-flash", 0.5, 1024)
        assert isinstance(llm, ChatGoogleGenerativeAI)

    def test_default_model_when_none(self):
        llm = build_llm("gemini", "test-key", None, 0.3, 128)
        assert llm.model == PROVIDER_DEFAULTS["gemini"]


class TestThinkingLevel:
    def test_flash_model_gets_minimal(self):
        assert _resolve_thinking_level("gemini-3-flash-preview") == "minimal"

    def test_pro_model_gets_low(self):
        assert _resolve_thinking_level("gemini-3-pro-preview") == "low"

    def test_non_gemini3_returns_none(self):
        assert _resolve_thinking_level("gemini-2.5-flash") is None

    def test_non_gemini_returns_none(self):
        assert _resolve_thinking_level("gpt-4o-mini") is None


class TestBYOKFallback:
    @patch("app.providers.llm.ChatGoogleGenerativeAI")
    def test_invalid_byok_uses_server_key(self, mock_chat_google):
        with patch("app.providers.llm.settings") as mock_settings:
            mock_settings.GEMINI_API_KEY = "server-side-key"
            build_llm("gemini", "   ", None, 0.3, 128)
            mock_chat_google.assert_called_once()
            assert (
                mock_chat_google.call_args.kwargs["google_api_key"] == "server-side-key"
            )

    def test_model_fallback_enabled(self):
        llm = build_llm(
            "gemini", "test-key", "gemini-2.5-flash", 0.3, 128, enable_fallback=True
        )
        assert hasattr(llm, "fallbacks")

    def test_model_fallback_not_added_for_default_model(self):
        llm = build_llm("gemini", "test-key", None, 0.3, 128, enable_fallback=True)
        assert not hasattr(llm, "fallbacks")
