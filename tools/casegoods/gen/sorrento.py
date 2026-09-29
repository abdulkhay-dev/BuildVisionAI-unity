"""«Сорренто» (Пинскдрев, П6.949): bedroom — coupe wardrobe 3Д, chest, bedside table, mirror, bed 2-16. All five modules
by instruction (P6-949-1-0x, cut lists in reference/sorrento/cutlists; the bed's table corrected in gen/cutlists/).

Construction (from the instructions and the site's product photos):
  * carcass ЛДСП 16 «Дуб Бордо лайт»: top and bottom run the full width and depth (cabinets stand on 20 mm block feet
    «k16»), the sides stand between them. Backs ХДФ 3.5 nailed on the rear (inset 4.5–7.5 from the edges). The catalogue
    depth B is the top's depth = sides 365 + front 16 + 1 mm: the nailed back is drawn inside the carcass's rear 3.5 mm
    (the checker lets backs overlap) so that the extent equals B — the real piece is 3.5 mm deeper.
  * fronts ЛДСП 16 overlaid on the sides' front edges between top and bottom, 3 mm gaps; the small drawers are «Дуб
    Монастырский» (role accent), the rest Бордо лайт. Drawer boxes: two sides and a back ЛДСП 16 screwed to the front,
    ХДФ bottom in grooves, 13–14 mm runner gaps (350 runners).
  * handles: square satin-aluminium pulls ~44 × 44 (a plate bent off the face), top middle of each front.
  * coupe wardrobe: sides / top / bottom ЛДСП 25, recessed plinth, three sliding doors 672 × 2165 on a double track
    (outer doors on the rear track, the middle mirror door on the front track), aluminium edge profiles «j9».
Coordinates: x from the left, y up from the floor, z from the wall (back) to the front; mm.

    /private/tmp/claude-501/venv/bin/python tools/casegoods/gen/sorrento.py
"""
import json
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))


def P(n, box, pid=None, **kw):
    p = {"n": n} if n is not None else {}
    if pid:
        p["id"] = pid
    p.update(kw)
    p["box"] = [round(v, 2) for v in box]
    return p


def pull(pid, x, y, z, letter="k1"):
    """Square satin-aluminium pull (a 44 × 44 plate bent off the face on two square posts)."""
    return {"id": pid, "kind": "handle", "model": "bar", "mat": "metal", "at": [x, y], "dir": "right", "d": 44,
            "band": 44, "t": 3, "standoff": 8, "post": 12, "section": "square", "z": z, "covers": [letter]}


def foot(pid, x0, z0, w=60, d=40, h=20):
    return {"id": pid, "kind": "panel", "mat": "door_enamel_whitey#8f9194", "edge": 2,
            "box": [x0, 0, z0, x0 + w, h, z0 + d], "covers": ["k16"]}


def drawer(tag, ns, x0, x1, y0, h, zf, depth=350, bottom=None):
    """Box screwed to the front: sides (full length), a back between them, ХДФ bottom in the sides' grooves."""
    zb = zf - depth
    bw, bl = bottom
    cx = (x0 + x1) / 2
    return [
        P(ns[0], [x0, y0, zb, x0 + 16, y0 + h, zf], f"{ns[0]}-{tag}"),
        P(ns[1], [x1 - 16, y0, zb, x1, y0 + h, zf], f"{ns[1]}-{tag}"),
        P(ns[2], [x0 + 16, y0, zb, x1 - 16, y0 + h, zb + 16], f"{ns[2]}-{tag}"),
        P(ns[3], [cx - bw / 2, y0 + 8, zf - 3 - bl, cx + bw / 2, y0 + 11.5, zf - 3], f"{ns[3]}-{tag}", kind="back"),
    ]


def dmove(name, parts, travel=300):
    return {"type": "drawer", "name": name, "parts": [q if isinstance(q, str) else q.get("id", q.get("n")) for q in parts], "travel": travel}


# ------------------------------------------------------------------------------------------ 1.04 тумба прикроватная
def m104():
    W, D, H = 424, 382, 445
    p = [
        P("4", [0, 20, 0, W, 36, D]),                      # bottom (on the feet)
        P("1", [0, 36, 0, 16, 429, 365]),
        P("2", [W - 16, 36, 0, W, 429, 365]),
        P("3", [0, 429, 0, W, H, D]),                      # top
        P("5", [17, 289, 5, 407, 305, 365]),               # fixed shelf over the drawer
        P("7", [4.5, 26.5, 0, 419.5, 438.5, 3.5], kind="back"),
    ]
    p += [foot("k16-1", 40, 30), foot("k16-2", W - 100, 30), foot("k16-3", 40, 312), foot("k16-4", W - 100, 312)]
    fr = P("6.1", [3, 37.5, 366, 421, 287.5, D], kind="front", mat="accent", grain="x")
    box = drawer("d", ("6.2", "6.3", "6.4", "6.5"), 30, 394, 58, 191, 366, bottom=(342, 344))
    h = pull("k1", 212, 287.5 - 40, D)
    p += [fr] + box + [h]
    moves = [dmove("drawer", [fr] + box + [h])]
    return dump("sorrento-1-04", [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------ 1.02 комод
def m102():
    W, D, H = 1084, 385, 1228
    FZ0, FZ1 = 366, 382                                     # fronts (the top overhangs them by 3)
    p = [
        P("5", [0, 20, 0, W, 36, D]),
        P("1", [0, 36, 0, 16, 1212, 365]),
        P("2", [W - 16, 36, 0, W, 1212, 365]),
        P("4", [0, 1212, 0, W, H, D]),
        P("3", [704.5, 36, 0, 720.5, 1212, 360]),           # partition behind the joint of the fronts
        P("6", [722.25, 420, 5, 1066.25, 436, 360], "6-1"),
        P("6", [722.25, 812, 5, 1066.25, 828, 360], "6-2"),
        P("10", [7.5, 25, 0, 712.5, 1223, 3.5], kind="back"),
        P("11", [712.5, 25, 0, 1076.5, 1223, 3.5], kind="back"),
    ]
    p += [foot("k16-1", 40, 30), foot("k16-2", W - 100, 30), foot("k16-3", 40, 315), foot("k16-4", W - 100, 315),
          foot("k16-5", 682.5, 172)]
    moves = []
    fronts = [("9.1", "a", 38, 374, 250), ("9.1", "b", 377, 713, 250), ("9.1", "c", 716, 1052, 250), ("8.1", "d", 1055, 1210, 110)]
    for n, tag, y0, y1, bh in fronts:
        fid = f"{n}-{tag}"
        fr = P(n, [3, y0, FZ0, 711, y1, FZ1], fid, kind="front", grain="x", **({"mat": "accent"} if n == "8.1" else {}))
        pre = n.split(".")[0]
        yb = y0 + (22 if n == "8.1" else 40)
        box = drawer(tag, (f"{pre}.2", f"{pre}.3", f"{pre}.4", f"{pre}.5"), 29.25, 691.25, yb, bh, FZ0, bottom=(640, 344))
        h = pull(f"k1-{tag}", 357, y1 - 42, FZ1)
        p += [fr] + box + [h]
        moves.append(dmove(f"drawer_{tag}", [fr] + box + [h]))
    door = P("7", [714, 38, FZ0, 1081, 1210, FZ1], kind="front", grain="y")
    h = pull("k1-door", 762, 1168, FZ1)
    p += [door, h]
    moves.append({"type": "door", "name": "door", "parts": ["7", "k1-door"], "hinge": "right", "angle": 105})
    return dump("sorrento-1-02", [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------ 1.03 зеркало
def m103():
    p = [
        P("1", [0, 0, 0, 1000, 700, 16], grain="x"),
        P("2", [20, 20, 17, 980, 680, 21], kind="mirror", edge=0.5),   # glued on with 1 mm tape
    ]
    return dump("sorrento-1-03", [1000, 21, 700], p, [])


# ------------------------------------------------------------------------------------------ 1.05 кровать 2-16
def m105():
    W, L, H = 1664, 2060, 970
    p = [
        P("1", [0, 4, 0, W, 970, 25], grain="x"),                       # headboard on glides
        P("1.1", [0, 703, 25, W, 920, 41], kind="front", mat="accent", grain="x"),
        P("3", [0, 126, 25, 25, 326, 2035], grain="z"),
        P("3.1", [W - 25, 126, 25, W, 326, 2035], grain="z"),
        P("2", [0, 4, 2035, W, 326, L], grain="x"),                    # foot board
    ]
    k = 0
    for z0, z1 in ((0, 25), (2035, L)):
        for x in (60, W / 2, W - 60):
            k += 1
            p.append({"id": f"g-{k}", "kind": "panel", "mat": "black", "shape": "circle", "edge": 0.5,
                      "box": [x - 12, 0, (z0 + z1) / 2 - 12, x + 12, 4, (z0 + z1) / 2 + 12], "covers": ["g"]})
    # the metal base «m» 2000 × 1600 between the rails (black tubes, middle beam, slats, legs) and the mattress
    fx0, fx1, fz0, fz1, fy = 32, W - 32, 30, 2030, 230
    p += [
        {"id": "m-l", "kind": "panel", "mat": "black", "box": [fx0, fy, fz0, fx0 + 30, fy + 40, fz1], "covers": ["m"]},
        {"id": "m-r", "kind": "panel", "mat": "black", "box": [fx1 - 30, fy, fz0, fx1, fy + 40, fz1]},
        {"id": "m-h", "kind": "panel", "mat": "black", "box": [fx0 + 30, fy, fz0, fx1 - 30, fy + 40, fz0 + 30]},
        {"id": "m-f", "kind": "panel", "mat": "black", "box": [fx0 + 30, fy, fz1 - 30, fx1 - 30, fy + 40, fz1]},
        {"id": "m-c", "kind": "panel", "mat": "black", "box": [W / 2 - 15, fy, fz0 + 30, W / 2 + 15, fy + 40, fz1 - 30]},
    ]
    for i, z in enumerate((700, 1360)):
        p.append({"id": f"m-leg{i + 1}", "kind": "tube", "mat": "black", "box": [W / 2 - 12, 4, z, W / 2 + 12, fy, z + 24]})
        p.append({"id": f"m-glide{i + 1}", "kind": "panel", "mat": "black", "shape": "circle", "box": [W / 2 - 15, 0, z - 3, W / 2 + 15, 4, z + 27]})
    for i in range(24):
        z = fz0 + 45 + i * 81.5
        p.append({"id": f"m-slat-l{i + 1}", "kind": "panel", "mat": "door_enamel_whitey#c9a877",
                  "box": [fx0 + 30, fy + 40, z, W / 2 - 15, fy + 48, z + 53]})
        p.append({"id": f"m-slat-r{i + 1}", "kind": "panel", "mat": "door_enamel_whitey#c9a877",
                  "box": [W / 2 + 15, fy + 40, z, fx1 - 30, fy + 48, z + 53]})
    p.append({"id": "mattress", "kind": "mattress", "box": [W / 2 - 800, fy + 48, 30, W / 2 + 800, fy + 248, 2030]})
    return dump("sorrento-1-05", [W, L, H], p, [])


# ------------------------------------------------------------------------------------------ 1.01 шкаф-купе 3Д
def m101():
    W, D, H = 2000, 650, 2300
    p = [
        P("1", [0, 4, 0, 25, 2275, D], grain="y"),
        P("2", [W - 25, 4, 0, W, 2275, D], grain="y"),
        P("6", [0, 2275, 0, W, H, D], grain="x"),
        P("12", [26, 4, 620, 1974, 69, 636], "12-1", grain="x"),       # plinth, front (recessed 14)
        P("12", [26, 4, 5, 1974, 69, 21], "12-2", grain="x"),          # plinth, back
        P("7", [26, 69, 5, 1974, 94, D], grain="x"),                   # bottom 25
        P("3", [1313.5, 94, 5, 1329.5, 1908, 549]),
        P("4", [670.5, 94, 5, 686.5, 1908, 549]),
        P("8", [26, 1908, 5, 1974, 1924, 549], grain="x"),              # hat shelf over the whole width
        P("5", [992, 1924, 5, 1008, 2275, 549]),                         # upright of the mezzanine
        P("11", [26, 2195, 634, 1974, 2275, D], grain="x"),              # front rail hiding the top track
        # middle column: shelves 626 (9) and 624 (10) alternating, the scheme's 5 compartments
        P("10", [688, 444, 5, 1312, 460, 549], "10-1"),
        P("9", [687, 810, 5, 1313, 826, 549], "9-1"),
        P("10", [688, 1176, 5, 1312, 1192, 549], "10-2"),
        P("9", [687, 1542, 5, 1313, 1558, 549], "9-2"),
        # backs ХДФ in the 25 mm sides' grooves (8 mm deep), passing behind the bottom / hat shelf; joints on the partitions
        P("17", [8, 61, 1.5, 680, 1908, 5], "17-1", kind="back"),
        P("18", [680, 61, 1.5, 1320, 1908, 5], kind="back"),
        P("17", [1320, 61, 1.5, 1992, 1908, 5], "17-2", kind="back"),
        P("16", [8, 1908, 1.5, 1000, 2285, 5], "16-1", kind="back"),
        P("16", [1000, 1908, 1.5, 1992, 2285, 5], "16-2", kind="back"),
        {"id": "w1-1", "kind": "tube", "mat": "chrome", "box": [30, 1858, 262, 666, 1883, 287], "covers": ["w1"]},
        {"id": "w1-2", "kind": "tube", "mat": "chrome", "box": [1334, 1858, 262, 1970, 1883, 287], "covers": ["w1"]},
        {"id": "F6-bottom", "kind": "panel", "mat": "chrome", "edge": 0.5, "box": [26, 94, 560, 1974, 98, 632], "covers": ["F6", "F6"]},
        {"id": "F6-top", "kind": "panel", "mat": "chrome", "edge": 0.5, "box": [26, 2269, 560, 1974, 2275, 632], "covers": ["F6", "F6"]},
    ]
    k = 0
    for x in (12.5, W - 12.5):
        for z in (40, 325, 610):
            k += 1
            p.append({"id": f"n-{k}", "kind": "panel", "mat": "black", "shape": "circle", "box": [x - 10, 0, z - 10, x + 10, 4, z + 10], "covers": ["n"]})
    for x in (300, 1000, 1700):
        for z in (13, 628):
            k += 1
            p.append({"id": f"n-{k}", "kind": "panel", "mat": "black", "shape": "circle", "box": [x - 8, 0, z - 8, x + 8, 4, z + 8], "covers": ["n"]})
    y0, y1 = 100, 2265
    # outer doors on the rear track, the middle mirror door on the front track; aluminium edge profiles «j9» (face strips)
    p += [
        P("13", [25, y0, 572, 697, y1, 588], kind="front", grain="y"),
        {"id": "j9-1", "kind": "panel", "mat": "metal", "edge": 1, "box": [25, y0, 588, 45, y1, 592], "covers": ["j9"]},
        P("15", [1303, y0, 572, 1975, y1, 588], kind="front", grain="y"),
        {"id": "j9-4", "kind": "panel", "mat": "metal", "edge": 1, "box": [1955, y0, 588, 1975, y1, 592], "covers": ["j9"]},
        P("14", [664, y0, 600, 1336, y1, 616], kind="front", grain="y"),
        {"id": "j9-2", "kind": "panel", "mat": "metal", "edge": 1, "box": [664, y0, 616, 684, y1, 620], "covers": ["j9"]},
        {"id": "j9-3", "kind": "panel", "mat": "metal", "edge": 1, "box": [1316, y0, 616, 1336, y1, 620], "covers": ["j9"]},
        # the middle door: two mirror panes with a «Монастырский» insert between them (supplied glued on the leaf)
        {"id": "mirror-lo", "kind": "mirror", "edge": 0.5, "box": [760, y0 + 67, 616, 1240, y0 + 797, 620]},
        {"id": "insert", "kind": "panel", "mat": "accent", "edge": 0.5, "grain": "x", "box": [760, y0 + 797, 616, 1240, y0 + 1043, 620]},
        {"id": "mirror-hi", "kind": "mirror", "edge": 0.5, "box": [760, y0 + 1043, 616, 1240, y1 - 67, 620]},
    ]
    moves = [
        {"type": "slide", "name": "door_left", "parts": ["13", "j9-1"], "by": [639, 0, 0]},
        {"type": "slide", "name": "door_middle", "parts": ["14", "j9-2", "j9-3", "mirror-lo", "insert", "mirror-hi"], "by": [-639, 0, 0]},
        {"type": "slide", "name": "door_right", "parts": ["15", "j9-4"], "by": [-639, 0, 0]},
    ]
    return dump("sorrento-1-01", [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------ catalogue fragment
NOTE = ("Каталог «Корпусная мебель ч. II» 2025, с. 113 (PDF; разворот 222–223). Корпус ЛДСП 16 «Дуб Бордо лайт 380» "
        "(крышка и дно на всю ширину и глубину, боковины между ними, блок-опоры 20 мм), задние стенки ХДФ 3,5 на гвоздях, "
        "фасады ЛДСП 16 накладные с зазорами 3 мм, малые ящики «Дуб Монастырский 375», квадратные ручки-скобы "
        "сатин-алюминий; шкаф-купе на ЛДСП 25 с цоколем, три двери-купе 672 на двойной направляющей, средняя с зеркалом "
        "и вставкой «Монастырский»; кровать с металлокаркасом.")
CATALOG = {
    "finishes": [
        {"id": "sorrento-bordo-monastyr", "name": "Дуб Бордо лайт 380 / Дуб Монастырский 375",
         "body": "door_enamel_whitey#e7e7e1", "front": "door_enamel_whitey#e7e7e1",
         "roles": {"accent": "door_enamel_whitey#5c4c44"}, "swatch": "#e7e7e1"},
    ],
    "profiles": {},
    "collections": [
        {"id": "sorrento", "name": "Сорренто", "brand": "Пинскдрев", "finishes": ["sorrento-bordo-monastyr"],
         "metal": "chrome", "note": NOTE},
    ],
    "models": [
        {"id": "sorrento-1-01", "code": "П6.949.1.01", "name": "Шкаф-купе 3Д «Сорренто»", "collection": "sorrento",
         "category": "bedroom", "size": [2000, 650, 2300], "is": "P6-949-1-01-SHkaf-kupe-3D-1.pdf", "page": 113,
         "note": "по инструкции; три двери-купе, средняя — зеркало со вставкой «Монастырский»"},
        {"id": "sorrento-1-02", "code": "П6.949.1.02", "name": "Комод «Сорренто»", "collection": "sorrento",
         "category": "bedroom", "size": [1084, 385, 1228], "is": "P6-949-1-02-Komod-1.pdf", "page": 113,
         "note": "по инструкции; дверь на правых петлях"},
        {"id": "sorrento-1-03", "code": "П6.949.1.03", "name": "Зеркало «Сорренто»", "collection": "sorrento",
         "category": "decor", "size": [1000, 21, 700], "is": "P6-949-1-03-Zerkalo-1.pdf", "page": 113, "mount": "wall",
         "note": "по инструкции; вешается горизонтально"},
        {"id": "sorrento-1-04", "code": "П6.949.1.04", "name": "Тумба прикроватная «Сорренто»", "collection": "sorrento",
         "category": "bedroom", "size": [424, 382, 445], "is": "P6-949-1-04-Tumba-prikrovatnaya-2.pdf", "page": 113,
         "note": "по инструкции"},
        {"id": "sorrento-1-05", "code": "П6.949.1.05", "name": "Кровать 2-16 «Сорренто»", "collection": "sorrento",
         "category": "bedroom", "size": [1664, 2060, 970], "is": "P6-949-1-05-Krovat-2-16-1.pdf", "page": 113,
         "note": "по инструкции; сп. место 2000×1600, металлокаркас; каталог L2060×B1664 (L — длина)"},
    ],
}


if __name__ == "__main__":
    for f in (m101, m102, m103, m104, m105):
        print(f())
    with open(os.path.join(HERE, "sorrento_catalog.json"), "w") as fh:
        json.dump(CATALOG, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
