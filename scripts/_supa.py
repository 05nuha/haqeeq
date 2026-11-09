"""Tiny Supabase helper (PostgREST + Storage over plain `requests`, service-role key). Shared by scripts/*.py.

Env: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY (also read from ./.env if present). With dry_run=True nothing is sent.
"""
import json
import mimetypes
import os
import sys

import requests

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
BUCKET = "media"


def load_env():
    p = os.path.join(ROOT, ".env")
    if os.path.exists(p):
        for ln in open(p, encoding="utf-8"):
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, v = ln.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


class Supa:
    def __init__(self, dry_run=False):
        load_env()
        self.dry = dry_run
        self.url = os.environ.get("SUPABASE_URL", "https://YOUR-PROJECT.supabase.co").rstrip("/")
        self.key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        if not dry_run and (not self.key or "YOUR-PROJECT" in self.url):
            sys.exit("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (env or .env), or use --dry-run.")
        self.h = {"apikey": self.key, "Authorization": f"Bearer {self.key}"}

    def _log(self, what, n=None):
        print(f"[dry-run] {what}" + (f" ({n} rows)" if n is not None else ""))

    def _check(self, r):
        if r.status_code >= 300:
            sys.exit(f"HTTP {r.status_code} {r.request.method} {r.request.url}\n{r.text[:500]}")
        return r

    def upsert(self, table, rows, on_conflict=None, chunk=500):
        if not rows:
            return
        if self.dry:
            self._log(f"POST /rest/v1/{table}?on_conflict={on_conflict} (upsert) sample={json.dumps(rows[0], ensure_ascii=False)[:300]}", len(rows))
            return
        q = f"?on_conflict={on_conflict}" if on_conflict else ""
        h = {**self.h, "Content-Type": "application/json", "Prefer": "resolution=merge-duplicates,return=minimal"}
        for i in range(0, len(rows), chunk):
            self._check(requests.post(f"{self.url}/rest/v1/{table}{q}", headers=h, data=json.dumps(rows[i:i + chunk]), timeout=60))

    def insert(self, table, rows, chunk=200):
        if not rows:
            return
        if self.dry:
            self._log(f"POST /rest/v1/{table} (insert) sample={json.dumps(rows[0], ensure_ascii=False)[:400]}", len(rows))
            return
        h = {**self.h, "Content-Type": "application/json", "Prefer": "return=minimal"}
        for i in range(0, len(rows), chunk):
            self._check(requests.post(f"{self.url}/rest/v1/{table}", headers=h, data=json.dumps(rows[i:i + chunk]), timeout=60))

    def delete(self, table, filt):
        """filt: PostgREST filter string, e.g. 'id=gt.0' (a filter is mandatory for DELETE)."""
        if self.dry:
            self._log(f"DELETE /rest/v1/{table}?{filt}")
            return
        self._check(requests.delete(f"{self.url}/rest/v1/{table}?{filt}", headers={**self.h, "Prefer": "return=minimal"}, timeout=60))

    def select(self, table, query="select=*"):
        if self.dry:
            self._log(f"GET /rest/v1/{table}?{query}")
            return []
        return self._check(requests.get(f"{self.url}/rest/v1/{table}?{query}", headers=self.h, timeout=60)).json()

    def upload(self, path_in_bucket, local_file):
        ct = mimetypes.guess_type(local_file)[0] or "application/octet-stream"
        if self.dry:
            self._log(f"POST /storage/v1/object/{BUCKET}/{path_in_bucket} <- {os.path.relpath(local_file, ROOT)} ({ct}, x-upsert)")
            return
        with open(local_file, "rb") as f:
            self._check(requests.post(f"{self.url}/storage/v1/object/{BUCKET}/{path_in_bucket}",
                                      headers={**self.h, "Content-Type": ct, "x-upsert": "true"}, data=f.read(), timeout=120))
