"""Simple report payloads (JSON/HTML stub)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone


def build_json_snapshot(
    *,
    run_id: uuid.UUID,
    status: str,
    risk_score: float | None,
    findings: list[dict],
    trace: list[dict],
    degraded_flags: dict,
    verdict: str | None = None,
) -> str:
    blob = {
        "evaluation_run_id": str(run_id),
        "status": status,
        "risk_score": risk_score,
        "verdict": verdict,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "findings": findings,
        "trace": trace,
        "metrics": degraded_flags,
    }
    return json.dumps(blob, indent=2)


def html_stub(summary: dict) -> str:
    pairs = "".join(f"<li><strong>{k}</strong>: {v}</li>" for k, v in summary.items())
    return (
        "<!doctype html><html><meta charset=utf-8><title>TrustGate Report</title><body>"
        f"<h1>TrustGate evaluation</h1><ul>{pairs}</ul></body></html>"
    )
