# XDD-I UV sterilisation lamp on an X-base trolley: white U reflector with 2 quartz tubes on a telescopic pole — other-1
# (detail review 2026-10-03: X base on the diagonals with tapered arms, hooded castors with silver wheel discs, the
#  reflector hangs in front-left of the pole on a swivel arm to a plate on its back, REAHER logo in letters)
import math
from o_lib import *
W = 620
C = 310
d = D("xdd-i", [W, W, 1750], {
    "white": "plastic#f1f2f4", "blk": "plastic#1e1f22", "chrome": "chrome", "uv": "gloss#f2f8ff",
    "uvglass": "acrylic#9ed6ffa0", "cable": "rubber#7d8086", "silver": "metal#c3c7cc"})


def arm(p0, p1, r0, r1, n=10):
    """Tapered arm outline (top plane x/z): width 2*r0 at p0, rounded end of radius r1 at p1."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    pts = [(p0[0] + nx * r0, p0[1] + ny * r0)]
    a0 = math.atan2(ny, nx)
    for k in range(n + 1):
        a = a0 - math.pi * k / n
        pts.append((p1[0] + r1 * math.cos(a), p1[1] + r1 * math.sin(a)))
    pts.append((p0[0] - nx * r0, p0[1] - ny * r0))
    return poly(pts)


# X base: 4 arms on the diagonals (photo 1, seen from the front), wide at the hub, rounded ends; white top over a
# black under-layer; hooded castors with big silver wheel discs under the ends
o = 262
ends = [(C - o, C - o), (C + o, C - o), (C - o, C + o), (C + o, C + o)]
for i, e in enumerate(ends):
    d.slab(f"base-blk{i}", "top", arm((C, C), e, 66, 42), [64, 88], "blk", r=4)
    d.slab(f"base-top{i}", "top", arm((C, C), e, 64, 40), [88, 96], "white", r=3)
d.slab("base-mid", "top", circle(C, C, 88), [64, 96], "white", r=4)
for i, (x, z) in enumerate(ends):
    d.add(f"wheel{i}", "wheel", "rubber#232427", at=[x, 34, z], d=68, d2=34)
    d.cyl(f"disc{i}", [x - 18, 34, z], [x + 18, 34, z], 58, "silver")
    d.box(f"hood{i}", [x - 22, 40, z - 30, x + 22, 66, z + 26], "blk", r=12)
# hub and pole: black hub, white lower tube with a black clamp + lever, chrome upper tube
PZ = C
d.cyl("hub", [C, 94, PZ], [C, 126, PZ], 96, "blk")
d.cyl("hub-collar", [C, 126, PZ], [C, 160, PZ], 54, "blk")
d.cyl("pole-low", [C, 158, PZ], [C, 765, PZ], 36, "white")
d.cyl("clamp", [C, 745, PZ], [C, 778, PZ], 46, "blk")
# levers on the back-left (photo 2, seen from behind: right of the pole)
d.cyl("clamp-boss", [C - 6, 760, PZ - 16], [C - 12, 760, PZ - 30], 16, "blk")
d.tube("clamp-lever", [[C - 10, 760, PZ - 28], [C - 18, 735, PZ - 34], [C - 28, 688, PZ - 40]], 12, "blk", bend=15)
d.cyl("pole-up", [C, 775, PZ], [C, 1205, PZ], 30, "chrome")
# lamp: white U-channel reflector facing the front, hung in front-left of the pole (photo 1: the pole shows at its
# right edge; photo 2 from the back: the pole at the reflector's edge, the swivel arm to a plate on its back)
Z0, Z1 = PZ + 28, PZ + 92
X0, X1 = C - 98, C + 4
XC = (X0 + X1) / 2
Y0, Y1 = 660, 1750
d.sphere("swivel", [C, 1222, PZ], 44, "chrome")
d.cyl("swivel-arm", [C, 1222, PZ], [C - 30, 1222, Z0 - 6], 28, "chrome")
d.cyl("swivel-boss", [C - 30, 1222, Z0 - 10], [C - 30, 1222, Z0 - 2], 36, "chrome")
d.cyl("swivel-lbase", [C - 6, 1222, PZ - 18], [C - 12, 1222, PZ - 32], 16, "blk")
d.tube("swivel-lever", [[C - 10, 1222, PZ - 30], [C - 18, 1195, PZ - 36], [C - 28, 1145, PZ - 42]], 12, "blk", bend=15)
d.box("plate", [C - 62, 1175, Z0 - 3, C + 2, 1270, Z0 + 1], "white", r=4)
d.box("refl-back", [X0, Y0, Z0, X1, Y1, Z0 + 6], "white", r=2)
d.box("refl-side", [X0, Y0, Z0, X0 + 5, Y1, Z1 - 8], "white", r=2, copies=[[X1 - X0 - 5, 0, 0]])
d.box("cap", [X0 - 2, Y1 - 22, Z0 - 2, X1 + 2, Y1, Z1], "white", r=6, copies=[[0, Y0 - Y1 + 22, 0]])
for i, x in enumerate((XC - 22, XC + 22)):
    d.cyl(f"tube{i}", [x, Y0 + 22, Z1 - 32], [x, Y1 - 22, Z1 - 32], 13, "uv", soft=True)
    d.cyl(f"tubeg{i}", [x, Y0 + 22, Z1 - 32], [x, Y1 - 22, Z1 - 32], 21, "uvglass", soft=True)
# REAHER logo on the reflector back, upper part (photo 2): green / blue swirl over the grey word
ZB = Z0 - 0.6
d.decal("logo-g", [XC + 2, 1596, ZB], [20, 7], "back", "gloss#3fae49", soft=True, rot=rot("z", 18, [XC + 2, 1596, ZB]))
d.decal("logo-b", [XC - 2, 1584, ZB], [20, 7], "back", "gloss#2c8fd0", soft=True, rot=rot("z", 18, [XC - 2, 1584, ZB]))
d.decal("logo-c", [XC + 7, 1590, ZB], [6, 18], "back", "gloss#2fa6a0", soft=True)
n0 = len(d.d["parts"])
h = 10
L = text_len("REAHER", h)
text(d, "logo-t", "REAHER", [XC, 1560, ZB], h, "plastic#6b6f75", stroke=1.8)
for p in d.d["parts"][n0:]:   # read from behind: mirror about x, put on the back face
    p["at"][0] = round(XC + L / 2 - (p["at"][0] - XC), 1)
    p["face"] = "back"
    p["rot"] = {"axis": "z", "deg": -p["rot"]["deg"], "about": p["at"]}
# power cable: out of the reflector back above the plate, a loop out to the pole side, down along the pole to a plug
d.tube("cable", [[C - 40, 1320, Z0 - 2], [C - 20, 1340, PZ - 10], [C + 60, 1300, PZ - 30], [C + 40, 1100, PZ - 30],
                 [C + 22, 860, PZ - 22], [C + 20, 330, PZ - 20]], 11, "cable", bend=80, soft=True)
d.box("plug", [C + 8, 240, PZ - 32, C + 32, 330, PZ - 8], "blk", r=6)
d.save()
