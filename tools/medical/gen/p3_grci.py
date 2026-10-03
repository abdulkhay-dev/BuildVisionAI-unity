"""XY-K-GR-CI (new design, desktop): white/graphite base box with the socket window, a thick white slab with the black
LED face tilted on top, a white vacuum-cup holder on the right."""
from p3lib import *

d = D("xy-k-gr-ci-v2", [500, 400, 365], {
    "shell": "gloss#f4f5f7", "graph": "plastic#3a3f46", "trim": "plastic#2f3338", "face": "gloss#24272c",
    "window": "plastic#5a5f66", "sock": "rubber#141517", "ring": "gloss#3b8fe0", "foot": "rubber#1b1c1e",
    "led-o": "gloss#f2a35a", "led-g": "gloss#dfe9a8", "digit": "gloss#e8552e", "key-w": "gloss#f4f6f8", "bar-g": "gloss#9fd65a", "bar-y": "gloss#f0c040", "mode": "plastic#4a5058",
    "mode-l": "gloss#8fdc6a", "key": "gloss#c7e3f6", "key-d": "gloss#5b8fc6", "knob": "metal#d0d3d7", "arc": "gloss#2f7fd0",
    "go": "gloss#3fbf6a", "stop": "gloss#e8792b", "logo": "plastic#5b6068", "cyan": "gloss#5fd0e8", "title": "gloss#2f6fbf"})
X0, X1, Z0, ZF = 20, 444, 10, 372
# ---- base: dark bottom trim and feet, graphite right side and rear block, white front shell
d.cyl("foot", [X0 + 40, 0, Z0 + 40], [X0 + 40, 16, Z0 + 40], 40, "foot", copies=[[X1 - X0 - 80, 0, 0], [0, 0, ZF - Z0 - 80], [X1 - X0 - 80, 0, ZF - Z0 - 80]])
d.box("trim", [X0 + 4, 14, Z0 + 4, X1 - 4, 42, ZF - 4], "trim", r=10)
d.box("graph-side", [X1 - 30, 30, Z0, X1, 196, ZF - 18], "graph", r=12)
d.box("graph-rear", [X0 + 30, 150, Z0, X1, 282, Z0 + 150], "graph", r=16)
d.box("shell", [X0, 36, Z0 + 20, X1 - 22, 196, ZF], "shell", r=18)
d.box("seam", [X0 + 6, 139, ZF - 1, X1 - 26, 141, ZF + 0.8], "trim", soft=True)
d.box("door-seam", [X0 + 172, 44, ZF - 1, X0 + 174, 139, ZF + 0.8], "trim", soft=True)
d.cyl("logo", [X0 + 48, 112, ZF], [X0 + 48, 112, ZF + 1.5], 26, "logo", soft=True)
d.cyl("logo-c", [X0 + 48, 112, ZF + 1], [X0 + 48, 112, ZF + 2], 14, "shell", soft=True)
d.box("door-slot", [X0 + 82, 88, ZF - 1, X0 + 112, 92, ZF + 1.2], "logo", soft=True)
d.box("door-text", [X0 + 70, 58, ZF - 1, X0 + 128, 62, ZF + 1], "logo", soft=True, copies=[[0, -7, 0]])
d.box("cyan", [X0 + 360, 143, ZF - 1, X0 + 382, 146, ZF + 1.5], "cyan", soft=True)
# socket window with three triangle plates (orange A, yellow B, red C), 3 blue-ringed sockets each
WX0, WX1 = X0 + 182, X0 + 396
d.box("window", [WX0, 50, ZF - 3, WX1, 128, ZF + 1.5], "window", r=10)
for i, (cx, m) in enumerate(zip((WX0 + 44, WX0 + 107, WX0 + 170), ("gloss#e8762b", "gloss#f2c62a", "gloss#e0372a"))):
    d.slab(f"tri{i}", "front", rpoly([(cx - 27, 118), (cx + 27, 118), (cx, 66)], [6, 6, 10]), [ZF + 1.5, ZF + 2.5], m, r=0.6)
    for j, (sx, sy) in enumerate(((-21, 108), (21, 108), (0, 74))):
        d.cyl(f"ring{i}{j}", [cx + sx, sy, ZF + 1], [cx + sx, sy, ZF + 5], 22, "ring")
        d.cyl(f"sock{i}{j}", [cx + sx, sy, ZF + 4], [cx + sx, sy, ZF + 5.5], 12, "sock", soft=True)
# white vertical handle on the left side
d.add("lhandle", "bar", "shell", **{"from": [X0 - 9, 70, 300], "to": [X0 - 9, 170, 300]}, section=[18, 26], r=8)
d.box("lhandle-stub", [X0 - 18, 66, 288, X0 + 2, 82, 312], "shell", r=6, copies=[[0, 92, 0]])
# right side: fine horizontal vent lines low on the graphite side
d.box("vent", [X1 - 0.5, 50, Z0 + 30, X1 + 1, 53, Z0 + 190], "trim", soft=True, repeat=rep(7, [0, 7, 0]))
# white vacuum-cup holder hanging on the right side: top hook arm, U-shaped holder with 2 cup slots
HX0, HX1, HZ0, HZ1 = X1, X1 + 54, 160, 330
d.box("cup-back", [HX0, 70, HZ0, HX0 + 6, 205, HZ1], "shell", r=3)
d.box("cup-bottom", [HX0, 66, HZ0, HX1, 74, HZ1], "shell", r=4)
d.slab("cup-front", "side", rpoly([(HZ0, 70), (HZ1, 70), (HZ1, 175), (HZ1 - 20, 175), (HZ1 - 30, 112), (HZ0 + 30, 112),
                                   (HZ0 + 20, 175), (HZ0, 175)], [4, 4, 4, 4, 22, 22, 4, 4]), [HX1 - 6, HX1], "shell", r=2)
d.box("cup-side", [HX0, 70, HZ0, HX1, 175, HZ0 + 6], "shell", r=2, copies=[[0, 0, HZ1 - HZ0 - 6]])
d.box("cup-mid", [HX0, 70, (HZ0 + HZ1) / 2 - 3, HX1, 150, (HZ0 + HZ1) / 2 + 3], "shell", r=2)
d.box("cup-arm", [HX0, 196, HZ0 + 10, HX1 - 8, 210, HZ0 + 50], "shell", r=5)
d.box("cup-arm-up", [HX1 - 18, 196, HZ0 + 10, HX1 - 8, 240, HZ0 + 50], "shell", r=4)
# ---- the tilted slab: white rim, black face and its displays (layout measured on the photo: the displays fill the
# left 2/3, the mode column and the knob the right third)
TZ, TY, DEG, SL = ZF + 14, 192, 24, 335
t = Tilt(TY, TZ, DEG)
t.box(d, "slab", X0 - 2, 0, X1 + 2, SL, 0, 38, "shell", r=16)
t.box(d, "face", X0 + 14, 30, X1 - 12, SL - 14, 37, 39.2, "face", r=8)
H = 39.4
t.box(d, "title", X0 + 160, SL - 30, X0 + 300, SL - 22, H - 0.5, H + 0.4, "title", soft=True)
t.box(d, "title-l", X0 + 150, SL - 34, X0 + 310, SL - 33, H - 0.5, H + 0.4, "title", soft=True)
t.box(d, "brand", X0 + 40, SL - 32, X0 + 70, SL - 22, H - 0.5, H + 0.4, "title", soft=True)
# LED windows: pale green glass with red digits, 2 rows of 3
for row, (sw, wins) in enumerate(((256, ((125, 156), (175, 206), (229, 271))), (212, ((114, 127), (153, 193), (214, 258))))):
    for k, (xa, xb) in enumerate(wins):
        t.box(d, f"win{row}{k}", xa, sw, xb, sw + 26, H - 0.5, H + 0.6, "led-g", soft=True)
        t.box(d, f"dig{row}{k}", xb - min(26, (xb - xa) * 0.7) - 3, sw + 6, xb - 3, sw + 21, H + 0.4, H + 1.0, "digit", soft=True)
        t.box(d, f"wlab{row}{k}", xa + 4, sw - 7, xb - 4, sw - 3, H - 0.5, H + 0.6, "mode", soft=True)
# A / B / C intensity bars (green, a yellow-orange part) with the channel letter and a green square
for k, sb in enumerate((176, 146, 116)):
    t.box(d, f"bar{k}", 130, sb, 251, sb + 13, H - 0.5, H + 0.6, "bar-g", soft=True)
    t.box(d, f"bar{k}y", 188, sb + 1, 227, sb + 12, H - 0.5, H + 0.9, "bar-y", soft=True)
    t.box(d, f"barf{k}", 128, sb - 2, 253, sb + 15, H - 0.5, H + 0.3, "mode", soft=True)
    t.box(d, f"barl{k}", 112, sb + 2, 121, sb + 11, H - 0.5, H + 0.6, "mode-l", soft=True)
    t.box(d, f"barc{k}", 98, sb + 4, 104, sb + 9, H - 0.5, H + 0.6, "mode", soft=True)
# column of 7 mode boxes (dark windows with a green level line)
for k in range(7):
    sm = 272 - 26 * k
    t.box(d, f"mode{k}", 293, sm, 337, sm + 15, H - 0.5, H + 0.6, "mode", soft=True)
    t.box(d, f"model{k}", 297, sm + 9, 320, sm + 12, H - 0.5, H + 0.9, "mode-l", soft=True)
# 7 key groups in a row at the front (light blue pill with a white middle)
for k in range(7):
    x = 79 + 31.7 * k
    t.box(d, f"key{k}", x, 46, x + 22, 88, H - 0.5, H + 2, "key", r=4)
    t.box(d, f"keyd{k}", x + 3, 60, x + 19, 72, H + 1.5, H + 2.6, "key-w", soft=True)
# knob with a blue arc on its right (1–4 o'clock)
KX, KS = 353, 140
d.add("knob-ring", "lathe", "face", at=t.pt(KX, KS, H), profile=[[0, 0], [31, 0], [31, 2], [0, 2]], rot=t.r)
arc = [t.world(KX + 36 * math.cos(math.radians(a)), KS + 36 * math.sin(math.radians(a)), H + 1) for a in range(60, -45, -15)]
d.tube("knob-arc", arc, 3.5, "arc", soft=True)
d.add("knob", "lathe", "knob", at=t.pt(KX, KS, H),
      profile=[[0, 0], [25, 0], [26, 6], [24, 18], [18, 24], [0, 26]], rot=t.r)
# start ▶ / stop ■ : dark squares with a coloured outline and icon
for nm, x, m in (("go", 318, "go"), ("stop", 348, "stop")):
    t.box(d, nm, x, 56, x + 16, 72, H - 0.5, H + 1.2, m, r=2)
    t.box(d, nm + "-in", x + 1.5, 57.5, x + 14.5, 70.5, H + 0.9, H + 1.5, "face", soft=True)
t.box(d, "stop-ico", 353, 61, 359, 67, H + 1.2, H + 1.8, "stop", soft=True)
t.box(d, "go-ico", 324, 61, 330, 67, H + 1.2, H + 1.8, "go", soft=True)
d.save()
