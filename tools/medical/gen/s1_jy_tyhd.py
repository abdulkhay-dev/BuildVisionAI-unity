"""jy-tyhd-i: mobile floor-projection cart with a 'face' (yellow C-shell, light-blue base)."""
import math
from s1lib import *

W, DD, H = 600, 700, 1600
ZF = 668                      # front faces of the blue box, the lower yellow box and the head
d = D("jy-tyhd-i", [W, DD, H], {
    "blue": "plastic#a6d9ee", "yel": "plastic#f0c46a", "white": "plastic#e8e9ea", "grey": "plastic#5a6368",
    "dark": "plastic#2d3b3e", "black": "gloss#0d0f12", "logo": "gloss#1e4fa0"})

# castors (white wheels) and the plinth
for i, (x, z) in enumerate([(75, 80), (W - 75, 80), (75, DD - 80), (W - 75, DD - 80)]):
    d.add(f"castor{i}", "caster", "plastic#f2f3f4", at=[x, 0, z], d=100)
top_slab(d, "plinth", rrect_pts(0, 0, W, DD, 60), 128, 195, "blue", r=14)

# light-blue lower box: side profile with the quarter-curve top at the back, front part with the arched recess
arc_pts = [(20, 270), (60, 370), (119, 445), (190, 520), (252, 570), (320, 615), (385, 645), (450, 668), (520, 684), (560, 690)]
side_slab(d, "bluebox", [(20, 195)] + arc_pts + [(560, 195)], 15, W - 15, "blue", r=18)
notch = [(300 + 120 * math.cos(math.radians(a)), 195 + 145 * math.sin(math.radians(a))) for a in range(180, -1, -15)]
front_slab(d, "bluefront", [(15, 195)] + notch + [(W - 15, 195), (W - 15, 690), (15, 690)], 555, ZF, "blue", r=32)
d.lathe("puck", [300, 195, 600], [[0, 0], [82, 0], [82, 8], [62, 10], [62, 34], [66, 36], [66, 62], [60, 66], [0, 66]], "dark", sides=28)
# mesh band with the arched notch and the white marker
d.box("band", [40, 420, ZF - 2, W - 40, 525, ZF + 3], "grey", r=10)
front_slab(d, "notch", [(300 + 52 * math.cos(math.radians(a)), 522 + 52 * math.sin(math.radians(a))) for a in range(0, 181, 15)],
           ZF - 2, ZF + 2, "dark", soft=True)
front_slab(d, "marker", tri_pts(300, 512, 64, "down"), ZF + 3, ZF + 4, "plastic#f6f6f6", soft=True)
front_slab(d, "marker-in", tri_pts(300, 514, 50, "down"), ZF + 4, ZF + 5, "plastic#4f585c", soft=True)
# the band's diagonal mesh texture: thin lighter hatch lines clipped to the band
def clip(x0, y0, x1, y1, bx0, by0, bx1, by1):
    t0, t1 = 0.0, 1.0
    dx, dy = x1 - x0, y1 - y0
    for p_, q_ in ((-dx, x0 - bx0), (dx, bx1 - x0), (-dy, y0 - by0), (dy, by1 - y0)):
        if p_ == 0:
            if q_ < 0: return None
            continue
        r_ = q_ / p_
        if p_ < 0: t0 = max(t0, r_)
        else: t1 = min(t1, r_)
    return None if t0 >= t1 else [(x0 + dx * t0, y0 + dy * t0), (x0 + dx * t1, y0 + dy * t1)]
hatch = []
for k in range(-8, 60):
    x = 40 + k * 10
    seg = clip(x, 424, x + 100, 521, 50, 424, W - 50, 521)
    if seg and not (250 < (seg[0][0] + seg[1][0]) / 2 < 350 and seg[1][1] > 470):
        hatch.append(seg)
strokes(d, "hatch", hatch, ZF + 3.2, 2.2, "plastic#737d82")
d.box("sideslot", [11, 330, 300, 16, 500, 322], "black", r=3, soft=True)

# yellow shell: rear column + head (full width), its cheeks curve back under the head
shell = [(0, 250), (0, 1430)] + [(100 - 100 * math.cos(math.radians(a)), 1430 + 100 * math.sin(math.radians(a))) for a in (20, 45, 70)] + \
        [(100, 1530), (640, 1530), (664, 1518), (ZF, 1490), (ZF, 1335), (650, 1310), (520, 1310), (430, 1292), (350, 1240),
         (305, 1160), (290, 1060), (290, 600)] + list(reversed(arc_pts[:5])) + [(0, 250)]
side_slab(d, "shell", shell[:-1], 0, W, "yel", r=28)
# lower yellow box with the round badge
d.box("ybox", [15, 690, 290, W - 15, 945, ZF], "yel", r=16)
d.cyl("badge", [352, 811, ZF - 1], [352, 811, ZF + 2], 72, "plastic#f4f1e8", soft=True)
front_slab(d, "badge-ring", ring_path(352, 811, 29, 34), ZF + 2, ZF + 3, "logo", soft=True)
strokes(d, "badge-mark", [[(338, 826), (352, 812), (366, 826)], [(352, 812), (352, 793)], [(342, 800), (362, 800)]], ZF + 3, 5, "logo")
# projector bay: white sloped face between two yellow cheeks
side_slab(d, "bay", [(290, 945), (640, 945), (470, 1310), (290, 1310)], 35, W - 35, "white", r=8)
for i, (x0, x1) in enumerate([(15, 35), (W - 35, W - 15)]):
    side_slab(d, f"cheek{i}", [(290, 940), (ZF, 940), (575, 1312), (290, 1312)], x0, x1, "yel", r=6)
ang = -math.degrees(math.atan2(170, 365))   # slope of the bay face (top leans back)
def on_slope(y): return 640 - (y - 945) * 170 / 365
zw = on_slope(1252)
d.box("window", [80, 1200, zw - 4, 520, 1305, zw + 6], "black", r=6, rot=rot("x", ang, [300, 1252, zw]))
d.box("window-tab", [110, 1258, zw + 6, 150, 1284, zw + 8], "plastic#f2f2f2", soft=True, rot=rot("x", ang, [300, 1252, zw]))
zp = on_slope(1100)
d.box("plate", [175, 1020, zp - 2, 300, 1180, zp + 7], "plastic#d9dbdd", r=6, rot=rot("x", ang, [237, 1100, zp]))
zd = on_slope(1150)
d.box("diamond", [362, 1122, zd, 418, 1178, zd + 3], "plastic#4a4f53", r=4, soft=True,
      rot=rot("z", 45, [390, 1150, zd]), rots=[rot("x", ang, [390, 1150, zd])])
zs_ = on_slope(1060)
d.box("sticker", [70, 1045, zs_, 165, 1075, zs_ + 2], "plastic#cfd3d6", soft=True, rot=rot("x", ang, [117, 1060, zs_]))
d.box("sticker-art", [80, 1055, zs_ + 2, 155, 1065, zs_ + 2.8], "plastic#6a7378", soft=True, rot=rot("x", ang, [117, 1060, zs_]))
d.box("btnstrip", [35, 1150, 520, 38, 1300, 575], "plastic#f4f4f4", soft=True)
d.box("btns", [38, 1165, 532, 39.5, 1175, 542], "black", soft=True, repeat={"n": 6, "step": [0, 22, 0]})
# head: two dark round mesh "eye" speakers
for i, x in enumerate((150, 450)):
    d.lathe(f"eye{i}", [x, 1420, ZF - 2], [[0, 0], [62, 0], [62, 6], [58, 10], [0, 10]], "dark", axis="z", sides=36)
    disc(d, f"eyemesh{i}", x, 1420, ZF + 8, 100, "plastic#4a565a", h=1.0)
    # the speaker mesh: rows of small dark holes
    for j in range(-5, 6):
        hc = math.sqrt(max(0.0, 46 ** 2 - (j * 8.5) ** 2))
        n = int(2 * hc / 8.5) + 1
        disc(d, f"eyehole{i}-{j + 5}", x - (n - 1) * 4.25, 1420 + j * 8.5, ZF + 9, 4.0, "plastic#20292c", h=0.6,
             repeat={"n": n, "step": [8.5, 0, 0]})
# vent dots on the left side (x = 0 face of the lower box / cheek)
d.box("vent", [12, 730, 470, 15.5, 737, 477], "dark", soft=True, repeat={"n": 16, "step": [0, 20, 0]},
      copies=[[0, 0, 20], [0, 0, 40], [0, 0, 60], [0, 0, 80]])
# two light-blue loop handles on top at the rear
for i, x in enumerate((42, W - 42)):
    d.tube(f"loop{i}", [[x, 1490 + 92 * math.sin(math.radians(a)), 150 - 92 * math.cos(math.radians(a))] for a in range(-10, 191, 20)], 26, "blue")
d.save()
