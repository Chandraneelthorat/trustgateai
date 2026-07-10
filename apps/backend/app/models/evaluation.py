from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.db.base import Base

# Cross-dialect column types: native UUID + JSONB on PostgreSQL (unchanged in
# production), portable CHAR/JSON on SQLite so the suite can run without Postgres.
PGUUID = Uuid(as_uuid=True)
JSONB_OR_JSON = JSON().with_variant(JSONB(), "postgresql")


class EvaluationRun(Base):
    """Single evaluation sweep over (prompt [, context [, response]]).

    Policy boundaries: callers must not persist raw secrets; callers redact upstream.
    """

    __tablename__ = "evaluation_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID, primary_key=True, default=uuid.uuid4
    )
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    context: Mapped[str | None] = mapped_column(Text, nullable=True)
    response: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    verdict: Mapped[str | None] = mapped_column(String(16), nullable=True, index=True)
    extra: Mapped[dict[str, Any]] = mapped_column(JSONB_OR_JSON, default=lambda: {})
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    findings: Mapped[list[Finding]] = relationship(
        back_populates="evaluation_run", cascade="all, delete-orphan"
    )
    trace_steps: Mapped[list[TraceStep]] = relationship(
        back_populates="evaluation_run", cascade="all, delete-orphan"
    )
    reports: Mapped[list[Report]] = relationship(
        back_populates="evaluation_run", cascade="all, delete-orphan"
    )


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID, primary_key=True, default=uuid.uuid4
    )
    evaluation_run_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID,
        ForeignKey("evaluation_runs.id", ondelete="CASCADE"),
        index=True,
    )
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict[str, Any]] = mapped_column(JSONB_OR_JSON, default=lambda: {})

    evaluation_run: Mapped[EvaluationRun] = relationship(back_populates="findings")


class TraceStep(Base):
    __tablename__ = "trace_steps"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID, primary_key=True, default=uuid.uuid4
    )
    evaluation_run_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID,
        ForeignKey("evaluation_runs.id", ondelete="CASCADE"),
        index=True,
    )
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB_OR_JSON, default=lambda: {})

    evaluation_run: Mapped[EvaluationRun] = relationship(back_populates="trace_steps")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        PGUUID, primary_key=True, default=uuid.uuid4
    )
    evaluation_run_id: Mapped[uuid.UUID] = mapped_column(
        PGUUID,
        ForeignKey("evaluation_runs.id", ondelete="CASCADE"),
        index=True,
    )
    format: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), default=lambda: datetime.now(timezone.utc)
    )

    evaluation_run: Mapped[EvaluationRun] = relationship(back_populates="reports")
