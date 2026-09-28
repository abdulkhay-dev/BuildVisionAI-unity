"""Kids' room (reference tile «Детская комната»): single storage bed with a blue-grey headboard, light-wood desk with a
shelf, small swivel chair, blue bean bag, open shelving with books and toys, round ringed rug, framed space posters."""
import math

import tex
from kit import Kit
from models_bedroom import cover, padded, soft_pillow

TOYS = {"toy_red": (0.55, 0.06, 0.04), "toy_yellow": (0.8, 0.5, 0.04), "toy_blue": (0.05, 0.16, 0.5),
        "toy_green": (0.1, 0.32, 0.1)}
KIDS_BOOKS = ("#d9553b", "#f0c24a", "#3f7fbf", "#5aa36b", "#f2efe8", "#2f3d5c", "#e98a3a", "#8fb3d9")


def _toys(names):
    return {n: {"color": TOYS[n], "rough": 0.4} for n in names}


def bed_single_storage(e):
    """Single bed, mattress 0.9 × 2.0: light-wood base with three storage drawers on the right-hand (+X) side, recessed
    plinth, blue-grey upholstered headboard of two padded panels, white bedding, navy blanket, three pillows. Pivot back."""
    k = Kit(e["id"])
    W, yb, yf = 1.0, 1.04, -1.04                 # base width, back / front of the base
    hb = 0.05                                    # headboard thickness
    # headboard: wooden board with two padded panels
    k.box("frame", (0, yb + hb / 2, 0.5), (W + 0.04, hb, 1.0), r=0.006, seg=2)
    for sx in (-1, 1):
        padded(k, "headboard", (sx * 0.25, yb - 0.03, 0.72), 0.49, 0.54, 0.06, bulge=0.014)
    # base box, plinth, drawers on +X
    k.box("frame", (0, 0, 0.205), (W, yb - yf, 0.35), r=0.006, seg=2)
    k.box("plinth", (0, 0, 0.015), (W - 0.06, yb - yf - 0.06, 0.03), seg=1)
    dl = (yb - yf - 0.08) / 3
    for i in range(3):
        y = yf + 0.04 + dl * (i + 0.5)
        k.box("fronts", (W / 2 + 0.006, y, 0.2), (0.012, dl - 0.006, 0.25), r=0.002, seg=1)
        k.box("handle", (W / 2 + 0.013, y, 0.3), (0.004, 0.14, 0.022), r=0.002, seg=1)
    # mattress + blanket, sheet fold, pillows
    k.box("sheet", (0, -0.02, 0.42), (0.9, 2.0, 0.18), r=0.05, seg=3, soft=True)
    top = 0.51 + 0.015
    cover(k, "blanket", top, -0.485, 0.485, -1.08, 0.3, t=0.03, rc=0.05, hang_x=0.1, hang_front=0.12, wave=0.007, seed=4)
    k.box("sheet", (0, 0.2, top + 0.03), (1.02, 0.28, 0.035), r=0.016, seg=3, bulge=0.008)
    soft_pillow(k, "sheet", (0, 0.82, 0.66), (0.62, 0.18, 0.42), rot=(-24, 0, 2))
    soft_pillow(k, "pillow_a", (-0.13, 0.66, 0.66), (0.44, 0.14, 0.4), rot=(-18, 0, 7))
    soft_pillow(k, "pillow_b", (0.18, 0.62, 0.64), (0.38, 0.12, 0.34), rot=(-16, 0, -8))
    return k.finish(e, {"frame": "white_oak_veneer", "headboard": "velvet#8093a8", "plinth": "furniture_dark",
                        "fronts": "white_oak_veneer", "handle": "furniture_dark", "sheet": "cotton_poplin#f4f2ee",
                        "blanket": "cotton_waffle#34466e", "pillow_a": "velvet#3a4a6c", "pillow_b": "linen_rough#9fb0c2"},
                    pivot="back")


def desk_kids_wall(e):
    """Kids' desk 1.2 × 0.6 × 0.75, light wood: 3-drawer pedestal on the left, panel leg on the right, open shelf hutch
    above the back edge (h 1.22) with a row of books."""
    k = Kit(e["id"])
    W, D, H, t = 1.2, 0.6, 0.75, 0.03
    k.box("top", (0, 0, H - t / 2), (W, D, t), r=0.004, seg=2)
    # pedestal
    px, pw = -W / 2 + 0.2, 0.4
    k.box("body", (px, 0.01, (0.04 + H - t) / 2), (pw, D - 0.02, H - t - 0.04), r=0.002, seg=1)
    k.box("plinth", (px, 0.03, 0.02), (pw - 0.04, D - 0.08, 0.04), seg=1)
    dh = (H - t - 0.04) / 3
    for i in range(3):
        z = 0.04 + dh * (i + 0.5)
        k.box("fronts", (px, -D / 2 + 0.004, z), (pw - 0.006, 0.012, dh - 0.006), r=0.002, seg=1)
        k.box("handle", (px, -D / 2 - 0.006, z + dh / 2 - 0.05), (0.14, 0.012, 0.012), r=0.003, seg=2)
    # right leg and modesty panel
    k.box("body", (W / 2 - 0.0125, 0, (H - t) / 2), (0.025, D, H - t), r=0.002, seg=1)
    k.box("body", ((px + pw / 2 + W / 2 - 0.025) / 2, D / 2 - 0.03, H - t - 0.16), (W / 2 - 0.025 - px - pw / 2, 0.018, 0.3), seg=1)
    # hutch: two uprights and a shelf
    sd, sz = 0.25, 1.2
    for sx in (-1, 1):
        k.box("top", (sx * (W / 2 - 0.009), D / 2 - sd / 2, (H + sz) / 2), (0.018, sd, sz - H), r=0.002, seg=1)
    k.box("top", (0, D / 2 - sd / 2, sz + 0.011), (W, sd, 0.022), r=0.003, seg=2)
    k.box("books", (-0.35, D / 2 - 0.12, sz + 0.022 + 0.11), (0.32, 0.17, 0.22), r=0.002, seg=1, uv="front")
    k.box("toy_blue", (0.1, D / 2 - 0.12, sz + 0.022 + 0.03), (0.24, 0.17, 0.06), r=0.004, seg=1)
    k.box("toy_yellow", (0.1, D / 2 - 0.12, sz + 0.022 + 0.08), (0.22, 0.16, 0.04), r=0.004, seg=1, rot=(0, 0, 6))
    own = {"books": {"albedo": tex.book_spines(256, 256, 83, KIDS_BOOKS), "rough": 0.7}}
    own.update(_toys(["toy_blue", "toy_yellow"]))
    return k.finish(e, {"top": "oak_light_veneer", "body": "oak_light_veneer", "fronts": "oak_light_veneer",
                        "plinth": "furniture_dark", "handle": "black_metal"}, own=own, pivot="back")


def chair_kids_swivel(e):
    """Small swivel desk chair: grey upholstered seat (h 0.46) and back on a black gas column, 5-star base with casters."""
    k = Kit(e["id"])
    for i in range(5):
        a = 2 * math.pi * i / 5 + math.pi / 2
        ca, sa = math.cos(a), math.sin(a)
        k.box("base", (0.13 * ca, 0.13 * sa, 0.075), (0.25, 0.034, 0.03), r=0.01, seg=2, rot=(0, 6, math.degrees(a)),
              taper=(1, 0.8))
        k.box("base", (0.25 * ca, 0.25 * sa, 0.055), (0.03, 0.03, 0.03), r=0.006, seg=2)
        k.cyl("base", (0.25 * ca, 0.25 * sa, 0.025), 0.025, 0.022, seg=16, r=0.006, rot=(90, 0, math.degrees(a) + 90))
    k.cyl("base", (0, 0, 0.09), 0.045, 0.05, seg=24, r=0.008)
    k.cyl("column", (0, 0, 0.25), 0.022, 0.32, seg=20)
    k.cyl("base", (0, 0, 0.38), 0.035, 0.07, seg=20, rad2=0.028)
    k.box("base", (0, 0, 0.405), (0.26, 0.24, 0.02), r=0.006, seg=2)
    k.box("upholstery", (0, -0.01, 0.445), (0.4, 0.39, 0.06), r=0.028, seg=3, bulge=0.012)
    # back: bent support and padded back
    k.tube("base", [(0, 0.12, 0.41), (0, 0.2, 0.42), (0, 0.21, 0.5), (0, 0.215, 0.6)], 0.012, seg=8)
    k.box("upholstery", (0, 0.225, 0.68), (0.36, 0.05, 0.24), r=0.024, seg=3, rot=(-10, 0, 0), soft=True)
    k.box("base", (0, 0.244, 0.66), (0.12, 0.02, 0.12), r=0.006, seg=2, rot=(-10, 0, 0))
    return k.finish(e, {"base": "furniture_dark", "column": "black_metal", "upholstery": "velvet#44474d"})


def bean_bag_blue(e):
    """Blue bean bag Ø0.9, slumped: higher at the back, a seat dip in front, soft lumps."""
    k = Kit(e["id"])
    prof = [(0.0, 0.0), (0.28, 0.0), (0.38, 0.015), (0.44, 0.06), (0.47, 0.13), (0.475, 0.2), (0.46, 0.28), (0.43, 0.36),
            (0.38, 0.44), (0.32, 0.5), (0.25, 0.55), (0.18, 0.585), (0.1, 0.605), (0.0, 0.61)]
    obj = k.lathe("fabric", (0, 0, 0), prof, seg=48)
    for v in obj.data.vertices:
        x, y, z = v.co
        h = z / 0.61
        v.co.z = z * (1 + 0.32 * (y / 0.47) * h)                       # back rises
        v.co.z -= 0.17 * math.exp(-(x * x + (y + 0.08) ** 2) / 0.045) * h ** 1.5     # seat dip
        v.co.y -= 0.05 * math.sin(math.pi * h) * (y < 0)               # front belly
        lump = 0.012 * math.sin(x * 13 + z * 7) * math.sin(y * 11 - z * 5) * math.sin(math.pi * h)
        r = math.hypot(v.co.x, v.co.y) or 1
        v.co.x += lump * v.co.x / r
        v.co.y += lump * v.co.y / r
    return k.finish(e, {"fabric": "velvet#4a6a98"})


def shelf_open_kids(e):
    """Open shelving 1.0 × 0.35 × 1.8: five compartments with offset dividers, thin back, recessed plinth; books, toy
    blocks, a ball and two felt bins."""
    k = Kit(e["id"])
    W, D, H, t, zp = 1.0, 0.35, 1.8, 0.022, 0.05
    k.box("plinth", (0, 0.02, zp / 2), (W - 0.06, D - 0.06, zp), seg=1)
    for sx in (-1, 1):
        k.box("wood", (sx * (W / 2 - t / 2), 0, H / 2), (t, D, H), r=0.002, seg=1)
    k.box("wood", (0, 0, H - t / 2), (W, D, t), r=0.002, seg=1)
    k.box("back", (0, D / 2 - 0.005, (zp + H) / 2), (W - 2 * t, 0.008, H - zp - t), seg=1)
    ch = (H - t - zp - t) / 5                      # clear height of a compartment + shelf
    levels = [zp + t / 2 + ch * i for i in range(5)]
    for z in levels:
        k.box("wood", (0, 0, z), (W - 2 * t, D, t), r=0.002, seg=1)
    divs = [0.0, -0.15, 0.2, -0.1, 0.18]
    ih = ch - t
    for z, dx in zip(levels, divs):
        k.box("wood", (dx, 0, z + t / 2 + ih / 2), (t, D - 0.01, ih), seg=1)
    fy = -0.02
    b = [lv + t / 2 for lv in levels]              # floor of each compartment
    # 0: felt bins
    for x in (-0.24, 0.24):
        k.box("bins", (x, fy, b[0] + 0.13), (0.4, 0.3, 0.26), r=0.02, seg=2, soft=True)
    # 1: books left, block stack right
    k.box("books", (-0.3, fy, b[1] + 0.12), (0.3, 0.22, 0.24), r=0.002, seg=1, uv="front")
    k.box("toy_red", (0.2, fy, b[1] + 0.05), (0.1, 0.1, 0.1), r=0.008, seg=2)
    k.box("toy_yellow", (0.3, fy - 0.02, b[1] + 0.05), (0.1, 0.1, 0.1), r=0.008, seg=2, rot=(0, 0, 12))
    k.box("toy_blue", (0.25, fy, b[1] + 0.15), (0.1, 0.1, 0.1), r=0.008, seg=2, rot=(0, 0, -8))
    # 2: ball left, books right
    k.lathe("toy_red", (-0.25, fy, b[2]), [(0.0, 0.0)] + [(0.1 * math.sin(math.pi * i / 10), 0.1 - 0.1 * math.cos(math.pi * i / 10))
                                                         for i in range(1, 10)] + [(0.0, 0.2)], seg=24)
    k.box("books", (0.33, fy, b[2] + 0.13), (0.24, 0.22, 0.26), r=0.002, seg=1, uv="front")
    # 3: lying book stack left, books right
    k.box("toy_green", (-0.3, fy, b[3] + 0.015), (0.26, 0.2, 0.03), r=0.003, seg=1)
    k.box("toy_blue", (-0.3, fy, b[3] + 0.045), (0.24, 0.19, 0.03), r=0.003, seg=1, rot=(0, 0, 5))
    k.box("toy_yellow", (-0.3, fy, b[3] + 0.072), (0.22, 0.17, 0.025), r=0.003, seg=1, rot=(0, 0, -4))
    k.box("books", (0.2, fy, b[3] + 0.11), (0.38, 0.2, 0.22), r=0.002, seg=1, uv="front")
    # 4: books left, pyramid of blocks right
    k.box("books", (-0.3, fy, b[4] + 0.12), (0.34, 0.22, 0.24), r=0.002, seg=1, uv="front")
    k.box("toy_green", (0.28, fy, b[4] + 0.04), (0.08, 0.08, 0.08), r=0.006, seg=2)
    k.box("toy_red", (0.37, fy, b[4] + 0.04), (0.08, 0.08, 0.08), r=0.006, seg=2, rot=(0, 0, 10))
    k.box("toy_yellow", (0.325, fy, b[4] + 0.12), (0.08, 0.08, 0.08), r=0.006, seg=2, rot=(0, 0, -6))
    own = {"books": {"albedo": tex.book_spines(256, 256, 85, KIDS_BOOKS), "rough": 0.7}}
    own.update(_toys(["toy_red", "toy_yellow", "toy_blue", "toy_green"]))
    return k.finish(e, {"plinth": "furniture_dark", "wood": "walnut_european", "back": "walnut_european",
                        "bins": "wool_felt#9aa3ad"}, own=own, pivot="back")


def rug_round_blue(e):
    """Round rug Ø1.6 in concentric blue rings."""
    k = Kit(e["id"])
    k.disc("rug", (0, 0, 0.006), 0.8, seg=72, thick=0.012)
    return k.finish(e, {}, own={"rug": {"albedo": tex.rug_round_rings(1024, 61), "rough": 0.95}})


def _poster(e, variant):
    """Framed space poster 0.44 × 0.59 m: thin black frame, 0.4 × 0.55 print; pivot on the wall."""
    k = Kit(e["id"])
    W, H, b, d = 0.44, 0.59, 0.02, 0.022
    k.box("frame", (0, 0, H / 2 - b / 2), (W, d, b), r=0.002, seg=1)
    k.box("frame", (0, 0, -H / 2 + b / 2), (W, d, b), r=0.002, seg=1)
    for sx in (-1, 1):
        k.box("frame", (sx * (W / 2 - b / 2), 0, 0), (b, d, H - 2 * b), r=0.002, seg=1)
    k.box("frame", (0, d / 2 - 0.004, 0), (W - 0.01, 0.008, H - 0.01), seg=1)
    k.panel("art", (0, -0.003, 0), W - 2 * b, H - 2 * b)
    img = tex.rocket_poster(880, 640, 41 + variant * 7, variant)
    return k.finish(e, {"frame": "black_metal"}, own={"art": {"albedo": img, "rough": 0.5}}, pivot="wall")


def poster_rocket(e):
    return _poster(e, 0)


def poster_rocket_2(e):
    return _poster(e, 1)


def poster_rocket_3(e):
    return _poster(e, 2)


ENTRIES = [
    ("bed_single_storage", "Кровать детская 90 × 200 с ящиками", "bedroom", bed_single_storage, {"pivot": "back"}),
    ("desk_kids_wall", "Стол письменный детский 1,2 м с полкой", "tables", desk_kids_wall, {"pivot": "back"}),
    ("chair_kids_swivel", "Кресло детское компьютерное", "seating", chair_kids_swivel, {}),
    ("bean_bag_blue", "Кресло-мешок синее", "seating", bean_bag_blue, {}),
    ("shelf_open_kids", "Стеллаж открытый с книгами и игрушками", "storage", shelf_open_kids, {"pivot": "back"}),
    ("rug_round_blue", "Ковёр круглый Ø1,6 м, синие кольца", "textiles", rug_round_blue, {}),
    ("poster_rocket", "Постер «Ракета» в рамке", "decor", poster_rocket, {"pivot": "wall"}),
    ("poster_rocket_2", "Постер «Ракета» в рамке, вариант 2", "decor", poster_rocket_2, {"pivot": "wall"}),
    ("poster_rocket_3", "Постер «Ракета» в рамке, вариант 3", "decor", poster_rocket_3, {"pivot": "wall"}),
]
