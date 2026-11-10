"""Engine thresholds (overridable by env for tuning with real images)."""
import os


def _f(name, default, cast=float):
    try:
        return cast(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


MATCH_THRESH = _f("HAQEEQ_MATCH_THRESH", 12, int)    # pHash Hamming distance (/64) <= this => derived from official
# Tamper check (engine v2). Both images are resized to FINE_W px wide (height by the official's aspect),
# blurred with a Gaussian of BLUR px, then a pixel counts as changed when its grey delta > PIXEL_THRESH.
PIXEL_THRESH = _f("HAQEEQ_PIXEL_THRESH", 25, int)    # grey delta for a pixel to count as changed (was 55 on a raw 256x256 grid)
TAMPER_PCT = _f("HAQEEQ_TAMPER_PCT", 0.04)           # global changed fraction (%) above which => altered
TAMPER_WIN_PX = _f("HAQEEQ_TAMPER_WIN_PX", 8, int)   # changed pixels inside any WIN x WIN window => altered (catches a changed digit)
WIN = 10                                             # side of the sliding window, in fine-grid pixels
FINE_W = 512                                         # comparison width (height follows the official aspect)
BLUR = 0.8                                           # Gaussian sigma applied to both images before diffing
REALIGN_CELLS = 10                                   # only re-align a flagged direct copy if >= this many of 16x16 cells changed
GRID = 256                                           # legacy: coarse resolution used by the crop aligner
CROP_MATCH_THRESH = _f("HAQEEQ_CROP_MATCH_THRESH", 6, int)  # stricter: crop search tries many windows
CROP_SEARCH = os.environ.get("HAQEEQ_CROP_SEARCH", "1") != "0"
