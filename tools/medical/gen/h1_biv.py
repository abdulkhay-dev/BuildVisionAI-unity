from h1lib import *
# XY-SL-BIV lower-limb + spine tub: D-plan tub (square left end, round right end), sides tapering to the bottom with
# groove facets, wide flat rim, inner seat at the left, 2 chrome buttons on the left rim, black valve + hand shower on a
# slide bar at the front left; two-step block at the left. Tub ~1000 × 650 × 880 (wider than tall as in the photo).
d = D("xy-sl-biv", [1520, 700, 900], {
    "shell": "gloss#f7f8f9", "inner": "gloss#eef1f4", "line": "plastic#dde1e6", "step": "plastic#f4f5f6",
    "dark": "black#2a2d31", "blue": "gloss#3a7fd0"})
TX0, TX1 = 520, 1520           # tub (rim) extent
RY, RT = 840, 42
CZ = 350
# body: square-ended loft (left part) + stadium loft (right part), both tapering in to the bottom
d.loft("body-l", [sec(40, 470, 556, 40, TX0 + 40 + 235 + 20, CZ), sec(RY + 5, 520, 646, 50, TX0 + 15 + 260, CZ)], "shell", caps=False)
d.loft("body-r", [sec(40, 850, 560, 280, TX0 + 500, CZ), sec(RY + 5, 960, 650, 325, TX0 + 495, CZ)], "shell", caps=False)
hole = rr(TX0 + 190, 100, TX1 - 100, 600, [245, 245, 40, 40])
tub(d, "", None, hole, rr(TX0, 15, TX1, 685, [335, 335, 40, 40]), RY, RT, 300,
    rr(TX0 + 175, 90, TX1 - 88, 610, [255, 255, 45, 45]))
d.lathe("btn", [TX0 + 70, RY + RT - 4, 250], [[0, 0], [22, 0], [22, 8], [16, 14], [0, 14]], "chrome", copies=[[70, 0, 0]])
d.box("seat", [TX0 + 185, 300, 95, TX0 + 300, 600, 605], "inner", r=40)
# vertical ribs on the front and back that flare out at the bottom into feet (photo), black feet under them
# Review 2026-10-02: replaced the flat groove lines; steps 280 / 440 high.
TAP = math.degrees(math.atan2(45, 805))
for i, x in enumerate((TX0 + 75, 870, 1150)):
    rib = f"M {x - 7} 560 L {x + 7} 560 L {x + 38} 50 Q {x + 44} 15 {x + 30} 15 L {x - 30} 15 Q {x - 44} 15 {x - 38} 50 Z"
    d.slab(f"rib{i}", "front", rib, [622, 640], "shell", r=6, rot=rot("x", TAP, [x, 40, 628]))
    d.slab(f"rib{i}b", "front", rib, [60, 78], "shell", r=6, rot=rot("x", -TAP, [x, 40, 72]))
    d.box(f"foot{i}", [x - 28, 0, 600, x + 28, 16, 650], "dark", r=5, copies=[[0, 0, -550]])
# hand shower at the front left: black valve knob, slide bar, handset, hose loop
FZ = 668
X = TX0 + 80
d.lathe("valve", [X, 790, FZ - 8], [[0, 0], [40, 0], [40, 14], [28, 30], [0, 34]], "dark", axis="z")
d.cyl("bar", [X + 65, 500, FZ + 14], [X + 65, 830, FZ + 14], 20, "chrome")
d.box("bar-clip", [X + 50, 490, FZ - 6, X + 80, 520, FZ + 24], "chrome", r=6, copies=[[0, 325, 0]])
d.box("holder", [X + 48, 750, FZ + 12, X + 82, 780, FZ + 42], "chrome", r=8)
d.cyl("handset", [X + 65, 670, FZ + 40], [X + 65, 830, FZ + 40], 30, "dark", d2=36)
d.decal("handset-strip", [X + 65, 780, FZ + 58], [8, 60], "front", "blue", soft=True)
d.tube("hose", [[X + 65, 670, FZ + 40], [X + 60, 350, FZ + 46], [X + 30, 110, FZ + 40], [X + 10, 350, FZ + 26], [X, 770, FZ + 10]],
       12, "chrome", bend=90, soft=True)
# two-step block at the left (upper step against the tub), embossed logo on the upper step
d.slab("steps", "front", "M 0 0 L 520 0 L 520 440 L 250 440 L 250 280 L 0 280 Z", [80, 620], "step", r=28)
d.decal("logo", [385, 441, 350], [110, 55], "top", "plastic#e6e8eb", soft=True)
d.save()
