"""XY-DSXB-01A abdominal / back (hydraulic exerciser). Patient sits facing +z, lumbar pad behind,
the lever pivots at hip height on the patient's left (+x), arches over behind the back to a roller with two handles."""
from k9lib import *
d = K("xy-dsxb-01a", [650, 850, 1300], dict(EX_MATS, hub="plastic#f4f4f2"))
CX = 300
foot(d, "foot-f", 130, 470, 745)
foot(d, "foot-r", 70, 530, 95)
d.cyl("post", [CX, 40, 740], [CX, 425, 700], TUBE, "frame")
d.sweep("arch", [[CX, 420, 560], [CX, 400, 400], [CX, 230, 230], [CX, 60, 135]], [70, 50], "frame", shape="oval", bend=160)
d.box("seat-plate", [CX - 90, 418, 360, CX + 90, 432, 700], "dark", r=4)
seat(d, "seat", CX, 330, 745, 330, 410, 432)
# lumbar pad on a cream U behind the seat
d.tube("pad-frame", [[CX - 110, 425, 380], [CX - 110, 425, 290], [CX - 110, 700, 260], [CX + 110, 700, 260],
                     [CX + 110, 425, 290], [CX + 110, 425, 380]], 36, "frame", bend=50)
d.box("lpad", [CX - 155, 590, 270, CX + 155, 770, 360], "blue", r=36)
d.box("lpad-pipe", [CX - 150, 600, 266, CX + 150, 611, 364], "pipe", r=4)
d.box("lpad-back", [CX - 140, 610, 262, CX + 140, 755, 272], "frame", r=6)
logo(d, "logo", CX, 690, 360.5, h=28)
N_LEV = len(d.d["parts"])
# --- lever: pivot hub at hip height on +x, arm back along the side, up behind the back, over to the roller
PX, PY, PZ = 590, 690, 470
d.cyl("axle", [CX + 110, PY, PZ], [PX + 30, PY, PZ], 30, "chrome")
d.bar("axle-arm", [CX + 110, 700, 260], [CX + 110, PY, PZ], [30, 30], "frame", r=5)
d.cyl("hub", [PX - 40, PY, PZ], [PX + 40, PY, PZ], 70, "frame")
d.cyl("hub-cap", [PX + 40, PY, PZ], [PX + 62, PY, PZ], 56, "hub")
d.cyl("hub-cap-in", [PX - 62, PY, PZ], [PX - 40, PY, PZ], 56, "hub")
RY, RZ = 905, 300      # (review) photo: the roller rests just above the lumbar pad, over the shoulders
d.tube("arm", [[PX, PY, PZ], [PX, 790, 400], [PX - 50, RY, RZ + 10], [CX + 175, RY, RZ]], 50, "frame", bend=120)
roller(d, "roll", [CX - 130, RY, RZ], [CX + 130, RY, RZ], dia=120, cap=False)
for nm, s in (("l", -1), ("r", 1)):
    xb = CX + s * 155
    d.box(f"roll-end-{nm}", [xb - 25, RY - 62, RZ - 62, xb + 25, RY + 62, RZ + 62], "cap", r=20)
    d.cyl(f"roll-disc-{nm}", [xb + s * 25, RY, RZ], [xb + s * 29, RY, RZ], 40, "metal#c8cbcf")
    # black handle: up from the end block, over forward, its grip end down above the shoulder
    d.sweep(f"handle-{nm}", [[xb, RY + 40, RZ], [xb, 1200, RZ - 30], [xb, 1295, RZ + 50], [xb, 1190, RZ + 140]],
            [42, 26], "foam", shape="rect", r=10, bend=70)
    grip(d, f"grip-{nm}", [xb, 1235, RZ + 120], [xb, 1110, RZ + 155], dia=48)
# hydraulic cylinder: from the arm near the pivot down-back to the frame under the seat
hydro(d, "hyd", [CX + 150, 440, 330], [PX - 10, PY - 5, PZ - 90], body=0.55)
# (review 2026-10-03) the photo has the pivot, the arm and the cylinder on the patient's RIGHT: mirror the lever
# group about the middle of the width
def _mx(x): return 650 - x
for p in d.d["parts"][N_LEV:]:
    for k in ("from", "to", "at"):
        if k in p: p[k][0] = _mx(p[k][0])
    if "path" in p:
        for q in p["path"]: q[0] = _mx(q[0])
    if "box" in p:
        b = p["box"]; b[0], b[3] = _mx(b[3]), _mx(b[0])
    assert "rot" not in p and "sections" not in p, p["id"]
d.save()
