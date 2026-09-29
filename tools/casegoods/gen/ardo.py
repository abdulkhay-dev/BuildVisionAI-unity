"""«Ардо» (Пинскдрев П3.598, каталог «Корпусная мебель ч. II», PDF p. 97): 9 articles, all by catalogue + site photos.

No instruction exists for any module. Sources: the p. 97 spread (living room nearly front-on, front-on module cut-outs
with sizes, the swatch «Белый» / «Дуб мадура») and the pinskdrev.by product photos (front-on studio shots, open-door
shots, 3/4 views) — the positions are measured off the front-on photos (scale = catalogue size / photo pixels).

Construction (read off the photos; the same in every cabinet):
  * carcass ЛДСП 16 «Дуб мадура»: top and bottom over the full width and depth (420), the sides between them, partitions
    and shelves oak, set back behind the fronts (z 10…402); back ХДФ white in grooves (z 6…9.5);
  * fronts ЛДСП 16 white, inset between the sides flush with the carcass (z 404…420), 2 mm gaps to the carcass, 3 mm
    between fronts; the joints lie over the partitions;
  * the motif: an oak «pilaster» strip 152 wide — three oak boards with two dark 5 mm lines between them — glued to a
    white door as one front (0.02, 0.03, 0.07: the knob sits on the strip or the door opens with it), or fixed in front
    of a narrow closed column (0.01, 0.06: the vitrine's door hinges on the partition behind the strip's edge);
  * black round knobs; black square legs 40 × 40 × 100 set 30 mm in.

    python3 tools/casegoods/gen/ardo.py        # writes the designs and gen/ardo_catalog.json
"""
import json
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
T = 16           # ЛДСП
D = 420          # catalogue depth of the cabinets
ZF0, ZF1 = 404, 420   # the fronts' plane
LH = 100         # legs
BYPHOTO = "по фото, без инструкции"

MODELS = []


def r1(b):
    return [round(v, 1) for v in b]


def P(pid, b, **kw):
    p = {"id": pid}
    p.update(kw)
    p["box"] = r1(b)
    return p


def ids(parts):
    return [p.get("id") or p.get("n") for p in parts]


def model(mid, code, name, category, size, note, **kw):
    m = {"id": mid, "code": code, "name": name, "collection": "ardo", "category": category, "size": size}
    m.update(kw)
    m["page"] = 97
    m["note"] = note
    MODELS.append(m)


# ------------------------------------------------------------------------------------------------ helpers


def carcass(W, H, lh=LH):
    """Top and bottom over the full width, sides between them, the white back in grooves."""
    return [P("top", [0, H - T, 0, W, H, D]),
            P("bottom", [0, lh, 0, W, lh + T, D]),
            P("side-l", [0, lh + T, 0, T, H - T, D]),
            P("side-r", [W - T, lh + T, 0, W, H - T, D]),
            P("back", [T - 7, lh + T - 7, 6, W - T + 7, H - T + 7, 9.5], kind="back", mat="white")]


def legs(xs, zs, extra=(), w=40, h=LH):
    out, k = [], 0
    for x in xs:
        for z in zs:
            k += 1
            out.append(P(f"leg-{k}", [x - w / 2, 0, z - w / 2, x + w / 2, h, z + w / 2], mat="metal", edge=1, covers=["g"]))
    for x, z in extra:
        k += 1
        out.append(P(f"leg-{k}", [x - w / 2, 0, z - w / 2, x + w / 2, h, z + w / 2], mat="metal", edge=1, covers=["g"]))
    return out


def strip(tag, x0, x1, y0, y1, z0=ZF0, z1=ZF1, line=5, kind="front"):
    """The oak pilaster: three oak boards with two dark 5 mm lines (black strips 2 mm below the face) between them."""
    b = (x1 - x0 - 2 * line) / 3
    out, x = [], x0
    for i in range(3):
        out.append(P(f"{tag}-oak-{i + 1}", [x, y0, z0, x + b, y1, z1], kind=kind, mat="body", grain="y"))
        x += b
        if i < 2:
            out.append(P(f"{tag}-line-{i + 1}", [x, y0, z0, x + line, y1, z1 - 2], kind=kind, mat="black"))
            x += line
    return out


def knob(tag, x, y, z=ZF1, d=30):
    return {"id": f"k-{tag}", "kind": "handle", "model": "knob", "at": [round(x, 1), round(y, 1)], "d": d, "t": 12,
            "standoff": 20, "z": z, "covers": ["k"]}


def drawer(tag, front, bx0, bx1, by0, bh, z0=30, zf=ZF0, kx=None, ky=None):
    """Drawer: the white front (a box), a white ЛДСП 16 box (sides, back) with an ХДФ bottom in grooves, a knob."""
    x0, y0, _, x1, y1, _ = front
    parts = [P(f"{tag}-front", front, kind="front"),
             P(f"{tag}-side-l", [bx0, by0, z0, bx0 + T, by0 + bh, zf], mat="white"),
             P(f"{tag}-side-r", [bx1 - T, by0, z0, bx1, by0 + bh, zf], mat="white"),
             P(f"{tag}-back", [bx0 + T, by0, z0, bx1 - T, by0 + bh, z0 + T], mat="white"),
             P(f"{tag}-bottom", [bx0 + 10, by0 + 8, z0 + 6, bx1 - 10, by0 + 11.5, zf - 2], kind="back", mat="white")]
    parts.append(knob(tag, (x0 + x1) / 2 if kx is None else kx, (y0 + y1) / 2 if ky is None else ky))
    return parts, {"type": "drawer", "name": tag, "parts": ids(parts), "travel": round((zf - z0) * 0.8)}


def door(name, parts, hinge, axis=None, angle=100):
    mv = {"type": "door", "name": name, "parts": ids(parts), "hinge": hinge, "angle": angle}
    if axis:
        mv["axis"] = axis
    return mv


def mirror_x(W, parts, moves):
    """The mirror image (-01 «зеркальное отражение»): x → W − x, hinges swapped."""
    out = []
    for p in parts:
        q = json.loads(json.dumps(p))
        if "box" in q:
            b = q["box"]
            q["box"] = r1([W - b[3], b[1], b[2], W - b[0], b[4], b[5]])
        if "at" in q:
            q["at"] = [round(W - q["at"][0], 1), q["at"][1]]
        out.append(q)
    mv = []
    for m in moves:
        m = dict(m)
        if m.get("hinge") in ("left", "right"):
            m["hinge"] = "right" if m["hinge"] == "left" else "left"
        if m.get("axis") and m["type"] == "door":
            m["axis"] = [round(W - m["axis"][0], 1), m["axis"][1]]
        mv.append(m)
    return out, mv


# ------------------------------------------------------------------------------------------------ tall cabinets
W1, H1 = 634, 1958
XJ = 462          # the joint door | strip; the partition behind it
FY0, FY1 = LH + T + 2, H1 - T - 2     # 118 … 1940


def tall_common():
    p = carcass(W1, H1)
    p.append(P("partition", [XJ - 8, LH + T, 10, XJ + 8, H1 - T, ZF0 - 2]))
    p += strip("strip", XJ + 1, W1 - T - 2, FY0, FY1, kind="front")
    p += legs([50, W1 - 50], [50, D - 50])
    return p


def vitrina():
    """Шкаф-витрина П3.598.0.01 (634 × 420 × 1958): a glazed door (white board 348 at the top, frameless clear glass,
    white board 429 at the bottom) hinged on the partition, the oak strip fixed in front of a narrow closed column to
    its right; inside: fixed oak shelves at the joints of the door, two glass shelves in the vitrine; knob on the glass."""
    p = tall_common()
    p += [P("shelf-low", [T, 530, 10, XJ - 8, 546, ZF0 - 2]),
          P("shelf-high", [T, 1576, 10, XJ - 8, 1592, ZF0 - 2]),
          P("glass-1", [T + 1, 786, 30, XJ - 9, 792, 380], kind="glass"),
          P("glass-2", [T + 1, 1256, 30, XJ - 9, 1262, 380], kind="glass")]
    d = [P("door-top", [18, 1592, ZF0, XJ - 1, FY1, ZF1], kind="front"),
         P("door-glass", [18, 548, ZF0, XJ - 1, 1590, ZF0 + 4], kind="glass"),
         P("door-bottom", [18, FY0, ZF0, XJ - 1, 546, ZF1], kind="front"),
         knob("door", 95, 1010, z=ZF0 + 4)]
    p += d
    return p, [door("door", d, "right", [XJ - 1, ZF1])]


def s001():
    p, mv = vitrina()
    model("ardo-0-01", "П3.598.0.01", "Шкаф-витрина «Ардо»", "living", [W1, D, H1],
          BYPHOTO + "; дверь со стеклом слева (петли на перегородке), дубовая планка справа неподвижная")
    return dump("ardo-0-01", [W1, D, H1], p, mv)


def s00101():
    p, mv = vitrina()
    p, mv = mirror_x(W1, p, mv)
    model("ardo-0-01-01", "П3.598.0.01-01", "Шкаф-витрина «Ардо» (зеркальное отражение)", "living", [W1, D, H1],
          BYPHOTO + "; зеркальное отражение П3.598.0.01: планка слева, дверь справа; код по сайту (в каталоге напечатано П6.598.0.01-01)")
    return dump("ardo-0-01-01", [W1, D, H1], p, mv)


def s006():
    """Шкаф П3.598.0.06 (634 × 420 × 1958): open oak shelves over a white door without a knob (push-to-open), the oak
    strip fixed in front of the narrow column on the right."""
    p = tall_common()
    p.append(P("shelf-fixed", [T, 507, 10, XJ - 8, 523, ZF0 - 2]))
    for i, y in enumerate([872, 1218, 1596]):
        p.append(P(f"shelf-{i + 1}", [T + 0.5, y, 10, XJ - 8.5, y + T, ZF0 - 2]))
    d = [P("door", [18, FY0, ZF0, XJ - 1, 505, ZF1], kind="front")]
    p += d
    model("ardo-0-06", "П3.598.0.06", "Шкаф «Ардо»", "living", [W1, D, H1],
          BYPHOTO + "; открытые полки, нижняя дверь без ручки (push-to-open), дубовая планка справа неподвижная")
    return dump("ardo-0-06", [W1, D, H1], p, [door("door", d, "left")])


# ------------------------------------------------------------------------------------------------ тумба 0.02


def s002():
    """Тумба П3.598.0.02 (881 × 420 × 1318): left door = white board + oak strip (the knob on the strip), hinged left,
    shelves behind it; right column: a drop-down flap (writing flap on stays) at the top, a drawer, a door hinged right;
    5 legs."""
    W, H = 881, 1318
    y0, y1 = LH + T + 2, H - T - 2          # 118 … 1300
    XP = 367                                 # joint over the partition
    p = carcass(W, H)
    p.append(P("partition", [XP - 8, LH + T, 10, XP + 8, H - T, ZF0 - 2]))
    for i, y in enumerate([389, 665, 998]):
        p.append(P(f"shelf-l{i + 1}", [T + 0.5, y, 10, XP - 8.5, y + T, ZF0 - 2]))
    p += [P("shelf-r-low", [XP + 8.5, 389, 10, W - T - 0.5, 405, ZF0 - 2]),
          P("shelf-r-1", [XP + 8, 669, 10, W - T, 685, ZF0 - 2]),
          P("shelf-r-2", [XP + 8, 860, 10, W - T, 876, ZF0 - 2])]
    dl = [P("dl-white", [18, y0, ZF0, 214, y1, ZF1], kind="front")] + strip("dl", 214, XP - 1.5, y0, y1)
    dl.append(knob("dl", 214 + 50 + 5 + 23.5, 812))
    xr0, xr1 = XP + 1.5, W - 18
    fl = [P("flap", [xr0, 878, ZF0, xr1, y1, ZF1], kind="front"), knob("flap", 616, 1239)]
    dr = [P("dr", [xr0, y0, ZF0, xr1, 685, ZF1], kind="front"), knob("dr", 616, 618)]
    dp, dmv = drawer("drawer", [xr0, 688, ZF0, xr1, 875, ZF1], XP + 8 + 13, W - T - 13, 700, 150, ky=812)
    p += dl + fl + dr + dp
    p += legs([50, W - 50], [50, D - 50], extra=[(XP, D / 2)])
    moves = [door("door_left", dl, "left"), {"type": "flap", "name": "flap", "parts": ids(fl), "hinge": "bottom", "angle": 90},
             dmv, door("door_right", dr, "right")]
    model("ardo-0-02", "П3.598.0.02", "Тумба «Ардо»", "living", [W, D, H],
          BYPHOTO + "; левая дверь — белый щит + дубовая планка; справа откидная (вниз) крышка-секретер, ящик, дверь")
    return dump("ardo-0-02", [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------------ комод 0.07


def s007():
    """Комод П3.598.0.07 (1540 × 420 × 860): two doors (oak strip at the outer edge + white board, hinged at the outer
    sides, a white shelf behind each) round a column of three drawers; 5 legs."""
    W, H = 1540, 860
    y0, y1 = LH + T + 2, H - T - 2          # 118 … 842
    j1, j2 = 519, 1019
    p = carcass(W, H)
    p += [P("partition-1", [j1 - 8, LH + T, 10, j1 + 8, H - T, ZF0 - 2]),
          P("partition-2", [j2 - 8, LH + T, 10, j2 + 8, H - T, ZF0 - 2]),
          P("shelf-l", [T + 0.5, 470, 10, j1 - 8.5, 486, ZF0 - 2], mat="white"),
          P("shelf-r", [j2 + 8.5, 470, 10, W - T - 0.5, 486, ZF0 - 2], mat="white")]
    dl = strip("dl", 18, 170, y0, y1) + [P("dl-white", [170, y0, ZF0, j1 - 1.5, y1, ZF1], kind="front"),
                                          knob("dl", 463, 475)]
    dr = [P("dr-white", [j2 + 1.5, y0, ZF0, 1370, y1, ZF1], kind="front")] + strip("dr", 1370, W - 18, y0, y1)
    dr.append(knob("dr", 1075, 475))
    p += dl + dr
    moves = [door("door_left", dl, "left"), door("door_right", dr, "right")]
    fh = (y1 - y0 - 2 * 3) / 3
    for k in range(3):
        fy0 = y0 + k * (fh + 3)
        dp, mv = drawer(f"drawer_{k + 1}", [j1 + 1.5, fy0, ZF0, j2 - 1.5, fy0 + fh, ZF1], j1 + 8 + 13, j2 - 8 - 13,
                        fy0 + 25, 150)
        p += dp
        moves.append(mv)
    p += legs([50, W - 50], [50, D - 50], extra=[(W / 2, D / 2)])
    model("ardo-0-07", "П3.598.0.07", "Комод «Ардо»", "living", [W, D, H],
          BYPHOTO + "; двери — дубовая планка у наружного края + белый щит, в середине три ящика")
    return dump("ardo-0-07", [W, D, H], p, moves)


# ------------------------------------------------------------------------------------------------ тумба ТВ 0.03


def s003():
    """Тумба ТВ П3.598.0.03 (1581 × 420 × 486): left door = white board + oak strip (knob on the strip, high), hinged
    left; right: an open niche (a small partition in it) over a wide drawer; 5 legs."""
    W, H = 1581, 486
    y0, y1 = LH + T + 2, H - T - 2          # 118 … 468
    XP = 563.5
    p = carcass(W, H)
    p += [P("partition", [XP - 8, LH + T, 10, XP + 8, H - T, ZF0 - 2]),
          P("niche-bottom", [XP + 8, 307, 10, W - T, 323, D]),
          P("niche-partition", [1027, 323, 10, 1043, H - T, ZF0 - 2])]
    dl = [P("dl-white", [18, y0, ZF0, 410, y1, ZF1], kind="front")] + strip("dl", 410, XP - 1.5, y0, y1)
    dl.append(knob("dl", 410 + 50 + 5 + 24, 405))
    dp, dmv = drawer("drawer", [XP + 1.5, y0, ZF0, W - 18, 305, ZF1], XP + 8 + 13, W - T - 13, 135, 140,
                     kx=1064, ky=235)
    p += dl + dp
    p += legs([55, W - 55], [50, D - 50], extra=[(XP, D / 2)])
    model("ardo-0-03", "П3.598.0.03", "Тумба ТВ «Ардо»", "living", [W, D, H],
          BYPHOTO + "; левая дверь — белый щит + дубовая планка, справа открытая ниша над ящиком")
    return dump("ardo-0-03", [W, D, H], p, [door("door", dl, "left"), dmv])


# ------------------------------------------------------------------------------------------------ стол журнальный 0.05


def s005():
    """Стол журнальный П3.598.0.05 (1100 × 600 × 455), all «Дуб мадура»: top 16 over four L-shaped panel legs 120 ×
    120 (two boards each), aprons 92 high round the top, a shelf 165 above the floor between the end boards (its ends
    hidden behind the legs' face boards)."""
    W, Dt, H = 1100, 600, 455
    yt = H - T                     # 439: underside of the top
    p = [P("top", [0, yt, 0, W, H, Dt])]
    k = 0
    for xs in ("l", "r"):
        for zs in ("b", "f"):
            k += 1
            x0 = 0 if xs == "l" else W - 120
            xo0, xo1 = (0, T) if xs == "l" else (W - T, W)          # the outer (end) board
            if zs == "f":
                p.append(P(f"leg-{k}-face", [x0, 0, Dt - T, x0 + 120, yt, Dt], grain="y"))
                p.append(P(f"leg-{k}-end", [xo0, 0, Dt - 120, xo1, yt, Dt - T], grain="y"))
            else:
                p.append(P(f"leg-{k}-face", [x0, 0, 0, x0 + 120, yt, T], grain="y"))
                p.append(P(f"leg-{k}-end", [xo0, 0, T, xo1, yt, 120], grain="y"))
    p += [P("apron-f", [120, yt - 92, Dt - T, W - 120, yt, Dt]),
          P("apron-b", [120, yt - 92, 0, W - 120, yt, T]),
          P("apron-l", [0, yt - 92, 120, T, yt, Dt - 120]),
          P("apron-r", [W - T, yt - 92, 120, W, yt, Dt - 120]),
          P("shelf", [T, 165, T, W - T, 181, Dt - T])]
    model("ardo-0-05", "П3.598.0.05", "Стол журнальный «Ардо»", "tables", [W, Dt, H],
          BYPHOTO + "; весь в «Дуб мадура»")
    return dump("ardo-0-05", [W, Dt, H], p, [])


# ------------------------------------------------------------------------------------------------ полка 0.04


def s004():
    """Полка навесная П3.598.0.04 (1200 × 215 × 240, wall): a white back board 240 high with the oak strip in it
    (left of the middle), a shelf 22 × 199 over the full width 20 mm above its lower edge."""
    W, Dp, H = 1200, 215, 240
    p = [P("back-l", [45, 0, 0, 398, H, T], kind="panel", mat="front"),
         P("back-r", [533, 0, 0, 1155, H, T], kind="panel", mat="front")]
    p += strip("strip", 398, 533, 0, H, z0=0, z1=T, kind="panel")
    p.append(P("shelf", [0, 20, T, W, 42, Dp]))
    model("ardo-0-04", "П3.598.0.04", "Полка навесная «Ардо»", "living", [W, Dp, H],
          BYPHOTO + "; белая задняя доска с дубовой планкой, полка 22 мм", mount="wall")
    return dump("ardo-0-04", [W, Dp, H], p, [])


# ------------------------------------------------------------------------------------------------ стол письменный 0.08


def rknob(tag, x, y, zc, d=30):
    """A knob on a +x face (the pedestal's drawers face the knee space): built on a +z face and turned 90° about y."""
    return {"id": f"k-{tag}", "kind": "handle", "model": "knob", "at": [x, round(y, 1)], "d": d, "t": 12,
            "standoff": 20, "z": round(zc, 1), "rot": {"axis": "y", "deg": 90, "about": [x, round(y, 1), round(zc, 1)]},
            "covers": ["k"]}


def s008():
    """Стол письменный П3.598.0.08 (1250 × 1250 × 755): an L — the desk (oak top 1250 × 600, white right side panel,
    white modesty panel) and a white pedestal return 450 wide × 1250 long along its left end. The pedestal's outer
    panel rises to the desk top and carries its left end (an upstand 150 over the pedestal top); the pedestal faces the
    knee space (+x): open shelves under the desk top, three drawers in front of it. The pedestal stands on 10 mm
    glides."""
    W, B, H = 1250, 1250, 755
    Dd = 600                       # desk depth
    yt = H - T                     # 739
    PW = 450                       # pedestal width (x)
    g = 10                         # glides
    ptop = 574                     # pedestal top underside
    p = [P("top", [0, yt, 0, W, H, Dd], grain="x"),
         P("side-r", [W - T, 0, 0, W, yt, Dd], mat="front"),
         P("modesty", [PW, 549, T, W - T, yt, 2 * T], mat="front"),
         # the pedestal
         P("p-outer", [0, g, 0, T, yt, B], mat="front"),
         P("p-end-back", [T, g, 0, PW, ptop, T], mat="front"),
         P("p-end-front", [T, g, B - T, PW, ptop, B], mat="front"),
         P("p-top", [T, ptop, 0, PW, ptop + T, B], mat="front"),
         P("p-bottom", [T, g, T, PW, g + T, B - T], mat="front"),
         P("p-partition", [T, g + T, 616, PW, ptop, 632], mat="front"),
         P("p-shelf", [T, 300, T, PW, 316, 616], mat="front")]
    k = 0
    for x in (60, PW - 60):
        for z in (40, B - 40):
            k += 1
            p.append(P(f"glide-{k}", [x - 15, 0, z - 15, x + 15, g, z + 15], mat="black", covers=["h"]))
    moves = []
    z0, z1 = 634, B - T - 2
    y0, y1 = g + T + 2, ptop - 2
    fh = (y1 - y0 - 2 * 3) / 3
    for i in range(3):
        fy0 = y0 + i * (fh + 3)
        tag = f"drawer_{i + 1}"
        by0, bh = fy0 + 15, min(fh - 40, 140)
        parts = [P(f"{tag}-front", [PW - T, fy0, z0, PW, fy0 + fh, z1], kind="front", grain="z"),
                 P(f"{tag}-side-a", [30, by0, 632 + 13, PW - T, by0 + bh, 632 + 13 + T], mat="front"),
                 P(f"{tag}-side-b", [30, by0, B - T - 13 - T, PW - T, by0 + bh, B - T - 13], mat="front"),
                 P(f"{tag}-back", [30, by0, 632 + 13 + T, 30 + T, by0 + bh, B - T - 13 - T], mat="front"),
                 P(f"{tag}-bottom", [36, by0 + 8, 632 + 13 + 10, PW - T - 2, by0 + 11.5, B - T - 13 - 10], kind="back", mat="white"),
                 rknob(tag, PW, fy0 + fh / 2, (z0 + z1) / 2)]
        p += parts
        moves.append({"type": "slide", "name": tag, "parts": ids(parts), "by": [330, 0, 0]})
    model("ardo-0-08", "П3.598.0.08", "Стол письменный «Ардо»", "office", [W, B, H],
          BYPHOTO + "; угловой: стол 1250×600 + тумба-приставка 450×1250 (ящики к месту сидящего, открытые полки под "
                    "столешницей); белый корпус, столешница «Дуб мадура»")
    return dump("ardo-0-08", [W, B, H], p, moves)


# ------------------------------------------------------------------------------------------------ catalogue fragment
FINISHES = [
    {"id": "ardo-white-madura", "name": "Белый / Дуб мадура",
     "body": "door_enamel_whitey#b09989", "front": "door_enamel_whitey#dee0df", "back": "door_enamel_whitey#dee0df",
     "swatch": "#dee0df"},
]
COLLECTION = {
    "id": "ardo", "name": "Ардо", "brand": "Пинскдрев", "finishes": ["ardo-white-madura"], "metal": "black",
    "note": "Каталог «Корпусная мебель ч. II» 2025, PDF с. 97 (с. 190–191). Набор для гостиной П3.598; все модули по "
            "каталогу и фото сайта (инструкций нет). Корпус ЛДСП 16 «Дуб мадура» (крышка и дно во всю ширину, боковины "
            "между ними), фасады ЛДСП 16 белые вкладные, дубовая планка-пилястра 152 мм из трёх досок с тёмными "
            "линиями; задние стенки ХДФ белые в пазах; чёрные круглые ручки-кнопки, чёрные квадратные опоры 100 мм.",
}


def write_catalog():
    frag = {"finishes": FINISHES, "profiles": {}, "collections": [COLLECTION], "models": MODELS}
    path = os.path.join(HERE, "ardo_catalog.json")
    with open(path, "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return path


if __name__ == "__main__":
    for f in [s001, s00101, s006, s002, s007, s003, s005, s004, s008]:
        print(f())
    print(write_catalog())
