# XY-83 overbed table: wood top (round right end) on a white telescopic column with a brace, H base - table-3 batch
import math
from lib import *
d = D("xy-83", [850, 450, 1000], {
  "wood": "wood#a8642f", "ply": "wood#dcc39a", "frame": "plastic#f2f3f4", "blk": "plastic#1d1f22",
  "cast": "plastic#8d939b"})
W, Dp, H = 850, 450, 1000
zc = Dp / 2
# top: left end square, right end round (big corner radii), 20 thick plywood with a brown veneer
def top_outline(x0, z0, x1, z1, r):
    return (f"M {x0} {z0} L {x1 - r} {z0} A {r} {r} 0 0 1 {x1} {z0 + r} L {x1} {z1 - r} "
            f"A {r} {r} 0 0 1 {x1 - r} {z1} L {x0} {z1} Z")
d.slab("top", "top", top_outline(0, 0, W, Dp, 170), [H - 22, H - 4], "ply", r=2)
d.slab("veneer", "top", top_outline(0, 0, W, Dp, 170), [H - 4, H], "wood", r=1.5)
# black rubber stops / brackets under the top ends
d.box("stop", [40, H - 34, 30, 80, H - 22, 60], "blk", r=3, copies=[[0, 0, 360], [700, 0, 0], [700, 0, 360]])
# support channel under the top along x and bracket
d.bar("rail", [60, H - 37, zc], [760, H - 37, zc], [40, 30], "frame", r=4)
d.box("bracket", [120, H - 90, zc - 35, 190, H - 22, zc + 35], "frame", r=5)
d.cyl("bracket-knob", [120, H - 60, zc], [95, H - 60, zc], 14, "blk")
d.cyl("bracket-knob2", [95, H - 60, zc], [85, H - 60, zc], 26, "blk")
# telescopic column: lower 50 sq tube, upper 40 sq tube, height lock knob on the left
X = 155
d.bar("col-low", [X, 90, zc], [X, 690, zc], [50, 50], "frame", r=5)
d.bar("col-up", [X, 680, zc], [X, H - 90, zc], [40, 40], "frame", r=4)
d.box("col-cap", [X - 27, 682, zc - 27, X + 27, 696, zc + 27], "blk", r=3)
d.cyl("knob-stem", [X - 25, 860, zc], [X - 45, 860, zc], 10, "blk")
d.cyl("knob", [X - 45, 860, zc], [X - 70, 860, zc], 34, "blk")
# diagonal flat brace from the column to the long base bar
d.bar("brace", [X + 25, 690, zc], [470, 110, zc], [40, 20], "frame", r=3)
d.cyl("brace-bolt", [X + 32, 685, zc - 14], [X + 32, 685, zc + 14], 14, "blk")
# H base: two crossbars along the depth, the long bar along x
d.bar("cross", [X, 75, 0], [X, 75, Dp], [50, 40], "frame", r=4, copies=[[640, 0, 0]])
d.bar("long", [X, 75, zc], [795, 75, zc], [50, 40], "frame", r=4)
d.box("endcap", [X - 25, 55, -2, X + 25, 95, 8], "blk", r=3, copies=[[0, 0, Dp - 6], [640, 0, 0], [640, 0, Dp - 6]])
d.add("castor", "caster", "cast", at=[X, 0, 35], d=50, copies=[[0, 0, Dp - 70], [640, 0, 0], [640, 0, Dp - 70]])
d.save()
