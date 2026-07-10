from pydantic import BaseModel, Field


class PromptAnalyzeRequest(BaseModel):
    prompt: str
    include_attack_variants: bool = Field(
        default=False,
        description="When true, runs the LangGraph attack generator stub.",
    )


class PromptAnalyzeResponse(BaseModel):
    injection_signals: dict = Field(default_factory=dict)
    attack_variants: list[str] = Field(default_factory=list)
