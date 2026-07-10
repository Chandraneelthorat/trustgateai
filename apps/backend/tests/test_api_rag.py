def test_faithfulness_endpoint_returns_bounded_result(client):
    resp = client.post(
        "/rag/faithfulness",
        json={
            "question": "Summarize renewal terms?",
            "context": "Renews for $2500/month through 2030.",
            "answer": "There is no renewal language.",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    # score may be null when RAGAS is unavailable; degraded flag communicates that.
    assert "degraded" in data
    assert "meta" in data
    assert 0.0 <= data["meta"]["score_risk"] <= 1.0
