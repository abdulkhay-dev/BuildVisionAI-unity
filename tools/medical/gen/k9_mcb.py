"""XY-MCB-I smart peg board (standard): white glossy tablet-like base, wood-grain insert with 5x4 shape holes,
black glass strip on the right with a 7" portrait screen and the blue logo; vents and a button on the right edge,
finger notch in the front edge."""
import math
from k9lib import *
d = K("xy-mcb-i", [500, 350, 50], {
    "shell": "gloss#f4f5f6", "wood": "wood#c98f4c", "glass": "gloss#0a0a0b", "hole": "plastic#b9bcbf",
    "blue": "gloss#2f86d0", "dark": "plastic#2a2c30"})
W, D, H = 500, 350, 50
# (review 2026-10-03) the shape holes are real recesses: the wood insert is a 15 mm slab with the holes cut through,
# over the white shell (its top 14 mm below the surface is the holes' floor); the white rim is a ring around it
OUT = rpoly([(0, 0), (W, 0), (W, D), (0, D)], 34)
INS = rpoly([(9, 9), (W - 9, 9), (W - 9, D - 9), (9, D - 9)], 26)
d.slab("shell", "top", OUT, [0, H - 14], "shell", r=12)
d.slab("rim", "top", OUT + " " + INS, [16, H - 1], "shell", r=3)     # its lower edge hides in the shell
WOOD = rpoly([(9, 9), (380, 9), (417, D - 9), (9, D - 9)], 26)
d.screen("screen", [400, H - 4, 78, 484, H + 0.5, 246], "dark", face="top", bezel=2, r=1)
d.decal("logo", [427, H + 0.6, 39], [14, 14], "top", "blue")
d.decal("logo-t", [460, H + 0.6, 39], [38, 7], "top", "blue")
# 5x4 shape holes: square, circle, triangle in the photo's order (light shell visible inside)
order = ["sq", "ci", "tr", "sq", "ci", "tr", "sq", "ci", "tr", "sq", "ci", "tr", "sq", "ci", "tr", "sq", "ci", "tr", "sq", "ci"]
paths = []
for r_ in range(4):
    for c in range(5):
        k = r_ * 5 + c
        sh = order[k]
        x = 48 + c * 74
        z = 50 + r_ * 83
        s = 32
        if sh == "sq":
            paths.append(f"M {x - s / 2} {z - s / 2} H {x + s / 2} V {z + s / 2} H {x - s / 2} Z")
        elif sh == "ci":
            paths.append(circle(x, z, s / 2 + 1))
        else:
            h = s * 0.9
            paths.append(f"M {x} {z - h / 2} L {x + s / 2 + 2} {z + h / 2} L {x - s / 2 - 2} {z + h / 2} Z")
d.slab("wood", "top", WOOD + " " + " ".join(paths), [H - 15, H], "wood", r=1)
d.slab("glass", "top", rpoly([(380, 9), (W - 9, 9), (W - 9, D - 9), (417, D - 9)], 26), [H - 6, H], "glass", r=1)
# finger notch in the front edge (wood showing under the rim)
d.slab("notch", "front", f"M 168 {H} A 42 42 0 0 1 232 {H} Z", [D - 2, D + 0.8], "wood", r=0.5)
# right edge: two vent slot groups with a small hole between, and a rounded button
d.box("vent-a", [W - 1, 16, 150, W + 0.6, 18, 190], "dark", r=0.5, repeat=rep(6, [0, 3.8, 0]))
d.box("vent-b", [W - 1, 16, 205, W + 0.6, 18, 245], "dark", r=0.5, repeat=rep(6, [0, 3.8, 0]))
d.decal("vent-hole", [W + 0.7, 26, 197.5], [4, 4], "right", "dark")
d.box("button", [W - 2, 18, 290, W + 2, 34, 302], "plastic#9a9ea3", r=3)
d.save()
