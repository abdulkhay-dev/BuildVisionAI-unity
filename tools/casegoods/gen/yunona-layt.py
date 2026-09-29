"""«Юнона Лайт» (Пинскдрев П3.0582, каталог «Корпусная мебель ч. II», PDF с. 109–112): 23 articles.

Sources: the assembly instructions of the older set «Юнона» (П582.01 … П582.07, Городищенская мебельная фабрика, 2020–21;
materials «ЛДСП 16 Дуб Версаль / ЛДСП 16 Белый / ДВП ламинированная белая»), the catalogue (interiors p. 109–111, module
cut-outs, wardrobe schemes and the swatch «Дуб Каньон» / «Дуб Бордо лайт» on p. 112) and the pinskdrev.by product photos.
Instructions exist for П582.01 (шкаф 2Д с ящиками = 1.55), .02 (шкаф 2Д = 1.56), .03 (стеллаж = 1.57), .04 (стол
туалетный = 1.58), .06 (тумба прикроватная, drawer over a niche = 1.60) and .07 (кровать 2-16 with a panel headboard =
1.61). index.json links 1.21 (комод) to the bedside-table instruction and 1.28 (bed with the upholstered headboard) to the
panel-bed instruction (identical files): 1.21 is built by photo, 1.28 is the П582.07 frame with the upholstered pad.

Construction (from the instructions): carcass ЛДСП 16 in the Каньон oak — top and bottom over the full width and depth,
the sides between them (2 mm shallower than the top), ДВП backs 3.2 in grooves (z 6..9.2); inner parts (fixed shelves,
stiles, drawer boxes) ЛДСП 16 white; the living pieces stand on 88×54×20 glides, tables and beds on nail glides 4 mm.
Wardrobes: overlay doors 446 (Бордо лайт), bedside / chest / sideboards: fronts inset flush between the sides (the light
edge bands of the carcass show round them). Drawer boxes: sides and back ЛДСП white (back 19 lower, standing on the
bottom), ДВП bottom in grooves and 5 mm into the front, 13–14 mm runner gaps. Handles UA-AA-06-128 / -416: satin
aluminium bars. Every visible front edge of a Каньон carcass board carries a light (Бордо лайт) edge band: a 0.6 mm
moulding (profile yunona-layt-edge16) on the edge face — the format has no edge-band colour.

Coordinates (Docs/casegoods-designs.md): x left→right, y up from the floor, z from the wall (0) to the front.
    /private/tmp/claude-501/venv/bin/python tools/casegoods/gen/yunona-layt.py
"""
import json
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "yunona-layt"
T = 16          # ЛДСП
BK = 3.2        # ДВП ламинированная (thickness not in the tables)
EB = 0.6        # edge band: how far the band moulding stands off the edge face
G = 3           # gap round inset fronts
BYPHOTO = "по фото, без инструкции"

MODELS = []
CUTLISTS = {}


# ------------------------------------------------------------------------------------------------ helpers
def P(pid, b, n=None, **kw):
    p = {}
    if n is not None:
        p["n"] = n
    if pid is not None and pid != n:
        p["id"] = pid
    p.update(kw)
    p["box"] = [round(v, 2) for v in b]
    return p


def band(pid, x0, y0, x1, y1, z):
    """A light edge band on the front edge face of a board (the face x0..x1 × y0..y1 at z): a flat moulding 0.6 thick
    along the edge's long side. The box is its real extent for the checker (a moulding has no solid overlap test)."""
    if x1 - x0 >= y1 - y0:
        w, path = y1 - y0, [[x0, y1], [x1, y1]]
    else:
        w, path = x1 - x0, [[x0, y0], [x0, y1]]
    assert abs(w - T) < 0.01, (pid, w)
    return {"id": pid, "kind": "moulding", "mat": "edge", "profile": "yunona-layt-edge16", "plane": "front", "z": round(z, 2),
            "side": -1, "path": [[round(a, 2), round(b, 2)] for a, b in path],
            "box": [round(x0, 2), round(y0, 2), round(z, 2), round(x1, 2), round(y1, 2), round(z + EB, 2)]}


def fband(p):
    """Band on the +z face of a panel part."""
    b = p["box"]
    return band(f"eb-{p.get('id') or p.get('n')}", b[0], b[1], b[3], b[4], b[5])


def handle(pid, x, y, z, d=150, dirn="right", hw="h"):
    """UA-AA-06-128 (d 150) / UA-AA-06-416 (d 450): satin aluminium bar, 10 × 8, 22 mm off the face."""
    return {"id": pid, "kind": "handle", "model": "bar", "at": [round(x, 2), round(y, 2)], "dir": dirn, "d": d, "band": 10,
            "t": 8, "standoff": 22, "post": 9, "z": round(z, 2), "covers": [hw]}


def glides(xs, zs, cov="007", w=88, d=54, h=20):
    out, k = [], 0
    for x in xs:
        for z in zs:
            k += 1
            out.append({"id": f"glide-{k}", "kind": "panel", "mat": "black", "edge": 2,
                        "box": [x - w / 2, 0, z - d / 2, x + w / 2, h, z + d / 2], "covers": [cov]})
    return out


def nails(pts, cov, h=4, d=20):
    """Nail glides «опора гвоздь» (discs under the panel ends)."""
    return [{"id": f"nail-{i + 1}", "kind": "panel", "mat": "black", "shape": "circle", "edge": 0.5,
             "box": [x - d / 2, 0, z - d / 2, x + d / 2, h, z + d / 2], "covers": [cov]} for i, (x, z) in enumerate(pts)]


def ids(parts):
    return [p.get("id") or p.get("n") for p in parts]


def drawer(tag, front, fmat, box_x, y0, h, hb, z0, zf, ns=None, hdl=None, extra=()):
    """A drawer: front (box), a box of ЛДСП white — sides (h) from z0 to the front's back face zf, the back (hb) between
    them standing on the ДВП bottom (in the sides' grooves, 5 mm into the front) — and a handle.
    ns = cut-list numbers (front, side L, side R, back, bottom) or None. Returns (parts, move)."""
    x0, x1 = box_x
    n = ns or (None,) * 5
    fr = P(f"d{tag}-front" if n[0] else f"d{tag}-front", front, n[0], kind="front", **({"mat": fmat} if fmat else {}))
    if n[0]:
        fr["id"] = f"{n[0]}-{tag}"
    parts = [fr,
             P(f"{n[1] or 'dside'}-{tag}-l", [x0, y0, z0, x0 + T, y0 + h, zf], n[1], mat="white"),
             P(f"{n[2] or 'dside'}-{tag}-r", [x1 - T, y0, z0, x1, y0 + h, zf], n[2], mat="white"),
             P(f"{n[3] or 'dback'}-{tag}", [x0 + T, y0 + h - hb, z0, x1 - T, y0 + h, z0 + T], n[3], mat="white")]
    bw = (x1 - x0) - 2 * T + 2 * 5.25                    # bottom in 5.25 mm grooves of the sides
    bx0 = (x0 + x1) / 2 - bw / 2
    parts.append(P(f"{n[4] or 'dbottom'}-{tag}", [bx0, y0 + h - hb - BK, z0, bx0 + bw, y0 + h - hb, zf + 5], n[4],
                   kind="back", mat="white"))
    parts += list(extra)
    if hdl:
        parts.append(handle(f"h-d{tag}", hdl[0], hdl[1], front[5], d=hdl[2] if len(hdl) > 2 else 150))
    return parts, {"type": "drawer", "name": f"drawer_{tag}", "parts": ids(parts), "travel": round((zf - z0) * 0.8)}


def door(name, parts, hinge, angle=100):
    return {"type": "door", "name": name, "parts": ids(parts), "hinge": hinge, "angle": angle}


def model(mid, code, name, category, size, page, note, **kw):
    m = {"id": mid, "code": code, "name": name, "collection": SLUG, "category": category, "size": size}
    m.update(kw)
    m["page"] = page
    if note:
        m["note"] = note
    MODELS.append(m)


def cutlist(mid, code, source, note, rows):
    CUTLISTS[mid] = {"code": code, "source": source, "note": note,
                     "rows": [{"n": n, "code": c, "name": nm, "size": s, "count": k} for n, c, nm, s, k in rows]}


# ------------------------------------------------------------------------------------------------ 1.55 / 1.56 / 1.11 / 1.65 wardrobes
def wardrobe_carcass(W, ns=("1", "2", "3", "4")):
    """900/450 × 595 × 2292: bottom and top W × 579 over the sides 2240 × 579, on four glides 20; doors 16 overlay → 595."""
    D, H = 579, 2292
    p = [P(ns[2], [0, 2276, 0, W, H, D], ns[2] if ns[2] in "34" else None),
         P(ns[3], [0, 20, 0, W, 36, D], ns[3] if ns[3] in "34" else None),
         P(ns[0], [0, 36, 0, T, 2276, D], ns[0] if ns[0] in "12" else None),
         P(ns[1], [W - T, 36, 0, W, 2276, D], ns[1] if ns[1] in "12" else None)]
    p += [fband(q) for q in p]
    p += glides([60, W - 60], [40, D - 40])
    return p


def w155():
    """Шкаф для одежды 2Д П3.0582.1.55 = П582.01: two doors 1356 over three drawers 300 (Каньон fronts)."""
    W, D, zf = 900, 579, 595
    p = wardrobe_carcass(W)
    # inner white parts: drawer-zone shelf 6 (867 × 560), hat shelf 5 (867 × 520), the stile 12 between them
    p += [P("6", [16.5, 925, 10, 883.5, 941, 570], "6", mat="white"),
          P("5", [16.5, 1901, 10, 883.5, 1917, 530], "5", mat="white"),
          P("12", [386, 941, 10, 514, 1901, 26], "12", mat="white")]
    # backs: 7 top 878 × 372, 8 middle 2 × 974 × 438 (joint on the stile 12), 9 bottom 2 × 900 × 438, joined to the
    # middle ones by the profile 010 (886) behind shelf 6
    p += [P("7", [11, 1910, 6, 889, 2282, 6 + BK], "7", kind="back"),
          P("8-1", [11, 934, 6, 449, 1908, 6 + BK], "8", kind="back"),
          P("8-2", [451, 934, 6, 889, 1908, 6 + BK], "8", kind="back"),
          P("9-1", [11, 31, 6, 449, 931, 6 + BK], "9", kind="back"),
          P("9-2", [451, 31, 6, 889, 931, 6 + BK], "9", kind="back"),
          {"id": "010", "kind": "back", "mat": "white", "edge": 0.3, "box": [11, 929, 9.2, 889, 936, 10], "covers": ["010"]}]
    p.append({"id": "rail", "kind": "tube", "mat": "chrome", "box": [19, 1850, 282, 881, 1865, 312], "covers": ["019"]})
    moves = []
    # drawers: fronts 896 × 300 overlay (x 2..898), 4 mm gaps; boxes 841.5 wide, 500 deep, 224 high
    for i, fy in enumerate([22, 326, 630]):
        tag = str(3 - i)
        parts, mv = drawer(tag, [2, fy, D, 898, fy + 300, zf], "kanon", (29.25, 870.75), fy + 40, 224, 205, 79, D,
                           ns=("14.4", "14.1", "14.2", "14.3", "14.5"), hdl=(450, fy + 300 - 65, 450))
        for q in parts:
            if q.get("n") == "14.4":
                q["grain"] = "x"
        p += parts
        moves.append(mv)
    # doors 10 / 11: 1356 × 446, y 934..2290, handles UA-AA-06-128 horizontal just above the door bottom (cut-out p. 112)
    d1 = [P("10", [2, 934, D, 448, 2290, zf], "10", kind="front"), handle("h-10", 312, 990, zf, hw="011")]
    d2 = [P("11", [452, 934, D, 898, 2290, zf], "11", kind="front"), handle("h-11", 588, 990, zf, hw="011")]
    p += d1 + d2
    moves += [door("door_left", d1, "left"), door("door_right", d2, "right")]
    model("yunona-layt-1-55", "П3.0582.1.55", "Шкаф для одежды 2Д «Юнона Лайт»", "bedroom", [900, 595, 2292], 112,
          "по инструкции П582.01; две двери над тремя ящиками", **{"is": "IS-P582-01-shkaf-2-1.pdf"})
    cutlist("yunona-layt-1-55", "П3.0582.1.55",
            "IS-P582-01-shkaf-2-1.pdf p. 1 (a.pinskdrev.ru; the PDF has a text layer, rows read off the table picture)",
            "Материалы: 1–4 ЛДСП 16 Дуб Версаль (= Каньон), 5, 6, 10–12, 14.1–14.3 ЛДСП 16 белый, 7–9, 14.5 ДВП "
            "ламинированная белая (толщина 3.2 принята), 14.4 ЛДСП 16 Дуб Версаль. Двери 10/11 белые в «Юноне» — в «Юноне "
            "Лайт» Бордо лайт (каталог). Row 11 (the second door) is missing from the PDF text; it is in the table picture.",
            [("1", "82.01.01", "Стенка вертикальная", [2240, 579, 16], 1),
             ("2", "82.01.02", "Стенка вертикальная", [2240, 579, 16], 1),
             ("3", "82.01.03", "Стенка горизонтальная", [900, 579, 16], 1),
             ("4", "82.01.04", "Стенка горизонтальная", [900, 579, 16], 1),
             ("5", "82.01.05", "Стенка горизонтальная (белый)", [867, 520, 16], 1),
             ("6", "82.01.06", "Стенка горизонтальная (белый)", [867, 560, 16], 1),
             ("7", "82.01.07", "Стенка задняя (ДВП)", [878, 372, BK], 1),
             ("8", "82.01.08", "Стенка задняя (ДВП)", [974, 438, BK], 2),
             ("9", "82.01.09", "Стенка задняя (ДВП)", [900, 438, BK], 2),
             ("10", "82.01.10", "Дверь", [1356, 446, 16], 1),
             ("11", "82.01.11", "Дверь", [1356, 446, 16], 1),
             ("12", "82.01.12", "Брусок (белый)", [960, 128, 16], 1),
             ("14.1", "82.01.14.1", "Стенка боковая ящика (белый)", [500, 224, 16], 3),
             ("14.2", "82.01.14.2", "Стенка боковая ящика (белый)", [500, 224, 16], 3),
             ("14.3", "82.01.14.3", "Стенка задняя ящика (белый)", [809.5, 205, 16], 3),
             ("14.4", "82.01.14.4", "Стенка передняя ящика (Дуб Версаль)", [896, 300, 16], 3),
             ("14.5", "82.01.14.5", "Дно ящика (ДВП)", [820, 505, BK], 3)])
    return dump("yunona-layt-1-55", [900, 595, 2292], p, moves)


def w156():
    """Шкаф для одежды 2Д П3.0582.1.56 = П582.02: two full-height doors, hat shelf, rail, lower shelf."""
    W, D, zf = 900, 579, 595
    p = wardrobe_carcass(W)
    p += [P("6", [16.5, 381, 10, 883.5, 397, 530], "6", mat="white"),
          P("5", [16.5, 1901, 10, 883.5, 1917, 530], "5", mat="white"),
          P("7", [386, 397, 10, 514, 1901, 26], "7", mat="white"),
          P("9", [11, 1910, 6, 889, 2282, 6 + BK], "9", kind="back"),
          P("10-1", [11, 390, 6, 449, 1908, 6 + BK], "10", kind="back"),
          P("10-2", [451, 390, 6, 889, 1908, 6 + BK], "10", kind="back"),
          P("11", [11, 31, 6, 889, 387, 6 + BK], "11", kind="back"),
          {"id": "rail", "kind": "tube", "mat": "chrome", "box": [19, 1850, 282, 881, 1865, 312], "covers": ["018"]}]
    d1 = [P("8-1", [2, 24, D, 448, 2290, zf], "8", kind="front"), handle("h-1", 394, 1140, zf, 450, "up", "010")]
    d2 = [P("8-2", [452, 24, D, 898, 2290, zf], "8", kind="front"), handle("h-2", 506, 1140, zf, 450, "up", "010")]
    p += d1 + d2
    moves = [door("door_left", d1, "left"), door("door_right", d2, "right")]
    model("yunona-layt-1-56", "П3.0582.1.56", "Шкаф для одежды 2Д «Юнона Лайт»", "bedroom", [900, 595, 2292], 112,
          "по инструкции П582.02; полка, штанга, нижняя полка", **{"is": "IS-P582-02-shkaf-2-1.pdf"})
    cutlist("yunona-layt-1-56", "П3.0582.1.56",
            "IS-P582-02-shkaf-2-1.pdf p. 1, rows read off the table picture (the PDF text lists positions 6–11 in a "
            "scrambled order: the picture is authoritative)",
            "Материалы: 1–4 ЛДСП 16 Дуб Версаль (= Каньон), 5–8 ЛДСП 16 белый (двери 8 — Бордо лайт в «Юноне Лайт»), "
            "9–11 ДВП ламинированная белая (3.2 принята).",
            [("1", "82.02.01", "Стенка вертикальная", [2240, 579, 16], 1),
             ("2", "82.02.02", "Стенка вертикальная", [2240, 579, 16], 1),
             ("3", "82.02.03", "Стенка горизонтальная", [900, 579, 16], 1),
             ("4", "82.02.04", "Стенка горизонтальная", [900, 579, 16], 1),
             ("5", "82.02.05", "Стенка горизонтальная (белый)", [867, 520, 16], 1),
             ("6", "82.02.06", "Стенка горизонтальная (белый)", [867, 520, 16], 1),
             ("7", "82.02.07", "Брусок (белый)", [1504, 128, 16], 1),
             ("8", "82.02.08", "Дверь", [2266, 446, 16], 2),
             ("9", "82.02.06", "Стенка задняя (ДВП)", [878, 372, BK], 1),
             ("10", "82.02.07", "Стенка задняя (ДВП)", [1518, 438, BK], 2),
             ("11", "82.02.08", "Стенка задняя (ДВП)", [878, 356, BK], 1)])
    return dump("yunona-layt-1-56", [900, 595, 2292], p, moves)


def w450(mid, code, shelves):
    """Шкаф для одежды 450 (1.11 hanging: hat shelf + rail + lower shelf, like one half of 1.56; 1.65: shelves) — by the
    p. 112 cut-outs and schemes; door hinged right (the handle by its left edge in both cut-outs and on p. 111)."""
    W, D, zf = 450, 579, 595
    p = wardrobe_carcass(W, ("side-l", "side-r", "top", "bottom"))
    p += [P("shelf-low", [16.5, 381, 10, 433.5, 397, 530], mat="white"),
          P("shelf-top", [16.5, 1901, 10, 433.5, 1917, 530], mat="white"),
          P("back-top", [11, 1910, 6, 439, 2282, 6 + BK], kind="back"),
          P("back-mid", [11, 390, 6, 439, 1908, 6 + BK], kind="back"),
          P("back-low", [11, 31, 6, 439, 387, 6 + BK], kind="back")]
    if shelves:
        step = (1504 - 2 * T) / 3
        for i in range(2):
            y = 397 + step * (i + 1) + T * i
            p.append(P(f"shelf-{i + 1}", [16.5, y, 10, 433.5, y + T, 530], mat="white"))
    else:
        p.append({"id": "rail", "kind": "tube", "mat": "chrome", "box": [19, 1850, 282, 431, 1865, 312], "covers": ["rail"]})
    d = [P("door", [2, 24, D, 448, 2290, zf], kind="front"), handle("h-door", 62, 1140, zf, 450, "up")]
    p += d
    what = "полки (4 полки, как стеллаж)" if shelves else "полка, штанга, нижняя полка (половина 1.56)"
    model(mid, code, "Шкаф для одежды «Юнона Лайт»", "bedroom", [450, 595, 2292], 112,
          f"{BYPHOTO}; по конструкции П582.02; {what}; дверь на правых петлях")
    return dump(mid, [450, 595, 2292], p, [door("door", d, "right")])


# ------------------------------------------------------------------------------------------------ 1.57 / 1.15 стеллажи
def shelving(mid, W, D, ns):
    """Стеллаж 2292 high: top and bottom W × D over the sides 2240 × D, four fixed shelves (5 equal compartments),
    the back in two ДВП pieces (900 below, 1348 above) joined on shelf 2."""
    H = 2292
    nn = (lambda k: k) if ns else (lambda k: None)
    p = [P("3" if ns else "top", [0, 2276, 0, W, H, D], nn("3")),
         P("4" if ns else "bottom", [0, 20, 0, W, 36, D], nn("4")),
         P("1" if ns else "side-l", [0, 36, 0, T, 2276, D], nn("1")),
         P("2" if ns else "side-r", [W - T, 36, 0, W, 2276, D], nn("2"))]
    step = (2240 - 4 * T) / 5
    sw = W - 2 * T - 1
    zs0, zs1 = (25, 565) if ns else (10, D - 6)
    for i in range(4):
        y = 36 + step * (i + 1) + T * i
        p.append(P(f"5-{i + 1}" if ns else f"shelf-{i + 1}", [T + 0.5, y, zs0, T + 0.5 + sw, y + T, zs1], nn("5")))
    bw = W - 2 * T + 10
    j = 36 + 2 * step + T + T / 2                         # the joint on shelf 2
    p += [P("7" if ns else "back-low", [T - 5, 31, 6, T - 5 + bw, 31 + 900, 6 + BK], nn("7"), kind="back"),
          P("6" if ns else "back-up", [T - 5, 2281 - 1348, 6, T - 5 + bw, 2281, 6 + BK], nn("6"), kind="back")]
    p += [fband(q) for q in p if q.get("kind") is None]
    p += glides([60, W - 60], [40, D - 40], "006")
    return p, j


def s157():
    p, _ = shelving("yunona-layt-1-57", 252, 579, True)
    model("yunona-layt-1-57", "П3.0582.1.57", "Стеллаж «Юнона Лайт»", "bedroom", [252, 579, 2292], 112,
          "по инструкции П582.03; узкий глубокий стеллаж, 4 полки", **{"is": "IS-P582-03-stellaj-2.pdf"})
    cutlist("yunona-layt-1-57", "П3.0582.1.57", "IS-P582-03-stellaj-2.pdf p. 1, rows read off the table picture",
            "Материалы: 1–5 ЛДСП 16 Дуб Версаль (= Каньон), 6, 7 ДВП ламинированная белая (3.2 принята; в «Юноне Лайт» "
            "задняя стенка — Бордо лайт, фото 1.15). Полки 5 — 4 шт. (текст PDF путает номера 5–7).",
            [("1", "82.03.01", "Стенка вертикальная", [2240, 579, 16], 1),
             ("2", "82.03.02", "Стенка вертикальная", [2240, 579, 16], 1),
             ("3", "82.03.03", "Стенка горизонтальная", [252, 579, 16], 1),
             ("4", "82.03.04", "Стенка горизонтальная", [252, 579, 16], 1),
             ("5", "82.03.05", "Стенка горизонтальная (полка)", [219, 540, 16], 4),
             ("6", "82.03.06", "Стенка задняя (ДВП)", [1348, 230, BK], 1),
             ("7", "82.03.07", "Стенка задняя (ДВП)", [900, 230, BK], 1)])
    return dump("yunona-layt-1-57", [252, 579, 2292], p, [])


def s115():
    p, _ = shelving("yunona-layt-1-15", 579, 252, False)
    model("yunona-layt-1-15", "П3.0582.1.15", "Стеллаж «Юнона Лайт»", "bedroom", [579, 252, 2292], 112,
          f"{BYPHOTO}; стеллаж 1.57, развёрнутый к фронту 579: 4 полки, задняя стенка Бордо лайт")
    return dump("yunona-layt-1-15", [579, 252, 2292], p, [])


# ------------------------------------------------------------------------------------------------ bedside tables, chest
def bedside_carcass(W, H, sides_h, ns):
    """Top and bottom W × 441, sides sides_h × 439 between them (flush at the front, 2 mm short at the back), ДВП back
    in grooves, four glides 20."""
    D = 441
    yb, yt = 20, 20 + T + sides_h
    p = [P(ns[0], [0, yt, 0, W, yt + T, D], ns[0] if ns[0][0].isdigit() else None),
         P(ns[1], [0, yb, 0, W, yb + T, D], ns[1] if ns[1][0].isdigit() else None),
         P(ns[2], [0, yb + T, 2, T, yt, D], ns[2] if ns[2][0].isdigit() else None),
         P(ns[3], [W - T, yb + T, 2, W, yt, D], ns[3] if ns[3][0].isdigit() else None)]
    p += [fband(q) for q in p]
    bw, bh = W - 2 * T + 8, sides_h + 10
    p.append(P(ns[4], [T - 4, yb + T - 5, 6, T - 4 + bw, yb + T - 5 + bh, 6 + BK], ns[4] if ns[4][0].isdigit() else None,
               kind="back"))
    p += glides([60, W - 60], [40, D - 40], "006")
    return p


def t160():
    """Тумба прикроватная П3.0582.1.60 = П582.06: a drawer 198 over an open niche, the rail 6 (508 × 76) between."""
    W, D = 542, 441
    p = bedside_carcass(W, 460, 408, ("1", "2", "3", "4", "5"))
    rail = P("6", [17, 224, D - 76, 525, 240, D], "6")
    p += [rail, fband(rail)]
    parts, mv = drawer("7", [19, 243, D - T, 523, 441, D], "kanon", (29.75, 512.25), 263, 128, 109, D - T - 350, D - T,
                       ns=("7.4", "7.1", "7.2", "7.3", "7.5"), hdl=(271, 392))
    p += parts
    model("yunona-layt-1-60", "П3.0582.1.60", "Тумба прикроватная «Юнона Лайт»", "bedroom", [542, 441, 460], 112,
          "по инструкции П582.06; ящик над открытой нишей", **{"is": "IS-P582-06-tumba-prikrovatnaya-3-1.pdf"})
    cutlist("yunona-layt-1-60", "П3.0582.1.60", "IS-P582-06-tumba-prikrovatnaya-3-1.pdf p. 1, rows read off the table "
            "picture (the PDF text swaps rows 2/3: 2 is the bottom, 3/4 the sides)",
            "Материалы: 1–4, 6, 7.4 ЛДСП 16 Дуб Версаль (= Каньон), 7.1–7.3 ЛДСП 16 белый, 5, 7.5 ДВП ламинированная белая "
            "(3.2 принята). The same file is linked by index.json for the chest 1.21 (a different product).",
            [("1", "82.06.01", "Крышка", [542, 441, 16], 1),
             ("2", "82.06.02", "Дно", [542, 441, 16], 1),
             ("3", "82.06.03", "Стенка вертикальная", [408, 439, 16], 1),
             ("4", "82.06.04", "Стенка вертикальная", [408, 439, 16], 1),
             ("5", "82.06.05", "Стенка задняя (ДВП)", [518, 418, BK], 1),
             ("6", "82.06.06", "Брусок", [508, 76, 16], 1),
             ("7.1", "82.06071", "Стенка боковая ящика (белый)", [350, 128, 16], 1),
             ("7.2", "82.06072", "Стенка боковая ящика (белый)", [350, 128, 16], 1),
             ("7.3", "82.06073", "Стенка задняя ящика (белый)", [450.5, 109, 16], 1),
             ("7.4", "82.06074", "Стенка передняя ящика (Дуб Версаль)", [504, 198, 16], 1),
             ("7.5", "82.06075", "Дно ящика (ДВП)", [461, 355, BK], 1)])
    return dump("yunona-layt-1-60", [542, 441, 460], p, [mv])


def t118():
    """Тумба прикроватная П3.0582.1.18 (by photo): 1.60 upside down — the drawer at the bottom, a full shelf (the niche
    floor) over it, the open niche on top."""
    W, D = 542, 441
    p = bedside_carcass(W, 460, 408, ("top", "bottom", "side-l", "side-r", "back"))
    sh = P("shelf", [17, 240, 18, 525, 256, D])
    p += [sh, fband(sh)]
    parts, mv = drawer("1", [19, 39, D - T, 523, 237, D], "kanon", (29.75, 512.25), 59, 128, 109, D - T - 350, D - T,
                       hdl=(271, 188))
    p += parts
    model("yunona-layt-1-18", "П3.0582.1.18", "Тумба прикроватная «Юнона Лайт»", "bedroom", [542, 441, 460], 112,
          f"{BYPHOTO}; детали П582.06 (1.60), ящик внизу, ниша сверху")
    return dump("yunona-layt-1-18", [542, 441, 460], p, [mv])


def k121():
    """Комод П3.0582.1.21 (by photo): the bedside construction 1254 high, five inset drawers (two 196, three 264)."""
    W, D = 540, 441
    p = bedside_carcass(W, 1254, 1202, ("top", "bottom", "side-l", "side-r", "back"))
    moves = []
    y = 36 + G
    for i, h in enumerate([264, 264, 264, 196, 196]):
        bh = 128 if h < 200 else 192
        parts, mv = drawer(str(5 - i), [T + G, y, D - T, W - T - G, y + h, D], "kanon", (28.75, 511.25), y + 20, bh,
                           bh - 19, D - T - 350, D - T, hdl=(W / 2, y + h - round(0.27 * h)))
        p += parts
        moves.append(mv)
        y += h + G
    model("yunona-layt-1-21", "П3.0582.1.21", "Комод «Юнона Лайт»", "bedroom", [540, 441, 1254], 112,
          f"{BYPHOTO}; конструкция тумбы П582.06 (ссылка index.json на инструкцию — это тумба 1.60); 5 ящиков")
    return dump("yunona-layt-1-21", [540, 441, 1254], p, moves)


# ------------------------------------------------------------------------------------------------ sideboards 1.62 / 1.63
def sideboard(mid, code, W, left_doors):
    """Тумба 850 high, B 400: top / bottom W × 400 over the sides 798 × 398; left: one (1.62) or two (1.63) doors
    (Бордо лайт), right column: two drawers (Каньон) over a door, the partition behind the joint (the fronts cover it)."""
    D, H = 400, 850
    p = [P("top", [0, 834, 0, W, H, D]), P("bottom", [0, 20, 0, W, 36, D]),
         P("side-l", [0, 36, 2, T, 834, D]), P("side-r", [W - T, 36, 2, W, 834, D])]
    p += [fband(q) for q in p]
    xs = W - T - G - 352.5 - 1.5                         # the joint of the right column (its fronts are 352.5 wide)
    p += [P("partition", [xs - 8, 36, 10, xs + 8, 834, D - T]),
          P("back", [T - 5, 31, 6, W - T + 5, 839, 6 + BK], kind="back"),
          P("shelf-r", [xs + 8, 478, 10, W - T, 494, D - T], mat="white")]
    for i, y in enumerate([290, 560]):
        p.append(P(f"shelf-l{i + 1}", [T + 1, y, 20, xs - 9, y + T, D - T - 4], mat="white"))
    fz0 = D - T
    moves = []
    xr0, xr1 = xs + 1.5, W - T - G
    for i, (y0, y1) in enumerate([(665, 831), (496, 662)]):
        cx = (xr0 + xr1) / 2
        parts, mv = drawer(str(i + 1), [xr0, y0, fz0, xr1, y1, D], "kanon", (xs + 8 + 13.5, W - T - 13.5), y0 + 20, 110,
                           91, fz0 - 350, fz0, hdl=(cx, y1 - 45))
        p += parts
        moves.append(mv)
    dr = [P("door-r", [xr0, 39, fz0, xr1, 493, D], kind="front"), handle("h-door-r", (xr0 + xr1) / 2, 493 - 45, D)]
    p += dr
    xl0, xl1 = T + G, xs - 1.5
    if left_doors == 1:
        dl = [P("door-l", [xl0, 39, fz0, xl1, 831, D], kind="front"), handle("h-door-l", (xl0 + xl1) / 2, 831 - 45, D)]
        p += dl
        moves += [door("door_left", dl, "left")]
    else:
        xm = (xl0 + xl1) / 2
        dl = [P("door-l", [xl0, 39, fz0, xm - 1.5, 831, D], kind="front"),
              handle("h-door-l", (xl0 + xm - 1.5) / 2, 831 - 45, D)]
        dm = [P("door-m", [xm + 1.5, 39, fz0, xl1, 831, D], kind="front"),
              handle("h-door-m", (xm + 1.5 + xl1) / 2, 831 - 45, D)]
        p += dl + dm
        moves += [door("door_left", dl, "left"), door("door_middle", dm, "right")]
    moves.append(door("door_right", dr, "right"))
    p += glides([60, xs, W - 60], [40, D - 40], "glide")
    return p, moves


def t162():
    p, mv = sideboard("yunona-layt-1-62", "П3.0582.1.62", 803, 1)
    model("yunona-layt-1-62", "П3.0582.1.62", "Тумба «Юнона Лайт»", "bedroom", [803, 400, 850], 112,
          f"{BYPHOTO}; B400 по с. 111 и index.json (с. 112 печатает B415); дверь слева, справа 2 ящика над дверью")
    return dump("yunona-layt-1-62", [803, 400, 850], p, mv)


def t163():
    p, mv = sideboard("yunona-layt-1-63", "П3.0582.1.63", 1200, 2)
    model("yunona-layt-1-63", "П3.0582.1.63", "Тумба «Юнона Лайт»", "bedroom", [1200, 400, 850], 112,
          f"{BYPHOTO}; две двери слева, справа 2 ящика над дверью")
    return dump("yunona-layt-1-63", [1200, 400, 850], p, mv)


# ------------------------------------------------------------------------------------------------ shelf, mirrors
def p164():
    """Полка П3.0582.1.64 (by photo): a board 800 × 230 with two uprights 214 at its ends, no back; on the wall."""
    p = [P("bottom", [0, 0, 0, 800, 16, 230]), P("upright-l", [0, 16, 0, 16, 230, 230]), P("upright-r", [784, 16, 0, 800, 230, 230])]
    p += [fband(q) for q in p]
    model("yunona-layt-1-64", "П3.0582.1.64", "Полка «Юнона Лайт»", "decor", [800, 230, 230], 112,
          f"{BYPHOTO}; доска 800 и две стойки по краям, без задней стенки", mount="wall")
    return dump("yunona-layt-1-64", [800, 230, 230], p, [])


def m125():
    """Зеркало П3.0582.1.25 (by photo): a faceted mirror 4 on a Каньон backing board 16 (its edge shows round it)."""
    p = [P("board", [0, 0, 0, 939, 751, 16]),
         {"id": "mirror", "kind": "mirror", "edge": 3, "box": [2, 2, 16, 937, 749, 20]}]
    model("yunona-layt-1-25", "П3.0582.1.25", "Зеркало «Юнона Лайт»", "decor", [939, 20, 751], 112,
          f"{BYPHOTO}; зеркало с фацетом на основе ЛДСП Каньон; крепление к стене", mount="wall")
    return dump("yunona-layt-1-25", [939, 20, 751], p, [])


def m159():
    """Зеркало П3.0582.1.59 (by photo): a folding triptych — a centre panel 497 and two wings 247 on hinges, each a
    mirror 4 on a Каньон backing 16; the wings fold forward (door moves)."""
    p, moves = [], []
    panels = [("wing-l", 0, 247), ("centre", 249, 746), ("wing-r", 748, 995)]
    groups = {}
    for name, x0, x1 in panels:
        g = [P(f"{name}-board", [x0, 0, 0, x1, 700, 16], kind="front", mat="kanon"),
             {"id": f"{name}-mirror", "kind": "mirror", "edge": 1, "box": [x0 + 2, 2, 16, x1 - 2, 698, 20]}]
        groups[name] = g
        p += g
    for x in (247, 746):
        for i, y in enumerate((110, 590)):
            p.append({"id": f"hinge-{int(x)}-{i + 1}", "kind": "panel", "mat": "gold", "edge": 0.3,
                      "box": [x + 0.3, y - 30, 2, x + 1.7, y + 30, 18]})
    moves = [door("wing_left", groups["wing-l"], "right", 35), door("wing_right", groups["wing-r"], "left", 35)]
    model("yunona-layt-1-59", "П3.0582.1.59", "Зеркало «Юнона Лайт»", "decor", [995, 20, 700], 112,
          f"{BYPHOTO}; складное трёхстворчатое (створки 247 + 497 + 247 на петлях), настольное — поставлено на стену",
          mount="wall")
    return dump("yunona-layt-1-59", [995, 20, 700], p, moves)


# ------------------------------------------------------------------------------------------------ dressing table, desk
def st158():
    """Стол туалетный П3.0582.1.58 = П582.04: top 1066 × 441 on two side panels 780 (2 mm in from its ends), a drawer
    (Каньон front 1026 × 135, organiser partitions) over the shelf 5, the modesty panel 6 at the back; nail glides."""
    W, D = 1066, 441
    p = [P("2", [0, 784, 0, W, 800, D], "2"),
         P("3", [2, 4, 0, 18, 784, 439], "3"), P("4", [1048, 4, 0, 1064, 784, 439], "4"),
         P("5", [18, 629, 16, 1048, 645, 438], "5"), P("6", [18, 368, 0, 1048, 784, 16], "6")]
    p += [fband(q) for q in p if q.get("n") != "6"]
    p += nails([(10, 30), (10, 409), (1056, 30), (1056, 409)], "007")
    x0, x1, z0, zf = 30.75, 1035.25, 39, 423
    y0 = 667
    hw = 308.5 / 2
    extra = [P("1.6", [533 - hw - T, y0 + 19, z0 + T, 533 - hw, y0 + 96, zf], "1.6", mat="white"),
             P("1.7", [533 + hw, y0 + 19, z0 + T, 533 + hw + T, y0 + 96, zf], "1.7", mat="white"),
             P("1.8", [533 - hw, y0 + 19, z0 + 150, 533 + hw, y0 + 96, z0 + 150 + T], "1.8", mat="white")]
    parts, mv = drawer("1", [20, 647, 423, 1046, 782, 439], "kanon", (x0, x1), y0, 96, 77, z0, zf,
                       ns=("1.4", "1.1", "1.2", "1.3", "1.5"), hdl=(533, 728, 450), extra=extra)
    for q in parts:
        if q.get("n") == "1.4":
            q["grain"] = "x"
    p += parts
    model("yunona-layt-1-58", "П3.0582.1.58", "Стол туалетный «Юнона Лайт»", "bedroom", [1066, 441, 800], 112,
          "по инструкции П582.04; ящик с перегородками", **{"is": "IS-P582-04-stol-tualetnyiy-1-1.pdf"})
    cutlist("yunona-layt-1-58", "П3.0582.1.58", "IS-P582-04-stol-tualetnyiy-1-1.pdf p. 1, rows read off the table picture",
            "Материалы: 2–6 и 1.4 ЛДСП 16 Дуб Версаль (= Каньон), 1.1–1.3, 1.6–1.8 ЛДСП 16 белый, 1.5 ДВП ламинированная "
            "белая (3.2 принята).",
            [("1.1", "82.04011", "Стенка боковая ящика (белый)", [384, 96, 16], 1),
             ("1.2", "82.04012", "Стенка боковая ящика (белый)", [384, 96, 16], 1),
             ("1.3", "82.04013", "Стенка задняя ящика (белый)", [972.5, 77, 16], 1),
             ("1.4", "82.04014", "Стенка передняя ящика (Дуб Версаль)", [1026, 135, 16], 1),
             ("1.5", "82.04015", "Дно ящика (ДВП)", [983, 389, BK], 1),
             ("1.6", "82.04016", "Перегородка (белый)", [368, 77, 16], 1),
             ("1.7", "82.04017", "Перегородка (белый)", [368, 77, 16], 1),
             ("1.8", "82.04018", "Перегородка (белый)", [308.5, 77, 16], 1),
             ("2", "82.04.02", "Крышка", [1066, 441, 16], 1),
             ("3", "82.04.03", "Стенка вертикальная", [780, 439, 16], 1),
             ("4", "82.04.04", "Стенка вертикальная", [780, 439, 16], 1),
             ("5", "82.04.05", "Стенка горизонтальная", [1030, 422, 16], 1),
             ("6", "82.04.06", "Царга", [1030, 416, 16], 1)])
    return dump("yunona-layt-1-58", [1066, 441, 800], p, [mv])


def desk(mid, code, mirrored):
    """Стол П3.0582.1.26 / 1.26-01 (by catalogue): the dressing-table construction 1342 × 441 × 780 (a drawer with a
    Бордо лайт front over a shelf, the modesty panel at the back) and, under its right end, a low return 448 wide
    running forward to B 1051: two side panels, a top at 590, and a cabinet with a door (Бордо лайт) at its front end;
    its rear part under the desk is open. -01: the mirror image (the return at the left, as on p. 111)."""
    W, D, H = 1342, 441, 780
    p = [P("top", [0, 764, 0, W, H, D]), P("side-l", [2, 4, 0, 18, 764, 439]), P("side-r", [W - 18, 4, 0, W - 2, 764, 439]),
         P("shelf", [18, 609, 16, W - 18, 625, 438]), P("modesty", [18, 348, 0, W - 18, 764, 16])]
    p += [fband(q) for q in p if q["id"] != "modesty"]
    p += nails([(10, 30), (10, 409), (W - 10, 30), (W - 10, 409)], "nail")
    x0, x1 = 18 + 12.75, W - 18 - 12.75
    parts, mv = drawer("1", [20, 627, 423, W - 20, 762, 439], None, (x0, x1), 647, 96, 77, 39, 423, hdl=(W / 2, 708, 450))
    p += parts
    moves = [mv]
    # the return (x 870..1318, z 20..1051)
    rx0, rx1, rz0, rz1 = 870, 1318, 20, 1051
    ret = [P("r-top", [rx0, 574, rz0, rx1, 590, rz1]),
           P("r-side-l", [rx0, 4, rz0, rx0 + T, 574, rz1]), P("r-side-r", [rx1 - T, 4, rz0, rx1, 574, rz1]),
           P("r-bottom", [rx0 + T, 30, 611, rx1 - T, 46, rz1]),
           P("r-back", [rx0 + T, 46, 595, rx1 - T, 574, 611]),
           P("r-shelf", [rx0 + T + 1, 300, 620, rx1 - T - 1, 316, rz1 - T - 4], mat="white")]
    ret += [fband(q) for q in ret if q["id"] in ("r-top", "r-side-l", "r-side-r", "r-bottom")]
    ret += nails([(rx0 + 8, rz0 + 20), (rx0 + 8, rz1 - 20), (rx1 - 8, rz0 + 20), (rx1 - 8, rz1 - 20)], "nail")
    for q in ret[-4:]:
        q["id"] = "r-" + q["id"]
    dr = [P("r-door", [rx0 + T + G, 49, rz1 - T, rx1 - T - G, 571, rz1], kind="front"),
          handle("h-r-door", (rx0 + rx1) / 2, 571 - 45, rz1)]
    p += ret + dr
    moves.append(door("door", dr, "right"))
    size = [W, 1051, H]
    if mirrored:
        p = [mirror_x(q, W) for q in p]
        for m in moves:
            if m["type"] == "door":
                m["hinge"] = "left" if m["hinge"] == "right" else "right"
    note = (f"по каталогу, без инструкции; письменный стол (конструкция П582.04) с приставной тумбой-приставкой под правым "
            f"концом (ящик — Бордо лайт){'; зеркальное исполнение: приставка слева' if mirrored else ''}")
    model(mid, code, "Стол «Юнона Лайт»" + (" (зеркальный)" if mirrored else ""), "office", size, 112 if not mirrored else 111,
          note)
    return dump(mid, size, p, moves)


def mirror_x(q, W):
    q = json.loads(json.dumps(q))
    if "box" in q:
        b = q["box"]
        q["box"] = [round(W - b[3], 2), b[1], b[2], round(W - b[0], 2), b[4], b[5]]
    if q.get("kind") == "handle":
        q["at"][0] = round(W - q["at"][0], 2)
    if q.get("kind") == "moulding":
        q["path"] = [[round(W - a, 2), b] for a, b in q["path"]][::-1]
        q["side"] = -q.get("side", 1)
        # a reversed path with the side flipped keeps the band on the same side of the edge
        q["side"] = -1 if q["side"] == 1 else 1
        q["path"] = q["path"][::-1]
        if q["path"][0][0] > q["path"][-1][0] or q["path"][0][1] > q["path"][-1][1]:
            q["path"] = q["path"][::-1]
        b = q["box"]
        if abs(b[3] - b[0]) < abs(b[4] - b[1]):      # vertical band: the path runs along the edge's left x
            q["path"] = [[b[0], b[1]], [b[0], b[4]]]
        else:
            q["path"] = [[b[0], b[4]], [b[3], b[4]]]
        q["side"] = -1
    return q


def d126():
    return desk("yunona-layt-1-26", "П3.0582.1.26", False)


def d12601():
    return desk("yunona-layt-1-26-01", "П3.0582.1.26-01", True)


# ------------------------------------------------------------------------------------------------ beds
def bed(mid, code, name, W, H, ns, head, base, note, is_file=None):
    """П582.07 construction: headboard 1.3 (W × 885) on nail glides with two Каньон strips 1.1 / 1.4 (877 × 128) at its
    ends and a Бордо лайт panel 1.2 (W − 272 × 256) at the top — or the upholstered pad — and a Бордо лайт strip 1.5 (128)
    lower down; rails 3.1 (2010 × 200) between the headboard layer and the foot 2.1 (W − 64 × 320, on the floor), the
    Бордо лайт overlays 3.2 (2026 × 128) on the rails' outer faces and 2.2 (W − 32 × 128) on the foot; W × 2074 × H."""
    g = H - 885                                        # nail glides (4 on the double, 5 on the single)
    L = 2074
    n = (lambda k: k) if ns else (lambda k: None)
    pw = W - 272
    p = [P(n("1.3") or "headboard", [0, g, 0, W, g + 885, T], n("1.3"), grain="x"),
         P(n("1.4") or "strip-l", [0, g + 8, T, 128, g + 885, 2 * T], n("1.4")),
         P(n("1.1") or "strip-r", [W - 128, g + 8, T, W, g + 885, 2 * T], n("1.1")),
         P(n("1.5") or "panel-low", [136, g + 365, T, 136 + pw, g + 493, 2 * T], n("1.5"), mat="bordo", grain="x")]
    if head == "panel":
        p.append(P(n("1.2") or "panel", [136, g + 621, T, 136 + pw, g + 877, 2 * T], n("1.2"), mat="bordo", grain="x"))
    else:
        cols = 8 if W > 1200 else 4
        p.append({"id": "pad", "kind": "soft", "mat": "fabric", "tufts": [cols, 2], "box": [136, g + 517, T, 136 + pw, g + 877, 2 * T + 40]})
    ry0 = g + 120
    p += [P(n("3.1") and "3.1-l" or "rail-l", [T, ry0, 2 * T, 2 * T, ry0 + 200, 2 * T + 2010], n("3.1"), grain="z"),
          P(n("3.1") and "3.1-r" or "rail-r", [W - 2 * T, ry0, 2 * T, W - T, ry0 + 200, 2 * T + 2010], n("3.1"), grain="z"),
          P(n("3.2") and "3.2-l" or "overlay-l", [0, ry0 + 36, 2 * T, T, ry0 + 164, 2 * T + 2026], n("3.2"), mat="bordo", grain="z"),
          P(n("3.2") and "3.2-r" or "overlay-r", [W - T, ry0 + 36, 2 * T, W, ry0 + 164, 2 * T + 2026], n("3.2"), mat="bordo", grain="z"),
          P(n("2.1") or "foot", [2 * T, g, 2 * T + 2010, W - 2 * T, g + 320, 2 * T + 2010 + T], n("2.1"), grain="x"),
          P(n("2.2") or "foot-overlay", [T, ry0 + 36, L - T, W - T, ry0 + 164, L], n("2.2"), mat="bordo", grain="x")]
    pts = [(x, 8) for x in (40, W / 2, W - 40)] + [(x, 2 * T + 2010 + 8) for x in (60, W / 2, W - 60)]
    p += nails(pts, "001", h=g, d=16)
    sleep = W - 106
    fx0, fx1, fz0, fz1 = (W - sleep) / 2, (W + sleep) / 2, 2 * T + 5, 2 * T + 5 + 2000
    if base == "metal":
        # «Основание гибкое WS 1.01 (2000 × W/230-6)»: black tube frame (the double one in two halves), birch slats on
        # plastic holders, six legs; the slats' top at 238, the mattress on them
        halves = [(fx0, fx1)] if sleep < 1200 else [(fx0, W / 2), (W / 2, fx1)]
        k = 0
        for a, b in halves:
            k += 1
            p += [{"id": f"m{k}-rail-l", "kind": "panel", "mat": "black", "box": [a, 200, fz0, a + 25, 230, fz1], **({"covers": ["002"]} if k == 1 else {})},
                  {"id": f"m{k}-rail-r", "kind": "panel", "mat": "black", "box": [b - 25, 200, fz0, b, 230, fz1]},
                  {"id": f"m{k}-end-h", "kind": "panel", "mat": "black", "box": [a + 25, 200, fz0, b - 25, 230, fz0 + 25]},
                  {"id": f"m{k}-end-f", "kind": "panel", "mat": "black", "box": [a + 25, 200, fz1 - 25, b - 25, 230, fz1]}]
            for i in range(24):
                z = fz0 + 10 + i * 82.5
                p.append({"id": f"m{k}-slat-{i + 1}", "kind": "panel", "mat": "door_enamel_whitey#c9a877", "edge": 2,
                          "box": [a + 2, 230, z, b - 2, 238, z + 53]})
        legx = [W / 2 - 25, W / 2 + 25] if sleep >= 1200 else [fx0 + 12.5, fx1 - 12.5]
        k = 0
        for cx in legx:
            for z in (fz0 + 60, (fz0 + fz1) / 2, fz1 - 60):
                k += 1
                p.append({"id": f"m-leg-{k}", "kind": "tube", "mat": "black", "box": [cx - 11, 0, z - 11, cx + 11, 200, z + 11]})
        top = 238
    else:
        # slats on cleats screwed to the rails (no metal frame)
        p += [P("cleat-l", [2 * T, ry0 + 40, 2 * T, 2 * T + 25, ry0 + 80, 2 * T + 2010], mat="door_enamel_whitey#c9a877"),
              P("cleat-r", [W - 2 * T - 25, ry0 + 40, 2 * T, W - 2 * T, ry0 + 80, 2 * T + 2010], mat="door_enamel_whitey#c9a877")]
        for i in range(22):
            z = 2 * T + 30 + i * 90
            p.append({"id": f"slat-{i + 1}", "kind": "panel", "mat": "door_enamel_whitey#c9a877", "edge": 2,
                      "box": [2 * T + 25, ry0 + 80, z, W - 2 * T - 25, ry0 + 88, z + 53]})
        top = ry0 + 88
    p.append({"id": "mattress", "kind": "mattress", "box": [fx0, top, fz0, fx1, top + 200, fz1]})
    kw = {"is": is_file} if is_file else {}
    model(mid, code, name, "bedroom", [W, L, H], 112, note, **kw)
    return dump(mid, [W, L, H], p, [])


def b161():
    r = bed("yunona-layt-1-61", "П3.0582.1.61", "Кровать 2-16 «Юнона Лайт»", 1706, 889, True, "panel", "metal",
            "по инструкции П582.07; спальное место 2000×1600, основание WS 1.01 на опорах; изголовье с панелью Бордо лайт; "
            "каталог L1706×B2074 (L — ширина)", "IS-P582-07-krovat-dvoynaya-2.pdf")
    cutlist("yunona-layt-1-61", "П3.0582.1.61", "IS-P582-07-krovat-dvoynaya-2.pdf p. 1, rows read off the table picture",
            "Материалы: 1.1, 1.3, 1.4, 2.1, 3.1 ЛДСП 16 Дуб Версаль (= Каньон), 1.2, 1.5, 2.2, 3.2 ЛДСП 16 белый (в «Юноне "
            "Лайт» — Бордо лайт, фото). Основание гибкое WS 1.01 2000×1600 с опорами — покупное (002). The same file is "
            "linked by index.json for 1.28 (the upholstered-headboard bed).",
            [("1.1", "82.07011", "Накладка", [877, 128, 16], 1),
             ("1.2", "82.07012", "Накладка (белый)", [1434, 256, 16], 1),
             ("1.3", "82.07013", "Спинка головная", [1706, 885, 16], 1),
             ("1.4", "82.07014", "Накладка", [877, 128, 16], 1),
             ("1.5", "82.07015", "Накладка (белый)", [1434, 128, 16], 1),
             ("2.1", "82.07021", "Спинка ножная", [1642, 320, 16], 1),
             ("2.2", "82.07022", "Накладка (белый)", [1674, 128, 16], 1),
             ("3.1", "82.07031", "Царга", [2010, 200, 16], 2),
             ("3.2", "82.07032", "Накладка (белый)", [2026, 128, 16], 2)])
    return r


def b128():
    return bed("yunona-layt-1-28", "П3.0582.1.28", "Кровать 2-16 «Юнона Лайт»", 1706, 889, False, "soft", "metal",
               "по фото, без инструкции (index.json ссылается на инструкцию 1.61 — тот же файл); рама П582.07, вместо панели 1.2 "
               "мягкое изголовье с пуговицами; спальное место 2000×1600, основание WS на опорах; "
               "index.json L2074×B1706 — каталог с. 112 L1706×B2074")


def b145():
    return bed("yunona-layt-1-45", "П3.0582.1.45", "Кровать 1-09 «Юнона Лайт» с металлокаркасом", 1006, 890, False, "panel",
               "metal", f"{BYPHOTO}; рама П582.07 на ширину 1006; спальное место 2000×900, металлокаркас на опорах; "
               "изголовье с панелью Бордо лайт; index.json L2074×B1006 — каталог с. 112 L1006×B2074")


def b147():
    return bed("yunona-layt-1-47", "П3.0582.1.47", "Кровать 1-09 «Юнона Лайт»", 1006, 890, False, "soft", "slats",
               f"{BYPHOTO}; рама П582.07 на ширину 1006; мягкое изголовье с пуговицами; спальное место 2000×900, ламели на "
               "брусках царг")


# ------------------------------------------------------------------------------------------------ coupe wardrobes
def coupe(mid, code, name, W, mirror):
    """Шкаф-купе 2292 high, 650 deep (by catalogue: the p. 112 cut-outs and interior schemes, the product photos).
    Sides 650 to the floor-glides, top over them, a plinth 60 and the bottom between the sides; sliding doors in aluminium
    profile frames (a vertical profile 20 at each edge, top / bottom profiles 30) run between the sides on a bottom track
    and under a top track: upper filling Бордо лайт, lower 810 Каньон (1.05: the middle door a full mirror). Two tracks:
    2 doors — the left one behind; 3 doors — the middle one in front. Interior 550 deep, white."""
    D, H = 650, 2292
    p = [P("top", [0, 2276, 0, W, H, D]), P("side-l", [0, 20, 0, T, 2276, D]), P("side-r", [W - T, 20, 0, W, 2276, D]),
         P("plinth", [T, 20, D - T, W - T, 80, D]), P("plinth-back", [T, 20, 30, W - T, 80, 46]),
         P("bottom", [T, 80, 0, W - T, 96, D])]
    p += [fband(q) for q in p if q["id"] not in ("plinth", "plinth-back")]
    inner = W - 2 * T
    zi = 560                                            # interior front
    if W < 1800:
        parts_x = [898]
    else:
        parts_x = [676, 1351]
    xs = [T] + [x for c in parts_x for x in (c - 8, c + 8)] + [W - T]
    secs = [(xs[2 * i], xs[2 * i + 1]) for i in range(len(xs) // 2)]
    for i, c in enumerate(parts_x):
        p.append(P(f"partition-{i + 1}", [c - 8, 96, 10, c + 8, 2276, zi], mat="white"))
    shelf_y = [494, 836, 1180, 1525, 1867]
    hang = [0, len(secs) - 1] if len(secs) == 3 else [0]
    for k, (a, b) in enumerate(secs):
        if k in hang:
            p += [P(f"s{k + 1}-hat", [a, 1920, 10, b, 1936, zi], mat="white"),
                  P(f"s{k + 1}-low", [a, 440, 10, b, 456, zi], mat="white"),
                  P(f"s{k + 1}-rail-back", [a, 1130, 10, b, 1250, 26], mat="white"),
                  {"id": f"s{k + 1}-rail", "kind": "tube", "mat": "chrome", "box": [a + 3, 1855, 270, b - 3, 1870, 300]}]
        else:
            for j, y in enumerate(shelf_y):
                p.append(P(f"s{k + 1}-shelf-{j + 1}", [a, y, 10, b, y + T, zi], mat="white"))
        p.append(P(f"back-{k + 1}", [a - 5, 91, 6, b + 5, 2281, 6 + BK], kind="back"))
    # the backs of neighbouring sections meet behind the partitions: trim them to the partition's middle
    for i, c in enumerate(parts_x):
        for q in p:
            if q.get("id") == f"back-{i + 1}":
                q["box"][3] = c - 0.5
            if q.get("id") == f"back-{i + 2}":
                q["box"][0] = c + 0.5
    # tracks
    p += [{"id": "track-top", "kind": "panel", "mat": "metal", "edge": 0.5, "box": [T, 2266, 572, W - T, 2276, D - 4], "covers": ["track"]},
          {"id": "track-bottom", "kind": "panel", "mat": "metal", "edge": 0.5, "box": [T, 96, 572, W - T, 102, D - 4]}]
    n = 2 if W < 1800 else 3
    ov = 25
    dw = (inner + (n - 1) * ov) / n
    y0, y1, ysplit = 104, 2264, 104 + 810
    moves = []
    for i in range(n):
        x0 = T + i * (dw - ov)
        x1 = x0 + dw
        front = (i == 1 and n == 3) or (i == 1 and n == 2)
        z0, z1 = (612, 640) if front else (576, 604)
        zc = (z0 + z1) / 2
        tag = f"door{i + 1}"
        g = [P(f"{tag}-prof-l", [x0, y0, z0, x0 + 20, y1, z1], mat="metal", edge=1),
             P(f"{tag}-prof-r", [x1 - 20, y0, z0, x1, y1, z1], mat="metal", edge=1),
             P(f"{tag}-prof-b", [x0 + 20, y0, z0 + 4, x1 - 20, y0 + 30, z1 - 4], mat="metal", edge=0.5),
             P(f"{tag}-prof-t", [x0 + 20, y1 - 30, z0 + 4, x1 - 20, y1, z1 - 4], mat="metal", edge=0.5)]
        if mirror and i == 1:
            g += [P(f"{tag}-backing", [x0 + 12, y0 + 22, zc - 8, x1 - 12, y1 - 22, zc + 4], mat="white"),
                  {"id": f"{tag}-mirror", "kind": "mirror", "edge": 0.5, "box": [x0 + 12, y0 + 22, zc + 4, x1 - 12, y1 - 22, zc + 8]}]
        else:
            g += [P(f"{tag}-low", [x0 + 12, y0 + 22, zc - 8, x1 - 12, ysplit, zc + 8], kind="front", mat="kanon", grain="y"),
                  P(f"{tag}-up", [x0 + 12, ysplit, zc - 8, x1 - 12, y1 - 22, zc + 8], kind="front", grain="y")]
        p += g
        shift = dw - ov
        by = shift if i == 0 else -shift
        moves.append({"type": "slide", "name": f"coupe_{i + 1}", "parts": ids(g), "by": [round(by, 1), 0, 0]})
    # glides: under the sides' ends and under both plinth boards at the partitions
    k = 0
    for x0, x1 in ((0, T), (W - T, W)):
        for z in (40, D - 40):
            k += 1
            p.append({"id": f"glide-{k}", "kind": "panel", "mat": "black", "edge": 1, "box": [x0, 0, z - 20, x1, 20, z + 20], "covers": ["glide"]})
    for c in parts_x:
        for z0, z1 in ((30, 46), (D - T, D)):
            k += 1
            p.append({"id": f"glide-{k}", "kind": "panel", "mat": "black", "edge": 1, "box": [c - 20, 0, z0, c + 20, 20, z1], "covers": ["glide"]})
    model(mid, code, name, "bedroom", [W, D, H], 112,
          f"по каталогу, без инструкции: вырезка и схема с. 112, фото сайта; двери-купе в алюминиевом профиле, верх Бордо "
          f"лайт, низ Каньон{'; средняя дверь — зеркало' if mirror else ''}")
    return dump(mid, [W, D, H], p, moves)


def c102():
    return coupe("yunona-layt-1-02", "П3.0582.1.02", "Шкаф-купе 2д «Юнона Лайт»", 1529, False)


def c103():
    return coupe("yunona-layt-1-03", "П3.0582.1.03", "Шкаф-купе 3д «Юнона Лайт» (без зеркала)", 2027, False)


def c105():
    return coupe("yunona-layt-1-05", "П3.0582.1.05", "Шкаф-купе 3д «Юнона Лайт» (с зеркалом)", 2027, True)


# ------------------------------------------------------------------------------------------------ catalogue fragment
KANON, BORDO = "#978071", "#d4d4d8"
FINISHES = [{
    "id": "yunona-layt-kanon-bordo", "name": "Дуб Каньон / Дуб Бордо лайт",
    "body": f"door_enamel_whitey{KANON}", "front": f"door_enamel_whitey{BORDO}", "back": f"door_enamel_whitey{BORDO}",
    "roles": {"kanon": f"door_enamel_whitey{KANON}", "bordo": f"door_enamel_whitey{BORDO}",
              "edge": f"door_enamel_whitey{BORDO}", "fabric": "velvet#846d5d"},
    "swatch": KANON,
}]
PROFILES = {"yunona-layt-edge16": {"name": "Кромка 16 (светлая кромка Бордо лайт на торце ЛДСП Каньон)",
                                   "pts": [[0, 0], [0, EB], [16, EB], [16, 0]]}}
COLLECTION = {
    "id": SLUG, "name": "Юнона Лайт", "brand": "Пинскдрев", "finishes": ["yunona-layt-kanon-bordo"], "metal": "chrome#b6b0ab",
    "note": "Каталог «Корпусная мебель ч. II» 2025, PDF с. 109–112 (П3.0582). Корпус ЛДСП 16 «Дуб Каньон» со светлой кромкой "
            "(крышка и дно на всю ширину, боковины между ними), двери «Дуб Бордо лайт», фасады ящиков «Дуб Каньон», "
            "внутренние детали ЛДСП белый, задние стенки ДВП 3.2 в пазах; ручки-скобы UA-AA-06-128/416 (сатин-алюминий); "
            "шкафы, тумбы и стеллажи на опорах 88×54×20, столы и кровати на опорах-гвоздях; шкафы-купе в алюминиевом "
            "профиле. Инструкции «Юнона» П582.01–.07 (Дуб Версаль / белый) — для 1.55, 1.56, 1.57, 1.58, 1.60, 1.61.",
}


def write_catalog():
    frag = {"finishes": FINISHES, "profiles": PROFILES, "collections": [COLLECTION], "models": MODELS}
    path = os.path.join(HERE, "yunona-layt_catalog.json")
    with open(path, "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    for mid, cl in CUTLISTS.items():
        with open(os.path.join(HERE, "cutlists", mid + ".json"), "w") as fh:
            json.dump(cl, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
    return path


ALL = [w155, w156, lambda: w450("yunona-layt-1-11", "П3.0582.1.11", False),
       lambda: w450("yunona-layt-1-65", "П3.0582.1.65", True), s157, s115, t160, t118, k121, t162, t163, p164, m125,
       m159, st158, d126, d12601, b161, b128, b145, b147, c102, c103, c105]

if __name__ == "__main__":
    for f in ALL:
        print(f())
    print(write_catalog())
