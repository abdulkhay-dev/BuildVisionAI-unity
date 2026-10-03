"""XYQL-1 multifunctional standing frame: a white cabinet column across the back, a plywood tray with a grey padded
top and a front cut-out, grey knee and shin pads with side arms on the column front, black knobs and grips, a plywood
floor plate in a white aluminium edge, small castors at the back. The patient stands on the plate facing the column."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from k8lib import *

W, DP, H = 740, 770, 1250
d = D("xyql-1", [W, DP, H], {"shell": "plastic#f3f3f1", "rail": "plastic#e9e9e6", "pad": "leather#86898d", "ply": "plastic#c99c69",
                             "black": "plastic#1b1c1e", "grey": "metal#a7abb0", "edge": "metal#e6e7e8"})
# Layout read on the photo (front-left view, so parts further forward appear further right; corrected for that):
# the cabinet is ~430 wide and ~200 deep; the floor plate (~400 wide) starts ~75 in from the cabinet's left side and
# runs a little past its right side; the knee/shin pads sit over the plate; the tray does not overhang on the left
# at the back and runs ~270 past the cabinet on the right, the raised grey pad on its right part.
X0, X1, ZC = 40, 470, 200      # cabinet
PC = 300                       # centre of the plate / pads (the user's place)
YT = 1180                      # cabinet top
d.box("cabinet", [X0, 30, 0, X1, YT, ZC], "shell", r=10)
d.box("plinth", [X0 + 5, 0, 5, X1 - 5, 32, ZC - 5], "shell", r=4)
# front face: two raised rails with dark slots, a recessed centre panel, a gas spring
for k, x in (("l", X0 + 38), ("r", X1 - 38)):
    d.box(f"rail-{k}", [x - 32, 220, ZC - 2, x + 32, YT - 20, ZC + 12], "rail", r=5)
    d.decal(f"slot-{k}", [x, 680, ZC + 12.6], [9, 860], "front", "plastic#6f7378")
d.decal("panel", [(X0 + X1) / 2, 690, ZC + 0.6], [280, 900], "front", "plastic#e7e7e4")
d.cyl("spring", [PC, YT - 10, ZC + 14], [PC, 790, ZC + 14], 12, "black")
d.cyl("spring-rod", [PC, 790, ZC + 14], [PC, 640, ZC + 14], 7, "grey")
for y in (1110, 750, 490, 250):
    star_knob(d, f"knob-l{y}", [X0 + 38, y, ZC + 12], "z", 1, "black", dd=36, l=30)
star_knob(d, "knob-r", [X1 - 38, 860, ZC + 12], "z", 1, "black", dd=36, l=30)
# black grips: left one across the left rail, right one sticking out at the right under the tray
d.box("grip-l-st", [X0 + 18, 990, ZC + 10, X0 + 58, 1030, ZC + 30], "rail", r=4)
d.cyl("grip-l", [X0 - 15, 1010, ZC + 38], [X0 + 110, 1010, ZC + 38], 32, "black")
d.box("grip-r-st", [X1 - 10, 1090, ZC - 40, X1 + 25, 1130, ZC - 10], "rail", r=4)
d.cyl("grip-r", [X1 + 10, 1110, ZC - 25], [X1 + 100, 1110, ZC - 25], 32, "black")
# tray: plywood with a grey pad, concave cut-out at the front over the plate, raised pad on the right part
TX0, TX1, TD = 70, 740, 560
tray = (f"M {TX0 + 110} 0 L {TX1 - 20} 0 Q {TX1} 0 {TX1} 20 L {TX1} {TD - 20} Q {TX1} {TD} {TX1 - 20} {TD} "
        f"L {PC + 205} {TD} Q {PC + 200} 405 {PC} 405 Q {PC - 200} 405 {PC - 205} {TD} "
        f"L {TX0 + 20} {TD} Q {TX0} {TD} {TX0} {TD - 20} L {TX0} 110 Q {TX0} 0 {TX0 + 110} 0 Z")
d.slab("tray", "top", tray, [YT, YT + 18], "ply", r=3)
tray2 = (f"M {TX0 + 112} 10 L {TX1 - 30} 10 Q {TX1 - 10} 10 {TX1 - 10} 30 L {TX1 - 10} {TD - 30} Q {TX1 - 10} {TD - 12} {TX1 - 28} {TD - 12} "
         f"L {PC + 218} {TD - 12} Q {PC + 210} 392 {PC} 392 Q {PC - 210} 392 {PC - 218} {TD - 12} "
         f"L {TX0 + 28} {TD - 12} Q {TX0 + 10} {TD - 12} {TX0 + 10} {TD - 30} L {TX0 + 10} 112 Q {TX0 + 10} 10 {TX0 + 112} 10 Z")
d.slab("tray-pad", "top", tray2, [YT + 17, YT + 45], "pad", r=10)
chest = f"M {PC + 190} 22 L {TX1 - 32} 22 Q {TX1 - 22} 22 {TX1 - 22} 40 L {TX1 - 22} {TD - 40} Q {TX1 - 22} {TD - 24} {TX1 - 40} {TD - 24} L {PC + 250} {TD - 24} Q {PC + 150} 300 {PC + 190} 22 Z"
d.slab("chest", "top", chest, [YT + 40, H], "pad", r=12)
# knee and shin pads on a grey carriage over the plate, side arms (left lower, right higher)
d.box("carriage", [PC - 140, 300, ZC, PC + 140, 760, ZC + 10], "grey", r=4)
d.box("knee", [PC - 170, 430, ZC + 8, PC + 170, 750, ZC + 80], "pad", r=26, puff=6)
d.box("shin", [PC - 165, 225, ZC + 40, PC + 165, 440, ZC + 105], "pad", r=22, puff=5)
d.box("shin-st", [PC - 60, 260, ZC + 8, PC + 60, 400, ZC + 42], "grey", r=4)
for k, x0, x1, y0 in (("l", PC - 232, PC - 170, 420), ("r", PC + 170, PC + 232, 545)):
    d.box(f"arm-{k}", [x0, y0, ZC + 20, x1, y0 + 58, ZC + 300], "pad", r=18, puff=2)
    d.box(f"arm-sup-{k}", [x0 + 16, y0 - 14, ZC, x1 - 16, y0, ZC + 270], "rail", r=3)
    d.box(f"arm-cap-{k}", [x0 + 18, y0 - 16, ZC + 270, x1 - 18, y0 + 10, ZC + 292], "black", r=3)
# floor plate: plywood with white aluminium side rails (black end caps at the front)
PX0, PX1 = PC - 205, PC + 215
d.box("plate-base", [PX0, 0, ZC - 5, PX1, 30, DP - 4], "edge", r=3)
d.box("plate", [PX0 + 8, 28, ZC, PX1 - 8, 40, DP - 6], "ply", r=2)
d.box("plate-rail", [PX0, 0, ZC - 5, PX0 + 10, 44, DP], "edge", r=2, copies=[[PX1 - PX0 - 10, 0, 0]])
d.box("plate-cap", [PX0 - 1, 0, DP - 14, PX0 + 11, 45, DP], "black", r=2, copies=[[PX1 - PX0 - 10, 0, 0]])
# castors at the back corners on white brackets
for k, x in (("l", X0 - 12), ("r", X1 + 12)):
    d.box(f"cbr-{k}", [x - 28, 62, 15, x + 28, 82, 85], "shell", r=5)
    caster(d, f"cas-{k}", [x, 0, 50], 62, "plastic#9a9ea3")
d.save()
