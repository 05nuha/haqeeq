import hashlib
import hmac
import json

import pytest

from test_api import SCAM, FakeResp, env, client  # noqa: F401  (reuse fixtures)
from _lib import app as appmod


@pytest.fixture
def sent(monkeypatch):
    out = []
    monkeypatch.setattr(appmod, "meta_send", lambda to, text: out.append((to, text)))
    monkeypatch.setenv("META_VERIFY_TOKEN", "vt")
    return out


def _payload(msg):
    return {"entry": [{"changes": [{"value": {"messages": [msg]}}]}]}


def test_verify_handshake(client, sent):
    r = client.get("/api/meta?hub.mode=subscribe&hub.verify_token=vt&hub.challenge=123")
    assert r.status_code == 200 and r.get_data(as_text=True) == "123"
    assert client.get("/api/meta?hub.mode=subscribe&hub.verify_token=no&hub.challenge=1").status_code == 403


def test_text_message(client, env, sent):
    r = client.post("/api/meta", json=_payload({"from": "971501234567", "type": "text",
                                                 "text": {"body": "عاجل غرامة"}}))
    assert r.status_code == 200
    assert sent == [("971501234567", SCAM)]
    row = env["insert"][0][1]
    assert row["sender_masked"] == "+97150•••567" and row["seeded"] is False


def test_image_message(client, env, sent, monkeypatch):
    monkeypatch.setattr(appmod, "_meta_media", lambda mid: b"img")
    client.post("/api/meta", json=_payload({"from": "971501234567", "type": "image",
                                             "image": {"id": "M1", "mime_type": "image/jpeg"}}))
    assert sent == [("971501234567", "OK-genuine")]
    assert env["upload"] and env["insert"][0][1]["kind"] == "image"


def test_status_callbacks_ignored(client, sent):
    r = client.post("/api/meta", json={"entry": [{"changes": [{"value": {"statuses": [{"id": "x"}]}}]}]})
    assert r.status_code == 200 and sent == []


def test_app_secret_signature(client, sent, monkeypatch):
    monkeypatch.setenv("META_APP_SECRET", "s3")
    body = json.dumps(_payload({"from": "9715", "type": "text", "text": {"body": "hi"}})).encode()
    assert client.post("/api/meta", data=body, content_type="application/json",
                       headers={"X-Hub-Signature-256": "sha256=bad"}).status_code == 403
    good = "sha256=" + hmac.new(b"s3", body, hashlib.sha256).hexdigest()
    assert client.post("/api/meta", data=body, content_type="application/json",
                       headers={"X-Hub-Signature-256": good}).status_code == 200
