# Prompt for Replit Agent — build the HAQEEQ pitch deck

Paste everything inside the block below into Replit Agent (a new Repl, "Slides"/web app).
Fill in the three [TEAM] items first if you know them (team names, roles, targets).

```
Build a 7-slide pitch presentation as a polished, presenter-friendly web app (16:9, one slide per screen, keyboard arrows to navigate, press "N" to toggle speaker notes, press "F" for fullscreen, a discreet 3:00 countdown timer toggled with "T"). Also provide a "Download as PDF" button (print-optimised CSS) and, if feasible, a PPTX export.

PROJECT: HAQEEQ (حقيق) — an Arabic-first WhatsApp service that helps UAE residents check whether an official-looking image or message is genuine, altered, unverified or a scam, plus a "National Trust Control Center" dashboard for public entities. Audience: UAE Hackathon 2026 judges (TDRA, UAE Cyber Security Council, DESC), mostly non-technical. The pitch is exactly 3 minutes. Tone: calm, credible, government-grade. Never hype.

DESIGN SYSTEM (strict):
- Flat, restrained, institutional. NO neon, NO glows, NO glassmorphism, NO gradient text, NO stock photos, NO emoji-heavy decoration, NO 3D.
- Colours: page navy #0A1628, panel #0F1F36, hairline borders #22364F, text #E8EEF5, muted text #93A4B8, verified emerald #1FA37A, danger red #E5484D, warning amber #E0A030, neutral grey #8795A8, gold accent #C9A24B (thin rules and the logo only). One border radius (10px).
- Typography: IBM Plex Sans Arabic for everything (Arabic + Latin in one family), weights 500 and 700 only. Slide titles 44px, body 26-28px, source/captions never below 16px (this is read on a projector).
- Layout: generous whitespace, left-aligned titles with a thin gold rule under the title, max 4 short items per slide, one idea per slide. Arabic text must render right-to-left with correct shaping.
- Logo placeholder: a rounded shield containing the Arabic letter ح with a small check mark, in emerald/gold on navy (I will replace it with my own logo file at /public/logo.svg — load it if present).
- Motion: subtle fade/slide between slides only (200ms). No looping animations.
- Any text in square brackets like [TEAM: names and roles] must be rendered as a visible amber highlighted placeholder so it is impossible to miss.
- Put the spoken script for each slide in speaker notes (toggle with N). Include the time budget per slide in the notes.

HONESTY RULES: use ONLY the facts written below. Do not invent statistics, names, logos of real agencies, partners or approvals. Show agency names only as text, always labelled "proposed". The word "Illustrative" must appear on any mock visual.

SLIDES

1) HOOK (0:00-0:20)
Title: "When Seeing Is No Longer Believing". Large logo + "HAQEEQ حقيق" + tagline "Make Trust Part of Every Forward".
Visual: a simple fictional government-style notice card shown inside a family WhatsApp chat bubble (drawn with CSS, not a screenshot), tag "Illustrative".
One stat, large: "7 in 10 surveyed UAE residents have encountered a scam — on average once every three days". Small source: "GASA + Trend Micro, 1,000 UAE residents, 27 Jan 2026".
Notes: "A government-looking notice arrives in a family chat. Real, altered, or a scam? In a survey of 1,000 UAE residents, seven in ten had encountered a scam. HAQEEQ gives people a way to check official content before they forward it." (Say 'encountered', never 'were scammed'.)

2) THE GAP (0:20-0:40)
Title: "People already verify. The loop isn't closed."
Three big numbers in a row: "96%" take at least one verification step · "1 in 3" lost money · "About half" of those who reported saw no action or didn't know the outcome. Source line as slide 1.
Below, a 3-stage strip: Forward → Check → Response, with one line: "The missing step: a trusted check at the moment of forwarding — and a way for the official source to answer back."
Small tag: "Challenge 40 — Building Trust in Digital Content".
Notes: "People already try to verify. The gap is a trusted check at the moment of forwarding, and a clear response path from the official source. HAQEEQ connects a familiar forward to an explanation — and proposes that response path."

3) DEMO (0:40-1:35) — keep the slide light because a live demo / video runs here.
Title: "Forward. Understand. Respond."
Left: 3-step strip "Forward → Arabic explanation → Verdict". Right: four verdict cards, each with a coloured left border and one line:
 ✓ Genuine (emerald) — matches an available official reference
 ✕ Altered (red) — differs from the reference
 ○ Unverified (grey) — not the same as false
 ! Scam risk (amber) — scam wording detected
Bottom-left small tag: "Prototype · test account · sample content".
Add a large centred "PLAY DEMO" button that opens a fullscreen video overlay playing /public/demo.mp4 (I will upload the file; if missing show a clear "demo.mp4 not found" message). Pressing Esc closes it.
Notes (demo order, ~55s): 1) live: forward the official notice -> Genuine in Arabic. 2) real phone screenshot of the same notice -> Genuine (only if tested). 3) doctored notice -> Altered, show heat-map. 4) scam text -> Scam risk with Arabic AI explanation. 5) point at the campaign ranking (reports per 100,000 residents). 6) Push official correction (only if delivery is confirmed). Backup: play the recording. Script: "A resident forwards the image in the app they already use. A match supports a genuine result; a mismatch exposes edits; scam wording is flagged with an explanation in Arabic. If there is no reliable match, the result stays unverified — never 'fake'. The dashboard shows public teams what is being reported and where."

4) TECHNOLOGY, DATA AND HONESTY (1:35-2:00)
Title: "What is built — and what is not"
Top: one flow line of 5 small boxes: Forward → Fingerprint match + pixel check / scam-text analysis (Gemini + rules) → Verdict + explanation → Dashboard → Proposed official response.
Three columns with status badges:
 WORKING IN THE PROTOTYPE (emerald badge): image fingerprinting · pixel-level edit check · scam-text analysis · dashboard · correction workflow
 CONTEXT DATA — GOVERNMENT SOURCES (gold badge): Bayanat entity directory (57 entities) · UAE population statements by emirate (reference years differ) · Dubai area names (2017 snapshot via Bayanat)
 SIMULATED / PLANNED (grey badge): background activity (simulated) · government signing key (mocked) · C2PA signing · voice & video
Bottom "honesty strip" (full width, subtle border): "We prove what is genuine instead of guessing what is fake · Unverified never means false · The map shows where reports come from, not how messages spread · No agency approval or agreement exists yet".
Tiny privacy line: "Minimal data; phone numbers masked on the dashboard."
Notes: "Images are checked against official references and compared for pixel edits; scam text is analysed by Gemini plus rules. Government open data gives us source and geographic context — it doesn't train the model. Background data is simulated, the signing key is mocked, and voice and video are next." Speaker-only: Dubai Pulse datasets were not reachable during the hackathon — don't imply an integration; don't claim PDPL compliance.

5) OPERATING MODEL (2:00-2:25)
Title: "A pilot a public entity can actually run"
Render a clean one-page Business Model Canvas (9 blocks, 5-4 grid, small text but >=16px): 
 Customer segments: residents (free); public entity responsible for trust (proposed buyer). 
 Value: a trusted Arabic check at the moment of forwarding; issuers get structured reports and a response workflow. 
 Channels: official WhatsApp number; dashboard for public teams. 
 Key partners (all "proposed"): TDRA, UAE Cyber Security Council, DESC, Dubai Police, a government media partner. 
 Key activities/resources: reference registry, verification engine, open-data context, privacy and security review. 
 Revenue options to validate in the pilot: entity licence · programme funding · co-funding with oversight. 
 Costs: messaging [TEAM: verify price before quoting], hosting, AI usage, human review. 
 Relationships: issuer maintains references and answers within an agreed time. 
Highlight three callouts in gold outline: Buyer · Funding options · Biggest risk ("an issuing entity must maintain references and answer fast").
Footer metric bar: "Pilot measure: confirmed reports answered with an official decision within 24 hours — target [TEAM: e.g. 80%]".
Notes: "Residents use it free; the buyer is the public entity that owns the official source. Funding options are an entity licence, programme funding or co-funding — pricing is for the pilot to validate. Our riskiest assumption is that an issuer maintains references and answers fast, so that's what we'll measure."

6) TEAM AND 90-DAY PILOT (2:25-2:50)
Title: "A proposed 90-day pilot". Top row: team members [TEAM: names and roles — cybersecurity student; computing & IT student]. 
Table with 3 rows (columns: Days · Work · Owner · Proposed measure):
 0-30 | One sponsoring entity; agree reference-update and response process; privacy/security review; confirm WhatsApp terms; ~20 vetted posts | HAQEEQ tech lead + entity communications lead | 1 scoped agreement · 20 approved references · 50 invited users [TEAM adjust]
 31-60 | Limited-access pilot; log unmatched cases; refine escalation to the issuer | HAQEEQ lead + entity contact | 1-2 entities · up to 500 checks · report the unverified rate
 61-90 | Review safety, accuracy, response time, cost; decide continue or stop | Team + proposed advisor | Evaluation report incl. the 24-hour metric
Banner above the table: "Proposed — depends on a sponsoring entity, written channel terms and a privacy/security review".
Notes: "[Team intro.] Our proposal is a limited 90-day pilot, not a national rollout. First: one sponsoring entity and about twenty vetted references. Then a controlled test with invited users, measuring unmatched cases. By day 90 we present response-time, safety and cost results and recommend whether to continue." Do not say 'approved', 'partnered' or 'ready for deployment'.

7) ASK (2:50-3:00)
Large centred logo + "HAQEEQ" + "Make Trust Part of Every Forward". The ask: "A scoped 90-day pilot with TDRA and one government media partner." Footer: "Working prototype and pilot proposal — no approvals or agreements yet." Optional small line: "Continuing in LaunchPad".
Notes: "HAQEEQ: Make Trust Part of Every Forward. We ask TDRA and one government media partner to consider a scoped 90-day pilot. This is a working prototype and a proposal. Thank you."

ACCEPTANCE: every slide fits 1920x1080 with no scrolling; Arabic renders correctly; all [TEAM] placeholders are visibly highlighted; no invented facts; speaker notes present on every slide; PDF export works; total spoken script about 400 words (180 seconds).
```

## After Replit builds it
1. Upload `public/logo.svg` (your Gemini logo) and `public/demo.mp4` (the 55-second screen recording).
2. Fill the amber `[TEAM]` placeholders (names, roles, targets, Meta price).
3. Check slide 4's numbers against your database (57 entities) and confirm the two flagged facts in `DECK_CONTENT_PLAN.md` ("Verify before presenting").
4. Rehearse to 2:50 with the timer (press T). Export a PDF as the submission backup.
