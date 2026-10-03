"""XYH-1 seated ankle exerciser: long white base beam, a pedestal with the seat frame and a white-framed grey seat and
backrest at the back, two black footplates on pivot shafts at the front end (z = depth), two chrome levers with black
grips pivoting at the ends of the seat frame's front bar and leaning toward the footplates."""
from k6lib import *

W, DEP, H = 650, 1300, 880
d = D("xyh-1", [W, DEP, H], {"white": "plastic#eeefed", "grey": "leather#6d7177", "black": "rubber#2a2c30",
                             "alu": "metal#d6d8da", "blue": "gloss#2b56a8"})
CX = W / 2
# base beam and the pedestal
d.box("beam", [CX - 100, 0, 380, CX + 100, 190, DEP - 70], "white", r=10)
d.box("pedestal", [CX - 165, 0, 250, CX + 165, 430, 660], "white", r=10)
# floor loop (white tube) round the back for stability
d.tube("loop", [[CX - 165, 22, 520], [30, 22, 520], [30, 22, 40], [W - 30, 22, 40], [W - 30, 22, 520], [CX + 165, 22, 520]],
       28, "white", bend=70)
# seat frame: front cross bar with a blue label, side chrome rods, rear bar, small end knobs
d.box("front-bar", [CX - 205, 430, 640, CX + 205, 478, 680], "alu", r=6)
d.decal("label", [CX - 40, 456, 680.6], [190, 16], "front", "blue", soft=True)
d.box("rear-bar", [CX - 175, 430, 250, CX + 175, 470, 285], "alu", r=6)
d.cyl("rod", [CX - 150, 458, 285], [CX - 150, 458, 640], 18, "chrome", mirror="x")
d.box("end-knob", [CX + 175, 438, 255, CX + 195, 462, 280], "plastic#1d1f22", r=4, mirror="x")
# seat: grey pad on a white pan, backrest in a white tube frame tilted back
d.box("seat-pan", [CX - 165, 478, 275, CX + 165, 498, 640], "white", r=8)
d.box("seat", [CX - 158, 492, 282, CX + 158, 545, 632], "grey", r=20, puff=5)
br = rot("x", -10, [CX, 520, 280])
d.sweep("back-frame", [[CX - 165, 520, 268], [CX - 165, H - 15, 268], [CX + 165, H - 15, 268], [CX + 165, 520, 268]],
        [26, 26], "white", shape="round", bend=70, rot=br)
d.box("back-pad", [CX - 150, 560, 262, CX + 150, H - 32, 300], "grey", r=16, puff=4, rot=br)
d.box("back-panel", [CX - 160, 540, 248, CX + 160, H - 25, 262], "white", r=10, rot=br)
# levers: pivot plates at the ends of the front bar, chrome rods leaning forward, black grips
for s, x in (("l", CX - 222), ("r", CX + 222)):
    d.box(f"pivot-{s}", [x - 12, 420, 625, x + 12, 485, 690], "alu", r=5)
    d.cyl(f"pivot-pin-{s}", [x - 20, 455, 660], [x + 20, 455, 660], 26, "chrome")
    top = [x, H - 5, 930]
    d.cyl(f"lever-{s}", [x, 455, 660], [x, H - 120, 930 - 120 * 0.64], 20, "chrome")
    d.cyl(f"grip-{s}", [x, H - 125, 930 - 125 * 0.64], top, 32, "black")
# footplates (photo): two black moulded shoe plates side by side ON TOP of the beam's front end, toes overhanging the
# beam end and turned a little outward; a deep heel cup with a high back wall, a low outer side wall; each plate on a
# chrome pivot standing on the beam top
BE = DEP - 70                                 # beam front end; the toes overhang it
for s_, sx in (("l", -1), ("r", 1)):
    xc = CX + sx * 128                        # plate centre line (they overhang the beam sides)
    x0, x1 = xc - 75, xc + 75
    Z0, Z1 = 960, DEP - 2
    turn = rot("y", sx * 7, [xc, 0, 1000])   # toe out (about the heel)
    out = (f"M {x0 + 20} {Z0} L {x1 - 20} {Z0} Q {x1} {Z0} {x1} {Z0 + 25} L {x1 - 6} {Z1 - 70} "
           f"Q {x1 - 10} {Z1} {xc} {Z1} Q {x0 + 10} {Z1} {x0 + 6} {Z1 - 70} L {x0} {Z0 + 25} Q {x0} {Z0} {x0 + 20} {Z0} Z")
    d.slab(f"foot-{s_}", "top", out, [212, 232], "black", r=6, rot=turn)
    # heel cup: U-shaped wall round the heel, high at the back
    cup = (f"M {x0} {Z0 + 150} L {x0} {Z0 + 20} Q {x0} {Z0} {x0 + 20} {Z0} L {x1 - 20} {Z0} Q {x1} {Z0} {x1} {Z0 + 20} "
           f"L {x1} {Z0 + 150} L {x1 - 16} {Z0 + 150} L {x1 - 16} {Z0 + 30} Q {x1 - 16} {Z0 + 16} {x1 - 30} {Z0 + 16} "
           f"L {x0 + 30} {Z0 + 16} Q {x0 + 16} {Z0 + 16} {x0 + 16} {Z0 + 30} L {x0 + 16} {Z0 + 150} Z")
    d.slab(f"heel-{s_}", "top", cup, [228, 300], "black", r=6, rot=turn)
    # low outer side wall toward the toe
    xo = x1 - 16 if sx > 0 else x0
    d.box(f"wall-{s_}", [xo, 228, Z0 + 140, xo + 16, 262, Z0 + 250], "black", r=6, rot=turn)
    # pivot: chrome stem and a small housing on the beam top
    d.cyl(f"fpivot-{s_}", [xc, 188, 1060], [xc, 214, 1060], 40, "chrome")
    d.box(f"fpivot-box-{s_}", [xc - 30, 186, 1035, xc + 30, 200, 1090], "alu", r=4)
d.save()
