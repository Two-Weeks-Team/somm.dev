"""Graph state definition for the evaluation pipeline."""

from typing import Annotated, TypedDict, Optional, List, Required, NotRequired, Dict
from operator import add


def merge_dicts(
    current: Optional[Dict[str, object]], incoming: Optional[Dict[str, object]]
) -> Dict[str, object]:
    return {**(current or {}), **(incoming or {})}


class EvaluationState(TypedDict):
    """State definition for the evaluation graph.

    This TypedDict represents the complete state of the evaluation pipeline,
    tracking inputs, sommelier results, synthesis, and progress.
    """

    # Input fields
    repo_url: Required[str]
    repo_context: Required[dict]
    evaluation_criteria: Required[str]
    user_id: Required[str]

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

    # RAG enrichment
    rag_context: NotRequired[Optional[dict]]

    # Metadata
    started_at: NotRequired[str]
    completed_at: NotRequired[Optional[str]]
