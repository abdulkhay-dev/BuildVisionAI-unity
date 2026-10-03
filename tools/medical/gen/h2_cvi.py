from h2lib import *
# XY-SL-CVI walk-in tub with a transfer beam, printed 1270 x 860 x 1000 (rim 720 / beam top 1000).
# Review 2026-10-02: the photo (front-left view) has its near vertical corner at x~420 px: the face with the door is the
# LONG face (750 px, edges slope 0.23) and the photo's left face is the SHORT end (390 px, slope 0.32) -> the door face is
# the front, size as printed [1270, 860, 1000] (the first version swapped W/D and put the door on a short face).
# Front (door face, left to right): narrow fixed panel with small recess marks, the door (teal U trim, white hinge strip
# at its right), fixed panel with a tall recessed moulding and the blue 翔宇医疗 logo at its top.
# Left end: big recessed panel with a horizontal handle moulding, a low recess band. Rim: black cap at the front-left
# corner, valve cluster + blue lever + flush key strip at the back-left; seat + cushion backrest at the left end.
# Transfer beam: light teal, across the depth near the right end, on a grey wedge at the front rim, teal end block at
# the back with the grey L arm reaching left over the basin (red pin, loop handle). Curtain rail with hooks over the basin.
W, DP = 1270, 860
RY, RT = 662, 58
T = RY + RT
d = D("xy-sl-cvi", [W, DP, 1000], {
    "shell": "gloss#f7f8f9", "inner": "gloss#eef1f4", "line": "plastic#dde2e7", "teal": "gloss#8ccfd8",
    "grey": "plastic#a9b0b8", "red": "gloss#d83a2e", "blue": "gloss#2f6fd0", "dark": "black#202326"})
hole = rr(200, 110, 1120, 795, 70)
d.slab("body", "top", ring(rr(4, 4, W - 4, DP - 4, 36), rr(60, 60, W - 60, DP - 60, 50)), [40, RY + 2], "shell", r=12)
d.box("plinth", [10, 0, 10, W - 10, 44, DP - 10], "shell", r=8)
tub(d, "", None, hole, rr(0, 0, W, DP, 40), RY, RT, 120, rr(180, 90, 1140, 815, 70), rim_r=16)
# seat block at the left end and the cushion backrest leaning on the left inner wall, shower roller behind it
d.box("seat", [200, 120, 110, 560, 440, 795], "inner", r=30)
d.box("cushion", [205, 430, 250, 285, 712, 650], "gloss#fbfbfc", r=40, puff=10, rot=rot("z", 8, [245, 430, 450]))
d.cyl("roller", [215, 690, 150], [340, 690, 150], 110, "gloss#fbfbfc")
d.lathe("shower", [340, 690, 150], [[0, 0], [40, 0], [40, 8], [30, 14], [0, 14]], "chrome", axis="x")
d.lathe("jet", [600, 300, 112], [[0, 0], [16, 0], [16, 4], [0, 6]], "chrome", axis="z", copies=[[250, 0, 0], [125, 140, 0]])
# ---- front: left fixed panel (small recess marks), door with the teal trim, hinge strip, right panel + logo
d.slab("lp-mark", "front", ring(rr(60, 618, 240, 650, 14), rr(68, 626, 232, 642, 8)), [DP - 2, DP + 2], "line", r=1,
       copies=[[0, -560, 0]])
DX0, DX1, DY0, DY1, DR = 300, 880, 200, 712, 90
door = f"M {DX0} {DY1} L {DX0} {DY0 + DR} Q {DX0} {DY0} {DX0 + DR} {DY0} L {DX1 - DR} {DY0} Q {DX1} {DY0} {DX1} {DY0 + DR} L {DX1} {DY1} Z"
fr = 18
frame = (f"M {DX0 - fr} {DY1} L {DX0 - fr} {DY0 + DR} Q {DX0 - fr} {DY0 - fr} {DX0 + DR} {DY0 - fr} L {DX1 - DR} {DY0 - fr} "
         f"Q {DX1 + fr} {DY0 - fr} {DX1 + fr} {DY0 + DR} L {DX1 + fr} {DY1} Z")
d.slab("door-frame", "front", frame, [DP - 6, DP + 5], "teal", r=4)
d.slab("door", "front", door, [DP - 4, DP + 10], "shell", r=5)
d.slab("door-inner", "front", P(rr(DX0 + 30, DY0 + 30, DX1 - 30, DY1 - 40, 70)), [DP + 9, DP + 12], "plastic#f1f3f5", r=2)
d.box("hinge", [DX1 + 14, 280, DP - 2, DX1 + 36, DY1 - 10, DP + 14], "shell", r=6)
d.slab("panel-line", "front", ring(rr(960, 210, 1230, 670, 30), rr(974, 224, 1216, 656, 22)), [DP - 2, DP + 3], "line", r=1)
d.slab("rp-mark", "front", ring(rr(960, 50, 1230, 130, 20), rr(970, 60, 1220, 120, 14)), [DP - 2, DP + 2], "line", r=1)
brand_cn(d, "logo", 985, 590, DP + 1, 30, "blue")
d.decal("door-label", [800, 630, DP + 12.5], [70, 90], "front", "plastic#e4e7ea", soft=True)
# teal swing arm across the door top (hub at its left), red lever, diagonal rod from above the hub to the door middle
d.tube("arm", [[340, 625, DP + 30], [850, 650, DP + 30]], 26, "teal")
d.lathe("arm-hub", [350, 625, DP + 10], [[0, 0], [28, 0], [28, 30], [0, 30]], "teal", axis="z")
d.lathe("arm-end", [850, 650, DP + 10], [[0, 0], [16, 0], [16, 24], [0, 24]], "teal", axis="z")
d.lathe("knob-red", [350, 625, DP + 40], [[0, 0], [14, 0], [14, 14], [0, 18]], "red", axis="z")
d.cyl("lever-red", [410, 628, DP + 44], [418, 680, DP + 44], 14, "red")
d.tube("rod", [[330, 780, DP + 22], [450, 560, DP + 26], [560, 340, DP + 26]], 22, "teal", bend=40)
d.box("rod-fork", [540, 300, DP + 14, 585, 345, DP + 38], "teal", r=8, rot=rot("z", 25, [562, 322, DP + 26]))
# teal curtain rail over the basin (front → back) with small hooks under it
d.tube("top-rail", [[680, T, 800], [680, T + 40, 800], [680, T + 40, 260], [680, T, 260]], 24, "teal", bend=25)
d.box("hook", [676, T, 700, 684, T + 30, 708], "chrome", r=2, soft=True, repeat=rep(5, [0, 0, -95]))
# ---- left end: big recessed panel with a horizontal handle moulding, low recess band
d.slab("side-panel", "side", ring(rr(110, 240, 750, 650, 60), rr(126, 256, 734, 634, 50)), [-3, 2], "line", r=1)
d.box("side-handle", [-12, 290, 140, 6, 360, 720], "shell", r=16)
d.slab("side-low", "side", ring(rr(100, 50, 760, 120, 20), rr(110, 60, 750, 110, 14)), [-3, 2], "line", r=1)
# ---- rim: valve cluster + blue lever (back-left), flush key strip, black cap at the front-left corner
valve(d, "valve1", 70, T - 2, 90, disc=60, lever=60, ang=90)
valve(d, "valve2", 120, T - 2, 90, disc=60, lever=55, ang=90)
d.cyl("lever-blue", [95, T + 50, 90], [95, T + 75, 150], 18, "blue")
d.box("keys", [60, T - 2, 210, 150, T + 4, 330], "plastic#e9edf1", r=4)
d.box("key", [80, T + 2, 222, 130, T + 6, 240], "plastic#cfd6dd", r=3, soft=True, repeat=rep(4, [0, 0, 27]))
d.lathe("cap", [90, T - 2, 760], [[0, 0], [40, 0], [40, 36], [34, 40], [0, 40]], "dark")
# ---- transfer beam across the depth near the right end
BX0, BX1 = 1080, 1142
d.box("beam", [BX0, 850, 80, BX1, 1000, 760], "teal", r=10)
d.box("beam-rail", [BX0 - 8, 895, 100, BX0, 955, 740], "metal#c4c8cc", r=3)
d.slab("wedge", "side", "M 650 720 L 840 720 L 840 760 L 760 850 L 690 850 Z", [BX0 - 30, BX1 + 60], "grey", r=10)
d.box("beam-end", [BX0 - 6, 840, 20, BX1 + 6, 1000, 150], "teal", r=12)
d.box("plate", [BX0 - 14, 860, 40, BX0 - 4, 990, 130], "grey", r=4)
# grey L arm from the beam's back end leftwards over the basin, red pin, loop handle
d.bar("arm-h", [BX0 - 10, 930, 85], [700, 930, 85], [80, 70], "grey", r=12)
d.bar("arm-v", [715, 960, 85], [740, 780, 85], [70, 70], "grey", r=12)
d.cyl("pin", [690, 935, 85], [640, 935, 85], 20, "red")
d.tube("loop", [[700, 900, 110], [670, 840, 130], [680, 760, 130], [720, 740, 110]], 16, "grey", bend=20)
d.save()
