"""Tiny Supabase client (PostgREST + Storage) over plain `requests`."""
import os
import time

import requests

TIMEOUT = 5
CACHE_TTL = 60
_cache = {}          # key -> (expires, value)
_image_cache = {}    # storage path -> bytes


def _base():
    return os.environ.get("SUPABASE_URL", "").rstrip("/")


_KEY_NAMES = ("SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SECRET_KEY", "SUPABASE_SERVICE_KEY",
              "SUPABASE_SERVICE_ROLE", "SUPABASE_KEY")


def service_key():
    for n in _KEY_NAMES:
        v = os.environ.get(n, "").strip()
        if v:
            return v
    return ""


def _headers(extra=None):
    key = service_key()
    h = {"apikey": key}
    if key.startswith("eyJ"):          # legacy JWT service_role key; new sb_secret_ keys use apikey only
        h["Authorization"] = "Bearer " + key
    if extra:
        h.update(extra)
    return h


def configured():
    return bool(_base() and service_key())


def select(table, params=None):
    r = requests.get(f"{_base()}/rest/v1/{table}", params=params or {"select": "*"},
                     headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def insert(table, row):
    r = requests.post(f"{_base()}/rest/v1/{table}", json=row,
                      headers=_headers({"Prefer": "return=representation"}), timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def upsert(table, row, on_conflict=None):
    params = {"on_conflict": on_conflict} if on_conflict else None
    r = requests.post(f"{_base()}/rest/v1/{table}", json=row, params=params,
                      headers=_headers({"Prefer": "return=representation,resolution=merge-duplicates"}),
                      timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()


def upload(path, data, content_type="image/jpeg"):
    r = requests.post(f"{_base()}/storage/v1/object/media/{path}", data=data,
                      headers=_headers({"Content-Type": content_type, "x-upsert": "true"}),
                      timeout=TIMEOUT)
    r.raise_for_status()
    return path


def public_url(path):
    return f"{_base()}/storage/v1/object/public/media/{path}"


def download(path):
    """Download a storage object (public bucket, but we send the key anyway)."""
    r = requests.get(f"{_base()}/storage/v1/object/media/{path}", headers=_headers(), timeout=TIMEOUT)
    r.raise_for_status()
    return r.content


def load_image(path):
    """Per-instance cache of image bytes (official registry images)."""
    if path not in _image_cache:
        _image_cache[path] = download(path)
    return _image_cache[path]


def cached(table):
    """Cached full-table select (registry, known_fakes, entities) for ~60 s."""
    now = time.time()
    hit = _cache.get(table)
    if hit and hit[0] > now:
        return hit[1]
    try:
        rows = select(table)
    except Exception:
        if hit:           # serve stale rather than fail
            return hit[1]
        raise
    _cache[table] = (now + CACHE_TTL, rows)
    return rows


def clear_cache():
    _cache.clear()
    _image_cache.clear()
