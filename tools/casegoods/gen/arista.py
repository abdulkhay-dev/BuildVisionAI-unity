"""«Ариста» (Пинскдрев, каталог «Корпусная мебель ч. II», с. 28–30): 21 articles.

Construction (from the only instruction, the 4-door wardrobe П3.593.1.31): carcass ЛДСП 16 «Персидский жемчуг» — the top
and the base span the sides, the sides stand between them; inner parts (partitions, shelves, rails) ЛДСП 16 white; back
ХДФ 3 white nailed onto the rear edges (in pieces joined over fixed horizontals); the top is 16 deeper than the sides and
reaches over the fronts to 3 mm behind their face; fronts МДФ 19 «Беж нубук» and «Дуб Артизан Трюфель», overlay, 3 mm
gaps; a two-colour door is two boards glued edge to edge (oak strip + beige panel); bracket handles AKS PS36 (160 mm
centres, black); wardrobes stand on 88×54×20 adjustable glides, the living and bedroom pieces on black square tapered
legs that splay outwards. The other 20 articles are built "by catalogue" (the cut-outs of p. 30, the interiors of
p. 28–29) the same way.

Coordinates (Docs/casegoods-designs.md): x left→right, y up from the floor, z from the wall (0) to the front.
    python3 tools/casegoods/gen/arista.py            # writes the designs and gen/arista_catalog.json
"""
import json
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
T = 16      # ЛДСП
F = 19      # МДФ fronts
BK = 3      # ХДФ back, nailed on the rear edges
G = 3       # gap between fronts

# ------------------------------------------------------------------------------------------------ helpers


def box(pid, b, n=None, **kw):
    p = {}
    if n is not None:
        p["n"] = n
    if pid is not None and pid != n:
        p["id"] = pid
    p.update(kw)
    p["box"] = [round(v, 1) for v in b]
    return p


def handle(tag, x, y, zf, axis="y", L=176, so=22, s=10):
    """Bracket handle AKS PS36 (black, square 10 mm, ~176 long): a `bar` handle centred at (x, y) on the face zf,
    vertical (axis y) or horizontal (axis x). It stands out of the catalogue depth (B = carcass + fronts)."""
    return [{"id": f"h-{tag}", "kind": "handle", "model": "bar", "at": [x, y], "dir": "up" if axis == "y" else "right",
             "d": L, "band": s, "t": s, "standoff": so, "z": zf, "covers": ["c3"]}]


def ids(parts):
    return [p.get("id") or p.get("n") for p in parts]


def leg(tag, x, z, top, dx=0, dz=0, d=40, d2=30, glide=3):
    """Black square tapered leg from the carcass bottom (y = top) to a felt glide on the floor; the foot is offset by
    (dx, dz) — a splayed leg. The rod has no box, the glide gives the floor line."""
    xb, zb = x + dx, z + dz
    return [{"id": f"leg-{tag}", "kind": "rod", "mat": "metal", "section": "square", "d": d, "d2": d2,
             "from": [x, top, z], "to": [xb, glide, zb], "covers": ["g"]},
            {"id": f"leg-{tag}-glide", "kind": "panel", "mat": "black", "edge": 0.5,
             "box": [xb - d2 / 2, 0, zb - d2 / 2, xb + d2 / 2, glide, zb + d2 / 2]}]


def glides(xs, zs, w=88, d=54, h=20):
    """Adjustable glides 88×54×20 (the wardrobes): plastic blocks under the base."""
    out, k = [], 0
    for x in xs:
        for z in zs:
            k += 1
            out.append({"id": f"k2-{k}", "kind": "panel", "mat": "black", "edge": 2,
                        "box": [x - w / 2, 0, z - d / 2, x + w / 2, h, z + d / 2], "covers": ["k2"]})
    return out


def drawer(tag, front, box_x, y0, h, z0, zf, fmat=None, handle_at=None, n=None):
    """A drawer: the front (list of boxes or one), a box of ЛДСП 16 white (sides, back, front-less: the front is the
    front) with an ХДФ bottom in grooves, and a handle. Returns (parts, move)."""
    x0, x1 = box_x
    fr = []
    fronts = front if isinstance(front[0], (list, tuple)) else [front]
    for i, b in enumerate(fronts):
        p = {"id": f"d{tag}-front" + (f"-{i + 1}" if len(fronts) > 1 else ""), "kind": "front", "box": list(b)}
        m = (fmat[i] if isinstance(fmat, (list, tuple)) else fmat)
        if m:
            p["mat"] = m
        fr.append(p)
    bx = [
        {"id": f"d{tag}-side-l", "mat": "white", "box": [x0, y0, z0, x0 + T, y0 + h, zf]},
        {"id": f"d{tag}-side-r", "mat": "white", "box": [x1 - T, y0, z0, x1, y0 + h, zf]},
        {"id": f"d{tag}-back", "mat": "white", "box": [x0 + T, y0, z0, x1 - T, y0 + h, z0 + T]},
        {"id": f"d{tag}-bottom", "kind": "back", "mat": "white", "box": [x0 + 10, y0 + 8, z0 + 6, x1 - 10, y0 + 11, zf - 2]},
    ]
    parts = fr + bx
    zface = max(b[5] for b in fronts)
    for i, at in enumerate(handle_at or []):
        parts += handle(f"d{tag}" + (f"-{i + 1}" if len(handle_at) > 1 else ""), at[0], at[1], zface, axis="x")
    parts = [dict(p, box=[round(v, 1) for v in p["box"]]) if "box" in p else p for p in parts]
    return parts, {"type": "drawer", "name": f"drawer_{tag}", "parts": ids(parts), "travel": round((zf - z0) * 0.8)}


def door(name, parts, hinge, axis=None, angle=100):
    mv = {"type": "door", "name": name, "parts": ids(parts), "hinge": hinge, "angle": angle}
    if axis:
        mv["axis"] = axis
    return mv


# ------------------------------------------------------------------------------------------------ catalogue
MODELS = []


def model(mid, code, name, category, size, page, note, **kw):
    m = {"id": mid, "code": code, "name": name, "collection": "arista", "category": category, "size": size}
    m.update(kw)
    m["page"] = page
    if note:
        m["note"] = note
    MODELS.append(m)


BYCAT = "по каталогу, без инструкции"

# ------------------------------------------------------------------------------------------------ 4-door wardrobe


def w131():
    """Шкаф для одежды 4Д П3.593.1.31 (instruction IS-Arista-PZ-593-1-31): 1802 × 582 × 2292."""
    W, H = 1802, 2292
    zb, zc = BK, BK + 560          # carcass from the back (nailed on z 0..3) to its front edge
    zf = zc + F                    # door face = 582
    yb, yt = 20, H - T             # base on the glides; top underside
    p = [
        box("1", [0, yt, zb, W, H, zb + 576], "1"),
        box("2", [0, yb, zb, W, yb + T, zc], "2"),
        box("3", [0, yb + T, zb, T, yt, zc], "3"),
        box("4", [W - T, yb + T, zb, W, yt, zc], "4"),
        box("5", [893, yb + T, zb, 909, yt, zc], "5", mat="white"),
    ]
    # fixed horizontals on the back joints (y 408, 1156, 1904): left 3 (bottom, middle, top), right 2 (bottom, top)
    for i, (x0, y0) in enumerate([(16.5, 400), (16.5, 1148), (16.5, 1896), (909.5, 400), (909.5, 1896)]):
        p.append(box(f"7-{i + 1}", [x0, y0, zb, x0 + 876, y0 + T, zb + 559], "7", mat="white"))
    for i, y0 in enumerate([774, 1522]):
        p.append(box(f"6-{i + 1}", [17.5, y0, zb + 7, 891.5, y0 + T, zb + 557], "6", mat="white"))
    # the right compartment: a rail at the back under the middle joint of the back, the oval hanger rail under the top shelf
    p.append(box("10", [909.5, 1092, zb, 1785.5, 1220, zb + T], "10", mat="white"))
    p.append({"id": "z6", "kind": "tube", "mat": "chrome", "box": [913.5, 1815, 276, 1782.5, 1845, 291], "covers": ["z6", "d4", "d4"]})
    # back: per half a 386 piece at the bottom and at the top, between them 2 × 2 pieces 448 × 746 on a joining profile
    for h, x0 in enumerate([2, 902]):
        p.append(box(f"11-{2 * h + 1}", [x0, 21, 0, x0 + 898, 407, BK], "11", kind="back", mat="white"))
        p.append(box(f"11-{2 * h + 2}", [x0, 1905, 0, x0 + 898, 2291, BK], "11", kind="back", mat="white"))
        k = 0
        for y0 in (409, 1157):
            for xx in (x0, x0 + 450):
                k += 1
                p.append(box(f"12-{4 * h + k}", [xx, y0, 0, xx + 448, y0 + 746, BK], "12", kind="back", mat="white"))
    # doors: 4 × 446 (the outer ones: oak strip 160 + beige 286), 3 mm gaps, 2 mm under the top
    y0, y1 = 22, 22 + 2252
    d1 = [box("13-1", [4.5, y0, zc, 164.5, y1, zf], "13", kind="front", mat="accent", grain="y"),
          box("14-1", [164.5, y0, zc, 450.5, y1, zf], "14", kind="front")]
    d2 = [box("15-1", [453.5, y0, zc, 899.5, y1, zf], "15", kind="front")]
    d3 = [box("15-2", [902.5, y0, zc, 1348.5, y1, zf], "15", kind="front")]
    d4 = [box("14-2", [1351.5, y0, zc, 1637.5, y1, zf], "14", kind="front"),
          box("13-2", [1637.5, y0, zc, 1797.5, y1, zf], "13", kind="front", mat="accent", grain="y")]
    hy = 1150
    d1 += handle("1", 388, hy, zf)
    d2 += handle("2", 516, hy, zf)
    d3 += handle("3", 1286, hy, zf)
    d4 += handle("4", 1414, hy, zf)
    p += d1 + d2 + d3 + d4
    p += glides([64, 901, 1738], [BK + 30, zc - 30])
    moves = [door("door_1", d1, "left", [4.5, zf]), door("door_2", d2, "right"),
             door("door_3", d3, "left"), door("door_4", d4, "right", [1797.5, zf])]
    model("arista-1-31", "П3.593.1.31", "Шкаф для одежды 4Д «Ариста»", "bedroom", [1802, 582, 2292], 30,
          "по инструкции; наружные двери — щит дуба 160 + щит беж 286", **{"is": "IS-Arista-PZ-593-1-31---SHkaf-dlya-odejdyi-4D.pdf"})
    return dump("arista-1-31", [W, 582, H], p, moves)


# ------------------------------------------------------------------------------------------------ by catalogue: helpers


def carcass(W, H, Ds, LH, top_over=16, back=True, body_top="body"):
    """Carcass of the collection: base and top over the full width, sides between them, the back nailed on (z 0..3).
    Ds = side depth; the top reaches 16 further (over the fronts). Returns parts and zc (the carcass front)."""
    zb, zc = BK, BK + Ds
    p = [
        {"id": "top", "mat": body_top, "box": [0, H - T, zb, W, H, zc + top_over]},
        {"id": "base", "box": [0, LH, zb, W, LH + T, zc]},
        {"id": "side-l", "box": [0, LH + T, zb, T, H - T, zc]},
        {"id": "side-r", "box": [W - T, LH + T, zb, W, H - T, zc]},
    ]
    if back:
        p.append({"id": "back", "kind": "back", "mat": "white", "box": [1, LH + 1, 0, W - 1, H - 1, BK]})
    return p, zc


def legs4(xs, zs, LH, splay=10, extra=(), pre=""):
    """Black tapered legs splayed outwards (a few mm) at the carcass corners; `extra` = more (x, z) without splay."""
    out, k, xm, zm = [], 0, sum(xs) / len(xs), sum(zs) / len(zs)
    for x in xs:
        for z in zs:
            k += 1
            out += leg(f"{pre}{k}", x, z, LH, dx=splay if x > xm else -splay, dz=(splay * 0.6 if z > zm else -splay * 0.6))
    for x, z in extra:
        k += 1
        out += leg(f"{pre}{k}", x, z, LH)
    return out


def shelf(pid, x0, x1, y, z0, z1, mat="white", t=T):
    return {"id": pid, "mat": mat, "box": [x0, y, z0, x1, y + t, z1]}


def glass_shelf(pid, x0, x1, y, z0, z1):
    return {"id": pid, "kind": "glass", "box": [x0, y, z0, x1, y + 6, z1]}


# ------------------------------------------------------------------------------------------------ living room


def s003():
    """Шкаф П3.593.0.03, 662 × 418 × 2104: one door of three boards (white 89, an oak column with a glass window,
    white 228), handle on the narrow strip, hinged right; glass shelf in the window; legs 100."""
    W, H, LH = 662, 2104, 100
    p, zc = carcass(W, H, 396, LH)
    zf = zc + F
    p += [shelf("sh-1", 16.5, 645.5, 400, 8, zc - 2), shelf("sh-2", 16, 646, 700, BK, zc - 1),
          glass_shelf("gl-1", 18, 644, 1060, 20, zc - 20), shelf("sh-3", 16, 646, 1440, BK, zc - 1),
          shelf("sh-4", 16.5, 645.5, 1770, 8, zc - 2)]
    y0, y1 = LH + 2, H - T - 2
    d = [{"id": "door-l", "kind": "front", "box": [2, y0, zc, 91, y1, zf]},
         {"id": "door-oak-1", "kind": "front", "mat": "accent", "box": [91, y0, zc, 432, 698, zf]},
         {"id": "door-glass", "kind": "glass", "box": [91, 698, zc + 8, 432, 1425, zc + 12]},
         {"id": "door-oak-2", "kind": "front", "mat": "accent", "box": [91, 1425, zc, 432, y1, zf]},
         {"id": "door-r", "kind": "front", "box": [432, y0, zc, 660, y1, zf]}]
    d += handle("door", 46, 1045, zf)
    p += d
    p += legs4([75, 587], [60, 360], LH, splay=5)
    model("arista-0-03", "П3.593.0.03", "Шкаф «Ариста»", "living", [662, 418, 2104], 30,
          BYCAT + "; с витриной (стекло в дубовой вставке двери); размер по с. 30 (на с. 28 L660×B416)")
    return dump("arista-0-03", [W, 418, H], p, [door("door", d, "right", [660, zf])])


def s004():
    """Шкаф 2Д П3.593.0.04, 1038 × 419 × 1580: two unequal doors (613 / 425), each white + oak column with a glass
    window + white; partition under the door joint; glass shelves on the right; legs 75."""
    W, H, LH = 1038, 1580, 75
    p, zc = carcass(W, H, 397, LH)
    zf = zc + F
    p.append({"id": "part", "mat": "white", "box": [605, LH + T, BK, 621, H - T, zc]})
    p += [shelf("sh-l1", 16.5, 604.5, 520, 8, zc - 2), shelf("sh-l2", 16, 605, 974, BK, zc - 1),
          shelf("sh-l3", 16.5, 604.5, 1351, 8, zc - 2),
          shelf("sh-r1", 621.5, 1021.5, 300, 8, zc - 2), shelf("sh-r2", 621, 1022, 566, BK, zc - 1),
          glass_shelf("gl-r1", 623, 1020, 857, 20, zc - 20), glass_shelf("gl-r2", 623, 1020, 1117, 20, zc - 20)]
    y0, y1 = LH + 2, H - T - 2
    dl = [{"id": "dl-w1", "kind": "front", "box": [2, y0, zc, 89, y1, zf]},
          {"id": "dl-oak-1", "kind": "front", "mat": "accent", "box": [89, y0, zc, 453, 990, zf]},
          {"id": "dl-glass", "kind": "glass", "box": [89, 990, zc + 8, 453, 1367, zc + 12]},
          {"id": "dl-oak-2", "kind": "front", "mat": "accent", "box": [89, 1367, zc, 453, y1, zf]},
          {"id": "dl-w2", "kind": "front", "box": [453, y0, zc, 611.5, y1, zf]}]
    dl += handle("dl", 551, 981, zf)
    dr = [{"id": "dr-w1", "kind": "front", "box": [614.5, y0, zc, 701, y1, zf]},
          {"id": "dr-oak-1", "kind": "front", "mat": "accent", "box": [701, y0, zc, 950, 582, zf]},
          {"id": "dr-glass", "kind": "glass", "box": [701, 582, zc + 8, 950, 1367, zc + 12]},
          {"id": "dr-oak-2", "kind": "front", "mat": "accent", "box": [701, 1367, zc, 950, y1, zf]},
          {"id": "dr-w2", "kind": "front", "box": [950, y0, zc, 1036, y1, zf]}]
    dr += handle("dr", 675, 981, zf)
    p += dl + dr
    p += legs4([70, 968], [60, 360], LH, splay=5)
    model("arista-0-04", "П3.593.0.04", "Шкаф 2Д «Ариста»", "living", [1038, 419, 1580], 30,
          BYCAT + "; двери неравные (613 и 425) с витринами")
    return dump("arista-0-04", [W, 419, H], p, [door("door_left", dl, "left", [2, zf]), door("door_right", dr, "right", [1036, zf])])


def s007():
    """Тумба ТВ П3.593.0.07, 1828 × 418 × 627: two columns of two drawers (oak over white), a white front rail under
    the top, partition in the middle, 5 legs."""
    W, H, LH = 1828, 627, 110
    p, zc = carcass(W, H, 396, LH)
    zf = zc + F
    p.append({"id": "part", "mat": "white", "box": [906, LH + T, BK, 922, H - T, zc]})
    p.append({"id": "rail", "kind": "front", "box": [2, 527, zc, 1826, 608, zf]})
    moves = []
    for c, (fx0, fx1, bx0, bx1) in enumerate([(2, 912.5, 29, 893), (915.5, 1826, 935, 1799)]):
        xc = (fx0 + fx1) / 2
        for r, (fy0, fy1, mat, by0, bh) in enumerate([(359, 524, "accent", 375, 120), (112, 356, None, 136, 180)]):
            dp, mv = drawer(f"{c + 1}{r + 1}", [fx0, fy0, zc, fx1, fy1, zf], (bx0, bx1), by0, bh, 49, zc, mat,
                            [[xc, fy1 - 35]])
            p += dp
            moves.append(mv)
    p += legs4([75, 1753], [60, 360], LH, splay=12, extra=[(914, 210)])
    model("arista-0-07", "П3.593.0.07", "Тумба ТВ «Ариста»", "living", [1828, 418, 627], 30,
          BYCAT + "; белая планка под крышкой — неподвижная")
    return dump("arista-0-07", [W, 418, H], p, moves)


def s001():
    """Комод П3.593.0.01, 1828 × 418 × 863: two doors (oak 160 over white) round a column of three drawers (oak, two
    white), a white front rail under the top, 6 legs."""
    W, H, LH = 1828, 863, 110
    p, zc = carcass(W, H, 396, LH)
    zf = zc + F
    p += [{"id": "part-1", "mat": "white", "box": [600.5, LH + T, BK, 616.5, H - T, zc]},
          {"id": "part-2", "mat": "white", "box": [1211.5, LH + T, BK, 1227.5, H - T, zc]},
          {"id": "rail", "kind": "front", "box": [2, 750, zc, 1826, 844, zf]},
          shelf("sh-l", 16.5, 599.5, 430, 8, zc - 2), shelf("sh-r", 1228.5, 1811.5, 430, 8, zc - 2)]
    y0, y1 = LH + 2, 747
    dl = [{"id": "dl-oak", "kind": "front", "mat": "accent", "box": [2, 587, zc, 607, y1, zf]},
          {"id": "dl-w", "kind": "front", "box": [2, y0, zc, 607, 587, zf]}] + handle("dl", 500, 712, zf, axis="x")
    dr = [{"id": "dr-oak", "kind": "front", "mat": "accent", "box": [1221, 587, zc, 1826, y1, zf]},
          {"id": "dr-w", "kind": "front", "box": [1221, y0, zc, 1826, 587, zf]}] + handle("dr", 1327, 712, zf, axis="x")
    p += dl + dr
    moves = [door("door_left", dl, "left"), door("door_right", dr, "right")]
    for k, (fy0, fy1, mat, by0, bh) in enumerate([(587, 747, "accent", 605, 110), (349.5, 584, None, 370, 160),
                                                  (112, 346.5, None, 136, 160)]):
        dp, mv = drawer(str(k + 1), [610, fy0, zc, 1218, fy1, zf], (629.5, 1198.5), by0, bh, 49, zc, mat,
                        [[914, fy1 - 35]])
        p += dp
        moves.append(mv)
    p += legs4([75, 1753], [60, 360], LH, splay=12, extra=[(914, 60), (914, 360)])
    model("arista-0-01", "П3.593.0.01", "Комод «Ариста»", "living", [1828, 418, 863], 30,
          BYCAT + "; двери из двух щитов (дуб 160 + беж), белая планка под крышкой — неподвижная")
    return dump("arista-0-01", [W, 418, H], p, moves)


def s009():
    """Стол журнальный П3.593.0.09, 900 × 500 × 451: an open box (top, bottom, sides white), an oak partition and an
    oak shelf in the left part; open front and back; 4 legs."""
    W, D, H, LH = 900, 500, 451, 110
    p = [{"id": "top", "box": [0, H - T, 0, W, H, D]},
         {"id": "bottom", "box": [0, LH, 0, W, LH + T, D]},
         {"id": "side-l", "box": [0, LH + T, 0, T, H - T, D]},
         {"id": "side-r", "box": [W - T, LH + T, 0, W, H - T, D]},
         {"id": "part", "mat": "oak", "box": [500, LH + T, 0, 516, H - T, D]},
         {"id": "shelf", "mat": "oak", "box": [T, 272, 0, 500, 288, D]}]
    p += legs4([71, 829], [70, 430], LH, splay=12)
    model("arista-0-09", "П3.593.0.09", "Стол журнальный «Ариста»", "tables", [900, 500, 451], 30, BYCAT)
    return dump("arista-0-09", [W, D, H], p, [])


def s006():
    """Полка П3.593.0.06, 520 × 230 × 520 (wall): two white shelves over the full width, a white upright through
    them, four oak back panels."""
    W, D, H = 520, 230, 520
    p = [{"id": "shelf-1", "box": [0, 0, 0, W, T, D]},
         {"id": "shelf-2", "box": [0, 268, 0, W, 284, D]},
         {"id": "upright-1", "box": [252, T, T, 268, 268, D]},
         {"id": "upright-2", "box": [252, 284, T, 268, H, D]}]
    k = 0
    for x0, x1 in ((18, 252), (268, 502)):
        for y0, y1 in ((T, 268), (284, 504)):
            k += 1
            p.append({"id": f"back-{k}", "mat": "oak", "box": [x0, y0, 0, x1, y1, T]})
    model("arista-0-06", "П3.593.0.06", "Полка «Ариста»", "living", [520, 230, 520], 30, BYCAT, mount="wall")
    return dump("arista-0-06", [W, D, H], p, [])


def s139():
    """Зеркало П3.593.1.39, 350 × 20 × 350 (wall): a round frame of solid oak painted «Персидский жемчуг» (23 wide,
    rounded), the mirror in its rebate on an ХДФ back."""
    p = [{"id": "frame", "shape": "ring", "inner": 304, "edge": 6, "box": [0, 0, 7, 350, 350, 20]},
         {"id": "mirror", "kind": "mirror", "shape": "circle", "box": [19, 19, 3, 331, 331, 7]},
         {"id": "back", "kind": "back", "shape": "circle", "mat": "white", "box": [25, 25, 0, 325, 325, 3]}]
    model("arista-1-39", "П3.593.1.39", "Зеркало «Ариста»", "decor", [350, 20, 350], 30, BYCAT, mount="wall")
    return dump("arista-1-39", [350, 20, 350], p, [])


# ------------------------------------------------------------------------------------------------ bedroom: wardrobes


def wardrobe_carcass(W, parts_x=()):
    """Wardrobe carcass like the 4-door one (instruction 1.31) but sides 561 deep (B 583): top 577, base, sides on
    88×54×20 glides, partitions white. Returns parts, zc, zf."""
    H, yb, yt = 2292, 20, 2276
    zb, zc = BK, BK + 561
    p = [{"id": "top", "box": [0, yt, zb, W, H, zb + 577]},
         {"id": "base", "box": [0, yb, zb, W, yb + T, zc]},
         {"id": "side-l", "box": [0, yb + T, zb, T, yt, zc]},
         {"id": "side-r", "box": [W - T, yb + T, zb, W, yt, zc]}]
    for i, x in enumerate(parts_x):
        p.append({"id": f"part-{i + 1}", "mat": "white", "box": [x - 8, yb + T, zb, x + 8, yt, zc]})
    return p, zc, zc + F


def hanging(tag, x0, x1, zc):
    """A hanging compartment between x0 and x1 (inner faces): fixed bottom and top horizontals on the back joints,
    the oval chrome rail under the top one."""
    return [shelf(f"{tag}-bottom", x0 + 0.5, x1 - 0.5, 400, BK, zc - 1),
            shelf(f"{tag}-top", x0 + 0.5, x1 - 0.5, 1896, BK, zc - 1),
            {"id": f"{tag}-rail", "kind": "tube", "mat": "chrome", "box": [x0 + 4, 1815, 276, x1 - 4, 1845, 291]}]


def w129():
    """Шкаф для одежды 2Д П3.593.1.29, 902 × 583 × 2292: the 4-door wardrobe's hanging half — two doors of oak 160 +
    beige 286, top shelf, rail, back rail at the middle joint of the back."""
    W = 902
    p, zc, zf = wardrobe_carcass(W)
    p += hanging("in", T, W - T, zc)
    p.append({"id": "rail-back", "mat": "white", "box": [16.5, 1092, BK, 885.5, 1220, BK + T]})
    p += [{"id": "back-1", "kind": "back", "mat": "white", "box": [2, 21, 0, 900, 407, BK]},
          {"id": "back-2", "kind": "back", "mat": "white", "box": [2, 1905, 0, 900, 2291, BK]}]
    k = 0
    for y0 in (409, 1157):
        for xx in (2, 452):
            k += 1
            p.append({"id": f"back-m{k}", "kind": "back", "mat": "white", "box": [xx, y0, 0, xx + 448, y0 + 746, BK]})
    y0, y1 = 22, 2274
    d1 = [{"id": "d1-oak", "kind": "front", "mat": "accent", "grain": "y", "box": [3.5, y0, zc, 163.5, y1, zf]},
          {"id": "d1-w", "kind": "front", "box": [163.5, y0, zc, 449.5, y1, zf]}] + handle("d1", 387, 1150, zf)
    d2 = [{"id": "d2-w", "kind": "front", "box": [452.5, y0, zc, 738.5, y1, zf]},
          {"id": "d2-oak", "kind": "front", "mat": "accent", "grain": "y", "box": [738.5, y0, zc, 898.5, y1, zf]}] + handle("d2", 515, 1150, zf)
    p += d1 + d2
    p += glides([64, 838], [BK + 30, zc - 30])
    model("arista-1-29", "П3.593.1.29", "Шкаф для одежды 2Д «Ариста»", "bedroom", [902, 583, 2292], 30,
          BYCAT + "; как половина шкафа 4Д (П3.593.1.31)")
    return dump("arista-1-29", [W, 583, 2292], p, [door("door_1", d1, "left", [3.5, zf]), door("door_2", d2, "right", [898.5, zf])])


def w130():
    """Шкаф для одежды 3Д П3.593.1.30, 1352 × 583 × 2292: hanging compartments left and right (doors oak 160 + beige
    286), the middle column: a door over four drawers, shelves."""
    W = 1352
    p, zc, zf = wardrobe_carcass(W, (451.5, 900.5))
    p += hanging("l", T, 443.5, zc) + hanging("r", 908.5, W - T, zc)
    p += [shelf("m-over", 459.5, 892.5, 804, BK, zc - 1), shelf("m-1", 460, 892, 1200, 10, zc - 2),
          shelf("m-2", 460, 892, 1560, 10, zc - 2), shelf("m-top", 459.5, 892.5, 1896, BK, zc - 1)]
    for i, (x0, x1) in enumerate([(2, 450.5), (452.5, 899.5), (901.5, 1350)]):
        p.append({"id": f"back-{i + 1}", "kind": "back", "mat": "white", "box": [x0, 21, 0, x1, 2291, BK]})
    y0, y1 = 22, 2274
    d1 = [{"id": "d1-oak", "kind": "front", "mat": "accent", "grain": "y", "box": [4, y0, zc, 164, y1, zf]},
          {"id": "d1-w", "kind": "front", "box": [164, y0, zc, 450, y1, zf]}] + handle("door1", 386, 1150, zf)
    d2 = [{"id": "d2", "kind": "front", "box": [453, 822, zc, 899, y1, zf]}] + handle("door2", 835, 1150, zf)
    d3 = [{"id": "d3-w", "kind": "front", "box": [902, y0, zc, 1188, y1, zf]},
          {"id": "d3-oak", "kind": "front", "mat": "accent", "grain": "y", "box": [1188, y0, zc, 1348, y1, zf]}] + handle("door3", 966, 1150, zf)
    p += d1 + d2 + d3
    moves = [door("door_1", d1, "left", [4, zf]), door("door_2", d2, "left"), door("door_3", d3, "right", [1348, zf])]
    for k, fy0 in enumerate([622, 422, 222, 22]):
        fy1 = fy0 + 197
        dp, mv = drawer(str(k + 1), [453, fy0, zc, 899, fy1, zf], (472.5, 879.5), max(fy0 + 25, 46), 140, 64, zc,
                        None, [[676, (fy0 + fy1) / 2]])
        p += dp
        moves.append(mv)
    p += glides([64, 676, 1288], [BK + 30, zc - 30])
    model("arista-1-30", "П3.593.1.30", "Шкаф для одежды 3Д «Ариста»", "bedroom", [1352, 583, 2292], 30,
          BYCAT + "; средняя секция: дверь над четырьмя ящиками")
    return dump("arista-1-30", [W, 583, 2292], p, moves)


# ------------------------------------------------------------------------------------------------ bedroom: chests


def chest(mid, code, name, W, D, H, fronts, handles_x, page=30, note=None, niche=None):
    """A chest / bedside table on legs 110: carcass (sides D-22), drawers with fronts [(y0, y1, [(ya, yb, mat), …])]
    (a front of two boards: oak and white), handles at handles_x, y = handle height given per drawer."""
    LH = 110
    p, zc = carcass(W, H, D - BK - F, LH)
    zf = zc + F
    moves = []
    for k, (fy0, fy1, boards, hy) in enumerate(fronts):
        fb = [[2, a, zc, W - 2, b, zf] for a, b, _ in boards]
        mats = [m for _, _, m in boards]
        by0 = max(fy0 + 20, LH + T + 10)
        bh = min(fy1 - fy0 - 60, 180)
        dp, mv = drawer(str(k + 1), fb, (29, W - 29), by0, bh, max(zc - 400, 20), zc, mats,
                        [[x, hy] for x in handles_x])
        p += dp
        moves.append(mv)
    if niche:
        p += niche(zc)
    p += legs4([80, W - 80], [60, D - 60], LH, splay=8)
    model(mid, code, name, "bedroom", [W, D, H], page, note or BYCAT)
    return dump(mid, [W, D, H], p, moves)


def k126():
    W = 1100
    return chest("arista-1-26", "П3.593.1.26", "Комод «Ариста»", W, 450, 860,
                 [(600, 841, [(600, 760, "accent"), (760, 841, None)], 800),
                  (356, 597, [(356, 597, None)], 532),
                  (112, 353, [(112, 353, None)], 288)], [256, 844],
                 note=BYCAT + "; верхний ящик — фасад из двух щитов (беж + дуб 160), по две ручки")


def k127():
    return chest("arista-1-27", "П3.593.1.27", "Комод «Ариста»", 900, 417, 1094,
                 [(836.5, 1075, [(836.5, 996.5, "accent"), (996.5, 1075, None)], 1036),
                  (595, 833.5, [(595, 833.5, None)], 768.5),
                  (353.5, 592, [(353.5, 592, None)], 527),
                  (112, 350.5, [(112, 350.5, None)], 285.5)], [450],
                 note=BYCAT + "; верхний ящик — фасад из двух щитов (беж + дуб 160)")


def t137():
    return chest("arista-1-37", "П3.593.1.37", "Тумба прикроватная «Ариста»", 500, 417, 580,
                 [(338, 561, [(338, 454, None), (454, 561, "accent")], 496),
                  (112, 335, [(112, 335, None)], 270)], [250],
                 note=BYCAT + "; верхний ящик — фасад из двух щитов (дуб сверху, беж снизу)")


def t147():
    def niche(zc):
        return [shelf("niche-bottom", T, 500 - T, 336, BK, zc)]
    return chest("arista-1-47", "П3.593.1.47", "Тумба прикроватная «Ариста»", 500, 416, 554,
                 [(112, 333, [(112, 272, "accent"), (272, 333, None)], 300)], [250], niche=niche,
                 note=BYCAT + "; открытая ниша над ящиком; фасад ящика — дуб 160 + беж")


# ------------------------------------------------------------------------------------------------ tables


def t140():
    """Стол туалетный П3.593.1.40, 1120 × 440 × 807: a table (left side panel, white top, an oak drawer front under
    it) whose right end rests on a three-drawer pedestal on small glides, partly under the table."""
    W, D, H = 1120, 440, 807
    zc, zf = D - F, D
    p = [{"id": "top", "box": [0, H - T, 0, 781, H, D - 3]},
         {"id": "side-l", "box": [0, 0, 0, T, H - T, D - 3]},
         {"id": "side-r", "box": [765, 637, 0, 781, H - T, zc]},
         {"id": "rail-back", "mat": "white", "box": [T, 637, 0, 765, H - T, T]},
         # the pedestal
         {"id": "p-top", "box": [634, 621, BK, 1120, 637, D - 3]},
         {"id": "p-base", "box": [634, 10, BK, 1120, 26, zc]},
         {"id": "p-side-l", "box": [634, 26, BK, 650, 621, zc]},
         {"id": "p-side-r", "box": [1104, 26, BK, 1120, 621, zc]},
         {"id": "p-back", "kind": "back", "mat": "white", "box": [635, 11, 0, 1119, 636, BK]}]
    k = 0
    for x in (660, 1094):
        for z in (40, 380):
            k += 1
            p.append({"id": f"glide-{k}", "kind": "panel", "mat": "black", "edge": 1, "box": [x - 15, 0, z - 15, x + 15, 10, z + 15]})
    dp, mv = drawer("t", [18, 640, zc, 779, 788, zf], (29, 752), 652, 110, 40, zc, "accent")
    p += dp
    moves = [mv]
    for i, fy0 in enumerate([418, 215, 12]):
        fy1 = fy0 + 200
        dp, mv = drawer(str(i + 1), [636, fy0, zc, 1118, fy1, zf], (663, 1091), max(fy0 + 20, 36), 140, 40, zc, None,
                        [[877, (fy0 + fy1) / 2]])
        p += dp
        moves.append(mv)
    model("arista-1-40", "П3.593.1.40", "Стол туалетный «Ариста»", "bedroom", [1120, 440, 807], 30,
          BYCAT + "; ящик стола без ручки (нажимной), тумба с тремя ящиками под правым концом столешницы")
    return dump("arista-1-40", [W, D, H], p, moves)


def d242():
    """Стол письменный П3.593.2.42, 1200 × 560 × 754: oak top, a left side panel to the floor, an oak modesty
    panel, a pedestal to the floor on the right: open niche over a door (beige + oak 160, hinged right)."""
    W, D, H = 1200, 560, 754
    zc, zf = D - 3 - F, D - 3
    p = [{"id": "top", "mat": "oak", "box": [0, H - T, 0, W, H, D]},
         {"id": "side-l", "box": [27, 0, 0, 43, H - T, zf]},
         {"id": "modesty", "mat": "oak", "box": [43, 450, 40, 777, H - T, 56]},
         {"id": "p-side-l", "box": [777, 0, BK, 793, H - T, zc]},
         {"id": "p-side-r", "box": [1159, 0, BK, 1175, H - T, zc]},
         {"id": "p-base", "box": [793, 0, BK, 1159, T, zc]},
         {"id": "p-shelf", "mat": "white", "box": [793.5, 270, 8, 1158.5, 286, zc - 2]},
         {"id": "p-niche", "box": [793, 551, BK, 1159, 567, zc]},
         {"id": "p-back", "kind": "back", "mat": "white", "box": [778, 1, 0, 1174, H - T - 1, BK]}]
    d = [{"id": "door-w", "kind": "front", "box": [779, 3, zc, 1013, 547, zf]},
         {"id": "door-oak", "kind": "front", "mat": "accent", "grain": "y", "box": [1013, 3, zc, 1173, 547, zf]}]
    d += handle("door", 851, 390, zf)
    p += d
    model("arista-2-42", "П3.593.2.42", "Стол письменный «Ариста»", "office", [1200, 560, 754], 30, BYCAT)
    return dump("arista-2-42", [W, D, H], p, [door("door", d, "right", [1173, zf])])


def d243():
    """Стол письменный 2Т П3.593.2.43, 1408 × 556 × 754: oak top on two pedestals on legs — three drawers (oak,
    white, white) on the left, a door (beige + oak 160) on the right; oak modesty panel."""
    W, D, H, LH = 1408, 556, 754, 110
    zc, zf = D - 3 - F, D - 3
    p = [{"id": "top", "mat": "oak", "box": [0, H - T, 0, W, H, D]},
         {"id": "modesty", "mat": "oak", "box": [417, 466, 40, 991, H - T, 56]}]
    for tag, x0 in (("l", 31), ("r", 991)):
        x1 = x0 + 386
        p += [{"id": f"{tag}-base", "box": [x0, LH, BK, x1, LH + T, zc]},
              {"id": f"{tag}-side-l", "box": [x0, LH + T, BK, x0 + T, H - T, zc]},
              {"id": f"{tag}-side-r", "box": [x1 - T, LH + T, BK, x1, H - T, zc]},
              {"id": f"{tag}-back", "kind": "back", "mat": "white", "box": [x0 + 1, LH + 1, 0, x1 - 1, H - T - 1, BK]}]
        p += legs4([x0 + 45, x1 - 45], [60, D - 80], LH, splay=6, pre=tag)
    moves = []
    for k, (fy0, fy1, mat) in enumerate([(526, 735, "accent"), (318, 523, None), (112, 315, None)]):
        dp, mv = drawer(str(k + 1), [33, fy0, zc, 415, fy1, zf], (60, 388), max(fy0 + 20, LH + T + 10), 140, 60, zc, mat,
                        [[224, fy1 - 68]])
        p += dp
        moves.append(mv)
    p.append({"id": "r-shelf", "mat": "white", "box": [1007.5, 420, 8, 1360.5, 436, zc - 2]})
    d = [{"id": "door-w", "kind": "front", "box": [993, 112, zc, 1215, 735, zf]},
         {"id": "door-oak", "kind": "front", "mat": "accent", "grain": "y", "box": [1215, 112, zc, 1375, 735, zf]}]
    d += handle("door", 1061, 592, zf)
    p += d
    moves.append(door("door", d, "right", [1375, zf]))
    model("arista-2-43", "П3.593.2.43", "Стол письменный 2Т «Ариста»", "office", [1408, 556, 754], 30, BYCAT)
    return dump("arista-2-43", [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------------ beds


def foot_outline(plane_a0, a1, top, bottom=240, leg_top=170, leg_bot=110, flip=(True, True)):
    """SVG outline of a bed panel with trapezoid feet at its ends (the collection's «\\_/» legs): along a (x or z)
    from a0 to a1, y from 0 to top; the edge between the feet at `bottom`."""
    a0 = plane_a0
    pts = [(a0, top), (a1, top)]
    if flip[1]:
        pts += [(a1, 0), (a1 - leg_bot, 0), (a1 - leg_top, bottom)]
    else:
        pts += [(a1, bottom)]
    if flip[0]:
        pts += [(a0 + leg_top, bottom), (a0 + leg_bot, 0), (a0, 0)]
    else:
        pts += [(a0, bottom)]
    return "M " + " L ".join(f"{a:g} {b:g}" for a, b in pts) + " Z"


def bed(mid, code, name, W, H, soft, page, sleep):
    """Bed 2123 long: oak (Дуб Канзас) headboard panel to the floor, side rails and a foot board with trapezoid
    feet at the foot corners, white inner rails carrying the metal base (металлокаркас) with slats, a mattress;
    the upholstered version has a channelled soft panel on the headboard, the other an oak face panel with a milled
    frame."""
    D, t = 2123, 22
    ih = 850 if soft else H                     # the oak headboard panel
    zh = t                                       # its front face
    zfoot = D - t
    rail_top, rail_bot = 420, 240
    p = [{"id": "head", "mat": "oak", "shape": "path", "box": [0, 0, 0, W, ih, t],
          "outline": foot_outline(0, W, ih, bottom=240)},
         {"id": "foot", "mat": "oak", "shape": "path", "box": [0, 0, zfoot, W, rail_top, D],
          "outline": foot_outline(0, W, rail_top, bottom=rail_bot)},
         {"id": "rail-l", "mat": "oak", "shape": "path", "box": [0, 0, zh, t, rail_top, zfoot],
          "outline": foot_outline(zh, zfoot, rail_top, bottom=rail_bot, flip=(False, True))},
         {"id": "rail-r", "mat": "oak", "shape": "path", "box": [W - t, 0, zh, W, rail_top, zfoot],
          "outline": foot_outline(zh, zfoot, rail_top, bottom=rail_bot, flip=(False, True))},
         {"id": "inner-l", "box": [t, 190, zh, t + T, 400, zfoot]},
         {"id": "inner-r", "box": [W - t - T, 190, zh, W - t, 400, zfoot]}]
    if soft:
        n = 6 if W > 1200 else 4
        p.append({"id": "soft", "kind": "soft", "channels": n, "box": [70, 440, zh, W - 70, H, zh + 60]})
    else:
        p.append({"id": "head-face", "mat": "oak", "box": [60, 480, zh, W - 60, H - 40, zh + T],
                  "face": {"type": "grooves", "w": 4, "depth": 2, "flute": "u",
                           "lines": [[100, 520, W - 100, 520], [W - 100, 520, W - 100, H - 80],
                                     [W - 100, H - 80, 100, H - 80], [100, H - 80, 100, 520]]}})
    # the metal base (m): frame rails on the inner rails, slats, middle legs for the double bed
    fx0, fx1 = (W - sleep) / 2, (W + sleep) / 2
    z0, z1 = 101, 2101
    p += [{"id": "m-frame-l", "mat": "black", "box": [fx0, 300, z0, fx0 + 30, 330, z1], "covers": ["m"]},
          {"id": "m-frame-r", "mat": "black", "box": [fx1 - 30, 300, z0, fx1, 330, z1]},
          {"id": "mattress", "kind": "mattress", "box": [fx0, 340, z0, fx1, 560, z1]}]
    for i in range(24):
        z = 120 + i * 81
        p.append({"id": f"m-slat-{i + 1}", "mat": "door_enamel_whitey#c9a877", "box": [fx0 + 30, 330, z, fx1 - 30, 338, z + 53]})
    if W > 1200:
        p += [{"id": "m-beam", "mat": "black", "box": [W / 2 - 15, 300, z0, W / 2 + 15, 330, z1]},
              {"id": "m-leg-1", "kind": "tube", "mat": "black", "box": [W / 2 - 12.5, 0, 700, W / 2 + 12.5, 300, 725]},
              {"id": "m-leg-2", "kind": "tube", "mat": "black", "box": [W / 2 - 12.5, 0, 1400, W / 2 + 12.5, 300, 1425]}]
    kind = "мягкое изголовье с каналами" if soft else "изголовье ЛДСП с фрезерованной рамкой"
    model(mid, code, name, "bedroom", [W, D, H], page,
          f"{BYCAT}; спальное место 2000×{sleep}, металлокаркас; {kind}")
    return dump(mid, [W, D, H], p, [])


def b124():
    return bed("arista-1-24", "П3.593.1.24", "Кровать 2-16 «Ариста»", 1750, 900, True, 30, 1600)


def b145():
    return bed("arista-1-45", "П3.593.1.45", "Кровать 1-09 «Ариста»", 1050, 944, True, 30, 900)


def b146():
    return bed("arista-1-46", "П3.593.1.46", "Кровать 2-16 «Ариста»", 1750, 900, False, 30, 1600)


def b121():
    return bed("arista-1-21", "П3.593.1.21", "Кровать 1-09 «Ариста»", 1050, 900, False, 30, 900)


# ------------------------------------------------------------------------------------------------ catalogue fragment
FINISHES = [
    {"id": "arista-nubuk", "name": "Беж нубук / Дуб Артизан Трюфель; каркас Персидский жемчуг / Дуб Канзас",
     "body": "door_enamel_whitey#dfe3e2", "front": "door_enamel_whitey#c1c6cf",
     "roles": {"accent": "door_enamel_whitey#6e5241", "oak": "door_enamel_whitey#7d6752"},
     "swatch": "#c1c6cf"},
]

COLLECTION = {
    "id": "arista", "name": "Ариста", "brand": "Пинскдрев", "finishes": ["arista-nubuk"], "metal": "black",
    "note": "Каталог «Корпусная мебель ч. II» 2025, с. 28–30 (PDF). Корпус ЛДСП 16 «Персидский жемчуг» (крышка и основание "
            "на всю ширину, боковины между ними), внутренние детали ЛДСП 16 белый, задняя стенка ХДФ 3 накладная, фасады МДФ 19 "
            "«Беж нубук» и «Дуб Артизан Трюфель», ЛДСП «Дуб Канзас» (кровати, столешницы, полки), ручки-скобы AKS PS36 чёрные, "
            "чёрные квадратные конические опоры враспор; шкафы для одежды на регулируемых опорах 88×54×20.",
}


def write_catalog():
    frag = {"finishes": FINISHES, "profiles": {}, "collections": [COLLECTION], "models": MODELS}
    path = os.path.join(HERE, "arista_catalog.json")
    with open(path, "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return path


if __name__ == "__main__":
    for f in [w131, w129, w130, s003, s004, s007, s001, s009, s006, s139, k126, k127, t137, t147, t140, d242, d243,
              b124, b145, b146, b121]:
        print(f())
    print(write_catalog())
