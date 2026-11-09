# DATA_SOURCES — government open data used by Haqeeq

Date accessed: **2026-11-09**. Only official UAE government portals were used (Bayanat, Dubai Pulse content hosted on
Bayanat, and the UAE Government Portal u.ae). Raw files: `assets/open-data/raw/`; cleaned: `assets/open-data/clean/`;
paste-able SQL: `supabase/seed/open_data.sql`; loader: `scripts/load_open_data.py`; re-download: `scripts/fetch_open_data.py`.

## Datasets actually obtained

| # | Dataset (exact name) | Publisher | Portal / URL | Format | Rows | Columns used | Powers (feature) |
|---|---|---|---|---|---|---|---|
| 1 | **Entities** (government entity list) | UAE government entities listed on Bayanat | Bayanat — https://bayanat.ae/en/entities | HTML/AJAX listing (saved as `raw/bayanat_entities_en.json`) | **57** entities | entity name, official website (-> `domain`), dataset count | `entities` table: trusted-source registry — the "not issued by any registered government entity" message and link/domain checks |
| 2 | **The Seven Emirates** (population statement per emirate) | UAE Government Portal (u.ae), citing SCAD, Sharjah Census, Fujairah Statistics Centre, RAK Media Office | https://u.ae/en/about-the-uae/the-seven-emirates (+ `/abu-dhabi`, `/Dubai`, `/Sharjah`, `/Ajman`, `/Umm-Al-Quwain`, `/Ras-Al-Khaimah`, `/Fujairah`) | HTML (7 pages, saved as `raw/uae_portal_*.html`) | **7** emirates | population figure + year as stated on each page | `population` table: denominators of **fake reports per 100,000 residents** on the map/ranking ("where to target Verify Before You Share") |
| 3 | **Population By Emirates, Nationality and Gender** | Federal Competitiveness and Statistics Centre (FCSC) | Bayanat — https://bayanat.ae/en/Datasets (search the title; updated 19/05/2026) | XLSX (`raw/fcsc_population_by_emirate_1975_2005.xlsx`) | **140** (7 emirates x 2 nationality x 2 sex x 5 census years 1975-2005) | `Emirates_EN/AR`, `year`, `value` | Reference baseline only (2005 census shares); **not** used for the displayed denominators — see caveats |
| 4 | **Lands registered in Dubai Land Department** (resource `Land_Registry_2017-03-28_08-21-00.xlsx`) | Dubai Pulse / Dubai Land Department | Dubai Pulse content on Bayanat — https://bayanat.ae/en/Datasets (publisher filter "Dubai Pulse") | XLSX, 19 MB, 145,152 rows x 33 cols (not committed; sha256 `c46bdf13…d413`; re-download with `fetch_open_data.py`) | **264** distinct Dubai areas extracted | `area_name_en`, `area_name_ar` | `dubai_areas` table: Dubai community names for report location labels (`reports.area`) |

Load counts into Supabase: entities 57, population 7, dubai_areas 264, open_datasets 4.

## Datasets requested but NOT obtained (and why)

| Dataset | Result |
|---|---|
| Dubai Pulse — organisation register (`registers/orgztoa`) | `dubaipulse.gov.ae` resets every connection from the build sandbox (egress gateway cannot reach it); `data.dubai`/`data.dubai.gov.ae` also unreachable/stub. `api.dubaipulse.gov.ae` is reachable but answers 401 (needs a registered OAuth app token). **Not obtained.** Entities therefore come from Bayanat only. To add it: sign in on Dubai Pulse, download the register CSV, then `python scripts/load_challenge_data.py <csv> --table entities`. |
| Dubai Pulse — population by community (`dsc_population_by_community-open`) | Same reason. Not on Bayanat either (Dubai Pulse's 161 Bayanat-hosted datasets searched: no population/community set). `dubai_areas.population` is therefore **null** for all areas. |
| Dubai Pulse — `dld_lkp_areas-open` | Same reason. Replaced by #4 (area names from the DLD land registry on Bayanat). It has **no area codes**, so `dubai_areas.code` is a slug of the English name (e.g. `business-bay`), not the DLD code. |
| FCSC Open Data (`opendata.fcsc.gov.ae`) population by emirate | Site returns a Cloudflare 403 challenge to automated clients. The FCSC datasets that are mirrored on Bayanat were used instead (#3). |
| FCSC "Population Estimates" (by emirate) | Obtained and inspected, then dropped: Emirati citizens only, 2006-2010. |
| FCSC "Population Estimate by Age Group and Sex", "Population by Age Groups, Gender and Nationality", UAE Total Population Estimates by Age Groups | Obtained/inspected (via Bayanat listing): national (UAE-wide) only, no emirate dimension, or years 2002-2008. **Age breakdown by emirate does not exist in accessible open data, so `population.older_share` is null** (no 60+/65+ weighting; the dashboard must not claim one). |
| "Population by Sex and District" (FCSC / Abu Dhabi medical districts, 2002-2008) | Dropped: health districts, outdated. |
| Dubai Statistics Center "Population Bulletin Emirate of Dubai 2024" (dsc.gov.ae) | Cited in a search snippet as 4,248,200 for end-2024, but the host is unreachable from the sandbox, so it was **not used or verified**. Dubai uses the u.ae figure (3,759,864). |

## Caveats (state these honestly)
- **Population years differ per emirate** (Abu Dhabi 2024 census; Dubai undated "current estimate"; Sharjah 2022 census, rounded 1.8 M; Ajman 2017; RAK 2015; Fujairah mid-2024; **Umm Al Quwain 2005 census**). UAQ, RAK and Ajman likely understate today's population, so their per-100k rates are overstated. Treat the ranking as indicative; replace `population` rows with the latest FCSC/emirate statistics-centre figures when accessible (`load_open_data.py` is idempotent).
- `entities.kind` (`federal_entity` / `local_entity`) is **our** classification; `domain` is the website link Bayanat lists for the entity (a few point at a parent body, e.g. Insurance Authority -> centralbank.ae). `name_ar` is empty (Bayanat's AJAX listing returns English only).
- Bayanat has no public listing API; the fetch script mimics the site's own AJAX calls. Dataset "last updated" dates on Bayanat (2026) are portal metadata, not the data's reference year (the DLD land registry is a 2017 snapshot; FCSC emirate data ends at the 2005 census year).
- Dubai area names come from a 2017 land-registry snapshot; some entries are sub-zones (e.g. "Al Barsha First").

## Challenge 40 datasets from the organisers (PLACEHOLDER — load these FIRST if they arrive)
<!-- CHALLENGE-DATA:BEGIN -->
Status: none received as of 2026-11-09. Ask organisers/mentors (UAE Cyber Security Council, TDRA, DESC) on Day 2.
When received, record: dataset name | provider | date | format | rows | which feature uses it. Load with
`python scripts/load_challenge_data.py <file> --table entities` (extend `HANDLERS` for other shapes), add a row to
`open_datasets` (via `scripts/build_open_data.py` catalogue list), and update the Data slide below.
<!-- CHALLENGE-DATA:END -->

## Data slide (ready to paste)
"Haqeeq is built on UAE government open data. The trusted-source registry is seeded from the 57 government entities
published on Bayanat, so any message claiming an official origin can be checked against a registered government entity.
The risk map normalises fake-report counts by official population statements for all seven emirates (UAE Government
Portal u.ae, citing the Abu Dhabi Census 2024 and Sharjah Census 2022, among others), turning raw counts into reports per
100,000 residents and a ranking of where to target the 'Verify Before You Share' campaign. Dubai location labels use
264 area names from the Dubai Land Department registry published by Dubai Pulse on Bayanat. Sources are listed in the
dashboard's Open data panel; population years differ by emirate and we say so."
