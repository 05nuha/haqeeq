# Haqeeq image engine: controlled-test evaluation

Reproduce: `python scripts/eval/run_eval.py` (about 95 s on 4 cores, deterministic, seeded).
Outputs: `assets/eval/results.json` (one row per image), `assets/eval/summary.json`, `assets/eval/run_log.txt`,
`assets/eval/samples/` (one example of each variant). Engine defaults were NOT changed:
`MATCH_THRESH=12, PIXEL_THRESH=55, TAMPER_PCT=0.04, CROP_MATCH_THRESH=6`.

**These are controlled-test numbers on synthetic images from one renderer. They are not accuracy in the wild.**

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
