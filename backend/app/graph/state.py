"""Graph state definition for the evaluation pipeline."""

from typing import Annotated, TypedDict, Optional, List
from operator import add


class EvaluationState(TypedDict):
    """State definition for the evaluation graph.

    This TypedDict represents the complete state of the evaluation pipeline,
    tracking inputs, sommelier results, synthesis, and progress.
    """

    # Input fields
    repo_url: str
    repo_context: dict
    evaluation_criteria: str
    user_id: str

    # Sommelier results
    marcel_result: Optional[dict]
    isabella_result: Optional[dict]
    heinrich_result: Optional[dict]
    sofia_result: Optional[dict]
    laurent_result: Optional[dict]

    # Synthesis result
    jeanpierre_result: Optional[dict]

    # Progress tracking with aggregation
    completed_sommeliers: Annotated[List[str], add]
    errors: Annotated[List[str], add]

    # Metadata
    started_at: str
    completed_at: Optional[str]
