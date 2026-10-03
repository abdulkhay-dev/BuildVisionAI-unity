"""XYYL-1 dumbbell rack: white H base on 4 castors, two bent white A-frames (z = 210 / 290) on the cross tube,
2 x 9 vinyl dumbbells (axis along z) on cradle arms outside the legs, small at the top, big at the bottom."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from k8lib import *

W, DP, H = 570, 500, 1100
d = D("xyyl-1", [W, DP, H], {"frame": "plastic#f1f1ee", "teal": "gloss#2aa79b", "blue": "gloss#2266c4", "red": "gloss#d42a2a",
                             "black": "rubber#1c1d1f", "grey": "plastic#8d9196"})
CX = W / 2
YB0, YB1 = 92, 132          # base tube bottom / top
# base: two tubes along z with castors, a cross tube along x
for x in (45, W - 45):
    d.box(f"base{x}", [x - 25, YB0, 12, x + 25, YB1, DP - 12], "frame", r=4)
    d.box(f"cap{x}", [x - 25, YB0, 8, x + 25, YB1, 14], "black", r=3, copies=[[0, 0, DP - 22]])
    for z in (45, DP - 45):
        d.box(f"plate{x}-{z}", [x - 28, YB0 - 6, z - 28, x + 28, YB0, z + 28], "grey", r=3)
        caster(d, f"cas{x}-{z}", [x, 0, z], 75, "black")
d.box("cross", [70, YB0, 225, W - 70, YB1, 275], "frame", r=4)
for x in (45, W - 45):
    d.box(f"brake{x}", [x - 12, 34, DP - 30, x + 12, 44, DP - 2], "grey", r=3)
# A-frames: bent square tubes with a rounded top
XB, XT, YT = 165, 50, H - 15   # photo: the legs land near the ends of the cross tube     # half spread at the bottom / near the top
for k, z in (("f", 290), ("b", 210)):
    d.sweep(f"A-{k}", [[CX - XB, YB1, z], [CX - XT, YT - 30, z], [CX, YT, z], [CX + XT, YT - 30, z], [CX + XB, YB1, z]],
            [30, 30], "frame", shape="rect", r=5, bend=70)
    d.box(f"Afoot-{k}", [CX - XB - 22, YB1, z - 22, CX - XB + 22, YB1 + 10, z + 22], "frame", r=3, copies=[[2 * XB, 0, 0]])


def leg_x(y, side):
    t = (y - YB1) / (YT - 30 - YB1)
    return CX + side * (XB + (XT - XB) * t)


cols = {-1: ["teal", "teal", "blue", "red", "blue", "blue", "red", "teal", "blue"],
        1: ["teal", "teal", "blue", "red", "blue", "red", "red", "teal", "blue"]}
heads = [50, 54, 58, 64, 70, 76, 82, 88, 94]
y = H - 125
ys = []
for i in range(9):
    ys.append(y)
    y -= heads[i] * 0.5 + (heads[i + 1] if i < 8 else 90) * 0.5 + 12
for side, names in cols.items():
    for i, (yy, hd, m) in enumerate(zip(ys, heads, names)):
        x = leg_x(yy, side) + side * (hd / 2 + 20)
        L = 165 + i * 12
        dumbbell_round(d, f"db{side}-{i}", [x, yy, 250 - L / 2], L, hd, "z", m, hl=hd * 0.58)
        # cradle arms from both A-frame legs (white), a small lip outside
        ya = yy - hd * 0.21 - 4
        xl = leg_x(yy, side)
        x0, x1 = sorted([xl, x + side * hd * 0.3])
        d.box(f"arm{side}-{i}", [x0, ya - 10, 200, x1, ya, 220], "frame", r=2, copies=[[0, 0, 80]])
        xo = x + side * hd * 0.3
        d.box(f"lip{side}-{i}", [xo - 5, ya - 10, 200, xo + 5, ya + 16, 220], "frame", r=2, copies=[[0, 0, 80]])
d.decal("label", [70, (YB0 + YB1) / 2, DP - 11.4], [36, 10], "front", "gloss#3a68b8")
d.save()
