"""Parma (П7.050.*, «Пинскдрев-Заславль»), a country collection: «Сосна Рандерс» (white pine) with «Дуб Кантри золотой»
(the tops and the visible horizontals).

The construction, read off the 6 instructions (tables «№, наименование, a×b мм, n», two sizes; pictured hardware —
transcribed into gen/cutlists/parma-*.json; the full PDFs p. 5–6 show where the pilasters go), the p. 52–56 photos, the
p. 56 cut-outs and the site's product photos:
* Sides ЛДСП 16 run to the floor and are the legs (on adjustable glides): H = sides + the top 16. The top («крышка», oak)
  lies on them and overhangs 10 at each end; the bottom («стенка горизонтальная нижняя», oak) sits between the sides
  80 above the floor (the photos: an oak band under the fronts, an open recess under it).
* Pilasters «44 × side height» (ЛДСП 16) are glued edge to edge onto the sides' front edges with short dowels (full PDF
  step 7 / 15): they extend each side 44 forward. The fronts (МДФ 18) sit between them, flush with their faces, in front
  of the carcass edge (partitions stay behind the joints; 0.29's doors 386 overlay its partitions). This is the only
  reading that lets the drawer boxes (runners on the sides) pass and that matches the photos (a 16 strip at each end,
  the partition's edge in the doors' joint). B = side + 44: 434 / 460 / 516 / 630 — the catalogue writes 10–16 less
  (it measures the top: 0.29 420, 1.31 450, 1.53 500; 0.13 424): the designs keep B = side + 44 and say so in the note.
  Horizontals between fronts (0.13's partition 7, the shelf of 1.31, the wardrobes' drawer tier) are oak and show as
  bands in the joints.
* Backs ДВП in grooves (z 6–9). Fronts: a flat frame (50 on doors, 36 on drawers) round a slightly sunk panel with a small
  bevel («parma-bevel»); glazed doors: the frame round clear glass laid in from the back. Handles: black round knobs.
* Drawers: overlay fronts, boxes ЛДСП 16 (sides 350 × 160), ДВП bottom under the box with a «брусок продольный» under it,
  ball runners, 13 mm gaps.

z: back in grooves, sides 0–sd, pilasters sd–sd + 16, fronts to sd + 34, top from z 0.
Run: python3 tools/casegoods/gen/parma.py  (writes the designs and gen/parma_catalog.json)
"""
import json
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "parma"

T = 16            # boards, top, pilasters
FT = 18           # fronts
OV = 10           # the top's overhang
YB = 80           # the bottom's underside
DOOR_FACE = {"type": "frame", "border": 50, "depth": 3, "r": 1, "profile": "parma-bevel"}
DRAWER_FACE = {"type": "frame", "border": 36, "depth": 3, "r": 1, "profile": "parma-bevel"}
GLASS = {"frame": 62, "rebate": 12, "t": 4, "tint": "clear"}
MIRROR = {"frame": 62, "rebate": 12, "t": 4, "tint": "mirror"}
OAK = "top"


class Case:
    """A Parma carcass: L = the top's width, S = the sides' height (floor → the top's underside), sd = the sides' depth."""

    def __init__(self, did, L, S, sd, *, td=None, size=None):
        self.did, self.L, self.S, self.sd = did, L, S, sd
        self.td = td or sd + 30
        self.xl, self.xr = OV, L - OV                  # the sides' outer faces
        self.xi0, self.xi1 = self.xl + T, self.xr - T
        self.zf1 = sd + 44                             # the pilasters' and the fronts' face
        self.zp1 = self.zf1 - FT                       # the fronts' back face
        self.fx0, self.fx1 = self.xi0 + 2, self.xi1 - 2  # inset between the pilasters
        self.yb1 = YB + T                              # the bottom's top face
        self.parts, self.moves = [], []
        self.size = size or [L, self.zf1, S + T]

    def P(self, n, box, pid=None, **kw):
        p = {"n": n, "box": [round(v, 2) for v in box], **kw}
        if pid:
            p["id"] = pid
        self.parts.append(p)
        return p

    def carcass(self, nt, nl, nr, npil, nb=None, top_mat=OAK):
        self.P(nt, [0, self.S, 0, self.L, self.S + T, self.td], mat=top_mat, edge=2, grain="x")
        self.P(nl, [self.xl, 0, 0, self.xl + T, self.S, self.sd], grain="y")
        self.P(nr, [self.xr - T, 0, 0, self.xr, self.S, self.sd], grain="y")
        self.P(npil, [self.xl, 0, self.sd, self.xl + T, self.S, self.zf1], f"{npil}-l", grain="y")
        self.P(npil, [self.xr - T, 0, self.sd, self.xr, self.S, self.zf1], f"{npil}-r", grain="y")
        if nb:
            self.horizontal(nb, self.xi0, self.xi1, YB)

    def horizontal(self, n, x0, x1, y, pid=None, depth=None, mat=OAK, z0=0):
        return self.P(n, [x0, y, z0, x1, y + T, z0 + (depth or self.sd)], pid, mat=mat, grain="x")

    def upright(self, n, x0, y0, y1, pid=None, depth=None, z0=0):
        return self.P(n, [x0, y0, z0, x0 + T, y1, z0 + (depth or self.sd)], pid, grain="y")

    def shelf(self, n, x0, x1, y, depth, pid=None, kind=None, t=T, z1=None):
        z1 = z1 or self.sd - 4
        kw = {"kind": kind} if kind else {}
        return self.P(n, [x0, y, z1 - depth, x1, y + t, z1], pid, **kw)

    def back(self, n, x0, x1, y0, y1, pid=None):
        return self.P(n, [x0, y0, 6, x1, y1, 9.2], pid, kind="back")

    def rrail(self, n, x0, x1, y1, h, pid=None):
        """A rear rail on edge in front of the back, its top at y1."""
        return self.P(n, [x0, y1 - h, 10, x1, y1, 26], pid, grain="x")

    # ------------------------------------------------------------------ fronts
    def front(self, n, x0, x1, y0, y1, pid=None, glass=None, face=None, grain="y"):
        p = {"n": n, "kind": "front", "box": [round(v, 2) for v in (x0, y0, self.zp1, x1, y1, self.zf1)], "edge": 1.5,
             "grain": grain}
        if pid:
            p["id"] = pid
        if glass:
            p["glass"] = dict(glass)
        else:
            p["face"] = dict(face or DOOR_FACE)
        self.parts.append(p)
        return p.get("id", n)

    def knob(self, kid, x, y):
        self.parts.append({"id": kid, "kind": "handle", "model": "knob", "at": [round(x, 2), round(y, 2)], "d": 30, "t": 14,
                           "standoff": 12, "z": self.zf1})
        return kid

    def door(self, name, n, x0, x1, y0, y1, hinge, hy, pid=None, glass=None, hx=None):
        fid = self.front(n, x0, x1, y0, y1, pid, glass)
        if hx is None:
            hx = x1 - 32 if hinge == "left" else x0 + 32
        k = self.knob(f"k-{name}", hx, hy)
        self.moves.append({"type": "door", "name": name, "parts": [fid, k], "hinge": hinge, "angle": 105})

    def drawer(self, tag, ns, fx0, fx1, fy0, fy1, box_w, side_h=160, side_l=350, bottom=None, bar=None, hy=None,
               extra=()):
        """Overlay front ns[0]; the box (sides ns[1], ns[2], back ns[3]) box_w wide behind it; the ДВП bottom ns[4]
        (bottom = [w, l]) under the box; bar = (n, 90): the «брусок продольный» under the bottom."""
        nf, nl, nr, nb, nd = ns
        xm = (fx0 + fx1) / 2
        bx0, bx1 = xm - box_w / 2, xm + box_w / 2
        yb = fy0 + 22
        z1 = self.zp1
        z0 = z1 - side_l
        ids = [f"{nf}-{tag}", f"{nl}-{tag}", f"{nr}-{tag}", f"{nb}-{tag}", f"{nd}-{tag}"]
        self.front(nf, fx0, fx1, fy0, fy1, ids[0], face=DRAWER_FACE, grain="x")
        self.P(nl, [bx0, yb, z0, bx0 + T, yb + side_h, z1], ids[1])
        self.P(nr, [bx1 - T, yb, z0, bx1, yb + side_h, z1], ids[2])
        self.P(nb, [bx0 + T, yb, z0, bx1 - T, yb + side_h, z0 + T], ids[3])
        bw, bl = bottom
        self.P(nd, [xm - bw / 2, yb - 3, z1 - bl, xm + bw / 2, yb, z1], ids[4], kind="back")
        parts = list(ids)
        if bar:
            n_bar, w_bar = bar
            parts.append(self.P(n_bar, [xm - w_bar / 2, yb - 19, z1 - side_l, xm + w_bar / 2, yb - 3, z1], f"{n_bar}-{tag}")["id"])
        for e in extra:
            self.parts.append(e)
            parts.append(e["id"])
        parts.append(self.knob(f"k-{tag}", xm, hy or fy1 - 50))
        self.moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": parts, "travel": int(side_l * 0.85)})

    def dump(self):
        return dump(self.did, self.size, self.parts, self.moves)


def spread(x0, widths, gap):
    out, x = [], x0
    for w in widths:
        out.append((x, x + w))
        x += w + gap
    return out


def rail_tube(pid, x0, x1, y, z, covers=None):
    p = {"id": pid, "kind": "tube", "mat": "chrome", "box": [x0, y - 12.5, z - 12.5, x1, y + 12.5, z + 12.5]}
    if covers:
        p["covers"] = covers
    return p


# ================================================================================================== living room
def vitrine(did, L, ns, *, instructed, size):
    """A glazed door 1478 over a panel door 386 per bay (0.13: two bays of 428 either side of partitions 6 / 8; 0.11: one
    bay): the oak bottom 5 at 80 and the oak horizontal 7 at the doors' joint show as bands; 3 glass shelves per bay, a rear
    царга 10 under the top in each upper bay."""
    c = Case(did, L, 1984, 390, td=420, size=size)
    n = ns
    c.carcass(n["top"], n["left"], n["right"], n["pil"], n["bottom"])
    y7 = c.yb1 + 390
    c.horizontal(n["h7"], c.xi0, c.xi1, y7)
    bays = [(c.xi0, c.xi1)]
    if L > 600:
        xm = (c.xi0 + c.xi1) / 2 - 8
        c.upright(n["p8"], xm, c.yb1, y7)
        c.upright(n["p6"], xm, y7 + T, c.S)
        bays = [(c.xi0, xm), (xm + T, c.xi1)]
    for k, (a, b) in enumerate(bays):
        for j, y in enumerate((830, 1200, 1570)):
            c.shelf(n["glass"], a + 1, b - 1, y, 360, pid=f"{n['glass']}-{k + 1}{j + 1}", kind="glass", t=5, z1=c.sd - 15)
        c.rrail(n["tsarga"], a, b, c.S, 200, pid=f"{n['tsarga']}-{k + 1}" if len(bays) > 1 else None)
    fr = spread(c.fx0, [424] * len(bays), c.fx1 - c.fx0 - 424 * len(bays)) if len(bays) > 1 else [(c.fx0, c.fx1)]
    hinges = ["left", "right"] if len(bays) > 1 else ["left"]
    for k, ((a, b), hg) in enumerate(zip(fr, hinges)):
        sfx = f"-{k + 1}" if len(bays) > 1 else ""
        c.door(f"door_bottom{sfx}", n["d12"], a, b, c.yb1 + 2, y7 - 2, hg, (c.yb1 + y7) / 2, pid=f"{n['d12']}{sfx}" if sfx else None)
        c.door(f"door_top{sfx}", n["d11"], a, b, y7 + T + 2, c.S - 2, hg, 1240, pid=f"{n['d11']}{sfx}" if sfx else None,
               glass=GLASS)
    # backs: 2 × 2 of 449 × 957 in the grooves of the sides, the partition, the bottom and the top
    bw = (c.xi1 - c.xi0) / len(bays) + 21 - (8 if len(bays) > 1 else 0)
    for k, (a, b) in enumerate(bays):
        x0 = a - 10.5
        for j, y0 in enumerate((YB - 5, YB - 5 + 957)):
            c.back(n["back"], x0, x0 + (449 if instructed else b - a + 21), y0, y0 + 957, f"{n['back']}-{k + 1}{j + 1}")
    return c.dump()


NS_013 = {"top": "1", "left": "2", "right": "3", "pil": "4", "bottom": "5", "p6": "6", "h7": "7", "p8": "8", "glass": "9",
          "tsarga": "10", "d11": "11", "d12": "12", "back": "13"}


def m0_13():
    """П7.050.0.13 Шкаф 2Д 924 × 424 × 2000 (instruction; built B434 = side 390 + pilaster 44, see the module doc)."""
    return vitrine("parma-0-13", 924, NS_013, instructed=True, size=[924, 434, 2000])


def m0_11():
    """П7.050.0.11 Шкаф 480 × 424 × 2000 (by catalogue / photo: one bay of 0.13, «универсальный» — the doors can hang either
    way; the numbers of 0.13 kept as labels)."""
    return vitrine("parma-0-11", 480, NS_013, instructed=False, size=[480, 434, 2000])


def tv(did, L, ns, *, doors, size, instructed):
    """TV units 0.29 (door | niche over a drawer | door) and 0.21 (door | niche over a drawer): sides 486 as legs, the oak
    bottom 5 at 84 under the fronts, partitions 370 on it, flat rails 15 (381 × 80) under the top over the side bays, overlay
    doors 386 × 386 and the drawer front 636 × 200; the knobs at the doors' inner top corners."""
    n = ns
    c = Case(did, L, 486, 390, td=420, size=size)
    c.carcass(n["top"], n["left"], n["right"], n["pil"])
    yb0 = 84
    c.horizontal(n["bottom"], c.xi0, c.xi1, yb0)
    y0 = yb0 + T
    bays = []
    x = c.xi0
    if "left" in doors:
        bays.append(("door", x, x + 381))
        x += 381
        c.upright(n["p6"], x, y0, y0 + 370, depth=390)
        c.P(n["bar"], [bays[-1][1], y0 + 370, 10, bays[-1][2], c.S, 90], f"{n['bar']}-l")
        x += T
    xr = c.xi1 - 381 - T if "right" in doors else c.xi1
    bays.append(("mid", x, xr))
    if "right" in doors:
        c.upright(n["p7"], xr, y0, y0 + 370, depth=390)
        bays.append(("door", xr + T, c.xi1))
        c.P(n["bar"], [xr + T, y0 + 370, 10, c.xi1, c.S, 90], f"{n['bar']}-r")
    _, a, b = bays[[k for k, bb in enumerate(bays) if bb[0] == "mid"][0]]
    yd1 = y0 + 200
    c.shelf(n["shelf"], a, b, yd1 + 20, 370, z1=c.sd - 4)
    # fronts
    fx = c.fx0
    fronts = []
    for kind, a_, b_ in bays:
        w = 386 if kind == "door" else 636
        fronts.append((kind, fx, fx + w))
        fx += w + 2
    for kind, fa, fb in fronts:
        if kind == "door":
            side = "left" if fa < L / 2 else "right"
            c.door(f"door_{side}", n["door"], fa, fb, y0, c.S, side, c.S - 50, pid=f"{n['door']}-{side[0]}" if len(doors) > 1 else None)
        else:
            c.drawer("1", n["drawer"], fa, fb, y0, yd1, 596, bottom=[592, 355], hy=(y0 + yd1) / 2)
    # backs: the door bays 402 × 402, the drawer 636 × 216 (the niche is open)
    for kind, a_, b_ in bays:
        if kind == "door":
            c.back(n["back_d"], a_ - 10.5, b_ + 10.5, y0 - 8, y0 + 394, f"{n['back_d']}-{'l' if a_ < L / 2 else 'r'}"
                   if len(doors) > 1 else None)
        else:
            xm = (a_ + b_) / 2
            c.back(n["back_m"], xm - 318, xm + 318, y0 - 8, y0 + 208)
    return c.dump()


NS_029 = {"top": "1", "left": "2", "right": "3", "pil": "4", "bottom": "5", "p6": "6", "p7": "7", "shelf": "8", "door": "9",
          "drawer": ("10", "11", "12", "13", "14"), "bar": "15", "back_d": "16", "back_m": "17"}


def m0_29():
    """П7.050.0.29 Тумба 1468 × 420 × 502 (instruction). The catalogue's B420 is the top; the pilasters and fronts reach
    390 + 44 = 434 — built 434."""
    return tv("parma-0-29", 1468, NS_029, doors=("left", "right"), size=[1468, 434, 502], instructed=True)


def m0_21():
    """П7.050.0.21 Тумба 1080 × 420 × 502 (by catalogue, p. 53 / 56: 0.29 without its right door bay — a door on the left,
    the niche over the drawer 636 on the right; the numbers of 0.29 kept as labels)."""
    return tv("parma-0-21", 1080, NS_029, doors=("left",), size=[1080, 434, 502], instructed=False)


def m0_22():
    """П7.050.0.22 Тумба 830 × 420 × 1296 (by catalogue, p. 53 photo / p. 56 cut-out): three rows of two doors (386 wide,
    like 0.29's) between oak horizontals, a partition in the middle."""
    c = Case("parma-0-22", 830, 1280, 390, td=420, size=[830, 434, 1296])
    c.carcass("top", "side-l", "side-r", "pil", "bottom")
    xm = (c.xi0 + c.xi1) / 2 - 8
    row = (c.S - c.yb1 - 2 * T) / 3
    ys = [c.yb1 + k * (row + T) for k in range(3)]
    for k in (1, 2):
        c.horizontal(f"h-{k}", c.xi0, c.xi1, ys[k] - T)
    for k in range(3):
        c.upright(f"part-{k + 1}", xm, ys[k], ys[k] + row)
    fr = spread(c.fx0, [386, 386], c.fx1 - c.fx0 - 772)
    for k, y in enumerate(ys):
        for (fa, fb), side in zip(fr, ("left", "right")):
            c.door(f"door_{k + 1}{side[0]}", f"door-{k + 1}{side[0]}", fa, fb, y + 1, y + row - 1, side,
                   y + row - 60 if k < 2 else y + row - 60)
    for k in range(3):
        for side, (a, b) in (("l", (c.xi0, xm)), ("r", (xm + T, c.xi1))):
            c.back(f"back-{k + 1}{side}", a - 10.5, b + 10.5, ys[k] - 8, ys[k] + row + 8)
    return c.dump()


def m0_32():
    """П7.050.0.32 Комод 830 × 450 × 1296 (by catalogue, p. 55 photo / p. 56 cut-out): a full-width drawer on top over an
    oak horizontal, two doors below with two shelves; sides 416 as 1.31's."""
    c = Case("parma-0-32", 830, 1280, 416, td=450, size=[830, 460, 1296])
    c.carcass("top", "side-l", "side-r", "pil", "bottom")
    yh = c.S - 2 - 200 - 2 - T
    c.horizontal("h-1", c.xi0, c.xi1, yh)
    c.rrail("rail", c.xi0, c.xi1, c.S, 80)
    for k, y in enumerate((440, 760)):
        c.shelf(f"shelf-{k + 1}", c.xi0 + 1, c.xi1 - 1, y, 390)
    fr = spread(c.fx0, [386, 386], c.fx1 - c.fx0 - 772)
    for (fa, fb), side in zip(fr, ("left", "right")):
        c.door(f"door_{side}", f"door-{side[0]}", fa, fb, c.yb1 + 2, yh - 2, side, yh - 60)
    c.drawer("1", ("df", "ds-l", "ds-r", "db", "dd"), c.fx0, c.fx1, yh + T + 2, c.S - 2, 752, bottom=[748, 355],
             bar=("dbar", 90))
    c.back("back-1", c.xi0 - 10, c.xi1 + 10, YB - 5, yh + 8)
    c.back("back-2", c.xi0 - 10, c.xi1 + 10, yh + 8, c.S + 5)
    return c.dump()


def m0_61():
    """П7.050.0.61 Стеллаж 1468 × 450 × 1296 (by catalogue, the site photos): two drawers on top (a divider between their
    boxes) over an oak horizontal, below it 4 × 3 open cells (three partitions, two white shelf rows) on the oak bottom."""
    c = Case("parma-0-61", 1468, 1280, 416, td=450, size=[1468, 460, 1296])
    c.carcass("top", "side-l", "side-r", "pil", "bottom")
    yh = c.S - 2 - 200 - 2 - T
    c.horizontal("h-1", c.xi0, c.xi1, yh)
    xm = (c.xi0 + c.xi1) / 2 - 8
    c.upright("div", xm, yh + T, c.S)
    cw = (c.xi1 - c.xi0 - 3 * T) / 4
    row = (yh - c.yb1 - 2 * T) / 3
    for k in (1, 2):
        c.horizontal(f"shelf-{k}", c.xi0, c.xi1, c.yb1 + k * row + (k - 1) * T, mat="body")
    for k in range(3):
        x = c.xi0 + (k + 1) * cw + k * T
        for r in range(3):
            y0 = c.yb1 + r * (row + T)
            c.upright(f"part-{k + 1}{r + 1}", x, y0, y0 + row)
    fr = spread(c.fx0, [(c.fx1 - c.fx0 - 2) / 2] * 2, 2)
    for k, (fa, fb) in enumerate(fr):
        c.drawer(str(k + 1), ("df", "ds-l", "ds-r", "db", "dd"), fa, fb, yh + T + 2, c.S - 2, (c.xi1 - c.xi0 - T) / 2 - 26,
                 bottom=[(c.xi1 - c.xi0 - T) / 2 - 30, 355])
    c.back("back-1", c.xi0 - 10, xm + 8, YB - 5, c.S + 5)
    c.back("back-2", xm + 8, c.xi1 + 10, YB - 5, c.S + 5)
    return c.dump()


def m0_55():
    """П7.050.0.55 Стол журнальный 700 × 700 × 500 (by catalogue, the site photo): an oak top 16 over an apron of white
    boards (100) between four L-shaped corner legs (two boards 80 × 16 each), an oak shelf low between the legs."""
    c = Case("parma-0-55", 700, 484, 700, size=[700, 700, 500])
    c.parts.append({"id": "top", "box": [0, 484, 0, 700, 500, 700], "mat": OAK, "edge": 2, "grain": "x"})
    o, s, w = 30, 640, 80
    for tag, sx, sz in (("fl", 0, 1), ("fr", 1, 1), ("bl", 0, 0), ("br", 1, 0)):
        x0 = o if sx == 0 else o + s - w
        xa = o if sx == 0 else o + s - T
        z0 = o + s - T if sz else o
        za = o + s - w if sz else o + T
        c.parts.append({"id": f"leg-{tag}a", "box": [x0, 0, z0, x0 + w, 484, z0 + T], "grain": "y"})
        c.parts.append({"id": f"leg-{tag}b", "box": [xa, 0, za, xa + T, 484, za + w - T], "grain": "y"})
    for tag, box in (("f", [o + w, 384, o + s - T, o + s - w, 484, o + s]), ("b", [o + w, 384, o, o + s - w, 484, o + T]),
                     ("l", [o, 384, o + w, o + T, 484, o + s - w]), ("r", [o + s - T, 384, o + w, o + s, 484, o + s - w])):
        c.parts.append({"id": f"apron-{tag}", "box": box, "grain": "x" if tag in "fb" else "z"})
    c.parts.append({"id": "shelf", "box": [o + T, 110, o + T, o + s - T, 126, o + s - T], "mat": OAK, "grain": "x"})
    return c.dump()


def m0_51():
    """П7.050.0.51 Стол обеденный 1000 × 1000 × 750 (by catalogue, p. 53 photo / p. 56 cut-out): an oak top 25 on four white
    L-shaped legs (two boards 100 × 25), an apron 100 between them."""
    c = Case("parma-0-51", 1000, 725, 1000, size=[1000, 1000, 750])
    c.parts.append({"id": "top", "box": [0, 725, 0, 1000, 750, 1000], "mat": OAK, "edge": 3, "grain": "x"})
    o, s, w, t = 60, 880, 100, 25
    for tag, sx, sz in (("fl", 0, 1), ("fr", 1, 1), ("bl", 0, 0), ("br", 1, 0)):
        x0 = o if sx == 0 else o + s - w
        xa = o if sx == 0 else o + s - t
        z0 = o + s - t if sz else o
        za = o + s - w if sz else o + t
        c.parts.append({"id": f"leg-{tag}a", "box": [x0, 0, z0, x0 + w, 725, z0 + t], "grain": "y"})
        c.parts.append({"id": f"leg-{tag}b", "box": [xa, 0, za, xa + t, 725, za + w - t], "grain": "y"})
    for tag, box in (("f", [o + w, 625, o + s - 16 - 10, o + s - w, 725, o + s - 10]),
                     ("b", [o + w, 625, o + 10, o + s - w, 725, o + 26]),
                     ("l", [o + 10, 625, o + w, o + 26, 725, o + s - w]),
                     ("r", [o + s - 26, 625, o + w, o + s - 10, 725, o + s - w])):
        c.parts.append({"id": f"apron-{tag}", "box": box, "grain": "x" if tag in "fb" else "z"})
    return c.dump()


def m0_71():
    """П7.050.0.71 Полка 1080 × 260 × 97 (by catalogue, the p. 52–55 photos): an oak board 16 on two black steel L brackets
    (a wall leg 97 and an arm under the board, a scroll at its end)."""
    c = Case("parma-0-71", 1080, 81, 260, size=[1080, 260, 97])
    c.parts.append({"id": "board", "box": [0, 81, 0, 1080, 97, 260], "mat": OAK, "edge": 2, "grain": "x"})
    for k, x in enumerate((160, 920)):
        c.parts.append({"id": f"bracket-{k + 1}a", "box": [x - 15, 0, 0, x + 15, 81, 4], "mat": "black"})
        c.parts.append({"id": f"bracket-{k + 1}b", "box": [x - 15, 77, 4, x + 15, 81, 215], "mat": "black"})
        c.parts.append({"id": f"bracket-{k + 1}c", "kind": "rod", "mat": "black", "from": [x, 79, 60], "to": [x, 20, 4],
                        "d": 6, "section": "square"})
    return c.dump()


# ================================================================================================== bedroom
def m1_31():
    """П7.050.1.31 Комод 900 × 450 × 940 (instruction): four drawers 844 × 200, the oak shelf 6 under the top drawer (a band
    in the joint, as the photos show), the oak bottom 5 at 80, a rear rail 7 under the top, a rear царга 14 behind the
    backs' joint."""
    c = Case("parma-1-31", 900, 924, 416, td=450, size=[900, 460, 940])
    c.carcass("1", "2", "3", "4", "5")
    ys = [c.yb1 + 2, c.yb1 + 204, c.yb1 + 406]
    y6 = ys[2] + 202 + 2
    c.horizontal("6", c.xi0, c.xi1, y6)
    ys.append(y6 + T + 2)
    c.rrail("7", c.xi0, c.xi1, c.S, 80)
    c.rrail("14", c.xi0, c.xi1, 398 + 100, 200)
    for k, y in enumerate(ys):
        c.drawer(str(k + 1), ("8", "9", "10", "11", "13"), c.fx0, c.fx1, y, y + 200, 822, bottom=[818, 355], bar=("12", 90))
    xm = (c.xl + c.xr) / 2
    c.back("16", xm - 438, xm + 438, YB + 5, YB + 318, "16-1")
    c.back("16", xm - 438, xm + 438, YB + 318, YB + 631, "16-2")
    c.back("15", xm - 438, xm + 438, YB + 631, YB + 840)
    return c.dump()


def m1_26():
    """П7.050.1.26 Тумба прикроватная 480 × 450 × 502 (by catalogue, p. 54–55 photos): 1.31's sides (416) at 486, the oak
    bottom at 84, one overlay door 424 × 386 hinged on the right (the knob near its left edge), a shelf behind it."""
    c = Case("parma-1-26", 480, 486, 416, td=450, size=[480, 460, 502])
    c.carcass("top", "side-l", "side-r", "pil")
    c.horizontal("bottom", c.xi0, c.xi1, 84)
    c.rrail("rail", c.xi0, c.xi1, c.S, 80)
    c.shelf("shelf", c.xi0 + 1, c.xi1 - 1, 290, 390)
    c.door("door", "door", c.fx0, c.fx1, 100, c.S, "right", c.S - 60)
    c.back("back", c.xi0 - 10, c.xi1 + 10, 92, c.S + 5)
    return c.dump()


def m1_53():
    """П7.050.1.53 Стол 900 × 500 × 800 (instruction): solid sides 472 on glides, the top on them, a rear modesty panel 5
    under the top, the drawer housing floor 6, one drawer 844 × 200 with an organiser (two walls 10, dividers 11) in its
    rear half. The catalogue's B500 is the top; the pilasters and the drawer front reach 472 + 44 = 516 — built 516."""
    c = Case("parma-1-53", 900, 784, 472, td=500, size=[900, 516, 800])
    c.carcass("1", "2", "3", "4")
    c.P("5", [c.xi0, c.S - 400, 0, c.xi1, c.S, T], grain="x")
    y6 = c.S - 2 - 200 - 2 - T
    c.shelf("6", c.xi0, c.xi1, y6, 454, z1=c.sd)
    fy0 = y6 + T + 2
    bw = 822
    xm = (c.xi0 + c.xi1) / 2
    bx0 = xm - bw / 2
    yb = fy0 + 22
    zb = c.zp1 - 400
    extra = [{"n": "10", "id": "10-inner", "box": [bx0 + T, yb, zb + T + 183, bx0 + bw - T, yb + 160, zb + 2 * T + 183]}]
    for k in range(3):
        x = bx0 + T + (k + 1) * (790 - 3 * T) / 4 + k * T
        extra.append({"n": "11", "id": f"11-{k + 1}", "box": [round(x, 2), yb, zb + T, round(x + T, 2), yb + 160, zb + T + 183]})
    c.drawer("1", ("7", "8", "9", "10", "12"), c.fx0, c.fx1, fy0, c.S - 2, bw, side_l=400, bottom=[818, 405], extra=extra)
    return c.dump()


def m1_41():
    """П7.050.1.41 Зеркало 900 × 19 × 660 (instruction: one part «рамка с зеркалом»): a frame ≈ 90 wide round the mirror."""
    c = Case("parma-1-41", 900, 660, 19, size=[900, 19, 660])
    c.parts.append({"n": "1", "kind": "front", "box": [0, 0, 0, 900, 660, 19], "edge": 3, "grain": "x",
                    "glass": {"frame": 80, "rebate": 10, "t": 4, "tint": "mirror"}})
    return c.dump()


def wardrobe(did, L, sd, doors, size, mirrors=()):
    """Wardrobes 1.18 / 1.19 (two doors 424) and 1.10-01 (four doors 433): an oak drawer tier (drawers 180 under the
    doors) between the oak bottom and an oak horizontal, the doors above; inside a hat shelf with a rail in the hanging
    bay and shelves in the others (the p. 56 interior sketches)."""
    c = Case(did, L, 2184, sd, td=sd + 34, size=size)
    c.carcass("top", "side-l", "side-r", "pil", "bottom")
    yd = c.yb1 + 2 + 180 + 2
    c.horizontal("h-drawers", c.xi0, c.xi1, yd)
    wd = (c.fx1 - c.fx0 - 2 * (doors - 1)) / doors
    fr = spread(c.fx0, [wd] * doors, 2)
    # partitions behind the door joints: 2 doors → one in the middle; 4 doors → behind 1|2 and 3|4
    joints = [(fr[0][1] + fr[1][0]) / 2] if doors == 2 else [(fr[0][1] + fr[1][0]) / 2, (fr[2][1] + fr[3][0]) / 2]
    bays, x = [], c.xi0
    for k, j in enumerate(joints):
        c.upright(f"part-{k + 1}", j - 8, yd + T, c.S)
        bays.append((x, j - 8))
        x = j + 8
    bays.append((x, c.xi1))
    # the drawer tier: a divider under each door joint
    for k in range(doors - 1):
        j = (fr[k][1] + fr[k + 1][0]) / 2
        c.upright(f"div-{k + 1}", j - 8, c.yb1, yd)
    hang = [len(bays) // 2] if doors == 4 else [0]
    yh = 1880
    for k, (a, b) in enumerate(bays):
        if k in hang:
            c.shelf(f"shelf-{k + 1}h", a, b, yh, sd - 10)
            c.parts.append(rail_tube(f"rail-{k + 1}", a + 3, b - 3, yh - 60, sd / 2))
        else:
            for j, y in enumerate((700, 1000, 1300, 1600, yh)):
                c.shelf(f"shelf-{k + 1}{j + 1}", a + 1, b - 1, y, sd - 10)
    hinges = ["left", "right"] if doors == 2 else ["left", "left", "right", "right"]
    for k, ((fa, fb), hg) in enumerate(zip(fr, hinges)):
        c.door(f"door_{k + 1}", f"door-{k + 1}", fa, fb, yd + T + 2, c.S - 2, hg, 1150,
               glass=MIRROR if k in mirrors else None)
        c.drawer(str(k + 1), ("df", "ds-l", "ds-r", "db", "dd"), fa, fb, c.yb1 + 2, yd - 2,
                 (fb - fa) - 30 - 26, side_h=120, side_l=min(450, sd - 40), bottom=[(fb - fa) - 60, min(450, sd - 40)])
    c.back("back-low", c.xi0 - 10, c.xi1 + 10, YB - 5, yd + 8)
    xs = [c.xi0 - 10] + [j for j in joints] + [c.xi1 + 10]
    for k in range(len(xs) - 1):
        c.back(f"back-{k + 1}", xs[k], xs[k + 1], yd + 8, c.S + 5)
    return c.dump()


def m1_18():
    return wardrobe("parma-1-18", 906, 390, 2, [906, 434, 2200])


def m1_19():
    return wardrobe("parma-1-19", 906, 586, 2, [906, 630, 2200])


def m1_10_01():
    return wardrobe("parma-1-10-01", 1794, 586, 4, [1794, 630, 2200], mirrors=(1, 2))


def bed(did, W, sleep, *, instructed, lift=False):
    """Beds (L2058, H1070): a headboard 25 (W × 1070) on glides with the quilted soft panel 5 (W − 100 × 450) 50 below its
    top, the side rails 3 / 4 (2008 × 220) from the headboard to the footboard 2 (W − 116 × 322) which closes their ends,
    the metal base with slats inside (1.00: with the lifting frame and the bedding box)."""
    L = 2058
    c = Case(did, W, 1070, 25, size=[W, L, 1070])
    n = (lambda k, i: {"n": k}) if instructed else (lambda k, i: {"id": i})
    p = c.parts
    p.append({**n("1", "headboard"), "box": [0, 0, 0, W, 1070, 25], "edge": 2, "grain": "x"})
    cols = round(12 * (W - 100) / 1678)
    p.append({**n("5", "soft"), "kind": "soft", "box": [50, 570, 25, W - 50, 1020, 70], "tufts": [cols, 3]})
    fw = W - 116
    x0, x1 = 58, 58 + fw
    p.append({**n("2", "footboard"), "box": [x0, 0, L - 25, x1, 322, L], "edge": 2, "grain": "x"})
    p.append({**({"n": "3"} if instructed else {"id": "rail-l"}), "box": [x0, 102, 25, x0 + T, 322, L - 25], "grain": "z"})
    p.append({**({"n": "4"} if instructed else {"id": "rail-r"}), "box": [x1 - T, 102, 25, x1, 322, L - 25], "grain": "z"})
    g = (fw - 2 * T - sleep) / 2
    bx0, bx1 = x0 + T + g, x1 - T - g
    bz0, bz1 = 29, 2029
    yt = 300
    p += [{"id": "base-l", "kind": "panel", "mat": "black", "box": [bx0, yt - 40, bz0, bx0 + 40, yt - 8, bz1], "covers": ["A"]},
          {"id": "base-r", "kind": "panel", "mat": "black", "box": [bx1 - 40, yt - 40, bz0, bx1, yt - 8, bz1]},
          {"id": "base-h", "kind": "panel", "mat": "black", "box": [bx0 + 40, yt - 40, bz0, bx1 - 40, yt - 8, bz0 + 40]},
          {"id": "base-f", "kind": "panel", "mat": "black", "box": [bx0 + 40, yt - 40, bz1 - 40, bx1 - 40, yt - 8, bz1]}]
    fields = [(bx0 + 40, bx1 - 40)]
    if bx1 - bx0 > 1200:
        xm = (bx0 + bx1) / 2
        p.append({"id": "base-m", "kind": "panel", "mat": "black", "box": [xm - 20, yt - 40, bz0 + 40, xm + 20, yt - 8, bz1 - 40]})
        fields = [(bx0 + 40, xm - 20), (xm + 20, bx1 - 40)]
    if lift:
        # the bedding box of the lifting base: black walls and a hardboard floor inside the rails
        p += [{"id": "box-floor", "kind": "back", "mat": "black", "box": [bx0, 40, bz0, bx1, 44, bz1]},
              {"id": "box-l", "kind": "panel", "mat": "black", "box": [bx0, 44, bz0, bx0 + 10, yt - 40, bz1]},
              {"id": "box-r", "kind": "panel", "mat": "black", "box": [bx1 - 10, 44, bz0, bx1, yt - 40, bz1]},
              {"id": "box-h", "kind": "panel", "mat": "black", "box": [bx0 + 10, 44, bz0, bx1 - 10, yt - 40, bz0 + 10]},
              {"id": "box-f", "kind": "panel", "mat": "black", "box": [bx0 + 10, 44, bz1 - 10, bx1 - 10, yt - 40, bz1]}]
        legs = [(bx0 + 30, bz0 + 30), (bx1 - 30, bz0 + 30), (bx0 + 30, bz1 - 30), (bx1 - 30, bz1 - 30)]
        leg_top = 40
    else:
        legs = [(bx0 + 20, bz0 + 20), (bx1 - 20, bz0 + 20), (bx0 + 20, bz1 - 20), (bx1 - 20, bz1 - 20),
                ((bx0 + bx1) / 2, (bz0 + bz1) / 2)]
        leg_top = yt - 40
    for k, (x, z) in enumerate(legs):
        p.append({"id": f"base-leg-{k + 1}", "kind": "tube", "mat": "black", "box": [x - 12, 0, z - 12, x + 12, leg_top, z + 12]})
    slats = []
    npitch = 22
    pitch = (bz1 - bz0 - 80) / npitch
    for f, (a, b) in enumerate(fields):
        for i in range(npitch):
            z = bz0 + 40 + pitch * i + (pitch - 53) / 2
            sid = f"slat-{f + 1}-{i + 1}"
            p.append({"id": sid, "kind": "panel", "mat": "door_enamel_whitey#c9a877", "edge": 2,
                      "box": [round(a - 20, 2), yt - 8, round(z, 2), round(b + 20, 2), yt, round(z + 53, 2)]})
            slats.append(sid)
    p.append({"id": "mattress", "kind": "mattress", "box": [bx0, yt, bz0, bx1, yt + 200, bz1]})
    if lift:
        lid = ["base-l", "base-r", "base-h", "base-f"] + (["base-m"] if len(fields) > 1 else []) + slats + ["mattress"]
        c.moves.append({"type": "flap", "name": "lift", "parts": lid, "hinge": "top", "axis": [yt, bz0], "angle": 40})
    return c.dump()


def m1_00():
    return bed("parma-1-00", 1778, 1600, instructed=True, lift=True)


def m1_01():
    return bed("parma-1-01", 1778, 1600, instructed=False)


def m1_02():
    return bed("parma-1-02", 1378, 1200, instructed=False)


# ================================================================================================== catalogue
PROFILES = {
    "parma-bevel": {"name": "Фасад «Парма»: узкий скос рамки к филёнке", "pts": [[0, 0], [0, 3], [1.5, 3], [7, 0.6], [9, 0]]},
}

FINISHES = [
    {"id": "parma-randers-kantri", "name": "Сосна Рандерс / Дуб Кантри золотой", "body": "door_enamel_whitey#d9d9d9",
     "front": "door_enamel_whitey#d9d9d9", "roles": {"top": "door_enamel_whitey#a88059", "fabric": "velvet#cdbfa8"},
     "swatch": "#d9d9d9", "note": "оба декора — текстуры (gen/parma_decors.md); цвета — образцы с. 56"},
]

COLLECTION = {"id": "parma", "name": "Парма", "brand": "Пинскдрев", "finishes": ["parma-randers-kantri"], "metal": "black",
              "note": "Каталог «Корпусная мебель ч. II» 2025, с. 52–56 (100–109 по нумерации каталога); 6 модулей по "
                      "инструкциям (gen/cutlists/parma-*.json), 14 — по каталогу и фото сайта. Боковины ЛДСП 16 до пола "
                      "(ножки), крышка «Дуб Кантри» на боковинах со свесом 10, дно дубовое на 80 над полом, пилястры 44 × 16 "
                      "на кромках боковин, фасады МДФ 18 накладные перед ними (рамка + филёнка), дубовые горизонтали в швах "
                      "фасадов, стеклянные двери, чёрные ручки-кнопки."}

MODELS = []


def index():
    with open(os.path.join(HERE, "..", "reference", "index.json")) as fh:
        return {a["code"]: a for a in json.load(fh) if a.get("slug") == SLUG}


REG = [
    ("parma-0-13", "П7.050.0.13", m0_13, "living", "B434 = боковина 390 + пилястра 44 (каталог B424)"),
    ("parma-0-11", "П7.050.0.11", m0_11, "living", "универсальный, необходимо крепление к стене; как одна секция 0.13"),
    ("parma-0-29", "П7.050.0.29", m0_29, "living", "B434 = боковина 390 + пилястра 44 (каталог B420 — по крышке)"),
    ("parma-0-21", "П7.050.0.21", m0_21, "living", "как 0.29 без правой двери; B434 как у 0.29 (каталог 420 — по крышке)"),
    ("parma-0-22", "П7.050.0.22", m0_22, "living", "B434 как у 0.29 (каталог 420 — по крышке)"),
    ("parma-0-32", "П7.050.0.32", m0_32, "living", "B460 = боковина 416 + пилястра 44 (каталог B450)"),
    ("parma-0-61", "П7.050.0.61", m0_61, "living", "B460 = боковина 416 + пилястра 44 (каталог B450)"),
    ("parma-0-55", "П7.050.0.55", m0_55, "tables", ""),
    ("parma-0-51", "П7.050.0.51", m0_51, "tables", ""),
    ("parma-0-71", "П7.050.0.71", m0_71, "decor", "навесная на кронштейнах"),
    ("parma-1-31", "П7.050.1.31", m1_31, "bedroom", "B460 = боковина 416 + пилястра 44 (каталог B450 — по крышке)"),
    ("parma-1-26", "П7.050.1.26", m1_26, "bedroom", "B460 = боковина 416 + пилястра 44 (каталог B450)"),
    ("parma-1-53", "П7.050.1.53", m1_53, "bedroom", "B516 = боковина 472 + пилястра 44 (каталог B500 — по крышке)"),
    ("parma-1-41", "П7.050.1.41", m1_41, "decor", "навесное"),
    ("parma-1-18", "П7.050.1.18", m1_18, "bedroom", "B434 = боковина 390 + пилястра 44 (каталог B424)"),
    ("parma-1-19", "П7.050.1.19", m1_19, "bedroom", "B630 = боковина 586 + пилястра 44 (каталог B620)"),
    ("parma-1-10-01", "П7.050.1.10-01", m1_10_01, "bedroom", "средние двери с зеркалом; B630 = боковина 586 + пилястра 44 (каталог B620)"),
    ("parma-1-00", "П7.050.1.00", m1_00, "bedroom", "металлокаркас с подъёмным механизмом и нишей для белья"),
    ("parma-1-01", "П7.050.1.01", m1_01, "bedroom", "как 1.00 на металлокаркасе без подъёмного механизма"),
    ("parma-1-02", "П7.050.1.02", m1_02, "bedroom", "как 1.01 шириной 1378"),
]


def nm(name):
    name = name.replace("ШКАФ", "Шкаф")
    return name[0].upper() + name[1:]


def main():
    idx = index()
    for did, code, fn, cat, note in REG:
        a = idx[code]
        path = fn()
        with open(path) as fh:
            size = json.load(fh)["size"]
        is_ = os.path.basename(a["pdf"]) if a.get("pdf") else None
        n = note + ("" if is_ else ("; " if note else "") + "по каталогу, без инструкции")
        m = {"id": did, "code": code, "name": nm(a["name"]), "collection": SLUG, "category": cat, "size": size,
             "page": a["pages"][0]}
        if is_:
            m["is"] = is_
        if n:
            m["note"] = n
        if "навес" in note:
            m["mount"] = "wall"
        MODELS.append(m)
        print(path)
    out = os.path.join(HERE, "parma_catalog.json")
    with open(out, "w") as fh:
        json.dump({"finishes": FINISHES, "profiles": PROFILES, "collections": [COLLECTION], "models": MODELS}, fh,
                  ensure_ascii=False, indent=1)
    print(out)


if __name__ == "__main__":
    main()
