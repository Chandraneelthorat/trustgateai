"""Celery tasks backing async evaluation runs."""

from __future__ import annotations

import logging
import uuid

from app.celery_app import celery_app
from app.db.session import SessionLocal
from app.models import EvaluationRun
from app.services import evaluation_service

log = logging.getLogger(__name__)


@celery_app.task(name="evaluation.run_evaluation")
def run_evaluation(run_id: str) -> None:
    rid = uuid.UUID(run_id)
    with SessionLocal() as db:
        try:
            evaluation_service.execute_run(db, rid)
        except Exception:
            log.exception("evaluation failed run_id=%s", run_id)
            db.rollback()
            run = db.get(EvaluationRun, rid)
            if run is not None:
                run.status = "failed"
                run.extra = dict(run.extra or {}) | {"worker_error": True}
                db.add(run)
                db.commit()
            raise
