"""XY-20 posture mirror and XY-21 posture mirror with grid (kinesio-3). Writes xy-20.json and xy-21.json."""
from k3_lib import *


def mirror(id_, grid):
    W, Dd, H = 850, 670, 1910
    d = D(id_, [W, Dd, H], {"gold": "metal#b9a468", "frame": "plastic#eceeee", "glass": "gloss#dfeaf2"})
    # (review) the engine mirror read mid grey; the photo glass is a light bluish white: glossy light-blue face
    zc = 335
    X0, X1 = 48, W - 48           # mirror frame outer
    Y0, Y1 = 150, H              # frame bottom / top
    F = 60                       # frame profile face width ((review) photo: ~63 mm)
    T = 40                       # frame depth
    # gold aluminium frame: four profiles with a chamfered inner lip
    d.box("fr-l", [X0, Y0, zc - T / 2, X0 + F, Y1, zc + T / 2], "gold", r=3, mirror="x")
    d.box("fr-t", [X0 + F, Y1 - F, zc - T / 2, X1 - F, Y1, zc + T / 2], "gold", r=3)
    d.box("fr-b", [X0 + F, Y0, zc - T / 2, X1 - F, Y0 + F + 8, zc + T / 2], "gold", r=3)
    d.box("lip-l", [X0 + F - 2, Y0 + F, zc + 6, X0 + F + 8, Y1 - F, zc + 14], "metal#8f7f4c", mirror="x")
    d.box("lip-t", [X0 + F, Y1 - F - 8, zc + 6, X1 - F, Y1 - F + 2, zc + 14], "metal#8f7f4c")
    d.box("lip-b", [X0 + F, Y0 + F + 6, zc + 6, X1 - F, Y0 + F + 14, zc + 14], "metal#8f7f4c")
    # glass (mirror) with a thin blue-green edge, white back board
    d.box("glass", [X0 + F, Y0 + F + 8, zc - 2, X1 - F, Y1 - F, zc + 6], "glass")
    d.box("edge", [X0 + F - 1, Y0 + F + 7, zc - 3, X1 - F + 1, Y1 - F + 1, zc + 4], "plastic#5f8f92")
    d.box("back", [X0 + 6, Y0 + 6, zc - T / 2 - 2, X1 - 6, Y1 - 6, zc - T / 2 + 1], "plastic#d8d8d4")
    if grid:
        gx0, gx1, gy0, gy1 = X0 + F, X1 - F, Y0 + F + 8, Y1 - F
        n = int((gx1 - gx0) // 100)
        off = ((gx1 - gx0) - n * 100) / 2
        d.decal("gv", [gx0 + off, (gy0 + gy1) / 2, zc + 6.6], [3, gy1 - gy0], "plastic#b3bec8", face="front", soft=True,
                repeat=rep(n + 1, [100, 0, 0]))
        m = int((gy1 - gy0) // 100)
        offy = ((gy1 - gy0) - m * 100) / 2
        d.decal("gh", [(gx0 + gx1) / 2, gy0 + offy, zc + 6.6], [gx1 - gx0, 3], "plastic#b3bec8", face="front", soft=True,
                repeat=rep(m + 1, [0, 100, 0]))
    # A-shaped side stands (white square tubes) clamping the frame sides, 4 castors
    xs = 22
    for nm, x in (("l", xs), ("r", W - xs)):
        d.bar(f"st-base-{nm}", [x, 62, 25], [x, 62, Dd - 25], [28, 28], "frame", r=3)
        d.bar(f"st-f-{nm}", [x, 62, Dd - 70], [x, 520, zc + 18], [26, 26], "frame", r=3)
        d.bar(f"st-b-{nm}", [x, 62, 70], [x, 520, zc - 18], [26, 26], "frame", r=3)
        d.box(f"st-top-{nm}", [x - 16, 470, zc - 30, x + 16, 560, zc + 30], "frame", r=4)
        d.cyl(f"knob-{nm}", [x + (-1 if nm == "l" else 1) * 16, 515, zc], [x + (-1 if nm == "l" else 1) * 34, 515, zc], 30,
              "plastic#2a2b2d")
        d.box(f"st-cap-{nm}", [x - 15, 48, 18, x + 15, 76, 34], "plastic#2a2b2d", copies=[[0, 0, Dd - 52]])
        d.caster(f"cas-{nm}", [x, 0, 60], 48, "rubber", copies=[[0, 0, Dd - 120]])
    # low cross tube under the mirror between the stands, black latch near the right
    d.bar("cross", [xs, 100, zc], [W - xs, 100, zc], [24, 24], "frame", r=3)
    d.box("latch", [X1 - 70, 112, zc - 14, X1 - 40, 148, zc + 14], "plastic#2a2b2d", r=3)
    d.save()


mirror("xy-20", False)
mirror("xy-21", True)
