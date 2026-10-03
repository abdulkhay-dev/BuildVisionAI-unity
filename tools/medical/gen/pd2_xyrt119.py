# XYRT-119 exercise bicycle (children): yellow egg body, red saddle on a blue post, blue heart handlebar, orange counter
import math
from pd2_lib import *

W, D, H = 350, 550, 700
C = W / 2
d = Design("xyrt-119", [W, D, H], {"yel": YEL, "body": "gloss#f5c21a", "red": "gloss#d9262c", "blue": BLU,
                                    "bluep": "plastic#2a5db0", "blk": BLK, "grey": "metal#b9bcc0",
                                    "orange": "gloss#f08a1e", "pedal": "plastic#202124"})
# floor bars across the width, black caps
capped_bar_x(d, "bar-rear", 0, W, 24, 75, 44, "yel", "blk", capl=50)
capped_bar_x(d, "bar-front", 0, W, 24, 480, 44, "yel", "blk", capl=50)
# egg-shaped body (side outline extruded across x), rounded edges: the big end up at the front (under the stem),
# the narrow end down at the rear, sitting on a short grey bracket over the rear bar
X0, X1 = C - 68, C + 68
TH = math.radians(20)          # long axis rising a little toward the front
ZC, YC, A, B = 282, 246, 212, 166


def egg(grow=0.0):
    pts = []
    for k in range(56):
        t = 2 * math.pi * k / 56
        c, s_ = math.cos(t), math.sin(t)
        u = (A + grow) * c
        v = (B + grow) * s_ * (1.0 + 0.26 * c)      # fuller toward +u (front/top), narrower toward the rear
        pts.append((ZC + u * math.cos(TH) - v * math.sin(TH), YC + u * math.sin(TH) + v * math.cos(TH)))
    return svg_poly(pts)


d.slab("body", "side", egg(), [X0, X1], "body", r=44)
d.slab("body-seam", "side", egg(3), [C - 6, C + 6], "body", r=4)     # the ridge where the two shells meet
d.decal("label", [X0 - 0.5, 290, 330], [44, 22], "left", "gloss#7fb4e8", soft=True)
d.decal("label2", [X1 + 0.5, 290, 330], [44, 22], "right", "gloss#7fb4e8", soft=True)
# mounts: short grey brackets down to both floor bars
d.box("mount-rear", [C - 28, 34, 84, C + 28, 140, 126], "grey", r=6)
d.box("mount-front", [C - 26, 34, 458, C + 26, 70, 498], "grey", r=6)
d.cyl("mount-front-tube", [C, 60, 476], [C, 175, 456], 30, "grey")
# cranks (yellow) and black cage pedals on both sides of the lower front: +x pedal forward-down, -x rear-up
HZ, HY = 385, 190
d.cyl("crank-hub", [X0 - 12, HY, HZ], [X1 + 12, HY, HZ], 40, "grey")
for side, sx, ang in (("l", -1, 150), ("r", 1, -30)):
    xh = X0 - 16 if sx < 0 else X1 + 16
    pz, py = HZ + 80 * math.cos(math.radians(ang)), HY + 80 * math.sin(math.radians(ang))
    d.bar(f"crank-{side}", [xh, HY, HZ], [xh, py, pz], [12, 26], "yel", r=5)
    xi = xh + sx * 10            # inner plate of the pedal
    xo = xh + sx * 95            # outer plate
    d.cyl(f"pedal-axle-{side}", [xh, py, pz], [xo, py, pz], 12, "grey")
    ring = ("M {a0} {b0} A 44 34 0 1 0 {a1} {b0} A 44 34 0 1 0 {a0} {b0} Z "
            "M {c0} {b0} A 30 20 0 1 1 {c1} {b0} A 30 20 0 1 1 {c0} {b0} Z").format(
        a0=pz - 44, a1=pz + 44, b0=py, c0=pz - 30, c1=pz + 30)
    for k, xp in enumerate((xi, xo)):
        lo, hi = (xp - 7, xp + 7)
        d.slab(f"pedal-{side}{k}", "side", ring, [lo, hi], "pedal", r=3)
    d.cyl(f"pedal-rod-{side}", [xi, py + 30, pz], [xo, py + 30, pz], 12, "pedal", copies=[[0, -60, 0]])
    d.cyl(f"pedal-rodz-{side}", [xi, py, pz - 40], [xo, py, pz - 40], 12, "pedal", copies=[[0, 0, 80]])
# seat: blue sleeve post from the top rear, red saddle (wide back, narrow nose toward the front)
d.cyl("seat-post", [C, 345, 172], [C, 438, 162], 68, "bluep")
d.cyl("seat-tube", [C, 436, 162], [C, 452, 160], 34, "grey")
d.loft("saddle", [sec(95, 170, 52, 24, C, 470), sec(140, 178, 62, 28, C, 473), sec(205, 130, 54, 24, C, 471),
                  sec(262, 74, 44, 19, C, 468), sec(292, 54, 38, 16, C, 465)], "red", axis="z", dome="both", domeH=14)
# handlebar stem from the body's front top
d.cyl("stem-collar", [C, 385, 400], [C, 430, 406], 48, "bluep")
d.cyl("stem", [C, 425, 405], [C, 540, 425], 30, "yel")
d.cyl("stem-knob", [C, 455, 410], [C, 460, 452], 12, "blk")
d.lathe("stem-knob-head", [C, 457, 452], [[0, 0], [18, 0], [18, 14], [0, 16]], "blk", axis="z")
d.box("stem-clip", [C - 22, 478, 404, C + 22, 498, 432], "blk", r=6)
# counter: small orange round box facing the rider (back, -z) on the stem top
d.lathe("counter", [C, 572, 452], [[0, 0], [42, 0], [44, 6], [44, 34], [40, 40], [0, 40]], "orange", axis="z",
        rot=rot("y", 180, [C, 572, 452]))
d.lathe("counter-face", [C, 572, 411], [[0, 0], [30, 0], [30, 1.5], [0, 1.5]], "plastic#f6f2e6", axis="z",
        rot=rot("y", 180, [C, 572, 411]), soft=True)
# heart-shaped blue foam handlebar (open at the top), black end caps
ZH = 445
arm = [[C + 6, 528, ZH], [C + 60, 560, ZH], [C + 128, 618, ZH], [C + 142, 656, ZH], [C + 112, 680, ZH], [C + 40, 680, ZH]]
d.tube("bar-r", arm, 40, "blue", bend=40)
d.tube("bar-l", [[W - p[0], p[1], p[2]] for p in arm], 40, "blue", bend=40)
d.cyl("bar-cap-r", [C + 52, 680, ZH], [C + 24, 680, ZH], 42, "blk")
d.cyl("bar-cap-l", [C - 52, 680, ZH], [C - 24, 680, ZH], 42, "blk")
d.save()
