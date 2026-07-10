"""Hallucination / groundedness proxies."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass


@dataclass
class HallucinationResult:
    heuristic_score: float
    deepeval_score: float | None = None
    degraded_reason: str | None = None


def _overlap_score(context: str, response: str) -> float:
    if not response.strip():
        return 0.35
    if not context.strip():
        return 0.5

    ct = set(re.findall(r"[a-z0-9']{3,}", context.lower()))
    rs = set(re.findall(r"[a-z0-9']{3,}", response.lower()))
    if not rs:
        return 0.2
    if not ct:
        return 0.6
    jacc = len(ct & rs) / max(1, len(ct | rs))
    return float(max(0.0, min(1.0, 1.2 * (1.0 - jacc))))


def optional_deepeval(context: str, response: str) -> tuple[float | None, str | None]:
    """Best-effort DeepEval measure; skips unless optional deps + OPENAI_API_KEY."""

    if not os.getenv("OPENAI_API_KEY"):
        return None, "deepeval_skipped_no_openai_api_key"

    try:
        from deepeval.metrics import AnswerRelevancyMetric  # noqa: WPS433
        from deepeval.test_case import LLMTestCase

        test_case = LLMTestCase(
            input=context[:4000],
            actual_output=response[:4000],
        )
        metric = AnswerRelevancyMetric(threshold=0.5)
        metric.measure(test_case)
        raw = getattr(metric, "score", None)
        if raw is None:
            return None, "deepeval_empty_score"
        danger = float(max(0.0, min(1.0, 1.0 - float(raw))))
        return danger, None
    except Exception as exc:
        return None, f"deepeval_unavailable: {exc}"


def analyze(
    *,
    prompt: str,
    context: str | None,
    response: str | None,
    use_deepeval: bool = False,
) -> HallucinationResult:
    prompt_len_boost = float(max(0.0, min(0.55, len(prompt) / 800.0)))
    if not response:
        heuristic_score = prompt_len_boost * 0.5 + 0.15
    else:
        heuristic_score = _overlap_score(context or "", response)

    deepeval_danger: float | None = None
    degraded: str | None = None

    if use_deepeval and context and response:
        deepeval_danger, degraded = optional_deepeval(context, response)

    blended = heuristic_score
    if deepeval_danger is not None:
        blended = float(max(blended, deepeval_danger * 0.85))

    return HallucinationResult(
        heuristic_score=blended,
        deepeval_score=deepeval_danger,
        degraded_reason=degraded,
    )
