"""Find an official post inside a larger picture (phone screenshot with status/browser bars,
chat UI around it): multi-scale crop search on pHash, then pixel-accurate box alignment so the
tamper check compares like with like. Only used when the whole-image match fails."""
import numpy as np
from PIL import Image, ImageFilter

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
        if best[0] <= 2:          # near-perfect hash match already found at a larger scale: stop scanning
            break
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


def align(gray, box, official_gray, size):
    """Sub-pixel box refinement.

    `gray` is the full picture (PIL 'L'), `box` a rough (x0,y0,x1,y1) of the post in it, `official_gray` the registry
    image (PIL 'L'), `size` the comparison grid (w, h). Coordinate descent on the box (float coordinates, Lanczos
    resampling straight from a source box) minimising the mean absolute grey difference to the official image.
    Coarse-to-fine: a 48x60 grid first (wide capture range; stops a periodic design such as stripes from locking
    onto the wrong repeat), then the comparison grid, down to ~0.05 source px. Stage 1 keeps the official's aspect
    ratio (moves/scales the box as a whole); stage 2 frees the four edges at fine steps. numpy + Pillow only.
    Returns a float box inside the picture."""
    from . import config
    W, H = gray.size
    size = tuple(size)
    blur = ImageFilter.GaussianBlur(config.BLUR) if config.BLUR else None

    def prep(im):
        return np.asarray(im.filter(blur) if blur else im, dtype=np.float32)

    best = [float(v) for v in box]
    best[0], best[1] = max(0.0, best[0]), max(0.0, best[1])
    best[2], best[3] = min(float(W), best[2]), min(float(H), best[3])
    # Work on a crop around the rough box (cheaper resizes); coordinates are shifted back at the end.
    mx, my = 0.18 * (best[2] - best[0]), 0.18 * (best[3] - best[1])
    ox, oy = max(0, int(best[0] - mx)), max(0, int(best[1] - my))
    ex, ey = min(W, int(best[2] + mx) + 1), min(H, int(best[3] + my) + 1)
    gray = gray.crop((ox, oy, ex, ey))
    W, H = gray.size
    best = [best[0] - ox, best[1] - oy, best[2] - ox, best[3] - oy]
    pyr = {1: gray}                       # pre-reduced copies make the coarse levels cheap
    refs = {}

    def cost(b, sz):
        r = 1
        f = (b[2] - b[0]) / sz[0]
        for cand in (2, 4):
            if f >= 2 * cand:
                r = cand
        if r not in pyr:
            pyr[r] = gray.reduce(r)
        if sz not in refs:
            refs[sz] = prep(official_gray.resize(sz, _LANCZOS))
        a = prep(pyr[r].resize(sz, _LANCZOS, box=tuple(float(v) / r for v in b)))
        return float(np.abs(a - refs[sz]).mean())

    def inside(nb):
        return not (nb[0] < 0 or nb[1] < 0 or nb[2] > W or nb[3] > H or nb[2] - nb[0] < 20 or nb[3] - nb[1] < 20)

    def descend(best, moves, fracs_sizes, rounds):
        for frac, sz in fracs_sizes:
            cur = cost(best, sz)
            for _ in range(rounds):
                improved = False
                w, h = best[2] - best[0], best[3] - best[1]
                for v in moves:
                    nb = [best[i] + v[i] * frac * (w if i % 2 == 0 else h) for i in range(4)]
                    if inside(nb):
                        c = cost(nb, sz)
                        if c < cur - 1e-6:
                            cur, best, improved = c, nb, True
                            w, h = best[2] - best[0], best[3] - best[1]
                if not improved:
                    break
        return best

    asp = official_gray.size[0] / official_gray.size[1]
    cx, cy = (best[0] + best[2]) / 2, (best[1] + best[3]) / 2
    w0 = best[2] - best[0]
    reasp = [cx - w0 / 2, cy - w0 / asp / 2, cx + w0 / 2, cy + w0 / asp / 2]
    if inside(reasp):
        best = reasp
    else:                                  # picture is cropped tighter than the official's aspect: shrink to fit
        k = min(1.0, W / max(1e-6, reasp[2] - reasp[0]), H / max(1e-6, reasp[3] - reasp[1]))
        hw, hh = (reasp[2] - reasp[0]) * k / 2, (reasp[3] - reasp[1]) * k / 2
        cx, cy = min(max(cx, hw), W - hw), min(max(cy, hh), H - hh)
        best = [cx - hw, cy - hh, cx + hw, cy + hh]
    uni = [[1, 0, 1, 0], [-1, 0, -1, 0], [0, 1, 0, 1], [0, -1, 0, -1]]   # shift x / y (units of box w, h)
    for sgn in (-1, 1):
        uni.append([-sgn, -sgn, sgn, sgn])                                 # grow / shrink about the centre
    tiny = (48, max(16, int(round(48 * size[1] / size[0]))))
    mid = (max(16, size[0] // 2), max(16, size[1] // 2))
    plan, f = [(0.04, tiny), (0.015, tiny), (0.006, tiny)], 0.012
    while f * w0 >= 0.3:
        plan.append((f, mid))
        f /= 3
    # Seed: a small grid of shifts and scales around the rough box on the tiny grid, so the descent starts in the right
    # basin even when the rough box is off by several percent (flat or repeating designs have local minima).
    cx, cy = (best[0] + best[2]) / 2, (best[1] + best[3]) / 2
    bw, bh = best[2] - best[0], best[3] - best[1]
    seed, seed_c = best, cost(best, tiny)
    for sc in (0.92, 0.96, 1.0, 1.04, 1.08, 1.12, 1.16):
        for iy in range(-3, 4):
            for ix in range(-3, 4):
                nb = [cx + ix * 0.03 * bw - bw * sc / 2, cy + iy * 0.03 * bh - bh * sc / 2,
                      cx + ix * 0.03 * bw + bw * sc / 2, cy + iy * 0.03 * bh + bh * sc / 2]
                if inside(nb):
                    c = cost(nb, tiny)
                    if c < seed_c:
                        seed, seed_c = nb, c
    best = descend(seed, uni, plan, 8)
    # Stage 2: free edges. Single-edge moves plus compound moves (stretch / shift along one axis): moving one edge
    # alone rescales the whole content, so two edges that are both slightly wrong can only be fixed together.
    free = []
    for i in range(4):
        for sgn in (-1, 1):
            v = [0.0] * 4
            v[i] = sgn
            free.append(v)
    for sgn in (-1, 1):
        free += [[-sgn, 0, sgn, 0], [0, -sgn, 0, sgn], [sgn, 0, sgn, 0], [0, sgn, 0, sgn]]
    best = descend(best, free, [(0.012, mid), (0.004, mid), (0.0013, mid)], 5)
    best = descend(best, free, [(f, size) for f in (0.0006, 0.0002) if f * w0 >= 0.08], 3)
    return (best[0] + ox, best[1] + oy, best[2] + ox, best[3] + oy)
