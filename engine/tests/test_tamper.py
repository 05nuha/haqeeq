"""Engine v2 tamper check: a tiny concentrated edit (one digit) must be flagged, genuine copies and phone
screenshots must not be, and the crop aligner must be sub-pixel."""
import io
import os

import numpy as np
import pytest
from PIL import Image, ImageDraw

from engine import phash, verify_image, config, crop
from engine.phash import to_gray
from .conftest import to_bytes

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = os.path.join(ROOT, "assets")
needs_assets = pytest.mark.skipif(not os.path.isdir(os.path.join(A, "official")), reason="assets missing")


def _registry():
    rows = []
    for f in sorted(os.listdir(os.path.join(A, "official"))):
        if f.endswith(".png"):
            p = os.path.join(A, "official", f)
            rows.append({"id": f[:-4], "title": f[:-4], "issuer": "x", "phash": phash(Image.open(p)), "image_path": p})
    return rows


def _load(p):
    with open(p, "rb") as f:
        return f.read()


def _jpeg(im, q):
    b = io.BytesIO()
    im.convert("RGB").save(b, "JPEG", quality=q)
    return b.getvalue()


def _phone(im, size=(1170, 2532), post_w=1170, xy=(0, 520), q=80):
    c = Image.new("RGB", size, (245, 245, 245))
    d = ImageDraw.Draw(c)
    d.rectangle((0, 0, size[0], 140), fill=(20, 20, 20))
    d.rectangle((0, 140, size[0], 300), fill=(230, 230, 235))
    c.paste(im.convert("RGB").resize((post_w, round(post_w * im.height / im.width)), Image.LANCZOS), xy)
    return _jpeg(c, q)


def _one_digit_edit(im):
    """A digit-sized (10x16 px of 1080x1350) mark near the footer date, white on a dark area, black on a light one."""
    e = im.convert("RGB").copy()
    box = (168, 1262, 178, 1278)
    dark = float(np.asarray(e.crop(box).convert("L")).mean()) < 128
    ImageDraw.Draw(e).rectangle((box[0], box[1], box[2] - 1, box[3] - 1), fill=(255, 255, 255) if dark else (0, 0, 0))
    return e


# ---------------- synthetic (no assets needed) ----------------
def test_tiny_localised_edit_is_altered_not_genuine(registry, loader, official):
    e = official.copy()
    ImageDraw.Draw(e).rectangle((60, 586, 69, 600), fill=(255, 255, 255))   # digit-sized mark inside the date box
    r = verify_image(to_bytes(e), registry, loader)
    assert r["verdict"] == "altered", r
    assert r["max_window_px"] >= config.TAMPER_WIN_PX
    assert r["changed_pct"] < 0.1                                           # global % alone would have missed it
    assert max(max(row) for row in r["heat"]) > 0.5                         # and the heat-map shows where


def test_heavy_jpeg_and_resize_stay_genuine(registry, loader, official):
    for q, s in ((30, 1.0), (50, 0.5), (60, 1.5)):
        im = official.resize((round(official.width * s), round(official.height * s)), Image.LANCZOS)
        r = verify_image(_jpeg(im, q), registry, loader)
        assert r["verdict"] == "genuine", (q, s, r["changed_pct"], r["max_window_px"])


def test_small_crop_is_realigned_not_called_altered(registry, loader, official):
    w, h = official.size
    r = verify_image(_jpeg(official.crop((6, 8, w - 6, h - 8)), 80), registry, loader)
    assert r["verdict"] == "genuine", r


def test_tiny_edit_in_cropped_copy_still_altered(registry, loader, official):
    e = official.copy()
    ImageDraw.Draw(e).rectangle((60, 586, 69, 600), fill=(255, 255, 255))
    w, h = e.size
    r = verify_image(_jpeg(e.crop((6, 8, w - 6, h - 8)), 80), registry, loader)
    assert r["verdict"] == "altered", r


def test_reply_for_localised_edit_has_no_zero_percent():
    from engine import reply_for
    msg = reply_for({"verdict": "altered", "changed_pct": 0.012})
    assert "0.0%" not in msg and "موضعي" in msg


def test_align_is_subpixel(official):
    canvas = Image.new("RGB", (900, 1400), (230, 230, 230))
    canvas.paste(official.resize((540, 720), Image.LANCZOS), (137, 300))
    gray = to_gray(canvas)
    og = to_gray(official)
    box = crop.align(gray, (146, 293, 691, 1055), og, (512, 683))
    for got, want in zip(box, (137, 300, 677, 1020)):
        assert abs(got - want) < 0.6, (box, want)


@needs_assets
@pytest.mark.parametrize("kw", [
    dict(size=(1080, 2340), post_w=1020, xy=(30, 420), q=60),
    dict(size=(1290, 2796), post_w=1290, xy=(0, 380), q=95),
    dict(size=(1170, 2532), post_w=900, xy=(135, 700), q=70),
])
def test_phone_screenshot_geometries_genuine_and_edit_altered(kw):
    reg = _registry()
    for pid in ("public_holiday_notice", "rta_notice"):      # rta_notice has periodic stripes (alignment trap)
        off = Image.open(os.path.join(A, "official", pid + ".png"))
        r = verify_image(_phone(off, **kw), reg, _load)
        assert r["verdict"] == "genuine" and r["matched_id"] == pid, (pid, kw, r["changed_pct"], r["max_window_px"])
        r = verify_image(_phone(_one_digit_edit(off), **kw), reg, _load)
        assert r["verdict"] == "altered" and r["matched_id"] == pid, (pid, kw, r["changed_pct"], r["max_window_px"])


@needs_assets
def test_direct_one_digit_edit_on_real_posts_altered_and_originals_genuine():
    reg = _registry()
    for row in reg:
        off = Image.open(row["image_path"])
        assert verify_image(_jpeg(off, 40), reg, _load)["verdict"] == "genuine", row["id"]
        r = verify_image(_jpeg(_one_digit_edit(off), 60), reg, _load)
        assert r["verdict"] == "altered", (row["id"], r["changed_pct"], r["max_window_px"])


def test_global_brightness_change_is_normalised_but_edit_still_caught(registry, loader, official):
    from PIL import ImageEnhance
    dark = ImageEnhance.Brightness(official).enhance(0.8)
    assert verify_image(_jpeg(dark, 85), registry, loader)["verdict"] == "genuine"
    e = dark.copy()
    ImageDraw.Draw(e).rectangle((60, 586, 69, 600), fill=(255, 255, 255))
    assert verify_image(_jpeg(e, 85), registry, loader)["verdict"] == "altered"
