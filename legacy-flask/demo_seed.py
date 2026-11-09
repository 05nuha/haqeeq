"""
demo_seed.py  —  OWNER: Person B (CIT)
Fills the database with realistic sample reports spread over the last 60 minutes,
so the dashboard map, feed, chart and trending panel look alive.

    python demo_seed.py          add sample reports
    python demo_seed.py --clear  wipe ALL reports and corrections (fresh start)

In the pitch, be honest: "the background activity is simulated; the live forwards
you are about to see are real."
"""
import sys
import random
from datetime import datetime, timedelta
from db import init_db, get_conn

# Weighted so Dubai and Sharjah look like the hotspots of the fake "explosions" rumour.
PLACES = ["Dubai"] * 8 + ["Sharjah"] * 5 + ["Abu Dhabi"] * 4 + ["Ajman"] * 3 + \
         ["Al Ain"] * 2 + ["Ras Al Khaimah"] * 2 + ["Fujairah"] + ["Umm Al Quwain"]

SCENARIOS = [
    # (kind, verdict, detail, weight)
    ("image", "unverified", "Fake: 'explosions in Downtown Dubai' image", 14),
    ("image", "altered", "Altered: public holiday notice with a fake date", 8),
    ("text", "scam_risk", "Scam: 'Dubai Police fine — pay now via link'", 7),
    ("image", "unverified", "Fake: AI video of Burj Khalifa collapsing", 6),
    ("text", "scam_risk", "Scam: 'Emirates ID suspended — verify OTP'", 4),
    ("image", "genuine", "Matches official MOHRE announcement", 6),
    ("image", "genuine", "Matches official weekend schedule notice", 4),
]


def fake_sender():
    return "+97150•••" + str(random.randint(100, 999))


def seed(n=55):
    init_db()
    conn = get_conn()
    weighted = [s for s in SCENARIOS for _ in range(s[3])]
    now = datetime.utcnow()
    for _ in range(n):
        kind, verdict, detail, _w = random.choice(weighted)
        ts = now - timedelta(minutes=random.uniform(0, 58))
        conn.execute(
            """INSERT INTO reports (ts, sender, kind, verdict, matched_id, distance, emirate, detail, image_path)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (ts.isoformat(timespec="seconds"), fake_sender(), kind, verdict, None,
             random.randint(2, 9) if verdict in ("genuine", "altered") else random.randint(24, 36),
             random.choice(PLACES), detail, None),
        )
    conn.commit()
    conn.close()
    print(f"Added {n} sample reports.")


def clear():
    init_db()
    conn = get_conn()
    conn.execute("DELETE FROM reports")
    conn.execute("CREATE TABLE IF NOT EXISTS corrections (detail TEXT PRIMARY KEY, ts TEXT, message TEXT)")
    conn.execute("DELETE FROM corrections")
    conn.commit()
    conn.close()
    print("Cleared all reports and corrections.")


if __name__ == "__main__":
    if "--clear" in sys.argv:
        clear()
    else:
        seed()
