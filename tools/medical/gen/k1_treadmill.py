"""gait-obstacle-treadmill: low rehab treadmill with full-length handrails, a console on a curved bar at the console end
(z=0, the user walks toward it from the tail at z max), white obstacle boards on the belt, a striped panel on the far rail."""
import math
from k1lib import *

d = D("gait-obstacle-treadmill", [900, 2100, 1400], {
    "frame": "metal#8f949a", "belt": "rubber#232426", "black": "plastic#1f2022", "hood": "plastic#4a4e54",
    "rail": "metal#aeb3b9", "white": "plastic#f4f4f2", "console": "plastic#c9ccd0", "red": "gloss#c8324a",
    "green": "gloss#5fc84f"})
# --- deck: grey side frames, black belt, black tail cap, dark motor hood at the console end, feet, outer floor beams
d.box("side-frame", [110, 55, 300, 195, 200, 2010], "frame", r=12, mirror="x")
d.box("deck", [195, 150, 320, 705, 175, 2000], "black", r=4)
d.box("belt", [205, 172, 320, 695, 192, 2020], "belt", r=8)
d.box("tail-cap", [105, 45, 1990, 795, 185, 2090], "black", r=30)
d.box("hood", [115, 55, 140, 785, 255, 320], "hood", r=40)
d.box("floor-beam", [35, 18, 220, 115, 70, 2060], "frame", r=10, mirror="x")
d.cyl("foot", [75, 0, 260], [75, 20, 260], 64, "black", mirror="x", copies=[[0, 0, 900], [0, 0, 1760]])
# --- posts (3 per side) with black collars and knobs, rails, tail ends bending down and out
Z = (300, 1640)          # photo: two posts per side, at the console end and ~3/4 toward the tail
for s, x in ((1, 75), (-1, 825)):
    nm = "l" if s > 0 else "r"
    for z in Z:
        d.box(f"post-{nm}{z}", [x - 25, 70, z - 25, x + 25, 935, z + 25], "frame", r=5)
        d.box(f"collar-{nm}{z}", [x - 31, 900, z - 31, x + 31, 945, z + 31], "black", r=6)
        d.lathe(f"knob-{nm}{z}", [x - s * 25, 820, z], [[0, 0], [7, 0], [7, 8], [17, 10], [17, 24], [0, 26]], "black",
                axis="x", sides=8, rot=rot("y", 180, [x - s * 25, 820, z]) if s > 0 else None)
    # the rail runs on past the tail post and bends down in the air above the deck's tail
    d.tube(f"rail-{nm}", [[x, 960, 280], [x, 960, 1830], [x, 930, 1940], [x, 790, 1975]], 40, "rail", bend=80)
# curved bar from the rails' console ends up over the hood to the console
d.tube("console-bar", [[75, 960, 330], [75, 990, 140], [75, 1170, 110], [825, 1170, 110], [825, 990, 140], [825, 960, 330]],
       38, "rail", bend=110)
# --- console: light-grey box tilted toward the user, LCD, red / green keys
T = rot("x", 35, [450, 1205, 120])
d.box("console", [255, 1180, 20, 645, 1240, 230], "console", r=14, rot=T)
d.add("lcd", "screen", "console", box=[340, 1236, 60, 560, 1242, 140], r=4, face="top", bezel=6, rot=T)
d.decal("lcd-seg", [450, 1242.8, 100], [180, 50], "top", "plastic#5b8fc8", soft=True, rot=T)
d.box("key-red", [285, 1238, 165, 320, 1246, 195], "red", r=6, rot=T, copies=[[300, 0, 0]])
d.box("key-green", [400, 1238, 170, 430, 1245, 195], "green", r=6, rot=T, copies=[[70, 0, 0]])
d.decal("panel-print", [450, 1241, 205], [300, 30], "top", "plastic#5c6b7c", soft=True, rot=T)
# --- obstacle boards on edge along the belt; fruit pictures on the near (-x) one
for x in (330, 520):
    d.box(f"board-{x}", [x, 192, 520, x + 40, 345, 1980], "white", r=8)
for i, z in enumerate(range(620, 1900, 210)):
    col = ("gloss#d4262a", "gloss#f1c232", "gloss#6cbf3a")[i % 3]
    d.lathe(f"fruit-{i}", [329, 268, z], [[0, 0], [34 if i % 3 == 0 else 24, 0], [34 if i % 3 == 0 else 24, 1.5],
                                           [0, 1.5]], col, axis="x", rot=rot("y", 180, [329, 268, z]))
# --- striped panel hanging from the far rail: grey frame, red / green / white stripes
# (photo: the panel starts by the console-end post)
d.tube("panel-frame", [[790, 945, 520], [790, 440, 560], [790, 440, 1120], [790, 945, 1160]], 22, "frame", bend=30)
for i in range(7):
    col = ("red", "white", "green")[i % 3]
    y = 480 + i * 64
    d.box(f"stripe-{i}", [784, y, 540, 796, y + 46, 1140], col, r=4)
d.save()
