"""«Линель» (П6.934, kids' room, «Белый»; the bed «Молоко / Белый»): all 6 modules by instruction.

Carcass ЛДСП 16: the sides stand on nail-in glides «Опора ФБ 482» (4 mm), the top 16 lies over them (1 mm proud of the
sides on the chest), the bottom 16 sits between the sides on two plinth rails 90 (front one flush with the fronts);
fixed shelves 562 / 432 deep, backs ХДФ 3 / 3.5 in grooves 8 mm from the back edge, joined at the fixed shelves. Fronts
ЛДСП 16 INSET, flush with the carcass front: 2 mm off the sides, 2–4 mm gaps. No handles: grips milled into the fronts —
a lens cut into the meeting edges of the doors, a shallow arched notch in the top edge of the drawer fronts (photos).
Drawer boxes ЛДСП 16, the ХДФ bottom in grooves (5 mm into the front).

The bed П6.934.5.01 (Pinsk factory, its own table): a daybed along the wall — two end panels 25 with a cove strip and a
cap 60 × 18, a back panel with its cap, 14 slats on a strip; under it a trundle on castors (front rail with an arched
dip, back 1994, ends and middle 273) carrying 15 slats and two drawers with milled-frame fronts.

    python3 tools/casegoods/gen/linel.py
"""
from kit_w4k import (P, H, back, front, bar, drawer_box, dmove, door, ids, glides, write_cutlist, write_fragment,
                     notch_top, notch_side, dump)

SLUG = "linel"
ZF = 16.0  # front thickness


def grip_door(x0, y0, x1, y1, side, cy, h=420, dep=15):
    return {"shape": "path", "outline": notch_side(x0, y0, x1, y1, side, cy, h, dep)}


def grip_drawer(x0, y0, x1, y1, w, dep=16):
    return {"shape": "path", "outline": notch_top(x0, y0, x1, y1, (x0 + x1) / 2, w, dep)}


# ------------------------------------------------------------------------------------------ 1.01 шкаф 2Д
def m101():
    W, B = 865, 580
    zf0 = B - ZF
    p = [
        P(1, (1, 4, 0, 17, 2093, B)), P(2, (848, 4, 0, 864, 2093, B)), P(3, (0, 2093, 0, 865, 2109, B)),
        P(13, (17, 4, zf0, 848, 94, B), "13-f"), P(13, (17, 4, 30, 848, 94, 46), "13-b"),
        P(4, (17, 94, 0, 848, 110, B)),
        P(7, (17, 314, 0, 848, 330, 562)), P(6, (17, 534, 0, 848, 550, 562)),
        P(8, (17, 1757, 16, 848, 1773, 562)),
        P(9, (423.5, 550, 26, 439.5, 1757, 562)),
    ]
    for i, y in enumerate((834, 1140, 1422)):
        p.append(P(5, (17.5, y, 31, 423, y + 16, 562), f"5-{i + 1}"))
    p += [back(16, (12, 103, 8, 853, 539, 11.5)), back(15, (12, 543, 8, 431.5, 1764, 11.5), "15-l"),
          back(15, (433.5, 543, 8, 853, 1764, 11.5), "15-r"), back(14, (12, 1766, 8, 853, 2098, 11.5))]
    p.append(H("r", (443.5, 1700, 280, 843.5, 1725, 295), "r", kind="tube", mat="chrome"))
    # doors with grips at the meeting edges
    d1 = front(10, (19, 552, zf0, 431.5, 2091, B), **grip_door(19, 552, 431.5, 2091, "r", 1180, 440))
    d2 = front(11, (433.5, 552, zf0, 846, 2091, B), **grip_door(433.5, 552, 846, 2091, "l", 1180, 440))
    p += [d1, d2]
    moves = [door("door_left", ["10"], "left"), door("door_right", ["11"], "right")]
    for k, (y0, y1) in enumerate(((112, 312), (332, 532))):
        f = front("12.1", (19, y0, zf0, 846, y1, B), f"12.1-{k + 1}", **grip_drawer(19, y0, 846, y1, 380))
        bx = drawer_box(k + 1, ("12.2", "12.3", "12.4", "12.5"), 29.5, 835.5, y0 + 20, 160, zf0 - 500, zf0,
                        bottom=(784, 505, 3))
        p += [f] + bx
        moves.append(dmove(f"drawer_{k + 1}", [f["id"]] + ids(bx), 380))
    p += glides((9, 856), (30, 200, 380, 550), 4, d=14) + glides((432.5,), (30, 550), 4, d=14, tag="gm")
    return dump("linel-1-01", [865, 580, 2109], p, moves)


# ------------------------------------------------------------------------------------------ 1.02 стол
def m102():
    B = 580
    zf0 = 534
    p = [
        P(1, (3, 4, 0, 19, 743, 550)), P(3, (524, 4, 0, 540, 743, 550)), P(2, (1181, 4, 0, 1197, 743, 550)),
        P(4, (0, 743, 0, 1200, 759, B)),
        P(6, (19, 4, zf0, 524, 94, 550)), P(5, (19, 94, 0, 524, 110, 550)), P(7, (19, 110, 0, 524, 743, 16)),
        P(8, (540, 423, 0, 1181, 743, 16)),
    ]
    moves = []
    for k, (y0, y1) in enumerate(((112, 319), (322, 529), (532, 739))):
        f = front("9.1", (21, y0, zf0, 522, y1, 550), f"9.1-{k + 1}", **grip_drawer(21, y0, 522, y1, 300))
        bx = drawer_box(k + 1, ("9.2", "9.3", "9.4", "9.5"), 31.5, 511.5, y0 + 20, 160, zf0 - 500, zf0,
                        bottom=(458, 505, 3))
        p += [f] + bx
        moves.append(dmove(f"drawer_{k + 1}", [f["id"]] + ids(bx), 380))
    p += glides((11, 532, 1189), (40, 275, 510), 4, d=14) + glides((271.5,), (542,), 4, d=14, letter="k", tag="gp")
    for q in p:
        if q.get("covers") == ["s"]:
            q["covers"] = ["k"]
    return dump("linel-1-02", [1200, 580, 759], p, moves)


# ------------------------------------------------------------------------------------------ 1.03 стеллаж
def m103():
    B = 450
    zf0 = B - ZF
    p = [
        P(1, (1, 4, 0, 17, 2093, B)), P(2, (538, 4, 0, 554, 2093, B)), P(3, (0, 2093, 0, 555, 2109, B)),
        P(9, (17, 4, zf0, 538, 94, B), "9-f"), P(9, (17, 4, 30, 538, 94, 46), "9-b"),
        P(4, (17, 94, 0, 538, 110, B)),
        P("5.1", (17, 420, 0, 538, 436, 432)), P(5, (17, 626, 0, 538, 642, 432)),
        back(11, (12, 105, 8, 543, 633.5, 11)),
        back(10, (12, 636, 2, 543, 2099.5, 18), mat="body"),
    ]
    for i, y in enumerate((992.8, 1359.5, 1726.3)):
        p.append(P(6, (18, y, 26, 537, y + 16, 448), f"6-{i + 1}"))
    d = front(7, (19, 112, zf0, 536, 418, B), **grip_drawer(19, 112, 536, 418, 240))
    f = front("8.1", (19, 438, zf0, 536, 624, B), **grip_drawer(19, 438, 536, 624, 240))
    bx = drawer_box(1, ("8.2", "8.3", "8.4", "8.5"), 29.5, 525.5, 458, 146, zf0 - 400, zf0, hb=132,
                    bottom=(474, 405, 3))
    p += [d, f] + bx
    moves = [door("door", ["7"], "left"), dmove("drawer", ["8.1"] + ids(bx), 300)]
    p += glides((9, 546), (30, 225, 420), 4, d=14)
    return dump("linel-1-03", [555, 450, 2109], p, moves)


# ------------------------------------------------------------------------------------------ 1.04 комод
def m104():
    B = 450
    zf0 = B - ZF
    p = [
        P(1, (1, 4, 0, 17, 898, B)), P(2, (850, 4, 0, 866, 898, B)), P(3, (0, 898, 0, 867, 914, B)),
        P(8, (17, 4, zf0, 850, 94, B), "8-f"), P(8, (17, 4, 30, 850, 94, 46), "8-b"),
        P(4, (17, 94, 0, 850, 110, B)),
        P(6, (425.5, 110, 26, 441.5, 718, 432)),
        P(7, (18, 396, 30, 424.5, 412, 430), "7-l"), P(7, (442.5, 396, 30, 849, 412, 430), "7-r"),
        P(5, (17, 718, 0, 850, 734, 432)),
        back(12, (12, 104, 8, 432.5, 724, 11), "12-l"), back(12, (434.5, 104, 8, 855, 724, 11), "12-r"),
        back(13, (12, 728, 8, 855, 904, 11)),
    ]
    d1 = front(9, (19, 112, zf0, 431.5, 716, B), **grip_door(19, 112, 431.5, 716, "r", 462, 380))
    d2 = front("9.1", (435.5, 112, zf0, 848, 716, B), **grip_door(435.5, 112, 848, 716, "l", 462, 380))
    f = front("11.1", (19, 736, zf0, 848, 896, B), **grip_drawer(19, 736, 848, 896, 330))
    bx = drawer_box(1, ("11.2", "11.3", "11.4", "11.5"), 29.5, 837.5, 754, 120, zf0 - 400, zf0, hb=106,
                    bottom=(786, 405, 3))
    p += [d1, d2, f] + bx
    moves = [door("door_left", ["9"], "left"), door("door_right", ["9.1"], "right"),
             dmove("drawer", ["11.1"] + ids(bx), 300)]
    g = glides((9, 858), (30, 160, 290, 420), 4, d=14)
    for q in g:
        q["covers"] = ["i"]
    p += g
    return dump("linel-1-04", [867, 450, 914], p, moves)


# ------------------------------------------------------------------------------------------ 1.05 полка
def m105():
    p = [P(1, (0, 0, 0, 1100, 250, 16)), P(2, (24, 0, 16, 1076, 16, 216))]
    return dump("linel-1-05", [1100, 216, 250], p, [])


# ------------------------------------------------------------------------------------------ 5.01 кровать раздвижная
def m501():
    p = []
    # upper bed: end panels 25, cove strips 23 × 23 outside under the caps, caps 60 × 18
    p += [P("1.1", (32, 0, 21, 57, 745, 986)), P("1.2", (2057, 0, 21, 2082, 745, 986)),
          P(3, (9, 722, 21, 32, 745, 986), "3-l", edge=6), P(3, (2082, 722, 21, 2105, 745, 986), "3-r", edge=6),
          P(2, (0, 745, 0, 60, 763, 1007), edge=3), P(4, (2054, 745, 0, 2114, 763, 1007), edge=3),
          P(5, (57, 230, 21, 2057, 745, 39)), P(6, (60, 745, 0, 2054, 763, 60), edge=3),
          P(22, (57, 450, 950, 2057, 470, 955), mat="white")]
    pitch = 2000 / 14
    for i in range(14):
        cx = 57 + pitch / 2 + i * pitch
        p.append(P(18, (cx - 26.5, 470, 45, cx + 26.5, 482, 970), f"18-{i + 1}", mat="birch"))
    p.append(P(21, (150, 451, 45, 233, 470, 95), mat="birch"))
    p.append({"id": "mattress-up", "kind": "mattress", "box": [57, 482, 45, 2057, 662, 945]})
    # the trundle (moves out to the front): back 15 behind the ends, the front rail 9 in front of them
    t = []
    t += [P(15, (60, 15, 65, 2054, 288, 83)),
          P(11, (79, 15, 83, 97, 288, 967)), P(13, (2017, 15, 83, 2035, 288, 967)),
          P(12, (1048, 15, 83, 1066, 288, 967), shape="path",
            outline="M 101 15 L 967 15 L 967 288 L 83 288 L 83 95 L 101 95 Z"),
          P(14, (97, 15, 83, 2017, 95, 101)),
          P(9, (60.5, 262, 967, 2053.5, 422, 986), shape="path",
            outline=notch_top(60.5, 262, 2053.5, 422, 1057, 620, 62, 300)),
          P(20, (300, 100, 83, 370, 120, 103), "20-1", mat="white"), P(20, (1700, 100, 83, 1770, 120, 103), "20-2", mat="white")]
    pitch = 1920 / 15
    for i in range(15):
        cx = 97 + pitch / 2 + i * pitch
        t.append(P(19, (cx - 26.5, 288, 66, cx + 26.5, 300, 966), f"19-{i + 1}", mat="birch"))
    t.append({"id": "mattress-low", "kind": "mattress", "box": [97, 300, 83, 2017, 420, 963]})
    k = 0
    for x in (88, 1057, 2026):
        for z in (160, 890):
            k += 1
            t.append(H(f"j-{k}", (x - 15, 0, z - 20, x + 15, 15, z + 20), "J", kind="tube", mat="black"))
    moves = []
    for (n, x0, x1, bx0, tag) in (("16", 60, 1055, 109.5, "l"), ("17", 1059, 2054, 1078.5, "r")):
        lines = [[x0 + 28, 58, x1 - 28, 58], [x0 + 28, 58, x0 + 28, 200], [x1 - 28, 58, x1 - 28, 200]]
        f = front(n, (x0, 30, 967, x1, 260, 986), shape="path",
                  outline=notch_top(x0, 30, x1, 260, (x0 + x1) / 2, 330, 34, 150),
                  face={"type": "grooves", "w": 5, "depth": 2, "flute": "u", "lines": lines})
        bx = drawer_box(tag, ("16.1", "16.2", "16.3", "16.4"), bx0, bx0 + 926, 45, 170, 467, 967, hb=170, t=18,
                        bottom=(900, 494, 3.5), under=True)
        t += [f] + bx
        moves.append(dmove(f"drawer_{tag}", [n] + ids(bx), 420))
    trundle = [q.get("id") or q["n"] for q in t]
    dr = set(sum((m["parts"] for m in moves), []))
    moves = [{"type": "slide", "name": "trundle", "parts": [i for i in trundle], "by": [0, 0, 850]}]
    p += t
    return dump("linel-5-01", [2114, 1007, 763], p, moves)


def cutlists():
    write_cutlist("linel-1-03", "П6.934.1.03", [
        ("1", 2089, 450, 16, 1, "Стенка боковая"), ("2", 2089, 450, 16, 1, "Стенка боковая"),
        ("3", 555, 450, 16, 1, "Крышка"), ("4", 521, 450, 16, 1, "Дно"), ("5", 521, 432, 16, 1, "Полка"),
        ("5.1", 521, 432, 16, 1, "Полка"), ("6", 519, 422, 16, 3, "Полка"), ("7", 306, 517, 16, 1, "Дверь"),
        ("8.1", 186, 517, 16, 1, "Фасад ящика"), ("8.2", 146, 400, 16, 1, "Бок ящика"),
        ("8.3", 146, 400, 16, 1, "Бок ящика"), ("8.4", 132, 464, 16, 1, "Задняя стенка ящика"),
        ("8.5", 474, 405, 3, 1, "Дно ящика (ХДФ)"), ("9", 90, 521, 16, 2, "Цоколь"),
        ("10", 1463.5, 531, 16, 1, "Задняя стенка"), ("11", 528.5, 531, 3, 1, "Задняя стенка (ХДФ)")],
        "IS-Linel-P6-934-1-03-Stellaj.pdf p. 4 (table picture + text layer)",
        "Row 10 (1463.5 × 531 × 16, the upper back) was lost from the text layer — added from the picture. Row 8.5 "
        "(the drawer bottom 474 × 405) is printed 16 thick: a misprint (it sits in the sides' grooves like every other "
        "Линель drawer bottom, 12.5 / 9.5 / 11.5 = 3) — written as 3.")
    write_cutlist("linel-5-01", "П6.934.5.01", [
        ("1.1", 965, 745, 25, 1, "Спинка"), ("1.2", 965, 745, 25, 1, "Спинка"), ("2", 60, 1007, 18, 1, "Накладка спинки"),
        ("3", 965, 23, 23, 2, "Брусок (карниз)"), ("4", 60, 1007, 18, 1, "Накладка спинки"),
        ("5", 2000, 515, 18, 1, "Стенка задняя"), ("6", 60, 1994, 18, 1, "Накладка задней стенки"),
        ("9", 1993, 160, 19, 1, "Царга выкатной части"), ("11", 884, 273, 18, 1, "Боковина выкатной части"),
        ("12", 884, 273, 18, 1, "Перегородка выкатной части"), ("13", 884, 273, 18, 1, "Боковина выкатной части"),
        ("14", 1920, 80, 18, 1, "Брусок"), ("15", 1994, 273, 18, 1, "Задняя стенка выкатной части"),
        ("16", 995, 230, 19, 1, "Фасад ящика"), ("16.1", 500, 170, 18, 2, "Бок ящика"),
        ("16.2", 500, 170, 18, 2, "Бок ящика"), ("16.3", 890, 170, 18, 2, "Задняя стенка ящика"),
        ("16.4", 900, 494, 3.5, 2, "Дно ящика"), ("17", 995, 230, 19, 1, "Фасад ящика"),
        ("18", 925, 53, 12, 14, "Ламель"), ("19", 900, 53, 12, 15, "Ламель"), ("20", 70, 20, 20, 2, "Брусок"),
        ("21", 83, 50, 19, 1, "Брусок-шаблон ламелей"), ("22", 2000, 20, 5, 1, "Планка")],
        "P6-934-5-01-Krovat-Linel.pdf p. 2 (table picture, no text layer)")


FIN = [
    {"id": "linel-belyi", "name": "Белый", "body": "door_enamel_whitey#f6f6f7", "swatch": "#f6f6f7",
     "roles": {"white": "door_enamel_whitey#f6f6f7", "birch": "door_enamel_whitey#d9bf94"}},
    {"id": "linel-moloko-belyi", "name": "Молоко / Белый (кровать)", "body": "door_enamel_whitey#f5f5f6",
     "front": "door_enamel_whitey#fdfcfe", "swatch": "#fdfcfe",
     "roles": {"white": "door_enamel_whitey#f5f5f6", "birch": "door_enamel_whitey#d9bf94"}},
]
COLL = [{"id": "linel", "name": "Линель", "brand": "Пинскдрев", "finishes": ["linel-belyi", "linel-moloko-belyi"],
         "metal": "chrome",
         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 123–124 (разворот 242–245); все 6 модулей по инструкциям. "
                 "Детская: ЛДСП 16 «Белый», боковины на подпятниках ФБ 482, крышка на боковинах, дно на цоколе 90; "
                 "вкладные фасады заподлицо, ручки — фрезерованные вырезы (линза на кромке дверей, дуга в верхней "
                 "кромке ящиков); задние стенки ХДФ в пазах. Кровать раздвижная — своя таблица (Пинск), «Молоко / Белый»."}]
MODELS = [
    {"id": "linel-1-01", "code": "П6.934.1.01", "name": "Шкаф для одежды 2Д «Линель»", "collection": "linel",
     "category": "kids", "size": [865, 580, 2109], "is": "IS-Linel-P6-934-1-01-SHkaf-dlya-odejdyi-2D.pdf", "page": 124},
    {"id": "linel-1-02", "code": "П6.934.1.02", "name": "Стол письменный «Линель»", "collection": "linel",
     "category": "kids", "size": [1200, 580, 759], "is": "IS-Linel-P6-934-1-02-Stol-pismennyiy.pdf", "page": 124},
    {"id": "linel-1-03", "code": "П6.934.1.03", "name": "Стеллаж «Линель»", "collection": "linel", "category": "kids",
     "size": [555, 450, 2109], "is": "IS-Linel-P6-934-1-03-Stellaj.pdf", "page": 124},
    {"id": "linel-1-04", "code": "П6.934.1.04", "name": "Комод «Линель»", "collection": "linel", "category": "kids",
     "size": [867, 450, 914], "is": "IS-Linel-P6-934-1-04-komod-poshagovaya-2.pdf", "page": 124,
     "note": "каталог L865; крышка по спецификации 867 (на 1 мм шире боковин с каждой стороны)"},
    {"id": "linel-1-05", "code": "П6.934.1.05", "name": "Полка «Линель»", "collection": "linel", "category": "kids",
     "size": [1100, 216, 250], "is": "IS-P6-934-1-05-polka-Linel.pdf", "page": 124, "mount": "wall"},
    {"id": "linel-5-01", "code": "П6.934.5.01", "name": "Кровать раздвижная «Линель»", "collection": "linel",
     "category": "kids", "size": [2114, 1007, 763], "is": "P6-934-5-01-Krovat-Linel.pdf", "page": 124,
     "finish": "linel-moloko-belyi",
     "note": "спальное место 900 (1800) × 2000: выкатная часть на колёсах с двумя ящиками; матрасы «Линель»"},
]

if __name__ == "__main__":
    for f in (m101, m102, m103, m104, m105, m501):
        print(f())
    cutlists()
    write_fragment(SLUG, FIN, COLL, MODELS)
