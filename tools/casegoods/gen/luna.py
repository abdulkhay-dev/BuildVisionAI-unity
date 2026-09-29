"""«Луна» (П7.049, «Пинскдрев-Заславль»; kids' / teen room, «Сосна рандерс» + «Оникс»): 15 modules.

By instruction (the Заславль tables «№, наименование, a×b, n» without thickness: every board is ЛДСП 16, backs ДВП
4): 1.09 брусок-ограждение, 1.14 шкаф угловой, 1.31 комод, 1.72 полка, 2.52 / 2.53 столы, 2.62 стеллаж.
By photo (site pinskdrev.by, catalogue p. 121–122), built with the instructed modules' construction: 1.11 / 1.12 /
1.13 шкафы комбинированные, 1.21 тумба, 1.71 полка, 1.01 кровать 1-09, 2.51 стол, 2.61 стеллаж.

Construction (instructions): carcass ЛДСП 16 on adjustable plastic feet «опора 50×17» (17 mm: 840 + 17 = 857,
1888 + 32 + 17 = 1937, 2000 + 17 = 2017); tall pieces: top and bottom full width, the sides between them; the chest:
a full bottom, the left side on it, the top over the left side, the right side full height; the backs ДВП nailed
over the back edges (4 mm: 380 + 4 + 16 = 400, 300 + 4 = 304). Fronts ЛДСП 16 overlay (2–4 mm reveals, 3–4 mm gaps).
Drawers: the front is the box's front wall, sides / back ЛДСП 16, the ДВП bottom nailed under, a lengthwise batten
under the bottom (1.31). Handles: dark square bars ≈ 160 (catalogue p. 122 close-up) — upright on doors, level on
drawers. Open shelf towers in «Оникс» beside the pine cabinets.

    python3 tools/casegoods/gen/luna.py
"""
from kit_w4k import (P, H, back, front, bar, drawer_box, dmove, door, ids, write_cutlist, write_fragment,
                     notch_top, rounded_rect_path, dump, r1)

SLUG = "luna"
T = 16.0
FT = 17.0   # the feet


def feet(xs, zs, tag="f", letter="F"):
    out, k = [], 0
    for x in xs:
        for z in zs:
            k += 1
            out.append(H(f"{tag}-{k}", (x - 25, 0, z - 25, x + 25, FT, z + 25), letter, kind="tube", mat="black"))
    return out


def hbar(pid, x, y, z, dirn="right", letter="D", length=160):
    return bar(pid, x, y, z, length, dirn, band=12, t=10, standoff=25, post=10, section="square", letter=letter)


def flap(name, parts, hinge="bottom", angle=90):
    return {"type": "flap", "name": name, "parts": parts, "hinge": hinge, "angle": angle}


def acc(p):
    p["mat"] = "accent"
    return p


# ------------------------------------------------------------------------------------------ 1.31 комод
def m131():
    B = 400
    zb, zc, zf = 4, 384, 400
    p = [
        P(2, (0, FT, zb, 800, FT + 16, zc)),
        P(3, (0, 33, zb, 16, 839, zc)),
        P(1, (0, 839, zb, 782, 855, zc)),
        acc(P(4, (784, 33, zb, 800, 857, zc))),
        P(9, (18, 335, zb, 782, 535, zb + 16)),
        back(16, (4, 17, 0, 796, 433, 4), "16-1", mat="white"), back(16, (4, 437, 0, 796, 853, 4), "16-2", mat="white"),
        # the open shelf tower in «Оникс»
        acc(P(8, (800, FT, 6, 1048, 33, 384))),
        acc(P(5, (1032, 33, 6, 1048, 761, 384))),
        acc(P(6, (800, 761, 6, 1049, 777, 384))),
        acc(P(7, (800, 265, 6, 1032, 281, 384), "7-1")), acc(P(7, (800, 513, 6, 1032, 529, 384), "7-2")),
    ]
    moves = []
    for k, (y0, y1) in enumerate(((17, 224), (228, 435), (439, 646), (650, 857))):
        f = front(10, (4, y0, zc, 796, y1, zf), f"10-{k + 1}")
        by = y0 + 40
        bx = drawer_box(k + 1, ("11", "12", "13", "15"), 31, 769, by, 144, zc - 350, zc, hb=144,
                        bottom=(734, 355, 4), under=True)
        bat = P(14, (355, by - 20, zc - 352, 445, by - 4, zc - 2), f"14-{k + 1}")
        h = hbar(f"k-{k + 1}", 400, (y0 + y1) / 2, zf, "right", "k")
        p += [f] + bx + [bat, h]
        moves.append(dmove(f"drawer_{k + 1}", [f["id"]] + ids(bx) + [bat["id"], h["id"]], 300))
    p += feet((40, 760), (40, 350)) + feet((1008,), (40, 350), "fu")
    return dump("luna-1-31", [1048, 400, 857], p, moves)


# ------------------------------------------------------------------------------------------ 1.72 полка
def m172():
    p = [P(2, (0, 0, 0, 942, 16, 250)), P(1, (0, 584, 0, 942, 600, 250)),
         P(3, (0, 16, 0, 16, 584, 248)), P(5, (926, 16, 0, 942, 584, 248)), P(4, (316, 16, 0, 332, 584, 248)),
         P(6, (16, 276, 0, 316, 292, 248)),
         P(7, (333, 194.7, 0, 925, 210.7, 248), "7-1"), P(7, (333, 389.3, 0, 925, 405.3, 248), "7-2")]
    return dump("luna-1-72", [942, 250, 600], p, [])


# ------------------------------------------------------------------------------------------ 2.62 стеллаж
def m262():
    p = [acc(P(3, (0, FT, 4, 350, 33, 304))), acc(P(1, (0, 1921, 4, 350, 1937, 304))),
         acc(P(2, (0, 33, 4, 16, 1921, 302), "2-l")), acc(P(2, (334, 33, 4, 350, 1921, 302), "2-r"))]
    cub = (1888 - 5 * 16) / 6
    for k in range(5):
        y = 33 + (k + 1) * cub + k * 16
        p.append(acc(P(4, (17, y, 6, 333, y + 16, 302), f"4-{k + 1}")))
    for k in range(3):
        y0 = 18.5 + k * 639.5
        p.append(back(5, (3, y0, 0, 347, y0 + 637, 4), f"5-{k + 1}", mat="white"))
    p += feet((40, 310), (40, 270))
    for q in p:
        if q.get("covers") == ["F"]:
            q["covers"] = ["C"]
    return dump("luna-2-62", [350, 304, 1937], p, [])


# ------------------------------------------------------------------------------------------ 1.09 брусок-ограждение
def m109():
    p = [P(1, (0, 0, 0, 900, 400, 16), shape="path", outline=rounded_rect_path(0, 0, 900, 400, {"tl": 90, "tr": 90}))]
    return dump("luna-1-09", [900, 16, 400], p, [])


# ------------------------------------------------------------------------------------------ 2.52 стол
def m252():
    zf = 620
    p = [P(1, (0, 744, 0, 1200, 760, 700), shape="path", outline=rounded_rect_path(0, 0, 1200, 700, {"tl": 60, "tr": 60})),
         P(2, (40, 0, 0, 56, 744, 620)), P(5, (56, 394, 30, 778, 744, 46)),
         acc(P(3, (778, 0, 0, 794, 744, 620))), acc(P(4, (1144, 0, 0, 1160, 744, 620))),
         acc(P(7, (794, 20, 0, 1144, 36, 620), "7-1")), acc(P(7, (794, 570, 0, 1144, 586, 620), "7-2")),
         acc(P(6, (794, 36, 0, 1144, 570, 16)))]
    # the top's outline lies in its top plane (x, z): rounded front corners
    p[0]["outline"] = top_outline(0, 0, 1200, 700, 60)
    moves = []
    for k, (y0, y1) in enumerate(((22, 208), (211, 397), (400, 586))):
        f = front(8, (780, y0, zf, 1158, y1, 636), f"8-{k + 1}")
        by = y0 + 34
        bx = drawer_box(k + 1, ("9", "10", "11", "12"), 807, 1131, by, 120, zf - 500, zf, hb=120,
                        bottom=(322, 505, 4), under=True)
        h = hbar(f"k-{k + 1}", 969, (y0 + y1) / 2, 636, "right", "k")
        p += [f] + bx + [h]
        moves.append(dmove(f"drawer_{k + 1}", [f["id"]] + ids(bx) + [h["id"]], 380))
    return dump("luna-2-52", [1200, 700, 760], p, moves)


def top_outline(x0, z0, x1, z1, r):
    """A top's outline in the top plane (a = x, b = z): the front corners (z1) rounded r."""
    return rounded_rect_path(x0, z0, x1, z1, {"tl": r, "tr": r})


# ------------------------------------------------------------------------------------------ 2.53 стол
def m253():
    zb, zc, zf = 4, 604, 620
    p = [P(1, (0, 734, 0, 2200, 750, 700)),
         P(2, (49, 0, zb, 65, 734, zc)), P(3, (2135, 0, zb, 2151, 734, zc)),
         P(4, (65, 384, 30, 699, 734, 46), "4-l"), P(4, (1501, 384, 30, 2135, 734, 46), "4-r"),
         acc(P(8, (699, 16, zb, 1501, 32, zc))),
         acc(P(5, (699, 32, zb, 715, 734, zc))), acc(P(6, (1485, 32, zb, 1501, 734, zc))),
         acc(P(7, (1092, 32, zb, 1108, 734, zc))),
         acc(P(9, (716, 518, zb, 1091, 534, zc))), acc(P(10, (1109, 518, zb, 1484, 534, zc))),
         acc(P(11, (716, 654, zb, 1091, 734, zb + 16), "11-l")), acc(P(11, (1109, 654, zb, 1484, 734, zb + 16), "11-r")),
         back(13, (701, 16, 0, 1097, 523, 4), "13-l", mat="white"), back(13, (1103, 16, 0, 1499, 523, 4), "13-r", mat="white"),
         back(12, (701, 529, 0, 1097, 734, 4), "12-l", mat="white"), back(12, (1103, 529, 0, 1499, 734, 4), "12-r", mat="white")]
    moves = []
    for col, (x0, n, ox) in enumerate(((701, "14", 715), (1103, "15", 1108))):
        for k, (y0, y1) in enumerate(((19, 189), (193, 363), (367, 537))):
            f = front(n, (x0, y0, zc, x0 + 396, y1, zf), f"{n}-{k + 1}")
            by = y0 + 22
            tag = f"{col}{k}"
            bx = drawer_box(tag, ("16", "17", "18", "19"), ox + 14, ox + 14 + 349, by, 128, zc - 500, zc, hb=128,
                            bottom=(345, 505, 4), under=True)
            h = hbar(f"k-{tag}", x0 + 198, (y0 + y1) / 2, zf, "right", "k")
            p += [f] + bx + [h]
            moves.append(dmove(f"drawer_{tag}", [f["id"]] + ids(bx) + [h["id"]], 380))
    p += [H(f"f-{k + 1}", (x - 25, 0, z - 25, x + 25, 16, z + 25), "F", kind="tube", mat="black")
          for k, (x, z) in enumerate(((740, 40), (740, 560), (1460, 40), (1460, 560)))]
    return dump("luna-2-53", [2200, 700, 750], p, moves)


# ------------------------------------------------------------------------------------------ 1.14 шкаф угловой
def m114():
    """Corner wardrobe for the back-left corner of a room: walls along z = 0 (back) and x = 0 (left). Plan (x, z):
    ДВП backs on both walls (0…4), top / bottom 1000 × 1000 with the front corner cut from (382, 1004) to (1004, 382);
    the end sides 2 (z 1004…1020, x 4…382) and 3 (x 1004…1020, z 4…382); the left column (shelves 10, 300 wide) between
    side 2 and partition 5; the right column (400 wide, 298 deep: shelves 12, two drawers on the batten 11 and the rail
    13) between partition 6 (300 deep) and side 3; the middle hanging space behind the ЛДСП back 7 (584, on the back
    wall) with the two big shelves 8, the rail N (660) from 7 to 5 and the rail stiffener 9. Two doors 437 on the
    diagonal (x + z = 1386), written as swept slabs (moulding, see the notes)."""
    Y0, Y1 = FT, FT + 2000
    yb, yt = Y0 + 16, Y1 - 16
    cut = 1386
    pent = f"M 4 4 L 1004 4 L 1004 382 L 382 1004 L 4 1004 Z"
    p = [P(4, (4, Y0, 4, 1004, yb, 1004), shape="path", outline=pent),
         P(1, (4, yt, 4, 1004, Y1, 1004), shape="path", outline=pent),
         P(2, (4, Y0, 1004, 382, Y1, 1020)), P(3, (1004, Y0, 4, 1020, Y1, 382)),
         P(5, (4, yb, 686, 382, yt, 702)), P(6, (588, yb, 4, 604, yt, 304)),
         P(7, (4, yb, 4, 588, yt, 20))]
    # middle: two big shelves 8 (584 × 666, the front corner cut clear of the doors), the stiffener 9 under the top
    sh8 = "M 4 20 L 588 20 L 588 686 L 4 686 Z"
    p += [P(8, (4, 300, 20, 588, 316, 686), "8-1", shape="path", outline=sh8),
          P(8, (4, 1700, 20, 588, 1716, 686), "8-2", shape="path", outline=sh8),
          P(9, (4, yt - 280, 20, 20, yt, 686)),
          H("N", (296, 1650, 20, 311, 1680, 686), "N", kind="tube", mat="chrome")]
    # left column: 5 shelves 10 (300 × 376) between partition 5 and side 2
    for k in range(5):
        y = yb + (k + 1) * (yt - yb - 5 * 16) / 6 + k * 16
        p.append(P(10, (5, y, 703, 381, y + 16, 1003), f"10-{k + 1}"))
    # right column: batten 11 on side 3, rail 13 over the drawers, shelves 12
    p += [P(11, (988, yb, 4, 1004, yb + 354, 302)), P(13, (604, yb + 354, 222, 1004, yb + 434, 238))]
    for k in range(4):
        y = yb + 450 + (k + 1) * 290
        p.append(P(12, (604, y, 4, 1004, y + 16, 302), f"12-{k + 1}"))
    moves = []
    for k in range(2):
        fy0 = yb + 6 + k * 170
        f = front(22, (606, fy0, 286, 986, fy0 + 150, 302), f"22-{k + 1}")
        bx = drawer_box(k + 1, ("23", "24", "25", "26"), 617, 975, fy0 + 8, 134, 36, 286, hb=134,
                        bottom=(356, 255, 4), under=True)
        moves.append(dmove(f"drawer_{k + 1}", [f["id"]] + ids(bx), 220))
        p += [f] + bx
    # the ДВП backs on the two walls (sizes of the table; the joints on the shelves), all 4 thick
    p += [back(15, (0, Y0, 683, 4, Y0 + 637, 1004), "15-1", mat="white"),
          back(15, (0, Y0 + 640, 683, 4, Y0 + 1277, 1004), "15-2", mat="white"),
          back(16, (0, Y0 + 1280, 683, 4, Y0 + 1998, 1004), mat="white"),
          back(18, (0, Y0, 4, 4, Y0 + 623, 691), "18-1", mat="white"),
          back(17, (0, Y0 + 623, 4, 4, Y0 + 994, 691), "17-1", mat="white"),
          back(17, (0, Y0 + 994, 4, 4, Y0 + 1365, 691), "17-2", mat="white"),
          back(18, (0, Y0 + 1365, 4, 4, Y0 + 1988, 691), "18-2", mat="white"),
          back(19, (575, Y0 + 1659, 0, 1003, Y0 + 2000, 4), mat="white"),
          back(20, (575, Y0 + 316, 0, 1003, Y0 + 986, 4), "20-1", mat="white"),
          back(20, (575, Y0 + 989, 0, 1003, Y0 + 1659, 4), "20-2", mat="white"),
          back(21, (575, Y0, 0, 1003, Y0 + 308, 4), mat="white")]
    # doors on the diagonal: their back faces on x + z = 1386, 437 wide, 1996 high, 3 mm apart
    import math
    s2 = math.sqrt(2)
    ux, uz = 1 / s2, -1 / s2         # along the doors, from side 2 to side 3
    nx, nz = 1 / s2, 1 / s2          # outwards
    start = (382.0, 1004.0)
    L = math.dist(start, (1004.0, 382.0))
    g = (L - 2 * 437 - 3) / 2
    dy0, dy1 = Y0 + 2, Y1 - 2
    for k, (a0, hinge, hid) in enumerate(((g, "left", "D-1"), (g + 437 + 3, "right", "D-2"))):
        a1 = a0 + 437
        path = [[r1(start[0] + ux * a0 + nx * 8), r1(start[1] + uz * a0 + nz * 8)],
                [r1(start[0] + ux * a1 + nx * 8), r1(start[1] + uz * a1 + nz * 8)]]
        did = f"14-{k + 1}"
        p.append({"id": did, "kind": "moulding", "mat": "front", "profile": "luna-door-16x1996", "plane": "top",
                  "z": dy0, "path": path, "covers": ["14"]})
        # the handle near the meeting edge, turned onto the diagonal
        am = a1 - 40 if hinge == "left" else a0 + 40
        cx, cz = start[0] + ux * am + nx * 16, start[1] + uz * am + nz * 16
        p.append({"id": hid, "kind": "handle", "model": "bar", "mat": "metal", "at": [r1(cx), 1017], "dir": "up",
                  "d": 160, "band": 12, "t": 10, "standoff": 25, "post": 10, "section": "square", "z": r1(cz),
                  "covers": ["D"], "rot": {"axis": "y", "deg": 45, "about": [r1(cx), 1017, r1(cz)]}})
        hx, hz = (path[0] if hinge == "left" else path[1])
        moves.append(door(f"door_{k + 1}", [did, hid], hinge, 100, axis=(hx + nx * 8, hz + nz * 8)))
    p += [H(f"f-{k + 1}", (x - 25, 0, z - 25, x + 25, FT, z + 25), "F", kind="tube", mat="black")
          for k, (x, z) in enumerate(((40, 40), (500, 40), (960, 40), (40, 500), (500, 500), (960, 340),
                                      (40, 960), (340, 960), (660, 660)))]
    return dump("luna-1-14", [1020, 1020, 2017], p, moves)


# ------------------------------------------------------------------------------------------ by photo: combined wardrobes
def lower_box(W, zc, h_front=448, split=None):
    """The lower box under the combined wardrobes: bottom on the feet, sides, the fixed top (full width) at 449…465.
    split = x of a middle partition (1.13)."""
    p = [P(None, (0, FT, 4, W, 33, zc), "bottom"), P(None, (0, 33, 4, 16, 449, zc), "lb-side-l"),
         P(None, (W - 16, 33, 4, W, 449, zc), "lb-side-r"), P(None, (0, 449, 4, W, 465, zc), "lb-top")]
    if split:
        p.append(P(None, (split - 8, 33, 4, split + 8, 449, zc), "lb-part"))
    return p


def column(x0, x1, zc, top_y, n_shelves, tag="c"):
    """An open shelf tower in «Оникс» on the lower box: its outer side, its top, the shelves (its inner side is the
    wardrobe's side, given by the caller)."""
    p = [acc(P(None, (x1 - 16, 465, 4, x1, top_y - 16, zc), f"{tag}-side")),
         acc(P(None, (x0, top_y - 16, 4, x1, top_y, zc), f"{tag}-top"))]
    step = (top_y - 16 - 465 - n_shelves * 16) / (n_shelves + 1)
    for k in range(n_shelves):
        y = 465 + (k + 1) * step + k * 16
        p.append(acc(P(None, (x0, y, 6, x1 - 16, y + 16, zc), f"{tag}-shelf-{k + 1}")))
    return p


def m111(W=800, B=600, wx=600, did="luna-1-11", rail=True, shelves=(1760,), inner_shelves=()):
    zc, zf = B - 16, B
    p = lower_box(W, zc)
    p += [P(None, (0, 465, 4, 16, 2001, zc), "w-side-l"), acc(P(None, (wx - 16, 465, 4, wx, 2001, zc), "w-side-r")),
          P(None, (0, 2001, 4, wx, 2017, zc), "w-top")]
    p += column(wx, W, zc, 1985, 4)
    for k, y in enumerate(shelves):
        p.append(P(None, (16.5, y, 6, wx - 16.5, y + 16, zc - 4), f"w-shelf-{k + 1}"))
    for k, y in enumerate(inner_shelves):
        p.append(P(None, (16.5, y, 6, wx - 16.5, y + 16, zc - 4), f"w-shelf-i{k + 1}"))
    if rail:
        cz = (4 + zc) / 2
        p.append(H("rail", (16, 1690, cz - 7.5, wx - 16, 1720, cz + 7.5), "N", kind="tube", mat="chrome"))
    p += [back(None, (2, FT + 1, 0, W - 2, 465, 4), "back-low", mat="white"),
          back(None, (2, 465, 0, wx - 2, 2015, 4), "back-w", mat="white"),
          acc(back(None, (wx - 2, 465, 0, W - 2, 1983, 4), "back-c"))]
    fl = front(None, (2, 19, zc, W - 2, 463, zf), "flap")
    fh = hbar("k-flap", W / 2, 400, zf, "right", "D")
    dr = front(None, (2, 467, zc, wx - 2, 2015, zf), "door")
    dh = hbar("k-door", wx - 40, 1250, zf, "up", "D")
    p += [fl, fh, dr, dh]
    moves = [flap("flap", ["flap", "k-flap"]), door("door", ["door", "k-door"], "left")]
    p += feet((40, W - 40), (40, B - 60))
    return dump(did, [W, B, 2017], p, moves)


def m112():
    return m111(600, 400, 420, "luna-1-12", rail=False, shelves=(), inner_shelves=(760, 1060, 1360, 1660))


def m113():
    W, B, wx = 1460, 600, 1260
    zc, zf = B - 16, B
    p = lower_box(W, zc, split=840)
    p += [P(None, (0, 465, 4, 16, 2001, zc), "w-side-l"), P(None, (412, 465, 4, 428, 2001, zc), "w-part"),
          acc(P(None, (wx - 16, 465, 4, wx, 2001, zc), "w-side-r")), P(None, (0, 2001, 4, wx, 2017, zc), "w-top")]
    p += column(wx, W, zc, 1985, 4)
    for k, y in enumerate((760, 1060, 1360, 1660)):
        p.append(P(None, (16.5, y, 6, 411.5, y + 16, zc - 4), f"w-shelf-l{k + 1}"))
    p.append(P(None, (428.5, 1760, 6, wx - 16.5, 1776, zc - 4), "w-shelf-top"))
    cz = (4 + zc) / 2
    p.append(H("rail", (428, 1690, cz - 7.5, wx - 16, 1720, cz + 7.5), "N", kind="tube", mat="chrome"))
    p += [back(None, (2, FT + 1, 0, W - 2, 465, 4), "back-low", mat="white"),
          back(None, (2, 465, 0, 420, 2015, 4), "back-w1", mat="white"),
          back(None, (420, 465, 0, wx - 2, 2015, 4), "back-w2", mat="white"),
          acc(back(None, (wx - 2, 465, 0, W - 2, 1983, 4), "back-c"))]
    moves = []
    # the lower left: two drawers under the doors 1–2; the lower right: a flap under door 3 and the tower
    for k, (y0, y1) in enumerate(((19, 239), (243, 463))):
        f = front(None, (2, y0, zc, 838, y1, zf), f"dr-{k + 1}")
        bx = drawer_box(k + 1, ("dr-sl", "dr-sr", "dr-b", "dr-bot"), 29, 823, y0 + 30, 150, zc - 450, zc, hb=150,
                        bottom=(794, 450, 4), under=True)
        for q in bx:
            q.pop("n", None)
        h = hbar(f"k-dr-{k + 1}", 420, (y0 + y1) / 2 + 60, zf, "right", "D")
        p += [f] + bx + [h]
        moves.append(dmove(f"drawer_{k + 1}", [f["id"]] + ids(bx) + [h["id"]], 380))
    fl = front(None, (842, 19, zc, W - 2, 463, zf), "flap")
    fh = hbar("k-flap", 1151, 400, zf, "right", "D")
    p += [fl, fh]
    moves.append(flap("flap", ["flap", "k-flap"]))
    for k, (x0, x1, hinge, hx) in enumerate(((2, 418, "left", 378), (422, 838, "right", 462), (842, 1258, "right", 882))):
        d = front(None, (x0, 467, zc, x1, 2015, zf), f"door-{k + 1}")
        h = hbar(f"k-door-{k + 1}", hx, 1250, zf, "up", "D")
        p += [d, h]
        moves.append(door(f"door_{k + 1}", [d["id"], h["id"]], hinge))
    p += feet((40, 730, W - 40), (40, B - 60))
    return dump("luna-1-13", [1460, 600, 2017], p, moves)


# ------------------------------------------------------------------------------------------ 1.21 тумба
def m121():
    W, B = 800, 400
    zc, zf = B - 16, B
    wx = 560
    p = lower_box(W, zc)
    p += [P(None, (0, 465, 4, 16, 1001, zc), "w-side-l"), acc(P(None, (wx - 16, 465, 4, wx, 1001, zc), "w-side-r")),
          P(None, (0, 1001, 4, wx, 1017, zc), "w-top"), P(None, (16.5, 725, 6, wx - 16.5, 741, zc - 4), "w-shelf")]
    p += column(wx, W, zc, 985, 1)
    p += [back(None, (2, FT + 1, 0, W - 2, 465, 4), "back-low", mat="white"),
          back(None, (2, 465, 0, wx - 2, 1015, 4), "back-w", mat="white"),
          acc(back(None, (wx - 2, 465, 0, W - 2, 983, 4), "back-c"))]
    moves = []
    for k, (y0, y1) in enumerate(((19, 239), (243, 463))):
        f = front(None, (2, y0, zc, W - 2, y1, zf), f"dr-{k + 1}")
        bx = drawer_box(k + 1, ("dr-sl", "dr-sr", "dr-b", "dr-bot"), 29, W - 29, y0 + 30, 150, zc - 350, zc, hb=150,
                        bottom=(W - 62, 350, 4), under=True)
        for q in bx:
            q.pop("n", None)
        h = hbar(f"k-dr-{k + 1}", W / 2, (y0 + y1) / 2 + 40, zf, "right", "D")
        p += [f] + bx + [h]
        moves.append(dmove(f"drawer_{k + 1}", [f["id"]] + ids(bx) + [h["id"]], 300))
    d = front(None, (2, 467, zc, wx - 2, 1015, zf), "door")
    h = hbar("k-door", wx - 40, 790, zf, "up", "D")
    p += [d, h]
    moves.append(door("door", ["door", "k-door"], "left"))
    p += feet((40, W - 40), (40, B - 60))
    return dump("luna-1-21", [800, 400, 1017], p, moves)


# ------------------------------------------------------------------------------------------ 1.71 полка
def m171():
    """A wall cabinet 780 with a lift-up flap (gas struts), an open «Оникс» cube 220 beside it, lower by 60."""
    p = [P(None, (0, 0, 4, 780, 16, 234), "bottom"), P(None, (0, 384, 4, 780, 400, 234), "top"),
         P(None, (0, 16, 4, 16, 384, 234), "side-l"), P(None, (764, 16, 4, 780, 384, 234), "side-r"),
         P(None, (16.5, 192, 6, 763.5, 208, 230), "shelf"),
         back(None, (2, 2, 0, 778, 398, 4), "back", mat="white"),
         acc(P(None, (780, 0, 4, 1000, 16, 250), "cube-bottom")), acc(P(None, (780, 324, 4, 1000, 340, 250), "cube-top")),
         acc(P(None, (984, 16, 4, 1000, 324, 250), "cube-side")),
         acc(back(None, (782, 2, 0, 998, 338, 4), "cube-back"))]
    f = front(None, (2, 2, 234, 778, 398, 250), "flap")
    h = hbar("k-flap", 390, 40, 250, "right", "D")
    p += [f, h]
    return dump("luna-1-71", [1000, 250, 400], p, [flap("flap", ["flap", "k-flap"], "top", 95)])


# ------------------------------------------------------------------------------------------ 2.61 стеллаж
def m261():
    """Open shelving 942 × 251 × 802 in «Оникс» (the site photo): a partition at a third, one shelf left, two right."""
    p = [acc(P(None, (0, FT, 4, 942, 33, 251), "bottom")), acc(P(None, (0, 786, 4, 942, 802, 251), "top")),
         acc(P(None, (0, 33, 4, 16, 786, 249), "side-l")), acc(P(None, (926, 33, 4, 942, 786, 249), "side-r")),
         acc(P(None, (316, 33, 4, 332, 786, 249), "part")),
         acc(P(None, (16.5, 401, 6, 315.5, 417, 249), "shelf-l")),
         acc(P(None, (332.5, 271, 6, 925.5, 287, 249), "shelf-r1")), acc(P(None, (332.5, 530, 6, 925.5, 546, 249), "shelf-r2")),
         acc(back(None, (2, FT + 1, 0, 940, 800, 4), "back"))]
    p += feet((40, 471, 902), (40, 210))
    return dump("luna-2-61", [942, 251, 802], p, [])


# ------------------------------------------------------------------------------------------ 2.51 стол
def m251():
    """Desk 1210 × 618 × 760: a leg panel on the left, the top 0…960, a pedestal 480 wide on the right: two drawers,
    above them a door under the top and an open «Оникс» box whose top is level with the desk top."""
    zc, zf = 602, 618
    px0 = 730
    p = [P(None, (0, 744, 0, 960, 760, 618), "top"), P(None, (40, 0, 0, 56, 744, 600), "leg"),
         P(None, (56, 404, 20, px0, 744, 36), "modesty"),
         P(None, (px0, FT, 2, 1210, 33, zc), "p-bottom"), P(None, (px0, 33, 2, px0 + 16, 744, zc), "p-side-l"),
         P(None, (1194, 33, 2, 1210, 500, zc), "p-side-r"), P(None, (px0 + 16, 484, 2, 1194, 500, zc), "p-shelf"),
         P(None, (944, 500, 2, 960, 744, zc), "p-part"),
         acc(P(None, (960, 500, 2, 1210, 516, zc), "box-bottom")), acc(P(None, (960, 744, 2, 1210, 760, zc), "box-top")),
         acc(P(None, (1194, 516, 2, 1210, 744, zc), "box-side")),
         back(None, (px0 + 2, FT + 1, 0, 1208, 500, 2), "p-back", mat="white"),
         acc(back(None, (962, 500, 0, 1208, 758, 2), "box-back"))]
    moves = []
    for k, (y0, y1) in enumerate(((19, 256), (260, 498))):
        f = front(None, (px0 + 2, y0, zc, 1208, y1, zf), f"dr-{k + 1}")
        bx = drawer_box(k + 1, ("dr-sl", "dr-sr", "dr-b", "dr-bot"), px0 + 29, 1181, y0 + 30, 150, zc - 450, zc, hb=150,
                        bottom=(1181 - px0 - 58, 450, 4), under=True)
        for q in bx:
            q.pop("n", None)
        h = hbar(f"k-dr-{k + 1}", (px0 + 1210) / 2, (y0 + y1) / 2 + 40, zf, "right", "D")
        p += [f] + bx + [h]
        moves.append(dmove(f"drawer_{k + 1}", [f["id"]] + ids(bx) + [h["id"]], 380))
    d = front(None, (px0 + 2, 502, zc, 958, 742, zf), "door")
    h = hbar("k-door", 925, 622, zf, "up", "D", length=128)
    p += [d, h]
    moves.append(door("door", ["door", "k-door"], "left"))
    p += feet((px0 + 40, 1170), (40, 560))
    return dump("luna-2-51", [1210, 618, 760], p, moves)


# ------------------------------------------------------------------------------------------ 1.01 кровать 1-09
def m101():
    """Daybed 2044 × 942 × 802 (sleeping place 900 × 2000): two end panels with the top back corner rounded, a back
    panel on the wall, the front rail over two drawers with arched grips, a ЛДСП base on cleats, the mattress."""
    L, B, Hh = 2044, 942, 802
    end = rounded_rect_path(0, 0, B, Hh, {"tl": 160})       # side plane (a = z, b = y): the back top corner
    p = [P(None, (0, 0, 0, 16, Hh, B), "end-l", shape="path", outline=end),
         P(None, (L - 16, 0, 0, L, Hh, B), "end-r", shape="path", outline=end),
         P(None, (16, 250, 0, L - 16, 700, 16), "back-panel"),
         P(None, (16, 250, B - 16, L - 16, 380, B), "front-rail"),
         P(None, (16, 0, 16, L - 16, 60, 32), "plinth-back"),
         P(None, (16, 330, 16, 32, 346, B - 16), "cleat-l"), P(None, (L - 32, 330, 16, L - 16, 346, B - 16), "cleat-r"),
         P(None, (32, 330, 16, L - 32, 346, 40), "cleat-b"), P(None, (32, 330, B - 40, L - 32, 346, B - 16), "cleat-f"),
         P(None, (1014, 60, 32, 1030, 330, B - 16), "mid-rail"),
         P(None, (16, 346, 16, L - 16, 362, B - 16), "base"),
         {"id": "mattress", "kind": "mattress", "box": [22, 362, 20, 2022, 542, 920]}]
    moves = []
    for k, (x0, x1) in enumerate(((18, 1012), (1032, L - 18))):
        f = front(None, (x0, 30, B - 16, x1, 246, B), f"dr-{k + 1}", shape="path",
                  outline=notch_top(x0, 30, x1, 246, (x0 + x1) / 2, 260, 40, 110))
        bx = drawer_box(k + 1, ("dr-sl", "dr-sr", "dr-b", "dr-bot"), x0 + 20, x1 - 20, 40, 170, B - 16 - 700, B - 16,
                        hb=170, bottom=(x1 - x0 - 40, 700, 4), under=True)
        for q in bx:
            q.pop("n", None)
        p += [f] + bx
        moves.append(dmove(f"drawer_{k + 1}", [f["id"]] + ids(bx), 450))
    return dump("luna-1-01", [2044, 942, 802], p, moves)


# ------------------------------------------------------------------------------------------ cut lists (Заславль tables)
def cutlists():
    src = "{} p. 3 (table picture «№, наименование, a×b, n»; ЛДСП 16, ДВП 4 — the thickness is not printed)"
    rows = {
        "luna-1-31": ("П7.049.1.31", "LUNA_049-301.pdf", [
            (1, 782, 380, 16, 1, "Стенка горизонтальная верхняя"), (2, 800, 380, 16, 1, "Стенка горизонтальная нижняя"),
            (3, 806, 380, 16, 1, "Стенка боковая левая"), (4, 824, 380, 16, 1, "Стенка боковая правая"),
            (5, 728, 378, 16, 1, "Стенка боковая правая внешняя"), (6, 250, 378, 16, 1, "Стенка горизонтальная верхняя малая"),
            (7, 232, 378, 16, 2, "Полка"), (8, 248, 378, 16, 1, "Стенка горизонтальная нижняя малая"),
            (9, 764, 200, 16, 1, "Царга"), (10, 792, 207, 16, 4, "Стенка ящика передняя"),
            (11, 350, 144, 16, 4, "Стенка боковая ящика левая"), (12, 350, 144, 16, 4, "Стенка боковая ящика правая"),
            (13, 706, 144, 16, 4, "Стенка ящика задняя"), (14, 350, 90, 16, 4, "Брусок продольный"),
            (15, 734, 355, 4, 4, "Дно ящика (ДВП)"), (16, 792, 416, 4, 2, "Стенка задняя (ДВП)")]),
        "luna-1-72": ("П7.049.1.72", "LUNA_049-702.pdf", [
            (1, 942, 250, 16, 1, "Стенка горизонтальная верхняя"), (2, 942, 250, 16, 1, "Стенка горизонтальная нижняя"),
            (3, 568, 248, 16, 1, "Стенка боковая левая"), (4, 568, 248, 16, 1, "Перегородка"),
            (5, 568, 248, 16, 1, "Стенка боковая правая"), (6, 300, 248, 16, 1, "Полка малая"),
            (7, 592, 248, 16, 2, "Полка большая")]),
        "luna-2-62": ("П7.049.2.62", "P049-602.pdf", [
            (1, 350, 300, 16, 1, "Стенка горизонт. верхняя"), (2, 298, 1888, 16, 2, "Стенка боковая"),
            (3, 350, 300, 16, 1, "Стенка горизонт. нижняя"), (4, 316, 296, 16, 5, "Полка"),
            (5, 344, 637, 4, 3, "Стенка задняя (ДВП)")]),
        "luna-1-09": ("П7.049.1.09", "P049-1401.pdf", [(1, 900, 400, 16, 1, "Стенка вертикальная")]),
        "luna-2-52": ("П7.049.2.52", "LUNA_049-502.pdf", [
            (1, 1200, 700, 16, 1, "Крышка"), (2, 744, 620, 16, 1, "Стенка боковая стола левая"),
            (3, 744, 620, 16, 1, "Стенка боковая тумбы левая"), (4, 744, 620, 16, 1, "Стенка боковая тумбы правая"),
            (5, 722, 350, 16, 1, "Царга"), (6, 534, 350, 16, 1, "Стенка задняя"), (7, 620, 350, 16, 2, "Полка"),
            (8, 378, 186, 16, 3, "Стенка ящика передняя"), (9, 500, 120, 16, 3, "Стенка боковая ящика левая"),
            (10, 500, 120, 16, 3, "Стенка боковая ящика правая"), (11, 292, 120, 16, 3, "Стенка ящика задняя"),
            (12, 505, 322, 4, 3, "Дно ящика (ДВП)")]),
        "luna-2-53": ("П7.049.2.53", "P049-503.pdf", [
            (1, 2200, 700, 16, 1, "Крышка"), (2, 734, 600, 16, 1, "Стенка боковая левая"),
            (3, 734, 600, 16, 1, "Стенка боковая правая"), (4, 634, 350, 16, 2, "Царга"),
            (5, 702, 600, 16, 1, "Стенка боковая внутр. левая"), (6, 702, 600, 16, 1, "Стенка боковая внутр. правая"),
            (7, 702, 600, 16, 1, "Перегородка"), (8, 802, 600, 16, 1, "Стенка горизонт. нижняя"),
            (9, 600, 375, 16, 1, "Стенка горизонт. левая"), (10, 600, 375, 16, 1, "Стенка горизонт. правая"),
            (11, 375, 80, 16, 2, "Брусок"), (12, 396, 205, 4, 2, "Стенка задняя (ДВП)"),
            (13, 507, 396, 4, 2, "Стенка задняя (ДВП)"), (14, 396, 170, 16, 3, "Стенка передняя ящика левая"),
            (15, 396, 170, 16, 3, "Стенка передняя ящика правая"), (16, 500, 128, 16, 6, "Стенка боковая ящика левая"),
            (17, 500, 128, 16, 6, "Стенка боковая ящика правая"), (18, 317, 128, 16, 6, "Стенка задняя ящика"),
            (19, 505, 345, 4, 6, "Дно ящика (ДВП)")]),
        "luna-1-14": ("П7.049.1.14", "P049-104.pdf", [
            (1, 1000, 1000, 16, 1, "Стенка горизонтальная верхняя"), (2, 378, 2000, 16, 1, "Стенка боковая левая"),
            (3, 378, 2000, 16, 1, "Стенка боковая правая"), (4, 1000, 1000, 16, 1, "Стенка горизонтальная нижняя"),
            (5, 378, 1968, 16, 1, "Перегородка левая"), (6, 300, 1968, 16, 1, "Перегородка правая"),
            (7, 584, 1968, 16, 1, "Стенка задняя"), (8, 666, 584, 16, 2, "Полка большая"), (9, 666, 280, 16, 1, "Царга"),
            (10, 300, 376, 16, 5, "Полка левая"), (11, 298, 354, 16, 1, "Брусок"), (12, 400, 298, 16, 4, "Полка правая"),
            (13, 80, 400, 16, 1, "Брусок"), (14, 437, 1996, None, 2, "Дверь (16)"),
            (15, 321, 637, 4, 2, "Стенка задняя (ДВП)"), (16, 321, 718, 4, 1, "Стенка задняя (ДВП)"),
            (17, 687, 371, 4, 2, "Стенка задняя (ДВП)"), (18, 687, 623, 4, 2, "Стенка задняя (ДВП)"),
            (19, 428, 341, 4, 1, "Стенка задняя (ДВП)"), (20, 428, 670, 4, 2, "Стенка задняя (ДВП)"),
            (21, 428, 308, 4, 1, "Стенка задняя (ДВП)"), (22, 380, 150, 16, 2, "Стенка передняя ящика"),
            (23, 250, 134, 16, 2, "Стенка боковая ящика левая"), (24, 250, 134, 16, 2, "Стенка боковая ящика правая"),
            (25, 326, 134, 16, 2, "Стенка задняя ящика"), (26, 356, 255, 4, 2, "Дно ящика (ДВП)")]),
    }
    for did, (code, pdf, rr) in rows.items():
        write_cutlist(did, code, rr, src.format(pdf),
                      "The doors 14 are swept slabs on the diagonal (moulding), counted by covers." if did == "luna-1-14" else None)


PROFILES = {"luna-door-16x1996": {"name": "Дверь углового шкафа «Луна» 16 × 1996 (плита, протянутая по диагонали)",
                                  "pts": [[-8, 0], [-8, 1996], [8, 1996], [8, 0]]}}
FIN = [{"id": "luna-sosna-oniks", "name": "Сосна рандерс 540 SWN / Оникс 817 TM", "body": "door_enamel_whitey#c7c8c3",
        "swatch": "#c7c8c3", "roles": {"accent": "door_enamel_whitey#726e65", "white": "door_enamel_whitey#eeeeec"}}]
COLL = [{"id": "luna", "name": "Луна", "brand": "Пинскдрев", "finishes": ["luna-sosna-oniks"], "metal": "black",
         "note": "Каталог «Корпусная мебель ч. II» 2025, с. 121–122 (разворот 238–241); ПУП «Пинскдрев-Заславль». "
                 "7 модулей по инструкциям, 8 по фото сайта. ЛДСП 16 «Сосна рандерс», открытые стеллажи и секции "
                 "«Оникс»; опоры 50×17; задние стенки ДВП накладные; фасады накладные; ручки — тёмные прямоугольные "
                 "скобы ≈160."}]
MODELS = [
    ("1-11", "П7.049.1.11", "Шкаф комбинированный «Луна»", "storage", [800, 600, 2017], None, "по фото, без инструкции; секция-стеллаж «Оникс», откидной нижний фасад"),
    ("1-12", "П7.049.1.12", "Шкаф комбинированный «Луна»", "storage", [600, 400, 2017], None, "по фото, без инструкции"),
    ("1-13", "П7.049.1.13", "Шкаф комбинированный «Луна»", "storage", [1460, 600, 2017], None, "по фото, без инструкции"),
    ("1-14", "П7.049.1.14", "Шкаф угловой «Луна»", "storage", [1020, 1020, 2017], "P049-104.pdf", "в угол, стены сзади и слева"),
    ("1-21", "П7.049.1.21", "Тумба «Луна»", "kids", [800, 400, 1017], None, "по фото, без инструкции"),
    ("1-31", "П7.049.1.31", "Комод «Луна»", "kids", [1048, 400, 857], "LUNA_049-301.pdf", None),
    ("1-71", "П7.049.1.71", "Полка «Луна»", "kids", [1000, 250, 400], None, "по фото, без инструкции; подъёмная дверца"),
    ("1-72", "П7.049.1.72", "Полка «Луна»", "kids", [942, 250, 600], "LUNA_049-702.pdf", None),
    ("1-01", "П7.049.1.01", "Кровать 1-09 «Луна»", "kids", [2044, 942, 802], None, "по фото, без инструкции; спальное место 900×2000"),
    ("1-09", "П7.049.1.09", "Брусок ограждение «Луна»", "kids", [900, 16, 400], "P049-1401.pdf", "крепится к кровати П7.049.1.01"),
    ("2-51", "П7.049.2.51", "Стол «Луна»", "office", [1210, 618, 760], None, "по фото, без инструкции"),
    ("2-52", "П7.049.2.52", "Стол «Луна»", "office", [1200, 700, 760], "LUNA_049-502.pdf", None),
    ("2-53", "П7.049.2.53", "Стол «Луна»", "office", [2200, 700, 750], "P049-503.pdf", "на двоих"),
    ("2-61", "П7.049.2.61", "Стеллаж «Луна»", "kids", [942, 251, 802], None, "по фото, без инструкции; «Оникс»"),
    ("2-62", "П7.049.2.62", "Стеллаж «Луна»", "kids", [350, 304, 1937], "P049-602.pdf", "«Оникс»"),
]


def models():
    out = []
    for tail, code, name, cat, size, is_, note in MODELS:
        m = {"id": f"luna-{tail}", "code": code, "name": name, "collection": "luna", "category": cat, "size": size}
        if is_:
            m["is"] = is_
        m["page"] = 122
        if tail in ("1-71", "1-72"):
            m["mount"] = "wall"
        if note:
            m["note"] = note
        out.append(m)
    return out


if __name__ == "__main__":
    for f in (m131, m172, m262, m109, m252, m253, m114, m111, m112, m113, m121, m171, m261, m251, m101):
        print(f())
    cutlists()
    write_fragment(SLUG, FIN, COLL, models(), PROFILES)
