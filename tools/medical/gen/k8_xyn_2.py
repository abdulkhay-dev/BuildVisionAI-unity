"""XYN-2 wrist exerciser: wooden plank, a semi-elliptic steel wire arc, a wooden handle hanging from the arc."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from k8lib import *

W, DP, H = 1100, 250, 510
d = D("xyn-2", [W, DP, H], {"wood": "plastic#e2bd5c", "edge": "plastic#d38b3a", "wire": "metal#8e9296", "chrome": "chrome",
                            "handle": "gloss#ad6630", "foot": "rubber#2b2c2e"})
YB, YT = 6, 26
d.box("plank", [0, YB, 0, W, YT, DP], "wood", r=4)
d.box("edge-f", [2, YB + 1, DP - 1, W - 2, YT - 1, DP + 0.8], "edge", r=1)
d.box("edge-r", [W - 0.8, YB + 1, 2, W + 0.6, YT - 1, DP - 2], "edge", r=1)
d.box("edge-l", [-0.6, YB + 1, 2, 0.8, YT - 1, DP - 2], "edge", r=1)
d.cyl("foot", [25, 0, 25], [25, YB, 25], 22, "foot", copies=[[W - 50, 0, 0], [0, 0, DP - 50], [W - 50, 0, DP - 50]])
CX, CZ, RX, RY = W / 2, DP / 2, 440, H - YT - 4
pts = [[CX - RX * math.cos(math.pi * k / 32), YT + RY * math.sin(math.pi * k / 32), CZ] for k in range(33)]
pts[0][1] = YT - 2; pts[-1][1] = YT - 2
d.tube("arc", pts, 6, "wire")
for sx in (-1, 1):
    d.cyl(f"ferrule{sx}", [CX + sx * RX, YT, CZ], [CX + sx * RX, YT + 14, CZ], 13, "chrome")
# handle on a small ring just right of the top
hx = CX
yt = YT + RY - 2
d.tube("ring", ring_pts([hx, yt - 2, CZ], 9, 9, "xy", 12), 3, "chrome", soft=True)
d.cyl("ferr", [hx, yt - 22, CZ], [hx, yt - 10, CZ], 12, "metal#b08a3a")
d.lathe("handle", [hx, yt - 160, CZ], [[0, 0], [7, 1], [11, 6], [13, 20], [14, 70], [13.5, 118], [11, 126], [9, 128], [9, 136], [6, 140], [0, 140]],
        "handle")
d.save()
