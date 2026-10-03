"""Playground items of batch pediatric-4: XYRT-5 double horse swing, XYRT-65 obstacle-course kit.
Front = +z, x from the left seen from the front."""
import random
from pd4lib import *
from sflib import round_poly


def xyrt5():
    W, DD, H = 1600, 1300, 1550
    d = D("xyrt-5", [W, DD, H], {"green": "gloss#2f9a45", "yel": "gloss#f4c62a", "red": "gloss#e03a26",
                                 "tube": "plastic#eef0ee", "floor": "plastic#22304a", "belt": "fabric#4a68b8",
                                 "cable": "plastic#6f7c90"})
    zc = 650
    # roof: red inverted-V (pitched) block on top, the two hanging pivots
    ch = P([(520, 1350), (800, 1525), (1080, 1350), (1080, 1285), (800, 1445), (520, 1285)])
    d.slab("roof", "front", ch, [645, 800], "red", r=12)   # over the front necks; the back heads stand free
    d.box("sign", [830, 1440, 800, 1000, 1470, 802], "plastic#f2f2f2", soft=True,
          rot=rot("z", -32, [915, 1455, 801]))
    d.box("sign-txt", [850, 1450, 802, 980, 1458, 803], "plastic#5a2a2a", soft=True,
          rot=rot("z", -32, [915, 1455, 802]))
    # white A-frame tubes from the roof ends to the four feet; red foot caps; grey ground cables along x
    feet = {"lb": (85, 110), "lf": (85, 1190), "rb": (1515, 110), "rf": (1515, 1190)}
    # front tubes end under the roof's front corners, back tubes on the back necks below the heads (photo)
    tops = {"lb": (560, 540, 1240), "lf": (560, 760, 1320), "rb": (1040, 540, 1240), "rf": (1040, 760, 1320)}
    for k in feet:
        (fx, fz), (tx, tz, ty) = feet[k], tops[k]
        d.cyl(f"leg-{k}", [tx, ty, tz], [fx, 30, fz], 34, "tube")
        # red cap over the lower end of the tube, red foot block
        t = 0.1
        d.cyl(f"cap-{k}", [fx + (tx - fx) * t, 30 + (ty - 30) * t, fz + (tz - fz) * t], [fx, 22, fz], 52, "red", sides=8)
        d.box(f"foot-{k}", [fx - 45, 0, fz - 45, fx + 45, 30, fz + 45], "red", r=8)
    for z in (110, 1190):
        d.cyl(f"cable-{z}", [85, 14, z], [1515, 14, z], 9, "cable")
    d.cyl("axle", [560, 1330, 650], [560, 1330, 800], 30, "tube", copies=[[480, 0, 0]])
    # hanging side boards (photo): each is two horse-neck uprights (front and back) standing close together under
    # the roof and spreading to the bottom, mane bumps on the back edge of each neck, a snout bulge at the front of
    # each head with a peg (ear) on top; an X brace between the necks; a solid lower body with two bottom lobes on
    # the pivots and an arch between them. Green on the left, yellow on the right.
    def neck(zb0, zb1, zt0, zt1):
        """Upright from the bottom (zb0..zb1 at y 470) to the head (zt0..zt1 at y 1390); mane on the back edge."""
        pts = [(zb0, 380), (zb0, 470)]
        n = 7
        for k in range(1, n + 1):                      # back edge with mane bumps over the upper third
            t = k / (n + 1)
            yv = 470 + (1360 - 470) * t
            zv = zb0 + (zt0 - zb0) * t
            pts.append((zv, yv))
            if t > 0.55:
                pts.append((zv - 26, yv + 30)); pts.append((zv - 4, yv + 55))
        pts += [(zt0, 1360), (zt0 + 10, 1440), (zt0 + 45, 1482), (zt1 - 5, 1478), (zt1 + 20, 1440), (zt1 + 22, 1405),
                (zt1, 1385), (zb1, 470), (zb1, 380)]
        return pts
    nb = neck(330, 478, 522, 612)
    nf = neck(828, 970, 690, 780)
    body = [(330, 410), (330, 280), (350, 200), (400, 170), (455, 185), (495, 245), (805, 245), (845, 185), (900, 170),
            (950, 200), (970, 280), (970, 410)]
    def brace(p, q, w=48):
        dz, dy = q[0] - p[0], q[1] - p[1]
        L = math.hypot(dz, dy); nz, ny = -dy / L * w / 2, dz / L * w / 2
        return [(p[0] + nz, p[1] + ny), (q[0] + nz, q[1] + ny), (q[0] - nz, q[1] - ny), (p[0] - nz, p[1] - ny)]
    shapes = [round_poly(nb, 10, 3), round_poly(nf, 10, 3), round_poly(body, 22),
              brace((556, 1080), (845, 520)), brace((744, 1080), (455, 520))]
    for nm, x0, x1, col, boss, ring_ in (("l", 568, 613, "green", "red", "yel"), ("r", 987, 1032, "yel", "red", "red")):
        for j, sh in enumerate(shapes):
            d.slab(f"board-{nm}{j}", "side", P(sh), [x0 + (2 if j > 2 else 0), x1 - (2 if j > 2 else 0)], col, r=8)
        d.sphere(f"knob-{nm}", [(x0 + x1) / 2, 1500, 567], 44, col, copies=[[0, 0, 168]])
        d.cyl(f"knobn-{nm}", [(x0 + x1) / 2, 1470, 567], [(x0 + x1) / 2, 1500, 567], 26, col, copies=[[0, 0, 168]])
        xo = x0 - 1 if nm == "l" else x1 + 1
        ax = -1 if nm == "l" else 1
        # round bosses on the outer face
        for j, (z, y) in enumerate(((470, 330), (830, 330))):
            d.cyl(f"boss-{nm}{j}", [xo, y, z], [xo + 10 * ax, y, z], 64, ring_)
            d.cyl(f"bossc-{nm}{j}", [xo + 9 * ax, y, z], [xo + 14 * ax, y, z], 30, boss)
        d.cyl(f"pivot-{nm}", [xo, 215, 400], [xo + 12 * ax, 215, 400], 40, "plastic#5a6a80", copies=[[0, 0, 500]])
    # white hand grip across the gap between the two necks (photo: on the green board under the roof)
    d.cyl("grip", [590, 1300, 585], [590, 1300, 715], 30, "plastic#f2f2ee", copies=[[420, 0, 0]])
    # car: dark slatted floor, two red seats facing each other, blue T restraints
    d.box("floor", [613, 172, 420, 987, 205, 880], "floor", r=6)
    d.box("slat", [630, 205, 440, 970, 210, 452], "plastic#2f3d5c", r=2, repeat=rep(14, [0, 0, 31]))
    for nm, z0, z1, zb0, zb1, tilt, about in (("b", 400, 570, 360, 384, -12, 372), ("f", 730, 900, 916, 940, 12, 928)):
        d.box(f"seat-{nm}", [613, 380, z0, 987, 418, z1], "red", r=12)
        d.box(f"seatback-{nm}", [622, 390, zb0, 978, 640, zb1], "red", r=30, rot=rot("x", tilt, [800, 380, about]))
        zs = (z0 + z1) / 2
        d.strap(f"belt-{nm}", [[800, 420, zs], [800, 560, zs + (40 if nm == "b" else -40)]], [50, 5], "belt", soft=True)
        d.strap(f"belt2-{nm}", [[700, 560, zs + (40 if nm == "b" else -40)], [900, 560, zs + (40 if nm == "b" else -40)]],
                [45, 5], "belt", soft=True)
    return d


def hand_pts(cx, cz, s=1.0, ang=0.0):
    """Flat hand-print outline (top plane), fingers to the back (-z) before turning by ang deg."""
    pts = [(-55, 60), (55, 60), (70, 0), (95, -30), (85, -45), (62, -20), (55, -95), (40, -100), (32, -40), (25, -110),
           (8, -112), (5, -45), (-8, -110), (-25, -108), (-22, -40), (-38, -95), (-55, -90), (-55, -10), (-62, 30)]
    a = math.radians(ang)
    return [(cx + s * (x * math.cos(a) - z * math.sin(a)), cz + s * (x * math.sin(a) + z * math.cos(a))) for x, z in pts]


def foot_pts(cx, cz, s=1.0, ang=0.0):
    pts = []
    for k in range(24):
        t = 2 * math.pi * k / 24
        w = 50 if math.sin(t) < 0 else 38       # wider fore-foot (back, -z), narrow heel
        pts.append((w * math.cos(t), 120 * math.sin(t)))
    a = math.radians(ang)
    return [(cx + s * (x * math.cos(a) - z * math.sin(a)), cz + s * (x * math.sin(a) + z * math.cos(a))) for x, z in pts]


def xyrt65():
    W, DD, H = 1900, 1000, 860
    C = {"R": "plastic#e0242a", "Y": "plastic#f6c51a", "G": "plastic#1f9a40", "B": "plastic#2049c0"}
    d = D("xyrt-65", [W, DD, H], dict(C, hole="plastic#1d1e22", bridge="plastic#2050c4", tex="plastic#3a68d8"))
    n = [0]

    def block(x, z, col, half=False, y=0, along="x"):
        """A hollow brick 150 cube (or half 150x150x75) with a round stud on top and a dark side hole."""
        n[0] += 1
        hh = 75 if half else 150
        d.box(f"blk{n[0]}", [x, y, z, x + 150, y + hh, z + 150], col, r=10)
        d.lathe(f"blk{n[0]}-stud", [x + 75, y + hh, z + 75], [[0, 0], [40, 0], [40, 10], [24, 10], [24, 4], [0, 4]], col)
        d.cyl(f"blk{n[0]}-hole", [x + 75, y + hh / 2, z + 150], [x + 75, y + hh / 2, z + 151.5], 34 if half else 40,
              "hole", soft=True)
    # left: a stack of bricks (red / yellow / green / blue)
    block(60, 260, "R", half=True); block(60, 260, "Y", y=75); block(60, 260, "R", y=225)
    block(60, 430, "R", half=True); block(210, 430, "Y", half=True); block(60, 430, "Y", half=True, y=75)
    block(220, 250, "G"); block(370, 250, "G")
    block(240, 420, "B", y=75); block(390, 420, "B", y=75); block(240, 420, "B", half=True); block(390, 420, "B", half=True)
    block(60, 600, "Y", half=True)
    # back balance bridge on two half bricks, two poles in a yellow brick, hoops
    block(700, 220, "G", half=True); block(1260, 220, "Y", half=True)
    d.box("bridge-b", [660, 75, 200, 1440, 125, 400], "bridge", r=22)
    d.box("bridge-b-tex", [690, 125, 225, 714, 129, 249], "tex", r=4, soft=True, repeat=rep(24, [30, 0, 0]),
          copies=[[0, 0, 40], [0, 0, 80], [0, 0, 120]])
    block(560, 330, "Y", half=True)
    d.cyl("pole-r", [610, 70, 405], [610, H, 405], 32, "R")
    d.cyl("pole-b", [660, 70, 380], [660, H - 10, 380], 32, "B")
    # three big hoops (Ø600) standing in a row (photos 1 and 2): the yellow and green ones are held by round stud
    # connectors on the back part of the front bridge (blue under yellow, red under green); the blue + red pair
    # stands in a yellow half brick on the floor at the right end; small hoops fan out of a red double brick
    yb = 125                                   # front bridge top
    for i, (cx, cz, col, conn, y0) in enumerate(((820, 585, "Y", "B", yb + 42), (1160, 585, "G", "R", yb + 42),
                                                 (1520, 470, "B", None, 75 + 10))):
        pts = [[cx + 300 * math.sin(math.radians(a)), y0 + 300 + 300 * math.cos(math.radians(a)), cz] for a in range(0, 361, 8)]
        d.tube(f"hoop{i}", pts, 20, col, rot=rot("y", 12, [cx, 0, cz]))
        if conn:
            # round connector: a disc with a raised ring and a slotted stud gripping the hoop
            d.lathe(f"hoop{i}-conn", [cx, yb, cz], [[0, 0], [62, 0], [62, 22], [44, 26], [44, 36], [30, 40], [0, 40]], conn)
            d.box(f"hoop{i}-grip", [cx - 22, yb + 30, cz - 26, cx + 22, yb + 58, cz + 26], conn, r=8,
                  rot=rot("y", 12, [cx, 0, cz]))
    block(1445, 395, "Y", half=True)       # under the blue / red hoops
    pts = [[1520 + 300 * math.sin(math.radians(a)), 85 + 300 + 300 * math.cos(math.radians(a)), 445] for a in range(0, 361, 8)]
    d.tube("hoop3", pts, 20, "R", rot=rot("y", 12, [1520, 0, 445]))
    block(1640, 540, "R", half=True); block(1760, 540, "R", half=True)
    for i, (col, r_, lean, dx) in enumerate((("B", 180, -6, 30), ("G", 172, -14, 10), ("Y", 166, -22, -5),
                                             ("R", 176, -30, -20))):
        cx, cz = 1790 + dx, 610 - i * 12
        pts = [[cx + r_ * math.sin(math.radians(a)) * 0.35, 75 + r_ + r_ * math.cos(math.radians(a)),
                cz + r_ * math.sin(math.radians(a))] for a in range(0, 361, 12)]
        d.tube(f"small-hoop{i}", pts, 16, col, rot=rot("z", lean, [cx, 75, cz]))
    # front balance bridge on a green and a blue brick
    block(640, 560, "G", half=True); block(1180, 560, "B", half=True)
    d.box("bridge-f", [580, 75, 545, 1390, 125, 725], "bridge", r=24)
    d.box("bridge-f-tex", [610, 125, 570, 634, 129, 594], "tex", r=4, soft=True, repeat=rep(25, [30, 0, 0]),
          copies=[[0, 0, 40], [0, 0, 80], [0, 0, 110]])
    # short sticks laid side by side (front left), long sticks across the front
    cols = "YRBGRBGYRBYGBRY"
    for i, c in enumerate(cols):
        x = 260 + i * 27
        d.cyl(f"stick{i}", [x, 13, 600], [x - 15, 13, 900], 24, c)
    for i, c in enumerate("GYRBGY"):
        z = 760 + i * 27
        d.cyl(f"lstick{i}", [800, 13, z], [1500, 13, z], 24, c)
    # hand prints and foot prints flat on the floor, clamps and bean bags at the right front
    for i, (x, z, c, a) in enumerate(((90, 760, "B", -10), (80, 930, "R", 5), (330, 960, "Y", 0), (560, 950, "G", 8),
                                      (700, 940, "R", -5))):
        d.slab(f"hand{i}", "top", P(hand_pts(x, z, 0.9, a)), [0, 10], c, r=3)
    for i, (x, z, c, a) in enumerate(((880, 935, "B", 75), (1060, 950, "R", 80), (1250, 950, "G", 85),
                                      (1430, 940, "B", 80), (1600, 930, "Y", 70))):
        d.slab(f"foot{i}", "top", P(foot_pts(x, z, 0.85, a)), [0, 10], c, r=3)
    rnd_ = random.Random(65)
    # ~24 small C clips (blue and green) scattered at the right front: little arches with a foot stud
    for c in "BG":
        for o in range(3):                     # three orientations per colour, copies at random spots
            pts = [(1500 + rnd_.uniform(0, 330), rnd_.uniform(600, 790)) for _ in range(4)]
            x0, z0 = pts[0]
            ang = rnd_.uniform(0, 180)
            arc_ = [[x0 + 17 * math.cos(math.radians(t)), 22 + 17 * math.sin(math.radians(t)), z0] for t in range(-30, 211, 30)]
            cop = [[x - x0, 0, z - z0] for x, z in pts[1:]]
            d.tube(f"clip-{c}{o}", arc_, 10, c, rot=rot("y", ang, [x0, 0, z0]), copies=cop, soft=True)
            d.cyl(f"clipf-{c}{o}", [x0, 0, z0], [x0, 10, z0], 22, c, copies=cop, soft=True)
    # four bean bags (green, red, blue, yellow) with white printed label squares
    for i, (x, c) in enumerate(((1560, "G"), (1650, "R"), (1740, "B"), (1830, "Y"))):
        zc = 880 + i * 15
        r_ = rot("y", 14 * i - 15, [x + 60, 0, zc])
        d.box(f"beanbag{i}", [x, 0, zc - 60, x + 115, 45, zc + 60], c, r=20, puff=8, rot=r_)
        d.box(f"beanbag{i}-lbl", [x + 30, 52, zc - 30, x + 85, 55, zc + 15], "plastic#f4f1e6", r=3, soft=True, rot=r_)
    return d


if __name__ == "__main__":
    main({"xyrt-5": xyrt5, "xyrt-65": xyrt65})
