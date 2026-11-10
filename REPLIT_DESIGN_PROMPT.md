# Replit prompt — restyle the HAQEEQ deck to match UAE government design

How to use: open the Repl that built `HAQEEQ-Pitch-Deck.pptx`, and paste everything inside the block below into Replit Agent.
Content stays exactly as it is now; only the design changes. Keep your amber `[TEAM]` placeholders.

**Where these specs come from:** the official **UAE Design System 2.0** (maintained by TDRA; designsystem.gov.ae — colour system and typography pages), which is the reference for federal government digital design. I could not browse government social-media posts from here, so this is the published design system, not a survey of posts. Abu Dhabi and Dubai publish their own variants; this prompt follows the federal one.
Contrast ratios below were computed (WCAG): gold-500 on white is only 3.15:1, so gold is used as a *fill/accent*, and **gold-600 / gold-700 for any gold text on white**.

```
TASK: Restyle my existing 7-slide pitch deck (HAQEEQ-Pitch-Deck.pptx) so it looks like an official UAE federal-government presentation, following the UAE Design System 2.0 (TDRA). KEEP ALL TEXT CONTENT, SLIDE ORDER AND SPEAKER NOTES UNCHANGED. Rebuild the .pptx with native, editable PowerPoint shapes, text and charts (NOT screenshots or images of text). Output: HAQEEQ-Pitch-Deck-v2.pptx plus a PDF export.

CURRENT PROBLEMS TO FIX
- Dark navy "tech-startup" look with neon-ish teal/red/gold on dark cards; many small low-contrast labels; boxes everywhere with equal weight.
- The Business Model Canvas is a loose cluster, not the standard 9-block canvas layout.
- No real charts; stats are only big coloured numbers.
GOAL: calm, institutional, light, high-contrast, generous whitespace, one clear message per slide — like a ministry or TDRA briefing.

CANVAS
- 16:9, 13.333 x 7.5 in. Margins 0.6 in. 12-column grid, 0.25 in gutters. Align everything to the grid. Left-aligned titles (mirror to right-aligned for Arabic text; Arabic runs right-to-left with correct shaping).
- Content slides: WHITE background (#FFFFFF). Slide 1 (title) and slide 7 (ask): AE Black 950 (#0E0F12) background with gold accents and white text.

COLOUR TOKENS (exact — UAE Design System)
- AE Gold: 50 #F9F7ED · 100 #F2ECCF · 200 #E6D7A2 · 300 #D7BC6D · 400 #CBA344 · 500 #B68A35 · 600 #92722A · 700 #7C5E24 · 800 #6C4527 · 900 #5D3B26 · 950 #361E12
- AE Black: 50 #F7F7F7 · 100 #E1E3E5 · 200 #C3C6CB · 300 #9EA2A9 · 400 #797E86 · 500 #5F646D · 600 #4B4F58 · 700 #3E4046 · 800 #232528 · 900 #1B1D21 · 950 #0E0F12
- AE Green: 100 #E4F4E7 · 500 #4A9D5C · 600 #3F8E50 · 700 #2F663C · 800 #2A5133
- AE Red: 100 #FDE4E3 · 500 #EA4F49 · 600 #D83731 · 700 #B52520 · 800 #95231F
- Supporting palette (for charts/illustration only): Sea Blue 500 #00ABEB / 600 #0090D4 / 700 #0073AB · Tech Blue 600 #043DFF · Camel Yellow 500 #F29F0E · Desert Orange 500 #EB5F24 · Slate 100 #F1F5F9 / 400 #94A3B8 / 500 #64748B / 700 #334155
- Roles: page white #FFFFFF; section/panel fill AE Black 50 #F7F7F7; hairline borders AE Black 100 #E1E3E5; primary text AE Black 900 #1B1D21; secondary text AE Black 600 #4B4F58 (never lighter than 500 on white); brand accent AE Gold 500 #B68A35 for rules, bars, icons and fills; GOLD TEXT on white must use Gold 600 #92722A or 700 #7C5E24.
- Semantic verdict colours (use consistently everywhere): Genuine = AE Green 600 #3F8E50 (tint #E4F4E7); Altered / Scam risk = AE Red 600 #D83731 (tint #FDE4E3); Unverified = AE Black 400 #797E86 (tint #F7F7F7); Warning / [TEAM] placeholder = Camel Yellow 500 #F29F0E with dark text.
- On dark slides: white text, gold 400 #CBA344 accents (8.1:1 contrast on #0E0F12).
- NO gradients, NO glows, NO shadows heavier than a 1px border, NO neon. Do not use the UAE emblem, flag or any government logo — use the HAQEEQ logo only.

TYPOGRAPHY (UAE Design System)
- English body: Roboto. English headings/titles: Inter. Arabic body: Noto Kufi Arabic. Arabic headings: Alexandria. (All Google Fonts.) Fallbacks: Arial / Segoe UI. Weights: body 400/500, headings 600/700. The ح/HAQEEQ wordmark may use Alexandria 700.
- Scale (for a 13.333 in slide): slide title 36 pt bold; section label 14 pt caps (gold 700, letter-spaced); body 20 pt; secondary body 18 pt; KPI numbers 54-72 pt; captions/sources 14 pt MINIMUM (the system recommends 16 px minimum; nothing smaller than 14 pt anywhere). Line spacing 1.2-1.3. Max ~6 lines of text per card.
- Titles: sentence case, one line, with a short gold accent rule (0.8 in x 0.06 in, #B68A35) under or beside the title.

MASTER LAYOUT (apply to slides 2-6)
- Top: 0.1 in full-width AE Gold 500 bar. Title top-left at 0.6 in margin. Small HAQEEQ logo (shield + wordmark) top-right, 0.4 in tall.
- Footer (0.35 in): hairline AE Black 100 rule; left "HAQEEQ · UAE Hackathon 2026 · Challenge 40 — Building Trust in Digital Content" (14 pt, AE Black 500); right slide number "n / 7".
- Cards: white fill, 1 pt border #E1E3E5, 8 px radius (0.08 in), 0.2 in inner padding; panel sections use #F7F7F7 fill with no border. Only ONE emphasised element per slide may have a coloured border (gold 500, 2 pt).
- Icons: simple outlined line icons, 1.5 pt stroke, AE Black 700 (or gold 600), 0.35 in; no emoji in the deck (use drawn check / cross / circle / alert icons for verdicts).

SLIDE-BY-SLIDE
1) Hook (dark): left 55%: title "When Seeing Is No Longer Believing" (Inter 54 pt white), gold rule, tagline in gold 400. Large HAQEEQ حقيق wordmark with logo top-left. Stat block bottom-left: "7 in 10" (gold 400, 96 pt) + the sentence in white 20 pt + source 14 pt AE Black 300. Right 40%: the fictional "family chat" mock inside a clean phone outline with the label "Illustrative" (white 14 pt, outlined tag).
2) Gap: three equal stat cards across the top. Each: big number (54 pt; "96%" AE Green 700, "1 in 3" AE Red 700, "About half" Gold 700), label 18 pt, and a thin proportion bar beneath (track #E1E3E5, fill in the semantic colour: 96%, 33%, 50%). Below: a 3-step chevron strip Forward → Check → Response (first two in #F7F7F7 with AE Black text, "Response" outlined in gold = the missing step). One-sentence takeaway in 20 pt with "The missing step:" in Gold 700 bold. Source line 14 pt.
3) Demo: left: 3 numbered steps in a vertical list (gold numbered circles). Right: four verdict cards in a 2x2 grid; each card has a 6 px left border in its verdict colour, a drawn icon, the verdict name (20 pt bold) and one-line meaning (18 pt); fill = the tint. Bottom: "Play demo" button (gold 600 fill, white text) and tag "Prototype · test account · sample content".
4) What is built: top: 5 chevron boxes (flow) in #F7F7F7, text 18 pt. Middle: three columns as cards with a status chip each — WORKING (AE Green 700 text on #E4F4E7), CONTEXT DATA (Gold 700 text on #F9F7ED), SIMULATED / PLANNED (AE Black 600 text on #F7F7F7). Bottom: one full-width "honesty strip" with a 4 pt gold left border: four short statements separated by thin dividers, 16-18 pt. Privacy line 14 pt.
5) Business Model Canvas — rebuild as the STANDARD 9-block canvas (see layout below). Title 36 pt "A pilot a public entity can actually run".
6) 90-day pilot: top row: team cards (placeholders amber). Middle: a horizontal TIMELINE chart: one axis 0-90 days with three phase bars (0-30, 31-60, 61-90) in Gold 300 / Gold 500 / Gold 700 with white or black text for contrast, milestone dots below each bar; under it, a 4-column table (Phase · Work · Owner · Proposed measure) in a clean light table: header row AE Black 900 fill + white text, rows alternating white / #F7F7F7, 1 pt row dividers. A banner "Proposed — depends on a sponsoring entity, written channel terms and a privacy/security review" (Camel Yellow 100 tint #FDF4C8, dark text).
7) Ask (dark): centred logo + HAQEEQ, tagline in gold 400, the ask in white 32 pt, footer note 16 pt AE Black 300.

BUSINESS MODEL CANVAS LAYOUT (slide 5) — standard arrangement on a 5-column x 3-row grid inside the content area, 1 pt borders #E1E3E5, white cards, small caps header 14 pt Gold 700 with a tiny line icon, content 16-18 pt:
  | Key Partners (col 1, rows 1-2) | Key Activities (col 2, row 1) | Value Proposition (col 3, rows 1-2, fill Gold 50 #F9F7ED, 2 pt gold border = the emphasised block) | Customer Relationships (col 4, row 1) | Customer Segments (col 5, rows 1-2) |
  |                                | Key Resources (col 2, row 2)  |                                                                            | Channels (col 4, row 2)               |                                    |
  | Cost Structure (cols 1-3, row 3)                                | Revenue Streams — options to validate in the pilot (cols 4-5, row 3)  |
Below the canvas, one full-width "Pilot measure" bar (AE Black 900 fill, white text, gold label): "Pilot measure: confirmed reports answered with an official decision within 24 hours — target [TEAM]".
Keep the existing text for each block (partners all labelled "proposed"). Mark the three callouts (Buyer, Funding options, Biggest risk) as small gold tags attached to the relevant blocks, not as extra boxes. Keep every [TEAM] placeholder as an amber (#F29F0E) highlighted chip.

CHARTS AND DATA VISUALS (professional rules)
- Use native, editable PowerPoint charts or shapes only. One message per chart; the slide title states the takeaway.
- Chart colours: single series = AE Gold 500 (#B68A35) or the semantic colour of the meaning; categorical series in this order: Gold 500, Sea Blue 700 #0073AB, AE Green 600 #3F8E50, Desert Orange 500 #EB5F24, Slate 500 #64748B. Max 4 colours per chart.
- No 3D, no shadows, no gradients, no pie charts with more than 3 slices; prefer horizontal bars, a simple timeline, or a ring for a single percentage.
- Label values directly on the bars/segments (no legend if avoidable); remove gridlines or use only #E1E3E5 hairlines; axis text 14 pt AE Black 600; thousands separators; units in the title or axis label; source line 14 pt under every chart with the survey name and date.
- Every chart needs a plain-text alt description in the shape's alt text.

ACCESSIBILITY / QUALITY RULES
- Body text contrast >= 4.5:1; large text >= 3:1; never put gold-500 text on white.
- Minimum font size 14 pt; titles never wrap to more than 2 lines.
- Consistent margins, equal card heights per row, nothing touching the slide edge, no overlapping shapes, no text clipped (check the PDF export).
- Arabic text: RTL, right-aligned, Noto Kufi Arabic / Alexandria; keep Latin numerals as in the current deck.
- Keep the speaker notes and timings exactly as they are now.

DELIVERABLES: HAQEEQ-Pitch-Deck-v2.pptx, HAQEEQ-Pitch-Deck-v2.pdf, and a short list of the fonts used (so I can install Roboto, Inter, Noto Kufi Arabic and Alexandria on the presenting laptop). Render each slide to an image and check for overlaps, clipped text and low contrast BEFORE you finish; fix anything you find.
```

## After Replit finishes
1. **Install the fonts** (Roboto, Inter, Noto Kufi Arabic, Alexandria — all free on Google Fonts) on the laptop that will present. PowerPoint cannot always embed them.
2. Submit the **PDF** on the portal; keep the PPTX for the live pitch.
3. Compare each slide against the checklist: light background, gold used sparingly, verdict colours consistent, canvas in the standard layout, nothing below 14 pt.
