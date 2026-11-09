# Supabase setup, migrations and seeds

Run everything in the Supabase dashboard (SQL editor) or with the scripts. Order matters.

## 1. Migrations (SQL editor, paste in this order)
1. `supabase/migrations/0001_init.sql` — tables, RLS, Realtime publication, storage bucket `media`.
   (Further `0002_*.sql` only if the lead adds one.)

## 2. Seeds
| Step | With keys (preferred) | Without keys |
|---|---|---|
| Open data (entities, population, Dubai areas, dataset catalogue) | `python scripts/load_open_data.py` | paste `supabase/seed/open_data.sql` in the SQL editor |
| Official registry + known fakes (needs image upload + pHash) | `python scripts/seed_registry.py` | scripts only (Storage upload) |
| Demo background reports (~55, `seeded=true`) | `python scripts/demo_seed.py` | scripts only |
| Wipe demo data | `python scripts/demo_clear.py` (all) / `--seeded-only` | `delete from reports; delete from corrections;` |

Order: 0001 -> `load_open_data` -> `seed_registry` -> `demo_seed` (reports reference `official_posts` ids).
Run `seed_registry` again if the engine's pHash or the images change.

## 3. Scripts environment
```
pip install -r scripts/requirements.txt
export SUPABASE_URL=https://<project-ref>.supabase.co
export SUPABASE_SERVICE_ROLE_KEY=<service role key>   # or put both in ./.env (never commit)
python scripts/<script>.py --dry-run                   # prints what would be sent
```
Run from the repo root (scripts import the `engine` package). All scripts are idempotent.

## 4. Regenerating assets / open data
- `python scripts/make_assets.py` rebuilds every demo image (deterministic).
- `python scripts/fetch_open_data.py` re-downloads the raw government files; `python scripts/build_open_data.py [--land <xlsx>]` rebuilds the clean CSVs and `seed/open_data.sql`.
- Challenge-specific datasets from the organisers: `scripts/load_challenge_data.py` (stub) and the marked section in `DATA_SOURCES.md`.
