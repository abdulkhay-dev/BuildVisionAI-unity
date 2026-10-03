"""XY-K-GR-AI: the white desktop (xy-k-gr-ai-v2) and the trolley (xy-k-gr-ai-trolley) share the wedge head:
vertical front with the socket window, a black control top rising to a rounded ridge, a short back slope."""
from p3lib import *

TRI = [("A1", "gloss#c0397f"), ("B1", "gloss#2e8fd8"), ("A2", "gloss#f2cf2a"), ("B2", "gloss#e8792b")]


def wedge(d, x0, x1, zb, zf, yb, hf, hr, hb, zr, mat="shell", r=22, pre="", rb=26):
    """The wedge body (side profile) and its black control top. Returns the Tilt of the top."""
    yf, yr, yk = yb + hf, yb + hr, yb + hb
    pts = [(zb, yb), (zf, yb), (zf, yf), (zr, yr), (zb, yk)]
    d.slab(pre + "body", "side", rpoly(pts, [rb, rb, 28, 70, 40]), [x0, x1], mat, r=r)
    L = math.hypot(zf - zr, yr - yf)
    deg = math.degrees(math.atan2(yr - yf, zf - zr))
    t = Tilt(yf, zf, deg)
    # graphite top: from just behind the front rounding to just before the ridge rounding
    t.box(d, pre + "top", x0 + 12, 14, x1 - 12, L - 62, -1.5, 1.5, "top", r=10)
    return t, L


def top_content(d, t, L, x0, x1, pre="", knobs=((0.28, 42), (0.72, 78)), scale=1.0):
    W = x1 - x0
    k = scale
    # four channel columns of vertical LED bars (green + orange) at the rear
    for i in range(4):
        cx = x0 + W * (0.14 + 0.24 * i)
        t.box(d, f"{pre}bar-g{i}", cx - 9 * k, L - 64 - 50 * k, cx - 2 * k, L - 70, 1.2, 2.2, "led-g", soft=True)
        t.box(d, f"{pre}bar-o{i}", cx + 2 * k, L - 64 - 40 * k, cx + 9 * k, L - 70, 1.2, 2.2, "led-o", soft=True)
        t.box(d, f"{pre}ticks{i}", cx - 22 * k, L - 64 - 50 * k, cx - 17 * k, L - 70, 1.2, 1.8, "print", soft=True)
    # red digit windows: two rows across the middle band
    sm = L - 70 - 58 * k
    for row in range(2):
        t.box(d, f"{pre}digit{row}", x0 + W * 0.08, sm - 12 * k - row * 24 * k, x0 + W * 0.08 + 22 * k, sm - row * 24 * k,
              1.2, 2.2, "led-r", soft=True, repeat=rep(8, [W * 0.11, 0, 0]))
    # printed frames of the bands (thin grey lines)
    t.box(d, pre + "line1", x0 + 22, sm + 6 * k, x1 - 22, sm + 8 * k, 1.2, 1.7, "print", soft=True)
    t.box(d, pre + "line2", x0 + 22, sm - 58 * k, x1 - 22, sm - 56 * k, 1.2, 1.7, "print", soft=True)
    # the bands are printed as two rounded frames per half: vertical sides of the frames
    xm = (x0 + x1) / 2
    for j, xv in enumerate((x0 + 22, xm - 5, xm + 3, x1 - 24)):
        t.box(d, f"{pre}fside{j}", xv, sm - 58 * k - 34 * k, xv + 2, sm + 8 * k, 1.2, 1.7, "print", soft=True)
    t.box(d, pre + "line3", x0 + 22, sm - 92 * k, x1 - 22, sm - 90 * k, 1.2, 1.7, "print", soft=True)
    # keys in the front band: blue + white small squares
    sk = sm - 72 * k
    t.box(d, pre + "key-b", x0 + W * 0.10, sk - 9 * k, x0 + W * 0.10 + 11 * k, sk, 1.2, 3, "key-b", r=1.5,
          repeat=rep(5, [W * 0.085, 0, 0]))
    t.box(d, pre + "key-w", x0 + W * 0.56, sk - 9 * k, x0 + W * 0.56 + 11 * k, sk, 1.2, 3, "key-w", r=1.5,
          repeat=rep(4, [W * 0.09, 0, 0]))
    for j, (fx, s) in enumerate(knobs):
        cx = x0 + W * fx
        # silver knob in a dark ring, a green ▶ and a red ● ring button to its right
        d.add(f"{pre}knob{j}-ring", "lathe", "top-dark", at=t.pt(cx, s * k, 0.5), profile=[[0, 0], [30 * k, 0], [30 * k, 3], [0, 3]], rot=t.r)
        d.add(f"{pre}knob{j}", "lathe", "knob", at=t.pt(cx, s * k, 3),
              profile=[[0, 0], [22 * k, 0], [23 * k, 4 * k], [23 * k, 14 * k], [21 * k, 18 * k], [8 * k, 19 * k], [0, 19 * k]], rot=t.r)
        for b, (dx, m) in enumerate(((52, "led-g"), (82, "led-r"))):
            d.add(f"{pre}btn{j}{b}", "lathe", m, at=t.pt(cx + dx * k, s * k - 6, 1),
                  profile=[[0, 0], [8 * k, 0], [8 * k, 1.5], [6 * k, 1.5], [6 * k, 0.8], [0, 0.8]], rot=t.r, soft=True)


def sockets(d, zf, xs, ycen, pre="", k=1.0):
    """Four inverted triangle plates with 2 grey sockets on top and 1 blue-ringed socket at the tip."""
    for i, (cx, (nm, mat)) in enumerate(zip(xs, TRI)):
        top, tip = ycen + 34 * k, ycen - 34 * k
        pts = [(cx - 33 * k, top), (cx + 33 * k, top), (cx, tip)]
        d.slab(f"{pre}tri{i}", "front", rpoly(pts, [9 * k, 9 * k, 12 * k]), [zf, zf + 1.5], mat, r=1)
        for sx in (-17, 17):
            d.cyl(f"{pre}sock{i}{'lr'[sx > 0]}", [cx + sx * k, top - 12 * k, zf], [cx + sx * k, top - 12 * k, zf + 4], 16 * k, "sock")
            d.cyl(f"{pre}hole{i}{'lr'[sx > 0]}", [cx + sx * k, top - 12 * k, zf + 3], [cx + sx * k, top - 12 * k, zf + 4.6], 8 * k, "hole", soft=True)
        d.cyl(f"{pre}sockb{i}", [cx, tip + 14 * k, zf], [cx, tip + 14 * k, zf + 4], 18 * k, "blue-ring")
        d.cyl(f"{pre}holeb{i}", [cx, tip + 14 * k, zf + 3], [cx, tip + 14 * k, zf + 4.6], 8 * k, "hole", soft=True)


MATS = {"shell": "gloss#f4f5f7", "top": "gloss#2b2f35", "top-dark": "plastic#1d2024", "knob": "metal#c8ccd1",
        "window": "plastic#6a6f76", "sock": "plastic#a3a8ae", "hole": "rubber#111214", "blue-ring": "gloss#2e7fd0",
        "led-r": "gloss#e2342b", "led-g": "gloss#3fd25a", "led-o": "gloss#ff8a2a", "print": "plastic#6d737b",
        "key-b": "gloss#3d7fe0", "key-w": "gloss#f2f3f5", "foot": "rubber#1b1c1e", "wire": "chrome",
        "warn": "gloss#f2cf2a", "vent": "plastic#3c4148"}

# ---------------------------------------------------------------- desktop
W, D_, = 430, 380
d = D("xy-k-gr-ai-v2", [500, D_, 315], dict(MATS))
t, L = wedge(d, 0, W, 0, D_, 12, 180, 300, 165, 100)
top_content(d, t, L, 0, W)
# front socket window (dark grey, right of centre) with the 4 triangle groups
# (photo: the window starts ~125 from the left edge and ends ~40 from the right; the plates sit in its lower part)
d.box("window", [120, 50, D_ - 3, 394, 178, D_ + 1.5], "window", r=14)
sockets(d, D_ + 1.5, [163, 229, 295, 358], 100, k=0.9)
d.slab("warn", "front", rpoly([(188, 74), (206, 74), (197, 90)], 2), [D_ + 1.5, D_ + 2.5], "warn")
d.box("icon", [321, 102, D_ + 1.5, 331, 118, D_ + 2.5], "key-w", soft=True)
# left side: five vertical vent slots; feet
d.box("vent", [-1.5, 95, 160, 1, 160, 166], "vent", soft=True, repeat=rep(5, [0, 0, 13]))
d.cyl("foot", [45, 0, 45], [45, 13, 45], 34, "foot", copies=[[W - 90, 0, 0], [0, 0, D_ - 90], [W - 90, 0, D_ - 90]])
# chrome wire basket on the right side, upper part
BX, BZ0, BZ1 = W + 66, 80, 320
for j, y in enumerate((135, 175, 215)):
    d.tube(f"bwire{j}", [[W - 2, y, BZ0], [BX, y, BZ0], [BX, y, BZ1], [W - 2, y, BZ1]], 4, "wire", bend=8)
d.cyl("bpost", [BX, 128, BZ0 + 4], [BX, 220, BZ0 + 4], 4, "wire", repeat=rep(6, [0, 0, (BZ1 - BZ0 - 8) / 5]))
d.cyl("bpost-e", [W + 22, 128, BZ0], [W + 22, 220, BZ0], 4, "wire", copies=[[22, 0, 0], [0, 0, BZ1 - BZ0], [22, 0, BZ1 - BZ0]])
d.tube("bbottom", [[W - 2, 128, BZ0], [BX, 128, BZ0], [BX, 128, BZ1], [W - 2, 128, BZ1]], 4, "wire", bend=8)
d.cyl("bfloor", [W, 128, BZ0 + 46], [BX, 128, BZ0 + 46], 3.5, "wire", repeat=rep(4, [0, 0, 46]))
d.save()

# ---------------------------------------------------------------- trolley: the low wedge head on a white cabinet
m = dict(MATS); m.update({"wire": "plastic#eceef0", "band": "plastic#8d939a", "seam": "plastic#4a4f56", "flap": "plastic#d9dce0",
                          "inner": "plastic#2a2d31", "frame": "plastic#a9aeb4", "handle": "rubber#1d1e20", "housing": "plastic#e9ebee"})
d = D("xy-k-gr-ai-trolley", [600, 480, 1210], m)
# (photo: the front of cabinet + head is ~2.3× the width → the cabinet is ~810 tall, not 690 as first estimated)
CX0, CX1, CZ0, CZ1, CY0, CY1 = 6, 424, 18, 458, 150, 960       # cabinet
HX0, HX1, HZ0, HZ1, HY = 0, 432, 6, 474, 966                  # head
FZ = CZ1                                                       # cabinet front plane
# castors + grey under-frame with white housings
CC = [[0, 0, 0], [358, 0, 0], [0, 0, 392], [358, 0, 392]]
d.add("castor", "caster", "rubber#8f959c", at=[36, 0, 42], d=100, copies=CC[1:])
d.box("frame", [26, 118, 30, CX1 - 6, 150, CZ1 - 10], "frame", r=14)
d.bar("arm", [70, 134, 76], [36, 134, 42], [40, 26], "frame", r=8, copies=[[358 - 0, 0, 0]])
d.bar("arm-f", [70, 134, 400], [36, 134, 434], [40, 26], "frame", r=8, copies=[[358, 0, 0]])
d.cyl("housing", [36, 112, 42], [36, 160, 42], 62, "housing", copies=CC[1:])
d.cyl("housing-band", [36, 126, 42], [36, 134, 42], 64, "frame", copies=CC[1:])
# cabinet
d.box("cabinet", [CX0, CY0, CZ0, CX1, CY1, CZ1], "shell", r=18)
d.box("plinth", [CX0 + 30, CY0 - 4, CZ1 - 40, CX1 - 30, CY0 + 30, CZ1 + 2], "flap", r=10)
# grey band and the lower panel's vent dashes
d.box("band", [CX0 + 2, 310, FZ - 3, CX1 - 2, 342, FZ + 1.5], "band", r=4)
d.box("dash", [120, 236, FZ - 1, 146, 241, FZ + 1.5], "seam", r=2, soft=True, repeat=rep(3, [36, 0, 0]), copies=[[10, -20, 0]])
# drawer: thin seam outline, black slot handle near its top
d.box("drawer", [48, 358, FZ - 1, 322, 566, FZ + 1.2], "shell", r=10)
d.box("drawer-seam", [46, 356, FZ - 2, 324, 568, FZ + 0.6], "seam", r=11, soft=True)
d.box("handle", [135, 516, FZ, 235, 552, FZ + 14], "handle", r=5)
d.box("handle-slot", [143, 520, FZ + 13, 227, 532, FZ + 15], "inner", r=3, soft=True)
# open vacuum-cup compartment with the flap hinged at its bottom, open forward and up
d.box("comp", [46, 606, FZ - 2, 322, 898, FZ + 0.8], "inner", r=8)
d.box("comp-strip", [240, 640, FZ - 1, 250, 888, FZ + 1.6], "flap", soft=True)
d.box("comp-slots", [241, 650, FZ + 1.4, 249, 653, FZ + 1.9], "inner", soft=True, repeat=rep(16, [0, 14, 0]))
d.box("comp-bracket", [60, 690, FZ - 1, 72, 760, FZ + 1.6], "flap", soft=True)
fl = rot("x", 62, [0, 610, FZ + 4])
d.box("flap", [36, 610, FZ, 332, 880, FZ + 8], "flap", r=4, rot=fl)
d.slab("flap-cheek", "side", poly([(FZ, 610), (FZ + 200, 735), (FZ + 8, 700)]), [322, 326], "flap")
# right side: two columns of slanted vent slots (upper-rear, lower-front)
sl = lambda z, y: rot("x", -30, [CX1, y, z])
d.box("vent-up", [CX1 - 1, 600, 52, CX1 + 1.5, 605, 92], "seam", soft=True, rot=sl(72, 602), repeat=rep(16, [0, 20, 0]))
d.box("vent-lo", [CX1 - 1, 200, 370, CX1 + 1.5, 205, 410], "seam", soft=True, rot=sl(390, 202), repeat=rep(18, [0, 20, 0]))
# small grey box holder under the head on the right, near the front
d.box("holder", [CX1 - 4, 896, 280, CX1 + 28, 958, 400], "band", r=10)
# seam + head
d.box("seam", [CX0 + 8, CY1 - 2, CZ0 + 8, CX1 - 8, HY + 2, CZ1 - 8], "seam", r=4)
t, L = wedge(d, HX0, HX1, HZ0, HZ1, HY, 148, 236, 90, 175, r=18, rb=10)
top_content(d, t, L, HX0, HX1, knobs=((0.15, 26), (0.57, 26)), scale=0.85)
d.box("window", [40, HY + 26, HZ1 - 3, 314, HY + 116, HZ1 + 1.5], "window", r=12)
sockets(d, HZ1 + 1.5, [97, 157, 222, 285], HY + 71, k=0.7)
d.slab("warn", "front", rpoly([(120, HY + 34), (134, HY + 34), (127, HY + 46)], 2), [HZ1 + 1.5, HZ1 + 2.5], "warn")
d.box("icon", [250, HY + 34, HZ1 + 1.5, 258, HY + 46, HZ1 + 2.5], "key-w", soft=True)
d.box("hvent", [HX1 - 1, HY + 116, 150, HX1 + 1.5, HY + 156, 155], "seam", soft=True, repeat=rep(5, [0, 0, 11]))
# white wire basket on the right side of the head
BX, BZ0, BZ1 = HX1 + 160, 170, 420
B0 = HY + 66
for j, y in enumerate((B0, B0 + 35, B0 + 68)):
    d.tube(f"bwire{j}", [[HX1 - 2, y, BZ0], [BX, y, BZ0], [BX, y, BZ1], [HX1 - 2, y, BZ1]], 5, "wire", bend=10)
d.tube("bbottom", [[HX1 - 2, B0, BZ0], [BX, B0, BZ0], [BX, B0, BZ1], [HX1 - 2, B0, BZ1]], 5, "wire", bend=10)
d.cyl("bpost", [HX1 + 26, B0 - 2, BZ0], [HX1 + 26, B0 + 70, BZ0], 5, "wire", repeat=rep(6, [26.5, 0, 0]), copies=[[0, 0, BZ1 - BZ0]])
d.cyl("bpost-e", [BX, B0 - 2, BZ0 + 50], [BX, B0 + 70, BZ0 + 50], 5, "wire", repeat=rep(4, [0, 0, 50]))
d.cyl("bfloor", [HX1, B0, BZ0 + 50], [BX, B0, BZ0 + 50], 4, "wire", repeat=rep(4, [0, 0, 50]))
d.box("bclip", [HX1 - 2, B0 + 40, BZ0 + 10, HX1 + 14, B0 + 75, BZ1 - 10], "wire", r=4)
d.save()
