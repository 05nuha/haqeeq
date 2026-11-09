"""
engine.py  —  OWNER: Person A (Cyber)
The verification engine. This is the brain: it decides genuine / altered / unverified
for images, and scam-risk for text. No web server here, just the logic.

How image verification works (two steps):
  STEP 1 - MATCH. A 64-bit perceptual hash (pHash) is robust to WhatsApp recompression,
           so it answers "is this derived from one of our official posts?". A screenshot
           of a genuine post still matches, even though WhatsApp stripped the signature.
  STEP 2 - TAMPER. Once matched, we compare the incoming image to the stored official
           image pixel-region by pixel-region. A plain screenshot differs almost nowhere
           -> GENUINE. A doctored post (changed date/number) has a changed region
           -> ALTERED, and we can even say where (the heat-map).
"""
import os
import json
import numpy as np
import imagehash
from PIL import Image
from db import get_official_posts

# --- Thresholds. TUNE THESE in the end-of-night gate test with YOUR real images. ---
MATCH_THRESH = 12       # coarse pHash distance (/64) <= this  => derived from that official post
TAMPER_PCT = 0.04       # % of pixels clearly changed above which we call it ALTERED
PIXEL_THRESH = 55       # a single pixel counts as "changed" if its grey value moved this much
GRID = 256              # both images are compared at this resolution


def _phash(path):
    return imagehash.phash(Image.open(path).convert("RGB"), hash_size=8)


def _changed_fraction(incoming_path, official_path):
    """Percent of pixels that clearly changed between the two images (0-100).
    Also returns the per-cell grid so the dashboard can draw a heat-map."""
    a = np.asarray(Image.open(incoming_path).convert("L").resize((GRID, GRID)), dtype=float)
    b = np.asarray(Image.open(official_path).convert("L").resize((GRID, GRID)), dtype=float)
    diff = np.abs(a - b)
    pct = float((diff > PIXEL_THRESH).mean() * 100)
    # 16x16 heat grid of where it changed (for the forensic view, optional)
    step = GRID // 16
    heat = [[float((diff[r*step:(r+1)*step, c*step:(c+1)*step] > PIXEL_THRESH).mean())
             for c in range(16)] for r in range(16)]
    return pct, heat


def verify_image(path):
    h8 = _phash(path)
    best, best_coarse = None, 999
    for p in get_official_posts():
        d = h8 - imagehash.hex_to_hash(p["hash8"])
        if d < best_coarse:
            best_coarse, best = d, p

    if best is None or best_coarse > MATCH_THRESH:
        return {"verdict": "unverified", "matched_id": None, "distance": int(best_coarse),
                "detail": "No match in the official registry"}

    pct, _heat = _changed_fraction(path, best["image_path"])
    if pct <= TAMPER_PCT:
        return {"verdict": "genuine", "matched_id": best["id"], "distance": int(best_coarse),
                "detail": f"Matches {best['title']} ({best['issuer']})"}
    return {"verdict": "altered", "matched_id": best["id"], "distance": int(best_coarse),
            "detail": f"Looks like {best['title']} but {pct:.1f}% of it was changed"}


# --- Text check. Rule-based fallback always works; the LLM upgrade earns the AI marks. ---
SCAM_WORDS = [
    "urgent", "immediately", "transfer", "fine", "penalty", "suspended", "click",
    "verify your", "prize", "you won", "password", "otp", "deport", "bank account",
    "عاجل", "فوري", "حوّل", "تحويل", "غرامة", "احتجاز", "رابط", "جائزة", "فزت",
    "كلمة المرور", "الهوية", "تأشيرة",
]


def ai_text_check(text):
    """Optional AI upgrade. Returns a dict or None. Needs GEMINI_API_KEY in Secrets.
    NOTE: verify the model name below still exists; if the call fails we fall back to rules."""
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        return None
    try:
        import requests
        url = ("https://generativelanguage.googleapis.com/v1beta/models/"
               "gemini-2.0-flash:generateContent?key=" + key)
        prompt = (
            "You detect scams in messages forwarded by UAE residents. "
            "Reply ONLY with JSON: {\"risk\":\"high|medium|low\",\"reason_ar\":\"<short Arabic reason>\"}. "
            "Message: " + text
        )
        r = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=15)
        raw = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip().strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()
        return json.loads(raw)
    except Exception:
        return None


def check_text(text):
    ai = ai_text_check(text)
    if ai:
        verdict = "scam_risk" if ai.get("risk") == "high" else "unverified"
        return {"verdict": verdict, "detail": ai.get("reason_ar", "")}
    t = text.lower()
    hits = [w for w in SCAM_WORDS if w in t]
    if len(hits) >= 2:
        return {"verdict": "scam_risk", "detail": "Scam indicators: " + ", ".join(hits[:5])}
    return {"verdict": "unverified", "detail": "No official source; verify before trusting"}
