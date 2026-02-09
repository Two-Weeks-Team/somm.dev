"""Evaluation service for orchestrating code evaluations.

This module provides the main evaluation orchestration logic:
- Starting new evaluations
- Running the LangGraph evaluation pipeline
- Saving results to the database
- Handling errors gracefully
"""

import logging
import uuid
from asyncio import Queue
from typing import Any, Dict, Optional

from app.core.exceptions import CorkedError, EmptyCellarError
from app.database.repositories.evaluation import EvaluationRepository
from app.database.repositories.result import ResultRepository
from app.database.repositories.user import UserRepository
from app.graph.state import EvaluationState
from app.services.github_service import GitHubService, parse_github_url
from app.techniques import load_techniques
from app.providers.llm import resolve_byok
from app.services.provider_routing import decide_provider

logger = logging.getLogger(__name__)


async def _get_stored_key(
    user_id: str, provider: str = "google"
) -> tuple[str | None, str]:
    """Retrieve user's stored BYOK API key.

    Returns:
        Tuple of (decrypted_key_or_None, source_label)
        source_label: "stored_byok" if found, "none" if not
    """
    if not user_id:
        return None, "none"
    try:
        from app.database.repositories.api_key import APIKeyRepository
        from app.services.encryption import EncryptionService

        repo = APIKeyRepository()
        key_doc = await repo.get_key(user_id, provider)
        if not key_doc:
            return None, "none"

        encryption = EncryptionService()
        decrypted = encryption.decrypt(key_doc["encrypted_key"])
        return decrypted, "stored_byok"
    except Exception as e:
        logger.warning(f"Failed to retrieve stored key for user {user_id}: {e}")
        return None, "none"


async def _prepare_repo_context(
    repo_url: str,
    api_key: Optional[str] = None,
    github_token: Optional[str] = None,
    user_id: Optional[str] = None,
) -> tuple[dict, str]:
    """Prepare repository context for evaluation.

    Args:
        repo_url: The GitHub repository URL.
        api_key: Optional BYOK API key.
        github_token: Optional user's GitHub access token for private repo access.
        user_id: Optional user ID for stored key lookup.

    Returns:
        Tuple of (repo_context dict, resolved_api_key).
    """
    owner, repo_name = parse_github_url(repo_url)

    github = GitHubService(token=github_token)
    repo_context = await github.get_full_repo_context(owner, repo_name)

    techniques, technique_errors = load_techniques()
    if technique_errors:
        logger.warning("Technique load errors", extra={"errors": technique_errors})
    # Load all 75 techniques without source-based filtering
    repo_context["techniques"] = [tech.model_dump() for tech in techniques]

    effective_key = api_key
    api_key_source = "request_byok" if api_key else "system"
    if not effective_key and user_id:
        stored_key, source = await _get_stored_key(user_id)
        if stored_key:
            effective_key = stored_key
            api_key_source = source

    resolved_key, byok_error = resolve_byok(effective_key)
    repo_context["api_key_source"] = api_key_source
    if byok_error:
        repo_context["byok_error"] = byok_error

    return repo_context, resolved_key


async def _get_user_doc(user_id: str | None) -> dict | None:
    if not user_id:
        return None
    try:
        user_repo = UserRepository()
        return await user_repo.get_by_id(user_id)
    except Exception:
        logger.warning(
            "Failed to fetch user doc for provider routing", extra={"user_id": user_id}
        )
        return None


def _create_initial_state(
    repo_url: str,
    repo_context: dict,
    criteria: str,
    user_id: str = "",
    evaluation_id: Optional[str] = None,
    include_progress: bool = False,
) -> EvaluationState:
    """Create initial EvaluationState for the graph.

    Args:
        repo_url: The GitHub repository URL.
        repo_context: Prepared repository context.
        criteria: The evaluation criteria mode.
        user_id: The user ID.
        evaluation_id: Optional evaluation ID for event emission.
        include_progress: Whether to include progress fields.

    Returns:
        Initial EvaluationState dict.
    """
    state: EvaluationState = {
        "repo_url": repo_url,
        "repo_context": repo_context,
        "evaluation_criteria": criteria,
        "user_id": user_id,
        "marcel_result": None,
        "isabella_result": None,
        "heinrich_result": None,
        "sofia_result": None,
        "laurent_result": None,
        "jeanpierre_result": None,
        "completed_sommeliers": [],
        "errors": [],
        "token_usage": {},
        "cost_usage": {},
        "trace_metadata": {},
        "started_at": "",
        "completed_at": None,
    }

    if evaluation_id:
        state["evaluation_id"] = evaluation_id

    if include_progress:
        state["progress_percent"] = 0
        state["current_stage"] = ""

    return state


def _create_graph_config(
    resolved_key: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> dict:
    """Create graph configuration.

    Args:
        resolved_key: Resolved API key.
        provider: LLM provider.
        model: Model name.
        temperature: Model temperature.

    Returns:
        Graph config dict.
    """
    return {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "provider": provider or "vertex",
            "api_key": resolved_key,
            "model": model,
            "temperature": temperature,
            "max_output_tokens": 2048,
        }
    }


async def start_evaluation(
    repo_url: str,
    criteria: str,
    user_id: str,
    custom_criteria: Optional[list[str]] = None,
    evaluation_mode: str = "six_sommeliers",
) -> str:
    """Start a new evaluation for a repository.

    Args:
        repo_url: The GitHub repository URL.
        criteria: The evaluation criteria mode (basic, hackathon, academic, custom).
        user_id: The ID of the user requesting the evaluation.
        custom_criteria: Optional list of custom criteria for custom mode.
        evaluation_mode: Evaluation mode (six_sommeliers or grand_tasting).

    Returns:
        The evaluation ID.

    Raises:
        CorkedError: If the URL is invalid or criteria is not recognized.
    """
    try:
        owner, repo_name = parse_github_url(repo_url)
    except CorkedError:
        raise CorkedError("Invalid GitHub repository URL")

    valid_criteria = {"basic", "hackathon", "academic", "custom"}
    if criteria not in valid_criteria:
        raise CorkedError(
            f"Invalid criteria: {criteria}. Must be one of {valid_criteria}"
        )

    from app.graph.graph_factory import is_valid_mode

    if not is_valid_mode(evaluation_mode):
        raise CorkedError(
            f"Invalid evaluation mode: {evaluation_mode}. "
            "Must be 'six_sommeliers', 'grand_tasting', or 'full_techniques'"
        )

    repo = EvaluationRepository()
    eval_id = await repo.create_evaluation(
        eval_data={
            "repo_context": {
                "repo_url": repo_url,
            },
            "criteria": criteria,
            "user_id": user_id,
            "custom_criteria": custom_criteria,
            "evaluation_mode": evaluation_mode,
        }
    )

    return str(eval_id)


async def run_evaluation_pipeline(
    repo_url: str,
    criteria: str,
    user_id: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    api_key: Optional[str] = None,
    progress_queue: Optional[Queue] = None,
    github_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Run the LangGraph evaluation pipeline (blocking, legacy).

    Note: For non-blocking evaluation with SSE streaming,
    use run_evaluation_pipeline_with_events() instead.
    """
    repo_context, resolved_key = await _prepare_repo_context(
        repo_url, api_key, github_token, user_id
    )
    user_doc = await _get_user_doc(user_id)
    provider_decision = decide_provider(
        user_doc, provider, resolved_key if api_key else None
    )
    state = _create_initial_state(
        repo_url, repo_context, criteria, user_id=user_id or ""
    )
    config = _create_graph_config(
        resolved_key,
        provider_decision.provider,
        model,
        temperature,
    )

    from app.graph.graph import get_evaluation_graph

    graph = get_evaluation_graph()
    return await graph.ainvoke(state, config=config)


async def save_evaluation_results(
    evaluation_id: str,
    evaluation_data: Dict[str, Any],
    evaluation_mode: str = "six_sommeliers",
) -> str:
    """Save evaluation results to the database.

    Args:
        evaluation_id: The evaluation ID.
        evaluation_data: The evaluation results data.
        evaluation_mode: The evaluation mode used.

    Returns:
        The result ID.
    """
    repo = ResultRepository()

    from app.models.results import get_rating_tier, SommelierOutput, FinalEvaluation

    cellar_result = evaluation_data.get("cellar_result")
    jeanpierre_result = evaluation_data.get("jeanpierre_result")

    is_grand_tasting = evaluation_mode == "grand_tasting"
    is_full_techniques = evaluation_mode == "full_techniques"

    if is_grand_tasting:
        cellar_result = cellar_result or {}
        aggregate_score = cellar_result.get("aggregate_score", 0)
        overall_score = int(aggregate_score * 20)
        rating_tier = get_rating_tier(overall_score)
        summary = cellar_result.get("summary", "")

        tasting_note_names = {
            "aroma": ("Aroma Notes", "Problem Analysis"),
            "palate": ("Palate Notes", "Innovation"),
            "body": ("Body Notes", "Risk Analysis"),
            "finish": ("Finish Notes", "User-Centricity"),
            "balance": ("Balance Notes", "Feasibility"),
            "vintage": ("Vintage Notes", "Opportunity"),
            "terroir": ("Terroir Notes", "Presentation"),
        }
        sommelier_outputs = []
        for key, (name, role) in tasting_note_names.items():
            result = evaluation_data.get(f"{key}_result")
            if result:
                agg_score = result.get("aggregate_score", 0)
                techniques = result.get("techniques_applied", [])
                technique_names = [t.get("technique_name", "") for t in techniques]
                sommelier_outputs.append(
                    SommelierOutput(
                        sommelier_name=name,
                        score=int(agg_score * 20),
                        summary=result.get("summary", ""),
                        recommendations=technique_names,
                    )
                )
    elif is_full_techniques:
        normalized_score = evaluation_data.get("normalized_score", 0)
        overall_score = int(normalized_score)
        rating_tier = get_rating_tier(overall_score)
        quality_gate = evaluation_data.get("quality_gate", "")
        coverage = evaluation_data.get("coverage_rate", 0)

        summary = (
            f"Comprehensive evaluation using 75 techniques. "
            f"Quality Gate: {quality_gate}. "
            f"Coverage: {coverage * 100:.1f}%."
        )

        BMAD_CATEGORY_CONFIG = {
            "A": ("Problem Definition", 25, ["aroma", "palate"]),
            "B": ("Technical Design", 25, ["body", "balance"]),
            "C": ("Implementation", 30, ["vintage", "terroir"]),
            "D": ("Documentation", 20, ["cellar", "finish"]),
        }

        category_scores = evaluation_data.get("category_scores", {})
        trace_metadata = evaluation_data.get("trace_metadata", {})

        sommelier_outputs = []
        for cat_id, (name, max_score, tasting_cats) in BMAD_CATEGORY_CONFIG.items():
            cat_data = category_scores.get(cat_id, {})
            raw_score = cat_data.get("score", 0)
            scaled_score = int((raw_score / max_score) * 100) if max_score > 0 else 0

            technique_info = []
            for tasting_cat in tasting_cats:
                cat_trace = trace_metadata.get(tasting_cat, {})
                succeeded = cat_trace.get("techniques_succeeded", 0)
                total = cat_trace.get("techniques_count", 0)
                if total > 0:
                    technique_info.append(
                        f"{tasting_cat.capitalize()}: {succeeded}/{total}"
                    )

            cat_summary = (
                f"Category {cat_id} ({name}): Scored {raw_score:.1f}/{max_score} points. "
                f"Techniques evaluated: {', '.join(technique_info) if technique_info else 'N/A'}."
            )

            sommelier_outputs.append(
                SommelierOutput(
                    sommelier_name=name,
                    score=scaled_score,
                    summary=cat_summary,
                    recommendations=technique_info,
                )
            )
    else:
        jeanpierre_result = jeanpierre_result or {}
        overall_score = jeanpierre_result.get("total_score", 0)
        rating_tier = get_rating_tier(overall_score)
        summary = jeanpierre_result.get("verdict", "")

        sommelier_names = {
            "marcel": ("Marcel", "Cellar Master"),
            "isabella": ("Isabella", "Wine Critic"),
            "heinrich": ("Heinrich", "Quality Inspector"),
            "sofia": ("Sofia", "Vineyard Scout"),
            "laurent": ("Laurent", "Winemaker"),
        }
        sommelier_outputs = []
        for key, (name, role) in sommelier_names.items():
            result = evaluation_data.get(f"{key}_result")
            if result:
                sommelier_outputs.append(
                    SommelierOutput(
                        sommelier_name=name,
                        score=result.get("score", 0),
                        summary=result.get("notes", ""),
                        recommendations=result.get("techniques_used", []),
                    )
                )

    final_evaluation = FinalEvaluation(
        overall_score=overall_score,
        rating_tier=rating_tier,
        sommelier_outputs=sommelier_outputs,
        summary=summary,
    )

    result_id = await repo.create_result(
        result_data={
            "evaluation_id": evaluation_id,
            "final_evaluation": final_evaluation.model_dump(),
        }
    )

    return str(result_id)


async def handle_evaluation_error(
    evaluation_id: str,
    error_message: str,
) -> None:
    """Handle an evaluation error.

    Args:
        evaluation_id: The evaluation ID.
        error_message: The error message.
    """
    logger.error(f"Evaluation {evaluation_id} failed: {error_message}")

    repo = EvaluationRepository()
    await repo.update_status(evaluation_id, "failed", error_message)


async def get_evaluation_progress(
    evaluation_id: str,
) -> Dict[str, Any]:
    """Get the progress of an evaluation.

    Args:
        evaluation_id: The evaluation ID.

    Returns:
        A dictionary containing progress information.
    """
    repo = EvaluationRepository()
    evaluation = await repo.get_by_id(evaluation_id)

    if not evaluation:
        raise EmptyCellarError(f"Evaluation not found: {evaluation_id}")

    status = evaluation.get("status", "pending")
    completed = evaluation.get("completed_sommeliers", [])
    user_id = evaluation.get("user_id")
    evaluation_mode = evaluation.get("evaluation_mode", "six_sommeliers")

    total_steps = (
        10
        if evaluation_mode == "full_techniques"
        else (8 if evaluation_mode == "grand_tasting" else 6)
    )

    if status == "pending":
        return {
            "status": "pending",
            "user_id": user_id,
            "completed_steps": 0,
            "total_steps": total_steps,
            "percentage": 0,
        }
    elif status == "failed":
        return {
            "status": "failed",
            "user_id": user_id,
            "completed_steps": len(completed),
            "total_steps": total_steps,
            "percentage": round(len(completed) / total_steps * 100, 2),
            "error": evaluation.get("error_message"),
        }
    elif status == "running":
        return {
            "status": "running",
            "user_id": user_id,
            "completed_steps": len(completed),
            "remaining_steps": total_steps - len(completed),
            "total_steps": total_steps,
            "percentage": round(len(completed) / total_steps * 100, 2),
            "completed_sommeliers": completed,
        }
    else:
        return {
            "status": "completed",
            "user_id": user_id,
            "completed_steps": total_steps,
            "total_steps": total_steps,
            "percentage": 100,
        }


async def run_full_evaluation(
    repo_url: str,
    criteria: str,
    user_id: str,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    api_key: Optional[str] = None,
    github_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Run a complete evaluation from start to finish (blocking).

    Note: This is the legacy blocking version. For non-blocking evaluation
    with real-time SSE streaming, use run_evaluation_pipeline_with_events().
    """
    eval_id = await start_evaluation(repo_url, criteria, user_id)

    eval_repo = EvaluationRepository()
    await eval_repo.update_status(eval_id, "running")

    try:
        result = await run_evaluation_pipeline(
            repo_url,
            criteria,
            user_id=user_id,
            provider=provider,
            model=model,
            temperature=temperature,
            api_key=api_key,
            github_token=github_token,
        )
        if result.get("errors"):
            logger.warning(f"Evaluation {eval_id} node errors: {result['errors']}")
        await save_evaluation_results(eval_id, result)
        await eval_repo.update_status(eval_id, "completed")

        jeanpierre = result.get("jeanpierre_result") or {}
        return {
            "evaluation_id": eval_id,
            "status": "completed",
            "score": jeanpierre.get("overall_score", 0),
            "rating_tier": jeanpierre.get("rating_tier", ""),
        }
    except Exception as e:
        error_msg = str(e)
        await handle_evaluation_error(eval_id, error_msg)
        raise


async def run_evaluation_pipeline_with_events(
    evaluation_id: str,
    repo_url: str,
    criteria: str,
    user_id: str,
    evaluation_mode: str = "six_sommeliers",
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    api_key: Optional[str] = None,
    github_token: Optional[str] = None,
) -> Dict[str, Any]:
    """Run evaluation pipeline with SSE event emission (non-blocking).

    Designed to be called from a background task. Includes evaluation_id
    in graph state for sommelier nodes to emit progress events.
    """
    eval_repo = EvaluationRepository()
    await eval_repo.update_status(evaluation_id, "running")

    try:
        repo_context, resolved_key = await _prepare_repo_context(
            repo_url, api_key, github_token, user_id
        )
        user_doc = await _get_user_doc(user_id)
        provider_decision = decide_provider(
            user_doc, provider, resolved_key if api_key else None
        )
        state = _create_initial_state(
            repo_url,
            repo_context,
            criteria,
            user_id=user_id,
            evaluation_id=evaluation_id,
            include_progress=True,
        )
        config = _create_graph_config(
            resolved_key,
            provider_decision.provider,
            model,
            temperature,
        )

        from app.graph.graph_factory import get_evaluation_graph

        graph = get_evaluation_graph(evaluation_mode)
        result = await graph.ainvoke(state, config=config)

        if result.get("errors"):
            logger.warning(
                f"Evaluation {evaluation_id} node errors: {result['errors']}"
            )

        await save_evaluation_results(evaluation_id, result, evaluation_mode)
        await eval_repo.update_status(evaluation_id, "completed")

        if evaluation_mode == "full_techniques":
            return {
                "evaluation_id": evaluation_id,
                "status": "completed",
                "score": result.get("normalized_score", 0),
                "quality_gate": result.get("quality_gate", ""),
                "coverage_rate": result.get("coverage_rate", 0),
            }

        jeanpierre = result.get("jeanpierre_result") or {}
        return {
            "evaluation_id": evaluation_id,
            "status": "completed",
            "score": jeanpierre.get("overall_score", 0),
            "rating_tier": jeanpierre.get("rating_tier", ""),
        }
    except Exception:
        raise


async def get_evaluation_result(
    evaluation_id: str,
) -> Optional[Dict[str, Any]]:
    """Get the results of an evaluation.

    Args:
        evaluation_id: The evaluation ID.

    Returns:
        The evaluation results dictionary or None if not found.
    """
    repo = EvaluationRepository()
    evaluation = await repo.get_by_id(evaluation_id)

    if not evaluation:
        return None

    if evaluation.get("status") != "completed":
        raise CorkedError("Evaluation is still in progress or failed")

    result_repo = ResultRepository()
    result = await result_repo.get_by_evaluation_id(evaluation_id)

    if not result:
        return None

    return {
        "evaluation_id": evaluation_id,
        "final_evaluation": result.get("final_evaluation", {}),
        "created_at": result.get("created_at"),
    }


async def get_user_history(
    user_id: str,
    skip: int = 0,
    limit: int = 50,
) -> list[Dict[str, Any]]:
    """Get the evaluation history for a user.

    Args:
        user_id: The user ID to get history for.
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        A list of evaluation summaries.
    """
    repo = EvaluationRepository()
    evaluations = await repo.list_by_user(user_id, limit=limit, skip=skip)

    history = []
    for eval_doc in evaluations:
        summary = {
            "id": str(eval_doc["_id"]),
            "repo_context": eval_doc.get("repo_context", {}),
            "criteria": eval_doc.get("criteria"),
            "status": eval_doc.get("status"),
            "created_at": eval_doc.get("created_at"),
        }

        if eval_doc.get("status") == "completed":
            result_repo = ResultRepository()
            result = await result_repo.get_by_evaluation_id(str(eval_doc["_id"]))
            if result:
                summary["score"] = result.get("final_evaluation", {}).get(
                    "overall_score"
                )
                summary["rating_tier"] = result.get("final_evaluation", {}).get(
                    "rating_tier"
                )

        history.append(summary)

    return history
