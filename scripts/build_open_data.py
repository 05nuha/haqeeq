"""Offline: turn the raw government files in assets/open-data/raw/ into cleaned CSV/JSON in assets/open-data/clean/
and generate supabase/seed/open_data.sql (paste-able INSERTs).

    python scripts/build_open_data.py [--land path/to/dld_land_registry_2017.xlsx]

--land is only needed to regenerate dubai_areas.csv (the 19 MB raw file is NOT kept in git; run
scripts/fetch_open_data.py to download it). Needs pandas + openpyxl.
"""
import argparse, csv, html, json, os, re
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "assets", "open-data", "raw")
CLEAN = os.path.join(ROOT, "assets", "open-data", "clean")
SQL_OUT = os.path.join(ROOT, "supabase", "seed", "open_data.sql")
ACCESSED = "2026-11-09"

LOCAL = {"Dubai Pulse", "Dubai Police", "Roads and Transport Authority", "Department of Health - Abu Dhabi",
         "Statistics Centre − Abu Dhabi", "Municipality & Planning Department - Ajman", "Government of Fujairah",
         "Ras Al Khaimah Maritime City", "Al Jazeera Port", "Abu Dhabi Agriculture And Food Safety Authority",
         "Emirates Health Services"}


def entities():
    pv = json.load(open(os.path.join(RAW, "bayanat_entities_en.json"), encoding="utf-8"))["pv"]
    rows = []
    for b in pv.split("accordion-item")[1:]:
        nm = re.search(r"<h6>([^<]+)</h6>", b)
        if not nm:
            continue
        name = html.unescape(nm.group(1)).strip()
        site = re.search(r'href="(https?://[^"]+)"', b)
        dom = ""
        if site:
            h = (urlparse(site.group(1)).hostname or "").lower()
            dom = h[4:] if h.startswith("www.") else h
        n = re.search(r"(\d+) Dataset", b)
        rows.append(dict(name=name, name_ar="", kind="local_entity" if name in LOCAL else "federal_entity",
                         domain=dom, source="Bayanat — Entities", bayanat_datasets=n.group(1) if n else ""))
    return rows


def pop_u_ae():
    def num(emirate, rx, scale=1):
        t = open(os.path.join(RAW, f"uae_portal_{emirate}.html"), encoding="utf-8").read()
        t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
        t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))
        m = re.search(rx, t)
        return int(round(float(m.group(1).replace(",", "")) * scale))
    S = "UAE Government Portal (u.ae) — The Seven Emirates"
    return [
        ("Abu Dhabi", num("abu-dhabi", r"population of Abu Dhabi reached ([\d,]+)"), 2024, f"{S}: Abu Dhabi, citing Abu Dhabi Census 2024 (Statistics Centre − Abu Dhabi)"),
        ("Dubai", num("dubai", r"estimated population of the emirate of Dubai is ([\d,]+)"), None, f"{S}: Dubai, 'current estimated population' (year not stated on page)"),
        ("Sharjah", num("sharjah", r"approximately ([\d.]+) million as per the Sharjah Census 2022", 1_000_000), 2022, f"{S}: Sharjah, 'approximately 1.8 million as per the Sharjah Census 2022 report' (rounded by the source)"),
        ("Ajman", num("ajman", r"population of Ajman in 2017 was ([\d,]+)"), 2017, f"{S}: Ajman, 2017 figure"),
        ("Umm Al Quwain", num("umm-al-quwain", r"total population of Umm Al Quwain was ([\d,]+)"), 2005, f"{S}: Umm Al Quwain, December 2005 census (oldest figure; likely understates today)"),
        ("Ras Al Khaimah", num("ras-al-khaimah", r"As of 2015, it is estimated to have a total population of ([\d,]+)"), 2015, f"{S}: Ras Al Khaimah, 2015 estimate (Ras Al Khaimah Government Media Office)"),
        ("Fujairah", num("fujairah", r"Population of Fujairah reached ([\d,]+) in mid-2024"), 2024, f"{S}: Fujairah, mid-2024 (Fujairah Statistics Centre / GIS Center)"),
    ]


def fcsc_2005():
    import pandas as pd
    v = pd.read_excel(os.path.join(RAW, "fcsc_population_by_emirate_1975_2005.xlsx"))
    v.columns = [c.strip() for c in v.columns]
    return v


def dubai_areas(land):
    import pandas as pd
    l = pd.read_excel(land)
    g = l.groupby("area_name_en").agg(name_ar=("area_name_ar", "first"), plots=("area_name_en", "size")).reset_index()
    g["name_en"] = g.area_name_en.str.strip()
    g["code"] = g.name_en.str.lower().str.replace(r"[^a-z0-9]+", "-", regex=True).str.strip("-")
    g = g.drop_duplicates("code").sort_values("name_en")
    return [dict(code=r.code, name_en=r.name_en, name_ar=str(r.name_ar).strip(), population="",
                 source="Dubai Pulse — Lands registered in Dubai Land Department (via Bayanat), 2017 snapshot", plots=int(r.plots))
            for r in g.itertuples()]


def w_csv(name, rows, cols):
    os.makedirs(CLEAN, exist_ok=True)
    with open(os.path.join(CLEAN, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)


def q(v):
    if v is None or v == "":
        return "null"
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace("'", "''") + "'"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--land"); a = ap.parse_args()
    ents = entities()
    w_csv("entities.csv", ents, ["name", "name_ar", "kind", "domain", "source", "bayanat_datasets"])
    pop = [dict(emirate=e, population=p, older_share="", year=y or "", source=s) for e, p, y, s in pop_u_ae()]
    w_csv("population.csv", pop, ["emirate", "population", "older_share", "year", "source"])
    f05 = fcsc_2005()
    f05.to_csv(os.path.join(CLEAN, "fcsc_population_by_emirate_1975_2005.csv"), index=False)
    p = os.path.join(CLEAN, "dubai_areas.csv")
    if a.land:
        areas = dubai_areas(a.land); w_csv("dubai_areas.csv", areas, ["code", "name_en", "name_ar", "population", "source", "plots"])
    areas = list(csv.DictReader(open(p, encoding="utf-8")))
    cat = [
        dict(id="bayanat_entities", name="Bayanat — Entities (government entity list)", publisher="UAE federal open-data portal Bayanat", portal="Bayanat",
             url="https://bayanat.ae/en/entities", accessed=ACCESSED, powers="Trusted-source registry: 'issued by a registered government entity' check", rows=len(ents)),
        dict(id="uae_portal_emirate_population", name="The Seven Emirates — population per emirate", publisher="UAE Government Portal (u.ae)", portal="u.ae",
             url="https://u.ae/en/about-the-uae/the-seven-emirates", accessed=ACCESSED, powers="Per-100,000-residents risk map and campaign-targeting ranking (denominators; years differ per emirate)", rows=len(pop)),
        dict(id="fcsc_pop_by_emirate", name="Population By Emirates, Nationality and Gender (1975–2005 census years)", publisher="Federal Competitiveness and Statistics Centre (FCSC)", portal="Bayanat",
             url="https://bayanat.ae/en/Datasets", accessed=ACCESSED, powers="Reference baseline (2005 census) for emirate population shares; not used for displayed denominators", rows=len(f05)),
        dict(id="dubai_pulse_land_registry", name="Lands registered in Dubai Land Department (area names)", publisher="Dubai Pulse / Dubai Land Department", portal="Dubai Pulse",
             url="https://bayanat.ae/en/Datasets", accessed=ACCESSED, powers="Dubai community/area names for report location labels", rows=len(areas)),
    ]
    w_csv("open_datasets.csv", cat, ["id", "name", "publisher", "portal", "url", "accessed", "powers", "rows"])
    json.dump(dict(entities=ents, population=pop, dubai_areas=areas, open_datasets=cat), open(os.path.join(CLEAN, "open_data.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    L = ["-- Generated by scripts/build_open_data.py — safe to re-run (delete-then-insert). Paste into the Supabase SQL editor.",
         "begin;", "delete from entities;", "delete from population;", "delete from dubai_areas;", "delete from open_datasets;"]
    for r in ents:
        L.append(f"insert into entities (name, name_ar, kind, domain, source) values ({q(r['name'])}, {q(r['name_ar'])}, {q(r['kind'])}, {q(r['domain'])}, {q(r['source'])});")
    for r in pop:
        L.append(f"insert into population (emirate, population, older_share, year, source) values ({q(r['emirate'])}, {r['population']}, null, {q(r['year'])}, {q(r['source'])});")
    for r in areas:
        L.append(f"insert into dubai_areas (code, name_en, name_ar, population, source) values ({q(r['code'])}, {q(r['name_en'])}, {q(r['name_ar'])}, null, {q(r['source'])});")
    for r in cat:
        L.append(f"insert into open_datasets (id, name, publisher, portal, url, accessed, powers, rows) values ({q(r['id'])}, {q(r['name'])}, {q(r['publisher'])}, {q(r['portal'])}, {q(r['url'])}, {q(r['accessed'])}, {q(r['powers'])}, {r['rows']});")
    L.append("commit;")
    os.makedirs(os.path.dirname(SQL_OUT), exist_ok=True)
    open(SQL_OUT, "w", encoding="utf-8").write("\n".join(L) + "\n")
    print(f"entities={len(ents)} population={len(pop)} dubai_areas={len(areas)} fcsc2005={len(f05)} -> {SQL_OUT}")


if __name__ == "__main__":
    main()
