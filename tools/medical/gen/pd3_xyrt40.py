"""xyrt-40 — children ankle trainer: white pedestal chair (blue seat and back in chrome frames, two hand levers),
a long low foot box in front ending in a brushed-steel box with two black foot plates; chrome U loop round the
pedestal's back on the floor."""
from pd3_lib import *

W, Dp, H = 540, 900, 750
d = D("xyrt-40", [W, Dp, H], {"white": "plastic#eef0f2", "blue": "leather#3557ad", "black": "plastic#1b1c1e",
                              "plate": "rubber#1c2421", "steel": "metal#b9bcbf", "grip": "rubber#27407e"})
M = "x"
d.tube("loop", [[70, 16, 470], [70, 16, 30], [470, 16, 30], [470, 16, 470]], 26, "chrome", bend=70)
d.box("loop-foot", [58, 0, 50, 82, 4, 80], "rubber#1d1e20", r=2, mirror=M, copies=[[0, 0, 390]])
# pedestal, foot box, steel end box
d.box("ped", [100, 0, 120, 440, 300, 480], "white", r=10)
d.box("seam", [99, 15, 330, 100, 285, 332], "plastic#b6bbc1", soft=True, mirror=M)
d.box("fbox", [145, 0, 470, 395, 150, 765], "white", r=8)
d.box("fbox-top", [150, 146, 475, 390, 155, 760], "plastic#e2e5e8", r=4)
d.box("ebox", [125, 0, 745, 415, 175, 900], "steel", r=6)
# under-seat mechanism, slide rails, knob
d.box("mech", [115, 300, 115, 425, 350, 495], "plastic#7c8288", r=4)
d.box("slide", [82, 318, 40, 102, 338, 500], "chrome", r=3, mirror=M)
d.cyl("knob", [82, 305, 260], [48, 305, 260], 46, "black")
d.cyl("knob-stem", [100, 305, 260], [82, 305, 260], 14, "chrome")
# seat + chrome rim, backrest in a chrome frame
d.box("seat-rim", [64, 348, 85, 476, 362, 512], "chrome", r=6)
d.box("seat", [70, 358, 90, 470, 420, 505], "blue", r=24, puff=5)
RB = rot("x", -10, [270, 420, 120])
d.box("back", [96, 425, 92, 444, 742, 146], "blue", r=26, puff=4, rot=RB)
d.tube("back-frame", [[88, 360, 112], [88, 748, 112], [452, 748, 112], [452, 360, 112]], 18, "chrome", bend=55, rot=RB)
# hand levers on the pedestal sides
d.box("lv-brk", [78, 150, 270, 100, 215, 330], "chrome", r=4, mirror=M)
d.cyl("lever", [88, 182, 300], [70, 690, 420], 22, "chrome", mirror=M)
d.cyl("lv-grip", [72.6, 590, 396], [69.4, 712, 425], 34, "grip", mirror=M)
# foot plates on pivots at the sides of the steel box
for nm, x0, x1 in (("l", 45, 175), ("r", 365, 495)):
    R = rot("x", -8, [(x0 + x1) / 2, 185, 800])
    cx = (x0 + x1) / 2
    d.cyl(f"piv-{nm}", [min(cx, 270), 182, 800], [max(cx, 270) if nm == "r" else 270, 182, 800], 26, "chrome")
    # foot holder (photo): black sole, a C-shaped heel cup curling up round the heel (open to the toes), two
    # arched straps over the instep and the toes
    d.box(f"plate-{nm}", [x0, 188, 650, x1, 204, 895], "plate", r=6, rot=R)
    hz, hy, ro, ri = 700, 250, 58, 46
    cup = (f"M {hz + 10} {hy + ro - 6} C {hz - 34} {hy + ro + 6} {hz - ro - 4} {hy + 26} {hz - ro} {hy} "
           f"C {hz - ro + 4} {hy - 34} {hz - 30} {hy - ro} {hz + 6} {hy - ro + 4} "
           f"L {hz + 6} {hy - ri + 2} C {hz - 22} {hy - ri} {hz - ri + 2} {hy - 26} {hz - ri} {hy} "
           f"C {hz - ri - 4} {hy + 20} {hz - 28} {hy + ri + 4} {hz + 10} {hy + ri - 6} Z")
    d.slab(f"heel-{nm}", "side", cup, [x0 + 4, x1 - 4], "plate", r=4, rot=R)
    for k, (zz, hh, ww) in enumerate(((780, 58, 50), (860, 44, 44))):
        d.strap(f"strap{k}-{nm}", [[x0 + 14, 200, zz], [x0 - 3, 200, zz], [x0 - 3, 200 + hh, zz], [x1 + 3, 200 + hh, zz],
                                    [x1 + 3, 200, zz], [x1 - 14, 200, zz]], [ww, 8], "plate", bend=22, rot=R)
d.save()
