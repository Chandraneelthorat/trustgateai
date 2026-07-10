from app.services import hallucination_service


def test_missing_response_uses_prompt_length_boost():
    result = hallucination_service.analyze(prompt="short", context=None, response=None)
    assert 0.0 <= result.heuristic_score <= 1.0
    assert result.deepeval_score is None


def test_well_grounded_response_scores_low_risk():
    context = "The Eiffel Tower is located in Paris, France and was completed in 1889."
    response = "The Eiffel Tower is in Paris, France, completed in 1889."
    result = hallucination_service.analyze(prompt="Where is it?", context=context, response=response)
    assert result.heuristic_score < 0.5


def test_ungrounded_response_scores_higher_risk():
    context = "The Eiffel Tower is located in Paris, France."
    grounded = hallucination_service.analyze(
        prompt="q", context=context, response="The Eiffel Tower is in Paris France."
    )
    ungrounded = hallucination_service.analyze(
        prompt="q", context=context, response="Quantum bananas orbit the purple moon."
    )
    assert ungrounded.heuristic_score > grounded.heuristic_score


def test_deepeval_skipped_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = hallucination_service.analyze(
        prompt="q",
        context="some context here",
        response="some answer here",
        use_deepeval=True,
    )
    assert result.deepeval_score is None
    assert result.degraded_reason == "deepeval_skipped_no_openai_api_key"


def test_score_is_always_bounded():
    result = hallucination_service.analyze(
        prompt="x" * 5000, context="", response=None
    )
    assert 0.0 <= result.heuristic_score <= 1.0
