import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from langchain_core.runnables import RunnableConfig

from app.core.config import settings
from app.graph.state import EvaluationState
from app.services.event_channel import create_sommelier_event, get_event_channel

logger = logging.getLogger(__name__)


def _get_genai_client():
    from google import genai

    return genai.Client(
        vertexai=True,
        api_key=settings.VERTEX_API_KEY,
    )


async def web_search_enrich(
    state: EvaluationState, config: Optional[RunnableConfig] = None
) -> Dict[str, Any]:
    started_at = datetime.now(timezone.utc).isoformat()
    evaluation_id = state.get("evaluation_id")
    event_channel = get_event_channel()

    if evaluation_id:
        event_channel.emit_sync(
            evaluation_id,
            create_sommelier_event(
                evaluation_id=evaluation_id,
                sommelier="web_search",
                event_type="enrichment_start",
                progress_percent=0,
                message="Web search enrichment starting...",
            ),
        )

    if existing := state.get("web_search_context"):
        if evaluation_id:
            event_channel.emit_sync(
                evaluation_id,
                create_sommelier_event(
                    evaluation_id=evaluation_id,
                    sommelier="web_search",
                    event_type="enrichment_complete",
                    progress_percent=100,
                    message="Web search enrichment complete (cached)",
                ),
            )
        return {"web_search_context": existing}

    if not settings.VERTEX_API_KEY:
        if evaluation_id:
            event_channel.emit_sync(
                evaluation_id,
                create_sommelier_event(
                    evaluation_id=evaluation_id,
                    sommelier="web_search",
                    event_type="enrichment_complete",
                    progress_percent=100,
                    message="Web search skipped (no API key)",
                ),
            )
        return {
            "web_search_context": {
                "query": "",
                "content": "",
                "sources": [],
                "error": "disabled",
            },
            "trace_metadata": {
                "web_search_enrich": {
                    "started_at": started_at,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "skipped": True,
                }
            },
        }

    repo_context = state.get("repo_context", {})
    languages = repo_context.get("languages", {})
    tech_stack = ", ".join(languages.keys()) if languages else "unknown"

    query = (
        f"Latest best practices, known issues, and recommendations "
        f"for a software project using {tech_stack}. "
        f"Focus on code quality, security, and architecture patterns in 2026."
    )

    try:
        from google.genai import types

        client = _get_genai_client()
        grounding_tool = types.Tool(google_search=types.GoogleSearch())

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=query,
            config=types.GenerateContentConfig(
                tools=[grounding_tool],
                temperature=0.3,
                max_output_tokens=2048,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            ),
        )

        sources = []
        if response.candidates:
            gm = getattr(response.candidates[0], "grounding_metadata", None)
            if gm and hasattr(gm, "grounding_chunks"):
                for chunk in (gm.grounding_chunks or [])[:5]:
                    web = getattr(chunk, "web", None)
                    if web:
                        sources.append(
                            {
                                "title": getattr(web, "title", ""),
                                "uri": getattr(web, "uri", ""),
                            }
                        )

        if evaluation_id:
            event_channel.emit_sync(
                evaluation_id,
                create_sommelier_event(
                    evaluation_id=evaluation_id,
                    sommelier="web_search",
                    event_type="enrichment_complete",
                    progress_percent=100,
                    message=f"Web search complete ({len(sources)} sources)",
                ),
            )

        return {
            "web_search_context": {
                "query": query,
                "content": response.text or "",
                "sources": sources,
                "error": None,
            },
            "trace_metadata": {
                "web_search_enrich": {
                    "started_at": started_at,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "sources_count": len(sources),
                }
            },
        }

    except Exception as e:
        logger.warning(f"Web search grounding failed: {e}")
        if evaluation_id:
            event_channel.emit_sync(
                evaluation_id,
                create_sommelier_event(
                    evaluation_id=evaluation_id,
                    sommelier="web_search",
                    event_type="enrichment_error",
                    progress_percent=100,
                    message=f"Web search failed: {e}",
                ),
            )
        return {
            "web_search_context": {
                "query": query,
                "content": "",
                "sources": [],
                "error": str(e),
            },
            "errors": [f"web_search_enrich failed: {e!s}"],
            "trace_metadata": {
                "web_search_enrich": {
                    "started_at": started_at,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "error": str(e),
                }
            },
        }
