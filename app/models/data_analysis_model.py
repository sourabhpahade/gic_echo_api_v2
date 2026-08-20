from pydantic import BaseModel
from typing import Any
from dataclasses import field

class AnalysisResult(BaseModel):
    summary: str
    warnings: list[str] = field(default_factory=list)
    digest: str = ""
    profile: dict[str, Any] = field(default_factory=dict)
    size_tier: str = ""
