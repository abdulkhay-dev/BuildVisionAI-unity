from h1lib import *
# Infant hydrotherapy station, 4 modules left -> right: (1) wash unit with a wide oval basin, (2) plain unit with a pink
# control box, (3) wide oval swimming tub with a raised rim ring, a semicircular bulging front with a sweeping step
# line, (4) changing table: padded top, open left bay (see-through), 3 silver drawers on the right.
# White glossy cabinets with a thick rounded top lip (groove under it), back splash from the faucet of (1) to the end
# of (3), tall chrome faucets in front of the splash, chrome feet, sea-creature stickers (fish, crabs, turtles, bubbles).
# Review 2026-10-02: module widths from the photo, perspective-corrected against each module's height
# (≈ 0.98 / 0.95 / 1.36 / 1.13 × the 860 worktop) -> 840 / 820 / 1170 / 970 = 3800; lip 210 thick; tub 1000 × 720
# (rim ring ≈ 0.9 of the module); open bay without back; drawers silver; stickers as fish/crab/turtle/bubble shapes.
W1, W2, W3, W4 = 840, 820, 1170, 970
XA = [0, W1, W1 + W2, W1 + W2 + W3, W1 + W2 + W3 + W4]
d = D("baby-hydrotherapy-station", [XA[4], 860, 1200], {
    "shell": "gloss#f8f9fa", "inner": "gloss#eef2f5", "pink": "gloss#f2a9c9", "dark": "black#2a2d31",
    "pad": "leather#f3f3f1", "grey": "plastic#9ea4ab", "silver": "gloss#dcdfe3", "feet": "chrome",
    "bub": "gloss#6a72d8", "seam": "plastic#d6dade"})
CAB_Y, LIP_Y, TOP = 40, 650, 860
D0 = 650


def feet(nm, x0, x1, zf=D0):
    d.cyl(nm, [x0 + 70, 0, 80], [x0 + 70, CAB_Y + 2, 80], 34, "feet", copies=[[x1 - x0 - 140, 0, 0], [0, 0, zf - 160], [x1 - x0 - 140, 0, zf - 160]])


def faucet(nm, x, z):
    d.lathe(nm + "-base", [x, TOP, z], [[0, 0], [28, 0], [28, 14], [16, 22], [0, 22]], "chrome")
    d.tube(nm, [[x, TOP, z], [x, TOP + 320, z], [x + 20, TOP + 325, z + 150], [x + 20, TOP + 285, z + 165]], 28, "chrome", bend=30)
    d.cyl(nm + "-lever", [x, TOP + 90, z], [x + 60, TOP + 100, z], 16, "chrome")


def pink_box(nm, x, z, dial=False):
    d.box(nm, [x - 85, TOP + 15, z, x + 85, TOP + 125, z + 45], "pink", r=12)
    d.add(nm + "-lcd", "screen", box=[x - 65, TOP + 40, z + 40, x + 5, TOP + 100, z + 47], r=4, face="front", bezel=3, mat="pink")
    if dial:
        d.lathe(nm + "-dial", [x + 45, TOP + 70, z + 45], [[0, 0], [22, 0], [22, 3], [0, 3]], "gloss#3a7fd8", axis="z")
        d.lathe(nm + "-dial2", [x + 45, TOP + 70, z + 47], [[0, 0], [12, 0], [12, 3], [0, 3]], "gloss#e8463c", axis="z")
    else:
        d.lathe(nm + "-key", [x + 40, TOP + 85, z + 45], [[0, 0], [10, 0], [10, 3], [0, 3]], "gloss#3a7fd8", axis="z", copies=[[0, -32, 0]])


def cabinet(pre, x0, x1, top_outline=None):
    """Plain cabinet: body + lip with a groove line; top_outline (ring) replaces the lip box (basins)."""
    d.box(pre + "cab", [x0 + 6, CAB_Y, 0, x1 - 6, LIP_Y + 1, D0 - 8], "shell", r=12)
    if top_outline is None:
        d.box(pre + "lip", [x0 + 2, LIP_Y, 0, x1 - 2, TOP, D0], "shell", r=60)
    d.decal(pre + "groove", [(x0 + x1) / 2, LIP_Y + 4, D0 - 7.5], [x1 - x0 - 20, 5], "front", "seam", soft=True)
    feet(pre + "foot", x0, x1)


# ---- stickers (thin front slabs)
def ellp(cx, cy, rx, ry, n=16): return ell(cx, cy, rx, ry, n)
STK = []  # (id, polygon points, mat)
def fish(nm, x, y, L, col, flip=False):
    s = -1 if flip else 1
    STK.append((nm, ellp(x, y, L * 0.36, L * 0.2), col))
    STK.append((nm + "t", [(x - s * L * 0.3, y), (x - s * L * 0.5, y + L * 0.17), (x - s * L * 0.5, y - L * 0.17)], col))
def crab(nm, x, y, s):
    STK.append((nm, ellp(x, y, s * 0.4, s * 0.28), "gloss#e2473a"))
    STK.append((nm + "a", ellp(x - s * 0.42, y + s * 0.3, s * 0.13, s * 0.13, 10), "gloss#e2473a"))
    STK.append((nm + "b", ellp(x + s * 0.42, y + s * 0.3, s * 0.13, s * 0.13, 10), "gloss#e2473a"))
def turtle(nm, x, y, s):
    STK.append((nm, ellp(x, y, s * 0.42, s * 0.3), "gloss#7fae6a"))
    STK.append((nm + "h", ellp(x - s * 0.5, y + s * 0.08, s * 0.13, s * 0.11, 10), "gloss#9cc486"))
def blob(nm, x, y, s, col):
    STK.append((nm, [(x - s * .5, y - s * .1), (x - s * .2, y + s * .5), (x + s * .1, y + s * .2), (x + s * .45, y + s * .45),
                     (x + s * .35, y - s * .15), (x, y - s * .5), (x - s * .3, y - s * .4)], col))
BUB = []
def bubbles(pts): BUB.extend(pts)


# (1) wash unit, wide oval basin centred, splash from the faucet on
cx1 = W1 / 2
hole1 = ell(cx1 + 10, 345, 360, 215)
d.box("m1-cab", [6, CAB_Y, 0, W1 - 6, LIP_Y + 1, D0 - 8], "shell", r=12)
d.decal("m1-groove", [W1 / 2, LIP_Y + 4, D0 - 7.5], [W1 - 20, 5], "front", "seam", soft=True)
feet("m1-foot", 0, W1)
tub(d, "m1-", None, hole1, rr(2, 0, W1 - 2, D0, 60), LIP_Y, TOP - LIP_Y, 560, offset(hole1, 20), rim_r=70)
d.slab("m1-bowlrim", "top", ring(offset(hole1, 22), hole1), [TOP - 4, TOP + 8], "shell", r=6)
faucet("m1-faucet", 300, 120)
# (2) plain unit with the pink control box at the back left
cabinet("m2-", XA[1], XA[2]); pink_box("m2-ctrl", XA[1] + 150, 95)
# splash: from the faucet of (1) over (2) and (3)
d.box("splash", [250, TOP - 10, 0, XA[3] - 6, TOP + 120, 95], "shell", r=30)
# (3) wide oval tub, semicircular bulging front
X3a, X3b = XA[2], XA[3]
cx3 = (X3a + X3b) / 2
ZS, RZ = 450, 410  # straight sides to ZS, elliptic front to ZS + RZ = 860
def zfront(x): t = (x - cx3) / (W3 / 2); return ZS + RZ * math.sqrt(max(0.0, 1 - t * t))
out3 = [(X3a, 0), (X3b, 0)] + [(cx3 + W3 / 2 * math.cos(math.radians(a)), ZS + RZ * math.sin(math.radians(a))) for a in range(0, 181, 6)]
hole3 = ell(cx3, 465, 495, 345, n=64)
d.slab("m3-cab", "top", P(out3) + " " + P(offset(hole3, 40)), [CAB_Y, LIP_Y + 1], "shell", r=14)
d.slab("m3-lip", "top", P(out3) + " " + P(offset(hole3, 30)), [LIP_Y, TOP], "shell", r=60)
d.slab("m3-walls", "top", ring(offset(hole3, 34), hole3), [470, TOP - 20], "inner", r=4)
d.slab("m3-floor", "top", P(offset(hole3, 20)), [445, 470], "inner", r=4)
d.slab("m3-ring", "top", ring(offset(hole3, 45), hole3), [TOP - 20, TOP + 45], "shell", r=22)
# the groove under the lip and the sweeping step line of the front (tubes on the bulge surface)
d.tube("m3-groove", [[x, LIP_Y + 4, zfront(x) + 1] for x in [X3a + 4] + [cx3 + W3 / 2 * math.cos(math.radians(a)) for a in range(176, 3, -8)] + [X3b - 4]],
       6, "seam", soft=True)
sw = [(0.03, 440), (0.14, 395), (0.27, 345), (0.41, 328), (0.55, 345), (0.68, 395), (0.79, 460), (0.88, 560), (0.95, 665)]
d.tube("m3-step", [[X3a + f * W3, y, zfront(X3a + f * W3) + 2] for f, y in sw], 9, "seam", bend=40, soft=True)
d.tube("m3-step2", [[X3a + 0.955 * W3, 665, zfront(X3a + 0.955 * W3) + 2], [X3a + 0.96 * W3, 60, zfront(X3a + 0.96 * W3) + 2]], 9, "seam", soft=True)
d.cyl("m3-foot", [X3a + 120, 0, 120], [X3a + 120, CAB_Y + 2, 120], 34, "feet",
      copies=[[W3 - 240, 0, 0], [W3 * 0.5 - 120 - 300, 0, 650], [W3 * 0.5 - 120 + 300, 0, 650]])
faucet("m3-faucet", X3a + 0.18 * W3, 120); pink_box("m3-ctrl", X3b - 120, 95, dial=True)
# (4) changing table: padded top, open left bay (no back), drawer case with 3 silver drawers
X4a, X4b = XA[3], XA[4]
XC = X4a + 0.46 * W4
d.box("m4-top", [X4a + 10, 750, 0, X4b, 860, D0 + 10], "pad", r=28, puff=6)
d.box("m4-side", [X4a + 20, 70, 20, X4a + 75, 750, D0 - 10], "shell", r=6)
d.box("m4-bottom", [X4a + 20, 0, 20, XC, 80, D0 - 10], "shell", r=6)
d.box("m4-case", [XC, 0, 20, X4b - 10, 750, D0 - 20], "shell", r=6)
d.box("m4-rside", [X4b - 45, 0, 20, X4b - 5, 750, D0 - 10], "shell", r=6)
for k in range(3):
    y0 = 40 + k * 222
    d.box(f"m4-drawer{k}", [XC + 15, y0, D0 - 24, X4b - 50, y0 + 205, D0 - 8], "silver", r=6)
    d.box(f"m4-pull{k}", [XC + 15, y0 + 188, D0 - 10, X4b - 50, y0 + 205, D0 - 2], "grey", r=4)
# stickers: (1)
x = lambda f: f * W1
fish("s1a", x(0.2), 165, 120, "gloss#5577cc"); fish("s1b", x(0.33), 245, 80, "gloss#7bb06a", flip=True)
blob("s1c", x(0.48), 300, 110, "gloss#e98aa8"); crab("s1d", x(0.86), 200, 70); fish("s1e", x(0.7), 105, 70, "gloss#7a3f9a")
bubbles([(x(f), y) for f, y in ((0.12, 330), (0.29, 410), (0.32, 145), (0.41, 105), (0.52, 115), (0.63, 230), (0.72, 330),
                                    (0.8, 150), (0.9, 80), (0.95, 290), (0.6, 160))])
# (2)
x = lambda f: XA[1] + f * W2
fish("s2a", x(0.27), 210, 90, "gloss#e8a43a"); fish("s2b", x(0.6), 165, 85, "gloss#7a3f9a"); turtle("s2c", x(0.82), 155, 110)
fish("s2d", x(0.65), 40 + 60, 75, "gloss#f2d02c", flip=True); fish("s2e", x(0.17), 75, 75, "gloss#6cb06a", flip=True)
bubbles([(x(f), y) for f, y in ((0.09, 340), (0.41, 310), (0.74, 290), (0.94, 180), (0.95, 40 + 60), (0.84, 45), (0.43, 75),
                                    (0.33, 70), (0.05, 85), (0.41, 160), (0.07, 200))])
# (3) on the bulge
x = lambda f: X3a + f * W3
STK.append(("s3-island", ellp(x(0.38), 450, 165, 55, 20), "plastic#a7b0b2"))
STK.append(("s3-canopy", [(x(0.36) + 115 * math.cos(math.radians(a)), 620 + 75 * math.sin(math.radians(a))) for a in range(0, 181, 15)], "gloss#2f4fae"))
STK.append(("s3-canopy-r", [(x(0.36), 620)] + [(x(0.36) + 115 * math.cos(math.radians(a)), 620 + 75 * math.sin(math.radians(a))) for a in range(50, 91, 10)], "gloss#c8323e"))
STK.append(("s3-canopy-r2", [(x(0.36), 620)] + [(x(0.36) + 115 * math.cos(math.radians(a)), 620 + 75 * math.sin(math.radians(a))) for a in range(130, 171, 10)], "gloss#c8323e"))
STK.append(("s3-pole", rr(x(0.36) - 4, 460, x(0.36) + 4, 622, 1), "dark"))
crab("s3-crab", x(0.31), 500, 90); crab("s3-crab2", x(0.43), 455, 40)
STK.append(("s3-bucket", rr(x(0.48), 470, x(0.53), 520, 4), "gloss#3aa64a"))
turtle("s3-turtle", x(0.73), 380, 100); fish("s3-fa", x(0.2), 290, 70, "gloss#7a3f9a", flip=True)
blob("s3-coral", x(0.44), 200, 120, "gloss#e98aa8"); fish("s3-fb", x(0.79), 180, 70, "gloss#6cb06a", flip=True)
bubbles([(x(f), y) for f, y in ((0.12, 330), (0.29, 250), (0.22, 170), (0.55, 210), (0.62, 260), (0.6, 130), (0.73, 150),
                                    (0.07, 260), (0.86, 330))])


def zface(xm):
    if X3a <= xm <= X3b: return zfront(xm)
    return D0 - 8


def clip(poly, a, b):
    def cut(pts, keep, xc):
        out = []
        for i in range(len(pts)):
            p, q = pts[i - 1], pts[i]
            ip, iq = keep(p[0]), keep(q[0])
            if iq:
                if not ip: out.append((xc, p[1] + (q[1] - p[1]) * (xc - p[0]) / (q[0] - p[0])))
                out.append(q)
            elif ip: out.append((xc, p[1] + (q[1] - p[1]) * (xc - p[0]) / (q[0] - p[0])))
        return out
    return cut(cut(poly, lambda v: v >= a, a), lambda v: v <= b, b)


for nm, poly, mat in STK:
    xs = [p[0] for p in poly]
    x0, x1 = min(xs), max(xs)
    on_bulge = X3a < (x0 + x1) / 2 < X3b
    n = max(1, int((x1 - x0) / 40) + 1) if on_bulge else 1
    for k in range(n):
        a, b = x0 + (x1 - x0) * k / n, x0 + (x1 - x0) * (k + 1) / n
        part = clip(poly, a - 0.01, b + 0.01) if n > 1 else poly
        if len(part) < 3: continue
        z = zface((a + b) / 2) + 1.5 + (0.6 if "r" in nm[-2:] or nm.endswith("pole") or "crab" in nm or "bucket" in nm else 0)
        d.slab(f"{nm}-{k}" if n > 1 else nm, "front", P(part), [z - 1.2, z + 1.2], mat, soft=True)
for i, (bx, by) in enumerate(BUB):
    z = zface(bx) + 1.5
    d.slab(f"bub{i}", "front", ring(ell(bx, by, 17, 17, 14), ell(bx, by, 11, 11, 14)), [z - 1.2, z + 1.2], "bub", soft=True)
d.save()
