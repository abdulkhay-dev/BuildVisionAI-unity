from p1lib import *
d = D("xy-k-czld-v", [600, 750, 1550], {
  "shell": "gloss#f4f5f7", "black": "gloss#121314", "silver": "metal#c3c7cc", "line": "plastic#e9eaec"})
# base: white plinth, chrome band, white rim, black plate with white fingerprint lines and a small logo
CX, CZ = 300, 450
# review: taller base (~150) as in the photo: white plinth, thick chrome band, white rim, black plate
d.loft("plinth", [sec(0, 580, 580, 80, CX, CZ), sec(12, 600, 600, 90, CX, CZ), sec(78, 600, 600, 90, CX, CZ),
                  sec(84, 594, 594, 88, CX, CZ)], "shell")
d.loft("band", [sec(80, 594, 594, 88, CX, CZ), sec(120, 594, 594, 88, CX, CZ)], "chrome")
d.loft("rim", [sec(118, 600, 600, 90, CX, CZ), sec(136, 596, 596, 89, CX, CZ)], "shell")
d.slab("plate", "top", rpoly([(40, 270), (560, 270), (560, 725), (40, 725)], 70), [132, 146], "black", r=5)
for k in range(12):
    d.tube(f"print-{k}", arc(300, 520, 34 + 21 * k, 22 + 17 * k, -15, 195, 146.2, 22), 3, "line", soft=True)
d.decal("logo", [300, 146.4, 300], [22, 22], "line", face="top")
# curved column: silver body, black glossy front shell, leaning forward at the head
# review: the column is a deep body (~200 at the foot, photos 2/3), its head bending forward ~20 deg
OUT = ("M 60 100 L 262 100 Q 240 110 240 170 L 240 1150 L 336 1415 Q 346 1452 312 1462 L 165 1478 "
       "Q 112 1482 100 1440 L 64 1210 Q 58 1175 60 1150 Z")
d.slab("column", "side", OUT, [198, 402], "silver", r=16)
import re
def shift(path, dz):
    toks = path.split(); out = []; i = 0; nums = []
    res = []
    for t in toks:
        if t.isalpha(): res.append(t); nums = []
        else:
            nums.append(t)
            res.append(str(round(float(t) + (dz if len(nums) % 2 == 1 else 0), 1)))
    return " ".join(res)
d.slab("front", "side", shift(OUT, 5), [204, 396], "black", r=12)
# star perforations over the lower front (white crosses)
import random
random.seed(5)
cps = [[24 * j + (12 if i % 2 else 0), 24 * i, 0] for i in range(22) for j in range(7)
       if not (i == 0 and j == 0) and random.random() < (1.0 if i < 15 else 2.2 - i * 0.085)]
d.decal("star-h", [228, 180, 245.4], [9, 2.2], "line", face="front", soft=True, copies=cps)
d.decal("star-v", [228, 180, 245.4], [2.2, 9], "line", face="front", soft=True, copies=cps)
d.tube("wave", [[206, 300, 246], [250, 330, 246], [300, 315, 246], [350, 285, 246], [394, 300, 246]], 2, "plastic#8c9096", bend=40, soft=True)
# head: tilted touch screen (print), red E-stop above, small round button below
k = 96 / 265.0
A = math.degrees(math.atan(k))
def zf(y): return 245 + (y - 1150) * k
Q = [300, 1340, zf(1340)]
d.screen("screen", [212, 1268, Q[2] - 2, 388, 1396, Q[2] + 8], "black", r=6, face="front", bezel=2,
         print="med_xy-k-czld-v_screen", rot=rot("x", -A, Q))
d.sphere("estop", [300, 1428, zf(1428) - 2], 26, "gloss#d42020")
d.sphere("button", [355, 1238, zf(1238) - 3], 16, "plastic#2a2d31")
# chrome loop handrail and grip bar
# smooth chrome loop: from the column sides at ~540 bowing out and forward, over the head (review: was angular)
L = []
for k in range(10):
    t = k / 9.0
    y = 540 + t * 880
    hw = 100 + 92 * math.sin(math.pi * min(1, t * 1.6) * 0.5) - 8 * t
    z = 255 + 150 * math.sin(math.pi * t * 0.85) - 30 * t
    L.append([300 - hw, y, z])
L += [[128, 1490, 322], [170, 1532, 314], [232, 1550, 310], [300, 1554, 308]]
path = L + [[600 - p[0], p[1], p[2]] for p in reversed(L[:-1])]
d.tube("loop", path, 28, "chrome", bend=60)
# short grip bars from the column sides out through the loop
d.cyl("grip", [200, 1120, 190], [80, 1120, 400], 26, "chrome", mirror="x")
d.save()
