# HAQEEQ — Deck content v4 ("the investment case") — 7 slides, 180 s

Built from: the Challenge 40 profile, the HackArena playbook (Pioneers rubric), the Day 1 deck, and a numbers check against primary sources (10 Nov 2026).
Audience framing: a National Cyber Security Council / TDRA stakeholder who must decide **"would I sponsor this pilot?"**
Every number below has a status: **V** = verified on the primary page · **M** = modelled by us (assumptions shown) · **T** = team to fill.

---------------------------------------------------------------------------------------------------

## The numbers sheet (only these may appear)

| # | Number (exact wording) | Status | Source |
|---|---|---|---|
| N1 | 7 in 10 UAE residents encountered a scam; on average one every 3 days (~111 a year) | V | GASA + Trend Micro, *State of Scams in the UAE 2025*, 1,000 residents, 27 Jan 2026 |
| N2 | 1 in 3 residents reported losing money to scams in the last year | V | same |
| N3 | 96% took at least one step to verify an offer | V | same (gasa.org blog) |
| N4 | 79% of those who experienced a scam reported at least one incident; half of those who reported said no action was taken or they were unsure of the outcome | V | same |
| N5 | Average loss ≈ US$2,194 (≈ AED 8,000); only 9% of those who lost money fully recovered it | V | GASA/BioCatch, ~2,000 UAE residents, 28 Nov 2024 (older survey) |
| N6 | Dubai Police, Oct 2026: two suspects arrested over phone scams worth over AED 11.8 million; callers impersonated employees of official and international organisations | V | The National, 6 Oct 2026 |
| N7 | UAE population ≈ 11.3 million (end of 2024) | V | FCSC via Gulf News |
| N8 | Singapore 2025: scams + cybercrime cases down 24.8% to 41,974; scam losses down ~18% to S$913M; at least S$348M in potential losses avoided by police interventions | V | Singapore Police Force, 25 Feb 2026 — context only; no single tool credited |
| N9 | US Embassy in Conakry: invisible watermark + Content Credentials on official images, public verification tool | V (month unverified — say "2025") | Content Authenticity Initiative / Digimarc |
| N10 | Running cost ≈ US$0.70–16 per 1,000 checks (≈ AED 2.6–60): AI ≈ $0.70; messaging $0 for replies inside WhatsApp's 24-hour window, up to $15.70 if every reply were billed as a utility message | **M** | token estimates + public price lists; **confirm with Meta's rate card and Google's price table** |
| N11 | A correction pushed outside the 24-hour window needs an approved WhatsApp template: ≈ $0.016 each → ~AED 58 per 1,000 recipients | **M** | third-party rate summaries; confirm with Meta |
| N12 | Break-even arithmetic: a AED 1M/yr programme pays back if it helps avoid ≈ 124 losses of AED 8,058 a year (AED 0.5M → 62; AED 2M → 248) | **M** (arithmetic on N5, not a forecast) | |
| N13 | Direct run cost of the 90-day pilot (5,000 checks + hosting) < AED 1,000, excluding people, security review and WhatsApp provider fees | **M** | |
| N14 | National scale, 5% of residents × 12 checks a year ≈ 6.8M checks → AED 17k–408k a year in AI + messaging (modelled) | **M** | |

**Do NOT use:** "AED 11.8 billion", "Dh1M fine / 1–2 years jail" (unconfirmed), WhatsApp penetration percentages, "Singapore scam cases −24.8%" (that is combined), any claim that HAQEEQ reduces scams or losses.

---------------------------------------------------------------------------------------------------

## Slide 1 — "Would you forward this?" (0:00–0:25) — the instant hook

**Play-out (12 s, live, before any slide text; the fake post is on screen):**
- Teammate A (phone up): "Holiday next week — from the government page!"
- Teammate B: "Wait — are you sure?" … forwards it to HAQEEQ. On the big screen: **🔴 Altered — a modified copy of an official notice. Don't forward.**
**On the slide:** the fake post · title "Would you forward this?" · **7 in 10 residents have met a scam — one every three days (N1)**
**Say (≈35 words):** "In the UAE, seven in ten residents have met a scam — on average one every three days. And before you forward, there's nowhere trusted to check. HAQEEQ is that check."

## Slide 2 — "It costs real money — and nobody closes the loop" (0:25–0:50)

**On the slide:** four number tiles — **1 in 3** lost money (N2) · **≈ AED 8,000** average loss (N5) · **9%** fully recovered (N5) · **AED 11.8M+** one Dubai Police case, Oct 2026, callers posing as official bodies (N6). Below, the gap in one line: **96% try to verify (N3) — but half of those who reported saw no action or didn't know the outcome (N4).** Tag: Challenge 40 — Building Trust in Digital Content.
**Say (≈60 words):** "One in three residents lost money last year — about eight thousand dirhams on average, and only nine percent recovered it in full. In October, one Dubai Police case alone passed eleven million, with callers posing as official bodies. People do try to verify — ninety-six percent — but they have nothing official to check against, and half of those who report never learn the outcome."

## Slide 3 — Solution + live demo (0:50–1:40, 50 s)

**On the slide:** Forward → Arabic explanation → Verdict; four verdicts (✅ Genuine · 🔴 Altered · ⚪ Unverified — not the same as false · 🔴 Scam risk); a small strip "Answers Challenge 40 questions 1, 3, 4 and 6" (check at the moment of receipt · official content proves itself · Arabic plain-language results · reporting + response).
**Demo (live; backup video):** official notice → ✅ · real phone screenshot of it → ✅ · the doctored notice → 🔴 with heat-map · scam text → 🔴 + Gemini's Arabic explanation · dashboard: reports per 100,000 residents ranking · Push official correction (only if delivery is confirmed).
**Say (≈90 words, over the demo):** "A resident forwards what they received, in the app they already use. A match with an official post means genuine — even a screenshot, where every signature is gone. Change one date and HAQEEQ flags it and shows where. Scam wording is explained in Arabic. If there's no reliable match, it says unverified — never 'fake'. The issuing entity sees the reports instantly and can answer back, and open data shows where to focus the next awareness campaign."

## Slide 4 — Why it works: tech, AI, data, honesty (1:40–2:00, 20 s)

**On the slide:** flow: fingerprint match → pixel check → verdict → dashboard → response. Three columns: **Working in the prototype** (image fingerprinting + screenshot matching, pixel-level edit check, Gemini + rules scam-text analysis, dashboard + correction workflow) · **Open data used** (UAE population statements → reports per 100,000 residents; Bayanat entity directory (57 entities) → impersonation context; data portals and years cited) · **Simulated / planned** (demo registry of 8 sample posts, mocked signing key, C2PA, voice and video). Honesty strip: *We prove what is genuine instead of guessing what is fake · Unverified never means false · The map shows where reports come from, not how messages spread.*
**Difference line:** "Saraab detects fake video for experts. HAQEEQ gives residents an Arabic check against official posts." Precedent (N9): the US Embassy in Conakry publishes verifiable official images.
**Say (≈50 words):** "Official posts are fingerprinted, so a match survives screenshots and recompression; pixel analysis catches edits; Gemini explains scam wording in Arabic. Open population data turns raw reports into a per-capita campaign ranking. The registry is a demo, the signing key is mocked, and voice and video come next."

## Slide 5 — The business case (Business Model Canvas) (2:00–2:25, 25 s)

**On the slide:** the one-page standard canvas **with numbers inside the blocks**, and a three-number bar underneath:
**≈ AED 2.6–60 per 1,000 checks (N10) · ≈ 124 avoided losses/yr = break-even at AED 1M (N12) · pilot direct run cost < AED 1,000 (N13)** — all labelled *modelled*.
Canvas blocks: **Segments:** residents (free); issuing public entities (buyer — proposed) · **Value:** a trusted Arabic check at the moment of forwarding; entities get early warning and a one-click correction · **Channels:** official WhatsApp number; dashboard · **Relationships:** entity maintains posts and answers within an agreed time · **Key partners (proposed):** TDRA, UAE Cyber Security Council, DESC, Dubai Police, a government media partner · **Key activities:** reference registry, verification, response workflow · **Key resources:** engine, open data, privacy and security review · **Costs:** AI + messaging per N10; corrections outside 24 h ≈ AED 58 per 1,000 (N11); people, audit, WhatsApp provider fees **[T]** · **Revenue options (to validate):** entity licence · programme funding · co-funding with oversight; later banks/telecoms verifying their own messages.
**Say (≈60 words):** "Residents use it free; the buyer is the entity that owns the official source. Our modelled running cost is a few dirhams to sixty per thousand checks. At today's average loss of eight thousand dirhams, a one-million-dirham programme breaks even if it helps avoid about a hundred and twenty-four losses a year. The pilot's direct running cost is under a thousand dirhams — people and security review excluded."

## Slide 6 — The 90-day pilot: milestones, KPIs, risks (2:25–2:50, 25 s)

**On the slide:** a timeline chart (0–30 · 31–60 · 61–90) with owners and targets, and the KPI strip: **24-hour response rate** (target **[T]**, suggested 80%) · **unverified rate** · **median time from first report → official decision** · **cost per 1,000 checks (measured)**. Risks: issuer must keep posts current; corrections outside 24 h need approved WhatsApp templates; privacy and hosting-region review before any real users.
Table: Days 0–30 — sponsor + ~20 real official posts, security/privacy review, WhatsApp terms, limited-access number (target: 20 posts, 50 invited users **[T]**) · 31–60 — controlled pilot, log unmatched cases, escalate to issuer (1–2 entities, up to 500 checks) · 61–90 — evaluation report (response time, safety, cost) and a continue/stop recommendation.
Team: **[T names + roles]**.
**Say (≈60 words):** "[Team.] A limited ninety-day pilot, not a national rollout. First: one sponsoring entity and about twenty real official posts. Then a controlled test with invited users. By day ninety we report response time, unmatched cases and measured cost, and recommend whether to continue. Our biggest risk is an issuer keeping posts current — so that's the first thing we measure."

## Slide 7 — The ask (2:50–3:00, 10 s)

**On the slide:** HAQEEQ — Make Trust Part of Every Forward. **The ask:** sponsor a 90-day pilot — *you bring:* one issuing entity, ~20 official posts, a named contact · *we bring:* a working prototype, a measured evaluation, and the open-source-ready engine **[T: only if true]**. Footer: *Working prototype and pilot proposal — no approvals or agreements yet.*
**Say (≈25 words):** "HAQEEQ: Make Trust Part of Every Forward. Sponsor a ninety-day pilot with us — you bring one entity and twenty posts; we bring the prototype and a measured result. Thank you."

---------------------------------------------------------------------------------------------------

## Q&A shield (2 minutes)
- *Where's the proof it works?* — Demo tested on a small set of cases; accuracy is not a study; the pilot measures precision/false positives.
- *Voice and video deepfakes?* — Not covered; we answer questions 1, 3, 4, 6; voice/video is next; unmatched content stays "unverified".
- *Why would an entity maintain the registry?* — It's our riskiest assumption and the first pilot measure; they gain early warning and a correction channel.
- *Is the open data used meaningfully?* — Population statements drive the per-100,000 ranking; Bayanat entity list feeds impersonation context; areas data not used yet.
- *Corrections to people later?* — Outside WhatsApp's 24-hour window they need approved templates (N11).
- *PDPL/privacy?* — Masked numbers on the dashboard; full numbers server-side only; data-flow, retention and hosting-region review before the pilot.
