from k4lib import *
d = K("xy-2b", [585, 1520, 1130], {
    "body": "plastic#3d4147", "dark": "plastic#2a2d32", "silver": "metal#c8ccd2", "black": "plastic#18191b",
    "seat": "fabric#1b1c1f", "foot": "rubber#1a1b1d", "shell": "metal#9da1a8"})
CX = 292.5
# --- stabiliser feet (black trapezoids)
d.slab("foot-rear", "front", "M 0 0 L 585 0 L 548 75 L 37 75 Z", [40, 200], "foot", r=8)
d.slab("foot-front", "front", "M 0 0 L 585 0 L 548 75 L 37 75 Z", [1360, 1515], "foot", r=8)
# --- rear seat module: graphite shroud with angled faces, silver swoosh, rail on top
# photo: the module reaches close to the front housing (short beam gap); its rear face leans back at the top
mod = "M 100 70 L 760 70 Q 788 70 788 100 L 788 345 Q 788 386 748 386 L 78 386 Q 38 386 40 346 L 72 110 Q 78 70 100 70 Z"
d.slab("module", "side", mod, [108, 477], "body", r=28)
d.slab("module-swoosh", "side", "M 620 75 L 700 75 L 770 300 L 720 300 Z", [103, 482], "silver", r=4)
d.slab("module-groove", "side", "M 140 240 L 660 240 L 666 250 L 140 250 Z", [104, 481], "dark", r=1)
d.box("rail", [205, 380, 95, 380, 452, 770], "silver", r=26)
d.box("rail-cap", [200, 376, 755, 385, 456, 790], "black", r=18, copies=[[0, 0, -705]])
d.tube("rear-loop", [[150, 80, 70], [150, 240, 25], [435, 240, 25], [435, 80, 70]], 30, "black", bend=60)
# seat carriage, cushion, reclined backrest (fabric front, grey/silver shell)
d.slab("carriage", "side", "M 210 452 L 560 452 L 520 505 L 230 505 Z", [170, 415], "dark", r=8)
d.box("seat", [70, 500, 200, 515, 578, 585], "seat", r=40, puff=12)
d.box("seat-pan", [90, 492, 215, 495, 510, 570], "black", r=10)
BR = rot("x", -21, [CX, 560, 205])
d.box("back", [88, 560, 125, 497, 1150, 205], "seat", r=45, puff=9, rot=BR)
d.box("back-shell", [78, 575, 92, 507, 1140, 132], "shell", r=34, rot=BR)
d.box("back-head", [110, 1040, 118, 475, 1150, 210], "black", r=40, rot=BR)
d.tube("back-strut", [[CX, 495, 260], [CX, 470, 150], [CX, 560, 90]], 40, "black", bend=60)
# side handles: up from the seat sides and straight forward
for nm, x in (("l", 48), ("r", 537)):
    xi = 95 if x < CX else 490
    d.tube(f"handle-{nm}", [[xi, 505, 300], [x, 560, 310], [x, 640, 340], [x, 645, 660]], 32, "black", bend=45)
    d.cyl(f"handle-end-{nm}", [x, 645, 655], [x, 645, 672], 36, "black")
# --- low centre beam (silver top)
d.box("beam", [200, 30, 620, 385, 105, 1010], "dark", r=10)
d.box("beam-top", [205, 104, 640, 380, 112, 1000], "silver", r=3)
# --- front flywheel housing, silver swoosh band, crank covers, pedals
hs = "M 960 60 L 1395 60 L 1405 540 Q 1405 585 1355 590 L 1250 590 Q 1215 590 1200 555 L 1185 490 Q 1175 450 1130 450 L 1000 445 Q 962 445 960 405 Z"
d.slab("housing", "side", hs, [145, 440], "body", r=34)
for nm, x in (("l", 143), ("r", 442)):
    d.sweep(f"swoosh-{nm}", [[x, 125, 975], [x, 118, 1140], [x, 330, 1215], [x, 550, 1330]], [26, 5], "silver", bend=70, roll=90)
KZ, KY = 1215, 330
for nm, o in (("l", -1), ("r", 1)):
    xs = CX + o * 147
    d.lathe(f"crank-cover-{nm}", [xs, KY, KZ], [[0, 0], [66, 0], [64, 8], [50, 16], [0, 18]], "silver", axis="x",
            rot=rot("y", 0 if o > 0 else 180, [xs, KY, KZ]))
    ang = 70 if o > 0 else 250
    ez = KZ + 170 * math.cos(math.radians(ang)); ey = KY - 170 * math.sin(math.radians(ang))
    xc = xs + o * 24
    d.bar(f"crank-{nm}", [xc, KY, KZ], [xc, ey, ez], [38, 16], "silver", r=6, roll=90)
    px0, px1 = sorted([xc + o * 10, xc + o * 120])
    d.box(f"pedal-{nm}", [px0, ey - 18, ez - 60, px1, ey + 14, ez + 60], "black", r=8)
    d.strap(f"pedal-strap-{nm}", [[px0 + 5, ey + 14, ez + 30], [(px0 + px1) / 2, ey + 52, ez + 20], [px1 - 5, ey + 14, ez + 30]],
            [26, 3], "black", bend=40)
# --- column, console, handlebars
d.bar("column", [CX, 550, 1340], [CX, 880, 1290], [130, 95], "body", r=20)
d.box("column-collar", [222, 560, 1270, 363, 610, 1395], "dark", r=12)
CR = rot("x", 22, [CX, 800, 1320])
d.box("console", [140, 790, 1290, 445, 1130, 1370], "body", r=28, rot=CR)
d.box("console-rim", [148, 798, 1284, 437, 1122, 1296], "silver", r=22, rot=CR)
d.screen("display", [168, 850, 1276, 417, 1100, 1286], "black", face="back", bezel=8, rot=CR)
d.decal("ui-a", [225, 1040, 1275.4], [90, 60], "back", "gloss#e0a040", rot=CR)
d.decal("ui-b", [330, 1040, 1275.4], [90, 60], "back", "gloss#d8dde4", rot=CR)
d.decal("ui-c", [CX, 930, 1275.4], [200, 70], "back", "gloss#4a7fc0", rot=CR)
d.decal("ui-d", [CX, 870, 1275.4], [200, 18], "back", "gloss#8a9099", rot=CR)
for nm, x in (("l", 118), ("r", 467)):
    xi = 150 if x < CX else 435
    d.tube(f"bar-{nm}", [[xi, 880, 1300], [x, 880, 1290], [x, 880, 1160], [x, 1075, 1135]], 32, "black", bend=45)
d.save()
