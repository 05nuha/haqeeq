"""CLI: python -m engine.check <image> [--registry-dir assets/official]"""
import argparse
import os

from .phash import phash
from .image_check import verify_image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--registry-dir", default="assets/official")
    a = ap.parse_args()
    reg = []
    for fn in sorted(os.listdir(a.registry_dir)):
        stem, ext = os.path.splitext(fn)
        if ext.lower() in (".png", ".jpg", ".jpeg"):
            p = os.path.join(a.registry_dir, fn)
            with open(p, "rb") as f:
                reg.append({"id": stem, "title": stem, "issuer": "registry", "phash": phash(f.read()), "image_path": p})

    def load(p):
        with open(p, "rb") as f:
            return f.read()

    with open(a.image, "rb") as f:
        r = verify_image(f.read(), reg, load)
    print(f"verdict:     {r['verdict']}\nmatched_id:  {r['matched_id']}\ndistance:    {r['distance']}\n"
          f"changed_pct: {r['changed_pct']}\ndetail:      {r['detail']}")


if __name__ == "__main__":
    main()
