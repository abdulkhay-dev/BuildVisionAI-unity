# XY-81 PT stool: black saddle seat, chrome gas lift, chrome 5-star base, black twin castors - table-3 batch
import math
from lib import *
d = D("xy-81", [450, 450, 580], {
  "seat": "leather#1d1f22", "blk": "plastic#202226", "chr": "chrome", "caster": "plastic#1a1b1e"})
C = 225
# saddle seat: loft along x, middle a bit lower and thinner, ends rounded (kidney-ish plan)
secs = []
for i in range(15):
    t = i / 14; x = 10 + 430 * t
    e = abs(2 * t - 1)                      # 0 in the middle, 1 at the ends
    end_ = max(0.0, (e - 0.75) / 0.25)       # rounding of the two ends
    w = 350 - 110 * end_ ** 2; dd = 92 - 34 * end_ ** 2
    dip = 16 * (1 - e ** 2)                   # the middle is a bit lower (saddle)
    secs.append(sec(x, w, dd, min(44, dd / 2 - 1), 526 - dip, 224))
d.loft("seat", secs, "seat", axis="x", dome="both", domeH=14)
d.box("seat-plate", [140, 470, 150, 310, 488, 300], "blk", r=8)
# height lever (black paddle under the left of the seat)
d.box("lever", [70, 448, 250, 150, 458, 290], "blk", r=5, rot=rot("z", -12, [150, 453, 270]))
d.cyl("lever-rod", [150, 456, 270], [190, 470, 270], 10, "blk")
# gas column: thin chrome piston in a thick chrome sleeve with a black collar
# photo: the black collar sits at ~360 mm, the thick chrome sleeve runs from the hub up to it
d.cyl("piston", [C, 350, C], [C, 472, C], 28, "chr")
d.cyl("collar", [C, 338, C], [C, 362, C], 54, "blk")
d.cyl("sleeve", [C, 130, C], [C, 340, C], 52, "chr")
d.lathe("hub", [C, 92, C], [[0, 0], [52, 0], [55, 10], [52, 40], [36, 52], [0, 52]], "blk")
# five flat chrome arms with black end caps over the castors
R = 200
for k in range(5):
    a = math.radians(90 + 72 * k)   # first arm points to the front (+z)
    ex, ez = C + R * math.cos(a), C + R * math.sin(a)
    sx, sz = C + 40 * math.cos(a), C + 40 * math.sin(a)
    d.bar(f"arm{k}", [sx, 118, sz], [ex, 104, ez], [42, 22], "chr", r=4)
    d.box(f"cap{k}", [ex - 23, 86, ez - 23, ex + 23, 122, ez + 23], "blk", r=8,
          rot=rot("y", -math.degrees(a) + 90, [ex, 100, ez]))
    # black twin-wheel castor (photo): stem, a hood between two Ø50 wheels, trailing behind the stem
    cx, cz = ex + 6 * math.cos(a), ez + 6 * math.sin(a)
    d.cyl(f"cstem{k}", [ex, 62, ez], [ex, 88, ez], 16, "caster")
    d.box(f"chood{k}", [cx - 8, 22, cz - 30, cx + 8, 66, cz + 14], "caster", r=7)
    d.add(f"cwheel{k}", "wheel", "caster", at=[cx - 17, 25, cz - 12], d=50, d2=17, axis="x", copies=[[34, 0, 0]])
d.save()
