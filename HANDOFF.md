# HAQEEQ — SESSION HANDOFF (for a new Claude account/session)

Written Tue 10 Nov 2026, ~20:00 Dubai (UTC+4). Pitch is **Wed 11 Nov 2026**; the deck must be submitted on
admin.hackathon.ae by **~10:00am Wed**. Read this file first, then `CLAUDE.md` (full event/rubric/evidence/pitch
context — still accurate for those parts), `CONTRACT.md` (architecture), `DATA_SOURCES.md`, `api/README.md`.
**No secrets are in this file or the repo.** Secrets live only in Vercel env vars / the user's Meta, Twilio, Supabase accounts.

---------------------------------------------------------------------------------------------------

## 0. One-paragraph summary

Haqeeq (حقيق) = Arabic WhatsApp bot + government dashboard for UAE Hackathon 2026, Challenge 40 ("Building Trust in
Digital Content"). A citizen forwards an official-looking image/text to a WhatsApp number and gets an Arabic verdict
(✅ genuine / 🔴 altered / ⚪ unverified / 🔴 scam risk); every forward lands on a live "National Trust Control Center"
dashboard (UAE map, forensic view, trending fakes, Push official correction). The original Replit/Flask build was
abandoned; it was **rebuilt this session on Vercel + Supabase (+ Gemini)** using five parallel subagents, then the
messaging channel was moved from Twilio (blocked by trial limits) to **Meta WhatsApp Cloud API**. Everything works
end to end on real phones **except that the Meta access token keeps expiring** (see section 4 — this is the single
open blocker).

## 1. People and preferences

- User: aburamadannuha@gmail.com, GitHub `05nuha`, team of 2 (the user = cybersecurity student, "Person A"; a friend =
  CIT student, "Person B", now doing the dashboard UI + slides). Dubai-based, Pioneers track.
- Wants concrete step-by-step instructions, decisive recommendations (not option lists), exact where-to-click, short
  replies. Tired/under time pressure. Never ask them to paste secrets into chat — secrets go straight into Vercel,
  or via the secure `request_credential` form. Honest claims only (seeded data, mocked signing key, map ≠ spread path).
- Rubric weights (optimise for these): Alignment 15, **Data 15**, **AI 15**, **Feasibility + 90-day plan 20**, Market 15,
  **Pitch 20**. 40% is non-code (90-day plan + pitch) — don't let more building eat deck/rehearsal time.

## 2. Live system (what exists right now)

| Thing | Value |
|---|---|
| Dashboard + API (Vercel) | https://haqeeq.vercel.app (`/` and `/dashboard`), API under `/api/*`; push to `main` auto-deploys |
| GitHub | github.com/05nuha/haqeeq (branch `main`) |
| Supabase project | ref `voqslacetqbrkoueaptz` (Postgres + Storage bucket `media` public-read + Realtime on `reports`,`corrections`) |
| Meta WhatsApp test number | **+1 555 167 8203** (Phone number ID `1471731529349147`, WABA ID `1695628978747111`, Meta App ID `1073688265715265`, business id `1687844378236847`). Only phone numbers added under "To" on the API Testing page can use it |
| Meta webhook | `https://haqeeq.vercel.app/api/meta` (verify token = Vercel `META_VERIFY_TOKEN`), `messages` field subscribed; WABA→app subscription was done via `GET /api/meta?diag=1&waba=1695628978747111&subscribe=1` |
| Twilio (not used any more) | WhatsApp sender +1 737 221 2163, webhook `/api/whatsapp` still works (signature validated) but replies can't be delivered on trial (see 5) |
| Gemini | `GEMINI_API_KEY` set in Vercel; default model `gemini-3.5-flash-lite` (override `GEMINI_MODEL`); confirmed working live (`ai_used:true`, Arabic reasons) |
| Debug endpoints | `GET /api/health` (all env flags, registry count, error), `GET /api/meta` (last webhook + send result), `GET /api/meta?diag=1[&waba=ID][&subscribe=1][&business=ID]` (token validity/expiry/scopes/subscription/phone number), `GET /api/whatsapp` (last Twilio request) |

Vercel env vars set (Production + Preview): `SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
(holds the new `sb_secret_…` style key — code sends it as `apikey` only, accepts several alias names),
`SUPABASE_ANON_KEY`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` (publishable key), `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`,
`TWILIO_WHATSAPP_FROM` (should be `whatsapp:+17372212163`), `GEMINI_API_KEY`, `DASHBOARD_ADMIN_TOKEN`, `BASE_URL`
(code accepts `PUBLIC_BASE_URL` or `BASE_URL`; the user named it `BASE_URL`), `META_WHATSAPP_TOKEN`,
`META_PHONE_NUMBER_ID`, `META_VERIFY_TOKEN`. Optional: `META_APP_SECRET` (enables webhook signature check),
`TWILIO_CONTENT_SID`, `HAQEEQ_*` thresholds. Never set `SKIP_TWILIO_SIG` in Vercel.

## 3. Architecture and repo map

One Vercel project: Next.js (App Router, Tailwind, react-leaflet, chart.js) at repo root + Python serverless functions
in `api/` (single Flask app in `api/_lib/app.py`; thin entry files `api/whatsapp.py`, `api/meta.py`, `api/correct.py`,
`api/health.py` re-export it; `vercel.json` includes `engine/**` and `api/_lib/**`). **Never create `app/api/*`.**
Supabase schema: `supabase/migrations/0001_init.sql` (already run): `official_posts`, `known_fakes`, `senders`
(server-only), `reports` (anon may select all columns except `sender_id`), `corrections`, `entities`, `population`,
`dubai_areas`, `open_datasets`, bucket `media`.

```
engine/          numpy-only pHash + tamper check + crop search + text scam check (+Gemini) + Arabic replies; tests in engine/tests
api/_lib/app.py  channel-agnostic _process(); routes: /api/whatsapp (Twilio), /api/meta (Meta), /api/correct, /api/health
api/_lib/supa.py tiny PostgREST/Storage client (requests)
app/, components/, lib/   dashboard (mock mode: ?mock=1)
scripts/         seed_registry.py, load_open_data.py, demo_seed.py, demo_clear.py, make_assets.py, fetch/build_open_data.py, e2e/
assets/          official/ doctored/ screenshots/ fakes/ unrelated/ fonts/ open-data/ demo_texts.md
legacy-flask/    original Replit/Flask code (reference + fallback, untouched)
CLAUDE.md CONTRACT.md DEPLOY.md PREPITCH_CHECKLIST.md (Twilio-oriented — use Meta) DATA_SOURCES.md HANDOFF.md
```

Tests: `python -m pytest -q engine api/tests` → 39 passed at last run.

### Engine facts
- Verdicts: genuine | altered | unverified | scam_risk. Exact Arabic replies in `engine/replies.py` (from CLAUDE.md §8).
- Image: pHash (64-bit, numpy DCT) vs registry, `MATCH_THRESH`=12; then 256×256 grey per-pixel diff, `PIXEL_THRESH`=55,
  `TAMPER_PCT`=0.04% → genuine/altered; 16×16 heat grid. Known fakes (`known_fakes`) → unverified with that fake's detail.
- **Crop search** (added today): if whole-image match fails, multi-scale/aspect crop search on pHash (strict
  `CROP_MATCH_THRESH`=6) + pixel box alignment, so real phone screenshots with status/browser bars still verify.
  Simulated phone screenshots: genuine ✅ (0.02%), doctored 🔴 (0.95%), unrelated/fakes stay ⚪. **A camera photo of a
  laptop screen does NOT match (by design).** The user hasn't yet confirmed a *real* phone screenshot post-deploy.
- Text: rules (≥2 EN+AR keyword hits, Arabic normalisation) OR Gemini "high" → scam_risk; canonical `detail` labels
  for "Dubai Police fine" and "Emirates ID suspended" so live forwards join seeded trending groups.
- Known limit: single-digit date edits can fall under TAMPER_PCT (0.027% < 0.04%); tune `HAQEEQ_TAMPER_PCT` (0.02) with real images.

### Replies via Meta
`api/_lib/app.py: meta_send()` posts plain text via Graph API (`META_GRAPH_VERSION` default v23.0). Replies are one
message (verdict + "🤖 Gemini reason" on a new line for scam_risk). `/api/correct` sends real WhatsApp corrections via
Meta when `META_WHATSAPP_TOKEN`+`META_PHONE_NUMBER_ID` are set (else Twilio). **End-to-end correction delivery on a real
phone has NOT been tested yet.**

### Dashboard
Dark control-center UI, 1920×1080 design. Features: KPI strip, live feed, UAE map (Esri dark tiles fallback because
CARTO returned "API KEY REQUIRED" tiles from the sandbox — check the map on the venue network), activity chart, forensic
view with heat-map overlay, trending fakes + Push official correction (Operator unlock = admin token in localStorage →
`X-Admin-Token`), per-100k ranking, Open data panel, Demo-mode toggle, honesty footer. `?mock=1` = offline sample data.
The user thinks the UI "looks a mess"; their friend is redesigning it (branch workflow: edit `components/*.tsx` and
`app/globals.css`, `npm run dev`, open `/?mock=1`, `npm run build` must pass, push a branch → Vercel preview → merge).
I never verified Realtime updates against the real project (only saw mock-mode screenshots and a 401-polluted container capture).

### Data loaded into Supabase
8 official posts + 2 known fakes (`scripts/seed_registry.py`); open data (`scripts/load_open_data.py`): 57 Bayanat
entities, 7 emirate populations (u.ae "The Seven Emirates"; **different years per emirate, UAQ=2005, RAK=2015, Ajman=2017 →
per-100k overstated for those; no age data so `older_share` null**), 264 Dubai area names (Bayanat copy of DLD data, 2017),
4 `open_datasets` catalogue rows; 55 seeded demo reports. **Dubai Pulse portal and FCSC opendata portal were unreachable
from the build sandbox** → Dubai Pulse org register / population-by-community not used; say so honestly on the Data
slide (paragraph in DATA_SOURCES.md). Demo images are publicly reachable:
`https://voqslacetqbrkoueaptz.supabase.co/storage/v1/object/public/media/demo/` + `1-official.png`, `2-screenshot.jpg`,
`3-doctored.png`, `4-fake-explosions.png`, `5-unrelated.png`, `6-official-mohre.png`, `7-doctored-visa.png`.
Real test rows (ids ~60–80+, `seeded=false`) exist in `reports`; before the pitch run
`python scripts/demo_clear.py && python scripts/demo_seed.py` (needs `SUPABASE_URL` + service key in env).

### Gate test status (real phones, via Meta, before the token expired)
hello → ⚪ ✔; scam text → 🔴 ✔ (+Gemini reason); official image → ✅ ✔; (simulated) screenshot → ✅; doctored → 🔴 ✔;
fake → ⚪ ✔; unrelated → ⚪ ✔ (when sent as the image file). A *laptop-screen photo* returned ⚪ (expected → led to crop search).

## 4. THE OPEN BLOCKER — Meta access token (read carefully)

Meta's WhatsApp test setup issues **short-lived user tokens** (the API Testing page's "Generate access token"; the user
reports ~1 hour; one earlier lasted until 13:00 Dubai). When it expires, Meta rejects replies (`/api/meta` shows
`send_error` code 190 "Session has expired"), although inbound messages are still received and saved. Attempts so far:

1. **System user token (permanent route)**: Business settings → System users. Admin role is blocked (account <7 days old);
   created an **Employee** system user `haqeeq-bot`, assigned the app + "Test WhatsApp Account", generated tokens.
   The token is valid (expires 2027-01-09, correct scopes) and Meta accepts it for the phone-number lookup, **but sending fails
   with `(#10) Viewer cannot access the provided Paid Message Account 1695628978747111`** even after giving the system user
   "Everything" on the WhatsApp account and regenerating the token. Likely the test WABA is owned by Meta's test business,
   not the user's portfolio, so system-user tokens can't use it. **Dead end for the test number.**
   ⚠ **The token currently in Vercel `META_WHATSAPP_TOKEN` may be this system-user token → replies will fail until it's replaced.**
2. **60-day exchange (recommended next step, not completed)**: in the user's own browser open
   `https://graph.facebook.com/v23.0/oauth/access_token?grant_type=fb_exchange_token&client_id=1073688265715265&client_secret=<APP_SECRET>&fb_exchange_token=<SHORT_TOKEN_FROM_API_TESTING_PAGE>`
   → JSON with a ~60-day `access_token`; paste into Vercel `META_WHATSAPP_TOKEN`, Redeploy. (App secret: App settings → Basic → Show;
   never paste it in chat.) The user chose instead to "just use the token that lasts an hour" for tonight.
3. Other durable options if (2) fails: build a server-side exchange helper (needs `META_APP_ID` + `META_APP_SECRET` in Vercel);
   register the user's own business number with a real WABA (more setup, business verification may be required); fall back to Twilio
   with a paid account (see 5).

**Verify a token with:** `curl -s "https://haqeeq.vercel.app/api/meta?diag=1&waba=1695628978747111"` (look at `token_valid`,
`token_expires_at`, `phone_number`), then have the user text `hello` to +1 555 167 8203 and read `GET /api/meta` →
`last_request.send_status` / `send_error`. After changing a Vercel env var the user must **Redeploy** and wait until Ready.
**On pitch morning: refresh the token and test `hello` before going on stage.**

## 5. Twilio history (why it was dropped)

The user's WhatsApp sender (+1 737 221 2163, trial) delivered inbound messages to our webhook (signature check OK, Gemini
replies generated) but **outbound replies never arrived**: Twilio REST said `ContentSid Required` (sender only accepts
Content templates), and Content Template Builder is **not available on the trial**; the Content API returned 401 for the
bot. Replies as TwiML were silently dropped. The `TWILIO_REPLY_MODE`/content-template fallback code remains in `api/_lib/app.py`.
Note: a basic-auth credential for `api.twilio.com` was saved on the *Claude cloud environment* via the secure form but Twilio
returned 20003 (wrong credentials); it's irrelevant now. Twilio's phone-based sandbox `join` codes expire ~72h.

## 6. Environment / process notes for a Claude session

- The build container's network is "unrestricted" but proxies HTTPS. Supabase access from the container worked because the
  user saved the Supabase secret via `request_credential` (host `voqslacetqbrkoueaptz.supabase.co`, injected by proxy — use
  `apikey: proxy-injected` in curl). A **new Claude account will not have this** — ask the user for credentials via the secure
  form or have them run scripts locally. Gemini couldn't be saved that way (header name not allowed); we verified Gemini through
  the live bot instead.
- A Stop hook asks to commit + push any untracked files; commits are appended with the attribution lines the system provides.
- Parallel agents used: engine/api/dashboard/data on Sonnet, QA/deploy docs on Haiku. Their reports flagged: Vercel docs were
  unreachable (config written from memory; verified live — `engine/` bundling works), CARTO tiles blocked, Gemini model name
  unverified against Google docs (works in practice).
- I (assistant) changed after the agents finished: scam logic (rules OR AI), "hello" → ⚪ (not a help message), tolerant
  Twilio signature URL matching, REST/template reply path, Meta channel + diagnostics, crop search, `BASE_URL` alias,
  env fallbacks for the dashboard (`SUPABASE_URL`→`NEXT_PUBLIC_*`).

## 7. TODO, in priority order

1. **Fix the Meta token** (section 4): do the 60-day exchange, paste, redeploy, `hello` test. Then re-test everything from a real phone
   incl. a **real phone screenshot** of `1-official.png` (power+vol-up, crop tight) → expect ✅; doctored → 🔴.
2. **Test Push official correction end-to-end**: send `4-fake-explosions.png`, open dashboard, Operator unlock (admin token),
   click Push correction on "explosions" → correction must arrive on the user's WhatsApp.
3. Friend: dashboard visual redesign on a branch (see section 3); check it at 1920×1080 on the venue network (map tiles).
4. **Deck** (Gamma): problem, solution, live demo, impact, **90-day plan slide**, **Business Model Canvas page**, ask. Text for the
   90-day plan, BMC, pitch timing, judge Q&A is in CLAUDE.md §13; Data-slide paragraph in DATA_SOURCES.md. Rehearse ≥3 times.
5. **Create the team on admin.hackathon.ae** (UAE Pass → My Team → Create Team) and **submit by ~10:00am Wed 11 Nov**.
6. Record a **backup demo video** of the full run; bring phone hotspot.
7. Pitch morning: refresh Meta token (+redeploy), confirm the phones are listed under "To", `demo_clear.py` + `demo_seed.py`,
   open dashboard (Operator unlock) at 1920×1080, test `hello`.
8. Optional polish: record real thresholds if any verdict misbehaves (`HAQEEQ_TAMPER_PCT`, `HAQEEQ_MATCH_THRESH`,
   `HAQEEQ_CROP_MATCH_THRESH`); update PREPITCH_CHECKLIST.md/DEPLOY.md for Meta (they describe Twilio).

## 8. Honest caveats to keep in the pitch/slides

Seeded background activity (labelled "simulated"); government signing key/PKI is mocked (no real C2PA); the map shows where
reports come from, not the encrypted WhatsApp spread path; emirate of live reports is a weighted-random demo pick; "unverified"
never means "proven fake"; voice/video not checked yet; population denominators come from u.ae statements of different years;
Dubai Pulse/FCSC portals were not accessible, so those datasets were not used.

## 9. Core timeline (Dubai)

Mon 9 Nov Day 1 (concept, research, Flask code on Replit) → Tue 10 Nov Day 2: Replit dropped; Vercel+Supabase rebuild with 5 agents;
Twilio debugging; switched to Meta; gate test passed on real phones; crop search added; token expiry problem → Wed 11 Nov Day 3: submit
deck by ~10am, pitch (3 min + 2 min Q&A). After: Innovation Summit 16 Nov; winners' LaunchPad 18 Nov–3 Dec.
