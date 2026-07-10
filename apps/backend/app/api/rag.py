from fastapi import APIRouter

from app.schemas.rag import RagFaithfulnessRequest, RagFaithfulnessResponse
from app.services import rag_faithfulness_service

router = APIRouter(prefix="/rag", tags=["rag"])


@router.post("/faithfulness", response_model=RagFaithfulnessResponse)
async def faithfulness_metric(body: RagFaithfulnessRequest) -> RagFaithfulnessResponse:
    res = rag_faithfulness_service.analyze(
        question=body.question,
        context=body.context,
        answer=body.answer,
    )
    degraded = bool(res.degraded_reason)
    note = (
        "RAGAS unavailable or degraded; consult meta + risk score only."
        if degraded
        else None
    )
    return RagFaithfulnessResponse(
        score=res.raw_faithfulness,
        degraded=degraded,
        note=note,
        meta={"score_risk": res.score_risk, "detail": res.degraded_reason},
    )
