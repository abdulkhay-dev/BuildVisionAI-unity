"""«Формат» (П7.010, computer desks): 2.01 and 2.02, by catalogue / by photo (no instructions exist).

Sources: catalogue p. 64 (printed 124: the interior photo of 2.01, the cut-outs of 2.01 / 2.02, the swatches «Сосна
Карелия» / «Дуб Каньон») and the product photos of pinskdrev.by (2.01: the white cut-out and the interior photo — the same
as the catalogue's; 2.02: one 3/4 photo). Sizes inside the desks were measured on the near-front interior photo of 2.01
(x and y scaled separately: 1200 mm = the top's width, 760 mm = the height at the pedestal front); good to ±15 mm.

Construction (one scheme, the photos):
* ЛДСП 16 throughout, one decor (tops with a 2 mm ПВХ edge, rounded corners);
* 2.01: the top is 600 deep over the knee space and 700 over the pedestal (an S-curve joins the two at the pedestal's
  left side), 50 mm over the left side and 60 mm over the pedestal's right side; a left side, a knee rail 250 at the
  back, the keyboard shelf on runners 100 under the top; the pedestal 360 wide: an open niche under the top (its floor
  edge shows over the top drawer), three drawers 174 high on a recessed plinth, bow handles 128; a system-unit stand on
  castors (a base, a front board, a low rim on the right side) that rolls out;
* 2.02: an L-shaped top 1300 × 1300 (two 600 wings, the inner corner cut by a concave arc R 400); the left wing carries
  the pedestal (drawers face the knee space, +x; the niche's back-end panel is cut in a curve), the right wing ends in an
  open shelving support (two uprights, a middle and a bottom shelf with a rounded corner, on glides); a square corner
  post 120, knee rails along both walls, the keyboard shelf across the corner (at 45°, on two hanger boards), the stand.

    python3 tools/casegoods/gen/format.py        # writes Designs/format-*.json and gen/format_catalog.json
"""
import json
import math
import os

from common import dump

T = 16
H = 760
TOPY = H - T                     # 744: the underside of the top
GLIDE = "black"


def r5(v):
    return round(v * 2) / 2


def P(pid, box, **kw):
    d = {"id": pid, "box": [r5(v) for v in box]}
    d.update(kw)
    return d


def bow(hid, x, y, z):
    """Bow handle 128 (the photos: satin aluminium D-bow ≈ 150 long, standing ≈ 25 off the front)."""
    return {"id": hid, "kind": "handle", "model": "bar", "mat": "metal", "at": [r5(x), r5(y)], "dir": "right", "d": 160,
            "band": 10, "t": 8, "standoff": 25, "post": 9, "z": z}


def bow_x(hid, xf, y, zc):
    """The same bow handle on a front facing +x (engine handles stand out of +z only): a bar and two posts as rods."""
    return [
        {"id": f"{hid}-bar", "kind": "rod", "mat": "metal", "from": [xf + 25, y, zc - 78], "to": [xf + 25, y, zc + 78], "d": 10},
        {"id": f"{hid}-p1", "kind": "rod", "mat": "metal", "from": [xf, y, zc - 64], "to": [xf + 25, y, zc - 64], "d": 9},
        {"id": f"{hid}-p2", "kind": "rod", "mat": "metal", "from": [xf, y, zc + 64], "to": [xf + 25, y, zc + 64], "d": 9},
    ]


def castors(tag, pts, y0=0, h=36, d=30):
    return [{"id": f"{tag}-castor-{i + 1}", "kind": "tube", "mat": GLIDE, "box": [x - d / 2, y0, z - d / 2, x + d / 2, y0 + h, z + d / 2]}
            for i, (x, z) in enumerate(pts)]


# ------------------------------------------------------------------------------------------------------------ 2.01
def m_2_01():
    W, B = 1200, 700
    KD = 600                         # the top's depth over the knee space
    XL = 50                          # the left side's outer face
    PX0, PX1 = 780, 1140             # the pedestal
    PD = 664                         # the pedestal's sides (fronts 664..680, the top 20 over them)
    p, m = [], []
    p.append({"id": "top", "box": [0, TOPY, 0, W, H, B], "grain": "x", "edge": 2, "shape": "path",
              "outline": f"M 0 0 L {W} 0 L {W} 640 Q {W} {B} 1140 {B} L 860 {B} C 790 {B} 790 {KD} 720 {KD} "
                         f"L 40 {KD} Q 0 {KD} 0 560 Z"})
    p.append(P("side-l", [XL, 0, 0, XL + T, TOPY, 570], grain="y"))
    p.append(P("knee-rail", [XL + T, TOPY - 250, 0, PX0, TOPY, T], grain="x"))
    # pedestal
    p += [P("ped-side-l", [PX0, 0, 0, PX0 + T, TOPY, PD], grain="y"),
          P("ped-side-r", [PX1 - T, 0, 0, PX1, TOPY, PD], grain="y"),
          P("ped-back", [PX0 + T, 68, 0, PX1 - T, TOPY, T]),
          P("ped-bottom", [PX0 + T, 68, T, PX1 - T, 84, PD]),
          P("ped-plinth", [PX0 + T, 0, PD - 40, PX1 - T, 68, PD - 24]),
          P("niche-floor", [PX0 + T, 604, T, PX1 - T, 620, PD])]
    fx0, fx1 = PX0 + 2, PX1 - 2
    rows = [(426, 600), (249, 423), (72, 246)]
    for i, (y0, y1) in enumerate(rows):
        tag = f"drawer_{i + 1}"
        bx0, bx1, by0, bh, zb = PX0 + T + 13, PX1 - T - 13, y0 + 16, 120, PD - 450
        g = [P(f"{tag}-front", [fx0, y0, PD, fx1, y1, PD + T], kind="front", grain="x"),
             bow(f"{tag}-handle", (fx0 + fx1) / 2, (y0 + y1) / 2 - 4, PD + T),
             P(f"{tag}-side-l", [bx0, by0, zb, bx0 + T, by0 + bh, PD]),
             P(f"{tag}-side-r", [bx1 - T, by0, zb, bx1, by0 + bh, PD]),
             P(f"{tag}-back", [bx0 + T, by0, zb, bx1 - T, by0 + bh, zb + T]),
             P(f"{tag}-bottom", [bx0 + 8, by0 + 10, zb + 4, bx1 - 8, by0 + 13.5, PD - 2], kind="back")]
        p += g
        m.append({"type": "drawer", "name": tag, "parts": [q["id"] for q in g], "travel": 380})
    # keyboard shelf on runners (on the left side and the pedestal's left side), 100 under the top
    kx0, kx1 = XL + T + 13, PX0 - 13
    kb = [P("keyboard", [kx0, 628, 130, kx1, 644, 580], grain="x")]
    p += kb
    p += [P("runner-l", [XL + T, 628, 150, kx0, 648, 560], mat="metal", edge=0.5),
          P("runner-r", [kx1, 628, 150, PX0, 648, 560], mat="metal", edge=0.5)]
    m.append({"type": "slide", "name": "keyboard", "parts": ["keyboard"], "by": [0, 0, 320]})
    # system-unit stand on castors, against the left side
    sx0, sx1, sz0, sz1 = XL + T + 6, XL + T + 256, 90, 570
    st = [P("stand-base", [sx0, 36, sz0, sx1, 52, sz1 - T]),
          P("stand-front", [sx0, 20, sz1 - T, sx1, 110, sz1], grain="x"),
          P("stand-rim", [sx1 - T, 52, sz0, sx1, 150, sz1 - T], grain="z")]
    st += castors("stand", [(sx0 + 30, sz0 + 30), (sx1 - 30, sz0 + 30), (sx0 + 30, sz1 - 60), (sx1 - 30, sz1 - 60)])
    p += st
    m.append({"type": "slide", "name": "stand", "parts": [q["id"] for q in st], "by": [0, 0, 300]})
    return dump("format-2-01", [W, B, H], p, m)


# ------------------------------------------------------------------------------------------------------------ 2.02
def m_2_02():
    S = 1300                         # both wings' length
    WW = 600                         # the wings' width
    R = 400                          # the concave arc of the inner corner: centre (1000, 1000)
    c = 0.5523 * R
    p, m = [], []
    p.append({"id": "top", "box": [0, TOPY, 0, S, H, S], "edge": 2, "shape": "path",
              "outline": f"M 0 0 L {S} 0 L {S} 540 Q {S} {WW} 1240 {WW} L 1000 {WW} "
                         f"C {1000 - c:.0f} {WW} {WW} {1000 - c:.0f} {WW} 1000 L {WW} 1240 Q {WW} {S} 540 {S} L 0 {S} Z"})
    # corner post 120 × 120 (four boards) and knee rails along both walls
    p += [P("post-back", [0, 0, 0, 120, TOPY, T]),
          P("post-front", [0, 0, 104, 120, TOPY, 120]),
          P("post-left", [0, 0, T, T, TOPY, 104]),
          P("post-right", [104, 0, T, 120, TOPY, 104]),
          P("rail-back", [120, TOPY - 300, 0, 900, TOPY, T], grain="x"),
          P("rail-left", [0, TOPY - 300, 120, T, TOPY, 880], grain="z")]
    # pedestal on the left wing, z 880..1300, drawers facing +x (the knee space)
    Z0, Z1, PD = 880, S, 560
    p += [P("ped-end", [0, 0, Z1 - T, PD, TOPY, Z1], grain="y"),
          {"id": "ped-inner", "box": [0, 0, Z0, PD, TOPY, Z0 + T], "grain": "y", "shape": "path",
           "outline": f"M 0 0 L {PD} 0 L {PD} 542 C {PD} 610 470 620 470 690 L 470 {TOPY} L 0 {TOPY} Z"},
          P("ped-back", [0, 34, Z0 + T, T, TOPY, Z1 - T]),
          P("ped-bottom", [T, 34, Z0 + T, PD, 50, Z1 - T]),
          P("ped-plinth", [PD - 40, 0, Z0 + T, PD - 24, 34, Z1 - T]),
          P("niche-floor", [T, 526, Z0 + T, PD, 542, Z1 - T])]
    rows = [(362, 522), (199, 359), (36, 196)]
    fz0, fz1 = Z0 + 2, Z1 - 2
    for i, (y0, y1) in enumerate(rows):
        tag = f"drawer_{i + 1}"
        bz0, bz1, by0, bh, xb = Z0 + T + 13, Z1 - T - 13, y0 + 14, 110, PD - 450
        hid = f"{tag}-handle"
        hs = bow_x(hid, PD + T, (y0 + y1) / 2 - 4, (fz0 + fz1) / 2)
        g = [P(f"{tag}-front", [PD, y0, fz0, PD + T, y1, fz1], kind="front", grain="z"),
             P(f"{tag}-side-a", [xb, by0, bz0, PD, by0 + bh, bz0 + T]),
             P(f"{tag}-side-b", [xb, by0, bz1 - T, PD, by0 + bh, bz1]),
             P(f"{tag}-back", [xb, by0, bz0 + T, xb + T, by0 + bh, bz1 - T]),
             P(f"{tag}-bottom", [xb + 4, by0 + 10, bz0 + 8, PD - 2, by0 + 13.5, bz1 - 8], kind="back")] + hs
        p += g
        m.append({"type": "slide", "name": tag, "parts": [q["id"] for q in g], "by": [380, 0, 0]})
    # the stand behind the pedestal (towards the corner), rolling out towards +x
    sx0, sx1, sz0, sz1 = 60, 520, 620, 870
    st = [P("stand-base", [sx0, 36, sz0, sx1 - T, 52, sz1]),
          P("stand-front", [sx1 - T, 20, sz0, sx1, 110, sz1], grain="z"),
          P("stand-rim", [sx0, 52, sz0, sx1 - T, 150, sz0 + T], grain="x")]
    st += castors("stand", [(sx0 + 30, sz0 + 40), (sx0 + 30, sz1 - 30), (sx1 - 60, sz0 + 40), (sx1 - 60, sz1 - 30)])
    p += st
    m.append({"type": "slide", "name": "stand", "parts": [q["id"] for q in st], "by": [300, 0, 0]})
    # open shelving support at the right end of the back wing, on a base on glides
    X0, OX = 900, 1150
    shelf_outline = (f"M {X0 + T} 0 L {OX} 0 L {OX} 300 L {OX + T} 300 L {OX + T} 0 L {S} 0 L {S} 440 "
                     f"Q {S} 560 1180 560 L {X0 + T} 560 Z")
    p += [{"id": "rs-base", "box": [X0, 20, 0, S, 36, 560], "grain": "x", "shape": "path",
           "outline": f"M {X0} 0 L {S} 0 L {S} 440 Q {S} 560 1180 560 L {X0} 560 Z"},
          P("rs-upright-in", [X0, 36, 0, X0 + T, TOPY, 560], grain="y"),
          P("rs-upright-out", [OX, 36, 0, OX + T, TOPY, 300], grain="y"),
          {"id": "rs-shelf", "box": [X0 + T, 364, 0, S, 380, 560], "grain": "x", "shape": "path", "outline": shelf_outline}]
    for i, (x, z) in enumerate([(X0 + 30, 30), (X0 + 30, 530), (S - 40, 30), (1230, 520)]):
        p.append({"id": f"glide-{i + 1}", "kind": "tube", "mat": GLIDE, "box": [x - 12, 0, z - 12, x + 12, 20, z + 12]})
    # keyboard shelf across the corner (45°): a board 460 × 400 drawn by its outline, on two hanger boards
    u = (1 / math.sqrt(2), -1 / math.sqrt(2))       # along the shelf
    v = (-1 / math.sqrt(2), -1 / math.sqrt(2))      # back, towards the corner
    F = (705, 705)                                  # the middle of its front edge

    def pt(a, b):
        return (F[0] + a * u[0] + b * v[0], F[1] + a * u[1] + b * v[1])

    def poly(pts):
        return "M " + " L ".join(f"{x:.1f} {z:.1f}" for x, z in pts) + " Z"

    def bbox(pts):
        xs, zs = [q[0] for q in pts], [q[1] for q in pts]
        return min(xs), min(zs), max(xs), max(zs)

    def diag(pid, pts, y0, y1, **kw):
        x0, z0, x1, z1 = bbox(pts)
        d = {"id": pid, "box": [round(x0, 1), y0, round(z0, 1), round(x1, 1), y1, round(z1, 1)], "shape": "path",
             "outline": poly(pts)}
        d.update(kw)
        return d

    hw, dp = 230, 400
    kb = [pt(-hw, 0), pt(hw, 0), pt(hw, dp), pt(-hw, dp)]
    p.append(diag("keyboard", kb, 628, 644, grain="x"))
    for s, name in ((-1, "l"), (1, "r")):
        a0, a1 = (s * (hw + 13), s * (hw + 29)) if s > 0 else (s * (hw + 29), s * (hw + 13))
        p.append(diag(f"hanger-{name}", [pt(a0, 10), pt(a1, 10), pt(a1, dp - 10), pt(a0, dp - 10)], 660, TOPY, grain="z"))
        r0, r1 = (s * hw, s * (hw + 13)) if s > 0 else (s * (hw + 13), s * hw)
        p.append(diag(f"runner-{name}", [pt(r0, 20), pt(r1, 20), pt(r1, dp - 20), pt(r0, dp - 20)], 644, 660,
                      mat="metal", edge=0.5))
    m.append({"type": "slide", "name": "keyboard", "parts": ["keyboard"], "by": [212, 0, 212]})
    return dump("format-2-02", [S, S, H], p, m)


# ------------------------------------------------------------------------------------------------------ catalogue
def catalog():
    fins = [
        {"id": "format-sosna-kareliya", "name": "Сосна Карелия", "body": "door_enamel_whitey#e6e7e1", "swatch": "#e6e7e1"},
        {"id": "format-dub-kanon", "name": "Дуб Каньон", "body": "door_enamel_whitey#8a6b4e", "swatch": "#8a6b4e"},
    ]
    note = ("по каталогу и фото сайта, без инструкции; ЛДСП 16, размеры внутри по фото (±15 мм)")
    return {
        "finishes": fins,
        "profiles": {},
        "collections": [
            {"id": "format", "name": "Формат", "brand": "Пинскдрев", "finishes": [f["id"] for f in fins], "metal": "chrome",
             "note": "Каталог «Корпусная мебель ч. II» 2025, с. 64 (разворот 124–125) и фото pinskdrev.by; без инструкций. "
                     "Компьютерные столы из ЛДСП 16 в одном декоре («Сосна Карелия» или «Дуб Каньон»): тумба с нишей и "
                     "тремя ящиками, выдвижная полка для клавиатуры, подставка под системный блок на колёсах, ручки-скобы 128."}
        ],
        "models": [
            {"id": "format-2-01", "code": "П7.010.2.01", "name": "Стол компьютерный «Формат»", "collection": "format",
             "category": "office", "size": [1200, 700, 760], "page": 64, "note": note},
            {"id": "format-2-02", "code": "П7.010.2.02", "name": "Стол компьютерный угловой «Формат»", "collection": "format",
             "category": "office", "size": [1300, 1300, 760], "page": 64,
             "note": note + "; угловой: тумба на левом крыле (ящики к месту сидения), стеллаж-опора на правом"},
        ],
    }


def write_catalog():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "format_catalog.json")
    with open(path, "w") as fh:
        json.dump(catalog(), fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


if __name__ == "__main__":
    print(write_catalog())
    print(m_2_01())
    print(m_2_02())
