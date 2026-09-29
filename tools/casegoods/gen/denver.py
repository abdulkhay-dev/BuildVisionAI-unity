"""«Денвер» (Пинскдрев, П6.639): living room (0.xx) and bedroom (1.xx) modules.

Construction (from the instructions П6.639.0.01/0.02/0.03/0.13, 1.02/1.03/1.04/1.05):
  * carcass ЛДСП 16. The bottom (the panel the legs screw into) runs the full size L × 432; the sides (depth 428) stand on
    it 2 mm in from its ends and edges (so every panel between them is L − 36 long). Shelf 0.01 has a full top as well;
    the other cabinets have an inset top (depth 388; bedside 405) between the sides with a 100 mm rail behind it.
  * backs ХДФ 3.5 in grooves of the sides (and top / bottom), one piece per section, the joints behind the partitions.
  * partitions 384 deep, 15 mm short of the top (the cut lists: side − 31), standing on the bottom in front of the rail.
  * fronts ЛДСП 16 in the Кантри / Канзас oak decor, inset between the sides flush with their front edges (1 mm gaps),
    covering the inset top's edge and 6 mm of each partition; no handles (push-to-open hinges and runners).
  * legs: solid wood, tapered and splayed outward to the sides (cut-list blanks 80×80×130 / 86×60×130), felt pads.
Coordinates: x from the left, y up from the floor, z from the wall (back) to the front; mm.
"""
import json
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))

D = 432          # full depth (bottom, full top)
SZ0, SZ1 = 2, 430          # sides: 2 mm in from the back and front edges of the bottom
BZ0, BZ1 = 5.5, 9          # back (ХДФ 3.5) in grooves 3.5 mm from the sides' back edges
RZ0, RZ1 = 9, 25           # rail (царга) behind the inset top
FZ0, FZ1 = 414, 430        # fronts, flush with the sides
LEG_H = 130
FRONT = {"kind": "front", "grain": "x"}


def P(n, box, **kw):
    p = {"n": n} if n is not None else {}
    p.update(kw)
    p["box"] = [round(v, 1) for v in box]
    return p


def front(n, box, pid=None, grain="x"):
    p = {"n": n} if n is not None else {}
    if pid:
        p["id"] = pid
    p.update({"kind": "front", "grain": grain, "box": [round(v, 1) for v in box]})
    return p


def back(n, box, pid=None):
    p = {"n": n} if n is not None else {}
    if pid:
        p["id"] = pid
    p.update({"kind": "back", "box": [round(v, 1) for v in box]})
    return p


def leg(n, pid, x, z, sx, sz, d=58, d2=30, pad="r", h=LEG_H):
    """A tapered wooden leg under the bottom: square rod from its top face at (x, h, z), splayed by (sx, sz) at the floor,
    on a felt pad (2 mm)."""
    bx, bz = x + sx, z + sz
    p = {"id": pid, "kind": "rod", "mat": "legs", "section": "square", "from": [x, h, z], "to": [bx, 2, bz], "d": d, "d2": d2}
    if n is not None:
        p = {"n": n, **p}
    felt = {"id": f"{pad}-{pid}", "kind": "panel", "mat": "door_enamel_whitey#8a8378", "shape": "circle", "edge": 0.5,
            "box": [bx - 14, 0, bz - 14, bx + 14, 2, bz + 14], "covers": [pad]}
    return [p, felt]


def legs(n, w, middle=False, d=66, pad="r", inset=62, zin=55, splay=32, zsplay=10):
    out = []
    k = 0
    for x, sx in ((inset, -splay), (w - inset, splay)):
        for z, sz in ((D - zin, zsplay), (zin, -zsplay)):
            k += 1
            out += leg(n, f"leg-{k}", x, z, sx, sz, d=d, pad=pad)
    if middle:
        out += leg(n, "leg-m", w / 2, D - zin, 0, 0, d=55, d2=34, pad=pad)
    return out


def drawer(tag, x0, x1, y0, h, fx0, fx1, fy0, fy1, fn, ns, divider=None, depth=350, back_h=None, fz0=FZ0):
    """Front fn over [fx0, fx1] × [fy0, fy1]; box x0..x1 (outer), sides h high and `depth` deep behind the front, back
    between the sides standing on the bottom (h − 14), bottom 3.5 in grooves 10 mm up (5 mm into the sides and the front),
    optional middle divider. ns = (side_l, side_r, back, bottom[, divider]) cut-list numbers (None = not listed)."""
    z0 = fz0 - depth
    bh = back_h if back_h is not None else h - 14
    parts = [front(fn, [fx0, fy0, fz0, fx1, fy1, FZ1], pid=f"{fn}-{tag}" if fn else f"front-{tag}")]
    ids = [parts[0]["id"]]

    def add(n, box, kind="panel", sfx=""):
        pid = f"{n}-{tag}" if n else f"box{sfx}-{tag}"
        p = {"n": n} if n else {}
        p["id"] = pid
        if kind != "panel":
            p["kind"] = kind
        p["box"] = [round(v, 1) for v in box]
        parts.append(p)
        ids.append(pid)

    add(ns[0], [x0, y0, z0, x0 + 16, y0 + h, fz0], sfx="-sl")
    add(ns[1], [x1 - 16, y0, z0, x1, y0 + h, fz0], sfx="-sr")
    add(ns[2], [x0 + 16, y0 + 14, z0, x1 - 16, y0 + 14 + bh, z0 + 16], sfx="-bk")
    add(ns[3], [x0 + 11, y0 + 10, z0, x1 - 11, y0 + 13.5, fz0 + 5], kind="back", sfx="-bt")
    if divider is not None:
        xm = (x0 + x1) / 2
        add(ns[4], [xm - 8, y0 + 14, z0 + 16, xm + 8, y0 + 14 + bh, fz0], sfx="-dv")
    return parts, {"type": "drawer", "name": f"drawer_{tag}", "parts": ids, "travel": 300}


# ------------------------------------------------------------------------------------------------ living room (Кантри)
def m0_01():
    """Шкаф 816 × 432 × 2100: open shelving on the left, two doors and a niche on the right."""
    W, H = 816, 2100
    p = [
        P("5", [0, 130, 0, W, 146, D]),
        P("4", [0, 2084, 0, W, 2100, D]),
        P("1", [2, 146, SZ0, 18, 2084, SZ1]),
        P("2", [798, 146, SZ0, 814, 2084, SZ1]),
        P("3", [337, 146, BZ1, 353, 2084, BZ1 + 384]),
    ]
    # left column: four shelves splitting 146..2084 into five equal compartments (6 at the ends, 7 in the middle)
    for i, (n, y) in enumerate((("6", 521), ("7", 912), ("7", 1302), ("6", 1693))):
        p.append(P(n, [18, y, BZ1, 337, y + 16, BZ1 + 384], id=f"{n}-{i + 1}"))
    # right column: lower door, niche 942..1302, upper door; shelves 8 frame the niche, loose shelves 9 behind the doors
    p += [
        P("8", [353, 926, BZ1, 798, 942, BZ1 + 384], id="8-1"),
        P("8", [353, 1302, BZ1, 798, 1318, BZ1 + 384], id="8-2"),
        P("9", [354, 521, BZ1, 797, 537, BZ1 + 370], id="9-1"),
        P("9", [354, 1693, BZ1, 797, 1709, BZ1 + 370], id="9-2"),
        back("13", [14, 142, BZ0, 346, 1310, BZ1]),
        back("12", [14, 1310, BZ0, 346, 2088, BZ1]),
        back("15", [346, 142, BZ0, 802, 1310, BZ1]),
        back("14", [346, 1310, BZ0, 802, 2088, BZ1]),
        front("10", [347, 147, FZ0, 797, 942, FZ1], pid="10-1"),
        front("10", [347, 1288, FZ0, 797, 2083, FZ1], pid="10-2"),
    ]
    p += legs("11", W)
    moves = [{"type": "door", "name": "door_bottom", "parts": ["10-1"], "hinge": "right", "angle": 105},
             {"type": "door", "name": "door_top", "parts": ["10-2"], "hinge": "right", "angle": 105}]
    return dump("denver-0-01", [W, D, H], p, moves)


def inset_carcass(W, H, top_d=388, top_n="5", rail_n="7", bottom_n="6", sides=("1", "2")):
    """Bottom full, sides on it, inset top between the sides in front of the 100 mm back rail."""
    y1 = H
    return [
        P(bottom_n, [0, 130, 0, W, 146, D]),
        P(sides[0], [2, 146, SZ0, 18, y1, SZ1]),
        P(sides[1], [W - 18, 146, SZ0, W - 2, y1, SZ1]),
        P(top_n, [18, y1 - 16, RZ1, W - 18, y1, RZ1 + top_d]),
        P(rail_n, [18, y1 - 116, RZ0, W - 18, y1 - 16, RZ1]),
    ]


def m0_02():
    """Тумба 1396 × 432 × 598 (ТВ): two doors, open middle section with a shelf."""
    W, H = 1396, 598
    p = inset_carcass(W, H)
    p += [
        P("3", [463, 146, RZ1, 479, 567, RZ1 + 384]),
        P("4", [917, 146, RZ1, 933, 567, RZ1 + 384]),
        P("8", [480.5, 344, RZ1, 915.5, 360, RZ1 + 370]),
        back("11", [15, 147, BZ0, 473, 579, BZ1], pid="11-1"),
        back("12", [473, 147, BZ0, 923, 579, BZ1]),
        back("11", [923, 147, BZ0, 1381, 579, BZ1], pid="11-2"),
        front("9", [19, 147, FZ0, 469, 597, FZ1], pid="9-1"),
        front("9", [927, 147, FZ0, 1377, 597, FZ1], pid="9-2"),
    ]
    p += legs("10", W, middle=True)
    moves = [{"type": "door", "name": "door_left", "parts": ["9-1"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_right", "parts": ["9-2"], "hinge": "right", "angle": 105}]
    return dump("denver-0-02", [W, D, H], p, moves)


def m0_03():
    """Тумба 816 × 432 × 1350: a full-height door on the left; door, niche, door on the right."""
    W, H = 816, 1350
    p = inset_carcass(W, H, top_n="4", rail_n="6", bottom_n="5")
    p += [
        P("3", [337, 146, RZ1, 353, 1319, RZ1 + 384]),
        # left column behind the tall door: fixed shelf 7 in the middle, loose shelves 9
        P("9", [19, 431, RZ1, 336, 447, RZ1 + 370], id="9-1"),
        P("7", [18, 732, RZ1, 337, 748, RZ1 + 384]),
        P("9", [19, 1033, RZ1, 336, 1049, RZ1 + 370], id="9-2"),
        # right column: niche between the doors, framed by the shelves 8
        P("8", [353, 581, RZ1, 798, 597, RZ1 + 384], id="8-1"),
        P("8", [353, 910, RZ1, 798, 926, RZ1 + 384], id="8-2"),
        back("13", [14, 147, BZ0, 345, 738, BZ1], pid="13-1"),
        back("13", [14, 738, BZ0, 345, 1329, BZ1], pid="13-2"),
        back("16", [345, 147, BZ0, 802, 580, BZ1]),
        back("15", [345, 580, BZ0, 802, 926, BZ1]),
        back("14", [345, 926, BZ0, 802, 1326, BZ1]),
        front("10", [19, 147, FZ0, 342, 1349, FZ1]),
        front("11", [347, 147, FZ0, 797, 597, FZ1], pid="11-1"),
        front("11", [347, 899, FZ0, 797, 1349, FZ1], pid="11-2"),
    ]
    p += legs("12", W)
    moves = [{"type": "door", "name": "door_left", "parts": ["10"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_bottom", "parts": ["11-1"], "hinge": "right", "angle": 105},
             {"type": "door", "name": "door_top", "parts": ["11-2"], "hinge": "right", "angle": 105}]
    return dump("denver-0-03", [W, D, H], p, moves)


def m0_10():
    """Тумба 1396 × 432 × 1152 (by catalogue): tall door left; niche over a wide drawer in the middle; drawer, wide drawer
    and a door on the right; open shelving under the wide drawer. Built like 0.02 / 0.03."""
    W, H = 1396, 1152
    p = [
        {"id": "bottom", "box": [0, 130, 0, W, 146, D]},
        {"id": "side-l", "box": [2, 146, SZ0, 18, H, SZ1]},
        {"id": "side-r", "box": [W - 18, 146, SZ0, W - 2, H, SZ1]},
        {"id": "top", "box": [18, H - 16, RZ1, W - 18, H, RZ1 + 388]},
        {"id": "rail", "box": [18, H - 116, RZ0, W - 18, H - 16, RZ1]},
        {"id": "part-l", "box": [463, 146, RZ1, 479, H - 31, RZ1 + 384]},
        # the wide drawer runs over the middle and right sections: two dividers carry it, the right partition is split
        {"id": "div-low", "box": [479, 733, RZ1, W - 18, 749, RZ1 + 384]},
        {"id": "div-high", "box": [479, 949, RZ1, W - 18, 965, RZ1 + 384]},
        {"id": "part-r-low", "box": [917, 146, RZ1, 933, 733, RZ1 + 384]},
        {"id": "part-r-high", "box": [917, 965, RZ1, 933, H - 16, RZ1 + 384]},
        # shelves: left column (loose, behind the door), middle (open), right (behind the lower door)
        {"id": "shelf-l1", "box": [19, 465, RZ1, 462, 481, RZ1 + 370]},
        {"id": "shelf-l2", "box": [19, 800, RZ1, 462, 816, RZ1 + 370]},
        {"id": "shelf-m", "box": [480.5, 433, RZ1, 915.5, 449, RZ1 + 370]},
        {"id": "shelf-r", "box": [934, 433, RZ1, 1377, 449, RZ1 + 370]},
        back(None, [15, 148, BZ0, 471, 1134, BZ1], pid="back-l"),
        back(None, [471, 148, BZ0, 925, 1134, BZ1], pid="back-m"),
        back(None, [925, 148, BZ0, 1381, 1134, BZ1], pid="back-r"),
        front(None, [19, 147, FZ0, 469, 1151, FZ1], pid="door-l"),
        front(None, [927, 147, FZ0, 1377, 747, FZ1], pid="door-r"),
    ]
    moves = [{"type": "door", "name": "door_left", "parts": ["door-l"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_right", "parts": ["door-r"], "hinge": "right", "angle": 105}]
    parts, mv = drawer("wide", 492, W - 31, 779, 130, 474, 1377, 749, 949, None, (None, None, None, None))
    p += parts
    moves.append(mv)
    parts, mv = drawer("top", 946, W - 31, 985, 130, 927, 1377, 951, 1151, None, (None, None, None, None))
    p += parts
    moves.append(mv)
    p += legs(None, W, middle=True)
    return dump("denver-0-10", [W, D, H], p, moves)


def m0_13():
    """Полка навесная 1396 × 250 × 336: top and bottom over three uprights, open ends; a lift-up flap (hinges on the top,
    push-to-open latch); backs ЛДСП 16 in the open sections, ХДФ behind the flap."""
    W, H, DD = 1396, 336, 250
    p = [
        P("5", [0, 0, 0, W, 16, DD]),
        P("4", [0, 320, 0, W, 336, DD]),
        P("1", [199, 16, 0, 215, 320, 248]),
        P("2", [964, 16, 0, 980, 320, 248]),
        P("3", [1181, 16, 16, 1197, 320, 248]),
        P("6", [0, 16, 0, 199, 320, 16]),
        P("7", [980, 16, 0, 1395, 320, 16]),
        back("9", [210.5, 11, 5.5, 968.5, 325, 9]),
        front("8", [217.5, 18, 234, 961.5, 318, DD]),
        {"id": "L-1", "kind": "panel", "mat": "black", "edge": 0.5, "box": [215, 280, 9, 231, 316, 21], "covers": ["L"]},
        {"id": "L-2", "kind": "panel", "mat": "black", "edge": 0.5, "box": [948, 280, 9, 964, 316, 21], "covers": ["L"]},
    ]
    moves = [{"type": "flap", "name": "flap", "parts": ["8"], "hinge": "top", "angle": 85}]
    return dump("denver-0-13", [W, DD, H], p, moves)


# ------------------------------------------------------------------------------------------------ bedroom (Канзас)
def m1_02():
    """Комод 1396 × 432 × 956: two columns of three drawers (210 over 296 over 296), push-to-open runners."""
    W, H = 1396, 956
    p = inset_carcass(W, H, top_n="4", rail_n="6", bottom_n="5")
    p += [
        P("3", [690, 146, RZ1, 706, 925, RZ1 + 379]),
        back("11", [15, 148, BZ0, 699, 937, BZ1], pid="11-1"),
        back("11", [699, 148, BZ0, 1383, 937, BZ1], pid="11-2"),
    ]
    moves = []
    cols = ((20, 693, 31, 677, "l"), (703, 1376, 719, 1365, "r"))
    rows = ((744, 954, "small", "t"), (446, 742, "big", "m"), (148, 444, "big", "b"))
    for fx0, fx1, x0, x1, c in cols:
        for fy0, fy1, kind, r in rows:
            if kind == "small":
                fn = "7" if c == "l" else "9"
                parts, mv = drawer(r + c, x0, x1, fy0 + 40, 130, fx0, fx1, fy0, fy1, fn,
                                   ("7.1", "7.2", "7.4", "7.5", "7.3"), divider=True)
            else:
                fn = "8" if c == "l" else "10"
                parts, mv = drawer(r + c, x0, x1, fy0 + 48, 200, fx0, fx1, fy0, fy1, fn, ("8.1", "8.2", "8.3", "8.4"))
            p += parts
            moves.append(mv)
    p += legs("12", W, middle=True, pad="h4")
    return dump("denver-1-02", [W, D, H], p, moves)


def m1_03():
    """Зеркало 1096 × 168 × 763 (catalogue L1126): mirror on the carcass-colour panel 1, oak panel 2 with two shelves."""
    p = [
        P("1", [0, 0, 2, 796, 763, 18]),
        P("2", [796, 0, 2, 1096, 763, 18], mat="front", grain="x"),
        {"id": "4", "kind": "mirror", "edge": 0.5, "box": [30, 30, 18, 772, 733, 22]},
        P("3", [821, 201, 18, 1071, 217, 168], mat="front", grain="x", id="3-1"),
        P("3", [821, 517, 18, 1071, 533, 168], mat="front", grain="x", id="3-2"),
        {"id": "g-1", "kind": "panel", "mat": "chrome", "edge": 0.5, "box": [300, 700, 0, 340, 720, 2], "covers": ["g"]},
        {"id": "g-2", "kind": "panel", "mat": "chrome", "edge": 0.5, "box": [880, 700, 0, 920, 720, 2], "covers": ["g"]},
    ]
    return dump("denver-1-03", [1096, 168, 763], p, [])


def m1_04():
    """Тумба прикроватная 454 × 432 × 450: niche over a drawer."""
    W, H = 454, 450
    p = [
        P("4", [0, 130, 0, W, 146, D]),
        P("1", [2, 146, SZ0, 18, H, SZ1]),
        P("2", [W - 18, 146, SZ0, W - 2, H, SZ1]),
        P("3", [18, H - 16, RZ1, W - 18, H, RZ1 + 405]),
        P("6", [18, H - 116, RZ0, W - 18, H - 16, RZ1]),
        P("5", [18, 279, RZ1, W - 18, 295, RZ1 + 385]),
        back("9", [13, 146, BZ0, 441, 429, BZ1]),
    ]
    parts, mv = drawer("1", 31, 423, 167, 100, 20, 434, 147, 295, "7", ("7.1", "7.2", "7.3", "7.4"), back_h=86)
    p += parts
    p += legs("8", W, inset=50, pad="h4", splay=28)
    return dump("denver-1-04", [W, D, H], p, [mv])


def bed(did, W, instructed):
    """Кровать: headboard 854 on 15 mm glides, oak panels, side rails 200 × 2010 × 25 inside the foot board, two splayed
    legs at the foot, metal frame (2000 × (W − 132)) with slats and a middle leg, mattress."""
    L, HB = 2060, 25
    n = (lambda k: k) if instructed else (lambda k: None)
    xl, xr = 36, W - 36                  # the foot board's ends = the rails' outer faces
    pw = (W - 150) / 2                   # oak panels: 50 mm margins and gap
    p = [
        P(n("1"), [0, 15, 0, W, 869, HB], **({} if instructed else {"id": "headboard"})),
        {**({"n": "4"} if instructed else {}), "id": "4-1", "kind": "panel", "mat": "front", "grain": "x",
         "box": [50, 454, HB, 50 + pw, 869, HB + 16]},
        {**({"n": "4"} if instructed else {}), "id": "4-2", "kind": "panel", "mat": "front", "grain": "x",
         "box": [W - 50 - pw, 454, HB, W - 50, 869, HB + 16]},
        P(n("3"), [xl, 130, HB, xl + 25, 330, HB + 2010], **({} if instructed else {"id": "rail-l"})),
        P(n("3.1"), [xr - 25, 130, HB, xr, 330, HB + 2010], **({} if instructed else {"id": "rail-r"})),
        P(n("2"), [xl, 130, L - 25, xr, 330, L], **({} if instructed else {"id": "foot"})),
    ]
    for i, x in enumerate((140, W - 140)):
        p.append({"id": f"h2-hb{i + 1}", "kind": "panel", "mat": "door_enamel_whitey#8a8378", "shape": "circle", "edge": 1,
                  "box": [x - 15, 0, 12.5 - 12, x + 15, 15, 12.5 + 12], "covers": ["h2"]})
    # legs 5: inside the foot corners, 70 mm above the rails' lower edge, splayed outward
    for i, (x, sx) in enumerate(((xl + 25 + 42.5, -40), (xr - 25 - 42.5, 40))):
        p += leg(n("5"), f"5-{i + 1}", x, L - 25 - 42.5, sx, 38, d=85, d2=40, pad="h2", h=200)
    # metal frame m: W − 132 wide, 2000 long, 5 mm inside the rails / headboard / foot
    fx0, fx1, fz0, fz1 = xl + 30, xr - 30, HB + 5, L - 30
    p += [
        {"id": "m-rail-l", "kind": "panel", "mat": "black", "box": [fx0, 262, fz0, fx0 + 30, 302, fz1], "covers": ["m"]},
        {"id": "m-rail-r", "kind": "panel", "mat": "black", "box": [fx1 - 30, 262, fz0, fx1, 302, fz1]},
        {"id": "m-end-h", "kind": "panel", "mat": "black", "box": [fx0 + 30, 262, fz0, fx1 - 30, 302, fz0 + 30]},
        {"id": "m-end-f", "kind": "panel", "mat": "black", "box": [fx0 + 30, 262, fz1 - 30, fx1 - 30, 302, fz1]},
    ]
    fields = [(fx0 + 30, fx1 - 30)]
    if W - 132 >= 1200:
        xm = W / 2
        p.append({"id": "m-beam", "kind": "panel", "mat": "black", "box": [xm - 15, 262, fz0 + 30, xm + 15, 302, fz1 - 30]})
        p.append({"id": "m-leg", "kind": "tube", "mat": "black", "box": [xm - 12, 2, 1030, xm + 12, 262, 1054]})
        p.append({"id": "h2-m", "kind": "panel", "mat": "door_enamel_whitey#8a8378", "shape": "circle", "edge": 0.5,
                  "box": [xm - 14, 0, 1028, xm + 14, 2, 1056], "covers": ["h2"]})
        fields = [(fx0 + 30, xm - 15), (xm + 15, fx1 - 30)]
    for f, (a, b) in enumerate(fields):
        for i in range(22):
            z = fz0 + 50 + i * 88
            p.append({"id": f"m-slat-{f + 1}-{i + 1}", "kind": "panel", "mat": "door_enamel_whitey#c9a877",
                      "box": [a, 290, z, b, 298, z + 53]})
    p.append({"id": "mattress", "kind": "mattress", "box": [fx0, 302, fz0, fx1, 502, fz1]})
    return dump(did, [W, L, 869], p, [])


def m1_01():
    """Шкаф для одежды 3Д 1839 × 618 × 2300 (by catalogue): sides to the floor, recessed plinth, partition at 630; left
    section of shelves behind a hinged door, right section (top shelf, two boxes, hanging rail) behind the «WingLine L»
    folding pair; three overlay leaves in the oak decor, vertical grain, no handles."""
    W, DD, H = 1839, 618, 2300
    C = 600                               # carcass depth; fronts 2 mm in front of it
    bz0, bz1 = 6, 9.5
    p = [
        {"id": "side-l", "box": [0, 0, 0, 16, H, C]},
        {"id": "side-r", "box": [W - 16, 0, 0, W, H, C]},
        {"id": "top", "box": [16, H - 16, 0, W - 16, H, C]},
        {"id": "bottom", "box": [16, 60, 0, W - 16, 76, C]},
        {"id": "plinth-f", "box": [16, 0, C - 60, W - 16, 60, C - 44]},
        {"id": "plinth-b", "box": [16, 0, 0, W - 16, 60, 16]},
        {"id": "partition", "box": [622, 76, bz1, 638, H - 16, C]},
        back(None, [10, 70, bz0, 630, H - 10, bz1], pid="back-l"),
        back(None, [630, 70, bz0, W - 10, H - 10, bz1], pid="back-r"),
    ]
    for i, y in enumerate((419, 781, 1162, 1524, 1905)):
        p.append({"id": f"shelf-l{i + 1}", "box": [16, y, bz1, 622, y + 16, C - 20]})
    p += [
        {"id": "shelf-top", "box": [638, 1946, bz1, W - 16, 1962, C - 20]},
        {"id": "box-div", "box": [1213, 1646, bz1, 1229, 1946, C - 20]},
        {"id": "shelf-box", "box": [638, 1630, bz1, W - 16, 1646, C - 20]},
        {"id": "rail-d", "kind": "tube", "mat": "chrome", "box": [642, 1540, 290, W - 20, 1560, 310], "covers": ["d"]},
        {"id": "wingline", "kind": "panel", "mat": "chrome", "edge": 0.5, "box": [642, H - 36, C - 40, W - 20, H - 16, C - 10],
         "covers": ["WingLine L"]},
    ]
    leaves = ((0, 611, "leaf-l"), (614, 1225, "leaf-m"), (1228, W, "leaf-r"))
    for x0, x1, pid in leaves:
        p.append(front(None, [x0, 12, C + 2, x1, H - 2, DD], pid=pid, grain="y"))
    moves = [
        {"type": "door", "name": "door_left", "parts": ["leaf-l"], "hinge": "left", "angle": 100},
        # WingLine L: the pair folds to the right; the outer leaf swings on the side, the inner one ends folded behind it
        {"type": "door", "name": "fold_outer", "parts": ["leaf-r"], "hinge": "right", "angle": 90},
        {"type": "door", "name": "fold_inner", "parts": ["leaf-m"], "hinge": "left", "axis": [1210.5, 1214.5], "angle": 90},
    ]
    return dump("denver-1-01", [W, DD, H], p, moves)


BEDS = (("denver-1-05", 1732, True), ("denver-1-15", 1032, False), ("denver-1-16", 1332, False),
        ("denver-1-17", 1532, False), ("denver-1-18", 1932, False))

if __name__ == "__main__":
    for f in (m0_01, m0_02, m0_03, m0_10, m0_13, m1_01, m1_02, m1_03, m1_04):
        print(f())
    for did, w, ins in BEDS:
        print(bed(did, w, ins))
