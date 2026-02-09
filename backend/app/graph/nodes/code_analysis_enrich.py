import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from langchain_core.runnables import RunnableConfig

from app.graph.state import EvaluationState
from app.services.event_channel import create_sommelier_event, get_event_channel
from app.services.repo_clone_service import clone_and_analyze

logger = logging.getLogger(__name__)


async def code_analysis_enrich(
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
                sommelier="code_analysis",
                event_type="enrichment_start",
                progress_percent=0,
                message="Code analysis starting...",
            ),
        )

    if existing := state.get("code_analysis"):
        if evaluation_id:
            event_channel.emit_sync(
                evaluation_id,
                create_sommelier_event(
                    evaluation_id=evaluation_id,
                    sommelier="code_analysis",
                    event_type="enrichment_complete",
                    progress_percent=100,
                    message="Code analysis complete (cached)",
                ),
            )
        return {"code_analysis": existing}

    repo_url = state.get("repo_url", "")
    repo_context = state.get("repo_context", {})
    metadata = repo_context.get("metadata", {})
    branch = metadata.get("default_branch", "main")
    github_token = state.get("github_token")

    if not repo_url:
        if evaluation_id:
            event_channel.emit_sync(
                evaluation_id,
                create_sommelier_event(
                    evaluation_id=evaluation_id,
                    sommelier="code_analysis",
                    event_type="enrichment_complete",
                    progress_percent=100,
                    message="Code analysis skipped (no repo URL)",
                ),
            )
        return {
            "code_analysis": {
                "status": "skipped",
                "skipped_reason": "no repo_url",
                "main_files": [],
                "code_metrics": None,
                "summary": {},
            },
            "trace_metadata": {
                "code_analysis_enrich": {
                    "started_at": started_at,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "skipped": True,
                }
            },
        }

    try:
        clone_result = await clone_and_analyze(
            repo_url=repo_url,
            branch=branch,
            github_token=github_token,
        )

        status = "skipped" if clone_result.skipped_reason else "complete"
        if clone_result.errors and not clone_result.skipped_reason:
            status = "partial"

        code_analysis = {
            "status": status,
            "skipped_reason": clone_result.skipped_reason,
            "main_files": clone_result.main_files,
            "code_metrics": clone_result.code_metrics,
            "summary": clone_result.summary,
        }

        if evaluation_id:
            files_count = len(clone_result.main_files)
            event_channel.emit_sync(
                evaluation_id,
                create_sommelier_event(
                    evaluation_id=evaluation_id,
                    sommelier="code_analysis",
                    event_type="enrichment_complete",
                    progress_percent=100,
                    message=f"Code analysis complete ({files_count} files)",
                ),
            )

        result: Dict[str, Any] = {
            "code_analysis": code_analysis,
            "trace_metadata": {
                "code_analysis_enrich": {
                    "started_at": started_at,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "files_analyzed": len(clone_result.main_files),
                    "status": status,
                }
            },
        }

        if clone_result.errors:
            result["errors"] = [f"code_analysis: {e}" for e in clone_result.errors]

        return result

    except Exception as e:
        logger.exception("code_analysis_enrich failed")
        if evaluation_id:
            event_channel.emit_sync(
                evaluation_id,
                create_sommelier_event(
                    evaluation_id=evaluation_id,
                    sommelier="code_analysis",
                    event_type="enrichment_error",
                    progress_percent=100,
                    message=f"Code analysis failed: {e}",
                ),
            )
        return {
            "code_analysis": {
                "status": "error",
                "skipped_reason": str(e),
                "main_files": [],
                "code_metrics": None,
                "summary": {},
            },
            "errors": [f"code_analysis_enrich failed: {e!s}"],
            "trace_metadata": {
                "code_analysis_enrich": {
                    "started_at": started_at,
                    "completed_at": datetime.now(timezone.utc).isoformat(),
                    "error": str(e),
                }
            },
        }
