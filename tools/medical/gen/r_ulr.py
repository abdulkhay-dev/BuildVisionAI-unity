"""upper-limb-rehab-robot (batch robot-1): seated arm exoskeleton. The patient sits in the white egg chair facing
the front (+z); the brushed telescopic column stands right behind the chair on the back arm of a white L floor frame
whose front arm runs along the patient's left side (+x); on the column a tall white box with a grey end cap on its +x
end; a white boom rises from the box and reaches over the patient's right shoulder (-x) to a white post with a black
cap, from which the aluminium exoskeleton hangs: shoulder plate, parallel chrome links, elbow plate with its motor,
the flat forearm bar with the black cuff trough, the black vertical grip and the bent hand frame.
Review 2026-10-03: chair rebuilt as smooth lofts (domed bowl, a back lofted across x with rounded shoulders, wings
lofted along z with the sloping rounded rim), layout moved so the column is behind the chair as in the photo,
exoskeleton redrawn from the photo's flat bolted plates, round links and the elbow motor."""
import math
from r_lib import *


def poly(pts):
    return "M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in pts) + " Z"


W, DP, H = 1050, 1100, 1650
d = D("upper-limb-rehab-robot", [W, DP, H], {
    "white": "gloss#f4f5f6", "alu": "metal#c9ccd0", "alu2": "metal#b5bac0", "chrome": "chrome", "grey": "metal#8d9196",
    "black": "plastic#1e2023", "pad": "leather#202226", "cap": "plastic#8a8d93", "rubber": "rubber#2b2d30",
    "chair": "leather#f6f6f4", "bolt": "metal#7d8288", "frame": "gloss#f2f3f4"})
# --- L floor frame: back arm along x behind the chair, front arm along the patient's left side; castors
FY = 95
d.box("frame-back", [520, 40, 85, 1035, FY, 245], "frame", r=14)
d.box("frame-side", [905, 40, 85, 1035, FY, 1060], "frame", r=14)
d.caster("castor", [970, 0, 1005], 75, "rubber", copies=[[0, 0, -870], [-400, 0, -870]])
# --- telescopic brushed column (three stages) right behind the chair; the tall white box with the grey end cap
CX, CZ = 620, 150
d.box("col-foot", [CX - 135, FY, CZ - 95, CX + 135, FY + 30, CZ + 95], "frame", r=8)
d.box("col-low", [CX - 115, FY + 30, CZ - 90, CX + 115, 720, CZ + 90], "alu", r=8)
d.box("col-low-band", [CX - 117, 690, CZ - 92, CX + 117, 720, CZ + 92], "alu2", r=6)
d.box("col-mid", [CX - 92, 720, CZ - 72, CX + 92, 940, CZ + 72], "alu", r=6)
d.box("col-neck", [CX - 70, 940, CZ - 58, CX + 70, 1062, CZ + 58], "alu2", r=6)
d.box("col-joint", [CX - 40, 990, CZ + 50, CX + 40, 1050, CZ + 70], "grey", r=6)
d.box("box", [430, 1060, CZ - 85, 1040, 1380, CZ + 85], "white", r=22)
d.box("box-cap", [1000, 1072, CZ - 78, 1046, 1368, CZ + 78], "cap", r=10)
d.box("box-seam", [430, 1372, CZ - 86, 1000, 1376, CZ + 86], "black", soft=True)
# --- boom: rises from the box's -x end, then reaches over the patient's right shoulder to the white post
PX, PZ = 350, 460
d.box("boom-foot", [470, 1378, CZ - 40, 560, 1420, CZ + 40], "white", r=8)
d.sweep("boom", [[515, 1400, CZ], [515, 1585, CZ + 10], [PX + 35, 1585, PZ]], [62, 52], "white", bend=90, r=10)
d.cyl("post", [PX, 1450, PZ], [PX, 1615, PZ], 60, "white")
d.cyl("post-cap", [PX, 1615, PZ], [PX, 1650, PZ], 64, "black")
d.box("post-clamp", [PX - 42, 1430, PZ - 48, PX + 42, 1495, PZ + 48], "white", r=8)
d.lathe("clamp-knob", [PX - 42, 1462, PZ], [[0, 0], [8, 0], [8, 10], [16, 14], [16, 30], [0, 32]], "black", axis="x",
        rot=rot("y", 180, [PX - 42, 1462, PZ]))
# --- exoskeleton: brushed flat plates with bolts, round parallel links, elbow plate and motor, forearm bar, cuff, grip
XA = PX - 20                                      # plane of the arm plates
d.box("shoulder-plate", [XA - 8, 1215, PZ - 30, XA + 8, 1440, PZ + 30], "alu", r=4)
d.cyl("shoulder-bolt", [XA - 12, 1250, PZ - 14], [XA + 12, 1250, PZ - 14], 11, "bolt",
      copies=[[0, 0, 28], [0, 150, 0], [0, 150, 28], [0, 75, 14]])
EZ = 720
for k, y in enumerate((1395, 1290)):
    d.cyl(f"link-{k}", [XA - 30, y, PZ + 10], [XA - 30, y - 15, EZ - 12], 20, "chrome")
    d.box(f"link-head-{k}", [XA - 46, y - 16, PZ - 6, XA - 12, y + 16, PZ + 30], "alu2", r=4)
    d.box(f"link-tail-{k}", [XA - 46, y - 31, EZ - 30, XA - 12, y + 1, EZ + 4], "alu2", r=4)
d.box("link-bracket", [XA - 52, 1270, PZ + 120, XA - 10, 1420, PZ + 150], "alu", r=4)
d.cyl("link-bracket-bolt", [XA - 56, 1300, PZ + 135], [XA - 6, 1300, PZ + 135], 11, "bolt", copies=[[0, 90, 0]])
d.box("elbow-plate", [XA - 70, 1190, EZ - 10, XA - 54, 1420, EZ + 40], "alu", r=4)
d.cyl("elbow-bolt", [XA - 74, 1240, EZ + 15], [XA - 50, 1240, EZ + 15], 11, "bolt", copies=[[0, 120, 0]])
d.cyl("elbow-motor", [XA - 62, 1100, EZ + 15], [XA - 62, 1195, EZ + 15], 54, "alu2")
d.cyl("elbow-motor-ring", [XA - 62, 1085, EZ + 15], [XA - 62, 1105, EZ + 15], 46, "black")
d.tube("elbow-cable", [[XA - 62, 1090, EZ + 15], [XA - 110, 1120, EZ - 20], [XA - 90, 1230, EZ - 50], [XA - 50, 1300, EZ - 60]],
       8, "black", bend=40, soft=True)
d.bar("spring-bar", [XA - 2, 1420, PZ + 20], [XA - 2, 1600, PZ + 180], [16, 46], "alu", r=4)
d.bar("spring-slot", [XA - 11, 1450, PZ + 52], [XA - 11, 1580, PZ + 168], [3, 12], "black", r=1, soft=True)
d.bar("forearm", [XA - 62, 1330, EZ + 30], [XA - 62, 1330, EZ + 330], [22, 62], "alu", r=5)
FZ = EZ + 120
d.slab("cuff", "front", poly([(XA - 62 + 66 * math.cos(math.pi + math.pi * k / 12), 1430 + 66 * math.sin(math.pi + math.pi * k / 12))
                               for k in range(13)] + [(XA - 62 + 66, 1470), (XA - 62 + 56, 1470)] +
                              [(XA - 62 + 56 * math.cos(-math.pi * k / 12), 1430 + 56 * math.sin(-math.pi * k / 12)) for k in range(13)] +
                              [(XA - 62 - 56, 1490), (XA - 62 - 66, 1490)]), [FZ, FZ + 150], "pad", r=4)
d.box("cuff-seat", [XA - 82, 1358, FZ + 40, XA - 42, 1366, FZ + 110], "black")
GZ = EZ + 270
d.box("grip-base", [XA - 90, 1345, GZ - 30, XA - 34, 1375, GZ + 30], "alu2", r=6)
d.cyl("grip", [XA - 62, 1375, GZ], [XA - 62, 1540, GZ], 42, "black")
d.sphere("grip-top", [XA - 62, 1540, GZ], 42, "black")
d.box("grip-clamp", [XA - 85, 1290, GZ - 25, XA - 40, 1320, GZ + 25], "black", r=6)
d.sweep("hand-frame", [[XA - 62, 1330, EZ + 320], [XA - 62, 1330, EZ + 370], [XA - 110, 1300, EZ + 400],
                       [XA - 165, 1335, EZ + 390]], [16, 40], "alu", bend=35, r=4)
d.cyl("hand-tip", [XA - 170, 1310, EZ + 390], [XA - 170, 1365, EZ + 390], 30, "alu2")
d.tube("hand-cable", [[XA - 170, 1365, EZ + 390], [XA - 200, 1380, EZ + 360], [XA - 180, 1320, EZ + 330]], 6, "black",
       bend=20, soft=True)
# --- egg chair: chrome disc base, gas lift with a collar, front foot bar, domed bowl, back and wings as smooth lofts
SX, SZ = 540, 660
d.lathe("chair-disc", [SX, 0, SZ], [[0, 0], [280, 0], [280, 8], [210, 30], [60, 48], [0, 50]], "metal#9da2a8")
d.cyl("chair-lift", [SX, 50, SZ], [SX, 420, SZ], 64, "chrome")
d.cyl("chair-collar", [SX, 240, SZ], [SX, 270, SZ], 96, "chrome")
d.cyl("chair-lift-in", [SX, 50, SZ], [SX, 110, SZ], 90, "chrome")
d.box("chair-lever", [SX + 40, 400, SZ - 10, SX + 170, 412, SZ + 10], "black", r=4)
d.tube("chair-ring", [[SX - 30, 290, SZ], [SX - 150, 290, SZ + 190], [SX + 150, 290, SZ + 190], [SX + 30, 290, SZ]], 18,
       "chrome", bend=60)
d.loft("chair-bowl", [sec(380, 300, 290, 145, SX, SZ), sec(450, 570, 550, 260, SX, SZ + 5),
                      sec(520, 670, 650, 300, SX, SZ + 5), sec(600, 690, 670, 310, SX, SZ + 5)], "chair",
       dome="start", domeH=55)
d.box("chair-cushion", [SX - 255, 590, SZ - 220, SX + 255, 625, SZ + 300], "chair", r=40, puff=8)
# the back: lofted across x, curved in plan and with rounded top shoulders
bk = []
for x, zc, top in ((-345, -170, 930), (-305, -245, 995), (-200, -300, 1035), (0, -322, 1048),
                   (200, -300, 1035), (305, -245, 995), (345, -170, 930)):
    bk.append({"at": SX + x, "w": 92, "d": top - 580, "r": 44, "cx": (top + 580) / 2, "cz": SZ + zc})
d.loft("chair-back", bk, "chair", axis="x")
# the wings: lofted along z, rim sloping from the back to the front, rounded front end
for k, s in enumerate((-1, 1)):
    xw = SX + s * 300
    secs = []
    for z, top in ((-250, 1000), (-120, 905), (60, 790), (220, 735), (300, 715)):
        secs.append({"at": SZ + z, "w": 92, "d": top - 580, "r": 44, "cx": xw, "cz": (top + 580) / 2})
    d.loft(f"chair-wing-{k}", secs, "chair", axis="z", dome="end", domeH=45)
    d.sweep(f"armrest-{k}", [[xw, 1004, SZ - 245], [xw, 909, SZ - 120], [xw, 794, SZ + 60], [xw, 739, SZ + 220],
                             [xw, 722, SZ + 300]], [38, 8], "grey", bend=50, r=3)
    for j, (z, y) in enumerate(((SZ - 200, 975), (SZ + 10, 828), (SZ + 250, 734))):
        d.cyl(f"armrest-screw-{k}-{j}", [xw, y, z], [xw, y + 5, z], 9, "bolt", soft=True)
d.save()
