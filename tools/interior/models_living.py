"""Living room (reference tile «Гостиная»): corner sofa, drum coffee table, tufted pouf, TV, floating media console,
ring chandelier, arc floor lamp, abstract rug and canvas, coffee-table decor."""
import math

import tex
from kit import Kit


def sofa_corner_lounge(e):
    """Deep low corner sofa 3.4 × 2.45 m (backs on both legs, short leg on the right coming forward); plinth, thick seat
    and back cushions, scatter pillows."""
    k = Kit(e["id"])
    W, D, L = 3.40, 1.02, 2.45            # length of the long leg, depth of both legs, length of the right leg
    x0, x1, back = -W / 2, W / 2, D / 2   # back edge of the long leg at +Y
    arm, rail = 0.22, 0.22
    up = "upholstery"
    front = back - L
    # plinths
    k.box(up, (0, back - D / 2, 0.13), (W, D, 0.2), r=0.035, seg=4)
    k.box(up, (x1 - D / 2, (front + back - D) / 2, 0.13), (D, L - D + 0.002, 0.2), r=0.035, seg=4)
    # back rails and arms
    k.box(up, ((x0 + arm + x1) / 2, back - rail / 2, 0.45), (W - arm, rail, 0.48), r=0.06, seg=5, soft=True)
    k.box(up, (x1 - rail / 2, (front + arm + back - rail) / 2, 0.45), (rail, L - arm - rail + 0.004, 0.48), r=0.06, seg=5, soft=True)
    k.box(up, (x0 + arm / 2, back - D / 2, 0.36), (arm, D, 0.46), r=0.07, seg=5, soft=True)
    k.box(up, (x1 - D / 2, front + arm / 2, 0.36), (D, arm, 0.46), r=0.07, seg=5, soft=True)
    # seat cushions: three on the long leg, the corner square, two on the right leg
    sz, sh, gap = 0.305, 0.18, 0.012
    ix0, ix1 = x0 + arm, x1 - D
    cw = (ix1 - ix0) / 3
    sy = (back - D + back - rail) / 2
    for i in range(3):
        k.box(up, (ix0 + cw * (i + 0.5), sy, sz), (cw - gap, D - rail - gap, sh), r=0.06, seg=5, bulge=0.02)
    cx = (x1 - D + x1 - rail) / 2
    k.box(up, (cx, sy, sz), (D - rail - gap, D - rail - gap, sh), r=0.06, seg=5, bulge=0.02)
    ly0, ly1 = front + arm, back - D
    cl = (ly1 - ly0) / 2
    for j in range(2):
        k.box(up, (cx, ly0 + cl * (j + 0.5), sz), (D - rail - gap, cl - gap, sh), r=0.06, seg=5, bulge=0.02)
    # back cushions
    bz = 0.62
    by = back - rail - 0.09
    for i in range(3):
        k.box(up, (ix0 + cw * (i + 0.5), by, bz), (cw - 0.02, 0.2, 0.44), r=0.08, seg=5, rot=(-8, 0, 0), bulge=0.03)
    k.box(up, (cx - 0.05, by, bz), (D - rail - 0.12, 0.2, 0.44), r=0.08, seg=5, rot=(-8, 0, 0), bulge=0.03)
    bx = x1 - rail - 0.09
    for j in range(2):
        k.box(up, (bx, ly0 + cl * (j + 0.5), bz), (0.2, cl - 0.02, 0.44), r=0.08, seg=5, rot=(0, 8, 0), bulge=0.03)
    # scatter pillows
    pz, py = 0.6, back - rail - 0.24
    k.pillow("pillow_a", (ix0 + 0.3, py, pz), (0.5, 0.16, 0.48), rot=(-14, 0, 10))
    k.pillow("pillow_b", (ix0 + 0.8, py - 0.01, pz), (0.48, 0.15, 0.46), rot=(-14, 0, -6))
    k.pillow("pillow_c", (ix0 + 1.3, py, pz - 0.02), (0.44, 0.14, 0.42), rot=(-12, 0, 4))
    k.pillow("pillow_a", (ix1 + 0.1, py, pz), (0.5, 0.16, 0.48), rot=(-14, 0, -8))
    k.pillow("pillow_b", (bx - 0.2, py - 0.12, pz), (0.48, 0.15, 0.46), rot=(-14, 0, -45))
    k.pillow("pillow_c", (bx - 0.15, ly0 + 0.35, pz - 0.02), (0.44, 0.14, 0.42), rot=(-12, 0, -80))
    return k.finish(e, {up: "velvet#c9bba8", "pillow_a": "velvet#7a7672", "pillow_b": "linen_rough#a89683",
                        "pillow_c": "velvet#6a5040"}, pivot="back")


def coffee_table_drum(e):
    """Round coffee table Ø1.0, h 0.40: thin black top on a wide drum pedestal."""
    k = Kit(e["id"])
    k.cyl("top", (0, 0, 0.38), 0.5, 0.04, seg=72, r=0.008)
    k.cyl("base", (0, 0, 0.18), 0.3, 0.34, seg=64, r=0.01)
    k.cyl("base", (0, 0, 0.012), 0.33, 0.024, seg=64, r=0.006)
    return k.finish(e, {"top": "black_oak_veneer#3a3633", "base": "black_oak_veneer#2c2a28"})


def pouf_round_tufted(e):
    """Round upholstered pouf Ø0.8, h 0.42, with a domed buttoned top and a piped rim."""
    k = Kit(e["id"])
    prof = [(0.0, 0.0), (0.37, 0.0), (0.395, 0.03), (0.40, 0.2), (0.395, 0.34), (0.38, 0.37), (0.30, 0.40), (0.15, 0.415), (0.03, 0.41), (0.0, 0.405)]
    k.lathe("upholstery", (0, 0, 0), prof, seg=48)
    k.torus("upholstery", (0, 0, 0.365), 0.385, 0.012, seg=64, rseg=8)
    k.cyl("button", (0, 0, 0.408), 0.022, 0.012, seg=16, r=0.004)
    for i in range(8):                                  # pleats radiating from the button
        a = i * math.pi / 4
        k.box("upholstery", (0.17 * math.cos(a), 0.17 * math.sin(a), 0.405), (0.3, 0.02, 0.01), r=0.004, seg=2,
              rot=(0, 3.5, math.degrees(a)), soft=True)
    return k.finish(e, {"upholstery": "velvet#9c8a78", "button": "velvet#7d6b5a"})


def tv_flat_75(e):
    """Wall-mounted 75\" TV, 1.68 × 0.97, 45 mm thick; pivot on the wall at the screen centre."""
    k = Kit(e["id"])
    k.box("frame", (0, 0.03, 0), (1.68, 0.035, 0.97), r=0.006, seg=2)
    k.panel("screen", (0, 0.0115, 0.008), 1.655, 0.93)
    k.box("frame", (0, 0.07, 0), (0.6, 0.05, 0.4), r=0.01, seg=2)     # wall bracket / back bulge
    return k.finish(e, {"frame": "black_metal", "screen": "screen"}, pivot="wall")


def media_console_floating(e):
    """Floating TV console 2.4 × 0.42 × 0.36, four push-to-open doors, oak top, LED strip under it."""
    k = Kit(e["id"])
    W, D, H = 2.4, 0.42, 0.36
    k.box("body", (0, 0, 0), (W, D, H - 0.03), r=0.004, seg=2)
    k.box("top", (0, 0, H / 2 - 0.015 + 0.015), (W + 0.02, D + 0.01, 0.03), r=0.004, seg=2)
    for i in range(4):                                  # door gaps
        x = -W / 2 + W / 4 * (i + 0.5)
        k.box("fronts", (x, -D / 2 - 0.004, -0.015), (W / 4 - 0.006, 0.01, H - 0.05), r=0.002, seg=1)
    k.box("led", (0, -0.05, -H / 2 + 0.01), (W - 0.1, 0.02, 0.006))
    return k.finish(e, {"body": "furniture_dark", "fronts": "black_oak_veneer#8a8580", "top": "walnut_smoked", "led": "led"},
                    pivot="wall")


def chandelier_rings(e):
    """Two-ring LED chandelier Ø0.95 / Ø0.65, brass rings glowing underneath, on thin wires from a round canopy."""
    k = Kit(e["id"])
    drop = 0.95
    rings = [(0.475, -drop), (0.325, -drop + 0.22)]
    for R, z in rings:
        k.torus("frame", (0, 0, z), R, 0.018, seg=96, rseg=12)
        k.torus("led", (0, 0, z - 0.012), R, 0.011, seg=96, rseg=8)
        for i in range(3):
            a = 2 * math.pi * i / 3 + (0.5 if R < 0.4 else 0)
            p = (R * math.cos(a), R * math.sin(a))
            k.tube("wire", [(p[0], p[1], z + 0.02), (p[0] * 0.15, p[1] * 0.15, -0.03)], 0.0015, seg=4)
    k.cyl("frame", (0, 0, -0.015), 0.1, 0.03, seg=48, r=0.006)
    return k.finish(e, {"frame": "brass", "led": "led", "wire": "black_metal"}, hanging=True)


def floor_lamp_arc(e):
    """Arc floor lamp: round black base, curved stem 2.0 m high, dome shade 1.5 m out in front (-Y)."""
    k = Kit(e["id"])
    k.cyl("metal", (0, 0.0, 0.02), 0.17, 0.04, seg=48, r=0.01)
    pts = []
    for i in range(33):
        t = i / 32
        a = t * math.pi * 0.62
        pts.append((0, -0.95 * (1 - math.cos(a)) * 1.25, 0.04 + 1.95 * math.sin(a) / math.sin(math.pi * 0.62) * (1 - 0.1 * t)))
    k.tube("metal", pts, 0.011, seg=10)
    tip = pts[-1]
    shade = [(0.012, 0.13), (0.06, 0.125), (0.13, 0.09), (0.17, 0.04), (0.19, 0.0)]
    sy, sz = tip[1] - 0.03, tip[2] - 0.16
    k.tube("metal", [tip, (0, sy, tip[2] - 0.01), (0, sy, sz + 0.13)], 0.009, seg=8)
    k.lathe("metal", (0, sy, sz), shade, seg=40)
    k.lathe("glow", (0, sy, sz), [(0.18, 0.004), (0.12, 0.07), (0.05, 0.1), (0.0, 0.11)], seg=40)
    return k.finish(e, {"metal": "black_metal", "glow": "globe"})


def rug_living_abstract(e):
    k = Kit(e["id"])
    k.slab("rug", (0, 0, 0.006), (3.0, 2.2, 0.012), r=0.004)
    return k.finish(e, {}, own={"rug": {"albedo": tex.rug_abstract(1024, 1400, 51), "rough": 0.95}})


def art_abstract_canvas(e):
    """Gallery-wrapped canvas 1.0 × 1.3 m, 40 mm deep, thin black float frame; pivot on the wall at its centre."""
    k = Kit(e["id"])
    k.box("frame", (0, 0.0, 0), (1.04, 0.045, 1.34), r=0.003, seg=1)
    k.panel("art", (0, -0.0228, 0), 1.0, 1.3)
    return k.finish(e, {"frame": "black_metal"}, own={"art": {"albedo": tex.abstract_painting(1024, 788, 11), "rough": 0.8}},
                    pivot="wall")


def decor_table_set(e):
    """Coffee-table styling: oak tray, two stacked books, a low ceramic bowl and a small dark vase."""
    k = Kit(e["id"])
    k.box("tray", (0, 0, 0.01), (0.46, 0.3, 0.02), r=0.006, seg=2)
    k.box("book_a", (-0.1, 0.02, 0.035), (0.24, 0.18, 0.03), r=0.003, seg=1, rot=(0, 0, 8))
    k.box("book_b", (-0.1, 0.02, 0.063), (0.22, 0.16, 0.026), r=0.003, seg=1, rot=(0, 0, -4))
    k.lathe("ceramic", (0.12, -0.02, 0.02), [(0.0, 0.0), (0.05, 0.0), (0.085, 0.02), (0.1, 0.05), (0.096, 0.052), (0.08, 0.025), (0.0, 0.018)], seg=40)
    k.lathe("vase", (-0.1, 0.02, 0.076), [(0.0, 0.0), (0.04, 0.0), (0.055, 0.06), (0.045, 0.12), (0.018, 0.16), (0.02, 0.18), (0.014, 0.18), (0.0, 0.17)], seg=32)
    return k.finish(e, {"tray": "oak_veneer", "book_a": "linen_rough#d8d0c2", "book_b": "linen_rough#3b3835",
                        "ceramic": "ceramic", "vase": "black_glass"})


ENTRIES = [
    ("sofa_corner_lounge", "Диван угловой глубокий, 3,4 × 2,45 м", "seating", sofa_corner_lounge, {"pivot": "back"}),
    ("coffee_table_drum", "Журнальный стол круглый на тумбе, чёрный", "tables", coffee_table_drum, {}),
    ("pouf_round_tufted", "Пуф круглый с пуговицей", "seating", pouf_round_tufted, {}),
    ("tv_flat_75", "Телевизор 75\" настенный", "utility", tv_flat_75, {"pivot": "wall"}),
    ("media_console_floating", "ТВ-тумба подвесная 2,4 м с подсветкой", "storage", media_console_floating, {"pivot": "wall"}),
    ("chandelier_rings", "Люстра из двух LED-колец", "lighting", chandelier_rings, {"hanging": True}),
    ("floor_lamp_arc", "Торшер-дуга с куполом", "lighting", floor_lamp_arc, {}),
    ("rug_living_abstract", "Ковёр 3 × 2,2 м, серый абстрактный", "textiles", rug_living_abstract, {}),
    ("art_abstract_canvas", "Картина абстракция 1 × 1,3 м", "decor", art_abstract_canvas, {"pivot": "wall"}),
    ("decor_table_set", "Декор на столик: поднос, книги, чаша, ваза", "decor", decor_table_set, {}),
]
