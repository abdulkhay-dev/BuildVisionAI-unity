"""Bedroom (reference tile «Спальня»): king bed with a tall panelled headboard, floating dark nightstand, drum table lamp,
framed ink painting over the bed, large marbled rug. Also the soft-goods helpers (draped covers, light pillows) that the
kids' room reuses."""
import math

import bmesh
from mathutils import Vector

import tex
from kit import Kit, _link


# ---------------------------------------------------------------------- local helpers
def soft_pillow(k, slot, c, s, rot=(0, 0, 0), cuts=5):
    """Plump cushion like Kit.pillow but lighter (no subdivision surface): s = (width, thickness, height)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    sx, sy, sz = s
    for v in bm.verts:
        x, y, z = v.co.x * 2, v.co.y * 2, v.co.z * 2
        edge = max(abs(x), abs(z))
        thick = (1 - edge ** 4) * 0.88 + 0.12
        corner = 1 - 0.06 * (abs(x) * abs(z)) ** 3          # pinched corners
        v.co = Vector((x * sx / 2 * corner, y * sy / 2 * thick, z * sz / 2 * corner))
    return k._add(_link(bm, "pillow"), slot, c, rot, "m", "soft")


def _wrap(s, a, rc, flare):
    """Cloth laid over a rounded edge: distance s from the centre line → (lateral offset, drop below the top)."""
    sg = 1 if s >= 0 else -1
    s = abs(s)
    if s <= a:
        return sg * s, 0.0
    arc = math.pi / 2 * rc
    if s <= a + arc:
        th = (s - a) / rc
        return sg * (a + rc * math.sin(th)), rc * (1 - math.cos(th))
    h = s - a - arc
    return sg * (a + rc + h * flare), rc + h


def _params(a, rc, hang_lo, hang_hi, step=0.12):
    """Cloth parameters across one axis: coarse on the flat top, dense round the edges, a few rows down the hang."""
    n = max(2, int(round(2 * a / step)))
    us = [-a + 2 * a * i / n for i in range(n + 1)]
    arc = math.pi / 2 * rc
    for sg, hang in ((-1, hang_lo), (1, hang_hi)):
        if hang <= 0:
            continue
        us += [sg * (a + arc * i / 5) for i in range(1, 6)]
        m = max(2, int(math.ceil(hang / 0.08)))
        us += [sg * (a + arc + hang * j / m) for j in range(1, m + 1)]
    return sorted(us)


def cover(k, slot, top, x0, x1, y0, y1, t=0.03, rc=0.05, hang_x=0.0, hang_front=0.0, hang_back=0.0, flare=0.06,
          wave=0.006, seed=0):
    """Draped cloth (duvet, blanket, throw): a sheet lying flat at height `top` over the rectangle x0..x1 × y0..y1 (y0 =
    front), rolling over rounded edges (radius rc) and hanging hang_* metres down the sides / front / back, thickness t.
    A little waviness and vertical folds on the hanging parts keep it from looking like a box."""
    ax, ay = (x1 - x0) / 2, (y1 - y0) / 2
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    us = _params(ax, rc, hang_x, hang_x)
    vs = _params(ay, rc, hang_front, hang_back)
    ph = seed * 1.7
    verts = []
    for v in vs:
        wy, dy = _wrap(v, ay, rc, flare) if (v < 0 and hang_front > 0) or (v > 0 and hang_back > 0) else (v, 0.0)
        for u in us:
            wx, dx = _wrap(u, ax, rc, flare) if hang_x > 0 else (u, 0.0)
            d = max(dx, dy)
            x, y = cx + wx, cy + wy
            z = top - d + wave * math.sin(x * 7.3 + ph) * math.sin(y * 5.1 + ph * 0.7)
            fold = max(0.0, d - rc) * 0.12
            if dx > rc:
                x += math.copysign(fold * math.sin(y * 6.5 + ph), wx)
            if dy > rc:
                y += math.copysign(fold * math.sin(x * 5.5 + ph), wy)
            verts.append((x, y, z))
    nu = len(us)
    faces = [(j * nu + i, j * nu + i + 1, (j + 1) * nu + i + 1, (j + 1) * nu + i)
             for j in range(len(vs) - 1) for i in range(nu - 1)]
    obj = k.mesh(slot, verts, faces, smooth="soft")
    m = obj.modifiers.new("solid", "SOLIDIFY")
    m.thickness = t
    m.offset = 0.0
    m.use_even_offset = True
    return obj


def padded(k, slot, c, w, h, t, bulge=0.012, r=0.02):
    """Front-facing upholstered panel w × h, t deep, domed towards -Y (headboard panels)."""
    return k.box(slot, c, (w, h, t), r=r, seg=3, rot=(90, 0, 0), bulge=bulge)


# ---------------------------------------------------------------------- models
def bed_king_panel(e):
    """King bed, mattress 1.8 × 2.0: low upholstered taupe base on a recessed plinth, tall 2.3 m headboard of 3 × 3 padded
    horizontal panels, light sheet, grey duvet folded back, charcoal throw across the foot, 2 sleeping + 3 scatter
    pillows. Pivot at the back (headboard against the wall)."""
    k = Kit(e["id"])
    up = "upholstery"
    hb_back, hb_front = 1.14, 1.01            # headboard back / front face
    my0, my1 = -1.03, 0.97                    # mattress front / back
    by0 = -1.10                               # base front
    # headboard: backing board + 3 × 3 padded panels
    HW = 2.3
    k.box(up, (0, hb_back - 0.03, 0.66), (HW, 0.06, 1.2), r=0.02, seg=3, soft=True)
    rows, cols = 3, 3
    z0, z1, gap = 0.38, 1.24, 0.012
    rh, cw = (z1 - z0) / rows, (HW - 0.02) / cols
    for r in range(rows):
        for c in range(cols):
            padded(k, up, (-HW / 2 + 0.01 + cw * (c + 0.5), (hb_front + hb_back - 0.06) / 2, z0 + rh * (r + 0.5)),
                   cw - gap, rh - gap, 0.07, bulge=0.014)
    # base and plinth
    k.box(up, (0, (by0 + hb_front) / 2, 0.2), (1.96, hb_front - by0, 0.28), r=0.05, seg=3, soft=True)
    k.box("plinth", (0, (by0 + hb_front) / 2 + 0.02, 0.035), (1.76, hb_front - by0 - 0.2, 0.07), r=0.004, seg=1)
    # mattress with the fitted sheet
    k.box("sheet", (0, (my0 + my1) / 2, 0.41), (1.8, 2.0, 0.22), r=0.06, seg=3, soft=True)
    # duvet (grey), folded back at the head; throw across the foot
    top = 0.52 + 0.025
    cover(k, "duvet", top, -0.95, 0.95, -1.07, 0.32, t=0.05, rc=0.06, hang_x=0.13, hang_front=0.14, wave=0.008, seed=1)
    k.box("duvet", (0, 0.2, top + 0.045), (2.0, 0.3, 0.05), r=0.024, seg=3, bulge=0.012)
    cover(k, "throw", top + 0.035, -0.99, 0.99, -0.92, -0.3, t=0.016, rc=0.07, hang_x=0.2, flare=0.1, wave=0.01, seed=2)
    # pillows
    for sx in (-1, 1):
        soft_pillow(k, "pillows", (sx * 0.46, 0.83, 0.75), (0.76, 0.2, 0.5), rot=(-22, 0, sx * 3))
        soft_pillow(k, "pillow_a", (sx * 0.44, 0.66, 0.74), (0.52, 0.16, 0.46), rot=(-17, 0, -sx * 6))
    soft_pillow(k, "pillow_b", (0, 0.55, 0.68), (0.56, 0.14, 0.3), rot=(-12, 0, 0))
    return k.finish(e, {up: "linen_rough#b0a292", "plinth": "furniture_dark", "sheet": "cotton_poplin#f4f1eb",
                        "duvet": "cotton_poplin#c9c6c1", "throw": "wool_felt#4a4846", "pillows": "cotton_poplin#f2eee8",
                        "pillow_a": "velvet#6c6966", "pillow_b": "linen_rough#bdb0a0"}, pivot="back")


def nightstand_float_dark(e):
    """Dark walnut nightstand 0.55 × 0.40 × 0.50 on a recessed black plinth (floating look): one drawer with a slim black
    pull over an open niche."""
    k = Kit(e["id"])
    W, D, H, z0, th = 0.55, 0.40, 0.50, 0.07, 0.018
    k.box("plinth", (0, 0.03, z0 / 2), (W - 0.1, D - 0.1, z0), r=0.003, seg=1)
    # upper drawer section (solid) and top
    k.box("body", (0, 0, 0.385), (W, D, 0.19), r=0.003, seg=2)
    k.box("body", (0, 0, H - 0.0125), (W, D, 0.025), r=0.004, seg=2)
    # niche below: sides, bottom, back
    for sx in (-1, 1):
        k.box("body", (sx * (W / 2 - th / 2), 0, (z0 + 0.29) / 2), (th, D, 0.29 - z0), r=0.002, seg=1)
    k.box("body", (0, 0, z0 + th / 2), (W, D, th), r=0.002, seg=1)
    k.box("body", (0, D / 2 - 0.006, (z0 + 0.29) / 2), (W - 0.02, 0.012, 0.29 - z0), seg=1)
    # drawer front with shadow gaps, slim pull
    k.box("fronts", (0, -D / 2 - 0.006, 0.39), (W - 0.008, 0.012, 0.19 - 0.012), r=0.002, seg=1)
    k.box("handle", (0, -D / 2 - 0.017, 0.44), (0.2, 0.01, 0.012), r=0.003, seg=2)
    for sx in (-1, 1):
        k.box("handle", (sx * 0.09, -D / 2 - 0.013, 0.44), (0.01, 0.014, 0.01), seg=1)
    return k.finish(e, {"plinth": "furniture_dark", "body": "walnut_veneer#94806e", "fronts": "walnut_veneer#94806e",
                        "handle": "black_metal"}, pivot="back")


def _ring_tube(k, slot, c, ro, ri, h, seg=48):
    """Thin-walled open cylinder (lamp shade): outer and inner walls with rims, open at both ends."""
    verts = []
    for (r, z) in ((ro, -h / 2), (ro, h / 2), (ri, h / 2), (ri, -h / 2)):
        verts += [(r * math.cos(2 * math.pi * i / seg), r * math.sin(2 * math.pi * i / seg), z) for i in range(seg)]
    faces = []
    for ring in range(4):
        a, b = ring * seg, ((ring + 1) % 4) * seg
        faces += [(a + i, a + (i + 1) % seg, b + (i + 1) % seg, b + i) for i in range(seg)]
    return k.mesh(slot, verts, faces, c=c)


def table_lamp_drum(e):
    """Table lamp h 0.57: matte stoneware gourd base, brass neck, white drum shade Ø0.38 (glows)."""
    k = Kit(e["id"])
    k.lathe("base", (0, 0, 0), [(0.0, 0.0), (0.07, 0.0), (0.085, 0.012), (0.105, 0.07), (0.112, 0.12), (0.104, 0.18),
                                (0.075, 0.24), (0.04, 0.275), (0.026, 0.29), (0.026, 0.305), (0.0, 0.305)], seg=48)
    k.cyl("metal", (0, 0, 0.345), 0.009, 0.08, seg=16)
    k.cyl("metal", (0, 0, 0.388), 0.018, 0.012, seg=24, r=0.003)
    k.lathe("bulb", (0, 0, 0.39), [(0.0, 0.0), (0.02, 0.005), (0.03, 0.03), (0.026, 0.055), (0.0, 0.065)], seg=20)
    _ring_tube(k, "shade", (0, 0, 0.45), 0.19, 0.186, 0.24, seg=64)
    for i in range(3):                                   # spider arms
        a = 2 * math.pi * i / 3
        k.tube("metal", [(0.016 * math.cos(a), 0.016 * math.sin(a), 0.43), (0.185 * math.cos(a), 0.185 * math.sin(a), 0.565)],
               0.0025, seg=4)
    return k.finish(e, {"base": "stoneware", "metal": "brass", "bulb": "globe", "shade": "lamp_shade"})


def art_ink_framed(e):
    """Framed ink painting 1.1 × 0.85 m for over the bed: thin black frame, white mat, 0.8 × 0.6 ink wash; pivot wall."""
    k = Kit(e["id"])
    W, H, b, d = 1.1, 0.85, 0.018, 0.03
    k.box("frame", (0, 0, H / 2 - b / 2), (W, d, b), r=0.002, seg=1)
    k.box("frame", (0, 0, -H / 2 + b / 2), (W, d, b), r=0.002, seg=1)
    for sx in (-1, 1):
        k.box("frame", (sx * (W / 2 - b / 2), 0, 0), (b, d, H - 2 * b), r=0.002, seg=1)
    k.box("frame", (0, d / 2 - 0.004, 0), (W - 0.01, 0.008, H - 0.01), seg=1)          # backing board
    k.panel("mat", (0, -0.004, 0), W - 2 * b, H - 2 * b, uv="m")
    k.panel("art", (0, -0.0055, 0), 0.8, 0.6)
    return k.finish(e, {"frame": "black_metal", "mat": "soft_white"},
                    own={"art": {"albedo": tex.ink_painting(768, 1024, 23), "rough": 0.85}}, pivot="wall")


def rug_bedroom(e):
    """Large low-pile rug 3.0 × 2.0 m, cream with grey-blue marbling."""
    k = Kit(e["id"])
    k.slab("rug", (0, 0, 0.006), (3.0, 2.0, 0.012), r=0.004)
    img = tex.rug_abstract(683, 1024, 57, base="#d9d4cb", dark="#5d636b", light="#f0ece5")
    return k.finish(e, {}, own={"rug": {"albedo": img, "rough": 0.95}})


ENTRIES = [
    ("bed_king_panel", "Кровать 180 × 200 с высоким мягким изголовьем", "bedroom", bed_king_panel, {"pivot": "back"}),
    ("nightstand_float_dark", "Тумба прикроватная, тёмный орех, с ящиком", "bedroom", nightstand_float_dark, {"pivot": "back"}),
    ("table_lamp_drum", "Настольная лампа с абажуром-барабаном", "lighting", table_lamp_drum, {}),
    ("art_ink_framed", "Картина тушью в раме с паспарту 1,1 × 0,85 м", "decor", art_ink_framed, {"pivot": "wall"}),
    ("rug_bedroom", "Ковёр 3 × 2 м, кремово-серый мраморный", "textiles", rug_bedroom, {}),
]
