# XY-82 folding wheelchair with a lap tray: chrome frame, spoked rear wheels with push rims, black back,
# navy seat, grey side guards, swing-away footrests, wooden tray — other-1
import math
from o_lib import *
W, DP, H = 640, 1100, 900
d = D("xy-82", [W, DP, H], {
    "chrome": "chrome", "tyre": "rubber#6d7177", "blk": "leather#1c1d20", "seat": "leather#58628a",
    "guard": "metal#b8bcc2", "grip": "rubber#1b1b1d", "plate": "metal#aeb3b9", "tray": "plastic#dcbb8e", "edge": "plastic#c97a3c",
    "batten": "plastic#efb350"})
WR, WY, WZ = 300, 300, 290            # rear wheel radius, centre
for i, (xw, xr, xf) in enumerate(((44, 14, 92), (W - 44, W - 14, W - 92))):
    s = -1 if i == 0 else 1
    ring = lambda r: [[xw, WY + r * math.cos(math.radians(a)), WZ + r * math.sin(math.radians(a))] for a in range(0, 361, 10)]
    d.tube(f"tyre{i}", ring(284), 32, "tyre")
    d.tube(f"wrim{i}", ring(262), 14, "chrome")
    d.cyl(f"hub{i}", [xw - 28 * s, WY, WZ], [xw + 40 * s, WY, WZ], 46, "chrome")
    d.cyl(f"axle{i}", [xw, WY, WZ], [xf, WY, WZ], 18, "chrome")
    # push rim outside the wheel, on 3 stand-offs
    rim = [[xr, WY + 268 * math.cos(math.radians(a)), WZ + 268 * math.sin(math.radians(a))] for a in range(0, 361, 15)]
    d.tube(f"rim{i}", rim, 18, "chrome")
    # thin spokes
    for k in range(18):
        a = math.radians(k * 20)
        d.cyl(f"spoke{i}-{k}", [xw + 10 * s, WY, WZ], [xw, WY + 278 * math.cos(a), WZ + 278 * math.sin(a)], 3, "chrome", soft=True)
    # front castor: grey tyre, chrome fork and stem
    cz, cy = 960, 100
    xc = 120 if i == 0 else W - 120
    d.add(f"castor{i}", "wheel", "tyre", at=[xc, cy, cz], d=200, d2=32, axis="x")
    d.lathe(f"castor-hub{i}", [xc - 24, cy, cz], [[0, 0], [55, 0], [55, 48], [0, 48]], "plastic#9aa0a6", axis="x")
    d.bar(f"fork{i}", [xc - 28, cy, cz], [xc - 28, 245, cz - 30], [10, 22], "chrome", r=3, copies=[[56, 0, 0]])
    d.cyl(f"stem{i}", [xc, 235, cz - 30], [xc, 300, cz - 30], 30, "chrome")
    # side frame: lower rail, seat rail, back upright with push handle, front upright, armrest loop
    x = xf
    d.tube(f"low{i}", [[x, 270, 240], [x, 280, cz - 30], [xc, 300, cz - 30]], 24, "chrome", bend=30)
    d.tube(f"back{i}", [[x, 260, 250], [x, 880, 240], [x, 880, 175]], 24, "chrome", bend=50)
    d.cyl(f"grip{i}", [x, 880, 205], [x, 880, 120], 32, "grip")
    d.cyl(f"seat-rail{i}", [x, 505, 250], [x, 505, 810], 24, "chrome")
    d.tube(f"front{i}", [[x, 505, 810], [x, 470, 860], [x, 300, cz - 30]], 24, "chrome", bend=40)
    d.tube(f"armloop{i}", [[x, 505, 300], [x, 725, 300], [x, 725, 690], [x, 560, 700]], 22, "chrome", bend=40)
    d.box(f"guard{i}", [x + s * 4 - 2, 525, 300, x + s * 4 + 2, 700, 650], "guard", r=1)
    # brake lever
    d.cyl(f"brake{i}", [x + s * 18, 470, 520], [x + s * 18, 560, 470], 14, "chrome")
    d.sphere(f"brake-knob{i}", [x + s * 18, 565, 467], 24, "grip")
    # anti-tip tube at the back bottom
    d.tube(f"tip{i}", [[x, 270, 250], [x, 210, 160], [x, 170, 90]], 20, "chrome", bend=30)
    d.cyl(f"tip-end{i}", [x, 170, 90], [x, 165, 70], 24, "grip")
    # swing-away footrest hanger and grey footplate
    d.tube(f"hanger{i}", [[x - s * 0, 500, 820], [x - s * 10, 450, 880], [x - s * 25, 170, 1010]], 20, "chrome", bend=40)
    xp = (x + 10, x + 190) if i == 0 else (x - 190, x - 10)
    d.box(f"footplate{i}", [xp[0], 140, 960, xp[1], 156, 1095], "plate", r=4)
# folding X brace under the seat
d.cyl("brace-a", [92, 505, 520], [W - 92, 300, 520], 20, "chrome")
d.cyl("brace-b", [W - 92, 505, 520], [92, 300, 520], 20, "chrome")
# seat cushion and backrest upholstery
d.box("seat", [96, 505, 270, W - 96, 560, 790], "seat", r=18, puff=6)
d.box("back", [96, 540, 238, W - 96, 870, 252], "blk", r=6, puff=4)
# lap tray on the armrests: orange battens, light wood top with a body cut-out at the back
for i, x in enumerate((92, W - 92)):
    d.box(f"batten{i}", [x - 26, 727, 330, x + 26, 767, 900], "batten", r=4)
# (photo: a small round notch in the back edge, right of the middle; thick yellow-orange batten under the left edge)
tray = "M 30 340 L 312 340 Q 318 340 320 348 Q 330 410 380 410 Q 430 410 440 348 Q 442 340 448 340 L 610 340 L 610 890 Q 610 920 580 920 L 60 920 Q 30 920 30 890 Z"
d.slab("tray-edge", "top", tray, [767, 782], "edge", r=3)
d.slab("tray", "top", tray, [781, 785], "tray", r=1.5)
d.save()
