"""Phone screenshots with UI around the post (status bar, browser bars) must still verify."""
import io
import os

import pytest
from PIL import Image, ImageDraw

from engine import phash, verify_image

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
A = os.path.join(ROOT, "assets")
pytestmark = pytest.mark.skipif(not os.path.isdir(os.path.join(A, "official")), reason="assets missing")


def _registry():
    rows = []
    for f in sorted(os.listdir(os.path.join(A, "official"))):
        if f.endswith(".png"):
            p = os.path.join(A, "official", f)
            rows.append({"id": f[:-4], "title": f[:-4], "issuer": "x", "phash": phash(Image.open(p)), "image_path": p})
    return rows


def _load(p):
    return open(p, "rb").read()


def _phone_frame(src):
    o = Image.open(src).convert("RGB")
    c = Image.new("RGB", (1170, 2532), (245, 245, 245))
    d = ImageDraw.Draw(c)
    d.rectangle((0, 0, 1170, 140), fill=(20, 20, 20))
    d.rectangle((0, 140, 1170, 300), fill=(230, 230, 235))
    c.paste(o.resize((1170, 1462)), (0, 520))
    buf = io.BytesIO()
    c.save(buf, "JPEG", quality=80)
    return buf.getvalue()


def test_phone_screenshot_of_official_is_genuine():
    r = verify_image(_phone_frame(os.path.join(A, "official", "public_holiday_notice.png")), _registry(), _load)
    assert r["verdict"] == "genuine" and r["matched_id"] == "public_holiday_notice"


def test_phone_screenshot_of_doctored_is_altered():
    r = verify_image(_phone_frame(os.path.join(A, "doctored", "public_holiday_notice_doctored_date.png")),
                     _registry(), _load)
    assert r["verdict"] == "altered" and r["matched_id"] == "public_holiday_notice"


@pytest.mark.parametrize("f", ["unrelated/desert_sunset.png", "unrelated/recipe_card.png"])
def test_unrelated_in_phone_frame_stays_unverified(f):
    r = verify_image(_phone_frame(os.path.join(A, f)), _registry(), _load)
    assert r["verdict"] == "unverified"
