# Haqeeq image engine: controlled-test evaluation

Reproduce: `python scripts/eval/run_eval.py` (about 3 min on 4 cores, deterministic, seeded).
Outputs: `assets/eval/results.json` (one row per image), `assets/eval/summary.json`, `assets/eval/run_log.txt`,
`assets/eval/samples/` (one example of each variant). To re-run the BEFORE engine on the same images, export the old
`engine/` to a folder and set `HAQEEQ_ENGINE_ROOT=<that folder>`.

**These are controlled-test numbers on synthetic images from one renderer. They are not accuracy in the wild.**

# Engine v2 (branch `engine-fix`): BEFORE vs AFTER

Same 325 labelled images as before (the "base set"), plus an "extended set" of 211 more images with phone-screenshot
geometries and harsher transforms that were added in this round (same 8 posts, same renderer). Counts, not decimals.

## What changed in the engine and why
| Change | Why |
|---|---|
| Compare at 512 px wide (height by the post's aspect) instead of a 256x256 squashed grid, after a 0.8 px Gaussian blur of both images | A one-digit edit is a handful of pixels at 256x256. The blur makes JPEG/resampling noise vanish while text edits stay. The grid is never wider than the picture received (min 256) so a small copy is not compared against invented detail. |
| `PIXEL_THRESH` 55 -> 25 (on the blurred grid) | Evaluator finding: 25 gave 0 false-genuine and 0 false-altered on directly matched images; 55 was too blunt for thin strokes. |
| New localised rule: `altered` if ANY 10x10 window holds >= 8 changed pixels (`TAMPER_WIN_PX`), in addition to the old global `TAMPER_PCT` | A digit edit is a tiny share of the picture but concentrated; compression noise is thin and spread out. On this set genuine copies score 0 in every window; the weakest edit scores >= 10. Any window threshold from 2 to 8 gives 0/0 here, 12 starts to let edits through (see window sweep). 8 was picked at the edge of the safe plateau on the safe side. This was chosen on the same data it is scored on (see Limitations). |
| Robust brightness/contrast normalisation before diffing (gain 0.6-1.6, outlier-rejecting) | A 20% darkening (night shift / dark filter) was flagged altered with the lower pixel threshold; the old engine passed it. Pixels that disagree are excluded from the fit so an edit cannot be fitted away. |
| Crop/screenshot alignment rewritten (`engine/crop.py: align`): sub-pixel float box, Lanczos resample straight from a source box, coarse-to-fine (48x60 grid first, so periodic designs like the RTA stripes cannot lock onto the wrong repeat), a seed grid of shifts and scales, aspect-locked stage then free edges with compound stretch/shift moves | Old aligner was integer-pixel, left misalignment of a few px, which showed as 0.09-1.32% changed. New aligner lands within about 0.2 px. |
| A flagged direct copy (>= 10 of 16x16 cells changed) is re-aligned once, in both directions (post with margin, or picture is a crop of the post) | A genuine copy with 1-2% cropped border was called altered (0/8 genuine before). Alignment moves 4 numbers; it cannot erase a changed digit (tested: an edit stays altered inside cropped and screenshotted copies). Only flagged, spread-out copies pay the extra ~0.5 s. |
| Result gains `max_window_px` and `crop_box` (when realigned); heat-map cell = min(1, changed px / 12) so a single digit is visible; reply/detail text says "localised edit" instead of "0.0% changed" | Presentation of the new signal. Verdict contract (`genuine/altered/unverified`, same fields) unchanged. |

Not changed: `MATCH_THRESH`, `CROP_MATCH_THRESH`, the pHash, the crop search (apart from stopping the scale scan early once a window already matches within 2 bits), the unverified default.

## Headline: base set (325 images), same labels as the BEFORE run
| Metric | BEFORE (v1) | AFTER (v2) |
|---|---|---|
| Genuine recall (called genuine, right post) | 67/72 | **72/72** |
| False-altered on genuine | 5/72 | **0/72** |
| Simulated phone screenshots called genuine | 3/8 | **8/8** |
| **False-genuine on edited images (critical)** | **55/213** | **0/213** |
| Edit detection (called altered) | 111/213 | 166/213 |
| Edits called unverified (patch pasted from another post, pHash distance above 12) | 47/213 | 47/213 (unchanged, safe) |
| Unrelated / unmatched false match | 0/40 | 0/40 |

False-genuine by edit type (all deliveries: lossless, JPEG q60, phone screenshot):
| Edit type | n | BEFORE called genuine | AFTER called genuine | AFTER altered / unverified |
|---|---|---|---|---|
| date_1digit | 24 | 19 | **0** | 24 / 0 |
| date_2digit | 24 | 19 | **0** | 24 / 0 |
| key_line_1digit | 21 | 12 | **0** | 21 / 0 |
| number_changed | 24 | 5 | **0** | 24 / 0 |
| word_changed_body | 24 | 0 | 0 | 24 / 0 |
| patch_2pct | 24 | 0 | 0 | 11 / 13 |
| patch_5pct | 24 | 0 | 0 | 9 / 15 |
| patch_10pct | 24 | 0 | 0 | 6 / 18 |
| headline_replaced | 24 | 0 | 0 | 23 / 1 |

Patch edits that fall out of the pHash match are still "unverified" rather than "altered" (not touched by this change; safe, less informative).

## Extended set (211 images, new in this round)
Genuine (56): five phone-screenshot geometries (small phone q60, 1290x2796 lossless, post inside a dark chat bubble q70, tablet canvas q90), 1% border crop q80, JPEG q30, WhatsApp 1280 px q50. Edits (155): date_1digit, date_2digit, key_line_1digit, number_changed delivered through small-phone screenshot, lossless 1290 screenshot, chat-bubble screenshot, 1% crop, WhatsApp 1280 q50.
| Metric | BEFORE | AFTER |
|---|---|---|
| Genuine called genuine | 27/56 | **54/56** |
| Genuine false-altered | 27/56 | **0/56** |
| Genuine called unverified | 2/56 | 2/56 (both `weekend_schedule_notice` in chat-bubble/tablet: crop search distance 8 > 6, so never found; safe) |
| Edits called altered | 103/155 | **151/155** |
| **Edits called genuine (false-genuine)** | **48/155** | **0/155** |
| Edits called unverified | 4/155 | 4/155 (same weekend-notice cases) |

By transform (genuine): small phone q60 2/8 -> 8/8; lossless 1290 2/8 -> 8/8; chat bubble 4/8 -> 7/8; tablet 3/8 -> 7/8; 1% crop 0/8 -> 8/8; JPEG q30 and WhatsApp q50 8/8 -> 8/8.
By transform (edits, false-genuine): small phone 6 -> 0; lossless 1290 8 -> 0; chat bubble 11 -> 0; 1% crop 0 -> 0; WhatsApp q50 23 -> 0 (a q50 1280 px copy is where the old 256 px comparison was blindest).

## Window-rule sweep (AFTER, base set, global rule fixed at 0.04%)
Changed pixels needed in a 10x10 window to call it altered, with the false-genuine count on edits and the false-altered count on genuine:
k=2: 0/0, k=4: 0/0, k=6: 0/0, k=8 (default): 0/0, k=12: 3/0, k=16: 3/0, k=24: 18/0. Genuine copies score 0 in every window on this set, so the false-altered side has a wide margin here; real devices will add noise (see limitations).

Extra stress (8 posts each, direct path, all stayed genuine with max window 0): Gaussian noise sigma 2/4/8 + JPEG q85/75/70, JPEG q15, gamma 0.85 and 1.2, brightness -20%, downscale to 0.35 and upscale 1.4.

## Timing (per image; the eval runs 4 worker processes so the numbers are slightly pessimistic)
| Path | BEFORE median / p95 | AFTER median / p95 |
|---|---|---|
| Direct match, genuine | 19 / 41 ms | 36 / 66 ms |
| Direct match, edited | 24 / 40 ms | 45 / 685 ms (re-alignment only runs when many cells changed, i.e. big edits or crops) |
| Phone screenshot (crop search + alignment) | 1.94 / 2.65 s | 2.34 / 3.08 s (about 2.3-2.5 s when run alone) |
| Unmatched (full crop search, gives up) | 1.79 / 2.44 s | 1.72 / 1.88 s |
The BEFORE row was measured while the machine was also running other jobs; a clean earlier run gave 20 ms and 1.83 s. The screenshot path is about 0.4-0.5 s slower than before; the p95 is just over the 3 s target when 4 workers run in parallel.

## Limitations of this round (read these)
- The base-set images are the same ones the old numbers came from, but **the thresholds were chosen looking at this data** (`PIXEL_THRESH` 25 came from the earlier explore table; the window size/threshold from the same set). A plateau of safe values (k=2..8) and the stress tests are the evidence against pure overfitting, not a held-out set.
- The extended-set failures I saw (periodic RTA stripes, a post whose own edge is flat against the chat bubble) drove the aligner rewrite, so the extended set is partly in-sample for the aligner too. Real device screenshots are the missing test.
- Genuine copies here come from the same renderer as the originals, so genuine noise is near zero. Real WhatsApp re-encodes, different screenshot scalers and OS UI overlays (notification banners over the post, rounded corners, dark mode) are untested. A banner covering part of the post will be called altered (safe direction).
- Still not caught as "altered": 47 patch edits (called unverified), 4 extended edits (unverified because the crop search never finds the weekend notice in a chat bubble).
- Only 8 posts; 24 trials per edit type are not independent.


# Archived: engine v1 (BEFORE) detailed evaluation
Everything below describes the v1 engine (`PIXEL_THRESH=55, TAMPER_PCT=0.04` on a 256x256 grid, integer-pixel crop alignment) and is kept for reference;
its pitch-safe sentences no longer apply once v2 ships (and the TAMPER_PCT sweep is not applicable to v2).

## Method

The real `engine.verify_image` is run on 325 labelled images built from the 8 official posts (`assets/official/*.png`).
Registry = the 8 posts (pHash computed with `engine.phash`).

| Group | What | n | Expected |
|---|---|---|---|
| A. Genuine | 8 posts x 9 transforms: lossless copy, JPEG q80/q60/q40, downscale 0.75 and 0.5 (+JPEG q85), **simulated phone screenshot** (post resized into a 1170x2532 canvas with status and browser bars, JPEG q80), brightness +6% / contrast -5%, WhatsApp-style (long side 1600, JPEG q70) | 72 | genuine |
| B. Edited | 8 posts x edits, each re-rendered with `scripts/make_assets.py` (same fonts and layout), then delivered 3 ways: lossless, JPEG q60, simulated phone screenshot | 213 | altered, never genuine |
| C. Unmatched | the 2 fakes, the 2 unrelated images, 20 synthetic noise/gradient/blob/block images, and each official post (lossless and phone screenshot) checked against a registry that EXCLUDES it | 40 | unverified |

Edit types per post (x3 deliveries = 24 each; key-line single digit only exists for 7 posts, so 21):
`date_1digit` (footer date, last day digit), `date_2digit` (both day digits), `key_line_1digit` (one digit in the highlighted
key line), `number_changed` (all digits of the key line; for the weekend notice, which has none, the digits of the body),
`word_changed_body` (one body word replaced), `patch_2/5/10pct` (a patch of that fraction of the image area copied from a
different post and pasted at a random location), `headline_replaced` (headline and key line rewritten).
Size labels: tiny = date edits, small = digit/word edits, patch = 2/5/10% area, large = headline.

Sweep note: `TAMPER_PCT` is only used in the final comparison, so the sweep is computed from the recorded `changed_pct`.
This was spot-checked against 48 real re-runs with `config.TAMPER_PCT` patched: 0 mismatches.

## Headline numbers at current defaults (TAMPER_PCT 0.04)

| Metric | Result |
|---|---|
| Genuine recall (called genuine and matched to the right post) | **67/72 = 93.1%** |
| False-altered rate on genuine | 5/72 = 6.9% (all 5 are simulated phone screenshots, see below) |
| Genuine called unverified / matched to wrong post | 0/72 / 0/72 |
| Edit detection (called altered) | 111/213 = 52.1% |
| Edit not called genuine (altered or unverified) | 158/213 = 74.2% |
| **False-genuine rate on edits (critical)** | **55/213 = 25.8%** |
| Edits that fell out of the match and were called unverified | 47/213 = 22.1% (patch edits, see below) |
| Unrelated / unmatched false-match rate | 0/40 = 0.0% (0 false genuine; includes leave-one-out) |
| Correct post matched (genuine + edits) | 238/285 = 83.5% (the rest are the 47 edits above; 0 wrong-post matches) |

### Per genuine transform (n=8 each)
All 8/8 genuine for lossless, JPEG q80/q60/q40, downscale 0.75, downscale 0.5, brightness/contrast, WhatsApp-style.
**Simulated phone screenshot: only 3/8 genuine, 5/8 falsely called altered.** `changed_pct` for these was 0.09, 0.09, 0.13, 0.09 and 1.32 (RTA post).
The post was found by the crop search (distance 0-2) but the box alignment is a few pixels off, so edges of text count as changed.
Genuine non-screenshot images: `changed_pct` max 0.0.

### Edit detection by type at defaults (n includes all 3 deliveries)
| Edit type | altered | unverified | **called genuine** |
|---|---|---|---|
| date_1digit (tiny) | 5/24 | 0 | **19/24 (79%)** |
| date_2digit (tiny) | 5/24 | 0 | **19/24 (79%)** |
| key_line_1digit (small) | 9/21 | 0 | **12/21 (57%)** |
| number_changed (small) | 19/24 | 0 | **5/24 (21%)** |
| word_changed_body (small) | 24/24 | 0 | 0 |
| patch 2% | 11/24 | 13 | 0 |
| patch 5% | 9/24 | 15 | 0 |
| patch 10% | 6/24 | 18 | 0 |
| headline_replaced (large) | 23/24 | 1 | 0 |

By delivery at defaults: lossless 23/71 false-genuine, JPEG q60 23/71, simulated phone screenshot 9/71.
The phone-screenshot rate is lower only because alignment noise lifts every image above the threshold (the same effect that
falsely flags genuine screenshots), not because the engine sees the edit better.

### What is not reliably caught (stated plainly)
1. **Small-text digit edits are mostly missed.** A one- or two-digit change in the footer date shows up as 0.000-0.02% of the
   256x256 comparison grid (a handful of pixels) and is called genuine in 19/24 cases at the default, 16/24 and 13/24 even at 0.01.
   Changing one digit of a prominent number is missed in 12/21 cases at the default. **A date or amount changed by one or two digits is
   the most realistic scam edit and is the engine's weakest case.**
2. Larger edits (patch, replaced headline, replaced word) are never called genuine, but 47 of the patch edits are called
   **unverified** (pHash distance 14-24 > 12), not altered. The user sees "not an official post", not "altered version of the MOHRE post".
   No false-genuine, but the more informative verdict is lost. This is true for 13/24, 15/24 and 18/24 of the 2/5/10% patches.
3. The simulated phone screenshot path has a 5/8 false-altered rate on genuine posts.

## TAMPER_PCT sweep (all 285 post-derived images; phone screenshots included)

| TAMPER_PCT | False-genuine on edits | Edit detection | False-altered on genuine | Genuine recall |
|---|---|---|---|---|
| 0.01 | 29/213 (13.6%) | 64.3% | 6.9% | 93.1% |
| 0.02 | 45/213 (21.1%) | 56.8% | 6.9% | 93.1% |
| 0.03 | 47/213 (22.1%) | 55.9% | 6.9% | 93.1% |
| **0.04 (default)** | 55/213 (25.8%) | 52.1% | 6.9% | 93.1% |
| 0.06 | 64/213 (30.0%) | 47.9% | 6.9% | 93.1% |
| 0.10 | 77/213 (36.2%) | 41.8% | 2.8% | 97.2% |

Exploratory finer values (not in the requested grid): 0.0 -> 2 false-genuine, 0.002 -> 8, 0.005 -> 19; false-altered on genuine
stays 6.9% for every value from 0.0 to 0.06 (the 5 phone-screenshot genuine images all have `changed_pct` >= 0.09).
Exploratory `PIXEL_THRESH` x `TAMPER_PCT` on directly matched, non-screenshot images only (64 genuine, 114 edits):
`PIXEL_THRESH` 25 with `TAMPER_PCT` <= 0.005 gave 0/114 false-genuine and 0/64 false-altered; `PIXEL_THRESH` 35 with 0.002 also 0/114 and 0/64;
the default `PIXEL_THRESH` 55 needs `TAMPER_PCT` 0.0 to get to 2/114. Full table in `summary.json` (`explore_pixel_thresh_direct_only`).

### Recommendation
Within the requested grid, **`TAMPER_PCT = 0.01`**: it halves the false-genuine count (55 -> 29) with no extra false-altered on genuine in this test.
The cost side of the trade-off is flat from 0.01 to 0.06 because every genuine image with a pixel difference is a screenshot-alignment
case already well above 0.04. Going up to 0.10 only "fixes" screenshots by also letting more edits through (77 false-genuine), which is the wrong direction for a
safety number. Reasoning: a false "genuine" on an edited post is the worst failure, a false "altered" is recoverable.
Caveat: the test images are rendered and recompressed by the same pipeline, so genuine noise is near zero here. Real device
screenshots and re-encodes will have more noise, so the safe floor may be higher than the data suggests. Before shipping a lower value, check it against a few real
phone screenshots of the genuine posts. The next step with the biggest payoff is `PIXEL_THRESH` ~25-35 with `TAMPER_PCT` ~0.005, plus fixing crop alignment so genuine screenshots do not read 0.09-1.3% changed.
No defaults were changed by this evaluation.

## Timing (per image, 4 worker processes, so slightly pessimistic)

| Path | n | median | p95 |
|---|---|---|---|
| Matched, direct pHash (no crop search) | 178 | 20 ms | 41 ms |
| Matched via crop search (phone screenshots) | 60 | 1.83 s | 1.97 s |
| Unmatched (full crop search then give up) | 87 | 1.65 s | 1.78 s |
| All matched | 238 | 23.5 ms | 1.91 s |

## Simulated vs real
- All "screenshots" are simulated (pillow canvas with bars), not captured on a device. All JPEG/resize steps are local
  transforms, **no real WhatsApp round trips** were done.
- Edits are programmatic re-renders and pastes with the same fonts and layout as the originals, so differences are exactly
  the edit. A real forger using other tools would also shift anti-aliasing, fonts and colours (which makes detection
  easier but also produces more false-altered).
- The Gemini text/scam path and the registry's `known_fakes` list were not evaluated (images only; the two fake images were run without `known_fakes`).

## Limitations
- Only 8 posts, one renderer, one author; 24 trials per edit type are 8 posts x 3 deliveries and are NOT independent.
- Percentages are of small counts (n=8 to 24 per cell); do not quote decimals.
- Edit types and thresholds were chosen by the evaluator; some are deliberately hard (1-digit footer date).
- Unmatched set is easy for pHash (synthetic noise/gradients); 0/40 false matches does not prove real photos are safe.
- Phone screenshots use a single layout (post fills 1170 px width).

## Pitch-safe sentences (controlled tests, not accuracy in the wild)
- "On 325 controlled test images built from 8 official posts, Haqeeq never matched an unrelated image or an image of a post
  missing from the registry to an official post (0 of 40)."
- "On 64 genuine copies recompressed with JPEG q40-q80, resized to 50-75% or WhatsApp-style 1600 px, 64 of 64 were recognised as genuine."
  (Simulated phone screenshots were only 3 of 8 genuine, so do not claim screenshots all pass.)
- "Every edit that rewrote a headline, replaced a word, or pasted over 2-10% of the image was either flagged altered or
  flagged as not official; none was called genuine (0 of 120 such edits)." Check: word 24 + patches 72 + headline 24 = 120.
- "The hard case is a one- or two-digit change in small text: on our controlled tests the current threshold misses most of them
  (about 8 in 10 for a changed footer date), and we are tuning the threshold and a pixel-level check on exactly this."
  Say this proactively; it is honest and shows rigour.
- Do not say: "99% accurate", "never calls a fake genuine", or "works on real WhatsApp screenshots".
