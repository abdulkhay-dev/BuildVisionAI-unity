"""xyrt-4 — training swing frame: two A-frames (green, barber-striped lower legs) and a top beam; three swings:
striped bucket seat, light-blue bolster, light-blue column on a disc."""
import math
from pd3_lib import *

W, Dp, H = 2000, 1400, 1950
d = D("xyrt-4", [W, Dp, H], {"g": "gloss#4fa57a", "plate": "gloss#3d8f68", "foot": "plastic#2a7f74",
                             "rope": "fabric#d47a62", "lb": "leather#9db8e2", "y": "gloss#f2d21f", "b": "gloss#1d4fa8",
                             "r": "gloss#d82a2a", "red": "fabric#d8352a"})
XS = [60, W - 60]
zc = 700
apex, zf, zr = 2000, 1330, 70
TD = 50
for nm, x in (("l", XS[0]), ("r", XS[1])):
    d.tube(f"arch-{nm}", [[x, 10, zf], [x, apex, zc], [x, 10, zr]], TD, "g", bend=50)
    d.slab(f"plate-{nm}", "side", f"M {zc - 80} 1730 L {zc + 80} 1730 L {zc + 38} 1858 Q {zc} 1915 {zc - 38} 1858 Z", [x - 3, x + 3], "plate", r=1)
    d.cyl(f"xbar-{nm}", [x, 1000, 356], [x, 1000, 1044], 40, "g")
    for k, zz in enumerate([zf, zr]):
        d.cyl(f"foot-{nm}{k}", [x, 0, zz], [x, 10, zz], 120, "foot")
        top = [x, 950, zz + (1035 - zf if zz == zf else 365 - zr)]
        stripes(d, f"st-{nm}{k}", [x, 12, zz], top, 55, ["y", "b", "y", "r"], 55)
d.cyl("beam", [XS[0], 1880, zc], [XS[1], 1880, zc], TD, "g")
yb = 1855


def rope(id, p, q):
    """Twisted red-and-white cord (photo): a pale core with a salmon strand coiled round it."""
    _, L = unit(p, q)
    d.cyl(id, p, q, 9, "fabric#f1e2da", soft=True, sides=8)
    d.coil(id + "-tw", p, q, 10, 5, int(L / 16), "rope", soft=True)
# --- bucket seat (left): a soft sling sewn from vertical stripes (red / yellow / blue / yellow), sagging into a
# round bottom; each stripe is a strap running from the rim down to the bottom centre, a red lining closes the gaps
bx = 420
RX, RZ, YT = 245, 215, 505
prof = [(1.0, YT), (0.99, 430), (0.9, 350), (0.68, 285), (0.38, 248), (0.1, 236)]
d.loft("bucket", [sec(250, 110, 90, 45, bx, zc), sec(300, 360, 312, 150, bx, zc), sec(420, 458, 398, 190, bx, zc),
                  sec(YT - 6, 474, 414, 200, bx, zc)], "red", dome="start", domeH=14)
NG = 18
cyc = ["fabric#d8352a", "fabric#f2c81f", "fabric#1f4fa8", "fabric#f2c81f"]
for g in range(NG):
    th = 2 * math.pi * (g + 0.5) / NG
    c, sn = math.cos(th), math.sin(th)
    # a short inward lead-in under the rim makes the strap's width lie along the rim (tangent) all the way down
    path = [[bx + (RX + 12) * c, YT - 4, zc + (RZ + 12) * sn]] + \
           [[bx + (RX + 4) * f * c, y - (4 if k == 0 else 0), zc + (RZ + 4) * f * sn] for k, (f, y) in enumerate(prof)]
    gw = 2 * math.pi * math.sqrt((RX * RX + RZ * RZ) / 2) / NG + 2
    d.strap(f"gore{g}", path, [gw, 4], cyc[g % 4], bend=60, soft=True)
# rim: a soft light green-blue roll round the top edge
ring = [[bx + (RX + 6) * math.cos(t), YT, zc + (RZ + 6) * math.sin(t)] for t in [k * 2 * math.pi / 24 for k in range(25)]]
d.tube("brim", ring, 30, "fabric#86c3a6")
for k, (dx, dz) in enumerate([(-200, -150), (200, -150), (-200, 150), (200, 150)]):
    p = [bx + dx, 505, zc + dz]
    q = [bx, yb, zc]
    rope(f"brope{k}", p, q)
    u, L = unit(p, q)
    d.cyl(f"bslv{k}", p, [p[i] + u[i] * 270 for i in range(3)], 32, "lb")
# --- bolster (middle)
d.cyl("bolster", [800, 420, zc], [1580, 420, zc], 200, "lb", sides=32)
d.sphere("bol-end", [800, 420, zc], 200, "lb", radii=[25, 100, 100], copies=[[780, 0, 0]])
for k, x in enumerate([850, 1530]):
    rope(f"rope{k}", [x, 520, zc], [x, yb, zc])
    d.cyl(f"slv{k}", [x, 515, zc], [x, 790, zc], 32, "lb")
# --- column (right) on a tray and an orange disc
cx = 1720
d.cyl("disc", [cx, 250, zc], [cx, 268, zc], 420, "wood#d99c5c", sides=40)
d.lathe("tray", [cx, 268, zc], [[0, 0], [160, 0], [165, 30], [150, 32], [140, 8], [0, 8]], "plastic#6f98d4")
d.cyl("column", [cx, 276, zc], [cx, 830, zc], 230, "lb", sides=36)
d.sphere("col-top", [cx, 830, zc], 230, "lb", radii=[115, 18, 115])
d.cyl("col-rod", [cx, 840, zc], [cx, 1180, zc], 42, "lb")
rope("col-rope", [cx, 1180, zc], [cx, yb, zc])
# swivel hooks on the beam
for k, x in enumerate([bx, 850, 1530, cx]):
    d.cyl(f"hook{k}", [x, yb - 8, zc], [x, 1858, zc], 22, "chrome")
d.save()
