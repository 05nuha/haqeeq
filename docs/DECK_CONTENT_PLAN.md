# HAQEEQ — Deck content plan v3 (7 slides, 180 seconds)

Revised after two mock judge reviews. What changed vs v2:
- **Demo:** one *live* case + a 55-second recorded backup; the screenshot beat is kept but **only after a real-phone test**.
- **Disclaimers:** the honesty points are stated **once, on slide 4**. Other slides carry a single small tag at most.
- **Data:** one visible data output (the per-100,000 campaign ranking) is shown in the demo.
- **Dense slides trimmed:** slides 3–5 now have 3–4 short items each.
- **Two facts flagged for verification** (Guinea precedent, Singapore figures) — see "Verify before presenting".
- The internal score estimate is removed (never show it on a slide).
Items marked **[TEAM]** are yours to fill in; nothing here invents names, agreements, prices or results.

Timing: S1 0:00–0:20 · S2 0:20–0:40 · S3 0:40–1:35 · S4 1:35–2:00 · S5 2:00–2:25 · S6 2:25–2:50 · S7 2:50–3:00. Rehearse to **2:50**.

---------------------------------------------------------------------------------------------------

## Slide 1 — Hook (0:00–0:20)

**On the slide:** "When Seeing Is No Longer Believing" · logo + **HAQEEQ حقيق** · "Make Trust Part of Every Forward".
Visual: a fictional government-style notice in a family chat, tag *Illustrative*.
One stat: **7 in 10 surveyed UAE residents have encountered a scam — on average once every three days.**
Source line: GASA + Trend Micro, 1,000 UAE residents, 27 Jan 2026.

**Say (~45 words):** "A government-looking notice arrives in a family chat. Real, altered, or a scam? In a survey of 1,000 UAE residents, seven in ten had encountered a scam. HAQEEQ gives people a way to check official content before they forward it."
*Say "encountered", never "were scammed".*

## Slide 2 — The gap (0:20–0:40)

**On the slide:** title "People already verify. The loop isn't closed." Three numbers: **96%** take at least one verification step · **1 in 3** lost money · **About half** of those who reported saw no action or didn't know the outcome.
One line: "The missing step: a trusted check at the moment of forwarding — and a way for the official source to answer back."
Strip: Forward → Check → Response. Tag: *Challenge 40 — Building Trust in Digital Content*.

**Say (~45 words):** "People already try to verify. The gap is a trusted check at the moment of forwarding, and a clear response path from the official source. HAQEEQ connects a familiar forward to an explanation — and proposes that response path."

## Slide 3 — Demo (0:40–1:35, 55 s)

**On the slide (keep it light — the demo is the content):** 3-step strip **Forward → Arabic explanation → Verdict**; four verdicts with one-line meanings:
✅ Genuine — matches an available official reference · 🔴 Altered — differs from the reference · ⚪ Unverified — not the same as false · 🔴 Scam risk — scam wording detected.
Small tag: *Prototype · test account · sample content*.

**Demo order (live, teammate drives the phone, dashboard on the big screen):**
1. **Live:** forward the official notice → ✅ in Arabic; point at the new dot on the map. *(~12 s)*
2. **Real phone screenshot** of the same notice → ✅. *Slow down — this is the memorable beat.* **Only if tested on the real phone and current deployment; otherwise skip.** *(~10 s)*
3. **Doctored** notice → 🔴 Altered; show the heat-map in the forensic view. *(~10 s)*
4. **Scam text** → 🔴 Scam risk; show the Arabic Gemini explanation. *(~8 s)*
5. Point at the **campaign ranking** (reports per 100,000 residents): "Open data tells us where to focus the next 'Verify before you share' campaign." *(~7 s)*
6. **Push official correction** → map turns teal. **Only if correction delivery to a test phone has been confirmed;** otherwise say: "The operator workflow is built; delivery is being validated for the pilot." *(~8 s)*
**Backup:** a 55-second screen recording of the same steps. If anything lags, switch to the recording — don't improvise outcomes.

**Say over the demo (~60 words):** "A resident forwards the image in the app they already use. A match supports a genuine result; a mismatch exposes edits; scam wording is flagged with an explanation in Arabic. If there is no reliable match, the result stays unverified — never 'fake'. The dashboard shows public teams what is being reported and where."

## Slide 4 — Technology, data and honesty (1:35–2:00, 25 s)

**On the slide:** one flow line: *Forward → fingerprint match + pixel check / scam-text analysis (Gemini + rules) → verdict + explanation → dashboard → proposed official response*.
Three columns:
- **Working in the prototype:** image fingerprinting, pixel-level edit check, scam-text analysis, dashboard, correction workflow
- **Context data (government sources):** Bayanat entity directory (57 entities) · UAE population statements by emirate (reference years differ) · Dubai area names (2017 snapshot via Bayanat)
- **Simulated / planned:** background activity (simulated), government signing key (mocked), C2PA, voice & video
**Honesty strip (the one place all caveats live):** "We prove what is genuine instead of guessing what is fake · Unverified never means false · The map shows where reports come from, not how messages spread · No agency approval or agreement exists yet."
Small privacy line: "Minimal data; phone numbers masked on the dashboard."

**Say (~55 words):** "Images are checked against official references and compared for pixel edits; scam text is analysed by Gemini plus rules. Government open data gives us source and geographic context — it doesn't train the model. Background data is simulated, the signing key is mocked, and voice and video are next."

*Speaker notes only (don't put on the slide):* Dubai Pulse datasets were not reachable during the hackathon — don't imply a Dubai Pulse integration. Per-100,000 figures are indicative (population years differ). Don't claim PDPL compliance without legal review.

## Slide 5 — Operating model (2:00–2:25, 25 s)

**On the slide:** the Business Model Canvas as one clean page (required), with three highlighted callouts:
- **Buyer:** the public entity responsible for trust (proposed) · **Users:** residents, free
- **Funding options to validate in the pilot:** entity licence · programme funding · co-funding with oversight
- **Biggest risk:** an issuing entity must maintain references and answer fast
Footer metric: **Pilot measure — confirmed reports answered with an official decision within 24 hours. Target: [TEAM] (suggested 80%).**
Costs (on the canvas): messaging **[TEAM: check Meta's current price list before quoting any number]**, hosting, AI, human review.
Partners (all labelled *proposed*): TDRA, UAE Cyber Security Council, DESC, Dubai Police, a government media partner.

**Say (~55 words):** "Residents use it free; the buyer is the public entity that owns the official source. Funding options are an entity licence, programme funding or co-funding — pricing is for the pilot to validate. Our riskiest assumption is that an issuer maintains references and answers fast, so that's what we'll measure."

## Slide 6 — Team and 90-day pilot (2:25–2:50, 25 s)

**On the slide:** team names + roles **[TEAM]**. Table (label *Proposed — depends on a sponsoring entity, written channel terms and privacy/security review*):

| Days | Work | Owner | Proposed measure |
|---|---|---|---|
| 0–30 | One sponsor; agree reference-update + response process; privacy/security review; confirm WhatsApp terms; ~20 vetted posts | HAQEEQ tech lead + entity comms lead | 1 scoped agreement · 20 approved references · 50 invited users **[TEAM adjust]** |
| 31–60 | Limited-access pilot; log unmatched cases; refine escalation to the issuer | HAQEEQ lead + entity contact | 1–2 entities · up to 500 checks · report the unverified rate |
| 61–90 | Review safety, accuracy, response time, cost; decide continue/stop | Team + proposed advisor | Evaluation report incl. the 24-hour metric |

**Say (~55 words):** "[Team intro.] Our proposal is a limited 90-day pilot, not a national rollout. First: one sponsoring entity and about twenty vetted references. Then a controlled test with invited users, measuring unmatched cases. By day 90 we present response-time, safety and cost results and recommend whether to continue."
*Don't say "approved", "partnered" or "ready for deployment".*

## Slide 7 — Ask (2:50–3:00)

**On the slide:** HAQEEQ · "Make Trust Part of Every Forward" · **The ask:** a scoped 90-day pilot with TDRA and one government media partner · footer: *Working prototype and pilot proposal — no approvals or agreements yet.* (Optional: intent to continue in LaunchPad.)

**Say (~25 words):** "HAQEEQ: Make Trust Part of Every Forward. We ask TDRA and one government media partner to consider a scoped 90-day pilot. This is a working prototype and a proposal. Thank you."

---------------------------------------------------------------------------------------------------

## Q&A prep (2 minutes)

- **Not in your registry?** → Returns unverified, never "fake". The pilot measures that rate and routes it to the issuer.
- **Accuracy?** → Tested on a small set of demo cases with expected outcomes — not a representative study. The pilot would report precision, recall and false-positive rates before any accuracy claim.
- **Government data training the AI?** → No. It adds source/geographic context; image matching uses the reference posts; text uses rules + Gemini.
- **Is the signing key real?** → No, mocked. C2PA signing needs an issuing entity and a key-management agreement.
- **See how fakes spread?** → No — end-to-end encrypted; the map shows report origin.
- **Government partner committed?** → No. All partners are proposed; the pilot is the ask.
- **Personal data / PDPL?** → Masked numbers on the dashboard; full numbers server-side only; a documented data-flow, retention, access and hosting-region review comes before any pilot. **[TEAM] confirm your Supabase region before naming it.**
- **Corrections to real people today?** → Answer from the test result. If untested: "The operator workflow is built; end-to-end delivery is being validated."
- **How is it different from Saraab?** → Saraab detects fake video for experts; HAQEEQ gives citizens an Arabic way to check official content and gives issuers a way to answer back.
- **Would older people use it?** → No new app: they forward to one trusted number, a habit they already have.

## Verify before presenting (I could not confirm these)

1. **Guinea precedent:** earlier notes say "C2PA + Digimarc since ~Apr 2025"; the latest plan says "Digimarc watermarking, May 2025". Use whichever wording you can show a source for, and keep it in speaker notes.
2. **Singapore:** latest plan says combined scam-and-cybercrime cases fell 24.8% in 2025 and scam cases alone 27.6%; earlier notes said "scam cases −24.8%". Check the Singapore Police Force 2025 brief and quote one measure, labelled as context, not a HAQEEQ result.
3. **Entity count:** the real database holds **57** entities; the mock dashboard text says 230. Don't record the demo in `?mock=1` mode, or the screen and slide 4 will disagree.
4. Meta's current messaging price and channel terms; the Bayanat licence wording (not verified — leave it out if unsure).
5. Your Supabase region (for the privacy answer).

## Pre-pitch checklist

- [ ] Meta token refreshed; `hello` test returns ⚪.
- [ ] Official image → ✅ with the new wording ("matches an available official reference"); doctored → 🔴; scam text → 🔴 + Arabic explanation.
- [ ] **Real phone screenshot** of the official notice → ✅ (crop tight, power + volume-up; not a photo of a screen).
- [ ] Correction delivered to a test phone (only then show it as a result).
- [ ] Dashboard updates live when a message is sent (otherwise label the clip *Illustrative test view*).
- [ ] `demo_clear.py` then `demo_seed.py` ~10 min before; dashboard open at 1920×1080, Operator unlocked.
- [ ] 55-second backup recording ready; phone hotspot; team names and targets filled; no `[TEAM]` text left on slides.
- [ ] Deck submitted on admin.hackathon.ae by ~10:00am.
