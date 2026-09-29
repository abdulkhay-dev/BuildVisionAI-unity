"""«Мартина» (П3.573): all 16 catalogue articles by the catalogue (pp. 45–48) — no instruction, no front-on product
photo (the site has two photos of the bedside table only).

index.json holds only 10 Martina rows and their codes / names are garbled (the PDF text of p. 48 runs two columns
together): the codes here are the ones printed on p. 48 (the module spread) — the living-room articles are
П3.573.01, .01-1, .02, .09, .22, .23, .31, .32, .50, .54 (model ids martina-01 … martina-54), the bedroom ones
П3.573.1.01 … 1.06 (martina-1-01 …). The chair «Чикаго М» (p. 46) is another collection's seating — skipped.

Construction (one system, read off the cut-outs of p. 48 and the interiors pp. 45–47, the catalogue sizes as scale):
  * carcass ЛДСП 16 «Молоко» on a plinth 95 high with bracket feet (an ogee cut-out between the feet — `shape: path`)
    and a silver bead along its top; pilasters 80 wide (МДФ 22) at the front corners with carved fleurs-de-lis at their
    top and foot; the fronts inset between them, flush;
  * low pieces: a top 28 thick, 22 mm out, over a frieze rail 40 with a silver rope bead; tall pieces: a crown 60 high,
    30 mm out, over a frieze 70, and a cap;
  * fronts МДФ: the doors are a milled frame (border 70) round a carved panel — the leaves relief of the catalogue as
    milled lines on a panel in the role "carve" (the silver-patinated ground) — with a bead; the drawers and the
    plain upper doors a milled frame with a bead; glazed doors a 70 frame round clear glass; silver patina lines on
    the beads (thin rods, role "patina");
  * silver knobs Ø28 (vertical silver pulls on the wardrobe), drawer boxes ЛДСП 16 with ХДФ bottoms.

    python3 tools/casegoods/gen/martina.py      # Designs/martina-*.json, gen/martina_catalog.json
"""
import json
import math
import os

from kit_w3a import (back, bar, box, cornice, drawer_box, dump, fmt, frame_front, front_band, ids, knob, line,
                     line_rect, metal_base, part, ring)

HERE = os.path.dirname(os.path.abspath(__file__))
T, FT = 16, 22
G = 2.5
PLH = 95                         # plinth
PIL = 80                         # pilaster width
TOPT, TOPO = 28, 22              # low top
CRH, CRO, CAP = 60, 30, 12       # tall crown


# --------------------------------------------------------------------------------------------------------- ornament
def leaves(a0, b0, a1, b1, pitch=(62, 88), L=74, Wd=22, margin=8):
    """Milled lines of the leaves relief: leaves in staggered rows, leaning ±35°, each two arcs and a midrib."""
    out = []
    px, py = pitch
    rows_n = int((b1 - b0 - 2 * margin) // py) + 1
    cols_n = int((a1 - a0 - 2 * margin) // px) + 1
    ox = a0 + (a1 - a0 - (cols_n - 1) * px) / 2
    oy = b0 + (b1 - b0 - (rows_n - 1) * py) / 2
    for j in range(rows_n):
        for i in range(cols_n):
            cx = ox + i * px + (px / 2 if j % 2 else 0)
            cy = oy + j * py
            ang = math.radians(55 if (i + j) % 2 else 125)
            ux, uy = math.cos(ang), math.sin(ang)
            vx, vy = -uy, ux
            def P(t, side):
                s = t * L / 2
                w = side * Wd / 2 * (1 - t * t)
                return (cx + ux * s + vx * w, cy + uy * s + vy * w)
            pts = []
            for side in (1, -1):
                seq = [P(t, side) for t in (-1, -0.5, 0, 0.5, 1)]
                pts += list(zip(seq, seq[1:]))
            pts.append((P(-0.8, 0), P(0.8, 0)))
            for (x0, y0), (x1, y1) in pts:
                if all(a0 + margin <= x <= a1 - margin for x in (x0, x1)) and all(b0 + margin <= y <= b1 - margin for y in (y0, y1)):
                    out.append([fmt(x0), fmt(y0), fmt(x1), fmt(y1)])
    return out


def fleur(pid, cx, cy, z, w=46, h=64):
    """A carved fleur-de-lis block on a pilaster: a thin plate in the role "carve" with the lily milled into it."""
    a0, b0, a1, b1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    ln = [[cx, b0 + 8, cx, b1 - 6],
          [cx, b0 + 26, cx - 14, b1 - 14], [cx - 14, b1 - 14, cx - 18, b0 + 34],
          [cx, b0 + 26, cx + 14, b1 - 14], [cx + 14, b1 - 14, cx + 18, b0 + 34],
          [cx - 16, b0 + 20, cx + 16, b0 + 20], [cx - 8, b0 + 8, cx + 8, b0 + 8]]
    return part(pid, [a0, b0, z, a1, b1, z + 4], kind="front", mat="carve", edge=1,
                face={"type": "grooves", "w": 2.5, "depth": 1.2, "flute": "v", "lines": [[fmt(v) for v in l] for l in ln]})


def feet_bottom(x0, x1, y0, foot=110, rise=38):
    """Bracket feet: flat feet at the ends, an ogee up to the apron between them (commands from (x0, y0) to (x1, y0))."""
    a, b = x0 + foot, x1 - foot
    ym = y0 + rise
    return (f"L {fmt(a)} {fmt(y0)} C {fmt(a + 4)} {fmt(y0 + rise * 0.55)} {fmt(a + 22)} {fmt(y0 + rise * 0.3)} {fmt(a + 26)} {fmt(ym)} "
            f"L {fmt(b - 26)} {fmt(ym)} C {fmt(b - 22)} {fmt(y0 + rise * 0.3)} {fmt(b - 4)} {fmt(y0 + rise * 0.55)} {fmt(b)} {fmt(y0)} "
            f"L {fmt(x1)} {fmt(y0)}")


# ------------------------------------------------------------------------------------------------------------ case
class Case:
    def __init__(self, W, B, H, tall, frieze=None):
        self.W, self.B, self.H, self.tall = W, B, H, tall
        ov = CRO if tall else TOPO
        self.x0, self.x1 = ov, W - ov
        self.fz = B - ov
        self.dz = self.fz - FT
        self.yt = H - CRH - CAP if tall else H - TOPT
        self.p, self.m = [], []
        x0, x1, dz, fz, yt = self.x0, self.x1, self.dz, self.fz, self.yt
        fr = frieze or (70 if tall else 40)
        self.p += [part("side-l", [x0, PLH, 0, x0 + T, yt, dz]), part("side-r", [x1 - T, PLH, 0, x1, yt, dz]),
                   part("bottom", [x0 + T, PLH, 0, x1 - T, PLH + T, dz])]
        # plinth: front board with bracket feet, side boards, back board
        self.p += [part("plinth-f", [x0, 0, dz, x1, PLH, fz], kind="panel", shape="path",
                        outline=f"M {fmt(x0)} 0 {feet_bottom(x0, x1, 0)} L {fmt(x1)} {PLH} L {fmt(x0)} {PLH} Z"),
                   part("plinth-l", [x0, 0, 20, x0 + T, PLH, dz]), part("plinth-r", [x1 - T, 0, 20, x1, PLH, dz]),
                   part("plinth-b", [x0 + T, 20, 20, x1 - T, PLH, 36])]
        self.p.append(front_band("plinth-bead", x0, x1, PLH - 12, fz, "martina-bead", mat="patina"))
        # pilasters and their lilies
        self.rt = yt - T - fr if tall else yt - fr                  # the openings' top
        for s, (a, b) in (("l", (x0, x0 + PIL)), ("r", (x1 - PIL, x1))):
            self.p.append(part(f"pilaster-{s}", [a, PLH, dz, b, yt - (T if tall else 0), fz], edge=2))
            cx = (a + b) / 2
            self.p.append(fleur(f"lily-{s}-top", cx, self.rt + fr / 2 if tall else yt - 60, fz))
            self.p.append(fleur(f"lily-{s}-foot", cx, PLH + 60, fz))
        self.ox0, self.ox1 = x0 + PIL, x1 - PIL                      # the opening between the pilasters
        self.p.append(part("frieze", [self.ox0, self.rt, dz, self.ox1, yt - (T if tall else 0), fz]))
        self.p.append(front_band("rope", self.ox0, self.ox1, self.rt + fr / 2 - 6, fz, "martina-rope", mat="patina"))
        self.p.append(part("rail-bottom", [self.ox0, PLH, dz, self.ox1, PLH + 20, fz]))
        self.oy0 = PLH + 20
        if tall:
            self.p.append(part("top", [x0 + T, yt - T, 0, x1 - T, yt, dz]))
            self.p.append(cornice("crown", 0, W, 0, B, yt, "martina-crown"))
            self.p.append(part("cap", [0, H - CAP, 0, W, H, B], edge=3))
        else:
            self.p.append(part("top", [0, yt, 0, W, H, B], edge=5))
            self.p.append(line("top-silver", [0, yt + 3, B + 0.3], [W, yt + 3, B + 0.3], d=2.5))
        self.inner_top = yt - T if tall else yt

    def partition(self, pid, xc, y0=None, y1=None):
        self.p.append(part(pid, [xc - T / 2, y0 or PLH + T, 10, xc + T / 2, y1 or self.inner_top, self.dz]))

    def mullion(self, pid, xc, y0, y1, w=40):
        self.p.append(part(pid, [xc - w / 2, y0, self.dz, xc + w / 2, y1, self.fz]))

    def hrail(self, pid, a, b, y0, y1):
        self.p.append(part(pid, [a, y0, self.dz, b, y1, self.fz]))

    def shelf(self, pid, a, b, y, fixed=False, glass=False):
        if glass:
            self.p.append(part(pid, [a + 2, y - 6, 20, b - 2, y, self.dz - 20], kind="glass"))
        elif fixed:
            self.p.append(part(pid, [a, y - T, 10, b, y, self.dz]))
        else:
            self.p.append(part(pid, [a + 1, y - T, 20, b - 1, y, self.dz - 10]))

    def backs(self, xs=()):
        edges = [self.x0 + 8] + list(xs) + [self.x1 - 8]
        for k in range(len(edges) - 1):
            self.p.append(back(f"back-{k + 1}" if len(edges) > 2 else "back",
                               [edges[k], PLH + 8, 6, edges[k + 1], self.inner_top + 8 if self.tall else self.yt - 0.5, 9.5]))

    # fronts ---------------------------------------------------------------------------------------------------
    def carved(self, fid, a, y0, b, y1, border=70):
        holes = [(a + border, y0 + border, b - border, y1 - border)]
        f = frame_front(fid, None, a, y0, b, y1, self.dz, FT, holes, sink=4, pt=10, panel_mat="carve",
                        face={"type": "grooves", "w": 3, "depth": 2, "flute": "v", "lines": leaves},
                        bead="martina-pbead")
        h = holes[0]
        f += line_rect(f"{fid}-pa", h[0] + 0.8, h[1] + 0.8, h[2] - 0.8, h[3] - 0.8, self.fz - 0.8)
        return f

    def plain(self, fid, a, y0, b, y1, border=None):
        border = border or (60 if min(b - a, y1 - y0) > 300 else 36)
        f = part(fid, [a, y0, self.dz, b, y1, self.fz], kind="front",
                 face={"type": "frame", "border": border, "depth": 4, "r": 2, "profile": "martina-pbead"})
        return [f] + line_rect(f"{fid}-pa", a + border + 0.8, y0 + border + 0.8, b - border - 0.8, y1 - border - 0.8, self.fz - 0.6)

    def glazed(self, fid, a, y0, b, y1):
        f = part(fid, [a, y0, self.dz, b, y1, self.fz], kind="front", glass={"frame": 70, "rebate": 5, "t": 4, "tint": "clear"})
        return [f, ring(f"{fid}-gb", a + 75, y0 + 75, b - 75, y1 - 75, self.dz + FT / 2 + 2, "martina-gbead")] + \
            line_rect(f"{fid}-pa", a + 72, y0 + 72, b - 72, y1 - 72, self.fz - 0.6)

    def door(self, name, a, y0, b, y1, hinge, kind="carved", hy=None, pull=None):
        fr = {"carved": self.carved, "plain": self.plain, "glazed": self.glazed}[kind](f"f-{name}", a + G, y0 + G, b - G, y1 - G)
        hx = b - G - 32 if hinge == "left" else a + G + 32
        hy = hy if hy is not None else (y0 + y1) / 2
        if pull == "bar":
            h = [bar(f"h-{name}", hx, hy, self.fz, d=160, vertical=True, band=9, t=9, standoff=22, post=12)]
        else:
            h = [knob(f"h-{name}", hx, hy, self.fz, d=28, t=16, standoff=20)]
        self.p += fr + h
        self.m.append({"type": "door", "name": name, "parts": ids(fr + h), "hinge": hinge, "angle": 105})

    def drawer(self, name, a, y0, b, y1, c0, c1, carved=False, depth=None, knobs=1):
        fr = (self.carved if carved else self.plain)(f"f-{name}", a + G, y0 + G, b - G, y1 - G,
                                                   *( [60] if carved and y1 - y0 < 260 else []))
        d = depth or (400 if self.dz > 400 else 350)
        bh = max(70, min(200, y1 - y0 - 45))
        bx = drawer_box(name, c0 + 13, c1 - 13, y0 + 20, bh, self.dz - d, self.dz)
        hs = []
        for k in range(knobs):
            cx = (a + b) / 2 if knobs == 1 else a + (b - a) * (k + 1) / (knobs + 1)
            hs.append(knob(f"h-{name}-{k + 1}", cx, (y0 + y1) / 2, self.fz, d=28, t=16, standoff=20))
        self.p += fr + bx + hs
        self.m.append({"type": "drawer", "name": name, "parts": ids(fr + bx + hs), "travel": d - 60})

    def dump(self, did):
        return dump(did, [self.W, self.B, self.H], self.p, self.m)


def split(a, b, n, gap=0):
    w = (b - a - gap * (n - 1)) / n
    return [(a + k * (w + gap), a + k * (w + gap) + w) for k in range(n)]


# ------------------------------------------------------------------------------------------------------- living room
def vitrina(did, W, B, n, hinge1):
    """Шкаф с витриной 1 / 1.1 / 2 3Д: glazed door(s) (to 2198 − 72 − frieze) over carved doors 690 high, a fixed
    shelf at the joint, two glass shelves, one shelf below."""
    c = Case(W, B, 2198, True)
    yj = c.oy0 + 690
    c.shelf("shelf-joint", c.x0 + T, c.x1 - T, yj + T / 2, fixed=True)
    c.hrail("rail-joint", c.ox0, c.ox1, yj - 4, yj + 4)
    c.shelf("shelf-low", c.x0 + T, c.x1 - T, c.oy0 + 350)
    for k, y in enumerate([1250, 1640]):
        c.shelf(f"glass-{k + 1}", c.x0 + T, c.x1 - T, y, glass=True)
    c.backs()
    cols = split(c.ox0, c.ox1, n)
    for k, (a, b) in enumerate(cols):
        hg = hinge1 if n == 1 else ("left" if k == 0 else "right")
        c.door(f"door_up_{k + 1}", a, yj + 4, b, c.rt, hg, kind="glazed", hy=yj + 330)
        c.door(f"door_low_{k + 1}", a, c.oy0, b, yj - 4, hg, kind="carved", hy=yj - 170)
    return c.dump(did)


def tumba_chest(did, W, n):
    """Тумба «Мартина 2 / 3 3Д» (945): a row of drawers 150 high over carved doors, mullions 40 between columns."""
    c = Case(W, 412, 945, False)
    cols = split(c.ox0, c.ox1, n, 40)
    yd = c.rt - 150
    c.hrail("rail-drawers", c.ox0, c.ox1, yd - 25, yd)
    parts_x = []
    for k in range(n - 1):
        xm = (cols[k][1] + cols[k + 1][0]) / 2
        c.mullion(f"mullion-{k + 1}", xm, c.oy0, yd - 25)
        c.mullion(f"mullion-d{k + 1}", xm, yd, c.rt)
        c.partition(f"partition-{k + 1}", xm)
        parts_x.append(xm)
    bounds = [c.x0 + T] + parts_x + [c.x1 - T]
    for k, (a, b) in enumerate(cols):
        ca = bounds[k] + (T / 2 if k else 0)
        cb = bounds[k + 1] - (T / 2 if k < n - 1 else 0)
        c.shelf(f"shelf-drawer-{k + 1}", ca, cb, yd - 25 + T, fixed=True)
        c.shelf(f"shelf-{k + 1}", ca, cb, c.oy0 + 300)
        c.drawer(f"drawer_{k + 1}", a, yd, b, c.rt, ca, cb)
        hg = "left" if k < n / 2 else "right"
        if n == 3 and k == 1:
            hg = "right"
        c.door(f"door_{k + 1}", a, c.oy0, b, yd - 25, hg, hy=yd - 100)
    c.backs(parts_x)
    return c.dump(did)


def tumba_tv():
    """Тумба ТВ1 3Д 1430 × 412 × 513: carved door | open niche over a drawer | carved door."""
    c = Case(1430, 412, 513, False)
    wmid = 330
    xm0 = (c.ox0 + c.ox1) / 2 - wmid / 2
    xm1 = xm0 + wmid
    c.mullion("mullion-1", xm0 - 20, c.oy0, c.rt)
    c.mullion("mullion-2", xm1 + 20, c.oy0, c.rt)
    c.partition("partition-1", xm0 - 20)
    c.partition("partition-2", xm1 + 20)
    yd = c.oy0 + 150
    c.shelf("shelf-niche", xm0 - 12, xm1 + 12, yd + T, fixed=True)
    c.shelf("shelf-l", c.x0 + T, xm0 - 28, 250)
    c.shelf("shelf-r", xm1 + 28, c.x1 - T, 250)
    c.backs([xm0 - 20, xm1 + 20])
    c.door("door_l", c.ox0, c.oy0, xm0 - 40, c.rt, "left")
    c.door("door_r", xm1 + 40, c.oy0, c.ox1, c.rt, "right")
    c.drawer("drawer", xm0, c.oy0, xm1, yd, xm0 - 12, xm1 + 12, depth=350)
    return c.dump("martina-09")


def polka():
    """Полка «Мартина 10» 1300 × 300 × 250 (wall): a back board, a 28 shelf at its foot with a silver line, and a
    cornice-like apron under the shelf's front."""
    W, B, H = 1300, 300, 250
    p = [part("back", [0, 30, 0, W, H, 16], edge=2),
         part("shelf", [0, 30, 16, W, 58, B], edge=4),
         part("apron", [40, 0, B - 40, W - 40, 30, B - 22]),
         part("apron-l", [40, 0, 16, 58, 30, B - 40]), part("apron-r", [W - 58, 0, 16, W - 40, 30, B - 40]),
         line("silver", [0, 33, B + 0.3], [W, 33, B + 0.3], d=2.5)]
    return dump("martina-50", [W, B, H], p, [])


def table(did, W, B, H, leg=80, apron=90):
    """Столы «Мартина»: a top 30 over an apron with a silver rope bead, square legs 80 with fleurs-de-lis at the top
    (the dining table 1Р is extendable to 1800: built closed)."""
    p = [part("top", [0, H - 30, 0, W, H, B], edge=5),
         line("top-silver", [0, H - 27, B + 0.3], [W, H - 27, B + 0.3], d=2.5)]
    o = 30
    ya = H - 30
    for k, (x, z) in enumerate([(o, o), (W - o - leg, o), (o, B - o - leg), (W - o - leg, B - o - leg)]):
        p.append(part(f"leg-{k + 1}", [x, 0, z, x + leg, ya, z + leg], edge=2))
        if z > B / 2:
            p.append(fleur(f"lily-{k + 1}", x + leg / 2, ya - 45, z + leg))
    a0, a1 = o + leg, W - o - leg
    p += [part("apron-f", [a0, ya - apron, B - o - 20, a1, ya, B - o]),
          part("apron-b", [a0, ya - apron, o, a1, ya, o + 20]),
          part("apron-l", [o + 10, ya - apron, o + leg, o + 30, ya, B - o - leg]),
          part("apron-r", [W - o - 30, ya - apron, o + leg, W - o - 10, ya, B - o - leg])]
    p.append(front_band("rope", a0, a1, ya - 30, B - o, "martina-rope", mat="patina"))
    return dump(did, [W, B, H], p, [])


# ---------------------------------------------------------------------------------------------------------- bedroom
def wardrobe():
    """Шкаф для одежды 3Д 1678 × 618 × 2318: three doors — the outer ones a plain framed upper panel over a carved
    lower one (one leaf, a middle rail), the middle one a mirror over a carved panel; inside (the sketch): the left two
    doors hang (hat shelf, rail), the right one has shelves; vertical silver pulls."""
    c = Case(1678, 618, 2318, True)
    cols = split(c.ox0, c.ox1, 3)
    xp = (cols[1][1] + cols[2][0]) / 2
    c.partition("partition", xp)
    c.shelf("hat", c.x0 + T, xp - T / 2, 1960)
    c.p.append({"id": "rail", "kind": "tube", "mat": "chrome", "box": box(c.x0 + T + 2, 1880, c.dz / 2 - 12.5, xp - T / 2 - 2, 1905, c.dz / 2 + 12.5)})
    for j, y in enumerate([450, 800, 1150, 1500, 1850]):
        c.shelf(f"shelf-{j + 1}", xp + T / 2, c.x1 - T, y)
    c.backs([xp])
    ymid = c.oy0 + 780                                            # the carved lower panels' top
    for k, ((a, b), hg) in enumerate(zip(cols, ["left", "right", "right"])):
        name = f"door_{k + 1}"
        a, b, y0, y1 = a + G, b - G, c.oy0 + G, c.rt - G
        fz = c.fz
        if k == 1:
            holes_lo = [(a + 70, y0 + 70, b - 70, ymid - 30)]
            fr = frame_front(f"f-{name}", None, a, y0, b, y1, c.dz, FT, holes_lo, sink=4, pt=10, panel_mat="carve",
                             face={"type": "grooves", "w": 3, "depth": 2, "flute": "v", "lines": leaves}, bead="martina-pbead")
            fr.append(part(f"f-{name}-mirror", [a + 70, ymid + 30, fz, b - 70, y1 - 70, fz + 4], kind="mirror", edge=0.5))
            fr.append(ring(f"f-{name}-mframe", a + 60, ymid + 20, b - 60, y1 - 60, fz, "martina-mbead"))
        else:
            holes = [(a + 70, y0 + 70, b - 70, ymid - 30), (a + 70, ymid + 30, b - 70, y1 - 70)]
            fr = frame_front(f"f-{name}", None, a, y0, b, y1, c.dz, FT, holes, sink=4, pt=10, bead="martina-pbead")
            fr[1]["mat"] = "carve"
            fr[1]["face"] = {"type": "grooves", "w": 3, "depth": 2, "flute": "v",
                             "lines": leaves(*holes[0])}
            fr += line_rect(f"f-{name}-pu", holes[1][0] + 0.8, holes[1][1] + 0.8, holes[1][2] - 0.8, holes[1][3] - 0.8, fz - 0.8)
        fr += line_rect(f"f-{name}-pl", a + 70.8, y0 + 70.8, b - 70.8, ymid - 30.8, fz - 0.8)
        hx = b - 34 if hg == "left" else a + 34
        h = [bar(f"h-{name}", hx, 1150, fz, d=160, vertical=True, band=9, t=9, standoff=22, post=12)]
        c.p += fr + h
        c.m.append({"type": "door", "name": name, "parts": ids(fr + h), "hinge": hg, "angle": 105})
    return c.dump("martina-1-02")


def komod(did, W, H, n_carved, top_h=150):
    """Комоды 1.04 / 1.05: a plain top drawer over carved drawers."""
    c = Case(W, 465, H, False)
    rows_h = (c.rt - c.oy0 - top_h) / n_carved
    ys = [c.oy0 + k * rows_h for k in range(n_carved)] + [c.rt - top_h, c.rt]
    c.backs()
    for k in range(n_carved):
        c.drawer(f"drawer_{n_carved - k + 1}", c.ox0, ys[k], c.ox1, ys[k + 1], c.x0 + T, c.x1 - T, carved=True,
                 knobs=2 if W > 1000 else 1)
    c.drawer("drawer_1", c.ox0, ys[-2], c.ox1, ys[-1], c.x0 + T, c.x1 - T, knobs=2 if W > 1000 else 1)
    return c.dump(did)


def tumba_bed():
    """Тумба прикроватная 600 × 412 × 619: an open niche over a carved door (p. 47)."""
    c = Case(600, 412, 619, False)
    yn = c.rt - 170
    c.shelf("shelf-niche", c.x0 + T, c.x1 - T, yn + T, fixed=True)
    c.hrail("rail-niche", c.ox0, c.ox1, yn - 10, yn + T)
    c.backs()
    c.door("door", c.ox0, c.oy0, c.ox1, yn - 10, "left", hy=yn - 90)
    return c.dump("martina-1-03")


def mirror():
    """Зеркало 744 × 84 × 864 (wall): pilasters and a crown framing the mirror, a plinth rail below."""
    W, B, H = 744, 84, 864
    p = [part("backing", [40, 0, 0, W - 40, H - 60, 16], edge=1),
         part("pilaster-l", [40, 0, 16, 110, H - 60, 38], edge=2), part("pilaster-r", [W - 110, 0, 16, W - 40, H - 60, 38], edge=2),
         part("rail-top", [110, H - 150, 16, W - 110, H - 60, 38]), part("rail-bottom", [110, 0, 16, W - 110, 60, 38]),
         part("mirror", [110, 60, 16, W - 110, H - 150, 20], kind="mirror", edge=0.5),
         fleur("lily-l", 75, H - 105, 38), fleur("lily-r", W - 75, H - 105, 38),
         part("top", [40, H - 60, 0, W - 40, H - 48, 38])]
    p.append(cornice("crown", 0, W, 0, B, H - 48, "martina-crown-s"))
    p.append(part("cap", [0, H - 12, 0, W, H, B], edge=2))
    p.append(ring("mframe", 110, 60, W - 110, H - 150, 20, "martina-mbead"))
    return dump("martina-1-06", [W, B, H], p, [])


def bed():
    """Кровать 2-16 (x = width 1793, z = length 2075): a headboard 1160 high with an arched top and a carved leaves
    band under the arch; side rails and a foot rail 280 on massive block feet 150 (p. 47); a metal base, mattress
    1600 × 2000."""
    W, L, H = 1793, 2075, 1160
    arc = f"M 0 150 L {W} 150 L {W} 1020 C {W - 350} {H + 12} 350 {H + 12} 0 1020 Z"
    p = [part("headboard", [0, 150, 0, W, H, 30], shape="path", outline=arc, edge=3)]
    band = (f"M 120 820 C 520 {H - 70} {W - 520} {H - 70} {W - 120} 820 L {W - 120} 760 C {W - 560} {H - 170} 560 {H - 170} 120 760 Z")
    p.append(part("headboard-carve", [120, 760, 30, W - 120, H - 50, 36], kind="front", mat="carve", shape="path",
                  outline=band, face={"type": "grooves", "w": 3, "depth": 1.8, "flute": "v",
                                     "lines": leaves(300, 790, W - 300, H - 90, pitch=(70, 70))}))
    for k, x in enumerate([0, W - 150]):
        p.append(part(f"foot-h{k + 1}", [x, 0, 30, x + 150, 150, 230], edge=3))
        p.append(part(f"foot-f{k + 1}", [x, 0, L - 200, x + 150, 150, L], edge=3))
    top = 430
    p += [part("rail-l", [20, 150, 30, 50, top, L - 30]), part("rail-r", [W - 50, 150, 30, W - 20, top, L - 30]),
          part("rail-foot", [20, 150, L - 30, W - 20, top, L], edge=4)]
    p.append(line("foot-silver", [20, top - 20, L + 0.5], [W - 20, top - 20, L + 0.5], d=4))
    p += [part("cleat-l", [50, top - 100, 60, 80, top - 70, L - 60]), part("cleat-r", [W - 80, top - 100, 60, W - 50, top - 70, L - 60])]
    x0 = (W - 1600) / 2
    p += [q for q in metal_base(x0, W - x0, 40, L - 40, top - 70 + 30, mattress=200) if not q["id"].startswith("m-leg")]
    return dump("martina-1-01", [W, L, H], p, [])


def catalog():
    models = [
        ("martina-01-1", "П3.573.01-1", "Шкаф с витриной «Мартина 1.1 3Д»", "living", [690, 424, 2198], 48, "дверь на левых петлях"),
        ("martina-01", "П3.573.01", "Шкаф с витриной «Мартина 1 3Д»", "living", [690, 424, 2198], 48, "дверь на правых петлях"),
        ("martina-02", "П3.573.02", "Шкаф с витриной «Мартина 2 3Д»", "living", [1192, 429, 2198], 48, None),
        ("martina-22", "П3.573.22", "Тумба «Мартина 2 3Д»", "living", [1158, 412, 945], 48, None),
        ("martina-23", "П3.573.23", "Тумба «Мартина 3 3Д»", "living", [1650, 412, 945], 48, None),
        ("martina-09", "П3.573.09", "Тумба «Мартина ТВ1 3Д»", "living", [1430, 412, 513], 48, None),
        ("martina-50", "П3.573.50", "Полка «Мартина 10»", "living", [1300, 300, 250], 48, None),
        ("martina-54", "П3.573.54", "Стол обеденный «Мартина 1Р»", "tables", [1200, 900, 760], 48, "раздвижной 1200/1800, в сложенном виде"),
        ("martina-31", "П3.573.31", "Стол журнальный «Мартина 11»", "tables", [700, 700, 500], 48, None),
        ("martina-32", "П3.573.32", "Стол журнальный «Мартина 12»", "tables", [1200, 700, 500], 48, None),
        ("martina-1-02", "П3.573.1.02", "Шкаф для одежды 3Д «Мартина»", "bedroom", [1678, 618, 2318], 48, None),
        ("martina-1-03", "П3.573.1.03", "Тумба прикроватная «Мартина»", "bedroom", [600, 412, 619], 48, None),
        ("martina-1-01", "П3.573.1.01", "Кровать 2-16 «Мартина»", "bedroom", [1793, 2075, 1160], 48, "сп. место 2000×1600"),
        ("martina-1-06", "П3.573.1.06", "Зеркало «Мартина»", "decor", [744, 84, 864], 48, None),
        ("martina-1-05", "П3.573.1.05", "Комод «Мартина»", "bedroom", [1300, 465, 910], 48, None),
        ("martina-1-04", "П3.573.1.04", "Комод «Мартина»", "bedroom", [750, 465, 1310], 48, None),
    ]
    out = []
    for mid, code, name, cat, size, page, note in models:
        e = {"id": mid, "code": code, "name": name, "collection": "martina", "category": cat, "size": size, "page": page}
        if mid in ("martina-50", "martina-1-06"):
            e["mount"] = "wall"
        e["note"] = "по каталогу, без инструкции" + (f"; {note}" if note else "")
        out.append(e)
    frag = {
        "finishes": [{"id": "martina-moloko-silver", "name": "Молоко с серебром", "body": "door_enamel_whitey#e3e3e0",
                      "roles": {"carve": "door_enamel_whitey#b4b6b8", "patina": "chrome#b0b2b4"},
                      "swatch": "#e3e3e0"}],
        "profiles": {
            "martina-crown": {"name": "Карниз «Мартина»: полочка, выкружка, валик, полочка; вынос 30, высота 60",
                              "pts": [[30, 0], [29, 4], [27.5, 7], [26, 9], [24, 10], [23, 13], [21, 18], [18, 24],
                                      [14, 30], [10, 35], [6, 39], [4, 41], [4, 45], [2, 46], [0.5, 49], [0, 53],
                                      [0, 60], [60, 60], [60, 0]]},
            "martina-crown-s": {"name": "Карниз зеркала «Мартина»: вынос 22, высота 36",
                                "pts": [[22, 0], [21, 3], [18, 9], [14, 15], [9, 21], [5, 25], [3, 27], [3, 31],
                                        [0, 32], [0, 36], [46, 36], [46, 0]]},
            "martina-pbead": {"name": "Фасад «Мартина»: калёвка филёнки 14 × 4",
                              "pts": [[0, 0], [0, 4], [2, 4], [3.5, 3.4], [6, 3.3], [8.5, 2.6], [11, 1.6], [14, 0]]},
            "martina-gbead": {"name": "Штапик остекления «Мартина» 12 × 7",
                              "pts": [[0, 0], [0, 7], [3, 7], [5.5, 6], [8.5, 4], [11, 1.8], [12, 0]]},
            "martina-mbead": {"name": "Рамка зеркала «Мартина» 14 × 6", "pts": [[0, 0], [0, 5], [2, 6], [8, 6], [11, 4.5], [14, 0]]},
            "martina-bead": {"name": "Валик цоколя «Мартина» 12 × 5 (серебро)",
                             "pts": [[0, 0], [0, 2], [1.5, 4], [4, 5], [8, 5], [10.5, 4], [12, 2], [12, 0]]},
            "martina-rope": {"name": "Витой шнур «Мартина» 12 × 6 (серебро; витьё не передано — полукруглый валик)",
                             "pts": [[0, 0], [0.5, 2.3], [1.8, 4.2], [3.7, 5.5], [6, 6], [8.3, 5.5], [10.2, 4.2],
                                     [11.5, 2.3], [12, 0]]}},
        "collections": [{"id": "martina", "name": "Мартина", "brand": "Пинскдрев", "finishes": ["martina-moloko-silver"],
                         "metal": "chrome#c4c5c7",
                         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 45–48; инструкций нет — все модули по каталогу. Корпус ЛДСП 16 «Молоко» на цоколе с фигурными ножками, пилястры с резными лилиями, карниз / фриз с витым серебряным шнуром, фасады МДФ: рамка и филёнка с резьбой «листья» под серебряной патиной, стеклянные витрины, серебристые ручки-кнопки."}],
        "models": out}
    with open(os.path.join(HERE, "martina_catalog.json"), "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    print(vitrina("martina-01-1", 690, 424, 1, "left"), vitrina("martina-01", 690, 424, 1, "right"),
          vitrina("martina-02", 1192, 429, 2, None))
    print(tumba_chest("martina-22", 1158, 2), tumba_chest("martina-23", 1650, 3), tumba_tv(), polka())
    print(table("martina-54", 1200, 900, 760), table("martina-31", 700, 700, 500, leg=70, apron=70),
          table("martina-32", 1200, 700, 500, leg=70, apron=70))
    print(wardrobe(), tumba_bed(), mirror(), bed(), komod("martina-1-05", 1300, 910, 3), komod("martina-1-04", 750, 1310, 4, 150))
    catalog()
