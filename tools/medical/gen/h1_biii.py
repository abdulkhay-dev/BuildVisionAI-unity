from h1lib import *
# XY-SL-BIII deep lower-limb tub: D-plan tub (square left end, round right end), wide flat rim with a thicker platform
# at the left end, hand shower on a slide bar at the front left, water inside; two-step block at the left
d = D("xy-sl-biii", [1300, 700, 1000], {
    "shell": "gloss#f7f8f9", "inner": "gloss#eef2f5", "water": "acrylic#cfe9f2a8", "line": "plastic#dfe3e8",
    "step": "plastic#f4f5f6", "dark": "black#2a2d31", "blue": "gloss#3a7fd0"})
X0, X1, Z0, Z1 = 560, 1290, 60, 640
RY, RT = 905, 55
d.slab("body", "top", ring(rr(X0 + 10, Z0 + 10, X1 - 10, Z1 - 10, [280, 280, 30, 30]), rr(705, 100, 1255, 600, [245, 245, 55, 55])), [20, RY + 2], "shell", r=12)
hole = rr(720, 115, 1240, 585, [230, 230, 50, 50])
tub(d, "", None, hole, rr(X0 - 25, Z0 - 30, X1 + 10, Z1 + 30, [310, 310, 25, 25]), RY, RT, 300,
    rr(705, 100, 1255, 600, [245, 245, 55, 55]), water=RY - 45)
d.slab("base", "top", P(rr(X0 + 40, Z0 + 40, X1 - 50, Z1 - 40, [240, 240, 20, 20])), [0, 30], "shell", r=8)
# vertical facet lines on the front
d.box("facet", [600, 60, Z1 - 11, 604, 880, Z1 - 7], "line", copies=[[400, 0, -10]], soft=True)
# hand shower on the LEFT END face near the back corner (photo): slide bar, handset, round valve, two hoses down
# behind the step block. Review 2026-10-02: moved from the front face; seat platform on the left end rim added.
EX = X0 + 6
d.cyl("bar", [EX - 16, 600, 160], [EX - 16, 890, 160], 20, "chrome")
d.box("bar-clip", [EX - 30, 590, 145, EX, 615, 175], "chrome", r=6, copies=[[0, 290, 0]])
d.box("holder", [EX - 48, 815, 145, EX - 14, 845, 175], "chrome", r=8)
d.cyl("handset", [EX - 45, 740, 160], [EX - 45, 900, 160], 30, "chrome", d2=36)
d.decal("handset-strip", [EX - 63, 845, 160], [8, 60], "left", "blue", soft=True)
d.lathe("valve", [EX, 860, 270], [[0, 0], [30, 0], [30, 6], [20, 16], [8, 22], [0, 22]], "chrome", axis="x",
        rot=rot("y", 180, [EX, 860, 270]))
d.tube("hose", [[EX - 45, 740, 160], [EX - 40, 520, 120], [EX - 30, 450, 90], [EX - 20, 470, 60]], 12, "chrome", bend=80, soft=True)
d.tube("hose2", [[EX - 20, 845, 270], [EX - 25, 600, 280], [EX - 20, 445, 290]], 12, "chrome", bend=80, soft=True)
# vertical facet lines on the left end corner
d.box("facet-l", [X0 + 6, 60, Z1 - 60, X0 + 10, 880, Z1 - 56], "line", soft=True)
# seat platform on the left end rim (the patient sits on it)
d.slab("seat", "top", P(rr(X0 - 25, Z0 - 30, 735, Z1 + 30, [20, 20, 25, 25])), [RY + 5, RY + RT + 20], "shell", r=24)
# two-step block at the left (upper step against the tub)
d.slab("steps", "front", "M 0 0 L 555 0 L 555 440 L 280 440 L 280 220 L 0 220 Z", [80, 640], "step", r=30)
d.save()
