"""«Верес» (П3.564, hall set): all 10 modules by catalogue / by photo (no instructions exist).

Sources: catalogue p. 135 (printed 266–267: interior, the module cut-outs, the swatches «Дуб бордо лайт» (Фасад) /
«Дуб каньон» (Каркас)) and the product photos of pinskdrev.by (front-on views of 3.01, 3.05, 3.07, 3.09, 3.10, 3.14,
3.17, 3.18; open views of 3.01, 3.05, 3.07, 3.09, 3.10; 3/4 views of 3.06, 3.08).

Construction (the same in every case piece, measured on the front-on photos; scale = the known L / H):
* the outer frame is ЛДСП 25 «Дуб каньон»: the bottom and the top run the full width and depth, the sides stand between
  them (the photos show a 24–27 mm band all round the fronts, the same on the sides, the top and the bottom);
* the carcass stands on grey plastic block feet 18 high (40 × 30), 20 mm in from the ends, front and back;
* inner partitions / shelves ЛДСП 16, the back ХДФ 3.5 in grooves 6 mm from the back edge;
* fronts ЛДСП 16 inset between the sides / top / bottom, flush with the frame's front edge, 2–3 mm gaps; doors and flaps
  «Дуб бордо лайт», drawer fronts and the flap of 3.07 «Дуб каньон» (as in the catalogue cut-outs);
* shoe flaps tilt out on a bottom pivot (≈ 40°) and carry a two-level rack behind them (brown plastic ends + two ledges);
* handles: satin-chrome staple handles ≈ 170 long (c-c 128), horizontal and centred under the top edge of drawers and
  flaps, vertical by the free edge of doors.

    python3 tools/casegoods/gen/veres.py        # writes Designs/veres-*.json and gen/veres_catalog.json
"""
import json
import os

from common import dump

T, TI, FT = 25, 16, 16          # frame, inner boards, fronts
FEET = 18
G = 2.5                         # gap round the fronts
RACK = "door_enamel_whitey#4a3328"   # the brown plastic ends of the shoe racks
FOOT = "door_enamel_whitey#a3a5a6"   # grey plastic feet


def r5(v):
    return round(v * 2) / 2


def carcass(W, B, H, backs=None):
    p = [
        {"id": "bottom", "box": [0, FEET, 0, W, FEET + T, B]},
        {"id": "top", "box": [0, H - T, 0, W, H, B]},
        {"id": "side-l", "box": [0, FEET + T, 0, T, H - T, B]},
        {"id": "side-r", "box": [W - T, FEET + T, 0, W, H - T, B]},
    ]
    xs = [T - 10] + list(backs or []) + [W - T + 10]
    for i in range(len(xs) - 1):
        p.append({"id": f"back-{i + 1}" if len(xs) > 2 else "back", "kind": "back",
                  "box": [xs[i], FEET + T - 10, 6, xs[i + 1], H - T + 10, 9.5]})
    return p


def feet(W, B, extra_x=()):
    out = []
    xs = [20, W - 60] + list(extra_x)
    for i, x in enumerate(xs):
        for j, z in enumerate([20, B - 50]):
            out.append({"id": f"foot-{i + 1}{'ab'[j]}", "kind": "panel", "mat": FOOT, "edge": 3,
                        "box": [x, 0, z, x + 40, FEET, z + 30]})
    return out


def handle(hid, x, y, B, vertical=False):
    return {"id": hid, "kind": "handle", "model": "bar", "at": [r5(x), r5(y)], "dir": "up" if vertical else "right",
            "d": 170, "band": 12, "t": 8, "standoff": 24, "post": 10, "section": "square", "z": B}


def front(fid, x0, x1, y0, y1, B, mat=None):
    f = {"id": fid, "kind": "front", "box": [r5(x0), r5(y0), B - FT, r5(x1), r5(y1), B]}
    if mat:
        f["mat"] = mat
    return f


def door(p, m, name, x0, x1, y0, y1, B, hinge, hy, mat=None):
    f = front(f"f-{name}", x0, x1, y0, y1, B, mat)
    hx = x1 - 30 if hinge == "left" else x0 + 30
    h = handle(f"h-{name}", hx, hy, B, vertical=True)
    p += [f, h]
    m.append({"type": "door", "name": name, "parts": [f["id"], h["id"]], "hinge": hinge, "angle": 100})


def drawer(p, m, name, x0, x1, y0, y1, B, in0, in1, depth=320, mat="body"):
    """Drawer front x0..x1 × y0..y1 (a «Дуб каньон» front), its box between the inner faces in0..in1 (13 mm runners)."""
    f = front(f"f-{name}", x0, x1, y0, y1, B, mat)
    h = handle(f"h-{name}", (x0 + x1) / 2, y1 - 26, B)
    bx0, bx1 = in0 + 13, in1 - 13
    by0, bh = y0 + 12, min(y1 - y0 - 45, 150)
    zf = B - FT
    zb = zf - depth
    box = [
        {"id": f"{name}-side-l", "box": [bx0, by0, zb, bx0 + TI, by0 + bh, zf]},
        {"id": f"{name}-side-r", "box": [bx1 - TI, by0, zb, bx1, by0 + bh, zf]},
        {"id": f"{name}-back", "box": [bx0 + TI, by0, zb, bx1 - TI, by0 + bh, zb + TI]},
        {"id": f"{name}-bottom", "kind": "back", "box": [bx0 + 11, by0 + 10, zb + 4, bx1 - 11, by0 + 13.5, zf - 2]},
    ]
    p += [f, h] + box
    m.append({"type": "drawer", "name": name, "parts": [f["id"], h["id"]] + [q["id"] for q in box], "travel": depth - 40})


def flap(p, m, name, x0, x1, y0, y1, B, in0, in1, mat=None, depth=190):
    """Tilt-out shoe flap: the front on a bottom pivot, a two-level rack behind it (brown ends, two «каньон» ledges)."""
    f = front(f"f-{name}", x0, x1, y0, y1, B, mat)
    h = handle(f"h-{name}", (x0 + x1) / 2, y1 - 30, B)
    zf = B - FT
    zb = zf - depth
    hgt = y1 - y0
    ra, rb = in0 + 6, in1 - 6
    rack = [
        {"id": f"{name}-end-l", "mat": RACK, "box": [ra, y0 + 20, zb, ra + 4, y1 - 40, zf]},
        {"id": f"{name}-end-r", "mat": RACK, "box": [rb - 4, y0 + 20, zb, rb, y1 - 40, zf]},
        {"id": f"{name}-ledge-1", "box": [ra + 4, y0 + 30, zb, rb - 4, y0 + 30 + TI, zf - 60]},
        {"id": f"{name}-ledge-2", "box": [ra + 4, r5(y0 + hgt * 0.52), zb, rb - 4, r5(y0 + hgt * 0.52) + TI, zf - 60]},
        {"id": f"{name}-lip-1", "mat": RACK, "box": [ra + 4, y0 + 30 + TI, zb, rb - 4, y0 + 30 + TI + 30, zb + 4]},
        {"id": f"{name}-lip-2", "mat": RACK, "box": [ra + 4, r5(y0 + hgt * 0.52) + TI, zb, rb - 4, r5(y0 + hgt * 0.52) + TI + 30, zb + 4]},
    ]
    p += [f, h] + rack
    m.append({"type": "flap", "name": name, "parts": [f["id"], h["id"]] + [q["id"] for q in rack], "hinge": "bottom",
              "angle": 40})


def shelf(sid, x0, x1, ytop, B, fixed=False):
    if fixed:
        return {"id": sid, "box": [x0, ytop - TI, 10, x1, ytop, B - FT]}
    return {"id": sid, "box": [x0 + 1, ytop - TI, 20, x1 - 1, ytop, B - FT - 20]}


def partition(pid, x0, y0, y1, B):
    return {"id": pid, "box": [x0, y0, 10, x0 + TI, y1, B - FT]}


# ------------------------------------------------------------------------------------------------------ modules
Y0 = FEET + T + G / 2 + 0.75      # 45: the lowest front's bottom edge


def m_3_10():
    """Тумба для обуви 496×401×867: a drawer (200) over a door, a shelf behind the door (photo 3.10 /1, /2)."""
    W, B, H = 496, 401, 867
    p, m = carcass(W, B, H), []
    p += [shelf("shelf", T, W - T, 355, B)]
    p.append({"id": "rail", "box": [T, 623, 10, W - T, 623 + TI, B - FT]})       # the fixed shelf under the drawer
    drawer(p, m, "drawer", T + 2, W - T - 2, 641, H - T - 2, B, T, W - T, depth=340)
    door(p, m, "door", T + 2, W - T - 2, Y0, 638, B, "right", 545)
    p += feet(W, B)
    return dump("veres-3-10", [W, B, H], p, m)


def m_3_09():
    """Тумба для обуви 794×401×450 with a seat cushion: carcass 376 high, two doors, a shelf; cushion 74 (photo 3.09)."""
    W, B, H, HC = 794, 401, 450, 376
    p, m = carcass(W, B, HC), []
    p.append(shelf("shelf", T, W - T, 215, B))
    mid = W / 2
    door(p, m, "door_left", T + 2, mid - 1.5, Y0, HC - T - 2, B, "left", 230)
    door(p, m, "door_right", mid + 1.5, W - T - 2, Y0, HC - T - 2, B, "right", 230)
    # the handles of the pair sit by the meeting edges
    p.append({"id": "cushion", "kind": "soft", "mat": "fabric", "box": [0, HC, 0, W, H, B]})
    p += feet(W, B)
    return dump("veres-3-09", [W, B, H], p, m)


def m_3_07():
    """Тумба для обуви 812×382×1258: open niche on top, a «каньон» shoe flap, two doors, a shelf (photo 3.07)."""
    W, B, H = 812, 382, 1258
    p, m = carcass(W, B, H, backs=[W / 2]), []
    p.append({"id": "niche-shelf", "box": [T, 1032, 0 + 10, W - T, 1048, B]})    # the niche floor, full depth to the front
    p.append({"id": "rail", "box": [T, 636, 25.5, W - T, 652, B - FT]})           # fixed shelf between the flap and the doors
    p.append({"id": "back-rail", "box": [W / 2 - 40, FEET + T, 9.5, W / 2 + 40, 1032, 25.5]})   # the back rail at the joint
    p.append({"id": "shelf", "box": [T + 1, 334, 26, W - T - 1, 350, B - FT - 20]})
    flap(p, m, "flap", T + 2, W - T - 2, 655, 1029, B, T, W - T, mat="body")
    door(p, m, "door_left", T + 2, W / 2 - 1.5, Y0, 633, B, "left", 520)
    door(p, m, "door_right", W / 2 + 1.5, W - T - 2, Y0, 633, B, "right", 520)
    p += feet(W, B)
    return dump("veres-3-07", [W, B, H], p, m)


def shoe_block(p, m, x0, x1, B, H, tag=""):
    """The 812-wide flap block of 3.06 / 3.08 between the frame faces x0..x1: a drawer over two tilt-out flaps."""
    p.append({"id": f"rail{tag}", "box": [x0, 785, 10, x1, 801, B - FT]})         # fixed shelf under the drawer
    p.append({"id": f"rail2{tag}", "box": [x0, 405, 10, x1, 421, B - FT]})        # between the flaps (the rack stop)
    drawer(p, m, f"drawer{tag}", x0 + 2, x1 - 2, 804, H - T - 2, B, x0, x1, depth=300)
    flap(p, m, f"flap_top{tag}", x0 + 2, x1 - 2, 424, 801, B, x0, x1)
    flap(p, m, f"flap_low{tag}", x0 + 2, x1 - 2, Y0, 421, B, x0, x1)


def m_3_06():
    """Тумба для обуви 812×382×1044: a «каньон» drawer over two tilt-out flaps (catalogue cut-out p. 135, photo 3.06)."""
    W, B, H = 812, 382, 1044
    p, m = carcass(W, B, H), []
    shoe_block(p, m, T, W - T, B, H)
    p += feet(W, B)
    return dump("veres-3-06", [W, B, H], p, m)


def m_3_08():
    """Тумба для обуви 1208×382×1044: the 3.06 block on the left, a column with an open niche over a door on the right."""
    W, B, H = 1208, 382, 1044
    xp = 812                     # the partition 812..828 (the front-on photo and the cut-out: the flap block ≈ 0.69 L)
    p, m = carcass(W, B, H, backs=[xp + 8]), []
    p.append({"id": "partition", "box": [xp, FEET + T, 10, xp + TI, H - T, B]})
    shoe_block(p, m, T, xp, B, H)
    p.append({"id": "niche-shelf", "box": [xp + TI, 841, 10, W - T, 857, B]})
    p.append(shelf("shelf", xp + TI, W - T, 450, B))
    door(p, m, "door", xp + TI + 2, W - T - 2, Y0, 838, B, "right", 700)
    p += feet(W, B, extra_x=[xp - 12])
    return dump("veres-3-08", [W, B, H], p, m)


def m_3_05():
    """Тумба для обуви 1064×382×627: a low bench part (450) with a tilt-out flap and an upstand board behind it; a column
    (drawer over a door) on the right (photos 3.05 /1, /2)."""
    W, B, H, HL = 1064, 382, 627, 450
    xp = 636                                   # the column's left side 636..652 (16)
    p, m = [], []
    p += [
        {"id": "bottom", "box": [0, FEET, 0, W, FEET + T, B]},
        {"id": "side-l", "box": [0, FEET + T, 0, T, HL - T, B]},
        {"id": "top-low", "box": [0, HL - T, 16, xp, HL, B]},                   # the bench top in front of the upstand
        {"id": "upstand", "box": [0, HL - T, 0, xp, H, 16]},                    # the back board rising to the full height
        {"id": "partition", "box": [xp, FEET + T, 0, xp + TI, H - T, B]},
        {"id": "top", "box": [xp, H - T, 0, W, H, B]},
        {"id": "side-r", "box": [W - T, FEET + T, 0, W, H - T, B]},
        {"id": "back-low", "kind": "back", "box": [T - 10, FEET + T - 10, 6, xp + 6, HL - T + 10, 9.5]},
        {"id": "back-col", "kind": "back", "box": [xp + 10, FEET + T - 10, 6, W - T + 10, H - T + 10, 9.5]},
    ]
    flap(p, m, "flap", T + 2, xp - 2, Y0, HL - T - 2, B, T, xp, depth=200)
    p.append({"id": "rail", "box": [xp + TI, 413, 10, W - T, 429, B - FT]})
    p.append(shelf("shelf", xp + TI, W - T, 240, B))
    drawer(p, m, "drawer", xp + TI + 2, W - T - 2, 432, H - T - 2, B, xp + TI, W - T, depth=300)
    door(p, m, "door", xp + TI + 2, W - T - 2, Y0, 429, B, "right", 338)
    p += feet(W, B, extra_x=[420])
    return dump("veres-3-05", [W, B, H], p, m)


def m_3_01():
    """Шкаф для одежды 2д 991×597×2020: two doors, hat shelf + rail, a back rail at mid-height, a low shelf (photos 3.01)."""
    W, B, H = 991, 597, 2020
    p, m = carcass(W, B, H), []
    p.append(shelf("hat-shelf", T, W - T, 1790, B))
    p.append({"id": "rail", "kind": "tube", "mat": "chrome", "box": [T, 1720, 270, W - T, 1745, 295]})
    p.append({"id": "back-rail", "box": [T, 1150, 9.5, W - T, 1250, 25.5]})
    p.append(shelf("shelf", T, W - T, 455, B))
    mid = W / 2
    door(p, m, "door_left", T + 2, mid - 1.5, Y0, H - T - 2, B, "left", 1010)
    door(p, m, "door_right", mid + 1.5, W - T - 2, Y0, H - T - 2, B, "right", 1010)
    p += feet(W, B)
    return dump("veres-3-01", [W, B, H], p, m)


def hanger(did, H, shelf_top, hooks):
    """Вешалка 794×311×H: a «каньон» wall board 25 (730 wide, 32 in from the shelf ends), a shelf 25 × 286, chrome double hooks."""
    W, B = 794, 311
    p = [
        {"id": "board", "box": [32, 0, 0, W - 32, H, T], "grain": "y"},     # the board is narrower than the shelf
        {"id": "shelf", "box": [0, shelf_top - T, T, W, shelf_top, B]},
    ]
    for i, (x, y) in enumerate(hooks):
        # a chrome double hook: a foot plate on the board, a long arm down-and-out, a short arm up-and-out
        k = f"hook-{i + 1}"
        p.append({"id": k, "kind": "panel", "mat": "chrome", "edge": 3, "box": [x - 9, y - 20, T, x + 9, y + 25, T + 4]})
        p.append({"id": k + "-low", "kind": "rod", "mat": "chrome", "from": [x, y - 5, T + 4], "to": [x, y - 45, T + 60], "d": 8})
        p.append({"id": k + "-tip", "kind": "rod", "mat": "chrome", "from": [x, y - 45, T + 60], "to": [x, y - 25, T + 72], "d": 8})
        p.append({"id": k + "-up", "kind": "rod", "mat": "chrome", "from": [x, y + 15, T + 4], "to": [x, y + 40, T + 34], "d": 7})
    return dump(did, [W, B, H], p, [])


def m_3_14():
    """Зеркало 496×22×1000: a «каньон» board 16 with a bevelled mirror 4 glued on, border 45 at the sides and bottom, 38 at the top (photo 3.14)."""
    W, B, H = 496, 22, 1000
    p = [
        {"id": "board", "box": [0, 0, 0, W, H, TI], "grain": "y"},
        {"id": "mirror", "kind": "mirror", "box": [45, 45, TI + 2, W - 45, H - 38, B]},
    ]
    return dump("veres-3-14", [W, B, H], p, [])


# ------------------------------------------------------------------------------------------------------ catalogue
FIN = "veres-bordo-kanon"
MODELS = [
    ("3.18", "Вешалка «Верес»", "hall", [794, 311, 1370], {"mount": "wall"}),
    ("3.14", "Зеркало «Верес»", "decor", [496, 22, 1000], {"mount": "wall"}),
    ("3.10", "Тумба для обуви «Верес»", "hall", [496, 401, 867], {}),
    ("3.09", "Тумба для обуви «Верес»", "hall", [794, 401, 450], {"note": "по фото; с мягким сиденьем"}),
    ("3.01", "Шкаф для одежды 2д «Верес»", "hall", [991, 597, 2020], {}),
    ("3.07", "Тумба для обуви «Верес»", "hall", [812, 382, 1258], {}),
    ("3.06", "Тумба для обуви «Верес»", "hall", [812, 382, 1044], {}),
    ("3.08", "Тумба для обуви «Верес»", "hall", [1208, 382, 1044], {}),
    ("3.17", "Вешалка «Верес»", "hall", [794, 311, 2020], {"mount": "wall"}),
    ("3.05", "Тумба для обуви «Верес»", "hall", [1064, 382, 627], {"note": "по фото; сайт пишет L1046, каталог L1064"}),
]


def catalog():
    models = []
    for code, name, cat, size, extra in MODELS:
        e = {"id": "veres-" + code.replace(".", "-"), "code": "П3.564." + code, "name": name, "collection": "veres",
             "category": cat, "size": size, "page": 135, "note": "по каталогу и фото сайта, без инструкции"}
        e.update(extra)
        if "note" in extra:
            e["note"] = "по каталогу и фото сайта, без инструкции; " + extra["note"].replace("по фото; ", "")
        models.append(e)
    return {
        "finishes": [
            {"id": FIN, "name": "Дуб бордо лайт / Дуб каньон", "body": "door_enamel_whitey#7f6951",
             "front": "door_enamel_whitey#dbd8d7", "swatch": "#dbd8d7", "roles": {"fabric": "velvet#4a3a33"}}
        ],
        "profiles": {},
        "collections": [
            {"id": "veres", "name": "Верес", "brand": "Пинскдрев", "finishes": [FIN], "metal": "chrome",
             "note": "Каталог «Корпусная мебель ч. II» 2025, с. 135 (разворот 266–267) и фото сайта pinskdrev.by; все модули "
                     "по каталогу / фото, без инструкций. Рамка корпуса ЛДСП 25 «Дуб каньон» на пластиковых опорах 18 мм, "
                     "вкладные фасады ЛДСП 16 «Дуб бордо лайт» (ящики и откидная полка 3.07 — «Дуб каньон»), откидные "
                     "обувницы с решёткой, ручки-скобы 128 мм сатин-хром, задние стенки ХДФ в пазах."}
        ],
        "models": models,
    }


def write_catalog():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "veres_catalog.json")
    with open(path, "w") as fh:
        json.dump(catalog(), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


if __name__ == "__main__":
    print(write_catalog())
    print(m_3_10())
    print(m_3_09())
    print(m_3_07())
    print(m_3_06())
    print(m_3_08())
    print(m_3_05())
    print(m_3_01())
    print(hanger("veres-3-17", 2020, 1791, [(170, 1580), (397, 1580), (624, 1580), (284, 895), (510, 895)]))
    print(hanger("veres-3-18", 1370, 1174, [(132, 970), (397, 970), (662, 970)]))
    print(m_3_14())
