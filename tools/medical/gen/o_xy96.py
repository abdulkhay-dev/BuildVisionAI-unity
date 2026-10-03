# XY-96 pull-down wardrobe rail: aluminium rail with black end and middle blocks, thin arms down to black damper
# housings on the side walls, pull rod with a black T end, two coat hangers — other-1
from o_lib import *
W, DP, H = 900, 450, 1150
d = D("xy-96", [W, DP, H], {
    "alu": "metal#cfd3d8", "blk": "plastic#1c1d20", "felt": "fabric#1e2024", "blue": "plastic#8db5c6", "purple": "plastic#7a68d8"})
Z = 250
RY = 1118
d.cyl("rail", [40, RY, Z], [W - 40, RY, Z], 25, "alu")
for i, (a, b) in enumerate(((0, 52), (W - 52, W))):
    d.box(f"end{i}", [a, RY - 30, Z - 30, b, H, Z + 30], "blk", r=6)
d.slab("mid", "front", poly([(W / 2 - 34, H), (W / 2 + 34, H), (W / 2 + 14, RY - 40), (W / 2 - 14, RY - 40)]), [Z - 26, Z + 26], "blk", r=5)
# thin arms down to the black damper housings
for i, x in enumerate((24, W - 24)):
    d.cyl(f"arm{i}", [x, RY - 30, Z], [x, 395, Z], 12, "alu")
    a = 0 if i == 0 else W - 84
    d.box(f"damper{i}", [a, 60, Z - 45, a + 84, 400, Z + 45], "felt", r=10, puff=3)
# pull rod with a black T end
d.cyl("pull", [W / 2, RY - 40, Z], [W / 2, 62, Z], 16, "alu")
d.cyl("pull-grip", [W / 2, 62, Z], [W / 2, 22, Z], 26, "blk")
d.box("pull-t", [W / 2 - 34, 10, Z - 12, W / 2 + 34, 24, Z + 12], "blk", r=5)
# coat hangers on the rail
for i, (hx, mat) in enumerate(((258, "blue"), (690, "purple"))):
    d.tube(f"hook{i}", [[hx - 22, RY + 6, Z], [hx - 14, RY + 26, Z], [hx + 8, RY + 26, Z], [hx + 14, RY + 6, Z],
                        [hx, RY - 30, Z], [hx, RY - 55, Z]], 6, mat, bend=10, soft=True, rot=rot("y", 90, [hx, 0, Z]))
    d.tube(f"hanger{i}", [[hx, RY - 55, Z], [hx - 185, RY - 245, Z], [hx - 170, RY - 262, Z], [hx + 170, RY - 262, Z],
                          [hx + 185, RY - 245, Z], [hx, RY - 55, Z]], 9, mat, bend=12, soft=True, rot=rot("y", 52, [hx, 0, Z]))
    # (photo: the hangers hang turned across the rail, seen at an angle — not flat in the front plane)
d.save()
