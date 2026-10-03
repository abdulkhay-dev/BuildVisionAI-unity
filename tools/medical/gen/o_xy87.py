# XY-87 electric patient hoist: white U base on castors, battery box, white mast and boom, black actuator,
# ring push handle, hand controller, black hanger with a brown sling — other-1
import math
from o_lib import *
W, DP, H = 760, 1060, 2090
d = D("xy-87", [W, DP, H], {
    "white": "plastic#eeeeea", "blk": "plastic#1d1e21", "dot": "plastic#7d8288", "chrome": "chrome",
    "sling": "fabric#9b5a31", "edge": "fabric#27315f", "strapk": "fabric#1c1c1f"})
CX = W / 2
# base: two flat white legs along the depth + rear cross member, castors at the ends
for i, x in enumerate((100, W - 100)):
    d.bar(f"leg{i}", [x, 125, 50], [x, 125, 1010], [80, 52], "white", r=6)
    d.box(f"leg-cap{i}", [x - 41, 99, 1004, x + 41, 151, 1022], "plastic#c9ccd0", r=5)
    caster(d, f"castor-r{i}", [x, 0, 95], 80, "plastic#8a8f96")
    caster(d, f"castor-f{i}", [x, 0, 965], 80, "plastic#8a8f96")
d.bar("cross", [60, 128, 150], [W - 60, 128, 150], [90, 56], "white", r=6)
# battery / control box at the mast foot with a perforated face
MZ = 210
d.box("battery", [CX - 150, 156, MZ - 120, CX + 40, 330, MZ - 40], "white", r=8)
d.box("holes", [CX - 135, 190, MZ - 122, CX - 128, 197, MZ - 120], "dot", soft=True,
      repeat={"n": 10, "step": [14, 0, 0]}, copies=[[0, 22, 0], [0, 44, 0], [0, 66, 0], [7, 88, 0], [0, 110, 0]])
# mast and boom (photo pose, boom up 45 deg)
PY = 1405
d.box("mast-foot", [CX - 60, 156, MZ - 50, CX + 60, 190, MZ + 50], "white", r=6)
d.bar("mast", [CX, 180, MZ], [CX, PY + 30, MZ], [72, 72], "white", r=6)
d.cyl("pivot", [CX - 46, PY, MZ], [CX + 46, PY, MZ], 30, "chrome")
L = 860
tip = [CX, PY + L * math.sin(math.radians(45)), MZ + L * math.cos(math.radians(45))]
d.bar("boom", [CX, PY, MZ], tip, [64, 70], "white", r=8)
end = [CX, tip[1] + 20, tip[2] + 90]
d.bar("boom-end", tip, end, [64, 66], "white", r=8)
# actuator from the mast to the boom: black body, chrome rod, motor and control boxes
a0 = [CX, 760, MZ + 60]
t = 0.32
a1 = [CX, PY + L * t * math.sin(math.radians(45)), MZ + L * t * math.cos(math.radians(45)) + 20]
d.cyl("act-body", a0, lerp(a0, a1, 0.55), 56, "blk")
d.cyl("act-rod", lerp(a0, a1, 0.5), a1, 26, "chrome")
d.box("act-motor", [CX - 40, 690, MZ + 40, CX + 40, 800, MZ + 160], "blk", r=10)
d.box("ctrl", [CX + 38, 820, MZ + 30, CX + 110, 980, MZ + 110], "blk", r=8)
d.box("act-mount", [CX - 30, 720, MZ + 30, CX + 30, 760, MZ + 60], "white", r=4)
# ring push handle behind the mast
ring = [[CX + 150 * math.cos(math.radians(a)), 1080, MZ - 110 + 85 * math.sin(math.radians(a))] for a in range(0, 361, 15)]
d.tube("push-ring", ring, 30, "blk")
d.bar("push-arm", [CX, 1080, MZ - 30], [CX, 1080, MZ - 40], [40, 40], "blk", r=4)
d.box("push-clamp", [CX - 44, 1060, MZ - 44, CX + 44, 1100, MZ + 44], "blk", r=6)
# hand controller on a coiled cord, hanging on the mast's left
d.box("pendant", [CX - 82, 840, MZ - 20, CX - 44, 1010, MZ + 12], "plastic#3a3d42", r=10)
d.coil("cord", [CX - 63, 1015, MZ - 4], [CX - 50, 1300, MZ - 30], 26, 5, 16, "blk", soft=True)
# hanger: black spreader with up-turned hooks hung from the boom end
HY = end[1] - 70
d.cyl("link", [CX, end[1] - 30, end[2]], [CX, HY, end[2]], 18, "blk")
d.tube("spreader", [[CX - 150, HY + 55, end[2]], [CX - 135, HY, end[2]], [CX + 135, HY, end[2]], [CX + 150, HY + 55, end[2]]],
       24, "blk", bend=35)
d.tube("spreader-arc", [[CX - 100, HY, end[2]], [CX, HY - 60, end[2]], [CX + 100, HY, end[2]]], 14, "blk", bend=60)
# sling (photo): a brown folded U-sling whose body hangs ~1480 ... 520, diamond-shaped (narrow top, widest at
# ~1000, pointed bottom), navy piping along the edges, a multicolour band diagonally across the front panel; dark
# straps (with a yellow-green stripe) from the spreader hooks down to the body, two loose leg straps
SZ = end[2] - 10
d.loft("sling", [sec(520, 110, 50, 24, CX + 20, SZ + 20), sec(700, 360, 150, 60, CX + 15, SZ + 15),
                 sec(1000, 520, 190, 70, CX, SZ), sec(1220, 430, 150, 60, CX - 10, SZ),
                 sec(1480, 200, 60, 26, CX - 10, SZ)], "sling", dome="start", domeH=40)
ZF = SZ + 96
for k, (col, dz) in enumerate((("fabric#e3c21b", 0), ("fabric#2e9a3e", 9), ("fabric#c8342c", 18), ("fabric#2a5bb8", 27))):
    d.strap(f"stripe{k}", [[CX - 150, 820 + dz, ZF - 10], [CX, 960 + dz, ZF], [CX + 200, 1150 + dz, ZF - 22]],
            [11, 3], col, bend=80, soft=True)
for i, s_ in enumerate((-1, 1)):
    d.strap(f"edge{i}", [[CX + s_ * 95 - 10, 1480, SZ + 30], [CX + s_ * 262, 1000, SZ + 70], [CX + s_ * 60 + 20, 540, SZ + 30]],
            [16, 3], "edge", bend=220, soft=True)
    d.strap(f"strap{i}", [[CX + s_ * 145, HY + 40, end[2]], [CX + s_ * 120, 1700, SZ + 10], [CX + s_ * 80, 1470, SZ + 10]],
            [30, 4], "strapk", bend=80, soft=True)
    d.strap(f"loop{i}", [[CX + s_ * 140, HY + 30, end[2] + 8], [CX + s_ * 175, 1650, SZ + 70], [CX + s_ * 190, 1440, SZ + 90]],
            [28, 4], "strapk", bend=80, soft=True)
    d.strap(f"loopst{i}", [[CX + s_ * 140, HY + 26, end[2] + 11], [CX + s_ * 175, 1650, SZ + 73], [CX + s_ * 190, 1440, SZ + 93]],
            [9, 2], "fabric#b9c92a", bend=80, soft=True)
d.save()
print("tip", tip, "end", end)
