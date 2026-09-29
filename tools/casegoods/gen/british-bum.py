"""«Бритиш Бум» (П3.0551, kids' room): all 19 modules by catalogue / by photo (no assembly instructions exist).

Sources: catalogue pp. 129–131 (printed 254–259): interiors on 129 (3д, комоды 1.27 / 1.13, угловой стол, кровать 1-12)
and 130 (полка, стол 2т, шкаф 1.01, 2д, the loft bed with the 1-08 bed under it); front-on cut-outs of every module and
the «Крем» / «Дуб Трюфельный» swatches on 131. Product photos on pinskdrev.by («Бритиш» П551.xx): 1.13, 1.27, 1.03,
1.04 (+ a dimensioned drawing), 1.09 (+ a drawing), 2.17 / 2.17-01.

Construction (one scheme for the carcass pieces, measured on the site photos of 1.13 / 1.27 / 1.03 / 1.04):
* ЛДСП 16 «Дуб Трюфельный»: the sides stand on the floor (a skirting notch ≈ 50 × 50 at the back bottom — the 1.04
  drawing, the 1.13 photo), the top 16 lies over them (full width), a bottom 16 between the sides at 72…88 on a plinth
  board 72 high set flush with the fronts; ХДФ back 3 nailed over the back edges (cream in the niches, as photographed);
* INSET fronts ЛДСП/МДФ 16 «Крем» between the sides, flush with the carcass front: 2 mm off the sides, 3 mm gaps, the
  lowest front from y 90, 3 mm under the top; the cream fronts carry printed London line drawings (`print`);
* bow handles (arched «скоба», satin chrome) ≈ 184 long: centred on drawers, upright ≈ 22 mm from the meeting edge on
  wardrobe doors, horizontal near the top / bottom edge of short doors;
* drawer boxes ЛДСП 16, ХДФ bottoms, 13 mm runner gaps; wardrobe rails Ø25.

    python3 tools/casegoods/gen/british-bum.py      # writes Designs/british-bum-*.json and gen/british-bum_catalog.json
"""
import json
import math
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
T, FT, BK, G = 16, 16, 3, 3
PL, YB0, YB1, F0 = 72, 72, 88, 90          # plinth top, the bottom board, the lowest front edge
NOTCH = 50                                   # the skirting notch at the back bottom of the sides


def r5(v):
    return round(v * 2) / 2


def pr(name):
    return f"british_bum_{name}"


# ---------------------------------------------------------------------------------------------------- parts
def side(sid, x0, y1, B, z0=BK, notch=True, y0=0):
    """A side standing on the floor, from z0 (behind: the nailed back) to B; the skirting notch in its outline."""
    p = {"id": sid, "box": [x0, y0, z0, x0 + T, y1, B]}
    if notch and y0 == 0:
        p["shape"] = "path"
        p["outline"] = (f"M {z0} {NOTCH} L {z0} {y1} L {B} {y1} L {B} 0 L {z0 + NOTCH + 5} 0 "
                        f"Q {z0 + NOTCH - 8} {NOTCH - 6} {z0} {NOTCH} Z")
    return p


def carcass(W, B, H, x0=0, top=True, bottom=True, back=True, tag=""):
    """Sides, top over them, bottom between them on a plinth flush with the fronts, ХДФ back nailed on."""
    x1 = x0 + W
    yt = H - T if top else H
    p = [side(f"side-l{tag}", x0, yt, B), side(f"side-r{tag}", x1 - T, yt, B)]
    if top:
        p.append({"id": f"top{tag}", "box": [x0, H - T, BK, x1, H, B]})
    if bottom:
        p.append({"id": f"bottom{tag}", "box": [x0 + T, YB0, BK, x1 - T, YB1, B]})
        p.append({"id": f"plinth{tag}", "box": [x0 + T, 0, B - FT, x1 - T, PL, B]})
    if back:
        p.append({"id": f"back{tag}", "kind": "back", "box": [x0, YB0, 0, x1, H, BK]})
    return p


def shelf(sid, x0, x1, y0, B, fixed=False, front=None):
    """y0 = the underside. Fixed: over the whole depth up to the fronts' back face (or `front`); loose: 1 mm off the
    sides, 20 mm off the back and the fronts."""
    if fixed:
        return {"id": sid, "box": [x0, y0, BK, x1, y0 + T, front if front is not None else B - FT]}
    return {"id": sid, "box": [x0 + 1, y0, BK + 20, x1 - 1, y0 + T, (front if front is not None else B - FT) - 20]}


def rail(rid, x0, x1, y, zc):
    return {"id": rid, "kind": "tube", "mat": "metal", "box": [x0, y - 12.5, zc - 12.5, x1, y + 12.5, zc + 12.5]}


def bow(hid, x, y, z, vertical=False):
    """The arched bow handle («скоба», satin chrome): ≈ 184 long, c-c ≈ 150 (the engine: a straight bar on two posts)."""
    return {"id": hid, "kind": "handle", "model": "bar", "mat": "metal", "at": [r5(x), r5(y)],
            "dir": "up" if vertical else "right", "d": 184, "band": 13, "t": 9, "standoff": 24, "post": 10, "z": z}


def front(fid, x0, x1, y0, y1, zf, prn=None):
    f = {"id": fid, "kind": "front", "box": [r5(x0), r5(y0), zf - FT, r5(x1), r5(y1), zf]}
    if prn:
        f["print"] = pr(prn)
    return f


def door(p, m, name, x0, x1, y0, y1, zf, hinge, hx=None, hy=None, vertical=True, prn=None, extra=()):
    """A hinged inset door; the handle upright 22 mm from the free edge (hx / hy override), or horizontal."""
    f = front(f"f-{name}", x0, x1, y0, y1, zf, prn)
    if hx is None:
        hx = x1 - 22 if hinge == "left" else x0 + 22
    if hy is None:
        hy = (y0 + y1) / 2
    h = bow(f"h-{name}", hx, hy, zf, vertical)
    p += [f, h] + list(extra)
    m.append({"type": "door", "name": name, "parts": [f["id"], h["id"]] + [q["id"] for q in extra], "hinge": hinge,
              "angle": 100})


def drawer(p, m, name, x0, x1, y0, y1, zf, in0, in1, depth, prn=None, handle=True, hx=None, travel=None, bh=None):
    """An inset drawer front x0..x1 × y0..y1 (face at zf) with its box between in0 + 13 … in1 − 13, `depth` deep."""
    f = front(f"f-{name}", x0, x1, y0, y1, zf, prn)
    bx0, bx1 = in0 + 13, in1 - 13
    by0 = y0 + 10
    bh = bh or max(80, min(y1 - y0 - 40, 200))
    zb1 = zf - FT
    zb0 = zb1 - depth
    box = [
        {"id": f"{name}-side-l", "box": [bx0, by0, zb0, bx0 + T, by0 + bh, zb1]},
        {"id": f"{name}-side-r", "box": [bx1 - T, by0, zb0, bx1, by0 + bh, zb1]},
        {"id": f"{name}-back", "box": [bx0 + T, by0, zb0, bx1 - T, by0 + bh, zb0 + T]},
        {"id": f"{name}-bottom", "kind": "back", "box": [bx0 + 11, by0 + 10, zb0 + 4, bx1 - 11, by0 + 13.5, zb1 - 2]},
    ]
    parts = [f] + box
    if handle:
        parts.insert(1, bow(f"h-{name}", (x0 + x1) / 2 if hx is None else hx, (y0 + y1) / 2, zf))
    p += parts
    m.append({"type": "drawer", "name": name, "parts": [q["id"] for q in parts], "travel": travel or depth - 60})


def stack(y0, y1, hs):
    """Fronts from y0 upwards with the heights hs and 3 mm gaps (last one ends at y1): [(a, b), …] bottom first."""
    out, y = [], y0
    for i, h in enumerate(hs):
        b = y1 if i == len(hs) - 1 else y + h
        out.append((r5(y), r5(b)))
        y = b + G
    return out


def equal(y0, y1, n):
    h = (y1 - y0 - (n - 1) * G) / n
    return [(r5(y0 + i * (h + G)), r5(y0 + i * (h + G) + h)) for i in range(n)]


# ---------------------------------------------------------------------------------------------------- chests
def komod(did, W, B, H, rows, prints, hx=None):
    """Комод: the carcass, drawers in `rows` (bottom first), handles centred."""
    p = carcass(W, B, H)
    m = []
    n = len(rows)
    for i, (y0, y1) in enumerate(rows):
        k = n - i                                  # drawer_1 = the top one
        drawer(p, m, f"drawer_{k}", T + 2, W - T - 2, y0, y1, B, T, W - T, B - FT - BK - 30, prn=prints.get(k))
    return dump(did, [W, B, H], p, m)


def m_1_13():
    """Комод 910×435×749: three equal drawers (site photo П551.13: 207 / 205 / 206 at the photo's scale); the London
    skyline runs over the lower two."""
    W, B, H = 910, 435, 749
    return komod("british-bum-1-13", W, B, H, equal(F0, H - T - G, 3),
                 {2: "skyline_drawer_2", 3: "skyline_drawer_3"})


def m_1_27():
    """Комод 910×434×1074: five drawers, the top one short, the middle one ≈ 10 mm taller (site photo П551.27 and the
    p. 131 cut-out agree: 131 / 203 / 212 / 203 / 203 top to bottom); balloons over drawers 2–3, «England» on 4."""
    W, B, H = 910, 434, 1074
    return komod("british-bum-1-27", W, B, H, stack(F0, H - T - G, [203, 203, 213, 203, 131]),
                 {2: "balloons_drawer_2", 3: "balloons_drawer_3", 4: "england_drawer_4"})


# ---------------------------------------------------------------------------------------------------- wardrobes / cabinets
def doors2(W):
    """Two inset doors between the sides: 2 mm off the sides, a 3 mm joint in the middle."""
    xm = W / 2
    return (T + 2, xm - 1.5), (xm + 1.5, W - T - 2)


def m_1_25(did, H, mirror=False):
    """Шкаф для одежды 3д 1346×580: three doors 434.5 (joints at 454 / 892), a partition behind the second joint;
    left 2-door section: hat shelf + rail, right: shelves. Door 1 hinges left, doors 2 / 3 right (handles at the
    joints 1|2 and at the left edge of 3 — cut-outs p. 129 / 131). -01: a mirror 340 × 1608 on door 2."""
    W, B = 1346, 580
    yt = H - T - G
    p = carcass(W, B, H)
    m = []
    xa, xb = 454, 892                                # the joints
    p.append({"id": "partition", "box": [xb - T / 2, YB1, BK, xb + T / 2, H - T, B - FT]})
    p.append(shelf("hat-l", T, xb - T / 2, 1790, B, fixed=True))
    p.append(rail("rail", T, xb - T / 2, 1735, (B - FT) / 2))
    p.append(shelf("hat-r", xb + T / 2, W - T, 1790, B, fixed=True))
    for i, y in enumerate([420, 800, 1180]):
        p.append(shelf(f"shelf-r{i + 1}", xb + T / 2, W - T, y, B))
    hy = 1125
    door(p, m, "door_1", T + 2, xa - 1.5, F0, yt, B, "left", hy=hy, prn="flag_england_door")
    extra = []
    if mirror:
        extra = [{"id": "mirror", "kind": "mirror", "box": [503, 502, B - 3, 843, 2110, B + 1]}]
    door(p, m, "door_2", xa + 1.5, xb - 1.5, F0, yt, B, "right", hy=hy, extra=extra)
    door(p, m, "door_3", xb + 1.5, W - T - 2, F0, yt, B, "right", hy=hy, prn="lantern_london_door")
    return dump(did, [W, B, H], p, m)


def m_1_06():
    """Шкаф для одежды 2д 908×580×2205: left door over two drawers, right door full height (cut-out p. 131, the p. 130
    interior); a partition behind the joint; left: shelves, right: hat shelf + rail. The St Paul's skyline runs over
    both doors (flag + «England» on the left one)."""
    W, B, H = 908, 580, 2205
    yt = H - T - G
    p = carcass(W, B, H)
    m = []
    xa = W / 2
    p.append({"id": "partition", "box": [xa - T / 2, YB1, BK, xa + T / 2, H - T, B - FT]})
    (l0, l1), (r0, r1) = doors2(W)
    d1, d2 = (F0, 301), (304, 513)
    p.append(shelf("shelf-joint", T, xa - T / 2, 506.5, B, fixed=True))
    for i, y in enumerate([900, 1300, 1700]):
        p.append(shelf(f"shelf-l{i + 1}", T, xa - T / 2, y, B))
    p.append(shelf("hat-r", xa + T / 2, W - T, 1790, B, fixed=True))
    p.append(rail("rail", xa + T / 2, W - T, 1735, (B - FT) / 2))
    drawer(p, m, "drawer_2", l0, l1, *d1, B, T, xa - T / 2, 450)
    drawer(p, m, "drawer_1", l0, l1, *d2, B, T, xa - T / 2, 450)
    door(p, m, "door_left", l0, l1, 516, yt, B, "left", hy=1100, prn="stpauls_door_l")
    door(p, m, "door_right", r0, r1, F0, yt, B, "right", hy=1100, prn="stpauls_door_r")
    return dump("british-bum-1-06", [W, B, H], p, m)


def m_1_07():
    """Шкаф 908×434×2205: two doors (no partition) over two full-width drawers (cut-out p. 131); shelves. Balloons and
    Westminster Bridge on the left door, Big Ben on the right."""
    W, B, H = 908, 434, 2205
    yt = H - T - G
    p = carcass(W, B, H)
    m = []
    (l0, l1), (r0, r1) = doors2(W)
    p.append(shelf("shelf-joint", T, W - T, 506.5, B, fixed=True))
    for i, y in enumerate([900, 1300, 1700]):
        p.append(shelf(f"shelf-{i + 1}", T, W - T, y, B))
    drawer(p, m, "drawer_2", T + 2, W - T - 2, F0, 301, B, T, W - T, 380)
    drawer(p, m, "drawer_1", T + 2, W - T - 2, 304, 513, B, T, W - T, 380)
    door(p, m, "door_left", l0, l1, 516, yt, B, "left", hy=1060, prn="bigben_door_l")
    door(p, m, "door_right", r0, r1, 516, yt, B, "right", hy=1060, prn="bigben_door_r")
    return dump("british-bum-1-07", [W, B, H], p, m)


def m_1_04():
    """Шкаф 470×434×2205 (site drawing П551.04: door 434 × 1880, drawer 434 × 210, shelves at ≈ 683 / 1060 / 1438 /
    1811): a tall door over one drawer, the handle upright by the left edge (hinge right); Union Jack + «England» and
    the Gherkin / Big Ben street on the door."""
    W, B, H = 470, 434, 2205
    p = carcass(W, B, H)
    m = []
    p.append(shelf("shelf-joint", T, W - T, 294, B, fixed=True))
    for i, y in enumerate([667, 1044, 1422, 1795]):
        p.append(shelf(f"shelf-{i + 1}", T, W - T, y, B))
    drawer(p, m, "drawer", T + 2, W - T - 2, F0, 300, B, T, W - T, 380)
    door(p, m, "door", T + 2, W - T - 2, 304, 2184, B, "right", hx=T + 2 + 37, hy=1147, prn="gherkin_door")
    return dump("british-bum-1-04", [W, B, H], p, m)


def m_1_01():
    """Шкаф 470×434×2205 (cut-out p. 131, the p. 130 interior): two drawers, an open niche with two shelves between
    fixed shelves at 518 and 1484, a door 683 high on top with the shield-and-sword «England» print; its handle is
    horizontal, centred 55 mm over the bottom edge."""
    W, B, H = 470, 434, 2205
    p = carcass(W, B, H)
    m = []
    p.append(shelf("shelf-low", T, W - T, 518, B, fixed=True, front=B))
    p.append(shelf("shelf-1", T, W - T, 840, B, front=B + 16))
    p.append(shelf("shelf-2", T, W - T, 1162, B, front=B + 16))
    p.append(shelf("shelf-high", T, W - T, 1484, B, fixed=True, front=B))
    p.append(shelf("shelf-door", T, W - T, 1830, B))
    drawer(p, m, "drawer_2", T + 2, W - T - 2, F0, 301, B, T, W - T, 380)
    drawer(p, m, "drawer_1", T + 2, W - T - 2, 304, 515, B, T, W - T, 380)
    door(p, m, "door", T + 2, W - T - 2, 1503, H - T - G, B, "left", hx=W / 2, hy=1558, vertical=False,
         prn="shield_door")
    return dump("british-bum-1-01", [W, B, H], p, m)


def m_1_03():
    """Шкаф комбинированный 908×434×2205 (site photos П551.03, front-on and open): a two-drawer chest (full depth) with
    a stepped shelf tower on it, 290 deep: an ЛДСП back (wings 48…860 to 2132, the middle to 2189), a central column
    206…702 up to 2205, two full-width boxes 13…895 crossing it — a drop-down flap (857…1204) and two doors
    (1489…1822). «England» / football on the left door, the «10 UK England» stamp on the upper drawer."""
    W, B, H = 908, 434, 2205
    D = 290                                                  # the tower's depth (its fronts' face)
    CT = 534                                                 # the chest's top
    p = [side("side-l", 0, CT - T, B), side("side-r", W - T, CT - T, B),
         {"id": "top", "box": [0, CT - T, BK, W, CT, B]},
         {"id": "bottom", "box": [T, YB0, BK, W - T, YB1, B]},
         {"id": "plinth", "box": [T, 0, B - FT, W - T, PL, B]},
         {"id": "back", "kind": "back", "box": [0, YB0, 0, W, CT - T, BK]}]
    m = []
    drawer(p, m, "drawer_2", T + 2, W - T - 2, F0, 301, B, T, W - T, 380)
    drawer(p, m, "drawer_1", T + 2, W - T - 2, 304, 515, B, T, W - T, 380, prn="stamp_drawer")
    # the tower: ЛДСП back boards (visible oak), the column, two boxes
    cl, cr = 206, 702
    p += [{"id": "wing-l", "box": [48, CT, 0, cl, 2132, T]},
          {"id": "wing-r", "box": [cr, CT, 0, 860, 2132, T]},
          {"id": "back-mid", "box": [cl, CT, 0, cr, H - T, T]},
          {"id": "col-top", "box": [cl, H - T, 0, cr, H, D]}]
    fb0, fb1 = 857, 1204                                     # the flap box
    db0, db1 = 1489, 1822                                    # the door box
    bx0, bx1 = 13, 895
    for k, (a, b) in enumerate([(CT, fb0), (fb1, db0), (db1, H - T)]):
        p.append({"id": f"col-l{k + 1}", "box": [cl, a, T, cl + T, b, D]})
        p.append({"id": f"col-r{k + 1}", "box": [cr - T, a, T, cr, b, D]})
    for tag, (a, b) in (("flap", (fb0, fb1)), ("doors", (db0, db1))):
        p += [{"id": f"{tag}-bottom", "box": [bx0, a, T, bx1, a + T, D]},
              {"id": f"{tag}-top", "box": [bx0, b - T, T, bx1, b, D]},
              {"id": f"{tag}-side-l", "box": [bx0, a + T, T, bx0 + T, b - T, D]},
              {"id": f"{tag}-side-r", "box": [bx1 - T, a + T, T, bx1, b - T, D]}]
    p += [{"id": "doors-div-l", "box": [cl, db0 + T, T, cl + T, db1 - T, D - FT]},
          {"id": "doors-div-r", "box": [cr - T, db0 + T, T, cr, db1 - T, D - FT]}]
    fl = front("f-flap", bx0 + T + 2, bx1 - T - 2, fb0 + T + 2, fb1 - T - 2, D)
    hf = bow("h-flap", W / 2, fb1 - T - 2 - 40, D)
    p += [fl, hf]
    m.append({"type": "flap", "name": "flap", "parts": [fl["id"], hf["id"]], "hinge": "bottom", "angle": 90})
    xj = W / 2
    door(p, m, "door_left", bx0 + T + 2, xj - 1.5, db0 + T + 2, db1 - T - 2, D, "left", hx=xj - 1.5 - 25,
         prn="football_door")
    door(p, m, "door_right", xj + 1.5, bx1 - T - 2, db0 + T + 2, db1 - T - 2, D, "right", hx=xj + 1.5 + 25)
    return dump("british-bum-1-03", [W, B, H], p, m)


def m_1_09():
    """Шкаф для одежды угловой 759×759×2205 (site photos + drawing П551.09: door 432 × 2094). A 470-wide carcass box
    set diagonally into the corner (its back corners on the two walls) and two wing panels 427 deep square to the walls.
    Written in the DOOR'S axes (x along the door, z from the carcass back to the door): extent 1073.4 × 603.4 — the
    catalogue's 759 × 759 is along the walls (759·√2 = 1073.4; the room corner is 235 behind the back's middle, the
    back's two corners and the wings' back ends touch the walls); set it into a corner turned 45°. Only the wings
    are turned (rot y ±45); they start 16 mm behind the carcass' front corners (the checker tests turned parts by their
    bounding boxes — a mitred joint would read as an overlap)."""
    Ls = 759.0
    a = Ls - 470 / math.sqrt(2)                              # the wings' depth along the walls: 426.66
    W = Ls * math.sqrt(2)                                    # 1073.39
    CORNER = 235.0                                           # the room corner lies 235 behind the carcass back
    zf = (Ls + a) / math.sqrt(2) - CORNER                    # 603.38: the door plane
    xc = W / 2
    H = 2205
    zb = 0.0                                                 # the carcass back (its corners touch the two walls)
    x0, x1 = xc - 235, xc + 235
    R = lambda v: round(v, 2)
    p = [side("side-l", R(x0), H - T, R(zf), z0=zb + BK), side("side-r", R(x1 - T), H - T, R(zf), z0=zb + BK),
         {"id": "top", "box": [R(x0), H - T, zb + BK, R(x1), H, R(zf)]},
         {"id": "bottom", "box": [R(x0 + T), YB0, zb + BK, R(x1 - T), YB1, R(zf)]},
         {"id": "plinth", "box": [R(x0 + T), 0, R(zf - FT), R(x1 - T), PL, R(zf)]},
         {"id": "back", "kind": "back", "box": [R(x0), YB0, zb, R(x1), H, zb + BK]},
         {"id": "shelf-top", "box": [R(x0 + T + 1), 1941, zb + 20, R(x1 - T - 1), 1957, R(zf - FT - 20)]},
         rail("rail", R(x0 + T), R(x1 - T), 1836, R((zb + zf - FT) / 2)),
         {"id": "shelf-mid", "box": [R(x0 + T + 1), 1150, zb + 20, R(x1 - T - 1), 1166, R(zf - FT - 20)]},
         {"id": "shelf-low", "box": [R(x0 + T + 1), 290, zb + 20, R(x1 - T - 1), 306, R(zf - FT - 20)]}]
    m = []
    dx0 = xc - 216
    door(p, m, "door", R(dx0), R(xc + 216), 92, 2186, R(zf), "right", hx=R(dx0 + 25), hy=1108, prn="lamp_door")
    # the wings: outer face from the carcass' front corner to the wall point, 16 thick inwards, shortened 16 at the front
    full = (W - x1) * math.sqrt(2)                           # 426.7
    L = full - 16
    s = 1 / math.sqrt(2)
    for tag, px, ux, nx, deg in (("r", x1, s, -s, -45), ("l", x0, -s, s, 45)):
        # direction along the wing u = (ux, -s), inward normal n = (nx, -s)
        mid = 16 + L / 2
        cx = px + ux * mid + nx * 8
        cz = zf - s * mid - s * 8
        box = [R(cx - 8), 0, R(cz - L / 2), R(cx + 8), H, R(cz + L / 2)]
        z0 = box[2]
        out = (f"M {R(z0 + NOTCH)} 0 L {box[5]} 0 L {box[5]} {H} L {z0} {H} L {z0} {NOTCH} "
               f"Q {R(z0 + NOTCH - 8)} {NOTCH - 6} {R(z0 + NOTCH + 5)} 0 Z")
        p.append({"id": f"wing-{tag}", "box": box, "rot": {"axis": "y", "deg": deg, "about": [R(cx), 0, R(cz)]},
                  "shape": "path", "outline": out})
    return dump("british-bum-1-09", [R(W), R(zf), H], p, m)


# ---------------------------------------------------------------------------------------------------- desks, shelf
DT = 749 - T                                                  # 733: the desk top's underside


def pedestal(p, m, x0, B, tag, prints=("england_drawer_s", "bus_drawer_s")):
    """The desk pedestal 404 wide: open niche on top (a fixed shelf 518…534), two drawers (site photos П551.17)."""
    W = 404
    x1 = x0 + W
    p += [side(f"ped{tag}-side-l", x0, DT, B), side(f"ped{tag}-side-r", x1 - T, DT, B),
          {"id": f"ped{tag}-bottom", "box": [x0 + T, YB0, BK, x1 - T, YB1, B]},
          {"id": f"ped{tag}-plinth", "box": [x0 + T, 0, B - FT, x1 - T, PL, B]},
          {"id": f"ped{tag}-shelf", "box": [x0 + T, 518, BK, x1 - T, 534, B]},
          {"id": f"ped{tag}-back", "kind": "back", "box": [x0, YB0, 0, x1, DT, BK]}]
    drawer(p, m, f"drawer{tag}_2", x0 + T + 2, x1 - T - 2, F0, 301, B, x0 + T, x1 - T, 450, prn=prints[1])
    drawer(p, m, f"drawer{tag}_1", x0 + T + 2, x1 - T - 2, 304, 515, B, x0 + T, x1 - T, 450, prn=prints[0])


def mirror_x(parts, moves, W):
    """The mirror image of a design about x = W/2 (hinges swap; outlines in the top / front plane flip)."""
    def fx(v):
        return round(W - v, 2)
    out = []
    for q in parts:
        q = json.loads(json.dumps(q))
        if "box" in q:
            b = q["box"]
            q["box"] = [fx(b[3]), b[1], b[2], fx(b[0]), b[4], b[5]]
        if "at" in q:
            q["at"] = [fx(q["at"][0]), q["at"][1]]
        if q.get("outline") and q.get("plane_x"):
            pass
        out.append(q)
    mv = []
    for q in moves:
        q = dict(q)
        if q.get("hinge") in ("left", "right"):
            q["hinge"] = "right" if q["hinge"] == "left" else "left"
        mv.append(q)
    return out, mv


def desk_217(mirror=False):
    """Стол письменный угловой 1340×890×749 (site photos П551.17 / 17-01, cut-out p. 131): an L top — 590 deep along
    the back, the right 300 coming forward to 890 with a concave curve at the inner corner —, the pedestal (404) at the
    left, an ЛДСП modesty panel at the back, the return on two leg panels (front and back, 20 in from its edges).
    -01 is the mirror image."""
    W, B, H = 1340, 890, 749
    BD = 590                                                  # the long arm's depth
    xr = 1040                                                 # the return's inner edge
    p, m = [], []
    outline = f"M 0 0 L {W} 0 L {W} {B} L {xr} {B} L {xr} 770 C {xr} 670 980 {BD} 860 {BD} L 0 {BD} Z"
    pedestal(p, m, 0, BD, "")
    p += [{"id": "modesty", "box": [404, 490, 0, xr + 20, DT, T]},
          {"id": "leg-back", "box": [xr + 20, 0, 0, W - 20, 490, T]},
          {"id": "leg-back-top", "box": [xr + 20, 490, 0, W - 20, DT, T]},
          {"id": "leg-front", "box": [xr + 20, 0, B - 16 - T, W - 20, DT, B - 16]}]
    top = {"id": "top", "box": [0, DT, 0, W, H, B], "shape": "path", "outline": outline}
    p.append(top)
    did = "british-bum-2-17"
    if mirror:
        p, m = mirror_x(p, m, W)
        for q in p:
            if q["id"] == "top":
                q["outline"] = (f"M {W} 0 L 0 0 L 0 {B} L {W - xr} {B} L {W - xr} 770 "
                                f"C {W - xr} 670 {W - 980} {BD} {W - 860} {BD} L {W} {BD} Z")
            if q.get("shape") == "path" and q["id"] != "top":
                pass
        did = "british-bum-2-17-01"
    return dump(did, [W, B, H], p, m)


def m_2_16():
    """Стол письменный 1100×590×749 (cut-out p. 131): a leg panel at the left, the pedestal of 2.17 at the right,
    a modesty panel between; «England» / the bus on the drawers."""
    W, B, H = 1100, 590, 749
    p, m = [], []
    p.append(side("leg-l", 0, DT, B))
    pedestal(p, m, W - 404, B, "")
    p += [{"id": "modesty", "box": [T, 490, 0, W - 404, DT, T]},
          {"id": "top", "box": [0, DT, 0, W, H, B]}]
    return dump("british-bum-2-16", [W, B, H], p, m)


def m_2_15():
    """Стол письменный 2т 1400×590×749 (cut-out p. 131, the p. 130 interior): two pedestals 430 wide, each a short
    drawer (580…730) over a door (90…577, horizontal handle 122 under its top edge, a shelf behind); the doors carry
    Tower Bridge («Wow» on the left one)."""
    W, B, H = 1400, 590, 749
    PW = 430
    p, m = [], []
    for tag, x0, hinge, prn in (("l", 0, "left", "towerbridge_door_l"), ("r", W - PW, "right", "towerbridge_door_r")):
        x1 = x0 + PW
        p += [side(f"ped{tag}-side-l", x0, DT, B), side(f"ped{tag}-side-r", x1 - T, DT, B),
              {"id": f"ped{tag}-bottom", "box": [x0 + T, YB0, BK, x1 - T, YB1, B]},
              {"id": f"ped{tag}-plinth", "box": [x0 + T, 0, B - FT, x1 - T, PL, B]},
              {"id": f"ped{tag}-rail", "box": [x0 + T, 570.5, BK, x1 - T, 586.5, B - FT]},
              {"id": f"ped{tag}-shelf", "box": [x0 + T + 1, 320, BK + 20, x1 - T - 1, 336, B - FT - 20]},
              {"id": f"ped{tag}-back", "kind": "back", "box": [x0, YB0, 0, x1, DT, BK]}]
        drawer(p, m, f"drawer_{tag}", x0 + T + 2, x1 - T - 2, 580, 730, B, x0 + T, x1 - T, 450, bh=110)
        door(p, m, f"door_{tag}", x0 + T + 2, x1 - T - 2, F0, 577, B, hinge, hx=(x0 + x1) / 2, hy=455, vertical=False,
             prn=prn)
    p += [{"id": "modesty", "box": [PW, 490, 0, W - PW, DT, T]},
          {"id": "top", "box": [0, DT, 0, W, H, B]}]
    return dump("british-bum-2-15", [W, B, H], p, m)


def m_2_18():
    """Полка 1340×340×1124 (a hutch over the desk; cut-out p. 131, the p. 130 interior): a left side, a shelf block of
    three compartments (bottom board at 750) over an open window, a back stretcher 100 at the bottom, the right column
    (958…1340): the umbrella door (442…1105), an open niche between fixed shelves, a small drawer at the bottom."""
    W, B, H = 1340, 340, 1124
    cx0 = 958
    p, m = [], []
    p += [{"id": "side-l", "box": [0, 0, BK, T, H - T, B]},
          {"id": "col-side-l", "box": [cx0, 0, BK, cx0 + T, H - T, B]},
          {"id": "col-side-r", "box": [W - T, 0, BK, W, H - T, B]},
          {"id": "top", "box": [0, H - T, BK, W, H, B]},
          {"id": "block-bottom", "box": [T, 750, BK, cx0, 766, B]},
          {"id": "block-back", "kind": "back", "mat": "body", "box": [T, 750, 0, cx0, H - T, BK]},
          {"id": "stretcher", "box": [T, 0, BK, cx0, 100, BK + T]}]
    inner = (cx0 - T - 2 * T) / 3
    for i in range(2):
        xa = T + (i + 1) * inner + i * T
        p.append({"id": f"divider-{i + 1}", "box": [r5(xa), 766, BK, r5(xa + T), H - T, B]})
    c0, c1 = cx0 + T, W - T
    p += [{"id": "col-bottom", "box": [c0, 0, BK, c1, T, B]},
          {"id": "col-shelf-low", "box": [c0, 124, BK, c1, 140, B]},
          {"id": "col-shelf-high", "box": [c0, 424, BK, c1, 440, B]},
          {"id": "col-shelf-door", "box": [c0 + 1, 770, BK + 20, c1 - 1, 786, B - FT - 20]},
          {"id": "col-back", "kind": "back", "mat": "body", "box": [cx0, 0, 0, W, H - T, BK]}]
    drawer(p, m, "drawer", c0 + 2, c1 - 2, 18, 121, B, c0, c1, 280, bh=80)
    door(p, m, "door", c0 + 2, c1 - 2, 442, H - T - G, B, "right", hx=(c0 + c1) / 2, hy=496, vertical=False,
         prn="umbrella_door")
    return dump("british-bum-2-18", [W, B, H], p, m)


# ---------------------------------------------------------------------------------------------------- beds
def bed_108(did, soft=False):
    """Кровать 1-08 2042×839×650, sleeping 2000×800, written along its length (x = length, z = depth; the drawers'
    side is the front, as the catalogue draws it): two end boards 16 with a rounded front-top corner (R 200), a back
    board, a front rail 130 over two under-bed drawers (bus + stamp, London Eye + «England»; no handles — the grip is
    the shadow gap under the rail), an ЛДСП base at 426…442, a middle support, the mattress 120.
    1.34 adds the buttoned upholstered back (soft, tufts) on a backing board: it stands ≈ 150 over the end boards on the
    cut-out (H 800, the catalogue writes 650 for both)."""
    L, B = 2042, 839
    H = 800 if soft else 650
    HE = 650                                                  # the end boards and the back board
    rt = 442                                                  # the rail's top = the base's top
    p, m = [], []
    end = (f"M 0 0 L {B} 0 L {B} 450 C {B} 560 {B - 90} {HE} {B - 200} {HE} L 0 {HE} Z")
    p += [{"id": "end-l", "box": [0, 0, 0, T, HE, B], "shape": "path", "outline": end},
          {"id": "end-r", "box": [L - T, 0, 0, L, HE, B], "shape": "path", "outline": end},
          {"id": "back-board", "box": [T, 60, 0, L - T, HE, T]},
          {"id": "rail", "box": [T, 312, B - T, L - T, rt, B]},
          {"id": "base", "box": [T, rt - T, T, L - T, rt, B - T]},
          {"id": "support", "box": [L / 2 - 8, 0, T, L / 2 + 8, rt - T, B - T - 2]},
          {"id": "mattress", "kind": "mattress", "box": [21, rt, 23, 2021, rt + 120, 823]}]
    xs = [(T + 2, L / 2 - 8 - 2), (L / 2 + 8 + 2, L - T - 2)]
    for i, ((x0, x1), prn) in enumerate(zip(xs, ("bus_stamp_drawer", "eye_england_drawer"))):
        drawer(p, m, f"drawer_{i + 1}", x0, x1, 20, 300, B, x0 - 2 if i == 0 else L / 2 + 8,
               L / 2 - 8 if i == 0 else L - T, 700, prn=prn, handle=False, travel=550, bh=220)
    if soft:
        p += [{"id": "cushion-board", "box": [36, HE, 0, L - 36, H - 10, T]},
              {"id": "cushion", "kind": "soft", "mat": "fabric", "tufts": [17, 3], "box": [36, 470, T, L - 36, H, T + 60]}]
    return dump(did, [L, B, H], p, m)


def bed_112():
    """Кровать 1-12 1244×2092×850, sleeping 2000×1200 (cut-out p. 131, the p. 131 interior): x = width, z = length
    (the headboard at the back). The headboard board 850 with a buttoned upholstered panel (soft, tufts) over the
    mattress, side boards and a foot board 400 high to the floor, an ЛДСП base at 264…280 on a middle support, the
    mattress 200."""
    W, L, H = 1244, 2092, 850
    HS = 400
    p, m = [], []
    p += [{"id": "headboard", "box": [0, 0, 0, W, H, T]},
          {"id": "head-panel", "kind": "soft", "mat": "fabric_light", "tufts": [9, 2], "box": [40, 500, T, W - 40, 820, T + 50]},
          {"id": "side-l", "box": [0, 0, T, T, HS, L - T]},
          {"id": "side-r", "box": [W - T, 0, T, W, HS, L - T]},
          {"id": "foot", "box": [0, 0, L - T, W, HS, L]},
          {"id": "base", "box": [T, 264, T, W - T, 280, L - T]},
          {"id": "support", "box": [W / 2 - 8, 0, T, W / 2 + 8, 264, L - T]},
          {"id": "mattress", "kind": "mattress", "box": [22, 280, 76, 1222, 480, 2076]}]
    return dump("british-bum-1-32", [W, L, H], p, m)


def loft_123():
    """Кровать двухъярусная (loft) 2981×890×2205, sleeping 2000×800 (cut-out p. 131, the p. 130 interior — there the
    1-08 bed stands under it). Left to right: the stair-chest (0…500: four drawer steps rising from the front to the
    back, 178 deep and ≈ 310 high each, an S-curved left side, the top landing at the bed's level), the Big Ben
    wardrobe column (500…960) under the bed's head end, the open space under the bed with an ЛДСП back panel and a
    rack of five compartments, the guard cabinet (2516…2981) at the foot end over the bed's level on a full-height
    right end panel. The bed: an ЛДСП base at 1484…1500, the printed front board to 1720 (rounded at the head end),
    a back rail to 1860, the head end board, the mattress 120. Assembled with the stairs on the left, as shown."""
    W, B, H = 2981, 890, 2205
    p, m = [], []
    BED = 1500                                                # the base's top
    # --- the stair-chest
    tops = [370, 680, 990, 1300, BED]
    band = 178
    zf = [B - k * band for k in range(5)]                     # the fronts of the five bands (890, 712, …, 178)
    pts = [(B, 380)] + [(zf[k], tops[k] + 10) for k in range(1, 5)]
    path = f"M {BK} 0 L {B} 0 L {pts[0][0]} {pts[0][1]}"
    for (za, ya), (zb, yb) in zip(pts, pts[1:]):
        path += f" C {za} {r5(ya + (yb - ya) * 0.7)} {zb + 60} {yb} {zb} {yb}"
    path += f" L {BK} {BED + 10} Z"
    p += [{"id": "stair-side", "box": [0, 0, BK, T, BED + 10, B], "shape": "path", "outline": path},
          {"id": "stair-bottom", "box": [T, YB0, BK, 500, YB1, B]},
          {"id": "stair-plinth", "box": [T, 0, B - FT, 500, PL, B]},
          {"id": "stair-back", "kind": "back", "box": [T, YB0, 0, 500, BED, BK]}]
    for k in range(4):
        p.append({"id": f"tread-{k + 1}", "box": [T, tops[k] - T, BK, 500, tops[k], zf[k]]})
    p.append({"id": "landing", "box": [T, BED - T, BK, 500, BED, zf[4]]})
    for k in range(4):
        y0 = F0 if k == 0 else tops[k - 1] + 2
        y1 = tops[k] - T - 2
        drawer(p, m, f"step_{k + 1}", T + 2, 498, y0, y1, zf[k], T, 500, min(zf[k] - FT - 20, 560),
               bh=min(y1 - y0 - 40, 200))
    # --- the Big Ben column
    c0, c1 = 500, 960
    p += [side("col-side-l", c0, BED - T, B), side("col-side-r", c1 - T, BED - T, B),
          {"id": "col-bottom", "box": [c0 + T, YB0, BK, c1 - T, YB1, B]},
          {"id": "col-plinth", "box": [c0 + T, 0, B - FT, c1 - T, PL, B]},
          {"id": "col-back", "kind": "back", "box": [c0, YB0, 0, c1, BED - T, BK]}]
    for i, y in enumerate([420, 770, 1120]):
        p.append(shelf(f"col-shelf-{i + 1}", c0 + T, c1 - T, y, B))
    door(p, m, "door_column", c0 + T + 2, c1 - T - 2, F0, BED - T - 3, B, "right", hx=(c0 + c1) / 2, hy=790,
         vertical=False, prn="bigben_column_door")
    # --- the right end panel, the under-bed back and rack
    p.append(side("end-r", W - T, H, B))
    p.append({"id": "rack-back", "box": [c1, 750, BK, W - T, BED - T, BK + T]})
    p.append({"id": "rack-shelf", "box": [c1, 1184, BK + T, W - T, 1200, 269]})
    span = (W - T - c1 - 4 * T) / 5
    for i in range(4):
        xa = c1 + (i + 1) * span + i * T
        p.append({"id": f"rack-div-{i + 1}", "box": [r5(xa), 1200, BK + T, r5(xa + T), BED - T, 269]})
    # --- the bed
    xh, xf = c0, 2516                                         # the head end board, the cabinet's side (foot end)
    p += [{"id": "base", "box": [c0, BED - T, BK, W - T, BED, B - T]},
          {"id": "front-board", "box": [xh, BED - T, B - T, xf, 1720, B], "print": pr("london_rail"), "shape": "path",
           "outline": f"M {xh} {BED - T} L {xf} {BED - T} L {xf} 1720 L {xh + 110} 1720 Q {xh} 1720 {xh} 1610 Z"},
          {"id": "head-board", "box": [xh, BED, BK, xh + T, 1720, B - T], "shape": "path",
           "outline": f"M {BK} {BED} L {B - T} {BED} L {B - T} 1610 Q {B - T} 1720 {B - T - 110} 1720 L {BK} 1720 Z"},
          {"id": "back-rail", "box": [xh + T, BED, BK, xf, 1860, BK + T]},
          {"id": "mattress", "kind": "mattress", "box": [xh + T, BED, 47, xh + T + 2000, BED + 120, 847]}]
    # --- the guard cabinet
    g0 = xf
    p += [{"id": "cab-side-l", "box": [g0, BED, BK, g0 + T, H - T, B]},
          {"id": "cab-top", "box": [g0, H - T, BK, W - T, H, B]},
          {"id": "cab-back", "kind": "back", "box": [g0, BED, 0, W, H, BK]},
          shelf("cab-shelf", g0 + T, W - T, 1850, B)]
    door(p, m, "door_cabinet", g0 + T + 2, W - T - 2, BED + 2, H - T - G, B, "left", hx=(g0 + T + W - T) / 2,
         hy=BED + 52, vertical=False, prn="guard_door")
    return dump("british-bum-1-23", [W, B, H], p, m)


# ---------------------------------------------------------------------------------------------------- catalogue
MODELS = [
    ("1.25", "Шкаф для одежды 3д «Бритиш Бум»", "kids", [1346, 580, 2200], "по каталогу (вырезка с. 131, интерьер с. 129), без инструкции"),
    ("1.25-01", "Шкаф для одежды 3д «Бритиш Бум» с зеркалом", "kids", [1346, 580, 2205], "по каталогу (вырезка с. 131), без инструкции; зеркало на средней двери"),
    ("1.32", "Кровать 1-12 «Бритиш Бум»", "kids", [1244, 2092, 850], "по каталогу (вырезка и интерьер с. 131), без инструкции; спальное место 2000×1200; мягкое изголовье с каретной стяжкой"),
    ("1.27", "Комод «Бритиш Бум»", "kids", [910, 434, 1074], "по фото сайта (П551.27) и вырезке с. 131, без инструкции; L 910 по с. 131 (с. 129: 908), H 1074 по каталогу (сайт: 1095)"),
    ("1.13", "Комод «Бритиш Бум»", "kids", [910, 435, 749], "по фото сайта (П551.13), без инструкции"),
    ("2.17", "Стол письменный угловой «Бритиш Бум»", "kids", [1340, 890, 749], "по фото сайта (П551.17) и вырезке с. 131, без инструкции"),
    ("2.17-01", "Стол письменный угловой «Бритиш Бум» (зеркальный)", "kids", [1340, 890, 749], "по фото сайта (П551.17-01), без инструкции; зеркальное отражение 2.17"),
    ("1.01", "Шкаф «Бритиш Бум»", "kids", [470, 434, 2205], "по каталогу (вырезка с. 131, интерьер с. 130), без инструкции"),
    ("1.06", "Шкаф для одежды 2д «Бритиш Бум»", "kids", [908, 580, 2205], "по каталогу (вырезка с. 131, интерьер с. 130), без инструкции"),
    ("1.23", "Кровать двухъярусная «Бритиш Бум»", "kids", [2981, 890, 2205], "по каталогу (вырезка с. 131, интерьер с. 130), без инструкции; спальное место 2000×800; кровать-чердак: лестница-комод слева, шкаф-колонна, шкаф наверху, стеллаж под кроватью (нижнее место — кровать 1-08 отдельно); возможна и правосторонняя сборка"),
    ("2.18", "Полка «Бритиш Бум»", "kids", [1340, 340, 1124], "по каталогу (вырезка с. 131, интерьер с. 130), без инструкции; надстройка над столом"),
    ("2.15", "Стол письменный 2т «Бритиш Бум»", "kids", [1400, 590, 749], "по каталогу (вырезка с. 131, интерьер с. 130), без инструкции"),
    ("1.04", "Шкаф «Бритиш Бум»", "kids", [470, 434, 2205], "по фото и чертежу сайта (П551.04), без инструкции"),
    ("1.03", "Шкаф комбинированный «Бритиш Бум»", "kids", [908, 434, 2205], "по фото сайта (П551.03), без инструкции"),
    ("2.16", "Стол письменный «Бритиш Бум»", "kids", [1100, 590, 749], "по каталогу (вырезка с. 131), без инструкции"),
    ("1.07", "Шкаф «Бритиш Бум»", "kids", [908, 434, 2205], "по каталогу (вырезка с. 131), без инструкции"),
    ("1.09", "Шкаф для одежды угловой «Бритиш Бум»", "kids", [1073.39, 603.38, 2205], "по фото и чертежу сайта (П551.09), без инструкции; каталог L759×B759 — вдоль стен; модель в осях двери (x вдоль двери, z от задней стенки к двери): 1073×603, угол комнаты в 235 за серединой задней стенки; ставить в угол с поворотом 45°"),
    ("1.20", "Кровать 1-08 «Бритиш Бум»", "kids", [2042, 839, 650], "по каталогу (вырезка с. 131, интерьер с. 130), без инструкции; спальное место 2000×800; x — вдоль кровати (сторона ящиков — фасад)"),
    ("1.34", "Кровать 1-08 «Бритиш Бум» с мягкой спинкой", "kids", [2042, 839, 800], "по каталогу (вырезка с. 131), без инструкции; спальное место 2000×800; x — вдоль кровати; мягкая спинка с каретной стяжкой выше боковин ≈ на 150 по вырезке — H 800 (каталог пишет H650, как у 1.20)"),
]


def catalog():
    fin = {"id": "british-bum-krem-tryufel", "name": "Крем / Дуб Трюфельный",
           "body": "door_enamel_whitey#786657", "front": "door_enamel_whitey#e0d6cd", "back": "door_enamel_whitey#e0d6cd",
           "swatch": "#e0d6cd",
           "roles": {"fabric": "door_enamel_whitey#9e958e", "fabric_light": "door_enamel_whitey#bfbbb2"}}
    col = {"id": "british-bum", "name": "Бритиш Бум", "brand": "Пинскдрев", "finishes": [fin["id"]], "metal": "chrome",
           "note": ("Каталог «Корпусная мебель ч. II» 2025, с. 129–131 (разворот 254–259); все модули по каталогу / фото "
                    "сайта (pinskdrev.by «Бритиш» П551.xx), без инструкций. Детская: корпус ЛДСП 16 «Дуб Трюфельный» "
                    "(боковины до пола с вырезом под плинтус, крышка на боковинах, цоколь 72 заподлицо с фасадами), "
                    "вкладные фасады «Крем» с цветной фотопечатью (рисунки Лондона), ручки-скобы ≈ 184 мм, "
                    "задняя стенка ХДФ накладная.")}
    models = []
    for code, name, cat, size, note in MODELS:
        e = {"id": "british-bum-" + code.replace(".", "-"), "code": f"П3.0551.{code}", "name": name,
             "collection": "british-bum", "category": cat, "size": size, "page": 131, "note": note}
        if code == "2.18":
            e["mount"] = "wall"
        models.append(e)
    return {"finishes": [fin], "profiles": {}, "collections": [col], "models": models}


def main():
    m_1_13()
    m_1_27()
    m_1_25("british-bum-1-25", 2200)
    m_1_25("british-bum-1-25-01", 2205, mirror=True)
    m_1_06()
    m_1_07()
    m_1_04()
    m_1_01()
    m_1_03()
    m_1_09()
    desk_217()
    desk_217(mirror=True)
    m_2_16()
    m_2_15()
    m_2_18()
    bed_108("british-bum-1-20")
    bed_108("british-bum-1-34", soft=True)
    bed_112()
    loft_123()
    with open(os.path.join(HERE, "british-bum_catalog.json"), "w") as fh:
        json.dump(catalog(), fh, ensure_ascii=False, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()
