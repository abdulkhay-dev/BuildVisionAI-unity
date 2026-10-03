"""YHZ-II (microwave therapy) fibreglass traction bed — batch table-4. Writes only yhz-ii-microwave.
Length along x, the hood at the right end (x = W) as in the photo, front z = D."""
import math
from t4lib import *

d = D("yhz-ii-microwave", [2200, 750, 900], {
    "white": "plastic#f1f1ef", "grey": "plastic#bdc4d3", "pad": "leather#4c7a2a", "harn": "fabric#5c9a2c", "strap": "fabric#8b8e94",
    "black": "fabric#2b2d31", "panel": "gloss#3a7ea6", "led": "gloss#e0302a", "logo": "gloss#2f7fd0",
    "dark": "plastic#202226", "cable": "black#18191b", "ctrl": "gloss#2a6fc0"})
W, DP, ZC = 2200, 750, 375
SL = 0.24                                 # inward slope of the skirt faces (z per y)
ANG = math.degrees(math.atan(SL))

def hz(y): return 225 + SL * y           # half depth of the skirt at height y
def xl(y): return 110 - 0.19 * y          # left end of the skirt
def xr(y): return 2120 + 0.125 * y        # right end

def s_(y, xa, xb, r=30): return sec(y, xb - xa, 2 * hz(y), r, (xa + xb) / 2, ZC)

# --- light-grey skirt sloping inwards to the floor, deep arch under the left half
d.loft("skirt-top", [s_(295, xl(295), xr(295)), s_(480, xl(480), xr(480))], "grey")
d.loft("skirt-foot", [s_(0, xl(0), 300), s_(300, xl(300), 300)], "grey")
d.loft("skirt-main", [s_(0, 800, xr(0)), s_(300, 720, xr(300))], "grey")
d.box("arch-round", [292, 250, ZC - hz(260) + 4, 330, 300, ZC + hz(260) - 4], "grey", r=18)
# white trapezoid logo panel on the front, down to the floor (lies on the sloping face)
pr = rot("x", ANG, [0, 0, ZC + hz(0)])
z0 = ZC + hz(0) + 0.6
front_slab(d, "front-panel", [(830, 2), (1400, 2), (1430, 470), (700, 470)], z0, z0 + 4, "white", r=1.5, rot=pr)
brand(d, "logo", 1010, 300, z0 + 4, 62)
tilt_parts(d, "logo", pr)
# --- white upper shell band (bevel line) carrying the pads
d.loft("band", [sec(465, 2180, 2 * hz(465) + 10, 40, 1100, ZC), sec(560, 2200, 745, 55, 1100, ZC),
                sec(725, 2200, 750, 55, 1100, ZC)], "white")
d.decal("bevel", [880, 560, DP + 0.3], [1760, 3], "front", "plastic#d7d8d6", soft=True)
for k in range(4):
    x0 = 45 + k * 410
    top_pad(d, f"pad{k}", x0, x0 + 405, 45, DP - 45, 722, 742, "pad", cr=14, r=6)
# long traction straps and the black chest harness
for k, z in enumerate((245, 505)):
    d.strap(f"rope{k}", [[60, 743, z], [1650, 743, z]], [32, 3], "strap", soft=True)
    d.decal(f"rope-dash{k}", [90, 746.3, z], [20, 6], "top", "dark", soft=True, repeat=rep(30, [56, 0, 0]))
# harness (photo): two padded green belts lying across the pads (chest, pelvis), dark grey straps over them that
# stand up as loops at the back, black buckles
for nm, x0, x1 in (("c", 430, 650), ("p", 680, 930)):
    d.box(f"harn-{nm}", [x0, 742, 150, x1, 768, 640], "harn", r=12, puff=5)
    for k in range(3):
        xx = x0 + 35 + k * (x1 - x0 - 70) / 2
        d.strap(f"harn-t{nm}{k}", [[xx, 770, 655], [xx, 770, 170], [xx + 8, 805, 140], [xx + 14, 830, 128]], [40, 3], "black", bend=25, soft=True)
    d.box(f"harn-bk{nm}", [x0 + 20, 770, 300, x1 - 20, 776, 330], "black", r=3, soft=True)
d.strap("harn-l", [[300, 746, 330], [430, 770, 335], [930, 770, 335], [1000, 746, 330]], [38, 3], "black", bend=40, soft=True)
# --- hood at the right end: loft with the chamfered front and left faces
# white apron of the hood region: flush with the band front, down to y 380, from the logo panel to the end
d.loft("apron", [sec(380, 770, 712, 40, 1815, ZC), sec(600, 770, 750, 40, 1815, ZC)], "white")
d.loft("hood", [sec(470, 520, 750, 40, 1940, ZC), sec(765, 520, 750, 40, 1940, ZC),
                sec(900, 370, 560, 40, 2015, 280)], "white")
ca = math.degrees(math.atan2(750 - 560, 900 - 765))     # front chamfer: normal tilted from up towards the front
hr = rot("x", ca, [0, 832, 655])
d.box("panel", [1870, 829, 572, 2170, 834, 738], "panel", r=4, rot=hr)
d.box("panel-lab", [1890, 833, 584, 1990, 835.5, 600], "plastic#eef2f6", r=2, soft=True, rot=hr)
d.box("led", [2005, 833, 582, 2035, 836, 606], "led", r=2, soft=True, rot=hr, repeat=rep(5, [30, 0, 0]))
d.box("led-b", [1895, 833, 625, 1925, 836, 650], "led", r=2, soft=True, rot=hr, repeat=rep(2, [40, 0, 0]))
d.box("keys", [1995, 833, 628, 2010, 836, 648], "plastic#e8edf2", r=2, soft=True, rot=hr, repeat=rep(7, [22, 0, 0]))
d.box("key-red", [2150, 833, 628, 2160, 836, 648], "led", r=2, soft=True, rot=hr)
d.box("panel-line", [1890, 833, 668, 2150, 835.5, 671], "led", r=1, soft=True, rot=hr)
d.box("panel-txt", [1890, 833, 690, 2150, 835.5, 715], "plastic#d9e6ef", r=2, soft=True, rot=hr)
# sockets on the grey skirt under the hood (sloping face)
zs = ZC + hz(330) + 1
d.cyl("sock", [1690, 330, zs - 6], [1690, 330, zs + 10], 30, "dark", soft=True, copies=[[40, 0, 0]])
d.box("mains", [1780, 310, zs - 6, 1840, 345, zs + 6], "dark", r=8, soft=True)
d.box("dsub", [1880, 300, zs - 4, 1950, 355, zs + 2], "plastic#d5d8dc", r=3, soft=True)
d.box("dsub-in", [1900, 318, zs + 1, 1930, 336, zs + 5], "dark", r=2, soft=True)
# --- blue hand controller on the front rim, black cable down to the floor, coiled part up to the socket
d.box("hand", [1150, 615, 750, 1265, 685, 775], "ctrl", r=10)
d.decal("hand-lamp", [1170, 670, 775.5], [10, 10], "front", "gloss#e8f0ff", soft=True, repeat=rep(3, [0, -16, 0]))
d.decal("hand-lab", [1220, 660, 775.5], [70, 14], "front", "plastic#dfe8f5", soft=True)
d.tube("cable", [[1265, 650, 765], [1300, 600, 770], [1340, 420, 735], [1395, 230, 715], [1440, 200, 712]], 8, "cable", bend=150, soft=True)
d.coil("coil", [1440, 200, 712], [1690, 320, 700], 28, 7, 22, "cable", soft=True)
d.save()
