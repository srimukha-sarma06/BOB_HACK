from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class AnalyzeRequest(BaseModel):
    repo_link: Optional[str] = None
    repo_url: Optional[str] = None
    repo_name: Optional[str] = None
    repo_description: Optional[str] = ""


class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=2)
    top_k: int = Field(5, ge=1, le=20)


class ArtifactRequest(BaseModel):
    artifact_type: str = Field(..., min_length=2)
    content: str = ""


class ArtifactResponse(BaseModel):
    repo_id: str
    artifacts: Dict[str, str]


class HealthResponse(BaseModel):
    status: str
    vector_backend: str
