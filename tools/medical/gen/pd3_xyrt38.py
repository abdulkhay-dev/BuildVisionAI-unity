"""xyrt-38 — children hip-joint trainer (abduction/adduction): grey square-tube chair, blue seat and back, two leg
levers with blue cuffs on small castors in front (the right one swung out, as in the photo), chrome handles."""
import math
from pd3_lib import *

W, Dp, H = 600, 820, 720
d = D("xyrt-38", [W, Dp, H], {"fr": "plastic#c9ccd0", "blue": "leather#3557ad", "black": "plastic#1b1c1e",
                              "strap": "fabric#18191b", "feet": "rubber#1d1e20"})
M = "x"
# floor frame + uprights + seat frame
d.box("rail", [60, 0, 40, 100, 40, 600], "fr", r=4, mirror=M)
d.box("foot", [60, -0.1, 40, 100, 8, 80], "feet", r=2, mirror=M, copies=[[0, 0, 520]])
d.box("xrear", [100, 0, 60, 500, 40, 100], "fr", r=4)
d.box("xfront", [100, 0, 520, 500, 40, 560], "fr", r=4)
d.box("upr", [75, 40, 80, 110, 380, 115], "fr", r=4, mirror=M, copies=[[0, 0, 410]])
d.box("side-str", [75, 140, 115, 110, 172, 490], "fr", r=4, mirror=M)
d.box("sf-side", [70, 360, 75, 112, 400, 530], "fr", r=4, mirror=M)
d.box("sf-front", [112, 360, 490, 488, 400, 530], "fr", r=4)
d.box("sf-rear", [112, 360, 75, 488, 400, 115], "fr", r=4)
d.box("brk", [66, 356, 490, 116, 404, 534], "black", r=3, mirror=M, copies=[[0, 0, -415]])
# seat, back with chrome frame, armrests
d.box("seat", [80, 400, 100, 520, 462, 545], "blue", r=24, puff=5)
RB = rot("x", -10, [300, 445, 85])
d.box("back", [112, 445, 62, 488, 712, 112], "blue", r=30, puff=4, rot=RB)
d.tube("back-frame", [[104, 400, 58], [104, 716, 58], [496, 716, 58], [496, 400, 58]], 16, "chrome", bend=70, rot=RB)
d.tube("arm-loop", [[78, 400, 150], [78, 595, 150], [78, 595, 440], [78, 400, 480]], 20, "chrome", bend=50, mirror=M)
# black foam pad over the loop's top, wrapping down round its front bend (photo)
d.tube("arm-pad", [[78, 612, 140], [78, 612, 430], [78, 540, 468]], 36, "black", bend=46, mirror=M)
# mechanism under the seat front
d.cyl("screw", [150, 285, 470], [450, 285, 470], 18, "chrome")
d.coil("spring", [175, 285, 470], [265, 285, 470], 34, 5, 9, "chrome")
d.cyl("nut", [300, 285, 470], [325, 285, 470], 42, "chrome", sides=6, copies=[[70, 0, 0]])
d.cyl("turntable", [300, 340, 430], [300, 358, 430], 130, "chrome")
d.cyl("turnhub", [300, 300, 430], [300, 340, 430], 60, "chrome")
# rear diagonal adjustment handles (chrome, ribbed grips) with knobs at the frame side
d.cyl("handle", [38, 595, 120], [38, 300, 330], 20, "chrome", mirror=M)
d.tube("grip", [[38, 712, 37], [38, 595, 120]], 30, "chrome", rib=3, pitch=10, mirror=M)
d.cyl("h-knob", [10, 300, 330], [75, 300, 330], 42, "chrome", mirror=M)
d.cyl("h-pin", [38, 300, 330], [75, 300, 330], 16, "chrome", mirror=M, copies=[[0, 30, -40]])


def lever(id, px, deg):
    """lever pivoting at (px, 340, 500), built pointing forward, turned about y by deg (+ = swung to +x)."""
    R = rot("y", deg, [px, 0, 500])
    a, b = [px, 340, 500], [px, 72, 780]
    for k, o in enumerate((-20, 20)):
        d.cyl(f"{id}-rod{k}", [a[0] + o, a[1], a[2]], [b[0] + o, b[1], b[2]], 14, "chrome", rot=R)
    d.box(f"{id}-pivot", [px - 32, 322, 470, px + 32, 360, 530], "chrome", r=4, rot=R)
    d.add(f"{id}-cast", "caster", "rubber#2a2b2d", at=[px, 0, 790], d=46, rot=R)
    d.box(f"{id}-end", [px - 28, 66, 760, px + 28, 80, 800], "chrome", r=3, rot=R)
    u, L = unit(a, b)
    n = [0, u[2], -u[1]]  # up-normal in the lever plane
    # one long blue cuff (thigh to shin) on the twin rods, two black straps round it (photo)
    t0, t1 = 0.1, 0.78
    p0 = [a[i] + u[i] * L * t0 + n[i] * 52 for i in range(3)]
    p1 = [a[i] + u[i] * L * t1 + n[i] * 52 for i in range(3)]
    d.bar(f"{id}-cuff", p0, p1, [112, 78], "blue", r=26, rot=R)
    for k, tt in enumerate((0.2, 0.78)):
        m0 = along(p0, p1, tt - 0.07); m1 = along(p0, p1, tt + 0.07)
        d.bar(f"{id}-strap{k}", m0, m1, [120, 86], "strap", r=26, rot=R)
    # vertical hinge pin of the abduction pivot
    d.cyl(f"{id}-hinge", [px, 300, 500], [px, 398, 500], 22, "chrome", rot=R)
    # chrome U loop under the lever
    q0 = [a[i] + u[i] * L * 0.3 for i in range(3)]; q1 = [a[i] + u[i] * L * 0.6 for i in range(3)]
    d.tube(f"{id}-loop", [q0, [q0[0], q0[1] - 90, q0[2] + 20], [q1[0], q1[1] - 60, q1[2]], q1], 14, "chrome", bend=30, rot=R)


lever("lv-l", 205, 0)
lever("lv-r", 395, 26)
d.save()
