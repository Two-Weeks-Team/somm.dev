"""Evaluation service for orchestrating code evaluations.

This module provides the main evaluation orchestration logic:
- Starting new evaluations
- Running the LangGraph evaluation pipeline
- Saving results to the database
- Handling errors gracefully
"""

import logging
from asyncio import Queue
from typing import Any, Dict, Optional

from app.core.exceptions import CorkedError, EmptyCellarError
from app.database.repositories.evaluation import EvaluationRepository
from app.database.repositories.result import ResultRepository
from app.graph.state import EvaluationState
from app.services.github_service import GitHubService, parse_github_url

logger = logging.getLogger(__name__)


async def start_evaluation(
    repo_url: str,
    criteria: str,
    user_id: str,
    custom_criteria: Optional[list[str]] = None,
) -> str:
    """Start a new evaluation for a repository.

    Args:
        repo_url: The GitHub repository URL.
        criteria: The evaluation criteria mode (basic, hackathon, academic, custom).
        user_id: The ID of the user requesting the evaluation.
        custom_criteria: Optional list of custom criteria for custom mode.

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

    repo = EvaluationRepository()
    eval_id = await repo.create_evaluation(
        eval_data={
            "repo_context": {
                "repo_url": repo_url,
            },
            "criteria": criteria,
            "user_id": user_id,
            "custom_criteria": custom_criteria,
        }
    )

    return str(eval_id)


async def run_evaluation_pipeline(
    repo_url: str,
    criteria: str,
    progress_queue: Optional[Queue] = None,
) -> Dict[str, Any]:
    """Run the LangGraph evaluation pipeline.

    Args:
        repo_url: The GitHub repository URL.
        criteria: The evaluation criteria mode.
        progress_queue: Optional queue to send progress updates.

    Returns:
        The evaluation results dictionary.
    """
    owner, repo_name = parse_github_url(repo_url)

    github = GitHubService()
    repo_context = await github.get_full_repo_context(owner, repo_name)

    state: EvaluationState = {
        "repo_url": repo_url,
        "repo_context": repo_context,
        "evaluation_criteria": criteria,
        "user_id": "",
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

    from app.graph.graph import get_evaluation_graph

    graph = get_evaluation_graph()
    result = await graph.ainvoke(state)

    return result


async def save_evaluation_results(
    evaluation_id: str,
    evaluation_data: Dict[str, Any],
) -> str:
    """Save evaluation results to the database.

    Args:
        evaluation_id: The evaluation ID.
        evaluation_data: The evaluation results data.

    Returns:
        The result ID.
    """
    repo = ResultRepository()

    from app.models.results import get_rating_tier

    final_eval = evaluation_data.get("jeanpierre_result", {})
    overall_score = final_eval.get("overall_score", 0)
    rating_tier = get_rating_tier(overall_score)

    from app.models.results import FinalEvaluation

    final_evaluation = FinalEvaluation(
        overall_score=overall_score,
        rating_tier=rating_tier,
        sommelier_outputs=final_eval.get("sommelier_outputs", []),
        summary=final_eval.get("summary", ""),
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

    total_steps = 6

    if status == "pending":
        return {
            "status": "pending",
            "completed_steps": 0,
            "total_steps": total_steps,
            "percentage": 0,
        }
    elif status == "failed":
        return {
            "status": "failed",
            "completed_steps": len(completed),
            "total_steps": total_steps,
            "percentage": round(len(completed) / total_steps * 100, 2),
            "error": evaluation.get("error_message"),
        }
    elif status == "running":
        return {
            "status": "running",
            "completed_steps": len(completed),
            "remaining_steps": total_steps - len(completed),
            "total_steps": total_steps,
            "percentage": round(len(completed) / total_steps * 100, 2),
            "completed_sommeliers": completed,
        }
    else:
        return {
            "status": "completed",
            "completed_steps": total_steps,
            "total_steps": total_steps,
            "percentage": 100,
        }


async def run_full_evaluation(
    repo_url: str,
    criteria: str,
    user_id: str,
) -> Dict[str, Any]:
    """Run a complete evaluation from start to finish.

    Args:
        repo_url: The GitHub repository URL.
        criteria: The evaluation criteria mode.
        user_id: The user ID.

    Returns:
        A dictionary containing the evaluation results.
    """
    eval_id = await start_evaluation(repo_url, criteria, user_id)

    eval_repo = EvaluationRepository()
    await eval_repo.update_status(eval_id, "running")

    try:
        result = await run_evaluation_pipeline(repo_url, criteria)
        await save_evaluation_results(eval_id, result)
        await eval_repo.update_status(eval_id, "completed")

        return {
            "evaluation_id": eval_id,
            "status": "completed",
            "score": result.get("jeanpierre_result", {}).get("overall_score", 0),
            "rating_tier": result.get("jeanpierre_result", {}).get("rating_tier", ""),
        }
    except Exception as e:
        error_msg = str(e)
        await handle_evaluation_error(eval_id, error_msg)
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
    skip: int = 0,
    limit: int = 50,
) -> list[Dict[str, Any]]:
    """Get the evaluation history for a user.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.

    Returns:
        A list of evaluation summaries.
    """
    from app.api.deps import get_current_user

    user = await get_current_user()

    repo = EvaluationRepository()
    evaluations = await repo.list_by_user(user.id, limit=limit, skip=skip)

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
