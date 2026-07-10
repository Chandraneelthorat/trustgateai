from app.services import policy_engine
from app.services.policy_engine import FAIL, PASS, WARN


def _evaluate(risk, severities):
    return policy_engine.evaluate(
        risk_score=risk,
        finding_severities=severities,
        fail_threshold=67.0,
        warn_threshold=34.0,
    )


def test_low_risk_no_findings_passes():
    v = _evaluate(10.0, [])
    assert v.verdict == PASS
    assert v.reasons


def test_high_risk_score_fails():
    v = _evaluate(80.0, [])
    assert v.verdict == FAIL
    assert any("fail threshold" in r for r in v.reasons)


def test_high_severity_finding_fails_even_at_low_risk():
    v = _evaluate(5.0, ["high"])
    assert v.verdict == FAIL
    assert any("high-severity" in r for r in v.reasons)


def test_medium_risk_score_warns():
    v = _evaluate(40.0, [])
    assert v.verdict == WARN


def test_medium_severity_finding_warns_at_low_risk():
    v = _evaluate(5.0, ["medium"])
    assert v.verdict == WARN
    assert any("medium-severity" in r for r in v.reasons)


def test_fail_takes_precedence_over_warn():
    v = _evaluate(90.0, ["medium"])
    assert v.verdict == FAIL


def test_thresholds_echoed_in_result():
    v = _evaluate(10.0, [])
    assert v.thresholds == {"fail": 67.0, "warn": 34.0}


def test_none_risk_treated_as_zero():
    v = _evaluate(None, [])
    assert v.verdict == PASS


def test_severity_case_insensitive():
    assert _evaluate(5.0, ["HIGH"]).verdict == FAIL
