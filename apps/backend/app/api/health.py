from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "utc": datetime.now(timezone.utc).isoformat(),
        "service": "trustgateai-api",
    }
