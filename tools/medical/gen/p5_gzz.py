"""Integrated physiotherapy system XY-K-GZZ-III: workstation cart (5-spoke base, three white modules, keyboard tray,
monitor), cable hanger at the left, shockwave handpiece on a long arm at the right. Writes only xy-k-gzz-iii.json."""
from p5lib import *
import math

W, DP, H = 650, 600, 1600
CX, BZ = W / 2, 300
d = D("xy-k-gzz-iii", [W, DP, H],
      {"base": "plastic#3a3f46", "mod": "gloss#f4f5f6", "gap": "plastic#2b2e33", "blue": "gloss#2f8fd8",
       "tray": "plastic#454a51", "rim": "metal#b9bdc2", "black": "gloss#111214", "white": "plastic#f2f3f4",
       "wheel": "rubber#4a4e55", "arm": "plastic#555a61", "silver": "metal#c3c6cb"})
# ---- X base (4 flat spokes to the front/back corners, as in the photo), dark block hanging under the centre, castors
d.slab("base", "top", star_outline(CX, BZ, 4, 455, 200, 100, a0=45), [118, 172], "base", r=14)
d.slab("base-top", "top", star_outline(CX, BZ, 4, 440, 170, 80, a0=45), [171, 176], "base", r=4)
d.box("base-block", [CX - 78, 92, BZ - 70, CX + 78, 120, BZ + 70], "base", r=6)
for i, (x, z) in enumerate(spoke_tips(CX, BZ, 4, 405, a0=45)):
    d.add(f"castor{i}", "caster", "wheel", at=[round(x), 0, round(z)], d=90)
    d.cyl(f"swivel{i}", [x, 92, z], [x, 120, z], 44, "plastic#8a8f96")
# ---- column
d.box("column", [CX - 54, 176, 205, CX + 54, 990, 295], "base", r=8)
# ---- three white modules with dark gaps; blue line at the lower right of each front
Z0, Z1 = 200, 592
mods = [("m-bot", 400, 532), ("m-mid", 546, 734), ("m-top", 748, 946)]
for id_, y0, y1 in mods:
    d.box(id_, [95, y0, Z0, 555, y1, Z1], "mod", r=20)
    d.decal(id_ + "-line", [470, y0 + 36, Z1 + 0.4], [108, 4.5], "front", "blue", soft=True)
d.box("gaps", [110, 528, Z0 + 20, 540, 750, Z1 - 20], "gap", r=4)
d.decal("logo", [132, 918, Z1 + 0.4], [18, 18], "front", "blue", soft=True)
d.decal("logo-t", [170, 918, Z1 + 0.4], [44, 8], "front", "plastic#8fb7e2", soft=True)
d.box("badge", [285, 924, Z1 - 2, 365, 938, Z1 + 1.5], "plastic#b8bcc2", r=3)
d.box("badge-l", [292, 929, Z1 + 1, 358, 931, Z1 + 2], "plastic#7d8288", soft=True)
# middle module: dark trapezoid side wings
d.slab("wing", "front", poly([(97, 696), (22, 664), (22, 562), (97, 562)]), [Z0 + 30, Z1 - 40], "base", r=8, mirror="x")
# ---- keyboard tray with silver rim; keyboard, mouse; dark box under it at the right
d.slab("tray", "top", rrect(86, 190, W - 78, DP, 26), [982, 1002], "tray", r=5)
d.slab("tray-rim", "top", rrect(86, 190, W - 78, DP, 26) + " " + rrect(96, 200, W - 88, DP - 10, 18), [1000, 1008], "rim", r=2)
d.box("keyboard", [140, 1002, 470, 450, 1016, 585], "white", r=6)
d.box("keys", [152, 1015, 482, 438, 1018, 573], "plastic#d9dbde", r=2, soft=True)
d.sphere("mouse", [500, 1012, 540], None, "plastic#f4f4f4", radii=[30, 13, 44])
d.sphere("mouse-r", [500, 1016, 520], None, "gloss#d8322a", radii=[22, 9, 20])
d.box("under", [470, 948, 300, 560, 982, 520], "base", r=5)
# ---- monitor on a rectangular frame neck
d.slab("neck", "front", rrect(271, 1002, 379, 1110, 6) + " " + rrect(287, 1018, 363, 1088, 4), [300, 322], "base", r=3)
d.box("mback", [225, 1150, 318, 425, 1340, 338], "black", r=10)
d.add("monitor", "screen", "black", box=[70, 1092, 334, 580, 1392, 358], r=6, face="front", bezel=12,
      print="med_xy-k-gzz-iii_screen")
# ---- left: dark rod with a white 3-loop cable hanger, bracket at the top module
d.box("rod-br", [58, 880, 240, 97, 910, 280], "base", r=4)
d.bar("rod2", [74, 1000, 262], [74, 1340, 262], [12, 12], "base", r=4)
d.bar("rod", [56, 790, 260], [56, 1362, 260], [22, 22], "base", r=4)
d.box("rod-cup", [34, 812, 236, 92, 868, 284], "base", r=6)
pts = []
for k in range(41):
    x = 48 - 4.75 * k
    pts.append([round(x, 1), round(1282 + 32 * math.sin(k / 40 * 3 * 2 * math.pi - math.pi / 2), 1), 260])
d.tube("hanger", pts, 9, "plastic#eceef0", bend=6)
d.cyl("hanger-end", pts[-1], [pts[-1][0] - 4, pts[-1][1], 260], 12, "plastic#eceef0")
# ---- right: clamp, long arm (dark lower segment with a yellow label, white upper), shockwave handpiece
d.box("clamp", [596, 900, 330, 640, 1010, 392], "base", r=8)
A0, A1, A2 = [610, 962, 362], [704, 1165, 362], [866, 1440, 362]
d.bar("arm-lo", A0, A1, [60, 54], "arm", r=14)
d.bar("arm-label", [A0[0] + (A1[0] - A0[0]) * 0.45, A0[1] + (A1[1] - A0[1]) * 0.45, 362],
      [A0[0] + (A1[0] - A0[0]) * 0.8, A0[1] + (A1[1] - A0[1]) * 0.8, 362], [62, 56], "gloss#f2c419", r=14)
d.bar("arm-hi", A1, A2, [46, 42], "white", r=12)
d.sphere("arm-end", A2, 52, "arm")
d.bar("hp-link", A2, [874, 1522, 362], [34, 30], "arm", r=8)
d.cyl("hp-body", [868, 1530, 362], [1000, 1560, 362], 54, "silver")
d.cyl("hp-fins", [878, 1532, 362], [912, 1540, 362], 60, "plastic#9da2a8", sides=16)
d.cyl("hp-nose", [1000, 1560, 362], [1044, 1570, 362], 24, "metal#d8dadd")
d.cyl("hp-cap", [860, 1528, 362], [870, 1530, 362], 44, "plastic#3a3d42")
d.box("hp-grip", [906, 1440, 340, 948, 1532, 384], "plastic#8d9298", r=10)
d.tube("hp-cable", [[924, 1442, 362], [900, 1400, 372], [760, 1180, 392], [650, 990, 400]], 10, "plastic#9a9fa6",
       bend=80, soft=True)
# ---- white probe holder cup at the lower right of the bottom module
d.box("cup-br", [430, 402, Z1 - 4, 450, 420, Z1 + 26], "rim", r=3)
d.lathe("cup", [440, 320, Z1 + 30], [[0, 0], [22, 0], [26, 70], [28, 92], [24, 92], [20, 6], [0, 6]], "white")
d.save()
