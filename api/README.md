# api/ — Python functions (Vercel)

NOTE: vercel.com docs were unreachable from the build container, so this follows Vercel's documented
conventions from memory; verify on first deploy.

Routing: Next.js framework preset serves `app/`; any `api/*.py` file exporting a WSGI `app` becomes a
Python function at `/api/<name>`. Next.js has no `app/api/*` routes, so there is no conflict.
Three thin entry files (`whatsapp.py`, `correct.py`, `health.py`) each re-export the single Flask app in
`api/_lib/app.py` (underscore dirs are not deployed as functions). Because each file is its own URL,
Flask sees the real path (`/api/whatsapp`), no rewrites needed.

Importing `engine/`: each entry adds the repo root and `api/` to `sys.path`; `vercel.json`
`functions."api/*.py".includeFiles = "{engine/**,api/_lib/**}"` bundles them. Python 3.12 via `.python-version`;
deps from root `requirements.txt` (no scipy/imagehash; keeps bundle far below the 250 MB limit). `maxDuration` 15.

Design notes
- Audio/video/other media: reply Arabic "coming soon", stored as kind `text`, verdict `unverified`
  (schema only allows image/text/link).
- Bodies containing a URL are stored as kind `link` (check_text still runs).
- DB failures are logged; the citizen still gets a reply.
- Local: `python -m api.dev` serves on 127.0.0.1:5328. Tests: `python -m pytest api/tests`.
