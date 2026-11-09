"""Hash + upload the official registry and known fakes.

    python scripts/seed_registry.py [--dry-run]

official: assets/official/<id>.png  -> storage official/<id>.png, table official_posts (phash via engine.phash)
fakes:    assets/fakes/<id>.png     -> storage fakes/<id>.png,    table known_fakes   (detail = CONTRACT section 5)
Idempotent (storage x-upsert + table upsert).
"""
import argparse
import os

from _supa import Supa
from _registry import A, official_registry, KNOWN_FAKES, read
from engine import phash

ISSUERS = {}  # registry.json already carries issuer


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
    s = Supa(a.dry_run)
    rows = []
    for p in official_registry():
        local = os.path.join(A, "official", p["id"] + ".png")
        s.upload(f"official/{p['id']}.png", local)
        rows.append(dict(id=p["id"], title=p["title"], title_ar=p.get("title_ar"), issuer=p["issuer"], date=p.get("date"),
                         phash=phash(read(f"official/{p['id']}.png")), image_path=f"official/{p['id']}.png"))
    s.upsert("official_posts", rows, "id")
    fk = []
    for f in KNOWN_FAKES:
        s.upload(f"fakes/{f['id']}.png", os.path.join(A, f["file"]))
        fk.append(dict(id=f["id"], title=f["title"], detail=f["detail"], phash=phash(read(f["file"])), image_path=f"fakes/{f['id']}.png"))
    s.upsert("known_fakes", fk, "id")
    print(f"registry: {len(rows)} official posts, {len(fk)} known fakes")
    for r in rows + fk:
        print(f"  {r['id']:26s} {r['phash']}")


if __name__ == "__main__":
    main()
