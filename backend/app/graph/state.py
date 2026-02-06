"""Graph state definition for the evaluation pipeline."""

from typing import Annotated, TypedDict, Optional, List, Required, NotRequired, Dict
from operator import add

from app.models.graph import TraceEvent, ItemScore, ExcludedTechnique, AgentContribution


def merge_dicts(
    current: Optional[Dict[str, object]], incoming: Optional[Dict[str, object]]
) -> Dict[str, object]:
    return {**(current or {}), **(incoming or {})}


def merge_methodology_trace(
    current: Optional[List[TraceEvent]], incoming: Optional[List[TraceEvent]]
) -> List[TraceEvent]:
    """Merge methodology trace events with deterministic ordering.

    Orders by step, then timestamp, then agent, then technique_id.
    Dedupes by (step, agent, technique_id, item_id, action) tuple.

    Args:
        current: Existing trace events
        incoming: New trace events to merge

    Returns:
        Sorted, deduplicated list of trace events
    """
    current = current or []
    incoming = incoming or []

    seen = set()
    all_events = []

    for event in current + incoming:
        key = (event.step, event.agent, event.technique_id, event.item_id, event.action)
        if key not in seen:
            seen.add(key)
            all_events.append(event)

    all_events.sort(key=lambda e: (e.step, e.timestamp, e.agent, e.technique_id))
    return all_events


def merge_item_scores(
    current: Optional[Dict[str, ItemScore]], incoming: Optional[Dict[str, ItemScore]]
) -> Dict[str, ItemScore]:
    """Merge item scores with conflict resolution (latest timestamp wins).

    Args:
        current: Existing item scores
        incoming: New item scores to merge

    Returns:
        Merged dictionary with latest scores for each item
    """
    current = current or {}
    incoming = incoming or {}

    result = dict(current)
    for item_id, new_score in incoming.items():
        if item_id not in result:
            result[item_id] = new_score
        else:
            existing = result[item_id]
            if new_score.timestamp > existing.timestamp:
                result[item_id] = new_score
    return result


def merge_techniques_used(
    current: Optional[List[str]], incoming: Optional[List[str]]
) -> List[str]:
    """Merge technique IDs with unique, stable ordering.

    Args:
        current: Existing technique IDs
        incoming: New technique IDs to merge

    Returns:
        Sorted, deduplicated list of technique IDs
    """
    current = current or []
    incoming = incoming or []

    combined = set(current) | set(incoming)
    return sorted(combined)


def merge_excluded_techniques(
    current: Optional[List[ExcludedTechnique]],
    incoming: Optional[List[ExcludedTechnique]],
) -> List[ExcludedTechnique]:
    """Merge excluded techniques with deduplication by technique_id.

    Later entries for the same technique_id overwrite earlier ones.

    Args:
        current: Existing excluded techniques
        incoming: New excluded techniques to merge

    Returns:
        Deduplicated list of excluded techniques
    """
    current = current or []
    incoming = incoming or []

    by_id = {}
    for tech in current + incoming:
        by_id[tech.technique_id] = tech

    return sorted(by_id.values(), key=lambda x: x.technique_id)


def merge_agent_contributions(
    current: Optional[Dict[str, AgentContribution]],
    incoming: Optional[Dict[str, AgentContribution]],
) -> Dict[str, AgentContribution]:
    """Merge agent contributions with aggregation.

    Merges technique_ids, item_ids, and artifacts for each agent.

    Args:
        current: Existing agent contributions
        incoming: New agent contributions to merge

    Returns:
        Merged dictionary with aggregated contributions
    """
    current = current or {}
    incoming = incoming or {}

    result = dict(current)
    for agent, contribution in incoming.items():
        if agent not in result:
            result[agent] = contribution
        else:
            existing = result[agent]
            merged_techniques = sorted(
                set(existing.technique_ids) | set(contribution.technique_ids)
            )
            merged_items = sorted(set(existing.item_ids) | set(contribution.item_ids))
            merged_artifacts = {**existing.artifacts, **contribution.artifacts}
            result[agent] = AgentContribution(
                agent=agent,
                technique_ids=merged_techniques,
                item_ids=merged_items,
                artifacts=merged_artifacts,
            )
    return result


class EvaluationState(TypedDict):
    """State definition for the evaluation graph.

    This TypedDict represents the complete state of the evaluation pipeline,
    tracking inputs, sommelier results, synthesis, and progress.
    """

    evaluation_id: NotRequired[str]
    repo_url: Required[str]
    repo_context: Required[dict]
    evaluation_criteria: Required[str]
    user_id: Required[str]
    progress_percent: NotRequired[int]
    current_stage: NotRequired[str]

    # Sommelier results
    marcel_result: NotRequired[Optional[dict]]
    isabella_result: NotRequired[Optional[dict]]
    heinrich_result: NotRequired[Optional[dict]]
    sofia_result: NotRequired[Optional[dict]]
    laurent_result: NotRequired[Optional[dict]]

    # Synthesis result
    jeanpierre_result: NotRequired[Optional[dict]]

    # Progress tracking with aggregation
    completed_sommeliers: NotRequired[Annotated[List[str], add]]
    errors: NotRequired[Annotated[List[str], add]]

    # Observability
    token_usage: NotRequired[
        Annotated[Dict[str, Dict[str, Optional[int]]], merge_dicts]
    ]
    cost_usage: NotRequired[Annotated[Dict[str, Optional[float]], merge_dicts]]
    trace_metadata: NotRequired[
        Annotated[Dict[str, Dict[str, Optional[str]]], merge_dicts]
    ]

    rag_context: NotRequired[Optional[dict]]

    aroma_result: NotRequired[Optional[dict]]
    palate_result: NotRequired[Optional[dict]]
    body_result: NotRequired[Optional[dict]]
    finish_result: NotRequired[Optional[dict]]
    balance_result: NotRequired[Optional[dict]]
    vintage_result: NotRequired[Optional[dict]]
    terroir_result: NotRequired[Optional[dict]]
    cellar_result: NotRequired[Optional[dict]]

    started_at: NotRequired[str]
    completed_at: NotRequired[Optional[str]]

    # Enhanced state tracking (Phase G1)
    methodology_trace: NotRequired[Annotated[List[TraceEvent], merge_methodology_trace]]
    item_scores: NotRequired[Annotated[Dict[str, ItemScore], merge_item_scores]]
    techniques_used: NotRequired[Annotated[List[str], merge_techniques_used]]
    excluded_techniques: NotRequired[
        Annotated[List[ExcludedTechnique], merge_excluded_techniques]
    ]
    agent_contributions: NotRequired[
        Annotated[Dict[str, AgentContribution], merge_agent_contributions]
    ]

    # Normalized scoring fields
    raw_score: NotRequired[float]
    max_possible: NotRequired[float]
    normalized_score: NotRequired[float]
    evaluated_count: NotRequired[int]
    unevaluated_count: NotRequired[int]
    coverage_rate: NotRequired[float]
