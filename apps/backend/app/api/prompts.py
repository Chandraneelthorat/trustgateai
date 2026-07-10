from fastapi import APIRouter

from app.agents import attack_generator_agent
from app.schemas.prompt import PromptAnalyzeRequest, PromptAnalyzeResponse
from app.services import injection_service

router = APIRouter(prefix="/prompts", tags=["prompts"])


@router.post("/analyze", response_model=PromptAnalyzeResponse)
async def analyze_prompt(body: PromptAnalyzeRequest) -> PromptAnalyzeResponse:
    scan = injection_service.scan_prompt(body.prompt)
    variants: list[str] = []
    if body.include_attack_variants:
        variants = attack_generator_agent.invoke(body.prompt)["variants"]

    response = PromptAnalyzeResponse(
        injection_signals={"matched": scan.matched, "pattern_ids": list(scan.pattern_ids)},
        attack_variants=variants,
    )
    return response
