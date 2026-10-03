"""XY-DSSZ-02A pec dec / fly (hydraulic exerciser). Patient sits facing +z."""
from k9lib import *
d = K("xy-dssz-02a", [1100, 800, 1300], dict(EX_MATS, box="plastic#f4f3ef"))
CX = 550
foot(d, "foot-f", 375, 725, 715)
foot(d, "foot-r", 380, 720, 95)
d.cyl("post", [CX, 40, 710], [CX, 425, 690], TUBE, "frame")
d.sweep("spine", [[CX, 60, 140], [CX, 250, 230], [CX, 380, 380], [CX, 410, 560]], [60, 46], "frame", shape="oval", bend=150)
d.box("seat-plate", [CX - 90, 418, 360, CX + 90, 432, 690], "dark", r=4)
seat(d, "seat", CX, 330, 715, 330, 410, 432)
zf, BR = back(d, "back", CX, 540, 1300, 265, 290, 240, tilt=-7, rt=110)
logo(d, "logo", CX, 1120, zf, h=32, R=BR)
d.box("hinge", [CX - 50, 470, 235, CX + 50, 555, 320], "dark", r=10)
d.sweep("support", [[CX, 400, 380], [CX, 420, 230], [CX, 560, 205], rotx([CX, 1250, 205], -7, [CX, 540, 240])],
        [50, 35], "frame", shape="oval", bend=60)
# pivot hub under the seat: chrome hub, black resistance unit, pop pin with a black knob
d.cyl("hub", [CX, 330, 420], [CX, 410, 420], 90, "chrome")
d.cyl("hub-cyl", [CX, 300, 420], [CX, 335, 420], 110, "cyl")
d.cyl("pin", [CX - 40, 370, 470], [CX - 150, 360, 560], 14, "chrome")
d.sphere("pin-knob", [CX - 155, 360, 565], 32, "cap")
# the two swinging arms: out sideways from the hub, up to the elbow-pad boxes, black handles above
for nm, s in (("l", -1), ("r", 1)):
    n0 = len(d.d["parts"])
    xo = CX + s * 420
    d.tube(f"arm-{nm}", [[CX, 360, 420], [CX + s * 200, 360, 430], [xo, 380, 480], [xo, 560, 540], [xo + s * 10, 730, 560]],
           42, "frame", bend=110)
    # box: white, its pads on the inner face (towards the patient's arms), two dark marks on the outer face
    x0, x1 = (xo - 35, xo + 35)
    d.box(f"pbox-{nm}", [x0, 720, 500, x1, 890, 680], "box", r=14)
    d.decal(f"pbox-dot-{nm}", [xo + s * 35.6, 820, 560], [12, 12], "right" if s > 0 else "left", "dark",
            copies=[[0, 0, 50]])
    xi = xo - s * 35
    d.box(f"pad-a-{nm}", sorted([xi, xi - s * 55])[:1] + [735, 505] + sorted([xi, xi - s * 55])[1:] + [880, 590], "blue", r=16,
          rot=rot("y", s * 18, [xi, 800, 590]))
    d.box(f"pad-b-{nm}", sorted([xi, xi - s * 55])[:1] + [735, 590] + sorted([xi, xi - s * 55])[1:] + [880, 675], "blue", r=16,
          rot=rot("y", -s * 18, [xi, 800, 590]))
    d.box(f"pad-pipe-{nm}", sorted([xi, xi - s * 12])[:1] + [732, 502] + sorted([xi, xi - s * 12])[1:] + [883, 678], "pipe", r=4)
    # handle: from the outer front of the box forward, then up, its top bent inward; black foam on the upright
    hx = xo + s * 30
    path = [[hx, 760, 680], [hx + s * 25, 760, 740], [hx + s * 25, 1010, 745], [hx - s * 5, 1120, 735]]
    d.tube(f"hbar-{nm}", path, 30, "frame", bend=40)
    grip(d, f"handle-{nm}", [hx + s * 25, 790, 742], [hx + s * 25, 1030, 744], dia=40)
    d.tube(f"handle-top-{nm}", [[hx + s * 25, 1025, 744], [hx + s * 22, 1085, 742], [hx - s * 5, 1120, 735]], 40, "foam", bend=35)
    if s < 0:
        # (review 2026-10-03) follow the photo: the patient's right arm is swung out and up about the hub (its
        # upright leans outward, the pad box higher and further out); the left arm stays in the start position
        mark(n0, d, rots=[rot("z", 28, [CX, 360, 420])])
d.save()
