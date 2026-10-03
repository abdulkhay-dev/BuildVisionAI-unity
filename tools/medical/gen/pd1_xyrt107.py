from pd1_lib import *
W, D_, H = 480, 820, 750
d = K("xyrt-107", [W, D_, H], {"ply": "wood#e2c49c", "frame": "wood#c47e40", "dark": "wood#a5683a",
                                "pad": "fabric#2e8236", "pale": "gloss#c4ecaa", "pipe": "fabric#1c2a1c",
                                "lw": "wood#e6cfa2", "ring": "wood#d9a85a", "brown": "wood#8a4a26", "rod": "metal#8a8d90"})
# base frame of slats on the floor behind the board foot
d.box("fr-l", [0, 0, 40, 45, 40, 660], "frame", r=4, mirror="x")
d.box("fr-b", [0, 0, 40, W, 40, 85], "frame", r=4)
d.box("fr-f", [0, 0, 615, W, 40, 660], "frame", r=4)
d.cyl("fr-rod", [45, 26, 300], [W - 45, 26, 300], 14, "rod")
# the inclined board, drawn upright (front face at zF) and leaned back 25° about its foot
zF, T = 640, 18
TILT = 32
BR = rot("x", -TILT, [0, 0, zF])
cx = W / 2
arch = arc_pts(cx, 150, 70, 0, 180, 10)          # round-headed opening at the foot
out = [(60, 0), (cx - 70, 0)] + [(arch[-1][0], arch[-1][1] - 0)] + list(reversed(arch))[1:-1] + [(cx + 70, 150), (cx + 70, 0), (W - 60, 0), (W - 60, 780), (60, 780)]
pts = [(60, 0), (cx - 70, 0), (cx - 70, 150)] + [(cx + 70 * math.cos(math.radians(180 - 18 * i)), 150 + 70 * math.sin(math.radians(180 - 18 * i))) for i in range(1, 10)] + [(cx + 70, 150), (cx + 70, 0), (W - 60, 0), (W - 60, 780), (60, 780)]
d.slab("board", "front", poly(pts), [zF - T, zF], "ply", r=2, rot=BR)
d.box("head", [cx - 95, 730, zF - T - 10, cx + 95, 840, zF + 6], "dark", r=12, rot=BR)
# two thick green rolls with dark piping, each on a pale-green plate
for i, y0 in enumerate((620, 425)):
    d.box(f"plate{i}", [24, y0 - 6, zF, W - 24, y0 + 150, zF + 12], "pale", r=5, rot=BR)
    d.box(f"pad{i}", [20, y0, zF + 12, W - 20, y0 + 140, zF + 82], "pad", r=12, puff=2, rot=BR)
    d.box(f"pipe{i}", [18, y0 - 2, zF + 72, W - 18, y0 + 142, zF + 80], "pipe", r=4, rot=BR)
    d.box(f"pipe2{i}", [18, y0 - 2, zF + 14, W - 18, y0 + 142, zF + 20], "pipe", r=3, rot=BR)
# pale-green moulded knee block with a central ridge
d.box("knee", [15, 240, zF, W - 15, 385, zF + 60], "pale", r=12, rot=BR)
d.box("knee-ridge", [cx - 60, 245, zF + 30, cx + 60, 420, zF + 115], "pale", r=30, rot=BR)
# triangular prop behind the board to the base frame
def back(s): return (zF - T - s * math.sin(math.radians(TILT)), s * math.cos(math.radians(TILT)))
a, b = back(150), back(400)
d.slab("prop", "side", poly([(a[0], a[1]), (b[0], b[1]), (250, 40), (360, 40)]), [cx - 9, cx + 9], "frame", r=2)
# foot unit on the board's front face near its foot (photo: raised with the board, not on the floor):
# a long brown wooden roller across the full width with tan wooden rings round it, side plates holding its axle,
# and a thin light-wood rail in front of it with small clips at the ends
RY, RZ = 150, zF + 55                      # roller axis in the board's (upright) frame
d.box("ft-side", [0, RY - 55, zF, 22, RY + 45, RZ + 70], "lw", r=4, rot=BR, mirror="x")
d.cyl("roller", [22, RY, RZ], [W - 22, RY, RZ], 60, "brown", rot=BR)
for i, x in enumerate((130, 185, 245)):
    d.lathe(f"ring{i}", [x, RY, RZ], [[30, 0], [40, 4], [44, 16], [40, 28], [30, 32]], "ring", axis="x", rot=BR)
d.bar("ft-rail", [0, RY + 20, RZ + 62], [W, RY + 20, RZ + 62], [26, 12], "lw", r=3, rot=BR)
d.box("ft-clip", [30, RY - 10, RZ + 50, 44, RY + 36, RZ + 70], "lw", r=3, rot=BR, mirror="x")
d.save()
