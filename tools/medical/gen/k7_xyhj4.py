"""xyhj-4 Multifunctional Anklebone Rectification Board: white notched base, two ribbed white footboards hinged at
the centre line and tilted up into a V (35° each), light lilac-grey foam block lying in the valley."""
from k7lib import *

d = D("xyhj-4", [350, 450, 200], {
    "white": "plastic#eceef0", "board": "plastic#e4e7ec", "foam": "leather#c3c4d4", "black": "plastic#17181a",
    "groove": "plastic#c9ccd2", "rubber": "rubber#1c1d1f"})
# --- base: two notched side channels, front/back plates, centre hinge bar, small black feet, black stand bracket
# side channels (photo: an open U trough along each side, the inner wall notched for the props)
d.box("side-floor", [0, 8, 0, 40, 16, 450], "white", r=3, mirror="x")
d.box("side-outer", [0, 8, 0, 7, 40, 450], "white", r=2, mirror="x")
d.box("side-inner", [30, 8, 0, 40, 52, 450], "white", r=2, mirror="x")
d.box("notch", [29, 44, 60, 41, 53, 74], "groove", r=1, repeat={"n": 8, "step": [0, 0, 44]}, soft=True, mirror="x")
d.box("end-plate", [0, 8, 0, 350, 40, 14], "white", r=4, copies=[[0, 0, 436]])
d.box("floor-plate", [28, 8, 14, 322, 14, 436], "white", r=2)
d.cyl("hinge", [175, 42, 8], [175, 42, 442], 18, "white")
d.cyl("foot", [16, 0, 16], [16, 9, 16], 16, "rubber", copies=[[318, 0, 0], [0, 0, 418], [318, 0, 418]])
d.bar("stand", [8, 2, 300], [8, 46, 410], [10, 22], "black", r=2)
d.box("stand-foot", [2, 0, 290, 16, 6, 330], "black", r=2)
# --- two footboards hinged at the centre, tilted up into a V; ribbed tops, props sitting in the rail notches
for nm, x0, x1, deg in (("l", 16, 173, -35), ("r", 177, 334, 35)):
    piv = [173 if nm == "l" else 177, 42, 225]
    t = rot("z", deg, piv)
    d.box(f"board-{nm}", [x0, 42, 12, x1, 62, 438], "board", r=5, rot=t)
    d.box(f"board-lip-{nm}", [x0 if nm == "l" else x1 - 10, 42, 12, x0 + 10 if nm == "l" else x1, 70, 438], "board", r=4, rot=t)
    d.decal(f"rib-{nm}", [x0 + 22, 62.6, 225], [4, 410], "groove", face="top", soft=True, rot=t,
            repeat={"n": 9, "step": [15, 0, 0], "local": True})
    d.box(f"hinge-cap-{nm}", [x1 - 22 if nm == "l" else x0, 44, 4, x1 if nm == "l" else x0 + 22, 60, 14], "black", r=3, rot=t)
    xo = 50 if nm == "l" else 300
    xr = 35 if nm == "l" else 315
    d.tube(f"prop-{nm}", [[xr, 54, 92], [xo, 124, 100], [xo, 124, 350], [xr, 54, 358]], 10, "white", bend=10)
# hinge brackets with two dark bolt heads at the front end of the centre hinge (photo)
d.box("hinge-bracket", [150, 30, 436, 200, 66, 446], "white", r=4)
d.cyl("hinge-bolt", [163, 50, 446], [163, 50, 451], 11, "plastic#3a3a36", copies=[[24, 0, 0]])
# --- foam block lying in the valley
d.box("foam", [124, 88, 75, 226, 190, 375], "foam", r=10, puff=3)
d.save()
