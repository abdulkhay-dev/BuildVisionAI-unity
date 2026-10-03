# XY-89 ADL pine kitchen: base cabinets with a wooden worktop, stainless sink + tap, black glass hob, gas hose,
# pine back panel, wall cabinet, pine box with a black glass range hood, tall right side panel — other-1
import math
from o_lib import *
W, DP, H = 1900, 780, 1870
d = D("xy-89", [W, DP, H], {
    "pine": "wood#ffd384", "pine2": "wood#f9c574", "steel": "metal#c9cdd1", "chrome": "chrome", "glass": "gloss#141416",
    "iron": "black#1b1b1c", "seam": "wood#a87a45", "knob": "metal#b9a27e", "blk": "plastic#151517",
    "blue": "plastic#2f5fb0", "copper": "gloss#c9773a", "pink": "gloss#d88aa0"})
BX1 = 1840                 # base cabinets end; tall side panel to W
TY = 860                   # worktop top
d.box("plinth", [10, 0, 40, BX1 - 10, 70, 730], "pine2", r=2)
d.box("carcass", [0, 70, 20, BX1, TY - 50, 740], "pine", r=3)
# doors (2 + 1 + 2) with seams and small knob pairs
# (photo: left double door, middle single door, right double door, then a narrow fixed panel)
doors = [(10, 305), (309, 612), (628, 960), (976, 1345), (1349, 1720), (1724, BX1 - 8)]
for i, (a, b) in enumerate(doors):
    d.box(f"door{i}", [a, 78, 740, b, TY - 58, 758], "pine", r=3)
for i, x in enumerate((307, 1347)):
    d.cyl(f"knob{i}a", [x - 12, 445, 758], [x - 12, 445, 780], 18, "knob")
    d.cyl(f"knob{i}b", [x + 12, 445, 758], [x + 12, 445, 780], 18, "knob")
# worktop with the stainless sink (hole) on the left
SX0, SX1, SZ0, SZ1 = 100, 640, 230, 620
d.slab("worktop", "top", rr(0, 0, BX1, DP, 6) + " " + rr(SX0, SZ0, SX1, SZ1, 30), [TY - 50, TY], "pine2", r=4)
d.box("sink-rim", [SX0 - 15, TY, SZ0 - 15, SX1 + 15, TY + 4, SZ0], "steel", r=2,
      copies=[[0, 0, SZ1 - SZ0 + 15]])
d.box("sink-rim2", [SX0 - 15, TY, SZ0, SX0, TY + 4, SZ1], "steel", r=2, copies=[[SX1 - SX0 + 15, 0, 0]])
d.box("sink-bot", [SX0, TY - 190, SZ0, SX1, TY - 180, SZ1], "steel", r=4)
d.box("sink-wl", [SX0, TY - 190, SZ0, SX0 + 3, TY - 50, SZ1], "steel", copies=[[SX1 - SX0 - 3, 0, 0]])
d.box("sink-wb", [SX0, TY - 190, SZ0, SX1, TY - 50, SZ0 + 3], "steel", copies=[[0, 0, SZ1 - SZ0 - 3]])
d.cyl("tap-base", [423, TY, 150], [423, TY + 60, 150], 40, "chrome")
d.tube("tap", [[423, TY + 50, 150], [423, TY + 200, 160], [423, TY + 200, 260], [423, TY + 150, 285]], 20, "chrome", bend=50)
d.box("tap-lever", [440, TY + 50, 120, 456, TY + 64, 175], "chrome", r=5)
# black glass hob on the right with two pan supports
d.box("hob", [950, TY, 230, 1730, TY + 8, 620], "glass", r=8)
for i, bx in enumerate((1170, 1550)):
    d.lathe(f"burner{i}", [bx, TY + 8, 420], [[0, 0], [50, 0], [50, 16], [36, 22], [0, 22]], "iron")
    ring = [[bx + 115 * math.cos(math.radians(a)), TY + 40, 420 + 115 * math.sin(math.radians(a))] for a in range(0, 361, 20)]
    d.tube(f"grid{i}", ring, 9, "iron")
    for k in range(4):
        a = math.radians(k * 90 + 45)
        d.bar(f"arm{i}-{k}", [bx + 55 * math.cos(a), TY + 40, 420 + 55 * math.sin(a)],
              [bx + 150 * math.cos(a), TY + 40, 420 + 150 * math.sin(a)], [10, 22], "iron", r=2)
        d.cyl(f"foot{i}-{k}", [bx + 140 * math.cos(a), TY + 8, 420 + 140 * math.sin(a)],
              [bx + 140 * math.cos(a), TY + 40, 420 + 140 * math.sin(a)], 10, "iron")
d.cyl("hob-knob", [1360, TY + 8, 600], [1360, TY + 22, 600], 30, "iron", copies=[[40, 0, 0]])
# gas hose with a blue regulator, down the front into the middle door
d.box("regulator", [790, TY - 30, 762, 840, TY + 20, 800], "blue", r=10)
d.tube("gas-hose", [[815, TY + 10, 790], [800, TY - 60, 800], [745, 620, 790], [700, 520, 770]], 14, "blk", bend=80, soft=True)
d.tube("gas-hose2", [[815, TY + 20, 785], [830, TY + 30, 700], [860, TY + 10, 600]], 12, "chrome", bend=40, soft=True)
# pine back panel above the worktop
d.box("back", [260, TY, 0, BX1, H - 20, 22], "pine2", r=2)
# wall cabinet (2 doors) upper left
CY0, CY1 = 1316, 1830
d.box("wcab", [30, CY0, 22, 850, CY1, 320], "pine", r=3)
d.box("wcab-seam", [358, CY0 + 6, 319, 362, CY1 - 6, 322], "seam", soft=True)
d.cyl("wknob", [348, 1565, 320], [348, 1565, 340], 16, "knob", copies=[[24, 0, 0]])
# pine box with the black glass range hood (slanted, keys, flower graphic, copper light)
d.box("hood-top", [870, 1790, 22, 1810, H, 360], "pine", r=3)
d.box("hood-side", [870, CY0, 22, 905, 1790, 360], "pine", r=3, copies=[[905, 0, 0]])
d.box("hood-body", [905, 1460, 22, 1775, 1790, 240], "glass", r=4)
hood = poly([(260, 1340), (360, 1340), (300, 1770), (200, 1770)])
d.slab("hood-glass", "side", hood, [915, 1765], "glass", r=4)
tilt = rot("x", -7.9, [1300, 1340, 360])
d.box("hood-key", [1250, 1440, 359.5, 1264, 1452, 362.5], "gloss#e8eaee", soft=True, repeat=rep(4, [26, 0, 0]), rot=tilt)
d.box("hood-flower", [1245, 1580, 359.5, 1270, 1650, 362.5], "pink", soft=True, rot=tilt)
d.box("hood-label", [1500, 1440, 359.5, 1640, 1452, 362.5], "gloss#9aa0a8", soft=True, rot=tilt)
d.box("hood-light", [1250, 1330, 320, 1320, 1342, 350], "copper", r=4)
# tall right side panel, cable at the right
d.box("side-low", [BX1, 0, 0, W, TY, DP], "pine", r=3)
d.box("side-high", [BX1, TY, 0, W, H, 380], "pine", r=3)
d.tube("cable", [[1800, 1790, 300], [1830, 1700, 330], [1835, 1500, 340], [1825, 1260, 330]], 10, "blk", bend=60, soft=True)
# finger-jointed pine (photo): lamellas of short blocks in lighter / darker tones — vertical on the doors and cabinets,
# horizontal on the back panel; drawn as flush decals of every other block
import random
rnd_ = random.Random(89)
nb = [0]


def lamellas(x0, y0, x1, y1, z, vertical, lw=58):
    span0, span1, a0, a1 = (x0, x1, y0, y1) if vertical else (y0, y1, x0, x1)
    u = span0
    while u < span1 - 8:
        u1 = min(span1, u + lw)
        v = a0 + rnd_.uniform(-200, 0)
        while v < a1:
            L = rnd_.uniform(180, 520)
            va, vb = max(v, a0), min(v + L, a1)
            if vb - va > 30 and rnd_.random() < 0.55:
                col = rnd_.choice(("wood#ffe4ad", "wood#eeb766", "wood#f6c87a"))
                cu, cv = (u + u1) / 2, (va + vb) / 2
                at, size = ([cu, cv, z], [u1 - u - 2, vb - va - 2]) if vertical else ([cv, cu, z], [vb - va - 2, u1 - u - 2])
                d.decal(f"blk{nb[0]}", at, size, "front", col, soft=True); nb[0] += 1
            v += L
        u = u1


for i, (a, b) in enumerate(doors):
    lamellas(a + 4, 82, b - 4, TY - 62, 758.6, True)
lamellas(1810, TY + 4, BX1, H - 24, 22.6, False, lw=64)
lamellas(262, TY + 4, 1810, CY0 - 4, 22.6, False, lw=64)
lamellas(34, CY0 + 4, 846, CY1 - 4, 320.6, True)
d.save()
