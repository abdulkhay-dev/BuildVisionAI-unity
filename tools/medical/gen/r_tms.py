"""tms-navigation-robot (batch robot-2): TMS navigation robot. A white C-arch (side profile traced from the side photo):
column at the back on small castors with a perforated grille low on its sides, curving forward over the patient's
head; blue accent line along the outer edge, red e-stop near the top; S logo, lettering and a hatch on the inner
(front) face. A white 6-axis cobot hangs under the arch holding the TMS coil, its grey cable running down to the
dark-grey host cart beside the arch (+x): stacked vented boxes, a tray with an e-stop, a monitor."""
from r_lib import *

W, DP, H = 940, 1000, 1972
AX0, AX1 = 0, 560                     # arch width (x); review 2026-10-03: 480 -> 560, the photo column is about as wide as the cart
d = D("tms-navigation-robot", [W, DP, H], {
    "white": "gloss#eef0f2", "blue": "gloss#2f8fd8", "red": "gloss#d42a26", "grey": "plastic#a9aeb5",
    "dark": "plastic#4a4f57", "black": "plastic#2a2d31", "grille": "plastic#7d838b", "rubber": "rubber#3a3d42",
    "box": "plastic#e3e6ea", "ui": "gloss#eef3f8", "brain": "gloss#d9733a", "cam": "plastic#3a3d42",
    "cable": "plastic#c9cdd2", "hatch": "plastic#f6f7f8"})
ARCH = ("M 0 120 L 0 700 C 0 1300 120 1600 280 1765 C 420 1890 600 1940 950 1972 Q 995 1960 975 1915 "
        "Q 950 1878 835 1868 C 650 1840 480 1700 418 1578 C 330 1400 250 1200 255 1044 L 267 700 "
        "C 280 450 450 300 690 170 L 700 120 Z")
d.slab("arch", "side", ARCH, [AX0, AX1], "white", r=60)
d.box("plinth", [AX0 + 20, 70, 10, AX1 - 20, 125, 690], "white", r=20)
d.caster("castor", [70, 0, 80], 60, "rubber", copies=[[420, 0, 0], [0, 0, 540], [420, 0, 540]])
# blue accent line along the outer edge on both sides (a thin tube just proud of the side faces)
edge = [[0, 30, 160], [0, 30, 700], [0, 50, 1150], [0, 130, 1500], [0, 290, 1735], [0, 450, 1860], [0, 650, 1920],
        [0, 930, 1942]]
for k, x in enumerate((AX0 - 1, AX1 + 1)):
    d.tube(f"blue-line-{k}", [[x, y, z] for _, z, y in edge], 5, "blue", bend=120, soft=True)
d.sphere("estop", [(AX0 + AX1) / 2 + 150, 1790, 235], 46, "red")
# perforated grille low on both sides
for k, x in enumerate((AX0 - 1.5, AX1)):
    d.box(f"grille-{k}", [x, 150, 60, x + 1.5, 420, 470], "white", soft=True)
    d.box(f"grille-dot-{k}", [x - 0.5 if k == 0 else x + 1.5, 170, 80, x if k == 0 else x + 2, 182, 92], "grille", soft=True,
          repeat=rep(16, [0, 0, 24]), copies=[[0, 26 * j, 0] for j in range(1, 10)])
# inner (front) face of the column: S logo, lettering, hatch, a round button
FZ = 258
d.cyl("logo", [280, 1150, FZ], [280, 1150, FZ + 3], 70, "blue")
text(d, "logo-s", "S", [267, 1128, FZ + 3.5], 44, "white", stroke=8)
text(d, "brand", "SUNNYOU 翔宇", [180, 1050, FZ + 1], 26, "blue", stroke=4)
d.box("hatch", [170, 700, FZ + 4, 390, 920, FZ + 14], "hatch", r=20)
d.box("hatch-grip", [245, 850, FZ + 14, 315, 870, FZ + 16], "black", r=6)
d.lathe("button", [280, 1340, FZ - 10], [[0, 0], [20, 0], [20, 28], [0, 30]], "grey", axis="z")
d.box("depth-cam", [180, 1832, 860, 380, 1866, 930], "cam", r=10)
# --- cobot (review 2026-10-03, photo 1): hung under the arch top, the upper arm runs back and down to a tall
#     vertical elbow joint near the column, the forearm reaches forward horizontally, the wrist turns down to the
#     holder and the flat white figure-8 coil lies face-down over the patient's head (elbow-up, stretched pose)
AXC = 280
d.cyl("j1", [AXC, 1842, 640], [AXC, 1720, 640], 120, "white")
d.cyl("j1-ring", [AXC, 1745, 640], [AXC, 1735, 640], 124, "grey")
d.cyl("j2", [AXC - 75, 1690, 640], [AXC + 75, 1690, 640], 112, "white")
d.cyl("upper-arm", [AXC + 45, 1690, 640], [AXC + 45, 1560, 420], 88, "white")
d.cyl("j3", [AXC - 20, 1560, 420], [AXC + 110, 1560, 420], 100, "white")
d.cyl("elbow", [AXC + 45, 1400, 400], [AXC + 45, 1600, 400], 130, "white")
d.cyl("elbow-cap", [AXC + 45, 1600, 400], [AXC + 45, 1620, 400], 122, "grey")
d.cyl("forearm", [AXC + 45, 1480, 430], [AXC + 45, 1480, 760], 78, "white")
d.cyl("j4", [AXC - 15, 1480, 780], [AXC + 100, 1480, 780], 86, "white")
d.cyl("j5", [AXC + 10, 1490, 800], [AXC + 10, 1380, 800], 78, "white")
d.cyl("j-ring", [AXC + 10, 1420, 800], [AXC + 10, 1410, 800], 84, "grey")
d.cyl("holder", [AXC + 10, 1380, 800], [AXC + 10, 1350, 880], 40, "grey")
d.add("coil", "sphere", "white", at=[AXC + 10, 1330, 930], radii=[125, 24, 70])
d.add("coil-face", "sphere", "grey", at=[AXC + 10, 1312, 930], radii=[110, 8, 58])
d.tube("coil-cable", [[AXC + 10, 1385, 820], [AXC + 60, 1250, 860], [AXC + 70, 800, 780], [AXC + 160, 520, 640],
                      [600, 560, 560]], 30, "cable", bend=160, soft=True)
# --- host cart beside the arch (+x)
CX0, CX1, CZ0, CZ1 = 580, 930, 220, 780
cxm, czm = (CX0 + CX1) / 2, (CZ0 + CZ1) / 2
d.bar("cart-foot", [cxm, 60, CZ0 - 20], [cxm, 60, CZ1 + 20], [80, 50], "dark", r=10)
d.bar("cart-foot-x", [CX0 - 10, 60, czm], [CX1 + 10, 60, czm], [80, 50], "dark", r=10)
d.caster("cart-castor", [cxm, 0, CZ0 - 10], 60, "rubber", copies=[[0, 0, CZ1 - CZ0 + 20]])
d.caster("cart-castor-x", [CX0, 0, czm], 60, "rubber", copies=[[CX1 - CX0, 0, 0]])
d.box("cart-col", [cxm - 35, 85, czm - 35, cxm + 35, 1050, czm + 35], "black", r=6)
d.box("box-low", [CX0, 300, CZ0 + 20, CX1, 640, CZ1 - 20], "box", r=12)
d.box("box-up", [CX0, 660, CZ0 + 20, CX1, 900, CZ1 - 20], "box", r=12)
# vents on the FRONT face as in photo 1: two big grille fields on the lower box, a vent field left of the LED panel
for k, (y0, y1) in enumerate(((330, 470), (490, 620))):
    d.box(f"vent-{k}", [CX0 + 30, y0, CZ1 - 20, CX1 - 120, y1, CZ1 - 18.5], "grille", r=20, soft=True)
d.box("vent-up", [CX0 + 20, 700, CZ1 - 20, CX0 + 150, 860, CZ1 - 18.5], "grille", r=10, soft=True)
d.box("led-panel", [CX0 + 170, 700, CZ1 - 20, CX1 - 40, 860, CZ1 - 18], "black", r=6)
d.box("led", [CX0 + 250, 720, CZ1 - 18, CX0 + 232, 840, CZ1 - 17], "blue", soft=True, repeat=rep(5, [18, 0, 0]))
d.box("tray", [CX0 - 20, 1040, CZ0 - 10, CX1 + 10, 1065, CZ1 + 10], "dark", r=8)
d.box("keyboard", [CX0 + 30, 1065, CZ0 + 40, CX1 - 40, 1080, CZ0 + 300], "box", r=6)
d.lathe("cart-estop", [CX0 + 60, 1065, CZ1 - 60], [[0, 0], [22, 0], [22, 18], [30, 22], [30, 38], [0, 40]], "red")
d.cyl("mon-pole", [cxm, 1065, czm + 120], [cxm, 1120, czm + 120], 30, "black")
d.box("monitor", [CX0 + 10, 1110, czm + 120, CX1 - 10, 1370, czm + 160], "white", r=10)
d.box("monitor-ui", [CX0 + 25, 1125, czm + 160, CX1 - 25, 1355, czm + 162], "ui", r=4)
d.cyl("monitor-brain", [CX1 - 100, 1250, czm + 162], [CX1 - 100, 1250, czm + 163.5], 90, "brain")
d.box("monitor-bar", [CX0 + 25, 1340, czm + 162, CX1 - 25, 1355, czm + 163.5], "blue", soft=True)
d.save()
