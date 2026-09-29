"""«Призма Нью» (Пинскдрев П3.0592, каталог «Корпусная мебель ч. II», PDF с. 116–118): 19 articles.

Sources: 9 assembly instructions (IS-Prizma-P3-592-*, pictures without a text layer: the tables are transcribed into
gen/cutlists/prizma-nyu-*.json by this script), the p. 118 module cut-outs, the p. 116 / 117 interiors and the
pinskdrev.by product photos. The other 10 articles are built "by photo" with the instructed modules as the model.

Construction (the instructions): carcass ЛДСП 16 «Ночное небо» (the tables write «Металл Бруклин» — «указан условно»),
inner parts (bottoms, partitions, shelves, rails, drawer boxes) ЛДСП 16 white; the sides stand on nail glides (k1, 4 mm)
and run to the top, which lies over them (1 mm deeper than the sides); the bottom sits between the sides on a 56 mm
plinth; the back ХДФ 3 white is nailed onto the rear edges in pieces joined over fixed horizontals / rails (Царга);
fronts ЛДСП 16 «Призма» inset flush between the sides (inner hinges), middle doors of the 4-door wardrobe half-overlay
the partitions; square knobs UZ-40-032 (satin chrome); the sides have a skirting notch at the back bottom corner.
Coupe wardrobes: sides 2272 to the floor, base on two 74 mm plinths, backs in grooves, MITO PLUS tracks top and bottom,
doors = ЛДСП 16 panel between two aluminium handle profiles GTV A-R16ERG.

Coordinates (Docs/casegoods-designs.md): x left→right, y up from the floor, z from the wall (0) to the front.
    /private/tmp/claude-501/venv/bin/python tools/casegoods/gen/prizma-nyu.py
"""
import json
import math
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "prizma-nyu"
T = 16          # ЛДСП
BK = 3          # ХДФ back, nailed on
GL = 4          # nail glide k1
PROFILE = "chrome#c2beb3"   # the coupe doors' aluminium profiles (champagne silver, 1-21 photo)

MODELS = []
BYPHOTO = "по фото, без инструкции"


def r1(v):
    return round(v, 1)


def box(pid, b, n=None, **kw):
    p = {}
    if n is not None:
        p["n"] = n
    if pid is not None and pid != n:
        p["id"] = pid
    p.update(kw)
    p["box"] = [r1(v) for v in b]
    return p


def ids(parts):
    return [p.get("id") or p.get("n") for p in parts]


def model(mid, code, name, category, size, page, note, **kw):
    m = {"id": mid, "code": code, "name": name, "collection": SLUG, "category": category, "size": size}
    m.update(kw)
    m["page"] = page
    if note:
        m["note"] = note
    MODELS.append(m)


def glide(tag, x, z, letter="k1"):
    """Nail glide «опора гвоздь» (k1): a grey disc Ø16 × 4 under a side / plinth."""
    return {"id": f"{letter}-{tag}", "kind": "panel", "shape": "circle", "mat": "door_enamel_whitey#8c8c8c", "edge": 0.5,
            "box": [r1(x - 8), 0, r1(z - 8), r1(x + 8), GL, r1(z + 8)], "covers": [letter]}


def glides(pts, letter="k1"):
    return [glide(i + 1, x, z, letter) for i, (x, z) in enumerate(pts)]


def knob(tag, x, y, zf, letter="c2", rot=None):
    """Square knob UZ-40-032 (satin chrome): a 32 × 32 × 8 cap on two square stems, 18 mm off the face."""
    p = {"id": f"{letter}-{tag}", "kind": "handle", "model": "bar", "at": [r1(x), r1(y)], "dir": "right", "d": 32,
         "band": 32, "t": 8, "standoff": 18, "post": 10, "section": "square", "z": r1(zf), "covers": [letter]}
    if rot:
        p["rot"] = rot
    return p


def side_outline(z0, z1, y0, y1, notch=(20, 60)):
    """A side panel seen from the side (plane z, y): the skirting notch at the back bottom corner (20 deep, 60 high,
    its top rounded r 20) — drawn in every instruction's front view and seen in the photos."""
    nd, nh = notch
    return (f"M {r1(z0 + nd)} {r1(y0)} H {r1(z1)} V {r1(y1)} H {r1(z0)} V {r1(y0 + nh)} "
            f"A {nd} {nd} 0 0 0 {r1(z0 + nd)} {r1(y0 + nh - nd)} Z")


def side(pid, x0, y0, y1, z0, z1, n=None, mat=None, notch=True):
    p = box(pid, [x0, y0, z0, x0 + T, y1, z1], n)
    if mat:
        p["mat"] = mat
    if notch:
        p["shape"] = "path"
        p["outline"] = side_outline(z0, z1, y0, y1)
    return p


def back(pid, x0, y0, x1, y1, n=None, z0=0, t=BK):
    return box(pid, [x0, y0, z0, x1, y1, z0 + t], n, kind="back", mat="white")


def drawer(tag, fr, bx, y0, h, zb, zf, ns=None, back_h=None, bottom=None, knobs=(), fmat=None, rot_knob=None):
    """A drawer: front box `fr` (moves), a white box (sides h high from zb to the front's back face zf, a back between
    the sides standing on the bottom — back_h = h − 19 as the tables give it —, an ХДФ bottom in grooves 10 mm up,
    11 mm wider than the back, 5 mm into the front's groove), knobs at `knobs` [(x, y)]. ns = cut-list numbers
    (front, left, right, back, bottom)."""
    x0, x1 = bx
    ns = ns or (None, None, None, None, None)
    bh = back_h if back_h is not None else h - 19
    f = box(ns[0] and f"{ns[0]}-{tag}" or f"d{tag}-front", fr, ns[0], kind="front")
    if fmat:
        f["mat"] = fmat
    parts = [f,
             box(f"{ns[1] or 'dl'}-{tag}", [x0, y0, zb, x0 + T, y0 + h, zf], ns[1], mat="white"),
             box(f"{ns[2] or 'dr'}-{tag}", [x1 - T, y0, zb, x1, y0 + h, zf], ns[2], mat="white"),
             box(f"{ns[3] or 'db'}-{tag}", [x0 + T, y0 + h - bh, zb, x1 - T, y0 + h, zb + T], ns[3], mat="white")]
    bw = (x1 - x0 - 2 * T) + 11 if bottom is None else bottom[0]
    bd = (zf - zb) + 5 if bottom is None else bottom[1]
    xc = (x0 + x1) / 2
    parts.append(box(f"{ns[4] or 'dbt'}-{tag}", [xc - bw / 2, y0 + 10, zf + 5 - bd, xc + bw / 2, y0 + 13, zf + 5], ns[4],
                     kind="back", mat="white"))
    for i, (kx, ky) in enumerate(knobs):
        parts.append(knob(f"d{tag}-{i + 1}", kx, ky, fr[5], rot=rot_knob))
    return parts, {"type": "drawer", "name": f"drawer_{tag}", "parts": ids(parts), "travel": r1((zf - zb) * 0.75)}


def door(name, parts, hinge, axis=None, angle=105):
    mv = {"type": "door", "name": name, "parts": ids(parts), "hinge": hinge, "angle": angle}
    if axis:
        mv["axis"] = [r1(v) for v in axis]
    return mv


def rail(pid, x0, x1, y, z, letter="d3"):
    """Oval chrome hanger rail 15 × 30 (the tube takes the smaller side)."""
    return {"id": pid, "kind": "tube", "mat": "chrome", "box": [r1(x0), r1(y), r1(z - 15), r1(x1), r1(y + 15), r1(z + 15)],
            "covers": [letter]}


# ================================================================================================ cut lists (transcribed)
def rows(spec):
    out = []
    for n, code, name, a, b, t, c in spec:
        out.append({"n": str(n), "code": code, "name": name, "size": [a, b, t], "count": c})
    return out


P = "ЛДСП 16"
CUTLISTS = {
    "prizma-nyu-0-25": ("П3.0592.0.25", "IS-Prizma-P3-592-0-25---Polka-1.pdf p. 1 (table «Поз., Обозн., Наименование, "
                        "Материал, Кол-во, Длина, Ширина»; no text layer; thickness from the material column)", rows([
        (1, "592.25.01", "Ст. вертикальная (Ночное небо)", 900, 230, 16, 1),
        (2, "592.25.02", "Ст. горизонтальная (Призма 870)", 899, 214, 16, 1),
        (3, "592.25.03", "Ст. вертикальная (Призма 870), четверть круга", 198, 198, 16, 1)])),
    "prizma-nyu-1-02": ("П3.0592.1.02", "IS-Prizma-P3-592-1-02---Krovat-2-16-1.pdf p. 2 (no text layer)", rows([
        (1, "592.02.01", "Спинка головная", 1676, 896, 16, 1),
        (2, "592.02.02", "Спинка ножная", 1643, 321, 16, 1),
        (3, "592.02.03", "Накладка (Призма 870)", 1579, 168, 16, 1),
        (4, "592.02.04", "Царга", 2010, 200, 16, 2)])),
    "prizma-nyu-1-07": ("П3.0592.1.07", "IS-Prizma-P3-592-1-07---Krovat-1-09-1.pdf p. 2 (no text layer)", rows([
        (1, "592.07.01", "Спинка головная", 896, 976, 16, 1),
        (2, "592.07.02", "Спинка ножная", 943, 321, 16, 1),
        (3, "592.07.03", "Накладка (Призма 870)", 879, 168, 16, 1),
        (4, "592.07.04", "Царга", 2010, 200, 16, 2)])),
    "prizma-nyu-1-18": ("П3.0592.1.18", "IS-Prizma-P3-592-1-18---SHkaf-dlya-odejdyi-2D-1.pdf p. 2 (no text layer)", rows([
        (1, "592.18.01", "Крышка", 934, 589, 16, 1),
        (2, "592.18.02", "Основание (белый)", 900, 570, 16, 1),
        (3, "592.18.03", "Ст. вертикальная левая", 2254, 588, 16, 1),
        (4, "592.18.04", "Ст. вертикальная правая", 2254, 588, 16, 1),
        (5, "592.18.05", "Перегородка (белый)", 2182, 570, 16, 1),
        (6, "592.18.06", "Ст. горизонтальная (белый)", 562, 441, 16, 3),
        (7, "592.18.07", "Царга (белый)", 441, 128, 16, 1),
        (8, "592.18.08", "Полка (белый)", 562, 440, 16, 4),
        (9, "592.18.09", "Цоколь", 900, 56, 16, 1),
        (10, "592.18.10", "Дверь (Призма 870)", 2196, 446, 16, 2),
        (11, "592.18.11", "Ст. задняя 1 (ХДФ 3 белый)", 1105, 464, 3, 4)])),
    "prizma-nyu-1-19": ("П3.0592.1.19", "IS-Prizma-P3-592-1-19---SHkaf-dlya-odejdyi-4D-2.pdf p. 2 (no text layer); "
                        "numbers 17–19 do not exist in the table", rows([
        (1, "592.19.01", "Крышка", 1834, 589, 16, 1),
        (2, "592.19.02", "Основание (белый)", 1800, 570, 16, 1),
        (3, "592.19.03", "Ст. вертикальная левая", 2254, 588, 16, 1),
        (4, "592.19.04", "Ст. вертикальная правая", 2254, 588, 16, 1),
        (5, "592.19.05", "Перегородка левая (белый)", 2182, 570, 16, 1),
        (6, "592.19.06", "Перегородка правая (белый)", 2182, 570, 16, 1),
        (7, "592.19.07", "Ст. горизонтальная 1 (белый)", 562, 441, 16, 2),
        (8, "592.19.08", "Ст. горизонтальная 2 (белый)", 570, 883, 16, 2),
        (9, "592.19.09", "Полка (белый)", 562, 440, 16, 8),
        (10, "592.19.10", "Дверь А (Призма 870)", 2196, 446, 16, 2),
        (11, "592.19.11", "Дверь Б (Призма 870)", 1586, 446, 16, 1),
        (12, "592.19.12", "Дверь В (Призма 870)", 1586, 446, 16, 1),
        (13, "592.19.13", "Цоколь", 1800, 56, 16, 2),
        (14, "592.19.14", "Царга (белый)", 883, 128, 16, 1),
        (15, "592.19.15", "Ст. задняя 1 (ХДФ 3 белый)", 1105, 462, 3, 4),
        (16, "592.19.16", "Ст. задняя 2 (ХДФ 3 белый)", 1105, 448, 3, 4),
        (20, "592.19.20", "Ст. ящика передняя (Призма 870)", 200, 896, 16, 3),
        (21, "592.19.21", "Ст. ящика левая (белый)", 450, 148, 16, 3),
        (22, "592.19.22", "Ст. ящика правая (белый)", 450, 148, 16, 3),
        (23, "592.19.23", "Ст. ящика задняя (белый)", 825, 129, 16, 3),
        (24, "592.19.24", "Дно ящика (ХДФ 3 белый)", 836, 455, 3, 3)])),
    "prizma-nyu-1-20": ("П3.0592.1.20", "IS-Prizma-P3-592-1-20---SHkaf-uglovoy-2D-2.pdf p. 2 (no text layer)", rows([
        (1, "592.20.01", "Крышка (пятиугольная)", 1021, 1021, 16, 1),
        (2, "592.20.02", "Основание (пятиугольное)", 1004, 1004, 16, 1),
        (3, "592.20.03", "Ст. вертикальная левая", 2254, 369, 16, 1),
        (4, "592.20.04", "Ст. вертикальная правая", 2254, 369, 16, 1),
        (5, "592.20.05", "Перегородка левая (белый)", 2182, 349, 16, 1),
        (6, "592.20.06", "Перегородка правая (белый)", 2182, 349, 16, 1),
        (7, "592.20.07", "Ст. задняя правая (ЛДСП белый)", 2182, 579, 16, 1),
        (8, "592.20.08", "Царга (белый)", 655, 96, 16, 1),
        (9, "592.20.09", "Ст. горизонтальная 1 (белый)", 315, 348, 16, 2),
        (10, "592.20.10", "Ст. горизонтальная 2 (белый)", 408, 348, 16, 2),
        (11, "592.20.11", "Ст. горизонтальная 3 (белый)", 348, 655, 16, 1),
        (12, "592.20.12", "Полка 1 (белый)", 314, 340, 16, 3),
        (13, "592.20.13", "Полка 2 (белый)", 407, 340, 16, 3),
        (14, "592.20.14", "Дверь (Призма 870)", 2196, 446, 16, 2),
        (15, "592.20.15", "Цоколь", 902, 56, 16, 2),
        (16, "592.20.16", "Ст. задняя 1 (ХДФ 3 белый)", 736, 439, 3, 3),
        (17, "592.20.17", "Ст. задняя 2 (ХДФ 3 белый)", 736, 337, 3, 3),
        (18, "592.20.18", "Ст. задняя 3 (ХДФ 3 белый)", 1105, 337, 3, 4)])),
    "prizma-nyu-1-21": ("П3.0592.1.21", "IS-Prizma-P3-592-1-21---SHkaf-kupe-2D-1.pdf p. 2 (no text layer). Row 22 "
                        "«Брусок 100×50» is left out: the instruction (p. 7) uses it as the damping block for knocking the "
                        "handle profiles m7 onto the door panels — a tool, not a part of the wardrobe", rows([
        (1, "592.21.01", "Ст. вертикальная левая", 2272, 649, 16, 1),
        (2, "592.21.02", "Ст. вертикальная правая", 2272, 649, 16, 1),
        (3, "592.21.03", "Перегородка (белый)", 2182, 536, 16, 1),
        (4, "592.21.04", "Крышка", 1529, 650, 16, 1),
        (5, "592.21.05", "Основание", 1496, 648, 16, 1),
        (6, "592.21.06", "Царга (белый)", 128, 880, 16, 1),
        (7, "592.21.07", "Ст. горизонтальная 1 (белый)", 880, 535, 16, 2),
        (8, "592.21.08", "Ст. горизонтальная 2 (белый)", 599, 535, 16, 3),
        (9, "592.21.09", "Полка (белый)", 598, 526, 16, 2),
        (10, "592.21.10", "Цоколь", 1496, 74, 16, 2),
        (11, "592.21.11", "Ст. задняя 1 (ХДФ 3 белый)", 353, 893, 3, 2),
        (12, "592.21.12", "Ст. задняя 2 (ХДФ 3 белый)", 742, 446, 3, 4),
        (13, "592.21.13", "Ст. задняя 3 (ХДФ 3 белый)", 1096, 613, 3, 2),
        (20, "592.21.20", "Щит двери (Призма)", 2170, 764, 16, 2)])),
    "prizma-nyu-2-09": ("П3.0592.2.09", "IS-Prizma-P3-592-2-09---Stol-pismennyiy-2t-2.pdf p. 2 (no text layer); "
                        "row 6 is empty in the table", rows([
        (1, "592.09.01", "Ст. верт. левая", 740, 560, 16, 1),
        (2, "592.09.02", "Ст. верт. правая", 740, 560, 16, 1),
        (3, "592.09.03", "Перегородка", 740, 543, 16, 1),
        (4, "592.09.04", "Столешница", 2100, 600, 16, 1),
        (5, "592.09.05", "Царга левая", 2026, 506, 16, 1),
        (7, "592.09.07", "Ст. вертикальная 1", 351, 543, 16, 1),
        (8, "592.09.08", "Ст. вертикальная 2", 351, 543, 16, 1),
        (9, "592.09.09", "Ст. горизонтальная", 400, 542, 16, 1),
        (10, "592.09.10", "Ст. горизонтальная", 400, 542, 16, 1),
        (20, "592.08.20", "Ст. ящика передняя (Призма 870)", 163, 396, 16, 4),
        (21, "592.08.21", "Ст. ящика левая (белый)", 500, 136, 16, 4),
        (22, "592.08.22", "Ст. ящика правая (белый)", 500, 136, 16, 4),
        (23, "592.08.23", "Ст. ящика задняя (белый)", 341, 117, 16, 4),
        (24, "592.08.24", "Дно ящика (ХДФ 3 белый)", 352, 505, 3, 4)])),
    "prizma-nyu-2-10": ("П3.0592.2.10", "IS-Prizma-P3-592-2-10---Stol-pismennyiy--2.pdf p. 2 (no text layer)", rows([
        (1, "592.10.01", "Ст. вертикальная лев.", 730, 454, 16, 1),
        (2, "592.10.02", "Ст. вертикальная пр.", 730, 454, 16, 1),
        (3, "592.10.03", "Столешница", 1000, 500, 16, 1),
        (4, "592.10.04", "Царга", 966, 282, 16, 1),
        (5, "592.10.05", "Ст. горизонтальная", 966, 436, 16, 1),
        (6, "592.10.06", "Перегородка", 104, 419, 16, 1),
        (20, "592.10.20", "Ст. ящика передняя (Призма 870)", 487, 100, 16, 1),
        (21, "592.10.21", "Ст. ящика левая (белый)", 350, 96, 16, 1),
        (22, "592.10.22", "Ст. ящика правая (белый)", 350, 96, 16, 1),
        (23, "592.10.23", "Ст. ящика задняя (белый)", 416, 77, 16, 1),
        (24, "592.10.24", "Дно ящика (ХДФ 3 белый)", 427, 355, 3, 1)])),
}


def write_cutlists():
    out = []
    for did, (code, src, rr) in CUTLISTS.items():
        path = os.path.join(HERE, "cutlists", did + ".json")
        with open(path, "w") as fh:
            json.dump({"code": code, "source": src, "rows": rr}, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        out.append(path)
    return out


def isfile(did):
    return {"prizma-nyu-0-25": "IS-Prizma-P3-592-0-25---Polka-1.pdf",
            "prizma-nyu-1-02": "IS-Prizma-P3-592-1-02---Krovat-2-16-1.pdf",
            "prizma-nyu-1-07": "IS-Prizma-P3-592-1-07---Krovat-1-09-1.pdf",
            "prizma-nyu-1-18": "IS-Prizma-P3-592-1-18---SHkaf-dlya-odejdyi-2D-1.pdf",
            "prizma-nyu-1-19": "IS-Prizma-P3-592-1-19---SHkaf-dlya-odejdyi-4D-2.pdf",
            "prizma-nyu-1-20": "IS-Prizma-P3-592-1-20---SHkaf-uglovoy-2D-2.pdf",
            "prizma-nyu-1-21": "IS-Prizma-P3-592-1-21---SHkaf-kupe-2D-1.pdf",
            "prizma-nyu-2-09": "IS-Prizma-P3-592-2-09---Stol-pismennyiy-2t-2.pdf",
            "prizma-nyu-2-10": "IS-Prizma-P3-592-2-10---Stol-pismennyiy--2.pdf"}[did]


# ================================================================================================ swing-door wardrobes
# common heights: glides 4, plinth 4..60, bottom 60..76, sides 4..2258, top 2258..2274; doors 2196 at 61..2257 (1 mm
# gaps), the back 2 × 1105 from 60 to 2270 joined at 1165 over a fixed horizontal / the rail (Царга)
Y_BOT, Y_IN, Y_TOP = 60, 76, 2258
DOOR_Y = (61, 2257)
JOINT = 1165
ZS0, ZS1 = BK, BK + 588          # sides
ZF0, ZF1 = ZS1 - T, ZS1          # inset fronts, flush with the sides
ZIN = BK + 570                   # bottom / partitions / fixed horizontals front edge
KY = 1161                        # knob height on the doors (instruction front views)


def wardrobe_shell(W, ns=("1", "2", "3", "4"), n_plinth="9", plinths=1):
    """Top over the sides, sides to the glides, bottom between the sides on the plinth(s)."""
    p = [box(ns[0], [0, Y_TOP, ZS0, W, Y_TOP + T, ZS0 + 589], ns[0]),
         box(ns[1], [17, Y_BOT, ZS0, W - 17, Y_IN, ZIN], ns[1], mat="white"),
         side(ns[2], 0, GL, Y_TOP, ZS0, ZS1, ns[2]),
         side(ns[3], W - T, GL, Y_TOP, ZS0, ZS1, ns[3])]
    p.append(box(f"{n_plinth}-1", [17, GL, ZF0 - 2, W - 17, Y_BOT, ZF1 - 2], n_plinth))
    if plinths == 2:
        p.append(box(f"{n_plinth}-2", [17, GL, ZS0, W - 17, Y_BOT, ZS0 + T], n_plinth))
    return p


def column_shelves(tag, x0, x1, fixed, loose, n_fixed, n_loose, wf=441, wl=440):
    """A shelf column between x0..x1: fixed horizontals (Rastex, flush at the back, 562 deep) at `fixed` (top faces),
    loose shelves (562 × 440 on pins) at `loose`."""
    xc = (x0 + x1) / 2
    p = []
    for i, yt in enumerate(fixed):
        p.append(box(f"{n_fixed}-{tag}{i + 1}", [xc - wf / 2, yt - T, ZS0, xc + wf / 2, yt, ZS0 + 562], n_fixed, mat="white"))
    for i, yt in enumerate(loose):
        p.append(box(f"{n_loose}-{tag}{i + 1}", [xc - wl / 2, yt - T, ZS0 + 5, xc + wl / 2, yt, ZS0 + 567], n_loose, mat="white"))
    return p


def w118():
    """Шкаф для одежды 2Д П3.592.1.18 — by instruction."""
    W = 934
    p = wardrobe_shell(W)
    p.append(box("5", [459, Y_IN, ZS0, 475, Y_TOP, ZIN], "5", mat="white"))
    # left column (17..459): shelves 8 at 468 / 832 / 1531 / 1880, the fixed horizontal 6 on the back joint;
    # right column (475..917): a fixed horizontal 6 low (shoes) and one as the hat shelf, the rail under it, Царга 7
    # behind the back joint (photo 1-18_1 and the exploded view p. 1)
    p += column_shelves("l", 17, 459, [JOINT + 8], [468, 832, 1531, 1880], "6", "8")
    p += column_shelves("r", 475, 917, [588, 1931], [], "6", "8")
    p.append(box("7", [475.5, JOINT - 64, ZS0, 916.5, JOINT + 64, ZS0 + T], "7", mat="white"))
    p.append(rail("d3", 478.5, 913.5, 1850, 296))
    for i, (x0, y0) in enumerate([(3, Y_BOT), (467, Y_BOT), (3, JOINT), (467, JOINT)]):
        p.append(back(f"11-{i + 1}", x0, y0, x0 + 464, y0 + 1105, "11"))
    d1 = [box("10-1", [19.5, DOOR_Y[0], ZF0, 465.5, DOOR_Y[1], ZF1], "10", kind="front", grain="y"),
          knob("1", 435.5, KY, ZF1)]
    d2 = [box("10-2", [468.5, DOOR_Y[0], ZF0, 914.5, DOOR_Y[1], ZF1], "10", kind="front", grain="y"),
          knob("2", 498.5, KY, ZF1)]
    p += d1 + d2
    p += glides([(8, 60), (8, 540), (W - 8, 60), (W - 8, 540), (150, ZF0 + 6), (W - 150, ZF0 + 6)])
    moves = [door("door_left", d1, "left", [19.5, ZF1]), door("door_right", d2, "right", [914.5, ZF1])]
    did = "prizma-nyu-1-18"
    model(did, "П3.0592.1.18", "Шкаф для одежды 2д «Призма Нью»", "bedroom", [934, 592, 2274], 118,
          "по инструкции; двери вкладные на внутренних петлях, внутри ЛДСП белый", **{"is": isfile(did)})
    return dump(did, [934, 592, 2274], p, moves)


def w119():
    """Шкаф для одежды 4Д П3.592.1.19 — by instruction."""
    W = 1834
    p = wardrobe_shell(W, n_plinth="13", plinths=2)
    pa, pb = (459.5, 475.5), (1358.5, 1374.5)        # partitions: the middle section 883 between them
    p.append(box("5", [pa[0], Y_IN, ZS0, pa[1], Y_TOP, ZIN], "5", mat="white"))
    p.append(box("6", [pb[0], Y_IN, ZS0, pb[1], Y_TOP, ZIN], "6", mat="white"))
    p += column_shelves("l", 17, pa[0], [JOINT + 8], [468, 832, 1531, 1880], "7", "9")
    p += column_shelves("r", pb[1], W - 17, [JOINT + 8], [468, 832, 1531, 1880], "7", "9")
    # middle: horizontal 8 over the drawers, the hat shelf 8, the rail under it, Царга 14 behind the back joint
    for i, yt in enumerate([671, 1931]):
        p.append(box(f"8-{i + 1}", [pa[1], yt - T, ZS0, pb[0], yt, ZIN], "8", mat="white"))
    p.append(box("14", [pa[1], JOINT - 64, ZS0, pb[0], JOINT + 64, ZS0 + T], "14", mat="white"))
    p.append(rail("d3", 478.5, 1355.5, 1850, 296))
    # backs nailed on: 462 (outer) + 448 + 448 (middle, joined by the profile z3) + 462, two rows of 1105
    xs = [(7, 469, "15"), (469, 917, "16"), (917, 1365, "16"), (1365, 1827, "15")]
    k = {"15": 0, "16": 0}
    for y0 in (Y_BOT, JOINT):
        for x0, x1, n in xs:
            k[n] += 1
            p.append(back(f"{n}-{k[n]}", x0, y0, x1, y0 + 1105, n))
    moves = []
    # doors: A (outer, inset, inner hinges), Б / В (middle, half-overlay on the partitions) over three drawers
    dx = [(19.6, 465.6), (469.2, 915.2), (918.8, 1364.8), (1368.4, 1814.4)]
    dA1 = [box("10-1", [dx[0][0], DOOR_Y[0], ZF0, dx[0][1], DOOR_Y[1], ZF1], "10", kind="front", grain="y"),
           knob("1", dx[0][1] - 30, KY, ZF1)]
    dB = [box("11", [dx[1][0], 671, ZF0, dx[1][1], DOOR_Y[1], ZF1], "11", kind="front", grain="y"),
          knob("2", dx[1][1] - 30, KY, ZF1)]
    dV = [box("12", [dx[2][0], 671, ZF0, dx[2][1], DOOR_Y[1], ZF1], "12", kind="front", grain="y"),
          knob("3", dx[2][0] + 30, KY, ZF1)]
    dA2 = [box("10-2", [dx[3][0], DOOR_Y[0], ZF0, dx[3][1], DOOR_Y[1], ZF1], "10", kind="front", grain="y"),
           knob("4", dx[3][0] + 30, KY, ZF1)]
    p += dA1 + dB + dV + dA2
    moves += [door("door_1", dA1, "left", [dx[0][0], ZF1]), door("door_2", dB, "left", [dx[1][0], ZF1]),
              door("door_3", dV, "right", [dx[2][1], ZF1]), door("door_4", dA2, "right", [dx[3][1], ZF1])]
    # drawers 896 × 200 on ball runners (box 857 = 825 + 2 × 16 in the 883 opening: 13 mm a side)
    bx = (917 - 428.5, 917 + 428.5)
    for i, y0 in enumerate([61, 264.5, 468]):
        parts, mv = drawer(str(i + 1), [469, y0, ZF0, 1365, y0 + 200, ZF1], bx, y0 + 28, 148, ZF0 - 450, ZF0,
                           ns=("20", "21", "22", "23", "24"), knobs=[(619, y0 + 100), (1215, y0 + 100)])
        p += parts
        moves.append(mv)
    p += glides([(8, 60), (8, 540), (W - 8, 60), (W - 8, 540)] + [(x, ZF0 + 6) for x in (150, 650, 1184, W - 150)]
                + [(x, 11) for x in (150, 650, 1184, W - 150)])
    did = "prizma-nyu-1-19"
    model(did, "П3.0592.1.19", "Шкаф для одежды 4д «Призма Нью»", "bedroom", [1834, 592, 2274], 118,
          "по инструкции; средние двери полунакладные над тремя ящиками", **{"is": isfile(did)})
    return dump(did, [1834, 592, 2274], p, moves)


def w101():
    """Шкаф 3Д П3.592.1.01 — by photo: the 4Д's system; left column with shelves behind a full door, the right
    section 891 wide (hat shelf, rail, Царга) behind a door over three drawers (446) and a full right door; a short
    partition beside the drawers carries the fixed horizontal over them (photos 1-01_0 … 1-01_2)."""
    W = 1384
    p = wardrobe_shell(W, n_plinth="plinth", plinths=2)
    pa = (459.25, 475.25)
    p.append(box("partition", [pa[0], Y_IN, ZS0, pa[1], Y_TOP, ZIN], mat="white"))
    p += column_shelves("l", 17, pa[0], [JOINT + 8], [468, 832, 1531, 1880], "fix", "shelf")
    sx = (908.75, 924.75)          # the short partition under the middle / right door joint
    p.append(box("partition-low", [sx[0], Y_IN, ZS0, sx[1], 655, ZIN], mat="white"))
    p.append(box("hor-low", [pa[1], 655, ZS0, W - 17, 671, ZIN], mat="white"))
    p.append(box("hat", [pa[1], 1915, ZS0, W - 17, 1931, ZIN], mat="white"))
    p.append(box("rail-back", [pa[1], JOINT - 64, ZS0, W - 17, JOINT + 64, ZS0 + T], mat="white"))
    p.append(rail("d3", pa[1] + 3, W - 20, 1850, 296))
    for y0 in (Y_BOT, JOINT):
        p.append(back(f"back-l-{y0}", 7, y0, 469, y0 + 1105))
        p.append(back(f"back-m-{y0}", 469, y0, 923, y0 + 1105))
        p.append(back(f"back-r-{y0}", 923, y0, 1377, y0 + 1105))
    dx = [(19.5, 465.5), (469, 915), (918.5, 1364.5)]
    d1 = [box("door-1", [dx[0][0], DOOR_Y[0], ZF0, dx[0][1], DOOR_Y[1], ZF1], kind="front", grain="y"),
          knob("1", dx[0][1] - 30, KY, ZF1)]
    d2 = [box("door-2", [dx[1][0], 671, ZF0, dx[1][1], DOOR_Y[1], ZF1], kind="front", grain="y"),
          knob("2", dx[1][1] - 30, KY, ZF1)]
    d3 = [box("door-3", [dx[2][0], DOOR_Y[0], ZF0, dx[2][1], DOOR_Y[1], ZF1], kind="front", grain="y"),
          knob("3", dx[2][0] + 30, KY, ZF1)]
    p += d1 + d2 + d3
    moves = [door("door_1", d1, "left", [dx[0][0], ZF1]), door("door_2", d2, "left", [dx[1][0], ZF1]),
             door("door_3", d3, "right", [dx[2][1], ZF1])]
    bx = (pa[1] + 13, sx[0] - 13)
    for i, y0 in enumerate([61, 264.5, 468]):
        parts, mv = drawer(str(i + 1), [dx[1][0], y0, ZF0, dx[1][1], y0 + 200, ZF1], bx, y0 + 28, 148, ZF0 - 450, ZF0,
                           knobs=[(692, y0 + 100)])
        p += parts
        moves.append(mv)
    p += glides([(8, 60), (8, 540), (W - 8, 60), (W - 8, 540), (150, ZF0 + 6), (W - 150, ZF0 + 6), (150, 11),
                 (W - 150, 11)])
    did = "prizma-nyu-1-01"
    model(did, "П3.0592.1.01", "Шкаф 3д «Призма Нью»", "bedroom", [1384, 592, 2274], 118,
          f"{BYPHOTO}; по системе шкафов 2д / 4д: левая дверь — полки, средняя дверь над тремя ящиками, правая дверь; "
          "секция для одежды 891 с полкой и штангой")
    return dump(did, [1384, 592, 2274], p, moves)


# ------------------------------------------------------------------------------------------------ corner wardrobe
def w120():
    """Шкаф угловой 2Д П3.592.1.20 — by instruction. Plan (walls along z = 0 and x = 0): a pentagon 1024 × 1024 with
    the corner opposite the walls cut at 45°. Left wing: side 3 (z 1008..1024, parallel to the back wall, 369 deep
    along x) and partition 5, shelves 315 wide between them; right wing: side 4 (x 1008..1024) and partition 6, shelves
    408; between them the hanging corner: the ЛДСП back 7 on the back wall, the hat shelf 11 (655 × 348) and Царга 8
    along the left wall, two rails 648. Two doors 446 on the 45° diagonal on corner hinges (НСКТ 45°)."""
    S = 1024
    p = []
    top = box("1", [3, Y_TOP, 3, S, Y_TOP + T, S], "1", shape="path",
              outline=f"M 3 3 H {S} V 391 L 391 {S} H 3 Z")
    base = box("2", [3, Y_BOT, 3, 1007, Y_IN, 1007], "2", mat="white", shape="path",
               outline="M 3 3 H 1007 V 382 L 382 1007 H 3 Z")
    p += [top, base]
    # side 3: across x (0..372) at the front-left, parallel to the back wall; its notch at the wall end (x 3)
    s3 = box("3", [3, GL, 1008, 372, Y_TOP, S], "3", shape="path",
             outline=f"M 23 {GL} H 372 V {Y_TOP} H 3 V {GL + 60} A 20 20 0 0 0 23 {GL + 40} Z")
    s4 = side("4", 1008, GL, Y_TOP, 3, 372, "4")
    p += [s3, s4]
    # partitions 349 deep from the walls, shelves between them and the sides
    p.append(box("5", [3, Y_IN, 676, 352, Y_TOP, 692], "5", mat="white"))
    p.append(box("6", [583, Y_IN, 3, 599, Y_TOP, 352], "6", mat="white"))
    p.append(box("7", [3, Y_IN, 3, 582, Y_TOP, 19], "7", mat="white"))
    # fixed horizontals on the joints of the backs 16 / 17 (y 796, 1532), loose shelves between
    for i, yt in enumerate([804, 1540]):
        p.append(box(f"9-{i + 1}", [3, yt - T, 692.5, 351, yt, 1007.5], "9", mat="white"))
        p.append(box(f"10-{i + 1}", [599.5, yt - T, 3, 1007.5, yt, 351], "10", mat="white"))
    for i, yt in enumerate([440, 1172, 1900]):
        p.append(box(f"12-{i + 1}", [5, yt - T, 693, 345, yt, 1007], "12", mat="white"))
        p.append(box(f"13-{i + 1}", [600, yt - T, 5, 1007, yt, 345], "13", mat="white"))
    # the corner: hat shelf 11 along the left wall between the back 7 and partition 5, Царга 8 behind the back joint
    p.append(box("11", [3, 1915, 20, 351, 1931, 675], "11", mat="white"))
    p.append(box("8", [3, JOINT - 48, 20, 19, JOINT + 48, 675], "8", mat="white"))
    p.append({"id": "d3-1", "kind": "tube", "mat": "chrome", "box": [270, 1850, 23.5, 300, 1865, 671.5], "covers": ["d3"]})
    p.append({"id": "d3-2", "kind": "tube", "mat": "chrome", "box": [270, 1000, 23.5, 300, 1015, 671.5], "covers": ["d3"]})
    # backs: on the back wall 7 (ЛДСП, inside) + 16 (ХДФ 439, 3 × 736) over the right wing; on the left wall 18
    # (2 × 2 × 337 × 1105) over the corner and 17 (337, 3 × 736) over the left wing
    for i in range(3):
        y0 = Y_BOT + 736 * i
        p.append(back(f"16-{i + 1}", 585, y0, S, y0 + 736, "16"))
        p.append(box(f"17-{i + 1}", [0, y0, 687, BK, y0 + 736, S], "17", kind="back", mat="white"))
    k = 0
    for y0 in (Y_BOT, JOINT):
        for z0 in (3, 340):
            k += 1
            p.append(box(f"18-{k}", [0, y0, z0, BK, y0 + 1105, z0 + 337], "18", kind="back", mat="white"))
    # plinths: one under the diagonal (turned 45°), one along the back wall
    c = 670.0
    p.append({"id": "15-1", "kind": "panel", "box": [c - 451, GL, c - 8, c + 451, Y_BOT, c + 8],
              "rot": {"axis": "y", "deg": 45, "about": [c, 32, c]}, "covers": ["15"]})
    p.append(box("15-2", [105, GL, 3, 1007, Y_BOT, 19], "15"))
    # doors: the diagonal x + z = 1414 is their face; each door a 16-mm board swept along its line (a moulding with the
    # door's section) — see the notes: a turned `front` would be exact in the engine, but the checker bounds turned
    # boards by their axis-aligned box and reports false overlaps with the base
    e = (1 / math.sqrt(2), -1 / math.sqrt(2))
    M = (701.35, 701.35)                       # middle of the diagonal on the doors' mid-plane (x + z = 1402.7)

    def at(s, off=0.0):
        return (M[0] + s * e[0] + off / math.sqrt(2), M[1] + s * e[1] + off / math.sqrt(2))

    moves = []
    for name, (s0, s1), hinge, ks in (("door_left", (-447.5, -1.5), "left", -31.5),
                                      ("door_right", (1.5, 447.5), "right", 31.5)):
        a, b = at(s0), at(s1)
        tag = "1" if hinge == "left" else "2"
        dp = {"id": f"14-{tag}", "kind": "moulding", "profile": "prizma-nyu-door", "plane": "top", "z": DOOR_Y[0],
              "path": [[r1(a[0]), r1(a[1])], [r1(b[0]), r1(b[1])]], "mat": "front", "covers": ["14"]}
        kx, kz = at(ks, 8)
        kn = knob(tag, kx, KY, kz, rot={"axis": "y", "deg": 45, "about": [r1(kx), KY, r1(kz)]})
        hx, hz = at(s0 if hinge == "left" else s1, 8)
        p += [dp, kn]
        moves.append(door(name, [dp, kn], hinge, [hx, hz]))
    p += glides([(40, 1016), (340, 1016), (1016, 40), (1016, 340), (882, 458), (458, 882), (150, 11), (960, 11)])
    did = "prizma-nyu-1-20"
    model(did, "П3.0592.1.20", "Шкаф угловой 2д «Призма Нью»", "bedroom", [1024, 1024, 2274], 118,
          "по инструкции; угловой: план — квадрат 1024 со срезанным под 45° углом, двери на диагонали", **{"is": isfile(did)})
    return dump(did, [1024, 1024, 2274], p, moves)


# ------------------------------------------------------------------------------------------------ coupe wardrobes
# heights: sides 2272 on the glides (4..2276), top 2276..2292, plinths 74 (4..78), base 78..94 between the sides;
# the doors run 100..2270 between the bottom tracks (94..100) and the top tracks (2270..2276)
CY_BASE, CY_IN, CY_TOP = 78, 94, 2276
CD_Y = (100, 2270)
LANES = {"rear": (573, 589), "front": (612, 628)}   # door panel z (profiles ±10)


def coupe_door(tag, x0, x1, lane, n_panel=None, mirror=False):
    """A coupe door: the ЛДСП panel between two aluminium handle profiles (20 wide, 36 deep, 10 mm over the panel)."""
    z0, z1 = LANES[lane]
    p = [box(n_panel and f"{n_panel}-{tag}" or f"panel-{tag}", [x0 + 10, CD_Y[0], z0, x1 - 10, CD_Y[1], z1], n_panel,
             kind="front", grain="y"),
         {"id": f"m7-{tag}a", "kind": "panel", "mat": PROFILE, "edge": 2, "box": [r1(x0), CD_Y[0], z0 - 10, r1(x0 + 20), CD_Y[1], z1 + 10],
          "covers": ["m7"]},
         {"id": f"m7-{tag}b", "kind": "panel", "mat": PROFILE, "edge": 2, "box": [r1(x1 - 20), CD_Y[0], z0 - 10, r1(x1), CD_Y[1], z1 + 10],
          "covers": ["m7"]}]
    if mirror:
        p.append({"id": f"mirror-{tag}", "kind": "mirror", "box": [r1(x0 + 20), CD_Y[0] + 10, z1, r1(x1 - 20), CD_Y[1] - 10, z1 + 4]})
    return p


def tracks(x0, x1, instructed=True):
    out = []
    for lane, (z0, z1) in LANES.items():
        for pos, (y0, y1) in (("bottom", (CY_IN, CD_Y[0])), ("top", (CD_Y[1], CY_TOP))):
            q = {"id": f"m6-{lane}-{pos}", "kind": "panel", "mat": PROFILE, "edge": 1,
                 "box": [r1(x0), y0, z0 - 2, r1(x1), y1, z1 + 2]}
            if instructed:
                q["covers"] = ["m6"]
            out.append(q)
    return out


def coupe_shell(W, instructed):
    n = (lambda k: k) if instructed else (lambda k: None)
    p = [box(n("4") or "top", [0, CY_TOP, 0, W, CY_TOP + T, 650], n("4")),
         box(n("5") or "base", [16.5, CY_BASE, 0, W - 16.5, CY_IN, 648], n("5")),
         side(n("1") or "side-l", 0, GL, CY_TOP, 0, 649, n("1")),
         side(n("2") or "side-r", W - T, GL, CY_TOP, 0, 649, n("2")),
         box(n("10") and "10-1" or "plinth-1", [16.5, GL, 632, W - 16.5, CY_BASE, 648], n("10")),
         box(n("10") and "10-2" or "plinth-2", [16.5, GL, 0, W - 16.5, CY_BASE, T], n("10"))]
    p += tracks(17, W - 17, instructed)
    p += glides([(8, 60), (8, 590), (W - 8, 60), (W - 8, 590), (200, 640), (W - 200, 640), (200, 8), (W - 200, 8)])
    return p


def hang_section(tag, x0, x1, ns=("7", "6", "11", "12", "d3"), rail_len=None):
    """Hanging section of a coupe wardrobe (inner x0..x1 = 880): fixed horizontals 7 low (438) and high (1922) on the
    back joints, Царга 6 behind the middle joint (1180), the rail under the hat shelf; backs 11 (353) at the bottom and
    top, 2 × 2 × 12 (742 × 446) between them."""
    n7, n6, n11, n12, nd = ns
    p = []
    for i, yt in enumerate([446, 1930]):
        p.append(box(f"{n7 or 'hor'}-{tag}{i + 1}", [x0, yt - T, 5, x1, yt, 540], n7, mat="white"))
    p.append(box(f"{n6 or 'rail-back'}-{tag}", [x0, 1116, 13, x1, 1244, 29], n6, mat="white"))
    L = rail_len or (x1 - x0 - 7)
    xc = (x0 + x1) / 2
    p.append(rail(f"{nd}-{tag}", xc - L / 2, xc + L / 2, 1865, 300))
    bx0, bx1 = x0 - 6.5, x1 + 6.5
    p.append(back(f"{n11 or 'back'}-{tag}1", bx0, 85, bx1, 438, n11, z0=10))
    p.append(back(f"{n11 or 'back'}-{tag}2", bx0, 1922, bx1, 2275, n11, z0=10))
    k = 0
    xm = (bx0 + bx1) / 2
    for y0 in (438, 1180):
        for a, b in ((bx0, xm - 0.5), (xm + 0.5, bx1)):
            k += 1
            p.append(back(f"{n12 or 'back'}-{tag}m{k}", a, y0, b, y0 + 742, n12, z0=10))
    return p


def shelf_section(tag, x0, x1, ns=("8", "9", "13")):
    """Shelf section (inner x0..x1): fixed horizontals 8 at 446 / 1189 / 1930 (the back joint at 1181), loose shelves 9
    at 816 / 1566, backs 13 in two rows of 1096."""
    n8, n9, n13 = ns
    p = []
    for i, yt in enumerate([446, 1189, 1930]):
        p.append(box(f"{n8 or 'hor'}-{tag}{i + 1}", [x0 + 0.5, yt - T, 5, x1 - 0.5, yt, 540], n8, mat="white"))
    for i, yt in enumerate([816, 1566]):
        p.append(box(f"{n9 or 'shelf'}-{tag}{i + 1}", [x0 + 1, yt - T, 14, x1 - 1, yt, 540], n9, mat="white"))
    for i, y0 in enumerate([85, 1181]):
        p.append(back(f"{n13 or 'back'}-{tag}{i + 1}", x0 - 6.5, y0, x1 + 6.5, y0 + 1096, n13, z0=10))
    return p


def c121():
    """Шкаф-купе 2Д П3.592.1.21 — by instruction: hanging section 880 left, shelves 599 right."""
    W = 1529
    p = coupe_shell(W, True)
    p.append(box("3", [896.5, CY_IN, 4, 912.5, CY_TOP, 540], "3", mat="white"))
    p += hang_section("", 16.5, 896.5, rail_len=873)
    p += shelf_section("", 912.5, 1512.5)
    # doors 784 (panel 764 + 2 × 10 into the profiles): the left one on the rear track, the right one in front,
    # 71 mm overlap
    dl = coupe_door("l", 16, 800, "rear", "20")
    dr = coupe_door("r", 729, 1513, "front", "20")
    p += dl + dr
    moves = [{"type": "slide", "name": "coupe_left", "parts": ids(dl), "by": [713, 0, 0]},
             {"type": "slide", "name": "coupe_right", "parts": ids(dr), "by": [-713, 0, 0]}]
    did = "prizma-nyu-1-21"
    model(did, "П3.0592.1.21", "Шкаф-купе 2д «Призма Нью»", "bedroom", [1529, 650, 2292], 118,
          "по инструкции; двери-купе MITO PLUS: щит ЛДСП между алюминиевыми профилями-ручками", **{"is": isfile(did)})
    return dump(did, [1529, 650, 2292], p, moves)


def c122(did, code, mirror):
    """Шкаф-купе 3Д — by photo (catalogue cut-outs only): the 2Д's system at 2027; sections shelves 599 | hanging 880 |
    shelves 481, three doors 692 (two on the rear track, the middle one in front, 40 mm overlaps)."""
    W = 2027
    p = coupe_shell(W, False)
    pa, pb = (616, 632), (1512.5, 1528.5)
    p.append(box("partition-1", [pa[0], CY_IN, 4, pa[1], CY_TOP, 540], mat="white"))
    p.append(box("partition-2", [pb[0], CY_IN, 4, pb[1], CY_TOP, 540], mat="white"))
    p += shelf_section("a", 16.5, pa[0], ns=(None, None, None))
    p += hang_section("m", pa[1], pb[0], ns=(None, None, None, None, "d3"))
    p += shelf_section("b", pb[1], W - 16.5, ns=(None, None, None))
    d1 = coupe_door("1", 16, 708, "rear")
    d2 = coupe_door("2", 667.5, 1359.5, "front", mirror=mirror)
    d3 = coupe_door("3", 1319, 2011, "rear")
    p += d1 + d2 + d3
    moves = [{"type": "slide", "name": "coupe_1", "parts": ids(d1), "by": [651.5, 0, 0]},
             {"type": "slide", "name": "coupe_2", "parts": ids(d2), "by": [-651.5, 0, 0]},
             {"type": "slide", "name": "coupe_3", "parts": ids(d3), "by": [-651.5, 0, 0]}]
    model(did, code, "Шкаф-купе 3д «Призма Нью»", "bedroom", [2027, 650, 2292], 118,
          f"{BYPHOTO}; по системе шкафа-купе 2д (П3.0592.1.21); секции полки 599 | штанга 880 | полки 481"
          + ("; средняя дверь с зеркалом" if mirror else ""))
    return dump(did, [2027, 650, 2292], p, moves)


# ================================================================================================ small case pieces
def k103():
    """Комод П3.592.1.03 — by photo (1-03_1 front-on): the wardrobes' system at 903 × 442 × 932; four inset drawers
    157 / 231 / 231 / 231, two knobs each at ±292 from the middle."""
    W, D, H = 903, 442, 932
    zs0, zs1 = BK, D - 1                 # sides 438, top 439
    zf0, zf1 = zs1 - T, zs1
    yt = H - T                           # 916
    p = [box("top", [0, yt, zs0, W, H, D]),
         side("side-l", 0, GL, yt, zs0, zs1), side("side-r", W - T, GL, yt, zs0, zs1),
         box("bottom", [17, 54, zs0, W - 17, 70, zf0 - 2], mat="white"),
         box("plinth-1", [17, GL, zf0 - 2, W - 17, 54, zf1 - 2]), box("plinth-2", [17, GL, zs0, W - 17, 54, zs0 + T]),
         back("back", 3, 54, W - 3, 913)]
    moves = []
    fr = [(56, 287), (290, 521), (524, 755), (758, 915)]
    for i, (y0, y1) in enumerate(fr):
        h = 110 if i == 3 else 180
        parts, mv = drawer(str(i + 1), [18, y0, zf0, W - 18, y1, zf1], (29, W - 29), max(y0 + 22, 72), h, zf0 - 400, zf0,
                           knobs=[(158, (y0 + y1) / 2), (745, (y0 + y1) / 2)])
        p += parts
        moves.append(mv)
    p += glides([(8, 60), (8, 400), (W - 8, 60), (W - 8, 400), (150, zf0 + 4), (W - 150, zf0 + 4)])
    did = "prizma-nyu-1-03"
    model(did, "П3.0592.1.03", "Комод «Призма Нью»", "bedroom", [W, D, H], 118,
          f"{BYPHOTO}; четыре вкладных ящика (верхний ниже), по две ручки")
    return dump(did, [W, D, H], p, moves)


def t105():
    """Тумба прикроватная П3.592.1.05 — by photo (1-05_1 front-on): open niche 192 high over a fixed shelf, one inset
    drawer 200 with a knob in the middle, recessed plinth."""
    W, D, H = 486, 394, 482
    zs0, zs1 = BK, D - 1
    zf0, zf1 = zs1 - T, zs1
    yt = H - T                           # 466
    p = [box("top", [0, yt, zs0, W, H, D]),
         side("side-l", 0, GL, yt, zs0, zs1), side("side-r", W - T, GL, yt, zs0, zs1),
         box("shelf", [17, 258, zs0, W - 17, 274, zs1], mat="body"),
         box("bottom", [17, 54, zs0, W - 17, 70, zf0 - 2], mat="white"),
         box("plinth-1", [17, GL, zf0 - 4, W - 17, 54, zf1 - 4]), box("plinth-2", [17, GL, zs0, W - 17, 54, zs0 + T]),
         back("back", 3, 54, W - 3, 480)]
    parts, mv = drawer("1", [20, 56, zf0, W - 20, 256, zf1], (30, W - 30), 80, 150, zf0 - 350, zf0,
                       knobs=[(W / 2, 156)])
    p += parts
    p += glides([(8, 60), (8, 360), (W - 8, 60), (W - 8, 360)])
    did = "prizma-nyu-1-05"
    model(did, "П3.0592.1.05", "Тумба прикроватная «Призма Нью»", "bedroom", [W, D, H], 118,
          f"{BYPHOTO}; открытая ниша над ящиком")
    return dump(did, [W, D, H], p, [mv])


# ------------------------------------------------------------------------------------------------ стеллаж
def s106():
    """Стеллаж П3.592.1.06 — by photo (1-06_0 … 1-06_3). Two tall sides (left «Ночное небо», right «Призма») and six
    open boxes 582 × 360 × 370 stacked from a 50-mm plinth: boxes 1, 3, 5 (from the top) framed in «Призма» with a
    navy back, 2, 4, 6 navy with a «Призма» back; box 5 holds two navy drawers, box 6 two «Призма» drawers. The
    catalogue gives L614/1050: the same kit stands as a 614 tower or, the boxes shifted alternately to the two sides
    1050 apart, as the staggered 1050 variant — this design is the 1050 variant (index size)."""
    W, D, H = 1050, 360, 2274
    BW, BH = 582, 370
    p = [side("side-l", 0, GL, H, 0, D), side("side-r", W - T, GL, H, 0, D, mat="front")]
    moves = []
    for k in range(6):
        top = H - BH * k
        bot = top - BH
        right = k % 2 == 0                     # boxes 1, 3, 5 at the right side
        x0 = W - T - BW if right else T
        x1 = x0 + BW
        fm, bm = ("front", "body") if right else ("body", "front")
        t = f"b{k + 1}"
        p += [box(f"{t}-top", [x0, top - T, 0, x1, top, D], mat=fm),
              box(f"{t}-bottom", [x0, bot, 0, x1, bot + T, D], mat=fm),
              box(f"{t}-side-l", [x0, bot + T, 0, x0 + T, top - T, D], mat=fm, grain="y"),
              box(f"{t}-side-r", [x1 - T, bot + T, 0, x1, top - T, D], mat=fm, grain="y"),
              box(f"{t}-back", [x0 + T, bot + T, 0, x1 - T, top - T, T], mat=bm)]
        if k >= 4:
            dm = "body" if k == 4 else "front"
            ih = BH - 2 * T                    # 338 inside
            fh = (ih - 3 * 3) / 2
            for j in range(2):
                y0 = bot + T + 3 + j * (fh + 3)
                parts, mv = drawer(f"{k + 1}{j + 1}", [x0 + T + 2, y0, D - T, x1 - T - 2, y0 + fh, D],
                                   (x0 + T + 13, x1 - T - 13), y0 + 18, 120, D - T - 300, D - T,
                                   knobs=[((x0 + x1) / 2, y0 + fh / 2)], fmat=dm)
                p += parts
                moves.append(mv)
    # the plinth under the bottom box (left), front and back
    p += [box("plinth-1", [T, GL, D - T - 4, T + BW, 54, D - 4]), box("plinth-2", [T, GL, 0, T + BW, 54, T])]
    p += glides([(8, 60), (8, 320), (W - 8, 60), (W - 8, 320), (120, D - 12), (T + BW - 100, D - 12)])
    did = "prizma-nyu-1-06"
    model(did, "П3.0592.1.06", "Стеллаж «Призма Нью»", "storage", [W, D, H], 118,
          f"{BYPHOTO}; каталог L614/1050 — собран вариант 1050 (короба смещены попеременно к боковинам); "
          "вариант 614 — те же 6 коробов друг над другом между боковинами")
    return dump(did, [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------------ dressing table
def t140():
    """Стол туалетный П3.592.1.40 — by photo (p. 118 cut-out, p. 116 interior): a table on two side panels (top 800)
    with a full-width inset «Призма» drawer 156 under the top and a modesty panel at the back; on it a superstructure
    968 × 200 × 800: two shelf towers 210 wide («Призма» backs and shelves) either side of the mirror (476 × 675 on a
    navy back), the recess under the mirror open."""
    W, D, H = 1000, 439, 1600
    ty = 784                                  # the table top 784..800
    p = [side("leg-l", 0, GL, ty, 0, D, notch=False), side("leg-r", W - T, GL, ty, 0, D, notch=False),
         box("top", [0, ty, 0, W, ty + T, D]),
         box("modesty", [T, 430, 0, W - T, ty, T])]
    # no knob: neither the p. 118 cut-out nor the p. 116 photo shows one on this drawer (a push latch or a pull
    # under the front's edge)
    parts, mv = drawer("1", [18, 626, D - T, W - 18, 782, D], (T + 13, W - T - 13), 640, 120, 40, D - T)
    p += parts
    moves = [mv]
    # superstructure
    y0, y1 = ty + T, H
    SD = 200
    xs0, xs1 = 16, 984
    p += [box("s-side-l", [xs0, y0, 0, xs0 + T, y1 - T, SD], grain="y"),
          box("s-side-r", [xs1 - T, y0, 0, xs1, y1 - T, SD], grain="y"),
          box("s-top", [xs0, y1 - T, 0, xs1, y1, SD]),
          box("s-up-l", [242, y0, 0, 258, y1 - T, SD], grain="y"),
          box("s-up-r", [742, y0, 0, 758, y1 - T, SD], grain="y"),
          box("s-back-l", [xs0 + T, y0, 0, 242, y1 - T, T], mat="front"),
          box("s-back-r", [758, y0, 0, xs1 - T, y1 - T, T], mat="front"),
          box("s-back-m", [258, y0, 0, 742, y1 - T, T]),
          {"id": "mirror", "kind": "mirror", "box": [262, 905, T, 738, 1580, T + 4]}]
    for i, yt in enumerate([1089, 1347]):
        p.append(box(f"s-shelf-l{i + 1}", [xs0 + T, yt - T, T, 242, yt, SD - 2], mat="front"))
        p.append(box(f"s-shelf-r{i + 1}", [758, yt - T, T, xs1 - T, yt, SD - 2], mat="front"))
    p += glides([(8, 40), (8, 400), (W - 8, 40), (W - 8, 400)])
    did = "prizma-nyu-1-40"
    model(did, "П3.0592.1.40", "Стол туалетный «Призма Нью»", "bedroom", [W, D, H], 118,
          f"{BYPHOTO}; надстройка с зеркалом и открытыми полками по бокам; у ящика ручки на фото не видно")
    return dump(did, [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------------ mirrors, shelf
def m104():
    """Зеркало П3.592.1.04 — by photo: a navy board 973 × 801 with the mirror (14-mm navy border) and a «Призма» ledge
    973 × 112 under it (B 112 = the ledge)."""
    W, D, H = 973, 112, 817
    p = [box("board", [0, T, 0, W, H, T]),
         {"id": "mirror", "kind": "mirror", "box": [14, 30, T, W - 14, H - 14, T + 4]},
         box("ledge", [0, 0, 0, W, T, D], mat="front")]
    did = "prizma-nyu-1-04"
    model(did, "П3.0592.1.04", "Зеркало «Призма Нью»", "decor", [W, D, H], 118,
          f"{BYPHOTO}; B112 — полочка «Призма» под зеркалом", mount="wall")
    return dump(did, [W, D, H], p, [])


def m336():
    """Зеркало П3.592.3.36 — by photo (3-36_0, p. 117): a «Призма» board 430 × 790 with a round mirror Ø590 in a thin
    black ring that stands out past the board's right edge (L 642), a navy ledge 400 × 96 near the bottom."""
    W, D, H = 642, 112, 790
    cx, cy, R = W - 295, 444, 295
    p = [box("board", [0, 0, 0, 430, H, T], mat="front", grain="y"),
         {"id": "mirror", "kind": "mirror", "shape": "circle", "box": [cx - R + 4, cy - R + 4, T, cx + R - 4, cy + R - 4, T + 4]},
         {"id": "ring", "kind": "panel", "shape": "ring", "inner": 2 * R - 12, "mat": "black", "edge": 1,
          "box": [cx - R, cy - R, T + 4, cx + R, cy + R, T + 8]},
         box("ledge", [15, 10, T, 415, 26, D])]
    did = "prizma-nyu-3-36"
    model(did, "П3.0592.3.36", "Зеркало «Призма Нью»", "decor", [W, D, H], 118,
          f"{BYPHOTO}; круглое зеркало в чёрном ободе на щите «Призма», полочка «Ночное небо» внизу", mount="wall")
    return dump(did, [W, D, H], p, [])


def s025():
    """Полка П3.592.0.25 — by instruction: a navy back board 900 × 230 on two kitchen hangers, the «Призма» shelf
    899 × 214 at its foot, a quarter-round «Призма» divider R198 at x ≈ 294."""
    W, D, H = 900, 230, 230
    p = [box("1", [0, 0, 0, W, H, T], "1"),
         box("2", [0.5, 0, T, W - 0.5, T, D], "2", mat="front"),
         box("3", [294, T, T, 310, T + 198, T + 198], "3", mat="front", shape="path",
             outline=f"M {T} {T} H {T + 198} A 198 198 0 0 1 {T} {T + 198} Z")]
    did = "prizma-nyu-0-25"
    model(did, "П3.0592.0.25", "Полка «Призма Нью»", "living", [W, D, H], 118, "по инструкции; навесная",
          mount="wall", **{"is": isfile(did)})
    return dump(did, [W, D, H], p, [])


# ================================================================================================ desks
def desk_block(tag, xw, xb0, xb1, zb, zf, first_front, ns, wall_n=None, bottom_n=None, pid_wall=None, pid_bottom=None):
    """A hanging drawer block under the top (the 2.09 instruction): a wall 351 × 543 at xw, a bottom 400 × 542 between
    xb0..xb1 (393..409), two inset fronts 163 × 396 with drawers 500 deep."""
    p = [box(pid_wall or wall_n, [xw, 393, zb, xw + T, 744, zf], wall_n),
         box(pid_bottom or bottom_n, [xb0, 393, zb, xb1, 409, zf - 1], bottom_n)]
    moves = []
    for j, y0 in enumerate([412, 578]):
        parts, mv = drawer(f"{tag}{j + 1}", [xb0 + 2, y0, zf - T, xb1 - 2, y0 + 163, zf], (xb0 + 13.5, xb1 - 13.5), y0 + 14,
                           136, zf - T - 500, zf - T, ns=ns, knobs=[((xb0 + xb1) / 2, y0 + 81.5)])
        p += parts
        moves.append(mv)
    return p, moves


def d209():
    """Стол письменный 2т П3.592.2.09 — by instruction: top 2100 × 600 over two sides and a middle leg panel (all
    740 on glides), a modesty panel 2026 × 506 between the sides, two hanging blocks of two drawers each side of the
    middle panel."""
    W, D, H = 2100, 600, 760
    zb, zf = 37, 580
    p = [box("4", [0, 744, 0, W, H, D], "4"),
         box("1", [21, GL, 20, 37, 744, 580], "1"), box("2", [2063, GL, 20, 2079, 744, 580], "2"),
         box("3", [1042, GL, zb, 1058, 744, zf], "3"),
         box("5", [37, 238, 20, 2063, 744, 36], "5")]
    pl, ml = desk_block("l", 626, 642, 1042, zb, zf, None, ("20", "21", "22", "23", "24"), wall_n="7", bottom_n="9")
    pr, mr = desk_block("r", 1458, 1058, 1458, zb, zf, None, ("20", "21", "22", "23", "24"), wall_n="8", bottom_n="10")
    p += pl + pr
    p += glides([(29, 40), (29, 560), (2071, 40), (2071, 560), (1050, 60), (1050, 560)])
    did = "prizma-nyu-2-09"
    model(did, "П3.0592.2.09", "Стол письменный 2т «Призма Нью»", "office", [W, D, H], 118,
          "по инструкции; две подвесные тумбы по два ящика у средней стойки", **{"is": isfile(did)})
    return dump(did, [W, D, H], p, ml + mr)


def d208():
    """Стол письменный П3.592.2.08 — by photo (2-08_0/1, p. 117): the 2.09's construction at 1200 with one hanging
    block of two drawers at the right side."""
    W, D, H = 1200, 600, 760
    zb, zf = 37, 580
    p = [box("top", [0, 744, 0, W, H, D]),
         box("side-l", [21, GL, 20, 37, 744, 580]), box("side-r", [1163, GL, 20, 1179, 744, 580]),
         box("modesty", [37, 238, 20, 1163, 744, 36])]
    pr, mr = desk_block("r", 747, 763, 1163, zb, zf, None, (None,) * 5, pid_wall="block-wall", pid_bottom="block-bottom")
    p += pr
    p += glides([(29, 40), (29, 560), (1171, 40), (1171, 560)])
    did = "prizma-nyu-2-08"
    model(did, "П3.0592.2.08", "Стол письменный «Призма Нью»", "office", [W, D, H], 118,
          f"{BYPHOTO}; как 2т (П3.0592.2.09) с одной подвесной тумбой справа")
    return dump(did, [W, D, H], p, mr)


def d210():
    """Стол письменный П3.592.2.10 — by instruction: top 1000 × 500 on two sides 730 × 454, a back rail 966 × 282 and a
    shelf 966 × 436 under the top; the partition 104 splits the space over the shelf into an open niche (left) and the
    drawer (right, front 487 × 100 inset beside the partition)."""
    W, D, H = 1000, 500, 750
    s0 = 23                                   # the sides from z 23 to 477
    p = [box("3", [0, 734, 0, W, H, D], "3"),
         box("1", [1, GL, s0, 17, 734, s0 + 454], "1"), box("2", [983, GL, s0, 999, 734, s0 + 454], "2"),
         box("4", [17, 452, s0, 983, 734, s0 + T], "4"),
         box("5", [17, 614, s0 + T, 983, 630, s0 + T + 436], "5"),
         box("6", [476, 630, s0 + T, 492, 734, s0 + T + 419], "6")]
    zf = s0 + T + 436                         # 475: the drawer front flush with the shelf's edge
    parts, mv = drawer("1", [494, 632, zf - T, 981, 732, zf], (513.5, 961.5), 634, 96, zf - T - 350, zf - T,
                       ns=("20", "21", "22", "23", "24"), knobs=[(737.5, 682)])
    p += parts
    p += glides([(9, 60), (9, 440), (991, 60), (991, 440)])
    did = "prizma-nyu-2-10"
    model(did, "П3.0592.2.10", "Стол письменный «Призма Нью»", "office", [W, D, H], 118,
          "по инструкции; открытая ниша и ящик под столешницей", **{"is": isfile(did)})
    return dump(did, [W, D, H], p, [mv])


# ================================================================================================ beds
def bed(did, code, name, W, sleep, page, ns_head_first):
    """Кровать with a metal base (металлокаркас, z5): headboard 16 (x 0..W, 896 on glides) with a curved top and an
    upholstered panel (grey velour; 6 cushions on the double bed, one panel on the single), side rails 2010 × 200
    between the headboard and the foot board, the foot board W − 33 × 321 with the «Призма» overlay (накладка 168)
    on its outer face. L = 16 + 2010 + 16 + 16 = 2058."""
    L, H = 2058, 900
    fw = W - 33                                # foot board 1643 / 943
    fx0 = (W - fw) / 2
    ow = fw - 64                               # overlay 1579 / 879
    rail_y = (125, 325)
    # the headboard outline: straight sides to 800 (855 on the single bed), a flat arc to 900 in the middle,
    # the top corners rounded r 40
    ys = 800 if W > 1200 else 870
    head_outline = (f"M 0 {GL} H {W} V {ys - 40} Q {W} {ys} {W - 40} {ys + 4} "
                    f"Q {W / 2} {2 * H - ys - 4} 40 {ys + 4} Q 0 {ys} 0 {ys - 40} Z")
    p = [box("1", [0, GL, 0, W, H, T], "1", shape="path", outline=head_outline),
         box("2", [fx0, GL, 2026, fx0 + fw, 325, 2042], "2"),
         box("3", [(W - ow) / 2, 118, 2042, (W + ow) / 2, 286, 2058], "3", mat="front"),
         box("4-1", [fx0, rail_y[0], T, fx0 + T, rail_y[1], 2026], "4"),
         box("4-2", [fx0 + fw - T, rail_y[0], T, fx0 + fw, rail_y[1], 2026], "4")]

    def arc(x):                                # the headboard's top edge at x
        u = x / W
        return ys + 4 * (H - ys) * u * (1 - u)

    if W > 1200:
        n, x0, x1 = 6, 50, W - 50
        cw = (x1 - x0) / n
        for i in range(n):
            a, b = x0 + i * cw, x0 + (i + 1) * cw
            top = min(arc(a), arc(b)) - 40
            p.append({"id": f"soft-{i + 1}", "kind": "soft", "mat": "fabric", "box": [r1(a), 505, T, r1(b), r1(top), T + 35]})
    else:
        p.append({"id": "soft", "kind": "soft", "mat": "fabric", "box": [40, 505, T, W - 40, ys - 20, T + 35]})
    # the metal base z5 (sleep × 2000): black frame on the rails' brackets, slats, middle legs on the double bed
    bx0, bx1 = (W - sleep) / 2, (W + sleep) / 2
    z0, z1 = 21, 2021
    p += [{"id": "z5-frame-l", "mat": "black", "box": [r1(bx0), 265, z0, r1(bx0 + 30), 295, z1], "covers": ["z5"]},
          {"id": "z5-frame-r", "mat": "black", "box": [r1(bx1 - 30), 265, z0, r1(bx1), 295, z1]},
          {"id": "mattress", "kind": "mattress", "box": [r1(bx0), 303, z0, r1(bx1), 503, z1]}]
    for i in range(24):
        z = 40 + i * 82
        p.append({"id": f"z5-slat-{i + 1}", "mat": "door_enamel_whitey#c9a877", "box": [r1(bx0 + 30), 295, z, r1(bx1 - 30), 303, z + 53]})
    if W > 1200:
        p += [{"id": "z5-beam", "mat": "black", "box": [W / 2 - 15, 265, z0, W / 2 + 15, 295, z1]},
              {"id": "z5-leg-1", "kind": "tube", "mat": "black", "box": [W / 2 - 12.5, 0, 700, W / 2 + 12.5, 265, 725]},
              {"id": "z5-leg-2", "kind": "tube", "mat": "black", "box": [W / 2 - 12.5, 0, 1400, W / 2 + 12.5, 265, 1425]}]
        gp = [(40, 10), (W / 2, 10), (W - 40, 10), (fx0 + 40, 2034), (W / 2, 2034), (fx0 + fw - 40, 2034)]
    else:
        gp = [(40, 10), (W - 40, 10), (fx0 + 40, 2034), (fx0 + fw - 40, 2034)]
    p += glides(gp)
    model(did, code, name, "bedroom", [W, L, H], page,
          f"по инструкции; спальное место 2000×{sleep}, металлокаркас; изголовье с мягкой панелью (велюр)",
          **{"is": isfile(did)})
    return dump(did, [W, L, H], p, [])


def b102():
    return bed("prizma-nyu-1-02", "П3.0592.1.02", "Кровать 2-16 «Призма Нью»", 1676, 1600, 118, True)


def b107():
    return bed("prizma-nyu-1-07", "П3.0592.1.07", "Кровать 1-09 «Призма Нью»", 976, 900, 118, True)


# ================================================================================================ catalogue fragment
FINISHES = [
    {"id": "prizma-nyu-prizma", "name": "«Призма» / «Ночное небо»",
     "body": "door_enamel_whitey#2d3542", "front": "door_enamel_whitey#d5dce2", "back": "door_enamel_whitey#eeeeeb",
     "roles": {"fabric": "velvet#9a9d9d"}, "swatch": "#d5dce2"},
]

COLLECTION = {
    "id": SLUG, "name": "Призма Нью", "brand": "Пинскдрев", "finishes": ["prizma-nyu-prizma"], "metal": "chrome",
    "note": "Каталог «Корпусная мебель ч. II» 2025, с. 116–118 (PDF). Корпус ЛДСП 16 «Ночное небо» (крышка на боковинах, "
            "боковины на опорах-гвоздях с вырезом под плинтус, дно между боковинами на цоколе 56), внутренние детали ЛДСП 16 "
            "белый, задняя стенка ХДФ 3 белый накладная; фасады ЛДСП 16 «Призма» вкладные, квадратные ручки UZ-40-032 "
            "(сатин-хром); шкафы-купе на системе MITO PLUS с профилями-ручками; кровати с металлокаркасом и мягкой панелью "
            "изголовья.",
}

PROFILES = {"prizma-nyu-door": {"name": "Дверь углового шкафа (щит ЛДСП 16 × 2196, симметрично к линии)",
                                "pts": [[-8, 0], [-8, 2196], [8, 2196], [8, 0]]}}


def write_catalog():
    frag = {"finishes": FINISHES, "profiles": PROFILES, "collections": [COLLECTION], "models": MODELS}
    path = os.path.join(HERE, f"{SLUG}_catalog.json")
    with open(path, "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return path


if __name__ == "__main__":
    for f in write_cutlists():
        print(f)
    for f in [w118, w119, w101, w120, c121, lambda: c122("prizma-nyu-1-22", "П3.0592.1.22", False),
              lambda: c122("prizma-nyu-1-23", "П3.0592.1.23", True), k103, t105, s106, t140, m104, m336, s025,
              d209, d208, d210, b102, b107]:
        print(f())
    print(write_catalog())
