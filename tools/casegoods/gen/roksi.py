"""«Рокси» (П6.948): case pieces on V-shaped metal legs, oak (ЛДСП 16) carcass with a full top and bottom spanning the
sides, fronts МДФ 19.5 (the 0.01 door 19) laid over the sides' front edges between the top and the bottom, half of them
reeded (vertical ribs, pitch 16), black edge pulls «СА-1» on the fronts' top edges, backs ХДФ 3.5 in grooves.

Instructed: 0.01, 0.02, 0.03, 0.04, 1.01, 1.02, 1.03, 1.05 (cut lists; corrected / completed ones in gen/cutlists/).
By catalogue: 1.04 (bedside), 0.11 / 0.12 / 0.13 (dining tables on hairpin legs).

    python3 tools/casegoods/gen/roksi.py
"""
from common import dump

FZ = 404.0          # the top's / the fronts' face (catalogue depth B)
SD = 383.0          # sides' depth
F0 = 384.5          # the back face of a 19.5 front
REED = {"type": "fluted", "dir": "y", "pitch": 16, "depth": 3, "flute": "reed", "gap": 2}


# ------------------------------------------------------------------------------------------------ helpers
def carcass(w, hs, legh=100.0, sd=SD, td=FZ, bottom_t=16.0, n=("1", "2", "3", "4")):
    """Top and bottom span the full width and depth, the sides stand between them."""
    y1 = legh + bottom_t
    return [
        {"n": n[0], "box": [0, y1, 0, 16, y1 + hs, sd]},
        {"n": n[1], "box": [w - 16, y1, 0, w, y1 + hs, sd]},
        {"n": n[2], "box": [0, y1 + hs, 0, w, y1 + hs + 16, td]},
        {"n": n[3], "box": [0, legh, 0, w, y1, td]},
    ]


def back(n, x0, y0, x1, y1, pid=None):
    p = {"n": n, "kind": "back", "box": [x0, y0, 6, x1, y1, 9.5]}
    if pid:
        p["id"] = pid
    return p


def front(n, x0, y0, x1, y1, reed=False, pid=None, t=19.5):
    p = {"n": n, "kind": "front", "box": [x0, y0, FZ - t, x1, y1, FZ]}
    if pid:
        p["id"] = pid
    if reed:
        p["face"] = dict(REED)
    return p


def pull(pid, x, y_top, z=FZ, length=128, letter="s"):
    """Edge pull «СА-1» on a front's top edge: a black lip over the face (the engine's flat bar)."""
    return {"id": pid, "kind": "handle", "model": "bar", "mat": "metal", "at": [x, y_top - 8], "dir": "right", "d": length,
            "band": 14, "t": 6, "standoff": 2, "z": z, "covers": [letter]}


def vpull(pid, x, y, z=FZ, length=160, letter="s"):
    """The same pull set on a door's free edge, upright (the wardrobe)."""
    return {"id": pid, "kind": "handle", "model": "bar", "mat": "metal", "at": [x, y], "dir": "up", "d": length,
            "band": 14, "t": 6, "standoff": 2, "z": z, "covers": [letter]}


def drawer(tag, ns, x0, x1, y0, h, zf=F0, depth=352.0, back_t=16.0):
    """Box between x0..x1 (outer): sides full height and depth, the back (h − 14) standing on the bottom, the bottom
    (depth + 5) in grooves of the sides and 5 mm into the front's groove. ns = (left side, right side, back, bottom)."""
    zb = zf - depth
    return [
        {"n": ns[0], "id": f"{ns[0]}-{tag}", "box": [x0, y0, zb, x0 + 16, y0 + h, zf]},
        {"n": ns[1], "id": f"{ns[1]}-{tag}", "box": [x1 - 16, y0, zb, x1, y0 + h, zf]},
        {"n": ns[2], "id": f"{ns[2]}-{tag}", "box": [x0 + 16, y0 + 14, zb, x1 - 16, y0 + h, zb + back_t]},
        {"n": ns[3], "id": f"{ns[3]}-{tag}", "kind": "back", "box": [x0 + 11, y0 + 10, zb, x1 - 11, y0 + 13.5, zf + 5]},
    ]


def box_in(opening, outer):
    """Outer x0, x1 of a drawer box centred in an opening (a0, a1)."""
    c = (opening[0] + opening[1]) / 2
    return c - outer / 2, c + outer / 2


def vleg(tag, x, z, s, h=100.0, letter="h"):
    """Metal leg «Опора метал.»: a plate under the bottom and two black rods meeting in a V at the floor. s = +1 for a
    leg at the left end (its outer rod nearly upright at x), −1 at the right end, 0 for a symmetric middle leg."""
    if s:
        a, b, tip = x, x + s * 110, x + s * 12
    else:
        a, b, tip = x - 45, x + 45, x
    lo, hi = min(a, b), max(a, b)
    return [
        {"id": f"{letter}-{tag}", "kind": "panel", "mat": "metal", "edge": 0.5, "box": [lo - 8, h - 4, z - 18, hi + 8, h, z + 18], "covers": [letter]},
        {"id": f"{letter}-{tag}-r1", "kind": "rod", "mat": "metal", "from": [a, h - 4, z], "to": [tip, 8, z], "d": 10},
        {"id": f"{letter}-{tag}-r2", "kind": "rod", "mat": "metal", "from": [b, h - 4, z], "to": [tip, 8, z], "d": 10},
        {"id": f"{letter}-{tag}-f", "kind": "tube", "mat": "metal", "box": [tip - 6, 0, z - 6, tip + 6, 14, z + 6]},
    ]


def legs(w, zs=(35.0, 348.0), h=100.0, middle=(), letter="h"):
    out = []
    for i, z in enumerate(zs):
        out += vleg(f"l{i + 1}", 30, z, 1, h, letter)
        out += vleg(f"r{i + 1}", w - 30, z, -1, h, letter)
    for j, (x, z) in enumerate(middle):
        out += vleg(f"m{j + 1}", x, z, 0, h, letter)
    return out


def dmove(name, front_id, box, handle_id, travel=300):
    return {"type": "drawer", "name": name, "parts": [front_id] + [q["id"] for q in box] + [handle_id], "travel": travel}


# ------------------------------------------------------------------------------------------------ 0.01 шкаф
def m001():
    """Tall cabinet 616×404×2030: one door (19) with a glazed notch at its free edge, reeded on that half."""
    W = 616
    p = carcass(W, 1898)                       # bottom 100..116, sides 116..2014, top 2014..2030
    p += [
        {"n": "5", "id": "5-1", "box": [18, 367, 12, 598, 383, 365]},
        {"n": "8", "id": "8-1", "box": [17, 634, 10, 599, 650, 365]},
        {"n": "6", "id": "6-1", "kind": "glass", "box": [19, 922, 12, 597, 928, 362]},
        {"n": "6", "id": "6-2", "kind": "glass", "box": [19, 1200, 12, 597, 1206, 362]},
        {"n": "8", "id": "8-2", "box": [17, 1479, 10, 599, 1495, 365]},
        {"n": "5", "id": "5-2", "box": [18, 1754, 12, 598, 1770, 365]},
        back("9", 12, 112, 604, 642, "9-1"),
        back("10", 12, 642, 604, 1487),
        back("9", 12, 1487, 604, 2017, "9-2"),
    ]
    # the door: the notch 300 × 860 at the free edge (x 313..613) is filled by the glass 11; the free half is reeded
    x0, x1, y0, y1, n0, n1 = 3, 613, 118, 2012, 634, 1494
    lines = []
    for k in range(19):
        x = 313 + 8 + 16 * k
        if x < x1 - 4:
            lines += [[x, y0, x, n0], [x, n1, x, y1]]
    p.append({"n": "7", "kind": "front", "box": [x0, y0, 385, x1, y1, FZ], "shape": "path",
              "outline": f"M {x0} {y0} L {x1} {y0} L {x1} {n0} L 313 {n0} L 313 {n1} L {x1} {n1} L {x1} {y1} L {x0} {y1} Z",
              "face": {"type": "grooves", "w": 4, "depth": 2.5, "flute": "u", "lines": lines}})
    p.append({"n": "11", "kind": "glass", "mat": "glass", "box": [313, n0, 390, 613, n1, 393.5]})
    p.append({"id": "i", "kind": "handle", "model": "bar", "mat": "metal", "at": [596, 1070], "dir": "up", "d": 64,
              "band": 12, "t": 7, "standoff": 3, "z": 393.5, "covers": ["i"]})
    p += legs(W)
    moves = [{"type": "door", "name": "door", "parts": ["7", "11", "i"], "hinge": "left", "angle": 105}]
    return dump("roksi-0-01", [616, 404, 2030], p, moves)


# ------------------------------------------------------------------------------------------------ 0.02 тумба ТВ
def m002():
    W = 1506
    p = carcass(W, 488)                        # sides 116..604
    p += [
        {"n": "7", "box": [17, 379, 10, 1489, 395, 375]},
        {"n": "5", "box": [693.25, 395, 10, 709.25, 604, 375]},
        {"n": "6", "box": [801.75, 116, 10, 807.75, 379, 375]},
        back("14", 10, 389, 699, 610.5),
        back("13", 703, 389, 1495, 610.5),
        back("16", 10, 110, 802, 385.5),
        back("15", 802, 110, 1491, 385.5),
    ]
    moves = []
    # front n, x0, x1, y0, y1, reeded, opening, box outer, box h, parts (sides l/r, back, bottom), back t, tag, front t
    # (the table gives 11.1 as 16 thick and its box back 11.4 as 6 thick, unlike the others: built as listed)
    spec = [
        ("8.1", 3, 699.5, 389, 600, False, (16, 693.25), 650.5, 164, ("8.2", "8.3", "8.4", "8.5"), 16, "a", 19.5),
        ("9.1", 703, 1503, 389, 600, True, (709.25, 1490), 753.5, 164, ("9.2", "9.3", "9.4", "9.5"), 16, "a", 19.5),
        ("11.1", 3, 803, 118, 385, True, (16, 801.75), 753.5, 218, ("11.2", "11.3", "11.4", "9.5"), 6, "b", 16),
        ("12.1", 806.5, 1503, 118, 385, False, (807.75, 1490), 650.5, 218, ("12.2", "12.3", "12.4", "8.5"), 16, "b", 19.5),
    ]
    for fn, x0, x1, y0, y1, reed, op, outer, h, ns, bt, tag, ft in spec:
        p.append(front(fn, x0, y0, x1, y1, reed, t=ft))
        bx0, bx1 = box_in(op, outer)
        box = drawer(tag, ns, bx0, bx1, y0 + 23, h, zf=FZ - ft, back_t=bt)
        p += box
        hid = f"s-{fn}"
        p.append(pull(hid, (x0 + x1) / 2, y1))
        moves.append(dmove(f"drawer_{fn}", fn, box, hid))
    p += legs(W, middle=[(804.75, 200)])   # under the lower partition 6
    return dump("roksi-0-02", [1506, 404, 620], p, moves)


# ------------------------------------------------------------------------------------------------ 0.03 шкаф 4Д
def m003():
    W = 846
    p = carcass(W, 1368)                       # sides 116..1484
    p += [
        {"n": "12", "box": [17, 792, 10, 829, 808, 373]},
        {"n": "5", "box": [415, 808, 10, 431, 1484, 373]},
        {"n": "6", "box": [431, 116, 10, 447, 792, 373]},
        {"n": "7", "id": "7-1", "box": [17.5, 1138, 12, 413.5, 1154, 367]},
        {"n": "7", "id": "7-2", "box": [433, 1138, 12, 829, 1154, 367]},
        {"n": "7.1", "box": [17.5, 446, 12, 429.5, 462, 367]},
        {"n": "7.2", "box": [448.5, 446, 12, 828.5, 462, 367]},
        back("13", 10, 801.5, 420, 1490.5, "13-1"),
        back("13", 426, 801.5, 836, 1490.5, "13-2"),
        back("16", 10, 110.5, 437, 797.5),
        back("15", 441, 110.5, 835, 797.5),
        front("8", 3, 801, 503, 1480, True),
        pull("i-1", 439, 1480, letter="i"),
        front("9", 507, 801, 843, 1480, pid="9-1"),
        front("9", 3, 118, 339, 797, pid="9-2"),
        front("8.1", 343, 118, 843, 797, True),
        pull("i-2", 407, 797, letter="i"),
    ]
    p += legs(W)
    moves = [{"type": "door", "name": "door_top_left", "parts": ["8", "i-1"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_top_right", "parts": ["9-1"], "hinge": "right", "angle": 105},
             {"type": "door", "name": "door_bottom_left", "parts": ["9-2"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_bottom_right", "parts": ["8.1", "i-2"], "hinge": "right", "angle": 105}]
    return dump("roksi-0-03", [846, 404, 1500], p, moves)


# ------------------------------------------------------------------------------------------------ 0.04 тумба-комод
def m004():
    W = 1590
    p = carcass(W, 948)                        # sides 116..1064
    p += [
        {"n": "15", "box": [17, 802, 10, 1573, 818, 377]},
        {"n": "5", "box": [697, 818, 10, 713, 1064, 377]},
        {"n": "6", "id": "6-1", "box": [441.5, 116, 10, 447.5, 802, 377]},
        {"n": "6.1", "box": [881, 116, 10, 897, 802, 377]},
        {"n": "6", "id": "6-2", "box": [1232.5, 116, 10, 1238.5, 802, 377]},
        {"n": "7.2", "box": [19.75, 451, 12, 437.75, 467, 369]},
        {"n": "7.1", "box": [451.25, 451, 12, 877.25, 467, 369]},
        {"n": "7", "id": "7-1", "box": [900.75, 451, 12, 1228.75, 467, 369]},
        {"n": "7", "id": "7-2", "box": [1242.25, 451, 12, 1570.25, 467, 369]},
        back("21", 10, 110, 442, 808),
        back("20", 442, 110, 885, 808),
        back("19", 889, 110, 1232, 808, "19-1"),
        back("19", 1232, 110, 1575, 808, "19-2"),
        back("17", 10, 812, 702, 1070),
        back("16", 708, 812, 1580, 1070),
        front("11", 3, 118, 503, 808, True),
        pull("s-11", 439, 808),
        front("12", 507, 118, 887, 808, True),
        front("13", 891, 118, 1187, 808),
        front("14", 1191, 118, 1587, 808),
        pull("s-14", 1255, 808),
    ]
    moves = [{"type": "door", "name": "door_1", "parts": ["11", "s-11"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_2", "parts": ["12"], "hinge": "right", "angle": 105},
             {"type": "door", "name": "door_3", "parts": ["13"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_4", "parts": ["14", "s-14"], "hinge": "right", "angle": 105}]
    for fn, x0, x1, reed, op, outer, ns in [("9.1", 3, 703, False, (16, 697), 654, ("9.2", "9.3", "9.4", "9.5")),
                                            ("10.1", 707, 1587, True, (713, 1574), 834, ("9.2", "9.3", "10.4", "10.5"))]:
        p.append(front(fn, x0, 812, x1, 1060, reed))
        bx0, bx1 = box_in(op, outer)
        box = drawer(fn, ns, bx0, bx1, 836, 200)
        p += box
        hid = f"s-{fn}"
        p.append(pull(hid, (x0 + x1) / 2, 1060))
        moves.append(dmove(f"drawer_{fn}", fn, box, hid))
    p += legs(W, middle=[(795, 200)])
    return dump("roksi-0-04", [1590, 404, 1080], p, moves)


# ------------------------------------------------------------------------------------------------ 1.01 шкаф 3Д
def m101():
    W, D, LH = 1508, 569.5, 91.0
    FZW = 590.0
    p = carcass(W, 2184, legh=LH, sd=D, td=FZW, bottom_t=25)   # bottom 91..116 (25), sides 116..2300, top 2300..2316
    p += [
        {"n": "5", "box": [494, 116, 0, 510, 2300, 553.5]},
        {"n": "6", "id": "6-1", "box": [16, 473, 0, 494, 479, 553.5]},
        {"n": "6", "id": "6-2", "box": [16, 1935, 0, 494, 1941, 553.5]},
        {"n": "7", "id": "7-1", "box": [17.5, 831, 12, 492.5, 847, 552]},
        {"n": "7", "id": "7-2", "box": [17.5, 1199, 12, 492.5, 1215, 552]},
        {"n": "7", "id": "7-3", "box": [17.5, 1567, 12, 492.5, 1583, 552]},
        {"n": "9", "box": [511, 581, 0, 1491, 597, 553.5]},
        {"n": "8", "box": [511, 2000, 0, 1491, 2016, 553.5]},
        {"n": "10", "box": [997, 597, 441.5, 1013, 2000, 569.5]},
        back("17", 10, 110, 500, 476),
        back("15", 10, 476, 500, 1938),
        back("16", 10, 1938, 500, 2300),
        back("20", 504, 110, 1496, 587),
        back("18", 504, 590, 999, 2007, "18-1"),
        back("18", 999, 590, 1494, 2007, "18-2"),
        back("19", 504, 2008, 1496, 2304),
        {"id": "p1", "kind": "tube", "mat": "chrome", "box": [515, 1935, 270, 1487, 1960, 295], "covers": ["p1"]},
    ]
    fz0 = FZW - 19.5
    doors = [("11", 3, 118, 501, 2298, "left"), ("12", 505, 591, 1003, 2298, "left"), ("13", 1007, 591, 1505, 2298, "right")]
    for n, x0, y0, x1, y1, hinge in doors:
        p.append({"n": n, "kind": "front", "box": [x0, y0, fz0, x1, y1, FZW]})
    p.append(vpull("s-11", 491, 1190, z=FZW))
    p.append(vpull("s-13", 1017, 1190, z=FZW))
    moves = [{"type": "door", "name": "door_left", "parts": ["11", "s-11"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_middle", "parts": ["12"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_right", "parts": ["13", "s-13"], "hinge": "right", "angle": 105}]
    bx0, bx1 = box_in((510, 1492), 954)
    for tag, y0, y1 in [("1", 118, 348), ("2", 354.5, 584.5)]:
        fid = f"14.1-{tag}"
        p.append({"n": "14.1", "id": fid, "kind": "front", "box": [505, y0, fz0, 1505, y1, FZW], "face": dict(REED)})
        box = drawer(tag, ("14.2", "14.3", "14.4", "14.5"), bx0, bx1, y0 + 19, 192, zf=fz0, depth=500)
        p += box
        hid = f"s-d{tag}"
        p.append(pull(hid, 1005, y1, z=FZW))
        moves.append(dmove(f"drawer_{tag}", fid, box, hid, 400))
    p += legs(W, zs=(35.0, 530.0), h=LH, middle=[(754, 35.0), (754, 530.0)], letter="r")
    return dump("roksi-1-01", [1508, 590, 2316], p, moves)


# ------------------------------------------------------------------------------------------------ 1.02 комод
def m102():
    W = 1006
    p = carcass(W, 948)                        # sides 116..1064
    p += [
        back("7", 6, 106, 1000, 590, "7-1"),
        back("7", 6, 590, 1000, 1074, "7-2"),
        {"n": "8", "box": [17, 526, 10, 989, 654, 26]},
    ]
    # the catalogue (p. 13 photo, p. 14 cut-out) shows plain / reeded / plain / reeded from the top; the instruction's
    # sketch has them the other way round (reeded on top): built as the catalogue shows it, 6.1 = the reeded fronts
    moves = []
    bx0, bx1 = box_in((16, 990), 946)
    for k, (n, y0, reed) in enumerate([("6.1", 120, True), ("5.1", 356, False), ("6.1", 592, True), ("5.1", 828, False)]):
        tag = str(k + 1)
        fid = f"{n}-{tag}"
        p.append(front(n, 3, y0, 1003, y0 + 230, reed, pid=fid))
        box = drawer(tag, ("5.2", "5.3", "5.4", "5.5"), bx0, bx1, y0 + 19, 192)
        p += box
        hid = f"s-{tag}"
        p.append(pull(hid, 503, y0 + 230))
        moves.append(dmove(f"drawer_{tag}", fid, box, hid))
    p += legs(W, letter="r")
    return dump("roksi-1-02", [1006, 404, 1080], p, moves)


# ------------------------------------------------------------------------------------------------ 1.03 зеркало
def m103():
    p = [
        {"n": "1", "shape": "circle", "mat": "front", "edge": 2, "box": [0, 0, 0, 700, 700, 16]},
        {"n": "2", "kind": "mirror", "shape": "circle", "box": [60, 60, 17, 640, 640, 21]},
    ]
    return dump("roksi-1-03", [700, 21, 700], p, [])


# ------------------------------------------------------------------------------------------------ 1.04 тумба прикроватная (по каталогу)
def m104():
    W = 506
    p = carcass(W, 375, n=("side-l", "side-r", "top", "bottom"))   # sides 116..491
    p = [dict(q, id=q["n"]) for q in p]
    for q in p:
        del q["n"]
    p += [
        {"id": "shelf", "box": [17, 297, 10, 489, 313, 375]},
        {"id": "back-1", "kind": "back", "box": [10, 110, 6, 496, 303, 9.5]},
        {"id": "back-2", "kind": "back", "box": [10, 307, 6, 496, 497, 9.5]},
    ]
    moves = []
    bx0, bx1 = box_in((16, 490), 446)
    for tag, y0, y1, reed, h in [("bottom", 118, 303, True, 136), ("top", 307, 487, False, 130)]:
        fid = f"front-{tag}"
        p.append({"id": fid, "kind": "front", "box": [3, y0, F0, 503, y1, FZ], **({"face": dict(REED)} if reed else {})})
        box = drawer(tag, ("dside-l", "dside-r", "dback", "dbottom"), bx0, bx1, y0 + 20, h)
        p += box
        hid = f"s-{tag}"
        p.append(pull(hid, 253, y1))
        moves.append(dmove(f"drawer_{tag}", fid, box, hid))
    p += legs(W)
    return dump("roksi-1-04", [506, 404, 507], p, moves)


# ------------------------------------------------------------------------------------------------ 1.05 кровать 2-16
def m105():
    W, L = 1680, 2060
    p = [
        {"n": "1", "box": [0, 0, 0, W, 950, 25]},
        {"n": "2.1", "kind": "front", "box": [0, 780, 25, W, 950, 44], "face": dict(REED)},
        {"n": "2", "kind": "front", "box": [0, 520, 25, W, 720, 44]},
        {"n": "3", "box": [10, 110, 25, 35, 310, 2035]},
        {"n": "3.1", "box": [1645, 110, 25, 1670, 310, 2035]},
        {"n": "4", "box": [10, 110, 2035, 1670, 310, L]},
        # the metal base m (2000×1600) with its slats, the foot V legs and two middle legs; the head end hangs on brackets
        {"id": "m-rail-l", "kind": "panel", "mat": "metal", "box": [40, 250, 30, 70, 290, 2030], "covers": ["m"]},
        {"id": "m-rail-r", "kind": "panel", "mat": "metal", "box": [1610, 250, 30, 1640, 290, 2030]},
        {"id": "m-rail-h", "kind": "panel", "mat": "metal", "box": [70, 250, 30, 1610, 290, 60]},
        {"id": "m-rail-f", "kind": "panel", "mat": "metal", "box": [70, 250, 2000, 1610, 290, 2030]},
        {"id": "m-rail-c", "kind": "panel", "mat": "metal", "box": [825, 250, 60, 855, 290, 2000]},
        {"id": "m-leg-1", "kind": "tube", "mat": "metal", "box": [827.5, 0, 700, 852.5, 250, 725]},
        {"id": "m-leg-2", "kind": "tube", "mat": "metal", "box": [827.5, 0, 1350, 852.5, 250, 1375]},
        {"id": "mattress", "kind": "mattress", "box": [40, 298, 30, 1640, 498, 2030]},
    ]
    for i in range(26):
        z = 72 + i * 74
        p.append({"id": f"m-slat-l{i + 1}", "kind": "panel", "mat": "#c9a877", "box": [70, 290, z, 825, 298, z + 53]})
        p.append({"id": f"m-slat-r{i + 1}", "kind": "panel", "mat": "#c9a877", "box": [855, 290, z, 1610, 298, z + 53]})
    # V legs of the base at the foot corners
    for tag, x, s in [("l", 50, 1), ("r", W - 50, -1)]:
        p += vleg(f"foot-{tag}", x, 1990, s, h=250, letter="m")
    return dump("roksi-1-05", [1680, 2060, 950], p, [])


# ------------------------------------------------------------------------------------------------ столы (по каталогу)
def table(did, L, B, H=735, top_t=25):
    """A top on four hairpin legs (two black rods Ø10 in a V along the length, a plate under the top)."""
    p = [{"id": "top", "box": [0, H - top_t, 0, L, H, B], "radius": 3, "grain": "x"}]
    y = H - top_t
    k = 0
    for x in (70, L - 70):
        for z in (50, B - 50):
            k += 1
            p += [
                {"id": f"leg-{k}", "kind": "panel", "mat": "metal", "edge": 0.5, "box": [x - 60, y - 4, z - 30, x + 60, y, z + 30]},
                {"id": f"leg-{k}-r1", "kind": "rod", "mat": "metal", "from": [x - 50, y - 4, z], "to": [x, 10, z], "d": 10},
                {"id": f"leg-{k}-r2", "kind": "rod", "mat": "metal", "from": [x + 50, y - 4, z], "to": [x, 10, z], "d": 10},
                {"id": f"leg-{k}-f", "kind": "tube", "mat": "metal", "box": [x - 6, 0, z - 6, x + 6, 16, z + 6]},
            ]
    return dump(did, [L, B, H], p, [])


if __name__ == "__main__":
    for f in (m001, m002, m003, m004, m101, m102, m103, m104, m105):
        print(f())
    print(table("roksi-0-11", 1500, 900))
    print(table("roksi-0-12", 1350, 900))
    print(table("roksi-0-13", 1100, 800))
