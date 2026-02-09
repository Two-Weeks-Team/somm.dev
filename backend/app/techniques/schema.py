from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ScoringCriteria(BaseModel):
    min: int = Field(default=1)
    max: int = Field(default=5)
    criteria: Dict[int, str] = Field(default_factory=dict)
    weight: float = Field(default=1.0)


class TechniqueMetadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    complexity: Literal["low", "medium", "high"] = Field(default="medium")
    estimated_tokens: int = Field(default=500, alias="estimatedTokens")
    requires_web_search: bool = Field(default=False, alias="requiresWebSearch")
    requires_rag: bool = Field(default=False, alias="requiresRAG")
    source: Optional[str] = None


class TechniqueDefinition(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    category: str
    applicable_hats: List[str] = Field(default_factory=list, alias="applicableHats")
    evaluation_dimensions: List[str] = Field(
        default_factory=list, alias="evaluationDimensions"
    )
    description: str = Field(default="")
    prompt_template: str = Field(alias="promptTemplate")
    scoring: ScoringCriteria = Field(default_factory=ScoringCriteria)
    output_schema: Dict[str, Any] = Field(default_factory=dict, alias="outputSchema")
    metadata: TechniqueMetadata = Field(default_factory=TechniqueMetadata)
    fairthon_source: Optional[str] = Field(default=None, alias="requiredSources")
