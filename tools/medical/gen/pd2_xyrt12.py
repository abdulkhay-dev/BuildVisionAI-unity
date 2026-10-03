# XYRT-12 child ladder chair: light wood, ladder back of 7 round rungs, armrests, seat, two floor runners
from pd2_lib import *

W, D, H = 410, 650, 1000
d = Design("xyrt-12", [W, D, H], {"wood": "wood#e6ad4c", "wood2": "wood#d99a3e", "label": "plastic#e9efe9", "seatw": "wood#ecc888"})
RH = 36                                   # runner height
for nm, x0 in (("l", 8), ("r", W - 50)):
    x1 = x0 + 42
    # floor runner with sloped ends
    d.slab(f"runner-{nm}", "side", svg_poly([(0, 0), (650, 0), (612, RH), (42, RH)]), [x0, x1], "wood2", r=4)
    # back upright (to the top) and front leg (to the armrest)
    xa, xb = x0 + 1, x1 - 1
    d.box(f"upright-{nm}", [xa, RH - 2, 95, xb, H, 135], "wood", r=5)
    d.box(f"leg-{nm}", [xa + 1, RH - 2, 572, xb - 1, 418, 610], "wood", r=5)
    # armrest board with a rounded front roll
    AR = rot("x", -4.5, [x0, 391, 128])
    d.box(f"arm-{nm}", [x0 - 4, 380, 128, x1 + 4, 402, 628], "wood", r=6, rot=AR)
    d.cyl(f"arm-roll-{nm}", [x0 - 6, 391, 630], [x1 + 6, 391, 630], 30, "wood", rot=AR)
    # seat side rail
    d.box(f"seat-rail-{nm}", [xa + 6, 168, 135, xb - 6, 212, 572], "wood2", r=3)
# seat board, front and back aprons
wbox(d, "seat", [44, 212, 128, W - 44, 232, 612], "seatw", face="top", r=4)   # light plywood, grain across
wbox(d, "apron-front", [50, 168, 578, W - 50, 212, 600], "wood2", r=3)
wbox(d, "apron-back", [50, 168, 100, W - 50, 212, 122], "wood2", r=3)
# ladder back: 7 round rungs between the uprights
d.cyl("rung", [50, 338, 115], [W - 50, 338, 115], 22, "wood", repeat=rep(7, [0, 105, 0]))
d.box("label", [W / 2 - 14, 962, 126, W / 2 + 14, 974, 128], "label", r=2, soft=True)
d.save()
