"""«Мюнхен» (П3.983) extending dining tables 4.01, 4.02, 4.03, by catalogue / by photo (no instructions exist).

Sources: catalogue pp. 138–139 (printed 272–275: interiors with 4.02 «Дуб Онтарио» and 4.01 «Сосна Карелия», the
cut-outs folded / unfolded, five decors) and the product photos of pinskdrev.by (two 3/4 views of each). The page's
«Крашение» lines belong to the chairs; the tables are ЛДСП in one decor throughout (the site: «Каркас ЛДСП,
Столешница ЛДСП», the photos).

The three codes share the top and the frame and differ in the pedestal only:
* 4.01 — a V: two slanted leg blocks (160 wide, 100 deep, 13.7°) meeting at the bottom, a back spine board between them,
  on a stadium-shaped base plate;
* 4.02 — an X of seven layered boards (four full, three set back 15 mm: the dark grooves on the photos), on a
  rectangular plate;
* 4.03 — a trapezoid box (front and back panels 800 at the top, 500 at the bottom, slanted side boards), on a plate with
  rounded corners.
Common: top ЛДСП 22, 1200 × 800 folded, corners R 100, split across the middle; the halves run out 200 each on the
apron (ЛДСП 16, 800 × 460 × 80) and the insert 400 × 800 (a butterfly leaf, two 400 × 400 halves stored folded in the
apron) rises into the gap → 1600. Base plates ЛДСП 22 on the floor. Sizes inside are read off 3/4 photos: ±30 mm.

    python3 tools/casegoods/gen/myunhen.py        # writes Designs/myunhen-*.json and gen/myunhen_catalog.json
"""
import json
import os

from common import dump

W, B, H = 1200, 800, 780
TT = 22                          # top and plate
T = 16
YT = H - TT                      # 758
YA = YT - 80                     # 678: the apron's bottom
YP = TT                          # 22: the plate's top
AX0, AX1, AZ0, AZ1 = 200, 1000, 170, 630


def poly(pts):
    return "M " + " L ".join(f"{x:g} {y:g}" for x, y in pts) + " Z"


def top_and_frame(apron_front_back=True):
    p = [{"id": "top-left", "box": [0, YT, 0, 600, H, B], "edge": 2, "grain": "x", "shape": "path",
          "outline": f"M 600 0 L 100 0 Q 0 0 0 100 L 0 700 Q 0 {B} 100 {B} L 600 {B} Z"},
         {"id": "top-right", "box": [600, YT, 0, W, H, B], "edge": 2, "grain": "x", "shape": "path",
          "outline": f"M 600 0 L 1100 0 Q {W} 0 {W} 100 L {W} 700 Q {W} {B} 1100 {B} L 600 {B} Z"}]
    if apron_front_back:
        p += [{"id": "apron-front", "box": [AX0, YA, AZ1 - T, AX1, YT, AZ1], "grain": "x"},
              {"id": "apron-back", "box": [AX0, YA, AZ0, AX1, YT, AZ0 + T], "grain": "x"}]
    p += [{"id": "apron-end-l", "box": [AX0 + T, YA, AZ0 + T, AX0 + 2 * T, YT, AZ1 - T], "grain": "z"},
          {"id": "apron-end-r", "box": [AX1 - 2 * T, YA, AZ0 + T, AX1 - T, YT, AZ1 - T], "grain": "z"},
          {"id": "runner-f", "mat": "metal", "edge": 0.5, "box": [AX0 + 2 * T, YT - 30, AZ1 - T - 12, AX1 - 2 * T, YT, AZ1 - T]},
          {"id": "runner-b", "mat": "metal", "edge": 0.5, "box": [AX0 + 2 * T, YT - 30, AZ0 + T, AX1 - 2 * T, YT, AZ0 + T + 12]}]
    # butterfly insert 400 × 800 folded: two 400 × 400 halves stacked inside the apron
    p += [{"id": "leaf-a", "box": [400, YT - 2 - TT, 200, 800, YT - 2, 600], "edge": 2, "grain": "z"},
          {"id": "leaf-b", "box": [400, YT - 4 - 2 * TT, 200, 800, YT - 4 - TT, 600], "edge": 2, "grain": "z"}]
    m = [{"type": "slide", "name": "extend_left", "parts": ["top-left"], "by": [-200, 0, 0]},
         {"type": "slide", "name": "extend_right", "parts": ["top-right"], "by": [200, 0, 0]},
         {"type": "slide", "name": "leaf_a", "parts": ["leaf-a"], "by": [0, 2 + TT, 200]},
         {"type": "slide", "name": "leaf_b", "parts": ["leaf-b"], "by": [0, 4 + 2 * TT, -200]}]
    return p, m


def m_4_01():
    """V pedestal."""
    p, m = top_and_frame()
    p.append({"id": "plate", "box": [180, 0, 120, 1020, YP, 680], "grain": "x", "edge": 2, "shape": "path",
              "outline": "M 380 120 L 820 120 C 960 120 1020 180 1020 300 L 1020 500 C 1020 620 960 680 820 680 "
                         "L 380 680 C 240 680 180 620 180 500 L 180 300 C 180 180 240 120 380 120 Z"})
    z0, z1 = 350, 450
    p.append({"id": "leg-l", "box": [268, YP, z0, 588, YA, z1], "grain": "y", "shape": "path",
              "outline": poly([(428, YP), (588, YP), (428, YA), (268, YA)])})
    p.append({"id": "leg-r", "box": [612, YP, z0, 932, YA, z1], "grain": "y", "shape": "path",
              "outline": poly([(612, YP), (772, YP), (932, YA), (772, YA)])})
    p.append({"id": "spine", "box": [520, YP, z0 - 20, 680, YA, z0 - 4], "grain": "y"})
    return dump("myunhen-4-01", [W, B, H], p, m)


def x_outline(a, b, w, y0, y1):
    """An X of two bars with horizontal ends: bar 1 from (a..a+w, y0) to (b..b+w, y1), bar 2 its mirror about x=600."""
    def mir(x):
        return W - x

    def inter(p1, p2, p3, p4):
        (x1, y1_), (x2, y2), (x3, y3), (x4, y4) = p1, p2, p3, p4
        d = (x1 - x2) * (y3 - y4) - (y1_ - y2) * (x3 - x4)
        t = ((x1 - x3) * (y3 - y4) - (y1_ - y3) * (x3 - x4)) / d
        return (round(x1 + t * (x2 - x1), 1), round(y1_ + t * (y2 - y1_), 1))
    b1l = ((a, y0), (b, y1))                     # bar 1 left edge
    b1r = ((a + w, y0), (b + w, y1))             # bar 1 right edge
    b2l = ((mir(a + w), y0), (mir(b + w), y1))   # bar 2 left edge
    b2r = ((mir(a), y0), (mir(b), y1))           # bar 2 right edge
    low = inter(*b1r, *b2l)
    high = inter(*b1l, *b2r)
    right = inter(*b1r, *b2r)
    left = inter(*b1l, *b2l)
    pts = [(a, y0), (a + w, y0), low, (mir(a + w), y0), (mir(a), y0), right, (b + w, y1), (b, y1), high,
           (mir(b), y1), (mir(b + w), y1), left]
    return poly(pts)


def m_4_02():
    """X pedestal of layered boards."""
    p, m = top_and_frame()
    p.append({"id": "plate", "box": [190, 0, 140, 1010, YP, 660], "grain": "x", "edge": 2, "radius": 5})
    a, b, w = 330, 670, 200
    z = 344
    for i in range(7):
        full = i % 2 == 0
        if full:
            out = x_outline(a, b, w, YP, YA)
        else:
            out = x_outline(a + 15, b + 15, w - 30, YP, YA - 15)
        p.append({"id": f"x-{i + 1}", "box": [a if full else a + 15, YP, z, W - a if full else W - a - 15,
                                             YA if full else YA - 15, z + T], "grain": "y", "shape": "path",
                  "outline": out})
        z += T
    return dump("myunhen-4-02", [W, B, H], p, m)


def m_4_03():
    """Trapezoid pedestal: front / back panels run up to the top (they are the apron's long boards)."""
    p, m = top_and_frame(apron_front_back=False)
    p.append({"id": "plate", "box": [200, 0, 150, 1000, YP, 650], "grain": "x", "edge": 2, "radius": 60})
    k = 150 / (YT - YP)                            # the side's slope: 500 at the plate → 800 at the top

    def xl(y):
        return 350 - (y - YP) * k
    out = poly([(round(xl(YP), 1), YP), (round(W - xl(YP), 1), YP), (round(W - xl(YT), 1), YT), (round(xl(YT), 1), YT)])
    for nm, z0 in (("front", AZ1 - T), ("back", AZ0)):
        p.append({"id": f"ped-{nm}", "box": [round(xl(YT), 1), YP, z0, round(W - xl(YT), 1), YT, z0 + T], "grain": "y",
                  "shape": "path", "outline": out})
    import math
    th = math.atan(k)
    lb = (654 - T * math.sin(th)) / math.cos(th)
    ym = (YP + YA) / 2
    xo = xl(ym)                                   # the outer face at mid-height
    xc = xo + (T / 2) / math.cos(th)
    for s, nm in ((1, "l"), (-1, "r")):
        c = xc if s > 0 else W - xc
        p.append({"id": f"ped-side-{nm}", "box": [round(c - T / 2, 1), round(ym - lb / 2, 1), AZ0 + T,
                                                  round(c + T / 2, 1), round(ym + lb / 2, 1), AZ1 - T],
                  "grain": "y", "rot": {"axis": "z", "deg": round(s * math.degrees(th), 2)}})
    return dump("myunhen-4-03", [W, B, H], p, m)


# ------------------------------------------------------------------------------------------------------ catalogue
DECORS = [
    ("myunhen-dub-ontario", "Дуб Онтарио 385ТМ", "#a08357"),
    ("myunhen-beton-layt", "Бетон Лайт 818ТМ", "#cdcac4"),
    ("myunhen-dub-kanzas", "Дуб Канзас 377ТМ", "#74543c"),
    ("myunhen-mramor-nero", "Мрамор Неро Маркина 850ТМ", "#292929"),
    ("myunhen-sosna-kareliya", "Сосна Карелия 528SWA", "#e4e5e1"),
]


def catalog():
    fins = [{"id": i, "name": n, "body": f"door_enamel_whitey{c}", "swatch": c} for i, n, c in DECORS]
    note = ("по каталогу и фото сайта, без инструкции; размер — в сложенном виде, в разложенном виде L1600×B800×H780 "
            "(вставка 400)")
    return {
        "finishes": fins, "profiles": {},
        "collections": [{"id": "myunhen", "name": "Мюнхен", "brand": "Пинскдрев", "finishes": [f["id"] for f in fins],
                         "metal": "chrome",
                         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 138–139 (развороты 272–275) и фото pinskdrev.by; "
                                 "без инструкций. Раздвижные столы из ЛДСП в одном декоре (5 вариантов): столешница 22 со "
                                 "скруглёнными углами, царга, опора на плите; 4.01 — V-опора, 4.02 — X-опора из слоёв, "
                                 "4.03 — трапециевидная опора."}],
        "models": [
            {"id": "myunhen-4-01", "code": "П3.983.4.01", "name": "Стол «Мюнхен» (V-опора)", "collection": "myunhen",
             "category": "tables", "size": [W, B, H], "page": 139, "note": note},
            {"id": "myunhen-4-02", "code": "П3.983.4.02", "name": "Стол «Мюнхен» (X-опора)", "collection": "myunhen",
             "category": "tables", "size": [W, B, H], "page": 138, "note": note},
            {"id": "myunhen-4-03", "code": "П3.983.4.03", "name": "Стол «Мюнхен» (трапеция)", "collection": "myunhen",
             "category": "tables", "size": [W, B, H], "page": 139, "note": note},
        ],
    }


def write_catalog():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "myunhen_catalog.json")
    with open(path, "w") as fh:
        json.dump(catalog(), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


if __name__ == "__main__":
    print(write_catalog())
    print(m_4_01())
    print(m_4_02())
    print(m_4_03())
