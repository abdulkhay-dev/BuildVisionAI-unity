"""XY-DSXB-02A chest / back (hydraulic exerciser). Patient sits facing +z; two upright levers beside the seat,
their tops bent inward with black grips; black ribbed footplate on the floor in front."""
from k9lib import *
d = K("xy-dsxb-02a", [800, 1000, 1350], dict(EX_MATS))
CX = 400
foot(d, "foot-r", 140, 660, 95)
# footplate on the floor in front, on a cream stem
d.slab("fplate", "top", rpoly([(CX - 250, 660), (CX + 250, 660), (CX + 260, 995), (CX - 260, 995)], 55), [0, 26], "cap", r=8)
d.box("fplate-rib", [CX - 220, 25, 690, CX + 220, 31, 698], "rubber#2a2c30", r=2, repeat=rep(14, [0, 0, 21]))
d.sweep("stem", [[CX, 410, 620], [CX, 300, 680], [CX, 60, 760], [CX, 40, 800]], [55, 45], "frame", shape="oval", bend=120)
d.sweep("spine", [[CX, 410, 450], [CX, 300, 330], [CX, 60, 130]], [60, 46], "frame", shape="oval", bend=120)
d.box("seat-plate", [CX - 90, 418, 360, CX + 90, 432, 680], "dark", r=4)
seat(d, "seat", CX, 330, 700, 330, 410, 432)
zf, BR = back(d, "back", CX, 540, 1345, 265, 290, 240, tilt=-7, rt=110)
logo(d, "logo", CX, 1160, zf, h=32, R=BR)
d.box("hinge", [CX - 50, 470, 235, CX + 50, 555, 320], "dark", r=10)
d.sweep("support", [[CX, 400, 420], [CX, 420, 230], [CX, 560, 205], rotx([CX, 1250, 205], -7, [CX, 540, 240])],
        [50, 35], "frame", shape="oval", bend=60)
# pivot shaft across under the seat, the two levers, their cylinders
PY, PZ = 260, 590
d.cyl("pivot", [CX - 330, PY, PZ], [CX + 330, PY, PZ], 40, "frame")
d.box("pivot-hub", [CX - 50, PY - 40, PZ - 40, CX + 50, PY + 40, PZ + 40], "frame", r=12)
d.bar("pivot-strut", [CX, PY, PZ], [CX, 410, 560], [40, 40], "frame", r=6)
for nm, s in (("l", -1), ("r", 1)):
    x = CX + s * 330
    d.cyl(f"lever-hub-{nm}", [x - 30, PY, PZ], [x + 30, PY, PZ], 70, "frame")
    # (review 2026-10-03) photo: the lever tops are short hooks bending OUTWARD and up (not inward over the shoulders)
    top = [[x, 1060, PZ + 60], [x + s * 12, 1180, PZ + 66], [x + s * 62, 1262, PZ + 72]]
    d.tube(f"lever-{nm}", [[x, PY, PZ], [x, 700, PZ + 40]] + top, 38, "frame", bend=80)
    d.tube(f"grip-{nm}", [[x, 960, PZ + 55]] + top, 46, "foam", bend=80)
    d.sphere(f"grip-end-{nm}", top[-1], 46, "cap", radii=[23, 23, 23])
    d.bar(f"lever-arm-{nm}", [x, PY, PZ], [x, PY - 30, PZ - 160], [40, 30], "frame", r=6)
    hydro(d, f"hyd-{nm}", [CX + s * 200, 60, 140], [x, PY - 30, PZ - 160], body=0.6, dia=44)
d.save()
