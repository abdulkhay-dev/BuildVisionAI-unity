"""«Наполи» (П7.054): all 11 modules by catalogue (no instructions): catalogue pp. 15-17 (the interior photos on 15 and 16,
the module cut-outs and the «Капучино» swatch on 17).

Construction (the same for every module, read off the photos): carcass ЛДСП 16 standing on a bottom that spans the full
width, a top ЛДСП 22 lying on the sides (flush with them, 2 mm over the fronts), back ХДФ in grooves 6 mm from the back
edge, overlay fronts МДФ 16 with a milled frame (border 24, sunk 2 mm), gaps 3 mm between fronts and 1.5 mm at the outer
ends, bar handles c-c 128 in dark bronze, tapered square legs in the body colour (50 → 36 mm, leaning out 10 mm) on felt
pads. The catalogue depth B is the top's depth: carcass B - 18, fronts, the top 2 mm over the fronts; handles stand out.

    python3 tools/casegoods/gen/napoli.py        # writes Designs/napoli-*.json and gen/napoli_catalog.json
"""
import json
import os

from common import dump

T, TOP, FT, G, E = 16, 22, 16, 3, 1.5          # carcass, top, front thickness; gap between fronts; reveal at the ends
FACE = {"type": "frame", "border": 24, "depth": 2, "r": 1.5}
LEG_D, LEG_D2, SPLAY, PAD = 50, 36, 10, 3


def r5(v):
    return round(v * 2) / 2


def cols(x0, x1, n, e=E, g=G):
    w = (x1 - x0 - 2 * e - (n - 1) * g) / n
    return [(r5(x0 + e + i * (w + g)), r5(x0 + e + i * (w + g) + w)) for i in range(n)]


def rows(y0, y1, n, g=G):
    h = (y1 - y0 - (n - 1) * g) / n
    return [(r5(y0 + i * (h + g)), r5(y0 + i * (h + g) + h)) for i in range(n)]


def carcass(W, D, H, hl, B, backs=None):
    """Bottom over the full width on the legs, sides on it, the top over the sides; backs in grooves (split at xs)."""
    p = [
        {"id": "bottom", "box": [0, hl, 0, W, hl + T, D]},
        {"id": "side-l", "box": [0, hl + T, 0, T, H - TOP, D]},
        {"id": "side-r", "box": [W - T, hl + T, 0, W, H - TOP, D]},
        {"id": "top", "box": [0, H - TOP, 0, W, H, B], "edge": 2},
    ]
    xs = [10] + list(backs or []) + [W - 10]
    for i in range(len(xs) - 1):
        p.append({"id": f"back-{i + 1}" if len(xs) > 2 else "back", "kind": "back",
                  "box": [xs[i], hl + 10, 6, xs[i + 1], H - TOP + 6, 9.5]})
    return p


def partition(pid, xc, D, y0, y1):
    return {"id": pid, "box": [xc - T / 2, y0, 10, xc + T / 2, y1, D]}


def shelf(pid, x0, x1, ytop, D, fixed=False):
    """A loose shelf 1 mm off the sides, 20 mm off the back and behind the hinges; a fixed one over the full depth."""
    if fixed:
        return {"id": pid, "box": [x0, ytop - T, 10, x1, ytop, D]}
    return {"id": pid, "box": [x0 + 1, ytop - T, 20, x1 - 1, ytop, D - 20]}


def glass_shelf(pid, x0, x1, ytop, D):
    return {"id": pid, "kind": "glass", "box": [x0 + 2, ytop - 6, 20, x1 - 2, ytop, D - 30]}


def front(fid, x0, x1, y0, y1, D, glass=None):
    f = {"id": fid, "kind": "front", "box": [x0, y0, D, x1, y1, D + FT]}
    if glass:
        f["glass"] = glass
    else:
        f["face"] = FACE
    return f


def bar(hid, x, y, D, vertical=True):
    """Bar handle «рейлинг» c-c 128 (the engine sets its posts at ±0.4 d)."""
    return {"id": hid, "kind": "handle", "model": "bar", "at": [r5(x), r5(y)], "dir": "up" if vertical else "right",
            "d": 160, "band": 9, "t": 9, "standoff": 22, "z": D + FT}


def drawer(tag, x0, x1, y0, h, zb, zf):
    """Drawer box outer x0..x1: sides, back plate at zb, bottom ХДФ in grooves; open towards zf (the front's back face)."""
    s = 1 if zf > zb else -1
    za, zc = min(zb, zf), max(zb, zf)
    bz = sorted([zb, zb + s * T])
    return [
        {"id": f"{tag}-side-l", "box": [x0, y0, za, x0 + T, y0 + h, zc]},
        {"id": f"{tag}-side-r", "box": [x1 - T, y0, za, x1, y0 + h, zc]},
        {"id": f"{tag}-back", "box": [x0 + T, y0, bz[0], x1 - T, y0 + h, bz[1]]},
        {"id": f"{tag}-bottom", "kind": "back", "box": [x0 + 11, y0 + 10, za + (4 if s > 0 else 2), x1 - 11, y0 + 13.5, zc - (2 if s > 0 else 4)]},
    ]


def leg(tag, x, z, top_y, sx, sz):
    """Tapered square leg (body colour), its foot leaning out by (sx, sz), on a felt pad."""
    bx, bz = x + sx, z + sz
    return [
        {"id": f"leg-{tag}", "kind": "rod", "mat": "body", "section": "square", "from": [x, top_y, z],
         "to": [bx, PAD, bz], "d": LEG_D, "d2": LEG_D2},
        {"id": f"pad-{tag}", "kind": "panel", "mat": "black", "shape": "circle", "box": [bx - 15, 0, bz - 15, bx + 15, PAD, bz + 15]},
    ]


def legs(W, xs, zs, top_y):
    out, k = [], 0
    for x in xs:
        for z in zs:
            k += 1
            sx = -SPLAY if x == min(xs) else (SPLAY if x == max(xs) else 0)   # inner legs lean only back / forth
            sz = -SPLAY if z < max(zs) else SPLAY
            out += leg(str(k), x, z, top_y, sx, sz)
    return out


def door(p, moves, name, fr, hinge, hx, hy, D):
    """A hinged front with its handle at the free edge."""
    p.append(fr)
    h = bar(f"h-{name}", hx, hy, D)
    p.append(h)
    moves.append({"type": "door", "name": name, "parts": [fr["id"], h["id"]], "hinge": hinge, "angle": 100})


def drawer_front(p, moves, name, x0, x1, y0, y1, D, bx0, bx1, by0, bh, zb, travel=350, hx=None):
    fr = front(f"f-{name}", x0, x1, y0, y1, D)
    box = drawer(name, bx0, bx1, by0, bh, zb, D)
    h = bar(f"h-{name}", (x0 + x1) / 2 if hx is None else hx, (y0 + y1) / 2, D, vertical=False)
    p += [fr] + box + [h]
    moves.append({"type": "drawer", "name": name, "parts": [fr["id"]] + [q["id"] for q in box] + [h["id"]], "travel": travel})


# ------------------------------------------------------------------------------------------------ living (B 450)
def tumba_0_20():
    W, B, H, hl = 1464, 450, 689, 162
    D = B - 18
    p = carcass(W, D, H, hl, B)
    p += [partition("part-1", 488, D, hl + T, H - TOP), partition("part-2", 976, D, hl + T, H - TOP)]
    p += [shelf("shelf-l", T, 480, 430, D), shelf("shelf-r", 984, W - T, 430, D)]
    m = []
    (l0, l1), (c0, c1), (r0, r1) = cols(0, W, 3)
    fy0, fy1 = hl, H - TOP - G
    door(p, m, "door_left", front("f-door-l", l0, l1, fy0, fy1, D), "left", l1 - 20, (fy0 + fy1) / 2, D)
    door(p, m, "door_right", front("f-door-r", r0, r1, fy0, fy1, D), "right", r0 + 20, (fy0 + fy1) / 2, D)
    for i, (y0, y1) in enumerate(rows(fy0, fy1, 3)):
        drawer_front(p, m, f"drawer_{i + 1}", c0, c1, y0, y1, D, 496 + 13, 968 - 13, y0 + 20, y1 - y0 - 45, D - 400)
    p += legs(W, [37, W / 2, W - 37], [37, D - 37], hl)
    return dump("napoli-0-20", [W, B, H], p, m)


def tumba_0_21():
    W, B, H, hl = 1950, 450, 1061, 200
    D = B - 18
    p = carcass(W, D, H, hl, B, backs=[975])
    xc = [487.5, 975, 1462.5]
    p += [partition(f"part-{i + 1}", x, D, hl + T, H - TOP) for i, x in enumerate(xc)]
    inner = [(T, xc[0] - 8), (xc[0] + 8, xc[1] - 8), (xc[1] + 8, xc[2] - 8), (xc[2] + 8, W - T)]
    m = []
    fy1 = H - TOP - G                      # 1036
    dy0 = fy1 - 158                        # drawer fronts 158 high
    for i, ((x0, x1), (f0, f1)) in enumerate(zip(inner, cols(0, W, 4))):
        k = i + 1
        p.append(shelf(f"rail-{k}", x0, x1, dy0 - 2, D, fixed=True))       # the fixed shelf under the drawer
        p.append(shelf(f"shelf-{k}", x0, x1, 546, D))
        drawer_front(p, m, f"drawer_{k}", f0, f1, dy0, fy1, D, x0 + 13, x1 - 13, dy0 + 8, 158 - 45, D - 400)
        left = k <= 2
        door(p, m, f"door_{k}", front(f"f-door-{k}", f0, f1, hl, dy0 - G, D), "left" if left else "right",
             f1 - 20 if left else f0 + 20, 530, D)
    p += legs(W, [37, W / 2, W - 37], [37, D - 37], hl)
    return dump("napoli-0-21", [W, B, H], p, m)


def vitrine(did, W):
    """Шкаф 0.10 (2 doors) / 0.11 (1 door): glazed doors over solid ones, a fixed shelf at their joint, glass shelves."""
    B, H, hl = 450, 2055, 170
    D = B - 18
    p = carcass(W, D, H, hl, B)
    split = 662.5                                           # the joint of the lower and the glazed doors
    p.append(shelf("shelf-fixed", T, W - T, split + 8, D, fixed=True))
    p.append(shelf("shelf-low", T, W - T, 430, D))
    for i, y in enumerate([1024, 1361, 1700]):
        p.append(glass_shelf(f"glass-{i + 1}", T, W - T, y, D))
    glass = {"frame": 26, "rebate": 6, "t": 4, "tint": "bronze"}
    m = []
    fy1 = H - TOP - G
    doors = cols(0, W, 2 if W > 600 else 1)
    for i, (x0, x1) in enumerate(doors):
        left = i == 0
        hx = x1 - 20 if left else x0 + 20
        side = "l" if left else "r"
        door(p, m, f"door_up_{side}", front(f"f-up-{side}", x0, x1, split + G / 2, fy1, D, glass=glass),
             "left" if left else "right", hx, 1363, D)
        door(p, m, f"door_low_{side}", front(f"f-low-{side}", x0, x1, hl, split - G / 2, D),
             "left" if left else "right", hx, 413, D)
    p += legs(W, [37, W - 37], [37, D - 37], hl)
    return dump(did, [W, B, H], p, m)


def table_0_50():
    """Стол журнальный: top 702×702 over a box with an open niche through it and a drawer to each side (front, back)."""
    W, B, H, hl = 702, 702, 525, 180
    o = 16                                                  # the top over the carcass and the drawer faces
    zf0, zf1 = o + FT, B - o - FT                           # carcass between the two drawer fronts: 32 … 670
    x0, x1 = o, W - o
    ys = hl + T                                             # sides on the bottom
    p = [
        {"id": "bottom", "box": [x0, hl, zf0, x1, hl + T, zf1]},
        {"id": "side-l", "box": [x0, ys, zf0, x0 + T, H - TOP, zf1]},
        {"id": "side-r", "box": [x1 - T, ys, zf0, x1, H - TOP, zf1]},
        {"id": "top", "box": [0, H - TOP, 0, W, H, B], "edge": 2},
        {"id": "shelf", "box": [x0 + T, 345, zf0, x1 - T, 361, zf1]},              # the niche's floor
        {"id": "divider", "box": [x0 + T, ys, 343, x1 - T, 345, 359]},             # between the two drawers
    ]
    m = []
    fx0, fx1 = x0 + E, x1 - E
    fy0, fy1 = hl, 342
    bx0, bx1 = x0 + T + 13, x1 - T - 13
    # front drawer (+z)
    fr = front("f-drawer-front", fx0, fx1, fy0, fy1, zf1)
    box = drawer("drawer_front", bx0, bx1, 200, 115, 369, zf1)
    h = bar("h-drawer-front", W / 2, (fy0 + fy1) / 2, zf1, vertical=False)
    p += [fr] + box + [h]
    m.append({"type": "drawer", "name": "drawer_front", "parts": [fr["id"]] + [q["id"] for q in box] + [h["id"]], "travel": 250})
    # back drawer (-z): its handle is built of rods (the engine's handles stand out of +z only)
    fr = {"id": "f-drawer-back", "kind": "front", "box": [fx0, fy0, o, fx1, fy1, zf0]}
    box = drawer("drawer_back", bx0, bx1, 200, 115, 333, zf0)
    hy, hz = (fy0 + fy1) / 2, o - 22 - 4.5
    hb = [{"id": "h-drawer-back-bar", "kind": "rod", "mat": "metal", "from": [W / 2 - 80, hy, hz], "to": [W / 2 + 80, hy, hz], "d": 9},
          {"id": "h-drawer-back-p1", "kind": "rod", "mat": "metal", "section": "square", "from": [W / 2 - 64, hy, o], "to": [W / 2 - 64, hy, hz - 4.5], "d": 12},
          {"id": "h-drawer-back-p2", "kind": "rod", "mat": "metal", "section": "square", "from": [W / 2 + 64, hy, o], "to": [W / 2 + 64, hy, hz - 4.5], "d": 12}]
    p += [fr] + box + hb
    m.append({"type": "slide", "name": "drawer_back", "parts": [fr["id"]] + [q["id"] for q in box] + [q["id"] for q in hb], "by": [0, 0, -250]})
    p += legs(W, [x0 + 29, x1 - 29], [zf0 + 29, zf1 - 29], hl)
    return dump("napoli-0-50", [W, B, H], p, m)


# ------------------------------------------------------------------------------------------------ bedroom
def wardrobe(did, W, layout):
    """Шкаф для одежды 4Д / 3Д: 1 + 2 + 1 or 2 + 1 door sections; upper doors over lower ones with a fixed shelf at
    their joint; a hat shelf and a rail in the 2-door section, shelves in the 1-door ones (the catalogue's schemes)."""
    B, H, hl = 640, 2248, 175
    D = B - 18
    n = sum(layout)
    fr_cols = cols(0, W, n)
    joints = [(fr_cols[i][1] + fr_cols[i + 1][0]) / 2 for i in range(n - 1)]
    k, parts_x = 0, []
    for s in layout[:-1]:
        k += s
        parts_x.append(joints[k - 1])
    p = carcass(W, D, H, hl, B, backs=parts_x)
    p += [partition(f"part-{i + 1}", x, D, hl + T, H - TOP) for i, x in enumerate(parts_x)]
    edges = [T] + [v for x in parts_x for v in (x - 8, x + 8)] + [W - T]
    split = 653.5
    for i, s in enumerate(layout):
        x0, x1 = edges[2 * i], edges[2 * i + 1]
        p.append(shelf(f"shelf-fixed-{i + 1}", x0, x1, split + 8, D, fixed=True))
        if s == 2:
            p.append(shelf(f"shelf-hat-{i + 1}", x0, x1, 1970, D))
            p.append({"id": f"rail-{i + 1}", "kind": "tube", "mat": "chrome", "box": [x0 + 4, 1880, D / 2 - 10, x1 - 4, 1900, D / 2 + 10]})
        else:
            for j, y in enumerate([1066, 1460, 1860]):
                p.append(shelf(f"shelf-{i + 1}-{j + 1}", x0, x1, y, D))
    m = []
    fy1 = H - TOP - G
    # hinges: a 2-door section opens as a pair, a 1-door section at the wardrobe's end opens from its outer side
    hinge, d = [], 0
    for s in layout:
        if s == 2:
            hinge += ["left", "right"]
        else:
            hinge += ["left" if d == 0 else "right"]
        d += s
    if layout == [1, 2, 1]:
        hinge = ["left", "left", "right", "right"]         # the handles in the cut-out: 1 | 2 at the joint of 2-3 | 1
    for i, (x0, x1) in enumerate(fr_cols):
        hx = x1 - 20 if hinge[i] == "left" else x0 + 20
        door(p, m, f"door_up_{i + 1}", front(f"f-up-{i + 1}", x0, x1, split + G / 2, fy1, D), hinge[i], hx, 1100, D)
        door(p, m, f"door_low_{i + 1}", front(f"f-low-{i + 1}", x0, x1, hl, split - G / 2, D), hinge[i], hx, 400, D)
    xs = [37] + list(parts_x if layout == [1, 2, 1] else [joints[0]] + parts_x) + [W - 37]
    p += legs(W, xs, [37, D - 37], hl)
    return dump(did, [W, B, H], p, m)


def komod_1_30():
    W, B, H, hl = 1000, 454, 1011, 181
    D = B - 18
    p = carcass(W, D, H, hl, B)
    fy1 = H - TOP - G
    rs = rows(hl, fy1, 4)
    p.append(shelf("rail", T, W - T, rs[3][0] - 3, D, fixed=True))                 # under the top row
    p.append({"id": "divider", "box": [W / 2 - 8, rs[3][0] - 3, 10, W / 2 + 8, H - TOP, D]})
    m = []
    for i, (y0, y1) in enumerate(rs[:3]):
        drawer_front(p, m, f"drawer_{i + 1}", E, W - E, y0, y1, D, T + 13, W - T - 13, y0 + 20, y1 - y0 - 45, D - 400)
    y0, y1 = rs[3]
    (a0, a1), (b0, b1) = cols(0, W, 2)
    drawer_front(p, m, "drawer_4l", a0, a1, y0, y1, D, T + 13, W / 2 - 8 - 13, y0 + 20, y1 - y0 - 45, D - 400)
    drawer_front(p, m, "drawer_4r", b0, b1, y0, y1, D, W / 2 + 8 + 13, W - T - 13, y0 + 20, y1 - y0 - 45, D - 400)
    p += legs(W, [37, W - 37], [37, D - 37], hl)
    return dump("napoli-1-30", [W, B, H], p, m)


def bedside_1_24():
    W, B, H, hl = 480, 454, 527, 179
    D = B - 18
    p = carcass(W, D, H, hl, B)
    m = []
    for i, (y0, y1) in enumerate(rows(hl, H - TOP - G, 2)):
        drawer_front(p, m, f"drawer_{i + 1}", E, W - E, y0, y1, D, T + 13, W - T - 13, y0 + 20, y1 - y0 - 45, D - 400)
    p += legs(W, [37, W - 37], [37, D - 37], hl)
    return dump("napoli-1-24", [W, B, H], p, m)


def mirror_1_41():
    """Зеркало 1000×650 with rounded corners on a hidden backing board (hangs landscape or portrait)."""
    p = [
        {"id": "board", "box": [20, 20, 0, 980, 630, 16], "radius": 100},
        {"id": "mirror", "kind": "mirror", "box": [0, 0, 16, 1000, 650, 20], "radius": 120},
    ]
    return dump("napoli-1-41", [1000, 20, 650], p, [])


def bed_1_00():
    """Кровать 2-16: headboard ЛДСП 22 with an upholstered panel of 8 vertical channels, side and foot rails ЛДСП 16,
    a storage box (ХДФ bottom on cleats) under the lifting metal frame with slats, four tapered legs."""
    W, B, H = 1678, 2040, 1070
    hl, rt = 300, 610                                       # rails 300 … 610
    zh, zf = 22, B - T                                      # headboard face, foot rail's back face
    p = [
        {"id": "headboard", "box": [0, hl, 0, W, H, zh]},
        {"id": "soft", "kind": "soft", "channels": 8, "box": [0, 730, zh, W, H, zh + 60]},
        {"id": "rail-l", "box": [0, hl, zh, T, rt, zf]},
        {"id": "rail-r", "box": [W - T, hl, zh, W, rt, zf]},
        {"id": "rail-foot", "box": [0, hl, zf, W, rt, B]},
        {"id": "cleat-l", "box": [T, hl, zh, T + 20, hl + 30, zf]},
        {"id": "cleat-r", "box": [W - T - 20, hl, zh, W - T, hl + 30, zf]},
        {"id": "box-bottom", "kind": "back", "box": [T, hl + 30, zh, W - T, hl + 33.5, zf]},
        # the lifting frame (m, 2000×1600): steel rails, cross bars, slats
        {"id": "m-frame-l", "mat": "black", "box": [T + 6, 480, zh + 8, T + 46, 510, zf - 8], "covers": ["m"]},
        {"id": "m-frame-r", "mat": "black", "box": [W - T - 46, 480, zh + 8, W - T - 6, 510, zf - 8]},
        {"id": "m-frame-head", "mat": "black", "box": [T + 46, 480, zh + 8, W - T - 46, 510, zh + 48]},
        {"id": "m-frame-foot", "mat": "black", "box": [T + 46, 480, zf - 48, W - T - 46, 510, zf - 8]},
        {"id": "mattress", "kind": "mattress", "box": [39, 518, zh + 1, 1639, 718, zh + 2001]},
    ]
    for i in range(22):
        z = zh + 60 + i * 86
        p.append({"id": f"m-slat-{i + 1}", "mat": "#c9a877", "box": [T + 46, 510, z, W - T - 46, 518, z + 53]})
    for k, (x, z, sx, sz) in enumerate([(37, zh + 37, -SPLAY, -SPLAY), (W - 37, zh + 37, SPLAY, -SPLAY),
                                        (37, B - 37, -SPLAY, SPLAY), (W - 37, B - 37, SPLAY, SPLAY)]):
        p += leg(str(k + 1), x, z, hl, sx, sz)
    return dump("napoli-1-00", [W, B, H], p, [])


# ------------------------------------------------------------------------------------------------ catalogue
FIN = "napoli-kapuchino"
CATALOG = {
    "finishes": [
        {"id": FIN, "name": "Капучино 806 PO", "body": "door_enamel_whitey#cecbc5", "swatch": "#cecbc5",
         "roles": {"fabric": "velvet#8d7b73"}}
    ],
    "profiles": {},
    "collections": [
        {"id": "napoli", "name": "Наполи", "brand": "Пинскдрев", "finishes": [FIN], "metal": "gold#6d6158",
         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 15–17 (все модули по каталогу, без инструкций). Корпус ЛДСП 16 "
                 "на дне во всю ширину, крышка ЛДСП 22, задняя стенка ХДФ в пазах, накладные фасады МДФ 16 с фрезерованной "
                 "рамкой, витрины со стеклом бронза, ручки-рейлинги 128 мм тёмная бронза, конические квадратные опоры в цвет корпуса."}
    ],
    "models": [
        {"id": "napoli-0-10", "code": "П7.054.0.10", "name": "Шкаф 2Д «Наполи»", "collection": "napoli", "category": "living",
         "size": [978, 450, 2055], "page": 17, "note": "по каталогу, без инструкции"},
        {"id": "napoli-0-11", "code": "П7.054.0.11", "name": "Шкаф «Наполи»", "collection": "napoli", "category": "living",
         "size": [492, 450, 2055], "page": 17, "note": "по каталогу, без инструкции; универсальный"},
        {"id": "napoli-0-20", "code": "П7.054.0.20", "name": "Тумба «Наполи»", "collection": "napoli", "category": "living",
         "size": [1464, 450, 689], "page": 17, "note": "по каталогу, без инструкции"},
        {"id": "napoli-0-21", "code": "П7.054.0.21", "name": "Тумба «Наполи»", "collection": "napoli", "category": "living",
         "size": [1950, 450, 1061], "page": 17, "note": "по каталогу, без инструкции"},
        {"id": "napoli-0-50", "code": "П7.054.0.50", "name": "Стол журнальный «Наполи»", "collection": "napoli", "category": "tables",
         "size": [702, 702, 525], "page": 17, "note": "по каталогу, без инструкции; ящики с двух сторон"},
        {"id": "napoli-1-00", "code": "П7.054.1.00", "name": "Кровать 2-16 «Наполи»", "collection": "napoli", "category": "bedroom",
         "size": [1678, 2040, 1070], "page": 17, "note": "по каталогу, без инструкции; спальное место 2000×1600, металлокаркас с подъёмником"},
        {"id": "napoli-1-14", "code": "П7.054.1.14", "name": "Шкаф для одежды 4Д «Наполи»", "collection": "napoli", "category": "bedroom",
         "size": [1946, 640, 2248], "page": 17, "note": "по каталогу, без инструкции"},
        {"id": "napoli-1-16", "code": "П7.054.1.16", "name": "Шкаф для одежды 3Д «Наполи»", "collection": "napoli", "category": "bedroom",
         "size": [1460, 640, 2248], "page": 17, "note": "по каталогу, без инструкции"},
        {"id": "napoli-1-24", "code": "П7.054.1.24", "name": "Тумба прикроватная «Наполи»", "collection": "napoli", "category": "bedroom",
         "size": [480, 454, 527], "page": 17, "note": "по каталогу, без инструкции"},
        {"id": "napoli-1-30", "code": "П7.054.1.30", "name": "Комод «Наполи»", "collection": "napoli", "category": "bedroom",
         "size": [1000, 454, 1011], "page": 17, "note": "по каталогу, без инструкции"},
        {"id": "napoli-1-41", "code": "П7.054.1.41", "name": "Зеркало «Наполи»", "collection": "napoli", "category": "decor", "mount": "wall",
         "size": [1000, 20, 650], "page": 17, "note": "по каталогу, без инструкции; вешается горизонтально или вертикально"},
    ],
}


def write_catalog():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "napoli_catalog.json")
    with open(path, "w") as fh:
        json.dump(CATALOG, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    return path


if __name__ == "__main__":
    print(write_catalog())
    print(vitrine("napoli-0-10", 978))
    print(vitrine("napoli-0-11", 492))
    print(tumba_0_20())
    print(tumba_0_21())
    print(table_0_50())
    print(bed_1_00())
    print(wardrobe("napoli-1-14", 1946, [1, 2, 1]))
    print(wardrobe("napoli-1-16", 1460, [2, 1]))
    print(bedside_1_24())
    print(komod_1_30())
    print(mirror_1_41())
