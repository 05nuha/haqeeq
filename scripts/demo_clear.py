"""Delete demo data.

    python scripts/demo_clear.py [--seeded-only] [--dry-run]

default: delete ALL reports and ALL corrections (fresh start before the pitch).
--seeded-only: delete only reports with seeded=true (keeps real forwards) and leaves corrections alone.
"""
import argparse

from _supa import Supa

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--seeded-only", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(); s = Supa(a.dry_run)
    if a.seeded_only:
        s.delete("reports", "seeded=eq.true"); print("deleted seeded reports")
    else:
        s.delete("reports", "id=gt.0"); s.delete("corrections", "detail=neq.__none__"); print("deleted ALL reports and corrections")
