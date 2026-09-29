"""Turin (П7.036.*, «Пинскдрев-Заславль»), a classic collection in «Сосна Карелия» / «Дуб Каньон».

The construction, read off the 22 instructions (tables «№, наименование, A×B, кол.»: two sizes, the thickness is only
marked «T=25» on the 25-mm boards; transcribed into gen/cutlists/turin-*.json), the one orthographic front view
(0.21), the p. 57–63 photos and the close-ups:
* Carcass ЛДСП 16. The bottom («стенка горизонтальная нижняя», T=25) and the top («крышка», T=25) run the full width L0
  (446 / 450 deep, 600 in the wardrobes) with a rounded front edge; the sides stand on the bottom and carry the top, 16
  in from its ends: the inner width is L0 − 64 in every table (0.12: L0 − 62). H = 70 + 25 + sides + 25 (+ cornice).
* The back ДВП 3 is screwed onto the back edges (washers «шайба круглая / прямоугольная»): z 0–3; sides from z 3.
* Pilasters «2040×22» stand on the sides' front edges: 22 wide (flush with the side's inner face, 6 proud of its outer
  face) and 20 deep — the fronts (МДФ 20) sit between them, flush, in front of the carcass (partitions and fixed shelves
  stand behind their joints). This gives the listed depths: side 426 + 20 = 446 = the top of 0.10 / 0.11, side 580 + 20
  = 600 = the wardrobes' top; 450 tops overhang by 4. Fronts: gaps 2 (2.5 where the sizes say so).
* Plinth: a box of 70 mm boards (front / back L0 − 10 or − 12, ends 368 / 372 / 522 between them) under the bottom, its
  front flush with the sides' front edges; the front board's lower edge is cut into a flat arch with scrolls (0.21's
  front view, the photos). Adjustable glides inside it.
* Cornice on the tall pieces, a crown 40 high overhanging ~43: either one board «карниз L×491» (0.11, 0.12: a 12–16 slab
  with a rounded edge over a cove) or three crown strips «карниз передний / боковой … ×86» (a moulding «turin-crown»).
* Fronts: a milled frame (22 flat) and a wide ogee (40) down to the sunk panel (face «frame» + profile «turin-ogee», as
  the 0.21 front view draws them); glazed doors: the frame round clear glass (70 + rebate 10). Handles: antique brass —
  an ornate backplate with an oval knob (p. 62 close-up), vertical on doors, horizontal on drawers.
* Drawers: the facade is the box's front wall (in the front plane), sides / back ЛДСП 16, ДВП bottom under the box, 13 mm
  runner gaps (ball runners 400); «брусок продольный» under the bottom of the wide boxes.

z: back 0–3, sides 3–(3 + side depth), pilasters / fronts the next 20, top / bottom from z 3.
Run: python3 tools/casegoods/gen/turin.py  (writes the designs and gen/turin_catalog.json)
"""
import json
import math
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "turin"

BK = 3            # back ДВП, screwed on
FT = 20           # pilasters and fronts
TT = 25           # top / bottom
PH = 70           # plinth
GAP = 2

DOOR_FACE = {"type": "frame", "border": 22, "depth": 6, "r": 1, "profile": "turin-ogee"}
DRAWER_FACE = {"type": "frame", "border": 20, "depth": 6, "r": 1, "profile": "turin-ogee"}
GLASS = {"frame": 75, "rebate": 10, "t": 4, "tint": "clear"}
MIRROR = {"frame": 75, "rebate": 10, "t": 4, "tint": "mirror"}


def arch(x0, x1, h, rise=30, foot=None):
    """A plinth board's lower edge (front plane, y up from the floor): feet at the ends, a flat arch between scrolls."""
    w = x1 - x0
    f = foot or max(45.0, min(130.0, w * 0.085))
    a0, a1 = x0 + f, x1 - f
    s = min(18.0, f * 0.3)
    return ("M {x0:g} {h:g} L {x1:g} {h:g} L {x1:g} 0 L {a1:g} 0 C {a1c:g} 0 {a1:g} {r3:g} {a1s:g} {r6:g} "
            "C {m1:g} {r:g} {m0:g} {r:g} {a0s:g} {r6:g} C {a0:g} {r3:g} {a0c:g} 0 {a0:g} 0 L {x0:g} 0 Z").format(
        x0=x0, x1=x1, h=h, a0=a0, a1=a1, a1c=a1 - s * 0.4, a0c=a0 + s * 0.4, a1s=a1 - s, a0s=a0 + s,
        r=rise, r3=rise * 0.3, r6=rise * 0.62, m1=a1 - w * 0.2, m0=a0 + w * 0.2)


class Case:
    """A Turin carcass. L0 = the top's width, S = the sides' height, sd = the sides' depth, cx = the x of the top's left
    end (the cornice's overhang), y0 = the bottom's underside."""

    def __init__(self, did, L0, S, *, sd=426, td=450, bd=None, ov=16, cx=0, y0=PH, size=None):
        self.did, self.L0, self.S, self.sd, self.td, self.bd = did, L0, S, sd, td, bd or td
        self.cx, self.ov, self.y0 = cx, ov, y0
        self.ys0 = y0 + TT
        self.ys1 = self.ys0 + S
        self.xl = cx + ov                # the left side's outer face
        self.xr = cx + L0 - ov           # the right side's outer face
        self.xi0, self.xi1 = self.xl + 16, self.xr - 16
        self.zs1 = BK + sd               # the sides' front edge
        self.zf1 = self.zs1 + FT         # the fronts' face
        self.parts, self.moves = [], []
        self.size = size

    # ------------------------------------------------------------------ carcass
    def add(self, *ps):
        self.parts += ps
        return ps[-1] if ps else None

    def P(self, n, box, pid=None, **kw):
        p = {"n": n, "box": [round(v, 2) for v in box], **kw}
        if pid:
            p["id"] = pid
        return self.add(p)

    def bottom(self, n):
        return self.P(n, [self.cx, self.y0, BK, self.cx + self.L0, self.ys0, BK + self.bd], edge=5, grain="x")

    def top(self, n, y=None, td=None, z0=BK):
        y = self.ys1 if y is None else y
        return self.P(n, [self.cx, y, z0, self.cx + self.L0, y + TT, z0 + (td or self.td)], edge=5, grain="x")

    def sides(self, nl, nr, y0=None, y1=None, ids=(None, None)):
        y0 = self.ys0 if y0 is None else y0
        y1 = self.ys1 if y1 is None else y1
        self.P(nl, [self.xl, y0, BK, self.xl + 16, y1, self.zs1], ids[0], grain="y")
        self.P(nr, [self.xr - 16, y0, BK, self.xr, y1, self.zs1], ids[1], grain="y")

    def pilasters(self, nl, nr, y0=None, y1=None, ids=(None, None)):
        y0 = self.ys0 if y0 is None else y0
        y1 = self.ys1 if y1 is None else y1
        self.P(nl, [self.xl - 6, y0, self.zs1, self.xl + 16, y1, self.zf1], ids[0] or (f"{nl}-l" if nl == nr else None),
               mat="front", edge=2, grain="y")
        self.P(nr, [self.xr - 16, y0, self.zs1, self.xr + 6, y1, self.zf1], ids[1] or (f"{nr}-r" if nl == nr else None),
               mat="front", edge=2, grain="y")

    def upright(self, n, x0, y0=None, y1=None, pid=None, z0=BK, z1=None):
        """A partition 16 thick with its left face at x0."""
        y0 = self.ys0 if y0 is None else y0
        y1 = self.ys1 if y1 is None else y1
        return self.P(n, [x0, y0, z0, x0 + 16, y1, z1 or self.zs1], pid, grain="y")

    def shelf(self, n, x0, x1, y, depth=None, pid=None, z1=None, t=16):
        z1 = z1 or self.zs1 - 1
        depth = depth or (z1 - BK)
        return self.P(n, [x0, y, z1 - depth, x1, y + t, z1], pid)

    def glass_shelf(self, n, x0, x1, y, depth=416, pid=None, led=True):
        z1 = self.zs1 - 4
        p = {"n": n, "kind": "glass", "box": [x0, y, z1 - depth, x1, y + 5, z1]}
        if pid:
            p["id"] = pid
        self.add(p)
        if led:
            xm = (x0 + x1) / 2
            self.add({"id": f"led-{pid or n}", "kind": "light", "box": [xm - 20, y - 7, z1 - 16, xm + 20, y, z1 - 4]})

    def plinth(self, nf, nl, nr, nb, flen, slen, ids=(None, None, None, None)):
        x0 = self.cx + (self.L0 - flen) / 2
        x1 = x0 + flen
        z1 = self.zs1
        z0 = z1 - slen - 32
        self.P(nf, [x0, 0, z1 - 16, x1, PH, z1], ids[0], grain="x", shape="path", outline=arch(x0, x1, PH))
        self.P(nl, [x0, 0, z0 + 16, x0 + 16, PH, z1 - 16], ids[1])
        self.P(nr, [x1 - 16, 0, z0 + 16, x1, PH, z1 - 16], ids[2])
        self.P(nb, [x0, 0, z0, x1, PH, z0 + 16], ids[3], grain="x")

    def back(self, n, x0, x1, y0, y1, pid=None):
        return self.P(n, [x0, y0, 0, x1, y1, BK], pid, kind="back")

    # ------------------------------------------------------------------ cornices
    def cornice_board(self, n, L, depth, y, slab=16, z0=BK):
        """«Карниз» as one board L × depth: a slab with a rounded edge over a cove moulding (24) on the top."""
        cove = 24
        self.P(n, [0, y + cove, z0, L, y + cove + slab, z0 + depth], edge=5, grain="x", mat="front")
        pr = cove + 8
        ox = self.cx - pr
        self.add({"id": "cornice-cove", "kind": "moulding", "profile": f"turin-cove-{cove}", "plane": "top", "z": y,
                  "side": -1, "mat": "front",
                  "path": [[ox, BK], [ox, BK + self.td + pr], [self.cx + self.L0 + pr, BK + self.td + pr],
                           [self.cx + self.L0 + pr, BK]]})

    def cornice_strips(self, covers, L, depth, y, z0=0, h=40):
        """The crown strips round the top: the moulding's outer edge is the cornice's outline (L × depth from z0)."""
        self.add({"id": "cornice", "kind": "moulding", "profile": f"turin-crown-{h}", "plane": "top", "z": y + h - 16,
                  "side": -1, "mat": "front", "covers": covers,
                  "path": [[0, z0], [0, z0 + depth], [L, z0 + depth], [L, z0]]})

    # ------------------------------------------------------------------ fronts
    def front(self, n, x0, x1, y0, y1, pid=None, glass=None, face=None, grain="y"):
        p = {"n": n, "kind": "front", "box": [round(v, 2) for v in (x0, y0, self.zs1, x1, y1, self.zf1)], "edge": 2,
             "grain": grain}
        if pid:
            p["id"] = pid
        if glass:
            p["glass"] = dict(glass)
        else:
            p["face"] = dict(face or DOOR_FACE)
        self.add(p)
        return p.get("id", n)

    def handle(self, hid, x, y, vertical=True):
        """Antique brass: an ornate backplate 110 × 16 with an oval knob in its middle (p. 62 close-up)."""
        z = self.zf1
        self.add({"id": f"{hid}-plate", "kind": "handle", "model": "bar", "at": [round(x, 2), round(y, 2)],
                  "dir": "up" if vertical else "right", "d": 110, "band": 16, "t": 2, "standoff": 0.5, "post": 3, "z": z},
                 {"id": f"{hid}-knob", "kind": "handle", "model": "knob", "at": [round(x, 2), round(y, 2)], "d": 24, "t": 11,
                  "standoff": 13, "z": z})
        return [f"{hid}-plate", f"{hid}-knob"]

    def door(self, name, n, x0, x1, y0, y1, hinge, hy, pid=None, glass=None, hx=None, angle=105):
        fid = self.front(n, x0, x1, y0, y1, pid, glass)
        if hx is None:
            hx = x1 - 30 if hinge == "left" else x0 + 30
        hs = self.handle(f"k-{name}", hx, hy)
        self.moves.append({"type": "door", "name": name, "parts": [fid] + hs, "hinge": hinge, "angle": angle})
        return fid

    def drawer(self, tag, ns, fx0, fx1, fy0, fy1, box_w, side_h, *, side_l=400, bottom=None, bar=None, handle=True,
               extra=(), hy=None):
        """The facade ns[0] is the box's front wall (in the front plane); sides ns[1], ns[2] (side_l × side_h) and the
        back ns[3] behind it, box_w wide, centred; the ДВП bottom ns[4] (bottom = [w, l]) under the box; bar = the
        «брусок продольный» n under the bottom (400 × bw)."""
        nf, nl, nr, nb, nd = ns
        xm = (fx0 + fx1) / 2
        bx0, bx1 = xm - box_w / 2, xm + box_w / 2
        yb = fy0 + 18
        z1 = self.zs1
        z0 = z1 - side_l
        ids = [f"{nf}-{tag}", f"{nl}-{tag}", f"{nr}-{tag}", f"{nb}-{tag}", f"{nd}-{tag}"]
        self.front(nf, fx0, fx1, fy0, fy1, ids[0], face=DRAWER_FACE, grain="x")
        self.P(nl, [bx0, yb, z0, bx0 + 16, yb + side_h, z1], ids[1])
        self.P(nr, [bx1 - 16, yb, z0, bx1, yb + side_h, z1], ids[2])
        self.P(nb, [bx0 + 16, yb, z0, bx1 - 16, yb + side_h, z0 + 16], ids[3])
        bw, bl = bottom
        self.P(nd, [xm - bw / 2, yb - 3, z1 + 5 - bl, xm + bw / 2, yb, z1 + 5], ids[4], kind="back")
        parts = list(ids)
        if bar:
            n_bar, w_bar = bar
            parts.append(self.P(n_bar, [xm - w_bar / 2, yb - 19, z1 - 400, xm + w_bar / 2, yb - 3, z1], f"{n_bar}-{tag}")["id"])
        for e in extra:
            self.add(e)
            parts.append(e["id"])
        if handle:
            parts += self.handle(f"k-{tag}", xm, hy or (fy0 + fy1) / 2, vertical=False)
        self.moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": parts, "travel": int(side_l * 0.85)})
        return parts

    def dump(self):
        return dump(self.did, self.size, self.parts, self.moves)


def rrail(c, n, x0, x1, y1, h, pid=None, z0=BK):
    """A rail on edge against the back (z0 … z0 + 16), h high, its top at y1."""
    return c.P(n, [x0, y1 - h, z0, x1, y1, z0 + 16], pid, grain="x")


def frail(c, n, x0, x1, y0, h, pid=None):
    """A rail on edge behind the fronts (a «брусок» under a drawer / a door stop), h high, its bottom at y0."""
    return c.P(n, [x0, y0, c.zs1 - 16, x1, y0 + h, c.zs1], pid, grain="x")


def spread(x0, x1, widths, gap):
    """Fronts of the given widths from x0 with `gap` between them; returns [(a, b), …]."""
    out, x = [], x0
    for w in widths:
        out.append((x, x + w))
        x += w + gap
    return out


def ys_stack(y0, heights, gap):
    out, y = [], y0
    for h in heights:
        out.append((y, y + h))
        y += h + gap
    return out


def rod_rail(pid, x0, x1, y, z, covers=None):
    p = {"id": pid, "kind": "tube", "mat": "chrome", "box": [x0, y - 12.5, z - 12.5, x1, y + 12.5, z + 12.5]}
    if covers:
        p["covers"] = covers
    return p


# ================================================================================================== living room
def m0_12():
    """П7.036.0.12 Шкаф (универсальный) 710 × 494 × 2200: a glazed door over a panel door, a fixed shelf at their joint,
    2 glass shelves with LED clips above, 2 board shelves below; cornice board 710 × 491 (overhang 40)."""
    c = Case("turin-0-12", 630, 2040, cx=40, ov=15, size=[710, 494, 2200])
    c.bottom("4")
    c.sides("2", "3")
    c.top("1")
    c.pilasters("15", "16")
    x0, x1 = c.xi0, c.xi1                                  # 568
    ys = c.ys0 + 2 + 700 + 1                               # the doors' joint
    c.shelf("5", x0, x1, ys - 8, depth=426, z1=c.zs1)
    for k, y in enumerate((c.ys0 + 230, c.ys0 + 470)):
        c.shelf("6", x0 + 2, x1 - 2, y, depth=416, pid=f"6-{k + 1}", z1=c.zs1 - 4)
    for k, y in enumerate((1250, 1690)):
        c.glass_shelf("7", x0 + 1, x1 - 1, y, pid=f"7-{k + 1}")
    c.plinth("8", "9", "10", "11", 620, 368)
    c.cornice_board("12", 710, 491, c.ys1 + TT, slab=16)
    c.door("door_bottom", "14", x0 + 2, x1 - 2, c.ys0 + 2, c.ys0 + 702, "left", 470)
    c.door("door_top", "13", x0 + 2, x1 - 2, c.ys0 + 704, c.ys1 - 2, "left", 1470, glass=GLASS)
    xb0 = (c.xl + c.xr) / 2 - 298
    c.back("18", xb0, xb0 + 596, c.y0 + 3, ys, "18")
    c.back("17", xb0, xb0 + 596, ys, ys + 1359, "17")
    return c.dump()


def lower_2_3(c, secs, ns, *, top_n, top_td, bars, shelves, door_h=476, drawer_h=199, hinge=None,
              drawers=True, top_z0=BK):
    """The lower cupboard of 0.10 / 0.11 / 0.23 / 0.24: sections `secs` (inner widths) between sides and partitions (681
    high), each a drawer (199) over a door (476); fronts 425 wide overlaying the partitions; a loose shelf per section."""
    n = ns
    c.bottom(n["bottom"])
    c.sides(n["left"], n["right"])
    xs, x = [], c.xi0
    for k, w in enumerate(secs):
        xs.append((x, x + w))
        x += w
        if k < len(secs) - 1:
            c.upright(n["parts"][k], x, pid=None)
            x += 16
    c.pilasters(n["pil"], n["pil"])
    c.top(top_n, td=top_td, z0=top_z0)
    wf = 425
    g = (c.xi1 - c.xi0 - wf * len(secs)) / (len(secs) + 1)
    fr = spread(c.xi0 + g, c.xi1, [wf] * len(secs), g)
    yd0, yd1 = c.ys0 + 2, c.ys0 + 2 + door_h
    yr0, yr1 = yd1 + 2, yd1 + 2 + drawer_h
    for k, ((a, b), (fa, fb)) in enumerate(zip(xs, fr)):
        side = "left" if k == 0 else "right" if k == len(secs) - 1 else "mid"
        # «брусок» 70: flat behind the joint of the drawer and the door (the thick joint line of the 0.10 / 0.11 fronts)
        bn, bl = bars[k]
        c.P(bn, [a, yd1 - 15, c.zs1 - 70, b, yd1 + 1, c.zs1], f"{bn}-{k + 1}" if bars.count(bars[k]) > 1 else None, grain="x")
        sn, sw, sd_ = shelves[k]
        c.shelf(sn, (a + b - sw) / 2, (a + b + sw) / 2, c.ys0 + 250, depth=sd_, pid=f"{sn}-{k + 1}" if [s[0] for s in shelves].count(sn) > 1 else None,
                z1=c.zs1 - 2)
        hg = (hinge or {}).get(k) or ("left" if k == 0 else "right" if k == len(secs) - 1 else "left")
        dn = n["door"]
        c.door(f"door_{k + 1}", dn, fa, fb, yd0, yd1, hg, (yd0 + yd1) / 2, pid=f"{dn}-{k + 1}")
        if drawers:
            dr = n["drawers"][k]
            box_w = dr["box"]
            c.drawer(str(k + 1), dr["ns"], fa, fb, yr0, yr1, box_w, 150, bottom=dr["bottom"])
    return xs, fr


def m0_10():
    """П7.036.0.10 Шкаф 2д 1002 × 491 × 2200: a two-section cupboard (drawer over door, 681) with a two-door glazed showcase
    (1338) on its top; crown strips 1002 / 491 (overhang 41). Tops 25 → the crown is 36 high."""
    c = Case("turin-0-10", 920, 681, td=446, bd=446, cx=41, size=[1002, 491, 2200])
    names = {"bottom": "2", "left": "3", "right": "4", "parts": ["5"], "pil": "17", "door": "16",
             "drawers": [{"ns": ("7", "9", "10", "11", "18"), "box": 394, "bottom": [392, 405]},
                         {"ns": ("8", "9", "10", "11", "18"), "box": 394, "bottom": [392, 405]}]}
    xs, fr = lower_2_3(c, [420, 420], names, top_n="1", top_td=446, bars=[("15", 420), ("15", 420)],
                       shelves=[("6", 418, 416), ("6", 418, 416)])
    # the drawer parts share numbers 9/10/11/18: give them ids per drawer (done by the drawer tag)
    xb = (c.xl + c.xr) / 2
    yj = c.y0 + 8 + 714                                    # the backs' joint, behind top 1
    c.back("19", xb - 441, xb, yj - 714, yj, "19-1")
    c.back("19", xb, xb + 441, yj - 714, yj, "19-2")
    # the showcase on top 1
    u0 = c.ys1 + TT
    u1 = u0 + 1338
    c.sides("20", "21", u0, u1)
    c.upright("22", xs[0][1], u0, u1)
    c.pilasters("23", "23", u0, u1)
    c.top("26", u1, td=446)
    for k, (a, b) in enumerate(xs):
        for j, y in enumerate((u0 + 440, u0 + 880)):
            c.glass_shelf("24", a + 1, b - 1, y, pid=f"24-{k + 1}{j + 1}")
    for k, ((fa, fb), hg) in enumerate(zip(fr, ("left", "right"))):
        c.door(f"door_top_{k + 1}", "27", fa, fb, u0 + 2, u1 - 2, hg, u0 + 640, pid=f"27-{k + 1}", glass=GLASS)
    c.back("28", xb - 441, xb, yj, yj + 1373, "28-1")
    c.back("28", xb, xb + 441, yj, yj + 1373, "28-2")
    c.plinth("12", "13", "13", "14", 908, 368, ids=(None, "13-l", "13-r", None))
    c.cornice_strips(["25а", "25б", "25б"], 1002, 491, u1 + TT, z0=0, h=36)
    return c.dump()



def names_3(pil, door, top_ok=True):
    return {"bottom": "2", "left": "3", "right": "4", "parts": ["5", "6"], "pil": pil, "door": door,
            "drawers": [{"ns": ("13", "10", "11", "15", "25"), "box": 395, "bottom": [391, 405]},
                        {"ns": ("9", "10", "11", "12", "24"), "box": 385, "bottom": [381, 405]},
                        {"ns": ("14", "10", "11", "15", "25"), "box": 395, "bottom": [391, 405]}]}


def backs_row(c, specs, y0, h):
    """Back panels side by side, centred on the carcass: specs = [(n, w, id), …]."""
    total = sum(w for _, w, _ in specs)
    x = (c.xl + c.xr) / 2 - total / 2
    for n, w, pid in specs:
        c.back(n, x, x + w, y0, y0 + h, pid)
        x += w


def m0_11():
    """П7.036.0.11 Шкаф 3д 1431 × 491 × 2200: a three-section cupboard (drawer over door) with a three-door glazed
    showcase on its top 1; cornice board 1431 × 491 (a 12 slab over the cove: tops 25 → 36)."""
    c = Case("turin-0-11", 1349, 681, td=446, cx=41, size=[1431, 491, 2200])
    xs, fr = lower_2_3(c, [421, 411, 421], names_3("23", "22"), top_n="1", top_td=446,
                       bars=[("20", 421), ("21", 411), ("20", 421)],
                       shelves=[("7", 417, 415), ("8", 407, 415), ("7", 417, 415)])
    yj = c.y0 + 8 + 714
    backs_row(c, [("26", 441, "26-1"), ("27", 427, None), ("26", 441, "26-2")], yj - 714, 714)
    u0 = c.ys1 + TT
    u1 = u0 + 1338
    c.sides("29", "30", u0, u1)
    c.upright("31", xs[0][1], u0, u1)
    c.upright("32", xs[1][1], u0, u1)
    c.pilasters("34", "34", u0, u1)
    c.top("28", u1, td=446)
    for k, (a, b) in enumerate(xs):
        for j, y in enumerate((u0 + 440, u0 + 880)):
            if k == 1:
                c.glass_shelf("37", a + 2, b - 2, y, pid=f"37-{j + 1}")
            else:
                c.glass_shelf("36", a + 1.5, b - 1.5, y, pid=f"36-{k + 1}{j + 1}")
    for k, ((fa, fb), hg) in enumerate(zip(fr, ("left", "left", "right"))):
        c.door(f"door_top_{k + 1}", "33", fa, fb, u0 + 2, u1 - 2, hg, u0 + 640, pid=f"33-{k + 1}", glass=GLASS)
    backs_row(c, [("38", 441, "38-1"), ("39", 427, None), ("38", 441, "38-2")], yj, 1373)
    c.plinth("16", "17", "18", "19", 1339, 368)
    c.cornice_board("35", 1431, 491, u1 + TT, slab=12, z0=0)
    return c.dump()


def m0_24():
    """П7.036.0.24 Тумба 3д 1349 × 450 × 801: the lower part of 0.11 under its own top 1349 × 450."""
    c = Case("turin-0-24", 1349, 681, td=450, bd=446, size=[1349, 450, 801])
    lower_2_3(c, [421, 411, 421], names_3("23", "22"), top_n="1", top_td=450, top_z0=0,
              bars=[("20", 421), ("21", 411), ("20", 421)],
              shelves=[("7", 417, 415), ("8", 407, 415), ("7", 417, 415)])
    backs_row(c, [("26", 441, "26-1"), ("27", 427, None), ("26", 441, "26-2")], c.y0 + 14, 702)
    c.plinth("16", "17", "18", "19", 1339, 368)
    return c.dump()


def m0_23():
    """П7.036.0.23 Тумба 2д 920 × 450 × 801 (by catalogue, p. 62 cut-out): the lower part of 0.10 (two sections of 420,
    a drawer over a door each) under a top 920 × 450 — the numbers of 0.10 are kept as labels."""
    c = Case("turin-0-23", 920, 681, td=450, bd=446, size=[920, 450, 801])
    names = {"bottom": "2", "left": "3", "right": "4", "parts": ["5"], "pil": "17", "door": "16",
             "drawers": [{"ns": ("7", "9", "10", "11", "18"), "box": 394, "bottom": [392, 405]},
                         {"ns": ("8", "9", "10", "11", "18"), "box": 394, "bottom": [392, 405]}]}
    lower_2_3(c, [420, 420], names, top_n="1", top_td=450, top_z0=0, bars=[("15", 420), ("15", 420)],
              shelves=[("6", 418, 416), ("6", 418, 416)])
    backs_row(c, [("19", 441, "19-1"), ("19", 441, "19-2")], c.y0 + 14, 702)
    c.plinth("12", "13", "13", "14", 908, 368, ids=(None, "13-l", "13-r", None))
    return c.dump()


def m0_26():
    """П7.036.0.26 Тумба 1500 × 450 × 1200 (подсветка): glazed side doors (2 glass shelves, LED clips) round a centre
    section with a drawer over a door and a loose shelf; rails 10 / 11 on the bottom behind the fronts."""
    c = Case("turin-0-26", 1500, 1080, td=450, bd=446, size=[1500, 450, 1200])
    c.bottom("4")
    c.sides("2", "3")
    x5 = c.xi0 + 471
    x6 = x5 + 16 + 462
    c.upright("5", x5)
    c.upright("6", x6)
    c.pilasters("19", "19")
    c.top("1", z0=0)
    secs = [(c.xi0, x5), (x5 + 16, x6), (x6 + 16, c.xi1)]
    fr = spread(c.xi0 + 2, c.xi1, [476, 476, 476], 2)
    frail(c, "10", *secs[0], c.ys0, 70, "10-1")
    frail(c, "11", *secs[1], c.ys0, 70)
    frail(c, "10", *secs[2], c.ys0, 70, "10-2")
    a, b = secs[1]
    yd1 = c.ys0 + 3 + 820
    c.shelf("7", a, b, yd1 - 20, depth=425, z1=c.zs1)
    c.shelf("8", a + 1, b - 1, c.ys0 + 420, depth=416, z1=c.zs1 - 4)
    for k in (0, 2):
        a, b = secs[k]
        for j, y in enumerate((c.ys0 + 360, c.ys0 + 720)):
            c.glass_shelf("9", a + 1, b - 1, y, pid=f"9-{k + 1}{j + 1}")
    c.door("door_left", "17", *fr[0], c.ys0 + 3, c.ys1 - 3, "left", 620, pid="17-1", glass=GLASS)
    c.door("door_right", "17", *fr[2], c.ys0 + 3, c.ys1 - 3, "right", 620, pid="17-2", glass=GLASS)
    c.door("door_mid", "18", *fr[1], c.ys0 + 3, yd1, "left", yd1 - 110)
    c.drawer("1", ("12", "13", "14", "15", "16"), *fr[1], yd1 + 3, c.ys1 - 3, 436, 200, bottom=[434, 405])
    backs_row(c, [("23", 493, "23-1"), ("24", 476, None), ("23", 493, "23-2")], c.y0 + 13, 1103)
    c.plinth("20", "22", "22", "21", 1490, 368, ids=(None, "22-l", "22-r", None))
    return c.dump()


def m0_21():
    """П7.036.0.21 Тумба ТВ 1500 × 454 × 600 (подсветка): glazed doors (a glass shelf each) round a centre with an open
    niche over a drawer; rear rails 17 / 18 under the top. Checked against the instruction's front view."""
    c = Case("turin-0-21", 1500, 480, td=450, ov=15, size=[1500, 454, 600])
    c.bottom("4")
    c.sides("2", "3")
    x5 = c.xi0 + 420
    x6 = x5 + 16 + 566
    c.upright("5", x5)
    c.upright("6", x6)
    c.pilasters("21", "22")
    c.top("1")
    secs = [(c.xi0, x5), (x5 + 16, x6), (x6 + 16, c.xi1)]
    fr = spread(c.xi0 + 1.5, c.xi1, [425, 580, 425], 1.5)
    rrail(c, "17", *secs[0], c.ys1, 80, "17-1")
    rrail(c, "18", *secs[1], c.ys1, 80)
    rrail(c, "17", *secs[2], c.ys1, 80, "17-2")
    for k in (0, 2):
        c.glass_shelf("8", secs[k][0] + 1, secs[k][1] - 1, c.ys0 + 225, pid=f"8-{k + 1}")
    ydr = c.ys0 + 2 + 269
    c.shelf("7", *secs[1], ydr + 2, depth=426, z1=c.zs1)
    c.door("door_left", "19", *fr[0], c.ys0 + 2, c.ys1 - 2, "left", 338, glass=GLASS)
    c.door("door_right", "20", *fr[2], c.ys0 + 2, c.ys1 - 2, "right", 338, glass=GLASS)
    c.drawer("1", ("9", "10", "11", "12", "23"), *fr[1], c.ys0 + 2, ydr, 540, 220, bottom=[538, 405], hy=ydr - 40)
    xb = (c.xl + c.xr) / 2
    c.back("24", c.xl + 2, c.xl + 443, c.y0 + 13, c.y0 + 516, "24-1")
    c.back("24", c.xr - 443, c.xr - 2, c.y0 + 13, c.y0 + 516, "24-2")
    c.back("26", xb - 290, xb + 290, c.y0 + 13, c.y0 + 307)
    c.back("25", xb - 290, xb + 290, c.y0 + 307, c.y0 + 514)
    c.plinth("13", "14", "15", "16", 1490, 368)
    return c.dump()


def m0_70():
    """П7.036.0.70 Полка 764 × 198 × 25 (by catalogue, p. 57 / 60 photos): a 25 board with a rounded front edge on hidden
    shelf pins (none show)."""
    c = Case("turin-0-70", 764, 0, y0=0, size=[764, 198, 25])
    c.parts.append({"id": "shelf", "box": [0, 0, 0, 764, 25, 198], "edge": 5, "grain": "x"})
    return c.dump()



def m0_52():
    """П7.036.0.52 Стол журнальный 779 × 693 × 475: a top 25 — an equilateral triangle of side 800 with its corners cut
    (778.34 × 692.82 as listed; the long edge at the front) — on three walls 450 × 274 standing along the edges of a
    triangular shelf (side 542) about a quarter up: the walls' inner faces take the shelf's edges (Direkta), the shelf's
    corners stand out between them (the p. 62 cut-out: the front wall face-on, the back-left one edge-on)."""
    c = Case("turin-0-52", 778.34, 0, y0=0, size=[778.34, 692.82, 475])
    W, D = 778.34, 692.82
    a = 21.66                                  # the corner cut along the edges
    h = a * math.sqrt(3) / 2
    xm = W / 2
    top = [(a / 2, D), (W - a / 2, D), (W, D - h), (xm + a / 2, h), (xm - a / 2, h), (0, D - h)]
    c.parts.append({"n": "1", "box": [0, 450, 0, W, 475, D], "edge": 4, "grain": "x", "shape": "path",
                    "outline": "M " + " L ".join(f"{x:.2f} {z:.2f}" for x, z in top) + " Z"})
    cz = D * 2 / 3                             # the centroid
    r = 542 / (2 * math.sqrt(3))               # the shelf's inradius
    tri = [(xm, cz - 2 * r), (xm + 271, cz + r), (xm - 271, cz + r)]
    ys = 104
    c.parts.append({"n": "3", "box": [round(xm - 271, 2), ys, round(cz - 2 * r, 2), round(xm + 271, 2), ys + 16, round(cz + r, 2)],
                    "grain": "x", "shape": "path", "outline": "M " + " L ".join(f"{x:.2f} {z:.2f}" for x, z in tri) + " Z"})
    rc = r + 8
    c.parts.append({"n": "2", "id": "2-front", "box": [round(xm - 137, 2), 0, round(cz + r, 2), round(xm + 137, 2), 450, round(cz + r + 16, 2)],
                    "grain": "y"})
    # the slanted walls: a board 16 × 450 swept along its inner face (the shelf's edge), 274 long, centred on the edge
    for tag, (bx, bz), side in (("left", tri[2], -1), ("right", tri[1], 1)):
        ax, az = tri[0]
        L = math.hypot(ax - bx, az - bz)
        ux, uz = (ax - bx) / L, (az - bz) / L
        mx, mz = (ax + bx) / 2, (az + bz) / 2
        c.parts.append({"id": f"2-{tag}", "kind": "moulding", "profile": "turin-wall-450", "plane": "top", "z": 0,
                        "side": side, "mat": "body", "covers": ["2"],
                        "path": [[round(mx - ux * 137, 2), round(mz - uz * 137, 2)], [round(mx + ux * 137, 2), round(mz + uz * 137, 2)]]})
    return c.dump()


def m4_54():
    """П7.036.4.54 Стол обеденный 820 × 870 × 750: a top 820 × 870 × 25 on four L-shaped corner legs (two boards 725 × 100
    × 25 each: 1 + 2 at the front-left / back-right, 3 + 4 at the other two), an apron of 120 rails inside them
    (6: 720 along the depth, 7: 634 across between them), the legs screwed onto its corners."""
    c = Case("turin-4-54", 820, 0, y0=0, size=[820, 870, 750])
    L, B, t = 820, 870, 25
    c.parts.append({"n": "5", "box": [0, 725, 0, L, 750, B], "edge": 4, "grain": "z"})
    ax0, ax1 = (L - 666) / 2, (L + 666) / 2
    az0, az1 = (B - 720) / 2, (B + 720) / 2
    y0, y1 = 605, 725
    c.parts += [{"n": "6", "id": "6-l", "box": [ax0, y0, az0, ax0 + 16, y1, az1]},
                {"n": "6", "id": "6-r", "box": [ax1 - 16, y0, az0, ax1, y1, az1]},
                {"n": "7", "id": "7-b", "box": [ax0 + 16, y0, az0, ax1 - 16, y1, az0 + 16], "grain": "x"},
                {"n": "7", "id": "7-f", "box": [ax0 + 16, y0, az1 - 16, ax1 - 16, y1, az1], "grain": "x"}]
    corners = [("fl", -1, 1, ("1", "2")), ("fr", 1, 1, ("3", "4")), ("bl", -1, -1, ("3", "4")), ("br", 1, -1, ("1", "2"))]
    for tag, sx, sz, (na, nb) in corners:
        xo = ax0 - t if sx < 0 else ax1 + t          # the leg's outer corner
        zo = az1 + t if sz > 0 else az0 - t
        # board a: on the front / back face (along x); board b: on the side face (along z)
        ax = sorted([xo, xo - sx * 100])
        azz = sorted([zo, zo - sz * t])
        bx = sorted([xo, xo - sx * t])
        bz = sorted([zo - sz * t, zo - sz * (t + 100)])
        c.parts.append({"n": na, "id": f"{na}-{tag}", "box": [ax[0], 0, azz[0], ax[1], 725, azz[1]], "grain": "y"})
        c.parts.append({"n": nb, "id": f"{nb}-{tag}", "box": [bx[0], 0, bz[0], bx[1], 725, bz[1]], "grain": "y"})
    return c.dump()


def m2_14():
    """П7.036.2.14 Шкаф для книг 710 × 494 × 2200: open shelves above a door compartment (door 700, a lid 5 over it);
    crown strips 710 / 490 × 80."""
    c = Case("turin-2-14", 630, 2040, cx=40, ov=15, size=[710, 494, 2200])
    c.bottom("4")
    c.sides("2", "3")
    c.top("1")
    c.pilasters("14", "14", ids=("14-l", "14-r"))
    x0, x1 = c.xi0, c.xi1
    yd1 = c.ys0 + 2 + 700
    c.shelf("5", x0, x1, yd1 + 2, depth=425, z1=c.zs1 - 1)
    c.shelf("6", x0 + 1.5, x1 - 1.5, c.ys0 + 330, depth=410, pid="6-1", z1=c.zs1 - 6)
    for k, y in enumerate((1080, 1650, 1900)):
        c.shelf("6", x0 + 1.5, x1 - 1.5, y, depth=410, pid=f"6-{k + 2}", z1=c.zs1 - 6)
    c.shelf("15", x0, x1, 1370, depth=410, z1=c.zs1 - 6)
    c.door("door", "7", x0 + 2, x1 - 2, c.ys0 + 2, yd1, "left", 640)
    xb = (c.xl + c.xr) / 2
    c.back("17", xb - 298.5, xb + 298.5, c.y0 + 11, c.y0 + 729)
    c.back("16", xb - 298.5, xb + 298.5, c.y0 + 729, c.y0 + 729 + 1368)
    c.plinth("8", "10", "10", "9", 620, 372, ids=(None, "10-l", "10-r", None))
    c.cornice_strips(["11", "12", "13"], 710, 490, c.ys1 + TT, z0=4, h=40)
    return c.dump()


def m3_22():
    """П7.036.3.22 Тумба для обуви 670 × 460 × 440: a flap door (hinged at the bottom on two K-16, oil stays) under a front
    rail 11, a rear rail 5, and an upholstered lid 670 × 460 (a 4 × 2 buttoned pad) on top."""
    c = Case("turin-3-22", 660, 320, td=446, cx=5, size=[670, 460, 440])
    c.bottom("4")
    c.sides("2", "3")
    c.pilasters("10", "10")
    x0, x1 = c.xi0, c.xi1
    frail(c, "11", x0, x1, c.ys1 - 100, 100)
    rrail(c, "5", x0, x1, c.ys1, 70)
    c.parts.append({"n": "1", "kind": "soft", "box": [0, c.ys1, 0, 670, c.ys1 + 25, 460], "tufts": [4, 2]})
    fid = c.front("9", x0 + 2, x1 - 2, c.ys0 + 2, c.ys1 - 2, grain="x")
    hs = c.handle("k-flap", (x0 + x1) / 2, c.ys1 - 45, vertical=False)
    c.moves.append({"type": "flap", "name": "flap", "parts": [fid] + hs, "hinge": "bottom", "angle": 90})
    xb = (c.xl + c.xr) / 2
    c.back("12", xb - 312.5, xb + 312.5, c.y0 + 3, c.y0 + 345)
    c.plinth("6", "8", "8", "7", 650, 368, ids=(None, "8-l", "8-r", None))
    return c.dump()


def m3_92():
    """П7.036.3.92 Вешалка 746 × 139 × 1460 (on the wall): a panel 660 × 1418 with a board 658 × 80 × 25 on its top edge,
    crown strips 746 / 139 round it, three hooks K-209 under it."""
    c = Case("turin-3-92", 660, 0, y0=0, size=[746, 139, 1460])
    x0 = 43
    c.parts.append({"n": "1", "box": [x0, 0, 0, x0 + 660, 1418, 16], "edge": 3, "grain": "y",
                    "face": {"type": "grooves", "lines": [[x0 + 45, 45, x0 + 615, 45], [x0 + 615, 45, x0 + 615, 1373],
                                                          [x0 + 615, 1373, x0 + 45, 1373], [x0 + 45, 1373, x0 + 45, 45]],
                             "w": 5, "depth": 2, "flute": "u"}})
    c.parts.append({"n": "2", "box": [x0 + 1, 1418, 0, x0 + 659, 1443, 80], "edge": 3, "grain": "x"})
    c.parts.append({"id": "cornice", "kind": "moulding", "profile": "turin-crown-40", "plane": "top", "z": 1444, "side": -1,
                    "mat": "front", "covers": ["3", "4", "5"], "path": [[0, 0], [0, 139], [746, 139], [746, 0]]})
    for k, x in enumerate((x0 + 150, x0 + 330, x0 + 510)):
        c.parts.append({"id": f"hook-{k + 1}", "kind": "handle", "model": "knob", "at": [x, 1280], "d": 22, "t": 8,
                        "standoff": 55, "z": 16})
    return c.dump()


def m2_51():
    """П7.036.2.51 Стол письменный 2т 1500 × 650 × 750 (by catalogue, p. 60 photo, p. 62 cut-out): a top 25 over two
    pedestals (a drawer over a door each, pilasters, a plinth with the arch), a modesty panel between them."""
    c = Case("turin-2-51", 1500, 0, y0=0, size=[1500, 650, 750])
    c.parts.append({"id": "top", "box": [0, 725, 0, 1500, 750, 650], "edge": 5, "grain": "x"})
    for side, px in (("l", 20), ("r", 1070)):
        p = Case("x", 410, 630, sd=600, td=600, cx=px)
        p.P(f"bottom-{side}", [px, PH, BK, px + 410, PH + TT, BK + 620], edge=5, grain="x")
        p.sides(f"side-{side}l", f"side-{side}r")
        p.pilasters(f"pil-{side}l", f"pil-{side}r")
        x0, x1 = p.xi0, p.xi1
        rrail(p, f"rail-{side}", x0, x1, p.ys1, 70)
        p.shelf(f"shelf-{side}", x0 + 1, x1 - 1, p.ys0 + 230, depth=560, z1=p.zs1 - 4)
        ydr = p.ys1 - 2 - 150
        p.door(f"door_{side}", f"door-{side}", x0 + 2, x1 - 2, p.ys0 + 2, ydr - 2, "left" if side == "l" else "right", ydr - 110)
        p.drawer(side, (f"df-{side}", f"ds-{side}1", f"ds-{side}2", f"db-{side}", f"dd-{side}"), x0 + 2, x1 - 2, ydr,
                 p.ys1 - 2, x1 - x0 - 26, 100, side_l=450, bottom=[x1 - x0 - 30, 455])
        p.back(f"back-{side}", p.xl + 2, p.xr - 2, PH + 8, p.ys1 - 2)
        p.plinth(f"pf-{side}", f"ps-{side}1", f"ps-{side}2", f"pb-{side}", 400, 552)
        c.parts += p.parts
        c.moves += p.moves
    c.parts.append({"id": "modesty", "box": [446, 330, 300, 1054, 725, 316], "grain": "x"})
    return c.dump()


def m1_41():
    """П7.036.1.41 Зеркало 1200 × 19 × 660 (on the wall, landscape or portrait): a board 1200 × 660 with a milled line
    round a mirror 1036 × 494 centred on it."""
    c = Case("turin-1-41", 1200, 0, y0=0, size=[1200, 19, 660])
    g = 45
    c.parts.append({"n": "1", "box": [0, 0, 0, 1200, 660, 16], "edge": 4, "grain": "x", "mat": "front",
                    "face": {"type": "grooves", "lines": [[g, g, 1200 - g, g], [1200 - g, g, 1200 - g, 660 - g],
                                                          [1200 - g, 660 - g, g, 660 - g], [g, 660 - g, g, g]],
                             "w": 5, "depth": 2, "flute": "u"}})
    c.parts.append({"n": "2", "kind": "mirror", "box": [82, 83, 16, 1118, 577, 19]})
    return c.dump()



# ================================================================================================== bedroom
def m1_27():
    """П7.036.1.27 Тумба 694 × 450 × 1018: four drawers 222 (fronts 626), «брусок продольный» under each box, a rear rail 6
    under the top and a rear царга 5 behind the backs' joint."""
    c = Case("turin-1-27", 694, 898, td=450, bd=446, size=[694, 450, 1018])
    c.bottom("2")
    c.sides("3", "4")
    c.pilasters("14", "14")
    c.top("1", z0=0)
    x0, x1 = c.xi0, c.xi1
    rrail(c, "6", x0, x1, c.ys1, 70)
    rrail(c, "5", x0, x1, c.ys0 + 449 + 90, 180)
    for k, (a, b) in enumerate(ys_stack(c.ys0 + 2, [222] * 4, 2)):
        c.drawer(str(k + 1), ("9", "10", "11", "12", "13"), x0 + 2, x1 - 2, a, b, 604, 173, bottom=[600, 404],
                 bar=("8", 90))
    xb = (c.xl + c.xr) / 2
    c.back("7", xb - 329, xb + 329, c.y0 + 3, c.y0 + 463, "7-1")
    c.back("7", xb - 329, xb + 329, c.y0 + 463, c.y0 + 923, "7-2")
    c.plinth("15", "16", "16", "17", 682, 368, ids=(None, "16-l", "16-r", None))
    return c.dump()


def m1_28():
    """П7.036.1.28 Тумба прикроватная 500 × 450 × 500: a drawer 267 under a fixed shelf 5 and an open niche (≈ 93), a rear
    rail 16 under the top."""
    c = Case("turin-1-28", 500, 380, td=450, bd=446, size=[500, 450, 500])
    c.bottom("4")
    c.sides("2", "3")
    c.pilasters("6", "6")
    c.top("1", z0=0)
    x0, x1 = c.xi0, c.xi1
    rrail(c, "16", x0, x1, c.ys1, 70)
    yd1 = c.ys0 + 2 + 267
    c.shelf("5", x0, x1, yd1 + 2, depth=426, z1=c.zs1)
    c.drawer("1", ("10", "11", "12", "13", "14"), x0 + 2, x1 - 2, c.ys0 + 2, yd1, 410, 220, bottom=[406, 404],
             hy=yd1 - 60)
    xb = (c.xl + c.xr) / 2
    c.back("15", xb - 232, xb + 232, c.y0 + 3, c.y0 + 406)
    c.plinth("7", "9", "9", "8", 488, 368, ids=(None, "9-l", "9-r", None))
    return c.dump()


def m1_30():
    """П7.036.1.30 Комод 950 × 450 × 1018: two drawers side by side (fronts 439, a wall 24 between them on the horizontal
    23) over three wide drawers (882) with «брусок продольный» under their boxes; rear rails 6 in the top tier, a rear
    царга 5 behind the backs' joint."""
    c = Case("turin-1-30", 950, 898, td=450, bd=446, size=[950, 450, 1018])
    c.bottom("2")
    c.sides("3", "4")
    c.pilasters("19", "19")
    c.top("1", z0=0)
    x0, x1 = c.xi0, c.xi1
    y24 = c.ys1 - 220
    c.shelf("23", x0, x1, y24 - 16, depth=424, z1=c.zs1)
    xm = (x0 + x1) / 2
    c.upright("24", xm - 8, y24, c.ys1, z0=c.zs1 - 424)
    rrail(c, "6", x0, xm - 8, c.ys1, 70, "6-l")
    rrail(c, "6", xm + 8, x1, c.ys1, 70, "6-r")
    fr = spread(x0 + 2, x1, [439, 439], 4)
    c.drawer("tl", ("12", "8", "9", "10", "11"), *fr[0], y24 - 2, c.ys1 - 2, 409, 173, bottom=[405, 402])
    c.drawer("tr", ("7", "8", "9", "10", "11"), *fr[1], y24 - 2, c.ys1 - 2, 409, 173, bottom=[405, 402])
    for k, (a, b) in enumerate(ys_stack(c.ys0 + 2, [220] * 3, 4)):
        c.drawer(str(k + 1), ("13", "14", "15", "16", "18"), x0 + 2, x1 - 2, a, b, 860, 173, bottom=[856, 404],
                 bar=("17", 100))
    rrail(c, "5", x0, x1, c.ys0 + 363 + 90, 180)
    xb = (c.xl + c.xr) / 2
    c.back("26", xb - 457, xb + 457, c.y0 + 3, c.y0 + 366)
    c.back("25", xb - 457, xb + 457, c.y0 + 366, c.y0 + 920)
    c.plinth("20", "21", "21", "22", 940, 368, ids=(None, "21-l", "21-r", None))
    return c.dump()


def chest_2x4(did, L0, ns, sec_w, front_w, box_w, bottom, back_specs, plinth_len, size):
    c = Case(did, L0, 898, td=450, bd=446, size=size)
    c.bottom(ns["bottom"])
    c.sides(ns["left"], ns["right"])
    xp = c.xi0 + sec_w
    c.upright(ns["part"], xp)
    c.pilasters(ns["pil"], ns["pil"])
    c.top(ns["top"], z0=0)
    rrail(c, ns["rail"], c.xi0, xp, c.ys1, 70, f"{ns['rail']}-l")
    rrail(c, ns["rail"], xp + 16, c.xi1, c.ys1, 70, f"{ns['rail']}-r")
    fr = spread(c.xi0 + 2, c.xi1, [front_w, front_w], (c.xi1 - c.xi0 - 2 * front_w) / 3)
    for side, (fa, fb) in zip("lr", fr):
        for k, (a, b) in enumerate(ys_stack(c.ys0 + 2, [222] * 4, 2)):
            c.drawer(f"{side}{k + 1}", (ns["front_" + side], ns["ds_l"], ns["ds_r"], ns["db"], ns["dd"]), fa, fb, a, b,
                     box_w, 173, bottom=bottom)
    x = (c.xl + c.xr) / 2 - sum(w for _, w, _ in back_specs) / 2
    for n, w, pid in back_specs:
        c.back(n, x, x + w, c.y0 + 3, c.y0 + 924, pid)
        x += w
    c.plinth(ns["pf"], ns["ps"], ns["ps"], ns["pb"], plinth_len, 368, ids=(None, f"{ns['ps']}-l", f"{ns['ps']}-r", None))
    return c


NS_131 = {"bottom": "2", "left": "3", "right": "4", "part": "5", "pil": "14", "top": "1", "rail": "6", "front_l": "8",
          "front_r": "9", "ds_l": "10", "ds_r": "11", "db": "12", "dd": "13", "pf": "15", "ps": "16", "pb": "17"}


def m1_31():
    """П7.036.1.31 Комод 1200 × 450 × 1018: two columns of four drawers (fronts 565 × 222) either side of a partition,
    rear rails 6 under the top."""
    c = chest_2x4("turin-1-31", 1200, NS_131, 560, 565, 534, [530, 404], [("7", 581, "7-1"), ("7", 581, "7-2")], 1188,
                  [1200, 450, 1018])
    return c.dump()


def m1_32():
    """П7.036.1.32 Комод 1500 × 450 × 1018 (by catalogue, p. 59 photo and the p. 63 cut-out): 1.31 widened — two columns
    of four drawers (sections 710, fronts 715); the numbers of 1.31 are kept as labels."""
    c = chest_2x4("turin-1-32", 1500, NS_131, 710, 715, 684, [680, 404], [("7", 731, "7-1"), ("7", 731, "7-2")], 1488,
                  [1500, 450, 1018])
    return c.dump()


def m1_57():
    """П7.036.1.57 Стол туалетный 950 × 500 × 800: a top 25 on two sides 775 (on glides, a small arch cut in their lower
    edge), a drawer 130 under a flat front rail 5, the rear modesty panel 4 with a wavy lower edge; the drawer holds an
    organiser (10 × 2 along, 11 × 3 across the middle row)."""
    c = Case("turin-1-57", 950, 0, y0=0, size=[950, 500, 800])
    z0s, z1s = 20, 460
    c.parts.append({"n": "1", "box": [0, 775, 0, 950, 800, 500], "edge": 5, "grain": "x"})
    for n, x in (("2", 29), ("3", 905)):
        ar = (f"M {z0s} 775 L {z1s} 775 L {z1s} 0 L {z1s - 60} 0 C {z1s - 80} 22 {z0s + 80} 22 {z0s + 60} 0 L {z0s} 0 Z")
        c.parts.append({"n": n, "box": [x, 0, z0s, x + 16, 775, z1s], "grain": "y", "shape": "path", "outline": ar})
    x0, x1 = 45, 905
    c.parts.append({"n": "5", "box": [x0, 759, z1s - 70, x1, 775, z1s], "grain": "x"})
    c.parts.append({"n": "4", "box": [x0, 225, z0s, x1, 775, z0s + 16], "grain": "x", "shape": "path",
                    "outline": f"M {x0} 775 L {x1} 775 L {x1} 300 C {x1 - 200} 225 {x0 + 200} 225 {x0} 300 Z"})
    c.zs1 = z1s - FT
    c.zf1 = z1s
    fy0, fy1 = 757 - 130, 757
    box_w = 834
    xm = (x0 + x1) / 2
    bx0 = xm - box_w / 2
    zb0 = c.zs1 - 400 + 16
    yb = fy0 + 18
    extra = []
    for k, x in enumerate((bx0 + 16 + 257, bx0 + 16 + 257 + 16 + 256)):
        extra.append({"n": "10", "id": f"10-{k + 1}", "box": [x, yb, zb0, x + 16, yb + 90, zb0 + 382]})
    for k in range(3):
        z = zb0 + (k + 1) * 382 / 4 - 8
        extra.append({"n": "11", "id": f"11-{k + 1}", "box": [bx0 + 16 + 257 + 16, yb, z, bx0 + 16 + 257 + 16 + 256, yb + 90, z + 16]})
    c.drawer("1", ("6", "7", "8", "9", "12"), x0 + 2, x1 - 2, fy0, fy1, box_w, 90, bottom=[830, 403], extra=extra)
    return c.dump()



def column_backs(c, x, cols, y0):
    """Backs in columns from x: cols = [(width, [(n, h, id), … from the bottom]), …]."""
    for w, stack in cols:
        y = y0
        for n, h, pid in stack:
            c.back(n, x, x + w, y, y + h, pid)
            y += h
        x += w


def m1_16_01():
    """П7.036.1.16-01 Шкаф для одежды 3д 1596 × 640 × 2200: hanging sections left and right (a hat shelf, a low shelf, a
    rear царга, a rail), shelves in the middle (two fixed, four loose) behind a mirror door on half-overlay hinges;
    crown strips 1596 / 641."""
    c = Case("turin-1-16-01", 1514, 2040, sd=580, td=600, cx=41, size=[1596, 640, 2200])
    c.bottom("2")
    c.sides("3", "4")
    x5 = c.xi0 + 482
    x6 = x5 + 16 + 454
    c.upright("5", x5)
    c.upright("6", x6)
    c.pilasters("23", "24")
    c.top("1")
    secs = [(c.xi0, x5), (x5 + 16, x6), (x6 + 16, c.xi1)]
    yh = 1790
    for k in (0, 2):
        a, b = secs[k]
        c.shelf("7", a, b, yh, depth=578, pid=f"7-{k + 1}h", z1=c.zs1 - 1)
        c.shelf("7", a, b, 380, depth=578, pid=f"7-{k + 1}l", z1=c.zs1 - 1)
        rrail(c, "10", a, b, yh, 200, f"10-{k + 1}")
        c.parts.append(rod_rail(f"37-{k + 1}", a + 4, b - 4, yh - 60, 300, covers=["37"]))
    a, b = secs[1]
    c.shelf("9", a, b, yh, depth=578, pid="9-h", z1=c.zs1 - 1)
    c.shelf("9", a, b, 380, depth=578, pid="9-l", z1=c.zs1 - 1)
    for k, y in enumerate((660, 940, 1220, 1500)):
        c.shelf("8", a + 1, b - 1, y, depth=570, pid=f"8-{k + 1}", z1=c.zs1 - 5)
    fr = spread(c.xi0 + 2, c.xi1, [487, 468, 487], 2)
    y0, y1 = c.ys0 + 2, c.ys1 - 2
    c.door("door_left", "11", *fr[0], y0, y1, "left", 1100)
    c.door("door_mid", "13", *fr[1], y0, y1, "right", 1100, glass=MIRROR)
    c.door("door_right", "12", *fr[2], y0, y1, "right", 1100)
    xb = (c.xl + c.xr) / 2 - 737
    column_backs(c, xb, [(504, [("21", 1835, "21-1")]), (466, [("22", 1835, None)]), (504, [("21", 1835, "21-2")])], c.y0 + 3)
    c.back("20", (c.xl + c.xr) / 2 - 739, (c.xl + c.xr) / 2 + 739, c.y0 + 1838, c.y0 + 2087)
    c.plinth("14", "15", "16", "17", 1504, 522)
    c.cornice_strips(["18", "19/19-01", "19/19-01"], 1596, 640, c.ys1 + TT, z0=0, h=40)
    return c.dump()


def m1_18():
    """П7.036.1.18 Шкаф для одежды 2д 1130 × 643 × 2200: a top compartment (250) over the horizontal 7; below it a hanging
    section 578 (rail 34, a rear царга 9, a low shelf 8) and a section of four shelves 386; crown strips 1130 / 643."""
    c = Case("turin-1-18", 1044, 2040, sd=580, td=600, cx=43, size=[1130, 643, 2200])
    c.bottom("2")
    c.sides("4", "3")
    x5 = c.xi0 + 578
    y7 = c.ys0 + 1774
    c.upright("5", x5, c.ys0, y7, z1=c.zs1 - 2)
    c.shelf("7", c.xi0, c.xi1, y7, depth=579, z1=c.zs1)
    c.pilasters("14", "14")
    c.top("1")
    c.shelf("8", c.xi0, x5, 380, depth=577, z1=c.zs1)
    rrail(c, "9", c.xi0, x5, y7, 150)
    c.parts.append(rod_rail("34", c.xi0 + 3, x5 - 3, y7 - 60, 300, covers=["34"]))
    for k, y in enumerate((440, 800, 1160, 1520)):
        c.shelf("6", x5 + 16, c.xi1, y, depth=507, pid=f"6-{k + 1}", z1=c.zs1 - 5)
    fr = spread(c.xi0 + 2, c.xi1, [487, 487], 2)
    c.door("door_left", "10", *fr[0], c.ys0 + 2, c.ys1 - 2, "left", 1100, pid="10-1")
    c.door("door_right", "10", *fr[1], c.ys0 + 2, c.ys1 - 2, "right", 1100, pid="10-2")
    xb = (c.xl + c.xr) / 2 - 504
    column_backs(c, xb, [(599, [("21", 1059, None), ("20", 743, None)]), (409, [("19", 1806, None)])], c.y0 + 5)
    c.back("18", (c.xl + c.xr) / 2 - 505, (c.xl + c.xr) / 2 + 505, c.y0 + 1807, c.y0 + 2087)
    c.plinth("11", "13", "13", "12", 1032, 522, ids=(None, "13-l", "13-r", None))
    c.cornice_strips(["15", "16", "17"], 1130, 643, c.ys1 + TT, z0=0, h=40)
    return c.dump()


def m1_19():
    """П7.036.1.19 Шкаф для одежды 2д 1006 × 497 × 2200: two doors over a full-width drawer (on the horizontal 6); above,
    a hanging section 580 (a hat shelf 7, a rear царга 9, a pull-out rail 41 along the depth) and five shelves 260;
    crown strips 1006 / 493."""
    c = Case("turin-1-19", 920, 2040, cx=43, size=[1006, 497, 2200])
    c.bottom("4")
    c.sides("2", "3")
    y6 = c.ys0 + 2 + 222 + 1
    c.shelf("6", c.xi0, c.xi1, y6 - 8, depth=426, z1=c.zs1)
    x5 = c.xi0 + 580
    c.upright("5", x5, y6 + 8, c.ys1)
    c.pilasters("14", "14")
    c.top("1", z0=3)
    c.shelf("7", c.xi0, x5, 1800, depth=424, z1=c.zs1)
    rrail(c, "9", c.xi0, x5, 1800, 200)
    xm = (c.xi0 + x5) / 2
    c.parts.append({"id": "41", "kind": "tube", "mat": "chrome", "box": [xm - 10, 1740, 40, xm + 10, 1760, 390], "covers": ["41"]})
    for k, y in enumerate((620, 880, 1140, 1400, 1660)):
        c.shelf("8", x5 + 16, c.xi1, y, depth=424, pid=f"8-{k + 1}", z1=c.zs1)
    fr = spread(c.xi0 + 2, c.xi1, [425, 425], 2)
    c.door("door_left", "10", *fr[0], y6 + 1, c.ys1 - 2, "left", 1150, pid="10-1")
    c.door("door_right", "10", *fr[1], y6 + 1, c.ys1 - 2, "right", 1150, pid="10-2")
    c.drawer("1", ("22", "23", "24", "25", "27"), c.xi0 + 2, c.xi1 - 2, c.ys0 + 2, y6 - 1, 830, 173, bottom=[826, 404],
             bar=("26", 90))
    xb = (c.xl + c.xr) / 2 - 442
    c.back("20", xb, xb + 884, c.y0 + 3, c.y0 + 250)
    column_backs(c, xb + 1, [(601, [("19", 776, "19-1"), ("19", 776, "19-2"), ("18", 280, None)]),
                             (281, [("21", 1837, None)])], c.y0 + 250)
    c.plinth("11", "13", "13", "12", 910, 372, ids=(None, "13-l", "13-r", None))
    c.cornice_strips(["15", "16", "17"], 1006, 493, c.ys1 + TT, z0=4, h=40)
    return c.dump()


def m1_77_01():
    """П7.036.1.77-01 Шкаф для одежды 4д 2070 × 643 × 2200: shelf sections 482 left and right (two fixed, two loose
    shelves), a hanging section 924 in the middle (two fixed shelves, a rear царга, the rail 918) behind two mirror doors
    on half-overlay hinges (p. 63 cut-out); crown strips 2070 / 643."""
    c = Case("turin-1-77-01", 1984, 2040, sd=580, td=600, cx=43, size=[2070, 643, 2200])
    c.bottom("2")
    c.sides("3", "4")
    x5 = c.xi0 + 482
    x6 = x5 + 16 + 924
    c.upright("5", x5)
    c.upright("6", x6)
    c.pilasters("17", "17")
    c.top("1")
    secs = [(c.xi0, x5), (x5 + 16, x6), (x6 + 16, c.xi1)]
    for k, n in ((0, "8"), (2, "9")):
        a, b = secs[k]
        c.shelf(n, a, b, 380, depth=570, pid=f"{n}-l", z1=c.zs1 - 5)
        c.shelf(n, a, b, 1790, depth=570, pid=f"{n}-h", z1=c.zs1 - 5)
        for j, y in enumerate((850, 1320)):
            c.shelf("10", a + 1, b - 1, y, depth=570, pid=f"10-{k + 1}{j + 1}", z1=c.zs1 - 5)
    a, b = secs[1]
    c.shelf("7", a, b, 1790, depth=578, pid="7-h", z1=c.zs1 - 1)
    c.shelf("7", a, b, 380, depth=578, pid="7-l", z1=c.zs1 - 1)
    rrail(c, "11", a, b, 1790, 200)
    c.parts.append(rod_rail("38", a + 3, b - 3, 1730, 300, covers=["38"]))
    fr = spread(c.xi0 + 2, c.xi1, [487, 468, 468, 487], 2)
    y0, y1 = c.ys0 + 2, c.ys1 - 2
    c.door("door_1", "15", *fr[0], y0, y1, "left", 1100, pid="15-1")
    c.door("door_2", "16", *fr[1], y0, y1, "left", 1100, pid="16-1", glass=MIRROR)
    c.door("door_3", "16", *fr[2], y0, y1, "right", 1100, pid="16-2", glass=MIRROR)
    c.door("door_4", "15", *fr[3], y0, y1, "right", 1100, pid="15-2")
    xb = (c.xl + c.xr) / 2 - 972
    column_backs(c, xb, [(503, [("21", 430, "21-1"), ("22", 1222, "22-1"), ("21", 430, "21-2")]),
                         (938, [("23", 330, "23-1"), ("24", 710, "24-1"), ("24", 710, "24-2"), ("23", 330, "23-2")]),
                         (503, [("21", 430, "21-3"), ("22", 1222, "22-2"), ("21", 430, "21-4")])], c.y0 + 3)
    c.plinth("12", "13", "13", "14", 1974, 522, ids=(None, "13-l", "13-r", None))
    c.cornice_strips(["18", "19", "20"], 2070, 643, c.ys1 + TT, z0=0, h=40)
    return c.dump()



def metal_base(parts, x0, x1, z0, z1, y_top=300, tag="13"):
    """The metal slatted base («металлокаркас», hardware): a black frame of 40 × 40 tubes with a middle beam when it is
    wider than 1200, legs under it, birch slats; its top at y_top."""
    y0 = y_top - 40
    parts += [
        {"id": "base-l", "kind": "panel", "mat": "black", "box": [x0, y0, z0, x0 + 40, y_top - 8, z1], "covers": [tag]},
        {"id": "base-r", "kind": "panel", "mat": "black", "box": [x1 - 40, y0, z0, x1, y_top - 8, z1]},
        {"id": "base-h", "kind": "panel", "mat": "black", "box": [x0 + 40, y0, z0, x1 - 40, y_top - 8, z0 + 40]},
        {"id": "base-f", "kind": "panel", "mat": "black", "box": [x0 + 40, y0, z1 - 40, x1 - 40, y_top - 8, z1]},
    ]
    fields = [(x0 + 40, x1 - 40)]
    legs = [(x0 + 20, z0 + 20), (x1 - 20, z0 + 20), (x0 + 20, z1 - 20), (x1 - 20, z1 - 20)]
    if x1 - x0 > 1200:
        xm = (x0 + x1) / 2
        parts.append({"id": "base-m", "kind": "panel", "mat": "black", "box": [xm - 20, y0, z0 + 40, xm + 20, y_top - 8, z1 - 40]})
        fields = [(x0 + 40, xm - 20), (xm + 20, x1 - 40)]
        legs += [(xm, z0 + 20), (xm, (z0 + z1) / 2), (xm, z1 - 20)]
    else:
        legs += [(x0 + 20, (z0 + z1) / 2), (x1 - 20, (z0 + z1) / 2)]
    for k, (x, z) in enumerate(legs):
        parts.append({"id": f"base-leg-{k + 1}", "kind": "tube", "mat": "black", "box": [x - 12, 0, z - 12, x + 12, y0, z + 12]})
    n = 22
    pitch = (z1 - z0 - 80) / n
    for f, (a, b) in enumerate(fields):
        for i in range(n):
            z = z0 + 40 + pitch * i + (pitch - 53) / 2
            parts.append({"id": f"slat-{f + 1}-{i + 1}", "kind": "panel", "mat": "door_enamel_whitey#c9a877", "edge": 2,
                          "box": [round(a - 20, 2), y_top - 8, round(z, 2), round(b + 20, 2), y_top, round(z + 53, 2)]})
    parts.append({"id": "mattress", "kind": "mattress", "box": [x0, y_top, z0, x1, y_top + 200, z1]})


def bed_frame(did, W, sleep, *, instructed, size):
    """Кровать 1-09 / 2-16 (L2058, H848): a headboard 25 (W × 848) with the decorative frame 4 (W − 5 × 340, МДФ 20, a
    milled frame) at its top, side rails 3 (2008 × 198) between the head- and footboards, a footboard 2 (W × 300) with
    the arch cut in its lower edge, the metal base 2000 × sleep on its own legs, a mattress."""
    c = Case(did, W, 0, y0=0, size=size)
    n = (lambda k, i: {"n": k}) if instructed else (lambda k, i: {"id": i})
    L = 2058
    parts = c.parts
    parts.append({**n("1", "headboard"), "box": [0, 0, 0, W, 848, 25], "edge": 3, "grain": "x"})
    parts.append({**n("4", "frame"), "kind": "front", "box": [2.5, 498, 25, W - 2.5, 838, 45], "edge": 2, "grain": "x",
                  "face": {"type": "frame", "border": 60, "depth": 6, "r": 1, "profile": "turin-ogee"}})
    parts.append({**n("2", "footboard"), "box": [0, 0, L - 25, W, 300, L], "edge": 3, "grain": "x", "shape": "path",
                  "outline": arch(0, W, 300, rise=90, foot=max(60.0, W * 0.07))})
    for tag, x in (("l", 0), ("r", W - 16)):
        parts.append({**({"n": "3", "id": f"3-{tag}"} if instructed else {"id": f"rail-{tag}"}), "box": [x, 100, 25, x + 16, 298, L - 25],
                      "grain": "z"})
    g = (W - 32 - sleep) / 2
    metal_base(parts, 16 + g, W - 16 - g, 29, 2029)
    return c.dump()


def m1_02():
    return bed_frame("turin-1-02", 962, 900, instructed=True, size=[962, 2058, 848])


def m1_01():
    return bed_frame("turin-1-01", 1662, 1600, instructed=False, size=[1662, 2058, 848])


def bed_soft(did, W, sleep):
    """Кровать 2-16 / 2-18 / 1-12 / 2-14 with the upholstered headboard (L2211, H898; by catalogue, the p. 59 / 61 photos
    and the p. 63 cut-outs): a headboard 25 (W × 898) carrying a soft pad of four panels (seams) over its upper half, the
    rails and the arched footboard of 1.01 / 1.02, the base 2000 × sleep in front of the pad."""
    L = 2211
    c = Case(did, W, 0, y0=0, size=[W, L, 898])
    parts = c.parts
    parts.append({"id": "headboard", "box": [0, 0, 0, W, 898, 25], "edge": 3, "grain": "x"})
    parts.append({"id": "pad", "kind": "soft", "box": [30, 500, 25, W - 30, 890, 125], "channels": 4 if W > 1300 else 3})
    parts.append({"id": "footboard", "box": [0, 0, L - 25, W, 300, L], "edge": 3, "grain": "x", "shape": "path",
                  "outline": arch(0, W, 300, rise=90, foot=max(60.0, W * 0.07))})
    for tag, x in (("l", 0), ("r", W - 16)):
        parts.append({"id": f"rail-{tag}", "box": [x, 100, 25, x + 16, 298, L - 25], "grain": "z"})
    parts.append({"id": "rail-head", "box": [16, 100, 25, W - 16, 298, 41], "grain": "x"})
    g = (W - 32 - sleep) / 2
    metal_base(parts, 16 + g, W - 16 - g, L - 25 - 2006, L - 29)
    return c.dump()


# ================================================================================================== catalogue
def _ellipse(cx, cy, a, b, t0, t1, n=8):
    return [[round(cx + a * math.cos(math.radians(t0 + (t1 - t0) * i / n)), 2),
             round(cy + b * math.sin(math.radians(t0 + (t1 - t0) * i / n)), 2)] for i in range(n + 1)]


def crown(h, p=43):
    """A crown moulding h high overhanging p: an ovolo lip, a cove down to a fillet on the top; v from −(h − 16)."""
    off = -(h - 16)
    pts = [[0, h - 6], [0, h - 2], [2, h], [p + 15, h], [p + 15, 0], [p, 0], [p - 3, 0], [p - 3, 3]]
    pts += _ellipse(8, 3, p - 11, h - 15, 0, 90)[1:]            # the cove, (p − 3, 3) → (8, h − 12)
    pts += [[4, h - 12], [4, h - 10]]
    pts += [[round(4 - 4 * math.sin(math.radians(a)), 2), round(h - 6 - 4 * math.cos(math.radians(a)), 2)] for a in (30, 60)]
    return [[u, round(v + off, 2)] for u, v in pts]


def cove(h, p):
    """The cove under a cornice board: from the board's underside (outer edge u = 0) down to the top's front edge."""
    pts = [[0, h - 3], [0, h], [p + 12, h], [p + 12, 0], [p, 0]]
    pts += _ellipse(3, 0, p - 3, h - 3, 0, 90)[1:]
    return pts


OGEE = [[0, 0], [0, 6], [1.2, 5.8], [2.5, 5.2], [3.6, 4.3], [4.4, 3.3], [5, 2.6], [6.5, 1.9], [9, 1.2], [12, 0.7],
        [16, 0.35], [20, 0.12], [24, 0]]

PROFILES = {
    "turin-ogee": {"name": "Фасад «Турин»: скругление рамки и выкружка к филёнке (фрезеровка МДФ)", "pts": OGEE},
    "turin-crown-40": {"name": "Карниз «Турин» 40 × 43: валик, выкружка, полочка", "pts": crown(40)},
    "turin-crown-36": {"name": "Карниз «Турин» 36 × 43 (шкафы-витрины на тумбе)", "pts": crown(36)},
    "turin-wall-450": {"name": "Стенка стола «Турин» 16 × 450 (наклонная в плане стенка как профиль)",
                       "pts": [[0, 0], [0, 450], [16, 450], [16, 0]]},
    "turin-cove-24": {"name": "Карниз-щит «Турин»: выкружка 24 × 32 под щитом", "pts": cove(24, 32)},
}

FINISHES = [
    {"id": "turin-sosna-karelia", "name": "Сосна Карелия", "body": "door_enamel_whitey#e6e7e1", "front": "door_enamel_whitey#e6e7e1",
     "swatch": "#e6e7e1", "note": "декор (текстура — в gen/turin_decors.md); цвет — образец с. 62"},
    {"id": "turin-dub-kanyon", "name": "Дуб Каньон", "body": "door_enamel_whitey#8a6b4e", "front": "door_enamel_whitey#8a6b4e",
     "swatch": "#8a6b4e", "note": "декор (текстура — в gen/turin_decors.md); цвет — образец с. 62"},
]

COLLECTION = {"id": "turin", "name": "Турин", "brand": "Пинскдрев", "finishes": ["turin-sosna-karelia", "turin-dub-kanyon"],
              "metal": "gold#8c7446",
              "note": "Каталог «Корпусная мебель ч. II» 2025, с. 57–63 (110–123 по нумерации каталога); 22 модуля по "
                      "инструкциям (таблицы «№, наименование, A×B, кол.» — gen/cutlists/turin-*.json), 9 — по каталогу. "
                      "Корпус ЛДСП 16, крышка и дно 25 с закруглённой кромкой (боковины на дне, крышка на боковинах, "
                      "свес 16), пилястры 22 × 20 на кромках боковин, фасады МДФ 20 между ними с фрезеровкой «рамка + "
                      "выкружка», стеклянные двери, цоколь 70 с аркой, карниз 40 на высоких шкафах, ручки — "
                      "состаренная латунь (накладка с овальной кнопкой)."}

# id → (code, name, category, index page, "is" or None, note, extra)
MODELS = {}


def model(did, code, name, cat, size, page, is_=None, note=None, **extra):
    m = {"id": did, "code": code, "name": name, "collection": SLUG, "category": cat, "size": size, "page": page}
    if is_:
        m["is"] = is_
    if note:
        m["note"] = note
    m.update(extra)
    MODELS[did] = m


def catalog():
    data = {"finishes": FINISHES, "profiles": PROFILES, "collections": [COLLECTION], "models": list(MODELS.values())}
    path = os.path.join(HERE, "turin_catalog.json")
    with open(path, "w") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
    return path


def index():
    with open(os.path.join(HERE, "..", "reference", "index.json")) as fh:
        return {a["code"]: a for a in json.load(fh) if a.get("slug") == SLUG}


# ================================================================================================== registry
# model id → (builder, category, note); the code, name, size, page and instruction come from reference/index.json
REG = [
    ("turin-0-12", "П7.036.0.12", m0_12, "living", "универсальный, подсветка"),
    ("turin-0-10", "П7.036.0.10", m0_10, "living", "подсветка"),
    ("turin-0-11", "П7.036.0.11", m0_11, "living", "подсветка"),
    ("turin-0-24", "П7.036.0.24", m0_24, "living", ""),
    ("turin-0-23", "П7.036.0.23", m0_23, "living", "как нижняя часть 0.10"),
    ("turin-0-26", "П7.036.0.26", m0_26, "living", "подсветка"),
    ("turin-0-21", "П7.036.0.21", m0_21, "living", "подсветка"),
    ("turin-0-70", "П7.036.0.70", m0_70, "decor", "навесная"),
    ("turin-0-52", "П7.036.0.52", m0_52, "tables", ""),
    ("turin-4-54", "П7.036.4.54", m4_54, "tables", ""),
    ("turin-2-14", "П7.036.2.14", m2_14, "living", ""),
    ("turin-3-22", "П7.036.3.22", m3_22, "hall", "мягкое сиденье"),
    ("turin-3-92", "П7.036.3.92", m3_92, "hall", "навесная"),
    ("turin-2-51", "П7.036.2.51", m2_51, "office", ""),
    ("turin-1-41", "П7.036.1.41", m1_41, "decor", "навесное, горизонтально или вертикально"),
    ("turin-1-27", "П7.036.1.27", m1_27, "bedroom", ""),
    ("turin-1-28", "П7.036.1.28", m1_28, "bedroom", ""),
    ("turin-1-30", "П7.036.1.30", m1_30, "bedroom", ""),
    ("turin-1-31", "П7.036.1.31", m1_31, "bedroom", ""),
    ("turin-1-32", "П7.036.1.32", m1_32, "bedroom", "как 1.31 шириной 1500"),
    ("turin-1-57", "П7.036.1.57", m1_57, "bedroom", ""),
    ("turin-1-16-01", "П7.036.1.16-01", m1_16_01, "bedroom", "средняя дверь с зеркалом"),
    ("turin-1-18", "П7.036.1.18", m1_18, "bedroom", ""),
    ("turin-1-19", "П7.036.1.19", m1_19, "bedroom", ""),
    ("turin-1-77-01", "П7.036.1.77-01", m1_77_01, "bedroom", "средние двери с зеркалом"),
    ("turin-1-02", "П7.036.1.02", m1_02, "bedroom", "с металлокаркасом 900 × 2000"),
    ("turin-1-01", "П7.036.1.01", m1_01, "bedroom", "с металлокаркасом 1600 × 2000; как 1.02 шириной 1662"),
    ("turin-1-03", "П7.036.1.03", lambda: bed_soft("turin-1-03", 1678, 1600), "bedroom", "с металлокаркасом 1600 × 2000, мягкое изголовье"),
    ("turin-1-04", "П7.036.1.04", lambda: bed_soft("turin-1-04", 1278, 1200), "bedroom", "с металлокаркасом 1200 × 2000, мягкое изголовье"),
    ("turin-1-05", "П7.036.1.05", lambda: bed_soft("turin-1-05", 1478, 1400), "bedroom", "с металлокаркасом 1400 × 2000, мягкое изголовье"),
    ("turin-1-06", "П7.036.1.06", lambda: bed_soft("turin-1-06", 1878, 1800), "bedroom", "с металлокаркасом 1800 × 2000, мягкое изголовье"),
]


def nm(name):
    name = name.replace("ШКАФ", "Шкаф")
    return name[0].upper() + name[1:]


def main(only=None):
    idx = index()
    for did, code, fn, cat, note in REG:
        a = idx[code]
        path = fn()
        with open(path) as fh:
            size = json.load(fh)["size"]
        is_ = os.path.basename(a["pdf"]) if a.get("pdf") else None
        n = note + ("" if is_ else ("; " if note else "") + "по каталогу, без инструкции")
        extra = {"mount": "wall"} if "навес" in note else {}
        model(did, code, nm(a["name"]), cat, size, a["pages"][0], is_, n or None, **extra)
        print(path)
    print(catalog())


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
