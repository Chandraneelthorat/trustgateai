from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, evaluations, health, prompts, rag, reports
from app.api.deps import require_auth
from app.core.config import settings

app = FastAPI(title="TrustGateAI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
async def root() -> dict:
    return {"status": "ok", "kind": "trustgateai"}


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(evaluations.router, dependencies=[Depends(require_auth)])
app.include_router(prompts.router, dependencies=[Depends(require_auth)])
app.include_router(rag.router, dependencies=[Depends(require_auth)])
app.include_router(reports.router, dependencies=[Depends(require_auth)])
