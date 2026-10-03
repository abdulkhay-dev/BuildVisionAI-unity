"""xy-cpm-id: shoulder + elbow CPM on a mobile 5-star stand. Front = the box face with the LCD window."""
import math
from k1lib import *

d = D("xy-cpm-id", [650, 650, 1550], {
    "white": "gloss#f4f5f6", "black": "plastic#1e1f22", "chrome": "chrome", "pad": "leather#1c1d20",
    "grey": "plastic#bfc3c8", "red": "gloss#d32a22", "cable": "rubber#18191b"})
CX, CZ = 325, 325
# --- black 5-star base with twin castors, black lower column, chrome collar and upper tube
for i in range(5):
    a = math.radians(90 + i * 72)
    tx, tz = CX + 285 * math.cos(a), CZ + 285 * math.sin(a)
    d.bar(f"star-{i}", [CX, 110, CZ], [tx, 102, tz], [62, 34], "black", r=10)
    # black hooded twin castor (photo: all black, no chrome fork)
    d.add(f"castor-w-{i}", "wheel", "rubber#1a1b1d", at=[tx, 30, tz], d=60, d2=46, axis="x")
    d.box(f"castor-hood-{i}", [tx - 12, 8, tz - 34, tx + 12, 70, tz + 34], "black", r=11)
    d.cyl(f"castor-stem-{i}", [tx, 68, tz], [tx, 96, tz], 26, "black")
d.cyl("hub", [CX, 72, CZ], [CX, 128, CZ], 120, "black")
d.cyl("column", [CX, 120, CZ], [CX, 640, CZ], 60, "black")
d.cyl("collar", [CX, 615, CZ], [CX, 665, CZ], 72, "chrome")
d.cyl("upper-tube", [CX, 640, CZ], [CX, 910, CZ], 45, "chrome")
# --- white head box: grey LCD window on the front, red e-stop on top
# box 900-1140 (photo scale), its top-front edge well rounded; LCD window high on the front face
d.slab("box", "side", "M 205 900 L 445 900 L 445 1085 Q 445 1140 390 1140 L 205 1140 Z", [165, 485], "white", r=22)
d.box("lcd-frame", [252, 1022, 444, 372, 1080, 448], "grey", r=5)
d.box("lcd", [262, 1030, 447, 362, 1072, 449.5], "plastic#9aa59a", r=3, soft=True)
d.lathe("estop", [370, 1138, 360], [[0, 0], [14, 0], [14, 10], [18, 12], [18, 22], [0, 24]], "red")
# --- -x side: chrome rod frame with a black square pad and knobs; a black forearm rest with the hand controller
d.bar("frame-arm", [170, 1015, 300], [110, 1015, 300], [24, 24], "chrome", r=4)
d.tube("pad-frame", [[115, 1010, 300], [115, 1320, 300], [185, 1380, 300], [255, 1320, 300], [255, 1150, 300]],
       14, "chrome", bend=20)
d.box("pad", [125, 1145, 302, 245, 1290, 336], "pad", r=14, puff=6)
d.lathe("pad-knob", [115, 1210, 318], [[0, 0], [7, 0], [7, 8], [16, 10], [16, 24], [0, 26]], "black", axis="x",
        rot=rot("y", 180, [115, 1210, 318]), sides=8)
d.lathe("pad-knob-r", [255, 1210, 318], [[0, 0], [7, 0], [7, 8], [16, 10], [16, 24], [0, 26]], "black", axis="x",
        sides=8)
d.box("rest", [30, 985, 250, 168, 1018, 430], "pad", r=12, puff=4)
d.box("rest-bracket", [150, 970, 320, 172, 990, 380], "chrome", r=3)
d.box("controller", [55, 1018, 300, 140, 1040, 380], "plastic#f1f2f0", r=8)
d.box("controller-face", [62, 1039, 308, 133, 1041.5, 372], "gloss#1f5d9c", r=5, soft=True)
d.coil("cable-coil", [158, 955, 260], [158, 640, 260], 30, 6, 30, "cable", soft=True)
d.tube("cable", [[158, 640, 260], [150, 600, 260], [120, 750, 300], [95, 1018, 330]], 7, "cable", bend=50, soft=True)
# --- +x side: joint block, vertical chrome rod with two black C cuffs and red knobs
d.box("joint", [484, 950, 300, 528, 1020, 360], "black", r=8)
d.lathe("joint-knob", [528, 985, 330], [[0, 0], [7, 0], [7, 8], [16, 10], [16, 24], [0, 26]], "black", axis="x",
        sides=8)
T = rot("z", -5, [536, 950, 345])
d.cyl("arm-rod", [536, 925, 345], [536, 1500, 345], 18, "chrome", rot=T)
d.cyl("arm-tip", [536, 1500, 345], [536, 1548, 345], 8, "chrome", rot=T)
for nm, y in (("u", 1360), ("l", 1135)):
    d.box(f"cuff-clamp-{nm}", [522, y - 10, 330, 552, y + 30, 360], "black", r=5, rot=T)
    d.bar(f"cuff-arm-{nm}", [552, y + 10, 345], [540, y + 10, 340], [14, 14], "chrome", r=3, rot=T)
    cx, cy, r, t = 590, y + 10, 58, 14
    c = (f"M {cx + 20} {cy - r} L {cx} {cy - r} Q {cx - r} {cy - r} {cx - r} {cy} Q {cx - r} {cy + r} {cx} {cy + r} "
         f"L {cx + 20} {cy + r} L {cx + 20} {cy + r - t} L {cx} {cy + r - t} Q {cx - r + t} {cy + r - t} {cx - r + t} {cy} "
         f"Q {cx - r + t} {cy - r + t} {cx} {cy - r + t} L {cx + 20} {cy - r + t} Z")
    d.slab(f"cuff-{nm}", "front", c, [300, 380], "pad", r=6, rot=T)
    d.sphere(f"cuff-knob-{nm}", [536, y + 48, 362], 26, "red", rot=T)
d.save()
