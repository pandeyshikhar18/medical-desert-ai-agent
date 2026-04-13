from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Evidence(BaseModel):
    row_index: int
    source_columns: List[str] = Field(default_factory=list)
    snippet: str

class ExtractedFacility(BaseModel):
    row_index: int
    name: Optional[str] = None
    facility_type_id: Optional[str] = None
    operator_type_id: Optional[str] = None
    specialties: List[str] = Field(default_factory=list)

    procedures: List[str] = Field(default_factory=list)
    equipment: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)

    number_doctors: Optional[int] = None
    capacity: Optional[int] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    medical_desert_score: int = 0
    suspicious_claims: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()