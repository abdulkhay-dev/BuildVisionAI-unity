"""kinesio-5: balance boards xy-47 (orange rocker board) and xy-49 (maple board with a rear U-handle)."""
from k5lib import *

# ---- xy-47: orange lacquered board 900 x 700 x 20 on a red-orange rocker shell (arc along x), round badge in front
d = D("xy-47", [900, 700, 90], {"board": "plastic#ea8c10", "rocker": "plastic#e0531a", "badge": "gloss#f4f4f2",
                                 "ring": "gloss#2a2d33"})
d.box("board", [0, 70, 0, 900, 90, 700], "board", r=4)
d.box("board-under", [8, 64, 8, 892, 71, 692], "plastic#d06a12", r=2)
# rocker: a shell whose front/back faces are arcs (lowest in the middle), set back a little from the board edges
d.slab("rocker", "front", rocker_outline(30, 870, 66, 66), [25, 675], "rocker", r=6)
# small round badge on the rocker's front face
d.lathe("badge", [450, 32, 675], [[0, 0], [31, 0], [31, 3], [0, 4]], "ring", axis="z", soft=True)
d.lathe("badge-in", [450, 32, 678], [[0, 0], [26, 0], [26, 2], [0, 2.5]], "badge", axis="z", soft=True)
# the badge picture: a dark figure on a diagonal over a dark baseline
d.box("badge-mark", [436, 30, 680.2, 466, 36, 681.2], "ring", soft=True, rot=rot("z", 25, [451, 33, 680.7]))
d.box("badge-line", [432, 20, 680.2, 468, 23, 681.2], "ring", soft=True)
d.save()

# ---- xy-49: pale maple board 700 (x) x 900 (z) x 20 with an orange edge band, dark wooden rocker underneath
#      (arc along x), chrome U-handle Ø25 at the rear (short) edge
d = D("xy-49", [700, 900, 220], {"top": "plastic#eedcbc", "edge": "gloss#e39a4e", "rocker": "wood#8a5a34",
                                  "chrome": "chrome"})
d.box("board", [0, 42, 0, 700, 60, 900], "edge", r=3)
d.box("board-top", [3, 59.5, 3, 697, 62, 897], "top", r=1)
d.slab("rocker", "front", rocker_outline(120, 580, 44, 44), [140, 760], "rocker", r=5)
d.box("rocker-pad", [130, 40, 120, 570, 44, 780], "rocker", r=2)
# U-handle: two posts and a top bar with rounded corners, flanges on the board
d.tube("handle", [[95, 60, 70], [95, 220 - 12.5, 70], [605, 220 - 12.5, 70], [605, 60, 70]], 25, "chrome", bend=45)
d.lathe("flange", [95, 60, 70], [[0, 0], [24, 0], [24, 4], [14, 8], [0, 8]], "chrome", copies=[[510, 0, 0]])
d.save()
