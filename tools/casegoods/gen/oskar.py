"""«Оскар» (П7.040) tables: coffee tables 0.53, 0.54, 0.55 and extending dining tables 4.51, 4.52, by catalogue / photo.

Sources: catalogue p. 141 (printed 278–279: the interior with 4.51 «Сосна Карелия», the cut-outs of all five — the dining
tables folded and unfolded —, the swatches «Сосна Карелия» / «Дуб Каньон»; the «Крашение» lines on the page belong to
the chairs) and the product photos of pinskdrev.by (4.51: four views, «П040.512»; 4.52: folded and unfolded; 0.53, 0.54:
one view each; 0.55: two views). No instructions exist. Scale: the known L / H on each photo, x and y separately.

* 4.51 (1100/1600 × 700 × 750): top ЛДСП 22 with rounded ends (corners R 150), split across the middle; the halves run
  out 250 each on runners in the apron (ЛДСП 16, 100 high) and a butterfly insert 500 × 700 (two 500 × 350 halves,
  stored folded in the apron) rises into the gap. Four bent steel tube legs Ø40, painted white (a bow bulging ≈ 20 mm
  outwards), black glides.
* 4.52 (800/1200 × 600/800 × 750): a swivel-flip top — two leaves ЛДСП 16 800 × 600 lying one on the other on a small
  apron frame; unfolded they make 1200 × 800 (the top turns 90° and the upper leaf flips over). The engine has only
  straight slides: «unfold» moves the leaves apart along z into an 800 × 1200 top (the unfolded top, not turned).
  The same legs as 4.51.
* 0.55 (670 × 550 × 750): two crescent side boards (C-shaped, open to the front, 16) on a D-shaped base on castors, two
  shelves between them, a D-shaped top.
* 0.53 (450 × 450 × 650): a round base Ø450 on castors, a hollow column (two side boards and two framed boards with a
  window), a round top Ø450 with a black glass Ø440 on it.
* 0.54 (340 × 430 × 662): a C-shaped side table — base, an upright at the back end, a middle rib, the top.

    python3 tools/casegoods/gen/oskar.py        # writes Designs/oskar-*.json and gen/oskar_catalog.json
"""
import json
import math
import os

from common import dump

T = 16
LEGS = "legs"                     # finish role: the painted steel legs
GLIDE = "black"


def poly(pts):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def bow_leg(tag, top, knee, foot):
    return [{"id": f"{tag}-a", "kind": "rod", "mat": LEGS, "from": top, "to": knee, "d": 40},
            {"id": f"{tag}-b", "kind": "rod", "mat": LEGS, "from": knee, "to": foot, "d": 40},
            {"id": f"{tag}-glide", "kind": "tube", "mat": GLIDE, "box": [foot[0] - 20, 0, foot[2] - 20, foot[0] + 20, 15, foot[2] + 20]}]


def legs4(xl, xr, zb, zf, ytop, bulge=20):
    """Four bow legs at (xl | xr, zb | zf): the tube bows outwards (along x) by `bulge` at 45 % of the height."""
    out = []
    k = 0
    for x, s in ((xl, -1), (xr, 1)):
        for z in (zb, zf):
            k += 1
            out += bow_leg(f"leg-{k}", [x, ytop, z], [x + s * bulge, 340, z], [x + s * 15, 15, z])
    return out


# ------------------------------------------------------------------------------------------------------------ 4.51
def m_4_51():
    W, B, H = 1100, 700, 750
    TT = 22
    yt = H - TT
    ya = yt - 100
    half = W / 2
    p = [{"id": "top-left", "box": [0, yt, 0, half, H, B], "edge": 2, "grain": "x", "shape": "path",
          "outline": f"M {half} 0 L 150 0 C 40 0 0 60 0 150 L 0 550 C 0 640 40 {B} 150 {B} L {half} {B} Z"},
         {"id": "top-right", "box": [half, yt, 0, W, H, B], "edge": 2, "grain": "x", "shape": "path",
          "outline": f"M {half} 0 L 950 0 C 1060 0 {W} 60 {W} 150 L {W} 550 C {W} 640 1060 {B} 950 {B} L {half} {B} Z"}]
    x0, x1, z0, z1 = 82, 1018, 62, 638
    p += [{"id": "apron-front", "box": [x0, ya, z1 - T, x1, yt, z1], "grain": "x"},
          {"id": "apron-back", "box": [x0, ya, z0, x1, yt, z0 + T], "grain": "x"},
          {"id": "apron-end-l", "box": [x0, ya, z0 + T, x0 + T, yt, z1 - T], "grain": "z"},
          {"id": "apron-end-r", "box": [x1 - T, ya, z0 + T, x1, yt, z1 - T], "grain": "z"},
          {"id": "runner-f", "mat": "metal", "edge": 0.5, "box": [x0 + T, yt - 30, z1 - T - 12, x1 - T, yt, z1 - T]},
          {"id": "runner-b", "mat": "metal", "edge": 0.5, "box": [x0 + T, yt - 30, z0 + T, x1 - T, yt, z0 + T + 12]},
          {"id": "leaf-a", "box": [300, yt - 1 - TT, 175, 800, yt - 1, 525], "edge": 2, "grain": "z"},
          {"id": "leaf-b", "box": [300, yt - 2 - 2 * TT, 175, 800, yt - 2 - TT, 525], "edge": 2, "grain": "z"}]
    p += legs4(60, W - 60, 60, B - 60, yt)
    m = [{"type": "slide", "name": "extend_left", "parts": ["top-left"], "by": [-250, 0, 0]},
         {"type": "slide", "name": "extend_right", "parts": ["top-right"], "by": [250, 0, 0]},
         {"type": "slide", "name": "leaf_a", "parts": ["leaf-a"], "by": [0, 1 + TT, 175]},
         {"type": "slide", "name": "leaf_b", "parts": ["leaf-b"], "by": [0, 2 + 2 * TT, -175]}]
    return dump("oskar-4-51", [W, B, H], p, m)


# ------------------------------------------------------------------------------------------------------------ 4.52
def m_4_52():
    W, B, H = 800, 600, 750
    y1 = H - 2 * T                   # 718: the lower leaf's underside
    ya = y1 - 100
    p = [{"id": "leaf-lower", "box": [0, y1, 0, W, y1 + T, B], "edge": 2, "grain": "x"},
         {"id": "leaf-upper", "box": [0, y1 + T, 0, W, H, B], "edge": 2, "grain": "x"}]
    x0, x1, z0, z1 = 92, 708, 92, 508
    p += [{"id": "apron-front", "box": [x0, ya, z1 - T, x1, y1, z1], "grain": "x"},
          {"id": "apron-back", "box": [x0, ya, z0, x1, y1, z0 + T], "grain": "x"},
          {"id": "apron-end-l", "box": [x0, ya, z0 + T, x0 + T, y1, z1 - T], "grain": "z"},
          {"id": "apron-end-r", "box": [x1 - T, ya, z0 + T, x1, y1, z1 - T], "grain": "z"},
          {"id": "swivel", "mat": "metal", "edge": 1, "box": [340, y1 - 6, 240, 460, y1, 360]}]
    p += legs4(72, W - 72, 72, B - 72, y1)
    m = [{"type": "slide", "name": "unfold_lower", "parts": ["leaf-lower"], "by": [0, 0, -300]},
         {"type": "slide", "name": "unfold_upper", "parts": ["leaf-upper"], "by": [0, -T, 300]}]
    return dump("oskar-4-52", [W, B, H], p, m)


# ------------------------------------------------------------------------------------------------------------ 0.55
def arc(cx, cy, r, y_from, y_to, side, n=24):
    """Points of the circle (cx, cy, r) on its left half (side −1) from y_from to y_to."""
    pts = []
    for i in range(n + 1):
        y = y_from + (y_to - y_from) * i / n
        x = cx + side * math.sqrt(max(r * r - (y - cy) ** 2, 0))
        pts.append((x, y))
    return pts


def m_0_55():
    W, B, H = 670, 550, 750
    CAST = 40
    yb = CAST + T                    # 56
    yt = H - T                       # 734
    cy = (yb + yt) / 2               # 395
    R = 400
    p = [{"id": "base", "box": [60, CAST, 0, W, yb, B], "edge": 2, "grain": "x", "shape": "path",
          "outline": f"M 60 0 L 395 0 C 547 0 {W} 123 {W} 275 C {W} 427 547 {B} 395 {B} L 60 {B} Z"},
         {"id": "top", "box": [110, yt, 35, 640, H, 515], "edge": 2, "grain": "x", "shape": "path",
          "outline": "M 110 35 L 400 35 C 532 35 640 142 640 275 C 640 408 532 515 400 515 L 110 515 Z"}]
    band = 80
    outer = arc(R, cy, R, yb, yt, -1)                               # bottom → top on the left
    inner = arc(R + 160, cy, R, yt - band, yb + band, -1)           # top → bottom
    pts = [outer[-1], (560, yt)] + [(560 + 22 * math.sin(math.pi * t / 8), yt - band * t / 8) for t in range(1, 8)]
    pts += [(560, yt - band)] + inner + [(560, yb + band)]
    pts += [(560 + 22 * math.sin(math.pi * t / 8), yb + band - band * t / 8) for t in range(1, 8)] + [(560, yb)] + outer[:-1]
    out = poly(pts)
    for nm, z0 in (("l", 60), ("r", B - 60 - T)):
        p.append({"id": f"crescent-{nm}", "box": [0, yb, z0, 582, yt, z0 + T], "grain": "y", "shape": "path",
                  "outline": out})
    p += [{"id": "shelf-1", "box": [50, 200, 60 + T, 330, 216, B - 60 - T], "grain": "x"},
          {"id": "shelf-2", "box": [20, 430, 60 + T, 300, 446, B - 60 - T], "grain": "x"}]
    for i, (x, z) in enumerate([(110, 70), (110, 480), (560, 180), (560, 370)]):
        p.append({"id": f"castor-{i + 1}", "kind": "tube", "mat": GLIDE, "box": [x - 15, 0, z - 15, x + 15, CAST, z + 15]})
    return dump("oskar-0-55", [W, B, H], p, [])


# ------------------------------------------------------------------------------------------------------------ 0.53
def m_0_53():
    W, B, H = 450, 450, 650
    CAST = 40
    yb = CAST + T
    yt = H - 4 - T                   # 630: the top board's underside
    p = [{"id": "base", "shape": "circle", "box": [0, CAST, 0, W, yb, B], "edge": 2, "grain": "x"},
         {"id": "top", "shape": "circle", "box": [0, yt, 0, W, yt + T, B], "edge": 2, "grain": "x"},
         {"id": "glass", "shape": "circle", "mat": "gloss#141414", "edge": 1, "box": [5, yt + T, 5, W - 5, H, B - 5]}]
    cx0, cx1, cz0, cz1 = 30, 180, 125, 325
    p += [{"id": "col-side-l", "box": [cx0, yb, cz0, cx0 + T, yt, cz1], "grain": "y"},
          {"id": "col-side-r", "box": [cx1 - T, yb, cz0, cx1, yt, cz1], "grain": "y"}]
    for nm, z0 in (("back", cz0), ("front", cz1 - T)):
        a, b = cx0 + T, cx1 - T
        p += [{"id": f"col-{nm}-stile-l", "box": [a, yb, z0, a + 20, yt, z0 + T], "grain": "y"},
              {"id": f"col-{nm}-stile-r", "box": [b - 20, yb, z0, b, yt, z0 + T], "grain": "y"},
              {"id": f"col-{nm}-rail-t", "box": [a + 20, yt - 45, z0, b - 20, yt, z0 + T], "grain": "x"},
              {"id": f"col-{nm}-rail-b", "box": [a + 20, yb, z0, b - 20, yb + 60, z0 + T], "grain": "x"}]
    for i, (x, z) in enumerate([(90, 225), (360, 110), (360, 340), (225, 225)]):
        p.append({"id": f"castor-{i + 1}", "kind": "tube", "mat": GLIDE, "box": [x - 15, 0, z - 15, x + 15, CAST, z + 15]})
    return dump("oskar-0-53", [W, B, H], p, [])


# ------------------------------------------------------------------------------------------------------------ 0.54
def m_0_54():
    W, B, H = 340, 430, 662
    p = [{"id": "base", "box": [0, 0, 0, W, T, B], "grain": "x"},
         {"id": "upright", "box": [0, T, 0, T, H - T, B], "grain": "y"},
         {"id": "rib", "box": [T, T, B / 2 - T / 2, 176, H - T, B / 2 + T / 2], "grain": "y"},
         {"id": "top", "box": [0, H - T, 0, W, H, B], "grain": "x"}]
    return dump("oskar-0-54", [W, B, H], p, [])


# ------------------------------------------------------------------------------------------------------ catalogue
def catalog():
    legs = {"legs": "gloss#ececec"}
    fins = [{"id": "oskar-sosna-kareliya", "name": "Сосна Карелия", "body": "door_enamel_whitey#e7e8e1",
             "swatch": "#e7e8e1", "roles": legs},
            {"id": "oskar-dub-kanon", "name": "Дуб Каньон", "body": "door_enamel_whitey#8c6d51", "swatch": "#8c6d51",
             "roles": legs}]
    by = "по каталогу и фото сайта, без инструкции"
    return {
        "finishes": fins, "profiles": {},
        "collections": [{"id": "oskar", "name": "Оскар", "brand": "Пинскдрев", "finishes": [f["id"] for f in fins],
                         "metal": "chrome",
                         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 141 (разворот 278–279) и фото pinskdrev.by; без "
                                 "инструкций. Журнальные и раздвижные обеденные столы ЛДСП («Сосна Карелия» / «Дуб Каньон»), "
                                 "у обеденных — гнутые стальные опоры Ø40, окрашенные в белый."}],
        "models": [
            {"id": "oskar-0-55", "code": "П7.040.0.55", "name": "Стол журнальный «Оскар»", "collection": "oskar",
             "category": "living", "size": [670, 550, 750], "page": 141, "note": by + "; боковины-полумесяцы, на колёсах"},
            {"id": "oskar-0-53", "code": "П7.040.0.53", "name": "Стол журнальный «Оскар»", "collection": "oskar",
             "category": "living", "size": [450, 450, 650], "page": 141,
             "note": by + "; круглый, столешница с чёрным стеклом, на колёсах"},
            {"id": "oskar-0-54", "code": "П7.040.0.54", "name": "Стол журнальный «Оскар»", "collection": "oskar",
             "category": "living", "size": [340, 430, 662], "page": 141, "note": by + "; приставной С-образный"},
            {"id": "oskar-4-51", "code": "П7.040.4.51", "name": "Стол обеденный «Оскар» раздвижной", "collection": "oskar",
             "category": "tables", "size": [1100, 700, 750], "page": 141,
             "note": by + "; размер — в сложенном виде, в разложенном виде L1600×B700×H750 (вставка 500); сайт — П040.512"},
            {"id": "oskar-4-52", "code": "П7.040.4.52", "name": "Стол обеденный «Оскар» раскладной", "collection": "oskar",
             "category": "tables", "size": [800, 600, 750], "page": 141,
             "note": by + "; размер — в сложенном виде (L800×B600), в разложенном виде L1200×B800×H750 (поворотно-"
                          "раскладная столешница)"},
        ],
    }


def write_catalog():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oskar_catalog.json")
    with open(path, "w") as fh:
        json.dump(catalog(), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


if __name__ == "__main__":
    print(write_catalog())
    print(m_0_55())
    print(m_0_53())
    print(m_0_54())
    print(m_4_51())
    print(m_4_52())
