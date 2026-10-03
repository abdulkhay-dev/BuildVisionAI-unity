"""Transcranial magnetic stimulator XY-K-JLC-D: workstation cart (5-spoke base, two host boxes, tray, PC monitor),
coil on an articulated chrome arm at the left. Writes only xy-k-jlc-d.json."""
from p5lib import *

W, DP, H = 680, 630, 1680
CX, BZ = W / 2, 330
d = D("xy-k-jlc-d", [W, DP, H],
      {"base": "plastic#5a5e64", "col": "plastic#3f4349", "box": "plastic#f3f4f5", "side": "plastic#e3e5e8",
       "tray": "plastic#6b6f75", "black": "gloss#121315", "blue": "gloss#2f7fd8", "green": "gloss#3ad13a",
       "chrome": "chrome", "hose": "plastic#8d9298", "coil": "gloss#f2f3f4", "knob": "plastic#1d1e21",
       "wheel": "rubber#3a3d42", "hub": "plastic#e9eaec"})
# ---- X base (4 flat tapering spokes at 45 deg, both photos), small plate under the column, castors at the tips
BZ = 315
d.slab("base", "top", star_outline(CX, BZ, 4, 470, 210, 112, a0=45), [128, 186], "base", r=14)
d.slab("base-top", "top", star_outline(CX, BZ, 4, 455, 180, 92, a0=45), [185, 190], "base", r=4)
for i, (x, z) in enumerate(spoke_tips(CX, BZ, 4, 418, a0=45)):
    d.add(f"castor{i}", "caster", "wheel", at=[round(x), 0, round(z)], d=100)
    d.cyl(f"wcap{i}", [x - 17, 50, z], [x + 17, 50, z], 66, "hub", soft=True)
    d.cyl(f"swivel{i}", [x, 100, z], [x, 130, z], 46, "hub")
# ---- column at the back
d.box("column", [CX - 50, 186, 170, CX + 50, 990, 260], "col", r=8)
d.box("col-plate", [CX - 80, 186, 150, CX + 80, 200, 280], "col", r=6)
# ---- two host boxes: white front, light-grey perforated sides
ZB0, ZB1 = 250, 628
def host(id_, y0, y1):
    d.box(id_, [70, y0, ZB0, 610, y1, ZB1], "box", r=8)
    d.box(id_ + "-side", [68, y0 + 18, ZB0 + 30, 612, y1 - 18, ZB1 - 60], "side", r=4)
    dots = [[0, 14 * k, 0] for k in range(1, (y1 - y0 - 60) // 14)]
    d.cyl(id_ + "-dot", [67.6, y0 + 30, ZB0 + 50], [68.6, y0 + 30, ZB0 + 50], 6, "plastic#8d9197", sides=8,
          repeat=rep(20, [0, 0, 14]), copies=dots, mirror="x", soft=True)
host("upper", 702, 940)
host("lower", 452, 690)
F = ZB1 + 0.5
# upper front: logo, title, column of 4 displays, keys, start key, LEDs, socket, coil plug
d.decal("u-logo", [118, 905, F], [22, 22], "front", "blue", soft=True)
d.decal("u-title", [196, 880, F], [120, 13], "front", "plastic#3a3d42", soft=True)
d.decal("u-sub", [196, 862, F], [110, 5], "front", "plastic#55595f", soft=True)
for k in range(4):
    d.decal(f"disp{k}", [310, 892 - 34 * k, F], [56, 28], "front", "gloss#0f1b2b", soft=True)
    d.decal(f"dispv{k}", [320, 892 - 34 * k, F + 0.2], [26, 10], "front", "green" if k else "gloss#f2f2f2", soft=True)
d.cyl("u-key", [370, 850, ZB1], [370, 850, ZB1 + 5], 14, "plastic#2a2c30", copies=[[0, -24, 0], [0, -48, 0]])
d.cyl("start", [528, 900, ZB1], [528, 900, ZB1 + 6], 36, "gloss#f7f7f7")
d.cyl("start-ring", [528, 900, ZB1], [528, 900, ZB1 + 2], 44, "plastic#c5c8cc")
d.cyl("led", [478, 912, ZB1], [478, 912, ZB1 + 2], 6, "green", copies=[[0, -18, 0]])
d.cyl("u-sock", [500, 770, ZB1], [500, 770, ZB1 + 5], 24, "plastic#2a2c30")
d.cyl("u-sock-in", [500, 770, ZB1 + 5], [500, 770, ZB1 + 6], 10, "metal#b0b4ba")
d.decal("u-text", [430, 722, F], [300, 5], "front", "plastic#8a8e94", soft=True, copies=[[0, -10, 0]])
d.box("plug", [130, 742, ZB1, 205, 792, ZB1 + 40], "box", r=8)
# lower front: logo, two elbow fittings, 4 LEDs, text
d.decal("l-logo", [118, 664, F], [20, 20], "front", "blue", soft=True)
d.decal("l-title", [170, 664, F], [60, 8], "front", "blue", soft=True)
for k, y in enumerate((600, 520)):
    d.cyl(f"fit{k}", [130, y, ZB1], [130, y, ZB1 + 22], 26, "metal#a8acb2")
    d.lathe(f"fit-r{k}", [130, y, ZB1 + 22], [[0, 0], [16, 0], [16, 10], [0, 10]], "plastic#6e7278", axis="z")
d.cyl("l-led", [560, 640, ZB1], [560, 640, ZB1 + 2], 6, "green", copies=[[0, -20, 0], [0, -40, 0], [0, -60, 0]])
d.decal("l-text", [430, 472, F], [300, 5], "front", "plastic#8a8e94", soft=True, copies=[[0, -10, 0]])
# ---- tray with a raised lip; keyboard, mouse, E-stop
d.slab("tray", "top", rrect(36, 212, W - 36, DP, 30), [978, 1000], "tray", r=6)
d.slab("tray-lip", "top", rrect(36, 212, W - 36, DP, 30) + " " + rrect(52, 228, W - 52, DP - 16, 18), [999, 1010],
       "tray", r=3)
d.box("keyboard", [150, 1000, 480, 470, 1016, 600], "box", r=6)
d.box("keys", [162, 1015, 492, 458, 1018, 588], "plastic#d9dbde", r=2, soft=True)
d.sphere("mouse", [528, 1012, 548], None, "box", radii=[30, 13, 46])
d.box("estop-base", [568, 1000, 280, 612, 1022, 324], "gloss#f2c419", r=5)
d.lathe("estop", [590, 1022, 302], [[0, 0], [12, 0], [12, 8], [21, 10], [22, 20], [16, 25], [0, 26]], "gloss#d42a22")
# ---- PC monitor on a silver V stand
d.bar("mstand-a", [215, 1008, 420], [318, 1130, 362], [24, 8], "metal#c4c7cc", r=3)
d.bar("mstand-b", [465, 1008, 420], [362, 1130, 362], [24, 8], "metal#c4c7cc", r=3)
d.box("mfoot", [195, 1000, 405, 235, 1008, 440], "metal#c4c7cc", r=3, copies=[[250, 0, 0]])
d.box("mneck", [300, 1125, 345, 380, 1180, 362], "metal#c4c7cc", r=4)
d.box("mback", [240, 1180, 330, 440, 1400, 350], "black", r=10)
d.add("monitor", "screen", "black", box=[20, 1125, 345, 660, 1462, 368], r=6, face="front", bezel=10,
      print="med_xy-k-jlc-d_screen")
# ---- coil arm at the left (photo _2): dark bracket under the tray's left end, chrome rod up-left to a black T lock
# knob, a short chrome link to a ball joint, a horizontal chrome bar to the clamp hub (knurled knob pointing left)
# holding the white coil stem; the figure-8 coil stands ~300 mm left of the cart
ZA = 420
J1, J2, J3, HB = [16, 990, ZA], [-84, 1296, ZA], [-160, 1384, ZA], [-262, 1384, ZA]
d.box("arm-mount", [-14, 940, ZA - 32, 40, 1000, ZA + 32], "knob", r=6)
d.box("arm-mount2", [36, 960, ZA - 20, 72, 990, ZA + 20], "knob", r=4)
d.cyl("arm-rod", J1, J2, 24, "chrome")
d.sphere("joint1", J2, 40, "knob")
d.cyl("knob1-shaft", J2, [J2[0] - 40, J2[1] - 16, J2[2] + 30], 10, "knob")
d.bar("knob1", [J2[0] - 46, J2[1] - 18, J2[2] + 2], [J2[0] - 46, J2[1] - 18, J2[2] + 58], [12, 12], "knob", r=5)
d.cyl("arm2", J2, J3, 24, "chrome")
d.cyl("arm2-sleeve", [J2[0] - 22, J2[1] + 25, ZA], [J2[0] - 44, J2[1] + 51, ZA], 28, "gloss#2f6fd0")
d.sphere("joint2", J3, 42, "chrome")
d.cyl("arm3", J3, HB, 26, "chrome")
d.lathe("clamp", [HB[0], HB[1] - 34, HB[2]], [[0, 0], [26, 0], [28, 10], [28, 58], [26, 68], [0, 68]], "chrome")
d.cyl("clamp-knob", [HB[0] - 26, HB[1], HB[2]], [HB[0] - 72, HB[1], HB[2]], 44, "metal#b9bdc2", sides=14)
d.cyl("clamp-knob2", [HB[0] - 72, HB[1], HB[2]], [HB[0] - 78, HB[1], HB[2]], 36, "metal#d0d3d7")
CY, SX, SY = 1572, HB[0], 1250
d.lathe("stem", [SX, SY, ZA], [[0, 0], [21, 0], [21, 200], [26, 240], [30, CY - 70 - SY], [0, CY - 70 - SY]], "coil")
lobes = poly(arc(SX + 82, CY, 92, 157.6, -157.6, 28) + arc(SX - 82, CY, 92, -22.4, -337.6, 28))
d.slab("coil-neck", "front", poly([(SX - 66, CY - 30), (SX + 66, CY - 30), (SX + 34, CY - 140), (SX - 34, CY - 140)]),
       [ZA - 14, ZA + 14], "coil", r=10)
d.slab("coil", "front", lobes, [ZA - 12, ZA + 12], "coil", r=8)
d.decal("coil-cross", [SX - 60, CY + 10, ZA + 12.4], [14, 2], "front", "plastic#55595f", soft=True,
        copies=[[120, 0, 0]])
d.decal("coil-cross2", [SX - 60, CY + 10, ZA + 12.4], [2, 14], "front", "plastic#55595f", soft=True,
        copies=[[120, 0, 0]])
# ---- hoses: coil hose loops down near the floor and up into the plug; two cooling hoses between the boxes
d.tube("hose", [[SX, SY, ZA], [SX - 6, 800, ZA + 30], [SX + 20, 420, ZA + 90], [-90, 290, 560], [40, 330, 640],
                [150, 560, 672], [168, 742, 660]], 40, "hose", rib=3, pitch=12, bend=120, soft=True)
d.tube("cool1", [[130, 600, ZB1 + 26], [60, 640, 680], [40, 760, 640], [69, 790, 590]], 26, "hose", rib=2, pitch=9,
       bend=50, soft=True)
d.tube("cool2", [[130, 520, ZB1 + 26], [40, 560, 690], [20, 740, 660], [69, 820, 560]], 26, "hose", rib=2, pitch=9,
       bend=60, soft=True)
d.save()
