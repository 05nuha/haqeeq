"""Seed ~55 sample reports over the last 60 minutes (seeded=true) so the dashboard looks alive.

    python scripts/demo_seed.py [--n 55] [--seed 7] [--dry-run]

Same scenarios / weights / places as legacy-flask/demo_seed.py (CONTRACT section 5). Requires seed_registry.py
to have run first (matched_id references official_posts). Honest framing: this is SIMULATED background data
(reports.seeded = true); say so in the pitch.
"""
import argparse
import io
import os
import random
from datetime import datetime, timedelta, timezone

from PIL import Image

from _supa import Supa
from _registry import A, official_registry, read, D_EXPL, D_ALT, D_FINE, D_BURJ, D_EID, D_MOHRE, D_WKND

PLACES = ["Dubai"] * 8 + ["Sharjah"] * 5 + ["Abu Dhabi"] * 4 + ["Ajman"] * 3 + ["Al Ain"] * 2 + ["Ras Al Khaimah"] * 2 + ["Fujairah"] + ["Umm Al Quwain"]
DUBAI_AREAS = ["Business Bay", "Marsa Dubai", "Al Barsha", "Bur Dubai", "Jumeirah", "Mirdif", "Al Satwa", "Burj Khalifa", "Al Warqa First", "Hor Al Anz"]

# (kind, verdict, detail, weight, matched_id, image_path)
SCENARIOS = [
    ("image", "unverified", D_EXPL, 14, None, "fakes/explosions_downtown.png"),
    ("image", "altered", D_ALT, 8, "public_holiday_notice", "incoming/seed-public_holiday_doctored.png"),
    ("text", "scam_risk", D_FINE, 7, None, None),
    ("image", "unverified", D_BURJ, 6, None, "fakes/burj_collapse.png"),
    ("text", "scam_risk", D_EID, 4, None, None),
    ("image", "genuine", D_MOHRE, 6, "mohre_announcement", "official/mohre_announcement.png"),
    ("image", "genuine", D_WKND, 4, "weekend_schedule_notice", "official/weekend_schedule_notice.png"),
]
AI_REASONS = {D_FINE: "رسالة تنتحل صفة الشرطة وتطلب دفع غرامة عبر رابط مجهول — مؤشر احتيال.",
              D_EID: "رسالة تدّعي تعليق الهوية الإماراتية وتطلب رمز التحقق — أسلوب احتيال معروف."}


def real_altered_heat():
    """Run the real engine on the doctored asset so the seeded heat-map is a genuine tamper map."""
    try:
        from engine import phash, verify_image
        reg = [dict(p, phash=phash(read(f"official/{p['id']}.png")), image_path=f"official/{p['id']}.png") for p in official_registry()]
        r = verify_image(read("doctored/public_holiday_notice_doctored_date.png"), reg, lambda p: read(p))
        if r["verdict"] == "altered" and r.get("heat"):
            return r["heat"], r["changed_pct"], r["distance"]
    except Exception as e:  # engine optional
        print("note: engine heat unavailable:", e)
    heat = [[0.0] * 16 for _ in range(16)]
    for y in (10, 11):
        for x in range(3, 13):
            heat[y][x] = 0.6
    return heat, 0.9, 2


def sender(rng):
    ph = "+97150" + "".join(str(rng.randint(0, 9)) for _ in range(7))
    return ph[:6] + "•••" + ph[-3:]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--n", type=int, default=55); ap.add_argument("--seed", type=int)
    ap.add_argument("--dry-run", action="store_true"); a = ap.parse_args()
    rng = random.Random(a.seed)
    s = Supa(a.dry_run)
    # thumbnails the dashboard can show for altered rows (not in the registry bucket paths)
    s.upload("incoming/seed-public_holiday_doctored.png", os.path.join(A, "doctored", "public_holiday_notice_doctored_date.png"))
    heat, pct0, dist0 = real_altered_heat()
    weighted = [sc for sc in SCENARIOS for _ in range(sc[3])]
    now = datetime.now(timezone.utc)
    rows = []
    for _ in range(a.n):
        kind, verdict, detail, _w, matched, img = rng.choice(weighted)
        emirate = rng.choice(PLACES)
        r = dict(ts=(now - timedelta(minutes=rng.uniform(0, 58))).isoformat(timespec="seconds"), sender_masked=sender(rng),
                 kind=kind, verdict=verdict, matched_id=matched, emirate=emirate, detail=detail, image_path=img, seeded=True,
                 area=rng.choice(DUBAI_AREAS) if emirate == "Dubai" and rng.random() < .7 else None,
                 distance=None, changed_pct=None, heat=None, ai_reason=None, ai_used=False)
        if verdict == "genuine":
            r.update(distance=rng.randint(0, 6), changed_pct=round(rng.uniform(0, 0.02), 3))
        elif verdict == "altered":
            r.update(distance=min(12, max(0, dist0 + rng.randint(-1, 3))), changed_pct=round(max(0.05, pct0 * rng.uniform(.8, 1.2)), 3),
                     heat=[[round(min(1.0, max(0.0, v * rng.uniform(.85, 1.15))), 3) for v in row] for row in heat])
        elif verdict == "unverified":
            r.update(distance=rng.randint(24, 36))
        elif verdict == "scam_risk":
            r.update(ai_used=rng.random() < .5)
            if r["ai_used"]:
                r["ai_reason"] = AI_REASONS[detail]
        rows.append(r)
    rows.sort(key=lambda x: x["ts"])
    s.insert("reports", rows)
    from collections import Counter
    print(f"seeded {len(rows)} reports:", dict(Counter(r["verdict"] for r in rows)))


if __name__ == "__main__":
    main()
