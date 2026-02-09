import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import numpy as np
from langchain_core.runnables import RunnableConfig

from app.core.config import settings
from app.graph.state import EvaluationState

logger = logging.getLogger(__name__)

_README_MAX_LEN = 2000
_FILE_TREE_MAX_LEN = 1000
_METADATA_MAX_LEN = 500

_genai_client = None


def _get_genai_client():
    global _genai_client
    if _genai_client is None:
        from google import genai

        _genai_client = genai.Client(
            api_key=settings.VERTEX_API_KEY,
            vertexai=True,
            project=settings.GOOGLE_CLOUD_PROJECT or None,
        )
    return _genai_client


def _build_documents_from_context(repo_context: dict) -> List[Dict[str, str]]:
    docs = []

    if readme := repo_context.get("readme"):
        docs.append({"text": readme[:_README_MAX_LEN], "source": "readme"})

    if file_tree := repo_context.get("file_tree"):
        tree_str = str(file_tree)[:_FILE_TREE_MAX_LEN]
        docs.append({"text": tree_str, "source": "file_tree"})

    if languages := repo_context.get("languages"):
        lang_str = ", ".join(f"{k}: {v}" for k, v in languages.items())
        docs.append({"text": lang_str, "source": "languages"})

    if metadata := repo_context.get("metadata"):
        meta_str = str(metadata)[:_METADATA_MAX_LEN]
        docs.append({"text": meta_str, "source": "metadata"})

    return docs


def _create_query(state: EvaluationState) -> str:
    repo_url = state.get("repo_url", "")
    criteria = state.get("evaluation_criteria", "basic")
    return f"Evaluate repository {repo_url} using {criteria} criteria"


def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot_product / (norm_a * norm_b))


def _get_embeddings(texts: List[str]) -> List[List[float]]:
    client = _get_genai_client()
    response = client.models.embed_content(
        model=settings.RAG_EMBEDDING_MODEL,
        contents=texts,
    )
    return [emb.values for emb in response.embeddings]


def _similarity_search(
    query_embedding: List[float],
    doc_embeddings: List[List[float]],
    docs: List[Dict[str, str]],
    top_k: int,
) -> List[Dict[str, str]]:
    query_vec = np.array(query_embedding)
    similarities = []

    for idx, doc_emb in enumerate(doc_embeddings):
        doc_vec = np.array(doc_emb)
        sim = _cosine_similarity(query_vec, doc_vec)
        similarities.append((idx, sim))

    similarities.sort(key=lambda x: x[1], reverse=True)
    top_indices = [idx for idx, _ in similarities[:top_k]]

    return [
        {"text": docs[idx]["text"], "source": docs[idx]["source"]}
        for idx in top_indices
    ]


async def rag_enrich(
    state: EvaluationState, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:
    started_at = datetime.now(timezone.utc).isoformat()

    if existing := state.get("rag_context"):
        return {"rag_context": existing}

    repo_context = state.get("repo_context", {})
    query = _create_query(state)

    if not settings.VERTEX_API_KEY:
        return {
            "rag_context": {
                "query": query,
                "chunks": [],
                "error": "RAG disabled: no API key configured",
            },
            "trace_metadata": {
                "rag_enrich": {
                    "started_at": started_at,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "skipped": True,
                }
            },
        }

    try:
        docs = _build_documents_from_context(repo_context)
        if not docs:
            return {
                "rag_context": {"query": query, "chunks": [], "error": None},
            }

        texts = [d["text"] for d in docs]
        all_texts = [query] + texts

        all_embeddings = _get_embeddings(all_texts)
        query_embedding = all_embeddings[0]
        doc_embeddings = all_embeddings[1:]

        chunks = _similarity_search(
            query_embedding,
            doc_embeddings,
            docs,
            min(settings.RAG_TOP_K, len(docs)),
        )

        return {
            "rag_context": {"query": query, "chunks": chunks, "error": None},
            "trace_metadata": {
                "rag_enrich": {
                    "started_at": started_at,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                }
            },
        }

    except Exception as e:
        logger.warning(f"RAG embedding failed: {e}")
        return {
            "rag_context": {"query": query, "chunks": [], "error": str(e)},
            "errors": [f"rag_enrich failed: {e!s}"],
            "trace_metadata": {
                "rag_enrich": {
                    "started_at": started_at,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "error": str(e),
                }
            },
        }
