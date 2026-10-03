"""XYX-1 seated lower-limb exerciser: a white front column on a T foot with a black horizontal U handlebar, a long
floor beam back to a blue seat box with a light-blue seat and backrest, a swing lever and a diagonal brace carrying
two black footplates in front of the seat. Front (z = depth) = the column the seated user faces."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from k8lib import *

W, DP, H = 580, 1600, 1400
d = D("xyx-1", [W, DP, H], {"frame": "plastic#efefeb", "black": "plastic#1b1c1e", "foam": "rubber#1d1e20", "grey": "metal#a5a9ae",
                            "box": "plastic#2f6fc8", "pu": "leather#8fb8e0", "pedal": "rubber#222326"})
CX = W / 2
ZC = 1490                      # column centre
# T foot, column
d.box("tfoot", [0, 20, ZC - 30, W, 75, ZC + 30], "frame", r=4)
d.box("tfeet", [0, 0, ZC - 30, 60, 22, ZC + 30], "black", r=4, copies=[[W - 60, 0, 0]])
d.box("column", [CX - 30, 75, ZC - 30, CX + 30, 1300, ZC + 30], "frame", r=4)
d.box("col-cap", [CX - 34, 1290, ZC - 34, CX + 34, 1330, ZC + 34], "black", r=6)
star_knob(d, "top-knob", [CX, 1330, ZC], "y", 1, "black", dd=50, l=40)
d.lathe("side-knob", [CX + 30, 1100, ZC], [[0, 0], [10, 0], [10, 18], [36, 22], [36, 52], [30, 58], [0, 58]], "black", axis="x")
# black U handlebar, horns pointing back toward the seat
hb = [[CX - 215, 1355, ZC - 230], [CX - 250, 1345, ZC - 60], [CX - 140, 1335, ZC + 30], [CX + 140, 1335, ZC + 30],
      [CX + 250, 1345, ZC - 60], [CX + 215, 1355, ZC - 230]]
d.tube("handlebar", hb, 38, "foam", bend=110)
d.box("hb-clamp", [CX - 45, 1310, ZC - 10, CX + 45, 1345, ZC + 40], "black", r=8)
# photo linkage: a level floor beam from the T foot back into a notch at the bottom of the seat box; a diagonal brace
# from the column (~620) down to the beam; an arm back from the column at ~880 to a pivot; the swing lever hanging
# from it to a lower pivot; from there the footplate bar runs back (slightly down) into the box above the beam,
# the two black footplates side by side on it.
d.bar("beam", [CX, 45, ZC - 30], [CX, 45, 330], [60, 50], "frame", r=4)
BZ = 1010
d.bar("brace", [CX, 620, ZC - 30], [CX, 70, BZ], [50, 40], "frame", r=4)
d.cyl("brace-hub", [CX - 34, 78, BZ - 12], [CX + 34, 78, BZ - 12], 26, "grey", copies=[[0, 0, 34]])
PZ = 1265
d.box("pivot-plate", [CX - 25, 860, PZ - 20, CX + 25, 905, ZC - 30], "frame", r=4)
d.cyl("pivot", [CX - 40, 880, PZ], [CX + 40, 880, PZ], 30, "grey")
LY = 340
d.bar("lever", [CX, 880, PZ], [CX, LY, PZ - 25], [46, 30], "frame", r=4)
d.cyl("lever-hub", [CX - 34, LY, PZ - 25], [CX + 34, LY, PZ - 25], 28, "grey")
FB0, FB1 = [CX, LY, PZ - 25], [CX, 250, 360]          # footplate bar into the box
d.bar("fbar", FB0, FB1, [44, 36], "frame", r=4)
fy = lambda z: FB0[1] + (FB1[1] - FB0[1]) * (FB0[2] - z) / (FB0[2] - FB1[2])
FZ0, FZ1 = 600, 880
d.box("carriage", [CX - 45, fy(FZ0 + 60) + 10, FZ0 + 60, CX + 45, fy(FZ1 - 60) + 40, FZ1 - 60], "frame", r=6)
d.cyl("carriage-x", [CX - 165, fy(740) + 45, 740], [CX + 165, fy(740) + 45, 740], 24, "grey")
for k, x in (("l", CX - 88), ("r", CX + 88)):
    yb = fy(740) + 62
    d.bar(f"plate-{k}", [x, yb - 22, FZ0], [x, yb + 32, FZ1], [150, 28], "pedal", r=10)
    d.bar(f"heel-{k}", [x, yb - 22, FZ0], [x, yb + 26, FZ0 - 12], [150, 18], "pedal", r=6)
    d.box(f"pbr-{k}", [x - 12, yb - 30, 700, x + 12, yb, 780], "grey", r=3)
    star_knob(d, f"pknob-{k}", [x + (-1 if k == "l" else 1) * 75, yb - 12, 700], "x", -1 if k == "l" else 1, "black", dd=26, l=20)
# seat box: blue, rounded top-front, an opening for the beam
# photo: the rounded edge is the top-REAR one; the beam and footplate bar go into a tall dark slot low in the front
# face, seen from the side as an arched opening at the front-bottom
box = "M 0 0 L 420 0 L 420 450 L 130 450 Q 0 450 0 320 Z"
d.slab("seatbox", "side", box, [90, 490], "box", r=14)
d.decal("opening", [CX, 190, 420.6], [110, 300], "front", "plastic#1d2a44")
arch = "M 345 14 L 345 260 Q 345 300 375 300 Q 405 300 405 260 L 405 14 Z"
d.slab("arch-r", "side", arch, [489, 491.5], "plastic#1d2a44", soft=True)
d.slab("arch-l", "side", arch, [88.5, 91], "plastic#1d2a44", soft=True)
d.box("base", [80, 0, 10, 500, 12, 410], "frame", r=3)
# slide frame, seat, backrest, struts, handles
d.box("slide", [110, 450, 50, 470, 478, 390], "frame", r=5)
d.box("slide-rail", [130, 476, 60, 450, 484, 380], "metal#c6c9cd", r=3)
star_knob(d, "slide-knob", [470, 462, 300], "x", 1, "black", dd=36, l=28)
d.box("seat", [115, 482, 60, 465, 550, 410], "pu", r=40, puff=8)
d.box("seat-base", [130, 478, 70, 450, 488, 395], "plastic#3a3d42", r=6)
BP = [CX, 640, 70]
d.box("back", [150, 650, 30, 430, 1010, 92], "pu", r=36, puff=6, rot=rot("x", -12, BP))
for x in (175, 405):
    d.tube(f"strut{x}", [[x, 480, 80], [x, 560, 70], [x, 760, 25]], 22, "frame", bend=40)
d.cyl("handle-l", [140, 835, 40], [140, 835, 400], 32, "black")
d.cyl("handle-l-st", [150, 835, 40], [175, 835, 40], 24, "frame")
d.tube("handle-r", [[405, 790, 40], [455, 790, 60], [460, 740, 260]], 32, "black", bend=40)
d.save()
