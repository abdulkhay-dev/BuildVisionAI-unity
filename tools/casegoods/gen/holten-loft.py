"""«Хольтен Лофт» (Пинскдрев, П3.0579): hall set — 5 designs, all by instruction.

    /private/tmp/claude-501/venv/bin/python tools/casegoods/gen/holten-loft.py

Instructions (no text layer; tables read off the pictures into gen/cutlists/holten-loft-3-xx.json):
IS-Holten-zerkalo-50-1 (from index.json) and IS-Holten-tumba-10-1, -shkaf-01-1, -veshalka-40-1, -tumba-60-1 (found on
a.pinskdrev.ru by the same file-name pattern; not in index.json).

Construction:
  * carcass ЛДСП 22 «Дуб Стирлинг»: top and bottom 963 (802) × 374 over the full size; the sides 373 deep between them
    (every panel between the sides is L − 44).
  * plinth ЛДСП 22 × 40: a frame 40 in from the ends (41 on the wardrobe) and from the front, flush at the back
    (front and back boards L − 80, ends 290 between them), under the bottom.
  * inner panels ЛДСП 16 «Антрацит» (partitions, horizontal walls, shelves), 322 / 332 deep from the back.
  * backs ХДФ 3 «графит текстурный» in grooves, split behind a partition.
  * fronts МДФ 16 inset flush with the carcass; the wardrobe's oak door МДФ 18, its mirror door a 16 mm anthracite board
    with the mirror (1904 × 424) on it. Flaps of 3.10 fold down on bar stays.
  * handles: black tab pulls hooked over the front's edge (top edge of flaps and drawers, side edge of doors) — the
    engine's `edge` handle, turned for side edges.
  * soft elements 40 mm (seat 3.60, back 3.40).
"""
import json
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "holten-loft"
T = 22
BZ0, BZ1 = 6, 9      # backs ХДФ 3 in grooves
IZ0 = 9              # inner panels start in front of the back


def R(v):
    return round(v, 1)


class D:
    def __init__(self, did, size):
        self.id, self.size, self.parts, self.moves = did, size, [], []

    def add(self, n=None, box=None, pid=None, kind=None, **kw):
        p = {}
        if n is not None:
            p["n"] = n
        if pid is not None:
            p["id"] = pid
        if kind is not None and kind != "panel":
            p["kind"] = kind
        p.update(kw)
        if box is not None:
            p["box"] = [R(v) for v in box]
        self.parts.append(p)
        return p.get("id") or p.get("n")

    def write(self):
        return dump(self.id, self.size, self.parts, self.moves)


def carcass(d, W, B, H, plinth=40, pin=40, n=("1", "2", "3", "4", "5", "6"), side_h=None):
    """n = (top, bottom, side l, side r, plinth long, plinth end)."""
    top, bot, s1, s2, pl, pe = n
    y0 = plinth
    ytop = H if side_h is None else y0 + T + side_h + T
    d.add(pl, [pin, 0, 0, W - pin, plinth, T], pid=f"{pl}-back", grain="x")
    d.add(pl, [pin, 0, 334 - T, W - pin, plinth, 334], pid=f"{pl}-front", grain="x")
    d.add(pe, [pin, 0, T, pin + T, plinth, 334 - T], pid=f"{pe}-l", grain="z")
    d.add(pe, [W - pin - T, 0, T, W - pin, plinth, 334 - T], pid=f"{pe}-r", grain="z")
    d.add(bot, [0, y0, 0, W, y0 + T, B], grain="x")
    d.add(s1, [0, y0 + T, 0, T, ytop - T, B - 1], grain="y")
    d.add(s2, [W - T, y0 + T, 0, W, ytop - T, B - 1], grain="y")
    d.add(top, [0, ytop - T, 0, W, ytop, B], grain="x")
    return T, W - T, y0 + T, ytop - T, B - 1


def tab(d, pid, edge, x, y, z, t_front=16, length=32, band=55):
    """Black tab pull over a front's edge: edge = top / left / right; (x, y) = the point on that edge."""
    p = {"id": pid, "kind": "handle", "model": "edge", "at": [R(x), R(y)], "d": length, "band": band, "t": 2.5,
         "standoff": t_front + 2.5, "z": R(z)}
    if edge == "left":
        p["rot"] = {"axis": "z", "deg": 90, "about": [R(x), R(y), R(z)]}
    elif edge == "right":
        p["rot"] = {"axis": "z", "deg": -90, "about": [R(x), R(y), R(z)]}
    d.parts.append(p)
    return pid


def front(d, n, box, pid=None, **kw):
    return d.add(n, box, pid=pid, kind="front", **kw)


# ------------------------------------------------------------------------------------------------------------ modules
def m3_10():
    """Тумба 963 × 374 × 1088: four fronts in a pinwheel round an open square niche."""
    W, B, H = 963, 374, 1088
    d = D(f"{SLUG}-3-10", [W, B, H])
    x0, x1, yb, yt, zf = carcass(d, W, B, H)
    z1 = IZ0 + 322
    d.add("9", [340, yb, IZ0, 356, yb + 630, z1], mat="inner")
    d.add("7", [x0, yb + 630, IZ0, x0 + 585, yb + 646, z1], mat="inner")
    d.add("10", [607, yt - 630, IZ0, 623, yt, z1], mat="inner")
    d.add("8", [x1 - 585, yt - 646, IZ0, x1, yt - 630, z1], mat="inner")
    d.add("11", [19, yb - 5, BZ0, 347, yt + 5, BZ1], kind="back")
    d.add("12", [347, yb - 5, BZ0, 944, yt + 5, BZ1], kind="back")
    for i, (a, y) in enumerate(((x0 + 2.5, 272), (x0 + 2.5, 482), (623 + 2.5, 646), (623 + 2.5, 856))):
        d.add("13", [a, y, IZ0, a + 313, y + 16, z1], pid=f"13-{i + 1}", mat="inner")
    d.add("18", [x0 + 1, 880, IZ0, x0 + 584, 896, IZ0 + 293], pid="18-1", mat="inner")
    d.add("18", [x1 - 584, 235, IZ0, x1 - 1, 251, IZ0 + 293], pid="18-2", mat="inner")
    fz0, fz1 = zf - 16, zf
    tl = front(d, "16", [25.5, 701.5, fz0, 614.5, 1063.5, fz1], grain="x")
    tr = front(d, "14", [618.5, 429.5, fz0, 937.5, 1063.5, fz1], grain="y")
    bl = front(d, "17", [25.5, 64.5, fz0, 344.5, 698.5, fz1], grain="y")
    br = front(d, "15", [348.5, 64.5, fz0, 937.5, 426.5, fz1], grain="x")
    htl = tab(d, "h-16", "top", 315, 1063.5, fz1)
    htr = tab(d, "h-14", "left", 618.5, 730, fz1)
    hbl = tab(d, "h-17", "right", 344.5, 351, fz1)
    hbr = tab(d, "h-15", "top", 647, 426.5, fz1)
    d.moves += [{"type": "flap", "name": "flap_top", "parts": [tl, htl], "hinge": "bottom", "angle": 90},
                {"type": "door", "name": "door_right", "parts": [tr, htr], "hinge": "right", "angle": 105},
                {"type": "door", "name": "door_left", "parts": [bl, hbl], "hinge": "left", "angle": 105},
                {"type": "flap", "name": "flap_bottom", "parts": [br, hbr], "hinge": "bottom", "angle": 90}]
    return d.write()


def m3_01():
    """Шкаф для одежды 2Д 802 × 374 × 2000: a narrow oak door over shelves, a mirror door over the rail."""
    W, B, H = 802, 374, 2000
    d = D(f"{SLUG}-3-01", [W, B, H])
    x0, x1, yb, yt, zf = carcass(d, W, B, H, pin=41)
    z1 = IZ0 + 332
    xp = x0 + 219
    d.add("7", [xp, yb, IZ0, xp + 16, yt, z1], mat="inner")
    d.add("8", [18.5, yb - 5, BZ0, 248.5, yt + 5, BZ1], kind="back")
    d.add("9", [248.5, yb - 5, BZ0, 783.5, yt + 5, BZ1], kind="back")
    for tag, y in (("lo", 280), ("up", 1640)):
        d.add("10", [x0, y, IZ0, xp, y + 16, z1], pid=f"10-{tag}", mat="inner")
    d.add("12", [x1 - 520, 1640, IZ0, x1, 1656, z1], mat="inner")
    d.add("13", [x1 - 520, 280, IZ0, x1, 296, z1], mat="inner")
    for i, y in enumerate((565, 834, 1103, 1372)):
        d.add("11", [x0 + 0.5, y, IZ0, x0 + 218.5, y + 16, IZ0 + 322], pid=f"11-{i + 1}", mat="inner")
    d.add(box=[x1 - 520, 1590, 160, x1, 1615, 185], pid="rail-014", kind="tube", mat="chrome", covers=["014"])
    oak = front(d, "14", [25.3, yb + 2, zf - 18, 345.3, yb + 1910, zf], grain="y")
    base = front(d, "16", [348.7, yb + 2, zf - 20, 776.7, yb + 1910, zf - 4], mat="inner", grain="y")
    mir = d.add("15", [350.7, yb + 4, zf - 4, 774.7, yb + 1908, zf], kind="mirror")
    # the tab sits on the mirror door's left edge (cover drawing); door 14 has a notch cut in its edge to clear it
    h = tab(d, "h-16", "left", 348.7, 1032, zf, t_front=20)
    d.moves += [{"type": "door", "name": "door_left", "parts": [oak], "hinge": "left", "angle": 105},
                {"type": "door", "name": "door_mirror", "parts": [base, mir, h], "hinge": "right", "angle": 105}]
    return d.write()


def m3_60():
    """Тумба 963 × 374 × 502: a seat over a drawer with an open niche above it, and a door."""
    W, B, H = 963, 374, 502
    d = D(f"{SLUG}-3-60", [W, B, H])
    x0, x1, yb, yt, zf = carcass(d, W, B, H, n=("1", "2", "5", "6", "3", "4"), side_h=368)
    z1 = IZ0 + 332
    d.add("8", [608, yb, IZ0, 624, yt, z1], mat="inner")
    d.add("9", [x0, 281, IZ0, 608, 297, z1], mat="inner")
    d.add("10", [626, 246, IZ0, 939, 262, IZ0 + 300], mat="inner")
    d.add("7", [19, yb - 5, BZ0, 944, yt + 5, BZ1], kind="back")
    d.add("11", [0, yt + T, 0, W, H, B], kind="soft")
    fz0, fz1 = zf - 16, zf
    door = front(d, "12", [618.7, 64, fz0, 937.7, 428, fz1], grain="y")
    hd = tab(d, "h-12", "left", 618.7, 255, fz1)
    d.moves.append({"type": "door", "name": "door", "parts": [door, hd], "hinge": "right", "angle": 105})
    ids = [front(d, "13", [25.3, 64, fz0, 615.3, 278, fz1], grain="x")]
    z0 = fz0 - 300
    ids.append(d.add("14", [35, 84, z0, 51, 184, fz0], mat="drawer"))
    ids.append(d.add("15", [579, 84, z0, 595, 184, fz0], mat="drawer"))
    ids.append(d.add("16", [51, 98, z0, 579, 184, z0 + 16], mat="drawer"))
    ids.append(d.add("17", [46, 94.8, z0, 584, 97.8, fz0 + 5], kind="back", mat="drawer"))
    ids.append(tab(d, "h-13", "top", 320, 278, fz1))
    d.moves.append({"type": "drawer", "name": "drawer", "parts": ids, "travel": 260})
    return d.write()


def m3_40():
    """Вешалка 963 × 296 × 1298: a wall board with a shelf tray, two hanger arms, three hooks and a soft back pad."""
    W, B, H = 963, 296, 1298
    d = D(f"{SLUG}-3-40", [W, B, H])
    d.add("1", [0, 0, 0, W, H, T], grain="y")
    d.add("2", [3, 1095, T, 3 + T, 1159, T + 252], grain="z")
    d.add("3", [W - 3 - T, 1095, T, W - 3, 1159, T + 252], grain="z")
    d.add("4", [0, 1095, T + 252, W, 1159, B], grain="x")
    d.add("5", [3 + T, 1137, T, W - 3 - T, 1159, T + 252], grain="x")
    d.add("6", [0, 0, T, W, 250, T + 40], kind="soft")
    for i, x in enumerate((190, 771)):
        d.parts.append({"id": f"hanger-{i + 1}-a", "kind": "rod", "mat": "metal", "section": "square", "from": [x, 1095, 60],
                        "to": [x, 1020, 60], "d": 10})
        d.parts.append({"id": f"hanger-{i + 1}-b", "kind": "rod", "mat": "metal", "section": "square", "from": [x, 1020, 60],
                        "to": [x, 1020, 230], "d": 10})
        d.parts.append({"id": f"hanger-{i + 1}-c", "kind": "rod", "mat": "metal", "section": "square", "from": [x, 1020, 230],
                        "to": [x, 1045, 240], "d": 10})
    for i, x in enumerate((196, 482, 767)):
        d.parts.append({"id": f"hook-{i + 1}-a", "kind": "rod", "mat": "metal", "from": [x, 880, T], "to": [x, 880, T + 50], "d": 9})
        d.parts.append({"id": f"hook-{i + 1}-b", "kind": "rod", "mat": "metal", "from": [x, 880, T + 50], "to": [x, 905, T + 58], "d": 9})
    return d.write()


def m3_50():
    """Зеркало 963 × 22 × 800: an anthracite board with the mirror, between two oak strips 64."""
    W, B, H = 963, 22, 800
    d = D(f"{SLUG}-3-50", [W, B, H])
    d.add("1", [0, 64, 0, W, H - 64, 16], mat="inner", grain="x")
    d.add("2", [0, H - 64, 0, W, H, T], grain="x")
    d.add("3", [0, 0, 0, W, 64, T], grain="x")
    d.add(None, [3, 67, 16, W - 3, H - 67, 20], pid="mirror", kind="mirror")
    return d.write()


# ------------------------------------------------------------------------------------------------------------ cut lists
S22, A16, M16 = "ЛДСП 22мм ДУБ СТИРЛИНГ", "ЛДСП 16мм АНТРАЦИТ", "МДФ 16мм ДУБ СТИРЛИНГ"
HDF = "ХДФ 3мм графит текстурный"
CUTLISTS = {
    "3-10": ("П3.0579.3.10", "IS-Holten-tumba-10-1.pdf", "79.3.10", [
        ("1", "Крышка", S22, 963, 374, 22, 1), ("2", "Дно", S22, 963, 374, 22, 1),
        ("3", "Стенка вертикальная", S22, 1004, 373, 22, 1), ("4", "Стенка вертикальная", S22, 1004, 373, 22, 1),
        ("5", "Цоколь", S22, 883, 40, 22, 2), ("6", "Цоколь", S22, 290, 40, 22, 2),
        ("7", "Стенка горизонтальная", A16, 585, 322, 16, 1), ("8", "Стенка горизонтальная", A16, 585, 322, 16, 1),
        ("9", "Перегородка", A16, 630, 322, 16, 1), ("10", "Перегородка", A16, 630, 322, 16, 1),
        ("11", "Стенка задняя", HDF, 1014, 328, 3, 1), ("12", "Стенка задняя", HDF, 1014, 597, 3, 1),
        ("13", "Полка", A16, 313, 322, 16, 4), ("14", "Дверь правая", M16, 634, 319, 16, 1),
        ("15", "Дверь правая (откидная)", M16, 362, 589, 16, 1), ("16", "Дверь левая (откидная)", M16, 362, 589, 16, 1),
        ("17", "Дверь левая", M16, 634, 319, 16, 1), ("18", "Полка", A16, 583, 293, 16, 2)]),
    "3-01": ("П3.0579.3.01", "IS-Holten-shkaf-01-1.pdf", "79.3.01.0", [
        ("1", "Крышка", S22, 802, 374, 22, 1), ("2", "Дно", S22, 802, 374, 22, 1),
        ("3", "Стенка вертикальная", S22, 1916, 373, 22, 1), ("4", "Стенка вертикальная", S22, 1916, 373, 22, 1),
        ("5", "Цоколь", S22, 720, 40, 22, 2), ("6", "Цоколь", S22, 290, 40, 22, 2),
        ("7", "Перегородка", A16, 1916, 332, 16, 1), ("8", "Стенка задняя", HDF, 1926, 230, 3, 1),
        ("9", "Стенка задняя", HDF, 1926, 535, 3, 1), ("10", "Стенка горизонтальная", A16, 219, 332, 16, 2),
        ("11", "Полка", A16, 218, 322, 16, 4), ("12", "Стенка горизонтальная", A16, 520, 332, 16, 1),
        ("13", "Стенка горизонтальная", A16, 520, 332, 16, 1), ("14", "Дверь", "МДФ 18мм ДУБ СТИРЛИНГ", 1908, 320, 18, 1),
        ("15", "Накладка", "Зеркало", 1904, 424, None, 1), ("16", "Дверь(основа)", A16, 1908, 428, 16, 1)]),
    "3-40": ("П3.0579.3.40", "IS-Holten-veshalka-40-1.pdf", "79.3.40", [
        ("1", "Стенка вертикальная", S22, 1298, 963, 22, 1), ("2", "Стенка боковая", S22, 252, 64, 22, 1),
        ("3", "Стенка боковая", S22, 252, 64, 22, 1), ("4", "Стенка передняя", S22, 963, 64, 22, 1),
        ("5", "Стенка горизонтальная", S22, 913, 252, 22, 1), ("6", "Мягкий элемент \"спинка\"", "Мягкий элемент 40мм", 963, 250, 40, 1)]),
    "3-50": ("П3.0579.3.50", "IS-Holten-zerkalo-50-1.pdf", "79.50", [
        ("1", "Стенка вертикальная", "ЛДСП 16мм АНТРАЦИТ", 672, 963, 16, 1),
        ("2", "Стенка вертикальная", S22, 64, 963, 22, 1), ("3", "Стенка вертикальная", S22, 64, 963, 22, 1)]),
    "3-60": ("П3.0579.3.60", "IS-Holten-tumba-60-1.pdf", "79.3.60", [
        ("1", "Крышка", S22, 963, 374, 22, 1), ("2", "Дно", S22, 963, 374, 22, 1),
        ("3", "Цоколь", S22, 883, 40, 22, 2), ("4", "Цоколь", S22, 290, 40, 22, 2),
        ("5", "Стенка вертикальная", S22, 368, 373, 22, 1), ("6", "Стенка вертикальная", S22, 368, 373, 22, 1),
        ("7", "Стенка задняя", HDF, 378, 925, 3, 1), ("8", "Перегородка", A16, 368, 332, 16, 1),
        ("9", "Стенка горизонтальная", A16, 586, 332, 16, 1), ("10", "Полка", A16, 313, 300, 16, 1),
        ("11", "Мягкий элемент \"сиденье\"", "Мягкий элемент 40мм", 963, 374, None, 1),
        ("12", "Дверь", M16, 364, 319, 16, 1), ("13", "Стенка передняя", M16, 214, 590, 16, 1),
        ("14", "Стенка боковая ящика", "ЛДСП 16мм ДУБ АРТИЗАН", 300, 100, 16, 1),
        ("15", "Стенка боковая ящика", "ЛДСП 16мм ДУБ АРТИЗАН", 300, 100, 16, 1),
        ("16", "Стенка задняя ящика", "ЛДСП 16мм ДУБ АРТИЗАН", 528, 86, 16, 1),
        ("17", "Дно ящика", "ХДФ 3мм ДУБ АРТИЗАН", 538, 305, 3, 1)]),
}


def write_cutlists():
    for tail, (code, pdf, mark, rows) in CUTLISTS.items():
        out = {"code": code, "is": pdf,
               "source": f"page image reference/{SLUG}/pages/{SLUG}-{tail}-p1.png (no text layer): table «Поз., "
                         "Наименование, Маркировка, Материал, Кол-во, Длина × Ширина»; the thickness from the material. "
                         "3.60 row 11 (seat, «40 мм») is compared by two sizes: built 50 thick to reach the catalogue's H502",
               "rows": []}
        for n, name, mat, a, b, t, c in rows:
            out["rows"].append({"n": n, "code": f"{mark}.{int(n):02d}" if mark != "79.3.01.0" else f"79.3.01.{int(n):03d}",
                                "name": f"{name} ({mat})", "size": [a, b] + ([t] if t else []), "count": c})
        with open(os.path.join(HERE, "cutlists", f"{SLUG}-{tail}.json"), "w") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)


def write_catalog():
    models = [
        {"id": f"{SLUG}-3-01", "code": "П3.0579.3.01", "name": "Шкаф для одежды 2Д «Хольтен Лофт»", "collection": SLUG,
         "category": "hall", "size": [802, 374, 2000], "is": "IS-Holten-shkaf-01-1.pdf", "page": 134, "note": "с зеркалом"},
        {"id": f"{SLUG}-3-10", "code": "П3.0579.3.10", "name": "Тумба «Хольтен Лофт»", "collection": SLUG, "category": "hall",
         "size": [963, 374, 1088], "is": "IS-Holten-tumba-10-1.pdf", "page": 134},
        {"id": f"{SLUG}-3-40", "code": "П3.0579.3.40", "name": "Вешалка «Хольтен Лофт»", "collection": SLUG, "category": "hall",
         "size": [963, 296, 1298], "is": "IS-Holten-veshalka-40-1.pdf", "page": 134, "mount": "wall"},
        {"id": f"{SLUG}-3-50", "code": "П3.0579.3.50", "name": "Зеркало «Хольтен Лофт»", "collection": SLUG, "category": "hall",
         "size": [963, 22, 800], "is": "IS-Holten-zerkalo-50-1.pdf", "page": 134, "mount": "wall"},
        {"id": f"{SLUG}-3-60", "code": "П3.0579.3.60", "name": "Тумба «Хольтен Лофт»", "collection": SLUG, "category": "hall",
         "size": [963, 374, 502], "is": "IS-Holten-tumba-60-1.pdf", "page": 134, "note": "с мягким сиденьем"},
    ]
    frag = {
        "finishes": [
            {"id": f"{SLUG}-lancelot-stirling", "name": "Дуб Ланцелот / Дуб Стирлинг",
             "body": "door_enamel_whitey#755a4a", "front": "door_enamel_whitey#997658", "back": "door_enamel_whitey#3a3b3d",
             "roles": {"inner": "door_enamel_whitey#3f4144", "drawer": "door_enamel_whitey#a2825f", "fabric": "velvet#645c4d"},
             "swatch": "#997658"}],
        "profiles": {},
        "collections": [
            {"id": SLUG, "name": "Хольтен Лофт", "brand": "Пинскдрев", "finishes": [f"{SLUG}-lancelot-stirling"], "metal": "black",
             "note": "Каталог «Корпусная мебель ч. II» 2025, PDF с. 134 (каталог 264–265); все 5 модулей по инструкциям "
                     "IS-Holten-*. Корпус ЛДСП 22 «Дуб Стирлинг»: крышка и дно во всю ширину, боковины между ними; цоколь "
                     "22 × 40 с отступом 40 спереди и с торцов; внутренние детали ЛДСП 16 «Антрацит»; задние стенки ХДФ "
                     "«графит»; фасады МДФ 16 вкладные («Дуб Ланцелот» по каталогу); чёрные ручки-язычки на кромке."}],
        "models": models,
    }
    with open(os.path.join(HERE, f"{SLUG}_catalog.json"), "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)


def main():
    write_cutlists()
    write_catalog()
    for f in (m3_01, m3_10, m3_40, m3_50, m3_60):
        print(f())


if __name__ == "__main__":
    main()
