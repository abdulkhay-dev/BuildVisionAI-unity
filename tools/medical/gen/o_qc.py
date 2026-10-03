# XY-QC-I multifunctional debridement cart: white cabinet with front module, head with top screen, cups, shelves,
# IV pole, grey spider legs — other-1
from o_lib import *
d = D("xy-qc-i", [600, 600, 1900], {
    "white": "plastic#f3f4f6", "grey": "plastic#9aa0a8", "band": "plastic#4a4e55", "dark": "plastic#3a3f46",
    "blue": "gloss#2f8fd8", "deck": "plastic#b9bec5", "pole": "metal#c4c8cd", "chrome": "chrome",
    "bottle": "acrylic#6c747db8", "cav": "plastic#3b3e44", "glass": "acrylic#4a505860"})
X0, X1 = 75, 475          # cabinet
Z0, Z1 = 60, 540
CX = (X0 + X1) / 2
CZ = (Z0 + Z1) / 2
YB, YT = 110, 840         # lower cabinet
ZF = 500                  # behind the front module
# grey spider legs from the cabinet corners to white castors
for i, (cx, cz, lx, lz) in enumerate(((X0 + 40, Z0 + 40, 32, 34), (X1 - 40, Z0 + 40, 518, 34),
                                      (X0 + 40, Z1 - 40, 32, 566), (X1 - 40, Z1 - 40, 518, 566))):
    d.bar(f"leg{i}", [cx, 128, cz], [lx, 98, lz], [52, 34], "grey", r=10)
    d.cyl(f"leg-end{i}", [lx, 112, lz], [lx, 84, lz], 46, "grey")
    caster(d, f"castor{i}", [lx, 0, lz], 75, "plastic#eceef0")
d.box("plinth", [X0 + 20, 100, Z0 + 20, X1 - 20, 125, Z1 - 20], "grey", r=10)
# lower cabinet: core + two rounded front columns
# (the core steps back behind the bottle window: a real cavity, so the bottle can be round)
ZC = 405
for nm, ya, yb, zf in (("core-lo", YB, 229, ZF), ("core-mid", 229, 527, ZC), ("core-hi", 527, YT, ZF)):
    d.loft(nm, [sec(ya, X1 - X0, zf - Z0, 45, CX, (Z0 + zf) / 2), sec(yb, X1 - X0, zf - Z0, 45, CX, (Z0 + zf) / 2)], "white")
for i, (a, b) in enumerate(((X0, X0 + 62), (X1 - 62, X1))):
    d.loft(f"col{i}", [sec(YB, b - a, 120, 30, (a + b) / 2, Z1 - 60), sec(YT, b - a, 120, 30, (a + b) / 2, Z1 - 60)], "white")
# front module: knob + gauge panel, drawer with slot handle, door with the bottle window (hole)
MX0, MX1 = X0 + 62, X1 - 62
win = rr(MX0 + 22, 231, MX1 - 22, 525, 14)
d.slab("door", "front", rr(MX0, YB + 20, MX1, 597, 4) + " " + win, [ZF, Z1 - 4], "white", r=2)
d.box("drawer", [MX0, 600, ZF, MX1, 727, Z1 - 4], "white", r=3)
d.box("knobpanel", [MX0, 730, ZF, MX1, YT, Z1 - 4], "white", r=3)
d.box("cav-wall", [X0, 225, ZC - 50, MX0, 531, Z1 - 100], "white", copies=[[MX1 - X0, 0, 0]])
# dark-lined cavity behind the window with the grey glass jar (photo 1: round body, shoulders, wide neck with a lip)
# and a second jar half hidden at the left
d.box("cav-back", [MX0, 229, ZC - 2, MX1, 527, ZC + 2], "cav")
d.box("cav-floor", [MX0, 226, ZC, MX1, 232, ZF + 4], "cav")
d.box("cav-top", [MX0, 524, ZC, MX1, 529, ZF + 4], "cav")
d.box("cav-side", [MX0, 229, ZC, MX0 + 4, 527, ZF + 4], "cav", copies=[[MX1 - MX0 - 4, 0, 0]])
BZ = 462
d.loft("bottle", [sec(232, 150, 100, 48, CX + 10, BZ), sec(242, 166, 112, 54, CX + 10, BZ), sec(420, 166, 112, 54, CX + 10, BZ),
                  sec(452, 122, 96, 46, CX + 10, BZ), sec(466, 100, 86, 42, CX + 10, BZ), sec(482, 100, 86, 42, CX + 10, BZ)],
       "bottle", soft=True)
d.loft("bottle-lip", [sec(482, 122, 100, 48, CX + 10, BZ), sec(500, 122, 100, 48, CX + 10, BZ)], "bottle", soft=True)
d.loft("bottle2", [sec(232, 120, 90, 44, MX0 + 40, ZC + 50), sec(420, 120, 90, 44, MX0 + 40, ZC + 50),
                   sec(452, 90, 76, 36, MX0 + 40, ZC + 50)], "bottle", soft=True)
d.box("window-glass", [MX0 + 22, 231, Z1 - 7, MX1 - 22, 525, Z1 - 6], "glass", soft=True)
d.box("slot", [MX0 + 12, 588, Z1 - 5, MX1 - 12, 612, Z1 - 1], "dark", r=11)
d.box("label", [CX - 12, 640, Z1 - 4.5, CX + 12, 646, Z1 - 3.5], "blue", soft=True)
d.lathe("knob-ring", [CX - 50, 783, Z1 - 4], [[0, 0], [30, 0], [30, 3], [0, 3]], "blue", axis="z")
d.lathe("knob", [CX - 50, 783, Z1 - 1], [[0, 0], [24, 0], [24, 10], [21, 16], [0, 16]], "white", axis="z")
d.box("knob-grip", [CX - 54, 768, Z1 + 10, CX - 46, 798, Z1 + 18], "white", r=3)
d.box("gauge", [CX + 18, 750, Z1 - 4, CX + 82, 814, Z1 + 4], "plastic#cfd5db", r=4)
d.lathe("gauge-face", [CX + 50, 782, Z1 + 4], [[0, 0], [26, 0], [26, 1.5], [0, 1.5]], "gloss#d9ecf7", axis="z", soft=True)
d.box("gauge-needle", [CX + 49, 782, Z1 + 5.6, CX + 51, 804, Z1 + 6.4], "black", soft=True)
# blue light strips on both sides
d.box("strip-l", [X0 - 1.5, 330, CZ - 4, X0 + 1, 708, CZ + 4], "blue", soft=True)
d.box("strip-r", [X1 - 1, 330, CZ - 4, X1 + 1.5, 708, CZ + 4], "blue", soft=True)
# band and head (slightly larger, rounded), light grey deck with the flush screen
d.loft("band", [sec(836, X1 - X0 + 8, Z1 - Z0 + 8, 52, CX, CZ), sec(856, X1 - X0 + 8, Z1 - Z0 + 8, 52, CX, CZ)], "band")
d.loft("head", [sec(854, X1 - X0 + 10, Z1 - Z0 + 10, 55, CX, CZ), sec(978, X1 - X0 + 10, Z1 - Z0 + 10, 55, CX, CZ),
                sec(992, X1 - X0, Z1 - Z0, 50, CX, CZ)], "white")
d.loft("deck", [sec(990, X1 - X0 - 2, Z1 - Z0 - 2, 49, CX, CZ), sec(1000, X1 - X0 - 18, Z1 - Z0 - 18, 42, CX, CZ)], "deck")
screen(d, "screen", [CX - 105, 999, 345, CX + 125, 1003, 505], "dark", r=6, face="top", print="med_xy-qc-i_screen", bezel=6)
# logo badge on the head front: white plate, blue outline, blue 翔宇医疗
BY = 914
d.slab("badge-ring", "front", rr(CX - 52, BY - 18, CX + 52, BY + 18, 16) + " " + rr(CX - 48, BY - 14, CX + 48, BY + 14, 13),
       [Z1 + 4, Z1 + 6], "blue", soft=True)
text(d, "badge", "翔宇医疗", [CX - 36, BY - 7, Z1 + 5.6], 15, "blue", stroke=1.8, gap=0.12)
# handpiece holder cups at the front-left of the head, with white handpieces
for i, z in enumerate((Z1 - 70, Z1 - 175)):
    d.box(f"cup{i}", [X0 - 62, 885, z - 36, X0 + 2, 975, z + 36], "grey", r=12)
    d.box(f"cup-in{i}", [X0 - 54, 960, z - 28, X0 - 6, 976, z + 28], "dark", r=8, soft=True)
# right side: two white shelves (upper one with 3 handpieces / syringe), pale blue light between, IV pole
for i, y in enumerate((968, 772)):
    d.slab(f"shelf{i}", "top", rr(X1 - 10, 250, X1 + 112, Z1 - 10, 24), [y, y + 14], "white", r=5)
    d.box(f"shelf-lip{i}", [X1 + 100, y + 10, 252, X1 + 112, y + 26, Z1 - 12], "white", r=5)
d.box("glow", [X1 - 0.5, 786, 300, X1 + 1.5, 830, Z1 - 30], "acrylic#bfe3ff90", soft=True)
for i, (x, z, h, dd) in enumerate(((X1 + 40, 420, 150, 26), (X1 + 72, 460, 120, 22), (X1 + 40, 500, 135, 24))):
    d.cyl(f"tool{i}", [x, 982, z], [x, 982 + h, z], dd, "white")
    d.cyl(f"tool-tip{i}", [x, 982 + h, z], [x, 982 + h + 22, z], dd * 0.45, "plastic#d9dce0")
    d.tube(f"tool-cord{i}", [[x, 982, z], [x - 4, 900, z + 4], [x - 6, 786, z + 6]], 7, "plastic#eef0f2", bend=40, soft=True)
PX, PZ = X1 + 52, 300
d.cyl("pole", [PX, 786, PZ], [PX, 1872, PZ], 16, "pole")
d.cyl("pole-clamp", [PX, 960, PZ], [PX, 1000, PZ], 26, "white")
d.sphere("hook-hub", [PX, 1874, PZ], 22, "chrome")
for i, (dx, dz) in enumerate(((1, 0), (-1, 0), (0, 1), (0, -1))):
    d.tube(f"hook{i}", [[PX, 1874, PZ], [PX + dx * 70, 1878, PZ + dz * 70], [PX + dx * 92, 1892, PZ + dz * 92],
                        [PX + dx * 80, 1900, PZ + dz * 80]], 6, "chrome", bend=12)
# rear: power panel in the head (socket + green switch), two dark slots under the band
d.box("power", [CX - 70, 900, Z0 - 7, CX + 60, 950, Z0 + 2], "dark", r=6)
d.box("power-sock", [CX - 20, 912, Z0 - 9, CX + 4, 938, Z0 - 6], "black", r=2)
d.box("power-sw", [CX + 22, 910, Z0 - 10, CX + 46, 940, Z0 - 6], "gloss#29b34a", r=2)
d.box("slot-r", [CX - 110, 770, Z0 - 4, CX + 110, 802, Z0 + 2], "dark", r=15, copies=[[0, -62, 0]])
d.save()
