"""JYZ-IB double-motor traction table (table-3 batch): long white sheet-steel cabinet on 4 corner legs, a split
two-section top (white rounded rim, grey pad, blue straps), blue control panel in the middle of the front, two blue
hand switches on the right door, a stainless cervical pole at the back with the arm and sling over the table."""
from t3_jyzlib import *
D_ = 650
d = D("jyz-ib", [2100, D_, 2050], {
    "white": "plastic#f3f4f5", "cab": "plastic#eef0f2", "steel": "metal#c3c8ce", "chrome": "chrome",
    "pad": "leather#aea9b6", "black": "plastic#1c1d20", "blue": "gloss#2f7fd0", "strap": "fabric#4f9ad8",
    "panel": "gloss#1f5aa8"})
cz = D_ / 2
X0, X1 = 215, 1890
# ---- cabinet with 4 corner posts and feet
for x in (X0, X1):
    d.bar(f"post{x}", [x, 25, 55], [x, 600, 55], [40, 40], "white", r=4, copies=[[0, 0, 540]])
    d.box(f"foot{x}", [x - 24, 0, 31, x + 24, 28, 79], "plastic#5a6068", r=4, copies=[[0, 0, 540]])
d.box("cab", [X0 + 10, 130, 60, X1 - 10, 595, 600], "cab", r=4)
for x in (790, 1250):
    d.box(f"door-gap{x}", [x, 140, 599, x + 20, 590, 603], "plastic#c9ced4", soft=True)
d.box("cab-frame", [X0 - 20, 590, 50, X1 + 20, 612, 610], "plastic#6b7079", r=4)
d.cyl("lock", [600, 560, 600], [600, 560, 606], 16, "steel", soft=True, copies=[[1060, 0, 0]])
d.decal("label", [330, 520, 601], [70, 90], "front", "plastic#d7dbe0", soft=True)
d.cyl("end-knob", [X0 - 30, 560, 560], [X0 - 70, 560, 560], 30, "black")
# middle control panel: blue face, red 7-segment display, buttons
d.box("ctrl", [870, 220, 598, 1180, 520, 606], "panel", r=4)
d.box("ctrl-frame", [860, 210, 597, 1190, 530, 601], "plastic#d6dade", r=4)
d.add("ctrl-disp", "screen", "black", box=[990, 430, 605, 1080, 470, 608], r=2, face="front")
d.decal("ctrl-digits", [1005, 450, 609], [18, 28], "front", "gloss#e0403a", soft=True, repeat=rep(3, [30, 0, 0]))
d.decal("ctrl-logo", [900, 495, 607], [26, 20], "front", "gloss#e8eef6", soft=True)
d.cyl("btn-green", [930, 300, 605], [930, 300, 612], 30, "gloss#3cb371", copies=[[230, 60, 0], [230, 0, 0]])
d.cyl("btn-red", [1035, 270, 605], [1035, 270, 612], 26, "gloss#d03030", copies=[[30, 0, 0], [-30, 0, 0]])
d.add("ctrl-disp-s", "screen", "black", box=[900, 400, 605, 930, 440, 608], r=2, face="front")
# two blue hand switches hanging on the right door, cables looping down into the cabinet
for i, x in enumerate((1530, 1630)):
    d.box(f"hs{i}", [x, 400, 603, x + 75, 530, 640], "blue", r=14)
    d.decal(f"hs{i}-face", [x + 38, 495, 641], [50, 50], "front", "gloss#e8eef6", soft=True)
    d.tube(f"hs{i}-cord", [[x + 37, 400, 625], [x + 30 - 60 * i, 170, 640], [1450 + 60 * i, 150, 605]], 6, "black",
           bend=60, soft=True)
d.cyl("cord-socket", [1450, 150, 600], [1450, 150, 606], 18, "black", soft=True, copies=[[60, 0, 0]])
# ---- split top: two thick white rounded sections with grey pads, tapered at the junction (V gap)
import math
def sect(x0, x1, cut_left, cut_right):
    c = 70
    pts = [(x0 + (c if cut_left else 0), 20), (x1 - (c if cut_right else 0), 20), (x1, 20 + (c if cut_right else 0)),
           (x1, D_ - 20), (x0, D_ - 20), (x0, 20 + (c if cut_left else 0))]
    # simple: chamfer the junction-side front corners only (the photo shows a V opening at the front)
    pts = [(x0, 20), (x1, 20), (x1, D_ - 20 - (c if cut_right else 0)), (x1 - (c if cut_right else 0), D_ - 20),
           (x0 + (c if cut_left else 0), D_ - 20), (x0, D_ - 20 - (c if cut_left else 0))]
    return "M " + " L ".join(f"{x:.0f} {z:.0f}" for x, z in pts) + " Z"
for nm, (x0, x1, cl, cr) in (("l", (0, 928, False, True)), ("r", (938, 2100, True, False))):
    d.slab("top-" + nm, "top", sect(x0, x1, cl, cr), [612, 672], "white", r=26)
    d.slab("pad-" + nm, "top", sect(x0 + 22, x1 - 22, cl, cr).replace(" 20 ", " 42 ").replace(f" {D_ - 20} ", f" {D_ - 42} "),
           [665, 690], "pad", r=8)
    d.strap("strap-" + nm, [[x0 + 40, 692, 60], [x1 - 40, 692, 60]], [26, 3], "strap", soft=True, copies=[[0, 0, 530]])
    d.cyl("clip-" + nm, [x0 + 80, 690, 60], [x0 + 80, 700, 60], 30, "steel", copies=[[x1 - x0 - 160, 0, 0], [0, 0, 530],
                                                                                   [x1 - x0 - 160, 0, 530]])
belt(d, "belt-chest", 620, 830, 690, 100, 570, mat="fabric#aab3c4", stripe="fabric#4f86c8")
belt(d, "belt-pelvis", 850, 1080, 690, 90, 580, mat="fabric#aab3c4", stripe="fabric#4f86c8")
# ---- cervical pole at the back, white bar arm reaching over the table, light-blue sling
pole(d, 580, 30, 590, 2050, 1, 420, style="bar", slingmat="fabric#dde5ee", edgemat="fabric#4f9ad8", ys=1500, k=0.78,
     spreadmat="plastic#2a2d33")
d.box("pole-mount", [545, 540, 0, 615, 640, 60], "white", r=6)
d.save()
