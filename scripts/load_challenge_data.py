"""=== CHALLENGE 40 DATASETS (STUB) ===================================================================
If the Challenge 40 owners (UAE Cyber Security Council / TDRA / DESC) provide datasets (e.g. lists of official
domains, known scam numbers/URLs, verified official content), load them HERE FIRST and make them drive the
features (trusted-source registry, link check, known fakes). Then add the dataset to `open_datasets`
(DATA_SOURCES.md has a marked section) so the dashboard "Open data" panel and the Data slide list it.

    python scripts/load_challenge_data.py <file.csv> --table entities [--dry-run]

Supported out of the box: CSV with header columns matching the `entities` table (name, name_ar, kind, domain, source).
Extend `HANDLERS` for other shapes. Nothing is loaded unless you pass a file.
"""
import argparse
import csv

from _supa import Supa


def load_entities(rows, s):
    s.insert("entities", [dict(name=r["name"], name_ar=r.get("name_ar") or None, kind=r.get("kind") or "challenge_entity",
                               domain=r.get("domain") or None, source=r.get("source") or "Challenge 40 dataset") for r in rows])


HANDLERS = {"entities": load_entities}  # TODO: add handlers when the organisers' data format is known

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--table", default="entities")
    ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
    HANDLERS[a.table](list(csv.DictReader(open(a.file, encoding="utf-8"))), Supa(a.dry_run))
