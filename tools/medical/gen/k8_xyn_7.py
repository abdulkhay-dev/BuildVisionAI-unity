"""XYN-7 over-door pulley: a flat brass rod triangle bracket (hooks over the door at the right), a green pulley under
its apex, two tan cords down to two brass D-stirrups with wooden grips. Everything in the x-y plane (D = 30)."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from k8lib import *

# proportions measured on the photo (1.45 mm/px over the full 1160 height): bracket 330 wide, apex 116 below the
# top, pulley Ø60 centred 200 below the top, stirrups ~95 × 116. The drawn parts span 380 across x (printed 430).
W, DP, H = 380, 30, 1160
d = D("xyn-7", [W, DP, H], {"brass": "metal#c9a957", "green": "gloss#38a888", "cord": "fabric#c9b58c",
                            "grip": "gloss#e0a33a"})
Z = 15
AX, AY = 50, 1044
XB = W - 7
d.tube("rod-up", [[AX, AY, Z], [XB - 4, H - 8, Z]], 7, "brass")
d.tube("rod-lo", [[AX, AY, Z], [XB - 3, 1022, Z]], 7, "brass")
d.tube("rod-v", [[XB - 4, 1004, 3], [XB - 3, 1012, Z], [XB - 3, H - 6, Z], [XB + 3, H - 2, 3]], 7, "brass", bend=6)
d.sphere("foot", [XB - 4, 1003, 4], 11, "plastic#2a2b2d")
d.sphere("apex", [AX, AY, Z], 12, "brass")
# pulley in a small yoke under the apex
PY = 958
d.cyl("link", [AX, AY, Z], [AX, PY + 34, Z], 5, "brass")
d.box("yoke", [AX - 6, PY - 4, Z - 14, AX + 6, PY + 38, Z - 11], "brass", r=1, copies=[[0, 0, 25]])
d.add("pulley", "wheel", "green", at=[AX, PY, Z], d=60, d2=18, axis="z")
d.cyl("axle", [AX, PY, Z - 15], [AX, PY, Z + 15], 8, "brass")
# two cords to two D-stirrups (front one at the left and lower, the back one right of it)
st = [(47, 8, 0), (88, 22, 14)]          # stirrup centre x, z, lift
for k, (sx, sz, lift) in enumerate(st):
    cx = AX - 29 if k == 0 else AX + 29
    top = [sx, 116 + lift, sz]
    d.cyl(f"cord{k}", [cx, PY, Z], [sx, top[1] + 8, sz], 4, "cord", soft=True)
    d.sphere(f"knot{k}", [sx, top[1] + 8, sz], 10, "brass")
    # D-stirrup: brass rod, straight sides, round top, a wooden grip across the bottom
    path = [[sx - 44, 14 + lift, sz], [sx - 44, 58 + lift, sz]] + \
           [[sx - 44 * math.cos(math.pi * t / 10), 58 + lift + 58 * math.sin(math.pi * t / 10), sz] for t in range(1, 10)] + \
           [[sx + 44, 58 + lift, sz], [sx + 44, 14 + lift, sz]]
    d.tube(f"stirrup{k}", path, 6, "brass")
    d.lathe(f"grip{k}", [sx - 46, 15 + lift, sz], [[0, 0], [14, 0], [15, 6], [15, 86], [14, 92], [0, 92]], "grip", axis="x")
d.save()
