"""xym-2 Gym rods and throwing balls, wall rack. W 1190 = rack body ~1040 + the rods sticking out ~150 at the left."""
import math
from k7lib import *

d = D("xym-2", [1190, 130, 700], {"wood": "plastic#de9a30", "wood2": "plastic#e6a843", "wooddk": "plastic#c9862a"})
X0, X1 = 140, 1172
# --- carcass: back board, two side panels
d.box("back", [X0, 0, 0, X1, 700, 14], "wood2", r=3)
d.box("side", [X0, 0, 0, X0 + 18, 700, 128], "wood", r=4, copies=[[X1 - X0 - 18, 0, 0]])
d.box("top", [X0, 684, 0, X1, 700, 110], "wood", r=4)
# --- upper part: 5 shelves with a front lip, a round gym rod lying on each (sticking out at the left)
for k in range(5):
    y = 620 - k * 62
    d.box(f"shelf-{k}", [X0 + 18, y, 14, X1 - 18, y + 12, 104], "wood", r=3)
    d.box(f"lip-{k}", [X0 + 18, y + 4, 96, X1 - 18, y + 30, 110], "wooddk", r=4)
    d.cyl(f"rod-{k}", [2, y + 25, 66], [1188, y + 25, 66], 25, "wood")
    d.sphere(f"rod-end-{k}", [14, y + 25, 66], 25, "wood")
# --- lower trough: floor, front board with a lip, the felt patchwork balls in it
d.box("trough-floor", [X0 + 18, 140, 14, X1 - 18, 156, 128], "wood", r=3)
d.box("trough-front", [X0, 0, 112, X1, 186, 130], "wood", r=4)
d.box("trough-lip", [X0, 178, 108, X1, 194, 130], "wooddk", r=5)
d.box("bottom", [X0, 0, 0, X1, 16, 128], "wood", r=3)
cols = {"r": "fabric#d8302a", "y": "fabric#f2d23a", "b": "fabric#1e8fd8", "g": "fabric#6aa83a", "c": "fabric#3ab0e6"}
patt = ["gby", "ryb", "bcy", "ygr", "rgy"]
base = "ybcbr"
# photo: 5 big patchwork balls (~Ø215) across the trough, the front board hiding their lower part
for i in range(5):
    c = [X0 + 18 + 104 + i * 197, 272, 66]
    RX, RY, RZ = 108, 106, 62
    d.sphere(f"ball-{i}", c, None, cols[base[i]], radii=[RX, RY, RZ])
    for j, p in enumerate(patt[i]):
        a = math.radians(40 + 120 * j + 25 * i)
        u = [math.cos(a) * 0.75, math.sin(a) * 0.75, 0.66]
        d.sphere(f"ball-{i}-p{j}", [c[0] + u[0] * 16, c[1] + u[1] * 16, c[2] + u[2] * 9], None, cols[p],
                 radii=[RX * 0.89, RY * 0.89, RZ * 0.9])
d.save()
