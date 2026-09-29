"""«Симпл» (Pinskdrev П7.058, hall set): both modules by catalogue + product photos (no instructions exist).

Sources: catalogue p. 133 (printed 262–263: one interior photo of each module, nearly front-on; no swatches) and the
product photos on pinskdrev.by (front-on, 3/4, open). x is scaled by the catalogue L, y by H (the site photos are printed
4–7 % wider than true).

Construction (one scheme, measured on the front-on photos):
* ЛДСП 16 «Дуб Кантри золотой» carcasses on splayed tapered wooden legs; fronts ЛДСП 16 overlaid;
* 3.10: two tall panels (the coat and mirror boards) standing on the bottom behind a bench (open, one shelf) and a
  cabinet (a drawer over two drop-down flaps on gas struts, pearl fronts); a shelf with three black hooks on top, a
  facetted mirror glued on the right board;
* 3.11: a base of two wide drawers (oak fronts) whose top is the seat; on it an open coat niche (pearl back, hat shelf,
  three hooks) and a closet with four shelves behind a pearl door carrying a mirror;
* black round knobs, black steel hooks; backs ХДФ «Персидский жемчуг» (the open photos).

    python3 tools/casegoods/gen/simpl.py        # writes Designs/simpl-*.json and gen/simpl_catalog.json
"""
import json
import os

from common import dump

T = 16
HERE = os.path.dirname(os.path.abspath(__file__))


def knob(hid, x, y, z):
    return {"id": hid, "kind": "handle", "model": "knob", "mat": "metal", "at": [x, y], "d": 22, "t": 12, "standoff": 16, "z": z}


def hook(hid, xc, y0, zw=T):
    """A black L hook 60 high seen from the side (z, y): a flat bar on the board, its foot turned out 30 at the bottom."""
    return {"id": hid, "mat": "black", "edge": 1, "box": [xc - 6, y0, zw, xc + 6, y0 + 60, zw + 30], "shape": "path",
            "outline": f"M {zw} {y0} L {zw + 30} {y0} L {zw + 30} {y0 + 10} L {zw + 10} {y0 + 10} L {zw + 10} {y0 + 54} "
                       f"Q {zw + 10} {y0 + 60} {zw + 5} {y0 + 60} L {zw} {y0 + 60} Z"}


def legs(spots, h):
    """Tapered wooden legs splayed outwards: rods from (top x, z) at the carcass' underside to (foot x, z) on a 3 mm felt
    glide (the glide gives the floor line to the checker; the rods stay out of the extent)."""
    out = []
    for i, ((xt, zt), (xf, zf)) in enumerate(spots):
        out.append({"id": f"leg-{i + 1}", "kind": "rod", "mat": "body", "from": [xt, h, zt], "to": [xf, 3, zf], "d": 36, "d2": 24})
        out.append({"id": f"glide-{i + 1}", "mat": "black", "edge": 1, "box": [xf - 10, 0, zf - 10, xf + 10, 3, zf + 10]})
    return out


def drawer_box(tag, x0, x1, y0, h, z0, z1):
    return [
        {"id": f"dr-l-{tag}", "box": [x0, y0, z0, x0 + T, y0 + h, z1]},
        {"id": f"dr-r-{tag}", "box": [x1 - T, y0, z0, x1, y0 + h, z1]},
        {"id": f"dr-b-{tag}", "box": [x0 + T, y0, z0, x1 - T, y0 + h, z0 + T]},
        {"id": f"dr-bottom-{tag}", "kind": "back", "box": [x0 + 10, y0 + 8, z0 + 4, x1 - 10, y0 + 11.5, z1 - 2]},
    ]


def simpl_3_10():
    """Шкаф комбинированный 1026×440×2200 (photos 0–2 of 3-10; catalogue p. 133 left)."""
    W, D, H = 1026, 440, 2200
    LEG = 134
    yb = LEG + T                                       # 150
    XC = 500                                           # bench | cabinet
    ZF = D - T                                         # cabinet fronts' back face
    p, m = [], []
    p += [
        # the two tall boards (coat board and mirror board) on the floor line of the carcass, against the wall
        {"id": "board-l", "box": [50, LEG, 0, XC, H, T]},
        {"id": "board-r", "box": [XC, LEG, 0, 977, H, T]},
        {"id": "shelf-top", "box": [27, 2045, T, 998, 2061, 216]},
        {"id": "mirror", "kind": "mirror", "box": [514, 1203, T, 962, 1880, T + 4]},
        # bench (open box, one shelf)
        {"id": "bench-side", "box": [0, LEG, T, T, 440, D]},
        {"id": "bench-bottom", "box": [T, LEG, T, XC, yb, D]},
        {"id": "bench-shelf", "box": [T, 288, T, XC, 304, D]},
        {"id": "bench-top", "box": [0, 440, T, XC, 456, D]},
        # cabinet
        {"id": "cab-side-l", "box": [XC, LEG, T, XC + T, 973, ZF]},
        {"id": "cab-side-r", "box": [W - T, LEG, T, W, 973, ZF]},
        {"id": "cab-bottom", "box": [XC + T, LEG, T, W - T, yb, ZF]},
        {"id": "cab-top", "box": [XC, 973, T, W, 989, D]},
        {"id": "cab-shelf-1", "box": [XC + T, 438, T, W - T, 454, ZF - 2]},
        {"id": "cab-shelf-2", "box": [XC + T, 762, T, W - T, 778, ZF - 2]},
    ]
    for i, xc in enumerate([116, 272, 424]):
        p.append(hook(f"hook-{i + 1}", xc, 1900 if i == 1 else 1950))
    fx = (XC + 1.5, W - 1.5)
    for tag, (y0, y1) in (("2", (125, 445)), ("1", (448, 768))):
        f = {"id": f"flap-{tag}", "kind": "front", "box": [fx[0], y0, ZF, fx[1], y1, D]}
        k = knob(f"k-flap-{tag}", (fx[0] + fx[1]) / 2, y1 - 20, D)
        p += [f, k]
        m.append({"type": "flap", "name": f"flap_{tag}", "parts": [f["id"], k["id"]], "hinge": "bottom", "angle": 90})
    f = {"id": "front-drawer", "kind": "front", "box": [fx[0], 771, ZF, fx[1], 971, D]}
    k = knob("k-drawer", (fx[0] + fx[1]) / 2, 871, D)
    box = drawer_box("1", XC + T + 13, W - T - 13, 790, 120, 40, ZF)
    p += [f, k] + box
    m.append({"type": "drawer", "name": "drawer", "parts": [f["id"], k["id"]] + [q["id"] for q in box], "travel": 300})
    p += legs([((45, D - 45), (20, D - 20)), ((45, 61), (20, 36)), ((W - 45, D - 45), (W - 20, D - 20)),
               ((W - 45, 61), (W - 20, 36)), ((XC, 61), (XC, 36))], LEG)
    return dump("simpl-3-10", [W, D, H], p, m)


def simpl_3_11():
    """Шкаф комбинированный 994×420×2200 (photos 0–2 of 3-11; catalogue p. 133 right)."""
    W, D, H = 994, 420, 2200
    LEG = 122
    ZF = D - T                                         # base fronts' back face (404)
    ZU = 400                                           # upper carcass depth: door 16 + mirror 4 in front
    p, m = [], []
    # base: two wide drawers, the top is the seat
    p += [
        {"id": "base-side-l", "box": [0, LEG, 0, T, 612, ZF]},
        {"id": "base-side-r", "box": [W - T, LEG, 0, W, 612, ZF]},
        {"id": "base-bottom", "box": [T, LEG, 0, W - T, LEG + T, ZF]},
        {"id": "base-top", "box": [0, 612, 0, W, 628, D]},
        {"id": "base-back", "kind": "back", "box": [10, LEG + 10, 6, W - 10, 618, 9.5]},
    ]
    for tag, (y0, y1) in (("2", (122, 364.5)), ("1", (367.5, 609))):
        f = {"id": f"front-{tag}", "kind": "front", "mat": "body", "box": [1.5, y0, ZF, W - 1.5, y1, D]}
        ks = [knob(f"k-{tag}{s}", x, (y0 + y1) / 2, D) for s, x in (("a", 245), ("b", 749))]
        box = drawer_box(tag, T + 13, W - T - 13, y0 + 20, 160, 20, ZF)
        p += [f] + ks + box
        m.append({"type": "drawer", "name": f"drawer_{tag}", "parts": [f["id"]] + [q["id"] for q in ks + box], "travel": 300})
    # upper: coat niche | closet
    y0, yt = 628, 2183
    p += [
        {"id": "side-l", "box": [48, y0, 0, 64, yt, ZU]},
        {"id": "partition", "box": [545, y0, 0, 561, yt, ZU]},
        {"id": "side-r", "box": [W - T, y0, 0, W, yt, ZU]},
        {"id": "top", "box": [23, yt, 0, W, H, D]},
        {"id": "back-niche", "kind": "back", "box": [58, y0 - 6, 6, 551, yt + 6, 9.5]},
        {"id": "back-closet", "kind": "back", "box": [555, y0 - 6, 6, W - 10, yt + 6, 9.5]},
        {"id": "shelf-hat", "box": [64, 2014, 10, 545, 2030, 260]},
    ]
    for i, xc in enumerate([141, 305, 469]):
        p.append(hook(f"hook-{i + 1}", xc, 1925, zw=9.5))
    for i, yy in enumerate([1840, 1560, 1290, 940]):
        p.append({"id": f"shelf-{i + 1}", "box": [562, yy - T, 20, W - T - 1, yy, ZU - 10]})
    door = [
        {"id": "door", "kind": "front", "box": [563, 631, ZU, W - 1.5, 2180, ZU + T]},
        {"id": "door-mirror", "kind": "mirror", "box": [604, 640, ZU + T, 985, 2095, D]},
        knob("k-door", 581, 1393, ZU + T),
    ]
    p += door
    m.append({"type": "door", "name": "door", "parts": [q["id"] for q in door], "hinge": "right", "angle": 100})
    p += legs([((42, D - 45), (24, D - 25)), ((42, 45), (24, 25)), ((W - 42, D - 45), (W - 24, D - 25)),
               ((W - 42, 45), (W - 24, 25))], LEG)
    return dump("simpl-3-11", [W, D, H], p, m)


NOTE = "по каталогу и фото сайта, без инструкции"


def catalog():
    frag = {
        "finishes": [{
            "id": "simpl-kantri-zhemchug", "name": "Дуб Кантри золотой / Персидский жемчуг",
            "body": "door_enamel_whitey#b39266", "front": "door_enamel_whitey#dfe3e2", "back": "door_enamel_whitey#dfe3e2",
            "swatch": "#b39266",
        }],
        "profiles": {},
        "collections": [{
            "id": "simpl", "name": "Симпл", "brand": "Пинскдрев", "finishes": ["simpl-kantri-zhemchug"], "metal": "black",
            "note": "Каталог «Корпусная мебель ч. II» 2025, с. 133 (разворот 262–263) и фото сайта pinskdrev.by; инструкций нет — "
                    "всё по каталогу и фото. Корпус ЛДСП 16 «Дуб Кантри золотой» на разведённых конических деревянных опорах, "
                    "накладные фасады (у 3.10 и дверь 3.11 — «Персидский жемчуг», ящики 3.11 — дуб), чёрные ручки-кнопки и "
                    "крючки, зеркала с фацетом, задние стенки ХДФ «Персидский жемчуг».",
        }],
        "models": [
            {"id": "simpl-3-10", "code": "П7.058.3.10", "name": "Шкаф комбинированный «Симпл»", "collection": "simpl",
             "category": "hall", "size": [1026, 440, 2200], "page": 133, "note": NOTE + "; сайт B444 — взят каталог"},
            {"id": "simpl-3-11", "code": "П7.058.3.11", "name": "Шкаф комбинированный «Симпл»", "collection": "simpl",
             "category": "hall", "size": [994, 420, 2200], "page": 133, "note": NOTE + "; сайт B431 — взят каталог"},
        ],
    }
    path = os.path.join(HERE, "simpl_catalog.json")
    with open(path, "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


if __name__ == "__main__":
    print(simpl_3_10())
    print(simpl_3_11())
    print(catalog())
