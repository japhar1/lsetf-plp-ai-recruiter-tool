from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class ExtractedData(BaseModel):
    """Model for structured data extracted from a resume/CV."""
    raw_text: str
    skills: List[str] = Field(default_factory=list)
    education: List[str] = Field(default_factory=list)
    experience: Optional[str] = None

class CandidateProfile(BaseModel):
    """Complete profile of a candidate, ready for ranking."""
    candidate_id: str
    extracted_data: ExtractedData
    score: float = 0.0
    score_breakdown: Dict[str, float] = Field(default_factory=dict)

class RankingCriteria(BaseModel):
    """Weights for different criteria. Easy to tweak."""
    skills_weight: float = 0.5
    experience_weight: float = 0.3
    education_weight: float = 0.2
    required_skills: List[str] = Field(default_factory=list)