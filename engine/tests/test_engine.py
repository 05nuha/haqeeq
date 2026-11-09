import io
import pytest
from PIL import Image, ImageDraw

from engine import phash, hamming, verify_image, check_text, reply_for, ARABIC_REPLIES, text_check
from .conftest import announcement, unrelated, to_bytes, _font


def test_phash_format_and_stable(official):
    h1, h2 = phash(official), phash(to_bytes(official))
    assert h1 == h2 and len(h1) == 16 and h1 == h1.lower()
    int(h1, 16)
    assert hamming(h1, h1) == 0


def test_phash_agrees_with_imagehash(official):
    imagehash = pytest.importorskip("imagehash")
    for im in [official, unrelated(0), unrelated(1), unrelated(2)]:
        ref = str(imagehash.phash(im.convert("RGB"), hash_size=8))
        assert hamming(phash(im), ref) <= 4


def test_exact_genuine(registry, loader, official):
    r = verify_image(to_bytes(official), registry, loader)
    print("exact", r["distance"], r["changed_pct"])
    assert r["verdict"] == "genuine" and r["matched_id"] == "public_holiday_notice"
    assert len(r["heat"]) == 16 and len(r["heat"][0]) == 16
    assert r["detail"] == "Matches Public holiday notice (Gov Media Office)"


def test_screenshot_genuine(registry, loader, official):
    jpg = to_bytes(official, "JPEG", quality=60)
    im = Image.open(io.BytesIO(jpg))
    im = im.resize((int(im.width * .75), int(im.height * .75)))
    r = verify_image(to_bytes(im, "JPEG", quality=60), registry, loader)
    print("screenshot", r["distance"], r["changed_pct"])
    assert r["verdict"] == "genuine"


def test_changed_date_altered(registry, loader, official):
    im = official.copy()
    d = ImageDraw.Draw(im)
    d.rectangle([40, 560, 300, 640], fill=(20, 110, 60))
    d.text((50, 580), "Date: 29 Dec 2027", font=_font(34), fill="white")
    r = verify_image(to_bytes(im), registry, loader)
    print("altered", r["distance"], r["changed_pct"])
    assert r["verdict"] == "altered" and r["changed_pct"] > 0.04
    assert r["detail"].startswith("Altered: Public holiday notice — ")
    assert max(max(row) for row in r["heat"]) > 0


@pytest.mark.parametrize("k", [0, 1, 2])
def test_unrelated_unverified(registry, loader, k):
    r = verify_image(to_bytes(unrelated(k)), registry, loader)
    print("unrelated", k, r["distance"])
    assert r["verdict"] == "unverified" and r["distance"] > 12
    assert r["detail"] == "No match in the official registry" and r["matched_id"] is None


def test_known_fake(registry, loader):
    fake_img = unrelated(1)
    fakes = [{"id": "explosions_downtown", "title": "x", "detail": "Fake: 'explosions in Downtown Dubai' image",
              "phash": phash(fake_img), "image_path": "fakes/x.png"}]
    r = verify_image(to_bytes(fake_img, "JPEG", quality=70), registry, loader, fakes)
    assert r["verdict"] == "unverified" and r["detail"] == fakes[0]["detail"]


def test_odd_modes_and_tiny(registry, loader, official):
    for im in [official.convert("RGBA"), official.convert("P"), official.convert("L"), Image.new("RGB", (3, 3), "red")]:
        r = verify_image(to_bytes(im), registry, loader)
        assert r["verdict"] in ("genuine", "altered", "unverified")
    r = verify_image(to_bytes(official.convert("RGBA")), registry, loader)
    assert r["verdict"] == "genuine"


def test_exif_orientation(registry, loader, official):
    rot = official.rotate(90, expand=True)   # stored sideways
    exif = Image.Exif()
    exif[0x0112] = 6                         # display needs 90 CW => upright again
    b = io.BytesIO()
    rot.save(b, "JPEG", quality=95, exif=exif)
    r = verify_image(b.getvalue(), registry, loader)
    assert r["verdict"] == "genuine"


def test_empty_registry(loader, official):
    assert verify_image(to_bytes(official), [], loader)["verdict"] == "unverified"


# ---------------- text ----------------
def test_scam_arabic():
    r = check_text("عاجل حوّل المبلغ فوراً لتجنب غرامة")
    assert r["verdict"] == "scam_risk" and r["ai_used"] is False
    assert r["detail"].startswith("Scam indicators:")


def test_hello():
    r = check_text("hello")
    assert r["verdict"] == "unverified" and r["detail"] == "No official source; verify before trusting"


def test_canonical_labels():
    assert check_text("شرطة دبي: عليك غرامة مرورية ادفع الان عبر الرابط")["detail"] == text_check.POLICE_FINE
    assert check_text("Your Emirates ID is suspended, send the OTP")["detail"] == text_check.EID_OTP
    assert check_text("هويتك الإماراتية موقوفة أرسل رمز التحقق")["detail"] == text_check.EID_OTP


def test_diacritics():
    assert check_text("عَاجِل حَوِّل المبلغ")["verdict"] == "scam_risk"


class _Resp:
    def __init__(self, data):
        self._d = data

    def raise_for_status(self):
        pass

    def json(self):
        return self._d


def _gem(risk, reason="سبب"):
    import json
    return _Resp({"candidates": [{"content": {"parts": [{"text": json.dumps(
        {"risk": risk, "reason_ar": reason, "category": "phishing"})}]}}]})


def test_gemini_high(monkeypatch):
    import requests
    seen = {}

    def post(url, json=None, headers=None, timeout=None):
        seen.update(url=url, headers=headers, timeout=timeout, body=json)
        return _gem("high", "رابط مشبوه")
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setattr(requests, "post", post)
    r = check_text("win a free holiday")
    assert r == {"verdict": "scam_risk", "detail": "Scam indicators: AI flagged", "ai_reason": "رابط مشبوه", "ai_used": True}
    assert seen["headers"]["x-goog-api-key"] == "k" and ":generateContent" in seen["url"]
    assert seen["body"]["generationConfig"]["responseMimeType"] == "application/json"
    assert reply_for(r).endswith("\n🤖 رابط مشبوه")


def test_gemini_low_and_canonical(monkeypatch):
    import requests
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setattr(requests, "post", lambda *a, **k: _gem("low"))
    r = check_text("عاجل حوّل المبلغ فوراً")   # rules still flag it even if AI says low
    assert r["verdict"] == "scam_risk" and r["ai_used"] is True
    assert check_text("see you at dinner")["verdict"] == "unverified"
    monkeypatch.setattr(requests, "post", lambda *a, **k: _gem("high"))
    assert check_text("Dubai Police fine, pay now")["detail"] == text_check.POLICE_FINE


def test_gemini_timeout_fallback(monkeypatch):
    import requests

    def boom(*a, **k):
        raise requests.exceptions.Timeout()
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setattr(requests, "post", boom)
    r = check_text("عاجل حوّل المبلغ فوراً لتجنب غرامة")
    assert r["verdict"] == "scam_risk" and r["ai_used"] is False


def test_replies():
    assert reply_for({"verdict": "genuine"}) == ARABIC_REPLIES["genuine"]
    assert "12.5%" in reply_for({"verdict": "altered", "changed_pct": 12.5})
