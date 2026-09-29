"""«Сати» (П7.057): all 18 modules by catalogue and product photos — no instruction exists (a.pinskdrev.by/ru has no
IS-P7-057-*; index.json lists none).

Sources: catalogue pp. 21–24 (the living-room photo p. 21 is nearly front-on; the bedroom / hall photos pp. 22–23; the
close-ups of the fronts and handles p. 23; the module cut-outs, the wardrobe interior sketches and the «Персидский жемчуг»
swatch p. 24) and the product photos of pinskdrev.by (the 4Д wardrobe П7.057.1.17 is photographed square to the camera:
the proportions below come from it — 0.67 px/mm across, 0.65 px/mm up).

Construction (one system, measured on the photos, the catalogue sizes as the scale):
  * carcass ЛДСП 16 on square tapered legs (50 → 34, the end legs splayed 10 mm outwards) 85 high under the
    wardrobes, 100 under the other pieces; sides from the legs up, the bottom between them, ХДФ back in grooves;
  * tall pieces (шкафы, вешалка): a crown cornice 44 high over the carcass top, 40 mm out at the front and both sides,
    and an 18-mm cap over it (together 62: the 4Д photo); low pieces: a 22-mm top 12 mm over the sides and the fronts;
  * overlay fronts МДФ 19 (2 mm reveal, 3 mm gaps) with a milled frame — a flat border 55 / 45, a stepped bead
    (profile sati-bead) sinking to the panel — and two bronze patina lines along the bead (thin rods, role "patina");
    the small drawers of the living-room pieces and the wardrobes are plain (the photos); glazed doors with the same
    border round clear glass;
  * cast bronze bow handles c-c 128 (the catalogue: vertical on doors by the free edge, horizontal on drawers — two
    per drawer wider than 700);
  * drawer boxes ЛДСП 16 with ХДФ bottoms, 13 mm runner gap, 400 / 500 deep.

    python3 tools/casegoods/gen/sati.py      # Designs/sati-*.json, gen/sati_catalog.json
"""
import json
import os

from kit_w3a import (back, bow, box, cornice, drawer_box, dump, fmt, ids, leg_square, line_rect, metal_base, part, ring)

HERE = os.path.dirname(os.path.abspath(__file__))
T, FT = 16, 19
OV, CR, CAP = 40, 44, 18          # tall: cornice overhang, crown height, cap
OVL, TOPT = 12, 22                # low: top overhang, top thickness
G, RV = 3, 2                      # gaps between fronts, reveal at the carcass edges


def face(border):
    return {"type": "frame", "border": border, "depth": 4, "r": 1.5, "profile": "sati-bead"}


def sfront(pid, x0, y0, x1, y1, z0, framed=True, border=None, n=None):
    """An overlay front МДФ 19; framed: the milled frame + bead + two patina lines."""
    if border is None:
        border = 55 if min(x1 - x0, y1 - y0) > 300 else 42
    f = part(pid, [x0, y0, z0, x1, y1, z0 + FT], n, kind="front")
    out = [f]
    if framed:
        f["face"] = face(border)
        zf = z0 + FT
        out += line_rect(f"{pid}-pa", x0 + border + 0.8, y0 + border + 0.8, x1 - border - 0.8, y1 - border - 0.8, zf - 0.6)
        out += line_rect(f"{pid}-pb", x0 + border + 16, y0 + border + 16, x1 - border - 16, y1 - border - 16, zf - 3.4)
    return out


def sglazed(pid, x0, y0, x1, y1, z0):
    fr = part(pid, [x0, y0, z0, x1, y1, z0 + FT], kind="front",
              glass={"frame": 58, "rebate": 4, "t": 4, "tint": "clear"})
    zf = z0 + FT
    out = [fr, ring(f"{pid}-gb", x0 + 62, y0 + 62, x1 - 62, y1 - 62, z0 + FT / 2 + 2, "sati-gbead")]
    out += line_rect(f"{pid}-pa", x0 + 60, y0 + 60, x1 - 60, y1 - 60, zf - 0.6)
    return out


def vhandle(pid, x, y, z, toward=1):
    return bow(pid, x, y, z, cc=128, rise=-5 * toward, off=24, d=9, vertical=True)


def hhandle(pid, x, y, z):
    return bow(pid, x, y, z, cc=128, rise=5, off=24, d=9)


def cols(x0, x1, ws=None, n=None):
    """Front columns over the carcass x0..x1 (reveal RV at the ends, G between); ws = relative widths."""
    ws = ws or [1] * n
    free = x1 - x0 - 2 * RV - G * (len(ws) - 1)
    out, x = [], x0 + RV
    for w in ws:
        a = free * w / sum(ws)
        out.append((round(x * 2) / 2, round((x + a) * 2) / 2))
        x += a + G
    return out


def rows(y0, y1, hs=None, n=None):
    hs = hs or [1] * n
    free = y1 - y0 - G * (len(hs) - 1)
    out, y = [], y0
    for h in hs:
        a = free * h / sum(hs)
        out.append((round(y * 2) / 2, round((y + a) * 2) / 2))
        y += a + G
    return out


class Case:
    """The carcass of a Sati piece. tall = cornice + cap; else a 22 top. Coordinates: x0..x1 the carcass, the
    sides 0..dz deep, the fronts dz..fz, the carcass top at yt (under the cornice / the top board)."""

    def __init__(self, W, B, H, tall, leg):
        self.W, self.B, self.H, self.tall, self.leg = W, B, H, tall, leg
        ov = OV if tall else OVL
        self.x0, self.x1 = ov, W - ov
        self.dz = B - ov - FT
        self.fz = self.dz + FT
        self.yt = H - CR - CAP if tall else H - TOPT
        self.p, self.m = [], []
        x0, x1, dz, yt = self.x0, self.x1, self.dz, self.yt
        self.p += [part("side-l", [x0, leg, 0, x0 + T, yt, dz]), part("side-r", [x1 - T, leg, 0, x1, yt, dz]),
                   part("bottom", [x0 + T, leg, 0, x1 - T, leg + T, dz])]
        if tall:
            self.p.append(part("top", [x0 + T, yt - T, 0, x1 - T, yt, dz]))
            self.p.append(cornice("cornice", 0, W, 0, B, yt, "sati-crown"))
            self.p.append(part("cap", [0, H - CAP, 0, W, H, B], edge=4))
        else:
            self.p.append(part("top", [0, yt, 0, W, H, B], edge=3))
        self.fy0 = leg + 1                                   # fronts cover the bottom's edge
        self.fy1 = yt - 2 if tall else yt - G
        self.inner_top = yt - T if tall else yt


    def partition(self, pid, xc, y0=None, y1=None):
        self.p.append(part(pid, [xc - T / 2, y0 or self.leg + T, 10, xc + T / 2, y1 or self.inner_top, self.dz]))

    def shelf(self, pid, a, b, y, fixed=False):
        if fixed:
            self.p.append(part(pid, [a, y - T, 10, b, y, self.dz]))
        else:
            self.p.append(part(pid, [a + 1, y - T, 20, b - 1, y, self.dz - 20]))

    def glass_shelf(self, pid, a, b, y):
        self.p.append(part(pid, [a + 2, y - 6, 20, b - 2, y, self.dz - 25], kind="glass"))

    def rail(self, pid, a, b, y):
        self.p.append({"id": pid, "kind": "tube", "mat": "chrome", "box": box(a + 2, y - 12.5, self.dz / 2 - 12.5, b - 2,
                                                                                 y + 12.5, self.dz / 2 + 12.5)})

    def legs(self, xs, splay=10):
        zs = [45, self.dz - 40]
        k = 0
        for x in xs:
            sx = -splay if x == min(xs) else (splay if x == max(xs) else 0)
            for z, sz in zip(zs, (-6, 6)):
                k += 1
                self.p.append(leg_square(f"leg-{k}", x, z, self.leg, sx=sx, sz=sz))

    def door(self, name, x0, y0, x1, y1, hinge, hy=None, framed=True, glazed=False):
        fr = sglazed(f"f-{name}", x0, y0, x1, y1, self.dz) if glazed else sfront(f"f-{name}", x0, y0, x1, y1, self.dz, framed)
        hx = x1 - 26 if hinge == "left" else x0 + 26
        h = vhandle(f"h-{name}", hx, hy if hy is not None else (y0 + y1) / 2, self.fz, 1 if hinge == "left" else -1)
        self.p += fr + h
        self.m.append({"type": "door", "name": name, "parts": ids(fr + h), "hinge": hinge, "angle": 105})

    def drawer(self, name, x0, y0, x1, y1, c0, c1, framed=True, depth=None, pulls=None):
        """A drawer front x0..x1 × y0..y1 over the opening c0..c1 (between the sides / partitions)."""
        fr = sfront(f"f-{name}", x0, y0, x1, y1, self.dz, framed)
        d = depth or (500 if self.dz >= 540 else 400 if self.dz >= 430 else 350)
        bh = max(80, min(200, y1 - y0 - 45))
        bx = drawer_box(name, c0 + 13, c1 - 13, y0 + 18, bh, self.dz - d, self.dz)
        n = pulls or (2 if x1 - x0 > 700 else 1)
        hs = []
        for k in range(n):
            cx = x0 + (x1 - x0) * (k + 1) / (n + 1) if n > 1 else (x0 + x1) / 2
            hs += hhandle(f"h-{name}-{k + 1}", cx, (y0 + y1) / 2, self.fz)
        self.p += fr + bx + hs
        self.m.append({"type": "drawer", "name": name, "parts": ids(fr + bx + hs), "travel": d - 60})

    def dump(self, did):
        return dump(did, [self.W, self.B, self.H], self.p, self.m)


def fix_backs(c, xs=()):
    """ХДФ backs in grooves: 8 mm into the sides / partitions and the bottom / top."""
    edges = [c.x0 + 8] + list(xs) + [c.x1 - 8]
    ytop = c.inner_top + 8 if c.tall else c.yt - 0.5
    for k in range(len(edges) - 1):
        c.p.append(back(f"back-{k + 1}" if len(edges) > 2 else "back", [edges[k], c.leg + 8, 6, edges[k + 1], ytop, 9.5]))


# ----------------------------------------------------------------------------------------------------- living room
def shkaf_0_10():
    c = Case(608, 475, 2170, True, 100)
    (a, b), = cols(c.x0, c.x1, n=1)
    ly, dy, gy = rows(c.fy0, c.fy1, [610, 200, 1189])
    c.shelf("shelf-low-fix", c.x0 + T, c.x1 - T, 720, fixed=True)
    c.shelf("shelf-drawer", c.x0 + T, c.x1 - T, 924, fixed=True)
    c.shelf("shelf-1", c.x0 + T, c.x1 - T, 420)
    for k, y in enumerate([1215, 1510, 1805]):
        c.glass_shelf(f"glass-{k + 1}", c.x0 + T, c.x1 - T, y)
    fix_backs(c)
    c.door("door_low", a, ly[0], b, ly[1], "left", hy=420)
    c.drawer("drawer", a, dy[0], b, dy[1], c.x0 + T, c.x1 - T, framed=False)
    c.door("door_glass", a, gy[0], b, gy[1], "left", hy=1190, glazed=True)
    c.legs([c.x0 + 40, c.x1 - 40])
    return c.dump("sati-0-10")


def shkaf_0_11():
    c = Case(1130, 475, 2170, True, 100)
    xm = c.W / 2
    c.partition("partition", xm, c.leg + T, 300.5 - T)
    c.shelf("shelf-drawer", c.x0 + T, c.x1 - T, 300.5, fixed=True)
    c.partition("partition-up", xm, 300.5, c.inner_top)
    for side, (a, b) in (("l", (c.x0 + T, xm - T / 2)), ("r", (xm + T / 2, c.x1 - T))):
        for k, y in enumerate([700, 1060, 1420, 1780]):
            c.shelf(f"shelf-{side}{k + 1}", a, b, y)
    fix_backs(c, [xm])
    (l0, l1), (r0, r1) = cols(c.x0, c.x1, n=2)
    dy, gy = rows(c.fy0, c.fy1, [190, 1812])
    c.drawer("drawer_l", l0, dy[0], l1, dy[1], c.x0 + T, xm - T / 2, framed=False)
    c.drawer("drawer_r", r0, dy[0], r1, dy[1], xm + T / 2, c.x1 - T, framed=False)
    c.door("door_l", l0, gy[0], l1, gy[1], "left", hy=1200, glazed=True)
    c.door("door_r", r0, gy[0], r1, gy[1], "right", hy=1200, glazed=True)
    c.legs([c.x0 + 40, xm, c.x1 - 40])
    return c.dump("sati-0-11")


def tumba_0_21():
    c = Case(1990, 445, 712, False, 90)
    (l0, l1), (m0, m1), (r0, r1) = cols(c.x0, c.x1, [508, 940, 508])
    p1, p2 = (l1 + m0) / 2, (m1 + r0) / 2
    c.partition("partition-1", p1)
    c.partition("partition-2", p2)
    c.shelf("shelf-l", c.x0 + T, p1 - T / 2, 400)
    c.shelf("shelf-r", p2 + T / 2, c.x1 - T, 400)
    fix_backs(c, [p1, p2])
    c.door("door_l", l0, c.fy0, l1, c.fy1, "left", hy=(c.fy0 + c.fy1) / 2 + 60)
    c.door("door_r", r0, c.fy0, r1, c.fy1, "right", hy=(c.fy0 + c.fy1) / 2 + 60)
    for k, (y0, y1) in enumerate(rows(c.fy0, c.fy1, n=3)):
        c.drawer(f"drawer_{3 - k}", m0, y0, m1, y1, p1 + T / 2, p2 - T / 2, framed=False)
    c.legs([c.x0 + 40, p1, p2, c.x1 - 40])
    return c.dump("sati-0-21")


# -------------------------------------------------------------------------------------------------------- bedroom
def wardrobe(did, W, n):
    """Шкафы 2Д / 3Д / 4Д: doors over a row of drawers 200 high (the 4Д photo); interiors after the p. 24 sketches:
    2Д shelves | rail; 3Д shelves | rail (2 doors); 4Д shelves | rail (2 doors) | shelves."""
    c = Case(W, 630, 2200, True, 85)
    fc = cols(c.x0, c.x1, n=n)
    dy, gy = rows(c.fy0, c.fy1, [200, 1846])
    # sections: partitions behind the joints that bound them
    if n == 2:
        secs = [(0, 1, "shelves"), (1, 2, "rail")]
        hinges = ["left", "right"]
    elif n == 3:
        secs = [(0, 1, "shelves"), (1, 3, "rail")]
        hinges = ["left", "right", "right"]
    else:
        secs = [(0, 1, "shelves"), (1, 3, "rail"), (3, 4, "shelves")]
        hinges = ["left", "left", "right", "right"]
    joints = [(fc[i][1] + fc[i + 1][0]) / 2 for i in range(n - 1)]
    bounds = [c.x0 + T] + joints + [c.x1 - T]
    parts_x = [joints[s[1] - 1] for s in secs[:-1]]
    ydr = dy[1] + G / 2 + T / 2 + 5                                  # the fixed shelf over the drawers (top face)
    c.shelf("shelf-drawers", c.x0 + T, c.x1 - T, ydr, fixed=True)
    for k, xp in enumerate(parts_x):
        c.partition(f"partition-{k + 1}", xp, ydr, c.inner_top)
    for i in range(n - 1):
        c.p.append(part(f"divider-{i + 1}", [joints[i] - T / 2, c.leg + T, 10, joints[i] + T / 2, ydr - T, c.dz]))
    for k, (s0, s1, kind) in enumerate(secs):
        a = bounds[s0] + (T / 2 if s0 > 0 else 0)
        b = bounds[s1] - (T / 2 if s1 < n else 0)
        if kind == "shelves":
            for j, y in enumerate([760, 1120, 1480, 1840]):
                c.shelf(f"shelf-{k + 1}-{j + 1}", a, b, y)
        else:
            c.shelf(f"hat-{k + 1}", a, b, 1860)
            c.rail(f"rail-{k + 1}", a, b, 1790)
    fix_backs(c, parts_x)
    for i, ((a, b), hg) in enumerate(zip(fc, hinges)):
        c.door(f"door_{i + 1}", a, gy[0], b, gy[1], hg, hy=1130)
        c0 = bounds[i] + (T / 2 if i > 0 else 0)
        c1 = bounds[i + 1] - (T / 2 if i < n - 1 else 0)
        c.drawer(f"drawer_{i + 1}", a, dy[0], b, dy[1], c0, c1, framed=False, depth=500)
    c.legs([c.x0 + 45] + joints + [c.x1 - 45])
    return c.dump(did)


def komod_1_29():
    c = Case(805, 468, 1052, False, 100)
    (a, b), = cols(c.x0, c.x1, n=1)
    fix_backs(c)
    for k, (y0, y1) in enumerate(rows(c.fy0, c.fy1, n=4)):
        c.drawer(f"drawer_{4 - k}", a, y0, b, y1, c.x0 + T, c.x1 - T)
    c.legs([c.x0 + 40, c.x1 - 40])
    return c.dump("sati-1-29")


def komod_1_26():
    c = Case(1048, 458, 1015, False, 100)
    (a, b), = cols(c.x0, c.x1, n=1)
    rs = rows(c.fy0, c.fy1, [242, 242, 242, 150])
    xm = c.W / 2
    ytop_rail = rs[3][0] - G / 2 + T / 2 - 1                    # the fixed shelf under the small drawers
    c.shelf("rail", c.x0 + T, c.x1 - T, ytop_rail, fixed=True)
    c.partition("divider", xm, ytop_rail, c.inner_top)
    fix_backs(c)
    for k in range(3):
        y0, y1 = rs[k]
        c.drawer(f"drawer_{3 - k + 2}", a, y0, b, y1, c.x0 + T, c.x1 - T)
    (l0, l1), (r0, r1) = cols(c.x0, c.x1, n=2)
    c.drawer("drawer_1", l0, rs[3][0], l1, rs[3][1], c.x0 + T, xm - T / 2, framed=False)
    c.drawer("drawer_2", r0, rs[3][0], r1, rs[3][1], xm + T / 2, c.x1 - T, framed=False)
    c.legs([c.x0 + 40, c.x1 - 40])
    return c.dump("sati-1-26")


def tumba_1_25():
    c = Case(526, 434, 510, False, 100)
    (a, b), = cols(c.x0, c.x1, n=1)
    fix_backs(c)
    for k, (y0, y1) in enumerate(rows(c.fy0, c.fy1, n=2)):
        c.drawer(f"drawer_{2 - k}", a, y0, b, y1, c.x0 + T, c.x1 - T)
    c.legs([c.x0 + 35, c.x1 - 35])
    return c.dump("sati-1-25")


def tumba_1_23():
    """Тумба 1572 × 1108: three equal columns — door | five plain drawers | door."""
    c = Case(1572, 452, 1108, False, 100)
    (l0, l1), (m0, m1), (r0, r1) = cols(c.x0, c.x1, n=3)
    p1, p2 = (l1 + m0) / 2, (m1 + r0) / 2
    c.partition("partition-1", p1)
    c.partition("partition-2", p2)
    for side, (a, b) in (("l", (c.x0 + T, p1 - T / 2)), ("r", (p2 + T / 2, c.x1 - T))):
        c.shelf(f"shelf-{side}1", a, b, 420)
        c.shelf(f"shelf-{side}2", a, b, 750)
    fix_backs(c, [p1, p2])
    c.door("door_l", l0, c.fy0, l1, c.fy1, "left", hy=620)
    c.door("door_r", r0, c.fy0, r1, c.fy1, "right", hy=620)
    for k, (y0, y1) in enumerate(rows(c.fy0, c.fy1, n=5)):
        c.drawer(f"drawer_{5 - k}", m0, y0, m1, y1, p1 + T / 2, p2 - T / 2, framed=False)
    c.legs([c.x0 + 40, p1, p2, c.x1 - 40])
    return c.dump("sati-1-23")


def tumba_1_28():
    """Тумба 1572 × 1053: a door on the left third, four framed drawers (two pulls each) on the right."""
    c = Case(1572, 452, 1053, False, 100)
    (l0, l1), (m0, m1) = cols(c.x0, c.x1, [1, 2])
    p1 = (l1 + m0) / 2
    c.partition("partition", p1)
    for j, y in enumerate([380, 680]):
        c.shelf(f"shelf-{j + 1}", c.x0 + T, p1 - T / 2, y)
    fix_backs(c, [p1])
    c.door("door", l0, c.fy0, l1, c.fy1, "left", hy=620)
    for k, (y0, y1) in enumerate(rows(c.fy0, c.fy1, n=4)):
        c.drawer(f"drawer_{4 - k}", m0, y0, m1, y1, p1 + T / 2, c.x1 - T, pulls=2)
    c.legs([c.x0 + 40, p1, c.x1 - 40])
    return c.dump("sati-1-28")


def stol_2_51():
    """Стол письменный 2Т: a 22 top over two pedestals (a plain drawer over a framed door each), a modesty panel."""
    W, B, H, leg = 1500, 650, 746, 100
    p, m = [], []
    dz = B - OVL - FT
    fz = dz + FT
    yt = H - TOPT
    p.append(part("top", [0, yt, 0, W, H, B], edge=3))
    peds = [(OVL, OVL + 440, "left"), (W - OVL - 440, W - OVL, "right")]
    c = Case.__new__(Case)
    c.p, c.m, c.dz, c.fz, c.leg, c.tall = p, m, dz, fz, leg, False
    k = 0
    for i, (x0, x1, hg) in enumerate(peds):
        s = "lr"[i]
        p += [part(f"side-{s}1", [x0, leg, 0, x0 + T, yt, dz]), part(f"side-{s}2", [x1 - T, leg, 0, x1, yt, dz]),
              part(f"bottom-{s}", [x0 + T, leg, 0, x1 - T, leg + T, dz]),
              part(f"rail-{s}", [x0 + T, 552, 10, x1 - T, 568, dz]),
              part(f"shelf-{s}", [x0 + T + 1, 300, 20, x1 - T - 1, 316, dz - 20]),
              back(f"back-{s}", [x0 + 8, leg + 8, 6, x1 - 8, yt - 0.5, 9.5])]
        (a, b), = cols(x0, x1, n=1)
        c.door(f"door_{s}", a, leg + 1, b, 568, hg, hy=450)
        c.drawer(f"drawer_{s}", a, 571, b, yt - G, x0 + T, x1 - T, framed=False, depth=450)
        for x, sx in ((x0 + 40, -8), (x1 - 40, 8)):
            for z, sz in ((45, -6), (dz - 40, 6)):
                k += 1
                p.append(leg_square(f"leg-{k}", x, z, leg, sx=sx, sz=sz))
    p.append(part("modesty", [OVL + 440, 330, 40, W - OVL - 440, yt, 40 + T]))
    return dump("sati-2-51", [W, B, H], p, m)


# ------------------------------------------------------------------------------------------------------------- hall
def tumba_3_29():
    """Тумба для обуви: one framed front hinged at the bottom (a tilt-out shoe rack), the pull by its top edge."""
    c = Case(670, 462, 478, False, 100)
    (a, b), = cols(c.x0, c.x1, n=1)
    c.shelf("shelf", c.x0 + T, c.x1 - T, 290)
    fix_backs(c)
    fr = sfront("f-flap", a, c.fy0, b, c.fy1, c.dz)
    h = hhandle("h-flap", (a + b) / 2, c.fy1 - 32, c.fz)
    c.p += fr + h
    c.m.append({"type": "flap", "name": "flap", "parts": ids(fr + h), "hinge": "bottom", "angle": 40})
    c.legs([c.x0 + 40, c.x1 - 40])
    return c.dump("sati-3-29")


def veshalka_3_92():
    """Вешалка 746 × 139 × 1460 (wall): a 22 board under a hood — the tall pieces' crown and cap, 139 deep — and three
    double coat hooks (antique brass)."""
    W, B, H = 746, 139, 1460
    p = []
    yt = H - CR - CAP
    x0, x1 = OV, W - OV
    zf = B - OV                                      # the hood's front (under the crown)
    p.append(part("board", [x0, 0, 0, x1, yt, 22], edge=2))
    p += [part("hood-front", [x0, yt - 60, zf - T, x1, yt, zf]),
          part("hood-l", [x0, yt - 60, 22, x0 + T, yt, zf - T]), part("hood-r", [x1 - T, yt - 60, 22, x1, yt, zf - T]),
          part("hood-bottom", [x0 + T, yt - 60, 22, x1 - T, yt - 60 + T, zf - T])]
    p.append(cornice("cornice", 0, W, 0, B, yt, "sati-crown"))
    p.append(part("cap", [0, H - CAP, 0, W, H, B], edge=4))
    for k, (x, y) in enumerate([(165, 1180), (W - 165, 1180), (W / 2, 1000)]):
        hid = f"hook-{k + 1}"
        p += [{"id": f"{hid}-plate", "kind": "rod", "mat": "metal", "from": [fmt(x), fmt(y + 20), 22], "to": [fmt(x), fmt(y - 25), 22],
               "d": 14},
              {"id": f"{hid}-stem", "kind": "rod", "mat": "metal", "from": [fmt(x), fmt(y), 22], "to": [fmt(x), fmt(y - 45), 55], "d": 8},
              {"id": f"{hid}-l", "kind": "rod", "mat": "metal", "from": [fmt(x), fmt(y - 45), 55], "to": [fmt(x - 18), fmt(y - 15), 68], "d": 7},
              {"id": f"{hid}-r", "kind": "rod", "mat": "metal", "from": [fmt(x), fmt(y - 45), 55], "to": [fmt(x + 18), fmt(y - 15), 68], "d": 7}]
    return dump("sati-3-92", [W, B, H], p, [])


# ---------------------------------------------------------------------------------------------------------- mirrors
def mirror(did, W, H):
    """Зеркало on the wall: a 6-mm backing, the mirror 4, a moulded frame 72 wide and 16 high (profile sati-mframe)
    lying over the mirror's edge; two patina lines on its steps. B 22 = 6 + 16."""
    p = [part("backing", [0, 0, 0, W, H, 6], edge=1),
         part("mirror", [55, 55, 6, W - 55, H - 55, 10], kind="mirror", edge=0.5),
         ring("frame", 0, 0, W, H, 6, "sati-mframe")]
    p += line_rect("pa", 50.8, 50.8, W - 50.8, H - 50.8, 21.6)
    p += line_rect("pb", 66, 66, W - 66, H - 66, 17.8)
    return dump(did, [W, 22, H], p, [])


# -------------------------------------------------------------------------------------------------------------- beds
def bed(did, W, sleep_w):
    """Кровать 2-14 / 2-16 (x = width, z = length 2040): a 22 headboard to H 1000 with an upholstered panel in a
    moulded frame (the catalogue: a beige velour panel), a storage box of 22 panels on six tapered legs, a metal
    lifting base with slats (металлокаркас с подъёмным механизмом), the mattress ≤ 200."""
    L, H, leg = 2040, 1000, 110
    p = []
    p.append(part("headboard", [0, leg, 0, W, H, 22], edge=3))
    p.append({"id": "headboard-soft", "kind": "soft", "box": box(125, 610, 22, W - 125, 915, 52), "edge": 10})
    p.append(ring("headboard-frame", 95, 580, W - 95, 945, 22, "sati-hbframe"))
    p += line_rect("headboard-pa", 96, 581, W - 96, 944, 29.6)
    box_top = 420
    p += [part("rail-l", [0, leg, 22, 22, box_top, L - 22]), part("rail-r", [W - 22, leg, 22, W, box_top, L - 22]),
          part("foot", [0, leg, L - 22, W, box_top, L], edge=3)]
    p.append(back("box-bottom", [22, leg + 30, 22, W - 22, leg + 33.5, L - 22]))
    p += [part("cleat-l", [22, box_top - 110, 60, 52, box_top - 80, L - 60]),
          part("cleat-r", [W - 52, box_top - 110, 60, W - 22, box_top - 80, L - 60])]
    x0 = (W - sleep_w) / 2
    base = metal_base(x0, W - x0, 40, L - 40, box_top - 40, mattress=200)
    base = [q for q in base if not q["id"].startswith("m-leg")]
    p += base
    k = 0
    for x, sx in ((60, -8), (W - 60, 8)):
        for z, sz in ((60, 0), (L / 2, 0), (L - 60, 6)):
            k += 1
            p.append(leg_square(f"leg-{k}", x, z, leg, d=55, d2=38, sx=sx, sz=sz))
    return dump(did, [W, L, H], p, [])


def catalog():
    models = [
        ("sati-0-10", "П7.057.0.10", "Шкаф «Сати»", "living", [608, 475, 2170], 21, "универсальный"),
        ("sati-0-21", "П7.057.0.21", "Тумба «Сати»", "living", [1990, 445, 712], 21, None),
        ("sati-0-11", "П7.057.0.11", "Шкаф для книг «Сати»", "living", [1130, 475, 2170], 21, None),
        ("sati-1-04", "П7.057.1.04", "Кровать 2-14 «Сати»", "bedroom", [1610, 2040, 1000], 22, "сп. место 2000×1400, металлокаркас с подъёмным механизмом"),
        ("sati-1-16", "П7.057.1.16", "Шкаф для одежды 3Д «Сати»", "bedroom", [1652, 630, 2200], 22, None),
        ("sati-1-42", "П7.057.1.42", "Зеркало «Сати»", "decor", [964, 22, 664], 22, None),
        ("sati-1-25", "П7.057.1.25", "Тумба прикроватная «Сати»", "bedroom", [526, 434, 510], 22, None),
        ("sati-1-29", "П7.057.1.29", "Комод «Сати»", "bedroom", [805, 468, 1052], 22, None),
        ("sati-3-92", "П7.057.3.92", "Вешалка «Сати»", "hall", [746, 139, 1460], 23, None),
        ("sati-3-29", "П7.057.3.29", "Тумба для обуви «Сати»", "hall", [670, 462, 478], 23, None),
        ("sati-1-18", "П7.057.1.18", "Шкаф для одежды 2Д «Сати»", "bedroom", [1132, 630, 2200], 23, None),
        ("sati-1-26", "П7.057.1.26", "Комод «Сати»", "bedroom", [1048, 458, 1015], 23, None),
        ("sati-1-01", "П7.057.1.01", "Кровать 2-16 «Сати»", "bedroom", [1850, 2040, 1000], 23, "сп. место 2000×1600, металлокаркас с подъёмным механизмом"),
        ("sati-1-17", "П7.057.1.17", "Шкаф для одежды 4Д «Сати»", "bedroom", [2174, 630, 2200], 23, None),
        ("sati-1-40", "П7.057.1.40", "Зеркало «Сати»", "decor", [1374, 22, 653], 23, "вешается горизонтально или вертикально"),
        ("sati-1-23", "П7.057.1.23", "Тумба «Сати»", "bedroom", [1572, 452, 1108], 23, None),
        ("sati-1-28", "П7.057.1.28", "Тумба «Сати»", "bedroom", [1572, 452, 1053], 24, None),
        ("sati-2-51", "П7.057.2.51", "Стол письменный 2Т «Сати»", "office", [1500, 650, 746], 24, None),
    ]
    out = []
    for mid, code, name, cat, size, page, note in models:
        e = {"id": mid, "code": code, "name": name, "collection": "sati", "category": cat, "size": size, "page": page}
        if mid in ("sati-1-42", "sati-1-40", "sati-3-92"):
            e["mount"] = "wall"
        e["note"] = "по каталогу и фото сайта, без инструкции" + (f"; {note}" if note else "")
        out.append(e)
    frag = {
        "finishes": [
            {"id": "sati-zhemchug", "name": "Персидский жемчуг (патина бронза)", "body": "door_enamel_whitey#c6c0ba",
             "roles": {"patina": "door_enamel_whitey#5e4637", "fabric": "velvet#ab9a93"}, "swatch": "#c6c0ba"},
            {"id": "sati-white", "name": "Белый", "body": "door_enamel_whitey#e6e7e8",
             "roles": {"patina": "door_enamel_whitey#c9cacc", "fabric": "velvet#d6ccbf"}, "swatch": "#e6e7e8"}],
        "profiles": {
            "sati-crown": {"name": "Карниз «Сати»: выкружка с полочкой, вынос 40, высота 44",
                           "pts": [[40, 0], [39, 3], [37.2, 7], [34.5, 11.5], [31, 16.5], [26.5, 21.5], [21.5, 25.8],
                                   [16, 29.5], [11, 32.2], [7, 34], [4.5, 35.5], [4, 38], [2, 38.5], [0, 40], [0, 44],
                                   [62, 44], [62, 0]]},
            "sati-bead": {"name": "Фасад «Сати»: ступенчатый калёвочный штапик 18 × 4 (от рамки к филёнке)",
                          "pts": [[0, 0], [0, 4], [1.5, 4], [1.5, 3], [3, 2.9], [6, 2.6], [9, 2.1], [12, 1.6], [14, 1.4],
                                  [14.5, 0.8], [18, 0.6], [18, 0]]},
            "sati-gbead": {"name": "Штапик остекления «Сати» 12 × 7",
                           "pts": [[0, 0], [0, 7], [3, 7], [5, 6.2], [8, 4.5], [10.5, 2.5], [12, 0]]},
            "sati-mframe": {"name": "Рама зеркала «Сати» 72 × 16: плоская рамка 50, ступень, штапик к зеркалу",
                            "pts": [[0, 0], [0, 14], [1.5, 15.6], [3, 16], [50, 16], [50, 13.5], [52, 13.4], [56, 12.6],
                                    [60, 11.6], [64, 10.8], [66, 10.6], [66.5, 9.5], [72, 9], [72, 0]]},
            "sati-hbframe": {"name": "Рамка изголовья «Сати» 30 × 10",
                             "pts": [[0, 0], [0, 8], [1.5, 9.6], [3, 10], [8, 10], [8, 8.5], [14, 7.8], [22, 6],
                                     [26, 4], [30, 0]]}},
        "collections": [{"id": "sati", "name": "Сати", "brand": "Пинскдрев", "finishes": ["sati-zhemchug", "sati-white"],
                         "metal": "gold#8a5d3f",
                         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 21–24; инструкций нет — все модули по каталогу и фото сайта. Корпус ЛДСП 16 на квадратных конических опорах, высокие модули с карнизом, фасады МДФ 19 с фрезерованной рамкой и штапиком с бронзовой патиной, литые бронзовые ручки-скобы."}],
        "models": out}
    with open(os.path.join(HERE, "sati_catalog.json"), "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    for f in (shkaf_0_10, shkaf_0_11, tumba_0_21, komod_1_29, komod_1_26, tumba_1_25, tumba_1_23, tumba_1_28, stol_2_51,
              tumba_3_29, veshalka_3_92):
        print(f())
    print(wardrobe("sati-1-18", 1132, 2), wardrobe("sati-1-16", 1652, 3), wardrobe("sati-1-17", 2174, 4))
    print(mirror("sati-1-42", 964, 664), mirror("sati-1-40", 1374, 653))
    print(bed("sati-1-01", 1850, 1600), bed("sati-1-04", 1610, 1400))
    catalog()
