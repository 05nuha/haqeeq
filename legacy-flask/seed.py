"""
seed.py  —  OWNER: Person A (Cyber)
Run this ONCE (and again whenever you change the official images) to:
  1. create the database tables, and
  2. fingerprint every image in the official_posts/ folder into the registry.

Put your genuine announcement images in  official_posts/  named simply, e.g.
  new_weekend.png, golden_visa.png, holiday_notice.png
The file name (without extension) becomes the post id and title.
"""
import os
import imagehash
from PIL import Image
from db import init_db, get_conn

OFFICIAL_DIR = "official_posts"


def seed_official():
    init_db()
    conn = get_conn()
    conn.execute("DELETE FROM official_posts")
    count = 0
    for fname in sorted(os.listdir(OFFICIAL_DIR)):
        if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        path = os.path.join(OFFICIAL_DIR, fname)
        img = Image.open(path).convert("RGB")
        h8 = str(imagehash.phash(img, hash_size=8))
        h16 = str(imagehash.phash(img, hash_size=16))
        pid = os.path.splitext(fname)[0]
        conn.execute(
            """INSERT OR REPLACE INTO official_posts
               (id, title, issuer, date, hash8, hash16, image_path)
               VALUES (?,?,?,?,?,?,?)""",
            (pid, pid.replace("_", " ").title(), "UAE Government Media Office", "2026", h8, h16, path),
        )
        count += 1
    conn.commit()
    conn.close()
    print(f"Seeded {count} official posts into the registry.")


if __name__ == "__main__":
    seed_official()
