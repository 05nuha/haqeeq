"""Reproducible controlled-test evaluation of the REAL Haqeeq image engine.

    python scripts/eval/run_eval.py [--workers 4] [--out assets/eval]

Generates labelled images from the 8 official posts (genuine transforms, controlled edits re-rendered
with scripts/make_assets.py, unrelated/unmatched images), runs engine.verify_image on each, writes
assets/eval/results.json + summary.json and prints tables. Deterministic (fixed seeds).
Engine code and defaults are NOT modified. Everything here is a CONTROLLED TEST on synthetic,
same-renderer images; it is not accuracy in the wild.
"""
import argparse
import copy
import io
import json
import os
import random
import statistics
import collections
import sys
import time
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
if os.environ.get("HAQEEQ_ENGINE_ROOT"):       # evaluate another checkout's engine/ (e.g. the BEFORE version)
    sys.path.insert(0, os.environ["HAQEEQ_ENGINE_ROOT"])
import make_assets as MA  # noqa: E402  (re-use fonts/layouts)
from engine import config, phash, verify_image  # noqa: E402
V2 = hasattr(config, "TAMPER_WIN_PX")           # engine v2: localised window rule in addition to the global %

A = os.path.join(ROOT, "assets")
SWEEP = [0.01, 0.02, 0.03, 0.04, 0.06, 0.1]
SWEEP_EXTRA = [0.0, 0.002, 0.005]          # exploratory finer values below the requested range
PIX_EXPLORE = [25, 35, 55]                 # exploratory PIXEL_THRESH values (direct-match, non-screenshot images only)
DEFAULTS = dict(MATCH_THRESH=config.MATCH_THRESH, PIXEL_THRESH=config.PIXEL_THRESH,
                TAMPER_PCT=config.TAMPER_PCT, CROP_MATCH_THRESH=config.CROP_MATCH_THRESH)


# ---------------------------------------------------------------- image helpers
def jpeg(img, q):
    b = io.BytesIO()
    img.convert("RGB").save(b, "JPEG", quality=q)
    return b.getvalue()


def png(img):
    b = io.BytesIO()
    img.save(b, "PNG")
    return b.getvalue()


def phone_screenshot(img, q=80):
    """SIMULATED phone screenshot: post resized into a 1170x2532 canvas with status/browser bars."""
    c = Image.new("RGB", (1170, 2532), (245, 245, 245))
    d = ImageDraw.Draw(c)
    d.rectangle((0, 0, 1170, 140), fill=(20, 20, 20))
    d.rectangle((0, 140, 1170, 300), fill=(230, 230, 235))
    d.rectangle((0, 2380, 1170, 2532), fill=(235, 235, 240))
    c.paste(img.convert("RGB").resize((1170, 1462), Image.LANCZOS), (0, 520))
    return jpeg(c, q)


def whatsapp_style(img):
    img = img.convert("RGB")
    s = 1600 / max(img.size)
    if s < 1:
        img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    return jpeg(img, 70)


def scale_jpeg(img, s, q=85):
    img = img.convert("RGB")
    return jpeg(img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS), q)


def brightness_contrast(img):
    img = ImageEnhance.Brightness(img.convert("RGB")).enhance(1.06)
    return jpeg(ImageEnhance.Contrast(img).enhance(0.95), 92)


def lossless(img):
    return png(img.convert("RGB"))


GENUINE_TX = [
    ("lossless_copy", lossless),
    ("jpeg_q80", lambda i: jpeg(i, 80)),
    ("jpeg_q60", lambda i: jpeg(i, 60)),
    ("jpeg_q40", lambda i: jpeg(i, 40)),
    ("downscale_0.75_jpeg", lambda i: scale_jpeg(i, 0.75)),
    ("downscale_0.5_jpeg", lambda i: scale_jpeg(i, 0.5)),
    ("simulated_phone_screenshot", phone_screenshot),
    ("brightness_contrast", brightness_contrast),
    ("whatsapp_style_1600_q70", whatsapp_style),
]
# Transforms applied to EDITED images (as they arrive via WhatsApp)
EDIT_TX = [("lossless", lossless), ("jpeg_q60", lambda i: jpeg(i, 60)),
           ("simulated_phone_screenshot", phone_screenshot)]


# ---- extended variants (reported separately; the base 325-image set above is unchanged so runs stay comparable)
def _canvas_shot(img, size, post_w, xy_top, bars, q, fmt="jpeg", bg=(245, 245, 245)):
    c = Image.new("RGB", size, bg)
    d = ImageDraw.Draw(c)
    for box, col in bars:
        d.rectangle(box, fill=col)
    ph = round(post_w * img.height / img.width)
    c.paste(img.convert("RGB").resize((post_w, ph), Image.LANCZOS), xy_top)
    return png(c) if fmt == "png" else jpeg(c, q)


def shot_small_q60(img):      # smaller phone, post narrower than the screen, q60
    return _canvas_shot(img, (1080, 2340), 1020, (30, 420),
                        [((0, 0, 1080, 120), (20, 20, 20)), ((0, 120, 1080, 260), (232, 232, 236))], 60)


def shot_png(img):            # lossless full-width screenshot, different bar heights
    return _canvas_shot(img, (1290, 2796), 1290, (0, 380),
                        [((0, 0, 1290, 170), (10, 10, 10)), ((0, 170, 1290, 340), (225, 225, 230))], 0, "png")


def shot_chat_bubble(img):    # post inside a dark chat UI with margins (not full width), q70
    return _canvas_shot(img, (1170, 2532), 820, (175, 700),
                        [((0, 0, 1170, 150), (30, 36, 40)), ((150, 660, 1020, 2100), (255, 255, 255))],
                        70, bg=(14, 20, 24))


def shot_tablet(img):         # tablet-sized canvas, post centred at an odd scale, q90
    return _canvas_shot(img, (1640, 2360), 903, (368, 200), [((0, 0, 1640, 90), (240, 240, 240))], 90, bg=(200, 200, 205))


def crop_1pct(img):           # 1% of each border cropped off, then q80
    img = img.convert("RGB")
    mx, my = round(img.width * 0.01), round(img.height * 0.01)
    return jpeg(img.crop((mx, my, img.width - mx, img.height - my)), 80)


def jpeg_q30(img):
    return jpeg(img, 30)


def whatsapp_q50_1280(img):
    img = img.convert("RGB")
    s = 1280 / max(img.size)
    return jpeg(img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS) if s < 1 else img, 50)


EXT_GENUINE_TX = [("shot_small_q60", shot_small_q60), ("shot_png_1290", shot_png),
                  ("shot_chat_bubble_q70", shot_chat_bubble), ("shot_tablet_q90", shot_tablet),
                  ("crop_1pct_q80", crop_1pct), ("jpeg_q30", jpeg_q30), ("whatsapp_q50_1280", whatsapp_q50_1280)]
EXT_EDIT_TX = [("shot_small_q60", shot_small_q60), ("shot_png_1290", shot_png),
               ("shot_chat_bubble_q70", shot_chat_bubble), ("crop_1pct_q80", crop_1pct),
               ("whatsapp_q50_1280", whatsapp_q50_1280)]
EXT_EDIT_TYPES = ("date_1digit", "date_2digit", "key_line_1digit", "number_changed")
EXT_SHOT_NAMES = {"shot_small_q60", "shot_png_1290", "shot_chat_bubble_q70", "shot_tablet_q90"}


# ---------------------------------------------------------------- edits
def _digits_swap(s, mode):
    """mode 'one': change the last digit found; 'all': change every digit."""
    out, idx = list(s), [i for i, c in enumerate(s) if c.isdigit()]
    if not idx:
        return None
    if mode == "one":
        i = idx[-1]
        out[i] = str((int(s[i]) + 3) % 10)
    else:
        for i in idx:
            out[i] = str((int(s[i]) + 3) % 10)
    return "".join(out)


def _alt_date(date, n):
    """n digits changed in the footer date (YYYY-MM-DD)."""
    d = list(date)
    pos = [9, 8][:n]            # day digits, last first
    for p in pos:
        d[p] = str((int(d[p]) + 3) % 10)
    return "".join(d)


ALT_HEAD = "إلغاء جميع الإجراءات المعلنة سابقاً بقرار عاجل جديد"
SWAP_WORD = "مؤجلة"


def make_edits(p, donor, seed):
    """-> list of (edit_type, size_label, PIL image). Re-rendered with the same renderer."""
    out = []
    rnd = random.Random(seed)
    base = MA.render_post(p)

    q = copy.deepcopy(p); q["date"] = _alt_date(p["date"], 1)
    out.append(("date_1digit", "tiny", MA.render_post(q)))
    q = copy.deepcopy(p); q["date"] = _alt_date(p["date"], 2)
    out.append(("date_2digit", "tiny", MA.render_post(q)))

    k1 = _digits_swap(p["key"], "one")
    if k1 is not None:
        out.append(("key_line_1digit", "small", MA.render_post(p, key=k1)))
    # changed amount/number: all digits of the key line, else of the body text (weekend notice has none in key)
    kn = _digits_swap(p["key"], "all")
    if kn is not None:
        out.append(("number_changed", "small", MA.render_post(p, key=kn)))
    else:
        q = copy.deepcopy(p); q["body"] = _digits_swap(p["body"], "all")
        out.append(("number_changed", "small", MA.render_post(q)))

    q = copy.deepcopy(p)
    w = q["body"].split()
    w[len(w) // 2] = SWAP_WORD
    q["body"] = " ".join(w)
    out.append(("word_changed_body", "small", MA.render_post(q)))

    W, H = base.size
    for frac in (0.02, 0.05, 0.10):
        area = frac * W * H
        pw = int((area * 1.6) ** 0.5); ph = int(area / pw)
        sx = rnd.randint(0, W - pw); sy = rnd.randint(0, H - ph)
        dx = rnd.randint(0, W - pw); dy = rnd.randint(0, H - ph)
        img = base.copy()
        img.paste(donor.crop((sx, sy, sx + pw, sy + ph)), (dx, dy))
        out.append((f"patch_{int(frac*100)}pct", f"{int(frac*100)}% area", img))

    q = copy.deepcopy(p); q["head"] = ALT_HEAD
    out.append(("headline_replaced", "large", MA.render_post(q, key=_digits_swap(p["key"], "all") or p["key"],
                                                            key2="تم تعديل هذا الإشعار")))
    return out


def synthetic_unrelated(seed=1234, n=20):
    rng = np.random.RandomState(seed)
    imgs = []
    W, H = 1080, 1350
    for i in range(n):
        kind = i % 4
        if kind == 0:   # noise
            a = rng.randint(0, 256, (H // 4, W // 4, 3), dtype=np.uint8)
            im = Image.fromarray(a).resize((W, H), Image.NEAREST)
        elif kind == 1:  # gradient
            gx = np.linspace(0, 1, W)[None, :, None]; gy = np.linspace(0, 1, H)[:, None, None]
            c = rng.rand(3, 3)
            a = (255 * (c[0] * gx + c[1] * gy + c[2] * gx * gy) / 3).clip(0, 255).astype(np.uint8)
            im = Image.fromarray(a)
        elif kind == 2:  # blobs
            im = Image.new("RGB", (W, H), tuple(int(v) for v in rng.randint(0, 256, 3)))
            d = ImageDraw.Draw(im)
            for _ in range(12):
                x, y, r = rng.randint(0, W), rng.randint(0, H), rng.randint(60, 300)
                d.ellipse((x - r, y - r, x + r, y + r), fill=tuple(int(v) for v in rng.randint(0, 256, 3)))
        else:            # blocks / stripes
            im = Image.new("RGB", (W, H), (255, 255, 255))
            d = ImageDraw.Draw(im)
            for _ in range(15):
                x, y = rng.randint(0, W), rng.randint(0, H)
                d.rectangle((x, y, x + rng.randint(80, 500), y + rng.randint(40, 400)),
                            fill=tuple(int(v) for v in rng.randint(0, 256, 3)))
        imgs.append((["noise", "gradient", "blobs", "blocks"][kind], im))
    return imgs


# ---------------------------------------------------------------- worker
_REG = None


def _load(p):
    with open(p, "rb") as f:
        return f.read()


def _init():
    global _REG
    _REG = []
    for f in sorted(os.listdir(os.path.join(A, "official"))):
        if f.endswith(".png"):
            p = os.path.join(A, "official", f)
            _REG.append({"id": f[:-4], "title": f[:-4], "issuer": "x", "phash": phash(Image.open(p)), "image_path": p})


def _run(task):
    meta, data = task
    reg = [r for r in _REG if r["id"] != meta.get("exclude")]
    t = time.perf_counter()
    r = verify_image(data, reg, _load)
    dt = time.perf_counter() - t
    return {**meta, "verdict": r["verdict"], "matched_id": r["matched_id"], "distance": r["distance"],
            "changed_pct": r["changed_pct"], "win": r.get("max_window_px"), "ms": round(dt * 1000, 1), "bytes": len(data)}


# ---------------------------------------------------------------- build tasks
def build_tasks():
    posts = {p["id"]: p for p in MA.POSTS}
    ids = [p["id"] for p in MA.POSTS]
    off = {i: Image.open(os.path.join(A, "official", i + ".png")).convert("RGB") for i in ids}
    tasks, samples = [], {}

    def add(meta, data, sample_key=None):
        tasks.append((meta, data))
        if sample_key and sample_key not in samples:
            samples[sample_key] = data

    for i in ids:
        for name, fn in GENUINE_TX:
            add(dict(group="genuine", kind=name, post=i, expected="genuine"), fn(off[i]),
                f"genuine_{name}" if i == ids[0] else None)
    for n, i in enumerate(ids):
        donor = off[ids[(n + 3) % len(ids)]]
        for etype, size, img in make_edits(posts[i], donor, seed=100 + n):
            for tname, fn in EDIT_TX:
                add(dict(group="edit", kind=etype, size=size, transform=tname, post=i, expected="altered"),
                    fn(img), f"edit_{etype}_{tname}" if i == ids[0] else None)
    # extended variants (separate groups)
    for i in ids:
        for name, fn in EXT_GENUINE_TX:
            add(dict(group="genuine_ext", kind=name, post=i, expected="genuine"), fn(off[i]))
    for n, i in enumerate(ids):
        donor = off[ids[(n + 3) % len(ids)]]
        for etype, size, img in make_edits(posts[i], donor, seed=100 + n):
            if etype not in EXT_EDIT_TYPES:
                continue
            for tname, fn in EXT_EDIT_TX:
                add(dict(group="edit_ext", kind=etype, size=size, transform=tname, post=i, expected="altered"), fn(img))
    # unrelated / unmatched
    for sub, group in (("fakes", "fake_rumour"), ("unrelated", "unrelated_art")):
        for f in sorted(os.listdir(os.path.join(A, sub))):
            add(dict(group=group, kind=f, post=None, expected="unverified"), _load(os.path.join(A, sub, f)))
    for n, (kind, im) in enumerate(synthetic_unrelated()):
        add(dict(group="synthetic", kind=f"{kind}_{n}", post=None, expected="unverified"), jpeg(im, 85))
    for i in ids:   # leave-one-out: the post is NOT in the registry
        add(dict(group="leave_one_out", kind="lossless", post=i, exclude=i, expected="unverified"), lossless(off[i]))
        add(dict(group="leave_one_out", kind="simulated_phone_screenshot", post=i, exclude=i,
                 expected="unverified"), phone_screenshot(off[i]))
    return tasks, samples


# ---------------------------------------------------------------- analysis
def verdict_at(rec, thr):
    """Verdict at a given TAMPER_PCT. TAMPER_PCT is only used in the final comparison, so for matched
    images this is exact (spot-checked against real re-runs in main())."""
    if rec["changed_pct"] is None or (V2 and thr == config.TAMPER_PCT):
        return rec["verdict"]
    return "genuine" if rec["changed_pct"] <= thr else "altered"


def rate(n, d):
    return None if d == 0 else round(100.0 * n / d, 2)


def metrics(res, thr):
    V = lambda r: verdict_at(r, thr)
    g = [r for r in res if r["group"] == "genuine"]
    e = [r for r in res if r["group"] == "edit"]
    u = [r for r in res if r["group"] in ("fake_rumour", "unrelated_art", "synthetic", "leave_one_out")]
    m = dict(tamper_pct=thr)
    m["genuine_n"] = len(g)
    m["genuine_recall_pct"] = rate(sum(V(r) == "genuine" and r["matched_id"] == r["post"] for r in g), len(g))
    m["false_altered_on_genuine_pct"] = rate(sum(V(r) == "altered" for r in g), len(g))
    m["genuine_called_unverified_pct"] = rate(sum(V(r) == "unverified" for r in g), len(g))
    m["genuine_wrong_post_matched"] = sum(r["matched_id"] not in (None, r["post"]) for r in g)
    m["edit_n"] = len(e)
    m["edit_detection_pct"] = rate(sum(V(r) == "altered" for r in e), len(e))
    m["edit_flagged_not_genuine_pct"] = rate(sum(V(r) != "genuine" for r in e), len(e))
    m["edit_false_genuine_n"] = sum(V(r) == "genuine" for r in e)
    m["edit_false_genuine_pct"] = rate(m["edit_false_genuine_n"], len(e))
    m["edit_called_unverified_n"] = sum(V(r) == "unverified" for r in e)
    m["unmatched_n"] = len(u)
    m["unrelated_false_match_pct"] = rate(sum(V(r) in ("genuine", "altered") for r in u), len(u))
    m["unrelated_false_genuine_n"] = sum(V(r) == "genuine" for r in u)
    # correct post matched (all images whose source post is in the registry)
    inreg = g + e
    m["correct_post_matched_pct"] = rate(sum(r["matched_id"] == r["post"] for r in inreg), len(inreg))
    return m


def ext_summary(res):
    g = [r for r in res if r["group"] == "genuine_ext"]
    e = [r for r in res if r["group"] == "edit_ext"]
    out = dict(genuine_n=len(g), genuine_called_genuine=sum(r["verdict"] == "genuine" and r["matched_id"] == r["post"] for r in g),
               genuine_called_altered=sum(r["verdict"] == "altered" for r in g),
               genuine_called_unverified=sum(r["verdict"] == "unverified" for r in g),
               edit_n=len(e), edit_called_altered=sum(r["verdict"] == "altered" for r in e),
               edit_called_unverified=sum(r["verdict"] == "unverified" for r in e),
               edit_false_genuine=sum(r["verdict"] == "genuine" for r in e))
    byg, bye = {}, {}
    for r in g:
        c = byg.setdefault(r["kind"], collections.Counter())
        c[r["verdict"]] += 1
    for r in e:
        c = bye.setdefault(r["transform"], collections.Counter())
        c[r["verdict"]] += 1
    out["genuine_by_transform"] = {k: dict(v) for k, v in byg.items()}
    out["edit_by_transform"] = {k: dict(v) for k, v in bye.items()}
    return out


def group_table(res, thr, keyf, groups):
    rows = {}
    for r in res:
        if r["group"] not in groups:
            continue
        k = keyf(r)
        c = rows.setdefault(k, dict(n=0, genuine=0, altered=0, unverified=0, wrong=0))
        v = verdict_at(r, thr)
        c["n"] += 1
        c[v] += 1
        c["wrong"] += int(r["matched_id"] not in (None, r["post"]) and r["post"] is not None)
    return rows


def timing(res):
    ext_shots = [r for r in res if r["group"].endswith("_ext") and (r["kind"] in EXT_SHOT_NAMES or r.get("transform") in EXT_SHOT_NAMES)]
    res = [r for r in res if not r["group"].endswith("_ext")]      # base set only, comparable with older runs

    def st(xs):
        if not xs:
            return None
        xs = sorted(xs)
        return dict(n=len(xs), median_ms=round(statistics.median(xs), 1),
                    p95_ms=round(xs[min(len(xs) - 1, int(0.95 * len(xs)))], 1), max_ms=round(xs[-1], 1))
    return dict(extended_screenshots=st([r["ms"] for r in ext_shots]),
                matched=st([r["ms"] for r in res if r["matched_id"]]),
                unmatched=st([r["ms"] for r in res if not r["matched_id"]]),
                matched_direct_phash=st([r["ms"] for r in res if r["matched_id"] and
                                         r["kind"] != "simulated_phone_screenshot" and
                                         r.get("transform") != "simulated_phone_screenshot"]),
                matched_via_crop_search=st([r["ms"] for r in res if r["matched_id"] and (
                    r["kind"] == "simulated_phone_screenshot" or r.get("transform") == "simulated_phone_screenshot")]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default=os.path.join(ROOT, "assets", "eval"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    t0 = time.time()
    tasks, samples = build_tasks()
    print(f"built {len(tasks)} labelled images in {time.time()-t0:.1f}s; running engine with defaults {DEFAULTS}")
    sd = os.path.join(args.out, "samples")
    os.makedirs(sd, exist_ok=True)
    for k, data in samples.items():
        ext = "jpg" if data[:2] == b"\xff\xd8" else "png"
        with open(os.path.join(sd, f"{k}.{ext}"), "wb") as f:
            f.write(data)
    with Pool(args.workers, initializer=_init) as pool:
        res = pool.map(_run, tasks, chunksize=2)
    print(f"engine run done in {time.time()-t0:.1f}s")

    # spot-check: the sweep shortcut equals a real re-run with config.TAMPER_PCT patched
    _init()
    chk = [t for t in tasks if t[0]["group"] == "edit"][::9]
    mism = 0
    for thr in (() if V2 else (0.01, 0.1)):
        config.TAMPER_PCT = thr
        for meta, data in chk:
            r = verify_image(data, [x for x in _REG if x["id"] != meta.get("exclude")], _load)
            rec = next(x for x in res if x["kind"] == meta["kind"] and x["post"] == meta["post"] and
                       x.get("transform") == meta.get("transform"))
            mism += int(r["verdict"] != verdict_at(rec, thr))
    config.TAMPER_PCT = DEFAULTS["TAMPER_PCT"]
    print("sweep spot-check: skipped (engine v2 verdict also depends on the window rule)" if V2 else
          f"sweep spot-check: {len(chk)*2} real re-runs, {mism} mismatches")

    # exploratory 2-D sweep on images that match directly (no crop search needed): PIXEL_THRESH x TAMPER_PCT
    direct = [(t, r) for t, r in zip(tasks, res) if r["matched_id"] and r["group"] in ("genuine", "edit") and
              r["kind"] != "simulated_phone_screenshot" and r.get("transform") != "simulated_phone_screenshot"]
    explore = []
    for pt in ([] if V2 else PIX_EXPLORE):
        config.PIXEL_THRESH = pt
        pcts = [(r["group"], verify_image(t[1], _REG, _load)["changed_pct"]) for t, r in direct]
        for thr in SWEEP_EXTRA + SWEEP:
            g = [c for gr, c in pcts if gr == "genuine"]
            e = [c for gr, c in pcts if gr == "edit"]
            explore.append(dict(pixel_thresh=pt, tamper_pct=thr, n_genuine=len(g), n_edit=len(e),
                                false_altered_genuine=sum(c > thr for c in g),
                                false_genuine_edits=sum(c <= thr for c in e)))
    config.PIXEL_THRESH = DEFAULTS["PIXEL_THRESH"]

    summary = dict(defaults=DEFAULTS, n_images=len(res), spot_check_mismatches=mism,
                   headline=metrics(res, config.TAMPER_PCT),
                   sweep=[] if V2 else [metrics(res, t) for t in SWEEP],
                   sweep_extra=[] if V2 else [metrics(res, t) for t in SWEEP_EXTRA],
                   explore_pixel_thresh_direct_only=explore, timing=timing(res))
    tg = lambda groups, keyf: group_table(res, config.TAMPER_PCT, keyf, groups)
    summary["extended"] = ext_summary(res)
    if V2:   # window-rule sweep, computed from the recorded max_window_px and changed_pct (global rule fixed at TAMPER_PCT)
        ge = [r for r in res if r["group"] == "genuine"]
        ee = [r for r in res if r["group"] == "edit"]
        summary["window_sweep"] = [dict(win_px=k,
                                        false_genuine_edits=sum(not (r["changed_pct"] is not None and (r["changed_pct"] > config.TAMPER_PCT or r["win"] >= k)) for r in ee if r["matched_id"]),
                                        false_altered_genuine=sum(r["changed_pct"] is not None and (r["changed_pct"] > config.TAMPER_PCT or r["win"] >= k) for r in ge))
                                   for k in (2, 4, 6, 8, 12, 16, 24)]
    summary["by_genuine_transform"] = tg({"genuine"}, lambda r: r["kind"])
    summary["by_edit_type"] = tg({"edit"}, lambda r: r["kind"])
    summary["by_edit_size"] = tg({"edit"}, lambda r: r["size"])
    summary["by_edit_type_at_0.01"] = group_table(res, 0.01, lambda r: r["kind"], {"edit"})
    summary["by_edit_transform_at_0.01"] = group_table(res, 0.01, lambda r: r["transform"], {"edit"})
    summary["by_edit_transform"] = tg({"edit"}, lambda r: r["transform"])
    summary["by_edit_type_and_transform"] = tg({"edit"}, lambda r: f'{r["kind"]} | {r["transform"]}')
    summary["by_unmatched_group"] = tg({"fake_rumour", "unrelated_art", "synthetic", "leave_one_out"},
                                       lambda r: r["group"] + (" | " + r["kind"] if r["group"] == "leave_one_out" else ""))
    # changed_pct distributions
    def dist(rs):
        xs = sorted(r["changed_pct"] for r in rs if r["changed_pct"] is not None)
        return None if not xs else dict(n=len(xs), min=xs[0], median=round(statistics.median(xs), 3), max=xs[-1])
    summary["changed_pct_genuine"] = dist([r for r in res if r["group"] == "genuine"])
    summary["changed_pct_by_edit"] = {k: dist([r for r in res if r["group"] == "edit" and r["kind"] == k])
                                      for k in sorted({r["kind"] for r in res if r["group"] == "edit"})}
    # worst offenders
    summary["false_genuine_edits"] = [r for r in res if r["group"] == "edit" and r["verdict"] == "genuine"]
    summary["false_altered_genuine"] = [r for r in res if r["group"] == "genuine" and r["verdict"] == "altered"]
    summary["unmatched_false_matches"] = [r for r in res if r["group"] in ("fake_rumour", "unrelated_art", "synthetic",
                                                                           "leave_one_out") and r["verdict"] != "unverified"]
    with open(os.path.join(args.out, "results.json"), "w") as f:
        json.dump(res, f, indent=1)
    with open(os.path.join(args.out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)

    h = summary["headline"]
    print("\nHEADLINE (defaults):")
    for k, v in h.items():
        print(f"  {k}: {v}")
    print("\nSWEEP (TAMPER_PCT; v1 engine only):  thr | false-genuine on edits | edit detection | false-altered on genuine | genuine recall")
    for m in summary["sweep"]:
        print(f"  {m['tamper_pct']:<5} | {m['edit_false_genuine_n']}/{m['edit_n']} ({m['edit_false_genuine_pct']}%) | "
              f"{m['edit_detection_pct']}% | {m['false_altered_on_genuine_pct']}% | {m['genuine_recall_pct']}%")
    print("\nEXPLORE (direct-match, non-screenshot): pixel_thresh tamper_pct false_altered_genuine/n false_genuine_edits/n")
    for x in explore:
        print(f"  {x['pixel_thresh']:>3} {x['tamper_pct']:<6} {x['false_altered_genuine']}/{x['n_genuine']}  {x['false_genuine_edits']}/{x['n_edit']}")
    if not V2:
        print("EXTRA SWEEP:", [(m['tamper_pct'], m['edit_false_genuine_n'], m['false_altered_on_genuine_pct']) for m in summary['sweep_extra']])
    for name in ("by_genuine_transform", "by_edit_type", "by_edit_transform", "by_unmatched_group"):
        print(f"\n{name}:")
        for k, c in summary[name].items():
            print(f"  {k:45s} {c}")
    print("\ntiming:", json.dumps(summary["timing"], indent=1))
    print("\nEXTENDED:", json.dumps(summary["extended"], indent=1))
    if V2:
        print("WINDOW SWEEP:", summary["window_sweep"])
    print("false-genuine edits:", len(summary["false_genuine_edits"]))
    print("false-altered genuine:", len(summary["false_altered_genuine"]))
    print("unmatched false matches:", len(summary["unmatched_false_matches"]))


if __name__ == "__main__":
    main()
