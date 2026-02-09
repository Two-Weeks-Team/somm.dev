"""API routes for evaluating techniques.

This module provides endpoints for listing and inspecting the 75 evaluation techniques.
"""

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from app.techniques.registry import get_registry, TechniqueRegistry
from app.techniques.mappings import TECHNIQUE_PRIORITY, Priority
from app.techniques.schema import TechniqueCategory, TechniqueDefinition
from app.criteria.technique_mappings import (
    get_techniques_for_mode,
    TECHNIQUE_TO_ITEMS,
)

router = APIRouter(prefix="/techniques", tags=["techniques"])

VALID_CATEGORIES = {cat.value for cat in TechniqueCategory}
VALID_HATS = {"white", "red", "black", "yellow", "green", "blue"}


class TechniqueSummary(BaseModel):
    """Summary response for a technique."""

    id: str
    name: str
    category: TechniqueCategory
    applicable_hats: List[str]
    priority: str
    fairthon_source: Optional[str] = None


class TechniqueDetail(BaseModel):
    """Full detail response for a technique."""

    id: str
    name: str
    category: TechniqueCategory
    applicable_hats: List[str]
    evaluation_dimensions: List[str]
    description: str
    prompt_template: str
    scoring: Dict[str, Any]
    output_schema: Dict[str, Any]
    metadata: Dict[str, Any]
    fairthon_source: Optional[str] = None
    bmad_items: List[str]


class TechniqueStats(BaseModel):
    """Statistics response for all techniques."""

    total: int
    by_category: Dict[str, int]
    by_priority: Dict[str, int]
    by_mode: Dict[str, int]


def _get_priority_str(technique_id: str) -> str:
    """Get priority string for a technique ID."""
    priority = TECHNIQUE_PRIORITY.get(technique_id, Priority.P2)
    return f"P{priority.value}"


def _technique_to_summary(tech: TechniqueDefinition) -> TechniqueSummary:
    """Convert TechniqueDefinition to TechniqueSummary."""
    return TechniqueSummary(
        id=tech.id,
        name=tech.name,
        category=tech.category,
        applicable_hats=tech.applicable_hats,
        priority=_get_priority_str(tech.id),
        fairthon_source=tech.fairthon_source,
    )


def _technique_to_detail(tech: TechniqueDefinition) -> TechniqueDetail:
    """Convert TechniqueDefinition to TechniqueDetail with BMAD items."""
    return TechniqueDetail(
        id=tech.id,
        name=tech.name,
        category=tech.category,
        applicable_hats=tech.applicable_hats,
        evaluation_dimensions=[d.value for d in tech.evaluation_dimensions],
        description=tech.description,
        prompt_template=tech.prompt_template,
        scoring=tech.scoring.model_dump(),
        output_schema=tech.output_schema,
        metadata=tech.metadata.model_dump(),
        fairthon_source=tech.fairthon_source,
        bmad_items=TECHNIQUE_TO_ITEMS.get(tech.id, []),
    )


@router.get("/stats", response_model=TechniqueStats)
async def get_techniques_stats() -> TechniqueStats:
    """Get aggregated statistics about all techniques.

    Returns:
        Statistics including total count, breakdown by category, priority, and mode.
    """
    registry: TechniqueRegistry = get_registry()

    total = registry.count()
    by_category = registry.count_by_category()

    by_priority: Dict[str, int] = {"P0": 0, "P1": 0, "P2": 0}
    for tech in registry.list_techniques():
        priority_str = _get_priority_str(tech.id)
        by_priority[priority_str] = by_priority.get(priority_str, 0) + 1

    by_mode = {
        "full_techniques": len(get_techniques_for_mode("full_techniques")),
        "grand_tasting": len(get_techniques_for_mode("grand_tasting")),
        "six_sommeliers": len(get_techniques_for_mode("six_sommeliers")),
    }

    return TechniqueStats(
        total=total,
        by_category=by_category,
        by_priority=by_priority,
        by_mode=by_mode,
    )


@router.get("", response_model=List[TechniqueSummary])
async def list_techniques(
    category: Optional[str] = Query(
        None, description="Filter by category (e.g., aroma, palate)"
    ),
    hat: Optional[str] = Query(
        None, description="Filter by applicable hat (e.g., white, red, black)"
    ),
    mode: Optional[str] = Query(
        None,
        description="Filter by mode: six_sommeliers, grand_tasting, or full_techniques",
    ),
) -> List[TechniqueSummary]:
    """List all techniques with optional filtering.

    Query Parameters:
        category: Filter by category (aroma, palate, body, finish, balance, vintage, terroir, cellar)
        hat: Filter by applicable hat color
        mode: Filter by evaluation mode (six_sommeliers, grand_tasting, full_techniques)

    Returns:
        List of technique summaries matching the filters.
    """
    registry: TechniqueRegistry = get_registry()

    if category and category not in VALID_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category: {category}. Must be one of: {', '.join(sorted(VALID_CATEGORIES))}",
        )

    if hat and hat not in VALID_HATS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid hat: {hat}. Must be one of: {', '.join(sorted(VALID_HATS))}",
        )

    if mode:
        if mode not in ("six_sommeliers", "grand_tasting", "full_techniques"):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid mode: {mode}. Must be one of: six_sommeliers, grand_tasting, full_techniques",
            )
        mode_technique_ids = set(get_techniques_for_mode(mode))
        techniques = [
            tech for tech in registry.list_techniques() if tech.id in mode_technique_ids
        ]
    else:
        techniques = registry.list_techniques()

    if category:
        techniques = [tech for tech in techniques if tech.category.value == category]

    if hat:
        techniques = [tech for tech in techniques if hat in tech.applicable_hats]

    return [_technique_to_summary(tech) for tech in techniques]


@router.get("/{technique_id}", response_model=TechniqueDetail)
async def get_technique_detail(technique_id: str) -> TechniqueDetail:
    """Get detailed information about a specific technique.

    Args:
        technique_id: The unique identifier for the technique.

    Returns:
        Full technique definition including BMAD item mappings.

    Raises:
        HTTPException: If the technique is not found (404).
    """
    registry: TechniqueRegistry = get_registry()
    tech = registry.get_technique(technique_id)

    if tech is None:
        raise HTTPException(
            status_code=404, detail=f"Technique not found: '{technique_id}'"
        )

    return _technique_to_detail(tech)
