# Rebuild Haqeeq on Vercel + Supabase, using parallel agents

First read CLAUDE.md in this folder end to end. It has the full context: the hackathon, the official
rubric (optimise for it), Challenge 40, every product decision, the evidence, the demo beats, and the
existing working Flask code (main.py, engine.py, db.py, seed.py, dashboard.py, demo_seed.py,
templates/dashboard.html). That code is the reference implementation and our FALLBACK. Do not delete it;
move it into `legacy-flask/` untouched.

## Goal
Rebuild Haqeeq so it runs on **Vercel + Supabase** (no Replit), keeping the same product, verdicts,
Arabic replies, demo beats and dashboard design, and making the dashboard even more impressive for
non-technical judges. Deadline: a fully working deployed version that passes the gate test by
**Tue 10 Nov 2026, 1pm Dubai time**. If that slips, we revert to the Flask fallback.

## Target architecture
- **One Vercel project**: Next.js (App Router, TypeScript, Tailwind) for the dashboard, plus **Python
  serverless functions** for the bot and engine (Vercel Python runtime, e.g. `api/*.py` with rewrites, like
  Vercel's Next.js + Flask starter). Deployed from a GitHub repo.
- **Supabase**: Postgres (tables below), Storage (bucket `media` for forwarded and official images),
  **Realtime** on `reports` and `corrections` so the dashboard updates instantly (no polling).
- **Twilio WhatsApp sandbox** webhook → `https://<production-domain>/api/whatsapp` (use the stable production
  domain, never a preview URL).
- **Gemini** (Google AI Studio key) for the AI scam-text analysis; rule-based fallback must remain.

## Hard constraints
- Vercel functions have no persistent disk: images go to Supabase Storage, data to Supabase Postgres.
- **Do not use scipy**. Reimplement pHash with numpy only (grayscale → 32×32 → 2D DCT-II via a precomputed
  cosine matrix → top-left 8×8 → compare to median → 64-bit hash). Hamming distance as before. Registry
  hashes and incoming hashes must use the SAME function (re-seed the registry with it).
- Keep the engine logic from legacy engine.py: STEP 1 pHash match (`MATCH_THRESH` 12, coarse /64) → else
  unverified; STEP 2 pixel tamper check against the matched official image at 256×256 greyscale,
  `PIXEL_THRESH` 55, `TAMPER_PCT` 0.04% → genuine vs altered. Thresholds in one config file / env vars.
- Exact Arabic replies and verdict names from CLAUDE.md section 8. Verdicts: genuine | altered | unverified | scam_risk.
- Security (this is a cyber challenge; it earns points and protects the demo):
  - Validate Twilio's `X-Twilio-Signature` on `/api/whatsapp` (allow a `SKIP_TWILIO_SIG=1` env flag for local tests only).
  - Supabase RLS: dashboard (anon key) can only SELECT safe columns; all writes via the service-role key on the server.
  - Store full phone numbers only in a server-only table (`senders`, RLS deny-all for anon); the dashboard only ever sees masked numbers.
  - No secrets in the repo; `.env.example` lists them.
- Never write `{{` inside any template, and keep honest labels: seeded background data, mocked government
  signing key, map shows where reports come from (not the encrypted WhatsApp spread path).

## Phase 0 — you (lead) do this first, alone, before spawning agents
1. Create the repo layout: `app/` (Next.js), `api/` (Python functions), `engine/` (pure Python package
   shared by functions + tests), `supabase/` (migrations + seed), `scripts/`, `assets/`, `legacy-flask/`.
2. Write the **contract** every agent builds against and commit it as `CONTRACT.md`:
   - SQL migration: `official_posts(id text pk, title, title_ar, issuer, date, phash text, image_path text)`,
     `reports(id bigserial pk, ts timestamptz default now(), sender_masked, sender_id fk, kind, verdict,
     matched_id, distance int, changed_pct real, emirate, detail, image_path)`,
     `senders(id pk, phone text unique)`, `corrections(detail pk, ts, message, recipients int)`,
     `entities(name, kind, source)`. RLS policies + Realtime publication for reports/corrections.
   - API: `POST /api/whatsapp` (Twilio form → TwiML reply), `POST /api/correct {detail, message}` →
     sends the correction via Twilio REST to every sender who forwarded that fake, records it, returns
     `{recipients}`; protect it with a simple `DASHBOARD_ADMIN_TOKEN` header.
   - Env vars: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `TWILIO_ACCOUNT_SID`,
     `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`, `GEMINI_API_KEY`, `DASHBOARD_ADMIN_TOKEN`,
     `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`.
3. Then spawn the agents below **in parallel**, each owning only its own folders (no two agents edit the
   same file). Give each one CLAUDE.md + CONTRACT.md.

## Agents (run in parallel)
1. **Engine agent** — owns `engine/` and `engine/tests/`. numpy-only pHash, tamper check (also return a
   16×16 change grid for a heat-map), text scam check (rules + Gemini with JSON output and fallback; verify the
   current Gemini model name works). Write pytest tests that reproduce the legacy results: exact official →
   genuine; recompressed/resized screenshot → genuine; changed date line → altered; unrelated images →
   unverified; Arabic scam text → scam_risk; "hello" → unverified. Add a CLI `python -m engine.check <image>`
   that prints verdict, distance, changed_pct for threshold tuning.
2. **Bot/API agent** — owns `api/`. Twilio webhook (signature validation, media download with basic auth,
   upload to Supabase Storage, call engine, insert report + sender, TwiML Arabic reply, respond < 10 s),
   `/api/correct` (real WhatsApp sends via Twilio REST, admin token), Vercel config/rewrites,
   `requirements.txt` without scipy. Pick the emirate from a weighted list for the demo (document it).
3. **Dashboard agent** — owns `app/`. Port the legacy dashboard design (dark "National Trust Control Center",
   KPI strip, live feed, UAE map with pulsing hotspots sized by OPEN fakes that turn teal ✓ when corrected,
   per-report dots, ripple on new report, activity chart, forensic view with animated steps + side-by-side
   images + similarity bar + heat-map overlay for altered images, trending fakes with Push official correction
   + toast). Use react-leaflet with `dynamic(..., { ssr: false })`, CARTO dark tiles, Supabase Realtime
   subscriptions, Arabic/English labels. Make it look premium on a 1920×1080 projector; add a "Demo mode"
   toggle that hides seeded data counts if needed. Map hotspot tooltips and a ranking panel show
   **fake reports per 100,000 residents** (from the government population data) next to raw counts. Add an
   "Open data" panel listing each government dataset used, its publisher and what it powers.
4. **Data & assets agent** — owns `supabase/`, `scripts/`, `assets/`. Migrations from CONTRACT.md;
   generate 6–8 realistic Arabic official-announcement images (government-style header, logo placeholder, date)
   + 2 doctored versions + 2 fake rumour images ("explosions in Downtown Dubai", "Burj Khalifa collapse") +
   scam texts, all clearly fictional; `seed_registry` script (hash + upload official posts); `demo_seed` /
   `demo_clear` scripts (~55 reports over last 60 min, same scenarios/weights as legacy demo_seed.py).
   **Government open data is REQUIRED by the rubric ("open data provided by government entities", 15%).
   Use ONLY official government portals** and make the data drive real features, not decoration:
   a) Trusted-source registry → `entities` table from Bayanat's entity list (https://bayanat.ae/en/entities)
      and the Dubai Pulse organisation register (https://www.dubaipulse.gov.ae/registers/orgztoa). The engine's
      "not issued by any registered government entity" message and any future link check use this table.
   b) Per-capita risk map → population tables: FCSC open data
      (https://opendata.fcsc.gov.ae/@federal-competitiveness-and-statistics-center/uae-population-estimates-by-gender-age-group-year,
      find the by-emirate breakdown on opendata.fcsc.gov.ae / bayanat.ae) and Dubai Pulse population by community
      (https://www.dubaipulse.gov.ae/data/dsc-statistics/dsc_population_by_community-open). Dashboard shows
      "fake reports per 100,000 residents" and a "where to target the Verify Before You Share campaign" ranking;
      if age breakdowns are usable, weight by share of older residents.
   c) Dubai area names/codes → Dubai Pulse area lookup (https://www.dubaipulse.gov.ae/data/dld-transactions/dld_lkp_areas-open).
   Open each dataset and confirm columns and download format before using it; drop any that don't fit and say so.
   Store raw downloaded files in `assets/open-data/` and write `DATA_SOURCES.md` with exact dataset names,
   publisher, URL, date accessed and which feature uses each (this is copied onto the Data slide).
   The team will also ask organisers whether the Challenge 40 owners (Cyber Security Council, TDRA, DESC) provided
   challenge-specific datasets; leave a clearly marked place to load them first if they arrive.
5. **QA & deploy agent** — owns `scripts/e2e/` and `DEPLOY.md`. Script that POSTs Twilio-style form requests
   (text, image URLs) to a local and the deployed `/api/whatsapp` and checks verdicts + DB rows; Playwright
   screenshot of the dashboard at 1920×1080; step-by-step DEPLOY.md (GitHub → Vercel import, env vars,
   Supabase setup, Twilio sandbox webhook, re-join sandbox note, production domain); a pre-pitch checklist.

## After agents finish (lead)
- Merge, run all tests, deploy to Vercel production, run the e2e script against production.
- Walk me through the real-phone gate test: "hello" → ⚪; Arabic scam text → 🔴; official image → ✅;
  tight-cropped screenshot → ✅; doctored → 🔴 altered; unrelated photo → ⚪; dashboard shows each instantly;
  Push correction → real WhatsApp correction arrives on the phone.
- Report anything not done, honestly. Then update CLAUDE.md "Status/TODO" for the new stack.

Ask me only for things you cannot do yourself (account creation, pasting keys, scanning a QR, joining the
sandbox). Batch those requests into one list at the start so I can do them while the agents work.
