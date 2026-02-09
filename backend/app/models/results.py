"""Results models for somm.dev backend.

This module contains all Pydantic models related to evaluationTier: Enum for results:
- Rating wine-themed rating tiers
- SommelierOutput: Model for individual sommelier evaluation output
- FinalEvaluation: Model for final evaluation results
- ResultInDB: Model for result data in database
- ResultResponse: Model for result data in API responses
- get_rating_tier: Helper function to determine rating tier from score
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class RatingTier(str, Enum):
    """Wine-themed rating tiers for code evaluation scores.

    Attributes:
        legendary: Exceptional quality (95-100)
        grand_cru: Outstanding (90-94)
        premier_cru: Excellent (85-89)
        village: Good (80-84)
        table: Acceptable (70-79)
        house_wine: Light, enjoyable (60-69)
        corked: Below standards (<60)
    """

    Legendary = "Legendary"
    Grand_Cru = "Grand Cru"
    Premier_Cru = "Premier Cru"
    Village = "Village"
    Table = "Table"
    House_Wine = "House Wine"
    Corked = "Corked"


def get_rating_tier(score: int) -> RatingTier:
    """Determine the rating tier based on a score.

    Args:
        score: An integer score between 0 and 100.

    Returns:
        The corresponding RatingTier based on the score range.
    """
    if score >= 95:
        return RatingTier.Legendary
    elif score >= 90:
        return RatingTier.Grand_Cru
    elif score >= 85:
        return RatingTier.Premier_Cru
    elif score >= 80:
        return RatingTier.Village
    elif score >= 70:
        return RatingTier.Table
    elif score >= 60:
        return RatingTier.House_Wine
    else:
        return RatingTier.Corked


class TechniqueDetail(BaseModel):
    id: str = Field(..., description="Technique ID")
    name: str = Field(..., description="Technique name")
    status: str = Field(..., description="success, failed, or skipped")
    score: Optional[float] = Field(None, description="Score if evaluated")
    max_score: Optional[float] = Field(None, description="Maximum possible score")
    error: Optional[str] = Field(None, description="Error message if failed")


class SommelierOutput(BaseModel):
    sommelier_name: str = Field(..., description="Name of the sommelier agent")
    score: int = Field(..., ge=0, le=100, description="Score from 0 to 100")
    summary: str = Field(..., description="Brief summary of the evaluation")
    recommendations: List[str] = Field(
        default_factory=list, description="List of recommendations"
    )
    technique_details: List[TechniqueDetail] = Field(
        default_factory=list, description="Detailed technique results"
    )


class FinalEvaluation(BaseModel):
    """Model for final evaluation results.

    This model contains the aggregated results from all sommeliers.
    """

    overall_score: int = Field(
        ..., ge=0, le=100, description="Overall score from 0 to 100"
    )
    rating_tier: RatingTier = Field(..., description="Wine-themed rating tier")
    sommelier_outputs: List[SommelierOutput] = Field(
        ..., description="List of individual sommelier outputs"
    )
    summary: str = Field(..., description="Final summary of the evaluation")


class ResultInDB(BaseModel):
    """Model for result data stored in the database."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(..., alias="_id", description="MongoDB document ID")
    evaluation_id: str = Field(..., description="Reference to the evaluation")
    final_evaluation: FinalEvaluation = Field(
        ..., description="Final evaluation results"
    )
    created_at: datetime = Field(..., description="Result creation timestamp")


class ResultResponse(BaseModel):
    """Model for result data in API responses."""

    evaluation_id: str = Field(..., description="Reference to the evaluation")
    final_evaluation: FinalEvaluation = Field(
        ..., description="Final evaluation results"
    )
    created_at: datetime = Field(..., description="Result creation timestamp")
