"""Shared helpers: load the local asset registry and canonical scenario strings (CONTRACT section 5)."""
import json
import os

from _supa import ROOT

A = os.path.join(ROOT, "assets")

# exact `detail` strings from CONTRACT section 5
D_EXPL = "Fake: 'explosions in Downtown Dubai' image"
D_ALT = "Altered: public holiday notice with a fake date"
D_FINE = "Scam: 'Dubai Police fine — pay now via link'"
D_BURJ = "Fake: AI video of Burj Khalifa collapsing"
D_EID = "Scam: 'Emirates ID suspended — verify OTP'"
D_MOHRE = "Matches official MOHRE announcement"
D_WKND = "Matches official weekend schedule notice"

KNOWN_FAKES = [
    dict(id="explosions_downtown", title="Explosions in Downtown Dubai (fake image)", detail=D_EXPL, file="fakes/explosions_downtown.png"),
    dict(id="burj_collapse", title="Burj Khalifa collapse (fake / AI video still)", detail=D_BURJ, file="fakes/burj_collapse.png"),
]


def official_registry():
    return json.load(open(os.path.join(A, "official", "registry.json"), encoding="utf-8"))


def read(rel):
    with open(os.path.join(A, rel), "rb") as f:
        return f.read()
