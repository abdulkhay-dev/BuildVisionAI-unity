from h2lib import *
# XY-SL-RV mobile baby swimming tub and XY-SL-RIV (same body, microcomputer control). Photos: front, slightly from the
# left. White cabinet on 4 castors; the front green with a wave-shaped lower edge and a border line (two humps: over the
# knee recess at the left and around the cartoon at the right), white below; a cartoon sticker (umbrella, crabs, sand,
# bucket), fish and bubbles; white deck with an oval tub (green basin in RV, white in RIV), blue dots round it; a raised
# block at the back right with green cups and a green handle, a chrome gooseneck faucet; a green fold-out tray at the
# right end on a chrome bracket.
import sys


def build(id, basin_col, border_col, faucet_x, riv=False):
    W, DP, H = 1300, 700, 960
    CW = 1000                    # cabinet width; the tray adds 300
    DY = 720                     # deck top
    d = D(id, [W, DP, H], {
        "shell": "gloss#f7f8f9", "green": "gloss#4fb848", "border": border_col, "basin": basin_col,
        "blue": "gloss#2f6fd0", "water": "acrylic#cfe8e070", "dark": "black#2b2f35"})
    Y0 = 125
    d.box("cabinet", [0, Y0, 0, CW, DY - 28, DP], "shell", r=18)
    # Review 2026-10-02: both photos are front-LEFT views with the near corner at x~420 (RV) / ~345 px (RIV): the cartoon
    # face is the long front (1000), the knee arch with its split line is on the LEFT END (700) where the nurse sits.
    # The raised block is at the RIGHT end over the full depth: its white left face (green recessed handle) faces the
    # basin, its front is green flush with the front, a step down at the right under the tray; the faucet stands on the
    # deck at the block's front-left corner and arches back over the basin.
    t, r = DY - 30, CW - 6
    segs = [((r, 280), (900, 290), (840, 320), (810, 400)), ((810, 400), (790, 500), (770, 565), (680, 568)),
            ((680, 568), (580, 570), (530, 550), (500, 450)), ((500, 450), (480, 360), (470, 250), (420, 250))]
    curve = []
    for p0, p1, p2, p3 in segs:
        for k in range(12):
            u = k / 12
            curve.append(tuple((1 - u) ** 3 * p0[i] + 3 * (1 - u) ** 2 * u * p1[i] + 3 * (1 - u) * u * u * p2[i] + u ** 3 * p3[i]
                               for i in range(2)))
    curve += [(420, 250), (6, 250)]
    green = [(6, t), (r, t)] + curve
    d.slab("wave", "front", P(green), [DP - 2, DP + 4], "green", r=1.5)
    bord = [(min(max(x, 6), r), min(max(y, 135), t)) for x, y in offset(green, 20)]
    d.slab("wave-border", "front", P(bord), [DP - 1, DP + 2], "border", r=1)
    # left end: green with the white knee arch (split line in it), border band around it
    arch = [(6, t), (DP - 6, t), (DP - 6, 250)]
    for k in range(25):
        a = math.pi * k / 24
        arch.append((372 + 300 * math.cos(a), 250 + 275 * math.sin(a) ** 0.8))
    arch.append((6, 250))
    d.slab("wave-l", "side", P(arch), [-4, 2], "green", r=1.5)
    bl = [(min(max(z, 6), DP - 6), min(max(y, 135), t)) for z, y in offset(arch, 20)]
    d.slab("wave-l-border", "side", P(bl), [-3, 3], "border", r=1)
    d.box("split", [-2, Y0 + 10, 330, 1, 480, 336], "plastic#d6dbe0", r=1, soft=True, copies=[[0, 0, 30]])
    # cartoon sticker in the right hump: white oval, umbrella, crabs, sand, bucket; fish and bubbles below
    CX, CY = 650, 390
    d.slab("cartoon", "front", P(ell(CX, CY, 140, 145)), [DP + 1, DP + 5], "gloss#eef3f6", r=1)
    d.slab("sand", "front", P(ell(CX, CY - 95, 125, 32)), [DP + 4, DP + 6], "gloss#a8a397", r=0.5)
    d.slab("umbrella", "front", f"M {CX - 85} {CY + 75} Q {CX} {CY + 165} {CX + 85} {CY + 75} Z", [DP + 4, DP + 7], "gloss#2e4fc0", r=0.5)
    d.slab("umbrella-in", "front", f"M {CX - 40} {CY + 78} Q {CX} {CY + 135} {CX + 40} {CY + 78} Z", [DP + 6, DP + 8], "gloss#7a2f90", r=0.5)
    d.box("umbrella-pole", [CX - 2, CY - 95, DP + 5, CX + 2, CY + 120, DP + 8], "dark", r=1, soft=True)
    for i, (x, y, s) in enumerate([(CX - 55, CY - 40, 30), (CX + 15, CY - 65, 18)]):
        d.lathe(f"crab{i}", [x, y, DP + 5], [[0, 0], [s, 0], [s, 3], [0, 3]], "gloss#d83a2e", axis="z", soft=True)
        d.box(f"crab{i}-c", [x - s * 1.4, y + s * 0.6, DP + 5, x + s * 1.4, y + s * 0.8, DP + 8], "gloss#d83a2e", r=2, soft=True)
    d.box("bucket", [CX + 70, CY - 60, DP + 5, CX + 110, CY - 10, DP + 8], "gloss#2f9a4a", r=3, soft=True)
    d.slab("fish1", "front", P(ell(360, 150, 26, 11)) + " " + "M 382 150 L 400 162 L 400 138 Z", [DP + 4, DP + 6], "gloss#8a4fb8", r=0.5)
    d.slab("fish2", "front", P(ell(560, 215, 22, 10)) + " " + "M 580 215 L 596 226 L 596 204 Z", [DP + 4, DP + 6], "gloss#3aa04a", r=0.5)
    for i, (x, y, s) in enumerate([(330, 120, 8), (420, 175, 9), (450, 135, 7), (480, 210, 6), (520, 160, 10),
                                   (600, 175, 7), (640, 240, 8), (700, 210, 9), (740, 250, 7), (780, 280, 10), (300, 190, 6)]):
        d.lathe(f"bub{i}", [x, y, DP + 2], [[0, 0], [s, 0], [s, 2], [0, 2]], "gloss#3f7fe0", axis="z", soft=True)
    # deck with the oval tub at the left
    hole = ell(375, 350, 320, 278, 56)
    deck = rr(-4, -4, CW + 4, DP + 4, 16)
    tub(d, "", None, hole, deck, DY - 30, 30, 420, offset(hole, 26), mat="shell", inner="basin")
    d.slab("water", "top", P(offset(hole, 3)), [430, 650], "water", r=2, soft=True)
    for i in range(10):
        a = math.radians(i * 36 + 18)
        d.lathe(f"dot{i}", [375 + 340 * math.cos(a), DY - 1, 350 + 296 * math.sin(a)], [[0, 0], [7, 0], [7, 2], [0, 3]],
                "blue", soft=True)
    # raised block at the right end over the full depth, stepped down at the right; green front; green handle on its
    # left face; green cups / inlay on top
    BX = 745
    d.box("block-a", [BX, DY - 4, 8, 950, 950, DP - 8], "shell", r=20)
    d.box("block-b", [944, DY - 4, 8, CW, 900, DP - 8], "shell", r=14)
    d.box("block-front", [BX + 12, DY - 4, DP - 10, 950, 948, DP - 2], "green", r=8)
    d.box("block-front-b", [948, DY - 4, DP - 10, CW, 898, DP - 2], "green", r=6)
    d.box("handle", [BX - 6, 840, 140, BX + 4, 884, 560], "green", r=10)
    d.box("handle-in", [BX - 8, 850, 160, BX + 2, 874, 540], "gloss#3a9a3c", r=6, soft=True)
    if riv:
        d.lathe("cup1", [800, 948, 90], [[0, 0], [40, 0], [40, 12], [28, 12], [28, 4], [0, 4]], "green")
        d.lathe("cup2", [800, 948, 200], [[0, 0], [36, 0], [36, 12], [26, 12], [26, 4], [0, 4]], "green")
    else:
        d.box("inlay", [BX + 8, 946, 20, 900, 954, 190], "green", r=6)
    d.lathe("cup3", [880, 948, 600], [[0, 0], [46, 0], [46, 12], [34, 12], [34, 4], [0, 4]], "green")
    d.lathe("tap", [880, 950, 600], [[0, 0], [10, 0], [10, 26], [6, 32], [0, 32]], "gloss#b8933a")
    # chrome gooseneck faucet on the deck at the block's front-left corner, arching back over the basin
    fx, fz = faucet_x, 600
    d.lathe("faucet-base", [fx, DY, fz], [[0, 0], [26, 0], [26, 50], [16, 60], [0, 60]], "chrome")
    d.cyl("faucet-lever", [fx, DY + 40, fz], [fx - 45, DY + 50, fz + 40], 14, "chrome")
    d.tube("faucet", [[fx, DY + 50, fz], [fx, H - 10, fz], [fx - 10, H - 10, fz - 200], [fx - 20, 885, fz - 250]], 18, "chrome", bend=90)
    d.lathe("faucet-head", [fx - 20, 845, fz - 252], [[0, 0], [22, 0], [20, 30], [12, 50], [0, 50]], "dark")
    # fold-out green tray at the right end over the step, on dark folding struts
    d.box("tray", [CW - 70, 902, 70, W, 924, 640], "green", r=8)
    d.box("tray-lip", [W - 30, 916, 70, W, 946, 640], "green", r=8)
    d.box("tray-lip-b", [CW + 20, 916, 70, W, 938, 95], "green", r=6)
    d.bar("bracket", [CW, 640, 140], [CW + 200, 900, 140], [14, 14], "black#3a3f45", r=4, copies=[[0, 0, 420]])
    d.bar("bracket2", [CW, 620, 160], [CW + 130, 900, 160], [10, 10], "black#3a3f45", r=3, copies=[[0, 0, 380]])
    # castors
    d.add("castor", "caster", at=[90, 0, 110], d=100, mat="rubber#7b8088", copies=[[820, 0, 0], [0, 0, 480], [820, 0, 480]])
    d.save()


build("xy-sl-rv", "gloss#bfe3a8", "gloss#2f9a4a", 715)
build("xy-sl-riv", "gloss#eef1f4", "gloss#66c4a2", 715, riv=True)
