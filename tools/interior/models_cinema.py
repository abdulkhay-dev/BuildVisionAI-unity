"""Home cinema (reference tile «Кинотеатр»): projection screen with a mountain picture, deep charcoal sectional, dark
padded acoustic panels, up/down wall sconces, low black media console with a centre speaker, black coffee table, dark rug."""
import bmesh
from mathutils import Vector

import tex
from kit import Kit, _link


def _pillow(k, slot, c, s, rot=(0, 0, 0), cuts=6):
    """Lighter version of Kit.pillow (no subsurf, ~0.6k tris) so five cushions fit the sofa's triangle budget."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    sx, sy, sz = s
    for v in bm.verts:
        x, y, z = v.co.x * 2, v.co.y * 2, v.co.z * 2
        edge = max(abs(x), abs(z))
        thick = (1 - edge ** 4) * 0.88 + 0.12
        v.co = Vector((x * sx / 2, y * sy / 2 * thick, z * sz / 2))
    return k._add(_link(bm, "pillow"), slot, c, rot, "m", "soft")


def cinema_screen_wall(e):
    """Fixed-frame projection screen 3.2 × 1.8 m (16:9) with a thin black velvet border, 60 mm deep, showing an alpine
    landscape (slightly emissive). Pivot on the wall at the screen centre."""
    k = Kit(e["id"])
    sw, sh, b = 3.2, 1.8, 0.05
    k.box("frame", (0, 0.03, 0), (sw + 2 * b, 0.06, sh + 2 * b), r=0.008, seg=2)
    k.panel("screen", (0, -0.0005, 0), sw, sh)
    return k.finish(e, {"frame": "charcoal"},
                    own={"screen": {"albedo": tex.mountain_picture(576, 1024, 31), "rough": 0.5, "emit": (0.35, 0.35, 0.35)}},
                    pivot="wall")


def sofa_theater_sectional(e):
    """Deep charcoal L-sectional 3.2 × 2.2 m for the cinema: the long run against the back wall, the return on the LEFT
    coming forward; wide track arms, thick seat cushions, tall loose back cushions, grey scatter pillows, low black feet."""
    k = Kit(e["id"])
    Wd, D, L = 3.2, 1.08, 2.2
    x0, x1, back = -Wd / 2, Wd / 2, D / 2
    front = back - L
    arm, rail = 0.26, 0.24
    up = "upholstery"
    feet = 0.06
    # base frame
    k.box(up, (0, back - D / 2, feet + 0.12), (Wd, D, 0.24), r=0.03, seg=3)
    k.box(up, (x0 + D / 2, (front + back - D) / 2, feet + 0.12), (D, L - D + 0.002, 0.24), r=0.03, seg=3)
    for x, y in ((x0 + 0.08, back - 0.08), (x1 - 0.08, back - 0.08), (x1 - 0.08, back - D + 0.08), (x0 + 0.08, front + 0.08),
                 (x0 + D - 0.08, front + 0.08), (x0 + D - 0.08, back - D + 0.08)):
        k.box("legs", (x, y, feet / 2), (0.05, 0.05, feet), seg=1)
    # back rails (long run, left return) and arms (right end, front of the return)
    bh = 0.5
    k.box(up, ((x0 + x1 - arm) / 2, back - rail / 2, feet + 0.22 + bh / 2), (Wd - arm, rail, bh), r=0.06, seg=3, soft=True)
    k.box(up, (x0 + rail / 2, (front + arm + back - rail) / 2, feet + 0.22 + bh / 2), (rail, L - arm - rail + 0.004, bh),
          r=0.06, seg=3, soft=True)
    ah = 0.4
    k.box(up, (x1 - arm / 2, back - D / 2, feet + 0.2 + ah / 2), (arm, D, ah), r=0.08, seg=3, soft=True)
    k.box(up, (x0 + D / 2, front + arm / 2, feet + 0.2 + ah / 2), (D, arm, ah), r=0.08, seg=3, soft=True)
    # seat cushions
    sz, sh, gap = feet + 0.24 + 0.1, 0.2, 0.014
    ix0, ix1 = x0 + D, x1 - arm
    cw = (ix1 - ix0) / 3
    sy = (back - D + back - rail) / 2
    for i in range(3):
        k.box(up, (ix0 + cw * (i + 0.5), sy, sz), (cw - gap, D - rail - gap, sh), r=0.07, seg=3, bulge=0.02)
    cx = (x0 + rail + x0 + D) / 2
    k.box(up, (cx, sy, sz), (D - rail - gap, D - rail - gap, sh), r=0.07, seg=3, bulge=0.02)
    ly0, ly1 = front + arm, back - D
    k.box(up, (cx, (ly0 + ly1) / 2, sz), (D - rail - gap, ly1 - ly0 - gap, sh), r=0.07, seg=3, bulge=0.02)
    # back cushions
    bz, by = feet + 0.62, back - rail - 0.1
    for i in range(3):
        k.box(up, (ix0 + cw * (i + 0.5), by, bz), (cw - 0.02, 0.22, 0.5), r=0.09, seg=3, rot=(-9, 0, 0), bulge=0.035)
    k.box(up, (cx + 0.05, by, bz), (D - rail - 0.14, 0.22, 0.5), r=0.09, seg=3, rot=(-9, 0, 0), bulge=0.035)
    bx = x0 + rail + 0.1
    k.box(up, (bx, (ly0 + ly1) / 2, bz), (0.22, ly1 - ly0 - 0.02, 0.5), r=0.09, seg=3, rot=(0, -9, 0), bulge=0.035)
    # scatter pillows
    pz, py = feet + 0.66, back - rail - 0.27
    _pillow(k, "pillow_a", (ix0 + 0.35, py, pz), (0.5, 0.16, 0.48), rot=(-14, 0, 8))
    _pillow(k, "pillow_b", (ix0 + 0.95, py, pz - 0.02), (0.46, 0.15, 0.44), rot=(-12, 0, -5))
    _pillow(k, "pillow_a", (ix1 - 0.3, py, pz), (0.5, 0.16, 0.48), rot=(-14, 0, -10))
    _pillow(k, "pillow_b", (cx + 0.1, py - 0.05, pz), (0.48, 0.15, 0.46), rot=(-14, 0, 40))
    _pillow(k, "pillow_a", (bx + 0.16, ly0 + 0.4, pz), (0.48, 0.16, 0.46), rot=(-14, 0, 82))
    return k.finish(e, {up: "velvet#6a6764", "pillow_a": "velvet#8f8c88", "pillow_b": "linen_rough#a29e98",
                        "legs": "black_metal"}, pivot="back")


def acoustic_panel_dark(e):
    """Acoustic wall panel module 0.6 × 2.4: dark fabric-wrapped board with six padded vertical flutes and a thin
    reveal all round. Pivot on the wall at the centre."""
    k = Kit(e["id"])
    pw, ph = 0.6, 2.4
    k.box("backer", (0, 0.009, 0), (pw, 0.018, ph), seg=1)
    n, g = 6, 0.006
    fw = (pw - 0.02) / n
    for i in range(n):
        x = -pw / 2 + 0.01 + fw * (i + 0.5)
        k.box("fabric", (x, -0.012, 0), (fw - g, 0.045, ph - 0.02), r=0.02, seg=3, soft=True)
    return k.finish(e, {"backer": "furniture_dark", "fabric": "wool_felt#4a4744"}, pivot="wall")


def sconce_up_down(e):
    """Black cylinder wall sconce Ø80 × 240 mm on a short arm, light washing up and down (glowing lenses at both ends).
    Pivot on the wall at the centre."""
    k = Kit(e["id"])
    r, h, off = 0.04, 0.24, 0.085
    k.cyl("body", (0, -off, 0), r, h, seg=32, r=0.003, caps=True)
    for sgn in (-1, 1):
        k.cyl("led", (0, -off, sgn * (h / 2 - 0.004)), r - 0.006, 0.004, seg=32)
    k.box("body", (0, -off / 2 + 0.005, 0), (0.024, off - 0.03, 0.03), r=0.004, seg=1)
    k.box("body", (0, -0.005, 0), (0.07, 0.01, 0.12), r=0.004, seg=2)       # wall plate
    return k.finish(e, {"body": "black_metal", "led": "led"}, pivot="wall")


def media_console_low_black(e):
    """Low black media console 2.0 × 0.45 × 0.4 on a recessed plinth: four push-to-open doors with shadow gaps and a
    black top; centre-channel speaker with a fabric grille on top. Pivot at the back."""
    k = Kit(e["id"])
    W, D, H, pl = 2.0, 0.45, 0.4, 0.05
    k.box("body", (0, 0.02, pl / 2), (W - 0.1, D - 0.08, pl), seg=1)
    k.box("body", (0, 0, pl + (H - pl - 0.025) / 2), (W, D - 0.02, H - pl - 0.025), r=0.003, seg=1)
    k.box("top", (0, -0.005, H - 0.0125), (W + 0.01, D, 0.025), r=0.004, seg=2)
    for i in range(4):
        x = -W / 2 + W / 4 * (i + 0.5)
        k.box("fronts", (x, -D / 2 + 0.002, pl + (H - pl - 0.025) / 2), (W / 4 - 0.006, 0.02, H - pl - 0.031), r=0.002, seg=1)
    # centre speaker
    sw, sd, sh = 0.62, 0.24, 0.16
    k.box("speaker", (0, -0.02, H + sh / 2), (sw, sd, sh), r=0.012, seg=2)
    k.box("grille", (0, -0.02 - sd / 2 - 0.001, H + sh / 2), (sw - 0.02, 0.006, sh - 0.02), r=0.004, seg=2)
    for x in (-sw / 2 + 0.06, sw / 2 - 0.06):
        k.box("speaker", (x, -0.02, H + 0.004), (0.04, 0.12, 0.008), seg=1)
    return k.finish(e, {"body": "furniture_dark", "fronts": "black_oak_veneer#4a4643", "top": "black_oak_veneer#2c2a28",
                        "speaker": "furniture_dark", "grille": "charcoal"}, pivot="back")


def coffee_table_rect_black(e):
    """Low black rectangular coffee table 1.2 × 0.6 × 0.38: black oak top, slim black metal frame, lower shelf."""
    k = Kit(e["id"])
    W, D, H = 1.2, 0.6, 0.38
    k.box("top", (0, 0, H - 0.02), (W, D, 0.04), r=0.006, seg=2)
    lw = 0.03
    for sx in (-1, 1):
        for sy in (-1, 1):
            k.box("frame", (sx * (W / 2 - 0.05), sy * (D / 2 - 0.05), (H - 0.04) / 2), (lw, lw, H - 0.04), r=0.002, seg=1)
    for sy in (-1, 1):
        k.box("frame", (0, sy * (D / 2 - 0.05), H - 0.055), (W - 0.1 + lw, lw, 0.03), r=0.002, seg=1)
    for sx in (-1, 1):
        k.box("frame", (sx * (W / 2 - 0.05), 0, H - 0.055), (lw, D - 0.1, 0.03), r=0.002, seg=1)
    k.box("shelf", (0, 0, 0.1), (W - 0.1 - lw, D - 0.1 - lw, 0.018), r=0.003, seg=1)
    return k.finish(e, {"top": "black_oak_veneer#3a3633", "frame": "black_metal", "shelf": "black_oak_veneer#2c2a28"})


def rug_cinema(e):
    """Dark grey low-pile rug 3 × 2 m with a soft marbled pattern."""
    k = Kit(e["id"])
    k.slab("rug", (0, 0, 0.006), (3.0, 2.0, 0.012), r=0.004)
    return k.finish(e, {}, own={"rug": {"albedo": tex.rug_abstract(700, 1024, 57, base="#4c4a48", dark="#383634",
                                                                    light="#6d6a66"), "rough": 0.95}})


ENTRIES = [
    ("cinema_screen_wall", "Проекционный экран 3,2 × 1,8 м с картинкой", "utility", cinema_screen_wall, {"pivot": "wall"}),
    ("sofa_theater_sectional", "Диван угловой для кинотеатра, графит, 3,2 × 2,2 м", "seating", sofa_theater_sectional,
     {"pivot": "back"}),
    ("acoustic_panel_dark", "Акустическая панель тёмная 0,6 × 2,4 м", "walls", acoustic_panel_dark, {"pivot": "wall"}),
    ("sconce_up_down", "Бра-цилиндр чёрное, свет вверх и вниз", "lighting", sconce_up_down, {"pivot": "wall"}),
    ("media_console_low_black", "Медиатумба низкая чёрная 2 м с центральной колонкой", "storage", media_console_low_black,
     {"pivot": "back"}),
    ("coffee_table_rect_black", "Журнальный стол прямоугольный чёрный", "tables", coffee_table_rect_black, {}),
    ("rug_cinema", "Ковёр 3 × 2 м, тёмно-серый", "textiles", rug_cinema, {}),
]
