"""Evaluation models for somm.dev backend.

This module contains all Pydantic models related to code evaluations:
- EvaluationStatus: Enum for evaluation status
- EvaluationCriteria: Enum for evaluation criteria modes
- RepoContext: Model for repository context information
- EvaluationCreate: Model for creating evaluations
- EvaluationInDB: Model for evaluation data in database
- EvaluationResponse: Model for evaluation data in API responses
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

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
