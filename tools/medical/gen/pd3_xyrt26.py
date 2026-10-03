"""xyrt-26 — children pedal chair (extremities recovery device): seat at the back, pedal drum and a big handlebar
in front (z = D)."""
import math
from pd3_lib import *

W, Dp, H = 410, 630, 750
d = D("xyrt-26", [W, Dp, H], {"white": "plastic#f2f3f4", "blue": "leather#2f5fb3", "foam": "rubber#1e2023",
                              "black": "plastic#1b1c1e", "feet": "rubber#202124"})
# floor frame
for nm, x in (("l", 20), ("r", W - 55)):
    d.box(f"rail-{nm}", [x, 25, 30, x + 35, 60, 610], "white", r=5)
    d.box(f"foot-{nm}", [x, 0, 30, x + 35, 25, 70], "feet", r=4, copies=[[0, 0, 540]])
d.box("xrear", [55, 25, 30, W - 55, 60, 65], "white", r=5)
d.box("xfront", [55, 25, 575, W - 55, 60, 610], "white", r=5)
d.box("spine", [187, 25, 65, 223, 60, 575], "white", r=5)
# seat column, knob, slide plate
d.box("column", [180, 60, 110, 230, 372, 160], "white", r=6)
d.cyl("col-knob", [230, 300, 135], [262, 300, 135], 38, "black")
d.box("slide", [160, 60, 200, 250, 70, 330], "chrome", r=3)
d.cyl("slide-knob", [160, 85, 260], [128, 85, 260], 34, "black")
# seat, backrest with its white frame
d.box("seat-plate", [70, 365, 80, 340, 378, 340], "plastic#9aa0a6", r=5)
# thin horseshoe seat: two front horns with a wide concave notch between them (photo)
SEAT = ("M 45 100 Q 45 70 75 70 L 335 70 Q 365 70 365 100 L 365 340 Q 365 360 345 360 L 315 360 Q 296 360 292 342 "
        "C 280 286 130 286 118 342 Q 114 360 95 360 L 65 360 Q 45 360 45 340 Z")
d.slab("seat", "top", SEAT, [376, 404], "blue", r=10)
R = rot("x", -8, [205, 430, 85])
d.box("back", [52, 404, 74, W - 52, 750, 108], "blue", r=16, puff=3, rot=R)
d.tube("back-frame", [[80, 380, 52], [80, 700, 52], [W - 80, 700, 52], [W - 80, 380, 52]], 22, "white", bend=40, rot=R)
d.sphere("back-bolt", [42, 690, 70], 14, "black", copies=[[W - 84, 0, 0]], rot=R)
# black foam armrests: from the back forward, curving down to the seat front
for nm, x in (("l", 38), ("r", W - 38)):
    # inverted L: a short pad forward from the back, then a vertical drop to the seat, a white post below it
    d.tube(f"arm-{nm}", [[x, 612, 95], [x, 612, 228], [x, 455, 240]], 48, "foam", bend=62)
    d.cyl(f"armpost-{nm}", [x, 360, 240], [x, 460, 240], 22, "white")
    d.sphere(f"armbolt-{nm}", [x + (-12 if nm == "l" else 12), 385, 240], 12, "black", soft=True)
# handlebar: white sockets, chrome uprights kinked back, black foam top bar
for nm, x in (("l", 37), ("r", W - 37)):
    d.box(f"sock-{nm}", [x - 20, 60, 555, x + 20, 300, 595], "white", r=6)
    d.tube(f"up-{nm}", [[x, 290, 575], [x, 420, 575], [x, 530, 510], [x, 545, 505]], 25, "chrome", bend=60)
d.cyl("sock-knob", [W - 17, 250, 575], [W + 0, 250, 575], 40, "black")
d.tube("bar", [[37, 532, 505], [37, 625, 487], [W - 37, 625, 487], [W - 37, 532, 505]], 42, "foam", bend=58)
# pedal drum on its pedestal
cy, cz = 225, 430
# drum support: a white bent flat bar from under the drum down and forward to the front rail, chrome foot plate
d.sweep("ped", [[205, 150, 425], [205, 95, 470], [205, 62, 575]], [56, 16], "white", shape="rect", bend=70, r=4)
d.cyl("ped-foot", [205, 60, 585], [205, 64, 585], 74, "chrome")
d.cyl("drum", [140, cy, cz], [270, cy, cz], 180, "white", sides=32)
d.cyl("drum-cap", [132, cy, cz], [278, cy, cz], 58, "black")
for nm, sgn, ang in (("l", -1, 35), ("r", 1, 215)):
    a = math.radians(ang)
    px, py, pz = 205 + sgn * 120, cy + 105 * math.sin(a), cz + 105 * math.cos(a)
    d.bar(f"crank-{nm}", [205 + sgn * 70, cy, cz], [205 + sgn * 70, py, pz], [16, 26], "chrome", r=5)
    d.cyl(f"spindle-{nm}", [205 + sgn * 70, py, pz], [px, py, pz], 16, "chrome")
    # pedal shoe (rigid on its crank, so the lower one is upside down as in the photo): black sole, a C-shaped
    # heel cup curling from the heel up over the ankle (open towards the toes, see-through from the side), toe strap
    R2 = rot("x", 180, [px, py, pz]) if ang > 180 else None
    d.box(f"sole-{nm}", [px - 38, py - 8, pz - 78, px + 38, py + 8, pz + 82], "black", r=6, rot=R2)
    cz0, cy0, ro, ri = pz - 34, py + 62, 66, 48
    cup = (f"M {cz0 + 12} {cy0 + ro - 4} C {cz0 - 40} {cy0 + ro + 8} {cz0 - ro - 6} {cy0 + 30} {cz0 - ro} {cy0} "
           f"C {cz0 - ro + 4} {cy0 - 40} {cz0 - 30} {cy0 - ro} {cz0 + 10} {cy0 - ro + 2} "
           f"L {cz0 + 10} {cy0 - ri + 2} C {cz0 - 22} {cy0 - ri} {cz0 - ri + 2} {cy0 - 30} {cz0 - ri} {cy0} "
           f"C {cz0 - ri - 4} {cy0 + 24} {cz0 - 32} {cy0 + ri + 6} {cz0 + 12} {cy0 + ri - 4} Z")
    d.slab(f"heel-{nm}", "side", cup, [px - 36, px + 36], "black", r=4, rot=R2)
    # toe strap: starts horizontally under the sole edge so its width lies along the foot (z)
    d.strap(f"toe-{nm}", [[px - 28, py + 6, pz + 42], [px - 41, py + 6, pz + 42], [px - 41, py + 42, pz + 42],
                           [px + 41, py + 42, pz + 42], [px + 41, py + 6, pz + 42], [px + 28, py + 6, pz + 42]],
            [44, 7], "fabric#1d1e21", bend=16, rot=R2)
d.save()
