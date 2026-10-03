"""Small desktop stimulators of physio-3: XYD-II, XYZP-IB, XYZP-IC, XYZP-ID (table)."""
import sys
from p3lib import *

which = sys.argv[1:] or ["xyd-ii", "xyzp-ib", "xyzp-ic", "xyzp-id-table"]


def bevel_pt(z0, y0, z1, y1, f, out=0.0):
    """Point at fraction f along the bevel (z0,y0)→(z1,y1), pushed out along its normal by `out`."""
    dz, dy = z1 - z0, y1 - y0
    l = math.hypot(dz, dy)
    nz, ny = -dy / l, dz / l
    if ny < 0: nz, ny = -nz, -ny
    return z0 + dz * f + nz * out, y0 + dy * f + ny * out, (nz, ny)


# ------------------------------------------------------------------ XYD-II electroacupuncture
if "xyd-ii" in which:
    W, D_, H = 260, 180, 55
    d = D("xyd-ii", [W, D_, H], {"shell": "gloss#f3f4f6", "maroon": "plastic#6b3a3a", "panel": "plastic#8a9bb0",
                                  "header": "plastic#5cb3ea", "white": "gloss#f8f9fa", "rib": "plastic#3a3b3e", "knob": "rubber#151618", "cap": "metal#c9ccd0", "jack": "plastic#f8f8f8",
                                  "jack-hole": "rubber#1b1c1e", "warn": "gloss#f2cf2a", "led-y": "gloss#f0c419", "led-g": "gloss#3fd25a",
                                  "rocker": "rubber#141517", "ink": "plastic#1f2733", "logo": "gloss#2f6fbf"})
    # (photo: a maroon bottom shell ~20 high, the white top body bevelled at the front right from the shell up)
    ZB, YB = 146, 24     # bevel from (ZB, H) down to (D_, YB)
    d.box("bottom", [1, 0, 1, W - 1, 21, D_ - 1], "maroon", r=6)
    d.slab("body", "side", rpoly([(0, 18), (D_ - 1, 18), (D_ - 1, YB), (ZB, H), (0, H)], [4, 4, 6, 8, 6]), [0, W], "shell", r=6)
    d.box("panel", [8, H - 1, 8, W - 8, H + 1, ZB - 2], "panel", r=4)
    # sky-blue header along the back: deeper on the left, a diagonal step down to a narrow strip with the power switch
    d.slab("header", "top", poly([(12, 12), (W - 12, 12), (W - 12, 32), (196, 32), (182, 46), (12, 46)]), [H + 0.6, H + 1.6], "header")
    d.cyl("logo", [30, H + 1.4, 29], [30, H + 2, 29], 22, "white", soft=True)
    d.cyl("logo-c", [30, H + 1.8, 29], [30, H + 2.3, 29], 12, "logo", soft=True)
    d.box("title", [64, H + 1.4, 20, 150, H + 2, 32], "ink", soft=True)
    d.box("title-en", [64, H + 1.4, 35, 160, H + 2, 39], "ink", soft=True)
    d.box("brand", [46, H + 1.4, 20, 58, H + 2, 40], "ink", soft=True)
    d.box("rocker", [218, H + 1, 14, 238, H + 7, 28], "rocker", r=2)
    d.box("rocker-lab", [214, H + 1.4, 29, 242, H + 2, 31], "ink", soft=True)
    d.cyl("led-pw", [206, H + 1, 20], [206, H + 3, 20], 5, "led-g")
    d.box("slide", [60, H + 1, 62, 74, H + 4, 74], "rocker", r=1.5)
    # knobs (positions measured on the photo): frequency rear right, waveform, timer, the 6 outputs in a diagonal row
    knobs = [(222, 52), (182, 58), (108, 78)] + [(44 + 37.4 * k, 126 - 6.5 * k) for k in range(6)]
    for i, (x, z) in enumerate(knobs):
        d.add(f"knob{i}", "lathe", "knob", at=[x, H + 1, z], profile=[[0, 0], [9, 0], [9.5, 2.5], [9, 11], [7.5, 13], [0, 13]])
        d.add(f"rib{i}", "lathe", "rib", at=[x, H + 3, z], profile=[[9.3, 0], [9.9, 0], [9.6, 8], [9.1, 8]], soft=True)
        d.add(f"cap{i}", "lathe", "cap", at=[x, H + 13, z], profile=[[0, 0], [7, 0], [7, 1], [4, 2], [0, 2]], soft=True)
        d.cyl(f"led{i}", [x - 15, H + 1, z - 10], [x - 15, H + 2.5, z - 10], 4, "led-y", soft=True)
    # printed output lines from the knob row down to the front edge
    d.box("oline", [30, H + 1.1, ZB - 10, W - 30, H + 1.5, ZB - 9], "ink", soft=True)
    # front bevel: 6 white output jacks and 2 yellow warning labels
    for k in range(6):
        z, y, (nz, ny) = bevel_pt(ZB, H, D_, YB, 0.5)
        x = 40 + 36 * k
        d.cyl(f"jack{k}", [x, y, z], [x, y + ny * 3, z + nz * 3], 9, "jack")
        d.cyl(f"jack{k}-h", [x, y + ny * 2.5, z + nz * 2.5], [x, y + ny * 3.6, z + nz * 3.6], 4, "jack-hole", soft=True)
    ang = math.degrees(math.atan2(H - YB, D_ - ZB))
    for i, x in enumerate((20, 232)):
        d.box(f"warn{i}", [x - 7, H, ZB + 6, x + 7, H + 1.2, ZB + 22], "warn", soft=True, rot=rot("x", ang, [0, H, ZB]))
    # DC socket on the right end
    d.box("dc", [W - 0.5, 28, 40, W + 1.5, 44, 58], "rocker", r=2)
    d.save()

# ------------------------------------------------------------------ XYZP-IB portable medium frequency
if "xyzp-ib" in which:
    W, D_ = 300, 200
    d = D("xyzp-ib", [W, D_, 76], {"shell": "gloss#f4f5f7", "violet": "plastic#c9a6d6", "membrane": "plastic#e6e7ea",
                                    "pink": "gloss#d7a2cf", "black": "gloss#141517", "red": "gloss#e2342b", "dot": "plastic#3a3d42",
                                    "key-p": "gloss#d9a6d0", "key-b": "gloss#2e4a6e", "logo": "plastic#b07fb5", "ink": "plastic#3a3340"})
    # (photo: a thin violet band at the bottom (~40 % of the low front), white wedge rising to the back)
    YF, YR, ZR = 34, 72, 14
    d.box("band", [0, 0, 0, W, 15, D_], "violet", r=7)
    d.slab("body", "side", rpoly([(0, 12), (D_, 12), (D_, YF), (ZR, YR), (0, YR)], [4, 4, 10, 10, 8]), [0, W], "shell", r=12)
    ang = math.degrees(math.atan2(YR - YF, D_ - ZR))
    t = Tilt(YF, D_, ang)
    Lb = math.hypot(YR - YF, D_ - ZR)
    # membrane with a thin pink outline
    t.box(d, "membrane-edge", 10, 10, W - 10, Lb - 6, -1.2, 0.6, "pink", r=6)
    t.box(d, "membrane", 12.5, 12.5, W - 12.5, Lb - 8.5, -1, 1, "membrane", r=5)
    # pink header along the back: narrow on the left, a diagonal step to a deep pink corner holding the black display
    hdr = [(14, Lb - 40), (176, Lb - 40), (196, Lb - 64), (W - 14, Lb - 64), (W - 14, Lb - 9), (14, Lb - 9)]
    # the slab is drawn in the tilt frame: local (x, s) → plane top outline in (x, z) with z = D_ − s, then turned
    d.slab("header", "top", poly([(x, D_ - sv) for x, sv in hdr]), [YF + 0.8, YF + 1.6], "pink", rot=t.r)
    t.box(d, "logo", 22, Lb - 36, 44, Lb - 14, 1.4, 2, "logo", soft=True)
    t.box(d, "title", 70, Lb - 54, 160, Lb - 46, 1.0, 1.6, "ink", soft=True)
    t.box(d, "title2", 40, Lb - 61, 175, Lb - 58, 1.0, 1.6, "ink", soft=True)
    t.box(d, "disp", 236, Lb - 50, 272, Lb - 18, 1.2, 2.6, "black", r=3)
    t.box(d, "line", 14, 24, W - 14, 30, 0.8, 1.6, "pink", soft=True)
    t.box(d, "line-r", 176, 34, W - 14, 46, 0.8, 1.6, "pink", soft=True)
    t.box(d, "line-r2", 176, 50, W - 14, 56, 0.8, 1.6, "pink", soft=True)
    t.box(d, "led", 84, 70, 124, 94, 0.8, 2, "black", r=2)
    t.box(d, "led-d", 90, 74, 102, 90, 1.8, 2.4, "red", soft=True, copies=[[16, 0, 0]])
    t.box(d, "dots", 84, 56, 88, 60, 0.8, 2, "dot", soft=True, repeat=rep(6, [7, 0, 0]))
    for i, (x, s, m) in enumerate(((160, 104, "key-p"), (192, 112, "key-p"), (168, 78, "key-p"), (200, 86, "key-p"),
                                   (232, 120, "key-b"), (238, 94, "key-b"))):
        t.box(d, f"key{i}", x, s, x + 22, s + 16, 0.8, 3, m, r=3)
    d.save()

# ------------------------------------------------------------------ XYZP-IC pebble
if "xyzp-ic" in which:
    # (photo: a low wide unit, straight sides with big corner radii; a blue basin tapering to the bottom under a white
    # lid that overhangs it; a large black island at the back right, the keys in pairs on an arc round its front-left)
    W, D_ = 300, 230
    d = D("xyzp-ic", [W, D_, 76], {"shell": "gloss#f4f5f7", "skirt": "gloss#6eaeea", "island": "gloss#121315",
                                    "lcd": "gloss#62b8f2", "seg": "gloss#1d3f86", "btn-w": "gloss#f2f3f5", "btn-b": "gloss#5aa0e6",
                                    "btn-g": "plastic#8d939a", "ink": "plastic#8a9099", "foot": "rubber#1b1c1e", "dot": "plastic#c9ced4"})
    CX, CZ = W / 2, D_ / 2
    d.add("skirt", "loft", "skirt", sections=[
        {"at": 2, "w": 252, "d": 186, "r": 62, "cx": CX, "cz": CZ}, {"at": 22, "w": 280, "d": 212, "r": 72, "cx": CX, "cz": CZ},
        {"at": 46, "w": 294, "d": 224, "r": 78, "cx": CX, "cz": CZ}])
    d.add("lid", "loft", "shell", sections=[
        {"at": 44, "w": 294, "d": 224, "r": 78, "cx": CX, "cz": CZ}, {"at": 51, "w": 300, "d": 230, "r": 80, "cx": CX, "cz": CZ},
        {"at": 57, "w": 298, "d": 228, "r": 79, "cx": CX, "cz": CZ}, {"at": 60, "w": 286, "d": 216, "r": 74, "cx": CX, "cz": CZ}])
    d.add("top", "loft", "shell", sections=[
        {"at": 59, "w": 284, "d": 214, "r": 73, "cx": CX, "cz": CZ}, {"at": 64, "w": 276, "d": 206, "r": 70, "cx": CX, "cz": CZ}],
          dome="end", domeH=3)
    IX, IZ, IW, ID = 178, 86, 212, 128
    d.add("island", "loft", "island", sections=[
        {"at": 63, "w": IW, "d": ID, "r": 58, "cx": IX, "cz": IZ}, {"at": 70, "w": IW - 4, "d": ID - 4, "r": 56, "cx": IX, "cz": IZ}],
          dome="end", domeH=1.5)
    Y = 71.5
    LX, LZ = IX - 22, IZ - 2
    d.box("lcd", [LX - 50, Y, LZ - 31, LX + 50, Y + 1, LZ + 31], "lcd", r=3)
    # '20-07' in segments and the two gauge arcs at the LCD ends
    SEG = {"2": "abged", "0": "abcdef", "7": "abc"}
    def digit(id_, x0, ch):
        w, h, t = 15, 26, 3
        z0 = LZ - h / 2
        segs = {"a": (x0, z0, x0 + w, z0 + t), "g": (x0, z0 + h / 2 - t / 2, x0 + w, z0 + h / 2 + t / 2), "d": (x0, z0 + h - t, x0 + w, z0 + h),
                "f": (x0, z0, x0 + t, z0 + h / 2), "b": (x0 + w - t, z0, x0 + w, z0 + h / 2),
                "e": (x0, z0 + h / 2, x0 + t, z0 + h), "c": (x0 + w - t, z0 + h / 2, x0 + w, z0 + h)}
        for k in SEG[ch]:
            xa, za, xb, zb = segs[k]
            d.box(f"{id_}{k}", [xa, Y + 0.8, za, xb, Y + 1.4, zb], "seg", soft=True)
    for i, (x0, ch) in enumerate(((LX - 38, "2"), (LX - 19, "0"), (LX + 6, "0"), (LX + 25, "7"))):
        digit(f"d{i}", x0, ch)
    d.box("dash", [LX - 2, Y + 0.8, LZ - 1.5, LX + 4, Y + 1.4, LZ + 1.5], "seg", soft=True)
    for side, a0 in (("l", 120), ("r", -60)):
        cx = LX - 30 if side == "l" else LX + 30
        pts = [[cx + 24 * math.cos(math.radians(a)), Y + 1.2, LZ + 24 * math.sin(math.radians(a))] for a in range(a0, a0 + 121, 20)]
        d.tube(f"arc-{side}", pts, 2.5, "seg", soft=True)
    d.box("ink", [LX - 50, Y - 0.6, LZ + 36, LX, Y - 0.2, LZ + 39], "ink", soft=True, copies=[[0, 0, 6]])
    d.box("grid", [LX + 18, Y - 0.6, LZ + 36, LX + 21, Y - 0.2, LZ + 39], "dot", soft=True, repeat=rep(5, [7, 0, 0]), copies=[[0, 0, 7], [0, 0, 14]])
    d.cyl("brand", [IX - 80, Y - 1, IZ - 50], [IX - 80, Y - 0.2, IZ - 50], 9, "btn-b", soft=True)
    d.box("title", [IX - 30, Y - 0.6, IZ - 54, IX + 60, Y - 0.2, IZ - 50], "ink", soft=True)
    # keys: 6 radial pairs on an arc round the island's front-left corner
    ox, oz = IX - IW / 2 + 58, IZ + ID / 2 - 58
    cols = [("btn-w", "btn-w"), ("btn-w", "btn-w"), ("btn-b", "btn-g"), ("btn-b", "btn-g"), ("btn-w", "btn-w"), ("btn-w", "btn-w")]
    for i, tdeg in enumerate((5, 25, 45, 65, 85, 105)):
        tr = math.radians(tdeg)
        for j, R in enumerate((78, 100)):
            x, z = ox - R * math.cos(tr), oz + R * math.sin(tr)
            m = cols[i][j]
            big = m != "btn-w"
            d.box(f"btn{i}{j}", [x - (9 if big else 8), 63, z - (6 if big else 4.5), x + (9 if big else 8), 69.5, z + (6 if big else 4.5)], m,
                  r=3 if not big else 5.5, rot=rot("y", 90 - tdeg, [x, 63, z]))
    d.save()

# ------------------------------------------------------------------ XYZP-ID table type
if "xyzp-id-table" in which:
    S = 380
    d = D("xyzp-id-table", [S, S, 200], {"shell": "gloss#f4f5f7", "blue": "gloss#2f74c9", "glass": "gloss#1b1d21",
                                         "frame": "gloss#9cc8f0", "panel": "plastic#e9ecef", "sock": "metal#b4b9be",
                                         "sock-c": "plastic#6f757c", "red": "gloss#e2342b", "win": "plastic#2a2c30", "key": "plastic#d8dadd",
                                         "line": "plastic#b07a3c", "vent": "plastic#1f4f8c", "foot": "rubber#1b1c1e",
                                         "field": "plastic#6f9fdc", "line2": "plastic#2f5f9c"})
    sq = lambda a, b, rr: rpoly([(a, a), (b, a), (b, b), (a, b)], rr)
    # (photo: the blue body shows high on the sides; the white cap is a thin band at the back and sides and comes down
    # over the front as an apron - a loft whose depth grows upwards; the big socket window sits in that apron)
    d.slab("blue", "top", rpoly([(8, 6), (S - 8, 6), (S - 8, S - 10), (8, S - 10)], 58), [4, 192], "blue", r=16)
    d.slab("white", "top", sq(0, S, 64), [150, 194], "shell", r=16)
    d.add("apron", "loft", "shell", sections=[
        {"at": 36, "w": S - 6, "d": 74, "r": 34, "cx": S / 2, "cz": S - 4 - 37},
        {"at": 80, "w": S - 4, "d": 150, "r": 58, "cx": S / 2, "cz": S - 3 - 75},
        {"at": 120, "w": S - 2, "d": 262, "r": 63, "cx": S / 2, "cz": S - 2 - 131},
        {"at": 154, "w": S - 1, "d": S - 1, "r": 64, "cx": S / 2, "cz": S / 2}])
    d.slab("glass", "top", sq(16, S - 16, 50), [190, 197], "glass", r=4)
    # four channel blocks framed by thin orange lines: red digit windows, a small 1-digit window, small round keys
    for i, (bx, bz) in enumerate(((36, 50), (200, 50), (36, 200), (200, 200))):
        for j, bb in enumerate(([bx - 8, bz - 10, bx + 152, bz - 8.5], [bx - 8, bz + 126.5, bx + 152, bz + 128],
                                [bx - 8, bz - 10, bx - 6.5, bz + 128], [bx + 150.5, bz - 10, bx + 152, bz + 128])):
            d.box(f"line{i}{j}", [bb[0], 197, bb[1], bb[2], 197.6, bb[3]], "line", soft=True)
        d.box(f"win{i}", [bx + 10, 197, bz + 22, bx + 40, 198, bz + 44], "win", soft=True, copies=[[42, 0, 0]])
        d.box(f"dig{i}", [bx + 16, 197.6, bz + 26, bx + 34, 198.4, bz + 40], "red", soft=True, copies=[[42, 0, 0]])
        d.box(f"dig{i}s", [bx + 100, 197.6, bz + 26, bx + 108, 198.4, bz + 40], "red", soft=True)
        for k, (kx, kz) in enumerate(((bx + 20, bz + 64), (bx + 44, bz + 64), (bx + 108, bz + 64), (bx + 120, bz + 64), (bx + 70, bz + 100))):
            d.add(f"key{i}{k}", "lathe", "key", at=[kx, 197, kz], profile=[[0, 0], [7, 0], [7, 1.5], [0, 2]], soft=True)
    d.box("logo", [26, 197, 24, 50, 198, 34], "frame", soft=True)
    d.box("title", [120, 197, 26, 260, 197.8, 31], "key", soft=True)
    # front socket window: thick light-blue rim, recessed blue field with printed diagonals, 8 grey sockets rising to the right
    d.box("sock-frame", [56, 43, S - 14, 324, 167, S + 1], "frame", r=14)
    d.box("sock-panel", [67, 54, S - 6, 313, 156, S + 2], "field", r=8)
    for k, ((x0, y0), (x1, y1)) in enumerate((((80, 62), (200, 150)), ((140, 62), (260, 150)), ((200, 62), (305, 140)))):
        L_ = math.hypot(x1 - x0, y1 - y0)
        d.box(f"pline{k}", [x0, y0, S + 1.8, x0 + L_, y0 + 1.2, S + 2.4], "line2", soft=True, rot=rot("z", math.degrees(math.atan2(y1 - y0, x1 - x0)), [x0, y0, S]))
    for k, (x, y) in enumerate(((132, 74), (178, 82), (220, 92), (260, 104), (154, 101), (204, 109), (244, 122), (284, 135))):
        d.cyl(f"sock{k}", [x, y, S - 2], [x, y, S + 8], 23, "sock-c")
        d.cyl(f"sockh{k}", [x, y, S + 6], [x, y, S + 15], 21, "sock")
    # vent grille low on the left side of the blue part
    d.box("vent", [7, 28, 145, 9.5, 31, 225], "vent", soft=True, repeat=rep(7, [0, 7, 0]))
    d.cyl("foot", [50, 0, 50], [50, 6, 50], 30, "foot", copies=[[280, 0, 0], [0, 0, 270], [280, 0, 270]])
    d.save()
