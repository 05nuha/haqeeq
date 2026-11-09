"""Haqeeq bot/API: one Flask WSGI app. Entry files api/whatsapp.py, api/correct.py,
api/health.py each re-export `app` so Vercel maps one function per URL."""
import hmac
import logging
import os
import random
import re
import sys
import uuid

import requests
from flask import Flask, Response, jsonify, request

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from . import supa  # noqa: E402

try:
    from engine import verify_image, check_text, reply_for  # noqa: E402
except ImportError:  # engine missing: handlers fail soft, tests monkeypatch these
    def _missing(*a, **k):
        raise RuntimeError("engine package not available")
    verify_image = check_text = reply_for = _missing

log = logging.getLogger("haqeeq")
app = Flask(__name__)

MAX_MEDIA = 8 * 1024 * 1024
URL_RE = re.compile(r"(https?://|www\.)\S+", re.I)
EMIRATES = [("Dubai", 8), ("Sharjah", 5), ("Abu Dhabi", 4), ("Ajman", 3), ("Al Ain", 2),
            ("Ras Al Khaimah", 2), ("Fujairah", 1), ("Umm Al Quwain", 1)]

HELP_AR = ("مرحباً بك في حقيق 👋\nأرسل لنا صورة أو رسالة مشبوهة (إعلان رسمي، رابط، أو نص) "
           "وسنخبرك إن كانت صحيحة أم معدّلة أم احتيالاً.")
MEDIA_UNSUPPORTED_AR = ("⚪ غير مؤكد — التحقق من الرسائل الصوتية والفيديو قريباً. "
                        "أرسل صورة أو نصاً للتحقق الآن.")
DEFAULT_CORRECTION = ("📢 تصحيح رسمي: المحتوى الذي أرسلته سابقاً غير صحيح. "
                      "يرجى عدم إعادة إرساله والاعتماد على المصادر الرسمية فقط.\n"
                      "Official correction: the content you previously sent is false. "
                      "Please do not forward it; rely on official sources only.")
UNVERIFIED_AR = "⚪ غير مؤكد — لم يصدر عن أي جهة رسمية. كن حذراً."


def mask(phone):
    return (phone[:6] + "•••" + phone[-3:]) if len(phone) > 9 else phone


def pick_emirate():
    names, weights = zip(*EMIRATES)
    return random.choices(names, weights)[0]


def _twiml(text):
    from twilio.twiml.messaging_response import MessagingResponse
    r = MessagingResponse()
    r.message(text)
    return Response(str(r), mimetype="text/xml")


def _candidate_urls():
    """URLs Twilio may have signed: configured base, then the host the request arrived on."""
    bases = []
    env = (os.environ.get("PUBLIC_BASE_URL") or os.environ.get("BASE_URL") or "").strip().rstrip("/")
    if env:
        if env.endswith("/api/whatsapp"):
            env = env[: -len("/api/whatsapp")]
        if not env.startswith("http"):
            env = "https://" + env
        bases.append(env)
    proto = request.headers.get("X-Forwarded-Proto", "https").split(",")[0].strip()
    for h in (request.headers.get("X-Forwarded-Host"), request.headers.get("Host")):
        if h:
            bases.append(f"{proto}://{h.split(',')[0].strip()}")
    urls = []
    for b in bases:
        for u in (b + "/api/whatsapp", b + "/api/whatsapp/"):
            if u not in urls:
                urls.append(u)
    return urls


LAST = {"at": None}   # last inbound request seen by this instance (no phone numbers stored)


def _sig_ok():
    import datetime
    sig = request.headers.get("X-Twilio-Signature", "")
    LAST.update(at=datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
                has_signature=bool(sig), has_token=bool(os.environ.get("TWILIO_AUTH_TOKEN")),
                urls_tried=_candidate_urls(), num_media=request.form.get("NumMedia"), sig_ok=None)
    if os.environ.get("SKIP_TWILIO_SIG") == "1":
        LAST["sig_ok"] = "skipped"
        return True
    from twilio.request_validator import RequestValidator
    token = os.environ.get("TWILIO_AUTH_TOKEN", "").strip()
    if not token or not sig:
        LAST["sig_ok"] = False
        return False
    v = RequestValidator(token)
    params = request.form.to_dict()
    ok = any(v.validate(u, params, sig) for u in LAST["urls_tried"])
    LAST["sig_ok"] = ok
    return ok


def _download_media(url):
    auth = (os.environ.get("TWILIO_ACCOUNT_SID", ""), os.environ.get("TWILIO_AUTH_TOKEN", ""))
    with requests.get(url, auth=auth, timeout=5, stream=True, allow_redirects=True) as r:
        r.raise_for_status()
        # requests drops auth on cross-host redirect, which is what Twilio's S3 redirect wants.
        buf = bytearray()
        for chunk in r.iter_content(65536):
            buf.extend(chunk)
            if len(buf) > MAX_MEDIA:
                raise ValueError("media too large")
        return bytes(buf)


def _save(row_fields, phone):
    """Upsert sender + insert report; never raises."""
    try:
        sender_id = None
        try:
            s = supa.upsert("senders", {"phone": phone}, on_conflict="phone")
            sender_id = s[0]["id"] if s else None
        except Exception:
            log.exception("sender upsert failed")
        row = dict(row_fields, sender_masked=mask(phone), sender_id=sender_id,
                   emirate=pick_emirate(), seeded=False)
        supa.insert("reports", row)
    except Exception:
        log.exception("report insert failed")


@app.route("/api/health", methods=["GET"])
def health():
    n, err = 0, None
    try:
        n = len(supa.cached("official_posts"))
    except Exception as e:
        log.exception("health registry")
        err = type(e).__name__ + ": " + str(e)[:160]
    return jsonify({"ok": True, "registry": n, "ai": bool(os.environ.get("GEMINI_API_KEY")),
                    "supabase_url": bool(os.environ.get("SUPABASE_URL")),
                    "service_key": bool(supa.service_key()),
                    "supabase_env_names": sorted(k for k in os.environ if "SUPABASE" in k.upper()),
                    "twilio": bool(os.environ.get("TWILIO_ACCOUNT_SID") and os.environ.get("TWILIO_AUTH_TOKEN")),
                    "base_url": bool(os.environ.get("PUBLIC_BASE_URL") or os.environ.get("BASE_URL")),
                    "admin_token": bool(os.environ.get("DASHBOARD_ADMIN_TOKEN")),
                    "error": err})


@app.route("/api/whatsapp", methods=["GET"])
def whatsapp_status():
    return jsonify({"ok": True, "hint": "Twilio must POST here", "last_request": LAST})


@app.route("/api/whatsapp", methods=["POST"])
def whatsapp():
    if not _sig_ok():
        return Response("invalid signature", status=403)
    phone = request.form.get("From", "").replace("whatsapp:", "")
    body = (request.form.get("Body") or "").strip()
    try:
        num_media = int(request.form.get("NumMedia", "0") or 0)
    except ValueError:
        num_media = 0

    if num_media > 0:
        ctype = (request.form.get("MediaContentType0") or "").lower()
        if not ctype.startswith("image/"):
            # audio/video/docs: not verifiable yet. Schema allows only image/text/link -> 'text'.
            _save({"kind": "text", "verdict": "unverified",
                   "detail": "Unsupported media (voice/video) - not checked", "ai_used": False}, phone)
            return _twiml(MEDIA_UNSUPPORTED_AR)
        try:
            data = _download_media(request.form.get("MediaUrl0", ""))
            path = f"incoming/{uuid.uuid4()}.jpg"
            try:
                supa.upload(path, data, "image/jpeg")
            except Exception:
                log.exception("upload failed")
                path = None
            res = verify_image(data, supa.cached("official_posts"), supa.load_image,
                               _safe_table("known_fakes"))
        except Exception:
            log.exception("image check failed")
            return _twiml(UNVERIFIED_AR)
        _save({"kind": "image", "verdict": res["verdict"], "matched_id": res.get("matched_id"),
               "distance": res.get("distance"), "changed_pct": res.get("changed_pct"),
               "heat": res.get("heat"), "detail": res.get("detail"), "ai_reason": None,
               "ai_used": False, "image_path": path}, phone)
        return _twiml(reply_for(res))

    if body.lower() in ("help", "start") or body in ("مساعدة",):
        return _twiml(HELP_AR)
    if not body:
        return _twiml(HELP_AR)
    try:
        res = check_text(body, _safe_table("entities"))
    except Exception:
        log.exception("check_text failed")
        res = {"verdict": "unverified", "detail": "No official source; verify before trusting",
               "ai_reason": None, "ai_used": False}
    _save({"kind": "link" if URL_RE.search(body) else "text", "verdict": res["verdict"],
           "detail": res.get("detail"), "ai_reason": res.get("ai_reason"),
           "ai_used": bool(res.get("ai_used"))}, phone)
    return _twiml(reply_for(res))


def _safe_table(name):
    try:
        return supa.cached(name)
    except Exception:
        log.exception("load %s", name)
        return []


@app.route("/api/correct", methods=["POST", "OPTIONS"])
def correct():
    if request.method == "OPTIONS":      # same-origin only: no CORS headers
        return Response("", status=204, headers={"Allow": "POST, OPTIONS"})
    expected = os.environ.get("DASHBOARD_ADMIN_TOKEN")
    if not expected:
        return jsonify({"ok": False, "error": "admin token not configured"}), 500
    given = request.headers.get("X-Admin-Token", "")
    if not hmac.compare_digest(given.encode(), expected.encode()):
        return jsonify({"ok": False, "error": "unauthorized"}), 401
    data = request.get_json(silent=True) or {}
    detail = (data.get("detail") or "").strip()
    if not detail:
        return jsonify({"ok": False, "error": "detail required"}), 400
    message = (data.get("message") or "").strip() or DEFAULT_CORRECTION
    try:
        rows = supa.select("reports", {"select": "sender_id,seeded", "detail": "eq." + detail})
        recipients = len(rows)
        real_ids = sorted({r["sender_id"] for r in rows if not r.get("seeded") and r.get("sender_id")})
        phones = []
        if real_ids:
            ids = ",".join(str(i) for i in real_ids)
            phones = [s["phone"] for s in supa.select("senders", {"select": "phone", "id": f"in.({ids})"})]
    except Exception:
        log.exception("correct: lookup failed")
        return jsonify({"ok": False, "error": "database error"}), 502
    delivered = 0
    if phones:
        try:
            from twilio.rest import Client
            client = Client(os.environ.get("TWILIO_ACCOUNT_SID", ""), os.environ.get("TWILIO_AUTH_TOKEN", ""))
            frm = os.environ.get("TWILIO_WHATSAPP_FROM", "")
        except Exception:
            log.exception("twilio client")
            client = None
        for p in phones if client else []:
            try:
                client.messages.create(from_=frm, to="whatsapp:" + p, body=message)
                delivered += 1
            except Exception:
                log.exception("send failed")
    try:
        supa.upsert("corrections", {"detail": detail, "message": message, "recipients": recipients,
                                    "delivered": delivered, "ts": _now()}, on_conflict="detail")
    except Exception:
        log.exception("corrections upsert")
        return jsonify({"ok": False, "error": "database error", "recipients": recipients,
                        "delivered": delivered}), 502
    return jsonify({"ok": True, "recipients": recipients, "delivered": delivered})


def _now():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
