"""«Лари» (П3.977) dining tables 4.01 and 4.02, by catalogue / by photo (no instructions exist).

Sources: catalogue p. 137 (printed 270–271: the interior with 4.02, the cut-outs of 4.01 and of 4.02 folded / unfolded,
the four top decors) and the product photos of pinskdrev.by (4.01: two views — one frame face-on; 4.02: four views,
folded and unfolded). Scale: the top Ø1000 on the photos (x) and the height (y), separately.

* Tops ЛДСП 25 (the edge measures 24–26 mm on the photos), round Ø1000, 2 mm ПВХ edge.
* 4.01 (1000 × 1000 × 765): the base is two welded frames of black square tube crossing at 90° under the centre — each a
  top rail 40 under the top, two legs 60 × 60 splayed outwards (outer width 757 at the top, 906 at the floor, 7.5°) and a
  floor rail 40; the frames' floor rails cross in an X (the photos).
* 4.02 (1000/1390 × 1000 × 770): the top is split across the middle and its halves run out on a black steel frame (an
  apron 820 × 540 × 110 under the top) — 195 mm each; the insert 390 × 1000 (a butterfly leaf, two 390 × 500 halves)
  lies folded inside the frame and rises into the gap. The base: a square column 120 under the frame and four legs
  50 × 50 splayed to the diagonals (feet ≈ 330 from the centre, the photos).

    python3 tools/casegoods/gen/lari.py        # writes Designs/lari-*.json and gen/lari_catalog.json
"""
import json
import os

from common import dump

TT = 25
R = 500
K = 0.5523 * R


def circle_half(side):
    """Half of the Ø1000 top in the top plane: side -1 = the left half (x 0..500), +1 = the right half."""
    if side < 0:
        return (f"M 500 0 C {500 - K:.1f} 0 0 {500 - K:.1f} 0 500 C 0 {500 + K:.1f} {500 - K:.1f} 1000 500 1000 Z")
    return (f"M 500 0 C {500 + K:.1f} 0 1000 {500 - K:.1f} 1000 500 C 1000 {500 + K:.1f} {500 + K:.1f} 1000 500 1000 Z")


def rod(pid, a, b, d, section="square", mat="metal", box=None):
    r = {"id": pid, "kind": "rod", "mat": mat, "from": [round(v, 1) for v in a], "to": [round(v, 1) for v in b], "d": d,
         "section": section}
    if box:
        r["box"] = box
    return r


def m_4_01():
    W, H = 1000, 765
    yt = H - TT
    p = [{"id": "top", "shape": "circle", "box": [0, yt, 0, W, H, W], "edge": 2, "grain": "x"}]
    c = 500
    for fname, axis in (("a", "x"), ("b", "z")):
        def P3(u, y):
            return [c + u, y, c] if axis == "x" else [c, y, c + u]
        top_u, foot_u = 378.5 - 30, 453 - 30       # leg centre lines (outer 757 at the top, 906 at the floor)
        p.append(rod(f"frame-{fname}-top", P3(-top_u - 30, yt - 20), P3(top_u + 30, yt - 20), 40))
        for s, nm in ((-1, "l"), (1, "r")):
            p.append(rod(f"frame-{fname}-leg-{nm}", P3(s * top_u, yt - 40), P3(s * foot_u, 40), 60))
        fb = [c - 453, 0, c - 20, c + 453, 40, c + 20] if axis == "x" else [c - 20, 0, c - 453, c + 20, 40, c + 453]
        p.append(rod(f"frame-{fname}-floor", P3(-453, 20), P3(453, 20), 40, box=fb))
    return dump("lari-4-01", [W, W, H], p, [])


def m_4_02():
    W, H = 1000, 770
    yt = H - TT
    AH = 110                                        # the frame (apron) under the top
    ya = yt - AH
    p, m = [], []
    tl = {"id": "top-left", "box": [0, yt, 0, 500, H, W], "edge": 2, "grain": "x", "shape": "path", "outline": circle_half(-1)}
    tr = {"id": "top-right", "box": [500, yt, 0, W, H, W], "edge": 2, "grain": "x", "shape": "path", "outline": circle_half(1)}
    p += [tl, tr]
    # the steel frame: two long runners (along x) and two end rails, black
    x0, x1, z0, z1 = 90, 910, 230, 770
    p += [{"id": "frame-front", "mat": "metal", "edge": 1, "box": [x0, ya, z1 - 16, x1, yt, z1]},
          {"id": "frame-back", "mat": "metal", "edge": 1, "box": [x0, ya, z0, x1, yt, z0 + 16]},
          {"id": "frame-end-l", "mat": "metal", "edge": 1, "box": [x0, ya, z0 + 16, x0 + 16, yt, z1 - 16]},
          {"id": "frame-end-r", "mat": "metal", "edge": 1, "box": [x1 - 16, ya, z0 + 16, x1, yt, z1 - 16]},
          {"id": "hub", "mat": "metal", "edge": 1, "box": [x0 + 16, ya, 440, x1 - 16, ya + 10, 560]}]
    # the insert (butterfly leaf 390 × 1000 = two halves 390 × 500), stored folded inside the frame
    la = {"id": "leaf-a", "box": [305, yt - 2 - TT, 250, 695, yt - 2, 750], "edge": 2, "grain": "z"}
    lb = {"id": "leaf-b", "box": [305, yt - 4 - 2 * TT, 250, 695, yt - 4 - TT, 750], "edge": 2, "grain": "z"}
    p += [la, lb]
    # column and four legs to the diagonals
    yc0 = 470
    p.append({"id": "column", "kind": "panel", "mat": "metal", "edge": 2, "box": [440, yc0, 440, 560, ya, 560]})
    k = 0
    for sx in (-1, 1):
        for sz in (-1, 1):
            k += 1
            top = [500 + sx * 40, yc0 + 60, 500 + sz * 40]
            foot = [500 + sx * 233, 25, 500 + sz * 233]
            p.append(rod(f"leg-{k}", top, foot, 50))
            p.append({"id": f"foot-{k}", "kind": "tube", "mat": "black",
                      "box": [foot[0] - 22, 0, foot[2] - 22, foot[0] + 22, 8, foot[2] + 22]})
    m += [{"type": "slide", "name": "extend_left", "parts": ["top-left"], "by": [-195, 0, 0]},
          {"type": "slide", "name": "extend_right", "parts": ["top-right"], "by": [195, 0, 0]},
          {"type": "slide", "name": "leaf_a", "parts": ["leaf-a"], "by": [0, 2 + TT, 250]},
          {"type": "slide", "name": "leaf_b", "parts": ["leaf-b"], "by": [0, 4 + 2 * TT, -250]}]
    return dump("lari-4-02", [W, W, H], p, m)


# ------------------------------------------------------------------------------------------------------ catalogue
DECORS = [
    ("lari-beton-layt", "Бетон Лайт 818ТМ", "#cdcac4"),
    ("lari-mramor-nero", "Мрамор Неро Маркина 850ТМ", "#292929"),
    ("lari-dub-ontario", "Дуб Онтарио 385ТМ", "#a08357"),
    ("lari-dub-kanzas", "Дуб Канзас 377ТМ", "#74543b"),
]


def catalog():
    fins = [{"id": i, "name": n, "body": f"door_enamel_whitey{c}", "swatch": c} for i, n, c in DECORS]
    return {
        "finishes": fins, "profiles": {},
        "collections": [{"id": "lari", "name": "Лари", "brand": "Пинскдрев", "finishes": [f["id"] for f in fins],
                         "metal": "black",
                         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 137 (разворот 270–271) и фото pinskdrev.by; без "
                                 "инструкций. Круглые столешницы ЛДСП 25 Ø1000 (4 декора), опоры — металл (чёрный)."}],
        "models": [
            {"id": "lari-4-01", "code": "П3.977.4.01", "name": "Стол «Лари»", "collection": "lari", "category": "tables",
             "size": [1000, 1000, 765], "page": 137,
             "note": "по каталогу и фото сайта, без инструкции; подстолье — две рамы из профильной трубы крест-накрест"},
            {"id": "lari-4-02", "code": "П3.977.4.02", "name": "Стол «Лари» раздвижной", "collection": "lari",
             "category": "tables", "size": [1000, 1000, 770], "page": 137,
             "note": "по каталогу и фото сайта, без инструкции; размер — в сложенном виде, в разложенном виде L1390 "
                     "(вставка 390; сайт пишет 1350 — принят каталог); опора — колонна и четыре ноги по диагоналям"},
        ],
    }


def write_catalog():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lari_catalog.json")
    with open(path, "w") as fh:
        json.dump(catalog(), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


if __name__ == "__main__":
    print(write_catalog())
    print(m_4_01())
    print(m_4_02())
