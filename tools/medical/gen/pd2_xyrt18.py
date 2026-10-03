# XYRT-18 guided training set, drawn as photographed: slatted bench (1500 x 650 x 430) with adjustable two-part legs and
# its accessories (tilted reading board on two base boards, peg blocks, a chest board with a half-round cut-out),
# three nested step boxes in front of it, and a ladder-back chair at the right facing the bench (-x).
from pd2_lib import *
import math

W, D, H = 2150, 1150, 1000
d = Design("xyrt-18", [W, D, H], {
    "slat": "wood#e3b273", "apron": "wood#b8673b", "leg": "wood#e7bf86", "block": "wood#efd6a6", "knob": "plastic#1c1d1f",
    "board": "wood#dba774", "pink": "wood#df9e82", "box": "plastic#d39550", "boxtop": "wood#dcab6e", "slot": "plastic#4a2e22",
    "chair": "wood#e8c184", "label": "metal#d6d9dc", "hole": "plastic#6b5a44"})
# ---------------- bench (x 0..1500, z 0..650)
BW, BD, BH = 1500, 650, 430
AH = 90
wbox(d, "apron-f", [0, BH - AH, BD - 26, BW, BH - 4, BD], "apron", r=4)
wbox(d, "apron-b", [0, BH - AH, 0, BW, BH - 4, 26], "apron", r=4)
d.box("end-l", [0, BH - AH, 26, 24, BH - 4, BD - 26], "apron", r=4)
d.box("end-r", [BW - 24, BH - AH, 26, BW, BH - 4, BD - 26], "apron", r=4)
n, sw = 10, 52
gap = (BD - n * sw) / (n + 1)
zc = gap + sw / 2
d.box("slat", [BW / 2 - sw / 2, BH - 22, zc - BW / 2 + 4, BW / 2 + sw / 2, BH, zc + BW / 2 - 4], "slat", r=3,
      rot=rot("y", 90, [BW / 2, BH, zc]), repeat=rep(n, [0, 0, sw + gap]))
for nm, x, z, s in (("lf", 30, BD - 70, -1), ("rf", BW - 75, BD - 70, 1), ("lb", 30, 25, -1), ("rb", BW - 75, 25, 1)):
    d.box(f"leg-{nm}", [x, 150, z, x + 45, BH - AH + 4, z + 45], "leg", r=3)
    d.box(f"sleeve-{nm}", [x - 10, 0, z - 10, x + 55, 210, z + 55], "block", r=4)
    zf = z + 55.5 if z > BD / 2 else z - 10.5
    d.box(f"holes-{nm}", [x + 18, 40, zf - 1, x + 27, 49, zf + 1], "hole", r=2, soft=True, repeat=rep(5, [0, 32, 0]))
    xk = x + 55 if s > 0 else x - 10
    d.lathe(f"knob-{nm}", [xk, 120, z + 22], [[0, 0], [6, 0], [6, 10], [15, 12], [15, 26], [0, 28]], "knob", axis="x",
            rot=rot("y", 180, [xk, 120, z + 22]) if s < 0 else None)
# accessories on the bench
Y = BH
wbox(d, "base-board1", [70, Y, 160, 560, Y + 16, 520], "board", face="top", r=3)
wbox(d, "base-board2", [110, Y + 16, 190, 520, Y + 30, 480], "board", face="top", r=3)
d.box("reader-ledge", [140, Y + 30, 445, 500, Y + 58, 475], "board", r=3)
wbox(d, "reader", [140, Y + 34, 140, 500, Y + 52, 450], "pink", face="top", r=4, rot=rot("x", 40, [320, Y + 40, 450]))
d.box("reader-strut", [300, Y + 30, 330, 340, Y + 160, 348], "board", r=3)
d.box("peg-base", [640, Y, 250, 800, Y + 24, 390], "board", r=4)
d.box("peg", [675, Y + 24, 300, 705, Y + 100, 330], "board", r=3, copies=[[70, 0, 0]])
d.box("pin-base", [860, Y, 120, 980, Y + 18, 190], "board", r=3)
d.cyl("pin", [920, Y + 18, 155], [920, Y + 125, 155], 26, "board")
d.lathe("knob-top1", [810, Y, 170], [[0, 0], [8, 0], [8, 12], [20, 14], [20, 30], [0, 32]], "knob")
# chest board with a half-round cut-out on its front edge and a raised rim
cut = (f"M 860 330 L 1460 330 L 1460 640 L 1220 640 A 110 110 0 0 0 1000 640 L 860 640 Z")
d.slab("chest-board", "top", cut, [Y, Y + 20], "board", r=3)
wbox(d, "chest-rim-b", [880, Y + 20, 350, 1440, Y + 38, 372], "board", r=3)
d.box("chest-rim-l", [880, Y + 20, 372, 902, Y + 38, 620], "board", r=3)
d.box("chest-rim-r", [1418, Y + 20, 372, 1440, Y + 38, 620], "board", r=3)
d.lathe("knob-top2", [1160, Y + 20, 300], [[0, 0], [8, 0], [8, 12], [20, 14], [20, 30], [0, 32]], "knob")
# ---------------- three nested step boxes in front of the bench (front edges at z = D)
for nm, x0, w, dd, h in (("l", 110, 480, 380, 360), ("m", 640, 400, 320, 300), ("s", 1080, 320, 260, 240)):
    z0 = D - dd
    for fx in (x0 + 8, x0 + w - 38):
        for fz in (z0 + 8, D - 38):
            d.box(f"box-{nm}-foot{fx}{fz}", [fx, 0, fz, fx + 30, 26, fz + 30], "boxtop", r=4)
    wbox(d, f"box-{nm}", [x0 + 6, 24, z0 + 6, x0 + w - 6, h - 66, D - 6], "box", r=4)   # smooth laminate, grain across
    # the lid stands on corner posts: a dark gap all round under it
    d.box(f"box-{nm}-gap", [x0 + 12, h - 70, z0 + 12, x0 + w - 12, h - 22, D - 12], "slot", r=2)
    for cx in (x0 + 6, x0 + w - 34):
        for cz in (z0 + 6, D - 34):
            d.box(f"box-{nm}-post{cx}{cz}", [cx, h - 70, cz, cx + 28, h - 22, cz + 28], "boxtop", r=3)
    d.box(f"box-{nm}-top", [x0 - 8, h - 24, z0 - 8, x0 + w + 8, h, D], "boxtop", r=8)
    d.box(f"box-{nm}-label", [x0 + w - 70, h, D - 40, x0 + w - 20, h + 1, D - 20], "label", r=3, soft=True)
# ---------------- ladder chair at the right: a tall ladder (rungs from low to the top) on two floor runners, a seat
# board sticking out of it toward the bench (-x) with half-round side aprons, diagonal braces from the runner fronts
ZL, ZR = 400, 840                      # chair sides
XU = 2060                              # ladder uprights
SY = 560                               # seat height
for nm, z in (("a", ZL), ("b", ZR - 44)):
    d.slab(f"runner-{nm}", "front", svg_poly([(1640, 0), (2150, 0), (2110, 42), (1680, 42)]), [z, z + 44], "chair", r=4)
    d.bar(f"upright-{nm}", [XU + 20, 40, z + 22], [XU + 20, H - 10, z + 22], [44, 40], "chair", r=4)
    d.bar(f"front-leg-{nm}", [1700, 40, z + 22], [XU, 330, z + 22], [40, 32], "chair", r=4)
    lobe = svg_poly([(1830 + 130 * math.cos(math.radians(a)), SY - 2 + 75 * math.sin(math.radians(a))) for a in range(180, 361, 10)])
    d.slab(f"seat-apron-{nm}", "front", lobe, [z + 4, z + 36], "chair", r=3)
d.box("seat", [1650, SY, ZL - 10, 2058, SY + 24, ZR + 10], "chair", r=6)
for i in range(12):
    y = 150 + i * 72
    if SY - 50 < y < SY + 60:
        continue
    d.cyl(f"rung{i}", [XU + 20, y, ZL + 20], [XU + 20, y, ZR - 20], 24, "chair")
d.save()
