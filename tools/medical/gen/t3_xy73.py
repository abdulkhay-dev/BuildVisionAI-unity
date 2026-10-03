# XY-73 PT training table, flat one-piece top (table-3 batch). Based on the XY-72 frame.
from lib import *
d = D("xy-73", [2020, 1240, 1000], {
  "pad": "leather#8fb8e0", "frame": "plastic#f1f2f4", "cap": "plastic#9aa0a8", "act": "metal#a9aeb5",
  "bolt": "metal#8d939a", "emb": "plastic#a3a8b0"})
W, Dp = 2020, 1240
T = 560   # underside of the pad = top of the top frame band
F = 525   # bottom of the top frame band
# --- pad: one piece, rounded corners in plan, ~90 thick, slightly domed
import math
def rr(x0, z0, x1, z1, r, n=6):
    pts = []
    for cx, cz, a0 in ((x1 - r, z0 + r, -90), (x1 - r, z1 - r, 0), (x0 + r, z1 - r, 90), (x0 + r, z0 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n); pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return "M " + " L ".join(f"{x:.1f} {z:.1f}" for x, z in pts) + " Z"
d.slab("pad", "top", rr(0, 0, W, Dp, 70), [T + 8, T + 85], "pad", r=20)
d.slab("pad-board", "top", rr(10, 10, W - 10, Dp - 10, 60), [T, T + 10], "frame", r=3)
# white frame band right under the pad (seen as a thin white strip in the photo)
d.box("band", [20, F, 20, W - 20, T, Dp - 20], "frame", r=5)
d.bar("top-ladder", [400, F - 30, 80], [400, F - 30, Dp - 80], [40, 40], "frame", r=6, copies=[[1220, 0, 0]])
d.bar("sub-rail", [250, F - 30, 160], [1800, F - 30, 160], [40, 40], "frame", r=5, copies=[[0, 0, 920]])
# --- base frame: two long rails + end bars, corner legs with grey caps, castors inside the legs
B1 = 290
d.bar("base-rail", [200, 260, 220], [1820, 260, 220], [60, 60], "frame", r=6, copies=[[0, 0, 800]])
d.bar("base-end", [230, 260, 190], [230, 260, 1050], [60, 60], "frame", r=6, copies=[[1560, 0, 0]])
d.bar("base-mid", [1000, 270, 220], [1000, 270, 1020], [50, 50], "frame", r=6)
d.bar("leg-arm", [110, 260, 220], [200, 260, 220], [60, 60], "frame", r=6,
      copies=[[0, 0, 800], [1710, 0, 0], [1710, 0, 800]])
d.box("leg", [70, 30, 185, 140, 300, 255], "frame", r=6, copies=[[0, 0, 800], [1810, 0, 0], [1810, 0, 800]])
d.box("leg-cap", [66, 12, 181, 144, 34, 259], "cap", r=5, copies=[[0, 0, 800], [1810, 0, 0], [1810, 0, 800]])
d.box("leg-top", [66, 296, 181, 144, 316, 259], "cap", r=4, copies=[[0, 0, 800], [1810, 0, 0], [1810, 0, 800]])
d.add("caster", "caster", at=[180, 0, 270], d=75, copies=[[0, 0, 700], [1660, 0, 0], [1660, 0, 700]])
d.box("caster-plate", [150, 100, 240, 210, 230, 300], "frame", r=6, copies=[[0, 0, 700], [1660, 0, 0], [1660, 0, 700]])
d.cyl("leg-link", [140, 160, 270], [150, 180, 270], 14, "chrome", copies=[[0, 0, 700]])
# --- lift: two lever plates per side; vertical edge on the LEFT, the slope runs down to the right (photo)
def lever(x0, xt, x1):
    # x0 vertical left edge, xt end of the short top edge, x1 end of the bottom edge
    return (f"M {x0} {B1} L {x1} {B1} L {x1 - 30} {B1 + 25} L {xt} {F} L {x0} {F} Z")
for nm, (x0, xt, x1) in (("xiangyu", (470, 700, 880)), ("medical", (1150, 1380, 1580))):
    d.slab("lever-" + nm, "front", lever(x0, xt, x1), [1052, 1064], "frame", r=3, copies=[[0, 0, -888]])
    d.cyl("bolt-top-" + nm, [x0 + 30, F - 25, 1062], [x0 + 30, F - 25, 1070], 26, "bolt", soft=True)
    d.cyl("bolt-bot-" + nm, [x0 + 30, B1 + 30, 1062], [x0 + 30, B1 + 30, 1070], 26, "bolt", soft=True)
    d.cyl("bolt-mid-" + nm, [xt + 30, F - 25, 1062], [xt + 30, F - 25, 1070], 22, "bolt", soft=True)
    d.cyl("lever-tube-" + nm, [x0 + 30, B1 + 30, 176], [x0 + 30, B1 + 30, 1064], 40, "frame")
# grey "XIANG YU" / "MEDICAL" lettering on the plates (stroke letters, front and back reading correctly)
from t3_alclib import FONT
FONT2 = dict(FONT, M=[[(0, 0), (0, 1), (0.5, 0.45), (1, 1), (1, 0)]],
             E=[[(1, 1), (0, 1), (0, 0), (1, 0)], [(0, 0.5), (0.8, 0.5)]],
             D=[[(0, 0), (0, 1), (0.6, 1), (1, 0.7), (1, 0.3), (0.6, 0), (0, 0)]],
             C=[[(1, 0.85), (0.75, 1), (0.25, 1), (0, 0.75), (0, 0.25), (0.25, 0), (0.75, 0), (1, 0.15)]])
def letters(text, x_start, y0, z, h=50, w=26, step=34):
    x = x_start; k = 0
    for ch in text:
        if ch != " ":
            for line in FONT2[ch]:
                pts = [[x + u * w, y0 + v * h, z] for u, v in line]
                d.tube(f"txt-{text[:2]}-{k}", pts, 7, "emb", bend=2, soft=True); k += 1
        x += step * (0.6 if ch == "I" else 1)
letters("XIANG YU", 560, 312, 1066)
letters("MEDICAL", 1250, 312, 1066)
# Linak actuator between the levers
d.cyl("actuator", [640, 415, 620], [1260, 435, 620], 50, "act")
d.cyl("actuator-rod", [1240, 435, 620], [1340, 440, 620], 26, "chrome")
d.bar("act-cross", [1350, 470, 200], [1350, 470, 1040], [40, 40], "frame", r=5)
d.box("motor", [560, 310, 560, 680, 380, 680], "act", r=15)
# hand-switch hook under the right end of the top
d.box("hook", [1960, F - 40, 1100, 2000, F, 1160], "plastic#3a3f45", r=6)
d.save()
