from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.models import EvaluationRun, Report
from app.schemas.evaluation import ReportExport
from app.services.report_service import build_json_snapshot

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/export")
async def export_report(
    payload: ReportExport,
    db: Session = Depends(get_db),
) -> dict:
    stmt = (
        select(EvaluationRun)
        .where(EvaluationRun.id == payload.evaluation_run_id)
        .options(selectinload(EvaluationRun.findings), selectinload(EvaluationRun.trace_steps))
    )
    run = db.execute(stmt).scalar_one_or_none()
    if run is None:
        raise HTTPException(status_code=404, detail="evaluation run not found")

    findings = sorted(run.findings or [], key=lambda f: str(f.title))
    trace = sorted(run.trace_steps or [], key=lambda t: (t.step_index, str(t.name)))
    degraded = dict(run.extra or {})

    serialized = [
        {
            "id": str(f.id),
            "category": f.category,
            "severity": f.severity,
            "title": f.title,
            "detail": f.detail,
            "meta": dict(f.meta or {}),
        }
        for f in findings
    ]
    traced = [
        {
            "step_index": step.step_index,
            "name": step.name,
            "payload": dict(step.payload or {}),
        }
        for step in trace
    ]

    if payload.format == "json":
        content = build_json_snapshot(
            run_id=run.id,
            status=run.status,
            risk_score=run.risk_score,
            findings=serialized,
            trace=traced,
            degraded_flags=degraded,
            verdict=run.verdict,
        )
    elif payload.format == "html":
        summary = {
            "run_id": str(run.id),
            "risk_score": run.risk_score,
            "verdict": run.verdict,
            "findings_count": len(serialized),
        }
        rows = "".join(f"<li>{s}</li>" for s in serialized[:10])
        content = (
            "<html><meta charset=utf-8><title>TrustGate Export</title><body>"
            f"<pre>{summary}</pre><ul>{rows}</ul></body></html>"
        )
    else:
        raise HTTPException(status_code=400, detail="unsupported format")

    report = Report(
        evaluation_run_id=run.id,
        format=payload.format,
        content=content[:200_000],
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "report_id": report.id,
        "evaluation_run_id": run.id,
        "format": payload.format,
        "content_length": len(content),
        "snippet": content[:1000],
    }
