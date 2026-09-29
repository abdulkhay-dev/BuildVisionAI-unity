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
    for f in [w131]:
        print(f())
    print(write_catalog())
