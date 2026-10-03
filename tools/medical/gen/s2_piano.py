"""piano-water-column: 8 square acrylic bubble columns of falling height on a lit white platform with colour touch
keys, on a pale-green base cabinet, in its mirrored niche (as in the photo)."""
import random
from s2lib import *

W, Dp, H = 1200, 350, 900
d = D("piano-water-column", [W, Dp, H], {
    "cab": "plastic#d3e0b2", "plat": "gloss#f7f8f4", "side": "plastic#ece6d0", "frame": "plastic#f4f3ee"})
PY = 184                      # top of the platform
# base cabinet and the platform
d.box("cabinet", [0, 0, 0, W, 157, Dp - 4], "cab", r=6)
d.box("platform", [0, 157, 0, W, PY, Dp], "plat", r=4)
d.cyl("btn-ring", [536, 70, Dp - 6], [536, 70, Dp + 2], 116, "plastic#4e6c68")
d.lathe("btn", [536, 70, Dp + 2], [[0, 0], [40, 0], [40, 4], [34, 8], [0, 9]], "gloss#2e9a5c", axis="z")
d.cyl("hole-l", [116, 68, Dp - 6], [116, 68, Dp + 0.8], 48, "black#0c0c0e")
d.cyl("hole-r", [1098, 68, Dp - 6], [1098, 68, Dp + 0.8], 48, "black#4a0c12")
# niche: mirror back, cream sides (left one with a mirror inside), white top frame
d.box("back", [0, PY, 0, W, H - 20, 14], "side")
# the mirror back reflects the dim sensory room on the photo (dark navy-teal); a studio mirror would render flat
# grey, so it is drawn as dark glossy glass of the photo's colour
d.box("mirror", [20, PY, 14, W - 20, H - 27, 16], "gloss#1f3a50", soft=True)
d.box("side-l", [0, PY, 0, 20, H, Dp], "side", r=3)
d.box("side-l-mirror", [20, PY, 16, 22, H - 27, Dp - 10], "gloss#2b4a5e", soft=True)
d.box("side-r", [W - 20, PY, 0, W, H, Dp], "side", r=3)
d.box("top", [0, H - 27, 0, W, H, Dp], "frame", r=3)
# bubble columns: square acrylic tubes standing on the back half of the platform
xs = [170, 293, 423, 539, 664, 798, 921, 1037]
hs = [618, 566, 501, 453, 396, 334, 280, 223]
cols = ["dceefe", "ec5fd8", "2f62ff", "2ec0f4", "3ee08a", "ffe040", "ffa030", "ff3a58"]
keys = [None, "d83aa8", "2636c8", "2a8ae6", "22b04a", "f0d018", "f07a1e", "e0202e"]
rnd = random.Random(3)
for i, (x, h, c) in enumerate(zip(xs, hs, cols)):
    z = 150
    d.box(f"tube{i}", [x - 45, PY, z - 45, x + 45, PY + h, z + 45], f"acrylic#{c}c8", r=4)
    d.box(f"tube{i}-core", [x - 14, PY + 14, z - 14, x + 14, PY + h - 30, z + 14], "led", soft=True)
    d.box(f"tube{i}-cap", [x - 46, PY + h - 8, z - 46, x + 46, PY + h + 2, z + 46], f"acrylic#{c}f0", r=4, soft=True)
    d.box(f"tube{i}-foot", [x - 47, PY, z - 47, x + 47, PY + 14, z + 47], f"gloss#{c}", r=3)
    # rising bubbles: small white spheres in two loose columns
    # dense fizz as on the photo: ~3 bubbles per 12 mm of height, small white discs facing out (front and sides)
    offs = []
    for k in range(int((h - 40) / 12)):
        for m in range(3):
            offs.append([rnd.uniform(-38, 38), 22 + k * 12 + rnd.uniform(-5, 5), 0])
    b0 = offs[0]
    for f, (zz, fz) in enumerate(((z + 44, 2), (z + 20, 2))):
        d.cyl(f"tube{i}-bub{f}", [x + b0[0], PY + b0[1], zz], [x + b0[0], PY + b0[1], zz + fz], 5 if f else 6,
              "gloss#ffffff", sides=8, soft=True,
              copies=[[o[0] - b0[0], o[1] - b0[1], 0] for o in (offs[1:] if f == 0 else offs[1::2])])
    if keys[i]:
        d.box(f"key{i}", [x - 32, PY - 1, 280, x + 32, PY + 2, 318], f"gloss#{keys[i]}", r=1)
d.save()
