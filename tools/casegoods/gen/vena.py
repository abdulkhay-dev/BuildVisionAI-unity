"""«Вена» (Пинскдрев, П6.115): kids' / teen bedroom — wardrobe 2Д, combined wardrobe, chest (тумба), desk, wall shelf,
bed 1-09 with drawers. All six modules by instruction (IS-P6-115-*; completed / transcribed tables in gen/cutlists/).

Construction (instructions + the site's product photos + catalogue p. 115):
  * carcass ЛДСП 16 «Гикори Кингстон»: top and bottom run the full width and depth (435 / 590), the sides stand between
    them and are 17 shallower (418 / 573): the fronts (ЛДСП 16, «Персидский жемчуг» or «Базальт») are overlaid on the
    sides' front edges between the top and the bottom, flush with the top's front edge, 1 mm off the sides; gaps 3 mm,
    2 mm to the top / bottom.
  * partitions and fixed shelves are 16 shallower than the sides and start at z 10, in front of the backs; backs ХДФ 3.5
    in the sides' grooves (z 6–9.5), one piece per section, joined behind the partitions / fixed shelves (the cut-list
    widths are the inner width + 12).
  * legs «Опора Вена»: turned tapered wooden legs 122 (Ø 45 → 28) on flanges and felt pads, the end legs splayed out;
    4 legs (wardrobes), 6 (тумба: 4 corners + 2 at mid-depth), 4 under the desk's pedestal.
  * handles «k»: turned wooden knobs Ø 44, 60 mm under the top edge of drawers; doors near the free edge.
  * drawer boxes ЛДСП 16 (sides, back), ХДФ bottom in grooves, 14 mm runner gaps; the bed's drawers roll on castors.
  * the odd-coloured drawer of a module carries the odd code (12.1 / 9.1) — the colours follow the catalogue photos.
Coordinates: x from the left, y up from the floor, z from the wall (back) to the front; mm.

    /private/tmp/claude-501/venv/bin/python tools/casegoods/gen/vena.py
"""
import json
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
LEG = 122.0
PEARL, BASALT = "front", "accent"


def P(n, box, pid=None, **kw):
    p = {"n": n} if n is not None else {}
    if pid:
        p["id"] = pid
    p.update(kw)
    p["box"] = [round(v, 2) for v in box]
    return p


def knob(pid, x, y, z):
    return {"id": pid, "kind": "handle", "model": "knob", "mat": "wood", "at": [x, y], "d": 44, "t": 18, "standoff": 12,
            "z": z, "covers": ["k"]}


def leg(tag, x, z, sx=0.0, sz=0.0, h=LEG):
    """«Опора Вена»: a turned tapered leg from the bottom's underside to a felt pad (3 mm), splayed by (sx, sz)."""
    return [
        {"id": f"h-{tag}", "kind": "rod", "mat": "wood", "from": [x, h, z], "to": [x + sx, 3, z + sz], "d": 45, "d2": 28,
         "covers": ["h"]},
        {"id": f"t-{tag}", "kind": "panel", "mat": "door_enamel_whitey#8a8378", "shape": "circle", "edge": 0.5,
         "box": [x + sx - 14, 0, z + sz - 14, x + sx + 14, 3, z + sz + 14], "covers": ["t"]},
    ]


def drawer(tag, ns, x0, x1, y0, h, zf, depth, bottom):
    """Box screwed to the front: sides the full length, a back between them, ХДФ bottom in the sides' grooves."""
    zb = zf - depth
    bw, bl = bottom
    cx = (x0 + x1) / 2
    return [
        P(ns[0], [x0, y0, zb, x0 + 16, y0 + h, zf], f"{ns[0]}-{tag}"),
        P(ns[1], [x1 - 16, y0, zb, x1, y0 + h, zf], f"{ns[1]}-{tag}"),
        P(ns[2], [x0 + 16, y0, zb, x1 - 16, y0 + h, zb + 16], f"{ns[2]}-{tag}"),
        P(ns[3], [cx - bw / 2, y0 + 8, zf - 2 - bl, cx + bw / 2, y0 + 11.5, zf - 2], f"{ns[3]}-{tag}", kind="back"),
    ]


def ids(parts):
    return [q.get("id", q.get("n")) for q in parts]


# ------------------------------------------------------------------------------------------ 1.02 тумба
def m102():
    W, D, H = 1300, 435, 782
    y0, y1 = LEG + 16, LEG + 16 + 628                # sides 138..766
    FZ0 = 419
    p = [
        P("4", [0, LEG, 0, W, y0, D], grain="x"),
        P("1", [0, y0, 0, 16, y1, 418]),
        P("2", [W - 16, y0, 0, W, y1, 418]),
        P("3", [0, y1, 0, W, H, D], grain="x"),
        P("5", [486, y0, 10, 502, y1, 412]),
        P("6", [798, y0, 10, 814, y1, 412]),
        # middle niche: a fixed shelf 7 and an upright 8 over it (Базальт, as the photos show)
        P("7", [503, 450, 10, 797, 466, 412], mat=BASALT),
        P("8", [614, 466, 10, 630, 764, 412], mat=BASALT),
        P("9", [815, 450, 12, 1283, 466, 404]),        # loose shelf behind the door
        P("14", [10, 133, 6, 492, 771, 9.5], "14-1", kind="back"),
        P("15", [496, 133, 6, 804, 771, 9.5], kind="back", mat=PEARL),
        P("14", [808, 133, 6, 1290, 771, 9.5], "14-2", kind="back"),
    ]
    moves = []
    # drawers: top pearl (the odd one, 12.1), two basalt (11.1)
    for tag, n, mat, fy0 in (("top", "12.1", PEARL, 558), ("mid", "11.1", BASALT, 349), ("low", "11.1", BASALT, 140)):
        fid = f"{n}-{tag}"
        fr = P(n, [1, fy0, FZ0, 501, fy0 + 206, D], fid, kind="front", mat=mat, grain="x")
        box = drawer(tag, ("11.2", "11.3", "11.4", "11.5"), 29, 473, fy0 + 15, 176, FZ0, 350, (422, 345))
        h = knob(f"k-{tag}", 251, fy0 + 206 - 60, D)
        p += [fr] + box + [h]
        moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": ids([fr] + box + [h]), "travel": 300})
    p += [P("10", [799, y0 + 2, FZ0, 1299, y1 - 2, D], kind="front", mat=PEARL, grain="y"),
          knob("k-door", 862, y1 - 2 - 60, D)]
    moves.append({"type": "door", "name": "door", "parts": ["10", "k-door"], "hinge": "right", "angle": 105})
    p += leg("1", 55, 50, -14) + leg("2", W - 55, 50, 14) + leg("3", 55, D - 50, -14) + leg("4", W - 55, D - 50, 14)
    p += leg("5", 436, D / 2) + leg("6", 864, D / 2)
    return dump("vena-1-02", [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------ 1.01 шкаф для одежды 2Д
def m101():
    W, D, H = 1008, 590, 2234
    y0, y1 = LEG + 16, LEG + 16 + 2080                # sides 138..2218
    FZ0 = 574
    p = [
        P("4", [0, LEG, 0, W, y0, D], grain="x"),
        P("1", [0, y0, 0, 16, y1, 573]),
        P("2", [W - 16, y0, 0, W, y1, 573]),
        P("3", [0, y1, 0, W, H, D], grain="x"),
        P("5", [496, y0, 10, 512, y1, 567]),
        # left column: fixed shelves 7 (bottom) and 6 (top), three loose shelves 8
        P("7", [16.5, 477, 10, 495.5, 493, 567], "7-1"),
        P("8", [17.5, 820, 12, 494.5, 836, 559], "8-1"),
        P("8", [17.5, 1167, 12, 494.5, 1183, 559], "8-2"),
        P("8", [17.5, 1514, 12, 494.5, 1530, 559], "8-3"),
        P("6", [16.5, 1861, 10, 495.5, 1877, 567]),
        # right column: fixed shelf 7 over the drawers, the hanging space, shelf 6.1 under the mezzanine
        P("7", [512.5, 757, 10, 991.5, 773, 567], "7-2"),
        P("6.1", [512.5, 1861, 10, 991.5, 1877, 567]),
        {"id": "w", "kind": "tube", "mat": "chrome", "box": [516, 1805, 280, 988, 1825, 300], "covers": ["w"]},
        P("15", [10, 134, 6, 501, 485, 9.5], kind="back"),
        P("14", [10, 485, 6, 501, 1869, 9.5], kind="back"),
        P("17", [507, 134, 6, 998, 765, 9.5], kind="back"),
        P("16", [507, 765, 6, 998, 1868, 9.5], kind="back"),
        P("18", [12, 1869, 6, 996, 2220, 9.5], kind="back"),
    ]
    moves = []
    for tag, n, mat, fy0 in (("top", "11.1", BASALT, 558), ("mid", "12.1", PEARL, 349), ("low", "11.1", BASALT, 140)):
        fid = f"{n}-{tag}"
        fr = P(n, [505.5, fy0, FZ0, 1005.5, fy0 + 206, D], fid, kind="front", mat=mat, grain="x")
        box = drawer(tag, ("11.2", "11.3", "11.4", "11.5"), 529.5, 982.5, fy0 + 15, 176, FZ0, 500, (431, 495))
        h = knob(f"k-{tag}", 755.5, fy0 + 206 - 60, D)
        p += [fr] + box + [h]
        moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": ids([fr] + box + [h]), "travel": 420})
    p += [P("9", [2.5, 140, FZ0, 502.5, 2216, D], kind="front", mat=BASALT, grain="y"),
          knob("k-9", 437, 1198, D),
          P("10", [505.5, 767, FZ0, 1005.5, 2216, D], kind="front", mat=PEARL, grain="y"),
          knob("k-10", 568, 1198, D)]
    moves += [{"type": "door", "name": "door_left", "parts": ["9", "k-9"], "hinge": "left", "angle": 105},
              {"type": "door", "name": "door_right", "parts": ["10", "k-10"], "hinge": "right", "angle": 105}]
    p += leg("1", 55, 55, -14) + leg("2", W - 55, 55, 14) + leg("3", 55, D - 55, -14) + leg("4", W - 55, D - 55, 14)
    return dump("vena-1-01", [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------ 2.04 шкаф комбинированный
def m204():
    W, D, H = 900, 435, 2234
    y0, y1 = LEG + 16, LEG + 16 + 2080
    FZ0 = 419
    p = [
        P("4", [0, LEG, 0, W, y0, D], grain="x"),
        P("1", [0, y0, 0, 16, y1, 418]),
        P("2", [W - 16, y0, 0, W, y1, 418]),
        P("3", [0, y1, 0, W, H, D], grain="x"),
        P("5", [442, y0, 0, 458, y1, 418]),               # full depth: the right column is open, without a back
        # left (closed) column: fixed shelves 6 at the door joints, loose shelves 8, backs 13 / 12 / 11
        P("6", [16.5, 820, 10, 441.5, 836, 412], "6-1"),
        P("6", [16.5, 1498, 10, 441.5, 1514, 412], "6-2"),
        P("8", [17.5, 471, 12, 440.5, 487, 404], "8-1"),
        P("8", [17.5, 1159, 12, 440.5, 1175, 404], "8-2"),
        P("8", [17.5, 1832, 12, 440.5, 1848, 404], "8-3"),
        P("13", [11.5, 137, 6, 446.5, 828, 9.5], kind="back", mat=PEARL),
        P("12", [11.5, 828, 6, 446.5, 1506, 9.5], kind="back", mat=PEARL),
        P("11", [11.5, 1506, 6, 446.5, 2222, 9.5], kind="back", mat=PEARL),
    ]
    # right (open) column: four fixed shelves 7, five equal openings
    for k in range(4):
        yy = y0 + 403.2 * (k + 1) + 16 * k
        p.append(P("7", [458.5, yy, 1, 883.5, yy + 16, 417], f"7-{k + 1}"))
    p += [P("10", [1.5, 140, FZ0, 454.5, 836, D], kind="front", mat=BASALT, grain="y"),
          knob("k-10", 404, 771, D),
          P("9", [1.5, 1496, FZ0, 454.5, 2216, D], kind="front", mat=PEARL, grain="y"),
          knob("k-9", 404, 1543, D)]
    moves = [{"type": "door", "name": "door_low", "parts": ["10", "k-10"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_up", "parts": ["9", "k-9"], "hinge": "left", "angle": 105}]
    p += leg("1", 55, 50, -14) + leg("2", W - 55, 50, 14) + leg("3", 55, D - 50, -14) + leg("4", W - 55, D - 50, 14)
    return dump("vena-2-04", [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------ 2.06 полка
def m206():
    W, D, H = 1300, 260, 340
    p = [
        P("2", [0, 0, 0, W, 16, D], grain="x"),
        P("1", [1, 16, 0, 1299, 324, 16], mat=PEARL, grain="x"),     # back board (ЛДСП 16) standing on the bottom
        P("5", [0, 16, 16, 16, 324, D]),
        P("4", [342, 16, 16, 358, 324, D], "4-1"),
        P("4", [684, 16, 16, 700, 324, D], "4-2"),
        P("6", [1284, 16, 16, 1300, 324, D]),
        P("3", [0, 324, 0, 700, 340, D], grain="x"),
    ]
    return dump("vena-2-06", [W, D, H], p, [])


# ------------------------------------------------------------------------------------------ 2.03-01 стол письменный
def m203():
    W, D, H = 1300, 650, 782
    y0, y1 = LEG + 16, LEG + 16 + 628                # pedestal sides 138..766
    FZ0, FZ1 = 628, 644
    p = [
        P("5", [0, LEG, 0, 504, y0, 644], grain="x"),
        P("1", [0, y0, 0, 16, y1, 627]),
        P("2", [488, y0, 0, 504, y1, 627]),
        P("6", [17, y0, 0, 487, y1, 16]),                              # the pedestal's back (ЛДСП 16)
        P("4", [0, y1, 0, W, H, D], grain="x"),
        P("3", [1284, 7, 3, 1300, y1, 647]),                           # the right leg panel on glides «o»
        P("7", [504, 446, 0, 1284, y1, 16], grain="x"),                # modesty panel
    ]
    for k, z in enumerate((40, 325, 610)):
        p.append({"id": f"o-{k + 1}", "kind": "panel", "mat": "black", "shape": "circle", "edge": 0.5,
                  "box": [1282, 0, z - 9, 1300, 7, z + 9], "covers": ["o"]})
    moves = []
    for tag, n, mat, fy0 in (("top", "8.1", BASALT, 558), ("mid", "9.1", PEARL, 349), ("low", "8.1", BASALT, 140)):
        fid = f"{n}-{tag}"
        fr = P(n, [2, fy0, FZ0, 502, fy0 + 206, FZ1], fid, kind="front", mat=mat, grain="x")
        box = drawer(tag, ("8.2", "8.3", "8.4", "8.5"), 30, 474, fy0 + 15, 176, FZ0, 500, (422, 495))
        h = knob(f"k-{tag}", 252, fy0 + 206 - 60, FZ1)
        p += [fr] + box + [h]
        moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": ids([fr] + box + [h]), "travel": 420})
    p += leg("1", 62, 50, -14) + leg("2", 442, 50, 14) + leg("3", 62, 594, -14) + leg("4", 442, 594, 14)
    return dump("vena-2-03-01", [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------ 1.05 кровать 1-09
def m105():
    """A day bed along the wall: its front is the long side (drawers), so x = the length 2042, z = the width 940."""
    W, D, H = 2042, 940, 720
    side = ("M 0 4 L 940 4 L 940 500 C 940 650 880 720 730 720 L 30 720 Q 0 720 0 690 Z")
    p = [
        P("3", [0, 4, 0, 16, H, D], shape="path", outline=side, grain="y"),
        P("4", [W - 16, 4, 0, W, H, D], shape="path", outline=side, grain="y"),
        P("2", [16, 54, 0, 2026, H, 16], grain="x"),                   # the back rest along the wall
        P("5", [16, 4, 444, 2026, 304, 460], grain="x"),               # the spine under the base
        P("9", [678, 4, 16, 694, 304, 444], "9-1"),
        P("9", [1348, 4, 16, 1364, 304, 444], "9-2"),
        P("7", [678, 4, 460, 694, 304, 923], "7-1"),
        P("7", [1348, 4, 460, 1364, 304, 923], "7-2"),
        P("1", [16, 304, 16, 2026, 320, 923], mat="door_enamel_whitey#d9d4cc", grain="x"),   # base (colour may vary)
        P("6", [16, 304, 924, 2026, 432, D], grain="x"),               # front rail over the drawers
        {"id": "mattress", "kind": "mattress", "box": [21, 320, 20, 2021, 480, 920]},
    ]
    k = 0
    glides = [(8, 60), (8, 880), (2034, 60), (2034, 880)]
    glides += [(686, 30), (686, 430), (1356, 30), (1356, 430), (686, 480), (686, 905), (1356, 480), (1356, 905)]
    glides += [(x, 452) for x in (40, 290, 540, 900, 1100, 1250, 1600, 1800, 2000)]
    for x, z in glides:
        k += 1
        p.append({"id": f"h-{k}", "kind": "panel", "mat": "black", "shape": "circle", "edge": 0.5,
                  "box": [x - 7, 0, z - 7, x + 7, 4, z + 7], "covers": ["h"]})
    moves = []
    # drawers on castors: fronts 666 between the end panels, the middle one basalt (12.1) and 8 mm narrower inside
    spec = [("left", "10.1", PEARL, 19, 685, (16, 678), ("10.2", "10.3", "10.4", "10.5"), (614, 445)),
            ("mid", "12.1", BASALT, 688, 1354, (694, 1348), ("10.2", "10.3", "12.4", "12.5"), (606, 445)),
            ("right", "11.1", PEARL, 1357, 2023, (1364, 2026), ("10.2", "10.3", "10.4", "10.5"), (614, 445))]
    for tag, n, mat, x0, x1, op, ns, bot in spec:
        fr = P(n, [x0, 20, 924, x1, 302, D], kind="front", mat=mat, grain="x")
        c = (op[0] + op[1]) / 2
        bw = (604 if ns[2] == "10.4" else 596) + 32
        box = drawer(tag, ns, c - bw / 2, c + bw / 2, 45, 238, 924, 450, bot)
        h = knob(f"k-{tag}", (x0 + x1) / 2, 302 - 54, D)
        cast = []
        for j, (cx, cz) in enumerate(((c - bw / 2 + 30, 500), (c + bw / 2 - 30, 500), (c - bw / 2 + 30, 890), (c + bw / 2 - 30, 890))):
            cast.append({"id": f"o-{tag}-{j + 1}", "kind": "panel", "mat": "black", "edge": 3,
                         "box": [cx - 12, 0, cz - 20, cx + 12, 43, cz + 20], "covers": ["o"]})
        p += [fr] + box + [h] + cast
        moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": ids([fr] + box + [h] + cast), "travel": 400})
    return dump("vena-1-05", [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------ catalogue fragment
NOTE = ("Каталог «Корпусная мебель ч. II» 2025, с. 115 (PDF; разворот 226–227). Корпус ЛДСП 16 «Гикори Кингстон» "
        "(крышка и дно на всю ширину и глубину, боковины между ними), фасады ЛДСП 16 «Персидский жемчуг» и «Базальт» "
        "накладные на кромки боковин, перегородки и полки за задними стенками ХДФ в пазах, точёные деревянные ножки "
        "«Опора Вена» 122 мм и деревянные ручки-кнопки; кровать 1-09 — тахта с тремя ящиками на роликах.")
CATALOG = {
    "finishes": [
        {"id": "vena-zhemchug-bazalt", "name": "Персидский жемчуг / Базальт; каркас Гикори Кингстон",
         "body": "door_enamel_whitey#a1876f", "front": "door_enamel_whitey#dfe3e2", "back": "door_enamel_whitey#dfe3e2",
         "roles": {"accent": "door_enamel_whitey#4d4e49", "wood": "door_enamel_whitey#b39a7c"}, "swatch": "#dfe3e2"},
    ],
    "profiles": {},
    "collections": [
        {"id": "vena", "name": "Вена", "brand": "Пинскдрев", "finishes": ["vena-zhemchug-bazalt"], "metal": "chrome",
         "note": NOTE},
    ],
    "models": [
        {"id": "vena-1-01", "code": "П6.115.1.01", "name": "Шкаф для одежды 2Д «Вена»", "collection": "vena",
         "category": "kids", "size": [1008, 590, 2234], "is": "IS-P6-115-1-01-SHkaf-dlya-odejdyi-2D.pdf", "page": 115,
         "note": "по инструкции"},
        {"id": "vena-1-02", "code": "П6.115.1.02", "name": "Тумба «Вена»", "collection": "vena", "category": "kids",
         "size": [1300, 435, 782], "is": "IS-P6-115-1-02-Tumba.pdf", "page": 115, "note": "по инструкции"},
        {"id": "vena-1-05", "code": "П6.115.1.05", "name": "Кровать 1-09 «Вена»", "collection": "vena",
         "category": "kids", "size": [2042, 940, 720], "is": "IS-P6-115-1-05-Krovat-1-09.pdf", "page": 115,
         "note": "по инструкции; тахта вдоль стены: x — длина 2042, ящики с длинной стороны; сп. место 2000×900"},
        {"id": "vena-2-03-01", "code": "П6.115.2.03-01", "name": "Стол письменный «Вена»", "collection": "vena",
         "category": "kids", "size": [1300, 650, 782], "is": "IS-P6-115-2-03-01-Stol-pismennyiy.pdf", "page": 115,
         "note": "по инструкции; тумба с ящиками слева"},
        {"id": "vena-2-04", "code": "П6.115.2.04", "name": "Шкаф комбинированный «Вена»", "collection": "vena",
         "category": "kids", "size": [900, 435, 2234], "is": "IS-P6-115-2-04-SHkaf-kombinirovannyiy.pdf", "page": 115,
         "note": "по инструкции; правая секция — открытый стеллаж без задней стенки"},
        {"id": "vena-2-06", "code": "П6.115.2.06", "name": "Полка «Вена»", "collection": "vena", "category": "kids",
         "size": [1300, 260, 340], "is": "IS-P6-115-2-06-Polka.pdf", "page": 115, "mount": "wall",
         "note": "по инструкции; навесная"},
    ],
}


if __name__ == "__main__":
    for f in (m101, m102, m105, m203, m204, m206):
        print(f())
    with open(os.path.join(HERE, "vena_catalog.json"), "w") as fh:
        json.dump(CATALOG, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
