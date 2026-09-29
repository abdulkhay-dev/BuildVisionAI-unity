"""«Элиза» (БМ2.841, Пинскдрев-Бобруйск): all 7 articles by the catalogue (p. 108: the bedroom interior, the module
cut-outs with the wardrobes' interior sketches, the «Белая Ваниль» swatch) — no instruction, no product photos.

Construction (read off the p. 108 cut-outs, the catalogue sizes as scale — 0.31 px/mm on the 4Д):
  * carcass ЛДСП 16 «Белая Ваниль»: the sides stand to the floor, a plinth board 65 high recessed 20 mm, the bottom over
    it; overlay fronts 18 (2 mm reveal, 3 mm gaps), the mirror doors with a 4-mm mirror glued on (so B = sides + 18 + 4);
  * the wardrobes' crown: a cornice (44 high, 25 out) along both sides with a cap, and across the front an arched crest
    board — flat ends, an ogee arch rising to H in the middle (`shape: path`) — with two gilded lines along its arch and
    a gilded ornament at its top; the bedroom pieces: a 25 top 15 mm out;
  * the décor: gilded mouldings on the fronts — rectangles with concave (inverted) corners over and under an oval
    medallion on the plain doors, round the arched mirrors, round the drawers — built as gilded rods 7 mm (role
    "patina", a gold colour), and flat gilded ornaments (role "ornament") in the medallions and on the crests;
  * antique-bronze knobs Ø32 on doors and small drawers, small bronze bar pulls on the chest's drawers;
  * drawer boxes ЛДСП 16 with ХДФ bottoms, 13 mm runner gap.

    python3 tools/casegoods/gen/eliza.py      # Designs/eliza-*.json, gen/eliza_catalog.json
"""
import json
import math
import os

from kit_w3a import back, bar, box, cornice, drawer_box, dump, fmt, ids, knob, line, metal_base, part

HERE = os.path.dirname(os.path.abspath(__file__))
T, FT, MT = 16, 18, 4
G, RV = 3, 2
PL = 65
GD = 7                   # gilded rod


# ----------------------------------------------------------------------------------------------------------- décor
def polyline(pid, pts, z, d=GD, closed=True):
    out = []
    n = len(pts)
    for k in range(n if closed else n - 1):
        a, b = pts[k], pts[(k + 1) % n]
        out.append(line(f"{pid}-{k + 1}", [a[0], a[1], z], [b[0], b[1], z], d=d))
    return out


def concave_rect(a0, b0, a1, b1, r=40, steps=4, top_arch=0):
    """Rectangle with inverted (concave) quarter-circle corners; top_arch > 0 raises the top edge's middle."""
    pts = []
    corners = [(a0, b0, 1, 1), (a1, b0, -1, 1), (a1, b1, -1, -1), (a0, b1, 1, -1)]
    # walk: bottom-left corner arc, bottom edge, bottom-right arc, right edge, top-right arc, top edge, top-left arc
    for k, (cx, cy, sx, sy) in enumerate(corners):
        # the arc around the corner point, from the edge coming in to the edge going out
        if k == 0:
            angs = [math.pi / 2 - math.pi / 2 * i / steps for i in range(steps + 1)]      # from (cx, cy+r) to (cx+r, cy)
            arc = [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in angs]
        elif k == 1:
            arc = [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in [math.pi - math.pi / 2 * i / steps for i in range(steps + 1)]]
        elif k == 2:
            arc = [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in [-math.pi / 2 - math.pi / 2 * i / steps for i in range(steps + 1)]]
        else:
            arc = [(cx + r * math.cos(t), cy + r * math.sin(t)) for t in [0 - math.pi / 2 * i / steps for i in range(steps + 1)]]
        if k == 3 and top_arch:
            n = 8
            for i in range(1, n):
                x = a1 - r - (a1 - a0 - 2 * r) * i / n
                u = (x - (a0 + a1) / 2) / ((a1 - a0) / 2 - r)
                pts.append((x, b1 + top_arch * (1 - u * u)))
        pts += arc
    return pts


def ellipse_pts(cx, cy, rx, ry, n=20):
    return [(cx + rx * math.cos(2 * math.pi * i / n), cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def ornament(pid, cx, cy, z, w=180, h=56):
    return part(pid, [cx - w / 2, cy - h / 2, z - 0.5, cx + w / 2, cy + h / 2, z + 0.9], kind="front", mat="ornament",
                shape="circle", edge=0.5)


# ------------------------------------------------------------------------------------------------------------ fronts
def panel_door(pid, x0, y0, x1, y1, z0, medallion=True):
    """A plain door with two gilded concave-cornered frames and an oval medallion between them."""
    zf = z0 + FT
    f = part(pid, [x0, y0, z0, x1, y1, zf], kind="front")
    out = [f]
    h = y1 - y0
    ym = y0 + h * 0.46
    m = 62
    out += polyline(f"{pid}-gu", concave_rect(x0 + m, ym + 95, x1 - m, y1 - m, r=45), zf + 1.5)
    out += polyline(f"{pid}-gl", concave_rect(x0 + m, y0 + m, x1 - m, ym - 95, r=45), zf + 1.5)
    if medallion:
        cx = (x0 + x1) / 2
        rx, ry = (x1 - x0) / 2 - m - 5, 62
        out += polyline(f"{pid}-go", ellipse_pts(cx, ym, rx, ry), zf + 1.5, d=6)
        out.append(ornament(f"{pid}-orn", cx, ym, zf, w=2 * rx - 50, h=ry * 1.1))
    return out


def mirror_door(pid, x0, y0, x1, y1, z0):
    """A door with the mirror glued on, its top arched up by 60 in the middle; a gilded line round the mirror."""
    zf = z0 + FT
    f = part(pid, [x0, y0, z0, x1, y1, zf], kind="front")
    a0, b0, a1, b1 = x0 + 45, y0 + 45, x1 - 45, y1 - 110
    arch = (f"M {fmt(a0)} {fmt(b0)} L {fmt(a1)} {fmt(b0)} L {fmt(a1)} {fmt(b1)} "
            f"C {fmt(a1 - (a1 - a0) * 0.3)} {fmt(b1 + 80)} {fmt(a0 + (a1 - a0) * 0.3)} {fmt(b1 + 80)} {fmt(a0)} {fmt(b1)} Z")
    mr = part(f"{pid}-mirror", [a0, b0, zf, a1, b1 + 60, zf + MT], kind="mirror", shape="path", outline=arch, edge=0.5)
    pts = [(a0 - 12, b0 - 12), (a1 + 12, b0 - 12), (a1 + 12, b1)]
    for i in range(1, 12):
        t = i / 12
        # the cubic of the mirror's top, offset up 12
        p0, p1, p2, p3 = (a1, b1), (a1 - (a1 - a0) * 0.3, b1 + 80), (a0 + (a1 - a0) * 0.3, b1 + 80), (a0, b1)
        x = (1 - t) ** 3 * p0[0] + 3 * (1 - t) ** 2 * t * p1[0] + 3 * (1 - t) * t * t * p2[0] + t ** 3 * p3[0]
        y = (1 - t) ** 3 * p0[1] + 3 * (1 - t) ** 2 * t * p1[1] + 3 * (1 - t) * t * t * p2[1] + t ** 3 * p3[1]
        pts.append((x, y + 12))
    pts.append((a0 - 12, b1))
    return [f, mr] + polyline(f"{pid}-g", pts, zf + 1.5)


def drawer_front(pid, x0, y0, x1, y1, z0, m=28, lines=("t", "b", "l", "r"), top_wave=0):
    zf = z0 + FT
    f = part(pid, [x0, y0, z0, x1, y1, zf], kind="front")
    a0, b0, a1, b1 = x0 + m, y0 + m * 0.8, x1 - m, y1 - m * 0.8
    out = [f]
    if "b" in lines:
        out.append(line(f"{pid}-gb", [a0, b0, zf + 1.5], [a1, b0, zf + 1.5], d=GD))
    if "l" in lines:
        out.append(line(f"{pid}-gl", [a0, b0, zf + 1.5], [a0, b1, zf + 1.5], d=GD))
    if "r" in lines:
        out.append(line(f"{pid}-gr", [a1, b0, zf + 1.5], [a1, b1, zf + 1.5], d=GD))
    if "t" in lines:
        if top_wave:
            n = 12
            pts = []
            for i in range(n + 1):
                x = a0 + (a1 - a0) * i / n
                u = (x - (a0 + a1) / 2) / ((a1 - a0) / 2)
                pts.append((x, b1 - top_wave + top_wave * max(0.0, 1 - (u / 0.6) ** 2) ** 2))
            out += polyline(f"{pid}-gt", pts, zf + 1.5, closed=False)
        else:
            out.append(line(f"{pid}-gt", [a0, b1, zf + 1.5], [a1, b1, zf + 1.5], d=GD))
    return out


# ------------------------------------------------------------------------------------------------------- wardrobes
def crest_outline(W, y0, y_end, H, flat=0.1):
    a, b = W * flat, W * (1 - flat)
    return (f"M 0 {fmt(y0)} L {fmt(W)} {fmt(y0)} L {fmt(W)} {fmt(y_end)} L {fmt(b)} {fmt(y_end)} "
            f"C {fmt(b - W * 0.12)} {fmt(y_end)} {fmt(W * 0.62)} {fmt(H)} {fmt(W / 2)} {fmt(H)} "
            f"C {fmt(W * 0.38)} {fmt(H)} {fmt(a + W * 0.12)} {fmt(y_end)} {fmt(a)} {fmt(y_end)} L 0 {fmt(y_end)} Z")


def crest_curve(W, y_end, H, flat=0.1, dy=0, n=24):
    """Points along the crest's top edge (the two cubics), moved down by dy."""
    a, b = W * flat, W * (1 - flat)
    segs = [((a, y_end), (a + W * 0.12, y_end), (W * 0.38, H), (W / 2, H)),
            ((W / 2, H), (W * 0.62, H), (b - W * 0.12, y_end), (b, y_end))]
    pts = [(25, y_end - dy)]
    for s in segs:
        for i in range(1, n // 2 + 1):
            t = i / (n // 2)
            x = sum(c[0] * w for c, w in zip(s, [(1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3]))
            y = sum(c[1] * w for c, w in zip(s, [(1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3]))
            pts.append((x, y - dy))
    pts.append((W - 25, y_end - dy))
    return pts


def wardrobe(did, W, H, kinds, hinges, sections):
    """kinds: per door "p" (plain with medallion) / "m" (mirror); sections: [(from door, to door, "rail" / "shelves" /
    "mixed")] — partitions behind the joints between sections."""
    B = 622
    OV = 25
    dz = B - FT - MT                         # sides
    fz = dz + FT
    x0, x1 = OV, W - OV
    ys = 2145                                # the carcass top (under the cornice at the ends: 2145 + 44 + 21 = 2210)
    y_end = 2210
    p, m = [], []
    p += [part("side-l", [x0, 0, 0, x0 + T, ys, dz]), part("side-r", [x1 - T, 0, 0, x1, ys, dz]),
          part("bottom", [x0 + T, PL, 0, x1 - T, PL + T, dz]), part("top", [x0 + T, ys - T, 0, x1 - T, ys, dz]),
          part("plinth", [x0 + T, 0, dz - 36, x1 - T, PL, dz - 20])]
    p.append({"id": "cornice-r", "kind": "moulding", "profile": "eliza-cornice", "plane": "top", "z": ys, "side": 1,
              "path": [[W, 0], [W, dz]]})
    p.append({"id": "cornice-l", "kind": "moulding", "profile": "eliza-cornice", "plane": "top", "z": ys, "side": 1,
              "path": [[0, dz], [0, 0]]})
    p.append(part("cap", [0, ys + 44, 0, W, y_end, dz], edge=3))
    p.append(part("crest", [0, ys, dz, W, H, B], shape="path", outline=crest_outline(W, ys, y_end, H), edge=3))
    p += polyline("crest-g1", crest_curve(W, y_end, H, dy=22), B + 1, d=6, closed=False)
    p += polyline("crest-g2", crest_curve(W, y_end, H, dy=40), B + 1, d=5, closed=False)
    p.append(ornament("crest-orn", W / 2, H - 75, B, w=260, h=60))
    n = len(kinds)
    free = x1 - x0 - 2 * RV - G * (n - 1)
    dw = free / n
    cols = [(x0 + RV + k * (dw + G), x0 + RV + k * (dw + G) + dw) for k in range(n)]
    joints = [(cols[k][1] + cols[k + 1][0]) / 2 for k in range(n - 1)]
    part_x = [joints[s[1] - 1] for s in sections[:-1]]
    for k, x in enumerate(part_x):
        p.append(part(f"partition-{k + 1}", [x - T / 2, PL + T, 10, x + T / 2, ys - T, dz]))
    bounds = [x0 + T] + part_x + [x1 - T]
    for k, (s0, s1, kind) in enumerate(sections):
        a = bounds[k] + (T / 2 if k else 0)
        b = bounds[k + 1] - (T / 2 if k < len(sections) - 1 else 0)
        if kind in ("rail", "mixed"):
            p.append(part(f"hat-{k + 1}", [a + 1, 1860, 20, b - 1, 1876, dz - 10]))
            p.append({"id": f"rail-{k + 1}", "kind": "tube", "mat": "chrome", "box": box(a + 2, 1780, dz / 2 - 12.5, b - 2, 1805, dz / 2 + 12.5)})
        if kind == "mixed":
            for j, y in enumerate([400, 700]):
                p.append(part(f"shelf-{k + 1}-{j + 1}", [a + 1, y - T, 20, b - 1, y, dz - 10]))
        if kind == "shelves":
            for j, y in enumerate([420, 780, 1140, 1500, 1860]):
                p.append(part(f"shelf-{k + 1}-{j + 1}", [a + 1, y - T, 20, b - 1, y, dz - 10]))
    edges = [x0 + 8] + part_x + [x1 - 8]
    for k in range(len(edges) - 1):
        p.append(back(f"back-{k + 1}", [edges[k], PL + 8, 6, edges[k + 1], ys - 8, 9.5]))
    for k, ((a, b), kind, hg) in enumerate(zip(cols, kinds, hinges)):
        name = f"door_{k + 1}"
        fr = (panel_door if kind == "p" else mirror_door)(f"f-{name}", a, PL + 1, b, ys - 3, dz)
        hx = b - 32 if hg == "left" else a + 32
        h = [knob(f"h-{name}", hx, 1015, fz + (MT if kind == "m" else 0), d=32, t=18, standoff=22)]
        p += fr + h
        m.append({"type": "door", "name": name, "parts": ids(fr + h), "hinge": hg, "angle": 105})
    return dump(did, [W, B, H], p, m)


# -------------------------------------------------------------------------------------------------- bedroom pieces
class Low:
    def __init__(self, W, B, H, pl=55):
        self.W, self.B, self.H = W, B, H
        o = 15
        self.x0, self.x1 = o, W - o
        self.fz = B - o
        self.dz = self.fz - FT
        self.yt = H - 25
        self.pl = pl
        self.p = [part("side-l", [self.x0, 0, 0, self.x0 + T, self.yt, self.dz]),
                  part("side-r", [self.x1 - T, 0, 0, self.x1, self.yt, self.dz]),
                  part("bottom", [self.x0 + T, pl, 0, self.x1 - T, pl + T, self.dz]),
                  part("plinth", [self.x0 + T, 0, self.dz - 36, self.x1 - T, pl, self.dz - 20]),
                  part("top", [0, self.yt, 0, W, H, B], edge=4),
                  back("back", [self.x0 + 8, pl + 8, 6, self.x1 - 8, self.yt - 0.5, 9.5])]
        self.m = []

    def drawer(self, name, y0, y1, handle="knob", **kw):
        a, b = self.x0 + RV, self.x1 - RV
        fr = drawer_front(f"f-{name}", a, y0, b, y1, self.dz, **kw)
        bh = max(70, min(200, y1 - y0 - 45))
        bx = drawer_box(name, self.x0 + T + 13, self.x1 - T - 13, y0 + 18, bh, self.dz - 350, self.dz)
        yc = (y0 + y1) / 2
        if handle == "knob":
            hs = [knob(f"h-{name}", (a + b) / 2, yc, self.fz, d=32, t=18, standoff=22)]
        else:
            hs = [bar(f"h-{name}-{k + 1}", a + (b - a) * f, yc - 12, self.fz, d=110, band=8, t=8, standoff=20, post=10)
                  for k, f in enumerate((0.2, 0.8))]
        self.p += fr + bx + hs
        self.m.append({"type": "drawer", "name": name, "parts": ids(fr + bx + hs), "travel": 290})


def komod():
    """Комод 1030 × 470 × 801: a shallow drawer with a knob over three drawers with two pulls each; the three share one
    gilded frame (its top waved in the middle, a gilded ornament under the wave)."""
    c = Low(1030, 470, 801)
    y0, y3 = c.pl + 1, c.yt - G
    ht = 118
    rows = (y3 - ht - G - y0 - 2 * G) / 3
    ys = [y0 + k * (rows + G) for k in range(3)]
    c.drawer("drawer_4", ys[0], ys[0] + rows, handle="bar", lines=("b", "l", "r"))
    c.drawer("drawer_3", ys[1], ys[1] + rows, handle="bar", lines=("l", "r"))
    c.drawer("drawer_2", ys[2], ys[2] + rows, handle="bar", lines=("t", "l", "r"), top_wave=40)
    c.p.append(ornament("f-drawer_2-orn", c.W / 2, ys[2] + rows - 75, c.fz, w=200, h=50))
    c.m[-1]["parts"].append("f-drawer_2-orn")
    c.drawer("drawer_1", y3 - ht, y3, handle="knob")
    return dump("eliza-1-31", [c.W, c.B, c.H], c.p, c.m)


def tumba():
    """Тумба прикроватная 470 × 440 × 481: two drawers with knobs and gilded frames."""
    c = Low(470, 440, 481)
    y0, y1 = c.pl + 1, c.yt - G
    h = (y1 - y0 - G) / 2
    c.drawer("drawer_2", y0, y0 + h)
    c.drawer("drawer_1", y0 + h + G, y1)
    return dump("eliza-1-30", [c.W, c.B, c.H], c.p, c.m)


def mirror():
    """Зеркало 856 × 36 × 925 (wall): a 22 board with an arched crest (the wardrobes' crest), a 14 crest cap to B 36,
    the mirror 4 with a concave-arched top, gilded lines and ornament."""
    W, B, H = 856, 36, 925
    y_end = 760
    p = [part("board", [0, 0, 0, W, H - 60, 22], shape="path",
              outline=crest_outline(W, 0, y_end - 60, H - 60, flat=0.12), edge=2),
         part("crest", [0, y_end - 40, 22, W, H, B], shape="path", outline=crest_outline(W, y_end - 40, y_end, H, flat=0.12), edge=3)]
    a0, b0, a1, b1 = 60, 60, W - 60, y_end - 110
    arch = (f"M {a0} {b0} L {a1} {b0} L {a1} {b1} C {fmt(a1 - 150)} {fmt(b1 + 60)} {fmt(a0 + 150)} {fmt(b1 + 60)} {a0} {b1} Z")
    p.append(part("mirror", [a0, b0, 22, a1, b1 + 50, 26], kind="mirror", shape="path", outline=arch, edge=0.5))
    p += polyline("g", concave_rect(a0 - 14, b0 - 14, a1 + 14, b1 + 14, r=30, top_arch=46), 23.5, d=6)
    p += polyline("crest-g", crest_curve(W, y_end, H, flat=0.12, dy=24), B + 1, d=5, closed=False)
    p.append(ornament("crest-orn", W / 2, H - 70, B, w=220, h=52))
    return dump("eliza-1-32", [W, B, H], p, [])


def bed(did, W):
    """Кровати 2-16 / 2-18 (x = width, z = length 2093): a shaped headboard to 1224 (wings flaring out at the posts, a
    gull-wing crest) with a buttoned upholstered panel (tufts) in a gilded frame; an arched foot board 720 with a
    gilded panel and ornament on block feet; side rails; a metal base; the mattress (sleeping 1600 / 1800 × 2000)."""
    L, H = 2093, 1224
    hb = (f"M 0 0 L {W} 0 L {W} 980 C {W - 20} 1080 {W - 90} 1110 {W - 170} 1110 "
          f"C {fmt(W * 0.7)} 1110 {fmt(W * 0.6)} {H} {fmt(W / 2)} {H} C {fmt(W * 0.4)} {H} {fmt(W * 0.3)} 1110 170 1110 "
          f"C 90 1110 20 1080 0 980 Z")
    p = [part("headboard", [0, 0, 0, W, H, 32], shape="path", outline=hb, edge=3)]
    p.append({"id": "headboard-soft", "kind": "soft", "box": box(180, 560, 32, W - 180, 1040, 92), "tufts": [12, 4], "edge": 12})
    p += polyline("hb-g", concave_rect(165, 545, W - 165, 1055, r=30), 33, d=6)
    p.append(ornament("hb-orn", W / 2, H - 55, 32, w=220, h=44))
    fb = (f"M 0 0 L {W} 0 L {W} 620 C {fmt(W * 0.8)} 640 {fmt(W * 0.62)} 720 {fmt(W / 2)} 720 "
          f"C {fmt(W * 0.38)} 720 {fmt(W * 0.2)} 640 0 620 Z")
    p.append(part("foot", [0, 110, L - 32, W, 720, L], shape="path", outline=fb.replace("M 0 0 L", "M 0 110 L", 1).replace(f"L {W} 0 L", f"L {W} 110 L", 1), edge=3))
    p += polyline("fb-g", concave_rect(90, 190, W - 90, 540, r=30, top_arch=70), L + 1.5, d=6)
    p.append(ornament("fb-orn", W / 2, 420, L, w=320, h=60))
    for k, x in enumerate([0, W - 130]):
        p.append(part(f"foot-block-{k + 1}", [x, 0, L - 60, x + 130, 110, L], edge=3))
    top = 420
    p += [part("rail-l", [30, 180, 32, 55, top, L - 32]), part("rail-r", [W - 55, 180, 32, W - 30, top, L - 32]),
          part("cleat-l", [55, top - 100, 60, 85, top - 70, L - 60]), part("cleat-r", [W - 85, top - 100, 60, W - 55, top - 70, L - 60])]
    sw = W - 169
    x0 = (W - sw) / 2
    p += [q for q in metal_base(x0 + 20, W - x0 - 20, 40, L - 40, top - 70 + 30, mattress=200, leg_xs=[W / 2], leg_zs=[700, 1400])]
    return dump(did, [W, L, H], p, [])


def catalog():
    models = [
        ("eliza-1-27-01", "БМ2.841.1.27-01", "Шкаф для одежды 4Д «Элиза»", "bedroom", [1798, 622, 2355], None),
        ("eliza-1-31", "БМ2.841.1.31", "Комод «Элиза»", "bedroom", [1030, 470, 801], None),
        ("eliza-1-32", "БМ2.841.1.32", "Зеркало «Элиза»", "decor", [856, 36, 925], None),
        ("eliza-1-16", "БМ2.841.1.16", "Кровать 2-16 «Элиза»", "bedroom", [1769, 2093, 1224], "сп. место 1600×2000"),
        ("eliza-1-30", "БМ2.841.1.30", "Тумба прикроватная «Элиза»", "bedroom", [470, 440, 481], None),
        ("eliza-1-01-01", "БМ2.841.1.01-01", "Шкаф для одежды 5Д «Элиза»", "bedroom", [2236, 622, 2382], None),
        ("eliza-1-15", "БМ2.841.1.15", "Кровать 2-18 «Элиза»", "bedroom", [1969, 2093, 1224], "сп. место 1800×2000, металлокаркас"),
    ]
    out = []
    for mid, code, name, cat, size, note in models:
        e = {"id": mid, "code": code, "name": name, "collection": "eliza", "category": cat, "size": size, "page": 108}
        if mid == "eliza-1-32":
            e["mount"] = "wall"
        e["note"] = "по каталогу, без инструкции" + (f"; {note}" if note else "")
        out.append(e)
    frag = {
        "finishes": [{"id": "eliza-vanil", "name": "Белая Ваниль (патина золото)", "body": "door_enamel_whitey#e8e6e4",
                      "roles": {"patina": "gold#c9a45c", "ornament": "gold#d2b479", "fabric": "leather_light#e7dcc4"},
                      "swatch": "#e8e6e4"}],
        "profiles": {
            "eliza-cornice": {"name": "Карниз «Элиза» по бокам: вынос 25, высота 44",
                              "pts": [[25, 0], [24, 3], [21, 9], [16, 16], [11, 23], [7, 29], [4, 34], [3, 38], [0, 40],
                                      [0, 44], [50, 44], [50, 0]]}},
        "collections": [{"id": "eliza", "name": "Элиза", "brand": "Пинскдрев", "finishes": ["eliza-vanil"],
                         "metal": "gold#6b5238",
                         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 108 (набор для спальни, Пинскдрев-Бобруйск); инструкций нет — все модули по каталогу. Корпус ЛДСП 16 «Белая Ваниль» на цоколе, у шкафов арочный гребень с золотыми линиями и орнаментом, накладные фасады с золочёными рамками (вогнутые углы, медальоны), зеркальные двери с арочным верхом, кнопки «античная бронза»; кровати с каретной стёжкой изголовья."}],
        "models": out}
    with open(os.path.join(HERE, "eliza_catalog.json"), "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    print(wardrobe("eliza-1-27-01", 1798, 2355, "pmmp", ["left", "right", "left", "right"],
                   [(0, 2, "rail"), (2, 4, "mixed")]))
    print(wardrobe("eliza-1-01-01", 2236, 2382, "pmmmp", ["left", "right", "right", "left", "right"],
                   [(0, 2, "rail"), (2, 3, "shelves"), (3, 5, "mixed")]))
    print(komod(), tumba(), mirror(), bed("eliza-1-16", 1769), bed("eliza-1-15", 1969))
    catalog()
