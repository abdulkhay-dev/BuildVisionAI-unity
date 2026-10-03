# XYRT-118 waist twister (children): yellow T base, orange twisting disc, yellow/red post, blue open ring handle
from pd2_lib import *

W, D, H = 380, 520, 1000
C = W / 2
d = Design("xyrt-118", [W, D, H], {"yel": YEL, "red": RED, "blue": BLU, "blk": BLK,
                                          "orange": "plastic#e8701a", "grey": "plastic#5a5d62"})
# base: tube along the depth, short cross bars with black caps at both ends
Y = 22
capped_bar_x(d, "bar-rear", C - 150, C + 150, Y, 30, 40, "yel", "blk")
capped_bar_x(d, "bar-front", C - 150, C + 150, Y, 490, 40, "yel", "blk")
d.cyl("spine", [C, Y, 30], [C, Y, 490], 40, "yel")
# twisting disc on a short stem over the spine
ZD = 315
d.cyl("disc-stem", [C, Y, ZD], [C, 50, ZD], 50, "grey")
d.lathe("disc-under", [C, 42, ZD], [[0, 0], [118, 0], [127, 4], [128, 18], [0, 18]], "grey")
d.lathe("disc", [C, 60, ZD], [[0, 0], [128, 0], [131, 5], [130, 14], [124, 18], [0, 18]], "orange")
d.lathe("disc-hub", [C, 78, ZD], [[0, 0], [22, 0], [20, 4], [0, 5]], "blk")
d.lathe("disc-ring", [C, 77.5, ZD], [[70, 0], [76, 0], [76, 1.2], [70, 1.2]], "plastic#d0621a", soft=True)
# post near the rear bar
ZP = 105
d.cyl("post-sleeve", [C, Y, ZP], [C, 80, ZP], 44, "yel")
d.cyl("post", [C, 70, ZP], [C, 605, ZP], 32, "yel")
d.cyl("post-foam", [C, 140, ZP], [C, 482, ZP], 46, "red")
# two grey adjustment bolts on the right side of the yellow top part
d.cyl("post-bolt", [C + 15, 520, ZP], [C + 24, 520, ZP], 11, "metal#9a9da2", soft=True, copies=[[0, 36, 0]])
# blue foam ring handle, open at the top a bit right of the middle
R, RY, YC = 166, 180, 778
ring = arc_xy(C, YC, ZP, R, 102, 70 + 360, n=44, ry=RY)
d.tube("ring", ring, 44, "blue")
for k, p in enumerate((ring[0], ring[-1])):   # rounded foam ends
    d.sphere(f"ring-end{k}", p, 44, "blue")
d.save()
