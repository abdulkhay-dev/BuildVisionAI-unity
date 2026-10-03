"""JYZ-IIIA / JYZ-IIIB multifunctional traction tables (table-3 batch). Head console + pole on the LEFT, the
cabinet bed in the middle, the cantilevered swinging lumbar (leg) section on the right. Usage: t3_jyz3.py a|b"""
import sys
from t3_jyzlib import *
var = sys.argv[1] if len(sys.argv) > 1 else "b"
B = var == "b"
D_ = 700
d = D("jyz-iiib" if B else "jyz-iiia", [2700, D_, 2050], {
    "white": "plastic#f3f4f5", "cab": "plastic#eef0f2", "steel": "metal#c3c8ce", "chrome": "chrome",
    "pad": "leather#c4bdd6" if B else "leather#9e8c9e", "black": "plastic#1c1d20", "knee": "leather#1d1e21",
    "logo": "gloss#1f6fc0", "vent": "plastic#3a3f46", "panel": "gloss#1d5f96"})
cz = D_ / 2
# ---- console at the head end: lower cabinet + wider head box with a sloped control panel
C0, C1 = (560, 840) if B else (520, 860)
d.box("con-low", [C0, 70, 60, C1, 610, 640], "white", r=10)
d.box("con-plinth", [C0 + 10, 40, 70, C1 - 10, 75, 630], "plastic#d5d9de", r=4)
d.box("con-head", [470 if B else 420, 600, 50, C1, 700, 650], "white", r=16)
tilt = rot("x", 10, [0, 800, 50])     # the top with the panel slopes down to the front
d.box("con-head-back", [470 if B else 420, 740, 50, C1, 800, 200], "white", r=16)
d.box("con-top", [470 if B else 420, 740, 50, C1, 800, 650], "white", r=16, rot=tilt)
pan = [500 if B else 450, 798, 360, C1 - 30, 806, 630]
if B:
    d.add("con-panel", "screen", "panel", box=pan, r=6, face="top", print="med_jyz-iiib_screen", bezel=8, rot=tilt)
else:
    d.add("con-panel", "screen", "panel", box=pan, r=6, face="top", bezel=8, rot=tilt)
    d.add("con-lcd", "screen", "black", box=[pan[0] + 20, 806, 400, pan[0] + 150, 810, 500], r=3, face="top", rot=tilt)
    d.decal("con-keys", [pan[0] + 220, 807, 560], [22, 18], "top", "gloss#e8edf3", soft=True,
            repeat=rep(5, [26, 0, 0]), copies=[[0, 0, -30], [0, 0, -60]], rot=tilt)
d.decal("con-grille", [C1 - 120, 670, 651], [8, 30], "front", "vent", soft=True, repeat=rep(9, [11, 0, 0]))
d.decal("con-logo", [C0 + 50, 380, 641], [36, 36], "front", "logo", soft=True)
d.decal("con-logo-txt", [C0 + 105, 380, 641], [60, 14], "front", "logo", soft=True)
# ---- cervical pole on the console top (back), arm and sling to the LEFT (toward x = 0)
pole(d, 610, 140, 800, 2050, -1, 440, style="rods", slingmat="fabric#cfc8e6" if B else "fabric#9c8fb7",
     edgemat="fabric#e9e6f2" if B else "fabric#6e6380", ys=1260, k=0.9,
     lattice=not B)
# ---- bed cabinet with two louvred doors, stainless tray with the lilac pad
X0, X1 = C1, 2090 if B else 2010
d.box("cab", [X0, 100, 70, X1, 595, 630], "cab", r=6)
d.box("cab-top", [X0 - 5, 585, 60, X1 + 5, 610, 640], "white", r=4)
xm = (X0 + X1) / 2
d.box("door-gap", [xm - 3, 110, 629, xm + 3, 580, 633], "plastic#c2c7cd", soft=True)
for k, x in enumerate((X0 + 120, xm + 100)):
    louvres(d, f"louvre{k}", x, 480, 630, n=9 if B else 8, cols=3, colstep=105)
d.cyl("screw", [X0 + 15, 570, 630], [X0 + 15, 570, 634], 8, "steel", soft=True,
      copies=[[X1 - X0 - 30, 0, 0], [0, -450, 0], [X1 - X0 - 30, -450, 0], [xm - X0 - 30, 0, 0], [xm - X0 - 30, -450, 0]])
d.add("castor", "caster", "steel", at=[X0 + 60, 0, 130], d=75, copies=[[X1 - X0 - 120, 0, 0], [0, 0, 440], [X1 - X0 - 120, 0, 440]])
d.add("castor-con", "caster", "steel", at=[C0 + 60, 0, 130], d=60, copies=[[0, 0, 440]])
T0, T1 = X0 + 10, X1 - 90
d.box("tray", [T0, 610, 35, T1, 650, 665], "steel", r=14)
d.box("pad", [T0 + 25, 640, 60, T1 - 25, 690, 640], "pad", r=16, puff=4)
d.box("pad-split", [T0 + 560, 670, 58, T0 + 566, 692, 642], "plastic#8d849c", soft=True)
# harnesses on the bed, a small remote with a blue display
BK = {} if B else {"mat": "fabric#8e9099", "stripe": "fabric#2c2e35"}   # IIIA photo: grey/black harnesses
belt(d, "belt-chest", T1 - 380, T1 - 230, 690, 120, 600, **BK)
belt(d, "belt-pelvis", T1 - 220, T1 - 40, 690, 110, 610, **BK)
d.box("remote", [xm - 160, 690, 520, xm - 20, 722, 600], "white", r=8)
d.add("remote-lcd", "screen", "panel", box=[xm - 140, 720, 535, xm - 50, 724, 585], r=3, face="top")
d.tube("remote-cord", [[xm - 160, 700, 560], [xm - 400, 692, 540], [X0 + 60, 692, 470]], 6, "black", bend=60, soft=True)
if not B:   # JYZ-IIIA photo: a second small control box further along the bed
    d.box("remote2", [xm + 60, 690, 470, xm + 190, 722, 550], "white", r=8)
    d.add("remote2-lcd", "screen", "panel", box=[xm + 80, 720, 485, xm + 160, 724, 535], r=3, face="top")
# ---- lumbar (leg) section: black joint, white rounded wedge housing, stainless tray + pad, knee rests, rails
L0 = X1 - 60
d.cyl("joint", [X1 - 30, 640, cz], [X1 + 90, 640, cz], 90, "black")
d.box("joint-arm", [X1 - 40, 610, cz - 60, L0 + 140, 660, cz + 60], "black", r=10)
d.tube("leg-cable", [[L0 + 160, 600, cz + 150], [L0 + 120, 380, cz + 200], [X1 - 10, 300, cz + 230]], 14, "black",
       bend=120, soft=True)
d.loft("leg-housing", [sec(570, 480, 420, 60, L0 + 330, cz), sec(640, 560, 540, 70, L0 + 310, cz),
                       sec(745, 580, 580, 70, L0 + 310, cz)], "white")
d.box("leg-tray", [L0 + 10, 745, 40, 2700 - 5, 780, 660], "steel", r=14)
d.box("leg-pad", [L0 + 30, 772, 60, 2700 - 25, 805, 640], "pad", r=14, puff=3)
for nm, z in (("a", cz - 115), ("b", cz + 115)):
    d.box("knee-" + nm, [L0 + 130, 800, z - 70, L0 + 190, 1010, z + 70], "knee", r=22, puff=4)
d.cyl("knee-bar", [L0 + 160, 900, 90], [L0 + 160, 900, D_ - 90], 26, "chrome")
for nm, z in (("a", 85), ("b", D_ - 85)):
    d.tube("rail-" + nm, [[L0 + 160, 780, z], [L0 + 160, 960, z], [L0 + 470, 960, z], [2690, 790, z]], 26, "chrome", bend=70)
belt(d, "belt-leg", L0 + 40, L0 + 120, 805, 110, 610, **BK)
d.save()
