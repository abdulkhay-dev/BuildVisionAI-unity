"""XYM-6 mechanical pedal exerciser. The user sits at the +z end; the arch runs along z, the crank axle along x."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from k8lib import *

d = D("xym-6", [410, 510, 410], {"frame": "plastic#efeeea", "black": "rubber#1c1d1f", "pl": "plastic#1f2023",
                                 "hub": "plastic#e4e2dc", "steel": "metal#b9bcc0", "chrome": "chrome"})
CX = 205
YT = 36                     # foot tube centre
ZF, ZB = 466, 44            # front / back foot tubes
# foot tubes across x, black triangular rubber feet at the ends
for k, z in (("f", ZF), ("b", ZB)):
    d.cyl(f"foot-{k}", [40, YT, z], [370, YT, z], 25, "frame")
    tri = f"M {z - 40} 0 L {z + 40} 0 L {z + 7} 54 L {z - 7} 54 Z"
    d.slab(f"wedge-{k}", "side", tri, [4, 46], "black", r=7)
    d.slab(f"wedge-{k}r", "side", tri, [364, 406], "black", r=7)
# arch along z
d.tube("arch", [[CX, YT, ZB], [CX, 192, ZB + 72], [CX, 192, ZF - 72], [CX, YT, ZF]], 25, "frame", bend=55)
d.box("clamp-b", [CX - 17, YT - 16, ZB - 18, CX + 17, YT + 16, ZB + 18], "steel", r=4)
d.box("clamp-f", [CX - 17, YT - 16, ZF - 18, CX + 17, YT + 16, ZF + 18], "steel", r=4)
d.cyl("bolt-f", [CX - 22, YT, ZF], [CX + 22, YT, ZF], 8, "chrome")
# hub housing on a saddle clamp
HY, HZ = 262, 255
d.box("saddle", [CX - 26, 183, HZ - 45, CX + 26, 210, HZ + 45], "steel", r=5)
d.box("saddle-post", [CX - 14, 206, HZ - 14, CX + 14, HY - 50, HZ + 14], "steel", r=3)
d.cyl("hub", [CX - 28, HY, HZ], [CX + 28, HY, HZ], 150, "hub", sides=40)
d.cyl("hub-rim", [CX - 30, HY, HZ], [CX + 30, HY, HZ], 142, "steel", sides=40)
d.cyl("hub-boss", [CX - 46, HY, HZ], [CX + 46, HY, HZ], 30, "chrome")
for sx in (-1, 1):
    d.cyl(f"screw{sx}", [CX + sx * 28, HY + 45, HZ - 25], [CX + sx * 31, HY + 45, HZ - 25], 9, "steel")
    d.cyl(f"screw2{sx}", [CX + sx * 28, HY - 40, HZ + 35], [CX + sx * 31, HY - 40, HZ + 35], 9, "steel")
d.decal("label", [CX - 30.6, HY + 20, HZ + 30], [30, 8], "left", "plastic#3a3d42")
# tension knob on top, a little to the back
d.cyl("knob-stem", [CX, HY + 70, HZ - 25], [CX, HY + 98, HZ - 25], 14, "chrome")
d.box("knob", [CX - 30, HY + 96, HZ - 37, CX + 30, HY + 118, HZ - 13], "pl", r=9)
# cranks: square silver bars, 180 deg apart, the upper one leans 20 deg to the front
L = 155
a = math.radians(28)
up = [HY + L * math.cos(a), HZ + L * math.sin(a)]
lo = [HY - L * math.cos(a), HZ - L * math.sin(a)]
XL, XR = CX - 58, CX + 58
d.bar("crank-l", [XL, HY, HZ], [XL, lo[0], lo[1]], [20, 15], "steel", r=3)
d.bar("crank-r", [XR, HY, HZ], [XR, up[0], up[1]], [20, 15], "steel", r=3)
d.cyl("crank-cap-l", [XL - 10, HY, HZ], [XL + 12, HY, HZ], 26, "chrome")
d.cyl("crank-cap-r", [XR - 12, HY, HZ], [XR + 10, HY, HZ], 26, "chrome")


def pedal(k, x_in, y, z, sgn):
    """pedal plate from the crank at x_in outward (sgn -1 = to -x), centre (y, z)"""
    x0, x1 = sorted([x_in + sgn * 12, x_in + sgn * 110])
    d.box(f"pblk-{k}", [x_in - 15, y - 22, z - 18, x_in + 15, y + 22, z + 18], "pl", r=4)
    d.box(f"pedal-{k}", [x0, y - 9, z - 78, x1, y + 9, z + 78], "pl", r=6)
    d.box(f"ptread-{k}", [x0 + 8, y + 8, z - 68, x1 - 8, y + 11, z + 68], "rubber#2a2c2f", r=3)
    xo = x1 if sgn > 0 else x0
    # heel cup (photo): a black wall hanging under the outer edge, an open oval slot through it, a lip curling inward
    # at the bottom, the wall ~2/3 of the plate length
    outer = (f"M {z - 52} {y - 4} L {z + 56} {y - 4} Q {z + 52} {y - 40} {z + 34} {y - 70} Q {z + 18} {y - 98} {z - 12} {y - 100} "
             f"L {z - 34} {y - 100} Q {z - 50} {y - 98} {z - 50} {y - 80} Z")
    hole = " ".join(("M" if i == 0 else "L") + f" {z + 6 + 13 * math.cos(t) * math.cos(0.45) - 30 * math.sin(t) * math.sin(0.45):.1f}"
                    f" {y - 50 + 13 * math.cos(t) * math.sin(0.45) + 30 * math.sin(t) * math.cos(0.45):.1f}"
                    for i, t in enumerate([2 * math.pi * k / 16 for k in range(16)])) + " Z"
    w = [xo - 8, xo] if sgn > 0 else [xo, xo + 8]
    d.slab(f"cup-{k}", "side", outer + " " + hole, w, "pl", r=2.5)
    xi = xo - sgn * 40
    d.box(f"lip-{k}", [min(xo, xi), y - 102, z - 46, max(xo, xi), y - 90, z - 2], "pl", r=5)
    d.box(f"cupfold-{k}", [min(xo, xo - sgn * 14), y - 12, z - 52, max(xo, xo - sgn * 14), y, z + 56], "pl", r=5)


pedal("l", XL, lo[0], lo[1], -1)
pedal("r", XR, up[0], up[1], 1)
d.save()
