#!/usr/bin/env python3
"""Haqeeq end-to-end test for the WhatsApp webhook (POST /api/whatsapp).

It plays the role of Twilio: it builds the form a WhatsApp message would produce,
signs it with X-Twilio-Signature (HMAC-SHA1, base64), posts it, parses the TwiML
reply and checks the first reply line against the exact ARABIC_REPLIES strings in
CONTRACT.md section 4.

Usage (see scripts/e2e/README.md for full details):
  export TWILIO_AUTH_TOKEN=...
  python scripts/e2e/whatsapp_e2e.py                       # local dev server
  python scripts/e2e/whatsapp_e2e.py --base-url https://<prod>.vercel.app \
      --image-base-url https://<proj>.supabase.co/storage/v1/object/public/media/ --check-db
  python scripts/e2e/whatsapp_e2e.py --no-sig              # server has SKIP_TWILIO_SIG=1

Exit code: 0 when every check passes, 1 otherwise, 2 for bad usage/config.
Standard library + requests only. Never prints the auth token.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import secrets
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin

import requests

HERE = Path(__file__).resolve().parent
DEFAULT_CASES = HERE / "cases.json"

# EXACT strings from CONTRACT.md section 4 (ARABIC_REPLIES). Do not edit.
ARABIC_REPLIES = {
    "genuine": "✅ صحيح — هذا محتوى رسمي موثّق.",
    "altered": "🔴 معدّل — نسخة معدّلة من إعلان رسمي. لا تقم بإعادة إرساله.",
    "unverified": "⚪ غير مؤكد — لم يصدر عن أي جهة رسمية. كن حذراً.",
    "scam_risk": "🔴 احتيال محتمل — الرسالة تحمل مؤشرات احتيال. تحقق قبل أي إجراء.",
}

# Contract verdict -> reports.verdict column value (same words, but kept explicit).
DB_VERDICT = {"genuine": "genuine", "altered": "altered",
              "unverified": "unverified", "scam_risk": "scam_risk"}

SCAM_TEXT = "عاجل حوّل المبلغ فوراً لتجنب غرامة"
HELLO_TEXT = "hello"
ENDPOINT_PATH = "/api/whatsapp"
TWILIO_FROM = "whatsapp:+14155238886"        # sandbox number (CONTRACT section 7)
TEST_SENDER = "whatsapp:+971500000000"       # fictional test phone, not a real subscriber


# ---------------------------------------------------------------------------
# Twilio request signature (https://www.twilio.com/docs/usage/webhooks/webhooks-security)
# Algorithm: take the full URL (scheme, host, path, and query string if present),
# append each POST parameter as key+value with keys sorted ascending (no separators),
# HMAC-SHA1 with the auth token as key, base64-encode the digest.
# ---------------------------------------------------------------------------
def twilio_signature(auth_token: str, url: str, params: dict) -> str:
    data = url
    for key in sorted(params):
        value = params[key]
        values = value if isinstance(value, (list, tuple)) else [value]
        for v in values:  # multi-valued params: append each value in order
            data += key + ("" if v is None else str(v))
    digest = hmac.new(auth_token.encode("utf-8"), data.encode("utf-8"), hashlib.sha1).digest()
    return base64.b64encode(digest).decode("ascii")


# ---------------------------------------------------------------------------
# TwiML helpers
# ---------------------------------------------------------------------------
def twiml_body(text: str) -> str | None:
    """Return the first <Message><Body> text in a TwiML document, or None."""
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return None
    body = root.find(".//Message/Body")
    if body is None:
        return None
    return (body.text or "").strip()


def first_line(s: str) -> str:
    return s.strip().splitlines()[0].strip() if s and s.strip() else ""


# ---------------------------------------------------------------------------
# Supabase helpers (service key, server-side check only)
# ---------------------------------------------------------------------------
class Db:
    def __init__(self, url: str, key: str):
        self.url = url.rstrip("/")
        self.h = {"apikey": key, "Authorization": f"Bearer {key}"}

    def latest_report_id(self) -> int:
        r = requests.get(
            f"{self.url}/rest/v1/reports",
            params={"select": "id", "seeded": "eq.false", "order": "id.desc", "limit": "1"},
            headers=self.h, timeout=15)
        r.raise_for_status()
        rows = r.json()
        return rows[0]["id"] if rows else 0

    def new_reports_after(self, last_id: int) -> list[dict]:
        r = requests.get(
            f"{self.url}/rest/v1/reports",
            params={"select": "id,verdict,kind,detail,image_path",
                    "seeded": "eq.false", "id": f"gt.{last_id}", "order": "id.asc"},
            headers=self.h, timeout=15)
        r.raise_for_status()
        return r.json()


# ---------------------------------------------------------------------------
# Case runner
# ---------------------------------------------------------------------------
def build_form(kind: str, body: str = "", media_url: str | None = None,
               media_type: str | None = None) -> dict:
    form = {
        "AccountSid": os.environ.get("TWILIO_ACCOUNT_SID", "ACe2e00000000000000000000000000000"),
        "MessageSid": "SM" + secrets.token_hex(16),
        "From": TEST_SENDER,
        "To": TWILIO_FROM,
        "Body": body,
        "NumMedia": "1" if media_url else "0",
        "ProfileName": "e2e test",
        "WaId": TEST_SENDER.split(":+")[-1],
    }
    if media_url:
        form["MediaUrl0"] = media_url
        form["MediaContentType0"] = media_type or "image/jpeg"
    return form


def post_signed(endpoint: str, form: dict, sign_url: str, token: str | None,
                timeout: float) -> requests.Response:
    headers = {}
    if token is not None:
        headers["X-Twilio-Signature"] = twilio_signature(token, sign_url, form)
    return requests.post(endpoint, data=form, headers=headers, timeout=timeout)


def resolve_url(url: str, image_base: str | None) -> str:
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if not image_base:
        raise SystemExit("relative image url in cases.json needs --image-base-url")
    return urljoin(image_base if image_base.endswith("/") else image_base + "/", url)


def guess_media_type(url: str) -> str:
    u = url.lower()
    if u.endswith(".png"):
        return "image/png"
    if u.endswith(".webp"):
        return "image/webp"
    return "image/jpeg"


def selftest() -> int:
    """Check twilio_signature() against the example in Twilio's signature docs.

    Values below are the documented example as recalled by the QA agent; if this fails,
    re-check the example text on twilio.com/docs/usage/webhooks/webhooks-security before
    assuming the implementation is wrong.
    """
    url = "https://mycompany.com/myapp.php?foo=1&bar=2"
    params = {
        "CallSid": "CA1234567890ABCDE",
        "Caller": "+14158675309",
        "Digits": "1234",
        "From": "+14158675309",
        "To": "+18005551212",
    }
    want = "RSOYDt4T1cUTdK1PDd93/VVr8B8="
    got = twilio_signature("12345", url, params)
    ok = got == want
    print(f"signature selftest: {'PASS' if ok else 'FAIL'} (got {got}, want {want})")
    return 0 if ok else 1


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-url", default=os.environ.get("E2E_BASE_URL", "http://127.0.0.1:5328"),
                    help="where the app is served (default http://127.0.0.1:5328)")
    ap.add_argument("--public-url", default=None,
                    help="full URL Twilio calls, used for signing (default: PUBLIC_BASE_URL env + "
                         "/api/whatsapp, else base-url + /api/whatsapp). Must match the server's view.")
    ap.add_argument("--image-base-url", default=os.environ.get("E2E_IMAGE_BASE_URL"),
                    help="public URL prefix for test images, e.g. Supabase public media URL")
    ap.add_argument("--cases", default=str(DEFAULT_CASES), help="JSON file with image cases")
    ap.add_argument("--no-sig", action="store_true",
                    help="do not send X-Twilio-Signature (server must have SKIP_TWILIO_SIG=1)")
    ap.add_argument("--skip-images", action="store_true", help="run only the text cases")
    ap.add_argument("--check-db", action="store_true",
                    help="confirm a new reports row per case (needs SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)")
    ap.add_argument("--selftest", action="store_true", help="only verify the signature function, then exit")
    ap.add_argument("--timeout", type=float, default=30.0, help="per-request timeout seconds (default 30)")
    args = ap.parse_args()

    token = None
    if not args.no_sig:
        token = os.environ.get("TWILIO_AUTH_TOKEN", "")
        if not token:
            print("ERROR: TWILIO_AUTH_TOKEN is not set (or pass --no-sig for SKIP_TWILIO_SIG=1 servers)",
                  file=sys.stderr)
            return 2

    base = args.base_url.rstrip("/")
    endpoint = base + ENDPOINT_PATH
    sign_url = args.public_url or (
        (os.environ.get("PUBLIC_BASE_URL", "").rstrip("/") + ENDPOINT_PATH)
        if os.environ.get("PUBLIC_BASE_URL") else endpoint)

    image_base = args.image_base_url
    if image_base is None and os.environ.get("SUPABASE_URL"):
        image_base = os.environ["SUPABASE_URL"].rstrip("/") + "/storage/v1/object/public/media/"

    # Build the case list.
    cases: list[dict] = [
        {"name": "text: hello", "kind": "text", "body": HELLO_TEXT, "expect": "unverified"},
        {"name": "text: Arabic scam", "kind": "text", "body": SCAM_TEXT, "expect": "scam_risk"},
    ]
    if not args.skip_images:
        cfg = json.loads(Path(args.cases).read_text(encoding="utf-8"))
        for c in cfg.get("image_cases", []):
            cases.append({"name": "image: " + c["name"], "kind": "image",
                          "media_url": resolve_url(c["url"], image_base),
                          "expect": c["expect"]})

    db = None
    if args.check_db:
        su = os.environ.get("SUPABASE_URL")
        sk = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not su or not sk:
            print("ERROR: --check-db needs SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY", file=sys.stderr)
            return 2
        db = Db(su, sk)

    # Security case: a wrong signature must be rejected.
    results: list[tuple[str, bool, str]] = []
    if not args.no_sig:
        form = build_form("text", HELLO_TEXT)
        try:
            r = post_signed(endpoint, form, sign_url, "wrong-token-e2e", args.timeout)
            ok = r.status_code == 403
            results.append(("bad signature -> 403", ok, f"HTTP {r.status_code}"))
        except requests.RequestException as e:
            results.append(("bad signature -> 403", False, f"request error: {e}"))
    else:
        print("note: bad-signature check skipped (--no-sig)")

    for case in cases:
        if case["kind"] == "text":
            form = build_form("text", case["body"])
        else:
            form = build_form("image", media_url=case["media_url"],
                              media_type=guess_media_type(case["media_url"]))

        before = None
        if db:
            try:
                before = db.latest_report_id()
            except requests.RequestException as e:
                results.append((case["name"], False, f"db read failed: {e}"))
                continue

        t0 = time.time()
        try:
            r = post_signed(endpoint, form, sign_url, token, args.timeout)
        except requests.RequestException as e:
            results.append((case["name"], False, f"request error: {e}"))
            continue
        elapsed = time.time() - t0

        if r.status_code != 200:
            results.append((case["name"], False, f"HTTP {r.status_code} {r.text[:120]!r}"))
            continue
        body = twiml_body(r.text)
        if body is None:
            results.append((case["name"], False, "reply is not parseable TwiML <Message><Body>"))
            continue

        got = first_line(body)
        want = ARABIC_REPLIES[case["expect"]]
        ok = got == want
        detail = f"{case['expect']} in {elapsed:.1f}s"
        if not ok:
            detail += f" | got: {got[:60]!r}"

        if db and ok:
            # Poll briefly: the row is written before/while replying, but allow for lag.
            found = []
            for _ in range(8):
                found = db.new_reports_after(before)
                if found:
                    break
                time.sleep(1)
            if not found:
                ok = False
                detail += " | no new reports row"
            else:
                row_verdict = found[-1]["verdict"]
                if row_verdict != DB_VERDICT[case["expect"]]:
                    ok = False
                    detail += f" | reports.verdict={row_verdict}"
                else:
                    detail += " | db row ok"
        results.append((case["name"], ok, detail))

    # Table.
    width = max(len(n) for n, _, _ in results) + 2
    print()
    print(f"{'CASE'.ljust(width)}RESULT  DETAIL")
    print("-" * (width + 40))
    for name, ok, detail in results:
        print(f"{name.ljust(width)}{'PASS' if ok else 'FAIL'}    {detail}")
    failed = [r for r in results if not r[1]]
    print("-" * (width + 40))
    print(f"{len(results) - len(failed)}/{len(results)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
