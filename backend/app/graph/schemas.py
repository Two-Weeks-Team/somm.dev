"""Pydantic schemas for graph nodes."""

from pydantic import BaseModel, Field
from typing import List


class SommelierOutput(BaseModel):
    """Output schema for individual sommelier evaluations."""

    score: int = Field(ge=0, le=100, description="Score from 0 to 100")
    notes: str = Field(description="Tasting notes using wine metaphor style")
    confidence: float = Field(
        ge=0.0, le=1.0, description="Confidence level of the evaluation"
    )
    techniques_used: List[str] = Field(
        default_factory=list, description="Analysis techniques used"
    )
    aspects: dict = Field(default_factory=dict, description="Detailed aspect scores")


class FinalEvaluation(BaseModel):
    """Final synthesis schema for the master sommelier."""

    total_score: int = Field(ge=0, le=100, description="Overall score from 0 to 100")
    rating: str = Field(
        description="Rating tier (Legendary, Grand Cru, Premier Cru, etc.)"
    )
    verdict: str = Field(description="Final tasting notes and summary")
    pairing_suggestions: List[str] = Field(
        default_factory=list, description="Suggested code pairing recommendations"
    )
    cellaring_advice: str = Field(
        description="Maintenance and improvement recommendations"
    )
    aspect_scores: dict = Field(
        default_factory=dict, description="Detailed breakdown of aspect scores"
    )
