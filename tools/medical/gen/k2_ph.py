"""xy-ph-iv (seated) / xy-ph-v (standing) — balance training platforms (kinesio-2)."""
import math
from k2lib import *

# ---------------- XY-PH-V: standing platform, two telescopic posts at the rear with C-shaped handrail loops
d = D("xy-ph-v", [800, 830, 1350], {
    "base": "plastic#e4e6e9", "side": "plastic#d3d6da", "graph": "plastic#4a4e55", "plat": "plastic#9a9ea4",
    "plattop": "plastic#a9adb3", "white": "plastic#f1f2f4", "darkgrey": "plastic#5b6068", "black": "plastic#1d1f22",
    "steel": "metal#b8bcc2", "grip": "rubber#55595f"})
# plinth on 4 levelling feet: light top, slightly darker sides; dark graphite rear rail carrying the posts
d.loft("plinth", [sec(35, 800, 800, 70, 400, 430), sec(120, 800, 800, 70, 400, 430), sec(135, 780, 780, 60, 400, 430)], "base")
d.box("plinth-skirt", [10, 30, 40, 790, 70, 820], "side", r=30)
for x in (70, 730):
    for z in (100, 760):
        d.cyl(f"foot-{x}-{z}", [x, 0, z], [x, 32, z], 50, "black")
# dark grip recesses in the side faces near the front (photo: right face, close to the front corner)
d.box("grip-recess", [796, 55, 600, 802, 112, 730], "darkgrey", r=12, mirror="x")
d.box("rear-rail", [20, 120, 30, 780, 190, 120], "graph", r=14)
# rounded graphite end blocks at the rail ends, down the plinth's back corners to their own feet
d.box("rail-end", [742, 22, 22, 802, 205, 150], "graph", r=26, mirror="x")
d.decal("logo", [715, 136, 225], [70, 26], "top", "gloss#2f7fd0", soft=True)
# round platform on a dark pivot housing (raised ~120)
PX, PZ = 400, 470
d.lathe("pivot", [PX, 135, PZ], [[0, 0], [265, 0], [270, 12], [255, 25], [235, 30], [235, 70], [0, 70]], "graph")
d.lathe("pivot-ring", [PX, 160, PZ], [[0, 0], [250, 0], [250, 14], [0, 14]], "darkgrey")
d.box("pivot-label", [PX - 40, 170, PZ + 228, PX + 40, 200, PZ + 238], "black", r=4)
d.lathe("platform", [PX, 205, PZ], [[0, 0], [255, 0], [272, 10], [275, 30], [262, 42], [0, 42]], "plat")
d.lathe("platform-top", [PX, 247, PZ], [[0, 0], [255, 0], [255, 2], [0, 2]], "plattop", soft=True)
# posts: white lower tube, black collar, slotted inner tube, dark grey head block with the knob
for side, x in (("l", 70), ("r", 730)):
    d.box(f"post-{side}", [x - 35, 190, 45, x + 35, 600, 105], "white", r=8)
    d.box(f"collar-{side}", [x - 38, 600, 42, x + 38, 650, 108], "black", r=6)
    d.box(f"inner-{side}", [x - 26, 650, 52, x + 26, 985, 98], "steel", r=5)
    d.box(f"slot-{side}", [x - 8, 665, 97, x + 8, 975, 100], "black", r=3)
    d.decal(f"hole-{side}", [x, 700, 100.6], [9, 9], "front", "plastic#e8e8e8", soft=True, repeat=rep(6, [0, 45, 0]))
    d.box(f"head-{side}", [x - 42, 980, 35, x + 42, 1290, 115], "darkgrey", r=10)
    d.lathe(f"knob-{side}", [x + (36 if x > 400 else -36), 500, 75], [[0, 0], [8, 0], [8, 12], [24, 14], [24, 34], [0, 36]], "black",
            axis="x", rot=rot("y", 0 if x > 400 else 180, [x + (36 if x > 400 else -36), 500, 75]))
    # C-shaped handrail loop facing forward: upper grip bar (dark), white bend, lower bar back to the post
    zf = 390
    d.sweep(f"loop-{side}", [[x, 1250, 110], [x, 1250, zf], [x, 1070, zf], [x, 1070, 110]], [36, 36], "white", shape="round", bend=95)
    d.cyl(f"loop-grip-{side}", [x, 1250, 120], [x, 1250, zf - 80], 42, "grip")
# white top crossbar between the post heads at the back
d.sweep("top-bar", [[70, 1300, 75], [70, 1318, 75], [730, 1318, 75], [730, 1300, 75]], [34, 34], "white", shape="round", bend=30)
d.cyl("top-grip", [420, 1318, 75], [680, 1318, 75], 42, "grip")
d.save()

# ---------------- XY-PH-IV: seated platform, central column, rear C-frame with backrest and armrests
d = D("xy-ph-iv", [700, 800, 1050], {
    "base": "plastic#e1e3e6", "col": "plastic#d9dbdf", "black": "plastic#1b1c1f", "pad": "leather#1f2023",
    "seat": "plastic#202124", "disc": "plastic#c2c4c7", "chrome": "chrome", "foam": "rubber#18191b"})
CX, SZ = 350, 470
# base plate on 4 small feet: rounded plate with two rounded lobes at the front corners
d.slab("base", "top", "M 60 30 L 640 30 Q 690 30 690 80 L 690 700 Q 690 780 610 780 L 480 780 Q 440 780 420 768 L 280 768 "
       "Q 260 780 220 780 L 90 780 Q 10 780 10 700 L 10 80 Q 10 30 60 30 Z", [25, 85], "base", r=14)
for x, z in ((60, 80), (640, 80), (70, 730), (630, 730)):
    d.cyl(f"foot-{x}-{z}", [x, 0, z], [x, 25, z], 46, "black")
d.decal("base-logo", [600, 70, 781], [40, 14], "front", "gloss#2f7fd0", soft=True)
# central square column, chrome bearing, black bowl, seat plate with the grey textured disc
d.box("column", [CX - 75, 85, SZ - 75, CX + 75, 420, SZ + 75], "col", r=8)
d.lathe("bearing", [CX, 420, SZ], [[0, 0], [85, 0], [85, 18], [75, 22], [75, 40], [0, 40]], "chrome")
d.lathe("bowl", [CX, 455, SZ], [[0, 0], [95, 0], [140, 25], [175, 60], [185, 75], [0, 75]], "black")
d.loft("seat", [sec(528, 500, 470, 110, CX, SZ), sec(548, 520, 490, 120, CX, SZ), sec(560, 500, 470, 110, CX, SZ)], "seat")
d.lathe("seat-disc", [CX, 560, SZ], [[0, 0], [190, 0], [195, 6], [190, 12], [0, 12]], "disc")
# rear C-frame: from the column foot back, up the slant, vertical to the backrest (light grey square tube)
d.sweep("c-frame", [[CX, 300, SZ - 75], [CX, 300, 280], [CX, 520, 120], [CX, 800, 120]], [70, 60], "col", r=8, bend=60)
# backrest on a chrome bar, armrest tube: U behind the backrest, ends forward with black foam sleeves
d.box("backrest", [CX - 160, 720, 90, CX + 160, 1050, 150], "pad", r=34, puff=8)
d.box("backrest-shell", [CX - 150, 730, 80, CX + 150, 1040, 92], "black", r=28)
d.bar("back-mount", [CX, 700, 110], [CX, 760, 95], [80, 40], "chrome", r=6)
AY = 750
d.sweep("arm-tube", [[CX - 275, AY, 520], [CX - 275, AY, 60], [CX + 275, AY, 60], [CX + 275, AY, 520]], [30, 30], "chrome",
        shape="round", bend=70)
d.cyl("arm-foam-l", [CX - 275, AY, 170], [CX - 275, AY, 600], 46, "foam", copies=[[550, 0, 0]])
d.cyl("arm-pin", [CX - 275, AY - 10, 100], [CX - 200, AY - 10, 100], 22, "chrome", copies=[[475, 0, 0]])
d.save()
