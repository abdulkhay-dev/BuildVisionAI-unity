# XY-88 ADL kitchen: white wall worktop on a wood-clad pedestal, black glass 2-burner hob, white sink with a
# chrome tap, 4 black knobs, lime-green wall cabinet — other-1
import math
from o_lib import *
W, DP, H = 1700, 620, 1410
d = D("xy-88", [W, DP, H], {
    "white": "plastic#f4f4f2", "glass": "gloss#141416", "iron": "black#1b1b1c", "chrome": "chrome", "wood": "wood#cdb48e",
    "green": "plastic#bcd63d", "seam": "plastic#7f9a22", "blk": "plastic#151517", "brass": "gloss#d9b23a"})
TY = 680
# sink hole on the right
SX0, SX1, SZ0, SZ1 = 870, 1560, 110, 520
d.slab("top", "top", rr(0, 0, W, DP, 12) + " " + rr(SX0, SZ0, SX1, SZ1, 50), [TY - 30, TY], "white", r=6)
d.box("apron", [0, TY - 112, DP - 34, W, TY - 28, DP], "white", r=6)
d.box("apron-back", [0, TY - 112, 0, W, TY - 28, 30], "white", r=4)
# sink basin: bottom and walls inside the hole
d.box("basin-bot", [SX0, TY - 108, SZ0, SX1, TY - 96, SZ1], "white", r=6)
d.box("basin-wl", [SX0, TY - 108, SZ0, SX0 + 12, TY - 28, SZ1], "white", r=4, copies=[[SX1 - SX0 - 12, 0, 0]])
d.box("basin-wb", [SX0, TY - 108, SZ0, SX1, TY - 28, SZ0 + 12], "white", r=4, copies=[[0, 0, SZ1 - SZ0 - 12]])
d.cyl("drain", [1215, TY - 95, 315], [1215, TY - 94, 315], 50, "chrome", soft=True)
# tap at the back of the sink
d.cyl("tap-base", [1215, TY, 70], [1215, TY + 50, 70], 40, "chrome")
d.tube("tap-spout", [[1215, TY + 45, 70], [1215, TY + 105, 78], [1215, TY + 105, 185], [1215, TY + 75, 205]], 20, "chrome", bend=50)
d.box("tap-lever", [1233, TY + 40, 45, 1248, TY + 54, 100], "chrome", r=5)
# black glass hob with 2 cast-iron pan supports and burners, small brass knob
d.box("hob", [60, TY, 120, 890, TY + 7, 540], "glass", r=8)
for i, bx in enumerate((270, 660)):
    d.lathe(f"burner{i}", [bx, TY + 7, 330], [[0, 0], [52, 0], [52, 16], [40, 22], [0, 22]], "iron")
    d.lathe(f"cap{i}", [bx, TY + 29, 330], [[0, 0], [26, 0], [26, 6], [0, 6]], "brass")
    ring = [[bx + 120 * math.cos(math.radians(a)), TY + 40, 330 + 120 * math.sin(math.radians(a))] for a in range(0, 361, 20)]
    d.tube(f"grid{i}", ring, 9, "iron")
    for k in range(5):
        a = math.radians(k * 72 + 18)
        d.bar(f"arm{i}-{k}", [bx + 62 * math.cos(a), TY + 40, 330 + 62 * math.sin(a)],
              [bx + 160 * math.cos(a), TY + 40, 330 + 160 * math.sin(a)], [10, 22], "iron", r=2)
        d.cyl(f"foot{i}-{k}", [bx + 150 * math.cos(a), TY + 7, 330 + 150 * math.sin(a)],
              [bx + 150 * math.cos(a), TY + 40, 330 + 150 * math.sin(a)], 10, "iron")
d.cyl("brass-knob", [840, TY, 80], [840, TY + 18, 80], 36, "brass")   # behind the hob's right end (photo)
# 4 black knobs on the apron between hob and sink
d.cyl("knob", [940, TY - 70, DP], [940, TY - 70, DP + 16], 24, "blk", repeat=rep(4, [40, 0, 0]))
d.box("knob-grip", [936, TY - 82, DP + 10, 944, TY - 58, DP + 22], "blk", r=2, repeat=rep(4, [40, 0, 0]))
# wood-clad pedestal leg and the chrome drain pipe
d.box("pedestal", [740, 0, 180, 925, TY - 112, 500], "wood", r=3)
d.cyl("drain-pipe", [1215, TY - 108, 315], [1215, 360, 315], 42, "chrome")
# lime-green wall cabinet: 2 doors with chrome bar handles, top cornice, bottom ledge
CY0, CY1 = 810, H
X0, X1 = 360, 1270
d.box("cab", [X0, CY0 + 16, 0, X1, CY1 - 22, 300], "green", r=4)
d.box("cornice", [X0 - 10, CY1 - 24, 0, X1 + 10, CY1, 320], "green", r=10)
d.box("ledge", [X0 - 4, CY0, 0, X1 + 4, CY0 + 18, 312], "green", r=6)
d.box("seam", [(X0 + X1) / 2 - 2, CY0 + 20, 299, (X0 + X1) / 2 + 2, CY1 - 26, 302], "seam", soft=True)
for i, x in enumerate(((X0 + X1) / 2 - 26, (X0 + X1) / 2 + 26)):
    d.tube(f"handle{i}", [[x, 1060, 300], [x, 1060, 322], [x, 1190, 322], [x, 1190, 300]], 10, "chrome", bend=8)
d.save()
