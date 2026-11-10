# HAQEEQ — Deck content v5 (after two mock-judge reviews: Cyber Security Council 66/100, TDRA 61/100)

Changes vs v4 (both judges agreed on most):
1. **Hook** now connects to the demo: the stat is about people posing as *official bodies* (Dubai Police case), not generic scams.
2. **Pacing:** still 7 slides, but retimed and trimmed (max 3 numbers per slide; demo cut to 4 beats; the canvas simplified to one line per block + 3 modelled numbers).
3. **Honest challenge fit:** "Partially answers Q1, Q4, Q6 — provenance (Q3) is simulated; voice/video, payments and calls are next."
4. **Measured evaluation** (from the evaluation run) replaces "it works" claims — see [EVAL] placeholders; fill from `docs/EVAL.md`.
5. **Business case:** one payer for the pilot; no "break-even" headline; a pass/fail gate; compliance line (UAE-region hosting, PDPL review, official Business number under the sponsor's account).
6. **Removed:** "open-source-ready engine", "areas data", "comprehensive", the live correction-push claim unless delivery is confirmed, "guaranteed" language.
Legend: **V** verified on primary page · **M** modelled · **T** team to fill · **[EVAL]** to be filled from docs/EVAL.md.

Timing: S1 0:00–0:20 · S2 0:20–0:40 · S3 0:40–1:25 · S4 1:25–1:50 · S5 1:50–2:15 · S6 2:15–2:45 · S7 2:45–3:00

---------------------------------------------------------------------------------------------------

## Numbers allowed on slides (and nothing else)
- **AED 11.8M+** — Dubai Police, Oct 2026: two suspects arrested over phone scams; callers impersonated employees of official and international organisations (V, The National, 6 Oct 2026)
- **7 in 10** residents encountered a scam, **one every three days** (V, GASA + Trend Micro, 1,000 residents, 27 Jan 2026)
- **1 in 3** residents lost money in the last year (V, same)
- **≈ AED 8,000** average loss; **9%** of victims recovered fully (V, GASA/BioCatch **2024** survey, ~2,000 residents — show the year)
- **96%** take a step to verify; **half** of those who reported saw no action or were unsure of the outcome (V, GASA 2025; speak it, don't put on slide)
- **[EVAL]** controlled-test numbers (n, genuine recall, false-genuine on edits, unrelated false-match) — from docs/EVAL.md
- **≈ AED 2.6–60 per 1,000 checks** modelled running cost (M); pilot direct run cost **< AED 1,000** (M, excludes people, security review, provider fees)
Do not use: break-even headline, Singapore (Q&A only), WhatsApp penetration, any claim that HAQEEQ reduces scams.

---------------------------------------------------------------------------------------------------

## Slide 1 — "Would you forward this?" (0:00–0:20)
**Play-out (≈10 s, live; the fake holiday post on screen):** A: "Holiday next week — it's on the government page!" B: "My aunt already sent it to the whole family… wait. Is it real?" B forwards it to HAQEEQ → **🔴 Altered — a modified copy of an official notice. Don't forward.** (Pre-load or pre-record the reply so latency can't break the beat.)
**On the slide:** the fake post · "Would you forward this?" · **AED 11.8M+ — one Dubai Police case, Oct 2026: callers posing as official bodies**
**Say (≈35 words):** "In October, one Dubai Police case passed eleven point eight million dirhams — callers posing as official bodies. Most of us meet the same trick as a forwarded notice, in a family chat. HAQEEQ is the check before you forward."

## Slide 2 — "It costs money, and the loop stays open" (0:20–0:40)
**On the slide (3 tiles):** **7 in 10** have met a scam — one every 3 days (2025) · **1 in 3** lost money (2025) · **≈ AED 8,000** average loss (2024 survey; 9% fully recovered). Gap line: *Residents try to verify — but have nothing official to check against, and issuers find out late.*
**Say (≈55 words):** "Seven in ten residents have met a scam, one every three days. One in three lost money — about eight thousand dirhams on average, and only nine percent recovered it in full. Ninety-six percent try to verify, yet half of those who report never learn the outcome. There's no official source to check against, and the issuer finds out late."

## Slide 3 — Solution and live demo (0:40–1:25, 45 s, 4 beats)
**On the slide:** Forward → Arabic explanation → Verdict · four verdicts (✅ Genuine — matches an official reference · 🔴 Altered · ⚪ Unverified — not the same as false · 🔴 Scam risk) · strip: **"Partially answers Challenge 40 questions 1, 4 and 6 · provenance (Q3) simulated · voice/video next"**
**Demo (each ≈11 s, rehearsed 10× on the real phone; backup video ready):** ① official notice → ✅ ② **real phone screenshot** of it → ✅ ③ doctored notice (large, clear change) → 🔴 + heat-map ④ scam text → 🔴 + Arabic explanation from Gemini. Dashboard stays on screen quietly (feed + map). Push-correction only if delivery is confirmed; otherwise skip.
**Say (≈75 words, over the demo):** "A resident forwards what they received. A match with an official post means genuine — even a tight screenshot with every signature gone. Edit the notice and HAQEEQ flags it and shows where. Scam wording is explained in Arabic by Gemini. If there's no reliable match it says unverified — never fake — because we prove what is genuine; we don't guess what is false."

## Slide 4 — What is proven, what is not (1:25–1:50, 25 s)
**On the slide:** a small result box **"Controlled test: [EVAL] images — genuine recall __% · edits caught __% · edits passed as genuine __% · unrelated falsely matched __%"** (label: *controlled test, 8 posts, simulated phone screenshots*) · three status chips: **Working** (fingerprint + screenshot match, pixel edit check, Gemini + rules scam text, dashboard) · **Data** (Bayanat entity list 57 · u.ae population statements → illustrative per-100,000 ranking) · **Simulated / planned** (demo registry of 8 samples, mocked signing, C2PA, voice and video).
**Say (≈55 words):** "We tested the engine on [N] controlled images: [x]% of genuine copies matched, [y]% of edits were caught, and [z]% slipped through — which is why 'unverified' is the safe default. Open data adds context only: the entity directory and a per-capita ranking, illustrative on demo data. The registry, signing key and background reports are simulated; voice and video are next."

## Slide 5 — The business case: Business Model Canvas (1:50–2:15, 25 s)
**On the slide:** standard 9-block canvas, **one line per block**, plus a 3-number bar (each labelled *modelled*): **≈ AED 2.6–60 per 1,000 checks · pilot direct run cost < AED 1,000 (excl. people, review, provider fees) · fully loaded pilot budget AED [T]**.
Blocks: **Segments:** residents (free) · issuing entities (buyer, proposed) · **Value:** trusted Arabic check at the moment of forwarding; early warning + correction channel · **Channels:** official WhatsApp number; dashboard · **Relationships:** sponsor entity maintains posts, answers within an agreed time · **Partners (proposed):** TDRA, Cyber Security Council, DESC, Dubai Police · **Activities:** registry, verification, response workflow · **Resources:** engine, open data, privacy/security review · **Costs:** AI + messaging per 1,000 checks; people; audit · **Revenue (pilot):** programme funding from a sponsoring entity; licence per entity after the pilot.
**Say (≈55 words):** "Residents use it free. For the pilot, a sponsoring entity funds it through its programme budget; after the pilot, a per-entity licence. Modelled running cost is a few dirhams to sixty per thousand checks; the pilot's direct run cost is under a thousand dirhams — people and the security review come on top, and we'll price them with you."

## Slide 6 — The 90-day pilot, the gate, and the risks (2:15–2:45, 30 s)
**On the slide:** timeline 0–30 · 31–60 · 61–90 with owners · **Pass/fail gate (proposed):** proceed to phase 2 only if **24-hour response ≥ [T]%** · **edits passed as genuine ≤ [T]%** · **cost per 1,000 checks measured** · Risks: issuer keeps posts current · **UAE-region hosting + privacy-law review before any real users; official Business number under the sponsor's account** · corrections after 24 h need approved WhatsApp templates (≈ AED 58 per 1,000, modelled).
Phases: **0–30** sponsor + ~20 real posts, security/privacy review, channel terms, limited-access number (targets [T]) · **31–60** controlled pilot, log unmatched cases, 1–2 entities · **61–90** evaluation report, continue/stop decision.
**Say (≈70 words):** "A limited ninety-day pilot, not a rollout. Days zero to thirty: one sponsor, about twenty real posts, a privacy and security review, and a limited-access number. Thirty to sixty: a controlled test with invited users. Sixty to ninety: an evaluation. We proceed only if response time and false-genuine meet an agreed gate. Hosting moves to a UAE region and privacy review comes first — before any real user."

## Slide 7 — Team and the ask (2:45–3:00, 15 s)
**On the slide:** **[T] team names + roles** · "Sponsor a 90-day pilot — *you bring* one issuing entity, ~20 official posts, a named contact; *we bring* a working prototype and a measured evaluation." · footer: *Working prototype and pilot proposal — no approvals or agreements yet.* · HAQEEQ — Make Trust Part of Every Forward
**Say (≈35 words):** "[Team intro.] HAQEEQ: Make Trust Part of Every Forward. We ask you to sponsor a ninety-day pilot — you bring one entity and twenty posts; we bring the prototype and a measured result. Thank you."

---------------------------------------------------------------------------------------------------

## Q&A shield (answers the judges' hardest questions)
1. **Do you ever say 'genuine' on a fake?** Use the measured number; say edits near the threshold can slip through; the pilot's #1 safety metric is false-genuine; the reply says "matches an official reference", not "safe".
2. **Isn't it just a lookup table?** By design: it proves what is genuine and says unverified for the rest; value comes from the registry growing and the response loop. We don't claim deepfake detection.
3. **Who keeps the registry current / stops a fake being registered?** Our riskiest assumption and first metric; pilot: issuer-authenticated uploads, each post with owner/hash/timestamp/withdrawn status; today's signing is mocked.
4. **Voice, video, payments, calls?** Nothing today; we address Q1, Q4, Q6 for official content; voice as a risk score with a callback-verification flow is a later phase.
5. **Data and hosting?** Test data is synthetic/consenting testers; phone numbers are masked on the dashboard and stored server-side only; the pilot moves to a UAE region after a privacy-law review; rate limits and a report threshold before trends trigger action are planned.
6. **Why WhatsApp / Meta dependency?** It's where forwarding happens; the engine is channel-agnostic (already ran on Twilio and Meta); the pilot uses an official Business number under the sponsor's account.
7. **Overlap with Saraab / eCrime?** Saraab detects fake video for experts; we check still images/text against official posts and propose feeding existing reporting channels. We haven't confirmed that no equivalent exists — mentor question.
8. **Singapore?** (only if asked) Scams + cybercrime cases fell 24.8% in 2025 (SPF, Feb 2026) with coordinated public interventions — context, not a HAQEEQ result.
