from __future__ import annotations

import uuid
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.core.config import settings
from app.models import EvaluationRun
from app.schemas.evaluation import EvaluationCreate, EvaluationListItem, EvaluationSummary, FindingRead, TraceStepRead
from app.services import evaluation_service
from app.tasks import run_evaluation

router = APIRouter(prefix="/evaluations", tags=["evaluations"])


def _summary_from(run: EvaluationRun) -> EvaluationSummary:
    findings = sorted(run.findings or [], key=lambda f: str(f.category))
    traces = sorted(run.trace_steps or [], key=lambda t: (t.step_index, str(t.name)))
    return EvaluationSummary(
        id=run.id,
        status=run.status,
        prompt=run.prompt,
        context=run.context,
        response=run.response,
        risk_score=run.risk_score,
        verdict=run.verdict,
        extra=dict(run.extra or {}),
        created_at=run.created_at,
        findings=[
            FindingRead(
                id=f.id,
                category=f.category,
                severity=f.severity,
                title=f.title,
                detail=f.detail,
                meta=dict(f.meta or {}),
            )
            for f in findings
        ],
        trace_steps=[
            TraceStepRead(
                id=t.id,
                step_index=t.step_index,
                name=t.name,
                payload=dict(t.payload or {}),
            )
            for t in traces
        ],
    )


def _run_inline(run_id: uuid.UUID) -> None:
    from app.db.session import SessionLocal

    with SessionLocal() as db:
        evaluation_service.execute_run(db, run_id)


@router.post("", response_model=EvaluationSummary)
async def create_evaluation(
    body: EvaluationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> EvaluationSummary:
    run = EvaluationRun(
        prompt=body.prompt,
        context=body.context,
        response=body.response,
        status="pending",
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    use_celery = body.enqueue_async and not settings.skip_celery_sync
    if use_celery:
        run_evaluation.delay(str(run.id))
    elif body.enqueue_async and settings.skip_celery_sync:
        background_tasks.add_task(_run_inline, run.id)
    else:
        evaluation_service.execute_run(db, run.id)

    db.refresh(run)
    run = db.execute(
        select(EvaluationRun)
        .where(EvaluationRun.id == run.id)
        .options(selectinload(EvaluationRun.findings), selectinload(EvaluationRun.trace_steps))
    ).scalar_one()
    return _summary_from(run)


@router.get("/{run_id}", response_model=EvaluationSummary)
async def get_evaluation(run_id: uuid.UUID, db: Session = Depends(get_db)) -> EvaluationSummary:
    stmt = (
        select(EvaluationRun)
        .where(EvaluationRun.id == run_id)
        .options(selectinload(EvaluationRun.findings), selectinload(EvaluationRun.trace_steps))
    )
    run = db.execute(stmt).scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return _summary_from(run)


@router.get("", response_model=list[EvaluationListItem])
async def list_evaluations(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
) -> list[EvaluationListItem]:
    stmt = select(EvaluationRun).order_by(EvaluationRun.created_at.desc()).limit(limit)
    runs = db.execute(stmt).scalars().all()
    return [
        EvaluationListItem(
            id=r.id,
            status=r.status,
            risk_score=r.risk_score,
            verdict=r.verdict,
            created_at=r.created_at,
        )
        for r in runs
    ]
