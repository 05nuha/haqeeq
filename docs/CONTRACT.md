# Haqeeq — Build CONTRACT (v1, Phase 0)

Every agent builds against this file. If you need to change it, don't: write the request in your
final report and the lead decides. **Each agent edits ONLY the paths it owns** (section 1).

Reference implementation (do not edit): `legacy-flask/` (engine.py, main.py, dashboard.py,
demo_seed.py, templates/dashboard.html). Product rules: `CLAUDE.md` sections 8, 10, 11, 13.

## 1. Repo layout and ownership

| Path | Owner |
|---|---|
| `CONTRACT.md`, `CLAUDE.md`, `.env.example`, `.gitignore`, `README.md`, `supabase/migrations/0001_init.sql` | Lead |
| `engine/` (package), `engine/tests/`, `requirements-dev.txt` | Engine agent |
| `api/` (Vercel Python functions), `vercel.json`, `requirements.txt` (root), `.python-version` | Bot/API agent |
| Next.js at repo root: `app/`, `components/`, `lib/`, `public/`, `package.json`, `package-lock.json`, `next.config.*`, `tsconfig.json`, `tailwind.config.*`, `postcss.config.*`, `next-env.d.ts`, `eslint` config | Dashboard agent |
| `supabase/` (except 0001), `scripts/` (except `scripts/e2e/`), `assets/`, `DATA_SOURCES.md` | Data & assets agent |
| `scripts/e2e/`, `DEPLOY.md`, `PREPITCH_CHECKLIST.md` | QA & deploy agent |

Python ≥ 3.12. Node 22. One Vercel project: Next.js framework preset; Python functions in `api/`.

## 2. Database (Supabase Postgres)

The schema is **`supabase/migrations/0001_init.sql`** — read it; it is the contract.
Tables: `official_posts`, `known_fakes`, `senders` (server-only), `reports`, `corrections`,
`entities`, `population`, `dubai_areas`, `open_datasets`.

Rules:
- Dashboard uses the **anon key**, SELECT only. `reports.sender_id` is not granted to anon — never
  `select('*')` on reports from the browser; list the columns explicitly.
- All writes use the **service-role key**, server-side only (Python functions and scripts).
- Realtime publication includes `reports` and `corrections` (INSERT/UPDATE events).
- Emirate labels (exact strings): `Abu Dhabi`, `Dubai`, `Sharjah`, `Ajman`, `Umm Al Quwain`,
  `Ras Al Khaimah`, `Fujairah`. (`Al Ain` is allowed in `reports.emirate` as a city of Abu Dhabi; for
  per-capita maths it is folded into Abu Dhabi.)
- `reports.seeded = true` for demo background rows; the bot always writes `false`.
- Sender masking: `phone[:6] + "•••" + phone[-3:]` (phone without `whatsapp:` prefix).

## 3. Storage

Bucket **`media`** (public read, service-role writes). Paths:
- `official/<post_id>.png` — registry images
- `fakes/<fake_id>.png` — known fakes
- `incoming/<uuid4>.jpg` — forwarded images (random names; never the phone number)

Public URL: `${SUPABASE_URL}/storage/v1/object/public/media/<path>`.
Talk to Supabase from Python with plain HTTP (`requests`) against PostgREST
(`/rest/v1/<table>`) and Storage (`/storage/v1/object/media/<path>`) using headers
`apikey: <service key>` and `Authorization: Bearer <service key>`. No supabase-py (keeps the function small).

## 4. Engine API (`engine/` package — pure logic, NO network to Supabase, NO scipy)

```python
from engine import config          # MATCH_THRESH=12, PIXEL_THRESH=55, TAMPER_PCT=0.04, GRID=256,
                                   # overridable by env HAQEEQ_MATCH_THRESH / HAQEEQ_PIXEL_THRESH / HAQEEQ_TAMPER_PCT
from engine import phash, hamming, verify_image, check_text, ARABIC_REPLIES, reply_for

phash(img: PIL.Image.Image | bytes) -> str          # 16 lowercase hex chars (64-bit), numpy DCT-II
hamming(a_hex: str, b_hex: str) -> int               # 0..64

verify_image(
    image_bytes: bytes,
    registry: list[dict],      # rows of official_posts: {id,title,title_ar,issuer,date,phash,image_path}
    load_image: Callable[[str], bytes],   # given a storage image_path -> image bytes (caller caches)
    known_fakes: list[dict] = (),         # rows of known_fakes: {id,title,detail,phash,image_path}
) -> dict
# returns {"verdict": "genuine"|"altered"|"unverified",
#          "matched_id": str|None, "distance": int, "changed_pct": float|None,
#          "heat": list[list[float]] (16x16) | None, "detail": str}
# Logic = legacy engine.py: best official match by Hamming; > MATCH_THRESH -> check known_fakes
# (<= MATCH_THRESH -> unverified with detail = that fake's `detail`), else unverified
# detail "No match in the official registry". Matched -> 256x256 grey per-pixel diff,
# pct of |diff| > PIXEL_THRESH; <= TAMPER_PCT genuine ("Matches <title> (<issuer>)"),
# else altered ("Altered: <title> — <pct>% changed"). heat = 16x16 cell fractions.

check_text(text: str, entities: list[dict] = ()) -> dict
# returns {"verdict": "scam_risk"|"unverified", "detail": str (English, grouping key),
#          "ai_reason": str|None (Arabic), "ai_used": bool}
# Gemini (env GEMINI_API_KEY, GEMINI_MODEL default chosen & verified by engine agent) with JSON output,
# hard timeout <= 6 s, any failure -> rules (>= 2 keyword hits EN+AR -> scam_risk).
# `detail` uses canonical labels when a known scam pattern matches, so live forwards join the
# seeded trending groups. Canonical labels (exact strings, shared with demo_seed):
#   "Scam: 'Dubai Police fine — pay now via link'"
#   "Scam: 'Emirates ID suspended — verify OTP'"
# otherwise "Scam indicators: <words>" / "No official source; verify before trusting".

ARABIC_REPLIES = {   # EXACT strings — do not edit
  "genuine":    "✅ صحيح — يتطابق مع مرجع رسمي متاح.",
  "altered":    "🔴 معدّل — نسخة معدّلة من إعلان رسمي. لا تقم بإعادة إرساله.",
  "unverified": "⚪ غير مؤكد — لم يصدر عن أي جهة رسمية. كن حذراً.",
  "scam_risk":  "🔴 احتيال محتمل — الرسالة تحمل مؤشرات احتيال. تحقق قبل أي إجراء.",
}
reply_for(result: dict) -> str   # ARABIC_REPLIES[verdict] (+ optional second line, e.g. AI reason in Arabic)
```
CLI: `python -m engine.check <image> [--registry-dir assets/official]` prints verdict, distance, changed_pct.

## 5. Canonical demo scenarios (exact `detail` strings — shared by demo_seed, known_fakes, engine)

| kind | verdict | detail | weight |
|---|---|---|---|
| image | unverified | `Fake: 'explosions in Downtown Dubai' image` | 14 |
| image | altered | `Altered: public holiday notice with a fake date` | 8 |
| text | scam_risk | `Scam: 'Dubai Police fine — pay now via link'` | 7 |
| image | unverified | `Fake: AI video of Burj Khalifa collapsing` | 6 |
| text | scam_risk | `Scam: 'Emirates ID suspended — verify OTP'` | 4 |
| image | genuine | `Matches official MOHRE announcement` | 6 |
| image | genuine | `Matches official weekend schedule notice` | 4 |

Known fakes seeded: `explosions_downtown` (detail row 1), `burj_collapse` (detail row 4).
Note: live "altered"/"genuine" forwards get their own detail from the engine ("Altered: <title> — x%").
The trending panel groups by `detail`; the altered holiday-notice official post must have
id `public_holiday_notice` and title `Public holiday notice` so it reads well.

## 6. HTTP API (Python, Vercel functions, all under `/api`)

The Next.js app must NOT define `app/api/*` routes — `/api/*` belongs to Python.

- `POST /api/whatsapp` — Twilio form (From, Body, NumMedia, MediaUrl0, MediaContentType0).
  Validates `X-Twilio-Signature` against the public URL (`PUBLIC_BASE_URL` + `/api/whatsapp`);
  `SKIP_TWILIO_SIG=1` disables (local tests only). Downloads media with basic auth (SID/token), uploads to
  `incoming/<uuid>.jpg`, runs engine, upserts `senders`, inserts `reports`, returns TwiML
  (`Content-Type: text/xml`) with `reply_for(result)`. Must answer < 10 s. Emirate = weighted random demo pick
  (Dubai 8, Sharjah 5, Abu Dhabi 4, Ajman 3, Al Ain 2, Ras Al Khaimah 2, Fujairah 1, Umm Al Quwain 1) — documented as demo.
- `POST /api/correct` — header `X-Admin-Token: <DASHBOARD_ADMIN_TOKEN>`; JSON `{detail, message?}`.
  Upserts `corrections`; sends `message` (Arabic default) via Twilio REST from `TWILIO_WHATSAPP_FROM`
  to every distinct real sender (senders join reports where `detail` matches and `seeded=false`);
  returns `{"ok": true, "recipients": <count of reports with detail>, "delivered": <real sends>}`.
  401 on bad token. CORS: same origin only.
- `GET /api/health` — `{"ok": true, "registry": <n official posts>, "ai": <bool key present>}`.

Dashboard stores the admin token entered by the operator in `localStorage` ("Operator unlock"); never
in `NEXT_PUBLIC_*`.

## 7. Environment variables (see `.env.example`)

`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `TWILIO_ACCOUNT_SID`,
`TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM` (e.g. `whatsapp:+14155238886`), `GEMINI_API_KEY`,
`GEMINI_MODEL` (optional), `DASHBOARD_ADMIN_TOKEN`, `PUBLIC_BASE_URL` (stable production domain),
`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SKIP_TWILIO_SIG` (local only),
`HAQEEQ_MATCH_THRESH`, `HAQEEQ_PIXEL_THRESH`, `HAQEEQ_TAMPER_PCT` (optional tuning).

## 8. Honesty rules (show in UI / docs)

Seeded background data is labelled; government signing/PKI is mocked; the map shows where reports
come from, not the encrypted WhatsApp spread path; emirate of live reports is a demo pick; verdict
"unverified" never claims "proven fake". All demo images are clearly fictional.

## 9. Environment constraints in the build container

This container's network blocks `*.supabase.co`, `vercel.com`, `api.twilio.com`, CARTO tiles and
the government portals unless the lead gets them allowed. Write code that works when deployed; test
locally with fakes/mocks (e.g. a fake Supabase via monkeypatch). Never commit secrets. Never write `{{`
in any template-like file that might go through Jinja (legacy rule; JSX is fine).
