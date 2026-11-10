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
                    "meta": bool(_meta_token() and os.environ.get("META_PHONE_NUMBER_ID")),
                    "error": err})


@app.route("/api/whatsapp", methods=["GET"])
def whatsapp_status():
    return jsonify({"ok": True, "hint": "Twilio must POST here", "last_request": LAST})


def _process(phone, body, media_loader=None, ctype=""):
    """Channel-agnostic core: run the engine, record the report, return the Arabic reply text.
    media_loader: zero-arg callable returning image bytes, or None for a text message."""
    body = (body or "").strip()
    if media_loader is not None:
        if not (ctype or "").lower().startswith("image/"):
            # audio/video/docs: not verifiable yet. Schema allows only image/text/link -> 'text'.
            _save({"kind": "text", "verdict": "unverified",
                   "detail": "Unsupported media (voice/video) - not checked", "ai_used": False}, phone)
            return MEDIA_UNSUPPORTED_AR
        try:
            data = media_loader()
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
            return UNVERIFIED_AR
        _save({"kind": "image", "verdict": res["verdict"], "matched_id": res.get("matched_id"),
               "distance": res.get("distance"), "changed_pct": res.get("changed_pct"),
               "heat": res.get("heat"), "detail": res.get("detail"), "ai_reason": None,
               "ai_used": False, "image_path": path}, phone)
        return reply_for(res)

    if not body or body.lower() in ("help", "start") or body in ("مساعدة",):
        return HELP_AR
    try:
        res = check_text(body, _safe_table("entities"))
    except Exception:
        log.exception("check_text failed")
        res = {"verdict": "unverified", "detail": "No official source; verify before trusting",
               "ai_reason": None, "ai_used": False}
    _save({"kind": "link" if URL_RE.search(body) else "text", "verdict": res["verdict"],
           "detail": res.get("detail"), "ai_reason": res.get("ai_reason"),
           "ai_used": bool(res.get("ai_used"))}, phone)
    return reply_for(res)


@app.route("/api/whatsapp", methods=["POST"])
def whatsapp():
    """Twilio WhatsApp webhook -> TwiML reply."""
    if not _sig_ok():
        return Response("invalid signature", status=403)
    phone = request.form.get("From", "").replace("whatsapp:", "")
    try:
        num_media = int(request.form.get("NumMedia", "0") or 0)
    except ValueError:
        num_media = 0
    if num_media > 0:
        url = request.form.get("MediaUrl0", "")
        reply = _process(phone, None, lambda: _download_media(url),
                         request.form.get("MediaContentType0") or "")
    else:
        reply = _process(phone, request.form.get("Body"))
    return _twilio_reply(request.form.get("From", ""), request.form.get("To", ""), reply)


def _twilio_reply(to, frm, text):
    """Send the reply via Twilio REST so failures come back with an exact error code
    (shown at GET /api/whatsapp). Falls back to a TwiML reply if the REST send fails."""
    LAST.update(reply_mode=None, reply_status=None, reply_error=None)
    if os.environ.get("TWILIO_REPLY_MODE", "rest") == "rest" and to:
        try:
            from twilio.rest import Client
            client = Client(os.environ.get("TWILIO_ACCOUNT_SID", "").strip(),
                            os.environ.get("TWILIO_AUTH_TOKEN", "").strip())
            m = client.messages.create(from_=frm or os.environ.get("TWILIO_WHATSAPP_FROM", ""), to=to, body=text)
            LAST.update(reply_mode="rest", reply_status=getattr(m, "status", None),
                        reply_sid=(getattr(m, "sid", "") or "")[:6] + "...")
            from twilio.twiml.messaging_response import MessagingResponse
            return Response(str(MessagingResponse()), mimetype="text/xml")   # empty: already sent
        except Exception as e:
            log.exception("twilio REST reply failed")
            LAST.update(reply_mode="rest_failed_fallback_twiml",
                        reply_error=(type(e).__name__ + ": " + str(e))[:400])
    else:
        LAST["reply_mode"] = "twiml"
    return _twiml(text)


# ---------------- Meta WhatsApp Cloud API (alternative to Twilio) ----------------

def _graph():
    return "https://graph.facebook.com/" + os.environ.get("META_GRAPH_VERSION", "v23.0")


def _meta_token():
    return os.environ.get("META_WHATSAPP_TOKEN", "").strip()


def meta_send(to_digits, text):
    """Send a WhatsApp text via Meta Cloud API. to_digits: international number without '+'."""
    r = requests.post(f"{_graph()}/{os.environ.get('META_PHONE_NUMBER_ID', '').strip()}/messages",
                      headers={"Authorization": "Bearer " + _meta_token()},
                      json={"messaging_product": "whatsapp", "to": to_digits.lstrip("+"),
                            "type": "text", "text": {"body": text}}, timeout=6)
    META_LAST["send_status"] = r.status_code
    if r.status_code >= 300:
        META_LAST["send_error"] = r.text[:300]
    r.raise_for_status()


def _meta_media(media_id):
    h = {"Authorization": "Bearer " + _meta_token()}
    meta = requests.get(f"{_graph()}/{media_id}", headers=h, timeout=5)
    meta.raise_for_status()
    with requests.get(meta.json()["url"], headers=h, timeout=6, stream=True) as r:
        r.raise_for_status()
        buf = bytearray()
        for chunk in r.iter_content(65536):
            buf.extend(chunk)
            if len(buf) > MAX_MEDIA:
                raise ValueError("media too large")
        return bytes(buf)


META_LAST = {"at": None}   # debugging aid for GET /api/meta?status=1 (no phone numbers stored)


def _meta_sig_ok(raw):
    secret = os.environ.get("META_APP_SECRET", "").strip()
    if not secret:
        return True          # optional; set META_APP_SECRET to enforce
    sig = request.headers.get("X-Hub-Signature-256", "")
    want = "sha256=" + hmac.new(secret.encode(), raw, "sha256").hexdigest()
    return hmac.compare_digest(sig, want)


@app.route("/api/meta", methods=["GET"])
def meta_verify():
    if request.args.get("hub.mode") == "subscribe":
        expected = os.environ.get("META_VERIFY_TOKEN", "").strip()
        if expected and hmac.compare_digest(request.args.get("hub.verify_token", ""), expected):
            return Response(request.args.get("hub.challenge", ""), mimetype="text/plain")
        return Response("verify token mismatch", status=403)
    return jsonify({"ok": True, "configured": bool(_meta_token() and os.environ.get("META_PHONE_NUMBER_ID")),
                    "verify_token_set": bool(os.environ.get("META_VERIFY_TOKEN")),
                    "app_secret_set": bool(os.environ.get("META_APP_SECRET")), "last_request": META_LAST})


@app.route("/api/meta", methods=["POST"])
def meta_webhook():
    import datetime
    raw = request.get_data()
    META_LAST.update(at=datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
                     sig_ok=None, handled=0, send_status=None, send_error=None)
    if not _meta_sig_ok(raw):
        META_LAST["sig_ok"] = False
        return Response("invalid signature", status=403)
    META_LAST["sig_ok"] = True
    payload = request.get_json(silent=True) or {}
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            for msg in (change.get("value") or {}).get("messages", []) or []:
                wa_id = msg.get("from", "")
                phone = "+" + wa_id.lstrip("+")
                mtype = msg.get("type")
                try:
                    if mtype == "text":
                        reply = _process(phone, (msg.get("text") or {}).get("body"))
                    elif mtype in ("image", "audio", "video", "document", "sticker"):
                        m = msg.get(mtype) or {}
                        ctype = m.get("mime_type", "image/jpeg" if mtype == "image" else mtype + "/x")
                        reply = _process(phone, None, lambda mid=m.get("id"): _meta_media(mid), ctype)
                    else:
                        reply = HELP_AR
                    meta_send(wa_id, reply)
                    META_LAST["handled"] += 1
                except Exception:
                    log.exception("meta message failed")
    return jsonify({"ok": True})   # always 200 so Meta doesn't retry


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
    if phones and _meta_token() and os.environ.get("META_PHONE_NUMBER_ID"):
        for p in phones:
            try:
                meta_send(p, message)
                delivered += 1
            except Exception:
                log.exception("meta correction send failed")
        phones = []          # Meta configured: don't double-send via Twilio
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
