"""Turn raw risk signals into a release-gate verdict.

The composite ``risk_score`` (0–100) and the set of finding severities are mapped
to one of three verdicts:

- ``pass``  — within policy thresholds, safe to ship
- ``warn``  — elevated risk or medium-severity findings; review recommended
- ``fail``  — over the fail threshold or a high-severity finding; block release

Thresholds are injected by the caller (from settings today, per-tenant policy
packs later), so this module stays pure and easy to test.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

PASS = "pass"
WARN = "warn"
FAIL = "fail"


@dataclass
class PolicyVerdict:
    verdict: str
    reasons: list[str] = field(default_factory=list)
    thresholds: dict[str, float] = field(default_factory=dict)


def evaluate(
    *,
    risk_score: float | None,
    finding_severities: Iterable[str],
    fail_threshold: float,
    warn_threshold: float,
) -> PolicyVerdict:
    score = float(risk_score or 0.0)
    severities = {s.lower() for s in finding_severities}
    thresholds = {"fail": float(fail_threshold), "warn": float(warn_threshold)}

    has_high = "high" in severities
    has_medium = "medium" in severities

    reasons: list[str] = []

    if score >= fail_threshold:
        reasons.append(f"risk score {score:.1f} at or above fail threshold {fail_threshold:.0f}")
    if has_high:
        reasons.append("high-severity finding present")

    if reasons:
        return PolicyVerdict(verdict=FAIL, reasons=reasons, thresholds=thresholds)

    if score >= warn_threshold:
        reasons.append(f"risk score {score:.1f} at or above warn threshold {warn_threshold:.0f}")
    if has_medium:
        reasons.append("medium-severity finding present")

    if reasons:
        return PolicyVerdict(verdict=WARN, reasons=reasons, thresholds=thresholds)

    return PolicyVerdict(
        verdict=PASS,
        reasons=[f"risk score {score:.1f} below warn threshold {warn_threshold:.0f}; no blocking findings"],
        thresholds=thresholds,
    )
