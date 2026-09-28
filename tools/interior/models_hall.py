"""Hall (reference tile «Прихожая»): floating walnut console, round backlit mirror, upholstered entry bench, coat hooks with
hanging coats, runner rug and doormat, slim shoe cabinet, tall flush-door wardrobe."""
import math

import tex
from kit import Kit


# ---------------------------------------------------------------------- local helpers
def loft(k, slot, rings):
    """Closed soft body through rings of equal point count (top to bottom), capped at both ends (coats, sleeves)."""
    n = len(rings[0])
    verts = [p for r in rings for p in r]
    faces = []
    for j in range(len(rings) - 1):
        for i in range(n):
            a, b = j * n + i, j * n + (i + 1) % n
            faces.append((a, b, b + n, a + n))
    faces.append(tuple(range(n))[::-1])
    faces.append(tuple(range((len(rings) - 1) * n, len(rings) * n)))
    return k.mesh(slot, verts, faces, smooth="soft")


def _sm(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def coat(k, slot, x0, ztop, L, seed, ytop=-0.075, width=1.0):
    """Coat hung by its loop on a hook: pinched collar, shoulders, body widening and draping towards the wall, soft
    folds on the front, two sleeves hanging along the sides."""
    n, m = 28, 16
    rings = []
    for j in range(m + 1):
        s = j / m
        z = ztop - s * L
        a = (0.045 + 0.155 * _sm(s / 0.14) + 0.04 * max(0.0, s - 0.14)) * width
        b = 0.028 + 0.075 * _sm(s / 0.18)
        yb = ytop + 0.06 * _sm(s / 0.45)            # back line moves from the hook towards the wall
        ring = []
        for i in range(n):
            t = 2 * math.pi * i / n
            ct, st = math.cos(t), math.sin(t)
            fold = 1 + 0.06 * _sm(s / 0.5) * math.sin(6 * t + seed + 3 * s) if st < 0 else 1.0
            bb = b * (0.55 if st > 0 else 1.0)
            ring.append((x0 + a * ct * fold, yb - 0.55 * b + bb * st * fold, z))
        rings.append(ring)
    loft(k, slot, rings)
    # sleeves
    for side in (-1, 1):
        rs = []
        for j in range(9):
            zz = ztop - 0.13 * L - j / 8 * min(0.6, 0.75 * L)
            s = (ztop - zz) / L
            a = (0.045 + 0.155 * _sm(s / 0.14) + 0.04 * max(0.0, s - 0.14)) * width
            yb = ytop + 0.06 * _sm(s / 0.45)
            cx = x0 + side * (a - 0.035 + 0.012 * j / 8)
            r = 0.045 + 0.012 * j / 8
            rs.append([(cx + r * math.cos(2 * math.pi * i / 12), yb - 0.07 + r * 0.9 * math.sin(2 * math.pi * i / 12), zz)
                       for i in range(12)])
        loft(k, slot, rs)


# ---------------------------------------------------------------------- models
def console_hall_floating(e):
    """Floating walnut console 1.2 × 0.4 × 0.3: two drawers with 4 mm shadow gaps and a black grip channel under the top;
    pivot on the wall at its centre."""
    k = Kit(e["id"])
    W, D, H = 1.2, 0.4, 0.3
    k.box("carcass", (0, 0.01, H / 2), (W, D - 0.02, H - 0.001), r=0.003, seg=2)
    k.box("top", (0, 0, H - 0.0125), (W, D, 0.025), r=0.003, seg=2)
    fh = H - 0.025 - 0.028
    fw = (W - 0.012) / 2
    for s in (-1, 1):
        k.box("fronts", (s * (fw / 2 + 0.002), -D / 2 + 0.0095, 0.004 + fh / 2), (fw, 0.019, fh), r=0.0015, seg=1)
    k.box("handle", (0, -D / 2 + 0.012, H - 0.025 - 0.012), (W - 0.01, 0.02, 0.022))
    return k.finish(e, {"carcass": "walnut_veneer", "top": "walnut_smoked#b08a6a", "fronts": "walnut_veneer",
                        "handle": "furniture_dark"}, pivot="wall")


def mirror_round_backlit(e):
    """Round mirror Ø0.8 with a thin black rim, on a 30 mm spacer with a warm LED ring glowing onto the wall behind."""
    k = Kit(e["id"])
    R = 0.4
    k.cyl("back", (0, 0.022, 0), R - 0.05, 0.03, seg=64, rot=(90, 0, 0))
    k.torus("led", (0, 0.03, 0), R - 0.045, 0.006, seg=64, rseg=6, rot=(90, 0, 0))
    k.cyl("back", (0, 0.004, 0), R - 0.002, 0.004, seg=96, rot=(90, 0, 0))
    k.disc("mirror", (0, 0.0015, 0), R - 0.004, seg=96, rot=(90, 0, 0), uv="m")
    k.torus("frame", (0, 0.004, 0), R, 0.006, seg=96, rseg=8, rot=(90, 0, 0))
    return k.finish(e, {"back": "furniture_dark", "led": "led", "mirror": "mirror", "frame": "black_metal"}, pivot="wall")


def bench_entry_upholstered(e):
    """Entry bench 1.2 × 0.4 × 0.46: dark walnut side panels and shoe shelf, brown upholstered seat cushion with a
    piped edge."""
    k = Kit(e["id"])
    W, D, H = 1.2, 0.4, 0.46
    wood = "base"
    for s in (-1, 1):
        k.box(wood, (s * (W / 2 - 0.02), 0, 0.19), (0.04, D, 0.38), r=0.003, seg=2)
    k.box(wood, (0, 0, 0.365), (W - 0.078, D, 0.03), r=0.002, seg=1)
    k.box(wood, (0, 0.01, 0.1), (W - 0.078, D - 0.04, 0.025), r=0.002, seg=1)
    k.box("upholstery", (0, 0, 0.41), (W - 0.01, D - 0.01, 0.07), r=0.025, seg=4, bulge=0.012)
    return k.finish(e, {wood: "walnut_veneer#7a6a5e", "upholstery": "suede#a07c5c"}, pivot="back")


def coat_hooks_wall(e):
    """Walnut wall rail 1.0 m with five black J-hooks, a long charcoal coat and a shorter camel coat hanging on it;
    pivot on the wall (centre of the bounding box)."""
    k = Kit(e["id"])
    k.box("rail", (0, -0.0125, 0), (1.0, 0.025, 0.09), r=0.003, seg=2)
    hooks = [-0.4, -0.2, 0.0, 0.2, 0.4]
    for x in hooks:
        k.cyl("hooks", (x, -0.027, 0.0), 0.012, 0.005, seg=16, rot=(90, 0, 0))
        k.tube("hooks", [(x, -0.027, 0.0), (x, -0.06, -0.012), (x, -0.08, -0.008), (x, -0.088, 0.008), (x, -0.086, 0.025)],
               0.005, seg=8)
        k.cyl("hooks", (x, -0.086, 0.028), 0.0065, 0.008, seg=12)
    coat(k, "coat_a", -0.2, 0.0, 1.05, 1.3)
    coat(k, "coat_b", 0.2, 0.0, 0.78, 4.1, width=0.95)
    return k.finish(e, {"rail": "walnut_veneer", "hooks": "black_metal", "coat_a": "wool_felt#3a3a3c",
                        "coat_b": "wool_felt#a4855f"}, pivot="wall")


def rug_runner(e):
    k = Kit(e["id"])
    k.slab("rug", (0, 0, 0.006), (2.4, 0.8, 0.012), r=0.004)
    return k.finish(e, {}, own={"rug": {"albedo": tex.rug_stripe(512, 1400, 73, base="#b8afa3", line="#80786e"),
                                        "rough": 0.95}})


def doormat_entry(e):
    """Dark loop-pile doormat 0.9 × 0.55 on a rubber border."""
    k = Kit(e["id"])
    k.box("border", (0, 0, 0.004), (0.9, 0.55, 0.008), r=0.003, seg=2)
    k.box("mat", (0, 0, 0.007), (0.84, 0.49, 0.01), r=0.003, seg=1)
    return k.finish(e, {"border": "furniture_dark", "mat": "carpet_loop#4a4643"})


def shoe_cabinet_slim(e):
    """Slim shoe cabinet 0.8 × 0.25 × 1.05: two tilt-out walnut flaps with finger grips, dark top, recessed plinth."""
    k = Kit(e["id"])
    W, D, H = 0.8, 0.25, 1.05
    k.box("carcass", (0, 0.01, (H + 0.06) / 2), (W, D - 0.02, H - 0.06 - 0.02), r=0.002, seg=1)
    k.box("plinth", (0, 0.02, 0.03), (W - 0.04, D - 0.06, 0.06))
    k.box("top", (0, 0, H - 0.01), (W + 0.01, D + 0.005, 0.02), r=0.003, seg=2)
    fh = (H - 0.02 - 0.064 - 0.004) / 2
    for i in range(2):
        z = 0.064 + fh / 2 + i * (fh + 0.004)
        k.box("fronts", (0, -D / 2 + 0.0095, z), (W - 0.004, 0.019, fh - 0.002), r=0.0015, seg=1)
        k.box("handle", (0, -D / 2 - 0.001, z + fh / 2 - 0.015), (0.16, 0.006, 0.012))
    return k.finish(e, {"carcass": "walnut_veneer", "plinth": "furniture_dark", "top": "black_oak_veneer#6f6a65",
                        "fronts": "walnut_veneer", "handle": "black_metal"}, pivot="back")


def wardrobe_hall_flush(e):
    """Tall hall wardrobe module 1.0 × 0.6 × 2.5: two full-height flush walnut doors with vertical grain and slim black
    bar pulls, recessed dark plinth; modules line up side by side. Pivot at the back."""
    k = Kit(e["id"])
    W, D, H = 1.0, 0.6, 2.5
    k.box("carcass", (0, 0.0095, (H + 0.08) / 2), (W, D - 0.019, H - 0.08), r=0.002, seg=1)
    k.box("plinth", (0, 0.03, 0.04), (W - 0.02, D - 0.08, 0.08))
    dw, dh = (W - 0.004 * 3) / 2, H - 0.08 - 0.006
    for s in (-1, 1):
        k.box("fronts", (s * (dw / 2 + 0.002), -D / 2 + 0.0095, 0.083 + dh / 2), (dw, 0.019, dh), r=0.0015, seg=1)
        hx = s * 0.045
        k.box("handle", (hx, -D / 2 - 0.028, 1.05), (0.012, 0.012, 0.6), r=0.003, seg=1)
        for dz in (-0.27, 0.27):
            k.box("handle", (hx, -D / 2 - 0.013, 1.05 + dz), (0.01, 0.02, 0.01))
    return k.finish(e, {"carcass": "walnut_veneer", "plinth": "furniture_dark", "fronts": "walnut_veneer",
                        "handle": "black_metal"}, pivot="back")


ENTRIES = [
    ("console_hall_floating", "Консоль подвесная орех, 2 ящика, 1,2 м", "storage", console_hall_floating, {"pivot": "wall"}),
    ("mirror_round_backlit", "Зеркало круглое Ø80 с подсветкой", "decor", mirror_round_backlit, {"pivot": "wall"}),
    ("bench_entry_upholstered", "Банкетка в прихожую с мягким сиденьем, 1,2 м", "seating", bench_entry_upholstered,
     {"pivot": "back"}),
    ("coat_hooks_wall", "Вешалка настенная с крючками и пальто", "storage", coat_hooks_wall, {"pivot": "wall"}),
    ("rug_runner", "Ковёр-дорожка 2,4 × 0,8 м", "textiles", rug_runner, {}),
    ("doormat_entry", "Коврик придверный тёмный", "textiles", doormat_entry, {}),
    ("shoe_cabinet_slim", "Обувница узкая с откидными дверцами", "storage", shoe_cabinet_slim, {"pivot": "back"}),
    ("wardrobe_hall_flush", "Шкаф в прихожую высокий, орех, 1 × 2,5 м", "storage", wardrobe_hall_flush, {"pivot": "back"}),
]
