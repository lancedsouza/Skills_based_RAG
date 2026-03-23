from pydantic import BaseModel
from typing import List


class SkillResponse(BaseModel):
    id: int
    name: str
    similarity: float


class SuggestResponse(BaseModel):
    suggestions: List[SkillResponse]