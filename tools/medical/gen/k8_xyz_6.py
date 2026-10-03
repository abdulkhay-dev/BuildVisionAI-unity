"""XYZ-6 teal walker with a seat. The user walks at the back (z = 0) holding the grips; the black foam bar across the
top front is the backrest when sitting; small white wheels at the front, black tips at the back."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from k8lib import *

W, DP, H = 600, 350, 930
d = D("xyz-6", [W, DP, H], {"teal": "metal#1aa59a", "teal2": "metal#22b0a4", "foam": "rubber#1d1e20", "grip": "rubber#55595e",
                            "seat": "leather#2e3034", "tyre": "plastic#f2f2f0", "hub": "plastic#9a9ea3", "tip": "rubber#2a2b2d",
                            "col": "plastic#5e6267"})
XS = [30, W - 30]
YS = 500                   # seat rail
YJ = 300                   # telescopic joint
for s, x in (("l", XS[0]), ("r", XS[1])):
    # front leg: up from the wheel, bending back above the seat to the backrest bar
    d.tube(f"front-{s}", [[x, YJ, 318], [x, YS, 314], [x, H - 30, 240]], 25, "teal", bend=60)
    d.cyl(f"flow-{s}", [x, 92, 322], [x, YJ + 30, 318], 22, "teal2")
    # rear leg up to the grip
    d.tube(f"rear-{s}", [[x, YJ, 34], [x, 845, 52], [x, 880, 30]], 25, "teal", bend=40)
    d.cyl(f"rlow-{s}", [x, 40, 30], [x, YJ + 30, 34], 22, "teal2")
    d.cyl(f"tip-{s}", [x, 0, 29], [x, 48, 30], 30, "tip")
    d.cyl(f"grip-{s}", [x, 870, 40], [x, 920, -0], 34, "grip", d2=30)
    for z0, k in ((318, "f"), (34, "r")):
        d.cyl(f"col{k}-{s}", [x, YJ - 15, z0], [x, YJ + 25, z0], 31, "col")
        d.cyl(f"btn{k}-{s}", [x, YJ - 45, z0 - 12], [x, YJ - 45, z0 - 15], 7, "foam", soft=True, repeat={"n": 4, "step": [0, -40, 0]})
    # wheel in a fork
    d.box(f"fork-{s}", [x - 16, 50, 312, x + 16, 100, 340], "col", r=5)
    d.add(f"wheel-{s}", "wheel", "tyre", at=[x, 50, 330], d=100, d2=22, axis="x")
    d.cyl(f"hub-{s}", [x - 13, 50, 330], [x + 13, 50, 330], 34, "hub")
    # seat rail and folding brace under it
    d.cyl(f"rail-{s}", [x, YS, 30], [x, YS, 318], 22, "teal")
    d.cyl(f"brace-{s}", [x, YS - 10, 60], [x, 260, 318], 20, "teal")
    d.box(f"rclamp-{s}", [x - 16, YS - 18, 300, x + 16, YS + 18, 334], "col", r=5)
# backrest bar (black foam) across the top front, front cross bar under the seat
d.cyl("backrest", [XS[0] - 5, H - 30, 240], [XS[1] + 5, H - 30, 240], 44, "foam")
d.cyl("cross", [XS[0], YS - 8, 316], [XS[1], YS - 8, 316], 22, "teal")
# seat: grey board and a black padded cushion between the rails
d.box("seat-board", [XS[0] + 10, YS + 8, 40, XS[1] - 10, YS + 16, 305], "plastic#3a3d42", r=3)
d.box("seat", [XS[0] + 22, YS + 14, 48, XS[1] - 22, YS + 58, 300], "seat", r=14, puff=4)
# small black bag hook under the grip of the +x frame (the photo is taken from the rear, so that frame is the one on
# the image LEFT; the first pass had it on the -x side)
d.tube("hook", [[XS[1] - 14, 880, 30], [XS[1] - 22, 840, 22], [XS[1] - 16, 815, 34], [XS[1] - 10, 835, 46]], 5, "foam",
       bend=10, soft=True)
d.save()
