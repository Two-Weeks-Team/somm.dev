"""Evaluation models for somm.dev backend.

This module contains all Pydantic models related to code evaluations:
- EvaluationStatus: Enum for evaluation status
- EvaluationCriteria: Enum for evaluation criteria modes
- RepoContext: Model for repository context information
- EvaluationCreate: Model for creating evaluations
- EvaluationInDB: Model for evaluation data in database
- EvaluationResponse: Model for evaluation data in API responses
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class EvaluationStatus(str, Enum):
    """Enum representing the status of an evaluation.

    Attributes:
        pending: Evaluation is queued but not started
        running: Evaluation is currently in progress
        completed: Evaluation has finished successfully
        failed: Evaluation encountered an error
    """

    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class EvaluationCriteria(str, Enum):
    """Enum representing the criteria mode for evaluations.

    Attributes:
        basic: General code review
        hackathon: Gemini 3 Hackathon judging criteria
        academic: Research project evaluation criteria
        custom: User-defined custom criteria
    """

    basic = "basic"
    hackathon = "hackathon"
    academic = "academic"
    custom = "custom"


class RepoContext(BaseModel):
    """Model for repository context information.

    This model contains information about the repository being evaluated.
    """

    repo_url: str = Field(..., description="URL of the repository")
    branch: Optional[str] = Field(default=None, description="Branch name")
    commit_sha: Optional[str] = Field(default=None, description="Commit SHA")


class EvaluationCreate(BaseModel):
    """Model for creating a new evaluation.

    This model is used when a user requests a new code evaluation.
    """

    repo_context: RepoContext = Field(..., description="Repository context information")
    criteria: EvaluationCriteria = Field(..., description="Evaluation criteria mode")
    user_id: str = Field(..., description="ID of the user requesting evaluation")
    custom_criteria: Optional[List[str]] = Field(
        default=None, description="Custom criteria for evaluation"
    )


class EvaluationInDB(EvaluationCreate):
    """Model for evaluation data stored in the database.

    This model extends EvaluationCreate with database-specific fields.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., alias="_id", description="MongoDB document ID")
    status: EvaluationStatus = Field(
        default=EvaluationStatus.pending, description="Evaluation status"
    )
    created_at: datetime = Field(..., description="Evaluation creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    error_message: Optional[str] = Field(
        default=None, description="Error message if failed"
    )


class EvaluationResponse(BaseModel):
    """Model for evaluation data in API responses.

    This model is used when returning evaluation data in API responses.
    """

    id: str = Field(..., description="Evaluation ID")
    repo_context: RepoContext = Field(..., description="Repository context information")
    criteria: EvaluationCriteria = Field(..., description="Evaluation criteria mode")
    status: EvaluationStatus = Field(..., description="Evaluation status")
    created_at: datetime = Field(..., description="Evaluation creation timestamp")


class FullTechniqueResult(BaseModel):
    """Model for full_techniques evaluation results.

    This model stores comprehensive evaluation results from the full_techniques
    evaluation mode, including detailed item scores, dimension scores, and
    methodology trace information.

    Attributes:
        evaluation_id: Reference to the parent evaluation
        evaluation_mode: Mode of evaluation (default: "full_techniques")
        repo_url: URL of the evaluated repository
        item_scores: Dictionary of 17 BMAD item scores
        dimension_scores: Dictionary of dimension scores with score/max structure
        total_score: Raw total score
        normalized_score: Normalized score (0-100)
        quality_gate: Quality gate status (PASS, CONCERNS, FAIL, INCOMPLETE)
        coverage: Coverage rate (0.0-1.0)
        techniques_used: List of technique IDs used
        failed_techniques: List of failed technique info with error details
        hat_contributions: Dictionary mapping hat types to technique IDs
        methodology_trace: List of trace events for methodology visualization
        api_key_source: Source of API key used (user or system)
        cost_summary: Cost tracking information
        duration_ms: Total evaluation duration in milliseconds
        created_at: Timestamp when result was created
    """

    evaluation_id: str = Field(..., description="Reference to the parent evaluation")
    evaluation_mode: str = Field(
        default="full_techniques", description="Mode of evaluation"
    )
    repo_url: str = Field(..., description="URL of the evaluated repository")
    item_scores: dict[str, Any] = Field(
        default_factory=dict, description="17 BMAD item scores"
    )
    dimension_scores: dict[str, dict] = Field(
        default_factory=dict, description="Dimension scores with score/max structure"
    )
    total_score: float = Field(default=0.0, description="Raw total score")
    normalized_score: float = Field(default=0.0, description="Normalized score (0-100)")
    quality_gate: str = Field(default="INCOMPLETE", description="Quality gate status")
    coverage: float = Field(default=0.0, description="Coverage rate (0.0-1.0)")
    techniques_used: list[str] = Field(
        default_factory=list, description="List of technique IDs used"
    )
    failed_techniques: list[dict] = Field(
        default_factory=list, description="Failed technique info with error details"
    )
    hat_contributions: dict[str, list[str]] = Field(
        default_factory=dict, description="Hat contributions mapping"
    )
    methodology_trace: list[dict] = Field(
        default_factory=list, description="Trace events for methodology"
    )
    api_key_source: str = Field(default="system", description="Source of API key used")
    cost_summary: dict = Field(default_factory=dict, description="Cost tracking info")
    duration_ms: int = Field(default=0, description="Evaluation duration in ms")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when result was created",
    )
