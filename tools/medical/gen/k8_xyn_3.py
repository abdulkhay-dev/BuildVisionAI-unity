"""XYN-3 wrist exerciser: wooden plank with a chrome wire bent into a zig-zag mountain profile (traced on the photo,
x_mm = (px - 40) * 1.067, y_mm = 25 + (375 - py) * 1.2) and a red-brown wooden handle hanging in a valley."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from k8lib import *

W, DP, H = 800, 200, 450
d = D("xyn-3", [W, DP, H], {"wood": "plastic#e4c46c", "edge": "plastic#d9963a", "wire": "chrome", "handle": "wood#8a2b18",
                            "brass": "metal#b8913e"})
YT = 22
d.box("plank", [0, 2, 0, W, YT, DP], "wood", r=3)
d.box("edge-f", [1, 3, DP - 1, W - 1, YT - 1, DP + 0.8], "edge", r=1)
d.box("foot", [10, 0, 10, 40, 2, 40], "rubber#2b2c2e", copies=[[W - 50, 0, 0], [0, 0, DP - 50], [W - 50, 0, DP - 50]])
d.cyl("sticker", [W - 52, YT, 150], [W - 52, YT + 0.8, 150], 30, "gloss#f4f6f8", soft=True)
d.cyl("sticker-b", [W - 52, YT, 150], [W - 52, YT + 1.2, 150], 18, "gloss#2f5fb0", soft=True)
CZ = DP / 2
px = [(138, 378), (135, 320), (128, 245), (170, 140), (205, 52), (220, 30), (238, 32), (250, 62), (257, 200), (262, 255), (275, 268),
      (290, 258), (335, 165), (352, 155), (368, 160), (388, 185), (400, 192), (412, 210), (430, 170), (520, 35), (538, 22),
      (556, 32), (572, 160), (580, 180), (590, 172), (668, 52), (684, 42), (698, 54), (697, 200), (692, 378)]
pts = [[(x - 40) * 1.067, YT + (375 - y) * 1.2 - 3, CZ] for x, y in px]
pts[0][1] = YT - 2; pts[-1][1] = YT - 2
d.tube("wire", pts, 8, "wire", bend=14)
for k in (0, -1):
    d.cyl(f"flange{k}", [pts[k][0], YT, CZ], [pts[k][0], YT + 4, CZ], 34, "chrome")
    d.cyl(f"boss{k}", [pts[k][0], YT, CZ], [pts[k][0], YT + 16, CZ], 15, "chrome")
# handle hanging from the valley at px (580, 180)
hx = (580 - 40) * 1.067
hy = YT + (375 - 180) * 1.2 - 3
d.tube("swivel", ring_pts([hx, hy - 4, CZ], 9, 8, "zy", 12), 3, "chrome", soft=True)
d.cyl("swivel-pin", [hx, hy - 12, CZ], [hx, hy - 30, CZ], 6, "chrome")
d.cyl("ferrule", [hx, hy - 42, CZ], [hx, hy - 28, CZ], 16, "brass")
d.lathe("handle", [hx, hy - 144, CZ], [[0, 0], [3, 0], [6, 5], [11, 18], [14, 48], [15, 80], [13, 95], [9, 102], [0, 104]],
        "handle")
d.save()
