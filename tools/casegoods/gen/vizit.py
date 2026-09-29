"""«Визит» (П8.971, hall series): all 8 modules by catalogue (no instructions exist).

Sources: catalogue p. 136 (printed 268–269: the interior with 3.07, 3.08, 3.01; front-on cut-outs of all eight modules;
the «Сосна Карелия 528» swatch) and the product photos of 3.01 on pinskdrev.by (closed front-on, 3/4, open). index.json
had these articles without a collection and with names / sizes shifted by one line: the sizes below are the page's.

Construction (one scheme, measured on the cut-outs; x scale = L, y scale = H per module — the cut-outs are printed
≈ 5 % wider than their true proportion):
* carcass ЛДСП 16 «Сосна Карелия»: a bottom over the full width on grey plastic glides 12 high, the sides on it, a top
  16 over the sides flush with the fronts; ХДФ back in grooves 6 mm from the back edge;
* overlay fronts ЛДСП 16 over the whole front (2 mm in from the ends, 3 mm gaps, 2 mm over the bottom board, 3 mm under
  the top); 3.03 stands on a recessed plinth 40 high instead of glides; 3.08 has inset fronts between the sides;
* black bar handles ≈ 190 long (c-c ≈ 150), square posts: horizontal and centred ≈ 30 mm under the top edge of doors,
  drawers and flaps (3.01, 3.04–3.06, 3.08), vertical by the meeting edge of the doors of 3.02, 3.03, 3.07;
* drawers: ЛДСП 16 boxes, ХДФ bottoms, 13 mm runner gaps; shoe flaps of 3.02 tilt out on a bottom pivot with a rack.

    python3 tools/casegoods/gen/vizit.py        # writes Designs/vizit-*.json and gen/vizit_catalog.json
"""
import json
import os

from common import dump

T, FT, G = 16, 16, 3
GL = 12                         # glides
Y0 = GL + T + 2                 # 30: the fronts' bottom edge
FOOT = "door_enamel_whitey#9fa1a2"
RACK = "door_enamel_whitey#3b3b3d"


def r5(v):
    return round(v * 2) / 2


def carcass(W, B, H, plinth=0, backs=None):
    """Bottom (full width) on glides — or between the sides on a recessed plinth —, sides, top; D = B − fronts."""
    D = B - FT
    if plinth:
        p = [
            {"id": "side-l", "box": [0, 0, 0, T, H - T, D]},
            {"id": "side-r", "box": [W - T, 0, 0, W, H - T, D]},
            {"id": "bottom", "box": [T, plinth, 0, W - T, plinth + T, D]},
            {"id": "plinth", "box": [T, 0, D - 36, W - T, plinth, D - 20]},
            {"id": "plinth-back", "box": [T, 0, 30, W - T, plinth, 46]},
        ]
        yb = plinth + T
    else:
        p = [
            {"id": "bottom", "box": [0, GL, 0, W, GL + T, D]},
            {"id": "side-l", "box": [0, GL + T, 0, T, H - T, D]},
            {"id": "side-r", "box": [W - T, GL + T, 0, W, H - T, D]},
        ]
        yb = GL + T
    p.append({"id": "top", "box": [0, H - T, 0, W, H, B]})
    xs = [T - 6] + list(backs or []) + [W - T + 6]
    for i in range(len(xs) - 1):
        p.append({"id": f"back-{i + 1}" if len(xs) > 2 else "back", "kind": "back",
                  "box": [xs[i], yb - 6, 6, xs[i + 1], H - T + 6, 9.5]})
    if not plinth:
        for i, x in enumerate([15, W - 55] + ([W / 2 - 20] if W > 900 else [])):
            for j, z in enumerate([15, D - 45]):
                p.append({"id": f"glide-{i + 1}{'ab'[j]}", "mat": FOOT, "edge": 3, "box": [x, 0, z, x + 40, GL, z + 30]})
    return p, D


def handle(hid, x, y, z, vertical=False):
    return {"id": hid, "kind": "handle", "model": "bar", "mat": "metal", "at": [r5(x), r5(y)],
            "dir": "up" if vertical else "right", "d": 190, "band": 10, "t": 8, "standoff": 26, "post": 10,
            "section": "square", "z": z}


def front(fid, x0, x1, y0, y1, z0):
    return {"id": fid, "kind": "front", "box": [r5(x0), r5(y0), z0, r5(x1), r5(y1), z0 + FT]}


def door(p, m, name, x0, x1, y0, y1, z0, hinge, top_handle=True, hy=None):
    f = front(f"f-{name}", x0, x1, y0, y1, z0)
    if top_handle:
        h = handle(f"h-{name}", (x0 + x1) / 2, y1 - 42, z0 + FT)
    else:
        h = handle(f"h-{name}", x1 - 30 if hinge == "left" else x0 + 30, hy, z0 + FT, vertical=True)
    p += [f, h]
    m.append({"type": "door", "name": name, "parts": [f["id"], h["id"]], "hinge": hinge, "angle": 100})


def drawer(p, m, name, x0, x1, y0, y1, z0, in0, in1, depth, hdrop=42):
    f = front(f"f-{name}", x0, x1, y0, y1, z0)
    h = handle(f"h-{name}", (x0 + x1) / 2, y1 - hdrop, z0 + FT)
    bx0, bx1 = in0 + 13, in1 - 13
    by0 = y0 + 12
    bh = max(60, min(y1 - y0 - 45, 180))
    zf, zb = z0, z0 - depth
    box = [
        {"id": f"{name}-side-l", "box": [bx0, by0, zb, bx0 + T, by0 + bh, zf]},
        {"id": f"{name}-side-r", "box": [bx1 - T, by0, zb, bx1, by0 + bh, zf]},
        {"id": f"{name}-back", "box": [bx0 + T, by0, zb, bx1 - T, by0 + bh, zb + T]},
        {"id": f"{name}-bottom", "kind": "back", "box": [bx0 + 11, by0 + 10, zb + 4, bx1 - 11, by0 + 13.5, zf - 2]},
    ]
    p += [f, h] + box
    m.append({"type": "drawer", "name": name, "parts": [f["id"], h["id"]] + [q["id"] for q in box], "travel": depth - 50})


def flap(p, m, name, x0, x1, y0, y1, z0, in0, in1, depth=200):
    f = front(f"f-{name}", x0, x1, y0, y1, z0)
    h = handle(f"h-{name}", (x0 + x1) / 2, y1 - 42, z0 + FT)
    zb = z0 - depth
    ra, rb = in0 + 6, in1 - 6
    hy = r5(y0 + (y1 - y0) * 0.5)
    rack = [
        {"id": f"{name}-end-l", "mat": RACK, "box": [ra, y0 + 20, zb, ra + 4, y1 - 40, z0]},
        {"id": f"{name}-end-r", "mat": RACK, "box": [rb - 4, y0 + 20, zb, rb, y1 - 40, z0]},
        {"id": f"{name}-ledge-1", "mat": RACK, "box": [ra + 4, y0 + 30, zb, rb - 4, y0 + 34, z0 - 60]},
        {"id": f"{name}-ledge-2", "mat": RACK, "box": [ra + 4, hy, zb, rb - 4, hy + 4, z0 - 60]},
    ]
    p += [f, h] + rack
    m.append({"type": "flap", "name": name, "parts": [f["id"], h["id"]] + [q["id"] for q in rack], "hinge": "bottom",
              "angle": 40})


def shelf(sid, x0, x1, ytop, D):
    return {"id": sid, "box": [x0 + 1, ytop - T, 20, x1 - 1, ytop, D - 5]}


def partition(pid, xc, y0, y1, D):
    return {"id": pid, "box": [xc - T / 2, y0, 10, xc + T / 2, y1, D]}


def stack(y0, y1, n, g=G):
    h = (y1 - y0 - (n - 1) * g) / n
    return [(r5(y0 + i * (h + g)), r5(y0 + i * (h + g) + h)) for i in range(n)][::-1]     # top first


def m_3_01():
    """Тумба для обуви 1000×470×500: two doors (handles on top), one shelf, no partition (site photos 3.01)."""
    W, B, H = 1000, 470, 500
    p, D = carcass(W, B, H)
    m = []
    p.append(shelf("shelf", T, W - T, 262, D))
    yt = H - T - G
    door(p, m, "door_left", 2, W / 2 - 1.5, Y0, yt, D, "left")
    door(p, m, "door_right", W / 2 + 1.5, W - 2, Y0, yt, D, "right")
    return dump("vizit-3-01", [W, B, H], p, m)


def m_3_02():
    """Тумба для обуви 800×380×1120: left column (500) a drawer over two tilt-out shoe flaps, right a door (cut-out)."""
    W, B, H = 800, 380, 1120
    p, D = carcass(W, B, H, backs=[500])
    m = []
    xc = 500
    p.append(partition("partition", xc, GL + T, H - T, D))
    p.append({"id": "rail", "box": [T, 827, 10, xc - T / 2, 843, D]})
    p.append({"id": "rail-2", "box": [T, 427, 10, xc - T / 2, 443, D]})
    for i, y in enumerate([370, 700, 950]):
        p.append(shelf(f"shelf-{i + 1}", xc + T / 2, W - T, y, D))
    yt = H - T - G
    drawer(p, m, "drawer", 2, xc - 1.5, 846, yt, D, T, xc - T / 2, 320)
    flap(p, m, "flap_top", 2, xc - 1.5, 446, 843, D, T, xc - T / 2)
    flap(p, m, "flap_low", 2, xc - 1.5, Y0, 443, D, T, xc - T / 2)
    door(p, m, "door", xc + 1.5, W - 2, Y0, yt, D, "right", top_handle=False, hy=900)
    return dump("vizit-3-02", [W, B, H], p, m)


def m_3_03():
    """Тумба для обуви 700×400×1000 on a recessed plinth 40: two doors, handles upright by the meeting edges, shelves."""
    W, B, H, PL = 700, 400, 1000, 40
    p, D = carcass(W, B, H, plinth=PL)
    m = []
    for i, y in enumerate([290, 530, 770]):
        p.append(shelf(f"shelf-{i + 1}", T, W - T, y, D))
    yt = H - T - G
    door(p, m, "door_left", 2, W / 2 - 1.5, PL + 4, yt, D, "left", top_handle=False, hy=840)
    door(p, m, "door_right", W / 2 + 1.5, W - 2, PL + 4, yt, D, "right", top_handle=False, hy=840)
    return dump("vizit-3-03", [W, B, H], p, m)


def m_3_04():
    """Тумба для обуви 1000×300×1200: two unequal doors (595 | 397 — the cut-out), handles on top by the meeting edge,
    a partition behind the joint, shoe shelves."""
    W, B, H = 1000, 300, 1200
    xj = 598.5                                           # the joint of the doors
    p, D = carcass(W, B, H, backs=[xj])
    m = []
    p.append(partition("partition", xj, GL + T, H - T, D))
    for i, y in enumerate([300, 560, 820]):
        p.append(shelf(f"shelf-l{i + 1}", T, xj - T / 2, y, D))
        p.append(shelf(f"shelf-r{i + 1}", xj + T / 2, W - T, y, D))
    yt = H - T - G
    fl = front("f-door_left", 2, xj - 1.5, Y0, yt, D)
    hl = handle("h-door_left", xj - 1.5 - 120, yt - 42, D + FT)
    fr = front("f-door_right", xj + 1.5, W - 2, Y0, yt, D)
    hr = handle("h-door_right", xj + 1.5 + 120, yt - 42, D + FT)
    p += [fl, hl, fr, hr]
    m.append({"type": "door", "name": "door_left", "parts": [fl["id"], hl["id"]], "hinge": "left", "angle": 100})
    m.append({"type": "door", "name": "door_right", "parts": [fr["id"], hr["id"]], "hinge": "right", "angle": 100})
    return dump("vizit-3-04", [W, B, H], p, m)


def drawer_column(p, m, tag, x0, x1, in0, in1, D, heights):
    """Drawers x0..x1 (front), boxes between in0..in1; heights = the front y ranges, top first."""
    for i, (y0, y1) in enumerate(heights):
        drawer(p, m, f"drawer_{tag}{i + 1}", x0, x1, y0, y1, D, in0, in1, 300)


def comod(did, W, cols):
    """Комод 700 / 1050 × 372 × 750: columns of 350 — 'D' a door (handle on top), 'Dv' a door with an upright handle,
    'K3' three drawers (170 / 170 / 350), 'K4' four equal drawers."""
    B, H = 372, 750
    n = len(cols)
    w = W / n
    xs = [w * i for i in range(1, n)]
    p, D = carcass(W, B, H, backs=xs)
    m = []
    yt = H - T - G
    for i, xc in enumerate(xs):
        p.append(partition(f"partition-{i + 1}", xc, GL + T, H - T, D))
    for i, c in enumerate(cols):
        fx0 = 2 if i == 0 else w * i + 1.5
        fx1 = W - 2 if i == n - 1 else w * (i + 1) - 1.5
        in0 = T if i == 0 else w * i + T / 2
        in1 = W - T if i == n - 1 else w * (i + 1) - T / 2
        if c in ("D", "Dv"):
            hinge = "left" if i == 0 else "right"
            p.append(shelf(f"shelf-{i + 1}", in0, in1, 390, D))
            door(p, m, f"door_{i + 1}", fx0, fx1, Y0, yt, D, hinge, top_handle=(c == "D"), hy=590)
        elif c == "K3":
            drawer_column(p, m, f"{i + 1}_", fx0, fx1, in0, in1, D, [(561, yt), (386, 558), (Y0, 383)])
        elif c == "K4":
            drawer_column(p, m, f"{i + 1}_", fx0, fx1, in0, in1, D, stack(Y0, yt, 4))
    return dump(did, [W, B, H], p, m)


def m_3_08():
    """Комод 536×480×1120: three drawers with inset fronts between the sides (319 / 318 / 405 — the cut-out)."""
    W, B, H = 536, 480, 1120
    p = [
        {"id": "bottom", "box": [0, GL, 0, W, GL + T, B]},
        {"id": "side-l", "box": [0, GL + T, 0, T, H - T, B]},
        {"id": "side-r", "box": [W - T, GL + T, 0, W, H - T, B]},
        {"id": "top", "box": [0, H - T, 0, W, H, B]},
        {"id": "back", "kind": "back", "box": [T - 6, GL + T - 6, 6, W - T + 6, H - T + 6, 9.5]},
    ]
    for i, x in enumerate([15, W - 55]):
        for j, z in enumerate([15, B - 45]):
            p.append({"id": f"glide-{i + 1}{'ab'[j]}", "mat": FOOT, "edge": 3, "box": [x, 0, z, x + 40, GL, z + 30]})
    m = []
    z0 = B - FT
    yt = H - T - 2
    for i, (y0, y1) in enumerate([(772, yt), (450, 769), (Y0, 447)]):
        drawer(p, m, f"drawer_{i + 1}", T + 2, W - T - 2, y0, y1, z0, T, W - T, 420, hdrop=r5((y1 - y0) * 0.3))
    return dump("vizit-3-08", [W, B, H], p, m)


# ------------------------------------------------------------------------------------------------------ catalogue
FIN = "vizit-sosna-kareliya"
MODELS = [
    ("3.01", "Тумба для обуви «Визит»", [1000, 470, 500]),
    ("3.02", "Тумба для обуви «Визит»", [800, 380, 1120]),
    ("3.03", "Тумба для обуви «Визит»", [700, 400, 1000]),
    ("3.04", "Тумба для обуви «Визит»", [1000, 300, 1200]),
    ("3.05", "Комод «Визит»", [700, 372, 750]),
    ("3.06", "Комод «Визит»", [1050, 372, 750]),
    ("3.07", "Комод «Визит»", [1050, 372, 750]),
    ("3.08", "Комод «Визит»", [536, 480, 1120]),
]


def catalog():
    return {
        "finishes": [
            {"id": FIN, "name": "Сосна Карелия 528", "body": "door_enamel_whitey#c6c4c5", "swatch": "#c6c4c5"}
        ],
        "profiles": {},
        "collections": [
            {"id": "vizit", "name": "Визит", "brand": "Пинскдрев", "finishes": [FIN], "metal": "black",
             "note": "Каталог «Корпусная мебель ч. II» 2025, с. 136 (разворот 268–269); все модули по каталогу, без инструкций. "
                     "Корпус ЛДСП 16 «Сосна Карелия» на пластиковых опорах 12 мм, крышка на боковинах, накладные фасады, "
                     "чёрные ручки-скобы ≈ 190 мм, задняя стенка ХДФ в пазах."}
        ],
        "models": [
            {"id": "vizit-" + c.replace(".", "-"), "code": "П8.971." + c, "name": n, "collection": "vizit",
             "category": "hall", "size": s, "page": 136,
             "note": "по каталогу, без инструкции (index.json: имя и размер со сдвигом строки — взяты со с. 136)"}
            for c, n, s in MODELS
        ],
    }


def write_catalog():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "vizit_catalog.json")
    with open(path, "w") as fh:
        json.dump(catalog(), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


if __name__ == "__main__":
    print(write_catalog())
    print(m_3_01())
    print(m_3_02())
    print(m_3_03())
    print(m_3_04())
    print(comod("vizit-3-05", 700, ["D", "K3"]))
    print(comod("vizit-3-06", 1050, ["D", "D", "K3"]))
    print(comod("vizit-3-07", 1050, ["Dv", "K4", "Dv"]))
    print(m_3_08())
