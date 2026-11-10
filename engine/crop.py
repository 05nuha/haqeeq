"""Find an official post inside a larger picture (phone screenshot with status/browser bars,
chat UI around it): multi-scale crop search on pHash, then pixel-accurate box alignment so the
tamper check compares like with like. Only used when the whole-image match fails."""
import numpy as np
from PIL import Image

from .phash import _C, to_gray

_LANCZOS = getattr(Image, "Resampling", Image).LANCZOS
ASPECTS = (0.8, 0.75, 0.85, 0.7, 1.0, 0.5625, 1.25)


def _bits_from_arr(a32):
    low = (_C @ a32 @ _C.T)[:8, :8].flatten()
    return low > np.median(low)


def _hex_bits(h):
    return np.array([c == "1" for c in bin(int(h, 16))[2:].zfill(64)], bool)


def search(img, rows):
    """-> (distance, row, box_in_full_image) for the best crop matching any row's phash."""
    targets = [(r, _hex_bits(r["phash"])) for r in rows if r.get("phash")]
    if not targets:
        return 64, None, None
    g = to_gray(img)
    W, H = g.size
    sc = 400.0 / max(W, H)
    small = g.resize((max(1, int(W * sc)), max(1, int(H * sc))))
    w, h = small.size

    def score(x, y, cw, ch):
        a = np.asarray(small.crop((int(x), int(y), int(x + cw), int(y + ch))).resize((32, 32), _LANCZOS), float)
        b = _bits_from_arr(a)
        d, r = min(((int((b != t).sum()), i) for i, (_r, t) in enumerate(targets)))
        return d, targets[r][0]

    best = (65, None, None)
    for s in np.arange(1.0, 0.44, -0.06):
        for ar in ASPECTS:
            cw = s * w
            ch = cw / ar
            if ch > h:
                ch = s * h
                cw = ch * ar
            if cw < 20 or ch < 20:
                continue
            for y in np.arange(0, h - ch + 1, max(2.0, 0.04 * h)):
                for x in np.arange(0, w - cw + 1, max(2.0, 0.04 * w)):
                    d, r = score(x, y, cw, ch)
                    if d < best[0]:
                        best = (d, r, (x, y, cw, ch))
    d, r, (x, y, cw, ch) = best
    for _ in range(2):                       # local refinement
        for ds in (-0.03, -0.015, 0, 0.015, 0.03):
            for dx in (-0.02, -0.01, 0, 0.01, 0.02):
                for dy in (-0.02, -0.01, 0, 0.01, 0.02):
                    ncw, nch, nx, ny = cw * (1 + ds), ch * (1 + ds), x + dx * w, y + dy * h
                    if nx < 0 or ny < 0 or nx + ncw > w or ny + nch > h:
                        continue
                    dd, rr = score(nx, ny, ncw, nch)
                    if dd < d:
                        d, r, (x, y, cw, ch) = dd, rr, (nx, ny, ncw, nch)
    box = tuple(int(v / sc) for v in (x, y, x + cw, y + ch))
    return d, r, box


def align(gray, box, official_grey, grid=128):
    """Refine box edges to minimise mean abs grey diff vs the official image (coarse to fine)."""
    ref = np.asarray(Image.fromarray(np.clip(official_grey, 0, 255).astype("uint8")).resize((grid, grid)), float)
    W, H = gray.size

    def cost(b):
        a = np.asarray(gray.crop(tuple(int(round(v)) for v in b)).resize((grid, grid)), float)
        return float(np.abs(a - ref).mean())

    best_c, best_b = cost(box), tuple(box)
    for frac in (0.03, 0.012, 0.005, 0.002):
        w, h = best_b[2] - best_b[0], best_b[3] - best_b[1]
        improved = True
        while improved:
            improved = False
            for i, step in ((0, w * frac), (1, h * frac), (2, w * frac), (3, h * frac)):
                for sgn in (-1, 1):
                    nb = list(best_b)
                    nb[i] += sgn * step
                    if nb[0] < 0 or nb[1] < 0 or nb[2] > W or nb[3] > H or nb[2] - nb[0] < 20 or nb[3] - nb[1] < 20:
                        continue
                    c = cost(nb)
                    if c < best_c - 1e-6:
                        best_c, best_b, improved = c, tuple(nb), True
    return tuple(int(round(v)) for v in best_b)
