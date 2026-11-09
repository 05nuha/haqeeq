# Haqeeq E2E checks

Two checks that exercise the real system the way a judge's phone would:

| File | What it does |
|---|---|
| `whatsapp_e2e.py` | Plays Twilio: signs and POSTs WhatsApp-shaped forms to `/api/whatsapp`, checks the Arabic TwiML reply, optionally checks the `reports` row in Supabase. |
| `screenshot.js` | Screenshots the dashboard at 1920x1080 to `scripts/e2e/out/dashboard-1920.png` and prints console errors. |

Files: `cases.json` (image cases), `out/` (screenshots, git-ignored).

## 1. Setup

Python 3.12+ with `requests` (`pip install requests`). Node 22 with Playwright for the screenshot.
Do **not** run `npx playwright install`: the Chromium in the container is used by `chromium.launch()`.

You need the same `TWILIO_AUTH_TOKEN` the server uses. Never paste it into a chat or commit it.

```bash
export TWILIO_AUTH_TOKEN='...'          # same value as the server
export PUBLIC_BASE_URL='https://<prod>.vercel.app'   # what the server signs against
```

## 2. Run against local dev

Start the server locally (with `SKIP_TWILIO_SIG=1` in `.env.local` if you do not want to sign), then:

```bash
# Signature ON (default). Server must have PUBLIC_BASE_URL matching --public-url below.
python scripts/e2e/whatsapp_e2e.py --base-url http://127.0.0.1:5328 \
  --public-url http://127.0.0.1:5328/api/whatsapp

# Server started with SKIP_TWILIO_SIG=1: no signature sent, bad-signature check skipped.
python scripts/e2e/whatsapp_e2e.py --base-url http://127.0.0.1:5328 --no-sig
```

Local Vercel dev (`vercel dev`) usually serves on `http://localhost:3000`; use that as `--base-url`.

Text cases only (no image hosting needed): add `--skip-images`.

## 3. Run against production

```bash
python scripts/e2e/whatsapp_e2e.py \
  --base-url https://<prod>.vercel.app \
  --image-base-url https://<project-ref>.supabase.co/storage/v1/object/public/media/ \
  --check-db
```

`--check-db` needs `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` in the shell. It reads
`reports` only (service key, never the browser). It confirms that each case wrote a new
non-seeded row with the expected verdict.

Image cases in `cases.json` use relative paths. They are resolved against `--image-base-url`.
Before the first production run, upload the fixtures to the `media` bucket:

1. Supabase dashboard -> Storage -> `media` -> Upload files (verify UI label).
2. Create folder `test/` and upload:
   - a tight screenshot of the official `public_holiday_notice` post -> `test/screenshot_public_holiday_notice.jpg`
   - a doctored copy (changed date) -> `test/doctored_public_holiday_notice.png` (take from `assets/doctored/`)
3. `official/public_holiday_notice.png` and `fakes/explosions_downtown.png` are written by the
   seed scripts. If a file is missing, the case fails with the HTTP/verdict detail shown.

Filenames in `cases.json` must match what is actually in `assets/`; check with `ls assets/*`.

## 4. Reading the output

```
CASE                                   RESULT  DETAIL
-----------------------------------------------------------------------
bad signature -> 403                   PASS    HTTP 403
text: hello                            PASS    unverified in 0.4s | db row ok
text: Arabic scam                      PASS    scam_risk in 0.6s | db row ok
image: official notice, original       PASS    genuine in 2.1s | db row ok
...
```

Exit code `0` = all pass, `1` = at least one failure, `2` = missing config.

Signature self-check (no network):

```bash
python scripts/e2e/whatsapp_e2e.py --selftest
```

## 5. Screenshot

```bash
node scripts/e2e/screenshot.js                                  # http://localhost:3000/?mock=1
node scripts/e2e/screenshot.js https://<prod>.vercel.app/?mock=1
```

Open `scripts/e2e/out/dashboard-1920.png`. Console errors print after the save line. Map tiles come
from CARTO, which some networks block; the script warns and still saves.

## 6. Common failures

| Symptom | Likely cause |
|---|---|
| `bad signature -> 403` shows HTTP 200 | Server has `SKIP_TWILIO_SIG=1` set. Use `--no-sig`, or remove the variable in production. |
| Every signed case returns 403 | `--public-url` / `PUBLIC_BASE_URL` does not equal the URL the server sees, or `TWILIO_AUTH_TOKEN` differs. |
| Image case 401/502 from the bot | Server cannot download media: wrong `TWILIO_ACCOUNT_SID`/`TWILIO_AUTH_TOKEN`. |
| Image case returns "unverified" when expected genuine | Registry not seeded (`python scripts/seed_registry.py`) or thresholds too tight (`HAQEEQ_MATCH_THRESH`). |
| `no new reports row` | The write failed server-side, or `--check-db` is pointed at a different project than the server. |
| TwiML parse error | Function timed out or returned an error page; check Vercel function logs. |
