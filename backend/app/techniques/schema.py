from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class TechniqueCategory(str, Enum):
    AROMA = "aroma"
    PALATE = "palate"
    BODY = "body"
    FINISH = "finish"
    BALANCE = "balance"
    VINTAGE = "vintage"
    TERROIR = "terroir"
    CELLAR = "cellar"


class EvaluationDimension(str, Enum):
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    A4 = "A4"
    B1 = "B1"
    B2 = "B2"
    B3 = "B3"
    B4 = "B4"
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"
    C4 = "C4"
    C5 = "C5"
    D1 = "D1"
    D2 = "D2"
    D3 = "D3"
    D4 = "D4"


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
    category: TechniqueCategory
    applicable_hats: List[str] = Field(default_factory=list, alias="applicableHats")
    evaluation_dimensions: List[EvaluationDimension] = Field(
        default_factory=list, alias="evaluationDimensions"
    )
    description: str = Field(default="")
    prompt_template: str = Field(alias="promptTemplate")
    scoring: ScoringCriteria = Field(default_factory=ScoringCriteria)
    output_schema: Dict[str, Any] = Field(default_factory=dict, alias="outputSchema")
    metadata: TechniqueMetadata = Field(default_factory=TechniqueMetadata)
    fairthon_source: Optional[str] = Field(default=None, alias="requiredSources")
