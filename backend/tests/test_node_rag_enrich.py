"""Tests for app/graph/nodes/rag_enrich.py - RAG enrichment node"""

import pytest
from unittest.mock import patch, MagicMock
import numpy as np


class TestRagEnrichNode:
    """Test cases for the RAG enrichment node"""

    @pytest.mark.asyncio
    async def test_rag_enrich_returns_existing_context(self):
        """Test that existing rag_context is returned without reprocessing"""
        from app.graph.nodes.rag_enrich import rag_enrich

        existing_context = {
            "query": "test",
            "chunks": [{"text": "cached"}],
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

    @pytest.mark.asyncio
    async def test_rag_enrich_empty_docs_returns_empty_chunks(self):
        """Test that empty repo_context returns empty chunks without API call"""
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

            assert result["rag_context"]["chunks"] == []
            assert result["rag_context"]["error"] is None

    @pytest.mark.asyncio
    async def test_rag_enrich_failure_does_not_break_evaluation(self):
        """Test that RAG failure returns error in context but doesn't raise"""
        from app.graph.nodes.rag_enrich import rag_enrich

        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {"readme": "Test README content"},
            "evaluation_criteria": "basic",
            "user_id": "user1",
        }

        with patch("app.graph.nodes.rag_enrich.settings") as mock_settings:
            mock_settings.SYNTHETIC_API_KEY = "test_key"

            with patch("app.graph.nodes.rag_enrich._get_embeddings") as mock_embed:
                mock_embed.side_effect = Exception("API connection failed")

                result = await rag_enrich(state)

                assert result["rag_context"]["chunks"] == []
                assert "API connection failed" in result["rag_context"]["error"]
                assert "rag_enrich failed" in result["errors"][0]

    @pytest.mark.asyncio
    async def test_rag_enrich_success_with_mocked_embeddings(self):
        """Test successful RAG enrichment with mocked embeddings"""
        from app.graph.nodes.rag_enrich import rag_enrich

        state = {
            "repo_url": "https://github.com/test/repo",
            "repo_context": {
                "readme": "A Python library for machine learning",
                "languages": {"Python": 80, "JavaScript": 20},
            },
            "evaluation_criteria": "basic",
            "user_id": "user1",
        }

        mock_embeddings = [
            [0.1] * 768,
            [0.2] * 768,
            [0.15] * 768,
        ]

        with patch("app.graph.nodes.rag_enrich.settings") as mock_settings:
            mock_settings.SYNTHETIC_API_KEY = "test_key"
            mock_settings.RAG_TOP_K = 3

            with patch("app.graph.nodes.rag_enrich._get_embeddings") as mock_embed:
                mock_embed.return_value = mock_embeddings

                result = await rag_enrich(state)

                assert result["rag_context"]["error"] is None
                assert len(result["rag_context"]["chunks"]) > 0
                assert "trace_metadata" in result


class TestRagEnrichHelpers:
    """Test helper functions in rag_enrich module"""

    def test_build_documents_from_context(self):
        """Test document building from repo context"""
        from app.graph.nodes.rag_enrich import _build_documents_from_context

        repo_context = {
            "readme": "Test README",
            "file_tree": ["src/", "tests/"],
            "languages": {"Python": 100},
            "metadata": {"stars": 50},
        }

        docs = _build_documents_from_context(repo_context)

        assert len(docs) == 4
        sources = [d["source"] for d in docs]
        assert "readme" in sources
        assert "file_tree" in sources
        assert "languages" in sources
        assert "metadata" in sources

    def test_create_query(self):
        """Test query creation from state"""
        from app.graph.nodes.rag_enrich import _create_query

        state = {
            "repo_url": "https://github.com/test/repo",
            "evaluation_criteria": "hackathon",
        }

        query = _create_query(state)

        assert "https://github.com/test/repo" in query
        assert "hackathon" in query

    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        from app.graph.nodes.rag_enrich import _cosine_similarity

        vec_a = np.array([1.0, 0.0, 0.0])
        vec_b = np.array([1.0, 0.0, 0.0])
        assert _cosine_similarity(vec_a, vec_b) == pytest.approx(1.0)

        vec_c = np.array([0.0, 1.0, 0.0])
        assert _cosine_similarity(vec_a, vec_c) == pytest.approx(0.0)

        vec_zero = np.array([0.0, 0.0, 0.0])
        assert _cosine_similarity(vec_a, vec_zero) == 0.0

    def test_similarity_search(self):
        """Test similarity search returns top-k results"""
        from app.graph.nodes.rag_enrich import _similarity_search

        query_embedding = [1.0, 0.0, 0.0]
        doc_embeddings = [
            [0.9, 0.1, 0.0],
            [0.1, 0.9, 0.0],
            [0.8, 0.2, 0.0],
        ]
        docs = [
            {"text": "doc1", "source": "s1"},
            {"text": "doc2", "source": "s2"},
            {"text": "doc3", "source": "s3"},
        ]

        results = _similarity_search(query_embedding, doc_embeddings, docs, top_k=2)

        assert len(results) == 2
        assert results[0]["text"] == "doc1"
        assert results[1]["text"] == "doc3"
