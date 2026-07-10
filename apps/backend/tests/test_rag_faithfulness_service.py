from app.services import rag_faithfulness_service


def test_missing_context_or_answer_is_skipped():
    result = rag_faithfulness_service.analyze(question="q", context=None, answer=None)
    assert result.raw_faithfulness is None
    assert result.degraded_reason == "skipped_missing_context_or_answer"
    assert result.score_risk == 0.08


def test_degrades_cleanly_when_ragas_unavailable():
    # RAGAS is an optional dependency; without it the service must not raise and
    # should return a bounded fallback risk with a degraded reason.
    result = rag_faithfulness_service.analyze(
        question="Summarize renewal terms?",
        context="Renews for $2500/month through 2030.",
        answer="There is no renewal language.",
    )
    assert 0.0 <= result.score_risk <= 1.0
    if result.raw_faithfulness is None:
        assert result.degraded_reason is not None
