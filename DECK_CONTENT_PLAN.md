# HAQEEQ — Deck content plan v2 (7 slides, 180 seconds)

Revised after a mock judge review (TDRA + Cyber Security Council view). Changes vs v1: the demo gets 55 seconds including the
screenshot beat; claims now match what is actually built; the "not a deepfake detector" line is reframed; proof points restored;
every 90-day phase has an owner and a target; dense slides simplified; "proposed/simulated" caveats stated once (slide 4) instead of on every line.

Script length ≈ 400 spoken words at ~150 wpm. **Rehearse against a timer** — the live demo is the part most likely to run long.
Items marked **[TEAM]** are for you to fill in; nothing below invents names, agreements, prices or results.

Timing: S1 0:00–0:20 · S2 0:20–0:40 · S3 0:40–1:35 · S4 1:35–2:00 · S5 2:00–2:25 · S6 2:25–2:50 · S7 2:50–3:00

---------------------------------------------------------------------------------------------------

## Slide 1 — Hook (0:00–0:20)

**On the slide:** "When Seeing Is No Longer Believing". Logo + **HAQEEQ حقيق** + tagline "Make Trust Part of Every Forward".
Visual: a fictional government notice inside a family WhatsApp chat, labelled *Illustrative*.
One stat: **7 in 10 surveyed UAE residents have encountered a scam — on average once every three days** (GASA + Trend Micro, 1,000 UAE residents, 27 Jan 2026).

**Say (≈50 words):** "A voice note from your son asking for money. A government notice with a payment link. In the UAE, seven in ten
surveyed residents have met a scam — on average once every three days. And in the seconds before you forward it, there is no trusted place to
check. HAQEEQ is that place."

**Caution:** this is *exposure* ("encountered a scam"), not "7 in 10 were scammed".

---------------------------------------------------------------------------------------------------

## Slide 2 — Problem and gap (0:20–0:40)

**On the slide:** title "People already verify. The loop isn't closed." Three numbers (GASA + Trend Micro, Jan 2026):
**96%** take at least one verification step · **1 in 3** lost money · **Half** of those who reported saw no action or didn't know the outcome.
Two gap lines: "Residents have no trusted check at the moment of forwarding." / "Public teams find out late."
Small tag: *Challenge 40 — Building Trust in Digital Content*.

**Say (≈50 words):** "Residents aren't careless — 96% take at least one step to verify. Yet one in three lost money, and half of those who
reported saw no action or didn't know the outcome. The gap isn't awareness. It's a trusted check at the moment of forwarding — and a way for the
official source to answer back."

---------------------------------------------------------------------------------------------------

## Slide 3 — Solution and live demo (0:40–1:35, 55 s)

**On the slide:** a 3-step strip — **Forward → Arabic explanation → Verdict** — and the four verdicts with honest one-line meanings:
- ✅ **Genuine** — matches an available official reference
- 🔴 **Altered** — differs from the reference
- ⚪ **Unverified** — not the same as false
- 🔴 **Scam risk** — scam wording detected

Right side: dashboard screenshot labelled *Illustrative — sample data*. Footer line: "Proven model: the US Embassy in Guinea signs official media and gives
citizens a public verifier (since ~2025). HAQEEQ brings that idea to Arabic and WhatsApp." (Guinea is the closest precedent; it is not an Arab-government deployment.)

**Say + do (≈90 words, speak while the phone is driven by teammate):**
1. "A resident forwards the image to HAQEEQ, in the app they already use." → send **official notice** → ✅ *Genuine* appears in Arabic; point at the map dot.
2. "Even a plain screenshot — where WhatsApp has stripped every signature — still matches." → send the **real phone screenshot** → ✅. *Slow down here.*
3. "Change one date and it flags the edit." → send **doctored notice** → 🔴 *Altered* (show heat-map in the forensic view).
4. "Scam wording is analysed too." → send the scam text → 🔴 *Scam risk* with the Gemini explanation.
5. "Public teams see it instantly and can answer back." → click **Push official correction** → map turns teal, toast shows citizens reached.
Close the slide with: "Unverified never means false."

**Before pitching (must do):** fresh Meta token + test `hello`; registry has 8 posts (add 10–20 vetted ones if you can); run `demo_clear.py` then `demo_seed.py`;
rehearse with a **real screenshot** (not a camera photo of a screen); record a backup video.
**Wording note:** the bot's Arabic Genuine reply now reads "✅ صحيح — يتطابق مع مرجع رسمي متاح." (matches an available official reference) — done in code.

---------------------------------------------------------------------------------------------------

## Slide 4 — Technology and data (1:35–2:00, 25 s)

**On the slide:** 5-step flow: *Forward → Fingerprint match → Pixel check → Scam-text analysis (Gemini + rules) → Dashboard & correction*.
Three status badges: **Working in prototype:** image fingerprinting, pixel-level edit detection, scam-text analysis, dashboard, real WhatsApp corrections (to test) ·
**Simulated:** background reports, government signing key, small reference registry (8 posts) · **Planned:** C2PA signing, more registries, voice/video.
**Limits box:** "We prove what is genuine instead of guessing what is fake. Images and text today; voice and video next."
**Open data box (government sources only):**
- Bayanat — government entities directory (57 entities) → trusted-source list
- u.ae "The Seven Emirates" population statements (7 emirates, different reference years) → per-100,000 risk ranking
- Land-registration area names (264 Dubai areas, 2017 snapshot, via Bayanat; Dubai Land Department data) → area labels
- Dubai Pulse datasets were not reachable during the hackathon → planned
- One line: "Open data gives context for where to act, not scam data."
Privacy line: "Minimal data; phone numbers are masked on the dashboard; full numbers are stored server-side only."

**Say (≈60 words):** "Images are fingerprinted against official references; pixel analysis flags edits; scam wording is analysed by Gemini plus rules. These work in
our prototype. Registry and background data are simulated, and C2PA signing is planned. We prove what's genuine rather than guess what's fake. Open
government data tells us where to act. We collect minimal data and mask phone numbers."

**Check before showing:** licence wording for Bayanat data ("CC BY 4.0" was **not verified** — look it up on the dataset page or leave it out); the Dubai Land Department dataset date.

---------------------------------------------------------------------------------------------------

## Slide 5 — Business model (2:00–2:25, 25 s)

**On the slide:** the Business Model Canvas as one clean page (required), but you only *speak* to three things — buyer, funding, biggest risk.
- **Users:** residents (free); **buyer:** the public entity responsible for trust
- **Channel:** official WhatsApp number (WhatsApp Business Platform — confirmation of terms needed)
- **Partners (all proposed):** TDRA, UAE Cyber Security Council, DESC, Dubai Police, a government media partner
- **Costs:** WhatsApp messaging (**[TEAM] check Meta's current price list — do not quote a number you haven't verified**), hosting, AI, human review
- **Funding (pricing to be validated in the pilot):** entity licence · central programme funding · co-funding with oversight
- **Value:** residents get a trusted check at the moment of forwarding; entities get early warning and one-click correction
- **Precedent:** Singapore pairs public scam alerts with reporting and reported scam cases down 24.8% in 2025 (SPF) — shown as context for the approach, **not as a Haqeeq result**
- **Biggest risk:** an issuing entity must maintain reference posts and answer quickly
- **Impact measure:** share of confirmed reports answered with an official decision within 24 hours — **target: [TEAM] (suggested: 80%)**

**Say (≈60 words):** "Residents use it free; the buyer is the public entity responsible for trust. Funding options: an entity licence, central programme
funding, or co-funding with oversight — pricing to be validated in the pilot. Costs are messaging, hosting, AI and human review. Our riskiest
assumption: an issuing entity maintains reference posts and answers fast. Our measure: confirmed reports answered within 24 hours."

---------------------------------------------------------------------------------------------------

## Slide 6 — Team and 90-day pathway (2:25–2:50, 25 s)

**On the slide:** team names + roles **[TEAM]** (cybersecurity student; computing & IT student — fill in). Optional: "Early test: 5 users" **only if you actually run it**.
Roadmap (all *proposed*; each phase has an owner and a target):

| Days | Milestone | Owner | Target |
|---|---|---|---|
| 0–30 | One sponsoring entity; ~20 real official posts loaded; limited-access number live; WhatsApp terms confirmed in writing | Entity comms lead + HAQEEQ tech lead | 20 posts live; 50 invited users **[TEAM adjust]** |
| 31–60 | One or two more entities; referral path to Dubai Police e-crime reporting; legal/privacy review | HAQEEQ lead + legal contact | 2 entities; ≥500 checks **[TEAM adjust]** |
| 61–90 | Evaluation report; decision on scale-up | Cyber Security Council advisor (proposed) | Report incl. the 24-hour response metric |

**Say (≈60 words):** "[Team intro.] Our proposed 90-day plan. Days 0 to 30: one sponsoring entity, about twenty real official posts, a
limited-access number, and written WhatsApp confirmation. Days 31 to 60: one or two more entities, a referral path to Dubai Police e-crime reporting,
and legal review. Days 61 to 90: an evaluation report with our 24-hour response metric. Every partner shown is proposed."

Changed from the original handoff: "3–5 ministries by day 60" and "national rollout + GCC" became "one or two more entities" and "evaluation report" — nothing supports the faster pace.

---------------------------------------------------------------------------------------------------

## Slide 7 — Close (2:50–3:00)

**On the slide:** HAQEEQ · "Make Trust Part of Every Forward" · The ask: "A 90-day pilot with TDRA and a government media partner." · Footer: "Prototype and proposal — no approvals or agreements exist yet."
Optional: mention continuing in LaunchPad.

**Say (≈25 words):** "HAQEEQ: Make Trust Part of Every Forward. We ask TDRA and a government media partner to consider a 90-day pilot. This is a prototype
and a proposal. Thank you."

---------------------------------------------------------------------------------------------------

## Q&A prep (2 minutes) — likely judge questions

- **"What about fakes that aren't in your registry?"** → They return ⚪ *Unverified*, never "fake". We don't claim to detect every deepfake; the value is proving what *is* genuine and routing the rest to the entity for a decision.
- **"False positives / accuracy?"** → Be honest: tested on about 16 demo images (genuine, screenshots, doctored, fakes, unrelated) with expected results; real accuracy would be measured in the pilot. Thresholds are tunable.
- **"Data protection / PDPL — where is data stored?"** → Minimal data; masked numbers on the dashboard; full numbers server-side only. **[TEAM] check which Supabase region you chose before stating it.**
- **"Who maintains the registry and why would an entity do it?"** → That is our riskiest assumption and the point of the pilot: one sponsoring entity, 20 posts, measured 24-hour response.
- **"How is this different from Saraab?"** → Saraab detects fake *video* for experts; HAQEEQ gives citizens an Arabic way to check *official* content and gives entities a way to answer back.
- **"Would older people use it?"** → No new app: they forward to one trusted number (a habit they already have); family members can set it up; every forward also feeds the dashboard.
- **"Can you see how fakes spread on WhatsApp?"** → No — it is end-to-end encrypted. The map shows where reports come from.
- **"Why WhatsApp / what if Meta changes terms?"** → It is where the problem happens; written confirmation of terms is a day 0–30 milestone.

## Open items for the team

1. Team names and roles (slide 6). 2. Targets you can defend (slides 5–6). 3. Meta's current pricing (slide 5) and the Bayanat licence wording (slide 4).
4. Whether to run the 5-person test. 5. Supabase region (for the privacy answer). 6. Fresh Meta token on pitch morning.
