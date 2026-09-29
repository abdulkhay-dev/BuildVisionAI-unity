"""«Плато» (П3.403.0.22) coffee table transformer, by catalogue (no instruction, no product page).

Source: catalogue p. 140 (printed 276–277: the interior with the table raised and unfolded, three cut-outs — folded,
raised with the leaf opening, raised and unfolded — and five decors). Measured on the cut-outs (scale: the folded
L745 / H500, the unfolded L1490 / H770).

Construction: a box of ЛДСП 16 on four castors 50 — a base board, two full-height sides (x), a back, an open niche
(184 high) under a fixed shelf, the front panel of the upper box (218) over the niche; the top is two leaves ЛДСП 16
745 × 800 lying one on the other (folded: 468…500). Inside the box two black lift mechanisms (base rails on the shelf,
arms, a plate under the leaves).
Moves: «lift» raises the mechanisms' plates and upper arms by 286; «unfold_a» / «unfold_b» raise the lower leaf by 286
and the upper leaf by 270 and slide them apart by ±372.5, so the unfolded top is 1490 × 800 at 754…770 centred over the
box — the catalogue's H770 / L1490. The real mechanism is a pair of scissor arms and the upper leaf flips over like a book
page; the engine has only straight slides (the arms telescope visibly, the leaf does not turn over).

    python3 tools/casegoods/gen/plato.py        # writes Designs/plato-0-22.json and gen/plato_catalog.json
"""
import json
import os

from common import dump

T = 16
W, B, H = 745, 800, 500
CAST = 50
YTOP = H - 2 * T                 # 468: the box's top edge, the lower leaf on it


def m_0_22():
    x0, x1, z0, z1 = 32, 713, 30, 770           # the box
    ys = 250                                     # the fixed shelf's underside (niche 66…250)
    p = [{"id": "base", "box": [x0, CAST, z0, x1, CAST + T, z1], "grain": "x"},
         {"id": "side-l", "box": [x0, CAST + T, z0, x0 + T, YTOP, z1], "grain": "x"},
         {"id": "side-r", "box": [x1 - T, CAST + T, z0, x1, YTOP, z1], "grain": "x"},
         {"id": "back", "box": [x0 + T, CAST + T, z0, x1 - T, YTOP, z0 + T], "grain": "x"},
         {"id": "shelf", "box": [x0 + T, ys, z0 + T, x1 - T, ys + T, z1 - T], "grain": "x"},
         {"id": "front", "box": [x0 + T, ys, z1 - T, x1 - T, YTOP, z1], "grain": "x"}]
    for i, (x, z) in enumerate([(x0 + 40, z0 + 40), (x1 - 40, z0 + 40), (x0 + 40, z1 - 40), (x1 - 40, z1 - 40)]):
        p.append({"id": f"castor-{i + 1}", "kind": "tube", "mat": "black", "box": [x - 18, 0, z - 18, x + 18, CAST, z + 18]})
    leaf_a = {"id": "leaf-a", "box": [0, YTOP, 0, W, YTOP + T, B], "edge": 2, "grain": "x"}
    leaf_b = {"id": "leaf-b", "box": [0, YTOP + T, 0, W, H, B], "edge": 2, "grain": "x"}
    p += [leaf_a, leaf_b]
    lift = []
    yb = ys + T                                   # 248: the shelf's top
    for u, (ux0, ux1) in enumerate([(70, 360), (385, 675)]):
        tag = f"mech{u + 1}"
        for k, xr in enumerate([ux0 + 10, ux1 - 30]):
            p.append({"id": f"{tag}-rail-{k + 1}", "mat": "metal", "edge": 0.5, "box": [xr, yb, 110, xr + 20, yb + 10, 690]})
        plate = {"id": f"{tag}-plate", "mat": "metal", "edge": 1, "box": [ux0, YTOP - 8, 180, ux1, YTOP, 620]}
        p.append(plate)
        lift.append(plate["id"])
        for k, (ax, az) in enumerate([(ux0 + 20, 200), (ux1 - 20, 200), (ux0 + 20, 600), (ux1 - 20, 600)]):
            p.append({"id": f"{tag}-arm-lo-{k + 1}", "kind": "rod", "mat": "metal", "from": [ax, yb + 10, az + 30],
                      "to": [ax, YTOP - 8, az + 30], "d": 20, "section": "square"})
            arm = {"id": f"{tag}-arm-up-{k + 1}", "kind": "rod", "mat": "metal", "from": [ax, yb + 10, az],
                   "to": [ax, YTOP - 8, az], "d": 20, "section": "square"}
            p.append(arm)
            lift.append(arm["id"])
    m = [{"type": "slide", "name": "lift", "parts": lift, "by": [0, 286, 0]},
         {"type": "slide", "name": "unfold_a", "parts": ["leaf-a"], "by": [-372.5, 286, 0]},
         {"type": "slide", "name": "unfold_b", "parts": ["leaf-b"], "by": [372.5, 270, 0]}]
    return dump("plato-0-22", [W, B, H], p, m)


DECORS = [
    ("plato-dub-votan", "Дуб Вотан", "#9b7146"),
    ("plato-dub-tryufelnyy", "Дуб Трюфельный", "#9c886c"),
    ("plato-venge", "Венге", "#2d211b"),
    ("plato-dub-kanon", "Дуб Каньон", "#8b6c4f"),
    ("plato-sosna-kareliya", "Сосна Карелия", "#e7e7e1"),
]


def catalog():
    fins = [{"id": i, "name": n, "body": f"door_enamel_whitey{c}", "swatch": c} for i, n, c in DECORS]
    return {
        "finishes": fins, "profiles": {},
        "collections": [{"id": "plato", "name": "Плато", "brand": "Пинскдрев", "finishes": [f["id"] for f in fins],
                         "metal": "black",
                         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 140 (разворот 276–277); без инструкции и без "
                                 "страницы на сайте. Журнальный стол-трансформер: короб ЛДСП 16 на колёсах, две створки "
                                 "столешницы 745 × 800, подъёмные механизмы (чёрные) — поднимается до 770 и раскладывается "
                                 "до 1490."}],
        "models": [{"id": "plato-0-22", "code": "П3.403.0.22", "name": "Стол журнальный «Плато» (трансформер)",
                    "collection": "plato", "category": "living", "size": [W, B, H], "page": 140,
                    "note": "по каталогу, без инструкции; размер — в сложенном виде (L745×B800×H500), в разложенном виде "
                            "L1490×B800×H770 (index.json писал L1490 — исправлено)"}],
    }


def write_catalog():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "plato_catalog.json")
    with open(path, "w") as fh:
        json.dump(catalog(), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


if __name__ == "__main__":
    print(write_catalog())
    print(m_0_22())
