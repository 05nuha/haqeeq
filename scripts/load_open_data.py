"""Load government open data into Supabase: entities, population, dubai_areas, open_datasets.

    python scripts/load_open_data.py [--dry-run]

Reads assets/open-data/clean/*.csv (built by scripts/build_open_data.py). Idempotent: delete-then-insert for
entities (no natural key), upsert for the rest. No keys? paste supabase/seed/open_data.sql into the SQL editor instead.
"""
import argparse
import csv
import os

from _supa import Supa, ROOT

CLEAN = os.path.join(ROOT, "assets", "open-data", "clean")


def rd(name):
    return list(csv.DictReader(open(os.path.join(CLEAN, name), encoding="utf-8")))


def n(v, cast=int):
    return cast(v) if v not in ("", None) else None


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
    s = Supa(a.dry_run)
    ents = [dict(name=r["name"], name_ar=r["name_ar"] or None, kind=r["kind"], domain=r["domain"] or None, source=r["source"]) for r in rd("entities.csv")]
    s.delete("entities", "id=gt.0"); s.insert("entities", ents)
    s.upsert("population", [dict(emirate=r["emirate"], population=int(r["population"]), older_share=n(r["older_share"], float),
                                 year=n(r["year"]), source=r["source"]) for r in rd("population.csv")], "emirate")
    s.upsert("dubai_areas", [dict(code=r["code"], name_en=r["name_en"], name_ar=r["name_ar"] or None, population=n(r["population"]),
                                  source=r["source"]) for r in rd("dubai_areas.csv")], "code")
    s.upsert("open_datasets", [dict(id=r["id"], name=r["name"], publisher=r["publisher"], portal=r["portal"], url=r["url"],
                                    accessed=r["accessed"], powers=r["powers"], rows=int(r["rows"])) for r in rd("open_datasets.csv")], "id")
    print("open data loaded" if not a.dry_run else "dry-run done")


if __name__ == "__main__":
    main()
