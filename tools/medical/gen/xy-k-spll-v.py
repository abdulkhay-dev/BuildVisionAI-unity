from p1lib import *
d = D("xy-k-spll-v", [560, 560, 1300], {
  "shell": "plastic#f2f3f5", "band": "plastic#5b6068", "grey": "plastic#8a9099", "lgrey": "plastic#c4c8ce",
  "black": "gloss#111214", "blue": "gloss#3a8be0", "dark": "plastic#2b2e33"})
# white base frame with a grey lower edge and four big castors
# white frame base on a grey lower edge, notched between the castors on every side (review)
N, L = 30, 130
bp = [(10, 20), (10 + L, 20), (10 + L, 20 + N), (550 - L, 20 + N), (550 - L, 20), (550, 20), (550, 20 + L), (550 - N, 20 + L),
      (550 - N, 540 - L), (550, 540 - L), (550, 540), (550 - L, 540), (550 - L, 540 - N), (10 + L, 540 - N), (10 + L, 540), (10, 540),
      (10, 540 - L), (10 + N, 540 - L), (10 + N, 20 + L), (10, 20 + L)]
d.slab("base-edge", "top", rpoly(bp, 14), [100, 126], "lgrey", r=8)
d.slab("base", "top", rpoly(bp, 14), [122, 158], "shell", r=10)
for k, (x, z) in enumerate(((60, 70), (500, 70), (60, 490), (500, 490))):
    d.caster(f"castor-{k}", [x, 0, z - 10], 90, "rubber#e3e5e8")
# cabinet column: dark band on the left side with a vent at its foot, drawers with grey pulls, logo
d.box("cabinet", [130, 160, 130, 430, 860, 450], "shell", r=14)
# the whole left side of the column is dark grey, with a vent grille at its foot (review: was a narrow band)
d.box("band", [127, 165, 136, 133, 855, 444], "band", r=4)
d.box("band-vent", [126, 175, 190, 128.5, 177.5, 400], "plastic#d0d4d8", repeat={"n": 16, "step": [0, 7, 0]})
for i, (y0, y1) in enumerate(((680, 800), (500, 630))):
    d.slab(f"drawer-{i}", "front", f"M 175 {y0} L 405 {y0} L 405 {y1} L 175 {y1} Z M 179 {y0+4} L 179 {y1-4} L 401 {y1-4} L 401 {y0+4} Z",
           [449, 451.5], "grey", r=0.5)
    d.box(f"pull-{i}", [255, y1 - 42, 446, 325, y1 - 18, 452], "grey", r=5)
text(d, "logo", "Sunnyou 翔宇", [262, 292, 450.5], 15, "plastic#4a4f57", stroke=2.4)
# thin shelf, wider than the column
d.box("shelf", [5, 860, 150, 555, 872, 460], "shell", r=6)
# head: white rounded box, grey recess and vent slots on the left side, blue light
d.box("head", [70, 872, 70, 490, 1115, 460], "shell", r=40)
d.slab("recess", "side", "M 200 900 L 350 900 L 350 970 Q 350 1010 310 1010 L 240 1010 Q 200 1010 200 970 Z", [66, 72], "grey", r=2)
d.box("slots", [66, 1035, 205, 72, 1060, 210], "dark", repeat={"n": 11, "step": [0, 0, 13]})
d.box("light", [66, 1018, 230, 72, 1026, 320], "blue", r=3)
# big screen at the front, tilted back 20 deg (print)
Q = [300, 1000, 474]
d.screen("screen", [150, 878, 462, 482, 1128, 487], "black", r=26, face="front", bezel=3,
         print="med_xy-k-spll-v_screen", rot=rot("x", -18, Q))
# the crop shows the yawed tablet as a skewed quad with the white head around it: cover the outside with the
# black bezel so the tablet reads as one black rounded frame (review)
X0, X1, Y0, Y1 = 153, 479, 881, 1125
def uv(u, v): return f"{X0 + u * (X1 - X0):.1f} {Y1 - v * (Y1 - Y0):.1f}"
TR = [(0, 0), (1, 0), (1, 1), (0.96, 1), (0.977, 0.9), (0.96, 0.8), (0.923, 0.6), (0.881, 0.4), (0.834, 0.2), (0.589, 0.1),
      (0.262, 0.06), (0.045, 0.03), (0, 0.025)]
BL = [(0, 0.57), (0.006, 0.6), (0.047, 0.8), (0.113, 0.9), (0.436, 0.93), (0.96, 0.955), (0.96, 1), (0, 1)]
for nm, poly in (("mask-tr", TR), ("mask-bl", BL)):
    d.slab(nm, "front", "M " + " L ".join(uv(u, v) for u, v in poly) + " Z", [488.7, 489.4], "black", r=0.3, rot=rot("x", -18, Q))
# on top at the back: holder tray, gel bottle, handpieces with cables
d.box("tray", [80, 1115, 150, 460, 1130, 330], "lgrey", r=12)
d.lathe("bottle", [270, 1130, 240], [[0, 0], [44, 0], [45, 30], [45, 130], [40, 150], [22, 165], [16, 168], [16, 178], [6, 190], [0, 192]], "shell")
d.lathe("bottle-band", [270, 1160, 240], [[46, 0], [46, 95], [0, 95], [0, 0]], "blue")
d.cyl("hp1", [120, 1110, 230], [120, 1230, 230], 40, "lgrey")
d.cyl("hp1-cap", [120, 1230, 230], [120, 1250, 230], 30, "dark")
d.tube("hp1-cable", [[120, 1245, 230], [110, 1285, 200], [90, 1270, 160], [85, 1180, 140]], 7, "dark", bend=30, soft=True)
d.cyl("hp2", [185, 1110, 210], [185, 1200, 225], 32, "dark")
d.sphere("hp2-head", [185, 1215, 230], 56, "lgrey")
d.tube("hp2-cable", [[185, 1150, 200], [175, 1260, 170], [160, 1250, 150], [150, 1160, 140]], 6, "dark", bend=30, soft=True)
d.cyl("hp3", [385, 1110, 220], [385, 1180, 220], 30, "lgrey")
d.lathe("hp3-head", [385, 1180, 220], [[0, 0], [40, 0], [42, 10], [38, 22], [0, 24]], "lgrey")
d.sphere("hp3-dot", [385, 1204, 220], 10, "dark", copies=[[-16, -2, 0], [16, -2, 0]])
d.save()
