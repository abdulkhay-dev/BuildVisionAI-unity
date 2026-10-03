from p1lib import *
d = D("xy-k-czld-i", [620, 700, 1450], {
  "shell": "gloss#f4f5f7", "plate": "plastic#4a4f56", "arc": "plastic#a3a9b0", "black": "gloss#141516",
  "rail": "plastic#e1e4e8", "collar": "plastic#9aa0a8"})
# two-tier white base with the dark grey top plate and its light arc lines
# review: taller pillow base, plan corners rounded big (slabs)
d.slab("base", "top", rpoly([(0, 100), (620, 100), (620, 700), (0, 700)], 120), [0, 92], "shell", r=34)
d.slab("rim", "top", rpoly([(14, 112), (606, 112), (606, 688), (14, 688)], 105), [86, 112], "shell", r=10)
d.slab("plate", "top", rpoly([(34, 132), (586, 132), (586, 668), (34, 668)], 90), [104, 118], "plate", r=6)
for i, rr in enumerate((150, 230, 310, 390)):
    d.tube(f"arc-a{i}", arc(35, 668, rr, rr, -90, 0, 118.5, 14), 5, "arc", soft=True)
for i, rr in enumerate((90, 160, 230)):
    d.tube(f"arc-b{i}", arc(585, 420, rr, rr, 90, 270, 118.5, 18), 5, "arc", soft=True)
# white flat column at the rear with black side faces, black vertical lettering and the logo
d.box("column", [235, 100, 30, 385, 1255, 125], "shell", r=14)
d.box("side", [231, 102, 36, 239, 1250, 119], "black", r=3, mirror="x")
# "XIANGYU MEDICAL" read downwards, letters' tops to the right (review: was blocks)
text(d, "txt", "XIANGYU MEDICAL", [295, 765, 125], 30, "black", along=(0, -1), stroke=3.6)
d.cyl("logo", [262, 1140, 125], [262, 1140, 126.5], 20, "gloss#1d3f78")
d.decal("logo-text", [298, 1142, 125], [40, 9], "gloss#1d3f78", soft=True)
d.decal("logo-sub", [298, 1132, 125], [36, 3], "gloss#1d3f78", soft=True)
# black wedge console with the sloped touch display and three keys
d.slab("console", "side", "M 25 1235 L 140 1235 L 200 1305 Q 205 1318 192 1322 L 60 1352 Q 25 1356 25 1330 Z", [205, 415], "black", r=10)
A = math.degrees(math.atan(30 / 132.0))
Q = [310, 1337, 126]
d.screen("display", [238, 1334, 72, 382, 1341, 176], "black", r=4, face="top", bezel=10, rot=rot("x", A, Q))
for i, x in enumerate((270, 310, 350)):
    d.sphere(f"key-{i}", rotx([x, 1342, 185], A, Q), 12, "plastic#8a9099")
# light-grey inverted-U handrail with a crossbar fixed to the column front
d.tube("rail", [[85, 980, 165], [85, 1420, 140], [535, 1420, 140], [535, 980, 165]], 30, "rail", bend=85)
d.cyl("crossbar", [85, 1190, 152], [535, 1190, 152], 30, "rail")
d.cyl("collar", [222, 1190, 152], [240, 1190, 152], 42, "collar", mirror="x")
d.save()
