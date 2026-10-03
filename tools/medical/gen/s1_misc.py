"""Batch sensory-1, the single devices: butterfly-fiber-falls, colorful-fluorescent-drawing-board, color-led-ball,
led-piano-pedals, lighting-color-changing-puzzle-table, multi-sensory-master-control-machine,
multi-sensory-matching-projection-system, bean-bag. Usage: s1_misc.py [id ...]"""
import math, sys
from s1lib import *


def scale_pts(pts, s, c):
    return [(c[0] + (x - c[0]) * s, c[1] + (y - c[1]) * s) for x, y in pts]


def mirror_half(half, cx):
    """Left half (from top centre round to the bottom tip) → closed symmetric outline."""
    right = [(2 * cx - x, y) for x, y in reversed(half)]
    return half + right[1:-1]


# ------------------------------------------------------------------------------------------------ butterfly
def butterfly():
    W, Dp, H = 600, 100, 1800
    d = D("butterfly-fiber-falls", [W, Dp, H], {
        "edge": "plastic#f0d21c", "green": "plastic#86c024", "wing": "gloss#f6dc44", "rim": "plastic#e6c812",
        "sheath": "plastic#e2d115"})
    cx, y0, su = 300, 1226, 1.1
    def P(u, v): return (cx + u * su, y0 + v)
    # outline traced on the photo about the body's centre line (left half, mirrored): rounded upper-wing lobes with a
    # V between them, a small waist on each side, lower lobes narrowing to the tail point
    half = [P(*q) for q in [(0, 499), (-41, 522), (-91, 538), (-150, 545), (-201, 542), (-243, 531), (-264, 507),
                            (-270, 456), (-262, 372), (-248, 300), (-234, 262), (-214, 242), (-220, 218), (-214, 175),
                            (-192, 128), (-152, 96), (-110, 86), (-80, 79), (-63, 68), (-53, 46), (-40, 14), (-20, 2),
                            (0, 0)]]
    outline = round_poly(mirror_half(half, cx), 14, 3)
    cen = (cx, y0 + 300)
    front_slab(d, "body", outline, 0, Dp - 3, "edge", r=14)
    front_slab(d, "face", scale_pts(outline, 0.955, cen), Dp - 4, Dp, "green", r=2)
    ring = path(scale_pts(outline, 0.925, cen)) + " " + path(list(reversed(scale_pts(outline, 0.905, cen))))
    front_slab(d, "line", ring, Dp, Dp + 1, "edge", soft=True)
    wing = [(-226, 452), (-150, 444), (-66, 427), (-36, 406), (-30, 346), (-30, 245), (-26, 152), (-41, 118), (-100, 106),
            (-167, 118), (-201, 169), (-235, 245), (-226, 270), (-239, 346), (-235, 422)]
    for side, sx in (("L", 1), ("R", -1)):
        pts = round_poly([P(sx * u, v) for u, v in wing], 30, 4)
        if sx < 0:
            pts = list(reversed(pts))
        wc = P(sx * -135, 280)
        front_slab(d, "rim" + side, scale_pts(pts, 1.05, wc), Dp, Dp + 2, "rim", soft=True)
        front_slab(d, "wing" + side, pts, Dp + 1, Dp + 3.5, "wing", r=1.5)
        for i, (u, v, dd) in enumerate([(-193, 412, 34), (-163, 330, 51), (-112, 177, 72)]):
            x, y = P(sx * u, v)
            disc(d, f"spot{side}{i}", x, y, Dp + 3.5, dd, "green", h=1.2)
        # antenna
        ant = [P(sx * u, v) for u, v in [(-12, 372), (-34, 418), (-66, 456), (-100, 486), (-130, 506), (-150, 503), (-146, 488)]]
        strokes(d, "ant" + side, [ant], Dp + 1.2, 8, "wing")
    # body (as on the photo: green with yellow lines): a round head ringed in yellow with a flower of yellow dots and two
    # small feelers, a thorax and abdomen outlined in yellow with 5 yellow chevrons across, and a yellow pointed tail
    hx, hy = P(0, 342)
    front_slab(d, "head", ring_path(hx, hy, 18, 23, 28), Dp, Dp + 2.5, "wing", soft=True)
    for i, (u, v) in enumerate([(0, 9), (-8, 2), (8, 2), (-5, -7), (5, -7)]):
        disc(d, f"hdot{i}", hx + u, hy + v, Dp, 6, "wing", h=2.2)
    strokes(d, "feel", [[(hx - 12, hy + 20), (hx - 20, hy + 32), (hx - 12, hy + 36)],
                        [(hx + 12, hy + 20), (hx + 20, hy + 32), (hx + 12, hy + 36)]], Dp + 1.0, 4, "wing")
    body = [(cx, y0 + 318), (cx + 20, y0 + 308), (cx + 26, y0 + 280), (cx + 23, y0 + 240), (cx + 15, y0 + 190),
            (cx + 6, y0 + 160)]
    strokes(d, "bodyline", [body, [(2 * cx - x, y) for x, y in body]], Dp + 1.0, 4, "wing")
    for k in range(5):
        y = y0 + 300 - k * 24
        hw = 24 - k * 3.5
        strokes(d, f"chev{k}", [[(cx - hw, y), (cx, y - 9), (cx + hw, y)]], Dp + 1.2, 7, "wing")
    front_slab(d, "tail", [(cx - 14, y0 + 160), (cx + 14, y0 + 160), (cx, y0 + 116)], Dp, Dp + 2.5, "wing", soft=True)
    # ribbed yellow fibre sheath from behind the bottom down to the floor, a smooth curve to the left
    def bez(t, p0, p1, p2, p3):
        return [round((1 - t) ** 3 * a + 3 * (1 - t) ** 2 * t * b + 3 * (1 - t) * t * t * c + t ** 3 * e, 1)
                for a, b, c, e in zip(p0, p1, p2, p3)]
    sheath = [bez(k / 14, [350, 1300, 45], [345, 950, 50], [235, 760, 50], [232, 40, 50]) for k in range(15)]
    d.tube("sheath", sheath, 62, "sheath", bend=60, rib=3, pitch=14)
    d.cyl("tip", [232, 40, 50], [232, 10, 50], 64, "sheath", d2=58)
    d.save()


# ------------------------------------------------------------------------------------------------ drawing board
def drawing_board():
    W, Dp, H = 1200, 50, 800
    FW = 62                               # frame width measured on the photo (sides ~70, top/bottom ~55)
    d = D("colorful-fluorescent-drawing-board", [W, Dp, H], {
        "frame": "wood#3e231c", "bevel": "wood#5a3a2c", "board": "gloss#173a62", "glow": "gloss#b4e05a",
        "stick": "gloss#d8f0a0"})
    fr = path(rrect_pts(0, 0, W, H, 6)) + " " + path(list(reversed(rrect_pts(FW, FW, W - FW, H - FW, 2))))
    front_slab(d, "frame", fr, 0, Dp, "frame", r=10)
    bev = path(rrect_pts(FW - 12, FW - 12, W - FW + 12, H - FW + 12, 3)) + " " + path(list(reversed(rrect_pts(FW, FW, W - FW, H - FW, 2))))
    front_slab(d, "bevel", bev, Dp - 14, Dp - 2, "bevel", r=3)
    d.box("board", [FW - 1, FW - 1, 0, W - FW + 1, H - FW + 1, Dp - 12], "board", r=1)
    # photo pixels (480 x 332; frame outer x 10-472, y 12-318) → mm
    def M(x, y): return ((x - 10) * 1200 / 462, 800 - (y - 12) * 800 / 306)
    z = Dp - 12 + 0.3
    rim = [M(235 + 80 * math.cos(a), 124 + 15 * math.sin(a)) for a in [2 * math.pi * k / 20 for k in range(21)]]
    left = [M(155, 125), M(153, 150), M(162, 180), M(182, 210), M(205, 229)]
    right = [M(315, 124), M(312, 150), M(300, 180), M(282, 208), M(262, 229)]
    foot = [M(205, 228), M(205, 237), M(262, 237), M(262, 228)]
    waves = []
    for k, (xa, xb) in enumerate(((172, 212), (198, 226), (226, 242), (254, 256))):
        waves.append([M(xa + (xb - xa) * j / 6 + 7 * math.sin(j * 1.6 + k * 0.8), 140 + j * 14) for j in range(7)])
    strokes(d, "draw", [rim, left, right, foot] + waves, z, 11, "glow")
    # the two chopsticks: bright outlined sticks with a paler fill, from inside the bowl up to the upper right
    for i, (a, b) in enumerate(((M(217, 124), M(286, 52)), (M(242, 124), M(307, 62)))):
        dx, dy = b[0] - a[0], b[1] - a[1]; ln = math.hypot(dx, dy); nx, ny = -dy / ln * 13, dx / ln * 13
        strokes(d, f"stickfill{i}", [[a, b]], z, 22, "stick")
        strokes(d, f"stick{i}", [[(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]],
                z + 0.3, 7, "glow")
    d.save()


# ------------------------------------------------------------------------------------------------ LED ball
def led_ball():
    W, Dp, H = 300, 300, 450
    d = D("color-led-ball", [W, Dp, H], {"white": "plastic#f2f3f4", "ball": "chrome", "led": "led", "cap": "plastic#2a2d30", "seam": "plastic#8a8f95"})
    c = 150
    d.cyl("plate", [c, H - 10, c], [c, H, c], 120, "white")
    d.cyl("motor", [c, H - 58, c], [c, H - 10, c], 72, "white")
    d.cyl("rod", [c, 290, c], [c, H - 58, c], 14, "chrome")
    prof = [[0, 0]] + [[round(150 * math.sin(math.pi * k / 12), 1), round(150 - 150 * math.cos(math.pi * k / 12), 1)] for k in range(1, 12)] + [[0, 300]]
    d.lathe("ball", [c, 0, c], prof, "ball", sides=20)
    # mirror facets: a fine grid of seams (17 latitudes, 24 meridians → ~40 mm tiles like a mirror ball)
    for k, lat in enumerate(range(-80, 81, 10)):
        r = 151 * math.cos(math.radians(lat)); y = 150 + 151 * math.sin(math.radians(lat))
        n = max(8, int(36 * math.cos(math.radians(lat))))
        d.tube(f"lat{k}", [[c + r * math.cos(2 * math.pi * j / n), y, c + r * math.sin(2 * math.pi * j / n)] for j in range(n + 1)],
               2, "seam", soft=True)
    for k in range(24):
        q = math.pi * k / 24
        d.tube(f"mer{k}", [[c + 151 * math.cos(math.radians(t)) * math.cos(q), 150 + 151 * math.sin(math.radians(t)),
                            c + 151 * math.cos(math.radians(t)) * math.sin(q)] for t in range(-80, 261, 10)], 2, "seam", soft=True)
    # the photo's light: a ring of ~18 small LEDs, 6 middle ones and 3 bright ones in the middle, in a dark window on
    # the lower front of the ball
    el = math.radians(-35)
    nrm = (0.0, math.sin(el), math.cos(el))                 # outward axis of the cluster
    t1 = (1.0, 0.0, 0.0); t2 = (0.0, math.cos(el), -math.sin(el))
    def on_ball(u, v, lift=0.0):
        rr = 151 + lift
        dx = nrm[0] * 151 + t1[0] * u + t2[0] * v; dy = nrm[1] * 151 + t1[1] * u + t2[1] * v; dz = nrm[2] * 151 + t1[2] * u + t2[2] * v
        L = math.sqrt(dx * dx + dy * dy + dz * dz)
        return [round(c + dx / L * rr, 1), round(150 + dy / L * rr, 1), round(c + dz / L * rr, 1)]
    ctr = on_ball(0, 0)
    cap = [[round(153 * math.sin(math.radians(a)), 1), round(153 * math.cos(math.radians(a)), 1)] for a in range(24, -1, -4)]
    d.lathe("ledwin", [c, 150, c], cap, "cap", soft=True, caps=False, sides=32, rot=rot("x", 125, [c, 150, c]))
    pts = [on_ball(50 * math.cos(2 * math.pi * k / 18), 50 * math.sin(2 * math.pi * k / 18), 3) for k in range(18)]
    pts += [on_ball(28 * math.cos(2 * math.pi * k / 6 + 0.5), 28 * math.sin(2 * math.pi * k / 6 + 0.5), 3) for k in range(6)]
    d.sphere("led", pts[0], 10, "led", soft=True, copies=[[round(p[i] - pts[0][i], 1) for i in range(3)] for p in pts[1:]])
    big = [on_ball(-9, 6, 4), on_ball(9, 8, 4), on_ball(4, -9, 4)]
    d.sphere("ledc", big[0], 15, "led", soft=True, copies=[[round(p[i] - big[0][i], 1) for i in range(3)] for p in big[1:]])
    d.save()


# ------------------------------------------------------------------------------------------------ floor piano
def piano():
    W, Dp, H = 2400, 700, 30
    d = D("led-piano-pedals", [W, Dp, H], {"frame": "plastic#1a1b1d", "black": "fabric#060606"})
    d.box("frame", [0, 0, 0, W, 22, Dp], "frame", r=4)
    d.box("divider", [20, 22, 330, W - 20, 30, 370], "black", r=2)
    cols = {"lav": "gloss#9a78dc", "pink": "gloss#e83c9c", "lblue": "gloss#74c0f0", "white": "gloss#f8f8f8",
            "orange": "gloss#f07010", "yellow": "gloss#f6dc10", "green": "gloss#3cb034", "purple": "gloss#8a38c4",
            "lime": "gloss#a6dc30"}
    back = ["lav", "pink", "lblue", "white", "orange", "yellow", "green", "purple"] * 2
    front = ["lime", "yellow", "orange", "white", "lblue", "pink", "purple", "green"] * 2
    kw = (W - 40) / 16
    for i in range(16):
        x0 = 20 + i * kw
        d.box(f"kb{i}", [x0 + 1.5, 20, 20, x0 + kw - 1.5, 30, 330], cols[back[i]], r=2)
        d.box(f"kf{i}", [x0 + 1.5, 20, 370, x0 + kw - 1.5, 30, 680], cols[front[i]], r=2)
    n = 0
    for i in range(15):
        if i % 7 in (0, 1, 3, 4, 5):
            x = 20 + (i + 1) * kw
            d.box(f"bk{n}", [x - 30, 29, 140, x + 30, 31, 330], "black", soft=True, copies=[[0, 0, 230]])
            n += 1
    d.save()


# ------------------------------------------------------------------------------------------------ puzzle light table
def puzzle_table():
    W, Dp, H = 700, 700, 200
    d = D("lighting-color-changing-puzzle-table", [W, Dp, H], {
        "base": "plastic#eceeee", "glow": "gloss#f3e36a", "tray": "acrylic#f07a2099", "rim": "plastic#111214"})
    d.box("base", [0, 0, 0, W, 130, Dp], "base", r=6)
    d.box("surface", [16, 128, 16, W - 16, 134, Dp - 16], "glow", r=2)
    tray = path(rrect_pts(15, 15, W - 15, Dp - 15, 4)) + " " + path(list(reversed(rrect_pts(22, 22, W - 22, Dp - 22, 2))))
    top_slab(d, "tray", tray, 130, 200, "tray", r=2)
    for i, (x, mat) in enumerate([(182, "gloss#9a2a20"), (266, "gloss#2850b0"), (350, "gloss#1f8a3a"), (434, "gloss#e0c020"),
                                  (518, "gloss#d8e4f0")]):
        d.cyl(f"brim{i}", [x, 62, Dp - 1], [x, 62, Dp + 3], 56, "rim")
        d.lathe(f"btn{i}", [x, 62, Dp + 3], [[0, 0], [22, 0], [22, 4], [18, 7], [0, 8]], mat, axis="z")
    shapes = [("t", 210, 250, 90, 20, "plastic#0b8a3c"), ("s", 300, 300, 80, 30, "plastic#0b8a3c"),
              ("t", 340, 260, 80, 200, "plastic#d81812"), ("c", 370, 420, 90, 0, "plastic#d81812"),
              ("c", 440, 395, 80, 0, "plastic#f2c40c"), ("t", 250, 430, 85, 160, "plastic#0b8a3c"),
              ("t", 560, 280, 90, 10, "plastic#f2c40c"), ("t", 110, 520, 80, 90, "plastic#0b8a3c"),
              ("t", 590, 620, 70, 40, "plastic#0b8a3c"), ("t", 160, 590, 70, 300, "plastic#f2c40c"),
              ("t", 420, 240, 70, 120, "plastic#d81812"), ("c", 300, 470, 60, 0, "plastic#0b8a3c")]
    for i, (k, x, z, s, a, mat) in enumerate(shapes):
        s = s * 1.45
        if k == "c":
            pts = circle_pts(x, z, s / 2, 20)
        elif k == "s":
            pts = [(x + s / 1.414 * math.cos(math.radians(a + 45 + 90 * j)), z + s / 1.414 * math.sin(math.radians(a + 45 + 90 * j))) for j in range(4)]
        else:
            pts = [(x + s * 0.58 * math.cos(math.radians(a + 120 * j)), z + s * 0.58 * math.sin(math.radians(a + 120 * j))) for j in range(3)]
        top_slab(d, f"shape{i}", pts, 134, 137 + (i % 3) * 0.6, mat, soft=True)
    d.save()


# ------------------------------------------------------------------------------------------------ master control kiosk
def master_control():
    W, Dp, H = 600, 550, 950
    HF = 650
    d = D("multi-sensory-master-control-machine", [W, Dp, H], {
        "shell": "plastic#eef0f2", "seam": "plastic#a3a9b0", "dark": "plastic#24282c", "bezel": "plastic#2e2a22"})
    side_slab(d, "cabinet", round_poly([(0, 0), (Dp, 0), (Dp, HF), (0, H)], 8, 3), 0, W, "shell", r=10)
    ang = math.degrees(math.atan2(H - HF, Dp))           # slope of the top
    ux, uy = Dp / math.hypot(Dp, H - HF), -(H - HF) / math.hypot(Dp, H - HF)
    def on_slope(s): return (ux * s, H + uy * s)          # (z, y) at distance s from the rear top edge
    zc, yc = on_slope(190)
    piv = [W / 2, yc, zc]
    d.add("screen", "screen", "bezel", box=[35, yc - 3, zc - 150, W - 35, yc + 7, zc + 150], r=6, face="top", bezel=14,
          rot=rot("x", ang, piv))
    yt = yc + 7.3
    # interface as on the photo: deep blue page, a bright blue bar top left under a light title line, a column of
    # lighter tiles at the left and darker panels to the right
    for i, (x, z, w, h, mat) in enumerate([(W / 2, zc, 500, 270, "gloss#0c2258"), (W / 2, zc - 122, 470, 10, "gloss#c8d4e8"),
                                           (150, zc - 88, 190, 34, "gloss#3a8ee0"), (130, zc - 30, 150, 34, "gloss#2c62b0"),
                                           (130, zc + 22, 150, 34, "gloss#2a5aa6"), (130, zc + 74, 150, 34, "gloss#24509a"),
                                           (390, zc - 60, 250, 80, "gloss#1e4c9c"), (390, zc + 50, 250, 90, "gloss#081a46")]):
        d.decal(f"ui{i}", [x, yt + 0.3 + i * 0.2, z], [w, h], "top", mat, soft=True, rot=rot("x", ang, piv))
    zp, yp = on_slope(430)
    d.box("panel", [70, yp - 2, zp - 45, W - 70, yp + 1.2, zp + 45], "plastic#e4e7ea", r=3, soft=True, rot=rot("x", ang, [W / 2, yp, zp]))
    # the faint embossed keyboard on that panel: 3 rows of keys a shade darker than the shell
    for r_ in range(3):
        d.decal(f"keys{r_}", [110, yp + 1.5, zp - 28 + r_ * 28], [26, 18], "top", "plastic#d9dde1", soft=True,
                rot=rot("x", ang, [W / 2, yp, zp]), repeat={"n": 14, "step": [29, 0, 0]})
    # front door seams (x 40-560, y 35-535 on the photo) and the dark 'smile' handle slot at its top middle
    for i, b in enumerate([[40, 35, 43, 535], [W - 43, 35, W - 40, 535], [40, 35, W - 40, 38], [40, 532, W - 40, 535]]):
        d.box(f"seam{i}", [b[0], b[1], Dp - 0.5, b[2], b[3], Dp + 0.8], "seam", soft=True)
    smile = [(W / 2 - 52, 432), (W / 2 + 52, 432)] + [(W / 2 + 52 * math.cos(math.radians(a)), 432 - 16 * math.sin(math.radians(a)))
                                                      for a in range(20, 161, 20)]
    front_slab(d, "handle", smile, Dp - 2, Dp + 1.5, "dark", soft=True)
    # right side: 4 long horizontal louvre slots stacked one above another (they look slanted on the photo only by
    # perspective) and a black port below them towards the front
    d.box("vent", [W - 1, 222, 150, W + 1.2, 234, 480], "dark", r=5, soft=True, repeat={"n": 4, "step": [0, 36, 0]})
    d.box("port", [W - 1, 70, 385, W + 1.5, 180, 465], "dark", r=4, soft=True)
    d.save()


# ------------------------------------------------------------------------------------------------ projector
def projector():
    W, Dp, H = 350, 300, 120
    d = D("multi-sensory-matching-projection-system", [W, Dp, H], {
        "black": "plastic#17181a", "silver": "metal#c8cacc", "grey": "plastic#8e9396"})
    d.box("body", [0, 8, 0, W, 96, Dp - 22], "black", r=18)
    d.box("top", [2, 62, 2, W - 2, 120, Dp - 6], "silver", r=26)
    d.box("front", [6, 10, Dp - 30, W - 6, 84, Dp - 4], "black", r=12)
    d.decal("panel", [110, 120.2, 70], [150, 70], "top", "grey", soft=True)
    d.decal("vent", [260, 120.2, 90], [110, 40], "top", "plastic#5e6265", soft=True)
    # front: a dark grille of horizontal slats on the left, a small silver badge left of the lens, a thin silver band
    # along the bottom edge with a white label in its middle
    d.box("grille", [22, 26, Dp - 4.5, 170, 78, Dp - 3], "plastic#2b2d30", r=3, soft=True)
    d.box("slat", [26, 30, Dp - 3, 166, 31.5, Dp - 2.2], "plastic#0e0f10", soft=True, repeat={"n": 11, "step": [0, 4.4, 0]})
    d.box("badge", [168, 60, Dp - 4, 200, 70, Dp - 2.5], "metal#bfc3c6", r=2, soft=True)
    d.box("band", [8, 8, Dp - 24, W - 8, 18, Dp - 2], "metal#c8cacc", r=4)
    d.decal("label", [150, 13, Dp - 1.9], [40, 7], "front", "plastic#f2f2f2", soft=True)
    # lens: a thick black ring with a grey lip, a chrome ring, a dark inner ring and light blue-grey glass
    d.lathe("lens", [255, 58, Dp - 12], [[0, 0], [55, 0], [55, 14], [52, 20], [42, 22], [40, 18], [0, 18]], "black", axis="z")
    d.lathe("lenslip", [255, 58, Dp + 8], [[49, 0], [53, 0], [53, 2], [49, 3]], "plastic#6a6e72", axis="z", caps=False, soft=True)
    d.lathe("lensring", [255, 58, Dp + 4], [[30, 0], [40, 0], [40, 3], [30, 4]], "chrome", axis="z", caps=False)
    d.lathe("glass", [255, 58, Dp + 2], [[0, 0], [31, 0], [26, 4], [0, 5]], "gloss#9db4c4", axis="z")
    d.lathe("glassring", [255, 58, Dp + 6.2], [[14, 0], [20, 0], [20, 0.8], [14, 0.8]], "plastic#2a3036", axis="z", caps=False, soft=True)
    d.cyl("foot", [40, 0, 40], [40, 8, 40], 22, "rubber", copies=[[270, 0, 0], [0, 0, 200], [270, 0, 200]])
    d.save()


# ------------------------------------------------------------------------------------------------ bean bag
def bean_bag():
    """A pinwheel of 6 gores (yellow, blue, red ×2) meeting at a pole on the lower front-left, as on the photo, on a wide
    low body, and a thick horseshoe roll round the back and the sides that leaves a seat dent at the top front (where
    the child sits on the photo). Each gore is an ellipsoid pushed out from the pole axis; the roll is a fat tube cut
    into pieces coloured by the gore they lie in, so the gore seams run on over it."""
    import math as m
    e, a, b, c = 95, 350, 220, 415
    order = ["yel", "blu", "red", "yel", "blu", "red"]
    tx, ty = 18, -20
    def turn(p):
        x, y, z = p
        t = m.radians(tx); y, z = y * m.cos(t) - z * m.sin(t), y * m.sin(t) + z * m.cos(t)
        t = m.radians(ty); x, z = x * m.cos(t) + z * m.sin(t), -x * m.sin(t) + z * m.cos(t)
        return (x, y, z)
    def unturn(p):
        x, y, z = p
        t = m.radians(-ty); x, z = x * m.cos(t) + z * m.sin(t), -x * m.sin(t) + z * m.cos(t)
        t = m.radians(-tx); y, z = y * m.cos(t) - z * m.sin(t), y * m.sin(t) + z * m.cos(t)
        return (x, y, z)
    def colour(p):                               # gore of a point (relative to the body centre)
        lx, ly, _ = unturn(p)
        return order[int(round(m.degrees(m.atan2(ly, lx)) / 60.0)) % 6]
    gores = []
    for k in range(6):
        ph = m.radians(60 * k)
        # narrower across the pole axis where the gore points up/down: a wide, low body
        gores.append((60 * k, a * (1 - 0.33 * abs(m.sin(ph))), b, (e * m.cos(ph), e * 0.85 * m.sin(ph), 0.0)))
    lo = [1e9] * 3; hi = [-1e9] * 3
    def grow(p):
        for n in range(3):
            lo[n] = min(lo[n], p[n]); hi[n] = max(hi[n], p[n])
    for ph, ak, bk, ctr in gores:
        q = m.radians(ph)
        for i in range(0, 181, 10):
            for j in range(0, 360, 10):
                u, v = m.radians(i), m.radians(j)
                lx, ly, lz = ak * m.sin(u) * m.cos(v), bk * m.sin(u) * m.sin(v), c * m.cos(u)
                grow(turn((ctr[0] + lx * m.cos(q) - ly * m.sin(q), ctr[1] + lx * m.sin(q) + ly * m.cos(q), ctr[2] + lz)))
    top = hi[1]
    # the roll: horseshoe of radius RH round the back (theta 0) to the front sides, high at the back, sinking in at the
    # front ends; centre-line points relative to the body centre
    RH, DR = 280, 270
    roll = []
    for deg in range(-105, 106, 10):
        t = m.radians(deg)
        y = top - 75 + 110 * m.cos(t) ** 2 - (190 if abs(deg) > 100 else 80 if abs(deg) > 90 else 0)
        roll.append((RH * m.sin(t), y, -RH * m.cos(t) - 20))
    for x, y, z in roll:
        grow((x - DR / 2, y - DR / 2, z - DR / 2)); grow((x + DR / 2, y + DR / 2, z + DR / 2))
    W, H, Dp = round(hi[0] - lo[0]), round(hi[1] - lo[1]), round(hi[2] - lo[2])
    C = [-lo[0], -lo[1], -lo[2]]
    d = D("bean-bag", [W, Dp, H], {"red": "fabric#da3e3a", "yel": "fabric#f2d84a", "blu": "fabric#1a6aa8"})
    tilt = [rot("x", tx, C), rot("y", ty, C)]
    for k, (ph, ak, bk, ctr) in enumerate(gores):
        at = [round(C[0] + ctr[0], 1), round(C[1] + ctr[1], 1), round(C[2] + ctr[2], 1)]
        d.add(f"gore{k}", "sphere", order[k], at=at, radii=[round(ak, 1), round(bk, 1), c], sides=32,
              rot=rot("z", ph, at), rots=tilt)
    # cut the roll where the gore colour (seen on its outer top side) changes
    def col_at(x, y, z):
        L = m.hypot(x, z) or 1.0
        return colour((x + x / L * DR * 0.4, y + DR * 0.3, z + z / L * DR * 0.4))
    pieces, cur = [], [roll[0]]
    cc = col_at(*roll[0])
    for p_ in roll[1:]:
        cur.append(p_)
        c2 = col_at(*p_)
        if c2 != cc:
            pieces.append((cc, cur)); cur = [p_]; cc = c2
    pieces.append((cc, cur))
    for k, (mat, pts) in enumerate(pieces):
        if len(pts) < 2:
            continue
        d.tube(f"roll{k}", [[round(C[0] + x, 1), round(C[1] + y, 1), round(C[2] + z, 1)] for x, y, z in pts], DR, mat, bend=80)
    # round off the joints and the two front ends of the roll
    for k, (mat, pts) in enumerate(pieces):
        for j, (x, y, z) in enumerate((pts[0], pts[-1])):
            d.sphere(f"rollend{k}{j}", [round(C[0] + x, 1), round(C[1] + y, 1), round(C[2] + z, 1)], DR, mat)
    d.save()
    print("bean-bag size", W, Dp, H, [p[0] for p in pieces])


ALL = {"butterfly-fiber-falls": butterfly, "colorful-fluorescent-drawing-board": drawing_board, "color-led-ball": led_ball,
       "led-piano-pedals": piano, "lighting-color-changing-puzzle-table": puzzle_table,
       "multi-sensory-master-control-machine": master_control, "multi-sensory-matching-projection-system": projector,
       "bean-bag": bean_bag}
if __name__ == "__main__":
    for k in (sys.argv[1:] or ALL):
        ALL[k]()
