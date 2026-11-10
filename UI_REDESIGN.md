# Haqeeq dashboard — UI redesign plan ("make it look like a government product, not an AI demo")

Audience: UAE government judges (mostly non-technical) looking at a **1920×1080 projector** for ~60 seconds of a 3-minute pitch.
Goal: calm, credible, premium, instantly readable. Based on the mock-mode screenshot of the current build.
Rules for whoever edits: work on a **branch** (never push straight to `main` — it deploys live), only touch `components/*.tsx`,
`app/globals.css`, `app/layout.tsx`, `public/`. Do not touch `api/`, `engine/`, `scripts/`, `supabase/`. Never create `app/api/`.
Check with `npm run dev` → `http://localhost:3000/?mock=1` at 1920×1080. `npm run build` must pass before pushing.

---------------------------------------------------------------------------------------------------

## 1. Why it currently looks "AI-generated" (diagnosis)

- Neon cyan/teal gradients and glowing borders on almost every card; gradient fills on buttons and the logo tile.
- Everything is a floating translucent "glass" card on a blurred blue backdrop.
- Dozens of tiny ALL-CAPS, letter-spaced micro-labels (10–11px equivalent) plus a second Arabic label on every heading.
- Too many things competing at once: 5 KPIs, feed, map, chart, ranking, open-data list, forensic, trending — all the same visual weight.
- Many different accent colours and pill shapes; emoji-style status icons.
- Cramped small text that will be unreadable from the back of a room.

## 2. Design direction

**Think:** u.ae / Digital Dubai / a national control room — flat, orderly, restrained. Authority comes from hierarchy, whitespace
and consistent alignment, not effects.

Principles
1. **One hero (the map)**, one secondary (the forensic panel), everything else quiet.
2. **Flat, not glowing.** Solid panels, 1px hairline borders, no outer glows, no text gradients, no blur backdrops.
3. **Colour means something.** Neutral base; emerald = verified/genuine; red = altered/scam; amber = warning; grey = unverified; gold = brand accent only.
4. **Big and legible.** Nothing below ~14px at 1920 wide; key numbers huge; labels sentence-case, not tiny caps.
5. **Fewer words.** One language per label where possible (English headings with Arabic as a compact secondary on the main titles only).
6. **Motion with purpose.** Only: new report slides in, new-report ripple on the map, number count-up, Push-correction success. Nothing decorative that loops.

## 3. Design tokens (put in `app/globals.css`)

```css
:root {
  --bg:        #0A1628;   /* flat deep navy page background (no gradient glow) */
  --panel:     #0F1F36;   /* card surface */
  --panel-2:   #13263F;   /* raised / hover */
  --line:      #22364F;   /* 1px borders */
  --text:      #E8EEF5;   /* primary text */
  --muted:     #93A4B8;   /* secondary text (keep contrast >= 4.5:1 on --panel) */
  --verified:  #1FA37A;   /* genuine / corrected */
  --danger:    #E5484D;   /* altered / scam */
  --warn:      #E0A030;   /* attention */
  --neutral:   #8795A8;   /* unverified */
  --gold:      #C9A24B;   /* brand accent, thin rules and the logo only */
  --radius:    10px;      /* one radius everywhere */
}
```
- Remove: `backdrop-filter`, `box-shadow` glows, `background-clip:text` gradients, radial-gradient page background blobs.
- Page background: flat `--bg`. Optional: a very faint dot grid at ~4% opacity (CSS only) — nothing else.
- Cards: `background: var(--panel); border: 1px solid var(--line); border-radius: var(--radius);`

## 4. Typography

- Headings + numbers: **IBM Plex Sans Arabic** (Arabic + Latin in one family, institutional feel) — or keep Noto Kufi Arabic for Arabic and **Inter** for Latin
  but use only two weights (500 and 700).
- Sizes at 1920×1080 (the app scales with rem; check the result visually): page title 28px, panel titles 18px, body 15–16px, numbers 44–56px,
  captions 13px minimum. **Delete every 10–11px caps label.**
- Panel titles: sentence case ("Live citizen reports"), left-aligned, with the Arabic version small and muted on the same line only for the 4 main panels.

## 5. Layout (1920×1080, no scroll)

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ [logo] National Trust Control Center  مركز الثقة الوطني      ● LIVE  12:04 GST │  header 72px, flat, gold 2px rule under it
├───────────────────────────────────────────────────────────────────────────────┤
│ Checks │ Genuine │ Altered │ Scam │ Corrections         (5 KPIs, one slim row) │  96px
├──────────────┬──────────────────────────────────────────────┬─────────────────┤
│ Live reports │                                              │ Forensic view   │
│ (feed)       │            UAE MAP  (hero, ~50% width)       │ (selected report)│
│ 360px        │                                              │ 480px           │
│              ├──────────────────────────────┬───────────────┤                 │
│              │ Activity (60 min)            │ Campaign targ.│ Trending fakes  │
└──────────────┴──────────────────────────────┴───────────────┴─────────────────┘
 footer 36px: "Simulated background activity · live forwards are real · signing key mocked"
```
- **Open data panel → move out of the main grid.** Make it a compact footer strip or a drawer opened by a button
  "Data sources (4)" listing Bayanat · u.ae · Dubai Land Dept. It matters for the Data score, but it shouldn't compete with the map.
  (Keep it one click away and also on the Data slide.)
- Give the map more room; make the chart and ranking shorter and quieter.
- 24px outer padding, 16px gaps, everything aligned to the same grid. Consistent panel header height.

## 6. Component-by-component

**Header (`Header.tsx`)** — Replace the gradient "ح" tile with the real logo (`public/logo.svg`, see §8). Title 24–28px, Arabic title beside it in muted gold-ish
white. LIVE indicator = small green dot + word "Live" (slow 2s pulse is fine). Clock plain text. Toggle/Operator buttons = flat outline buttons.
Thin 2px `--gold` line under the header.

**KPIs (`Kpis.tsx`)** — One slim row of five flat cards: big number (count-up), label below in 14px sentence case, small coloured left border (4px) in the
verdict colour. Drop the "incl. simulated background" sub-labels from each card; show it once in the footer/Demo-mode toggle.

**Live feed (`Feed.tsx`)** — Rows: 56px thumbnail, one-line title, verdict as a **solid small tag** (text + colour, no emoji), detail line muted, time right-aligned.
Remove pill outlines/glows. "Simulated" tag only as muted small text. New row slides in once and gets a 2s subtle highlight.

**Map (`UaeMap.tsx`)** — The star. Keep Leaflet but: darker flat basemap (CARTO dark_nolabels or Esri dark gray), hide extra labels, emirate labels in white 14px with a
subtle text shadow. Hotspot = flat filled circle + thin ring (no heavy glow); size by open fakes; number inside; teal check when corrected. New-report ripple stays.
Legend as a small flat box. Caption "Where reports come from — not the WhatsApp spread path" stays (honesty).

**Forensic (`Forensic.tsx`)** — Make it read like a case file: verdict banner at top (solid colour band, big verdict word), then 3 numbered steps as a clean
checklist (✓ / ✕ / – icons, not emoji), then forwarded vs official images side by side with the heat-map overlay and a single similarity bar. Fewer words per step.

**Trending (`Trending.tsx`)** — Each row: fake title, count (big), thin bar, "Push official correction" as the **single primary button** (solid emerald, white text, 40px tall).
This is the demo's climax — it should be the most obvious button on screen. Success state: row turns green with "Corrected · sent to N citizens".

**Ranking / Activity chart** — Make quieter: single-colour bars (red for fakes, emerald for genuine), thin axes, no gridline clutter, 13px labels.

## 7. Effects worth adding (free libraries; max 3–4 total)

Magic UI (https://magicui.design — MIT, copy components with the shadcn CLI; verify Tailwind 4 / React 19 compatibility per component):
- **Number Ticker** for KPI numbers (or keep the existing `CountUp`).
- **Animated List** for the live feed (new reports slide in).
- **Border Beam** or **Shine Border** on *one* element only: the newest report card or the Push-correction button.
- **Dot Pattern / Grid** at very low opacity behind the page.
Skip: particles, globes, aurora/spotlight backgrounds, 3D cards, marquees — they read as "AI template".
21st.dev: browse for a clean toast and a data-table row style if useful; copy only what matches the tokens in §3.

## 8. Logo

Use the logo from the Gemini brief (Arabic ح shaped into a check inside a shield; navy/emerald/gold). Put the final file at `public/logo.svg` (or `logo.png`,
transparent background) and a white-on-navy variant. Use `next/image` in the header at ~44px height. Add the same logo to the favicon (`app/icon.png`).
Do not use a falcon, UAE flag or any government emblem.

## 9. What NOT to change (keeps the demo working)

- Data/props and Supabase logic in `lib/useDashboardData.ts`, `lib/*.ts` — only touch presentation.
- Honest labels: "simulated background", "mocked signing key", map-origin caption, "Unverified never means proven fake".
- The `?mock=1` mode, the Operator unlock flow and the POST to `/api/correct` with `X-Admin-Token`.
- No new files under `app/api/`.

## 10. Acceptance checklist (before merging to `main`)

- [ ] At 1920×1080 there is **no scrolling** and nothing is cut off; also usable at 1366×768.
- [ ] Smallest text is ≥13px at 1920 wide; muted text still passes contrast (≥4.5:1).
- [ ] No glows, no gradient text, no blur backdrops; at most one animated border effect on screen.
- [ ] The map is the largest element; the Push-correction button is the most prominent control.
- [ ] Colours follow §3 only (emerald/red/amber/grey/gold meanings are consistent).
- [ ] `npm run build` passes; `?mock=1` and the real-data view both render; a new report still triggers feed slide-in + map ripple.
- [ ] Screenshot at 1920×1080 reviewed by the team on a projector or big monitor; fix anything unreadable from 3 metres away.
- [ ] Merged via pull request after checking the Vercel preview link.

## 11. Suggested order of work (about 3–4 hours)

1. Tokens + remove glows/blur/gradients (`globals.css`) — biggest visual change, 30 min.
2. Header + KPIs + footer strip + logo.
3. Layout re-grid and moving "Open data" into a footer drawer.
4. Feed, Forensic, Trending restyle (Push button first).
5. Map polish (basemap, hotspots, labels, legend).
6. Add the 3–4 effects, then final screenshot pass and acceptance checklist.
