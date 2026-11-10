"""Engine thresholds (overridable by env for tuning with real images)."""
import os


def _f(name, default, cast=float):
    try:
        return cast(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


MATCH_THRESH = _f("HAQEEQ_MATCH_THRESH", 12, int)    # pHash Hamming distance (/64) <= this => derived from official
PIXEL_THRESH = _f("HAQEEQ_PIXEL_THRESH", 55, int)    # grey delta for a pixel to count as changed
TAMPER_PCT = _f("HAQEEQ_TAMPER_PCT", 0.04)           # changed fraction of pixels above which => altered
GRID = 256                                           # comparison resolution
CROP_MATCH_THRESH = _f("HAQEEQ_CROP_MATCH_THRESH", 6, int)  # stricter: crop search tries many windows
CROP_SEARCH = os.environ.get("HAQEEQ_CROP_SEARCH", "1") != "0"
