"""kinesio-5: wall bars xy-7 (top curving forward) and xy-8 (straight rails + folded pull-up frame).
Wall at z = 0, rails stand on the floor (y = 0)."""
from k5lib import *

GREEN = "gloss#1f9a5a"
MATS = {"rail": GREEN, "wood": "gloss#e3a43a", "green": GREEN, "steel": "metal#c8ccce", "cap": "rubber#16171a",
        "nut": "plastic#1d1f22"}

# ---------------- xy-7 ----------------
W, DD, H = 970, 620, 2210
d = D("xy-7", [W, DD, H], dict(MATS, wood="gloss#d3a02a", green="gloss#0c7d68"))  # photo: golden wood, teal rungs
RW = 46            # rail section (x)
ZR = 95            # rail centre z (straight part)
YC = 1930          # curve starts
top_path = [[0, 0, ZR], [0, YC, ZR], [0, 2080, ZR + 70], [0, 2160, ZR + 240], [0, 2175, ZR + 330]]
for side, x in (("l", RW / 2), ("r", W - RW / 2)):
    pts = [[x, p[1], p[2]] for p in top_path]
    d.sweep(f"rail-{side}", pts, [RW, 56], "rail", shape="rect", r=6, bend=160)
    d.box(f"cap-{side}", [x - RW / 2 - 3, 2140, ZR + 320, x + RW / 2 + 3, 2210, ZR + 380], "cap", r=10)
    d.box(f"foot-{side}", [x - RW / 2 - 4, 0, ZR - 32, x + RW / 2 + 4, 8, ZR + 32], "cap", r=3)
    # wall brackets: green angle plates on the outside of the rails, at the bottom and near the top
    xo = x - RW / 2 - 4 if side == "l" else x + RW / 2
    for k, yb in enumerate((1800,)):
        # angle bracket: a side plate from the rail's outer face back to the wall, a wall plate behind the rail
        # reaching inward (stays inside the printed width)
        xo = x - RW / 2 if side == "l" else x + RW / 2 - 4
        d.box(f"brk-{side}{k}", [xo, yb - 40, 0, xo + 4, yb + 40, ZR], "rail", r=2)
        xi0, xi1 = (x - RW / 2, x + RW / 2 + 60) if side == "l" else (x - RW / 2 - 60, x + RW / 2)
        d.box(f"brk-plate-{side}{k}", [xi0, yb - 40, 0, xi1, yb + 40, 6], "rail", r=2)
# small white label on the right rail front (photo)
d.box("label", [W - RW + 6, 1640, ZR + 28, W - 6, 1690, ZR + 29.5], "plastic#f4f4f0", r=2, soft=True)
# rungs Ø30 between the rails: 5 wood, 5 green, 3 steel + 2 steel in the curved top
ys = [120 + 145 * k for k in range(13)]
for k, y in enumerate(ys):
    mat = "wood" if k < 5 else "green" if k < 10 else "steel"
    d.cyl(f"rung{k}", [RW, y, ZR], [W - RW, y, ZR], 30, mat)
    d.cyl(f"nut{k}", [RW - 2, y, ZR], [RW + 6, y, ZR], 36, "nut", copies=[[W - 2 * RW - 4, 0, 0]], soft=True)
for k, (y, z) in enumerate(((2050, ZR + 105), (2158, ZR + 300))):
    d.cyl(f"rung-top{k}", [RW, y, z], [W - RW, y, z], 30, "steel")
    d.cyl(f"clip-top{k}", [W / 2 - 40, y, z], [W / 2 + 40, y, z], 36, "metal#e2e4e6", soft=True)
d.save()

# ---------------- xy-8 ----------------
W, DD, H = 980, 580, 2310
d = D("xy-8", [W, DD, H], dict(MATS, rail="gloss#1a8c4c", wood="gloss#d8853a", green="gloss#16765a"))
RW, ZR = 48, 90
for side, x in (("l", RW / 2), ("r", W - RW / 2)):
    d.bar(f"rail-{side}", [x, 0, ZR], [x, H, ZR], [RW, 60], "rail", r=5)
    d.box(f"foot-{side}", [x - RW / 2, 0, ZR - 30, x + RW / 2, 8, ZR + 110], "rail", r=3)
    d.box(f"top-cap-{side}", [x - RW / 2 + 1, H - 6, ZR - 29, x + RW / 2 - 1, H, ZR + 29], "rail", r=4)
    xo = x - RW / 2 - 4 if side == "l" else x + RW / 2
    for k, yb in enumerate((350, 2000)):
        d.box(f"brk-{side}{k}", [xo, yb - 40, 0, xo + 4, yb + 40, ZR], "rail", r=2)
ys = [150 + 150 * k for k in range(14)]
for k, y in enumerate(ys):
    mat = "wood" if k < 5 else "green" if k < 10 else "steel"
    d.cyl(f"rung{k}", [RW, y, ZR], [W - RW, y, ZR], 30, mat)
    d.cyl(f"nut{k}", [RW - 2, y, ZR], [RW + 6, y, ZR], 36, "nut", copies=[[W - 2 * RW - 4, 0, 0]], soft=True)
# folded pull-up frame (as in the photo): two J side members hooked on the 1650 rung, a top bar along x in front,
# its left end sticking out past the left side member, and a wide green cross plate
XL, XR = 75, 895
YH, YT = 1650, 2010
ZB, ZT = ZR + 30, ZR + 150
for side, x in (("l", XL), ("r", XR)):
    d.tube(f"pu-side-{side}", [[x, YH - 30, ZR + 10], [x, YH - 30, ZB], [x, YT - 60, ZT - 10], [x, YT, ZT]],
           30, "rail", bend=40)
    d.tube(f"pu-hook-{side}", [[x, YH - 30, ZB], [x, YH - 30, ZR - 22], [x, YH + 25, ZR - 22]], 14, "rail", bend=12)
    d.box(f"pu-clamp-{side}", [x - 20, YH - 62, ZR + 4, x + 20, YH - 8, ZR + 44], "cap", r=6)  # black hook clamp
d.tube("pu-bar", [[14, YT, ZT], [XR - 60, YT, ZT], [XR, YT - 10, ZT]], 32, "rail", bend=50)
d.lathe("pu-bar-cap", [14, YT, ZT], [[0, 0], [17, 0], [17, 10], [0, 12]], "cap", axis="x",
        rot=rot("y", 180, [14, YT, ZT]))
d.box("pu-plate", [XL - 10, 1765, ZB + 30, XR + 10, 1865, ZB + 40], "rail", r=3, rot=rot("x", 25, [480, 1765, ZB + 35]))
d.save()
