"""xy-dgdx-i — multi-joint isokinetic dynamometer tower (kinesio-2)."""
import math
from k2lib import *
from p1lib import text, text_len

d = D("xy-dgdx-i", [700, 750, 1650], {
    "white": "gloss#f3f4f6", "trim": "plastic#5a5f66", "panel": "plastic#c3c6cb", "cyan": "gloss#38b4d6",
    "red": "gloss#d9363e", "grey": "plastic#a3a7ad", "black": "plastic#1b1c1f", "rubber": "rubber#202124",
    "chrome": "chrome", "steel": "metal#c9ccd0"})
CX, CZ = 330, 375
A, B, R = 255, 290, 78


def lobes(r, a=A, b=B):
    """4-lobe base outline (top plane x/z): round lobes over the castors joined by concave sides."""
    k = 0.5523 * r
    L = [(CX + a, CZ + b), (CX - a, CZ + b), (CX - a, CZ - b), (CX + a, CZ - b)]
    (x1, z1), (x2, z2), (x3, z3), (x4, z4) = L
    s = f"M {x1 + r} {z1 - 45} L {x1 + r} {z1} C {x1 + r} {z1 + k} {x1 + k} {z1 + r} {x1} {z1 + r} L {x1 - 45} {z1 + r} "
    s += f"Q {CX} {z1 + r - 110} {x2 + 45} {z2 + r} L {x2} {z2 + r} C {x2 - k} {z2 + r} {x2 - r} {z2 + k} {x2 - r} {z2} L {x2 - r} {z2 - 45} "
    s += f"Q {x2 - r + 120} {CZ} {x3 - r} {z3 + 45} L {x3 - r} {z3} C {x3 - r} {z3 - k} {x3 - k} {z3 - r} {x3} {z3 - r} L {x3 + 45} {z3 - r} "
    s += f"Q {CX} {z3 - r + 110} {x4 - 45} {z4 - r} L {x4} {z4 - r} C {x4 + k} {z4 - r} {x4 + r} {z4 - k} {x4 + r} {z4} L {x4 + r} {z4 + 45} "
    s += f"Q {x4 + r - 120} {CZ} {x1 + r} {z1 - 45} Z"
    return s


# --- base: white top skin over a dark grey trim, 4 castors under the lobes
d.slab("base-trim", "top", lobes(R + 6), [85, 135], "trim", r=14)
d.slab("base", "top", lobes(R), [128, 182], "white", r=18)
for sx in (-1, 1):
    for sz in (-1, 1):
        caster(d, f"castor{sx}{sz}", [CX + sx * A, 0, CZ + sz * B + 18], 60, "rubber#3b3d41")
# --- column: white rounded tower, thin red line by its front-left edge, red S logo + name
d.loft("column", [sec(178, 240, 290, 40, CX - 20, CZ), sec(690, 240, 290, 40, CX - 20, CZ)], "white")
d.box("red-line", [CX - 106, 200, CZ + 144.6, CX - 100, 680, CZ + 146], "red", soft=True)
d.cyl("s-logo", [CX + 20, 420, CZ + 144], [CX + 20, 420, CZ + 146.5], 48, "red", soft=True)
text(d, "s-logo-s", "S", [CX + 20 - 0.29 * 28, 420 - 14, CZ + 147.2], 28, "plastic#ffffff", stroke=5)
NAME, NH = "Sunnyou 翔宇", 15
text(d, "name", NAME, [CX + 20 - text_len(NAME, NH) / 2, 366, CZ + 146.2], NH, "red", stroke=2.6)
d.decal("name-sub", [CX + 20, 350, CZ + 146.2], [96, 5], "front", "plastic#9a9ea4", soft=True)
# --- head: big rounded box overhanging to the right (output side)
HX0, HX1, HY0, HY1, HZ0, HZ1 = 130, 590, 680, 985, 185, 565
d.box("head", [HX0, HY0, HZ0, HX1, HY1, HZ1], "white", r=70)
d.lathe("head-cup", [CX - 20, HY1 - 6, CZ + 60], [[0, 0], [70, 0], [70, 8], [0, 8]], "panel", soft=True)
# output face: light grey recessed panel, cyan rounded frame, black ring of holes, chrome shaft
d.box("panel", [HX1 - 6, HY0 + 25, HZ0 + 55, HX1 + 4, HY1 - 30, HZ1 - 55], "panel", r=30)
d.box("cyan", [HX1 + 2, 735, 290, HX1 + 8, 925, 460], "cyan", r=28)
d.box("cyan-in", [HX1 + 6, 750, 305, HX1 + 10, 910, 445], "plastic#eef0f2", r=20)
SY, SZ = 830, 375
d.lathe("ring", [HX1 + 8, SY, SZ], [[0, 0], [72, 0], [72, 8], [0, 8]], "black", axis="x")
d.lathe("ring-in", [HX1 + 14, SY, SZ], [[0, 0], [48, 0], [48, 4], [0, 4]], "plastic#e6e8ea", axis="x")
d.cyl("shaft", [HX1 + 14, SY, SZ], [HX1 + 70, SY, SZ], 46, "chrome")
# --- steering-wheel attachment on the shaft (plane y-z)
WX, RW = HX1 + 78, 168
rim = [[WX, SY + RW * math.sin(math.radians(a)), SZ + RW * math.cos(math.radians(a))] for a in range(0, 361, 15)]
d.tube("wheel-rim", rim, 32, "rubber")
d.cyl("wheel-hub", [WX - 14, SY, SZ], [WX + 14, SY, SZ], 118, "black")
for i, a in enumerate((0, 180, 270)):
    ra = math.radians(a)
    d.bar(f"spoke{i}", [WX, SY + 50 * math.sin(ra), SZ + 50 * math.cos(ra)], [WX, SY + (RW - 8) * math.sin(ra), SZ + (RW - 8) * math.cos(ra)],
          [16, 46], "black", r=6)
d.box("rim-mark", [WX - 18, SY + RW - 8, SZ - 8, WX + 18, SY + RW + 8, SZ + 8], "plastic#e8eaec", r=3, soft=True,
      copies=[[0, -RW - 30, RW - 60], [0, -RW - 30, -RW + 60]])
# --- grey loop handle on the left side, red S logo at its root
d.sweep("handle", [[HX0 + 20, 925, 430], [HX0 - 95, 925, 430], [HX0 - 95, 800, 430], [HX0 + 20, 800, 430]], [44, 32], "grey",
        r=10, bend=40)
d.cyl("handle-logo", [HX0 + 2, 790, 485], [HX0 - 3, 790, 485], 40, "red", soft=True)
text_side(d, "handle-logo-s", "S", [HX0 - 3.6, 790 - 9, 485 - 5.2], 18, "plastic#ffffff", face="left", stroke=3.2)
# --- chrome pole at the back of the head top, black collar, articulated monitor arm, 15.6" touch screen
PX, PZ = CX - 20, 255
d.cyl("pole", [PX, HY1 - 10, PZ], [PX, 1290, PZ], 40, "chrome")
d.cyl("pole-cap", [PX, 1290, PZ], [PX, 1296, PZ], 40, "steel")
d.cyl("collar", [PX, 1090, PZ], [PX, 1115, PZ], 52, "black")
d.cyl("collar-lever", [PX + 20, 1100, PZ], [PX + 55, 1080, PZ + 20], 10, "chrome")
# the arm swings out to the output (+x) side and back: the screen sits beyond the wheel side, turned ~50 deg to face
# the front-right (photo 1, taken from ~57 deg off the front)
d.sweep("arm1", [[PX, 1205, PZ], [PX + 90, 1218, PZ - 10], [PX + 170, 1238, PZ - 40]], [44, 56], "white", r=14, bend=60)
d.sweep("arm1-under", [[PX, 1183, PZ], [PX + 90, 1196, PZ - 10], [PX + 170, 1216, PZ - 40]], [38, 14], "black", r=6, bend=60)
d.cyl("joint", [PX + 175, 1190, PZ - 42], [PX + 175, 1300, PZ - 42], 50, "black")
d.bar("arm2", [PX + 175, 1290, PZ - 42], [PX + 180, 1440, PZ - 120], [46, 56], "white", r=14)
d.bar("arm2-under", [PX + 163, 1290, PZ - 36], [PX + 168, 1440, PZ - 114], [24, 50], "black", r=8)
d.box("tilt", [PX + 160, 1425, PZ - 160, PX + 210, 1485, PZ - 115], "black", r=8)
SCX, SCY, SCZ = 575, 1530, 150
R_ = rot("y", 50, [SCX, SCY, SCZ])
scr(d, "screen", [SCX - 195, SCY - 125, SCZ - 28, SCX + 195, SCY + 125, SCZ], "white", r=10, face="front", bezel=18, rot=R_)
d.decal("ui", [SCX, SCY, SCZ + 0.8], [350, 212], "front", "gloss#f6f8fb", soft=True, rot=R_)
d.decal("ui-side", [SCX - 160, SCY, SCZ + 1.4], [22, 200], "front", "gloss#4c9be0", soft=True, rot=R_)
d.decal("ui-head", [SCX + 10, SCY + 80, SCZ + 1.4], [300, 18], "front", "gloss#4c9be0", soft=True, rot=R_)
for i in range(3):
    for j in range(2):
        d.decal(f"ui-tile{i}{j}", [SCX - 80 + i * 90, SCY + 30 - j * 75, SCZ + 1.4], [70, 50], "front",
                "gloss#9cc8f0" if (i, j) != (0, 0) else "gloss#3f8ee0", soft=True, rot=R_)
d.decal("ui-btn", [SCX + 150, SCY - 88, SCZ + 1.4], [30, 14], "front", "gloss#e04848", soft=True, rot=R_)
d.save()
