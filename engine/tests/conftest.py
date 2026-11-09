import io
import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont

from engine import phash


def _font(n):
    try:
        return ImageFont.load_default(size=n)
    except TypeError:
        return ImageFont.load_default()


def announcement(title="HOLIDAY NOTICE", date="Date: 12 Nov 2026", seed=1, size=(600, 800)):
    rng = np.random.RandomState(seed)
    im = Image.new("RGB", size, (250, 248, 240))
    d = ImageDraw.Draw(im)
    w, h = size
    d.rectangle([0, 0, w, 110], fill=(150, 20, 30))
    d.text((30, 35), title, font=_font(44), fill="white")
    d.rectangle([10, 10, w - 10, h - 10], outline=(20, 20, 20), width=6)
    y = 150
    for i in range(7):
        ln = int(rng.randint(250, 520))
        d.rectangle([40, y, 40 + ln, y + 26], fill=(40, 40, 40))
        y += 55
    d.rectangle([40, 560, 300, 640], fill=(20, 110, 60))
    d.text((50, 580), date, font=_font(34), fill="white")
    d.text((40, 700), "Government Media Office", font=_font(30), fill=(30, 30, 30))
    return im


def unrelated(kind):
    w, h = 600, 800
    rng = np.random.RandomState(100 + kind)
    if kind == 0:   # photo-like noisy gradient
        x = np.linspace(0, 255, w)[None, :] * np.ones((h, 1))
        y = np.linspace(255, 0, h)[:, None] * np.ones((1, w))
        arr = (0.5 * x + 0.5 * y + rng.normal(0, 25, (h, w)))
    elif kind == 1:  # radial blobs
        yy, xx = np.mgrid[0:h, 0:w]
        arr = 128 + 100 * np.sin(xx / 37.0) * np.cos(yy / 53.0) + rng.normal(0, 15, (h, w))
    else:            # big diagonal bands + dark block
        yy, xx = np.mgrid[0:h, 0:w]
        arr = ((xx + yy) // 90 % 2) * 200 + 20.0
        arr[300:600, 100:450] = 30
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    return Image.fromarray(np.stack([arr, arr[::-1], arr[:, ::-1]], axis=2), "RGB")


def to_bytes(im, fmt="PNG", **kw):
    b = io.BytesIO()
    im.save(b, fmt, **kw)
    return b.getvalue()


@pytest.fixture(scope="session")
def official():
    return announcement()


@pytest.fixture(scope="session")
def store(official):
    other = announcement("WEEKEND NOTICE", "Date: 5 Dec 2026", seed=7)
    return {"official/holiday.png": to_bytes(official), "official/weekend.png": to_bytes(other)}


@pytest.fixture
def registry(store):
    return [
        {"id": "public_holiday_notice", "title": "Public holiday notice", "issuer": "Gov Media Office",
         "phash": phash(store["official/holiday.png"]), "image_path": "official/holiday.png"},
        {"id": "weekend_notice", "title": "Weekend notice", "issuer": "MOHRE",
         "phash": phash(store["official/weekend.png"]), "image_path": "official/weekend.png"},
    ]


@pytest.fixture
def loader(store):
    return lambda p: store[p]
