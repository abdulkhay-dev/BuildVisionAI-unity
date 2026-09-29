"""«Эрида» (П7.056): every module by catalogue (pp. 18–20) — the one linked instruction is another product (see notes).

The collection's construction, read off the front-on photos of p. 18 (витрина, тумба) and the cut-outs of p. 20:
  * carcass ЛДСП 16: sides stand on the legs, the top lies over the sides and the face frame (flush with the frame's
    face), the bottom between the sides, ХДФ back in grooves 6 mm from the back edge;
  * a flat face frame of 16 mm МДФ strips in front of the carcass edges: stiles 45 wide, a top rail 28 under the top and
    a bottom rail 20 on the tall pieces (витрина, шкафы: the fronts sit in a border ≈ 45 mm on three sides), no top rail
    and a 12 mm bottom rail on the low ones (тумбы, комоды — p. 18/19 photos, fronts up to 3 mm under the top);
    middle rails 45;
  * fronts МДФ 16 inset in the frame, flush with its face, 3 mm gaps; round gold knobs Ø34 standing 26 mm off the face
    (the catalogue depth B is the carcass with its frame: the knobs stand out of it);
  * square tapered legs 180 high, 45 → 30 mm, the outer faces vertical (they taper inwards), in the body colour.
All in «Персидский жемчуг»; nothing here has cut-list numbers, parts carry ids only.
"""
from common import dump

T = 16            # board
SW = 45           # face-frame stile
TR = 28           # top rail (under the top)
BR = 20           # bottom rail
G = 3             # gaps round fronts
LEG = 180         # leg height
LOW = {"tr": 0, "br": 12}   # low pieces (тумбы, комоды): the fronts reach up to 3 mm under the top, a 12 mm bottom rail


def leg(pid, x_out, z_out, sx, sz, h=LEG, d=45, d2=30, mat="body"):
    """Square tapered leg under the corner (x_out, z_out); sx / sz = +1 when the leg lies towards +x / +z of that corner.
    The two outer faces stay vertical: the axis leans in as the section shrinks. The box is its bounds (for the checker)."""
    fx, fz = x_out + sx * d / 2, z_out + sz * d / 2
    tx, tz = x_out + sx * d2 / 2, z_out + sz * d2 / 2
    xs = sorted([x_out, x_out + sx * d])
    zs = sorted([z_out, z_out + sz * d])
    return {"id": pid, "kind": "rod", "section": "square", "mat": mat, "from": [fx, h, fz], "to": [tx, 0, tz],
            "d": d, "d2": d2, "box": [xs[0], 0, zs[0], xs[1], h, zs[1]]}


def legs4(w, z_front, z_back=0, h=LEG, extra_x=()):
    out = [leg("leg-1", 0, z_back, 1, 1, h), leg("leg-2", w, z_back, -1, 1, h),
           leg("leg-3", 0, z_front, 1, -1, h), leg("leg-4", w, z_front, -1, -1, h)]
    k = 4
    for x in extra_x:           # middle legs (a long piece): front and back, square (no taper sideways)
        for z, sz in ((z_back, 1), (z_front, -1)):
            k += 1
            p = leg(f"leg-{k}", x - 22.5, z, 1, sz, h)
            p["from"][0] = p["to"][0] = x
            out.append(p)
    return out


def knob(pid, x, y, fz):
    return {"id": pid, "kind": "handle", "model": "knob", "at": [x, y], "d": 34, "t": 10, "standoff": 16, "z": fz}


class Case:
    """A carcass on legs with the face frame; fronts inset. w, b (catalogue depth: the frame's face), h."""

    def __init__(self, w, b, h, leg_h=LEG, tr=TR, br=BR):
        self.w, self.b, self.h = w, b, h
        self.fz = b                    # the face of the frame and the fronts
        self.cz = self.fz - T          # the carcass' front edge = the back of the frame and the fronts
        self.y0 = leg_h
        self.tr, self.br = tr, br
        self.parts, self.moves = [], []
        # the opening inside the frame
        self.ox0, self.ox1 = SW, w - SW
        self.oy0, self.oy1 = leg_h + br, h - T - tr

    def carcass(self, back=True, sides=True):
        w, h, cz, fz, y0 = self.w, self.h, self.cz, self.fz, self.y0
        p = []
        if sides:
            p += [{"id": "side-l", "box": [0, y0, 0, T, h - T, cz]},
                  {"id": "side-r", "box": [w - T, y0, 0, w, h - T, cz]}]
        p += [{"id": "top", "box": [0, h - T, 0, w, h, fz]},
              {"id": "bottom", "box": [T, y0, 0, w - T, y0 + T, cz]}]
        if back:
            p.append({"id": "back", "kind": "back", "box": [T - 5, y0 + T - 5, 6, w - T + 5, h - T + 5, 9.5]})
        p += [{"id": "frame-l", "mat": "front", "box": [0, y0, cz, SW, h - T, fz]},
              {"id": "frame-r", "mat": "front", "box": [w - SW, y0, cz, w, h - T, fz]},
              {"id": "frame-b", "mat": "front", "box": [SW, y0, cz, w - SW, y0 + self.br, fz]}]
        if self.tr:
            p.append({"id": "frame-t", "mat": "front", "box": [SW, h - T - self.tr, cz, w - SW, h - T, fz]})
        self.parts += p

    def door(self, name, x0, y0, x1, y1, hinge, kx, ky, glass=None, angle=100):
        f = {"id": name, "kind": "front", "box": [x0, y0, self.cz, x1, y1, self.fz]}
        if glass:
            f["glass"] = glass
        k = knob(f"{name}-knob", kx, ky, self.fz)
        self.parts += [f, k]
        self.moves.append({"type": "door", "name": name, "parts": [name, k["id"]], "hinge": hinge, "angle": angle})

    def drawer(self, name, x0, y0, x1, y1, wall0, wall1, knobs, depth=None, box_h=None, travel=None):
        """Front x0..x1 × y0..y1; the box between the walls wall0..wall1 (13 mm runner gap), sides / back ЛДСП 16,
        ХДФ bottom in grooves; knobs: [(x, y), …]."""
        cz = self.cz
        depth = depth or min(cz - 40, 450)
        bh = box_h or max(60, min(y1 - y0 - 55, 170))
        bx0, bx1 = wall0 + 13, wall1 - 13
        by0 = y0 + 20
        z0 = cz - depth
        box = [{"id": f"{name}-side-l", "box": [bx0, by0, z0, bx0 + T, by0 + bh, cz]},
               {"id": f"{name}-side-r", "box": [bx1 - T, by0, z0, bx1, by0 + bh, cz]},
               {"id": f"{name}-back", "box": [bx0 + T, by0, z0, bx1 - T, by0 + bh, z0 + T]},
               {"id": f"{name}-bottom", "kind": "back", "box": [bx0 + 11, by0 + 10, z0 + 4, bx1 - 11, by0 + 13.5, cz - 2]}]
        f = {"id": name, "kind": "front", "box": [x0, y0, cz, x1, y1, self.fz]}
        ks = [knob(f"{name}-knob{i + 1}", kx, ky, self.fz) for i, (kx, ky) in enumerate(knobs)]
        self.parts += [f] + box + ks
        self.moves.append({"type": "drawer", "name": name, "parts": [name] + [q["id"] for q in box] + [k["id"] for k in ks],
                           "travel": travel or int(depth * 0.75)})

    def shelf(self, pid, x0, x1, y, z0=20, z1=None, fixed=False):
        z1 = z1 if z1 is not None else self.cz - 4
        c = 0 if fixed else 1
        self.parts.append({"id": pid, "box": [x0 + c, y, z0, x1 - c, y + T, z1]})

    def glass_shelf(self, pid, x0, x1, y, z0=20, z1=None):
        z1 = z1 if z1 is not None else self.cz - 28
        self.parts.append({"id": pid, "kind": "glass", "box": [x0 + 2, y, z0, x1 - 2, y + 6, z1]})

    def rail(self, x0, x1, y):
        zc = (self.cz + 9.5) / 2
        self.parts.append({"id": "rail", "kind": "tube", "mat": "chrome", "box": [x0 + 4, y, zc - 10, x1 - 4, y + 20, zc + 10]})

    def partition(self, pid, xc, y0, y1, z0=9.5):
        self.parts.append({"id": pid, "box": [xc - T / 2, y0, z0, xc + T / 2, y1, self.cz]})

    def legs(self, extra_x=()):
        self.parts += legs4(self.w, self.fz, 0, self.y0, extra_x)

    def dump(self, did):
        return dump(did, [self.w, self.b, self.h], self.parts, self.moves)


def split(a0, a1, n, g=G):
    """n fronts between a0 and a1 (the opening) with gaps g round and between them."""
    s = (a1 - a0 - (n + 1) * g) / n
    return [(round(a0 + g + i * (s + g), 1), round(a0 + g + i * (s + g) + s, 1)) for i in range(n)]


# ------------------------------------------------------------------------------------------------ living room
def vitrina():
    """Шкаф-витрина 0.17, 600×450×2000: a glazed door (bronze glass) over a solid one, glazed sides above the belt."""
    c = Case(600, 450, 2000)
    w, h, cz, fz, y0 = c.w, c.h, c.cz, c.fz, c.y0
    belt0, belt1 = 697, 742                      # the middle rail of the frame (the "belt" between the doors)
    mid = 711                                    # fixed middle panel behind it, full width: the sides split at it
    c.parts += [
        {"id": "side-l", "box": [0, y0, 0, T, mid, cz]},
        {"id": "side-r", "box": [w - T, y0, 0, w, mid, cz]},
        {"id": "middle", "box": [0, mid, 0, w, mid + T, cz]},
    ]
    # the upper sides: glazed frames standing on the middle panel — МДФ stiles / rails 40 wide round bronze glass
    ys0, ys1, fw = mid + T, h - T, 40
    for tag, x0 in (("l", 0), ("r", w - T)):
        c.parts += [
            {"id": f"sframe-{tag}-back", "mat": "front", "box": [x0, ys0, 0, x0 + T, ys1, fw]},
            {"id": f"sframe-{tag}-front", "mat": "front", "box": [x0, ys0, cz - fw, x0 + T, ys1, cz]},
            {"id": f"sframe-{tag}-bottom", "mat": "front", "box": [x0, ys0, fw, x0 + T, ys0 + fw, cz - fw]},
            {"id": f"sframe-{tag}-top", "mat": "front", "box": [x0, ys1 - fw, fw, x0 + T, ys1, cz - fw]},
            {"id": f"sglass-{tag}", "kind": "glass", "box": [x0 + 6, ys0 + fw, fw, x0 + 10, ys1 - fw, cz - fw]},
        ]
    c.parts += [
        {"id": "top", "box": [0, h - T, 0, w, h, fz]},
        {"id": "bottom", "box": [T, y0, 0, w - T, y0 + T, cz]},
        {"id": "back-low", "kind": "back", "box": [T - 5, y0 + T - 5, 6, w - T + 5, mid + 5, 9.5]},
        {"id": "back-up", "kind": "back", "box": [T - 5, mid + T - 5, 6, w - T + 5, h - T + 5, 9.5]},
        {"id": "frame-l", "mat": "front", "box": [0, y0, cz, SW, h - T, fz]},
        {"id": "frame-r", "mat": "front", "box": [w - SW, y0, cz, w, h - T, fz]},
        {"id": "frame-t", "mat": "front", "box": [SW, h - T - TR, cz, w - SW, h - T, fz]},
        {"id": "frame-m", "mat": "front", "box": [SW, belt0, cz, w - SW, belt1, fz]},
        {"id": "frame-b", "mat": "front", "box": [SW, y0, cz, w - SW, y0 + BR, fz]},
    ]
    c.shelf("shelf", T, w - T, 440)
    for i, y in enumerate([1033, 1348, 1656]):   # glass shelves on pins (their tops at 1039 / 1354 / 1662, p. 18)
        c.glass_shelf(f"glass-{i + 1}", T, w - T, y)
    c.door("door-glass", SW + G, belt1 + G, w - SW - G, h - T - TR - G, "left", 522, 1354,
           glass={"frame": 30, "rebate": 6, "t": 4, "tint": "bronze"}, angle=105)
    c.door("door", SW + G, y0 + BR + G, w - SW - G, belt0 - G, "left", 522, 451)
    c.legs()
    return c.dump("erida-0-17")


def tumba():
    """Тумба 0.21, 1632×450×709: two doors, a niche over a drawer in the middle; six legs."""
    c = Case(1632, 450, 709, **LOW)
    c.carcass()
    (a0, a1), (b0, b1), (d0, d1) = split(c.ox0, c.ox1, 3)
    p1, p2 = (a1 + b0) / 2, (b1 + d0) / 2        # partitions behind the gaps
    c.partition("part-1", p1, c.y0 + T, c.h - T)
    c.partition("part-2", p2, c.y0 + T, c.h - T)
    # the niche floor: its edge flush with the fronts, the niche open up to the top rail
    ny = 440
    c.parts.append({"id": "niche-floor", "box": [p1 + T / 2, ny, 0, p2 - T / 2, ny + T, c.fz]})
    c.shelf("shelf-l", T, p1 - T / 2, 430)
    c.shelf("shelf-r", p2 + T / 2, c.w - T, 430)
    fy0, fy1 = c.oy0 + G, c.oy1 - G
    c.door("door-l", a0, fy0, a1, fy1, "left", a1 - 21, 421)
    c.door("door-r", d0, fy0, d1, fy1, "right", d0 + 21, 421)
    c.drawer("drawer", b0, fy0, b1, ny - G, p1 + T / 2, p2 - T / 2, [((b0 + b1) / 2, 403)], box_h=150)
    c.legs(extra_x=[c.w / 2])
    return c.dump("erida-0-21")


# ------------------------------------------------------------------------------------------------ bedroom
def wardrobe2():
    """Шкаф для одежды 2Д 1.12, 1050×587×2260: two doors over a full-width drawer; inside a hat shelf, shelves on the
    left of a partition, a hanging rail on the right (the sketch beside the cut-out, p. 20)."""
    c = Case(1050, 587, 2260)
    c.carcass()
    (a0, a1), (b0, b1) = split(c.ox0, c.ox1, 2)
    fy0 = c.oy0 + G
    dtop = fy0 + 230                               # the drawer front 230 high (p. 20 photo)
    c.shelf("over-drawer", T, c.w - T, dtop - 6, z0=9.5, fixed=True)
    c.partition("part", 460, dtop + 10, 1880)
    c.shelf("hat", T, c.w - T, 1880, z0=9.5, fixed=True)
    for i, y in enumerate([830, 1180, 1530]):
        c.shelf(f"shelf-{i + 1}", T, 460 - T / 2, y)
    c.rail(460 + T / 2, c.w - T, 1800)
    c.door("door-l", a0, dtop + G, a1, c.oy1 - G, "left", a1 - 40, 1310)
    c.door("door-r", b0, dtop + G, b1, c.oy1 - G, "right", b0 + 40, 1310)
    fw = c.ox1 - c.ox0 - 2 * G
    c.drawer("drawer", c.ox0 + G, fy0, c.ox1 - G, dtop, T, c.w - T,
             [(c.ox0 + G + fw * 0.25, (fy0 + dtop) / 2), (c.ox0 + G + fw * 0.75, (fy0 + dtop) / 2)], box_h=150)
    c.legs()
    return c.dump("erida-1-12")


def wardrobe3():
    """Шкаф для одежды 3Д 1.16, 1532×588×2259: a full-height door on the left (shelves), two doors over three drawers
    on the right (hat shelf, hanging rail)."""
    c = Case(1532, 588, 2259)
    c.carcass()
    (a0, a1), (b0, b1), (d0, d1) = split(c.ox0, c.ox1, 3)
    p1 = (a1 + b0) / 2
    fy0 = c.oy0 + G
    rows = split(c.oy0, 902 + G, 3)                # three drawers 230 high, doors from 902
    top_d = rows[-1][1]
    c.partition("part", p1, c.y0 + T, c.h - T)
    c.shelf("over-drawers", p1 + T / 2, c.w - T, top_d - 6, z0=9.5, fixed=True)
    c.shelf("hat", p1 + T / 2, c.w - T, 1880, z0=9.5, fixed=True)
    c.rail(p1 + T / 2, c.w - T, 1800)
    for i, y in enumerate([560, 900, 1240, 1580, 1920]):
        c.shelf(f"shelf-{i + 1}", T, p1 - T / 2, y)
    c.door("door-l", a0, fy0, a1, c.oy1 - G, "left", a1 - 21, 1210)
    c.door("door-m", b0, top_d + G, b1, c.oy1 - G, "left", b1 - 40, 1210)
    c.door("door-r", d0, top_d + G, d1, c.oy1 - G, "right", d0 + 40, 1210)
    fw = d1 - b0
    for i, (y0, y1) in enumerate(rows):
        yc = (y0 + y1) / 2
        c.drawer(f"drawer-{i + 1}", b0, y0, d1, y1, p1 + T / 2, c.w - T, [(b0 + fw * 0.26, yc), (b0 + fw * 0.76, yc)], box_h=150)
    c.legs(extra_x=[p1])
    return c.dump("erida-1-16")


def komod31():
    """Комод 1.31, 854×450×1337: two small drawers on top, four wide ones under them."""
    c = Case(854, 450, 1337, **LOW)
    c.carcass()
    # the top row is lower (≈175), the four under it 225 each (p. 19 photo, p. 20 cut-out)
    ys, y = [], c.oy0 + G
    for hh in (225, 225, 225, 225, c.oy1 - c.oy0 - 6 * G - 900):
        ys.append((y, y + hh))
        y += hh + G
    assert abs(ys[-1][1] + G - c.oy1) < 0.6, ys
    (a0, a1), (b0, b1) = split(c.ox0, c.ox1, 2)
    pm = (a1 + b0) / 2
    c.partition("part-top", pm, ys[3][1] - 10, c.h - T)
    c.shelf("under-top-row", T, c.w - T, ys[3][1] - 26, z0=9.5, fixed=True)
    fw = c.ox1 - c.ox0 - 2 * G
    for i, (y0, y1) in enumerate(ys[:4]):
        yc = (y0 + y1) / 2
        c.drawer(f"drawer-{i + 1}", c.ox0 + G, y0, c.ox1 - G, y1, T, c.w - T,
                 [(c.ox0 + G + fw * 0.25, yc), (c.ox0 + G + fw * 0.75, yc)], box_h=150 if i < 3 else 130)
    y0, y1 = ys[4]
    c.drawer("drawer-5l", a0, y0, a1, y1, T, pm - T / 2, [((a0 + a1) / 2, (y0 + y1) / 2)], box_h=110)
    c.drawer("drawer-5r", b0, y0, b1, y1, pm + T / 2, c.w - T, [((b0 + b1) / 2, (y0 + y1) / 2)], box_h=110)
    c.legs()
    return c.dump("erida-1-31")


def komod32():
    """Комод 1.32, 1622×450×928: four drawers in the top row, two and two under them; six legs."""
    c = Case(1622, 450, 928, **LOW)
    c.carcass()
    rows = split(c.oy0, c.oy1, 3)
    halves = split(c.ox0, c.ox1, 2)
    quarters = split(c.ox0, c.ox1, 4)
    pm = (halves[0][1] + halves[1][0]) / 2
    c.partition("part-m", pm, c.y0 + T, c.h - T)
    ry = rows[1][1] - 20                           # the fixed panel under the top row carries its two partitions
    c.shelf("under-top-l", T, pm - T / 2, ry, z0=9.5, fixed=True)
    c.shelf("under-top-r", pm + T / 2, c.w - T, ry, z0=9.5, fixed=True)
    q1 = (quarters[0][1] + quarters[1][0]) / 2
    q3 = (quarters[2][1] + quarters[3][0]) / 2
    c.partition("part-q1", q1, ry + T, c.h - T)
    c.partition("part-q3", q3, ry + T, c.h - T)
    walls = [(T, pm - T / 2), (pm + T / 2, c.w - T)]
    k = 0
    for r in (0, 1):
        y0, y1 = rows[r]
        for (x0, x1), (w0, w1) in zip(halves, walls):
            k += 1
            fw = x1 - x0
            c.drawer(f"drawer-{k}", x0, y0, x1, y1, w0, w1, [(x0 + fw * 0.25, (y0 + y1) / 2), (x0 + fw * 0.75, (y0 + y1) / 2)],
                     box_h=150 if r == 0 else 130)
    y0, y1 = rows[2]
    qwalls = [(T, q1 - T / 2), (q1 + T / 2, pm - T / 2), (pm + T / 2, q3 - T / 2), (q3 + T / 2, c.w - T)]
    for (x0, x1), (w0, w1) in zip(quarters, qwalls):
        k += 1
        c.drawer(f"drawer-{k}", x0, y0, x1, y1, w0, w1, [((x0 + x1) / 2, (y0 + y1) / 2)], box_h=130)
    c.legs(extra_x=[pm])
    return c.dump("erida-1-32")


def bedside():
    """Тумба прикроватная 1.22, 508×450×623: two drawers."""
    c = Case(508, 450, 623, **LOW)
    c.carcass()
    for i, (y0, y1) in enumerate(split(c.oy0, c.oy1, 2)):
        c.drawer(f"drawer-{i + 1}", c.ox0 + G, y0, c.ox1 - G, y1, T, c.w - T, [(c.w / 2, (y0 + y1) / 2)], box_h=120)
    c.legs()
    return c.dump("erida-1-22")


# ------------------------------------------------------------------------------------------------ tables, shelf, mirror
def desk():
    """Стол письменный 2.52, 1400×650×761: a framed pedestal on four legs (an open niche over two drawers) on the left,
    a panel leg on the right, a modesty panel between them, the top over all."""
    W, B, H = 1400, 650, 761
    c = Case(500, B, H, **LOW)
    c.carcass()
    for p in c.parts:
        if p["id"] == "top":
            p["box"] = [0, H - T, 0, W, H, B]
    niche = 621                                    # the niche floor (its edge flush with the fronts): niche ≈ 108 high
    c.parts += [{"id": "niche-floor", "box": [T, niche, 0, c.w - T, niche + T, c.cz]},
                {"id": "frame-m", "mat": "front", "box": [SW, niche, c.cz, c.w - SW, niche + T, c.fz]}]
    for i, (y0, y1) in enumerate(split(c.oy0, niche, 2)):
        c.drawer(f"drawer-{i + 1}", c.ox0 + G, y0, c.ox1 - G, y1, T, c.w - T, [(c.w / 2, (y0 + y1) / 2)], box_h=130)
    c.legs()
    c.parts += [{"id": "leg-panel", "box": [W - 25, 0, 0, W, H - T, B]},
                {"id": "modesty", "box": [c.w, 420, 40, W - 25, H - T, 56]}]
    c.w = W
    return c.dump("erida-2-52")


def dressing():
    """Стол туалетный 1.51, 1142×451×800: panel legs 25 to the floor, a drawer on each side, in the middle a lid in the
    top with the mirror under it (it lifts on hinges at the back) over a shallow tray behind a fixed apron."""
    W, B, H = 1142, 451, 800
    fz, cz = B, B - T
    S = 25
    pl, pr = 329, 797                              # partitions (left faces) under the top between drawers and tray
    lid0, lid1, zl = 340, 802, 60
    p = [
        {"id": "side-l", "box": [0, 0, 0, S, H - T, fz]},
        {"id": "side-r", "box": [W - S, 0, 0, W, H - T, fz]},
        {"id": "top-l", "box": [0, H - T, 0, lid0, H, fz]},
        {"id": "top-r", "box": [lid1, H - T, 0, W, H, fz]},
        {"id": "top-back", "box": [lid0, H - T, 0, lid1, H, zl]},
        {"id": "lid", "kind": "front", "mat": "body", "box": [lid0, H - T, zl, lid1, H, fz]},
        {"id": "mirror", "kind": "mirror", "box": [352, H - T - 8, zl + 10, 790, H - T - 3, cz - 5]},
        {"id": "part-l", "box": [pl, 600, 25.5, pl + T, H - T, cz]},
        {"id": "part-r", "box": [pr, 600, 25.5, pr + T, H - T, cz]},
        {"id": "tray-bottom", "box": [pl + T, 683, zl, pr, 699, cz]},
        {"id": "tray-back", "box": [pl + T, 699, zl - T, pr, H - T, zl]},   # the modesty panel closes the tray below
        {"id": "apron", "kind": "front", "box": [338.5, 683, cz, 803.5, H - T - G, fz]},
        {"id": "modesty", "box": [S, 330, 9.5, W - S, 699, 25.5]},
    ]
    c = Case(W, B, H)
    c.parts = p
    y0, y1 = 603, H - T - G
    c.drawer("drawer-l", S + 2, y0, 335.5, y1, S, pl, [((S + 2 + 335.5) / 2, (y0 + y1) / 2)], box_h=120)
    c.drawer("drawer-r", 806.5, y0, W - S - 2, y1, pr + T, W - S, [((806.5 + W - S - 2) / 2, (y0 + y1) / 2)], box_h=120)
    c.moves.append({"type": "flap", "name": "lid", "parts": ["lid", "mirror"], "hinge": "top", "axis": [H, zl], "angle": 95})
    return c.dump("erida-1-51")


def shelf():
    """Полка 2.71, 1142×318×350, on the wall: an open box (no back — the wall shows through on p. 20)."""
    W, B, H = 1142, 318, 350
    p = [{"id": "top", "box": [0, H - T, 0, W, H, B]},
         {"id": "bottom", "box": [0, 0, 0, W, T, B]},
         {"id": "side-l", "box": [0, T, 0, T, H - T, B]},
         {"id": "side-r", "box": [W - T, T, 0, W, H - T, B]}]
    return dump("erida-2-71", [W, B, H], p, [])


def mirror():
    """Зеркало 1.42, 620×22×620: a round frame (ring 75 wide) over a round mirror, on the wall."""
    p = [{"id": "frame", "shape": "ring", "inner": 470, "box": [0, 0, 6, 620, 620, 22], "edge": 3},
         {"id": "mirror", "kind": "mirror", "shape": "circle", "box": [60, 60, 2, 560, 560, 6]},
         {"id": "bumpers", "kind": "panel", "mat": "black", "box": [300, 40, 0, 320, 60, 2]}]
    return dump("erida-1-42", [620, 22, 620], p, [])


# ------------------------------------------------------------------------------------------------ beds
def bed(did, W, sleep_w):
    """Кровать: a headboard 22 with a milled frame face, side rails and a foot 16 on four tapered legs, cleats and slats
    inside, a middle beam on two glides; the mattress sleep_w × 2000."""
    L, H = 2040, 1003
    hb, ft, rail_top = 22, 16, 400
    p = [{"id": "headboard", "box": [0, LEG, 0, W, H, hb], "face": {"type": "frame", "border": 55, "depth": 4, "r": 2}},
         {"id": "rail-l", "box": [0, LEG, hb, T, rail_top, L - ft]},
         {"id": "rail-r", "box": [W - T, LEG, hb, W, rail_top, L - ft]},
         {"id": "foot", "box": [0, LEG, L - ft, W, rail_top, L]},
         {"id": "cleat-l", "box": [T, 300, hb, T + 30, 330, L - ft]},
         {"id": "cleat-r", "box": [W - T - 30, 300, hb, W - T, 330, L - ft]},
         {"id": "beam", "box": [W / 2 - 20, 270, hb, W / 2 + 20, 330, L - ft]},
         {"id": "beam-leg-1", "kind": "tube", "mat": "black", "box": [W / 2 - 15, 0, 700, W / 2 + 15, 270, 730]},
         {"id": "beam-leg-2", "kind": "tube", "mat": "black", "box": [W / 2 - 15, 0, 1330, W / 2 + 15, 270, 1360]}]
    for i in range(24):
        z = hb + 30 + i * 82
        p.append({"id": f"slat-{i + 1}", "kind": "panel", "mat": "door_enamel_whitey#c9a877",
                  "box": [T + 30, 330, z, W - T - 30, 338, z + 53]})
    mx = (W - sleep_w) / 2
    p.append({"id": "mattress", "kind": "mattress", "box": [mx, 338, hb + 1, mx + sleep_w, 538, hb + 2001]})
    p += legs4(W, L, 0, LEG)
    return dump(did, [W, L, H], p, [])


if __name__ == "__main__":
    for f in (vitrina, tumba, wardrobe2, wardrobe3, komod31, komod32, bedside, desk, dressing, shelf, mirror):
        print(f())
    print(bed("erida-1-02", 1728, 1600))
    print(bed("erida-1-04", 1328, 1200))
