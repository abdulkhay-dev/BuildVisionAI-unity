# XY-92 vertical platform lift: white deck with two white tube guard rails, black perforated gate on the near
# end, black pleated bellows, dark base plate, blue-grey ribbed ramp — other-1
from o_lib import *
W, DP, H = 1970, 1090, 1260
d = D("xy-92", [W, DP, H], {
    "white": "plastic#f1f2f2", "rail": "plastic#f3f4f4", "blk": "black#1d1e21", "bel": "gloss#2b3038",
    "bel2": "rubber#4a4d52", "base": "black#2b2e33", "ramp": "metal#4d6888", "chrome": "chrome"})
X0, X1 = 520, W - 10
Z0, Z1 = 50, DP - 50
TY = 780
# base plate and the ramp at the near (left) end
d.box("base", [X0 - 20, 0, Z0 - 10, X1 + 10, 28, Z1 + 10], "base", r=4)
d.slab("ramp", "front", poly([(0, 0), (X0 - 20, 0), (X0 - 20, 28), (40, 8), (0, 4)]), [Z0 + 30, Z1 - 30], "ramp", r=2)
# ramp ribs (photo): pressed ridges along the ramp's length and up-turned side flanges, all on the slope
CZ = (Z0 + Z1) / 2
for k, z in enumerate((Z0 + 170, CZ - 120, CZ + 120, Z1 - 170)):
    d.box(f"rib{k}", [40, 4, z - 16, X0 - 30, 40, z + 16], "ramp", r=7, rot=rot("z", 2.3, [X0 - 20, 28, z]))
for k, z in enumerate((Z0 + 30, Z1 - 38)):
    d.box(f"flange{k}", [20, 4, z, X0 - 20, 46, z + 8], "ramp", r=3, rot=rot("z", 2.3, [X0 - 20, 28, z]))
d.box("ramp-lip", [0, 0, Z0 + 30, 34, 12, Z1 - 30], "ramp", r=5)
# black pleated bellows (alternating outer / inner folds)
d.box("bel-out", [X0 + 40, 28, Z0 + 40, X1 - 40, 58, Z1 - 40], "bel", r=12, puff=5, repeat=rep(10, [0, 61, 0]))
d.box("bel-in", [X0 + 70, 58, Z0 + 70, X1 - 70, 89, Z1 - 70], "bel2", r=6, repeat=rep(10, [0, 61, 0]))
# white platform deck
d.box("deck", [X0, TY - 150, Z0, X1, TY, Z1], "white", r=8)
d.box("deck-edge", [X0 + 2, TY - 152, Z0 + 2, X1 - 2, TY - 140, Z1 - 2], "blk", r=4)
# guard rails: two white tube frames along the long sides
for i, z in enumerate((Z0 + 25, Z1 - 25)):
    d.tube(f"rail{i}", [[X0 + 60, TY, z], [X0 + 60, H - 18, z], [X1 - 40, H - 18, z], [X1 - 40, TY, z]], 32, "rail", bend=60)
# black perforated gate plate on the near end with hinge brackets
gate = rr(Z0 + 20, TY - 40, Z1 - 70, TY + 260, 10)
holes = ""
for r in range(4):
    for c in range(12):
        zc = Z0 + 80 + c * 66 + (33 if r % 2 else 0)
        if zc > Z1 - 120:
            continue
        yc = TY - 0 + r * 62
        holes += " " + circle(zc, yc, 22, ccw=True)
d.slab("gate", "side", gate + holes, [X0 - 14, X0 - 4], "blk", r=2)
d.box("hinge", [X0 - 24, TY - 50, Z1 - 75, X0 + 6, TY + 270, Z1 - 45], "blk", r=4)
d.box("hinge-plate", [X0 - 6, TY - 40, Z1 - 45, X0 + 30, TY + 230, Z1 - 10], "metal#9aa0a8", r=3)
# far-end black bracket
d.box("bracket", [X1 - 10, TY - 80, Z1 - 60, X1 + 8, TY + 140, Z1 - 30], "blk", r=3)
d.box("bracket-top", [X1 - 40, TY + 120, Z1 - 60, X1 + 8, TY + 140, Z1 - 30], "blk", r=3)
d.save()
