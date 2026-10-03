"""XY-DSXZ-02A hip abductor / adductor (hydraulic exerciser). Patient sits facing +z; two leg arms swing about
vertical pivots under the seat front, each carrying a white U cradle lined with light-blue pads at knee height.
As in the photo the patient's-right (-x) arm is swung out, the left (+x) arm points straight forward."""
import math
from k9lib import *
d = K("xy-dsxz-02a", [1100, 1100, 1350], dict(EX_MATS, box="plastic#f4f3ef"))
CX = 560
d.cyl("foot-f", [CX - 200, 45, 690], [CX + 200, 45, 690], TUBE, "frame")
for nm, x in (("l", CX - 225), ("r", CX + 225)):
    d.wheel(f"fwheel-{nm}", [x, 40, 690], 80, "cap", d2=42, axis="x")
    d.cyl(f"fhub-{nm}", [x - 23, 40, 690], [x + 23, 40, 690], 34, "metal#9a9ea4")
foot(d, "foot-r", CX - 250, CX + 250, 95)
d.cyl("post", [CX, 40, 690], [CX, 425, 640], TUBE, "frame")
d.sweep("spine", [[CX, 60, 140], [CX, 250, 230], [CX, 380, 380], [CX, 410, 560]], [60, 46], "frame", shape="oval", bend=150)
d.box("seat-plate", [CX - 90, 418, 330, CX + 90, 432, 640], "dark", r=4)
seat(d, "seat", CX, 300, 660, 340, 420, 432)
zf, BR = back(d, "back", CX, 540, 1345, 265, 290, 210, tilt=-7, rt=110)
logo(d, "logo", CX, 1165, zf, h=32, R=BR)
d.box("hinge", [CX - 50, 470, 205, CX + 50, 555, 290], "dark", r=10)
d.sweep("support", [[CX, 400, 420], [CX, 420, 200], [CX, 560, 175], rotx([CX, 1250, 175], -7, [CX, 540, 210])],
        [50, 35], "frame", shape="oval", bend=60)
# seat handles: cream tubes from behind the seat out to the sides, black grips pointing forward
for nm, s in (("l", -1), ("r", 1)):
    x = CX + s * 290
    d.tube(f"shandle-{nm}", [[CX, 520, 230], [x, 560, 250], [x, 590, 330]], 30, "frame", bend=60)
    grip(d, f"sgrip-{nm}", [x, 588, 320], [x, 600, 500], dia=40)
d.tube("shandle-root", [[CX, 420, 260], [CX, 520, 230]], 34, "frame")
# pivot block under the seat front, cylinder and chrome rods
d.box("pivot-block", [CX - 110, 300, 540, CX + 110, 380, 640], "frame", r=14)
hydro(d, "hyd", [CX, 120, 300], [CX, 320, 560], body=0.6)
# --- the two leg arms with their cradles
def cradle(nm, px, ang, L=380):
    """arm from the pivot (px) turned `ang` deg outward from straight forward (+ = towards +x)."""
    a = math.radians(ang)
    cx, cz = px + L * math.sin(a), 600 + L * math.cos(a)
    d.cyl(f"pv-{nm}", [px, 300, 600], [px, 385, 600], 60, "chrome")
    d.tube(f"arm-{nm}", [[px, 340, 600], [px + 0.55 * L * math.sin(a), 345, 600 + 0.55 * L * math.cos(a)],
                         [cx, 300, cz - 20]], 44, "frame", bend=80)
    R = rot("y", ang, [cx, 0, cz + 100])
    # white U shell (bottom + two walls), blue pads inside, two dark marks on each wall's outer face
    d.box(f"cb-{nm}", [cx - 115, 270, cz - 20, cx + 115, 300, cz + 210], "box", r=12, rot=R)
    # (review 2026-10-03) photo: the walls flare outward (~15 deg) and are higher at the seat end; thick rounded pads
    def wall_ol(z0, z1, yb, yb_hi, yf_hi, r):
        return rpoly([(z0, yb), (z1, yb), (z1, yf_hi), (z0, yb_hi)], r)
    for w, sx in (("o", -1), ("i", 1)):
        x0 = cx + sx * 115
        T = rot("z", -sx * 15, [x0, 285, cz])
        a_, b_ = sorted([x0, x0 - sx * 26])
        d.slab(f"cw-{w}-{nm}", "side", wall_ol(cz - 20, cz + 210, 270, 520, 430, 40), [a_, b_], "box", r=10, rot=T, rots=[R])
        xp = x0 - sx * 26
        a_, b_ = sorted([xp, xp - sx * 44])
        d.slab(f"cp-{w}-{nm}", "side", wall_ol(cz - 8, cz + 198, 300, 505, 418, 34), [a_, b_], "blue", r=18, rot=T, rots=[R])
        d.decal(f"cdot-{w}-{nm}", [x0 + sx * 0.6, 400, cz + 70], [12, 12], "right" if sx > 0 else "left", "dark",
                copies=[[0, 0, 60]], rot=T, rots=[R])
    d.box(f"cp-b-{nm}", [cx - 82, 298, cz - 10, cx + 82, 336, cz + 200], "blue", r=18, puff=5, rot=R)
cradle("r", CX + 70, 0, L=280)       # patient's left (+x): straight forward, in front of the seat
cradle("l", CX - 70, -40, L=470)     # patient's right (-x): swung out
d.save()
