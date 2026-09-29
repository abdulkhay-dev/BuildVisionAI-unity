"""«Ирвинг» (Пинскдрев, БМ2.748): bedroom set in «Сосна Джексон» — all modules by catalogue / product photo (no
instructions are published for БМ2.748).

Construction (read off the catalogue pp. 94–96 and the pinskdrev.by photos; the common Pinskdrev БМ scheme):
  * carcass ЛДСП 16: sides from the floor, a top 22 over them, a bottom on a front plinth rail 60 high;
  * the fronts sit inside a frame of thick front pilasters (58 wide, 22 deep, rounded edges) on the sides' front edges —
    the collection's look;
  * fronts ЛДСП 16 inset 2 mm behind the pilaster face, gaps 3 mm; no hardware: a semicircular finger notch (r 30) cut
    into the top edge of each drawer front / lower door (the catalogue close-up p. 95);
  * wardrobes: the plain columns have an upper and a lower door meeting at 1/2.3 of the height (the notch at the joint,
    by the free edge), the middle columns full-height mirror doors (1 in 3Д, 2 in 4Д, 3 in 5Д); white interior;
  * beds: square block posts 80 × 80, a headboard panel with the same notch in its top edge, side rails 22 × 220 on the
    posts, a metal base with slats (the catalogue beds come «с металлокаркасом» in the family); the 1-09 day bed БМ2.748.1.40
    has shaped ends, a back board and two drawers under the front rail.
Coordinates: x from the left, y up from the floor, z from the wall to the front; mm.

    /private/tmp/claude-501/venv/bin/python tools/casegoods/gen/irving.py
"""
import json
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "irving"
FIN = "irving-sosna-jackson"
PW, PD = 58.0, 22.0          # front pilaster width / depth
TT = 22.0                    # top thickness
PL = 60.0                    # plinth rail height


class D:
    def __init__(self, did, size):
        self.did, self.size, self.parts, self.moves = did, size, [], []

    def add(self, pid, box, kind=None, mat=None, **kw):
        p = {"id": pid}
        if kind:
            p["kind"] = kind
        if mat:
            p["mat"] = mat
        p.update(kw)
        p["box"] = [round(v, 2) for v in box]
        self.parts.append(p)
        return pid

    def write(self):
        return dump(self.did, self.size, self.parts, self.moves)


def notch_outline(x0, y0, x1, y1, cx, r=30.0, top=True):
    """A front's outline in the front plane with a semicircular finger notch in its top (or bottom) edge at cx."""
    if top:
        k = 1.33 * r
        return (f"M {x0} {y0} L {x1} {y0} L {x1} {y1} L {cx + r} {y1} "
                f"C {cx + r} {y1 - k} {cx - r} {y1 - k} {cx - r} {y1} L {x0} {y1} Z")
    k = 1.33 * r
    return (f"M {x0} {y0} L {cx - r} {y0} C {cx - r} {y0 + k} {cx + r} {y0 + k} {cx + r} {y0} "
            f"L {x1} {y0} L {x1} {y1} L {x0} {y1} Z")


def front(d, pid, x0, y0, x1, y1, z1, notch=None, grain="y", kind="front"):
    kw = {"grain": grain}
    if notch is not None:
        kw.update(shape="path", outline=notch_outline(x0, y0, x1, y1, notch))
    return d.add(pid, [x0, y0, z1 - 16, x1, y1, z1], kind=kind, **kw)


def carcass(d, W, H, B, bottom=True, plinth=True, back=True, inner="body"):
    """Sides, top, front pilasters, bottom on the plinth rail, back ДВП in grooves."""
    zf = B - PD
    d.add("side-l", [0, 0, 0, 16, H - TT, zf])
    d.add("side-r", [W - 16, 0, 0, W, H - TT, zf])
    d.add("pilaster-l", [0, 0, zf, PW, H - TT, B], edge=6, grain="y")
    d.add("pilaster-r", [W - PW, 0, zf, W, H - TT, B], edge=6, grain="y")
    d.add("top", [0, H - TT, 0, W, H, B], edge=3, grain="x")
    if plinth:
        d.add("plinth", [PW, 0, B - 18, W - PW, PL, B - 2], grain="x")
        d.add("plinth-back", [16, 0, 20, W - 16, PL, 36])
    if bottom:
        d.add("bottom", [16, PL, 0, W - 16, PL + 16, zf], mat=None if inner == "body" else inner)
    if back:
        d.add("back", [8, PL + 8, 6, W - 8, H - TT + 6, 9.5], kind="back", mat=None if inner == "body" else inner)


def drawer(d, tag, fbox, cx0, cx1, y0, h, z1, depth=400, notch=True):
    x0, fy0, x1, fy1 = fbox
    ids = [front(d, f"front-{tag}", x0, fy0, x1, fy1, z1, notch=(x0 + x1) / 2 if notch else None, grain="x")]
    zb = z1 - 20
    xb0, xb1 = cx0 + 13, cx1 - 13
    z0 = zb - depth
    ids.append(d.add(f"bs-l-{tag}", [xb0, y0, z0, xb0 + 16, y0 + h, zb]))
    ids.append(d.add(f"bs-r-{tag}", [xb1 - 16, y0, z0, xb1, y0 + h, zb]))
    ids.append(d.add(f"bb-{tag}", [xb0 + 16, y0 + 14, z0, xb1 - 16, y0 + h, z0 + 16]))
    ids.append(d.add(f"bot-{tag}", [xb0 + 11, y0 + 10, z0, xb1 - 11, y0 + 13, zb + 5], kind="back"))
    d.moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": ids, "travel": int(depth * 0.8)})
    return ids


# ------------------------------------------------------------------------------------------------ case pieces
def bedside():
    """Тумба прикроватная 610 × 386 × 450: a drawer on top, an open niche under it."""
    W, B, H = 610, 386, 450
    d = D("irving-1-30", [W, B, H])
    carcass(d, W, H, B)
    z1 = B - 2
    d.add("shelf", [16, 234, 20, W - 16, 250, B - PD])
    drawer(d, "1", [PW + 3, 252, W - PW - 3, H - TT - 3], 16, W - 16, 262, 140, z1, depth=320)
    return d


def chest():
    """Комод 1066 × 458 × 916: three equal drawers between the pilasters."""
    W, B, H = 1066, 458, 916
    d = D("irving-1-31", [W, B, H])
    carcass(d, W, H, B)
    z1 = B - 2
    y = PL + 2
    fh = (H - TT - 3 - y - 2 * 3) / 3
    for i in range(3):
        f0 = y + i * (fh + 3)
        if i:
            d.add(f"rail-{i}", [16, f0 - 12, 20, W - 16, f0 + 4 - 12, 120])
        drawer(d, str(i + 1), [PW + 3, f0, W - PW - 3, f0 + fh], 16, W - 16, f0 + 22, 170, z1, depth=380)
    return d


def wardrobe(did, W, cols):
    """Шкаф для одежды W × 586 × 2176: cols = list of 'split' (upper + lower door) / 'mirror' (full-height mirror door)."""
    B, H = 586, 2176
    d = D(did, [W, B, H])
    carcass(d, W, H, B, inner="white")
    z1 = B - 2
    n = len(cols)
    x0f, x1f = PW + 3, W - PW - 3
    cw = (x1f - x0f - (n - 1) * 3) / n
    yb, yt = PL + 2, H - TT - 3
    yj = 950.0                     # the joint of the split doors
    # partitions behind the joints between a split column and its neighbour (the mirror columns share a hanging space)
    xs = [x0f + i * (cw + 3) for i in range(n)]
    parts_x = []
    for i in range(1, n):
        if cols[i - 1] != cols[i]:
            parts_x.append(xs[i] - 1.5)
    for k, x in enumerate(parts_x):
        d.add(f"partition-{k + 1}", [x - 8, PL + 16, 20, x + 8, H - TT, B - PD - 16], mat="white")
    walls = [16] + [x for x in parts_x] + [W - 16]
    for k in range(len(walls) - 1):
        a = walls[k] + (8 if k else 0)
        b = walls[k + 1] - (8 if k + 1 < len(walls) - 1 else 0)
        # which kind of section: the column type of the fronts in front of it
        cx = (a + b) / 2
        ci = min(range(n), key=lambda i: abs(xs[i] + cw / 2 - cx))
        if cols[ci] == "split":
            for j, y in enumerate((430, 810, 1190, 1570, 1880)):
                d.add(f"shelf-{k + 1}-{j + 1}", [a + 1, y, 20, b - 1, y + 16, B - PD - 40], mat="white")
        else:
            d.add(f"hat-{k + 1}", [a, 1860, 20, b, 1876, B - PD - 40], mat="white")
            d.add(f"rail-{k + 1}", [a + 3, 1770, 262, b - 3, 1795, 287], kind="tube", mat="chrome", covers=["штанга"])
    for i, kind in enumerate(cols):
        x0, x1 = xs[i], xs[i] + cw
        hinge = "left" if (i < n / 2) else "right"
        free = x1 - 45 if hinge == "left" else x0 + 45
        if kind == "split":
            lo = front(d, f"door-{i + 1}b", x0, yb, x1, yj, z1, notch=free)
            up = front(d, f"door-{i + 1}t", x0, yj + 3, x1, yt, z1)
            d.moves.append({"type": "door", "name": f"door_{i + 1}_lower", "parts": [lo], "hinge": hinge, "angle": 105})
            d.moves.append({"type": "door", "name": f"door_{i + 1}_upper", "parts": [up], "hinge": hinge, "angle": 105})
        else:
            dr = d.add(f"door-{i + 1}", [x0, yb, z1 - 16, x1, yt, z1 - 4], kind="front", grain="y")
            m = d.add(f"mirror-{i + 1}", [x0 + 4, yb + 4, z1 - 4, x1 - 4, yt - 4, z1], kind="mirror")
            d.moves.append({"type": "door", "name": f"door_{i + 1}", "parts": [dr, m], "hinge": hinge, "angle": 105})
    return d


def desk():
    """Стол письменный 1200 × 600 × 780: two end panels, a modesty panel, a drawer box of two drawers under the top."""
    W, B, H = 1200, 600, 780
    d = D("irving-2-46", [W, B, H])
    d.add("top", [0, H - TT, 0, W, H, B], edge=3, grain="x")
    d.add("leg-l", [20, 0, 20, 42, H - TT, B - 20], grain="y")
    d.add("leg-r", [W - 42, 0, 20, W - 20, H - TT, B - 20], grain="y")
    d.add("modesty", [42, 300, 40, W - 42, H - TT, 56], grain="x")
    d.add("drawer-floor", [42, 600, 56, W - 42, 616, B - 38])
    d.add("drawer-div", [592, 616, 56, 608, H - TT, B - 38])
    z1 = B - 22
    for tag, a, b in (("l", 42, 592), ("r", 608, W - 42)):
        drawer(d, tag, [a + 3, 619, b - 3, H - TT - 3], a, b, 628, 110, z1, depth=480)
    return d


def mirror():
    """Зеркало 1060 × 5 × 600 (catalogue depth 5): a mirror on a thin pine-decor backing whose rim frames it."""
    d = D("irving-1-62", [1060, 5, 600])
    d.add("backing", [0, 0, 0, 1060, 600, 1], kind="back", grain="x")
    d.add("mirror", [40, 40, 1, 1020, 560, 5], kind="mirror")
    return d


# ------------------------------------------------------------------------------------------------ beds
def bed(did, W, L=2141, H=960):
    """Кровать W × 2141 × 960: block posts 80 × 80, headboard with a finger notch, rails and foot on the posts, metal
    base with slats, mattress."""
    d = D(did, [W, L, H])
    P = 80
    for tag, x0 in (("l", 0), ("r", W - P)):
        d.add(f"post-h{tag}", [x0, 0, 0, x0 + P, H, P], grain="y")
        d.add(f"post-f{tag}", [x0, 0, L - P, x0 + P, 420, L], grain="y")
    d.add("head", [P, 360, 29, W - P, H - 20, 51], grain="x", shape="path",
          outline=notch_outline(P, 360, W - P, H - 20, W / 2, r=60))
    d.add("head-rail", [P, 180, 29, W - P, 360, 51], grain="x")
    d.add("foot", [P, 180, L - 51, W - P, 400, L - 29], grain="x")
    for tag, x0 in (("l", 20), ("r", W - 42)):
        d.add(f"rail-{tag}", [x0, 180, P, x0 + 22, 400, L - P], grain="z")
    fx0, fx1, fz0, fz1 = 42, W - 42, P + 2, L - P - 2
    d.add("base-rail-l", [fx0, 230, fz0, fx0 + 30, 260, fz1], mat="black", covers=["основание"])
    d.add("base-rail-r", [fx1 - 30, 230, fz0, fx1, 260, fz1], mat="black")
    fields = [(fx0 + 30, fx1 - 30)]
    if W > 1200:
        xm = W / 2
        d.add("base-beam", [xm - 15, 230, fz0, xm + 15, 260, fz1], mat="black")
        d.add("base-leg", [xm - 12, 0, L / 2 - 12, xm + 12, 230, L / 2 + 12], kind="tube", mat="black")
        fields = [(fx0 + 30, xm - 15), (xm + 15, fx1 - 30)]
    for f, (a, b) in enumerate(fields):
        for i in range(22):
            z = fz0 + 40 + i * (fz1 - fz0 - 133) / 21
            d.add(f"slat-{f + 1}-{i + 1}", [a, 252, z, b, 260, z + 53], mat="door_enamel_whitey#c9a877")
    d.add("mattress", [fx0, 260, fz0, fx1, 460, fz1], kind="mattress")
    return d


def day_bed(did, W, B, H, drawers=2, handles=False, back_h=None, fin_metal=False):
    """Кровать 1-09 with storage (Ирвинг 1.40, Боро 1.40): two shaped ends, a back board along the wall, a front rail with
    drawers under it (Боро: 3 drawers with bar handles, a solid ЛДСП base), mattress 2000 × 900."""
    d = D(did, [W, B, H])
    T = 22
    k = 1.33 * 120
    # the ends: full height at the back, rounded down to the rail height at the front
    yr = 390.0
    for tag, x0 in (("l", 0), ("r", W - T)):
        out = (f"M 0 0 L {B} 0 L {B} {yr} C {B} {yr + 60} {B - 60} {yr + 90} {B - 150} {yr + 100} "
               f"L 160 {H - 60} C 110 {H - 20} 60 {H} 0 {H} Z")
        d.add(f"end-{tag}", [x0, 0, 0, x0 + T, H, B], grain="y", shape="path", outline=out)
    bh = back_h or (H - 30)
    d.add("back", [T, 60, 0, W - T, bh, 22], grain="x")
    d.add("rail-front", [T, 290, B - 22, W - T, yr, B], grain="x")
    d.add("base", [T, 274, 22, W - T, 290, B - 22], grain="x")
    d.add("plinth", [T, 0, 60, W - T, 40, 76])
    d.add("bottom", [T, 40, 22, W - T, 56, B - 40])
    n = drawers
    x0f, x1f = T + 3, W - T - 3
    fw = (x1f - x0f - (n - 1) * 3) / n
    for i in range(n):
        a = x0f + i * (fw + 3)
        b = a + fw
        if i:
            d.add(f"divider-{i}", [a - 9.5, 56, 22, a + 6.5, 274, B - 40])
        ids = [front(d, f"front-{i + 1}", a, 58, b, 286, B, notch=None if handles else (a + b) / 2, grain="x")]
        xb0, xb1 = a + 20, b - 20
        z0, zb = 60, B - 16
        ids.append(d.add(f"bs-l-{i + 1}", [xb0, 66, z0, xb0 + 16, 226, zb]))
        ids.append(d.add(f"bs-r-{i + 1}", [xb1 - 16, 66, z0, xb1, 226, zb]))
        ids.append(d.add(f"bb-{i + 1}", [xb0 + 16, 80, z0, xb1 - 16, 226, z0 + 16]))
        ids.append(d.add(f"bot-{i + 1}", [xb0 + 11, 70, z0, xb1 - 11, 73, zb + 5], kind="back"))
        if handles:
            ids.append(d.add(f"handle-{i + 1}", [0, 0, 0, 0, 0, 0], kind="handle", model="bar", mat="metal",
                             at=[(a + b) / 2, 200], dir="right", d=160, band=10, t=6, standoff=24, z=B, covers=["ручка"]))
            d.parts[-1].pop("box")
        d.moves.append({"type": "drawer", "name": f"drawer_{i + 1}", "parts": ids, "travel": 400})
    d.add("mattress", [T, 290, 22, W - T, 490, B - 22], kind="mattress")
    return d


# ------------------------------------------------------------------------------------------------ main
MODELS = [
    ("1-82", "Кровать 2-16 «Ирвинг»", "bedroom", lambda: bed("irving-1-82", 1684), "спальное место 2000×1600"),
    ("1-84", "Кровать 2-14 «Ирвинг»", "bedroom", lambda: bed("irving-1-84", 1484), "спальное место 2000×1400"),
    ("1-83", "Кровать 2-18 «Ирвинг»", "bedroom", lambda: bed("irving-1-83", 1884), "спальное место 2000×1800"),
    ("1-85", "Кровать 1-09 «Ирвинг»", "bedroom", lambda: bed("irving-1-85", 984), "спальное место 2000×900"),
    ("1-40", "Кровать 1-09 «Ирвинг»", "bedroom", lambda: day_bed("irving-1-40", 2041, 942, 634), "с ящиками, спальное место 2000×900"),
    ("1-30", "Тумба прикроватная «Ирвинг»", "bedroom", bedside, None),
    ("1-31", "Комод «Ирвинг»", "bedroom", chest, None),
    ("1-02", "Шкаф для одежды 2Д «Ирвинг»", "bedroom", lambda: wardrobe("irving-1-02", 1029, ["split", "split"]), None),
    ("1-03-01", "Шкаф для одежды 3Д «Ирвинг»", "bedroom",
     lambda: wardrobe("irving-1-03-01", 1463, ["split", "mirror", "split"]), "с зеркалом"),
    ("1-27-01", "Шкаф для одежды 4Д «Ирвинг»", "bedroom",
     lambda: wardrobe("irving-1-27-01", 1896, ["split", "mirror", "mirror", "split"]), "с зеркалами"),
    ("1-01-01", "Шкаф для одежды 5Д «Ирвинг»", "bedroom",
     lambda: wardrobe("irving-1-01-01", 2331, ["split", "mirror", "mirror", "mirror", "split"]), "с зеркалами"),
    ("2-46", "Стол письменный «Ирвинг»", "office", desk, None),
    ("1-62", "Зеркало «Ирвинг»", "decor", mirror, "навесное; not in index.json: listed on p. 96"),
]


def main():
    models = []
    for tail, name, cat, fn, note in MODELS:
        d = fn()
        d.write()
        parts = tail.split("-")
        code = f"БМ2.748.{parts[0]}.{parts[1]}" + (f"-{parts[2]}" if len(parts) > 2 else "")
        m = {"id": d.did, "code": code, "name": name, "collection": SLUG, "category": cat, "size": d.size,
             "page": 96, "note": "по каталогу и фото, без инструкции" + (f"; {note}" if note else "")}
        if tail == "1-62":
            m["mount"] = "wall"
        models.append(m)
        print(d.did)
    frag = {"finishes": [{"id": FIN, "name": "Сосна Джексон", "body": "door_enamel_whitey#6e6a60", "swatch": "#6e6a60"}],
            "profiles": {},
            "collections": [{"id": SLUG, "name": "Ирвинг", "brand": "Пинскдрев", "finishes": [FIN], "metal": "chrome",
                             "note": "Каталог «Корпусная мебель ч. II» 2025, с. 94–96 (разворот 184–189). Инструкций нет — всё по "
                                     "каталогу и фото сайта. ЛДСП «Сосна Джексон»: крышка 22, фасады вкладные в рамке из "
                                     "фронтальных пилястр 58 со скруглёнными кромками, ручки — полукруглые выборки в кромке фасада; "
                                     "шкафы с разъёмными дверями и зеркальными дверями по центру, белая внутренняя отделка."}],
            "models": models}
    with open(os.path.join(HERE, f"{SLUG}_catalog.json"), "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
