from app.core.config import settings


def _eval_payload():
    return {"prompt": "hello", "enqueue_async": False}


def test_open_by_default(client):
    # require_api_key defaults to False -> no key needed.
    resp = client.post("/evaluations", json=_eval_payload())
    assert resp.status_code == 200


def test_health_always_open(client, monkeypatch):
    monkeypatch.setattr(settings, "require_api_key", True)
    assert client.get("/health").status_code == 200
    assert client.get("/").status_code == 200


def test_enforced_when_required(client, monkeypatch):
    monkeypatch.setattr(settings, "require_api_key", True)
    resp = client.post("/evaluations", json=_eval_payload())
    assert resp.status_code == 401


def test_admin_key_grants_access(client, monkeypatch):
    monkeypatch.setattr(settings, "require_api_key", True)
    monkeypatch.setattr(settings, "admin_api_key", "admin-secret")
    resp = client.post("/evaluations", json=_eval_payload(), headers={"X-API-Key": "admin-secret"})
    assert resp.status_code == 200


def test_invalid_key_rejected(client, monkeypatch):
    monkeypatch.setattr(settings, "require_api_key", True)
    monkeypatch.setattr(settings, "admin_api_key", "admin-secret")
    resp = client.post("/evaluations", json=_eval_payload(), headers={"X-API-Key": "nope"})
    assert resp.status_code == 401


def test_key_management_requires_admin(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_api_key", "admin-secret")
    # No key -> rejected.
    assert client.post("/auth/keys", json={"name": "ci"}).status_code == 401
    # Wrong key -> rejected.
    assert client.post("/auth/keys", json={"name": "ci"}, headers={"X-API-Key": "wrong"}).status_code == 401


def test_create_then_use_api_key(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_api_key", "admin-secret")

    created = client.post(
        "/auth/keys", json={"name": "ci-runner"}, headers={"X-API-Key": "admin-secret"}
    )
    assert created.status_code == 200
    body = created.json()
    assert body["api_key"].startswith("tgk_")
    assert body["prefix"].startswith("tgk_")
    new_key = body["api_key"]

    # Now require auth and call a protected endpoint with the freshly minted key.
    monkeypatch.setattr(settings, "require_api_key", True)
    resp = client.post(
        "/evaluations", json=_eval_payload(), headers={"Authorization": f"Bearer {new_key}"}
    )
    assert resp.status_code == 200


def test_revoked_key_is_rejected(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_api_key", "admin-secret")
    created = client.post(
        "/auth/keys", json={"name": "temp"}, headers={"X-API-Key": "admin-secret"}
    ).json()
    key_id = created["id"]
    new_key = created["api_key"]

    revoke = client.delete(f"/auth/keys/{key_id}", headers={"X-API-Key": "admin-secret"})
    assert revoke.status_code == 200

    monkeypatch.setattr(settings, "require_api_key", True)
    resp = client.post(
        "/evaluations", json=_eval_payload(), headers={"Authorization": f"Bearer {new_key}"}
    )
    assert resp.status_code == 401


def test_list_keys_returns_no_secrets(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_api_key", "admin-secret")
    client.post("/auth/keys", json={"name": "k1"}, headers={"X-API-Key": "admin-secret"})
    listed = client.get("/auth/keys", headers={"X-API-Key": "admin-secret"})
    assert listed.status_code == 200
    rows = listed.json()
    assert len(rows) >= 1
    assert all("api_key" not in row and "key_hash" not in row for row in rows)
