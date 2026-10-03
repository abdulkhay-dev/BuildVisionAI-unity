"""XY-DSXB-03A back extension (hydraulic exerciser). Patient sits facing +z; lumbar roller behind the seat, the lever
pivots at chest height on +x and arches up and back to an upper roller behind the shoulders; footplate in front."""
from k9lib import *
d = K("xy-dsxb-03a", [700, 1000, 1250], dict(EX_MATS))
CX = 350
foot(d, "foot-f", 185, 515, 715)
foot(d, "foot-r", 110, 590, 95)
d.cyl("post", [CX, 40, 715], [CX, 425, 690], TUBE, "frame")
d.sweep("arch", [[CX, 420, 560], [CX, 400, 400], [CX, 230, 230], [CX, 60, 135]], [70, 50], "frame", shape="oval", bend=160)
d.box("seat-plate", [CX - 90, 418, 360, CX + 90, 432, 690], "dark", r=4)
seat(d, "seat", CX, 330, 730, 330, 410, 432)
# footplate on the floor in front, joined to the front foot, two small wheels under its front
d.bar("fp-link", [CX, 35, 715], [CX, 30, 790], [60, 24], "frame", r=6)
d.slab("fplate", "top", rpoly([(CX - 215, 760), (CX + 215, 760), (CX + 225, 995), (CX - 225, 995)], 45), [8, 34], "cap", r=8)
d.box("fplate-rib", [CX - 185, 33, 785, CX + 185, 39, 791], "rubber#2a2c30", r=2, repeat=rep(9, [0, 0, 22]))
d.wheel("fp-wheel-l", [CX - 170, 24, 960], 48, "cap", d2=22, axis="x")
d.wheel("fp-wheel-r", [CX + 170, 24, 960], 48, "cap", d2=22, axis="x")
# lumbar roller on a cream U behind the seat
d.tube("pad-frame", [[CX - 110, 425, 380], [CX - 110, 425, 290], [CX - 110, 790, 255], [CX + 110, 790, 255],
                     [CX + 110, 425, 290], [CX + 110, 425, 380]], 36, "frame", bend=50)
d.box("lpad", [CX - 160, 700, 265, CX + 160, 850, 365], "blue", r=45)
d.box("lpad-pipe", [CX - 154, 708, 261, CX + 154, 719, 369], "pipe", r=4)
for nm, x0, x1 in (("l", CX - 170, CX - 160), ("r", CX + 160, CX + 170)):
    d.cyl(f"lpad-cap-{nm}", [x0, 775, 315], [x1, 775, 315], 70, "cap")
logo(d, "logo", CX, 775, 365.5, h=28)
N_LEV = len(d.d["parts"])
# --- lever: pivot at chest height on +x, arm up and back over to the upper roller
PX, PY, PZ = 620, 810, 470
d.bar("axle-arm", [CX + 110, 790, 255], [CX + 110, PY, PZ], [30, 30], "frame", r=5)
d.cyl("axle", [CX + 110, PY, PZ], [PX + 30, PY, PZ], 30, "chrome")
d.cyl("hub", [PX - 40, PY, PZ], [PX + 40, PY, PZ], 70, "frame")
d.cyl("hub-cap", [PX + 40, PY, PZ], [PX + 62, PY, PZ], 56, "plastic#f4f4f2")
d.cyl("hub-cap-in", [PX - 62, PY, PZ], [PX - 40, PY, PZ], 56, "plastic#f4f4f2")
RY, RZ = 1185, 190
d.tube("arm", [[PX, PY, PZ], [PX, 1080, PZ - 30], [PX - 20, 1200, 330], [PX - 60, RY, RZ], [CX + 175, RY, RZ]], 50, "frame", bend=150)
roller(d, "roll", [CX - 175, RY, RZ], [CX + 175, RY, RZ], dia=125)
# hydraulic cylinder from a stub under the pivot down-back to the seat frame
d.bar("stub", [PX, PY, PZ], [PX - 20, PY - 90, PZ + 40], [34, 30], "frame", r=5)
hydro(d, "hyd", [CX + 120, 430, 420], [PX - 20, PY - 90, PZ + 40], body=0.55)
# (review 2026-10-03) the photo has the pivot, the arm and the cylinder on the patient's RIGHT: mirror the lever
# group about the middle of the width (roller: its two caps mirror onto each other)
W_ = d.d["size"][0]
def _mx(x): return W_ - x
for p in d.d["parts"][N_LEV:]:
    for k in ("from", "to", "at"):
        if k in p: p[k][0] = _mx(p[k][0])
    if "path" in p:
        for q in p["path"]: q[0] = _mx(q[0])
    if "box" in p:
        b = p["box"]; b[0], b[3] = _mx(b[3]), _mx(b[0])
    assert "rot" not in p and "sections" not in p and "profile" not in p, p["id"]
d.save()
