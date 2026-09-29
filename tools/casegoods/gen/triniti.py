"""Triniti (П6.114.*): a carcass of ЛДСП 16 «Гикори Кингстон» — top and bottom run the full width and depth, the sides
and partitions stand between them — on tapered square oak legs 130 (86 × 60 × 130, splayed sideways; the middle leg of
the wide pieces splays backwards). Backs ХДФ 3.5 in grooves 6 mm from the back, joined behind the partitions and fixed
shelves (стабилизаторы). The fronts sit INSIDE the carcass, flush with its front edge: МДФ 19 / 19.5 with milled
pyramids (100 × 100 cells) or plain 16.5 / 19; gaps 3 mm between fronts and at the sides, 2 mm top and bottom. They
overlay the partitions (the partitions stand behind the joints). Push-to-open everywhere: no handles.

z: back 6–9.5, partitions and fixed shelves 10 … B-35.5, fronts' back faces at B-19 / B-19.5, carcass front = B.
Run: python3 tools/casegoods/gen/triniti.py (writes the designs and the completed cut lists).
"""
import json
import math
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "reference", "triniti", "cutlists")
LEG = 130
T = 16
DIAMOND = {"type": "diamond", "cell": [100, 100], "depth": 8}


# ------------------------------------------------------------------------------------------------ helpers
def leg(pid, x_top, z0, splay, n=None, covers=None, h=LEG, mat="body"):
    """A tapered square oak leg: 60 × 60 at the top, 32 at the floor. splay: 'left' / 'right' (sideways, 40 mm out
    over 130: its box is 86 × 130 × 60 as the cut list gives it) or 'back' (a middle leg, 86 deep). x_top is the
    middle of its top; z0 the back of its box (for 'back': the back of its 86-mm box)."""
    if splay in ("left", "right"):
        s = -1 if splay == "left" else 1
        xb = x_top + s * 40
        box = [min(x_top - 30, xb - 16), 0, z0, max(x_top + 30, xb + 16), h, z0 + 60]
        a, b = [x_top, h, z0 + 30], [xb, 0, z0 + 30]
    else:
        box = [x_top - 30, 0, z0, x_top + 30, h, z0 + 86]
        a, b = [x_top, h, z0 + 56], [x_top, 0, z0 + 16]
    p = {"id": pid, "kind": "rod", "mat": mat, "section": "square", "from": a, "to": b, "d": 60, "d2": 32, "box": box}
    if n:
        p["n"] = n
    if covers:
        p["covers"] = covers
    return p


def corner_legs(w, b, n=None, covers=None):
    """Four legs under the corners: their tops 26 … 86 in from the sides, 15 mm in from the back and the front."""
    out = []
    for k, (x, sp, z) in enumerate([(56, "left", 15), (w - 56, "right", 15), (56, "left", b - 75), (w - 56, "right", b - 75)]):
        out.append(leg(f"{n or 'h'}-{k + 1}", x, z, sp, n=n, covers=covers))
    return out


def carcass(w, b, hs, n=("1", "2", "3", "4")):
    """Sides n[0], n[1] (hs tall) between the top n[2] and the bottom n[3] on the legs."""
    y0 = LEG + T
    sides = [{"n": n[0], "box": [0, y0, 0, T, y0 + hs, b]}, {"n": n[1], "box": [w - T, y0, 0, w, y0 + hs, b]}]
    if hs < b:                     # the cut list gives the height first: the grain runs up the side
        for p in sides:
            p["grain"] = "y"
    return sides + [
        {"n": n[2], "box": [0, y0 + hs, 0, w, y0 + hs + T, b]},
        {"n": n[3], "box": [0, LEG, 0, w, y0, b]},
    ]


def back(n, x0, x1, y0, y1, pid=None):
    p = {"n": n, "kind": "back", "box": [x0, y0, 6, x1, y1, 9.5]}
    if pid:
        p["id"] = pid
    return p


def front(n, x0, x1, y0, y1, zb, t, diamond=False, pid=None):
    """A front with its back face at zb, t thick."""
    p = {"n": n, "kind": "front", "box": [x0, y0, zb, x1, y1, zb + t]}
    if pid:
        p["id"] = pid
    if diamond:
        p["face"] = DIAMOND
    return p


def drawer(tag, ns, x0, x1, y0, h, z1, length, bottom_w, bottom_l=345):
    """Drawer box between x0..x1 (outer): sides ns[0], ns[1] (h × length), back ns[2] between them, bottom ns[3]
    (bottom_w × bottom_l) in grooves 10 mm up; the front (the facade) is screwed on at z1."""
    z0 = z1 - length
    xc = (x0 + x1) / 2
    return [
        {"n": ns[0], "id": f"{ns[0]}-{tag}", "box": [x0, y0, z0, x0 + T, y0 + h, z1]},
        {"n": ns[1], "id": f"{ns[1]}-{tag}", "box": [x1 - T, y0, z0, x1, y0 + h, z1]},
        {"n": ns[2], "id": f"{ns[2]}-{tag}", "box": [x0 + T, y0, z0, x1 - T, y0 + h, z0 + T]},
        {"n": ns[3], "id": f"{ns[3]}-{tag}", "kind": "back",
         "box": [xc - bottom_w / 2, y0 + 10, z1 - 2 - bottom_l, xc + bottom_w / 2, y0 + 13.5, z1 - 2]},
    ]


def ids(parts):
    return [p.get("id") or p["n"] for p in parts]


# ------------------------------------------------------------------------------------------------ living room
def m001():
    """Шкаф (универсальный) 638 × 435 × 2030: a door below, a glazed door above (two pyramid panels glued on a glass)."""
    W, B = 638, 435
    zb = B - 19
    p = carcass(W, B, 1868)
    p += [
        {"n": "5", "box": [17, 742, 10, 621, 758, 399.5]},                     # fixed shelf behind the back joint
        {"n": "7", "box": [18, 414, 16, 620, 430, 396]},
        {"n": "6", "id": "6-1", "kind": "glass", "box": [18, 1164, 16, 620, 1170, 396]},
        {"n": "6", "id": "6-2", "kind": "glass", "box": [18, 1582, 16, 620, 1588, 396]},
        back("11", 12, 626, 142, 750),
        back("10", 12, 626, 751, 2018),
    ]
    door = front("9", 19, 619, 148, 748, zb, 19)
    glazed = [front("8.1", 19, 619, 751, 951, zb, 19, True),
              {"n": "8.2", "kind": "glass", "box": [20, 941, zb - 4, 618, 1821, zb]},
              front("8", 19, 619, 1811, 2011, zb, 19, True)]
    p += [door] + glazed
    p += corner_legs(W, B, n="12")
    moves = [{"type": "door", "name": "door", "parts": ["9"], "hinge": "right", "angle": 105},
             {"type": "door", "name": "door_glass", "parts": ids(glazed), "hinge": "right", "angle": 105}]
    return dump("triniti-0-01", [W, B, 2030], p, moves)


def tv_like(did, H, hs, rows, doors_h, drawer_ys, shelves, ns):
    """Тумбы 0.02 (H 570) and 0.05 (H 975): 1644 wide; doors 500 left and right, drawers 600 in the middle between
    partitions at 512.5 and 1115.5."""
    W, B = 1644, 435
    zb = B - 19
    y1 = LEG + T + hs
    p = carcass(W, B, hs)
    p += [{"n": ns["p"][0], "box": [512.5, LEG + T, 10, 528.5, y1, 399.5]},
          {"n": ns["p"][1], "box": [1115.5, LEG + T, 10, 1131.5, y1, 399.5]}]
    for k, y in enumerate(shelves):
        p.append({"n": ns["shelf"], "id": f"{ns['shelf']}-{2 * k + 1}", "box": [18, y, 16, 511, y + 16, 396]})
        p.append({"n": ns["shelf"], "id": f"{ns['shelf']}-{2 * k + 2}", "box": [1133.5, y, 16, 1626.5, y + 16, 396]})
    bl, bm, br = ns["backs"]
    p += [back(bl, 12, 519, LEG + T - 5, y1 + 5), back(bm, 521.5, 1122.5, LEG + T - 5, y1 + 5),
          back(br, 1125, 1632, LEG + T - 5, y1 + 5)]
    dl = front(ns["door"], 19, 519, 148, 148 + doors_h, zb, 19, pid=f"{ns['door']}-left")
    dr = front(ns["door"], 1125, 1625, 148, 148 + doors_h, zb, 19, pid=f"{ns['door']}-right")
    p += [dl, dr]
    moves = [{"type": "door", "name": "door_left", "parts": [dl["id"]], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_right", "parts": [dr["id"]], "hinge": "right", "angle": 105}]
    for k, y in enumerate(drawer_ys):
        f = front(ns["dfront"], 522, 1122, y, y + 200, zb, 19, True, pid=f"{ns['dfront']}-{k + 1}")
        box = drawer(str(k + 1), ns["box"], 541.5, 1102.5, y + 16, 164, zb, 350, ns["bottom_w"])
        p += [f] + box
        moves.append({"type": "drawer", "name": f"drawer_{k + 1}", "parts": [f["id"]] + ids(box), "travel": 300})
    p += corner_legs(W, B, n=ns["leg"])
    p.append(leg(f"{ns['leg']}-5", 822, 174.5, "back", n=ns["leg"]))
    return dump(did, [W, B, H], p, moves)


def m002():
    return tv_like("triniti-0-02", 570, 408, None, 404, [148, 352], [342],
                   {"p": ("5", "6"), "shelf": "7", "backs": ("10", "11", "10.1"), "door": "9", "dfront": "8.1",
                    "box": ("8.2", "8.3", "8.4", "8.5"), "bottom_w": 539, "leg": "12"})


def m005():
    return tv_like("triniti-0-05", 975, 813, None, 809, [148, 351, 554, 757], [418, 691],
                   {"p": ("5", "6"), "shelf": "8", "backs": ("11", "12", "11.1"), "door": "10", "dfront": "9.1",
                    "box": ("9.2", "9.3", "9.4", "9.5"), "bottom_w": 537, "leg": "13"})


def m004():
    """Тумба 1242 × 435 × 1370: two columns, four pyramid doors 600 × 600, fixed shelves at the back joint."""
    W, B = 1242, 435
    zb = B - 19
    p = carcass(W, B, 1208)
    p += [
        {"n": "5", "box": [613, 146, 10, 629, 1354, 399.5]},
        {"n": "6", "box": [16.5, 742, 10, 612.5, 758, 399]},
        {"n": "7", "box": [629.5, 742, 10, 1225.5, 758, 399]},
        {"n": "8", "id": "8-1", "box": [17.5, 437, 16, 611.5, 453, 396]},
        {"n": "8", "id": "8-2", "box": [630.5, 437, 16, 1224.5, 453, 396]},
        {"n": "8", "id": "8-3", "box": [17.5, 1047, 16, 611.5, 1063, 396]},
        {"n": "8", "id": "8-4", "box": [630.5, 1047, 16, 1224.5, 1063, 396]},
        back("11", 12, 620, 142, 750, "11-left"), back("11", 622, 1230, 142, 750, "11-right"),
        back("10", 12, 620, 750, 1358), back("10.1", 622, 1230, 750, 1358),
    ]
    moves = []
    for k, (x0, y0, hinge) in enumerate([(19, 148, "left"), (623, 148, "right"), (19, 752, "left"), (623, 752, "right")]):
        d = front("9", x0, x0 + 600, y0, y0 + 600, zb, 19, True, pid=f"9-{k + 1}")
        p.append(d)
        moves.append({"type": "door", "name": f"door_{k + 1}", "parts": [d["id"]], "hinge": hinge, "angle": 105})
    p += corner_legs(W, B, n="12")
    p.append(leg("12-5", 621, 174.5, "back", n="12"))
    return dump("triniti-0-04", [W, B, 1370], p, moves)


# ------------------------------------------------------------------------------------------------ bedroom
def m101():
    """Шкаф для одежды 3Д 1544 × 590 × 2300: three columns (partitions full height behind the door joints); a drawer
    zone below and a mezzanine above behind pyramid fronts 300 × 500; three plain doors 1528 × 500 between them."""
    W, B = 1544, 590
    zb = B - 19.5
    L, M, R = (16, 512.5), (528.5, 1015.5), (1031.5, 1528)
    p = carcass(W, B, 2138)
    p += [{"n": "5", "box": [512.5, 146, 10, 528.5, 2284, 554.5]},
          {"n": "6", "box": [1015.5, 146, 10, 1031.5, 2284, 554.5]}]
    for k, y in enumerate([442, 1971]):
        p.append({"n": "7", "id": f"7-{2 * k + 1}", "box": [L[0] + 0.5, y, 10, L[1] - 0.5, y + T, 554.5]})
        p.append({"n": "7", "id": f"7-{2 * k + 2}", "box": [R[0] + 0.5, y, 10, R[1] - 0.5, y + T, 554.5]})
        p.append({"n": "8", "id": f"8-{k + 1}", "box": [M[0], y, 10, M[1], y + T, 554.5]})
    p += [{"n": "9", "id": "9-1", "box": [M[0], 826.5, 10, M[1], 842.5, 554.5]},
          {"n": "9", "id": "9-2", "box": [M[0], 1586.5, 10, M[1], 1602.5, 554.5]},
          {"n": "10", "box": [M[0] + 1, 1197, 16, M[1] - 1, 1213, 550]},
          {"n": "11", "box": [L[0] + 2, 795, 16, L[1] - 1.5, 811, 550]}]
    # hanger rails w1 (487): left and right at the top, right one more below (two-tier hanging)
    for k, (x0, y) in enumerate([(L[0] + 5, 1855), (R[0] + 4.5, 1855), (R[0] + 4.5, 1136)]):
        p.append({"id": f"w1-{k + 1}", "kind": "tube", "mat": "chrome", "box": [x0, y - 10, 272, x0 + 487, y + 10, 292], "covers": ["w1"]})
    p += [back("20", 12, 1532, 142, 450, "20-bottom"), back("20", 12, 1532, 1979, 2287, "20-top"),
          back("21", 12, 520, 450, 1979, "21-left"), back("21", 1024, 1532, 450, 1979, "21-right"),
          back("22", 522, 1023, 451, 834, "22-1"), back("23", 522, 1023, 835, 1594),
          back("22", 522, 1023, 1595, 1978, "22-2")]
    moves = []
    cols = [(19, "left", "15", "18", "12.1", L, ("12.4", "12.5", 437.5, 447)),
            (522, "left", "16", "19", "13.1", M, ("13.4", "13.5", 429, 439)),
            (1025, "right", "15", "18", "14.1", R, ("12.4", "12.5", 437.5, 447))]
    for k, (x0, hinge, nu, nd, nf, comp, (nb, nbot, _bw, bottom_w)) in enumerate(cols):
        tag = ["left", "middle", "right"][k]
        up = front(nu, x0, x0 + 500, 1982, 2282, zb, 19.5, True, pid=f"{nu}-{tag}")
        door = front(nd, x0, x0 + 500, 451, 1979, zb, 16.5, pid=f"{nd}-{tag}")
        df = front(nf, x0, x0 + 500, 148, 448, zb, 19.5, True)
        box = drawer(tag, ("12.2", "12.3", nb, nbot), comp[0] + 13.5 if k != 1 else comp[0] + 13,
                     comp[1] - 13.5 if k != 1 else comp[1] - 13, 165, 265, zb, 500, bottom_w, 495)
        p += [up, door, df] + box
        moves += [{"type": "door", "name": f"door_top_{tag}", "parts": [up["id"]], "hinge": hinge, "angle": 100},
                  {"type": "door", "name": f"door_{tag}", "parts": [door["id"]], "hinge": hinge, "angle": 100},
                  {"type": "drawer", "name": f"drawer_{tag}", "parts": [df["n"]] + ids(box), "travel": 400}]
    p += corner_legs(W, B, covers=["h"])
    p.append(leg("h-5", 520.5, 265, "left", covers=["h"]))
    p.append(leg("h-6", 1023.5, 265, "right", covers=["h"]))
    return dump("triniti-1-01", [W, B, 2300], p, moves)


def m102():
    """Комод 1038 × 435 × 975: four drawers 1000 wide, plain (16.5) and pyramid (19.5) fronts alternating; a back rail 5
    (128 × 1004) behind the joint of the two backs."""
    W, B = 1038, 435
    zb = B - 19.5
    p = carcass(W, B, 813)
    p += [{"n": "5", "box": [17, 488.5, 9.5, 1021, 616.5, 25.5]},
          back("9", 12, 1026, 142, 552), back("8", 12, 1026, 552, 962)]
    moves = []
    for k, (y, nf, t) in enumerate([(148, "7.1", 19.5), (351, "6.1", 16.5), (554, "7.1", 19.5), (757, "6.1", 16.5)]):
        f = front(nf, 19, 1019, y, y + 200, zb, t, nf == "7.1", pid=f"{nf}-{k + 1}")
        box = drawer(str(k + 1), ("6.2", "6.3", "6.4", "6.5"), 30, 1008, y + 16, 164, zb, 350, 956)
        p += [f] + box
        moves.append({"type": "drawer", "name": f"drawer_{k + 1}", "parts": [f["id"]] + ids(box), "travel": 300})
    p += corner_legs(W, B, covers=["h"])
    return dump("triniti-1-02", [W, B, 975], p, moves)


def m103():
    """Зеркало 1000 × 20 × 780 on the wall: a board 680 × 1000 (oak) with the mirror glued on, a pyramid strip 100 high
    joined to its top edge."""
    p = [{"n": "1", "box": [0, 0, 0, 1000, 680, 16]},
         {"n": "2", "kind": "mirror", "box": [20, 20, 16, 980, 680, 20]},
         {"n": "3", "kind": "front", "box": [0, 680, 0, 1000, 780, 19.5], "face": DIAMOND}]
    return dump("triniti-1-03", [1000, 20, 780], p, [])


def m104():
    """Тумба прикроватная 538 × 435 × 470: a shallow drawer (plain 100) over a deep one (pyramids 200)."""
    W, B = 538, 435
    zb = B - 19.5
    p = carcass(W, B, 308)
    p.append(back("8", 12, 526, 141, 459))
    lo = front("6.1", 19, 519, 148, 348, zb, 19.5, True)
    lob = drawer("low", ("6.2", "6.3", "6.4", "6.5"), 30, 508, 164, 164, zb, 350, 456)
    up = front("5.1", 19, 519, 352, 452, zb, 16.5)
    upb = drawer("up", ("5.2", "5.3", "5.4", "5.5"), 30, 508, 362, 80, zb, 350, 456)
    p += [up] + upb + [lo] + lob
    p += corner_legs(W, B, covers=["h"])
    moves = [{"type": "drawer", "name": "drawer_top", "parts": ["5.1"] + ids(upb), "travel": 300},
             {"type": "drawer", "name": "drawer_bottom", "parts": ["6.1"] + ids(lob), "travel": 300}]
    return dump("triniti-1-04", [W, B, 470], p, moves)


# the bed's headboard leans back: the panels 1.1, 6, 5 lie on the sloping front edges of the side panels 7 / ribs 8
SIN = 98.75 / 700          # 1.1 (700 long) rises from y 450 to the top 1143
COS = math.sqrt(1 - SIN * SIN)
HB_Z, HB_Y = 157, 450      # the foot of the slope: the top back edge of the lower panel 1 (z 157 … 182)


def slab_profile(s0, s1, n0, n1):
    """A board lying on the slope from s0 to s1 along it and n0 … n1 off it, as a moulding section (u = y - 450, v = z)."""
    def pt(s, n):
        return [round(s * COS + n * SIN, 2), round(HB_Z - s * SIN + n * COS, 2)]
    return [pt(s0, n0), pt(s0, n1), pt(s1, n1), pt(s1, n0)]


PROFILES = {
    "triniti-hb-1-1": {"name": "Изголовье «Тринити»: щит 1.1 (700 × 16) на наклоне 8°", "pts": slab_profile(0, 700, 0, 16)},
    "triniti-hb-6": {"name": "Изголовье «Тринити»: панель 6 (499 × 19.5) на щите 1.1", "pts": slab_profile(0, 499, 16, 35.5)},
    "triniti-hb-5": {"name": "Изголовье «Тринити»: планка 5 (200 × 16.5) с пирамидами на щите 1.1", "pts": slab_profile(500, 700, 16, 32.5)},
}


def m105():
    """Кровать 2-16 1700 × 2217 × 1143 (instruction; the catalogue text says B1800 H1193): a headboard box standing on
    the floor (sides 7 and ribs 8 cut to the slope, top 4, lower panel 1 25 thick, the sloping panel 1.1 faced with 6
    and the pyramid strip 5); side rails 3 / 3.1 and the foot 2 (25 thick) on two legs 200 at the foot; the flexible
    base 2000 × 1600 (k) inside."""
    W = 1700
    side = f"M 0 0 L {HB_Z} 0 L {HB_Z} {HB_Y} L {HB_Z - 677 * SIN / COS:.1f} 1127 L 0 1127 Z"
    p = []
    for n, pid, x in [("7", "7-left", 0), ("7", "7-right", W - T), ("8", "8-1", 560), ("8", "8-2", W - 560 - T)]:
        p.append({"n": n, "id": pid, "box": [x, 0, 0, x + T, 1127, HB_Z], "shape": "path", "outline": side})
    p += [
        {"n": "4", "box": [0, 1127, 0, W, 1143, 60]},
        {"n": "1", "mat": "front", "box": [0, 0, HB_Z, W, HB_Y, HB_Z + 25]},
        {"kind": "moulding", "profile": "triniti-hb-1-1", "mat": "front", "z": 0, "side": 1, "path": [[0, HB_Y], [W, HB_Y]], "covers": ["1.1"]},
        {"kind": "moulding", "profile": "triniti-hb-6", "mat": "front", "z": 0, "side": 1, "path": [[0, HB_Y], [W, HB_Y]], "covers": ["6"]},
        {"kind": "moulding", "profile": "triniti-hb-5", "mat": "front", "z": 0, "side": 1, "path": [[0, HB_Y], [W, HB_Y]], "covers": ["5"]},
        {"n": "3", "box": [20, 130, 182, 45, 330, 2192]},
        {"n": "3.1", "box": [W - 45, 130, 182, W - 20, 330, 2192]},
        {"n": "2", "box": [20, 130, 2192, W - 20, 330, 2217]},
        # the flexible base k (2000 × 1600): a black frame with beech slats, two middle legs; the mattress on it
        {"id": "k-frame-l", "kind": "panel", "mat": "black", "box": [50, 250, 187, 80, 290, 2187], "covers": ["k"]},
        {"id": "k-frame-r", "kind": "panel", "mat": "black", "box": [W - 80, 250, 187, W - 50, 290, 2187]},
        {"id": "k-frame-m", "kind": "panel", "mat": "black", "box": [835, 250, 187, 865, 290, 2187]},
        {"id": "k-leg-1", "kind": "tube", "mat": "black", "box": [837.5, 0, 800, 862.5, 250, 825]},
        {"id": "k-leg-2", "kind": "tube", "mat": "black", "box": [837.5, 0, 1500, 862.5, 250, 1525]},
        {"id": "mattress", "kind": "mattress", "box": [50, 298, 187, W - 50, 498, 2187]},
    ]
    for i in range(24):
        z = 215 + i * 81
        p.append({"id": f"k-slat-{i + 1}", "kind": "panel", "mat": "#c9a877", "box": [80, 290, z, 835, 298, z + 53]})
        p.append({"id": f"k-slat-{i + 25}", "kind": "panel", "mat": "#c9a877", "box": [865, 290, z, W - 80, 298, z + 53]})
    # two legs 200 at the foot: their tops in the corners behind the rails, splayed out below them
    for k, (x, sp) in enumerate([(86, "left"), (W - 86, "right")]):
        p.append(leg(f"h-{k + 1}", x, 2122, sp, covers=["h"], h=200))
    return dump("triniti-1-05", [W, 2217, 1143], p, [])


# ------------------------------------------------------------------------------------------------ cut lists
MISSING = {
    "triniti-0-02": [("1", "6.114.0.02.001", [408, 435, 16], 1), ("2", "6.114.0.02.002", [408, 435, 16], 1),
                     ("3", "6.114.0.02.003", [1644, 435, 16], 1), ("4", "6.114.0.02.004", [1644, 435, 16], 1)],
    "triniti-0-04": [("4", "6.114.0.04.004", [1242, 435, 16], 1)],
    "triniti-0-05": [("1", "6.114.0.05.001", [813, 435, 16], 1), ("2", "6.114.0.05.002", [813, 435, 16], 1),
                     ("3", "6.114.0.05.003", [1644, 435, 16], 1), ("6", "6.114.0.05.006", [813, 389.5, 16], 1)],
    "triniti-1-01": [("13.1", "6.114.1.01.13.1", [300, 500, 19.5], 1)],
    "triniti-1-02": [("6.2", "6.114.1.02.6.2", [164, 350, 16], 4)],
    "triniti-1-05": [("5", "6.114.1.05.005", [200, 1700, 16.5], 1), ("7", "6.114.1.05.007", [1127, 157, 16], 2)],
}


def nkey(n):
    return [float(x) for x in n.split(".")]


def cutlists():
    out = []
    os.makedirs(os.path.join(HERE, "cutlists"), exist_ok=True)
    for did, extra in MISSING.items():
        with open(os.path.join(REF, did + ".json")) as fh:
            ref = json.load(fh)
        rows = [dict(r) for r in ref["rows"]]
        have = {r["n"] for r in rows}
        for n, code, size, count in extra:
            assert n not in have, (did, n)
            rows.append({"n": n, "code": code, "size": size, "count": count})
        rows.sort(key=lambda r: nkey(r["n"]))
        lines = ["{", f'  "code": "{ref["code"]}",', '  "source": "page image",',
                 f'  "note": "reference/triniti/pages/{did}.png: rows {", ".join(e[0] for e in extra)} were lost from the PDF text; added from the table picture.",',
                 '  "rows": [']
        lines.append(",\n".join("    " + json.dumps(r, ensure_ascii=False) for r in rows))
        lines += ["  ]", "}"]
        path = os.path.join(HERE, "cutlists", did + ".json")
        with open(path, "w") as fh:
            fh.write("\n".join(lines) + "\n")
        out.append(path)
    return out


# ------------------------------------------------------------------------------------------------ catalogue fragment
HICKORY = "door_enamel_whitey#a1876f"      # «Гикори Кингстон 579 SWN», provisional: the swatch on p. 115 (Вена)
FINISHES = [
    {"id": "triniti-vanil", "name": "Ваниль / Гикори Кингстон 579 SWN", "body": HICKORY,
     "front": "door_enamel_whitey#e3e4df", "swatch": "#e3e4df"},
    {"id": "triniti-antracit", "name": "Антрацит / Гикори Кингстон 579 SWN", "body": HICKORY,
     "front": "door_enamel_whitey#3c3f41", "swatch": "#3c3f41"},
]
COLLECTION = {
    "id": "triniti", "name": "Тринити", "brand": "Пинскдрев", "finishes": ["triniti-vanil", "triniti-antracit"], "metal": "chrome",
    "note": "Каталог «Корпусная мебель ч. II» 2025, с. 9–11 (с. 14–19 по нумерации каталога). Корпус ЛДСП 16 «Гикори Кингстон» "
            "(крышка и дно на всю ширину, боковины и перегородки между ними), вкладные фасады МДФ 19 / 19,5 с фрезерованными "
            "пирамидами 100×100 и гладкие, push-to-open без ручек, наклонные конические опоры 130 из массива."}
MODELS = [
    ("triniti-0-01", "П6.114.0.01", "Шкаф «Тринити»", "living", [638, 435, 2030], "IS-P6-114-0-01-SHkaf.pdf", 9, "универсальный, с витриной"),
    ("triniti-0-02", "П6.114.0.02", "Тумба «Тринити»", "living", [1644, 435, 570], "IS-P6-114-0-02-Tumba.pdf", 9, "ТВ"),
    ("triniti-0-04", "П6.114.0.04", "Тумба «Тринити»", "living", [1242, 435, 1370], "IS-P6-114-0-04.pdf", 9, None),
    ("triniti-0-05", "П6.114.0.05", "Тумба «Тринити»", "living", [1644, 435, 975], "IS-P6-114-0-05.pdf", 9, None),
    ("triniti-1-01", "П6.114.1.01", "Шкаф для одежды 3Д «Тринити»", "bedroom", [1544, 590, 2300], "IS-P6-114-1-01-SHkaf-dlya-odejdyi-3D.pdf", 11, None),
    ("triniti-1-02", "П6.114.1.02", "Комод «Тринити»", "bedroom", [1038, 435, 975], "IS-P6-114-1-02-Komod.pdf", 11, None),
    ("triniti-1-03", "П6.114.1.03", "Зеркало «Тринити»", "decor", [1000, 20, 780], "IS-P6-114-1-03-Zerkalo.pdf", 11, None),
    ("triniti-1-04", "П6.114.1.04", "Тумба прикроватная «Тринити»", "bedroom", [538, 435, 470], "IS-P6-114-1-04-Tumba-prikrovatnaya.pdf", 11, None),
    ("triniti-1-05", "П6.114.1.05", "Кровать 2-16 «Тринити»", "bedroom", [1700, 2217, 1143], "IS-P6-114-1-05-Krovat-2-16.pdf", 11,
     "спальное место 2000×1600; размер по инструкции (в каталоге L2217×B1800×H1193)"),
]


def catalog():
    models = []
    for did, code, name, cat, size, is_, page, note in MODELS:
        m = {"id": did, "code": code, "name": name, "collection": "triniti", "category": cat, "size": size, "is": is_, "page": page}
        if did == "triniti-1-03":
            m["mount"] = "wall"
        if note:
            m["note"] = note
        models.append(m)
    lines = ["{", '  "finishes": [']
    lines.append(",\n".join("    " + json.dumps(f, ensure_ascii=False) for f in FINISHES))
    lines += ["  ],", '  "profiles": {']
    lines.append(",\n".join(f"    {json.dumps(k)}: " + json.dumps(v, ensure_ascii=False) for k, v in PROFILES.items()))
    lines += ["  },", '  "collections": [', "    " + json.dumps(COLLECTION, ensure_ascii=False), "  ],", '  "models": [']
    lines.append(",\n".join("    " + json.dumps(m, ensure_ascii=False) for m in models))
    lines += ["  ]", "}"]
    path = os.path.join(HERE, "triniti_catalog.json")
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return path


if __name__ == "__main__":
    for path in cutlists():
        print(path)
    for f in (m001, m002, m004, m005, m101, m102, m103, m104, m105):
        print(f())
    print(catalog())
