from pydantic import BaseModel, Field


class RagFaithfulnessRequest(BaseModel):
    question: str = ""
    context: str
    answer: str


class RagFaithfulnessResponse(BaseModel):
    score: float | None = None
    degraded: bool = False
    note: str | None = None
    meta: dict = Field(default_factory=dict)
