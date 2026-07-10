"""Optional RAGAS faithfulness; degrades cleanly without keys/models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RagFaithfulnessResult:
    score_risk: float  # higher = less trustworthy / weaker faithfulness
    raw_faithfulness: float | None
    degraded_reason: str | None


def _try_ragas_faithfulness(
    *,
    question: str,
    context: str,
    answer: str,
) -> RagFaithfulnessResult:
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import faithfulness

        ds = Dataset.from_dict(
            {
                "question": [question[:2000]],
                "contexts": [[context[:8000]]],
                "answer": [answer[:4000]],
            }
        )

        scored = evaluate(ds, metrics=[faithfulness]).to_pandas()
        fv = float(scored["faithfulness"].iloc[0])
        inverted = float(max(0.0, min(1.0, 1.0 - fv)))
        return RagFaithfulnessResult(
            score_risk=inverted, raw_faithfulness=fv, degraded_reason=None
        )
    except Exception as exc:
        return RagFaithfulnessResult(
            score_risk=0.35,
            raw_faithfulness=None,
            degraded_reason=f"ragas_unavailable_or_misconfigured: {exc}",
        )


def analyze(
    *,
    question: str,
    context: str | None,
    answer: str | None,
) -> RagFaithfulnessResult:
    if not context or not answer:
        return RagFaithfulnessResult(
            score_risk=0.08,
            raw_faithfulness=None,
            degraded_reason="skipped_missing_context_or_answer",
        )
    return _try_ragas_faithfulness(question=question, context=context, answer=answer)
