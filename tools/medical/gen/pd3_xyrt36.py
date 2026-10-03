"""xyrt-36 — children OT table, height adjustable (drawn at 800): wood top on a white T-leg base with a hand crank."""
from pd3_lib import *

W, Dp, H = 1200, 750, 800
d = D("xyrt-36", [W, Dp, H], {"wood": "plastic#d6a96c", "edge": "plastic#a8763e", "white": "plastic#f1f2f2",
                              "sleeve": "metal#6b625a", "crank": "metal#5a2a22", "foot": "rubber#1c1d1f"})
d.box("top", [0, H - 28, 0, W, H, Dp], "wood", r=6)
d.box("top-edge", [2, H - 30, 2, W - 2, H - 22, Dp - 2], "edge", r=4)
zc = Dp / 2
for nm, x in (("l", 215), ("r", W - 215)):
    # top bracket under the top
    d.box(f"brk-{nm}", [x - 45, H - 70, zc - 230, x + 45, H - 30, zc + 230], "white", r=6)
    # column: white upper part, dark lower sleeve
    d.box(f"col-{nm}", [x - 30, 190, zc - 28, x + 30, H - 70, zc + 28], "white", r=5)
    # the dark outer sleeve is a little wider than the white inner column (photo)
    d.box(f"slv-{nm}", [x - 35, 60, zc - 33, x + 35, 205, zc + 33], "sleeve", r=4)
    # foot bar along the depth with levelling feet
    d.box(f"foot-{nm}", [x - 28, 18, 40, x + 28, 62, Dp - 40], "white", r=6)
    d.box(f"fp-{nm}", [x - 26, 0, 40, x + 26, 18, 85], "foot", r=4, copies=[[0, 0, Dp - 125]])
# longitudinal bar between the foot bars
d.box("beam", [215, 30, zc - 22, W - 215, 74, zc + 22], "white", r=6)
# hidden cross beam under the top
d.box("ubeam", [215, H - 80, zc - 25, W - 215, H - 40, zc + 25], "white", r=4)
# hand crank on the right end, under the top
xr = W - 215 + 45
d.cyl("crank-shaft", [xr, H - 55, zc + 120], [W - 40, H - 55, zc + 120], 16, "crank")
d.box("crank-arm", [W - 52, H - 160, zc + 112, W - 36, H - 45, zc + 128], "crank", r=6)
d.cyl("crank-grip", [W - 36, H - 150, zc + 120], [W + 0, H - 150, zc + 120], 24, "crank")
d.save()
