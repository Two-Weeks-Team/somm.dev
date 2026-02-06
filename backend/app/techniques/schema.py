from typing import Any, Dict, Literal

from pydantic import BaseModel


class TechniqueDefinition(BaseModel):
    id: str
    category: str
    input_source: Literal["github", "pdf", "both"]
    scoring: Dict[str, Any]
    output_schema: Dict[str, Any]
    prompt_template: str
