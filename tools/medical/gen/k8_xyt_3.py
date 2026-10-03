"""XYT-3 mini stepper with a twist disc: light-grey base (block, rear foot, two splayed front legs with black caps),
two black ribbed pedals pivoting at the back with hydraulic cylinders, a grey column with a dumbbell holder (2 yellow,
2 pink), a black lyre handlebar with a small display, a black twist disc on an arm to the left. The user stands on the
pedals facing the column: pedals toward the front (z = depth), column at the back."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from k8lib import *

W, DP, H = 550, 650, 1300
d = D("xyt-3", [W, DP, H], {"frame": "metal#c3c7cb", "col": "plastic#cfd2d5", "black": "plastic#1b1c1e", "foam": "rubber#1d1e20",
                            "pedal": "rubber#1f2022", "chrome": "chrome", "yellow": "gloss#f2b01e", "pink": "gloss#f3a3bd"})
CX, CZ = 375, 140
# base block, rear foot, splayed front legs with black caps
d.box("block", [CX - 55, 55, 70, CX + 55, 205, 270], "frame", r=22)
d.cyl("rear", [CX - 95, 32, 70], [CX + 95, 32, 70], 40, "frame")
d.cyl("rear-cap", [CX - 125, 32, 70], [CX - 95, 32, 70], 52, "black", copies=[[220, 0, 0]])
for k, end in (("l", [CX - 120, 28, DP - 50]), ("r", [CX + 145, 28, DP - 70])):
    d.cyl(f"leg-{k}", [CX, 60, 240], end, 40, "frame")
    u = [end[i] - [CX, 60, 240][i] for i in range(3)]; L = math.dist(end, [CX, 60, 240]); u = [c / L for c in u]
    d.cyl(f"legcap-{k}", end, [end[i] + u[i] * 45 for i in range(3)], 56, "black")
# pedals pivoting at the back (z ~ 230), free ends toward the user, the right one raised
for k, x, yf in (("l", CX - 68, 190), ("r", CX + 68, 290)):
    y0 = 175
    yp = lambda z: y0 + (yf - y0) * (z - 235) / (DP - 90 - 235)
    d.bar(f"parm-{k}", [x, y0, 235], [x, yp(440), 440], [36, 30], "frame", r=4)
    d.bar(f"pedal-{k}", [x, yp(260) + 32, 260], [x, yp(DP - 90) + 32, DP - 90], [122, 30], "pedal", r=8)
    for j in range(7):
        z = 290 + j * 42
        d.bar(f"rib-{k}{j}", [x - 52, yp(z) + 48, z], [x + 52, yp(z) + 48, z], [8, 6], "rubber#34363a", r=2)
    d.cyl(f"hyd-{k}", [x, 80, 300], [x, yp(470) - 10, 470], 34, "black")
    d.cyl(f"hydrod-{k}", [x, yp(470) - 10, 470], [x, yp(500) + 5, 500], 12, "chrome")
d.cyl("pivot", [CX - 110, 175, 235], [CX + 110, 175, 235], 30, "chrome")
d.cyl("knob", [CX - 80, 120, 275], [CX - 80, 120, 300], 40, "black")
# column, collar, top clamp
d.cyl("column", [CX, 200, CZ], [CX, 1085, CZ], 60, "col")
d.cyl("column-lo", [CX, 200, CZ], [CX, 680, CZ], 62, "frame")
d.cyl("collar", [CX, 665, CZ], [CX, 700, CZ], 70, "chrome")
d.box("clamp", [CX - 42, 1050, CZ - 38, CX + 42, 1115, CZ + 42], "black", r=12)
# lyre handlebar and display
# photo: the horns run out sideways from the clamp, rise, and lean back IN toward each other at the tips (lyre)
bar = [[CX - 52, 1298, CZ], [CX - 88, 1250, CZ], [CX - 108, 1180, CZ], [CX - 100, 1115, CZ], [CX - 60, 1090, CZ], [CX, 1088, CZ],
       [CX + 60, 1090, CZ], [CX + 100, 1115, CZ], [CX + 108, 1180, CZ], [CX + 88, 1250, CZ], [CX + 52, 1298, CZ]]
d.tube("handlebar", bar, 32, "foam", bend=45)
d.box("display", [CX - 36, 1140, CZ - 25, CX + 36, 1255, CZ + 32], "black", r=10)
d.screen("display-scr", [CX - 26, 1190, CZ + 30, CX + 26, 1235, CZ + 33], "black", r=3)
d.cyl("display-post", [CX, 1110, CZ], [CX, 1145, CZ], 26, "black")
# dumbbell holder with 2 yellow and 2 pink dumbbells (axis along z), one each side of the column
d.box("holder", [CX - 48, 440, CZ - 38, CX + 48, 625, CZ + 52], "black", r=8)
for y, m in ((600, "yellow"), (470, "pink")):
    d.box(f"cradle{y}", [CX - 100, y - 38, CZ - 10, CX + 100, y - 26, CZ + 40], "black", r=3)
    for s in (-1, 1):
        x = CX + s * 76
        dumbbell_round(d, f"db{y}{s}", [x, y, CZ - 62], 165, 60, "z", m)
# twist disc on an arm to the left
DX, DZ = 140, 235
d.bar("disc-arm", [CX - 55, 40, 230], [DX + 100, 40, DZ], [40, 30], "frame", r=4)
d.lathe("disc", [DX, 8, DZ], [[0, 0], [130, 0], [140, 6], [140, 20], [133, 24], [128, 26], [128, 48], [124, 54], [0, 54]], "black")
d.lathe("disc-rim", [DX, 8, DZ], [[0, 0], [139, 0], [141, 6], [141, 22], [0, 22]], "plastic#b8bcc0")
for r_ in (40, 70, 100):
    d.add(f"disc-ring{r_}", "tube", "plastic#3a3c40", path=ring_pts([DX, 62.5, DZ], r_, r_, "xz", 24), d=4, soft=True)
d.cyl("disc-foot", [DX - 80, 0, DZ - 80], [DX - 80, 8, DZ - 80], 26, "black", copies=[[160, 0, 0], [0, 0, 160], [160, 0, 160]])
d.save()
