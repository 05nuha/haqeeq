# Haqeeq — pitch morning checklist (Day 3, Wed 11 Nov 2026)

Work through this top to bottom. Tick each box. Times are Dubai time (UTC+4). Pitch slot time: fill in
`__:__`. Everything with a **~T-minus** is relative to the pitch start.

Owner key: **[A]** = person who drives the phone, **[B]** = person who narrates the forensic view and
runs the dashboard, **[C]** = person on the laptop for checks and the backup video.

---

## 1. Night before (Day 2 evening)

- [ ] Backup video of the full run is recorded and saved to two places (laptop + phone). Length about
      2–3 minutes. Re-record if the verdicts changed since.
- [ ] Vercel deployment on `main` is **Ready** and is the one you will demo (Deployments tab).
- [ ] `PUBLIC_BASE_URL` is the production domain (not a preview URL). Sandbox "When a message comes
      in" points at `https://<prod-domain>/api/whatsapp`, POST.
- [ ] Phone hotspot is charged and tested (see section 4).

---

## 2. Morning, T-minus 90 min: connectivity and sandbox

- [ ] **Re-join the Twilio sandbox on every demo phone.** Send `join <code>` to the sandbox number
      (`+1 415 523 8886` at time of writing, verify in UI). Wait for the confirmation reply. Joins
      expire after about 72 hours.
  - [ ] [A] phone
  - [ ] [B] phone
  - [ ] [C] phone (spare)
- [ ] From each phone, send `hello`. Expect the ⚪ reply. If nothing comes back in 30 s, check the
      Twilio Monitor logs (error 11200 means URL wrong or function down).
- [ ] Twilio console: confirm sandbox webhook is still the production URL (Save again if unsure).

---

## 3. T-minus 60 min: warm up and health

- [ ] Hit the health endpoint to warm functions: `curl -s https://<prod-domain>/api/health`.
      Expect `"ok": true`, registry count matching the seed, `"ai": true`.
- [ ] Run the Gemini probe once: `python -m engine.gemini_probe`. If it fails, the bot still works on
      rules, but tell the team and do not promise AI text reasons on stage.
- [ ] Run the E2E script against production (`scripts/e2e/README.md`):
      `python scripts/e2e/whatsapp_e2e.py --base-url https://<prod-domain> --image-base-url <...> --check-db`
      Expect `N/N passed`. If a case fails, fix or cut it now; do not debug on stage.
- [ ] Take the dashboard screenshot as a sanity check: `node scripts/e2e/screenshot.js https://<prod-domain>/?mock=1`.
      Check `scripts/e2e/out/dashboard-1920.png` is not blank and console errors are none.

---

## 4. T-minus 45 min: network and screen

- [ ] Venue Wi-Fi tested with the phones. If the venue Wi-Fi is weak, switch the demo phone to the
      **hotspot** (phone hotspot on, demo phone on hotspot, not on venue Wi-Fi). Test a `hello` over the hotspot.
- [ ] The laptop is on power, not battery. Notifications off. Do not-disturb on every phone.
- [ ] Projector: laptop at **1920×1080**, display mode "Extend" or "Mirror" as the venue requires
      (verify with the AV crew). Browser zoom 100%. Full-screen the dashboard tab.
- [ ] Dashboard open at the real production URL, `https://<prod-domain>/` (not `?mock=1`, which is
      the offline demo mode). Confirm the map, trending panel and counters show data.
- [ ] **Operator unlock**: click the unlock control and enter `DASHBOARD_ADMIN_TOKEN`. Confirm the
      "Push official correction" button is available. Do this on the projector laptop, not on a phone.
- [ ] Phones: WhatsApp open on the demo thread with the sandbox chat, brightness up, screen timeout
      set to "never" while presenting.

---

## 5. T-minus 10 min: reset the demo data

- [ ] Clear the previous rehearsal reports: `python scripts/demo_seed.py --help` (verify the clear
      flag, then run it). Then seed: `python scripts/demo_seed.py`.
- [ ] Dashboard refreshed. Trending panel shows the seeded fake groups; the map shows the seeded
      spread; the live counter starts from the seeded baseline (honest: seeded rows are labelled).
- [ ] Pre-open the forensic view area (the screen that auto-opens when a live report arrives).
- [ ] Final `hello` from [A]'s phone: ⚪ reply, and a new row appears on the dashboard. Leave that
      row in place. If it confuses the story, re-run the clear and seed steps.

---

## 6. Demo beats (exact files to forward)

Forward from the phone, in WhatsApp, to the sandbox number. Use the files already on the phone
(saved from the team Drive); verify the exact filenames with `ls assets/official assets/doctored assets/fakes`.

| # | Beat | What to forward | Expected reply | What the audience should see |
|---|---|---|---|---|
| 1 | Genuine official post | `assets/official/public_holiday_notice.png` (original) | ✅ صحيح — هذا محتوى رسمي موثّق. | Live dot on map; forensic view auto-opens |
| 2 | **Showstopper**: screenshot of the same post | A tight screenshot of the official post, taken on the phone (not the file). Pre-made: `test/screenshot_public_holiday_notice.jpg` | ✅ still | Slow down. WhatsApp strips signatures; the fingerprint still matches |
| 3 | Doctored version | `assets/doctored/` copy with the changed date or number | 🔴 معدّل — نسخة معدّلة من إعلان رسمي. لا تقم بإعادة إرساله. | Heat-map on the changed area |
| 4 | Fake "explosions in Dubai" | `assets/fakes/` explosions image | ⚪ غير مؤكد — لم يصدر عن أي جهة رسمية. كن حذراً. | Appears on map and in the trending list |
| 5 | Scam text | Type or paste: `عاجل حوّل المبلغ فوراً لتجنب غرامة` | 🔴 احتيال محتمل — الرسالة تحمل مؤشرات احتيال. تحقق قبل أي إجراء. | Trending group "Dubai Police fine — pay now via link" |
| 6 | Correction push | Operator clicks **Push official correction** on the top trending fake | Toast with recipients count | Hotspots shrink, emirates turn teal |

Narration line for beat 6: "One forward from a grandmother just helped stop a fake before it reached
the next thousand families."

Honesty lines to say out loud at least once:
- "Unverified means no official source found. It never means proven fake."
- "Seeded rows are labelled. The map shows where reports come from, not how fakes spread on WhatsApp."
- "The emirate on live reports is a demo pick."

If a beat fails live: say the beat, show the backup video clip for that beat, and move on. Do not
retry more than once.

---

## 7. Judge Q&A cheat lines

| Question | Who answers | Line |
|---|---|---|
| "Would older people use this?" | B | No new app or behaviour. They forward to one trusted number. Children can set up guardian mode. Government distributes it through trusted channels, and every forward feeds the early-warning dashboard. |
| "WhatsApp strips your signature." | A | Yes. That's why the engine matches by image fingerprint, not by a signature. You just saw it: beat 2. |
| "What about text and voice?" | A | The AI text check covers text rumours. Voice is honest future work: a risk score, not a verdict. |
| "Does this already exist in the UAE?" | B | Saraab detects deepfake video for experts. There is no Arabic citizen tool for verifying official content. (Confirm with a DESC or CSC mentor before saying it as fact.) |
| "Absence of a signature isn't proof of fake." | A | Agreed. The app says "unverified, treat with caution", never "proven fake". |
| "Can you see how fakes spread on WhatsApp?" | B | No. WhatsApp is encrypted. We map where reports come from. |
| "Will adoption depend on government signing content?" | B | Yes. That is what the 90-day pilot is for: sign official posts, seed the registry, launch the verify number. |

---

## 8. Cut order if behind schedule

From CLAUDE.md, in this order:
1. Gemini LLM (keep rules-based text check).
2. Heat-map detail.
3. Push-correction beat (describe it instead of doing it live).
4. Static map.

Never cut: the fingerprint engine, the bot, the 90-day slide, the deck, the rehearsal.

---

## 9. After the pitch

- [ ] Note any case that failed live and why (for the report).
- [ ] Turn off the demo data if the production URL will stay public: re-run the clear step, or leave as-is
      if judges will look at the live site.
- [ ] Do not commit `.env`, `.env.local`, or the screenshots in `scripts/e2e/out/`.
