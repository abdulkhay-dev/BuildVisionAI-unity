# XY-KGJ-2 hip joint training chair (table-3 batch). Photo pose: the patient's right leg lever points forward-down
# to the floor, the left one is swung out (abducted) ~40 deg; both end in a small floor wheel.
import math
from lib import *
d = D("xy-kgj-2", [960, 1380, 880], {
  "frame": "plastic#f1f0ea", "pad": "leather#2c50a6", "cuff": "leather#7b9bdb", "arm": "leather#1f2a33",
  "blk": "rubber#1b1c1f", "chr": "chrome", "steel": "metal#9aa3ad", "plate": "plastic#1f8a4c", "strap": "fabric#1d2326",
  "bolt": "plastic#5a6068"})
# ---- base: square white tube frame on 4 black foot blocks
X0, X1, Z0, Z1 = 20, 640, 20, 640
d.bar("base-x", [X0, 45, Z0], [X1, 45, Z0], [40, 40], "frame", r=4, copies=[[0, 0, Z1 - Z0]])
d.bar("base-z", [X0, 45, Z0], [X0, 45, Z1], [40, 40], "frame", r=4, copies=[[X1 - X0, 0, 0]])
d.box("foot", [X0 - 30, 0, Z0 - 30, X0 + 30, 62, Z0 + 30], "blk", r=5,
      copies=[[X1 - X0, 0, 0], [0, 0, Z1 - Z0], [X1 - X0, 0, Z1 - Z0]])
# ---- posts and seat frame
for nm, (x, z) in (("pfl", (75, 590)), ("pfr", (585, 590)), ("pbr", (585, 90))):
    d.bar("post-" + nm, [x, 65, z], [x, 420, z], [50, 50], "frame", r=4)
d.bar("seat-rail-x", [60, 420, 590], [600, 420, 590], [40, 50], "frame", r=4, copies=[[0, 0, -500]])
d.bar("seat-rail-z", [75, 420, 80], [75, 420, 615], [40, 50], "frame", r=4, copies=[[510, 0, 0]])
d.bar("side-rail", [30, 380, 60], [30, 380, 470], [30, 60], "frame", r=4)   # bolted rail on the left side
d.cyl("rail-bolt", [14, 380, 120], [10, 380, 120], 14, "bolt", soft=True, repeat=rep(6, [0, 0, 65]))
# ---- tall rear frame on the left with the white top cap (cable guide of the weight stack)
d.bar("rear-post", [45, 65, 60], [45, 830, 60], [50, 50], "frame", r=4, copies=[[95, 0, 0]])
d.box("rear-cap", [15, 800, 15, 330, 880, 125], "frame", r=18)
d.cyl("guide-rod", [92, 90, 60], [92, 800, 60], 14, "chr")
# ---- seat and backrest (navy-blue PU)
d.box("seat", [110, 445, 120, 600, 520, 640], "pad", r=28, puff=4)
d.box("seat-board", [120, 425, 130, 590, 447, 625], "frame", r=4)
br = rot("x", -8, [335, 500, 110])
d.box("back-frame", [170, 470, 70, 560, 880, 95], "frame", r=14, rot=br)
d.box("back", [185, 520, 92, 545, 865, 152], "pad", r=26, puff=4, rot=br)
# ---- armrests: white tube supports with black padded arm pads curling down at the front
for nm, x in (("l", 100), ("r", 620)):
    d.tube("arm-tube-" + nm, [[x, 420, 560], [x, 650, 560], [x, 655, 440]], 30, "frame", bend=60)
    d.sweep("arm-pad-" + nm, [[x, 670, 170], [x, 690, 480], [x, 685, 570], [x, 620, 600]], [55, 45], "arm",
            shape="rect", r=16, bend=50)
    d.bar("arm-stay-" + nm, [x, 640, 165], [x, 560, 130], [25, 25], "frame", r=3)
# ---- weight stack: grey steel platform with two pegs of green plates, plus a storage peg at the front-left
d.box("platform", [30, 70, 120, 330, 86, 470], "steel", r=4)
for i, (x, z) in enumerate(((120, 250), (240, 330))):
    d.cyl(f"peg{i}", [x, 86, z], [x, 360, z], 22, "chr")
    d.cyl(f"plates{i}", [x, 190, z], [x, 255, z], 180, "plate", repeat=rep(1, [0, 0, 0]))
    d.cyl(f"plates{i}-gap", [x, 220, z], [x, 224, z], 184, "plastic#156b3a", soft=True)
    d.cyl(f"peg{i}-collar", [x, 255, z], [x, 275, z], 50, "steel")
d.cyl("store-peg", [70, 45, 560], [70, 300, 560], 25, "steel")
d.cyl("store-plate", [70, 66, 560], [70, 90, 560], 180, "plate")
# ---- leg levers: pivot hubs under the seat front, horizontal thigh cuff, double chrome rods down to a floor wheel
def lever(nm, px, yaw):
    a = math.radians(yaw)
    ux, uz = math.sin(a), math.cos(a)          # horizontal direction of the lever
    P = [px, 430, 600]
    d.cyl("hub-" + nm, [px, 375, 600], [px, 420, 600], 60, "steel")
    d.cyl("hub-cap-" + nm, [px, 370, 600], [px, 382, 600], 40, "bolt")
    # thigh cuff (horizontal, along the lever direction)
    A = [px + ux * 40, 455, 600 + uz * 40]; B = [px + ux * 250, 455, 600 + uz * 250]
    d.bar("thigh-" + nm, A, B, [150, 70], "cuff", r=24)
    M = [px + ux * 150, 455, 600 + uz * 150]
    d.bar("thigh-strap-" + nm, [M[0] - ux * 25, 460, M[2] - uz * 25], [M[0] + ux * 25, 460, M[2] + uz * 25],
          [156, 80], "strap", r=24)
    d.bar("thigh-bracket-" + nm, [px + ux * 10, 412, 600 + uz * 10], [px + ux * 220, 412, 600 + uz * 220], [70, 20], "steel", r=3)
    # rods from under the thigh cuff down to the floor wheel
    K = [px + ux * 160, 405, 600 + uz * 160]
    R = 760
    E = [px + ux * R, 55, 600 + uz * R]
    for s in (-1, 1):
        ox, oz = uz * 22 * s, -ux * 22 * s
        d.cyl(f"rod-{nm}{'ab'[s > 0]}", [K[0] + ox, K[1], K[2] + oz], [E[0] + ox, E[1], E[2] + oz], 16, "chr")
    d.box("end-" + nm, [E[0] - 30, 40, E[2] - 30, E[0] + 30, 70, E[2] + 30], "steel", r=6)
    d.add("wheel-" + nm, "wheel", "blk", at=[E[0], 25, E[2]], d=50, d2=18, axis="x" if abs(uz) > abs(ux) else "z")
    # shin cuff along the rods, with a black Velcro strap
    def at(t, up):
        return [K[0] + (E[0] - K[0]) * t, K[1] + (E[1] - K[1]) * t + up, K[2] + (E[2] - K[2]) * t]
    d.bar("shin-" + nm, at(0.38, 50), at(0.62, 50), [150, 80], "cuff", r=24)
    d.bar("shin-strap-" + nm, at(0.47, 54), at(0.55, 54), [156, 90], "strap", r=24)
lever("r", 250, 0)
lever("l", 440, 40)
d.save()
