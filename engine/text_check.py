"""Text scam check: Gemini (optional) with rule-based fallback."""
import json
import os
import re

POLICE_FINE = "Scam: 'Dubai Police fine — pay now via link'"
EID_OTP = "Scam: 'Emirates ID suspended — verify OTP'"
NO_SOURCE = "No official source; verify before trusting"

_TASHKEEL = re.compile("[ؐ-ًؚ-ٰٟۖ-ۭـ]")


def normalize(text):
    t = _TASHKEEL.sub("", text or "")
    t = re.sub("[إأآٱ]", "ا", t)
    t = t.replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    return t.lower()


_RAW_WORDS = [
    # English
    "urgent", "immediately", "transfer", "fine", "penalty", "suspended", "click", "verify your",
    "prize", "you won", "password", "otp", "deport", "bank account", "pay now", "wire", "gift card",
    "account will be", "limited time", "claim your",
    # Arabic (legacy + variants; matching is done on normalised text)
    "عاجل", "فوري", "فورا", "فوراً", "حوّل", "حول", "تحويل", "غرامة", "غرامه", "احتجاز", "رابط",
    "جائزة", "جائزه", "فزت", "كلمة المرور", "كلمه السر", "الهوية", "تأشيرة", "مخالفة", "موقوف",
    "إيقاف", "رمز التحقق", "الرمز", "ادفع", "سدد", "انقر", "اضغط", "ترحيل", "حسابك",
]
# (normalised, original label)
SCAM_WORDS = list(dict.fromkeys(_RAW_WORDS))
_NORM_WORDS = []
for _w in SCAM_WORDS:
    _n = normalize(_w)
    if _n not in [x[0] for x in _NORM_WORDS]:
        _NORM_WORDS.append((_n, _w))


def _has(t, *words):
    return any(normalize(w) in t for w in words)


def _canonical(text):
    t = normalize(text)
    if _has(t, "police", "شرطة", "شرطه") and _has(t, "fine", "غرامة", "مخالفة", "غرامه"):
        return POLICE_FINE
    if _has(t, "emirates id", "الهوية", "الهويه", "هويت", "هويه") and _has(
            t, "suspend", "موقوف", "إيقاف", "ايقاف", "otp", "رمز"):
        return EID_OTP
    return None


def _rules(text):
    t = normalize(text)
    hits, seen = [], set()
    for n, orig in _NORM_WORDS:
        if n in t and n not in seen:
            seen.add(n)
            hits.append(orig)
    canon = _canonical(text)
    if len(hits) >= 2 or canon:
        return True, canon or "Scam indicators: " + ", ".join(hits[:5])
    return False, NO_SOURCE


def _model():
    return os.environ.get("GEMINI_MODEL") or "gemini-3.5-flash-lite"


def ai_text_check(text, entities=()):
    """Return {risk, reason_ar, category} or None. Total timeout 6 s; any error -> None."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    try:
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{_model()}:generateContent"
        names = ", ".join(str(e.get("name", e)) if isinstance(e, dict) else str(e) for e in list(entities)[:30])
        prompt = ("You detect scams and misleading messages forwarded by UAE residents on WhatsApp. "
                  "Classify risk as high (clear scam/phishing/fraud), medium, or low. "
                  "reason_ar is a one-sentence reason in Arabic. category is a short English label. "
                  + (f"Official UAE entities (messages impersonating them are suspicious): {names}. " if names else "")
                  + "Message:\n" + text[:2000])
        body = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": {
                    "type": "OBJECT",
                    "properties": {
                        "risk": {"type": "STRING", "enum": ["high", "medium", "low"]},
                        "reason_ar": {"type": "STRING"},
                        "category": {"type": "STRING"},
                    },
                    "required": ["risk", "reason_ar", "category"],
                },
            },
        }
        r = requests.post(url, json=body, headers={"x-goog-api-key": key}, timeout=(3, 6))
        r.raise_for_status()
        raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
        data = json.loads(raw)
        if data.get("risk") not in ("high", "medium", "low"):
            return None
        return data
    except Exception:
        return None


def check_text(text, entities=()):
    ai = ai_text_check(text, entities)
    scam, detail = _rules(text)
    if ai:
        canon = _canonical(text)
        # Either signal is enough: AI "high" OR the rule engine's >=2 keyword hits.
        if ai["risk"] == "high" or scam:
            return {"verdict": "scam_risk",
                    "detail": canon or (detail if scam else "Scam indicators: AI flagged"),
                    "ai_reason": ai.get("reason_ar"), "ai_used": True}
        return {"verdict": "unverified", "detail": NO_SOURCE, "ai_reason": ai.get("reason_ar"), "ai_used": True}
    return {"verdict": "scam_risk" if scam else "unverified", "detail": detail, "ai_reason": None, "ai_used": False}
