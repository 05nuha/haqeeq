"""Image verification: pHash match against registry, then a localised pixel-level tamper check.

Tamper check (v2): both images are resized to a common fine grid (FINE_W wide), lightly blurred, and diffed.
The verdict is `altered` when EITHER the global changed fraction exceeds TAMPER_PCT OR any small WIN x WIN
window holds at least TAMPER_WIN_PX changed pixels. The second rule is what catches a one-digit date or amount
edit, which is a tiny share of the picture but concentrated in one spot. Genuine copies (recompression, resize,
screenshots) spread tiny differences thinly, so they never fill a window. A copy that was cropped/shifted slightly
is re-aligned before it is called altered. Alignment only moves the comparison box (4 numbers); it cannot make a
changed digit disappear.
"""
import io
import numpy as np
from PIL import Image, ImageFilter

from . import config
from .phash import phash, hamming, to_gray, load_pil

_LANCZOS = getattr(Image, "Resampling", Image).LANCZOS
_OFFICIAL_CACHE = {}   # image_path -> grey PIL image
_REF_CACHE = {}        # (image_path, size) -> blurred float array of the official at that grid


def _fine_size(official, src_w):
    """Comparison grid: FINE_W wide, but never wider than the picture we were given (upscaling a small copy
    would compare invented detail against real detail), and never narrower than 256."""
    w, h = official.size
    gw = int(min(config.FINE_W, max(256, src_w)))
    return gw, max(16, int(round(gw * h / w)))


def _fine(gray, size, box=None):
    """Resize (optionally from a float source box) to the fine grid and blur -> float array."""
    im = gray.resize(size, _LANCZOS, box=box) if box is not None else gray.resize(size, _LANCZOS)
    if config.BLUR:
        im = im.filter(ImageFilter.GaussianBlur(config.BLUR))
    return np.asarray(im, dtype=np.float32)


def _official(path, load_image):
    g = _OFFICIAL_CACHE.get(path)
    if g is None:
        g = to_gray(Image.open(io.BytesIO(load_image(path))))
        g.load()
        _OFFICIAL_CACHE[path] = g
    return g


def _ref(path, g, size):
    key = (path, size)
    a = _REF_CACHE.get(key)
    if a is None:
        a = _REF_CACHE[key] = _fine(g, size)
    return a


def _box_sum_max(m, k):
    """Largest count of True pixels in any k x k window (integral image)."""
    if m.shape[0] < k or m.shape[1] < k:
        return int(m.sum())
    c = np.zeros((m.shape[0] + 1, m.shape[1] + 1), dtype=np.int32)
    np.cumsum(np.cumsum(m, 0, dtype=np.int32), 1, out=c[1:, 1:])
    return int((c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]).max())


def _window(gw):
    """(window side, changed pixels needed) at grid width gw; scaled down from the FINE_W reference grid."""
    k = gw / config.FINE_W
    return max(5, int(round(config.WIN * k))), max(3, int(round(config.TAMPER_WIN_PX * k * k)))


def _normalise(a, b):
    """Undo a global brightness/contrast change of the copy: robust least-squares fit a*x+b -> reference, ignoring
    the pixels that disagree (a real edit is excluded from the fit, so it cannot be 'normalised away')."""
    x, y = a.ravel(), b.ravel()
    keep = np.ones(x.shape, bool)
    gain, bias = 1.0, 0.0
    for _ in range(3):
        xs, ys = x[keep], y[keep]
        vx = float(xs.var())
        if xs.size < 100 or vx < 1.0:
            break
        gain = float(((xs - xs.mean()) * (ys - ys.mean())).mean() / vx)
        gain = min(1.6, max(0.6, gain))                 # only moderate global changes are corrected
        bias = float(ys.mean() - gain * xs.mean())
        keep = np.abs(gain * x + bias - y) < config.PIXEL_THRESH
    return gain * a + bias


def _score(a, b):
    """-> (changed mask, global % changed, largest changed count in a window, pixels needed to call it tampered)."""
    a = _normalise(a, b)
    changed = np.abs(a - b) > config.PIXEL_THRESH
    k, need = _window(a.shape[1])
    return changed, float(changed.mean() * 100), _box_sum_max(changed, k), need


def _tampered(pct, win, need):
    return pct > config.TAMPER_PCT or win >= need


def _heat(changed):
    """16x16 grid; a cell reaches 1.0 once ~12 of its pixels changed, so one edited digit is visible."""
    H, W = changed.shape
    ys = np.linspace(0, H, 17).astype(int)
    xs = np.linspace(0, W, 17).astype(int)
    return [[float(min(1.0, changed[ys[r]:ys[r + 1], xs[c]:xs[c + 1]].sum() / 12.0)) for c in range(16)]
            for r in range(16)]


def _spread_cells(changed):
    """How many of the 16x16 cells hold >= 3 changed pixels. A misaligned/cropped copy lights up many cells (every
    edge and letter shifts); a genuine small edit touches only a few, so it skips the (slower) re-alignment."""
    H, W = changed.shape
    ys = np.linspace(0, H, 17).astype(int)
    xs = np.linspace(0, W, 17).astype(int)
    return sum(int(changed[ys[r]:ys[r + 1], xs[c]:xs[c + 1]].sum() >= 3) for r in range(16) for c in range(16))


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

    gray = to_gray(img)
    W, H = gray.size
    box = None          # source box (x0,y0,x1,y1) of the post inside the picture; None = the whole picture
    if (best is None or dist > config.MATCH_THRESH) and config.CROP_SEARCH:
        # The post may sit inside a bigger picture (phone screenshot with status/browser bars).
        from . import crop
        cd, crow, cbox = crop.search(img, list(registry or ()) + list(known_fakes or ()))
        if crow is not None and cd <= config.CROP_MATCH_THRESH:
            if crow in list(known_fakes or ()):
                return {"verdict": "unverified", "matched_id": None, "distance": int(cd),
                        "changed_pct": None, "heat": None,
                        "detail": crow.get("detail") or crow.get("title", "")}
            og = _official(crow["image_path"], load_image)
            box = crop.align(gray, cbox, og, _fine_size(og, cbox[2] - cbox[0]))
            best, dist = crow, cd

    if best is None or dist > config.MATCH_THRESH:
        fake, fd = _best(h, known_fakes)
        if fake is not None and fd <= config.MATCH_THRESH:
            return {"verdict": "unverified", "matched_id": None, "distance": int(fd),
                    "changed_pct": None, "heat": None, "detail": fake.get("detail") or fake.get("title", "")}
        return {"verdict": "unverified", "matched_id": None, "distance": int(dist),
                "changed_pct": None, "heat": None, "detail": "No match in the official registry"}

    og = _official(best["image_path"], load_image)
    size = _fine_size(og, (box[2] - box[0]) if box is not None else W)
    b = _ref(best["image_path"], og, size)
    changed, pct, win, need = _score(_fine(gray, size, box), b)
    if _tampered(pct, win, need) and box is None and _spread_cells(changed) >= config.REALIGN_CELLS:
        # Maybe the copy was only cropped/shifted a little: re-align once and keep the better score.
        from . import crop
        # (a) the post sits inside the picture with a margin, (b) the picture is a crop of the post.
        try:
            box2 = crop.align(gray, (0.0, 0.0, float(W), float(H)), og, size)
            c2, p2, w2, _n = _score(_fine(gray, size, box2), b)
            if (p2, w2) < (pct, win):
                changed, pct, win, box = c2, p2, w2, box2
        except (ValueError, SystemError):      # degenerate box: keep the unaligned score (never raise on a user image)
            pass
        if _tampered(pct, win, need):
            try:
                ow, oh = og.size
                sub = crop.align(og, (0.0, 0.0, float(ow), float(oh)), gray, size)
                c3, p3, w3, _n = _score(_fine(gray, size), _fine(og, size, sub))
                if (p3, w3) < (pct, win):
                    changed, pct, win = c3, p3, w3
            except (ValueError, SystemError):
                pass
    base = {"matched_id": best["id"], "distance": int(dist), "changed_pct": round(pct, 3),
            "heat": _heat(changed), "max_window_px": win}
    if box is not None and tuple(int(round(v)) for v in box) != (0, 0, W, H):
        base["crop_box"] = [int(round(v)) for v in box]
    if not _tampered(pct, win, need):
        return {"verdict": "genuine", **base, "detail": f"Matches {best['title']} ({best['issuer']})"}
    where = f"{pct:.1f}% changed" if pct >= 0.1 else "localised edit"
    return {"verdict": "altered", **base, "detail": f"Altered: {best['title']} — {where}"}
