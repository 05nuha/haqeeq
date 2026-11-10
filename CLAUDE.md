# HAQEEQ — FULL PROJECT CONTEXT (handoff for a new Claude session)

Read this whole file before doing anything. It is the complete context of a UAE Hackathon 2026
project built over one long session: the event rules, the scoring rubric, every decision and why,
the research evidence, the architecture, the current build status, and what is left to do.
All code lives in this repo (file list in section 9). A copy of every file is also in the
"Code appendix" at the end of the Google Doc version of this file.

Current local time context: the team is in DUBAI. Day 1 = Mon 9 Nov 2026, Day 2 = Tue 10 Nov,
Day 3 (pitch) = Wed 11 Nov 2026. Timezone Asia/Dubai (UTC+4). This file was written late on Day 1.

---------------------------------------------------------------------------------------------------

## ⚠ DIRECTION CHANGE (latest decision, overrides anything below about Replit)

The team is **dropping Replit** (it kept misbehaving). New target stack: **Vercel** (Next.js dashboard +
Python serverless functions for the WhatsApp webhook and engine) + **Supabase** (Postgres, Storage, Realtime)
+ Twilio WhatsApp sandbox + Gemini. Built by Claude Code using parallel agents. Full instructions:
**REBUILD_PROMPT.md** in this folder. The existing Flask code is the reference implementation and the
fallback (move to `legacy-flask/`). Cutoff: if the Vercel version can't pass the full real-phone gate test by
**Tue 10 Nov 1pm Dubai time**, revert to the Flask version (host it on Railway/Render) and focus on the deck.

## ✅ CURRENT STATUS (Tue 10 Nov, ~12:45 Dubai) — Vercel rebuild is LIVE; this overrides sections 9, 12, 14

- Live: dashboard https://haqeeq.vercel.app (also /dashboard), API under /api/*. Repo github.com/05nuha/haqeeq
  (push to main auto-deploys on Vercel). Supabase project voqslacetqbrkoueaptz (Postgres + Storage bucket `media` + Realtime).
- Messaging: **Meta WhatsApp Cloud API** (test number +1 555 167 8203, webhook https://haqeeq.vercel.app/api/meta).
  Real-phone gate test PASSED via Meta (text, scam text, official image, screenshot, doctored, fake, unrelated).
  Twilio (/api/whatsapp) still exists but the trial sender (+1 737 221 2163) requires Content templates, which the trial
  can't create -> replies never deliver. Don't use Twilio for the demo.
- Meta gotchas learned: (1) the WhatsApp Business Account had to be subscribed to the app — done via
  GET /api/meta?diag=1&waba=1695628978747111&subscribe=1 (diag also shows token validity/expiry);
  (2) the temporary token expires after 24 h -> create a permanent System User token (Business settings -> System users,
  permissions whatsapp_business_messaging + whatsapp_business_management, expiry Never) and put it in Vercel
  META_WHATSAPP_TOKEN; (3) only phone numbers added under "To" on the API Testing page can use the test number.
- Debug endpoints: GET /api/health (all env flags + registry count), GET /api/meta (last webhook), GET /api/whatsapp.
- Engine: numpy pHash + pixel tamper (engine/), plus crop search so phone screenshots with status/browser bars still
  match (strict threshold 6). Photos of a laptop screen do NOT match (by design: too noisy) — in the demo use a real
  screenshot. Gemini works (default model gemini-3.5-flash-lite, override GEMINI_MODEL); rules OR AI => scam_risk.
- Data loaded: 8 official posts + 2 known fakes (scripts/seed_registry.py), open data (scripts/load_open_data.py:
  57 Bayanat entities, 7 emirate populations from u.ae, 264 Dubai areas, 4 catalogue rows — see DATA_SOURCES.md for
  caveats: Dubai Pulse + FCSC portal unreachable; population years differ per emirate; no age data), 55 seeded reports.
  Before the pitch: python scripts/demo_clear.py && python scripts/demo_seed.py (needs SUPABASE_URL + service key).
- Demo images to forward: https://voqslacetqbrkoueaptz.supabase.co/storage/v1/object/public/media/demo/1-official.png
  (also 2-screenshot.jpg, 3-doctored.png, 4-fake-explosions.png, 5-unrelated.png, 6-official-mohre.png, 7-doctored-visa.png).
- Docs: CONTRACT.md (architecture/contract), DEPLOY.md, PREPITCH_CHECKLIST.md (written for Twilio — use Meta instead),
  DATA_SOURCES.md (Data slide text), api/README.md.
- TODO: permanent Meta token; test "Push official correction" delivers on WhatsApp via Meta; record backup video;
  deck (90-day plan + BMC); create team on admin.hackathon.ae; rehearse. Dashboard map uses Esri tiles if CARTO fails.

## 0. TL;DR

- Event: UAE Hackathon 2026, Track 2 (Youth), **Pioneers** group (university students), **Dubai** location.
- Challenge: **Challenge 40 — "Building Trust in Digital Content"** (Theme 4, Digital Trust & Cyber-Secure Nation).
- Product: **Haqeeq (حقيق, "real/true")**. A citizen forwards an "official" image or message to a WhatsApp
  number and gets an Arabic verdict in seconds (✅ genuine / 🔴 altered / ⚪ unverified / 🔴 scam risk).
  Every forward also lands on a **government dashboard** ("National Trust Control Center") with a live
  UAE map of where fakes are being reported, a forensic view, trending fakes, and a "Push official
  correction" button.
- Core tech: Python **Flask** on **Replit**, **Twilio WhatsApp sandbox**, **SQLite**, verification engine =
  **perceptual hash (pHash) matching against a registry of genuine official posts + pixel-level tamper
  check**, rule-based Arabic/English scam-text check with optional **Gemini** LLM upgrade. Dashboard uses
  **Leaflet** (CARTO dark tiles) + **Chart.js** from CDNs.
- Team of 2: **Person A** = the user (owns the Replit account; builds engine + bot + server).
  **Person B** = teammate (CIT student; builds dashboard UI, open-data wiring, slides/business).
  The team is one cybersecurity student and one CIT (computing & information technology) student.
- Status at handoff: Replit project set up as **Flask only** (an Express server from the Replit template
  was removed/stopped because it owned `/api`). Engine, bot, dashboard files are in place. The user is now
  **testing the WhatsApp bot end to end**. Open-data wiring, AI key, sample images, deck, 90-day slide,
  Business Model Canvas, rehearsal and backup video are still TODO (section 14).

---------------------------------------------------------------------------------------------------

## 1. The event (confirmed from official guide, Q&A PDF, Dubai playbook)

- Name: UAE Hackathon 2026 (9th edition). Organizer: **TDRA** (Telecommunications and Digital Government
  Regulatory Authority), delivered by GIE. Slogan: **"Beyond Ideas, Into Impact"** (BEYOND IDEAS .. INTO IMPACT).
- 2026 is the UAE **"Year of Family"** → Theme 1 (Family-Centric Digital Society) is the flagship theme.
- Track 2 = Youth Track: **Pioneers** (university students, ages ~17/18–25, incl. recent grads/postgrads
  under 25) and **Rising Stars** (school, 11–17).
- Dubai venue: **Higher Colleges of Technology (HCT) Dubai, Student Campus**. Dates **9–11 Nov 2026**,
  **8:00am–4:00pm** daily. In person only. Every member attends all 3 days. Bring own laptop.
- Journey: online Kickoff 16 Oct → **Day 1 Understand & Explore** (9 Nov) → **Day 2 Build & Shape** (10 Nov:
  first prototype + mentor feedback + Business Model Canvas) → **Day 3 Refine & Pitch** (11 Nov: rehearsal,
  final submission, judging).
- Submission: presentation must be **submitted by ~10:00am on Day 3**; only submitted teams present.
  Teams can edit their portal submission until the final deadline.
- Pitch: **3 minutes + 2 minutes of judges' questions**. All team members take part. Slides on a screen,
  any software, **Arabic or English**. The **Business Model Canvas is one page of the presentation (required)**.
- Teams: 2–7 members. Must pick a challenge from the published list. Challenges come from government entities.
- Prototype: officially optional ("you present your idea and solution; any development you add makes it
  stronger"). AI tools are explicitly encouraged this year.
- Winners: **one fixed set of criteria at every location; top 10 teams win in each track.**
- Pioneers prizes: **1st AED 20,000; 2nd AED 15,000; 3rd AED 10,000; 4th–10th AED 5,000 each**; certificates.
- After: **Innovation Summit & announcement 16 Nov 2026**; **post-hackathon phase for winners 18 Nov – 3 Dec**
  (called **LaunchPad**). Mention intent to continue in LaunchPad in the pitch.
- Portals: team portal **https://admin.hackathon.ae** (login with UAE Pass; My Team → Create Team; invite with
  the + button; the user's portal showed NO team created yet and Submissions said "Please add team first so you
  can add files" — **the team must be created on the portal before submission**). Guide/resources site:
  **https://hackathon-guide.gie.xyz/** (challenge profiles, playbooks, worksheets, Q&A, agenda).
- Mentors: optional; available on site. Ask a mentor on Day 2 for the detailed scorecard and to confirm the
  solution fits Challenge 40 and that the UAE has no equivalent citizen tool.

## 2. THE RUBRIC (official weights and definitions — optimise everything for this)

| Criterion | Weight | Official definition |
|---|---|---|
| Alignment with Challenge and Impact | 15% | Evaluated on alignment with the nature of the presented challenge, the ability to create tangible impact addressing issues related to the core themes, and the contribution to enhancing the quality of digital government services provided to the community. |
| Effective Use of Data | 15% | Evaluated on the effectiveness and sustainability of the use of open data provided by government entities. Priority is given to solutions that employ this data in an innovative and comprehensive manner. |
| Innovative Use of AI and Emerging Technologies | 15% | Evaluated on the degree of innovation in utilizing AI and emerging technologies to address the presented challenges and deliver tangible added value. |
| Solution Feasibility and Planning | **20%** | Evaluated on ease of implementation in the actual work environment of the government entity, including a **clear 90-day execution plan to test the product, with defined milestones and a realistic timeline**. |
| Market Potential and Commercialization | 15% | The potential for the solution to be commercially viable or adopted in the market — how likely it can be monetized or integrated into existing systems or services. |
| Presentation, Clarity of Communication and Creativity of the Pitch | **20%** | Evaluated on the clarity and persuasiveness of the presentation in conveying the solution's value, applicability, and potential impact. |

Older TDRA criteria language (earlier editions) also mentioned: reducing bureaucracy, feasibility, data
utilization, innovative AI use, the government entity's capacity to implement, creativity of the pitch.

Key strategic reading of the rubric:
- 40% is NON-CODE (Feasibility/90-day plan 20% + Pitch 20%). Do not let the build eat the deck/rehearsal time.
- **Data (15%)** and **AI (15%)** are the idea's weakest spots unless deliberately built in:
  → wire in **Bayanat** and **Dubai Pulse** open data and NAME the exact portal/dataset on a slide;
  → make the AI visible (Gemini scam-text analysis; say which AI tools were used).
- A judge-mode self-assessment during the session: idea scored ~7.5/10 as is; ~9/10 with (a) open data wired
  in, (b) visible AI layer, (c) a concrete 90-day plan slide, (d) a crisp emotional pitch + adoption answer.

## 3. Playbook facts (Dubai HackArena Playbook 2026, Track 2)

- Open data portals named in the playbook: **Bayanat.ae** (federal, has a REST API), **Dubai Pulse /
  data.dubai.ae** (Dubai datasets), **Ajman Data** (developer-friendly API with Python/GraphQL snippets),
  Abu Dhabi portal. Playbook rewards citing the exact dataset and its source portal.
- Free AI tools listed: Lovable, v0 (app/prototype), **Gamma** (decks, exports PPTX/PDF), Miro / Smaply
  (journey maps), Consensus / Perplexity (research), Gemini (free with Google account), others.
- "Read the Challenge Profile for your chosen challenge — it's the single most important input."
- Readiness checklist + logistics; same programme at every location.

## 4. Challenge 40 profile (the exact problem being solved)

- Title: **Building Trust in Digital Content** (open community challenge). Theme 4 — Digital Trust &
  Cyber-Secure Nation. Lead: **UAE Cyber Security Council** with **TDRA** and **Dubai Electronic Security
  Center (DESC)**.
- HMW: "How might we help people and organisations in the UAE quickly check whether a video, image or voice
  message is real — at the moment they receive it — so they are protected from deepfake-driven fraud,
  impersonation and misinformation?"
- Background: generative AI makes realistic fake video/images/voices in minutes; poor spelling or robotic
  voice are no longer reliable warning signs.
- Problem: people receive a video of a public figure, a voice note from a "relative" asking for money, or a
  message that appears to come from a government entity; they have seconds to decide and no easy trusted way
  to check. Detection tools are scattered, technical, mostly English, not available at the moment needed.
  **Genuine content has no simple way to prove it is genuine.** Result: financial loss, data theft, damaged
  reputations, falling trust.
- Recent UAE context in the profile: Sept 2026 MOHRE warned about fake videos/voice/images impersonating the
  Ministry and officials (Khaleej Times); same month DESC urged vigilance and announced **Saraab**.
- Aspects: A1 types of fakes (cloned voices of relatives/managers; fake videos of officials; impersonation of
  government entities and banks; fake images/documents/faces for identity checks); A2 the moment of decision
  (scams use urgency) … (profile continues with more aspects/sub-questions).

## 5. Saraab (DESC) — what it is and why we do NOT depend on it

- Built by DESC; unveiled **16 Sep 2026 at GISEC Global**. **Video-only** face deepfake detector (facial
  heat-maps + motion across frames); works from ~7-second clips; DESC claims up to 91% accuracy (89% on unseen
  data) — self-reported, no public test set.
- Planned release on Hugging Face / GitHub "by end of 2026". **As of 9 Nov 2026 NOT downloadable**: no repo,
  no weights, no API, no demo found. Does NOT cover audio/voice, still images, real-time calls.
- Decision: **do not depend on or "complement" Saraab** (user explicitly said they don't need to complement it).
  Use it only as framing: "Saraab detects fake video for experts; nobody gives citizens an Arabic way to verify
  official content — that is the gap we fill." Do not rebuild video deepfake detection.

## 6. How we got to this idea (decisions and rejected options)

- Reviewed all 40 challenges. Cyber-relevant: 9 (SCA incident reporting), 10 (u.ae content accuracy),
  22 (cybercrime reporting), 27 (secure agentic AI), 28 (critical infrastructure), 29 (SME cyber resilience),
  30 (gov payment data), 31 (gov identity impersonation, Fujairah Finance), 40 (digital content trust).
  Family theme = Challenge 39 "Family First" (Ministry of Family + TDRA).
- Considered and set aside:
  - **Challenge 39 Family First** ("Mabrouk for Every Family" proactive life-event services; "Osra Circle"
    eldercare). Strong on Year-of-Family theme but less cyber.
  - **Clone/impersonation-account detector** based on a real story (user's cousin's Instagram was cloned and
    mass-followed relatives around a wedding). Fits Challenge 31 better than 40; Instagram data access is a
    problem. The cousin story was NOT used in the final idea (could be a pitch anecdote only if relevant).
  - **Fake police calls** verification (UK 159-style callback): discussed, not chosen.
  - Pure deepfake detector: rejected (crowded, competes with Saraab, flaky live).
- Chosen: Challenge 40 with a **provenance-style "verify genuine official content"** approach inspired by
  **C2PA / Content Credentials** and the **US Embassy in Guinea** pilot, adapted as: Arabic-first,
  WhatsApp-forward bot, image-fingerprint registry (survives WhatsApp metadata stripping), plus a government
  early-warning dashboard. Positioning line: "the Guinea model, adapted for Arabic + WhatsApp — which no Arab
  government runs."
- Pivot during session: judges are mostly NOT IT people → focus on the **dashboard** (visual) and the
  **business side**; the engine is not shown as code, only through the forensic view.
- Adoption objection ("would older people use an app?") answer: no app — they **forward** (a habit they
  already have) to one trusted WhatsApp number; family "guardian mode" (pitch concept) lets children protect
  parents; government distributes via trusted channels; every forward feeds the government dashboard, so even
  people who never check are protected by the correction that follows.

## 7. Evidence for the pitch (verified unless marked)

Fake government news / war misinformation:
- UAE ordered arrest of **35 people** (19 Indian nationals) for misleading war videos, some AI-made or recycled
  footage passed off as UAE strikes — https://www.nationalheraldindia.com/amp/story/international/uae-orders-arrest-of-35-over-alleged-misleading-war-videos-on-social-media
- AI video of **Burj Khalifa collapsing: 12M+ views**; AI war content on X **1B+ views**; **500+ AFP debunks** —
  https://www.al-monitor.com/originals/2026/04/whats-real-anymore-ai-warps-truth-middle-east-war
- Deepfake broadcast announcing **Iran's surrender, 1M+ views** — https://www.aap.com.au/factcheck/deepfake-news-report-falsely-announces-irans-surrender/
- **51 websites** each pushing 12+ false war claims (NewsGuard) — https://www.arabnews.com/node/2605459/amp
- Fake "explosions, shortages, Dubai at a standstill" posts (Mar 2026); Dubai Media Office said most came from
  outside the UAE — https://www.khaleejtimes.com/uae/fake-dubai-claims-about-explosions-shortages-come-from-outside-uae
- **Reuters** falsely reported explosions in Downtown Dubai (Jul 2026); criminal probe continued after apology —
  https://www.khaleejtimes.com/uae/uae-investigation-publication-false-report-dubai-explosions
- Fake "capital-control laws" for foreign investors denied by Ministry of Economy (Mar 2026) —
  https://www.khaleejtimes.com/uae/no-new-strict-laws-foreign-investors-fact-check
- State news agency **WAM cloned** to post fake stories (2017). MOHRE deepfake-official warning (Sep 2026).
- Spreading fake news in UAE: **Dh100,000–1,000,000 fines, 1–2 years jail**; courts treat forwarding as fresh
  publication; TDRA advises verifying before forwarding "especially in family group chats" —
  https://www.khaleejtimes.com/uae/dh1-million-fine-for-spreading-rumours-fake-news-in-uae

WhatsApp / older users:
- Guess et al. 2019 (Science Advances): people **65+ shared fake news ~11% vs ~3% for ages 18–29** (≈3–4x) —
  https://spia.princeton.edu/news/fake-news-shared-very-few-those-over-65-more-likely-pass-such-stories-new-study-finds
  (newer work: driven by trust in personal networks, not just skills).
- ~75% WhatsApp penetration in MENA. WhatsApp forwarding limits: 2018 India, Jan 2019 global 5-chat, Apr 2020
  one-chat for "forwarded many times" (cuts velocity, not belief).
- Forward-to-verify tiplines proven: India Checkpoint 2019 ~158k messages. Arabic tiplines (Fatabyyano "Kinan"
  on Meedan) ran on Messenger/Instagram/Twitter, **not WhatsApp** → whitespace (verify no Arabic WhatsApp
  tipline already exists).

Business numbers (verified):
- GASA + Trend Micro, published 27 Jan 2026, 1,000 UAE residents: **70%** encountered a scam; a scam attempt
  **every 3 days** (~111/yr); **1 in 3** lost money last year; **half** of those who reported saw no action or
  outcome; **96%** tried to verify legitimacy —
  https://gasa.org/knowledge-base/blog/scams-hit-uae-residents-every-three-days-on-average-new-research-finds
- GASA/BioCatch Nov 2024 (~2,000): average loss **$2,194 (~AED 8,000)** per victim; only **9% fully recovered** —
  https://www.biocatch.com/press-release/uae-residents-lose-millions-to-scams-2024
- Dubai Police arrested two suspects; scammers **posing as officials stole AED 11.8 million** (Oct 2026) —
  https://www.emirates247.com/uae/dubai-police-arrest-two-suspects-in-phone-scam-as-victims-lose-aed118-million/6407
- Disinformation cost the world **$417 billion in 2024** (Sopra Steria; AI makes harm 15–20% worse) —
  https://www.emarketer.com/content/disinformation-s-417-billion-price-tag-what-marketers-need-know
- **Singapore 2025**: scam cases **−24.8%** (to 41,974); losses **~−18%** (to S$913M); bank/police alerts avoided
  **S$348M** — https://www.police.gov.sg/media-hub/police-life/2026/02/scams-and-cybercrime-fell-by-almost-a-quarter-in-2025
  (ScamShield helpline 30 → 700 calls/day in a year; ScamShield app 900k+ downloads.)
- DO NOT USE (wrong/unverified): "AED 11.8 billion foiled by Dubai Police" (that is 2020, too old);
  "56% face scam attempts monthly" (unverified); "$78 billion cost of fake news" (source gone).

Provenance proof points:
- **US Embassy in Guinea (Conakry)** since ~Apr 2025: signs official imagery with C2PA + invisible Digimarc
  watermark, "verify here" prompt, public mobile verifier on the open CAI stack, "Verify Before You Share"
  campaign — closest existing model to Haqeeq.
- C2PA used by Adobe, OpenAI DALL-E 3 (Feb 2024), Sony/Nikon/Leica cameras, YouTube (Oct 2024), TikTok
  (May 2024), Taiwan 2024 and Mexico 2024 election pilots. No government found running a citizen-facing
  "verify official media" portal in Arabic.
- Known limitation: WhatsApp/Facebook strip C2PA metadata and recompress → our fix is fingerprint matching
  against a registry (works on screenshots). "Absence of a credential is not proof of a fake."

## 8. Product definition

Three parts, one Replit project:
1. **WhatsApp bot (citizen side)**: forward an image or text to the Twilio sandbox number → Arabic reply:
   - genuine: "✅ صحيح — يتطابق مع مرجع رسمي متاح."
   - altered: "🔴 معدّل — نسخة معدّلة من إعلان رسمي. لا تقم بإعادة إرساله."
   - unverified: "⚪ غير مؤكد — لم يصدر عن أي جهة رسمية. كن حذراً."
   - scam_risk: "🔴 احتيال محتمل — الرسالة تحمل مؤشرات احتيال. تحقق قبل أي إجراء."
2. **Engine (brain)**: decides the verdict (section 10).
3. **Government dashboard** at `/dashboard` (section 11). Used by TDRA / DESC / Government Media Office staff
   in the real world; shown on the big screen in the demo. It is a real product component, not just a demo prop.

Honest framing rules:
- The map shows **where reports come from**, not the private WhatsApp spread path (end-to-end encrypted).
- Background activity on the dashboard is **seeded sample data**; live forwards in the demo are real.
- Government signing key / PKI is **mocked**; registry is small (6–8 posts); trend numbers seeded.
- The bot's emirate for each report is currently **random** (demo); real system would use reporter's area.

## 9. Repo / files

```
haqeeq/
  main.py              Person A — Flask app, Twilio /whatsapp webhook, Arabic replies, registers dashboard blueprint
  engine.py            Person A — verification engine (pHash match + pixel tamper) + text scam check (+ optional Gemini)
  db.py                Person A — SQLite helpers + schema (official_posts, reports, entities)
  seed.py              Person A — fingerprints every image in official_posts/ into the registry
  dashboard.py         Person B — Flask Blueprint: /dashboard, /api/reports, /api/corrections, /api/correct, /media/<file>
  demo_seed.py         Person B — adds ~55 sample reports over last 60 min; --clear wipes reports + corrections
  templates/dashboard.html  Person B — the control-center page (Leaflet map, Chart.js, feed, forensic, trending)
  official_posts/      put genuine official announcement images here (README.txt inside)
  requirements.txt     flask twilio pillow imagehash numpy scipy requests
  .replit / replit.nix run = "python main.py"
  CLAUDE.md            this file
```

Data contract (the ONLY interface between Person A's and Person B's halves) — table `reports`:
`id, ts (UTC ISO), sender (masked), kind (image|text|link), verdict (genuine|altered|unverified|scam_risk),
matched_id, distance, emirate, detail, image_path`.
Other tables: `official_posts(id, title, issuer, date, hash8, hash16, image_path)`,
`entities(name, kind, source)` (for Bayanat open data), `corrections(detail PK, ts, message)` (created by dashboard.py).

Routes: `/` (health text "Haqeeq is running. Open /dashboard"), `/whatsapp` (POST, Twilio webhook),
`/dashboard`, `/api/reports` (joined with official post title/issuer/image; adds image_url/official_url),
`/api/corrections`, `/api/correct` (POST {detail, message} → returns recipients count),
`/media/<file>` (serves official_posts/* and incoming_* images; basename only, path-traversal safe).

## 10. Engine details (engine.py)

Image verification, two steps:
1. **MATCH**: 64-bit pHash (`imagehash.phash(img, hash_size=8)`) of the incoming image vs each registry post's
   `hash8`; take the smallest Hamming distance. If > `MATCH_THRESH` (12) → **unverified**.
2. **TAMPER**: resize incoming and matched official image to 256×256 greyscale; percent of pixels whose grey
   value differs by more than `PIXEL_THRESH` (55). If ≤ `TAMPER_PCT` (0.04%) → **genuine**; else **altered**.
   (A 16×16 heat grid is computed but not yet shown on the dashboard.)

Why this design: pHash alone could NOT detect a small edit (tested: a changed date barely moved the hash), and
block-mean comparison washed edits out; per-pixel changed-fraction separated them.
Tested results with synthetic images: exact official → genuine; recompressed/resized "screenshot" → genuine;
changed date line → altered (~0.09% changed vs ~0.00% for screenshot); unrelated images → unverified (coarse
distance 30–34). Caveat: an image sharing the same template/border as an official post can coarse-match and be
called altered instead of unverified. **Thresholds must be tuned with the team's real images**:
- screenshot shows altered → raise TAMPER_PCT (0.04 → 0.1); also crop screenshots tight (no chat bubbles/status bar)
- doctored shows genuine → lower TAMPER_PCT (→ 0.02) or make the edit bigger/clearer
- unrelated image matches → lower MATCH_THRESH (12 → 8); everything unverified → raise it (→ 16) / re-run seed.py
- after editing engine.py, Stop + Run again.

Text check: `ai_text_check()` calls Gemini REST (`gemini-2.0-flash:generateContent`, key from secret
`GEMINI_API_KEY`) asking for JSON {risk, reason_ar}; **model name must be verified** — on any failure it falls
back to rules. Rule-based: ≥2 hits from an English+Arabic scam keyword list (urgent, transfer, fine, OTP,
عاجل، تحويل، غرامة، رابط، جائزة …) → scam_risk; else unverified.

NOT implemented (be honest / possible next steps): real **C2PA signing/verification** (forensic view always shows
"signature not found — stripped by WhatsApp" for images; a true "verified by signature" path does not exist —
the ✅ comes from fingerprint match); **link / lookalike-domain check** (discussed: compare against official
domains like wam.ae, mediaoffice.ae, u.ae, *.gov.ae with string similarity; not built); voice-note checking;
family guardian mode (pitch concept only); heat-map overlay in UI; real WhatsApp correction delivery (the
"push correction" only records it + shows a toast with recipient count; actual Twilio send not wired).

## 11. Dashboard details (dashboard.py + templates/dashboard.html)

- Dark "National Trust Control Center" UI (Inter + Noto Kufi Arabic fonts). Header with ح logo, LIVE dot, Dubai clock.
- KPI strip: checks today, verified genuine, altered official posts, scam messages, corrections sent.
- Live feed (left): newest first, slide-in animation for new items, thumbnail, verdict pill, detail, emirate, time, masked sender.
- **UAE map** (centre): Leaflet + CARTO `dark_all` tiles, fitted to UAE bounds. Pulsing hotspot per emirate
  sized by OPEN (uncorrected) fakes, red if altered/scam, grey if unverified, **teal ✓ when all corrected**;
  small dots per report (stable jitter); ripple when a new forward lands. Label positions per emirate to keep
  the Dubai/Sharjah/Ajman/UAQ cluster readable; Sharjah marker z-lifted.
- Activity chart (below map): fakes vs genuine per 5-min bucket, last 60 min.
- Forensic view (right top): auto-opens the newest forward; animated steps (1 signature, 2 fingerprint match
  with distance/64, 3 tamper check or source check; text: source + AI scam analysis); forwarded vs official
  image side by side; similarity % bar. Map only zooms when the user clicks (not on auto-select).
- Trending fakes (right bottom): grouped by `detail`, count, bar, where it's spreading, **Push official correction**
  button → POST /api/correct → hotspots shrink, items turn "corrected", toast "Correction sent to N citizens".
- Polls `/api/reports` + `/api/corrections` every 2 s.
- GOTCHAS learned: (1) **never write `{{` / `{%` in dashboard.html** — Jinja treats it as a template tag
  (this broke the page once; fixed by using a KIND_ICONS constant). (2) Flask caches templates — restart after
  editing. (3) Leaflet/Chart.js/fonts/tiles load from CDNs → Replit must be online (fine on Replit).
- demo_seed.py scenarios: Fake "explosions in Downtown Dubai" image (heaviest), altered public holiday notice
  with a fake date, scam "Dubai Police fine — pay now via link", AI video of Burj Khalifa collapsing, scam
  "Emirates ID suspended — verify OTP", genuine MOHRE announcement, genuine weekend schedule notice. Weighted to
  Dubai/Sharjah. Run it shortly before the pitch so the 60-min chart is full.
- A verified preview screenshot of the dashboard was produced (dark map tiles didn't load in the sandbox only).

## 12. Replit + Twilio setup (as done / to re-check)

1. Replit project (user's account), teammate invited. Project initially came with an **Express server owning
   `/api`** → resolved by choosing **"Use Flask only"**: stop/remove Express, Run = `python main.py`, Flask on
   `0.0.0.0` and `PORT` env (default 8080). Keep routes listed in section 9.
2. `pip install flask twilio pillow imagehash numpy scipy requests` (+ `pandas` for open data).
3. Secrets: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, optional `GEMINI_API_KEY` (aistudio.google.com).
4. Put 6–8 official-looking Arabic announcement images in `official_posts/` → `python seed.py`
   (prints "Seeded N official posts").
5. Twilio: Messaging → Try it out → Send a WhatsApp message; every demo phone sends `join <code>` to the sandbox
   number (**joins expire ~72h — re-join on pitch morning**). Sandbox settings → "When a message comes in" =
   `https://<repl-url>/whatsapp`, **POST**, Save. If Replit URL changes, update it here.
6. Media download from Twilio requires basic auth with SID/token (already in main.py).
7. Replit dev URL only works while the Repl is running (keep tab open / press Run before presenting; Deploy
   for an always-on URL).

Testing the bot (current step for the user): open `/` → health text; send `hello` → ⚪; send
`عاجل حوّل المبلغ فوراً لتجنب غرامة` → 🔴 scam; send official image → ✅; tight-cropped screenshot of it → ✅;
edited version → 🔴 altered; unrelated photo → ⚪; check `/dashboard` shows them.
Troubleshooting: no reply → Twilio Monitor → Logs → Errors (**11200** = URL wrong/app stopped);
`KeyError TWILIO_ACCOUNT_SID` → secrets missing; text works but images fail (401) → wrong SID/token;
always unverified → re-seed / raise MATCH_THRESH.

## 13. Demo, pitch, business

Demo beats (build only what's shown; dashboard on big screen, phone mirrored if possible):
1. Forward a genuine official post → ✅ (appears on map + forensic view auto-opens).
2. **Showstopper**: screenshot that post (WhatsApp would strip any signature) and forward → still ✅. Slow down.
3. Forward a doctored version (changed date/number) → 🔴 altered.
4. Forward a fake "explosions in Dubai" image → ⚪ unverified; appears on map and trending.
5. Forward a scam text (urgency + money) → 🔴 scam risk, Arabic.
6. Click **Push official correction** on the top trending fake → hotspots shrink, emirates turn teal, toast with
   recipients. Line: "One forward from a grandmother just helped stop a fake before it reached the next thousand families."
Record a **backup video** of the full run (Day 2 evening); bring a phone hotspot.

3-minute pitch (Gamma deck):
- 0:00–0:25 Hook: Burj Khalifa AI collapse video 12M views; UAE arrested 35 people for forwarding fake war
  videos; people over 65 share fake news 3–4x more.
- 0:25–0:45 Problem: fake official content spreads in family WhatsApp groups; no way to check if it's really
  from the government. 70% of residents faced a scam, one every 3 days; 96% try to verify but have no tool;
  half who report never hear back.
- 0:45–1:00 Solution in one line + proof: the US Embassy in Guinea runs this model; no Arab government does.
- 1:00–2:05 Live demo (beats above). Person B drives the phone; Person A narrates the forensic view.
- 2:05–2:25 Impact: protects families, cuts rumour spread, faster corrections; Year of Family; National
  Cybersecurity Strategy 2025–2031; enhancing digital government services (rubric wording).
- 2:25–2:45 Business model: BMC; government-owned/funded; Singapore proof (scam cases −25%, S$348M avoided);
  disinformation cost $417B (2024).
- 2:45–3:00 Ask + close: pilot with TDRA + Government Media Office; continue in LaunchPad.
  "Haqeeq — so the truth can prove itself, in the app every family already uses."

90-day execution plan (Feasibility 20% — its own slide):
| Days | Milestone | With whom | Metric |
|---|---|---|---|
| 0–30 | Pilot with one entity: sign official posts, seed registry, launch WhatsApp verify number | Dubai Media Office + TDRA | Time from fake appearing → correction sent |
| 31–60 | Add Dubai Police scam alerts; onboard 3–5 ministries; "Verify Before You Share" family campaign | DESC + Dubai Police | # verified checks; # fakes corrected |
| 61–90 | Measure impact, report, plan national rollout + GCC export | Cyber Security Council | Reach; reduction in how far a fake spreads |

Business Model Canvas (one page, required):
- Customer segments: UAE families (esp. older relatives in group chats) = beneficiaries; government entities that
  own/fund it (TDRA, Cyber Security Council, DESC, Government Media Office).
- Value proposition: proactive, Arabic-first verification of official content in the app families already use;
  early warning + one-click correction for government.
- Channels: WhatsApp for citizens; dashboard for government; distribution via trusted government/telecom channels.
- Key partners: TDRA, Cyber Security Council, DESC, Government Media Office / WAM, Dubai Police, Etisalat/du.
- Key activities/resources: signing + registry, verification engine, open-data feeds (Bayanat, Dubai Pulse),
  PDPL-compliant handling.
- Revenue/funding: B2G national licence + per-entity onboarding (not a consumer fee), justified by scam-loss
  prevention and public trust; later banks/telecoms pay to verify their own messages; GCC export (Arabic-first).
- Cost structure: low — cloud hosting, WhatsApp Business messaging, open standards; main cost is the team.
  (Pricing and cost figures not yet worked out — don't quote numbers you can't justify.)

Open data (Data 15%) — UPDATED PLAN (must use government-provided open data only; see REBUILD_PROMPT.md):
- Trusted-source registry from Bayanat entity list (https://bayanat.ae/en/entities) + Dubai Pulse organisation
  register (https://www.dubaipulse.gov.ae/registers/orgztoa).
- Per-capita risk map ("fake reports per 100,000 residents" + campaign-targeting ranking) from FCSC open data
  population estimates (opendata.fcsc.gov.ae) + Dubai Pulse population by community
  (https://www.dubaipulse.gov.ae/data/dsc-statistics/dsc_population_by_community-open).
- Dubai area names from Dubai Pulse area lookup (https://www.dubaipulse.gov.ae/data/dld-transactions/dld_lkp_areas-open).
- Datasets found but columns/format not yet verified. Ask organisers on Day 2 whether Challenge 40 owners
  provided challenge-specific datasets; use those first.
- Slide line: "Trusted-source registry built from Bayanat's government-entity list and the Dubai Pulse
  organisation register; the risk map normalises reports by FCSC and Dubai Pulse population data."
Older notes (superseded by the above):
- Bayanat: download a government-entities dataset (CSV) → load into `entities` table (pandas loader below) →
  use as the "trusted official sources" list. Slide wording: "Trusted-source registry seeded from Bayanat's
  government-entity data; spread map uses Dubai Pulse area data."
- Dubai Pulse: area/population dataset to weight/label map areas instead of random emirates.
- Loader sketch:
  ```python
  import pandas as pd
  from db import get_conn, init_db
  init_db(); df = pd.read_csv("bayanat_entities.csv"); conn = get_conn()
  for name in df["EntityName"].dropna().unique():
      conn.execute("INSERT INTO entities (name, kind, source) VALUES (?,?,?)", (str(name), "gov_entity", "Bayanat"))
  conn.commit(); conn.close()
  ```

Judge Q&A (who answers):
- "Would older people use this?" (B) No new app or behaviour — they forward to one trusted number; children set up
  guardian mode; government distributes via trusted channels; every forward feeds the early-warning dashboard.
- "WhatsApp strips your signature." (A) Yes — that's why the engine matches by image fingerprint; shown live in beat 2.
- "What about text and voice?" (A) AI text-check covers text rumours; voice is honest future work (risk score, not verdict).
- "Does this already exist in the UAE?" (B) Saraab detects deepfake video for experts; no Arabic citizen tool for
  verifying official content (confirm with a DESC/CSC mentor first).
- "Absence of a signature isn't proof of fake." (A) Agreed — app says "unverified, treat with caution", never "proven fake".
- "Can you see how fakes spread on WhatsApp?" — No, it's encrypted; we map where reports come from.
- Possible judge objection: adoption depends on government signing/registering its content → that's the 90-day pilot.

Cut order if behind: Gemini LLM (keep rules) → heat-map detail → push-correction beat (describe it) → static map.
Never cut: fingerprint engine, bot, 90-day slide, deck, rehearsal.

## 14. Status and TODO at handoff

Done:
- Research, challenge choice, product design, rubric strategy.
- Code written and tested locally (engine verdicts, Flask routes, webhook text path, dashboard in a real browser,
  correction flow). Dashboard redesign with live map done.
- User set up Replit (Flask only, Express removed) and built up to the dashboard; Replit Agent helped wire the
  dashboard blueprint.

In progress:
- User testing the WhatsApp bot end to end (section 12).

TODO (priority order):
1. Bot gate test passes on real phones (text, official image, screenshot, doctored, unrelated); tune thresholds.
2. Create the demo assets: 6–8 Arabic official-looking announcements (logo, date) in official_posts/ + seed;
   2 doctored versions; 2 fake rumour images (e.g. "explosions in Dubai"); scam text messages; correction message.
3. GEMINI_API_KEY + verify model name works (AI 15%).
4. Open data wiring: Bayanat entities + Dubai Pulse map data (Data 15%) and cite them.
5. **Create the team on admin.hackathon.ae** (UAE Pass → My Team → Create Team → invite teammate) so the deck can
   be submitted; submit by ~10:00am Day 3.
6. Deck in Gamma: problem, solution, demo, impact, **90-day plan slide**, **BMC page**, ask. Rehearse 3+ times, timed.
7. Feature freeze Day 2 ~6pm; record backup demo video; phone hotspot; re-join Twilio sandbox on Day 3 morning;
   run demo_seed.py before pitching; warm up the Repl.
8. Day 2 morning: ask a mentor for the detailed scorecard and confirm no UAE equivalent exists.

## 15. Documents created during the session (Google Drive, owner aburamadannuha@gmail.com)

- Build & Delivery Plan (v1, hour-by-hour): https://docs.google.com/document/d/1_fEv0Uwv41ubp7M9zgrRTVFFZK3UPz0s7yHR7yxoL88/edit
- Full Build Tutorial v1 (OUTDATED dashboard code): https://docs.google.com/document/d/1YUSJZ1Dsso-rnKG5xQMiOaPryj9A5qlRaxSKdZ3clmY/edit
- Full Build Tutorial v2 (current): https://docs.google.com/document/d/1U2ePvzJbxQ0gSL-5aiIsECTuyQF7cfyCCkL81WUWs90/edit
- dashboard.html code doc: https://docs.google.com/document/d/1OtNnBuyKFMLNdXiEC5A7_axn9k7E_ilMD5MIInLL3iA/edit
- Research reports produced (summarised in this file): "UAE Hackathon 2026 winning edge", "Challenge 40 ideas
  abroad", "Fake gov news and C2PA", Saraab status notes.
- Code pack: haqeeq_code.zip (this repo).

## 16. Working preferences of the user

- Wants concrete, thorough, step-by-step instructions with exact code; split by person.
- Values the rubric above everything; wants the dashboard to look impressive for non-technical judges.
- Short on time (hackathon is live). Prefers decisive recommendations over option lists.
- Do not fabricate numbers; flag anything unverified. Keep claims honest (seeded data, mocked signing, map ≠ spread path).
