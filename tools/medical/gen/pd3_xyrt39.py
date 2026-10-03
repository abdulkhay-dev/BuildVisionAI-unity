"""xyrt-39 — children quadriceps chair: off-white frame, navy seat and tall back, two knee levers at the front corners
(chrome hubs with ratchet discs, black rollers, green weight plates, black ankle cuffs), spare plates on floor pegs."""
import math
from pd3_lib import *


def circ(cx, cy, r):
    return f"M {cx - r:.1f} {cy:.1f} A {r} {r} 0 1 0 {cx + r:.1f} {cy:.1f} A {r} {r} 0 1 0 {cx - r:.1f} {cy:.1f} Z"

W, Dp, H = 740, 800, 940
d = D("xyrt-39", [W, Dp, H], {"fr": "plastic#dcdedb", "blue": "leather#3d4f9a", "navy": "leather#2d3c78",
                              "black": "plastic#1b1c1e", "foam": "rubber#1c1d20", "plate": "plastic#2f7a4c",
                              "cap": "rubber#1d1e20"})
M = "x"
d.box("rail", [100, 0, 25, 135, 35, 775], "fr", r=4, mirror=M)
d.box("cap", [98, 0, 0, 137, 37, 25], "cap", r=4, mirror=M, copies=[[0, 0, 775]])
d.box("xrear", [135, 0, 40, 605, 35, 75], "fr", r=4)
d.box("xfront", [135, 0, 735, 605, 35, 770], "fr", r=4)
d.box("xmid", [135, 0, 540, 605, 30, 575], "fr", r=4)
# legs, stretchers, seat frame
d.bar("rleg", [118, 35, 110], [165, 400, 290], [30, 30], "fr", r=4, mirror=M)
d.box("fleg", [155, 35, 615, 185, 400, 645], "fr", r=4, mirror=M)
d.bar("str", [150, 205, 225], [170, 205, 615], [28, 28], "fr", r=4, mirror=M)
d.box("sframe", [150, 380, 270, 590, 410, 660], "fr", r=5)
# seat, back, back support with knob, armrests
d.box("seat", [150, 408, 268, 590, 466, 672], "blue", r=24, puff=5)
RB = rot("x", -10, [370, 455, 250])
d.box("back", [165, 455, 222, 575, 940, 278], "blue", r=34, puff=4, rot=RB)
d.box("back-rim", [160, 450, 210, 580, 935, 226], "fr", r=30, rot=RB)
d.box("bsup", [138, 380, 225, 158, 570, 275], "plastic#b9bcc0", r=4, mirror=M)
d.cyl("bknob", [138, 470, 250], [100, 470, 250], 44, "black")
d.cyl("bknob-r", [602, 470, 250], [640, 470, 250], 44, "black")
d.tube("arm-sup", [[145, 410, 600], [145, 605, 600], [145, 605, 500]], 22, "fr", bend=40, mirror=M)
d.box("arm-pad", [120, 600, 330, 172, 636, 600], "navy", r=16, mirror=M)


def unit_lever(id, x, sg, roller_dir, plate_y):
    """sg = -1 left (outer side -x), +1 right."""
    z = 700
    d.box(f"{id}-post", [x - 15, 35, z - 30, x + 15, 470, z], "chrome", r=3)
    d.cyl(f"{id}-hub", [x - 40, 485, z], [x + 40, 485, z], 100, "chrome")
    xo = x + sg * 40
    # perforated ratchet disc: a ring of 16 real holes near the rim + a toothed edge look (photo)
    holes = " ".join(circ(z + 47 * math.cos(math.radians(k * 22.5)), 485 + 47 * math.sin(math.radians(k * 22.5)), 5)
                     for k in range(16))
    d.slab(f"{id}-disc", "side", circ(z, 485, 62) + " " + holes, sorted([xo, xo + sg * 8]), "metal#b3b7bc", r=1)
    d.cyl(f"{id}-cap", [xo + sg * 10, 485, z], [xo + sg * 22, 485, z], 50, "chrome")
    d.box(f"{id}-lever", [x - 15, 110, z + 5, x + 15, 480, z + 35], "chrome", r=3)
    for k, yy in enumerate((410, 340, 240)):
        d.cyl(f"{id}-knob{k}", [x + sg * 15, yy, z + 20], [x + sg * 45, yy, z + 20], 34, "black")
    # roller across (direction as in the photo)
    r0 = x + roller_dir * 15
    d.cyl(f"{id}-roller", [r0, 300, z + 20], [r0 + roller_dir * 160, 300, z + 20], 56, "foam", sides=20)
    # weight bar and plate on the outer side
    d.cyl(f"{id}-wbar", [x, plate_y, z + 20], [x + sg * 75, plate_y, z + 20], 24, "chrome")
    d.cyl(f"{id}-plate", [x + sg * 22, plate_y, z + 20], [x + sg * 48, plate_y, z + 20], 180, "plate", sides=32)
    # black ankle cuff at the bottom, pointing inwards
    xi = x - sg * 15
    # black ankle cuff: a padded U (open to the back, round the front of the ankle) running inwards from the lever
    zc, yc, ro, ri = z + 40, 150, 58, 34
    u = (f"M {zc - 45} {yc + ro} L {zc} {yc + ro} C {zc + ro * 1.3} {yc + ro} {zc + ro * 1.3} {yc - ro} {zc} {yc - ro} "
         f"L {zc - 45} {yc - ro} L {zc - 45} {yc - ri} L {zc} {yc - ri} C {zc + ri * 1.3} {yc - ri} {zc + ri * 1.3} "
         f"{yc + ri} {zc} {yc + ri} L {zc - 45} {yc + ri} Z")
    d.slab(f"{id}-cuff", "side", u, sorted([xi, xi - sg * 140]), "foam", r=8)
    d.box(f"{id}-cuffbrk", [min(xi, xi - sg * 30), 130, z + 5, max(xi, xi - sg * 30), 170, z + 35], "chrome", r=4)


unit_lever("lv-l", 120, -1, 1, 165)
unit_lever("lv-r", 618, 1, 1, 290)
# spare plates on floor pegs
d.cyl("peg1", [117, 35, 470], [117, 170, 470], 26, "chrome")
d.cyl("pl1", [117, 35, 470], [117, 85, 470], 180, "plate", sides=32)
d.cyl("pl1-gap", [117, 59, 470], [117, 61, 470], 182, "plastic#255f3b", soft=True)
d.cyl("peg2", [370, 30, 557], [370, 150, 557], 26, "chrome")
d.cyl("pl2", [370, 30, 557], [370, 55, 557], 180, "plate", sides=32)
d.save()
