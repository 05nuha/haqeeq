# Haqeeq (حقيق) — "so the truth can prove itself"

**UAE Hackathon 2026 · Challenge 40 "Building Trust in Digital Content" (Cyber Security Council / TDRA / DESC)**

Citizens forward a suspicious "official" image or message to a WhatsApp number and get an **Arabic verdict in seconds**:

- ✅ **genuine** — matches a registered official post
- 🔴 **altered** — doctored version of an official post
- 🔴 **scam risk** — message carries scam indicators
- ⚪ **unverified** — never issued by any official source

Every forward also lands on a **government dashboard** ("National Trust Control Center"): a live UAE map of where fakes are being reported, a step-by-step forensic view, trending fakes, and a one-click **Push official correction** button.

**Live:** [haqeeq.vercel.app](https://haqeeq.vercel.app)

## How the verification engine works

WhatsApp strips C2PA/metadata signatures and recompresses every image, so signature-based provenance dies in transit. Haqeeq instead fingerprints content:

1. **Match** — 64-bit perceptual hash (pHash) of the incoming image vs a registry of genuine official posts; smallest Hamming distance wins. No close match → *unverified*.
2. **Tamper check** — pixel-level diff (256×256 greyscale, changed-pixel fraction) against the matched original. A recompressed screenshot passes as *genuine*; a changed date or amount flags *altered*.
3. **Crop search** — phone screenshots with status/browser bars still match the underlying post.
4. **Text** — bilingual (Arabic/English) rule-based scam indicators, upgraded by a Gemini analysis when available.

## Stack

- **Next.js** dashboard + **Python serverless functions** on Vercel
- **Supabase** — Postgres, Storage, Realtime
- **Meta WhatsApp Cloud API** webhook (Twilio fallback)
- **Open data:** Bayanat government-entity registry, Dubai Pulse organisation/area registers, FCSC population estimates (per-capita risk map) — see `DATA_SOURCES.md`

## Repo guide

| Path | What it is |
| --- | --- |
| `app/`, `components/`, `lib/` | Next.js dashboard |
| `api/` | serverless functions — WhatsApp webhooks, engine endpoints |
| `engine/` | pHash matching + pixel tamper check |
| `scripts/` | registry seeding, open-data loaders, demo seeding, e2e tests |
| `supabase/` | schema & storage setup |
| `legacy-flask/` | original Flask reference implementation |
| `docs/` | hackathon planning, deck content & AI-session handoff notes |

Built in 3 days by a team of 2 at UAE Hackathon 2026 (Dubai · HCT).
