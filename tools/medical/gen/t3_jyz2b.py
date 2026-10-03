"""JYZ-IIB traction table (table-3 batch): head console with the pole on the RIGHT, a long two-section bed on a
white apron frame supported by a leg frame at the left (foot) end, black knee pad + stainless leg-rest frame."""
from t3_jyzlib import *
D_ = 650
d = D("jyz-iib", [2300, D_, 2050], {
    "white": "plastic#f3f4f5", "steel": "metal#c3c8ce", "chrome": "chrome", "pad": "leather#bab1db",
    "black": "plastic#1c1d20", "knee": "leather#1d1e21", "logo": "gloss#1f6fc0", "vent": "plastic#3a3f46",
    "panel": "gloss#cfd8e2", "strap": "fabric#8a7fc6"})
cz = D_ / 2
# ---- console (right): lower cabinet on castors, head box with the sloped LCD/keypad panel overhanging right
C0, C1 = 1690, 2050
d.box("con-low", [C0, 70, 50, C1, 650, 610], "white", r=10)
d.add("castor", "caster", "steel", at=[C0 + 60, 0, 110], d=75, copies=[[C1 - C0 - 120, 0, 0], [0, 0, 430], [C1 - C0 - 120, 0, 430]])
d.box("con-head", [C0 - 10, 640, 45, C1 + 60, 720, 615], "white", r=14)
tilt = rot("x", 9, [0, 780, 45])
d.box("con-head-back", [C0 - 10, 720, 45, C1 + 60, 780, 200], "white", r=14)
d.box("con-top", [C0 - 10, 720, 45, C1 + 60, 780, 615], "white", r=14, rot=tilt)
d.add("con-panel", "screen", "panel", box=[C0 + 90, 778, 300, C1 + 40, 784, 595], r=6, face="top", bezel=6, rot=tilt)
d.add("con-lcd", "screen", "black", box=[C0 + 110, 784, 330, C0 + 250, 788, 470], r=3, face="top", rot=tilt)
d.decal("con-keys", [C0 + 290, 785, 370], [22, 18], "top", "gloss#2f6fc8", soft=True,
        repeat=rep(4, [28, 0, 0]), copies=[[0, 0, 32], [0, 0, 64]], rot=tilt)
d.decal("con-grille", [C0 + 20, 685, 616], [7, 26], "front", "vent", soft=True, repeat=rep(10, [10, 0, 0]))
d.cyl("con-btn", [C0 + 40, 560, 610], [C0 + 40, 560, 618], 22, "black", soft=True, copies=[[30, 0, 0], [60, 0, 0]])
d.box("con-switch", [C0 + 100, 548, 610, C0 + 150, 572, 618], "black", r=8, soft=True)
d.decal("con-label", [C0 + 110, 470, 611], [80, 110], "front", "plastic#dfe2e6", soft=True)
d.decal("con-logo", [C0 + 210, 360, 611], [50, 50], "front", "logo", soft=True)
d.decal("con-logo-txt", [C0 + 290, 370, 611], [100, 26], "front", "logo", soft=True)
# ---- pole on the console top (back-left), arm and sling to the right
pole(d, C0 + 110, 140, 780, 2050, 1, 300, style="rods", slingmat="fabric#a8a4dc", edgemat="fabric#8582cf", ys=1380, k=0.72)
d.cyl("pole-disc", [C0 + 210, 1880, 130], [C0 + 210, 1880, 150], 120, "white")
# ---- bed frame: front/back aprons, end bar, legs at the foot end, black feet
d.box("apron", [0, 470, 40, C0, 560, 70], "white", r=6, copies=[[0, 0, 540]])
d.box("apron-end", [0, 470, 40, 40, 560, 610], "white", r=6)
d.bar("cross", [400, 500, 70], [400, 500, 580], [40, 40], "white", r=4, copies=[[500, 0, 0], [900, 0, 0]])
d.box("apron-slot", [560, 505, 69, 640, 520, 73], "plastic#c8ccd2", r=3, soft=True, copies=[[0, 25, 0]])
for x in (40, 360):
    d.bar(f"leg{x}", [x, 30, 55], [x, 480, 55], [40, 40], "white", r=4, copies=[[0, 0, 540]])
    d.box(f"foot{x}", [x - 24, 0, 31, x + 24, 32, 79], "black", r=4, copies=[[0, 0, 540]])
d.bar("leg-low", [40, 140, 55], [360, 140, 55], [35, 35], "white", r=4, copies=[[0, 0, 540]])
d.bar("leg-low-z", [40, 140, 55], [40, 140, 595], [35, 35], "white", r=4)
# ---- two bed sections: white rounded trays with lilac pads, purple straps along the edges
for nm, (x0, x1) in (("foot", (20, 540)), ("head", (560, C0 - 10))):
    d.box("tray-" + nm, [x0, 555, 30, x1, 605, 620], "white", r=24)
    d.box("pad-" + nm, [x0 + 15, 598, 45, x1 - 15, 632, 605], "pad", r=14, puff=3)
    d.strap("strap-" + nm, [[x0 + 30, 634, 70], [x1 - 30, 634, 70]], [30, 3], "strap", soft=True, copies=[[0, 0, 510]])
# ---- leg rest: stainless frame + black knee pad at the foot end
for nm, z in (("a", 70), ("b", D_ - 70)):
    d.tube("rest-" + nm, [[30, 630, z], [60, 760, z], [340, 830, z], [430, 760, z], [440, 630, z]], 24, "chrome", bend=60)
d.cyl("rest-bar", [400, 790, 70], [400, 790, D_ - 70], 22, "chrome")
d.box("knee", [430, 640, 130, 480, 860, 520], "knee", r=20, puff=4)
belt(d, "belt-chest", 430, 640, 634, 110, 560, mat="fabric#9a95cf", stripe="fabric#4d4c96")
belt(d, "belt-pelvis", 660, 880, 634, 100, 570, mat="fabric#9a95cf", stripe="fabric#4d4c96")
d.save()
