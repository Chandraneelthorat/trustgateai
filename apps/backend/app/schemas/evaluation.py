from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class FindingRead(BaseModel):
    id: uuid.UUID
    category: str
    severity: str
    title: str
    detail: str | None = None
    meta: dict = Field(default_factory=dict)


class TraceStepRead(BaseModel):
    id: uuid.UUID
    step_index: int
    name: str
    payload: dict = Field(default_factory=dict)


class EvaluationCreate(BaseModel):
    prompt: str
    context: str | None = None
    response: str | None = None
    enqueue_async: bool = False


class EvaluationSummary(BaseModel):
    id: uuid.UUID
    status: str
    prompt: str
    context: str | None = None
    response: str | None = None
    risk_score: float | None = None
    verdict: str | None = None
    extra: dict = Field(default_factory=dict)
    created_at: datetime
    findings: list[FindingRead] = Field(default_factory=list)
    trace_steps: list[TraceStepRead] = Field(default_factory=list)


class EvaluationListItem(BaseModel):
    id: uuid.UUID
    status: str
    risk_score: float | None
    verdict: str | None = None
    created_at: datetime


class ReportExport(BaseModel):
    evaluation_run_id: uuid.UUID
    format: str = "json"
