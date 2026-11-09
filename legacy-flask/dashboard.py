"""
dashboard.py  —  OWNER: Person B (CIT)
The government-facing control center. It only READS the shared database (plus its own
small 'corrections' table), so you can build and style it without touching the engine.

Routes:
  /dashboard          the control-center page (templates/dashboard.html)
  /api/reports        live data the page polls every 2 seconds
  /api/corrections    list of fakes the government has already corrected
  /api/correct        POST: mark a trending fake as corrected ("push correction")
  /media/<file>       serves forwarded images and official images to the forensic view
"""
import os
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, send_from_directory, abort
from db import get_conn

dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")

BASE_DIR = os.path.abspath(os.getcwd())
OFFICIAL_DIR = os.path.join(BASE_DIR, "official_posts")


def _init_corrections():
    conn = get_conn()
    conn.execute("""CREATE TABLE IF NOT EXISTS corrections (
        detail TEXT PRIMARY KEY,
        ts TEXT,
        message TEXT
    )""")
    conn.commit()
    conn.close()


_init_corrections()


def _media_url(path):
    if not path:
        return None
    return "/media/" + os.path.basename(path)


@dashboard_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@dashboard_bp.route("/api/reports")
def api_reports():
    conn = get_conn()
    rows = conn.execute("""
        SELECT r.*, o.title AS official_title, o.issuer AS official_issuer,
               o.image_path AS official_image
        FROM reports r
        LEFT JOIN official_posts o ON o.id = r.matched_id
        ORDER BY r.id DESC LIMIT 300
    """).fetchall()
    conn.close()
    out = []
    for r in rows:
        d = dict(r)
        d["image_url"] = _media_url(d.get("image_path"))
        d["official_url"] = _media_url(d.get("official_image"))
        out.append(d)
    return jsonify(out)


@dashboard_bp.route("/api/corrections")
def api_corrections():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM corrections").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@dashboard_bp.route("/api/correct", methods=["POST"])
def api_correct():
    data = request.get_json(force=True) or {}
    detail = data.get("detail")
    if not detail:
        return jsonify({"ok": False}), 400
    message = data.get("message") or "Official clarification issued by the UAE Government Media Office."
    conn = get_conn()
    conn.execute("INSERT OR REPLACE INTO corrections (detail, ts, message) VALUES (?,?,?)",
                 (detail, datetime.utcnow().isoformat(timespec="seconds"), message))
    # How many citizens forwarded this fake (they would receive the correction).
    n = conn.execute("SELECT COUNT(*) FROM reports WHERE detail = ?", (detail,)).fetchone()[0]
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "recipients": n})


@dashboard_bp.route("/media/<path:filename>")
def media(filename):
    name = os.path.basename(filename)          # no path tricks
    if os.path.exists(os.path.join(OFFICIAL_DIR, name)):
        return send_from_directory(OFFICIAL_DIR, name)
    if name.startswith("incoming_") and os.path.exists(os.path.join(BASE_DIR, name)):
        return send_from_directory(BASE_DIR, name)
    abort(404)
