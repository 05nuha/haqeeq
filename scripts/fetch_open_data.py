"""Download the RAW government open datasets used by Haqeeq into assets/open-data/raw/.

    python scripts/fetch_open_data.py [--skip-land]

Sources (all official government portals):
  * Bayanat (bayanat.ae, UAE federal open-data portal)
      - Entities list (57 federal/local government entities)  -> bayanat_entities_en.json
      - FCSC "Population By Emirates, Nationality and Gender" -> fcsc_population_by_emirate_1975_2005.xlsx
      - Dubai Pulse "Lands registered in Dubai Land Department" (hosted on Bayanat) -> dld_land_registry_2017.xlsx (19 MB)
  * u.ae (UAE Government Portal) "The Seven Emirates" pages -> uae_portal_<emirate>.html
Bayanat has no public API for listings, so this mimics the site's own AJAX calls (antiforgery token +
cookie). Needs only `requests`. Date accessed for the committed copies: 2026-11-09.
"""
import argparse, html, json, os, re, sys, time, urllib.parse
import requests

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "open-data", "raw")
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
s = requests.Session(); s.headers.update(UA)
TOKEN = re.compile(r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"')


def req(method, url, **kw):
    kw.setdefault("timeout", 120)
    for i in range(6):
        try:
            r = s.request(method, url, **kw); r.raise_for_status(); return r
        except requests.RequestException as e:
            err = e; time.sleep(2 + 2 * i)
    raise err


def save(name, data):
    os.makedirs(RAW, exist_ok=True)
    p = os.path.join(RAW, name); open(p, "wb").write(data if isinstance(data, bytes) else data.encode("utf-8"))
    print("saved", p, len(data)); return p


def entities():
    r = req("GET", "https://bayanat.ae/en/entities")
    d = {"__RequestVerificationToken": TOKEN.search(r.text).group(1), "pagingDTO[CurrentPageNumber]": 1,
         "pagingDTO[PageCount]": 100, "pagingDTO[IsFilterUpdated]": "true"}
    p = req("POST", "https://bayanat.ae/Listing/GetEntitiesListing", data=d,
            headers={"X-Requested-With": "XMLHttpRequest", "Referer": "https://bayanat.ae/en/entities"})
    save("bayanat_entities_en.json", p.text)


def listing(text, entity=""):
    r = req("GET", "https://bayanat.ae/en/Datasets")
    d = {"__RequestVerificationToken": TOKEN.search(r.text).group(1), "searchText": text, "lang": "en", "Language": "",
         "Entities": entity, "Goals": "", "Topics": "", "Subtopics": "", "selectedFromDate": "", "selectedToDate": "",
         "SortingBy": "newest", "pagingDTO[CurrentPageNumber]": 1, "pagingDTO[PageCount]": 50, "pagingDTO[IsFilterUpdated]": "true"}
    j = req("POST", "https://bayanat.ae/DatasetsListing/GetDatasetsListing", data=d,
            headers={"X-Requested-With": "XMLHttpRequest", "Referer": "https://bayanat.ae/en/Datasets"}).json()
    return {html.unescape(m.group(3).strip()): m.group(2) for m in re.finditer(
        r'href="(/en/Datasets/Dataset-info\?id=([^"]+))".*?<h3 class="sub-title">(.*?)</h3>', j["pv"], re.S)}


def resources(ds_id):
    t = req("GET", "https://bayanat.ae/en/Datasets/Dataset-info?id=" + ds_id).text
    dec, out = json.JSONDecoder(), {}
    for m in re.finditer(r'data-item="', t):
        try:
            o = dec.raw_decode(t[m.end():])[0]; out[o["id"]] = o
        except Exception:
            pass
    return list(out.values())


def download(res, name):
    r = req("GET", "https://bayanat.ae/api/DatasetResources/DownloadSingle",
            params={"resourceID": res["id"], "fileName": res["nameEN"]}, timeout=600)
    save(name, r.content)


def dataset(title, out_name, entity=""):
    ids = listing(title, entity)
    res = resources(ids[title]); download(res[0], out_name)


def uae_portal():
    for e in ["abu-dhabi", "Dubai", "Sharjah", "Ajman", "Umm-Al-Quwain", "Ras-Al-Khaimah", "Fujairah"]:
        r = req("GET", f"https://u.ae/en/about-the-uae/the-seven-emirates/{e}")
        save(f"uae_portal_{e.lower()}.html", r.text)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--skip-land", action="store_true"); a = ap.parse_args()
    entities()
    dataset("Population By Emirates, Nationality and Gender", "fcsc_population_by_emirate_1975_2005.xlsx")
    uae_portal()
    if not a.skip_land:
        dataset("Lands registered in Dubai Land Department", "dld_land_registry_2017.xlsx", entity="25")  # 25 = Dubai Pulse
