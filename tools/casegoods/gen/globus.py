"""«Глобус» (П7.038) and «Мокко» (П7.053) sliding-door wardrobes (шкафы-купе), by catalogue / by photo.

Sources: catalogue p. 64 (printed 125: the 3.18 interior photo in «Дуб Каньон», the cut-outs of 3.12 / 3.18 with their
interior schemes, the Мокко 1.10 cut-out and scheme, the swatches) and the product photos of pinskdrev.by: 3.18 — closed
(Каньон and Сосна Карелия), the middle door open (Каньон: the shelf column with two drawers), the left door open (Сосна:
two-tier hanging), the scheme; 3.12 — closed and the left door open (a shelf column with two drawers under a full-width
top shelf, a hanging section). Мокко 1.10 has no product page: the catalogue cut-out and its scheme only.
No instructions exist. Heights were measured on the photos (scale = H at the front corner, x and y separately).

Construction (the photos' corners):
* ЛДСП 16: the sides stand on the floor over the full depth 610, the top lies on them (16), the bottom sits between the
  sides on a plinth 80 recessed 30 behind the front edge (a band of the bottom's edge shows over it); ХДФ back in grooves
  6 mm from the back edge, split behind a partition; partitions and shelves 16, 520 deep (the doors' zone in front);
* sliding doors on two tracks between the sides: a bottom track on the bottom board, a top track under the top
  (hiding the doors' top 10 mm); the doors hang 106…2294 (Мокко 106…2286); each door is framed by aluminium profiles —
  a vertical handle-profile 20 × 28 on both edges, a top rail 30 and a bottom rail 40 — round a ЛДСП 10 filling;
  the doors overlap by 25; Глобус 3Д: the middle door on the front track, Глобус 2Д / Мокко: the right door in front;
* interiors from the schemes and the open-door photos (see the functions); inner drawers have inset fronts without
  handles (the photos), boxes ЛДСП 16 with ХДФ bottoms, 13 mm runner gaps; chrome rails Ø25.

    python3 tools/casegoods/gen/globus.py     # writes Designs/globus-*.json, mokko-1-10.json, gen/globus_catalog.json,
                                              # gen/mokko_catalog.json
"""
import json
import os

from common import dump

T = 16
D = 610
IZ = 520               # the interior's front (shelves, partitions); doors in front of it
PL = 80                # plinth
YB = PL + T            # 96: the bottom board's top
BACK = 3.5


def P(pid, box, **kw):
    d = {"id": pid, "box": [round(v, 1) for v in box]}
    d.update(kw)
    return d


def carcass(W, H, parts_x):
    YT = H - T
    p = [P("side-l", [0, 0, 0, T, YT, D], grain="y"), P("side-r", [W - T, 0, 0, W, YT, D], grain="y"),
         P("top", [0, YT, 0, W, H, D], grain="x"),
         P("bottom", [T, PL, 0, W - T, YB, D], grain="x"),
         P("plinth", [T, 0, D - 30 - T, W - T, PL, D - 30], grain="x"),
         P("plinth-back", [T, 0, 40, W - T, PL, 40 + T], grain="x")]
    xs = [T - 6] + list(parts_x) + [W - T + 6]
    for i in range(len(xs) - 1):
        a = xs[i] + (0.5 if i else 0)
        b = xs[i + 1] - (0.5 if i < len(xs) - 2 else 0)
        p.append(P(f"back-{i + 1}", [a, YB - 6, 6, b, YT + 6, 6 + BACK], kind="back"))
    for i, c in enumerate(parts_x):
        p.append(P(f"partition-{i + 1}", [c - T / 2, YB, 10, c + T / 2, YT, IZ], grain="y"))
    # tracks
    p += [P("track-top", [T, YT - 20, 528, W - T, YT, 606], mat="metal", edge=0.5),
          P("track-bottom", [T, YB, 528, W - T, YB + 8, 606], mat="metal", edge=0.5)]
    return p


def doors(W, H, n, front_idx, ytop, fill_mat="front"):
    """n sliding doors between the sides, overlapping by 25; front_idx = the doors on the front track."""
    inner = W - 2 * T
    ov = 25
    dw = (inner + (n - 1) * ov) / n
    y0, y1 = YB + 10, ytop
    p, m = [], []
    for i in range(n):
        x0 = T + i * (dw - ov)
        x1 = x0 + dw
        z0, z1 = (572, 600) if i in front_idx else (536, 564)
        zc = (z0 + z1) / 2
        tag = f"door{i + 1}"
        g = [P(f"{tag}-prof-l", [x0, y0, z0, x0 + 20, y1, z1], mat="metal", edge=1),
             P(f"{tag}-prof-r", [x1 - 20, y0, z0, x1, y1, z1], mat="metal", edge=1),
             P(f"{tag}-prof-b", [x0 + 20, y0, z0 + 4, x1 - 20, y0 + 40, z1 - 4], mat="metal", edge=0.5),
             P(f"{tag}-prof-t", [x0 + 20, y1 - 30, z0 + 4, x1 - 20, y1, z1 - 4], mat="metal", edge=0.5),
             P(f"{tag}-fill", [x0 + 12, y0 + 30, zc - 5, x1 - 12, y1 - 22, zc + 5], kind="front", mat=fill_mat, grain="y")]
        p += g
        by = (dw - ov) if i == 0 else -(dw - ov)
        m.append({"type": "slide", "name": f"coupe_{i + 1}", "parts": [q["id"] for q in g], "by": [round(by, 1), 0, 0]})
    return p, m


def shelf(pid, a, b, y):
    return P(pid, [a + 1, y - T, 10, b - 1, y, IZ - 2], grain="x")


def rail(pid, a, b, y):
    return {"id": pid, "kind": "tube", "mat": "chrome", "box": [round(a + 2, 1), y - 25, 255, round(b - 2, 1), y, 280]}


def inner_drawer(tag, a, b, y0, y1):
    """An inner drawer with an inset front between the column's panels (no handle: the photos)."""
    g = [P(f"{tag}-front", [a + 2, y0, IZ - T, b - 2, y1, IZ], kind="front", mat="body", grain="x")]
    bx0, bx1, by0, bh, zb = a + 13, b - 13, y0 + 12, y1 - y0 - 50, IZ - T - 420
    g += [P(f"{tag}-side-l", [bx0, by0, zb, bx0 + T, by0 + bh, IZ - T]),
          P(f"{tag}-side-r", [bx1 - T, by0, zb, bx1, by0 + bh, IZ - T]),
          P(f"{tag}-back", [bx0 + T, by0, zb, bx1 - T, by0 + bh, zb + T]),
          P(f"{tag}-bottom", [bx0 + 8, by0 + 10, zb + 4, bx1 - 8, by0 + 13.5, IZ - T - 2], kind="back")]
    return g, {"type": "drawer", "name": tag, "parts": [q["id"] for q in g], "travel": 350}


# ------------------------------------------------------------------------------------------------------------ Глобус
def globus_3_18():
    """1800: left section two-tier hanging (rail under the top, a shelf at 1346 with a rail under it — the Сосна photo
    with the left door open); middle shelf column 464 wide: shelves 1978 / 1670 / 1362, two drawers, a shelf under them,
    a shelf 536 (the Каньон photo with the middle door open); right section: a rail under the top and a shelf at 1150
    (the scheme)."""
    W, H = 1800, 2332
    c1, c2 = 628, 1108
    p = carcass(W, H, [c1, c2])
    m = []
    L0, L1 = T, c1 - T / 2
    M0, M1 = c1 + T / 2, c2 - T / 2
    R0, R1 = c2 + T / 2, W - T
    p += [rail("l-rail-top", L0, L1, 2180), shelf("l-shelf", L0, L1, 1346), rail("l-rail-low", L0, L1, 1270)]
    for i, y in enumerate([1978, 1670, 1362, 896, 536]):
        p.append(shelf(f"m-shelf-{i + 1}", M0, M1, y))
    for i, (y0, y1) in enumerate([(1130, 1340), (910, 1120)]):
        g, mv = inner_drawer(f"drawer_{i + 1}", M0, M1, y0, y1)
        p += g
        m.append(mv)
    p += [rail("r-rail", R0, R1, 2180), shelf("r-shelf", R0, R1, 1150)]
    dp, dm = doors(W, H, 3, {1}, 2294)
    p += dp
    return dump("globus-3-18", [W, D, H], p, dm + m)


def globus_3_12():
    """1200: a full-width top shelf at 1980; left a shelf column 400 wide: shelves 1515 / 1130, two drawers, shelves
    664 / 380; right a hanging section: rail 1920 under the top shelf and a low shelf 470 (the photo with the left door
    open and the scheme)."""
    W, H = 1200, 2332
    c1 = 424
    p = carcass(W, H, [c1])
    m = []
    L0, L1 = T, c1 - T / 2
    R0, R1 = c1 + T / 2, W - T
    # the top shelf runs over the partition: the partition stops under it
    for q in p:
        if q["id"] == "partition-1":
            q["box"][4] = 1964
    p.append(shelf("top-shelf", T, W - T, 1980))
    for i, y in enumerate([1515, 1130, 680, 380]):
        p.append(shelf(f"l-shelf-{i + 1}", L0, L1, y))
    for i, (y0, y1) in enumerate([(875, 1065), (684, 870)]):
        g, mv = inner_drawer(f"drawer_{i + 1}", L0, L1, y0, y1)
        p += g
        m.append(mv)
    p += [rail("r-rail", R0, R1, 1920), shelf("r-shelf", R0, R1, 470)]
    dp, dm = doors(W, H, 2, {1}, 2294)
    p += dp
    return dump("globus-3-12", [W, D, H], p, dm + m)


# ------------------------------------------------------------------------------------------------------------ Мокко
def mokko_1_10():
    """1536 × 610 × 2324, doors «Капучино», carcass «Дуб Монтерей» (the cut-out). Scheme: partition at 846; left section:
    top shelf 1990, rail 1865, a pull-out mirror against the left side (≈ 250 deep × 1190, slides out forward), a low
    shelf 460; right section: top shelf 1990, shelves 1640 / 1265, four drawers 1215…425, a shelf under them."""
    W, H = 1536, 2324
    c1 = 846
    p = carcass(W, H, [c1])
    m = []
    L0, L1 = T, c1 - T / 2
    R0, R1 = c1 + T / 2, W - T
    p += [shelf("l-shelf-top", L0, L1, 1990), rail("l-rail", L0 + 60, L1, 1865), shelf("l-shelf-low", L0, L1, 460)]
    # pull-out mirror: a board with a mirror on its inner face, on top / bottom runners fixed to the left side
    mz0, mz1 = 40, 500
    mg = [P("mirror-board", [T + 30, 500, mz0, T + 46, 1690, mz1], grain="y"),
          {"id": "mirror", "kind": "mirror", "edge": 0.5, "box": [T + 46, 520, mz0 + 20, T + 50, 1670, mz1 - 20]}]
    p += mg
    p += [P("mirror-runner-t", [T, 1690, mz0, T + 30, 1720, mz1], mat="metal", edge=0.5),
          P("mirror-runner-b", [T, 470, mz0, T + 30, 500, mz1], mat="metal", edge=0.5)]
    m.append({"type": "slide", "name": "mirror", "parts": [q["id"] for q in mg], "by": [0, 0, 440]})
    for i, y in enumerate([1990, 1640, 1265, 425]):
        p.append(shelf(f"r-shelf-{i + 1}", R0, R1, y))
    ys = [(1030, 1245), (818, 1026), (636, 814), (429, 632)]
    for i, (y0, y1) in enumerate(ys):
        g, mv = inner_drawer(f"drawer_{i + 1}", R0, R1, y0, y1)
        g.append({"id": f"drawer_{i + 1}-handle", "kind": "handle", "model": "bar", "mat": "metal",
                  "at": [round((R0 + R1) / 2, 1), y1 - 30], "dir": "right", "d": 128, "band": 8, "t": 6, "standoff": 8,
                  "post": 8, "z": IZ})
        mv["parts"].append(f"drawer_{i + 1}-handle")
        p += g
        m.append(mv)
    dp, dm = doors(W, H, 2, {1}, 2286)
    p += dp
    return dump("mokko-1-10", [W, D, H], p, dm + m)


# ------------------------------------------------------------------------------------------------------ catalogues
HERE = os.path.dirname(os.path.abspath(__file__))


def write(name, data):
    path = os.path.join(HERE, name)
    with open(path, "w") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


def globus_catalog():
    fins = [
        {"id": "globus-sosna-kareliya", "name": "Сосна Карелия", "body": "door_enamel_whitey#e7e7e1", "swatch": "#e7e7e1"},
        {"id": "globus-dub-kanon", "name": "Дуб Каньон", "body": "door_enamel_whitey#8a6b4e", "swatch": "#8a6b4e"},
    ]
    note = "по каталогу и фото сайта, без инструкции; наполнение по схеме и фото с открытой дверью"
    return {
        "finishes": fins, "profiles": {},
        "collections": [{"id": "globus", "name": "Глобус", "brand": "Пинскдрев", "finishes": [f["id"] for f in fins],
                         "metal": "gold#c0c3c6",
                         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 64 (разворот 124–125) и фото pinskdrev.by; без "
                                 "инструкций. Шкафы-купе: корпус ЛДСП 16 на цоколе 80, двери-купе в алюминиевом профиле "
                                 "(матовое серебро) с заполнением ЛДСП в цвет корпуса, две направляющие."}],
        "models": [
            {"id": "globus-3-18", "code": "П7.038.3.18", "name": "Шкаф-купе 3д «Глобус»", "collection": "globus",
             "category": "bedroom", "size": [1800, 610, 2332], "page": 64, "note": note},
            {"id": "globus-3-12", "code": "П7.038.3.12", "name": "Шкаф-купе 2д «Глобус»", "collection": "globus",
             "category": "bedroom", "size": [1200, 610, 2332], "page": 64, "note": note},
        ],
    }


def mokko_catalog():
    fins = [{"id": "mokko-monterey-kapuchino", "name": "Дуб Монтерей / Капучино", "body": "door_enamel_whitey#747474",
             "front": "door_enamel_whitey#a9a7a7", "swatch": "#a9a7a7"}]
    return {
        "finishes": fins, "profiles": {},
        "collections": [{"id": "mokko", "name": "Мокко", "brand": "Пинскдрев", "finishes": [f["id"] for f in fins],
                         "metal": "gold#5c5e61",
                         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 64 (разворот 124–125); без инструкции и без "
                                 "страницы на сайте. Шкаф-купе: корпус «Дуб Монтерей», двери «Капучино» в графитовом "
                                 "профиле, внутри выдвижное зеркало."}],
        "models": [{"id": "mokko-1-10", "code": "П7.053.1.10", "name": "Шкаф-купе 2Д «Мокко»", "collection": "mokko",
                    "category": "bedroom", "size": [1536, 610, 2324], "page": 64,
                    "note": "по каталогу (вырезка и схема наполнения), без инструкции; внутри выдвижное зеркало"}],
    }


if __name__ == "__main__":
    print(write("globus_catalog.json", globus_catalog()))
    print(write("mokko_catalog.json", mokko_catalog()))
    print(globus_3_18())
    print(globus_3_12())
    print(mokko_1_10())
