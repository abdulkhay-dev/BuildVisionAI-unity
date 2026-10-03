from pd1_lib import *
W, D_, H = 430, 450, 950
d = K("xyrt-100", [W, D_, H], {"w": "wood#e6c892", "board": "plastic#1d1f1e", "chalk": "plastic#e8e8e2", "wb": "plastic#f2f2ee"})
ZF = 405                                    # front face of the uprights
# front uprights (the board frame's sides, down to the floor, slightly splayed)
d.bar("up", [20, 0, ZF - 12], [55, H, ZF - 12], [40, 24], "w", r=3, mirror="x")
# board frame top and bottom rails, black chalkboard between
d.box("top", [36, H - 26, ZF - 24, W - 36, H, ZF], "w", r=3)
d.box("bot", [50, 520, ZF - 24, W - 50, 546, ZF], "w", r=3)
d.box("board", [72, 546, ZF - 18, W - 72, H - 26, ZF - 6], "board", r=1)
d.box("board-back", [72, 546, ZF - 24, W - 72, H - 26, ZF - 18], "w")
zf = ZF - 6 + 0.6
L = text_len("ABC", 95, gap=0.5)
text(d, "abc", "ABC", [136, 712, zf], 76, "chalk", stroke=7.5, gap=0.55)
for i, (c, m) in enumerate(zip("DCNU", ("gloss#e02828", "gloss#2fa040", "gloss#f2c21a", "gloss#2fa040"))):
    text(d, f"t{c}", c, [108 + i * 30, 872, zf], 26, m, stroke=7)
# the number column 1…9, 0 down the left edge of the board (chalk digits)
for i, ch in enumerate("1234567890"):
    text(d, f"n{i}", ch, [80, 892 - i * 30, zf], 19, "chalk", stroke=3.2)
# white butterfly (pink inside) at the top right, tilted
bf = [(0, 6), (6, 12), (24, 30), (40, 28), (44, 14), (34, 2), (18, -2), (32, -8), (34, -22), (22, -30), (8, -20), (0, -12)]
bf = bf + [(-x, y) for x, y in reversed(bf)][1:-1]
BX, BY = 328, 884
d.slab("bfly", "front", poly([(BX + x * 1.25, BY + y * 1.25) for x, y in bf]), [ZF - 6, ZF - 4.6], "chalk", r=0.5,
       soft=True, rot=rot("z", -18, [BX, BY, ZF]))
for sx in (-1, 1):
    d.slab(f"bfly-p{sx}", "front", circle(BX + sx * 22, BY + 10, 9), [ZF - 4.8, ZF - 4.0], "gloss#f070a0", r=0.3, soft=True,
           rot=rot("z", -18, [BX, BY, ZF]))
d.box("bfly-body", [BX - 3, BY - 26, ZF - 5, BX + 3, BY + 14, ZF - 3.6], "plastic#8a8a8a", soft=True, rot=rot("z", -18, [BX, BY, ZF]))
# pink handwritten alphabet strip along the bottom of the board: a row of small pink letter marks
d.decal("pink", [86, 572, zf], [7, 14], "front", "gloss#f070a0", repeat=rep(23, [12, 0, 0]))
d.decal("pink2", [92, 569, zf], [5, 8], "front", "gloss#e8506e", repeat=rep(22, [12, 0, 0]))
# rear legs from the top hinge back to the floor
d.bar("rear", [62, H - 40, ZF - 40], [32, 0, 25], [36, 22], "w", r=3, mirror="x")
d.cyl("rear-x", [44, 235, 25 + 235 / (H - 40) * (ZF - 65)], [W - 44, 235, 25 + 235 / (H - 40) * (ZF - 65)], 24, "w")
d.cyl("front-x", [24, 200, ZF - 12], [W - 24, 200, ZF - 12], 24, "w")
# shelf tray: white bottom, wooden rim
d.box("shelf", [40, 440, ZF - 150, W - 40, 452, ZF - 24], "wb", r=2)
d.box("rim-f", [36, 440, ZF - 40, W - 36, 470, ZF - 24], "w", r=3)
d.box("rim-b", [36, 440, ZF - 160, W - 36, 470, ZF - 144], "w", r=3)
d.save()
