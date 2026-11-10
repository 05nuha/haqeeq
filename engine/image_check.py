"""Image verification: pHash match against registry, then per-pixel tamper check."""
import io
import numpy as np
from PIL import Image

from . import config
from .phash import phash, hamming, to_gray, load_pil

_GREY_CACHE = {}   # image_path -> 256x256 float array of the official image


def _grey(img):
    return np.asarray(to_gray(img).resize((config.GRID, config.GRID)), dtype=float)


def _official_grey(path, load_image):
    arr = _GREY_CACHE.get(path)
    if arr is None:
        arr = _grey(Image.open(io.BytesIO(load_image(path))))
        _GREY_CACHE[path] = arr
    return arr


def _best(h, rows):
    best, bd = None, 64
    for r in rows or ():
        if not r.get("phash"):
            continue
        d = hamming(h, r["phash"])
        if best is None or d < bd:
            best, bd = r, d
    return best, bd


def verify_image(image_bytes, registry, load_image, known_fakes=()):
    img = load_pil(image_bytes)
    img.load()
    h = phash(img)
    best, dist = _best(h, registry)

    crop_box = None
    if (best is None or dist > config.MATCH_THRESH) and config.CROP_SEARCH:
        # The post may sit inside a bigger picture (phone screenshot with status/browser bars).
        from . import crop
        cd, crow, cbox = crop.search(img, list(registry or ()) + list(known_fakes or ()))
        if crow is not None and cd <= config.CROP_MATCH_THRESH:
            if crow in list(known_fakes or ()):
                return {"verdict": "unverified", "matched_id": None, "distance": int(cd),
                        "changed_pct": None, "heat": None,
                        "detail": crow.get("detail") or crow.get("title", "")}
            gray = to_gray(img)
            crop_box = crop.align(gray, cbox, _official_grey(crow["image_path"], load_image))
            img, best, dist = gray.crop(crop_box), crow, cd

    if best is None or dist > config.MATCH_THRESH:
        fake, fd = _best(h, known_fakes)
        if fake is not None and fd <= config.MATCH_THRESH:
            return {"verdict": "unverified", "matched_id": None, "distance": int(fd),
                    "changed_pct": None, "heat": None, "detail": fake.get("detail") or fake.get("title", "")}
        return {"verdict": "unverified", "matched_id": None, "distance": int(dist),
                "changed_pct": None, "heat": None, "detail": "No match in the official registry"}

    a = _grey(img)
    b = _official_grey(best["image_path"], load_image)
    changed = np.abs(a - b) > config.PIXEL_THRESH
    pct = float(changed.mean() * 100)
    step = config.GRID // 16
    heat = [[float(changed[r*step:(r+1)*step, c*step:(c+1)*step].mean()) for c in range(16)]
            for r in range(16)]
    base = {"matched_id": best["id"], "distance": int(dist), "changed_pct": round(pct, 3), "heat": heat}
    if crop_box is not None:
        base["crop_box"] = list(crop_box)
    if pct <= config.TAMPER_PCT:
        return {"verdict": "genuine", **base, "detail": f"Matches {best['title']} ({best['issuer']})"}
    return {"verdict": "altered", **base, "detail": f"Altered: {best['title']} — {pct:.1f}% changed"}
