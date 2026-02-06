import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from tests.mocks.providers import (
    MockLLM,
    MockLLMWithError,
    MockLLMWithTimeout,
    create_mock_sommelier_response,
)


class TestLLMErrorHandling:
    @pytest.mark.asyncio
    async def test_sommelier_node_handles_llm_error_gracefully(self):
        from app.graph.nodes.marcel import MarcelNode

        node = MarcelNode()
        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {"readme": "Test README"},
            "evaluation_criteria": "basic",
            "user_id": "user1",
        }

        mock_llm = MockLLMWithError(error_message="API rate limit exceeded")

        with patch("app.graph.nodes.base.build_llm", return_value=mock_llm):
            result = await node.evaluate(state)

            assert "errors" in result
            assert any("marcel evaluation failed" in err for err in result["errors"])
            assert result["marcel_result"] is None
            assert "completed_sommeliers" in result
            assert "marcel" in result["completed_sommeliers"]

    @pytest.mark.asyncio
    async def test_sommelier_node_handles_parse_error_gracefully(self):
        from app.graph.nodes.marcel import MarcelNode

        node = MarcelNode()
        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {"readme": "Test README"},
            "evaluation_criteria": "basic",
            "user_id": "user1",
        }

        mock_llm = MockLLM(response="invalid json response")

        with patch("app.graph.nodes.base.build_llm", return_value=mock_llm):
            result = await node.evaluate(state)

            assert "errors" in result
            assert result["marcel_result"] is None


class TestMissingInputHandling:
    @pytest.mark.asyncio
    async def test_sommelier_handles_empty_repo_context(self):
        from app.graph.nodes.marcel import MarcelNode

        node = MarcelNode()
        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user1",
        }

        mock_llm = MockLLM(sommelier_name="marcel")

        with patch("app.graph.nodes.base.build_llm", return_value=mock_llm):
            result = await node.evaluate(state)

            assert "completed_sommeliers" in result

    @pytest.mark.asyncio
    async def test_rag_enrich_handles_empty_context(self):
        from app.graph.nodes.rag_enrich import rag_enrich

        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user1",
        }

        with patch("app.graph.nodes.rag_enrich.settings") as mock_settings:
            mock_settings.SYNTHETIC_API_KEY = "test_key"

            result = await rag_enrich(state)

            assert "rag_context" in result
            assert result["rag_context"]["chunks"] == []
            assert result["rag_context"]["error"] is None


class TestRAGFailureHandling:
    @pytest.mark.asyncio
    async def test_rag_failure_does_not_block_evaluation(self):
        from app.graph.nodes.rag_enrich import rag_enrich

        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {"readme": "Test content"},
            "evaluation_criteria": "basic",
            "user_id": "user1",
        }

        with patch("app.graph.nodes.rag_enrich.settings") as mock_settings:
            mock_settings.SYNTHETIC_API_KEY = "test_key"

            with patch("app.graph.nodes.rag_enrich._get_embeddings") as mock_embed:
                mock_embed.side_effect = Exception("Embedding API unavailable")

                result = await rag_enrich(state)

                assert "rag_context" in result
                assert result["rag_context"]["chunks"] == []
                assert "Embedding API unavailable" in result["rag_context"]["error"]
                assert "errors" in result

    @pytest.mark.asyncio
    async def test_rag_returns_cached_context_if_exists(self):
        from app.graph.nodes.rag_enrich import rag_enrich

        existing_context = {
            "query": "cached query",
            "chunks": [{"text": "cached", "source": "readme"}],
            "error": None,
        }
        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {},
            "evaluation_criteria": "basic",
            "user_id": "user1",
            "rag_context": existing_context,
        }

        result = await rag_enrich(state)

        assert result["rag_context"] == existing_context


class TestProviderFallback:
    def test_build_llm_with_invalid_provider_raises_error(self):
        from app.providers.llm import build_llm

        with pytest.raises(ValueError, match="Unsupported provider"):
            build_llm(
                provider="invalid_provider",
                api_key=None,
                model=None,
                temperature=None,
                max_output_tokens=None,
            )

    def test_byok_validation_rejects_empty_key(self):
        from app.providers.llm import resolve_byok

        resolved, error = resolve_byok("   ", "gemini")

        assert resolved is None
        assert error is not None
        assert error.error_code == "invalid_api_key"


class TestRetryPolicy:
    @pytest.mark.asyncio
    async def test_sommelier_records_timing_on_success(self):
        from app.graph.nodes.marcel import MarcelNode

        node = MarcelNode()
        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {"readme": "Test README"},
            "evaluation_criteria": "basic",
            "user_id": "user1",
        }

        mock_llm = MockLLM(sommelier_name="marcel")

        with patch("app.graph.nodes.base.build_llm", return_value=mock_llm):
            result = await node.evaluate(state)

            assert "trace_metadata" in result
            assert "marcel" in result["trace_metadata"]
            assert "started_at" in result["trace_metadata"]["marcel"]
            assert "completed_at" in result["trace_metadata"]["marcel"]

    @pytest.mark.asyncio
    async def test_sommelier_records_timing_on_failure(self):
        from app.graph.nodes.marcel import MarcelNode

        node = MarcelNode()
        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {"readme": "Test README"},
            "evaluation_criteria": "basic",
            "user_id": "user1",
        }

        mock_llm = MockLLMWithError(error_message="Timeout")

        with patch("app.graph.nodes.base.build_llm", return_value=mock_llm):
            result = await node.evaluate(state)

            assert "trace_metadata" in result
            assert "marcel" in result["trace_metadata"]
            assert result["trace_metadata"]["marcel"]["completed_at"] is not None
