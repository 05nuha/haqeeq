import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))

from _lib import app as appmod  # noqa: E402
from _lib import supa  # noqa: E402

SCAM = "🔴 احتيال محتمل — الرسالة تحمل مؤشرات احتيال. تحقق قبل أي إجراء."


class FakeResp:
    content = b"\xff\xd8fakejpeg"
    def __init__(self, ctype="image/jpeg"): pass
    def raise_for_status(self): pass
    def iter_content(self, n): yield self.content
    def __enter__(self): return self
    def __exit__(self, *a): pass


@pytest.fixture
def env(monkeypatch):
    for k, v in {"SKIP_TWILIO_SIG": "1", "DASHBOARD_ADMIN_TOKEN": "sekret", "TWILIO_ACCOUNT_SID": "AC1",
                 "TWILIO_AUTH_TOKEN": "tok", "TWILIO_WHATSAPP_FROM": "whatsapp:+14155238886"}.items():
        monkeypatch.setenv(k, v)
    calls = {"insert": [], "upload": [], "upsert": []}
    monkeypatch.setattr(supa, "cached", lambda t: [])
    monkeypatch.setattr(supa, "upload", lambda p, d, c="": calls["upload"].append(p))
    monkeypatch.setattr(supa, "insert", lambda t, r: calls["insert"].append((t, r)) or [r])
    def up(t, r, on_conflict=None):
        calls["upsert"].append((t, r))
        return [{"id": 7, **r}]
    monkeypatch.setattr(supa, "upsert", up)
    monkeypatch.setattr(appmod, "check_text", lambda t, e=(): {
        "verdict": "scam_risk", "detail": "Scam: x", "ai_reason": None, "ai_used": False})
    monkeypatch.setattr(appmod, "verify_image", lambda b, reg, load, kf=(): {
        "verdict": "genuine", "matched_id": None, "distance": 3, "changed_pct": 0.0, "heat": None,
        "detail": "Matches x"})
    monkeypatch.setattr(appmod, "reply_for", lambda r: SCAM if r["verdict"] == "scam_risk" else "OK-" + r["verdict"])
    monkeypatch.setattr(appmod.requests, "get", lambda *a, **k: FakeResp())
    return calls


@pytest.fixture
def client(env):
    return appmod.app.test_client()


def test_text_scam(client, env):
    r = client.post("/api/whatsapp", data={"From": "whatsapp:+971501234567", "Body": "pay http://x.co now"})
    assert r.status_code == 200 and r.mimetype == "text/xml"
    assert SCAM in r.get_data(as_text=True)
    t, row = env["insert"][0]
    assert row["kind"] == "link" and row["sender_masked"] == "+97150•••567"
    assert row["sender_id"] == 7 and row["seeded"] is False


def test_image(client, env):
    r = client.post("/api/whatsapp", data={"From": "whatsapp:+971501234567", "NumMedia": "1",
                    "MediaUrl0": "https://api.twilio.com/m", "MediaContentType0": "image/jpeg"})
    assert "OK-genuine" in r.get_data(as_text=True)
    assert env["upload"][0].startswith("incoming/") and env["upload"][0].endswith(".jpg")
    assert env["insert"][0][1]["image_path"] == env["upload"][0]
    assert env["insert"][0][1]["kind"] == "image"


def test_audio(client, env):
    r = client.post("/api/whatsapp", data={"From": "whatsapp:+971501234567", "NumMedia": "1",
                    "MediaUrl0": "u", "MediaContentType0": "audio/ogg"})
    assert "قريباً" in r.get_data(as_text=True)
    assert env["insert"][0][1]["kind"] == "text"


def test_db_failure_still_replies(client, env, monkeypatch):
    def boom(*a, **k): raise RuntimeError("db down")
    monkeypatch.setattr(supa, "insert", boom)
    r = client.post("/api/whatsapp", data={"From": "whatsapp:+971501234567", "Body": "hi there win prize"})
    assert r.status_code == 200 and SCAM in r.get_data(as_text=True)


def test_bad_signature(client, monkeypatch):
    monkeypatch.delenv("SKIP_TWILIO_SIG")
    r = client.post("/api/whatsapp", data={"From": "x", "Body": "y"}, headers={"X-Twilio-Signature": "bad"})
    assert r.status_code == 403


def test_good_signature(client, monkeypatch):
    from twilio.request_validator import RequestValidator
    monkeypatch.delenv("SKIP_TWILIO_SIG")
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://haqeeq.example")
    form = {"From": "whatsapp:+971501234567", "Body": "hello scam"}
    sig = RequestValidator("tok").compute_signature("https://haqeeq.example/api/whatsapp", form)
    r = client.post("/api/whatsapp", data=form, headers={"X-Twilio-Signature": sig})
    assert r.status_code == 200


def test_correct_auth(client, monkeypatch):
    assert client.post("/api/correct", json={"detail": "d"}).status_code == 401
    assert client.post("/api/correct", json={"detail": "d"}, headers={"X-Admin-Token": "no"}).status_code == 401
    monkeypatch.delenv("DASHBOARD_ADMIN_TOKEN")
    assert client.post("/api/correct", json={"detail": "d"}, headers={"X-Admin-Token": "x"}).status_code == 500


def test_correct_delivery(client, env, monkeypatch):
    def sel(t, params=None):
        if t == "reports":
            return [{"sender_id": 1, "seeded": False}, {"sender_id": 2, "seeded": False},
                    {"sender_id": None, "seeded": True}, {"sender_id": 1, "seeded": False}]
        return [{"phone": "+971500000001"}, {"phone": "+971500000002"}]
    monkeypatch.setattr(supa, "select", sel)
    sent = []

    class C:
        def __init__(self, *a): self.messages = self
        def create(self, **k):
            if k["to"].endswith("2"): raise RuntimeError("fail")
            sent.append(k)
    import twilio.rest
    monkeypatch.setattr(twilio.rest, "Client", C)
    r = client.post("/api/correct", json={"detail": "Scam: x"}, headers={"X-Admin-Token": "sekret"})
    assert r.get_json() == {"ok": True, "recipients": 4, "delivered": 1}
    assert sent[0]["to"] == "whatsapp:+971500000001" and "تصحيح رسمي" in sent[0]["body"]
    assert env["upsert"][-1][0] == "corrections"
    assert client.open("/api/correct", method="OPTIONS").status_code == 204


def test_health(client, monkeypatch):
    monkeypatch.setattr(supa, "cached", lambda t: [1, 2, 3])
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    j = client.get("/api/health").get_json()
    assert j["ok"] is True and j["registry"] == 3 and j["ai"] is True and j["error"] is None
