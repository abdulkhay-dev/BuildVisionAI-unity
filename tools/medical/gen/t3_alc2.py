# ALC-2 far-infrared massage bed with the heat-preservation hood, hood open ~60 deg on two gas struts (table-3)
import math
from t3_alclib import *
W, Dp, Ht = 2050, 750, 650
d = D("alc-2", [W, Dp, 1830], dict(MATS, hood="gloss#f4f5f7", inner="gloss#e6ebf2", pillow="fabric#9fbfe6",
                                   cloth="fabric#7f9fd6"))
body(d, 0, W, Dp, Ht)
# ---- hood: arched shell (half-ellipse ring) extruded along x, end cap with the head cut-out, all turned about the
# hinge line at the bed top (x = HX)
HX, HL, ANG = 180, 1150, 60   # photo: hinges right at the head-end top edge
cz = Dp / 2; a, b, t = 362, 330, 16; y0 = Ht - 8
def arc(a_, b_, rev=False, n=32):
    # superellipse (n=3): straight-ish walls rounding into a flat-ish crown, like the photo's hood
    def se(v): return math.copysign(abs(v) ** (2 / 3), v)
    pts = [(cz + a_ * se(math.cos(math.pi * k / n)), y0 + b_ * se(math.sin(math.pi * k / n))) for k in range(n + 1)]
    return pts[::-1] if rev else pts
def path(pts):
    return "M " + " L ".join(f"{z:.1f} {y:.1f}" for z, y in pts) + " Z"
hr = rot("z", ANG, [HX, y0, cz])
d.slab("hood", "side", path(arc(a, b) + arc(a - t, b - t, rev=True)), [HX, HX + HL - t], "hood", r=5, rot=hr)
d.slab("hood-liner", "side", path(arc(a - t, b - t) + arc(a - t - 4, b - t - 4, rev=True)), [HX + 10, HX + HL - t - 5],
       "inner", rot=hr, soft=True)
nw, nh = 130, 170
cap = arc(a, b) + [(cz - a + 2, y0), (cz - nw, y0)] + \
      [(cz - nw * math.cos(math.pi * k / 10), y0 + nh - nw + nw * math.sin(math.pi * k / 10)) for k in range(11)] + \
      [(cz + nw, y0)]
# photo: the free end is a thick, well-rounded (domed-looking) end wall with the head slot
d.slab("hood-end", "side", path(cap), [HX + HL - 130, HX + HL], "hood", r=60, rot=hr)
d.slab("hood-rim", "side", path([(cz - a, y0), (cz - a + 22, y0), (cz - a + 22, y0 + 16), (cz - a, y0 + 16)]),
       [HX, HX + HL], "hood", r=3, rot=hr, mirror=None)
d.slab("hood-rim2", "side", path([(cz + a - 22, y0), (cz + a, y0), (cz + a, y0 + 16), (cz + a - 22, y0 + 16)]),
       [HX, HX + HL], "hood", r=3, rot=hr)
# hinges at the bed top
d.box("hinge", [HX - 30, y0 - 4, cz - a + 6, HX + 30, y0 + 22, cz - a + 40], "chr", r=4, copies=[[0, 0, 2 * a - 46]])
# ---- gas struts: from the bed top up to the inside of the hood walls
def hood_pt(lx, ly):
    r_ = math.radians(ANG)
    return [HX + lx * math.cos(r_) - ly * math.sin(r_), y0 + lx * math.sin(r_) + ly * math.cos(r_)]
top = hood_pt(560, 60)
for nm, z in (("f", cz + a - 45), ("b", cz - a + 45)):
    base = [HX + 330, y0 + 6, z]
    tp = [top[0], top[1], z]
    mid = [base[0] + (tp[0] - base[0]) * 0.55, base[1] + (tp[1] - base[1]) * 0.55, z]
    d.cyl("strut-" + nm, base, mid, 20, "metal#b9bdc3")
    d.cyl("strut-rod-" + nm, mid, tp, 9, "chr")
    d.box("strut-foot-" + nm, [base[0] - 20, y0 - 2, z - 15, base[0] + 20, y0 + 14, z + 15], "chr", r=3)
# ---- pillow at the head end, a folded blue gown near the hinge
# photo: a flat envelope pillow (thin, pointed corners), tilted a little
d.box("pillow", [1580, Ht, 200, 1940, Ht + 70, 560], "pillow", r=14, puff=28, rot=rot("y", -12, [1760, Ht, 380]))
# photo: a crumpled blue gown spread over the mat from the hinge to the middle (low folds, not a pad)
d.box("gown", [300, Ht, 360, 1080, Ht + 18, 650], "cloth", r=8, puff=6)
d.box("gown-fold", [420, Ht + 10, 420, 640, Ht + 42, 560], "cloth", r=14, puff=10, copies=[[300, -6, 30], [520, -8, -40]])
d.save()
