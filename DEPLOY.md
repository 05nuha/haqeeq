# Haqeeq — deploy guide (for the whole team)

Written for students who have not deployed before. Follow the steps in order. Each step ends with a
check. If a check fails, go to section 9 (troubleshooting) before moving on.

**UI labels in this guide were written from memory of the Vercel, Supabase, Twilio and Google AI Studio
dashboards. The docs sites were not reachable when this was written, so every label is marked
"verify in UI". If a button has moved, the action is the same: look for the word in brackets.**

Deadline: if the Vercel version does not pass the real-phone gate test by **Tue 10 Nov 2026, 1 pm
(Dubai)**, use the fallback in section 10. Pitch is **Wed 11 Nov 2026**.

Keep open at all times: a notepad with the values you copy in steps 2 to 6 (never share it outside
the team).

---

## (a) GitHub: create the repository and push

1. Go to https://github.com/new (log in first).
2. Repository name: `haqeeq`. Visibility: **Private** (verify in UI: the "Private" radio button).
   Do **not** tick "Add a README" (the repo already has files).
3. Click **Create repository** (verify in UI).
4. On the repo page, copy the HTTPS URL (green **Code** button → HTTPS).
5. On your computer, open a terminal in the project folder `haqeeq`, then run:
   ```bash
   git status                       # must NOT list .env or .env.local
   git add -A
   git commit -m "Haqeeq: initial import"
   git branch -M main
   git remote add origin <paste the HTTPS URL>
   git push -u origin main
   ```
   If git asks for a password, use a GitHub Personal Access Token, not your GitHub password
   (GitHub → Settings → Developer settings → Personal access tokens; verify in UI).
6. Check: the files show up on the GitHub page. `.env.local` and `.env` must **not** be there.

---

## (b) Supabase: database, storage, realtime

1. Go to https://supabase.com → **Start your project** → sign in with GitHub.
2. Click **New project** (verify in UI). Fill in:
   - **Name**: `haqeeq`
   - **Database password**: generate one and save it in your notepad.
   - **Region**: pick the one closest to the UAE that is offered. Mumbai (`ap-south-1`) is the usual
     choice; Frankfurt is the fallback. Verify in UI which options exist.
3. Click **Create new project** and wait 1–2 minutes until the dashboard loads.
4. Run the schema: left menu → **SQL Editor** → **New query** (verify in UI).
   - Open `supabase/migrations/0001_init.sql` from the repo, copy everything, paste into the editor.
   - Click **Run** (verify in UI). Expect "Success. No rows returned".
   - Run any later migration files in `supabase/migrations/` the same way, in filename order.
   - The script is written so re-running is safe (`if not exists`, `on conflict`).
5. Check the storage bucket: left menu → **Storage** → you should see a bucket named **`media`**.
   Click it. Its visibility must say **Public** (verify in UI: a badge or the bucket's settings).
   If it is private, open the bucket's settings and switch it to public.
6. Check Realtime: left menu → **Database** → **Replication** (verify in UI; older dashboards call it
   **Realtime** under Database). Under the `supabase_realtime` publication, `reports` and
   `corrections` must both be enabled. The migration does this; if either is missing, toggle it on.
7. Copy the keys: left menu → **Project Settings** (gear icon) → **API** (verify in UI; newer
   dashboards may show "API Keys" with publishable and secret keys). Copy into your notepad:
   - **Project URL** → `SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_URL` (same value)
   - **anon public** key → `SUPABASE_ANON_KEY` and `NEXT_PUBLIC_SUPABASE_ANON_KEY` (same value)
   - **service_role** key → `SUPABASE_SERVICE_ROLE_KEY`. **Secret.** Never put it in a `NEXT_PUBLIC_`
     variable, never in the browser, never in git.
8. Check: in **Table Editor**, you can see `official_posts`, `known_fakes`, `reports`, `corrections`
   and the other tables. (They are empty until step 4 of section (d).)

---

## (c) Vercel: import the repo and deploy

1. Go to https://vercel.com → sign up or log in with GitHub.
2. Click **Add New…** → **Project** → find `haqeeq` → **Import** (verify in UI).
3. **Framework Preset**: **Next.js** (it should be detected automatically; check the dropdown).
   **Root Directory**: leave as `./`. Leave the build command as default.
4. Open **Environment Variables** on the same import screen (verify in UI). Add each variable below.
   For each one, choose the environments listed. Both "Production" and "Preview" are the two boxes
   in the Environment dropdown (verify in UI).

   | Variable | Production | Preview | Notes |
   |---|---|---|---|
   | `SUPABASE_URL` | yes | yes | Project URL from (b)7 |
   | `SUPABASE_ANON_KEY` | yes | yes | anon key |
   | `SUPABASE_SERVICE_ROLE_KEY` | yes | yes | **secret**: Production and Preview only, never Development in the team's shared settings |
   | `NEXT_PUBLIC_SUPABASE_URL` | yes | yes | same as `SUPABASE_URL`; the browser needs it at build time |
   | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | yes | yes | same as `SUPABASE_ANON_KEY` |
   | `TWILIO_ACCOUNT_SID` | yes | yes | Twilio console home (step e) |
   | `TWILIO_AUTH_TOKEN` | yes | yes | **secret**; same screen as the SID (click the eye icon to show) |
   | `TWILIO_WHATSAPP_FROM` | yes | yes | `whatsapp:+14155238886` (sandbox number) |
   | `GEMINI_API_KEY` | yes | yes | from step (f) — add it later if you do not have it yet, then redeploy |
   | `GEMINI_MODEL` | yes | yes | optional; leave empty to use the default |
   | `DASHBOARD_ADMIN_TOKEN` | yes | yes | make up a long random string; this is the operator unlock password |
   | `PUBLIC_BASE_URL` | yes | **no** | the stable production domain from step 6 below; **Production only** |
   | `HAQEEQ_MATCH_THRESH` | optional | optional | default 12; leave unset unless the registry check tells you otherwise |
   | `HAQEEQ_PIXEL_THRESH` | optional | optional | default 55 |
   | `HAQEEQ_TAMPER_PCT` | optional | optional | default 0.04 |

   **Never set `SKIP_TWILIO_SIG` in Production or Preview.** It turns off signature checking and is for
   local tests only.

   For the first deploy, leave `PUBLIC_BASE_URL` empty or set a placeholder. You fill it in at step 6.
5. Click **Deploy** (verify in UI). Wait for the build. It usually takes 1–3 minutes.
   If the build fails, read the red log line, fix it in the repo, push again (section (a) step 5), and
   Vercel redeploys automatically.
6. Find the **stable production domain**: open the project → **Overview** (or **Domains** in
   **Settings**; verify in UI). It looks like `haqeeq-<something>.vercel.app`. Use the one without a
   long hash in the middle (the "production" domain, not a preview URL that contains a commit hash).
   Copy it.
7. Set `PUBLIC_BASE_URL`: project → **Settings** → **Environment Variables** → **Add** (verify in UI).
   - Key: `PUBLIC_BASE_URL`
   - Value: `https://<that domain>` (no trailing slash)
   - Environment: **Production** only.
8. Redeploy so the new variable is used: **Deployments** tab → the latest **Production** deployment →
   **⋯** → **Redeploy** (verify in UI). Wait until it shows **Ready**.
9. Check: open `https://<prod-domain>/api/health` in a browser. Expect JSON with `"ok": true`.
   (Section (g) explains this check in detail.)

---

## (d) Seed the data

Run these on your computer, in the repo folder, with your `.env` file filled in. Use a Python 3.12+ virtual environment.

1. Create the local env file: copy `.env.example` to `.env` (in the repo root) and fill in the Supabase
   and Twilio values. Never commit it.
2. Install the Python packages:
   ```bash
   python -m venv .venv
   source .venv/bin/activate          # Windows: .venv\Scripts\activate
   pip install -r scripts/requirements.txt
   ```
3. Load the trusted-source registry (official posts with fingerprints, images uploaded to `media`):
   ```bash
   python scripts/seed_registry.py
   ```
   Expect a line like `Seeded N official posts`. (Verify the exact message: the data agent writes this script.)
4. Load the open-data tables (entities, population, Dubai areas, dataset catalogue):
   ```bash
   python scripts/load_open_data.py
   ```
5. Load the demo background (fake reports, trending groups, the known fakes):
   ```bash
   python scripts/demo_seed.py
   ```
   Check the flags first with `python scripts/demo_seed.py --help` (verify the clear/reset option).
   Clear and reseed right before a demo (see the pitch checklist).
6. Check in the Supabase **Table Editor**: `official_posts` has rows, `reports` has rows with
   `seeded` = true.

---

## (e) Twilio: WhatsApp sandbox

1. Go to https://console.twilio.com and sign up or log in (verify in UI).
2. On the console home page, copy **Account SID** and **Auth Token** (click the eye icon to show it)
   → `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` in Vercel (Production and Preview) and in your local `.env`.
   The Auth Token is a secret: do not share it.
3. Open the WhatsApp sandbox: left menu → **Messaging** → **Try it out** → **Send a WhatsApp message**
   (verify in UI; the path may change, search the console for "WhatsApp sandbox").
4. On that page you will see:
   - the **sandbox number** (`+1 415 523 8886` at the time of writing, verify in UI) → `TWILIO_WHATSAPP_FROM=whatsapp:+14155238886`
   - a **join code** of the form `join <two-words>`. Copy it.
5. **Every demo phone** (each team member's phone): open WhatsApp, send a message to the sandbox number
   with the exact text `join <your code>`. Wait for the confirmation reply.
6. Set the webhook: on the same sandbox page, find **Sandbox configuration** (verify in UI) →
   - **When a message comes in**: `https://<prod-domain>/api/whatsapp`
   - Method: **POST**
   - Click **Save** (verify in UI).
   The URL must be the production domain from (c)6, not a preview URL.
7. Check: send `hello` from a joined phone. You should get the ⚪ reply within a few seconds.
8. **Sandbox joins expire after about 72 hours.** The morning of the pitch, every phone must send
   `join <code>` again. Do this on Day 3 morning (see the pitch checklist).

---

## (f) Gemini: API key

1. Go to https://aistudio.google.com and log in with a Google account (verify in UI).
2. Click **Get API key** → **Create API key** (verify in UI). Copy the key.
3. Put it in Vercel as `GEMINI_API_KEY` (Production and Preview), and in your local `.env`.
   Redeploy (c)8 after adding it.
4. Check locally:
   ```bash
   python -m engine.gemini_probe
   ```
   It should print that the key works and which model answered. If it reports an error, it prints the
   reason. Without a working key the bot still runs, using the rules-based text check.
   Free-tier quota can run out; if so, the probe prints a quota error.

---

## (g) Health check

Open in a browser or run:
```bash
curl -s https://<prod-domain>/api/health
```
Expect:
```json
{"ok": true, "registry": <number>, "ai": true}
```
- `registry` is the number of official posts loaded (should match the seed step).
- `ai` is `true` when `GEMINI_API_KEY` is set on the server. `false` means the bot falls back to rules.

The first request after a quiet period can take several seconds (cold start). Run this once before
you demo, and again 10 minutes before you present (see the pitch checklist).

---

## (h) Run the end-to-end script against production

From the repo folder, with `TWILIO_AUTH_TOKEN`, `PUBLIC_BASE_URL`, `SUPABASE_URL` and
`SUPABASE_SERVICE_ROLE_KEY` set in your shell:

```bash
python scripts/e2e/whatsapp_e2e.py \
  --base-url https://<prod-domain> \
  --image-base-url https://<project-ref>.supabase.co/storage/v1/object/public/media/ \
  --check-db
```

Expect every row to say `PASS` and the last line to read `N/N passed`. The full details, including
how to upload the test images, are in `scripts/e2e/README.md`.

Then the dashboard:
```bash
node scripts/e2e/screenshot.js https://<prod-domain>/?mock=1
```
Look at `scripts/e2e/out/dashboard-1920.png`. Check it is not blank.

Finally, forward the six demo images and texts from a real phone (pitch checklist, "demo beats") and
watch the dashboard update live.

---

## (i) Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Twilio Monitor → Logs shows **error 11200** ("HTTP retrieval failure") | The webhook URL is wrong, or the function is down or timing out | Check the URL in sandbox configuration matches `https://<prod-domain>/api/whatsapp` exactly; open `/api/health` (section g) |
| `/api/whatsapp` returns **403** | Signature mismatch. Almost always `PUBLIC_BASE_URL` is wrong, or the webhook points at a preview URL | Make `PUBLIC_BASE_URL` the production domain (Production only); redeploy; set the sandbox webhook to the same domain |
| Text works, images fail, Vercel logs show **401** on media download | Wrong `TWILIO_ACCOUNT_SID` or `TWILIO_AUTH_TOKEN` in Vercel | Copy both again from the Twilio console home; redeploy |
| Dashboard is empty, or shows "not connected" | Wrong anon key, RLS blocking reads, or Realtime not enabled | Check `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` (must be the **anon** key, not service role); re-run the migration; enable `reports` and `corrections` in Replication (b)6; redeploy (`NEXT_PUBLIC_` values are baked in at build time) |
| Dashboard works but the operator unlock fails (401) | `DASHBOARD_ADMIN_TOKEN` differs between Vercel and what you type | Use the value from Vercel exactly |
| Function **timeout** (no reply, or Vercel logs show a timeout) | Gemini slow, or cold start, or image download slow | Run `/api/health` before the demo; the bot falls back to rules after a short AI timeout; check Vercel's function duration limit on your plan (verify in UI) |
| Images always **unverified** (even the official ones) | Registry not seeded, or the registry images are missing from `media` | Re-run `python scripts/seed_registry.py`; check `/api/health` `registry` count; tune `HAQEEQ_MATCH_THRESH` (higher = more lenient, default 12) and redeploy |
| `python -m engine.gemini_probe` says quota or 403 | Key invalid or free-tier limit | Create a new key in AI Studio; check quota page |
| Build fails on Vercel | Missing root `requirements.txt` or `package.json` issue | Read the first red line in the build log; fix in the repo, push |

---

## (j) Fallback: revert to the Flask version

Use this only if the Vercel version has not passed the real-phone gate test by **Tue 10 Nov 2026, 1 pm
(Dubai)**. The old version is in `legacy-flask/` and has been tested before.

1. Create an account on https://render.com or https://railway.com (verify in UI).
2. New → **Web Service** (Render) or **New Project → Deploy from GitHub repo** (Railway). Choose the
   `haqeeq` repo and set **Root Directory** to `legacy-flask`.
3. Build command: `pip install -r requirements.txt`. Start command: `python main.py`
   (the legacy app reads `PORT` from the environment; verify the app listens on it).
4. Add the Twilio variables (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`) in the service's environment
   settings.
5. Deploy. Copy the public URL, and set the Twilio sandbox "When a message comes in" to
   `https://<that-url>/whatsapp` with method **POST**.
6. Re-join the sandbox on each phone (section e).
7. Tell the team the demo runs on the legacy version and focus the remaining time on the deck.
