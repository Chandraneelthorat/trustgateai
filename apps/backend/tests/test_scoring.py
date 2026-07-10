from app.services import scoring_weights


def test_weights_are_present():
    assert scoring_weights.WEIGHT_INJECTION > 0
    assert scoring_weights.WEIGHT_PII > 0
    assert scoring_weights.WEIGHT_HALLUCINATION_HEURISTIC > 0
    assert scoring_weights.WEIGHT_RAG_FAITHFULNESS > 0


def test_weights_sum_to_one():
    total = (
        scoring_weights.WEIGHT_INJECTION
        + scoring_weights.WEIGHT_PII
        + scoring_weights.WEIGHT_HALLUCINATION_HEURISTIC
        + scoring_weights.WEIGHT_RAG_FAITHFULNESS
    )
    assert round(total, 6) == 1.0


def test_composite_score_stays_within_bounds():
    # All subsystems maxed out should not exceed the 0..1 pre-normalization ceiling.
    composite = (
        scoring_weights.WEIGHT_INJECTION * 1.0
        + scoring_weights.WEIGHT_PII * 1.0
        + scoring_weights.WEIGHT_HALLUCINATION_HEURISTIC * 1.0
        + scoring_weights.WEIGHT_RAG_FAITHFULNESS * 1.0
    )
    assert composite <= 1.0
