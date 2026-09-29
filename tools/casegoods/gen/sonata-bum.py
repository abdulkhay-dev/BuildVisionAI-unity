"""«Соната Бум» (П3.0439; kids' room, «Сосна Карелия»): 23 modules, all by catalogue (no instruction, no product page
on pinskdrev.by; the beds 2-14 / 2-16 «Соната» have only a photo) — pages 125–128 (the room photos 246–251 and the
module cut-outs with sizes 252–253).

Construction (the collection's photos, the «Бум» line's instructed modules — Челси Бум — as the model): ЛДСП 16
«Сосна Карелия», the sides to the floor, the bottom on a 60 plinth rail recessed 20 behind the fronts, the top between
the sides, ХДФ 3 back in grooves; OVERLAY fronts ЛДСП 16 (2 mm reveals, 3–4 mm gaps); a wave-shaped crown board 90
on the tall pieces (the catalogue height includes it: body 2250 + 90); small satin-chrome knobs; drawers ЛДСП 16 with
ХДФ bottoms, 13 mm runner gaps; the beds: headboard with the crown outline, a lower footboard with rounded corners,
side rails, two drawers with arched grips under the long side; the «с полками» beds carry the round-fronted bedside
shelf units (356) at the head. Sizes: the catalogue's overall sizes exactly; the inner divisions are read off the
cut-outs and photos (±20 mm).

    python3 tools/casegoods/gen/sonata-bum.py
"""
import math

from kit_w4k import (P, H, back, front, drawer_box, dmove, door, ids, write_fragment, rounded_rect_path, notch_top,
                     coupe, coupe_doors, dump, r1, box)

SLUG = "sonata-bum"
T = 16.0
PL = 60.0            # plinth
HB = 2250.0          # body of the tall pieces (+ crown 90 = 2340)


def knob(pid, x, y, z, letter="k"):
    return {"id": pid, "kind": "handle", "model": "knob", "mat": "metal", "at": [r1(x), r1(y)], "d": 30, "t": 12,
            "standoff": 24, "z": r1(z), "covers": [letter]}


def crown_path(x0, x1, y0, h, e=30):
    W = x1 - x0
    X = lambda f: r1(x0 + f * W)
    y = lambda v: r1(y0 + v)
    return (f"M {X(0)} {y(0)} L {X(1)} {y(0)} L {X(1)} {y(e)} Q {X(0.8)} {y(e + 10)} {X(0.64)} {y(e + 10)} "
            f"C {X(0.57)} {y(e + 10)} {X(0.57)} {y(h)} {X(0.5)} {y(h)} C {X(0.43)} {y(h)} {X(0.43)} {y(e + 10)} "
            f"{X(0.36)} {y(e + 10)} Q {X(0.2)} {y(e + 10)} {X(0)} {y(e)} Z")


def carcass(W, Bc, Hb, crown=0.0, back_on=True, plinth=PL, bottom=True):
    p = [P(None, (0, 0, 0, T, Hb, Bc), "side-l"), P(None, (W - T, 0, 0, W, Hb, Bc), "side-r"),
         P(None, (T, Hb - T, 0, W - T, Hb, Bc), "top")]
    if bottom:
        p += [P(None, (T, plinth, 0, W - T, plinth + T, Bc), "bottom"),
              P(None, (T, 0, Bc - 36, W - T, plinth, Bc - 20), "plinth")]
    if back_on:
        p.append(back(None, (T - 6, plinth + T - 6, 8, W - T + 6, Hb - T + 6, 11), "back", mat="white"))
    if crown:
        p.append(P(None, (0, Hb, Bc - 32, W, Hb + crown, Bc - 16), "crown", shape="path",
                   outline=crown_path(0, W, Hb, crown)))
    return p


def shelves(tag, x0, x1, y0, y1, n, z0=12, z1=None, Bc=350, gap=0.5):
    z1 = z1 if z1 is not None else Bc - 2
    out = []
    step = (y1 - y0 - n * T) / (n + 1)
    for k in range(n):
        y = y0 + (k + 1) * step + k * T
        out.append(P(None, (x0 + gap, y, z0, x1 - gap, y + T, z1), f"{tag}-{k + 1}"))
    return out


def a_door(tag, x0, x1, y0, y1, Bc, hinge, ky):
    f = front(None, (x0, y0, Bc, x1, y1, Bc + T), tag)
    kx = x1 - 40 if hinge == "left" else x0 + 40
    k = knob(f"k-{tag}", kx, ky, Bc + T)
    return [f, k], door(tag, [f["id"], k["id"]], hinge)


def a_drawer(tag, x0, x1, y0, y1, Bc, ix0, ix1, depth=None, h=None):
    depth = depth or min(450.0, (Bc - 30) // 50 * 50)
    f = front(None, (x0, y0, Bc, x1, y1, Bc + T), tag)
    h = h or min(160.0, y1 - y0 - 50)
    bx = drawer_box(tag, (f"{tag}-sl", f"{tag}-sr", f"{tag}-b", f"{tag}-bot"), ix0 + 13, ix1 - 13, y0 + 22, h,
                    Bc - depth, Bc, bottom=(ix1 - ix0 - 26 - 21, depth + 5, 3))
    for q in bx:
        q.pop("n", None)
    k = knob(f"k-{tag}", (x0 + x1) / 2, y1 - 45, Bc + T)
    parts = [f] + bx + [k]
    return parts, dmove(tag, ids(parts), depth - 50)


# ------------------------------------------------------------------------------------------ 1.12 шкаф 2д
def m112():
    W, B = 954, 366
    Bc = B - T
    p = carcass(W, Bc, HB, 90)
    p += [P(None, (469, PL + T, 12, 485, HB - T, Bc), "part"),
          P(None, (T, 700, 12, 469, 716, Bc), "fix-l"), P(None, (485, 700, 12, W - T, 716, Bc), "fix-r")]
    p += shelves("sh-l", T, 469, 716, HB - T, 4, Bc=Bc) + shelves("sh-r", 485, W - T, 716, HB - T, 4, Bc=Bc)
    p += shelves("low-l", T, 469, PL + T, 700, 1, Bc=Bc) + shelves("low-r", 485, W - T, PL + T, 700, 1, Bc=Bc)
    moves = []
    for tag, x0, x1, hinge in (("door-l", 2, 475, "left"), ("door-r", 479, 952, "right")):
        ps, mv = a_door(tag, x0, x1, PL + 2, 698, Bc, hinge, 640)
        p += ps
        moves.append(mv)
    return dump("sonata-bum-1-12", [954, 366, 2340], p, moves)


# ------------------------------------------------------------------------------------------ 1.15 шкаф
def m115():
    W, B = 478, 366
    Bc = B - T
    p = carcass(W, Bc, HB, 90)
    p += [P(None, (T, 506, 12, W - T, 522, Bc), "fix-1"), P(None, (T, 735, 12, W - T, 751, Bc - 2), "niche-shelf"),
          P(None, (T, 965, 12, W - T, 981, Bc), "fix-2")]
    p += shelves("sh", T, W - T, 981, HB - T, 4, Bc=Bc)
    moves = []
    for tag, y0, y1 in (("dr-1", PL + 2, 290), ("dr-2", 294, 522)):
        ps, mv = a_drawer(tag, 2, W - 2, y0, y1, Bc, T, W - T, 300)
        p += ps
        moves.append(mv)
    ps, mv = a_door("door", 2, W - 2, 983, HB - 2, Bc, "left", 1160)
    p += ps
    moves.append(mv)
    return dump("sonata-bum-1-15", [478, 366, 2340], p, moves)


# ------------------------------------------------------------------------------------------ 1.18 стеллаж
def m118():
    W, B = 478, 350
    p = carcass(W, B, HB, 90)
    p += shelves("sh", T, W - T, PL + T, HB - T, 7, Bc=B)
    return dump("sonata-bum-1-18", [478, 350, 2340], p, [])


# ------------------------------------------------------------------------------------------ 1.19 стеллаж угловой
def m119():
    """End shelving with quarter-round shelves (a = x, b = z in their top plane): the side 16 on the right, the back 16,
    top, bottom and 5 shelves 446 × 334 rounded to the front-left."""
    W, B, Hh = 462, 350, 2200
    k = 0.5523
    q = (f"M 0 16 L 446 16 L 446 350 C {r1(446 - k * 446)} 350 0 {r1(16 + k * 334)} 0 16 Z")
    p = [P(None, (446, 0, 0, 462, Hh, 350), "side"), P(None, (0, 0, 0, 446, Hh, 16), "back-panel"),
         P(None, (0, 0, 16, 446, 16, 350), "bottom", shape="path", outline=q),
         P(None, (0, Hh - T, 16, 446, Hh, 350), "top", shape="path", outline=q)]
    step = (Hh - 32 - 5 * T) / 6
    for j in range(5):
        y = T + (j + 1) * step + j * T
        p.append(P(None, (0, y, 16, 446, y + T, 350), f"shelf-{j + 1}", shape="path", outline=q))
    return dump("sonata-bum-1-19", [462, 350, 2200], p, [])


# ------------------------------------------------------------------------------------------ тумбы 1.21 / 1.22
def tumba(did, W, cols):
    """cols = ["door-l" / "drawers" / "door-r"] for the lower zone; the upper zone is open, two rows."""
    B, Hh = 366, 1031
    Bc = B - T
    p = carcass(W, Bc, Hh)
    n = len(cols)
    inner = W - 2 * T - (n - 1) * T
    cw = inner / n
    xs = [T + i * (cw + T) for i in range(n)]
    moves = []
    for i, x0 in enumerate(xs):
        x1 = x0 + cw
        if i < n - 1:
            p.append(P(None, (x1, PL + T, 12, x1 + T, Hh - T, Bc), f"part-{i + 1}"))
        p.append(P(None, (x0, 537, 12, x1, 553, Bc), f"fix-{i + 1}"))
        p.append(P(None, (x0 + 0.5, 776, 12, x1 - 0.5, 792, Bc - 2), f"open-shelf-{i + 1}"))
        fx0 = 2 if i == 0 else x0 - T / 2 + 1.5
        fx1 = W - 2 if i == n - 1 else x1 + T / 2 - 1.5
        kind = cols[i]
        if kind == "drawers":
            for j, (y0, y1) in enumerate(((PL + 2, 297), (300, 535))):
                ps, mv = a_drawer(f"dr-{i + 1}-{j + 1}", fx0, fx1, y0, y1, Bc, x0, x1, 300)
                p += ps
                moves.append(mv)
        else:
            hinge = "left" if kind == "door-l" else "right"
            p.append(P(None, (x0 + 0.5, 300, 12, x1 - 0.5, 316, Bc - 30), f"in-shelf-{i + 1}"))
            ps, mv = a_door(f"door-{i + 1}", fx0, fx1, PL + 2, 535, Bc, hinge, 480)
            p += ps
            moves.append(mv)
    return dump(did, [W, B, Hh], p, moves)


# ------------------------------------------------------------------------------------------ 1.06 шкаф 3д
def m106():
    W, B = 1430, 580
    Bc = B - T
    p = carcass(W, Bc, HB, 90)
    p += [P(None, (476, PL + T, 12, 492, HB - T, Bc), "part-1"), P(None, (938, PL + T, 12, 954, 500, Bc), "part-2"),
          P(None, (492, 500, 12, 954, 516, Bc), "fix-mid"), P(None, (492.5, 1950, 12, W - T - 0.5, 1966, Bc - 2), "hat")]
    p += shelves("sh-l", T, 476, PL + T, HB - T, 5, Bc=Bc)
    p.append(H("rail", (492, 1880, 272, W - T, 1905, 297), "r", kind="tube", mat="chrome"))
    moves = []
    for tag, y0, y1 in (("dr-1", PL + 2, 287), ("dr-2", 290, 515)):
        ps, mv = a_drawer(tag, 478, 952, y0, y1, Bc, 492, 938, 450)
        p += ps
        moves.append(mv)
    ps, mv = a_door("door-l", 2, 476, PL + 2, HB - 2, Bc, "left", 1150)
    p += ps
    moves.append(mv)
    # the middle door: 12 mm with a mirror 4 mm in a 45 border on its face
    f = front(None, (478, 518, Bc, 952, HB - 2, Bc + 12), "door-m")
    mi = {"id": "mirror-m", "kind": "mirror", "box": box(523, 600, Bc + 12, 907, HB - 60, Bc + 16)}
    k = knob("k-door-m", 912, 1150, Bc + 16)
    p += [f, mi, k]
    moves.append(door("door-m", ["door-m", "mirror-m", "k-door-m"], "left"))
    ps, mv = a_door("door-r", 954, W - 2, PL + 2, HB - 2, Bc, "right", 1150)
    p += ps
    moves.append(mv)
    return dump("sonata-bum-1-06", [1430, 580, 2340], p, moves)


# ------------------------------------------------------------------------------------------ 1.08 шкаф угловой 2д
def m108():
    """Corner wardrobe for the back-left corner (walls z = 0 and x = 0), like «Луна» 1.14: ХДФ on the walls, end sides
    400 deep at x 0…400 / z 0…400, top and bottom cut on the diagonal x + z = 1424, two doors 438 on it (swept slabs),
    the crown turned onto the diagonal; wings with shelves, the corner with a hat shelf and a rail."""
    S = 1040
    c = 1424.0
    pent = f"M 3 3 L 1024 3 L 1024 400 L 400 1024 L 3 1024 Z"
    p = [P(None, (0, 0, 1024, 400, HB, S), "side-l"), P(None, (1024, 0, 0, S, HB, 400), "side-r"),
         P(None, (3, PL, 3, 1024, PL + T, 1024), "bottom", shape="path", outline=pent),
         P(None, (3, HB - T, 3, 1024, HB, 1024), "top", shape="path", outline=pent),
         P(None, (3, PL + T, 624, 400, HB - T, 640), "part-l"), P(None, (624, PL + T, 3, 640, HB - T, 400), "part-r"),
         back(None, (0, PL, 3, 3, HB - T, 1024), "back-l", mat="white"),
         back(None, (3, PL, 0, 1024, HB - T, 3), "back-b", mat="white"),
         P(None, (3.5, 1950, 3, 623.5, 1966, 623), "hat"),
         H("rail", (300, 1860, 3, 325, 1885, 624), "r", kind="tube", mat="chrome")]
    p += shelves("sh-l", 3, 400, PL + T, HB - T, 5, z0=640.5, z1=1023.5, gap=0)
    for q in p[-5:]:
        q["box"] = box(3.5, q["box"][1], 640.5, 399.5, q["box"][4], 1023.5)
    rs = shelves("sh-r", 640, 1024, PL + T, HB - T, 5, z0=3.5, z1=399.5)
    p += rs
    # plinth rails on the diagonal are left out: the doors come down to 2 mm over the floor line of the bottom
    s2 = math.sqrt(2)
    ux, uz, nx, nz = 1 / s2, -1 / s2, 1 / s2, 1 / s2
    start = (400.0, 1024.0)
    L = math.dist(start, (1024.0, 400.0))
    g = (L - 2 * 438 - 3) / 2
    moves = []
    for k, (a0, hinge) in enumerate(((g, "left"), (g + 441, "right"))):
        a1 = a0 + 438
        path = [[r1(start[0] + ux * a0 + nx * 8), r1(start[1] + uz * a0 + nz * 8)],
                [r1(start[0] + ux * a1 + nx * 8), r1(start[1] + uz * a1 + nz * 8)]]
        did = f"door-{k + 1}"
        p.append({"id": did, "kind": "moulding", "mat": "front", "profile": "sonata-door-16x2186", "plane": "top",
                  "z": PL + 2, "path": path})
        am = a1 - 40 if hinge == "left" else a0 + 40
        cx, cz = start[0] + ux * am + nx * 16, start[1] + uz * am + nz * 16
        kid = f"k-{did}"
        kn = knob(kid, cx, 1150, cz)
        kn["rot"] = {"axis": "y", "deg": 45, "about": [r1(cx), 1150, r1(cz)]}
        p.append(kn)
        hx, hz = path[0] if hinge == "left" else path[1]
        moves.append(door(did, [did, kid], hinge, 100, axis=(hx + nx * 8, hz + nz * 8)))
    # the crown on the diagonal: a board 882 × 90 standing on the top, turned 45° about y
    cx = cz = (c - 30) / 2
    p.append(P(None, (cx - L / 2, HB, cz - 8, cx + L / 2, HB + 90, cz + 8), "crown", shape="path",
               outline=crown_path(cx - L / 2, cx + L / 2, HB, 90), rot={"axis": "y", "deg": 45, "about": [r1(cx), HB, r1(cz)]}))
    return dump("sonata-bum-1-08", [1040, 1040, 2340], p, moves)


# ------------------------------------------------------------------------------------------ 1.25 сундук
def m125():
    W, B, Hh = 900, 440, 460
    p = [P(None, (0, 0, 0, T, Hh - T, B), "side-l"), P(None, (W - T, 0, 0, W, Hh - T, B), "side-r"),
         P(None, (T, 0, B - T, W - T, Hh - T, B), "front-panel"), P(None, (T, 40, 0, W - T, Hh - T, T), "back-panel"),
         P(None, (T, 40, T, W - T, 56, B - T), "bottom")]
    lid = P(None, (0, Hh - T, 0, W, Hh, B), "lid", mat="front")
    p.append(lid)
    return dump("sonata-bum-1-25", [900, 440, 460], p,
                [{"type": "flap", "name": "lid", "parts": ["lid"], "hinge": "top", "angle": 95, "axis": [Hh, 0]}])


# ------------------------------------------------------------------------------------------ 1.50 полка
def m150():
    end = "M 0 0 L 285 0 L 285 60 C 200 60 140 150 100 285 L 0 285 Z"     # side plane (a = z, b = y)
    p = [P(None, (0, 0, 0, T, 285, 285), "end-l", shape="path", outline=end),
         P(None, (769, 0, 0, 785, 285, 285), "end-r", shape="path", outline=end),
         P(None, (T, 30, T, 769, 46, 285), "shelf"), P(None, (T, 46, 0, 769, 200, T), "back-rail")]
    return dump("sonata-bum-1-50", [785, 285, 285], p, [])


# ------------------------------------------------------------------------------------------ столы 1.70 / 1.71
def desk(did, W, layout):
    B, Hh = 576, 724
    Bc = B - T
    p = [P(None, (0, Hh - T, 0, W, Hh, B), "top")]
    moves = []
    pw = 450

    def pedestal(tag, x0, lower):
        out = [P(None, (x0, 0, 0, x0 + T, Hh - T, Bc), f"{tag}-sl"), P(None, (x0 + pw - T, 0, 0, x0 + pw, Hh - T, Bc), f"{tag}-sr"),
               P(None, (x0 + T, PL, 0, x0 + pw - T, PL + T, Bc), f"{tag}-bottom"),
               P(None, (x0 + T, 0, Bc - 36, x0 + pw - T, PL, Bc - 20), f"{tag}-plinth"),
               P(None, (x0 + T, 520, 12, x0 + pw - T, 536, Bc), f"{tag}-fix"),
               back(None, (x0 + 10, PL + 10, 8, x0 + pw - 10, Hh - 16, 11), f"{tag}-back", mat="white")]
        mv = []
        if lower == "door":
            out.append(P(None, (x0 + T + 0.5, 290, 12, x0 + pw - T - 0.5, 306, Bc - 30), f"{tag}-shelf"))
            ps, m = a_door(f"{tag}-door", x0 + 2, x0 + pw - 2, PL + 2, 534, Bc, "right" if x0 > W / 2 else "left", 480)
            out += ps
            mv.append(m)
        else:
            for j, (y0, y1) in enumerate(((PL + 2, 296), (300, 534))):
                ps, m = a_drawer(f"{tag}-dr-{j + 1}", x0 + 2, x0 + pw - 2, y0, y1, Bc, x0 + T, x0 + pw - T, 450)
                out += ps
                mv.append(m)
        return out, mv

    for tag, x0, lower in layout:
        if lower == "leg":
            p.append(P(None, (x0, 0, 0, x0 + T, Hh - T, Bc), f"{tag}"))
        else:
            ps, mv = pedestal(tag, x0, lower)
            p += ps
            moves += mv
    # the modesty rail between the pedestal / legs at the back
    xs = sorted(x0 for _, x0, _ in layout)
    lo = xs[0] + (pw if layout[0][2] != "leg" else T)
    hi = xs[-1]
    p.append(P(None, (lo, 400, 30, hi, Hh - T, 46), "modesty"))
    if W > 1200:
        # the middle drawer under the top between the pedestals
        f = front(None, (lo + 2, 600, Bc, hi - 2, 705, Bc + T), "dr-mid")
        bx = drawer_box("mid", ("m-sl", "m-sr", "m-b", "m-bot"), lo + 13, hi - 13, 612, 80, Bc - 400, Bc,
                        bottom=(hi - lo - 26 - 21, 405, 3))
        for q in bx:
            q.pop("n", None)
        k = knob("k-dr-mid", (lo + hi) / 2, 660, Bc + T)
        p += [f] + bx + [k]
        moves.append(dmove("dr-mid", ["dr-mid"] + ids(bx) + ["k-dr-mid"], 330))
    return dump(did, [W, B, Hh], p, moves)


# ------------------------------------------------------------------------------------------ шкафы-купе
def m_coupe(did, W, sections, n, mirror_mid=False):
    p = coupe(W, 650, 2292, sections)
    fills = [[(0, 3000, "mirror")] if (mirror_mid and i == 1) else [(0, 3000, "front")] for i in range(n)]
    d, moves = coupe_doors(W, 650, 2292, n, fills)
    return dump(did, [W, 650, 2292], p + d, moves)


# ------------------------------------------------------------------------------------------ кровати
def headboard_path(x0, x1, y0, y1):
    W = x1 - x0
    hump = 90
    e = y1 - hump
    return (f"M {r1(x0)} {r1(y0)} L {r1(x1)} {r1(y0)} L {r1(x1)} {r1(e - 80)} "
            f"C {r1(x1)} {r1(e - 20)} {r1(x1 - 40)} {r1(e)} {r1(x1 - 110)} {r1(e)} "
            f"L {r1(x0 + 0.66 * W)} {r1(e)} C {r1(x0 + 0.58 * W)} {r1(e)} {r1(x0 + 0.58 * W)} {r1(y1)} {r1(x0 + 0.5 * W)} {r1(y1)} "
            f"C {r1(x0 + 0.42 * W)} {r1(y1)} {r1(x0 + 0.42 * W)} {r1(e)} {r1(x0 + 0.34 * W)} {r1(e)} "
            f"L {r1(x0 + 110)} {r1(e)} C {r1(x0 + 40)} {r1(e)} {r1(x0)} {r1(e - 20)} {r1(x0)} {r1(e - 80)} Z")


def shelf_unit(tag, x0, side):
    """The bedside shelf unit 356 at the head: an outer side panel 16 × 400 × 540 (rounded front top), three shelves
    340 × 400 rounded at the free front corner; it hangs on the headboard. side = -1 on the left, +1 on the right."""
    xo0, xo1 = (x0, x0 + T) if side < 0 else (x0 + 340, x0 + 356)
    sx0, sx1 = (x0 + T, x0 + 356) if side < 0 else (x0, x0 + 340)
    p = [P(None, (xo0, 0, T, xo1, 540, 416), f"{tag}-side", shape="path",
           outline=rounded_rect_path(T, 0, 416, 540, {"tr": 120}))]
    corner = {"tr": 160} if side > 0 else {"tl": 160}
    for j, y in enumerate((20, 260, 524)):
        p.append(P(None, (sx0, y, T, sx1, y + T, 416), f"{tag}-shelf-{j + 1}", shape="path",
                   outline=rounded_rect_path(sx0, T, sx1, 416, corner)))
    return p


def bed(did, Wb, units=0):
    """x across the bed: Wb = the bed's width; units = 0 / 1 (left) / 2 (both sides) bedside shelf units."""
    L, Hh = 2042, 805
    off = 356 if units else 0
    Wt = Wb + (712 if units == 2 else off)
    x0, x1 = off, off + Wb
    p = [P(None, (x0, 0, 0, x1, Hh, T), "headboard", shape="path", outline=headboard_path(x0, x1, 0, Hh)),
         P(None, (x0, 0, L - T, x1, 540, L), "footboard", shape="path",
           outline=rounded_rect_path(x0, 0, x1, 540, {"tl": 120, "tr": 120})),
         P(None, (x0, 250, T, x0 + T, 420, L - T), "rail-l"), P(None, (x1 - T, 250, T, x1, 420, L - T), "rail-r"),
         P(None, (x0 + T, 330, T, x0 + 36, 346, L - T), "cleat-l"), P(None, (x1 - 36, 330, T, x1 - T, 346, L - T), "cleat-r"),
         P(None, (x0 + T, 346, T, x1 - T, 362, L - T), "base", mat="white"),
         P(None, (x0 + T, 0, 1013, x1 - T, 330, 1029), "mid-part"),
         {"id": "mattress", "kind": "mattress", "box": box(x0 + 20, 362, 20, x1 - 20, 542, L - 22)}]
    moves = []
    for k, (z0, z1) in enumerate(((20, 1014), (1028, L - 20))):
        f = P(None, (x1 - T, 30, z0, x1, 244, z1), f"dr-{k + 1}", kind="front", shape="path",
              outline=notch_top(z0, 30, z1, 244, (z0 + z1) / 2, 240, 38, 100))
        bx0 = x1 - T - 440
        box_ = [P(None, (bx0, 40, z0 + 13, x1 - T, 200, z0 + 29), f"dr-{k + 1}-sl"),
                P(None, (bx0, 40, z1 - 29, x1 - T, 200, z1 - 13), f"dr-{k + 1}-sr"),
                P(None, (bx0, 54, z0 + 29, bx0 + T, 200, z1 - 29), f"dr-{k + 1}-b"),
                back(None, (bx0, 45, z0 + 24, x1 - T + 5, 48, z1 - 24), f"dr-{k + 1}-bot")]
        p += [f] + box_
        moves.append({"type": "slide", "name": f"dr-{k + 1}", "parts": [f"dr-{k + 1}"] + ids(box_), "by": [380, 0, 0]})
    if units:
        p += shelf_unit("su-l", 0, -1)
        if units == 2:
            p += shelf_unit("su-r", x1, 1)
    return dump(did, [Wt, L, Hh], p, moves)


# ------------------------------------------------------------------------------------------ 1.45 кровать раздвижная
def m145():
    """Daybed 900 × 2000 over a trundle (1950 × 900): x = the length. High ends with rounded tops, a back panel, the
    upper base on the front rail; the trundle on castors slides out to the front."""
    L, B, Hh = 2058, 952, 965
    end = rounded_rect_path(0, 0, B, Hh, {"tl": 120, "tr": 120})
    p = [P(None, (0, 0, 0, T, Hh, B), "end-l", shape="path", outline=end),
         P(None, (L - T, 0, 0, L, Hh, B), "end-r", shape="path", outline=end),
         P(None, (T, 330, 0, L - T, 820, T), "back-panel"), P(None, (T, 320, B - T, L - T, 436, B), "front-rail"),
         P(None, (T, 420, T, L - T, 436, B - T), "base", mat="white"),
         {"id": "mattress-up", "kind": "mattress", "box": [21, 436, 20, 2037, 616, 930]}]
    t = [P(None, (30, 30, B - T - 2, L - 30, 290, B - 2), "tr-front", kind="front", shape="path",
           outline=notch_top(30, 30, L - 30, 290, L / 2, 340, 40, 160)),
         P(None, (30, 30, 40, 46, 290, B - T - 2), "tr-end-l"), P(None, (L - 46, 30, 40, L - 30, 290, B - T - 2), "tr-end-r"),
         P(None, (46, 30, 40, L - 46, 200, 56), "tr-back"),
         P(None, (46, 110, 56, L - 46, 126, B - T - 2), "tr-base", mat="white"),
         {"id": "mattress-low", "kind": "mattress", "box": [54, 126, 60, 2004, 306, 930]}]
    t += [H(f"c-{k + 1}", (x - 14, 0, z - 14, x + 14, 30, z + 14), "c", kind="tube", mat="black")
          for k, (x, z) in enumerate(((100, 150), (100, 800), (L - 100, 150), (L - 100, 800), (L / 2, 150), (L / 2, 800)))]
    p += t
    moves = [{"type": "slide", "name": "trundle", "parts": ids(t), "by": [0, 0, 800]}]
    return dump("sonata-bum-1-45", [2058, 952, 965], p, moves)


# ------------------------------------------------------------------------------------------ 1.40 кровать двухъярусная
def m140():
    """Bunk bed 2 × (900 × 2000), x = the length: a stair of four step-drawers 450 on the left (its outer side stepped),
    the beds between end panels 16 (the right one 1760 high with a rounded top); the upper bed: base on rails, a front
    rail under the mattress and a guard rail at 1560…1700, the back rail; the lower bed: back panel, front rail, base,
    two drawers under it."""
    L, B, Hh = 2492, 990, 1760
    xb = 450                             # the bed starts here
    end = rounded_rect_path(0, 0, B, Hh, {"tl": 100, "tr": 100})
    p = [P(None, (xb, 0, 0, xb + T, Hh, B), "end-l", shape="path", outline=end),
         P(None, (L - T, 0, 0, L, Hh, B), "end-r", shape="path", outline=end)]
    xi0, xi1 = xb + T, L - T
    # upper bed
    p += [P(None, (xi0, 1150, B - T, xi1, 1330, B), "up-front"), P(None, (xi0, 1560, B - T, xi1, 1700, B), "up-guard"),
          P(None, (xi0, 1150, 0, xi1, 1700, T), "up-back"),
          P(None, (xi0, 1270, T, xi1, 1286, B - T), "up-base", mat="white"),
          P(None, (xi0, 1250, T, xi0 + 20, 1270, B - T), "up-cleat-l"), P(None, (xi1 - 20, 1250, T, xi1, 1270, B - T), "up-cleat-r"),
          {"id": "mattress-up", "kind": "mattress", "box": box(xi0 + 20, 1286, 30, xi1 - 20, 1466, 960)}]
    # lower bed
    p += [P(None, (xi0, 250, 0, xi1, 900, T), "low-back"), P(None, (xi0, 250, B - T, xi1, 420, B), "low-front"),
          P(None, (xi0, 330, T, xi1, 346, B - T), "low-base", mat="white"),
          P(None, (1463, 0, T, 1479, 330, 400), "low-part"),
          {"id": "mattress-low", "kind": "mattress", "box": box(xi0 + 20, 346, 30, xi1 - 20, 526, 960)}]
    moves = []
    for k, (a0, a1) in enumerate(((xi0 + 2, 1469), (1473, xi1 - 2))):
        f = front(None, (a0, 30, B - T, a1, 244, B), f"dr-{k + 1}", shape="path",
                  outline=notch_top(a0, 30, a1, 244, (a0 + a1) / 2, 240, 38, 100))
        bx = drawer_box(f"d{k + 1}", ("sl", "sr", "b", "bot"), a0 + 20, a1 - 20, 40, 170, B - T - 500, B - T,
                        bottom=(a1 - a0 - 40 - 21, 505, 3))
        for q in bx:
            q.pop("n", None)
        p += [f] + bx
        moves.append(dmove(f"dr-{k + 1}", [f["id"]] + ids(bx), 450))
    # the stair: outer side stepped (front plane outline), four step boxes with drawer fronts
    steps = [(0, 330), (330, 660), (660, 990), (990, 1270)]
    sd = 520                                  # the stair's depth, at the front
    z0 = B - sd
    step_side = "M 0 0 L 16 0 L 16 1270 L 0 1270 Z"
    p.append(P(None, (0, 0, z0, T, 1270, B), "st-side"))
    for k, (y0, y1) in enumerate(steps):
        # each step: a tread on top, its front is a drawer
        xs0 = T + k * 0 if k == 0 else T
        p.append(P(None, (T, y1 - T, z0, xb, y1, B), f"st-tread-{k + 1}"))
        if k == 0:
            p.append(P(None, (T, 0, z0, xb, T, B), "st-bottom"))
        f = front(None, (T + 2, y0 + (T if k == 0 else 2), B, xb - 2, y1 - T - 2, B + 0.001), f"st-dr-{k + 1}")
        f["box"] = box(T + 2, y0 + (T + 2 if k == 0 else 2), B - T, xb - 2, y1 - T - 2, B)
        f["shape"] = "path"
        fb = f["box"]
        f["outline"] = notch_top(fb[0], fb[1], fb[3], fb[4], (fb[0] + fb[3]) / 2, 160, 30, 60)
        by0 = fb[1] + 20
        bh = min(200.0, fb[4] - by0 - 20)
        bx = drawer_box(f"s{k + 1}", ("sl", "sr", "b", "bot"), T + 13, xb - 13, by0, bh, B - T - 450, B - T,
                        bottom=(xb - T - 26 - 21, 455, 3))
        for q in bx:
            q.pop("n", None)
        p += [f] + bx
        moves.append(dmove(f"st-dr-{k + 1}", [f["id"]] + ids(bx), 380))
    p.append(back(None, (T, 0, z0 - 3, xb, 1270, z0), "st-back", mat="white"))
    return dump("sonata-bum-1-40", [2492, 990, 1760], p, moves)


PROFILES = {"sonata-door-16x2186": {"name": "Дверь углового шкафа «Соната Бум» 16 × 2186 (плита по диагонали)",
                                    "pts": [[-8, 0], [-8, 2186], [8, 2186], [8, 0]]}}
FIN = [{"id": "sonata-bum-karelia", "name": "Сосна Карелия", "body": "door_enamel_whitey#e6e7e1", "swatch": "#e6e7e1",
        "roles": {"white": "door_enamel_whitey#f0f0ee"}}]
COLL = [{"id": SLUG, "name": "Соната Бум", "brand": "Пинскдрев", "finishes": ["sonata-bum-karelia"], "metal": "chrome",
         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 125–128 (разворот 246–253); все модули по каталогу (инструкций и "
                 "страниц сайта нет). ЛДСП 16 «Сосна Карелия»: боковины до пола, цоколь 60, накладные фасады, фигурная "
                 "корона 90 на высоких модулях, хромированные кнопки; кровати с фигурным изголовьем, ящиками с "
                 "фрезерованной ручкой; шкафы-купе как «Челси Бум»."}]


def models():
    rows = [
        ("1-06", "П3.0439.1.06", "Шкаф для одежды 3д «Соната Бум»", "kids", [1430, 580, 2340], "с зеркалом в средней двери"),
        ("1-08", "П3.0439.1.08", "Шкаф угловой 2д «Соната Бум»", "kids", [1040, 1040, 2340], "в угол: стены сзади и слева"),
        ("1-12", "П3.0439.1.12", "Шкаф 2д «Соната Бум»", "kids", [954, 366, 2340], None),
        ("1-15", "П3.0439.1.15", "Шкаф «Соната Бум»", "kids", [478, 366, 2340], None),
        ("1-18", "П3.0439.1.18", "Стеллаж «Соната Бум»", "kids", [478, 350, 2340], None),
        ("1-19", "П3.0439.1.19", "Стеллаж «Соната Бум»", "kids", [462, 350, 2200], "торцевой, полки со скруглением"),
        ("1-21", "П3.0439.1.21", "Тумба 3д «Соната Бум»", "kids", [1432, 366, 1031], None),
        ("1-22", "П3.0439.1.22", "Тумба 2д «Соната Бум»", "kids", [956, 366, 1031], None),
        ("1-25", "П3.0439.1.25", "Сундук «Соната Бум»", "kids", [900, 440, 460], "с. 127 и index B440 (с. 128 пишет B400)"),
        ("1-40", "П3.0439.1.40", "Кровать двухъярусная «Соната Бум»", "kids", [2492, 990, 1760],
         "спальные места 2 × 900×2000; лестница-комод слева; x — длина"),
        ("1-45", "П3.0439.1.45", "Кровать раздвижная «Соната Бум»", "kids", [2058, 952, 965],
         "матрацы 2000×900 и 1950×900; x — длина"),
        ("1-50", "П3.0439.1.50", "Полка «Соната Бум»", "kids", [785, 285, 285], None),
        ("1-52", "П3.0439.1.52", "Шкаф-купе 2Д «Соната Бум»", "kids", [1529, 650, 2292], None),
        ("1-53", "П3.0439.1.53", "Шкаф-купе 3Д «Соната Бум»", "kids", [2027, 650, 2292], None),
        ("1-55", "П3.0439.1.55", "Шкаф-купе 3Д «Соната Бум»", "kids", [2027, 650, 2292], "с зеркалом (средняя дверь)"),
        ("1-70", "П3.0439.1.70", "Стол письменный «Соната Бум»", "kids", [1000, 576, 724], None),
        ("1-71", "П3.0439.1.71", "Стол письменный «Соната Бум»", "kids", [1432, 576, 724], None),
        ("1-80", "П3.0439.1.80", "Кровать 1-09 «Соната Бум»", "kids", [950, 2042, 805], "спальное место 900×2000"),
        ("1-81", "П3.0439.1.81", "Кровать 1-12 «Соната Бум»", "kids", [1250, 2042, 805], "спальное место 1200×2000"),
        ("1-82", "П3.0439.1.82", "Кровать 2-14 «Соната Бум»", "kids", [1450, 2042, 805], "спальное место 1400×2000"),
        ("1-83", "П3.0439.1.83", "Кровать 2-16 «Соната Бум»", "kids", [1650, 2042, 805], "спальное место 1600×2000"),
        ("1-35", "П3.0439.1.35", "Кровать 1-09 «Соната Бум»", "kids", [1306, 2042, 805],
         "с полкой у изголовья (каталог: 950 без полок, 1306 с полками); спальное место 900×2000"),
        ("1-36", "П3.0439.1.36", "Кровать 1-12 «Соната Бум»", "kids", [1962, 2042, 805],
         "с полками по обе стороны изголовья (1250 без полок); спальное место 1200×2000"),
        ("1-37", "П3.0439.1.37", "Кровать 2-14 «Соната Бум»", "kids", [2162, 2042, 805],
         "с полками по обе стороны изголовья (1450 без полок); спальное место 1400×2000"),
        ("1-38", "П3.0439.1.38", "Кровать 2-16 «Соната Бум»", "kids", [2362, 2042, 805],
         "с полками по обе стороны изголовья (1650 без полок); спальное место 1600×2000"),
    ]
    out = []
    for tail, code, name, cat, size, note in rows:
        m = {"id": f"{SLUG}-{tail}", "code": code, "name": name, "collection": SLUG, "category": cat, "size": size,
             "page": 128, "note": "по каталогу, без инструкции" + (f"; {note}" if note else "")}
        if tail == "1-50":
            m["mount"] = "wall"
        out.append(m)
    return out


if __name__ == "__main__":
    for f in (m112, m115, m118, m119, m106, m108, m125, m150, m145, m140):
        print(f())
    print(tumba("sonata-bum-1-21", 1432, ["door-l", "drawers", "door-r"]))
    print(tumba("sonata-bum-1-22", 956, ["door-l", "door-r"]))
    print(desk("sonata-bum-1-70", 1000, [("ped", 0, "door"), ("leg", 984, "leg")]))
    print(desk("sonata-bum-1-71", 1432, [("ped-l", 0, "drawers"), ("ped-r", 982, "door")]))
    print(m_coupe("sonata-bum-1-52", 1529, [(740, "rail"), (741, "shelves")], 2))
    print(m_coupe("sonata-bum-1-53", 2027, [(654, "shelves"), (655, "rail"), (654, "shelves")], 3))
    print(m_coupe("sonata-bum-1-55", 2027, [(654, "shelves"), (655, "rail"), (654, "shelves")], 3, mirror_mid=True))
    for tail, w, u in (("1-80", 950, 0), ("1-81", 1250, 0), ("1-82", 1450, 0), ("1-83", 1650, 0),
                       ("1-35", 950, 1), ("1-36", 1250, 2), ("1-37", 1450, 2), ("1-38", 1650, 2)):
        print(bed(f"sonata-bum-{tail}", w, u))
    write_fragment(SLUG, FIN, COLL, models(), PROFILES)
