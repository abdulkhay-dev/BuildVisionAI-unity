"""XYN-6 elastic fingers exerciser: light-blue PU board on a low white tube frame, a white tube back frame strung
with an orange elastic grid (15 verticals in 7 top loops + 1, 12 horizontals tied to the uprights)."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from k8lib import *

W, DP, H = 610, 420, 500
d = D("xyn-6", [W, DP, H], {"frame": "plastic#f1f1ee", "pad": "leather#8fb8e0", "tip": "rubber#1c1d1f",
                            "cord": "plastic#f0a02a", "tie": "plastic#d9481e"})
YR = 100         # rim tube centre
ZF = 30          # back frame plane
XL, XR = 30, W - 30
# legs, tips, side stretchers
for x in (XL, XR):
    for z in (ZF, DP - 45):
        d.cyl(f"leg{x}-{z}", [x, 18, z], [x, YR, z], 25, "frame")
        d.cyl(f"tip{x}-{z}", [x, 0, z], [x, 22, z], 30, "tip")
    d.cyl(f"str{x}", [x, 40, ZF], [x, 40, DP - 45], 22, "frame")
# rim under the board edge
d.tube("rim", [[XL, YR, ZF], [W - 13, YR, ZF], [W - 13, YR, DP - 13], [13, YR, DP - 13], [13, YR, ZF],
              [XL, YR, ZF]], 25, "frame", bend=70)
# thin PU pad lying in the rim (photo: its top only ~10 mm above the tube), big rounded front corners like the rim
d.slab("board", "top", rpoly([[18, ZF + 14], [W - 18, ZF + 14], [W - 18, DP - 18], [18, DP - 18]], 55), [YR - 6, YR + 24], "pad", r=8)
# back frame: inverted U with rounded top corners
d.tube("back", [[XL, YR, ZF], [XL, H - 13, ZF], [XR, H - 13, ZF], [XR, YR, ZF]], 25, "frame", bend=75)
d.decal("logo", [140, H - 13, ZF + 13], [40, 8], "front", "gloss#2a4fa8")
# elastic grid
GX0, GS, NV = W / 2 - 7 * 32, 32, 15
Y0, Y1 = YR + 24, H - 40
rows = [Y0 + 14 + i * 28.5 for i in range(12)]
for i in range(NV):
    x = GX0 + i * GS
    top = Y1 + (0 if i else -18)
    d.cyl(f"v{i}", [x, Y0, ZF - 2], [x, top, ZF - 2], 5, "cord", soft=True)
for i in range(1, NV, 2):     # loops over the top hooks joining verticals i, i+1
    x0, x1 = GX0 + i * GS, GX0 + (i + 1) * GS
    d.tube(f"loop{i}", [[x0, Y1, ZF - 2], [x0, Y1 + 18, ZF - 2], [x1, Y1 + 18, ZF - 2], [x1, Y1, ZF - 2]], 5, "cord",
           bend=10, soft=True)
    xm = (x0 + x1) / 2
    d.box(f"hook{i}", [xm - 9, Y1 + 10, ZF - 7, xm + 9, H - 22, ZF + 3], "frame", r=3, soft=True)
for j, y in enumerate(rows):
    d.cyl(f"h{j}", [XL + 14, y, ZF + 3], [XR - 14, y, ZF + 3], 5, "cord", soft=True)
    d.cyl(f"tl{j}", [XL + 10, y, ZF + 3], [XL + 26, y, ZF + 3], 6, "tie", soft=True, copies=[[XR - XL - 36, 0, 0]])
d.cyl("diag1", [XL + 12, rows[9], ZF + 3], [GX0, H - 50, ZF + 3], 5, "tie", soft=True)
d.cyl("diag2", [XR - 12, rows[6] + 10, ZF + 3], [XR - 50, rows[6] - 6, ZF + 3], 5, "tie", soft=True)
d.cyl("diag3", [XL + 14, rows[4] + 12, ZF + 3], [XL + 30, rows[4] - 6, ZF + 3], 5, "tie", soft=True)
d.save()
