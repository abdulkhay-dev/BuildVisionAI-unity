"""Round play items of batch pediatric-4/5: XYRT-80 rotary disc, XYRT-79 balance disc, XYRT-93 ring climbing frame,
XYRT-83 balance lines (ring of 8 arcs). Front = +z; angles: 0 = +x (right), 90 = the front."""
from pd4lib import *


def xyrt80():
    d = D("xyrt-80", [650, 650, 120], {"red": "plastic#dd2a24", "redd": "plastic#b81e1a", "steel": "metal#c8ccd0"})
    c = 325
    # turntable base under the disc (hidden mostly)
    d.lathe("base", [c, 0, c], [[0, 0], [200, 0], [215, 4], [215, 14], [0, 14]], "redd")
    # the disc: thick rounded edge, flat outer rim band ~70 wide, the inner field a hair lower with a soft step
    d.lathe("field-line", [c, 0, c], [[243, 51], [251, 51], [251, 52], [243, 52]], "redd", soft=True)
    d.lathe("disc", [c, 0, c], [[0, 12], [270, 12], [305, 14], [321, 24], [325, 38], [322, 50], [314, 56], [250, 57],
                                [244, 51], [0, 51]], "red")
    # 4 stainless U grab handles on the rim, tangential
    for i, a in enumerate((62, 152, 242, 332)):
        hs = 13
        p0 = polar(c, c, 290, a - hs); p1 = polar(c, c, 290, a + hs)
        path = [[p0[0], 56, p0[1]], [p0[0], 120 - 6, p0[1]], [p1[0], 120 - 6, p1[1]], [p1[0], 56, p1[1]]]
        d.tube(f"handle{i}", path, 12, "steel", bend=16)
        for j, p in enumerate((p0, p1)):
            d.lathe(f"handle{i}-foot{j}", [p[0], 56, p[1]], [[0, 0], [11, 0], [11, 3], [8, 6], [0, 6]], "steel")
    return d


def xyrt79():
    d = D("xyrt-79", [730, 730, 220], {"or": "plastic#e8583a", "ord": "plastic#c9452c", "blue": "plastic#2a60c4",
                                      "hole": "plastic#7a2a1c"})
    c = 365
    slots, holes = (135, -45), (158, -22)

    def rad(a):
        r = 350.0
        for s in slots:
            da = (a - s + 180) % 360 - 180
            if abs(da) < 40: r += 46 * math.cos(math.radians(da / 40 * 90)) ** 2   # photo: big lobes
        return r
    outer = [polar(c, c, rad(360.0 * k / 96), 360.0 * k / 96) for k in range(96)]
    path = P(outer)
    # slot handles (stadium holes) and the round holes beside them
    for s in slots:
        cx_, cz_ = polar(c, c, 322, s)
        t = (-math.sin(math.radians(s)), math.cos(math.radians(s)))   # tangential unit
        pts = []
        for k in range(24):
            a = math.radians(360 * k / 24)
            u = (52 if math.cos(a) >= 0 else -52) + 17 * math.cos(a)
            v = 17 * math.sin(a)
            nx, nz = math.cos(math.radians(s)), math.sin(math.radians(s))
            pts.append((cx_ + u * t[0] + v * nx, cz_ + u * t[1] + v * nz))
        path += " " + P(pts)
    for h in holes:
        hx, hz = polar(c, c, 330, h)
        path += " " + P(circ(hx, hz, 17, 20))
    # blue rocking dome base
    d.lathe("dome", [c, 0, c], [[0, 0], [100, 2], [180, 20], [228, 60], [248, 110], [252, 152], [0, 152]], "blue")   # photo: tucked well under the top
    # orange top: outer rim slab with the handle holes, the recessed centre field with its step
    rim_in = P(circ(c, c, 262, 64))
    d.slab("rim", "top", path + " " + rim_in, [148, 220], "or", r=20)   # photo: a thick rounded edge
    d.lathe("field", [c, 0, c], [[0, 150], [268, 150], [268, 196], [250, 205], [0, 205]], "or")
    d.lathe("field-ring", [c, 0, c], [[205, 204], [214, 204], [214, 206.5], [205, 206.5]], "ord", soft=True)
    # cross lines on the field
    d.box("cross-x", [c - 200, 205, c - 3, c + 200, 207, c + 3], "ord", soft=True)
    d.box("cross-z", [c - 3, 205, c - 200, c + 3, 207, c + 200], "ord", soft=True)
    # white oval label
    lx, lz = polar(c, c, 175, 38)
    d.sphere("label", [lx, 205, lz], None, "plastic#ffffff", radii=[38, 3, 22], soft=True)
    # screw dots on the rim
    for i, a in enumerate((-118, 62, 205, 25)):
        px, pz = polar(c, c, 322, a)
        d.lathe(f"dot{i}", [px, 220, pz], [[0, 0], [7, 0], [7, 1.5], [0, 1.5]], "ord", soft=True)
    return d


def xyrt93():
    H = 600
    d = D("xyrt-93", [1600, 1600, H], {"red": "plastic#e2231e", "blue": "plastic#1f4fbf", "yel": "plastic#f5c518"})
    c = 800
    seams = (65, 155, 245, 335)
    cols = ("red", "blue", "red", "blue")      # front, left, back, right quarter
    bh = 105
    for ring_i, (y0, y1) in enumerate(((0, bh), (H - bh, H))):
        for q in range(4):
            a0, a1 = seams[q] + 0.4, seams[(q + 1) % 4] - 0.4 + (360 if q == 3 else 0)
            d.slab(f"ring{ring_i}-{q}", "top", P(sector(c, c, 675, 800, a0, a1, 24)), [y0, y1], cols[q], r=14)
        # yellow connector plates over the seams
        for k, s in enumerate(seams):
            yy = y1 if ring_i == 1 else y1
            d.slab(f"plate{ring_i}-{k}", "top", P(sector(c, c, 685, 790, s - 6, s + 6, 6)), [yy - 2, yy + 5], "yel", r=2)
    # 20 yellow posts with collars, caps on the top ring
    n = 20
    for i in range(n):
        a = 74 + 360.0 * i / n
        px, pz = polar(c, c, 738, a)
        d.cyl(f"post{i}", [px, bh - 5, pz], [px, H - bh + 5, pz], 46, "yel", sides=20)
        d.lathe(f"collar{i}", [px, bh, pz], [[30, 0], [30, 14], [23, 22], [23, 22]], "yel", caps=False)
        d.lathe(f"collart{i}", [px, H - bh, pz], [[23, -22], [30, -14], [30, 0]], "yel", caps=False)
        d.box(f"cap{i}", [px - 20, H - 1, pz - 20, px + 20, H + 0.0, pz + 20], "yel", r=3, soft=True,
              rot=rot("y", -(a + 90), [px, H, pz]))
    return d


def xyrt83():
    d = D("xyrt-83", [1250, 1250, 70], {"g": "plastic#2f9a3c", "y": "plastic#f6c41a"})
    c = 625
    r1, r0 = 624, 489
    for i in range(8):
        a0 = 22.5 + 45 * i + 0.25
        a1 = a0 + 45 - 0.5
        col = "g" if i % 2 == 0 else "y"
        # loaf-shaped arc: wide low base, rounded domed top
        d.slab(f"arc{i}", "top", P(sector(c, c, r0, r1, a0, a1, 24)), [0, 70], col, r=24)
    # bumpy texture (photo): the whole top is covered with small dense nubs, ~22 mm pitch, rows staggered
    for col, start in (("g", 0), ("y", 1)):
        offs = []
        for i in range(start, 8, 2):
            a0 = 22.5 + 45 * i
            for j, (rr_, yy) in enumerate(((508, 63), (528, 69), (548, 71), (568, 71), (588, 69), (606, 63))):
                ny = int(2 * math.pi * rr_ / 8 / 22)
                for k in range(ny):
                    a = a0 + 45 * (k + (0.25 if j % 2 else 0.75)) / ny
                    offs.append((polar(c, c, rr_, a), yy))
        (x0, z0), y0 = offs[0]
        d.sphere(f"studs-{col}", [x0, y0, z0], None, col, radii=[6, 5, 6], sides=6, soft=True,
                 copies=[[p[0] - x0, yy - y0, p[1] - z0] for p, yy in offs[1:]])
    return d


if __name__ == "__main__":
    main({"xyrt-80": xyrt80, "xyrt-79": xyrt79, "xyrt-93": xyrt93, "xyrt-83": xyrt83})
