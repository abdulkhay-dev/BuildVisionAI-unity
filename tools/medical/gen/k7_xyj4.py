"""xyj-4 Forearm Rotation Exerciser (wall). Photo front, 1.73 mm/px. Printed 48~70×40×98: the photo's front view is
only ~230 wide (same plates as XYJ-1/2/5), so W = 240; 480 is taken as the forearm rest's reach from the wall (D)."""
from k7lib import *

d = D("xyj-4", [240, 480, 980], {
    "teal": "plastic#1aa3a3", "tealdk": "plastic#117575", "chrome": "chrome", "black": "plastic#1b1d1f",
    "pad": "leather#7c6079"})
CX = 120
rail_unit(d, CX, 980, 0, (164, 450), None, plate_w=200, plate_h=(55, 55), rail_gap=141)
# --- dial on the carriage front: black ring with a hollow centre, black vertical handle hanging from its centre
DX, DY = 120, 330
ring = (f"M {DX - 56} {DY} A 56 56 0 1 0 {DX + 56} {DY} A 56 56 0 1 0 {DX - 56} {DY} Z "
        f"M {DX - 24} {DY} A 24 24 0 1 1 {DX + 24} {DY} A 24 24 0 1 1 {DX - 24} {DY} Z")
d.slab("dial-ring", "front", ring, [122, 146], "black", r=5)
d.cyl("dial-hub", [DX, DY, 122], [DX, DY, 150], 26, "chrome")
d.cyl("dial-spoke", [DX, DY, 146], [DX, DY, 160], 34, "black")
d.cyl("handle", [DX, DY - 6, 160], [DX + 2, 214, 182], 30, "black")
d.sphere("handle-end", [DX + 2, 214, 182], 30, "black")
d.strap("hand-strap", [[DX + 10, DY + 40, 148], [DX + 12, DY - 20, 176], [DX + 12, 222, 196]], [12, 3], "teal", bend=30)
# --- forearm rest (photo: its top rim at the carriage's bottom edge, the dial and the whole handle above it):
# grey-mauve U trough seen end-on, on a teal stem through a clamp on a teal reach arm low under the carriage
d.box("arm-bracket", [100, 60, 20, 140, 168, 70], "teal", r=4)
d.bar("reach-arm", [120, 76, 40], [120, 76, 400], [28, 28], "teal", r=3)
d.box("clamp", [96, 58, 300, 144, 96, 350], "teal", r=4)
d.lathe("clamp-knob", [144, 98, 325], [[0, 0], [9, 0], [9, 10], [18, 12], [18, 26], [0, 28]], "black", axis="x")
d.cyl("stem", [112, 40, 325], [112, 118, 325], 26, "teal")
d.cyl("stem-foot", [112, 30, 325], [112, 48, 325], 30, "black")
d.box("pad-plate", [50, 112, 190, 190, 122, 460], "tealdk", r=3)
U = "M 6 202 Q 120 146 234 202 L 226 156 Q 120 86 14 156 Z"
d.slab("saddle", "front", U, [184, 468], "pad", r=14)
d.save()
