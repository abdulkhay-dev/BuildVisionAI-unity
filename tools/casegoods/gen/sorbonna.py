"""«Сорбонна» (П7.055): all 10 modules by catalogue and product photos (no instruction exists).

Sources: catalogue pp. 50 (living room) and 51 (bedroom); the product photos of pinskdrev.by — the bookcase 0.10, the
TV unit 0.20 and the wardrobe 1.16 are photographed square to the camera, the proportions below are read from them
(0.47 / 0.68 / 0.47 px per mm across, the catalogue sizes as the scale).

Construction (one system, from the photos):
  * carcass ЛДСП 16 «Кобальт серый»: the sides run down to the floor; a flat face frame of МДФ 19 in front of the
    carcass — stiles 85 (tall pieces), 75 (tumbas), 64 / 68 (wardrobe, the inner stiles over the partitions), a top rail
    (42 / 37 / 57), a bottom rail 35–42 over a plinth recess 52 high (the stiles and sides stand to the floor as feet),
    rails behind every fixed shelf and between drawers and doors;
  * the fronts are inset in the frame, flush with its face, 2.5 mm gaps, a milled V-line 22 mm in from their edges;
  * low pieces: a 32 top 7 mm over the carcass; tall pieces: a crown 55 high, 20 mm out, in a lighter taupe (role
    "accent" — the catalogue shows the crown lighter than the carcass), with the top board inside it;
  * satin-nickel pulls with square posts c-c 64; drop-down flaps (pull at the top) on the TV unit and the 0.21 tumba;
  * drawer boxes ЛДСП 16, ХДФ bottoms, 13 mm runner gap.

    python3 tools/casegoods/gen/sorbonna.py      # Designs/sorbonna-*.json, gen/sorbonna_catalog.json
"""
import json
import math
import os

from kit_w3a import back, bar, box, cornice, drawer_box, dump, fmt, ids, metal_base, part

HERE = os.path.dirname(os.path.abspath(__file__))
T, FT = 16, 19
G = 2.5
PL = 52                       # plinth recess height (the bottom rail's underside)
CRH, CRO = 55, 20             # crown height / overhang
TOPT, TOPO = 32, 7            # low top: thickness / overhang


def vline_face(x0, y0, x1, y1, inset=22):
    a0, b0, a1, b1 = x0 + inset, y0 + inset, x1 - inset, y1 - inset
    return {"type": "grooves", "w": 2.5, "depth": 1.2, "flute": "v",
            "lines": [[fmt(a0), fmt(b0), fmt(a1), fmt(b0)], [fmt(a1), fmt(b0), fmt(a1), fmt(b1)],
                      [fmt(a1), fmt(b1), fmt(a0), fmt(b1)], [fmt(a0), fmt(b1), fmt(a0), fmt(b0)]]}


def pull(pid, x, y, z, vertical=False):
    return bar(pid, x, y, z, d=80, vertical=vertical, band=8, t=8, standoff=22, post=9, section="square")


class Case:
    """x0..x1 carcass, sides 0..dz deep to the floor, the face frame dz..fz; yt = the carcass top (under the top board
    or the crown)."""

    def __init__(self, W, B, H, tall, stile=75, top_rail=37, bottom_rail=37):
        self.W, self.B, self.H, self.tall = W, B, H, tall
        o = CRO if tall else TOPO
        self.x0, self.x1 = o, W - o
        self.fz = B - o
        self.dz = self.fz - FT
        self.yt = H - CRH if tall else H - TOPT
        self.p, self.m = [], []
        x0, x1, dz, yt = self.x0, self.x1, self.dz, self.yt
        self.ybot = PL + bottom_rail                          # the bottom's top face = the bottom rail's top
        self.p += [part("side-l", [x0, 0, 0, x0 + T, yt, dz]), part("side-r", [x1 - T, 0, 0, x1, yt, dz]),
                   part("bottom", [x0 + T, self.ybot - T, 0, x1 - T, self.ybot, dz]),
                   part("plinth", [x0 + T, 6, dz - 36, x1 - T, self.ybot - T, dz - 20])]
        if tall:
            self.p.append(part("top", [x0 + T, yt - T, 0, x1 - T, yt, dz]))
            self.p.append(cornice("crown", 0, W, 0, B, yt, "sorbonna-crown", mat="accent"))
            self.p.append(part("cap", [CRO + 35, H - 10, 0, W - CRO - 35, H, B - CRO - 35], mat="accent"))
        else:
            self.p.append(part("top", [0, yt, 0, W, H, B], edge=3))
        self.inner_top = yt - T if tall else yt
        # the face frame: rails top / bottom, stiles added by stiles()
        self.rt = self.inner_top - top_rail if tall else yt - top_rail   # the openings' top
        self.p.append(part("rail-top", [x0, self.rt, dz, x1, self.inner_top if tall else yt, self.fz]))
        self.stile_xs = []

    def stiles(self, spans):
        """spans: [(a, b), …] the stiles' x ranges (the outer ones from the carcass edge); returns the openings."""
        for k, (a, b) in enumerate(spans):
            y0 = 0 if k in (0, len(spans) - 1) else self.ybot
            self.p.append(part(f"stile-{k + 1}", [a, y0, self.dz, b, self.rt, self.fz]))
        self.p.append(part("rail-bottom", [spans[0][1], PL, self.dz, spans[-1][0], self.ybot, self.fz]))
        self.stile_xs = spans
        return [(spans[k][1], spans[k + 1][0]) for k in range(len(spans) - 1)]

    def hrail(self, pid, a, b, y0, y1):
        self.p.append(part(pid, [a, y0, self.dz, b, y1, self.fz]))

    def partition(self, pid, xc, y0=None, y1=None):
        self.p.append(part(pid, [xc - T / 2, y0 or self.ybot, 10, xc + T / 2, y1 or self.inner_top, self.dz]))

    def shelf(self, pid, a, b, y, fixed=False):
        if fixed:
            self.p.append(part(pid, [a, y - T, 10, b, y, self.dz]))
        else:
            self.p.append(part(pid, [a + 1, y - T, 20, b - 1, y, self.dz - 10]))

    def backs(self, xs=()):
        edges = [self.x0 + 8] + list(xs) + [self.x1 - 8]
        for k in range(len(edges) - 1):
            self.p.append(back(f"back-{k + 1}" if len(edges) > 2 else "back",
                               [edges[k], self.ybot - 8, 6, edges[k + 1], self.inner_top + 8, 9.5]))

    def front(self, fid, a, y0, b, y1, glass=None):
        f = part(fid, [a + G, y0 + G, self.dz, b - G, y1 - G, self.fz], kind="front")
        if glass:
            f["glass"] = {"frame": 70, "rebate": 5, "t": 4, "tint": "clear"}
        else:
            f["face"] = vline_face(a + G, y0 + G, b - G, y1 - G)
        return f

    def door(self, name, a, y0, b, y1, hinge, hy=None, hx=None, horizontal=False, glass=False):
        f = self.front(f"f-{name}", a, y0, b, y1, glass)
        if horizontal:
            h = pull(f"h-{name}", hx if hx is not None else (a + b) / 2, hy, self.fz)
        else:
            h = pull(f"h-{name}", (b - 30 if hinge == "left" else a + 30), hy if hy is not None else (y0 + y1) / 2,
                     self.fz, vertical=True)
        self.p += [f, h]
        self.m.append({"type": "door", "name": name, "parts": [f["id"], h["id"]], "hinge": hinge, "angle": 105})

    def flap(self, name, a, y0, b, y1, angle=90):
        f = self.front(f"f-{name}", a, y0, b, y1)
        h = pull(f"h-{name}", (a + b) / 2, y1 - 45, self.fz)
        self.p += [f, h]
        self.m.append({"type": "flap", "name": name, "parts": [f["id"], h["id"]], "hinge": "bottom", "angle": angle})

    def drawer(self, name, a, y0, b, y1, c0, c1, pulls=1, depth=None):
        f = self.front(f"f-{name}", a, y0, b, y1)
        d = depth or (500 if self.dz > 560 else 400 if self.dz > 420 else 350)
        bh = max(70, min(180, y1 - y0 - 40))
        bx = drawer_box(name, c0 + 13, c1 - 13, y0 + 16, bh, self.dz - d, self.dz)
        hs = []
        for k in range(pulls):
            cx = (a + b) / 2 if pulls == 1 else a + (b - a) * (0.17 if k == 0 else 0.83)
            hs.append(pull(f"h-{name}-{k + 1}", cx, (y0 + y1) / 2, self.fz))
        self.p += [f] + bx + hs
        self.m.append({"type": "drawer", "name": name, "parts": [f["id"]] + ids(bx) + ids(hs), "travel": d - 60})

    def dump(self, did):
        return dump(did, [self.W, self.B, self.H], self.p, self.m)


def even_stiles(x0, x1, n_open, sw_out, sw_in):
    """Stile spans for n_open equal openings between x0 and x1."""
    free = x1 - x0 - 2 * sw_out - (n_open - 1) * sw_in
    w = free / n_open
    spans, x = [(x0, x0 + sw_out)], x0 + sw_out
    for k in range(n_open - 1):
        x += w
        spans.append((x, x + sw_in))
        x += sw_in
    spans.append((x1 - sw_out, x1))
    return spans


# ------------------------------------------------------------------------------------------------------ living room
def shkaf_0_10():
    """Шкаф для книг 647 × 475 × 2085 (the front photo): open shelves over a 3 × 2 wine rack, a drawer, two open
    compartments below."""
    c = Case(647, 475, 2085, True, top_rail=42, bottom_rail=42)
    (o0, o1), = c.stiles([(c.x0, c.x0 + 85), (c.x1 - 85, c.x1)])
    a, b = c.x0 + T, c.x1 - T
    # fixed shelves behind rails 36 high (their tops): 1690, 1357, 1023 (the wine rack's top), 658 (the drawer's top
    # rail), 490 (under the drawer), 313
    for k, y in enumerate([1690, 1357, 1023]):
        c.shelf(f"shelf-{k + 1}", a, b, y, fixed=True)
        c.hrail(f"rail-s{k + 1}", o0, o1, y - 36, y)
    c.shelf("shelf-wine", a, b, 700, fixed=True)
    c.hrail("rail-wine", o0, o1, 664, 700)
    c.shelf("shelf-drawer", a, b, 490, fixed=True)
    c.hrail("rail-drawer", o0, o1, 454, 490)
    c.shelf("shelf-5", a, b, 313, fixed=True)
    c.hrail("rail-s5", o0, o1, 277, 313)
    # wine rack: 3 × 2 cells between y 700 and 987
    w = (b - a) / 3
    for k in (1, 2):
        x = a + w * k
        c.p.append(part(f"wine-v{k}a", [x - 8, 700, 10, x + 8, 836, c.dz]))
        c.p.append(part(f"wine-v{k}b", [x - 8, 852, 10, x + 8, 987, c.dz]))
    c.p.append(part("wine-h", [a, 836, 10, b, 852, c.dz]))
    c.drawer("drawer", o0, 490, o1, 664, a, b, depth=400)
    c.backs()
    return c.dump("sorbonna-0-10")


def shkaf_0_11():
    """Шкаф 647 × 475 × 2085 (универсальный): a glazed door over a drawer over a glazed door, shelves behind."""
    c = Case(647, 475, 2085, True, top_rail=42, bottom_rail=42)
    (o0, o1), = c.stiles([(c.x0, c.x0 + 85), (c.x1 - 85, c.x1)])
    a, b = c.x0 + T, c.x1 - T
    c.shelf("shelf-up", a, b, 1080, fixed=True)
    c.hrail("rail-up", o0, o1, 1044, 1080)
    c.shelf("shelf-low", a, b, 890, fixed=True)
    c.hrail("rail-low", o0, o1, 854, 890)
    for k, y in enumerate([1380, 1690]):
        c.shelf(f"shelf-{k + 1}", a, b, y)
    c.shelf("shelf-3", a, b, 480)
    c.backs()
    c.door("door_up", o0, 1080, o1, c.rt, "left", hy=1080 + 45, horizontal=True, glass=True)
    c.drawer("drawer", o0, 890, o1, 1044, a, b, depth=400)
    c.door("door_low", o0, c.ybot, o1, 854, "left", hy=854 - 45, horizontal=True, glass=True)
    return c.dump("sorbonna-0-11")


def tumba_0_20():
    """Тумба ТВ 1480 × 436 × 510 (front photo): drop-down flap | open niche with a shelf | drop-down flap."""
    c = Case(1480, 436, 510, False, top_rail=37, bottom_rail=35)
    sp = [(c.x0, 84), (459, 533), (939, 1015), (1391, c.x1)]
    ops = c.stiles(sp)
    p1, p2 = (sp[1][0] + sp[1][1]) / 2, (sp[2][0] + sp[2][1]) / 2
    c.partition("partition-1", p1)
    c.partition("partition-2", p2)
    c.shelf("shelf-mid", p1 + T / 2, p2 - T / 2, 280)
    c.shelf("shelf-l", c.x0 + T, p1 - T / 2, 280)
    c.shelf("shelf-r", p2 + T / 2, c.x1 - T, 280)
    c.backs([p1, p2])
    for name, (a, b) in (("flap_l", ops[0]), ("flap_r", ops[2])):
        c.flap(name, a, c.ybot, b, c.rt)
    return c.dump("sorbonna-0-20")


def tumba_0_21():
    """Тумба 1570 × 504 × 982 (p. 51): three columns, a drawer over a tilt-out front each."""
    c = Case(1570, 504, 982, False, top_rail=37, bottom_rail=37)
    sp = even_stiles(c.x0, c.x1, 3, 75, 75)
    ops = c.stiles(sp)
    parts_x = [(s[0] + s[1]) / 2 for s in sp[1:-1]]
    for k, x in enumerate(parts_x):
        c.partition(f"partition-{k + 1}", x)
    yd0 = 795
    for k, (a, b) in enumerate(ops):
        c.hrail(f"rail-mid-{k + 1}", a, b, 757, yd0)
        ca = c.x0 + T if k == 0 else parts_x[k - 1] + T / 2
        cb = c.x1 - T if k == 2 else parts_x[k] - T / 2
        c.shelf(f"shelf-fix-{k + 1}", ca, cb, yd0, fixed=True)
        c.shelf(f"shelf-{k + 1}", ca, cb, 420)
        c.drawer(f"drawer_{k + 1}", a, yd0, b, c.rt, ca, cb)
        c.flap(f"front_{k + 1}", a, c.ybot, b, 757, angle=40)
    c.backs(parts_x)
    return c.dump("sorbonna-0-21")


def polka_0_71():
    """Полка 1500 × 200 × 190 (wall): a 32 shelf board over the wall with a 16 back board rising behind it."""
    p = [part("back", [0, 0, 0, 1500, 190, 16], edge=2),
         part("shelf", [0, 0, 16, 1500, 32, 200], edge=3),
         part("bracket-l", [150, 32, 16, 166, 120, 110]), part("bracket-r", [1334, 32, 16, 1350, 120, 110])]
    return dump("sorbonna-0-71", [1500, 200, 190], p, [])


def stol_0_50():
    """Стол журнальный 930 × 930 × 502: a 32 top on four square block legs; under it a bottom shelf, a middle
    divider and, on the front half, a wine / magazine rack of 5 × 2 cells (the photos)."""
    W, B, H = 930, 930, 502
    p = [part("top", [0, H - 32, 0, W, H, B], edge=3)]
    L0, L1 = 20, 90
    yt = H - 32
    for k, (x, z) in enumerate([(L0, L0), (W - L1, L0), (L0, B - L1), (W - L1, B - L1)]):
        p.append(part(f"leg-{k + 1}", [x, 0, z, x + 70, yt, z + 70]))
    xa, xb = L1, W - L1
    p.append(part("shelf", [xa, 60, L0, xb, 76, B - L0]))
    p.append(part("divider", [xa, 76, 457, xb, yt, 473]))
    p.append(part("apron-l", [L0, yt - 60, L1, L0 + 16, yt, B - L1]))
    p.append(part("apron-r", [W - L0 - 16, yt - 60, L1, W - L0, yt, B - L1]))
    w = (xb - xa) / 5
    for k in range(1, 5):
        x = xa + w * k
        p.append(part(f"cell-v{k}", [x - 8, 76, 473, x + 8, yt, B - L0]))
    for k in range(5):
        a = xa + w * k + (8 if k else 0)
        b2 = xa + w * (k + 1) - (8 if k < 4 else 0)
        p.append(part(f"cell-h{k + 1}", [a, 265, 473, b2, 281, B - L0]))
    return dump("sorbonna-0-50", [W, B, H], p, [])


# ------------------------------------------------------------------------------------------------------- bedroom
def tumba_1_22():
    """Тумба прикроватная 500 × 401 × 498: an open niche over a drawer (p. 51)."""
    c = Case(500, 401, 498, False, top_rail=37, bottom_rail=37)
    (o0, o1), = c.stiles([(c.x0, c.x0 + 60), (c.x1 - 60, c.x1)])
    a, b = c.x0 + T, c.x1 - T
    c.shelf("shelf-niche", a, b, 300, fixed=True)
    c.hrail("rail-mid", o0, o1, 264, 300)
    c.drawer("drawer", o0, c.ybot, o1, 264, a, b, depth=300)
    c.backs()
    return c.dump("sorbonna-1-22")


def shkaf_1_16():
    """Шкаф для одежды 1988 × 643 × 2275 (front photo): door | two doors over two drawers | door; the p. 51 sketch:
    the outer sections hang (hat shelf, rail, two shelves at the bottom), the middle one has five shelves."""
    c = Case(1988, 643, 2275, True, top_rail=57, bottom_rail=42)
    sp = [(c.x0, 84), (505, 573), (1415, 1483), (1904, c.x1)]
    ops = c.stiles(sp)
    p1, p2 = (sp[1][0] + sp[1][1]) / 2, (sp[2][0] + sp[2][1]) / 2
    c.partition("partition-1", p1)
    c.partition("partition-2", p2)
    secs = [(c.x0 + T, p1 - T / 2), (p1 + T / 2, p2 - T / 2), (p2 + T / 2, c.x1 - T)]
    for k in (0, 2):
        a, b = secs[k]
        s = "lr"[k // 2]
        c.shelf(f"hat-{s}", a, b, 1900)
        c.p.append({"id": f"rail-{s}", "kind": "tube", "mat": "chrome",
                    "box": box(a + 2, 1805, c.dz / 2 - 12.5, b - 2, 1830, c.dz / 2 + 12.5)})
        c.shelf(f"shelf-{s}1", a, b, 330)
        c.shelf(f"shelf-{s}2", a, b, 560)
    a, b = secs[1]
    ymid = 629
    c.shelf("shelf-drawers", a, b, ymid, fixed=True)
    for j, y in enumerate([920, 1200, 1480, 1760, 1990]):
        c.shelf(f"shelf-m{j + 1}", a, b, y)
    c.backs([p1, p2])
    (l0, l1), (m0, m1), (r0, r1) = ops
    mm = (m0 + m1) / 2
    c.door("door_1", l0, c.ybot, l1, c.rt, "left", hy=1125)
    c.door("door_2", m0, ymid, mm + G / 2, c.rt, "left", hy=1125)
    c.door("door_3", mm - G / 2, ymid, m1, c.rt, "right", hy=1125)
    c.door("door_4", r0, c.ybot, r1, c.rt, "right", hy=1125)
    c.drawer("drawer_1", m0, 367, m1, ymid, a, b, pulls=2, depth=500)
    c.drawer("drawer_2", m0, c.ybot, m1, 367, a, b, pulls=2, depth=500)
    return c.dump("sorbonna-1-16")


def bed_1_01():
    """Кровать 2-16 1814 × 2044 × 919 (x = width): a 32 headboard to the floor with a milled frame (border 80) round a
    sunk panel, a box of 25 rails and a foot board 330 high over a recessed plinth, cleats and a metal base with slats,
    the mattress 1600 × 2000."""
    W, L, H = 1814, 2044, 919
    p = [part("headboard", [0, 0, 0, W, H, 32], edge=3, face={"type": "frame", "border": 80, "depth": 5, "r": 3})]
    top = 330
    p += [part("rail-l", [0, 50, 32, 25, top, L - 25]), part("rail-r", [W - 25, 50, 32, W, top, L - 25]),
          part("foot", [0, 50, L - 25, W, top, L], edge=3),
          part("plinth-l", [40, 0, 70, 56, 50, L - 60]), part("plinth-r", [W - 56, 0, 70, W - 40, 50, L - 60]),
          part("plinth-f", [56, 0, L - 76, W - 56, 50, L - 60]),
          part("cleat-l", [25, top - 90, 60, 55, top - 60, L - 60]), part("cleat-r", [W - 55, top - 90, 60, W - 25, top - 60, L - 60])]
    x0 = (W - 1600) / 2
    base = [q for q in metal_base(x0, W - x0, 40, L - 40, top - 60 + 30, mattress=200) if not q["id"].startswith("m-leg")]
    p += base
    return dump("sorbonna-1-01", [W, L, H], p, [])


def mirror_1_40():
    """Зеркало напольное 510 × 590 × 1600: an open rack at the back (two side panels, shelves, a rail) and the
    mirror in a 25 frame leaning against it, its foot at the front (turned 12.6° back about its foot)."""
    W, B, H = 510, 590, 1600
    p = [part("rack-l", [0, 0, 0, T, H - 40, 205]), part("rack-r", [W - T, 0, 0, W, H - 40, 205]),
         part("rack-top", [T, H - 56, 0, W - T, H - 40, 205]),
         part("rack-bottom", [T, 20, 0, W - T, 36, 205]), part("rack-shelf-1", [T, 300, 0, W - T, 316, 205]),
         part("rack-shelf-2", [T, 1150, 0, W - T, 1166, 205]), part("rack-back", [T, 36, 0, W - T, 60, 16]),
         {"id": "rack-rail", "kind": "tube", "mat": "chrome", "box": box(T, 1080, 100, W - T, 1100, 120)}]
    # the leaning frame: before the turn a board 510 × Lm × 25 standing at the front (z 565…590), turned back about its
    # front foot so its top reaches y 1600
    deg = 12.6
    t = math.radians(deg)
    Lm = (H - 25 * math.sin(t)) / math.cos(t)
    rot = {"axis": "x", "deg": -deg, "about": [W / 2, 0, B - 25]}
    # one part: the milled frame with the mirror set in it (a glazed front with a mirror "glass")
    p.append(part("frame", [0, 0, B - 25, W, Lm, B], kind="front", rot=rot, edge=2,
                  glass={"frame": 45, "rebate": 4, "t": 4, "tint": "mirror"}))
    return dump("sorbonna-1-40", [W, B, H], p, [])


def catalog():
    models = [
        ("sorbonna-0-10", "П7.055.0.10", "Шкаф для книг «Сорбонна»", "living", [647, 475, 2085], 50, None),
        ("sorbonna-0-20", "П7.055.0.20", "Тумба «Сорбонна»", "living", [1480, 436, 510], 50, None),
        ("sorbonna-0-71", "П7.055.0.71", "Полка «Сорбонна»", "living", [1500, 200, 190], 50, None),
        ("sorbonna-0-11", "П7.055.0.11", "Шкаф «Сорбонна»", "living", [647, 475, 2085], 50, "универсальный"),
        ("sorbonna-0-50", "П7.055.0.50", "Стол журнальный «Сорбонна»", "tables", [930, 930, 502], 50, None),
        ("sorbonna-1-22", "П7.055.1.22", "Тумба прикроватная «Сорбонна»", "bedroom", [500, 401, 498], 51, None),
        ("sorbonna-1-16", "П7.055.1.16", "Шкаф для одежды «Сорбонна»", "bedroom", [1988, 643, 2275], 51, None),
        ("sorbonna-1-01", "П7.055.1.01", "Кровать 2-16 «Сорбонна»", "bedroom", [1814, 2044, 919], 51, "сп. место 1600×2000"),
        ("sorbonna-1-40", "П7.055.1.40", "Зеркало напольное «Сорбонна»", "decor", [510, 590, 1600], 51, None),
        ("sorbonna-0-21", "П7.055.0.21", "Тумба «Сорбонна»", "bedroom", [1570, 504, 982], 51, None),
    ]
    out = []
    for mid, code, name, cat, size, page, note in models:
        e = {"id": mid, "code": code, "name": name, "collection": "sorbonna", "category": cat, "size": size, "page": page}
        if mid == "sorbonna-0-71":
            e["mount"] = "wall"
        e["note"] = "по каталогу и фото сайта, без инструкции" + (f"; {note}" if note else "")
        out.append(e)
    frag = {
        "finishes": [{"id": "sorbonna-kobalt", "name": "Кобальт серый", "body": "door_enamel_whitey#68625f",
                      "roles": {"accent": "door_enamel_whitey#9d8c7e"}, "swatch": "#68625f"}],
        "profiles": {
            "sorbonna-crown": {"name": "Карниз «Сорбонна»: полочка, выкружка, валик; вынос 20, высота 55",
                               "pts": [[20, 0], [19, 4], [18.5, 8], [17, 10], [15, 11], [14, 14], [12.5, 19], [10, 25],
                                       [7, 31], [4.5, 36], [3, 40], [3, 44], [1.5, 46], [0.5, 49], [0, 52], [0, 55],
                                       [55, 55], [55, 0]]}},
        "collections": [{"id": "sorbonna", "name": "Сорбонна", "brand": "Пинскдрев", "finishes": ["sorbonna-kobalt"],
                         "metal": "chrome#a9a8a5",
                         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 50–51; инструкций нет — все модули по каталогу и фото сайта. Корпус ЛДСП 16 «Кобальт серый» с фасадной рамкой МДФ (стойки, ригели, утопленный цоколь), вкладные фасады с фрезерованной линией, светлый карниз, ручки-скобы сатин-никель."}],
        "models": out}
    with open(os.path.join(HERE, "sorbonna_catalog.json"), "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    for f in (shkaf_0_10, shkaf_0_11, tumba_0_20, tumba_0_21, polka_0_71, stol_0_50, tumba_1_22, shkaf_1_16, bed_1_01,
              mirror_1_40):
        print(f())
    catalog()
