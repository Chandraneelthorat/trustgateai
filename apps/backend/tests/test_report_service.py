import json
import uuid

from app.services import report_service


def test_json_snapshot_is_valid_and_complete():
    run_id = uuid.uuid4()
    content = report_service.build_json_snapshot(
        run_id=run_id,
        status="completed",
        risk_score=42.5,
        findings=[{"category": "pii", "severity": "medium"}],
        trace=[{"step_index": 0, "name": "attack_generator"}],
        degraded_flags={"ragas": "unavailable"},
    )
    parsed = json.loads(content)
    assert parsed["evaluation_run_id"] == str(run_id)
    assert parsed["status"] == "completed"
    assert parsed["risk_score"] == 42.5
    assert parsed["findings"][0]["category"] == "pii"
    assert parsed["metrics"]["ragas"] == "unavailable"
    assert "generated_at" in parsed


def test_html_stub_contains_summary_pairs():
    html = report_service.html_stub({"run_id": "abc", "risk_score": 10})
    assert "<html>" in html
    assert "run_id" in html
    assert "risk_score" in html
