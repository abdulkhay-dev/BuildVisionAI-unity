"""«Брауни» (Пинскдрев П7.043, каталог «Корпусная мебель ч. II», PDF p. 114): 6 articles, all by catalogue.

No instruction exists. Sources: the p. 114 spread (bedroom photo, module cut-outs with sizes, the wardrobe's interior
sketch, the swatch «Дуб Каньон» / «Черный») and the only two product pages the site still has (Секция нижняя
П7.043.1.21 = 043.201: two front-on photos; Зеркало П7.043.1.41 = 043.401: a front-on photo). The Скамья П7.043.1.81
(an upholstered bench) is out of scope.

Construction (common Pinskdrev bedroom construction, read off the photos):
  * ЛДСП 16 «Дуб Каньон»: sides to the floor, tops over the sides, bottoms on a front plinth; backs ХДФ in grooves
    (z 6…9.5); «Черный» (a dark woodgrain ЛДСП) on the accent parts: the wardrobe's door panels, the chest's top, its
    door, the niche backs;
  * fronts ЛДСП 16 overlay (the chest, the section 1.21) or inset (the bedside table) with 2–3 mm gaps; black bar
    handles; the section 1.21 has grip gaps instead of handles;
  * the coupe wardrobe: two sliding doors in aluminium profiles on an upper and a lower track, each door a Каньон
    stile + two «Черный» panels round a Каньон band;
  * the bed: a Каньон box (headboard, side rails, foot board) on a recessed black plinth, a storage niche under a
    lifting metal frame (металлокаркас с подъёмным механизмом), a black buttoned soft panel on the headboard.

    python3 tools/casegoods/gen/brauni.py        # writes the designs and gen/brauni_catalog.json
"""
import json
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
T = 16
BYCAT = "по каталогу, без инструкции"

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
    m = {"id": mid, "code": code, "name": name, "collection": "brauni", "category": category, "size": size}
    m.update(kw)
    m["page"] = 114
    m["note"] = note
    MODELS.append(m)


def bar(tag, x, y, z, d=224, axis="x"):
    """Black bar handle (a round bar on two posts)."""
    return {"id": f"h-{tag}", "kind": "handle", "model": "bar", "at": [round(x, 1), round(y, 1)],
            "dir": "right" if axis == "x" else "up", "d": d, "band": 12, "t": 12, "standoff": 22, "z": z,
            "covers": ["h"]}


def drawer_box(tag, bx0, bx1, by0, bh, z0, zf, mat="body"):
    """ЛДСП 16 sides and back, an ХДФ bottom in grooves, between bx0 … bx1 (13 mm runner gaps are the caller's)."""
    return [P(f"{tag}-side-l", [bx0, by0, z0, bx0 + T, by0 + bh, zf], mat=mat),
            P(f"{tag}-side-r", [bx1 - T, by0, z0, bx1, by0 + bh, zf], mat=mat),
            P(f"{tag}-back", [bx0 + T, by0, z0, bx1 - T, by0 + bh, z0 + T], mat=mat),
            P(f"{tag}-bottom", [bx0 + 10, by0 + 8, z0 + 6, bx1 - 10, by0 + 11.5, zf - 2], kind="back")]


def drawer_move(tag, parts, z0, zf):
    return {"type": "drawer", "name": tag, "parts": ids(parts), "travel": round((zf - z0) * 0.8)}


# ------------------------------------------------------------------------------------------------ шкаф-купе 1.11


def w111():
    """Шкаф-купе 2д П7.043.1.11 (2000 × 610 × 2332): carcass Каньон (top over the sides, the sides to the floor, the
    bottom on a front plinth 90), a partition in the middle; two coupe doors ~1000 wide in silver profiles (rear track
    left, front track right, 32 mm overlap), each a Каньон stile 320 at the outer edge + a «Черный» panel over and
    under a Каньон band 311 (the door proportions measured on the p. 114 cut-out). Inside (the p. 114 sketch): left —
    two shelves over a hanging rail (the section 1.21 stands at its bottom), right — four shelves over a short
    hanging rail."""
    W, B, H = 2000, 610, 2332
    yb = 90                        # bottom on the plinth
    p = [P("top", [0, H - T, 0, W, H, B]),
         P("side-l", [0, 0, 0, T, H - T, B]),
         P("side-r", [W - T, 0, 0, W, H - T, B]),
         P("bottom", [T, yb, 0, W - T, yb + T, B]),
         P("plinth", [T, 0, B - 20 - T, W - T, yb, B - 20]),
         P("plinth-back", [T, 0, 30, W - T, yb, 30 + T]),
         P("back", [T - 7, yb + T - 7, 6, W - T + 7, H - T + 7, 9.5], kind="back"),
         P("partition", [W / 2 - 8, yb + T, 10, W / 2 + 8, H - T, 530])]
    xl0, xl1, xr0, xr1 = T, W / 2 - 8, W / 2 + 8, W - T
    for i, y in enumerate([1782, 2050]):
        p.append(P(f"shelf-l{i + 1}", [xl0 + 0.5, y, 10, xl1 - 0.5, y + T, 530]))
    for i, y in enumerate([1110, 1410, 1710, 2010]):
        p.append(P(f"shelf-r{i + 1}", [xr0 + 0.5, y, 10, xr1 - 0.5, y + T, 530]))
    p += [P("rail-l", [xl0 + 4, 1715, 258, xl1 - 4, 1740, 283], kind="tube", mat="chrome"),
          P("rail-r", [xr0 + 4, 1045, 258, xr1 - 4, 1070, 283], kind="tube", mat="chrome")]
    # tracks
    p += [P("track-top", [T, H - T - 20, 540, W - T, H - T, 604], mat="chrome", edge=0.5),
          P("track-bottom", [T, yb + T, 540, W - T, yb + T + 6, 604], mat="chrome", edge=0.5)]
    dy0, dy1 = yb + T + 8, H - T - 22           # 114 … 2294
    band0, band1 = 1050, 1361

    def coupe(tag, x0, x1, z0, outer):
        """A coupe door x0 … x1 on its track (boards z0 … z0+16, profiles 4 mm proud on both sides)."""
        pw = 20
        parts = [P(f"{tag}-prof-l", [x0, dy0, z0 - 4, x0 + pw, dy1, z0 + T + 4], mat="chrome", edge=1),
                 P(f"{tag}-prof-r", [x1 - pw, dy0, z0 - 4, x1, dy1, z0 + T + 4], mat="chrome", edge=1)]
        b0, b1 = x0 + pw, x1 - pw
        if outer == "left":
            s0, s1, p0, p1 = b0, b0 + 320, b0 + 320, b1
        else:
            s0, s1, p0, p1 = b1 - 320, b1, b0, b1 - 320
        parts += [P(f"{tag}-stile", [s0, dy0, z0, s1, dy1, z0 + T], kind="front", grain="y"),
                  P(f"{tag}-black-low", [p0, dy0, z0, p1, band0, z0 + T], kind="front", mat="accent", grain="y"),
                  P(f"{tag}-band", [p0, band0, z0, p1, band1, z0 + T], kind="front", grain="x"),
                  P(f"{tag}-black-high", [p0, band1, z0, p1, dy1, z0 + T], kind="front", mat="accent", grain="y")]
        return parts

    dl = coupe("dl", T, W / 2 + 16, 552, "left")          # rear track
    dr = coupe("dr", W / 2 - 16, W - T, 578, "right")     # front track
    p += dl + dr
    moves = [{"type": "slide", "name": "door_left", "parts": ids(dl), "by": [940, 0, 0]},
             {"type": "slide", "name": "door_right", "parts": ids(dr), "by": [-940, 0, 0]}]
    model("brauni-1-11", "П7.043.1.11", "Шкаф-купе 2д «Брауни»", "bedroom", [W, B, H],
          BYCAT + "; двери-купе в алюминиевом профиле: стойка «Дуб Каньон» + две панели «Черный»; в левое отделение "
                  "ставится секция П7.043.1.21")
    return dump("brauni-1-11", [W, B, H], p, moves)


# ------------------------------------------------------------------------------------------------ секция 1.21


def t121():
    """Тумба (секция нижняя) П7.043.1.21 (500 × 480 × 670), set into the left compartment of the wardrobe 1.11 and
    tied to it: sides to the floor, top over them, three drawers with overlay fronts 188 high and 31 mm grip gaps
    above them (no handles) — measured on the site's front-on photo."""
    W, B, H = 500, 480, 670
    zf0 = B - T
    p = [P("top", [0, H - T, 0, W, H, B]),
         P("side-l", [0, 0, 0, T, H - T, zf0]),
         P("side-r", [W - T, 0, 0, W, H - T, zf0]),
         P("bottom", [T, 0, 0, W - T, T, zf0]),
         P("back", [T - 7, 9, 6, W - T + 7, H - T + 7, 9.5], kind="back")]
    moves = []
    for k, (fy0, fy1) in enumerate([(2, 190), (221, 409), (440, 628)]):
        tag = f"drawer_{k + 1}"
        parts = [P(f"{tag}-front", [2, fy0, zf0, W - 2, fy1, B], kind="front", grain="x")]
        parts += drawer_box(tag, T + 13, W - T - 13, max(fy0 + 12, T + 8), 150, 20, zf0)
        p += parts
        moves.append(drawer_move(tag, parts, 20, zf0))
    model("brauni-1-21", "П7.043.1.21", "Тумба «Брауни»", "bedroom", [W, B, H],
          BYCAT + " (и фото сайта, секция нижняя 043.201); ставится в левое отделение шкафа-купе П7.043.1.11, "
                  "ящики без ручек (зазор-захват над каждым фасадом)")
    return dump("brauni-1-21", [W, B, H], p, moves)


# ------------------------------------------------------------------------------------------------ тумба прикроватная 1.23


def t123():
    """Тумба прикроватная П7.043.1.23 (402 × 350 × 500): sides to the floor, top over them, a front plinth 60, an
    inset drawer 238 high with a black bar handle, an open niche over it with a «Черный» back."""
    W, B, H = 402, 350, 500
    zf0 = B - T
    p = [P("top", [0, H - T, 0, W, H, B]),
         P("side-l", [0, 0, 0, T, H - T, B]),
         P("side-r", [W - T, 0, 0, W, H - T, B]),
         P("plinth", [T, 0, zf0, W - T, 60, B]),
         P("bottom", [T, 60, 0, W - T, 76, zf0]),
         P("niche-bottom", [T, 302, 10, W - T, 318, B]),
         P("back", [T - 7, 69, 6, W - T + 7, H - T + 7, 9.5], kind="back")]
    tag = "drawer"
    parts = [P(f"{tag}-front", [T + 2, 62, zf0, W - T - 2, 300, B], kind="front", grain="x"),
             bar(tag, W / 2, 190, B, d=224)]
    parts += drawer_box(tag, T + 13, W - T - 13, 90, 170, 20, zf0)
    p += parts
    model("brauni-1-23", "П7.043.1.23", "Тумба прикроватная «Брауни»", "bedroom", [W, B, H],
          BYCAT + "; ящик под открытой нишей, ниша с задней стенкой «Черный»")
    return dump("brauni-1-23", [W, B, H], p, [drawer_move(tag, parts, 20, zf0)])


# ------------------------------------------------------------------------------------------------ комод 1.31


def k131():
    """Комод П7.043.1.31 (1604 × 436 × 1065): a chest (four Каньон drawers, a «Черный» door hinged right, a
    «Черный» top at 896) standing in front of a shallower frame (336 deep): an open three-cell column on the left
    (black back), a Каньон top board over the full width at 1065, a right upright over the chest top, and an open
    niche with a «Черный» back between the chest top and the top board."""
    W, B, H = 1604, 436, 1065
    FD = 336                       # the frame's depth
    XC = 282                       # the chest's left edge (the column's width)
    CH = 896                       # the chest's height (top of its black top)
    zc = B - T                     # chest carcass front (420): overlay fronts in front of it
    p = [P("top", [0, H - T, 0, W, H, FD]),
         # the column
         P("col-side-l", [0, 0, 0, T, H - T, FD]),
         P("col-side-r", [XC - T, 0, 0, XC, H - T, FD]),
         P("col-plinth", [T, 0, FD - T - 4, XC - T, 64, FD - 4]),
         P("col-bottom", [T, 64, 0, XC - T, 80, FD]),
         P("col-shelf-1", [T, 412, 10, XC - T, 428, FD]),
         P("col-shelf-2", [T, 726, 10, XC - T, 742, FD]),
         P("col-back", [T - 7, 73, 6, XC - T + 7, H - T + 7, 9.5], kind="back"),
         # the chest
         P("c-side-l", [XC, 0, 0, XC + T, CH - T, zc]),
         P("c-side-r", [W - T, 0, 0, W, CH - T, zc]),
         P("c-top", [XC, CH - T, 0, W, CH, B], mat="accent"),
         P("c-plinth", [XC + T, 0, zc - T, W - T, 64, zc]),
         P("c-bottom", [XC + T, 64, 0, W - T, 80, zc - T]),
         P("c-partition", [1097, 80, 10, 1113, CH - T, zc]),
         P("c-shelf", [1113.5, 480, 10, W - T - 0.5, 496, zc]),
         P("c-back", [XC + T - 7, 73, 6, W - T + 7, CH - T + 7, 9.5], kind="back"),
         # the frame over the chest: the right upright and the niche's black back
         P("up-r", [W - T, CH, 0, W, H - T, FD]),
         P("niche-back", [XC, CH, 0, W - T, H - T, T], mat="accent")]
    moves = []
    fy0, fy1 = 82, CH - T - 2          # the fronts' zone (82 … 878)
    fh = (fy1 - fy0 - 3 * 3) / 4
    for k in range(4):
        y0 = fy0 + k * (fh + 3)
        tag = f"drawer_{k + 1}"
        parts = [P(f"{tag}-front", [XC + 2, y0, zc, 1103.5, y0 + fh, B], kind="front", grain="x"),
                 bar(tag, (XC + 2 + 1103.5) / 2, y0 + fh - 45, B, d=256)]
        parts += drawer_box(tag, XC + T + 13, 1097 - 13, y0 + 20, min(fh - 50, 150), 30, zc)
        p += parts
        moves.append(drawer_move(tag, parts, 30, zc))
    d = [P("door", [1106.5, fy0, zc, W - 2, fy1, B], kind="front", mat="accent", grain="y"),
         bar("door", 1354, 800, B, d=192)]
    p += d
    moves.append({"type": "door", "name": "door", "parts": ids(d), "hinge": "right", "angle": 100})
    model("brauni-1-31", "П7.043.1.31", "Комод «Брауни»", "bedroom", [W, B, H],
          BYCAT + "; комод (4 ящика + дверь «Черный») перед рамой-надстройкой глубиной 336: открытая колонка слева, "
                  "ниша с задней стенкой «Черный»")
    return dump("brauni-1-31", [W, B, H], p, moves)


# ------------------------------------------------------------------------------------------------ зеркало 1.41


def m141():
    """Зеркало П7.043.1.41 (1000 × 20 × 600, wall): a Каньон board 16 with the mirror 800 × 524 × 4 glued on
    (margins 100 at the ends, 38 along the long sides — the site's photo). It hangs either way: built landscape as
    the index / the module list / the site give it (L1000 × H600)."""
    W, B, H = 1000, 20, 600
    p = [P("board", [0, 0, 0, W, H, T], grain="x"),
         P("mirror", [100, 38, T, 900, 562, B], kind="mirror")]
    model("brauni-1-41", "П7.043.1.41", "Зеркало «Брауни»", "decor", [W, B, H],
          BYCAT + " (и фото сайта); вешается горизонтально или вертикально (на с. 114 также L600×B20×H1000), "
                  "построено горизонтальным", mount="wall")
    return dump("brauni-1-41", [W, B, H], p, [])


# ------------------------------------------------------------------------------------------------ кровать 1.08


def b108():
    """Кровать 2-16 П7.043.1.08 (1678 wide × 2058 long × 1020, sleeping place 2000 × 1600): a Каньон headboard
    22 × 1020 with a black buttoned soft panel 390 high over its top, side rails and a foot board 22 × 272 at
    y 100…372 on a black plinth set 140 mm in from the sides and 60 from the foot, a storage bottom inside, the lifting metal frame 2000 × 1600 with
    slats and a mattress."""
    W, L, H = 1678, 2058, 1020
    t = 22
    yb, yr = 100, 372
    PI = 140                       # the plinth's inset from the sides (the p. 114 cut-out)
    p = [P("head", [0, 0, 0, W, H, t], grain="x"),
         {"id": "soft", "kind": "soft", "mat": "fabric", "tufts": [10, 1], "box": [0, 630, t, W, H, t + 60]},
         P("rail-l", [0, yb, t, t, yr, L - t], grain="z"),
         P("rail-r", [W - t, yb, t, W, yr, L - t], grain="z"),
         P("foot", [0, yb, L - t, W, yr, L], grain="x"),
         P("storage-bottom", [t, yb, t, W - t, yb + T, L - t]),
         # the recessed black plinth
         P("plinth-l", [PI, 0, t + 38, PI + T, yb, L - 60], mat="accent"),
         P("plinth-r", [W - PI - T, 0, t + 38, W - PI, yb, L - 60], mat="accent"),
         P("plinth-foot", [PI + T, 0, L - 60 - T, W - PI - T, yb, L - 60], mat="accent"),
         P("plinth-head", [PI + T, 0, t + 38, W - PI - T, yb, t + 38 + T], mat="accent"),
         P("plinth-mid", [W / 2 - 8, 0, t + 38 + T, W / 2 + 8, yb, L - 60 - T], mat="accent")]
    fx0, fx1 = (W - 1600) / 2, (W + 1600) / 2        # 39 … 1639
    z0, z1 = 29, 2029
    p += [P("m-frame-l", [fx0, yr - 30, z0, fx0 + 30, yr, z1], mat="black", covers=["m"]),
          P("m-frame-r", [fx1 - 30, yr - 30, z0, fx1, yr, z1], mat="black"),
          P("m-frame-head", [fx0 + 30, yr - 30, z0, fx1 - 30, yr, z0 + 30], mat="black"),
          P("m-frame-foot", [fx0 + 30, yr - 30, z1 - 30, fx1 - 30, yr, z1], mat="black"),
          P("m-frame-mid", [W / 2 - 15, yr - 30, z0 + 30, W / 2 + 15, yr, z1 - 30], mat="black")]
    for i in range(24):
        z = 60 + i * 81
        p.append(P(f"m-slat-{i + 1}", [fx0 + 6, yr, z, fx1 - 6, yr + 8, z + 53], mat="door_enamel_whitey#c9a877"))
    p.append({"id": "mattress", "kind": "mattress", "box": [fx0, yr + 8, z0, fx1, yr + 208, z1]})
    model("brauni-1-08", "П7.043.1.08", "Кровать 2-16 «Брауни»", "bedroom", [W, L, H],
          BYCAT + "; спальное место 2000×1600, металлокаркас с подъёмным механизмом и нишей для белья; мягкая панель "
                  "изголовья «Черный» с пуговицами; цоколь «Черный» утоплен")
    return dump("brauni-1-08", [W, L, H], p, [])


# ------------------------------------------------------------------------------------------------ catalogue fragment
FINISHES = [
    {"id": "brauni-kanon-black", "name": "Дуб Каньон / Черный",
     "body": "door_enamel_whitey#856649", "front": "door_enamel_whitey#856649", "back": "door_enamel_whitey#1c1d18",
     "roles": {"accent": "door_enamel_whitey#1c1d18", "fabric": "velvet#1f1f1f"}, "swatch": "#856649"},
]
COLLECTION = {
    "id": "brauni", "name": "Брауни", "brand": "Пинскдрев", "finishes": ["brauni-kanon-black"], "metal": "black",
    "note": "Каталог «Корпусная мебель ч. II» 2025, PDF с. 114 (с. 224–225). Спальня П7.043; все модули по каталогу "
            "(инструкций нет; на сайте только секция 1.21 и зеркало). ЛДСП 16 «Дуб Каньон» и «Черный» (тёмный "
            "древесный декор): панели дверей-купе, крышка и дверь комода, задние стенки ниш, цоколь кровати; двери-купе "
            "в алюминиевом профиле; чёрные ручки-рейлинги; кровать с подъёмным металлокаркасом и мягкой панелью "
            "изголовья. Скамья П7.043.1.81 (мягкая) не входит в корпусную мебель.",
}


def write_catalog():
    frag = {"finishes": FINISHES, "profiles": {}, "collections": [COLLECTION], "models": MODELS}
    path = os.path.join(HERE, "brauni_catalog.json")
    with open(path, "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    return path


if __name__ == "__main__":
    for f in [w111, t121, t123, k131, m141, b108]:
        print(f())
    print(write_catalog())
