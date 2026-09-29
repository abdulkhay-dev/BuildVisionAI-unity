"""«Блэквуд Лофт» (Пинскдрев, П3.0556): living room 0.xx / 4.xx, bedroom 1.xx, hall 3.xx — 40 designs.

    /private/tmp/claude-501/venv/bin/python tools/casegoods/gen/blekvud-loft.py

Writes Assets/House4696/Resources/Casegoods/Designs/blekvud-loft-*.json, gen/blekvud-loft_catalog.json and the cut lists
transcribed from the instructions without a text layer (gen/cutlists/blekvud-loft-3-3x.json).

Construction (from the four hall instructions П570.01/03/04/05 = П3.0556.3.31/33/34/35; the living and bedroom modules are
built the same way, by the catalogue cut-outs pp. 79–80 and the site photos):
  * carcass ЛДСП 25 «Дуб Вотан»: top and bottom run the full L × B; the sides (B − 2 deep) stand between them, set 2 mm in
    from the ends (every panel between the sides is L − 54: 704 → 650, 904 → 850, 504 → 450).
  * back ДВП 3 laminated white in grooves of the sides (5 mm each side) and of the top / bottom (4–5 mm); split backs meet
    on a 128 rail («брусок», 3.31) or a fixed shelf.
  * inner panels ЛДСП 16 oak: fixed shelves 359 deep (L − 54 long) behind the fronts, loose shelves 339 deep.
  * fronts ЛДСП 16 inset between the sides / top / bottom, flush with the sides' front edge, 2 mm round, 3–4 between;
    «Черный 660 WML» or oak. Wardrobe doors = three panels joined on dowels: oak, a black band, oak (3.31: 748 + 280 + 698).
  * drawers: the black front is the box's front wall («стенка передняя»), oak sides 16, back on the ДВП bottom, ball runners
    (12.7 mm gap a side).
  * legs: black steel corner legs «Опора угловая 120 мм» — a 25 mm square post in each corner with two 85 mm arms under
    the bottom; handles: black bar «OZKM 5132» (~150 long, flat bar on two posts).
Coordinates: x from the left, y up from the floor, z from the wall (back) to the front; mm.
"""
import json
import os

from common import dump

HERE = os.path.dirname(os.path.abspath(__file__))
SLUG = "blekvud-loft"
T = 25        # carcass board
LEG = 120     # corner legs
BZ0, BZ1 = 4, 7.2           # back ДВП (3.2) in grooves 3 mm from the sides' back edge
RAIL = (7.5, 23.5)          # rail behind the fixed shelves
ALU = "chrome#c4c5c2"       # sliding-door aluminium profiles (satin)


def R(v):
    return round(v, 1)


class D:
    """A design under construction."""

    def __init__(self, did, size):
        self.id, self.size, self.parts, self.moves = did, size, [], []

    def add(self, n=None, box=None, pid=None, kind=None, **kw):
        p = {}
        if n is not None:
            p["n"] = n
        if pid is not None:
            p["id"] = pid
        if kind is not None and kind != "panel":
            p["kind"] = kind
        p.update(kw)
        if box is not None:
            p["box"] = [R(v) for v in box]
        self.parts.append(p)
        return p.get("id") or p.get("n")

    def move(self, **m):
        self.moves.append(m)

    def write(self):
        return dump(self.id, self.size, self.parts, self.moves)


# ------------------------------------------------------------------------------------------------------ building blocks
def carcass(d, W, B, H, y0=LEG, n=(None, None, None, None), inner="body"):
    """Bottom and top full W × B (25), sides B − 2 deep between them, 2 mm in from the ends.
    n = (left side, right side, top, bottom) cut-list numbers. Returns the inner box (x0, x1, yb, yt, zf)."""
    s1, s2, top, bot = n
    d.add(bot, [0, y0, 0, W, y0 + T, B], pid=None if bot else "bottom", grain="x")
    d.add(s1, [2, y0 + T, 1, 2 + T, H - T, B - 1], pid=None if s1 else "side-l", grain="y")
    d.add(s2, [W - 2 - T, y0 + T, 1, W - 2, H - T, B - 1], pid=None if s2 else "side-r", grain="y")
    d.add(top, [0, H - T, 0, W, H, B], pid=None if top else "top", grain="x")
    return 2 + T, W - 2 - T, y0 + T, H - T, B - 1


def corner_legs(d, W, B, h=LEG, post=25, arm=85):
    """«Опора угловая 120 мм»: a square post in each corner, two arms along the bottom's edges under it."""
    k = 0
    for x0, sx in ((0, 1), (W - post, -1)):
        for z0, sz in ((0, 1), (B - post, -1)):
            k += 1
            d.add(box=[x0, 0, z0, x0 + post, h, z0 + post], pid=f"leg-{k}", mat="metal", edge=1.5)
            ax0 = x0 + post if sx > 0 else x0 - arm
            d.add(box=[ax0, h - post, z0, ax0 + arm, h, z0 + post], pid=f"leg-{k}-ax", mat="metal", edge=1.5)
            az0 = z0 + post if sz > 0 else z0 - arm
            d.add(box=[x0, h - post, az0, x0 + post, h, az0 + arm], pid=f"leg-{k}-az", mat="metal", edge=1.5)


def glides(d, W, B, h=15, inset=40):
    k = 0
    for x in (inset, W / 2, W - inset):
        for z in (inset, B - inset):
            k += 1
            d.add(box=[x - 15, 0, z - 15, x + 15, h, z + 15], pid=f"glide-{k}", kind="tube", mat="black", covers=["glide"])


def bar(d, pid, x, y, z, length=150, vertical=False):
    """«OZKM 5132»: black flat bar on two square posts."""
    d.add(pid=pid, kind="handle", model="bar", at=[R(x), R(y)], dir="up" if vertical else "right", d=length, band=10, t=7,
          standoff=24, post=9, section="square", z=R(z))
    return pid


def back(d, n, box, pid=None, mat=None):
    kw = {"mat": mat} if mat else {}
    return d.add(n, box, pid=pid, kind="back", **kw)


def front(d, n, box, pid=None, mat=None, grain="x", **kw):
    if mat:
        kw["mat"] = mat
    return d.add(n, box, pid=pid, kind="front", grain=grain, **kw)


def drawer(d, tag, fbox, ix0, ix1, side_len=300, side_h=96, back_h=77, ns=(None, None, None, None, None), fmat=None):
    """Hall-style drawer (3.35): the front 16 is the box's front wall; oak sides 16 × side_len × side_h on ball runners
    (12.7 mm gap each side), the back (h = back_h) standing on the ДВП bottom, which sits in grooves of the sides and 5 mm
    in the front. ns = (front, side l, side r, back, bottom) cut-list numbers."""
    fx0, fy0, fz0, fx1, fy1, fz1 = fbox
    nf, nsl, nsr, nb, nbt = ns
    ids = [front(d, nf, fbox, pid=f"front-{tag}", mat=fmat)]
    bx0, bx1 = ix0 + 12.7, ix1 - 12.7
    by0 = fy0 + 18
    z0 = fz0 - side_len
    ids.append(d.add(nsl, [bx0, by0, z0, bx0 + 16, by0 + side_h, fz0], pid=f"side-l-{tag}"))
    ids.append(d.add(nsr, [bx1 - 16, by0, z0, bx1, by0 + side_h, fz0], pid=f"side-r-{tag}"))
    ids.append(d.add(nb, [bx0 + 16, by0 + side_h - back_h, z0, bx1 - 16, by0 + side_h, z0 + 16], pid=f"back-{tag}"))
    ids.append(back(d, nbt, [bx0 + 10, by0 + side_h - back_h - 3.2, z0, bx1 - 10, by0 + side_h - back_h, fz0 + 5], pid=f"bottom-{tag}"))
    return ids


def drawer_move(d, tag, ids, travel=280):
    d.move(type="drawer", name=f"drawer_{tag}", parts=ids, travel=travel)


def door3(d, tag, x0, x1, y0, y1, z0, z1, band, ns=(None, None, None), grain="x", band_mat="front", oak_mat="body"):
    """A wardrobe door of three panels joined on dowels: oak below, the black band, oak above. band = (y_lo, y_hi)."""
    nl, nbnd, nu = ns
    a = front(d, nl, [x0, y0, z0, x1, band[0], z1], pid=f"{tag}-lo", mat=oak_mat, grain=grain)
    b = front(d, nbnd, [x0, band[0], z0, x1, band[1], z1], pid=f"{tag}-band", mat=band_mat, grain="x")
    c = front(d, nu, [x0, band[1], z0, x1, y1, z1], pid=f"{tag}-up", mat=oak_mat, grain=grain)
    return [a, b, c]


def shelves(d, tag, x0, x1, ys, z0, z1, n=None, mat=None, t=16):
    out = []
    for i, y in enumerate(ys):
        kw = {"mat": mat} if mat else {}
        out.append(d.add(n, [x0, y, z0, x1, y + t, z1], pid=f"{tag}-{i + 1}", **kw))
    return out


def rail(d, pid, x0, x1, y, z, dia=25):
    d.add(box=[x0, y - dia / 2, z - dia / 2, x1, y + dia / 2, z + dia / 2], pid=pid, kind="tube", mat="chrome")


# ============================================================================================================== HALL 3.xx
def m3_31():
    """Шкаф 2д 704 × 400 × 1900 (instruction П570.01)."""
    W, B, H = 704, 400, 1900
    d = D(f"{SLUG}-3-31", [W, B, H])
    x0, x1, yb, yt, zf = carcass(d, W, B, H, n=("1", "2", "3", "4"))
    corner_legs(d, W, B)
    # rail 12 behind the joint of the backs, fixed shelves 7 (low) and 8 (under the rail «штанга выдвижная»)
    d.add("12", [x0, 946, RAIL[0], x1, 1074, RAIL[1]])
    d.add("7", [x0, 300, RAIL[1], x1, 316, RAIL[1] + 359])
    d.add("8", [x0, 1690, RAIL[1], x1, 1706, RAIL[1] + 359])
    back(d, "14", [x0 - 5, yb - 4, BZ0, x1 + 5, 1010, BZ1], pid="14-lo")
    back(d, "14", [x0 - 5, 1010, BZ0, x1 + 5, yt + 4, BZ1], pid="14-up")
    shelves(d, "11", x0 + 1, x1 - 1, [591, 866, 1150, 1420], 30, 30 + 339, n="11")
    # the pull-out rail under 8 (hardware 018, L 288)
    d.add(box=[x0 + 305, 1650, 60, x0 + 345, 1690, 348], pid="rail-018", kind="tube", mat="chrome", covers=["018"])
    fz0, fz1 = zf - 16, zf
    band = (845, 1125)
    left = door3(d, "door-l", x0 + 2.5, x0 + 323.5, yb + 2, yt - 2, fz0, fz1, band, ns=("9", "15", "5"))
    right = door3(d, "door-r", x1 - 323.5, x1 - 2.5, yb + 2, yt - 2, fz0, fz1, band, ns=("10", "16", "6"))
    left.append(bar(d, "h-l", x0 + 323.5 - 95, 985, fz1))
    right.append(bar(d, "h-r", x1 - 323.5 + 95, 985, fz1))
    d.move(type="door", name="door_left", parts=left, hinge="left", angle=105)
    d.move(type="door", name="door_right", parts=right, hinge="right", angle=105)
    return d.write()


def m3_32():
    """Вешалка 500 × 256 × 1780 (by catalogue p. 79): a board of oak / black band / oak, a shelf with a black hanger rail."""
    W, B, H = 500, 256, 1780
    d = D(f"{SLUG}-3-32", [W, B, H])
    d.add(box=[0, 0, 0, W, 720, T], pid="board-lo", grain="y")
    d.add(box=[0, 720, 0, W, 1000, T], pid="board-band", mat="front", grain="x")
    d.add(box=[0, 1000, 0, W, H, T], pid="board-up", grain="y")
    d.add(box=[0, 1610, T, W, 1635, B], pid="shelf", grain="x")
    # black steel rail: two flat brackets down from the shelf, a flat bar along x
    for i, x in enumerate((60, W - 60)):
        d.add(box=[x - 12, 1555, 150, x + 12, 1610, 160], pid=f"bracket-{i + 1}", mat="metal", edge=1)
    d.add(box=[20, 1540, 145, W - 20, 1555, 165], pid="hanger-bar", mat="metal", edge=2)
    return d.write()


def m3_33():
    """Тумба 504 × 400 × 480 (instruction П570.03): a seat with a cushion over one door and a shelf."""
    W, B, H = 504, 400, 480
    d = D(f"{SLUG}-3-33", [W, B, H])
    Hc = 450   # the carcass; the cushion (70.03.01) adds 30 (the drawing's 484 over-reads the catalogue's 480)
    x0, x1, yb, yt, zf = carcass(d, W, B, Hc, n=("4", "5", "3", "2"))
    corner_legs(d, W, B)
    back(d, "8", [x0 - 5, yb - 5, BZ0, x1 + 5, yt + 5, BZ1])
    d.add("6", [x0 + 1, 290, 30, x1 - 1, 306, 30 + 339])
    d.add("1", [5, Hc, 5, W - 5, H, 395], kind="soft")
    fz0, fz1 = zf - 16, zf
    f = front(d, "7", [x0 + 2, yb + 2, fz0, x1 - 2, yt - 2, fz1])
    h = bar(d, "h-door", W / 2, yt - 2 - 45, fz1)
    d.move(type="door", name="door", parts=[f, h], hinge="left", angle=105)
    return d.write()


def m3_34():
    """Зеркало 900 × 160 × 750 (instruction П570.04; the catalogue writes H700, the instruction's board is 750)."""
    W, B, H = 900, 160, 750
    d = D(f"{SLUG}-3-34", [W, B, H])
    d.add("1", [0, 0, 0, W, H, 16], grain="x")
    d.add("3", [20, 18, 16, W - 20, 34, B], mat="front", grain="x")
    d.add("2", [54.5, 37, 16, W - 54.5, 738, 20], kind="mirror")
    return d.write()


def m3_35():
    """Тумба для обуви 904 × 400 × 1150 (instruction П570.05): two drawers over two doors."""
    W, B, H = 904, 400, 1150
    d = D(f"{SLUG}-3-35", [W, B, H])
    x0, x1, yb, yt, zf = carcass(d, W, B, H, n=("1", "2", "3", "4"))
    corner_legs(d, W, B)
    d.add("5", [x0, 605, 23, x1, 621, 23 + 359])
    back(d, "15", [x0 - 5, yb - 4, BZ0, x1 + 5, 613, BZ1])
    back(d, "14", [x0 - 5, 613, BZ0, x1 + 5, yt + 4, BZ1])
    d.add("8", [x0 + 1, 370, 30, x1 - 1, 386, 30 + 339])
    fz0, fz1 = zf - 16, zf
    dl = front(d, "6", [x0 + 2, yb + 3, fz0, x0 + 423, yb + 699, fz1], pid="6", mat="body", grain="y")
    dr = front(d, "7", [x1 - 423, yb + 3, fz0, x1 - 2, yb + 699, fz1], pid="7", mat="body", grain="y")
    hl = bar(d, "h-door-l", x0 + 423 - 120, yb + 699 - 45, fz1)
    hr = bar(d, "h-door-r", x1 - 423 + 120, yb + 699 - 45, fz1)
    d.move(type="door", name="door_left", parts=[dl, hl], hinge="left", angle=105)
    d.move(type="door", name="door_right", parts=[dr, hr], hinge="right", angle=105)
    for tag, fy0 in (("lo", 847), ("up", 986)):
        ids = drawer(d, tag, [x0 + 2, fy0, fz0, x1 - 2, fy0 + 136, fz1], x0, x1, ns=("12", "10", "11", "9", "16"),
                     side_len=300, side_h=96, back_h=77)
        ids.append(bar(d, f"h-{tag}", W / 2, fy0 + 136 / 2 + 10, fz1))
        drawer_move(d, tag, ids)
    return d.write()


# ============================================================================================================= LIVING 0.xx
def m0_01():
    """Полка навесная 1600 × 285 × 375: a lift-up black flap (gas struts) and an open niche on the right."""
    W, B, H = 1600, 285, 375
    d = D(f"{SLUG}-0-01", [W, B, H])
    x0, x1, yb, yt, zf = carcass(d, W, B, H, y0=0)
    xp = 985
    d.add(box=[xp, yb, RAIL[0], xp + 16, yt, zf], pid="partition", grain="y")
    back(d, None, [x0 - 5, yb - 4, BZ0, xp + 5, yt + 4, BZ1], pid="back-flap")
    back(d, None, [xp + 11, yb - 4, BZ0, x1 + 5, yt + 4, BZ1], pid="back-niche", mat="body")
    f = front(d, None, [x0 + 2, yb + 2, zf - 16, xp - 2, yt - 2, zf], pid="flap")
    h = bar(d, "h-flap", (x0 + xp) / 2, yb + 2 + 30, zf)
    d.move(type="flap", name="flap", parts=[f, h], hinge="top", angle=95)
    return d.write()


def m0_02():
    """Стол журнальный 1100 × 600 × 445: a drawer on the left, an open niche with a shelf on the right."""
    W, B, H = 1100, 600, 445
    d = D(f"{SLUG}-0-02", [W, B, H])
    x0, x1, yb, yt, zf = carcass(d, W, B, H)
    corner_legs(d, W, B)
    xp = 727
    d.add(box=[xp, yb, RAIL[0], xp + 16, yt, zf], pid="partition", grain="y")
    back(d, None, [x0 - 5, yb - 4, BZ0, x1 + 5, yt + 4, BZ1], pid="back", mat="body")
    d.add(box=[xp + 17, 275, 30, x1 - 1, 291, zf - 20], pid="shelf")
    fz0, fz1 = zf - 16, zf
    ids = drawer(d, "1", [x0 + 2, yb + 2, fz0, xp - 2, yt - 2, fz1], x0, xp, side_len=450, side_h=200, back_h=180)
    ids.append(bar(d, "h-drawer", (x0 + xp) / 2, yt - 2 - 40, fz1))
    drawer_move(d, "1", ids, travel=400)
    return d.write()


def m0_03():
    """Тумба ТВ 1600 × 455 × 575: an open niche over a drawer on the left, a door on the right."""
    W, B, H = 1600, 455, 575
    d = D(f"{SLUG}-0-03", [W, B, H])
    x0, x1, yb, yt, zf = carcass(d, W, B, H)
    corner_legs(d, W, B)
    xp = 985
    d.add(box=[xp, yb, RAIL[0], xp + 16, yt, zf - 16], pid="partition", grain="y")
    back(d, None, [x0 - 5, yb - 4, BZ0, x1 + 5, yt + 4, BZ1], pid="back")
    fz0, fz1 = zf - 16, zf
    d.add(box=[x0, 434, RAIL[0], xp, 450, zf], pid="shelf-niche")
    d.add(box=[xp + 17, 330, 30, x1 - 1, 346, 30 + 390], pid="shelf-r")
    ids = drawer(d, "1", [x0 + 2, yb + 2, fz0, xp - 2, 431, fz1], x0, xp, side_len=400, side_h=220, back_h=200)
    ids.append(bar(d, "h-drawer", (x0 + xp) / 2, 431 - 40, fz1))
    drawer_move(d, "1", ids, travel=350)
    f = front(d, None, [xp + 2, yb + 2, fz0, x1 - 2, yt - 2, fz1], pid="door")
    h = bar(d, "h-door", (xp + x1) / 2, yt - 2 - 40, fz1)
    d.move(type="door", name="door", parts=[f, h], hinge="right", angle=105)
    return d.write()


def m0_04():
    """Шкаф-витрина 700 × 400 × 1900: black door, a bronze glass door over a lit glass shelf, black door."""
    W, B, H = 700, 400, 1900
    d = D(f"{SLUG}-0-04", [W, B, H])
    x0, x1, yb, yt, zf = carcass(d, W, B, H)
    corner_legs(d, W, B)
    d.add(box=[x0, 686, RAIL[0], x1, 702, zf - 17], pid="shelf-fix-lo")
    d.add(box=[x0, 1343, RAIL[0], x1, 1359, zf - 17], pid="shelf-fix-up")
    back(d, None, [x0 - 5, yb - 4, BZ0, x1 + 5, 694, BZ1], pid="back-lo")
    back(d, None, [x0 - 5, 694, BZ0, x1 + 5, 1351, BZ1], pid="back-mid", mat="body")
    back(d, None, [x0 - 5, 1351, BZ0, x1 + 5, yt + 4, BZ1], pid="back-up")
    d.add(box=[x0 + 1, 1020, 30, x1 - 1, 1026, 370], pid="glass-shelf", kind="glass")
    d.add(box=[x0 + 1, 400, 30, x1 - 1, 416, 369], pid="shelf-lo")
    d.add(box=[x0 + 1, 1600, 30, x1 - 1, 1616, 369], pid="shelf-up")
    d.add(box=[W / 2 - 30, 1339, 170, W / 2 + 30, 1343, 230], pid="led", kind="light", shape="circle")
    fz0, fz1 = zf - 16, zf
    lo = front(d, None, [x0 + 2.5, yb + 2, fz0, x1 - 2.5, 701, fz1], pid="door-lo")
    hlo = bar(d, "h-lo", W / 2, 701 - 40, fz1)
    gl = front(d, None, [x0 + 2.5, 704, zf - 5, x1 - 2.5, 1340, zf], pid="door-glass",
               glass={"frame": 2, "rebate": 0, "t": 4, "tint": "bronze"})
    up = front(d, None, [x0 + 2.5, 1343, fz0, x1 - 2.5, yt - 2, fz1], pid="door-up")
    hup = bar(d, "h-up", W / 2, 1343 + 40, fz1)
    d.move(type="door", name="door_lo", parts=[lo, hlo], hinge="left", angle=105)
    d.move(type="door", name="door_glass", parts=[gl], hinge="left", angle=105)
    d.move(type="door", name="door_up", parts=[up, hup], hinge="left", angle=105)
    return d.write()


def m0_05():
    """Тумба 1200 × 400 × 1274: four doors in a checkerboard of black and oak."""
    W, B, H = 1200, 400, 1274
    d = D(f"{SLUG}-0-05", [W, B, H])
    x0, x1, yb, yt, zf = carcass(d, W, B, H)
    corner_legs(d, W, B)
    xp = W / 2 - 8
    d.add(box=[xp, yb, RAIL[0], xp + 16, yt, zf - 17], pid="partition", grain="y")
    d.add(box=[x0, 689.5, RAIL[1], xp, 705.5, zf - 17], pid="shelf-fix-l")
    d.add(box=[xp + 16, 689.5, RAIL[1], x1, 705.5, zf - 17], pid="shelf-fix-r")
    d.add(box=[x0, 689.5, RAIL[0], xp, 705.5, RAIL[1]], pid="rail-l")
    d.add(box=[xp + 16, 689.5, RAIL[0], x1, 705.5, RAIL[1]], pid="rail-r")
    back(d, None, [x0 - 5, yb - 4, BZ0, x1 + 5, 697.5, BZ1], pid="back-lo")
    back(d, None, [x0 - 5, 697.5, BZ0, x1 + 5, yt + 4, BZ1], pid="back-up")
    for i, (a, b) in enumerate(((x0, xp), (xp + 16, x1))):
        shelves(d, f"shelf-{'lr'[i]}", a + 1, b - 1, [420, 975], 30, 369)
    fz0, fz1 = zf - 16, zf
    cells = [("tl", x0 + 2, xp - 1.5, 699, yt - 2, "front", "left", 699 + 40),
             ("tr", xp + 17.5, x1 - 2, 699, yt - 2, "body", "right", 699 + 40),
             ("bl", x0 + 2, xp - 1.5, yb + 2, 696, "body", "left", 696 - 40),
             ("br", xp + 17.5, x1 - 2, yb + 2, 696, "front", "right", 696 - 40)]
    for tag, a, b, c, e, mat, hinge, hy in cells:
        f = front(d, None, [a, c, fz0, b, e, fz1], pid=f"door-{tag}", mat=mat)
        h = bar(d, f"h-{tag}", (a + b) / 2, hy, fz1)
        d.move(type="door", name=f"door_{tag}", parts=[f, h], hinge=hinge, angle=105)
    return d.write()


def m0_07():
    """Тумба 1773 × 455 × 780: three drawers, two doors (three equal columns)."""
    W, B, H = 1773, 455, 780
    d = D(f"{SLUG}-0-07", [W, B, H])
    x0, x1, yb, yt, zf = carcass(d, W, B, H)
    corner_legs(d, W, B)
    cw = (x1 - x0 - 32) / 3
    cols = [(x0, x0 + cw), (x0 + cw + 16, x0 + 2 * cw + 16), (x0 + 2 * cw + 32, x1)]
    for i, xp in enumerate((cols[0][1], cols[1][1])):
        d.add(box=[xp, yb, RAIL[0], xp + 16, yt, zf - 17], pid=f"partition-{i + 1}", grain="y")
    back(d, None, [x0 - 5, yb - 4, BZ0, x1 + 5, yt + 4, BZ1], pid="back")
    fz0, fz1 = zf - 16, zf
    a, b = cols[0]
    for k, fy0 in enumerate((yb + 2, yb + 205, yb + 408)):
        tag = f"{k + 1}"
        fy1 = fy0 + 200
        ids = drawer(d, tag, [a + 2, fy0, fz0, b - 1.5, fy1, fz1], a, b, side_len=400, side_h=150, back_h=130)
        ids.append(bar(d, f"h-drawer-{tag}", (a + b) / 2, fy1 - 40, fz1))
        drawer_move(d, tag, ids, travel=350)
    for i, ((a, b), hinge) in enumerate(zip(cols[1:], ("left", "right"))):
        shelves(d, f"shelf-{i + 1}", a + 1, b - 1, [440], 30, 30 + 390)
        f = front(d, None, [a + 1.5, yb + 2, fz0, b - (2 if i else 1.5), yt - 2, fz1], pid=f"door-{i + 1}")
        h = bar(d, f"h-door-{i + 1}", (a + b) / 2, yt - 2 - 40, fz1)
        d.move(type="door", name=f"door_{i + 1}", parts=[f, h], hinge=hinge, angle=105)
    return d.write()


def m4_06():
    """Стол обеденный 1402 × 802 × 750 on a black steel frame (square legs, apron under the top)."""
    W, B, H = 1402, 802, 750
    d = D(f"{SLUG}-4-06", [W, B, H])
    top_y = H - T
    d.add(box=[0, top_y, 0, W, H, B], pid="top", grain="x", edge=2)
    i, lx, lz, ah = 15, 40, 60, 50
    for k, (x, z) in enumerate(((i, i), (W - i - lx, i), (i, B - i - lz), (W - i - lx, B - i - lz))):
        d.add(box=[x, 0, z, x + lx, top_y, z + lz], pid=f"leg-{k + 1}", mat="metal", edge=2)
    d.add(box=[i + lx, top_y - ah, i, W - i - lx, top_y, i + 20], pid="apron-back", mat="metal", edge=1.5)
    d.add(box=[i + lx, top_y - ah, B - i - 20, W - i - lx, top_y, B - i], pid="apron-front", mat="metal", edge=1.5)
    d.add(box=[i, top_y - ah, i + lz, i + 20, top_y, B - i - lz], pid="apron-l", mat="metal", edge=1.5)
    d.add(box=[W - i - 20, top_y - ah, i + lz, W - i, top_y, B - i - lz], pid="apron-r", mat="metal", edge=1.5)
    return d.write()


def m4_12():
    """Стол обеденный раздвижной 1302 (1802) × 902 × 770: oak top in two halves, black apron and L-section legs."""
    W, B, H = 1302, 902, 770
    d = D(f"{SLUG}-4-12", [W, B, H])
    ty = H - T
    d.add(box=[0, ty, 0, W / 2, H, B], pid="top-l", grain="x", edge=2)
    d.add(box=[W / 2, ty, 0, W, H, B], pid="top-r", grain="x", edge=2)
    i, lw, t = 20, 90, T
    k = 0
    for x0, sx in ((i, 1), (W - i, -1)):
        for z0, sz in ((i, 1), (B - i, -1)):
            k += 1
            xa, xb = sorted((x0, x0 + sx * lw))
            za, zb = sorted((z0, z0 + sz * t))
            d.add(box=[xa, 0, za, xb, ty, zb], pid=f"leg-{k}-a", mat="front", grain="y")
            xa, xb = sorted((x0, x0 + sx * t))
            za, zb = sorted((z0 + sz * t, z0 + sz * lw))
            d.add(box=[xa, 0, za, xb, ty, zb], pid=f"leg-{k}-b", mat="front", grain="y")
    ah, at = 100, 16
    d.add(box=[i + lw, ty - ah, i, W - i - lw, ty, i + at], pid="apron-back", mat="front", grain="x")
    d.add(box=[i + lw, ty - ah, B - i - at, W - i - lw, ty, B - i], pid="apron-front", mat="front", grain="x")
    d.add(box=[i, ty - ah, i + lw, i + at, ty, B - i - lw], pid="apron-l", mat="front", grain="z")
    d.add(box=[W - i - at, ty - ah, i + lw, W - i, ty, B - i - lw], pid="apron-r", mat="front", grain="z")
    return d.write()


# ============================================================================================================ BEDROOM 1.xx
def chest(did, W, B, H, cols, rows, door_cols=(), hinge="right", handle_off=None, niche=None):
    """Комоды / тумбы: carcass on corner legs; `cols` columns (16 mm partitions) of `rows` drawers, or doors in
    door_cols. niche = height of an open niche at the top (bedside 1.17)."""
    d = D(did, [W, B, H])
    x0, x1, yb, yt, zf = carcass(d, W, B, H)
    corner_legs(d, W, B)
    cw = (x1 - x0 - 16 * (cols - 1)) / cols
    xs = [(x0 + k * (cw + 16), x0 + k * (cw + 16) + cw) for k in range(cols)]
    for k in range(cols - 1):
        d.add(box=[xs[k][1], yb, RAIL[0], xs[k][1] + 16, yt, zf - 17], pid=f"partition-{k + 1}", grain="y")
    back(d, None, [x0 - 5, yb - 4, BZ0, x1 + 5, yt + 4, BZ1], pid="back")
    fz0, fz1 = zf - 16, zf
    ytop = yt
    if niche:
        ytop = yt - niche - 16
        d.add(box=[x0, ytop, RAIL[0], x1, ytop + 16, zf], pid="shelf-niche")
    for k, (a, b) in enumerate(xs):
        ga = 2 if k == 0 else 1.5
        gb = 2 if k == cols - 1 else 1.5
        if k in door_cols:
            f = front(d, None, [a + ga, yb + 2, fz0, b - gb, ytop - 2, fz1], pid=f"door-{k + 1}", grain="y")
            hx = (a + ga + 150) if hinge == "right" else (b - gb - 150)
            h = bar(d, f"h-door-{k + 1}", hx if handle_off else (a + b) / 2, ytop - 2 - 40, fz1)
            sd = 339 if B <= 400 else 380
            shelves(d, f"shelf-{k + 1}", a + 1, b - 1, [yb + (ytop - yb) / 3, yb + 2 * (ytop - yb) / 3], 30, 30 + sd)
            d.move(type="door", name=f"door_{k + 1}", parts=[f, h], hinge=hinge, angle=105)
            continue
        hgt = (ytop - yb - 4 - 3 * (rows - 1)) / rows
        for r in range(rows):
            fy0 = yb + 2 + r * (hgt + 3)
            fy1 = fy0 + hgt
            tag = f"{k + 1}-{r + 1}"
            side_h = max(80, min(hgt - 45, 180))
            ids = drawer(d, tag, [a + ga, fy0, fz0, b - gb, fy1, fz1], a, b, side_len=min(400, B - 70) // 50 * 50,
                         side_h=side_h, back_h=side_h - 19)
            ids.append(bar(d, f"h-{tag}", (a + b) / 2, fy1 - 40, fz1))
            drawer_move(d, tag, ids, travel=300)
    return d.write()


def m1_26():
    """Зеркало 1068 × 85 × 801: a box frame of oak 25 round a black panel with a bevelled mirror."""
    W, B, H = 1068, 85, 801
    d = D(f"{SLUG}-1-26", [W, B, H])
    d.add(box=[0, H - T, 0, W, H, B], pid="frame-top", grain="x")
    d.add(box=[0, 0, 0, W, T, B], pid="frame-bottom", grain="x")
    d.add(box=[0, T, 0, T, H - T, B], pid="frame-l", grain="y")
    d.add(box=[W - T, T, 0, W, H - T, B], pid="frame-r", grain="y")
    d.add(box=[T, T, 0, W - T, H - T, 16], pid="panel", mat="front", grain="x")
    d.add(box=[T + 40, T + 40, 16, W - T - 40, H - T - 40, 20], pid="mirror", kind="mirror")
    return d.write()


def m1_12():
    """Комод 935 × 557 × 727 for a compartment of the coupe 1.11: white, three drawers without handles."""
    W, B, H = 935, 557, 727
    d = D(f"{SLUG}-1-12", [W, B, H])
    d.add(box=[0, H - 16, 0, W, H, B], pid="top", mat="inner")
    d.add(box=[0, 0, 0, 16, H - 16, B], pid="side-l", mat="inner")
    d.add(box=[W - 16, 0, 0, W, H - 16, B], pid="side-r", mat="inner")
    d.add(box=[16, 30, 0, W - 16, 46, B - 16], pid="bottom", mat="inner")
    d.add(box=[16, 0, B - 36, W - 16, 30, B - 20], pid="plinth", mat="inner")
    back(d, None, [11, 41, 4, W - 11, H - 11, 7.2], pid="back")
    x0, x1 = 16, W - 16
    hgt = (H - 16 - 46 - 4 - 6) / 3
    for r in range(3):
        fy0 = 48 + r * (hgt + 3)
        tag = f"{r + 1}"
        ids = drawer(d, tag, [x0 + 2, fy0, B - 16, x1 - 2, fy0 + hgt, B], x0, x1, side_len=450, side_h=hgt - 50,
                     back_h=hgt - 69, fmat="inner")
        drawer_move(d, tag, ids, travel=400)
    for p in d.parts:
        if p.get("id", "").startswith(("side-l-", "side-r-", "back-")) and "mat" not in p:
            p["mat"] = "inner"
    return d.write()


def m1_13():
    W, B, H = 935, 520, 16
    d = D(f"{SLUG}-1-13", [W, B, H])
    d.add(box=[0, 0, 0, W, H, B], pid="shelf", mat="inner", grain="x")
    return d.write()


def bed(did, sleep_w):
    """Кровать with a metal frame: headboard (oak 25 faced with oak strips and a black panel) 35 mm wider than the box each
    side, box of oak 25 (side rails and foot) on corner legs 120, black steel frame with beech slats, mattress."""
    B = sleep_w + 150
    L, H = 2120, 890
    d = D(did, [B, L, H])
    hb = 25
    d.add(box=[0, LEG + 10, 0, B, H, hb], pid="headboard", grain="x")
    d.add(box=[0, H - 60, hb, B, H, hb + 16], pid="hb-strip-top", grain="x")
    d.add(box=[0, 400, hb, 60, H - 60, hb + 16], pid="hb-strip-l", grain="y")
    d.add(box=[B - 60, 400, hb, B, H - 60, hb + 16], pid="hb-strip-r", grain="y")
    d.add(box=[60, 400, hb, B - 60, H - 60, hb + 16], pid="hb-panel", mat="front", grain="x")
    z0 = hb + 16
    xo0, xo1 = 35, B - 35
    ytop = 400
    d.add(box=[xo0, LEG, z0, xo0 + T, ytop, L], pid="rail-l", grain="z")
    d.add(box=[xo1 - T, LEG, z0, xo1, ytop, L], pid="rail-r", grain="z")
    d.add(box=[xo0 + T, LEG, L - T, xo1 - T, ytop, L - 0], pid="foot", grain="x")
    # corner legs under the box
    k = 0
    for x, sx in ((xo0, 1), (xo1 - 25, -1)):
        for z, sz in ((z0, 1), (L - 25, -1)):
            k += 1
            d.add(box=[x, 0, z, x + 25, LEG, z + 25], pid=f"leg-{k}", mat="metal", edge=1.5)
            ax = x + 25 if sx > 0 else x - 85
            d.add(box=[ax, LEG - 25, z, ax + 85, LEG, z + 25], pid=f"leg-{k}-ax", mat="metal", edge=1.5)
            az = z + 25 if sz > 0 else z - 85
            d.add(box=[x, LEG - 25, az, x + 25, LEG, az + 85], pid=f"leg-{k}-az", mat="metal", edge=1.5)
    # metal frame (sleep_w × 2000) on brackets inside the rails
    fx0, fx1 = B / 2 - sleep_w / 2, B / 2 + sleep_w / 2
    fz0, fz1 = z0 + 20, z0 + 2020
    fy0, fy1 = 290, 330
    d.add(box=[fx0, fy0, fz0, fx0 + 25, fy1, fz1], pid="frame-l", mat="black")
    d.add(box=[fx1 - 25, fy0, fz0, fx1, fy1, fz1], pid="frame-r", mat="black")
    d.add(box=[fx0 + 25, fy0, fz0, fx1 - 25, fy1, fz0 + 25], pid="frame-head", mat="black")
    d.add(box=[fx0 + 25, fy0, fz1 - 25, fx1 - 25, fy1, fz1], pid="frame-foot", mat="black")
    rows = [(fx0 + 25, fx1 - 25)]
    if sleep_w >= 1200:
        xm = B / 2
        d.add(box=[xm - 12.5, fy0, fz0 + 25, xm + 12.5, fy1, fz1 - 25], pid="frame-mid", mat="black")
        rows = [(fx0 + 25, xm - 12.5), (xm + 12.5, fx1 - 25)]
        for j, z in enumerate((fz0 + 700, fz0 + 1350)):
            d.add(box=[xm - 12.5, 0, z - 12.5, xm + 12.5, fy0, z + 12.5], pid=f"frame-leg-{j + 1}", kind="tube", mat="black")
    n = 24
    pitch = (fz1 - fz0 - 50 - 53) / (n - 1)
    for r, (a, b) in enumerate(rows):
        for s in range(n):
            z = fz0 + 25 + s * pitch
            d.add(box=[a, fy1, z, b, fy1 + 8, z + 53], pid=f"slat-{r + 1}-{s + 1}", mat="door_enamel_whitey#d8bf95", grain="x", edge=1)
    d.add(box=[fx0, fy1 + 8, fz0, fx1, fy1 + 208, fz1], pid="mattress", kind="mattress")
    return d.write()


def wardrobe(did, W, ndoors, part_after, hinges, handle_edge):
    """Шкаф для одежды 2110 × 600: carcass on glides, inset doors of oak / black band / oak with the bar on the band.
    part_after = door index after which the partition stands (None = one compartment)."""
    B, H = 600, 2110
    d = D(did, [W, B, H])
    x0, x1, yb, yt, zf = carcass(d, W, B, H, y0=15)
    glides(d, W, B)
    inner = x1 - x0
    dw = (inner - 5 - 3 * (ndoors - 1)) / ndoors
    xs = [(x0 + 2.5 + k * (dw + 3), x0 + 2.5 + k * (dw + 3) + dw) for k in range(ndoors)]
    fz0, fz1 = zf - 16, zf
    sections = [(x0, x1)]
    if part_after is not None:
        xj = (xs[part_after][1] + xs[part_after + 1][0]) / 2
        xp = xj - 8
        d.add(box=[xp, yb, RAIL[0], xp + 16, yt, zf - 17], pid="partition", grain="y", mat="inner")
        sections = [(x0, xp), (xp + 16, x1)]
    for k, (a, b) in enumerate(sections):
        back(d, None, [a - 5 if k == 0 else a - 8, yb - 4, BZ0, b + 5 if k == len(sections) - 1 else b + 8, yt + 4, BZ1], pid=f"back-{k + 1}")
        if k == 0:
            d.add(box=[a + 1, 1760, 30, b - 1, 1776, 30 + 520], pid=f"hat-shelf-{k + 1}", mat="inner")
            rail(d, f"rail-{k + 1}", a + 1, b - 1, 1705, 300)
            d.add(box=[a + 1, 600, 30, b - 1, 616, 30 + 520], pid=f"shelf-{k + 1}", mat="inner")
        else:
            shelves(d, f"shelf-{k + 1}", a + 1, b - 1, [380, 720, 1060, 1400, 1760], 30, 30 + 520, mat="inner")
    band = (552, 1060)
    for k, (a, b) in enumerate(xs):
        ids = door3(d, f"door-{k + 1}", a, b, yb + 2, yt - 2, fz0, fz1, band)
        hx = b - 103 if handle_edge[k] == "r" else a + 103
        ids.append(bar(d, f"h-{k + 1}", hx, band[1] - 40, fz1))
        d.move(type="door", name=f"door_{k + 1}", parts=ids, hinge=hinges[k], angle=105)
    return d.write()


def sliding_door(d, tag, x0, x1, y0, y1, z0, band, lower="body", mid="front", upper="body", grain="x", mirror=False):
    """A coupe door: aluminium vertical profiles (18 wide, 22 deep) on both edges round a 16 mm panel of oak / black /
    oak (or a mirror)."""
    ids = []
    ids.append(d.add(box=[x0, y0, z0, x0 + 18, y1, z0 + 22], pid=f"{tag}-alu-l", mat=ALU, edge=1))
    ids.append(d.add(box=[x1 - 18, y0, z0, x1, y1, z0 + 22], pid=f"{tag}-alu-r", mat=ALU, edge=1))
    a, b = x0 + 18, x1 - 18
    ids.append(d.add(box=[a, y0, z0, b, y0 + 12, z0 + 22], pid=f"{tag}-alu-b", mat=ALU, edge=1))
    ids.append(d.add(box=[a, y1 - 12, z0, b, y1, z0 + 22], pid=f"{tag}-alu-t", mat=ALU, edge=1))
    pz0, pz1 = z0 + 3, z0 + 19
    yA, yB = y0 + 12, y1 - 12
    if mirror:
        ids.append(front(d, None, [a, yA, pz0, b, yB, pz1 - 4], pid=f"{tag}-base", mat="front"))
        ids.append(d.add(box=[a, yA, pz1 - 4, b, yB, pz1], pid=f"{tag}-mirror", kind="mirror"))
        return ids
    if band is None:
        ids.append(front(d, None, [a, yA, pz0, b, yB, pz1], pid=f"{tag}-panel", mat=upper, grain=grain))
        return ids
    ids.append(front(d, None, [a, yA, pz0, b, band[0], pz1], pid=f"{tag}-lo", mat=lower, grain=grain))
    if band[1] is None:
        ids.append(front(d, None, [a, band[0], pz0, b, yB, pz1], pid=f"{tag}-up", mat=upper, grain=grain))
    else:
        ids.append(front(d, None, [a, band[0], pz0, b, band[1], pz1], pid=f"{tag}-band", mat=mid, grain="x"))
        ids.append(front(d, None, [a, band[1], pz0, b, yB, pz1], pid=f"{tag}-up", mat=upper, grain=grain))
    return ids


def m1_11():
    """Шкаф-купе 2018 × 670 × 2161: an oak portal (sides and top) round a white interior, two sliding doors of oak with a
    black band in aluminium profiles."""
    W, B, H = 2018, 670, 2161
    d = D(f"{SLUG}-1-11", [W, B, H])
    d.add(box=[0, 0, 0, T, H, B], pid="side-l", grain="y")
    d.add(box=[W - T, 0, 0, W, H, B], pid="side-r", grain="y")
    d.add(box=[T, H - T, 0, W - T, H, B], pid="top", grain="x")
    d.add(box=[T, 70, 0, W - T, 95, 600], pid="bottom", mat="inner")
    d.add(box=[T, 0, 570, W - T, 70, 595], pid="plinth", grain="x")
    xm = W / 2
    d.add(box=[xm - 12.5, 95, RAIL[0], xm + 12.5, H - T, 600], pid="partition", mat="inner", grain="y")
    back(d, None, [T - 5, 91, BZ0, xm - 12.5 + 5, H - T + 4, BZ1], pid="back-l")
    back(d, None, [xm + 12.5 - 5, 91, BZ0, W - T + 5, H - T + 4, BZ1], pid="back-r")
    for k, (a, b) in enumerate(((T, xm - 12.5), (xm + 12.5, W - T))):
        d.add(box=[a + 1, 1830, 30, b - 1, 1846, 580], pid=f"hat-shelf-{k + 1}", mat="inner")
        rail(d, f"rail-{k + 1}", a + 1, b - 1, 1775, 300)
    d.add(box=[T + 1, 520, 30, xm - 13.5, 536, 580], pid="shelf-l", mat="inner")
    # doors: the left one on the front track, the right one on the rear; 40 mm overlap
    inner = W - 2 * T
    dw = (inner + 40) / 2
    band = (598, 1088)
    fl = sliding_door(d, "door-l", T, T + dw, 100, 2126, 636, band)
    fr = sliding_door(d, "door-r", W - T - dw, W - T, 100, 2126, 610, band)
    d.move(type="slide", name="door_left", parts=fl, by=[R(dw - 40), 0, 0])
    d.move(type="slide", name="door_right", parts=fr, by=[R(-(dw - 40)), 0, 0])
    return d.write()


def coupe(did, W, ndoors, mirror_mid=False):
    """Шкаф-купе 2292 × 650 (1.40 / 1.41 / 1.43): oak carcass with the sides to the floor, plinth 100, doors of oak over a
    black lower third (vertical grain) in aluminium profiles, the middle door of 1.43 a mirror."""
    B, H = 650, 2292
    d = D(did, [W, B, H])
    d.add(box=[0, 0, 0, T, H - T, B], pid="side-l", grain="y")
    d.add(box=[W - T, 0, 0, W, H - T, B], pid="side-r", grain="y")
    d.add(box=[0, H - T, 0, W, H, B], pid="top", grain="x")
    d.add(box=[T, 75, 0, W - T, 100, 580], pid="bottom", grain="x")
    d.add(box=[T, 0, 555, W - T, 75, 580], pid="plinth", grain="x")
    inner = W - 2 * T
    parts_x = [T + inner / ndoors * k for k in range(1, ndoors)] if ndoors == 3 else [T + inner * 0.62]
    secs = []
    prev = T
    for i, xp in enumerate(parts_x):
        d.add(box=[xp - 8, 100, RAIL[0], xp + 8, H - T, 560], pid=f"partition-{i + 1}", grain="y")
        secs.append((prev, xp - 8))
        prev = xp + 8
    secs.append((prev, W - T))
    for k, (a, b) in enumerate(secs):
        back(d, None, [a - 5, 96, BZ0, b + 5, H - T + 4, BZ1], pid=f"back-{k + 1}")
        hanging = (ndoors == 2 and k == 0) or (ndoors == 3 and k != 1)
        if hanging:
            d.add(box=[a + 1, 1900, 30, b - 1, 1916, 530], pid=f"hat-shelf-{k + 1}", mat="body")
            rail(d, f"rail-{k + 1}", a + 1, b - 1, 1845, 290)
            d.add(box=[a + 1, 420, 30, b - 1, 436, 530], pid=f"shelf-{k + 1}-lo", mat="body")
        else:
            shelves(d, f"shelf-{k + 1}", a + 1, b - 1, [420, 740, 1060, 1380, 1700, 1960], 30, 530)
    ov = 30
    dw = (inner + ov * (ndoors - 1)) / ndoors
    band = (925, None)   # lower black to 925, oak above
    y0, y1 = 102, 2257
    if ndoors == 2:
        fl = sliding_door(d, "door-l", T, T + dw, y0, y1, 616, band, lower="front", grain="y")
        fr = sliding_door(d, "door-r", W - T - dw, W - T, y0, y1, 590, band, lower="front", grain="y")
        d.move(type="slide", name="door_left", parts=fl, by=[R(dw - ov), 0, 0])
        d.move(type="slide", name="door_right", parts=fr, by=[R(-(dw - ov)), 0, 0])
    else:
        xa = [T + k * (dw - ov) for k in range(3)]
        fl = sliding_door(d, "door-l", xa[0], xa[0] + dw, y0, y1, 590, band, lower="front", grain="y")
        fm = sliding_door(d, "door-m", xa[1], xa[1] + dw, y0, y1, 616, band, lower="front", grain="y", mirror=mirror_mid)
        fr = sliding_door(d, "door-r", xa[2], xa[2] + dw, y0, y1, 590, band, lower="front", grain="y")
        d.move(type="slide", name="door_left", parts=fl, by=[R(dw - ov), 0, 0])
        d.move(type="slide", name="door_middle", parts=fm, by=[R(-(dw - ov)), 0, 0])
        d.move(type="slide", name="door_right", parts=fr, by=[R(-(dw - ov)), 0, 0])
    return d.write()


# ============================================================================================ cut lists (read off the pictures)
CUTLISTS = {
    "3-31": ("П3.0556.3.31", "IS-P570-01-shkaf-1.pdf", [
        ("1", "70.01.01", "Стенка вертикальная (ЛДСП 25мм ДУБ ВОТАН)", 1730, 398, 25, 1),
        ("2", "70.01.02", "Стенка вертикальная (ЛДСП 25мм ДУБ ВОТАН)", 1730, 398, 25, 1),
        ("3", "70.01.03", "Крышка (ЛДСП 25мм ДУБ ВОТАН)", 704, 400, 25, 1),
        ("4", "70.01.04", "Дно (ЛДСП 25мм ДУБ ВОТАН)", 704, 400, 25, 1),
        ("5", "70.01.05", "Щит двери (ЛДСП 16мм ДУБ ВОТАН)", 321, 748, 16, 1),
        ("6", "70.01.06", "Щит двери (ЛДСП 16мм ДУБ ВОТАН)", 321, 748, 16, 1),
        ("7", "70.01.07", "Стенка горизонтальная (ЛДСП 16мм ДУБ ВОТАН)", 650, 359, 16, 1),
        ("8", "70.01.08", "Стенка горизонтальная (ЛДСП 16мм ДУБ ВОТАН)", 650, 359, 16, 1),
        ("9", "70.01.09", "Щит двери (ЛДСП 16мм ДУБ ВОТАН)", 321, 698, 16, 1),
        ("10", "70.01.10", "Щит двери (ЛДСП 16мм ДУБ ВОТАН)", 321, 698, 16, 1),
        ("11", "70.01.11", "Полка (ЛДСП 16мм ДУБ ВОТАН)", 648, 339, 16, 4),
        ("12", "70.01.12", "Брусок (ЛДСП 16мм ДУБ ВОТАН)", 128, 650, 16, 1),
        ("14", "70.01.14", "Стенка задняя (ДВП ламинированная БЕЛАЯ)", 869, 660, None, 2),
        ("15", "70.01.15", "Щит двери (ЛДСП 16мм ЧЕРНЫЙ)", 321, 280, 16, 1),
        ("16", "70.01.16", "Щит двери (ЛДСП 16мм ЧЕРНЫЙ)", 321, 280, 16, 1)]),
    "3-33": ("П3.0556.3.33", "IS-P570-03-tumba-1.pdf", [
        ("1", "70.03.01", "Мягкий элемент", 494, 390, None, 1),
        ("2", "70.03.02", "Дно (ЛДСП 25мм ДУБ ВОТАН)", 504, 400, 25, 1),
        ("3", "70.03.03", "Крышка (ЛДСП 25мм ДУБ ВОТАН)", 504, 400, 25, 1),
        ("4", "70.03.04", "Стенка вертикальная (ЛДСП 25мм ДУБ ВОТАН)", 280, 398, 25, 1),
        ("5", "70.03.05", "Стенка вертикальная (ЛДСП 25мм ДУБ ВОТАН)", 280, 398, 25, 1),
        ("6", "70.03.06", "Полка (ЛДСП 16мм ДУБ ВОТАН)", 448, 339, 16, 1),
        ("7", "70.03.07", "Дверь откидная (ЛДСП 16мм ЧЕРНЫЙ 660 WML)", 446, 276, 16, 1),
        ("8", "70.03.08", "Стенка задняя (ДВП ламинированная БЕЛАЯ)", 290, 460, None, 1)]),
    "3-34": ("П3.0556.3.34", "IS-P570-04-zerkalo-navesnoe-1.pdf", [
        ("1", "70.04.01", "Стенка вертикальная (ЛДСП 16мм ДУБ ВОТАН)", 900, 750, 16, 1),
        ("2", "-----", "Зеркало (уже приклеено)", 701, 791, None, 1),
        ("3", "70.04.03", "Полка (ЛДСП 16мм ЧЕРНЫЙ 660 WML)", 860, 144, 16, 1)]),
    "3-35": ("П3.0556.3.35", "IS-P570-05-tumba-dlya-obuvi-1.pdf", [
        ("1", "70.05.01", "Стенка вертикальная (ЛДСП 25мм ДУБ ВОТАН)", 980, 398, 25, 1),
        ("2", "70.05.02", "Стенка вертикальная (ЛДСП 25мм ДУБ ВОТАН)", 980, 398, 25, 1),
        ("3", "70.05.03", "Крышка (ЛДСП 25мм ДУБ ВОТАН)", 904, 400, 25, 1),
        ("4", "70.05.04", "Дно (ЛДСП 25мм ДУБ ВОТАН)", 904, 400, 25, 1),
        ("5", "70.05.05", "Стенка горизонтальная (ЛДСП 16мм ДУБ ВОТАН)", 850, 359, 16, 1),
        ("6", "70.05.06", "Дверь (ЛДСП 16мм ДУБ ВОТАН)", 421, 696, 16, 1),
        ("7", "70.05.07", "Дверь (ЛДСП 16мм ДУБ ВОТАН)", 421, 696, 16, 1),
        ("8", "70.05.08", "Полка (ЛДСП 16мм ДУБ ВОТАН)", 848, 339, 16, 1),
        ("9", "70.05.09", "Стенка задняя ящика (ЛДСП 16мм ДУБ ВОТАН)", 792.6, 77, 16, 2),
        ("10", "70.05.10", "Стенка боковая ящика (ЛДСП 16мм ДУБ ВОТАН)", 300, 96, 16, 2),
        ("11", "70.05.11", "Стенка боковая ящика (ЛДСП 16мм ДУБ ВОТАН)", 300, 96, 16, 2),
        ("12", "70.05.12", "Стенка передняя (ЛДСП 16мм ЧЕРНЫЙ 660 WML)", 846, 136, 16, 2),
        ("14", "70.05.14", "Стенка задняя (ДВП ламинированная БЕЛАЯ)", 860, 516, None, 1),
        ("15", "70.05.15", "Стенка задняя (ДВП ламинированная БЕЛАЯ)", 860, 472, None, 1),
        ("16", "70.05.16", "Дно ящика (ДВП ламинированная БЕЛАЯ)", 804, 305, None, 2)]),
}


def write_cutlists():
    for tail, (code, pdf, rows) in CUTLISTS.items():
        out = {"code": code, "is": pdf,
               "source": f"page image reference/{SLUG}/pages/{SLUG}-{tail}-p1.png (the instruction has no text layer): table "
                         "«Поз., Наименование, Маркировка, Материал, Кол-во, Длина × Ширина»; the thickness is the "
                         "material's (ЛДСП 25 / 16); ДВП, the mirror and the cushion are compared by two sizes",
               "rows": []}
        for n, mark, name, a, b, t, c in rows:
            out["rows"].append({"n": n, "code": mark, "name": name, "size": [a, b] + ([t] if t else []), "count": c})
        with open(os.path.join(HERE, "cutlists", f"{SLUG}-{tail}.json"), "w") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=1)


# ============================================================================================================== catalogue
VOTAN = "door_enamel_whitey#9f836e"
BLACK = "door_enamel_whitey#26252b"

MODELS = [
    # id tail, code, name, category, size, page, extra
    ("0-01", "П3.0556.0.01", "Полка навесная «Блэквуд Лофт»", "living", [1600, 285, 375], 79, {"mount": "wall"}),
    ("0-02", "П3.0556.0.02", "Стол журнальный «Блэквуд Лофт»", "tables", [1100, 600, 445], 79, {}),
    ("0-03", "П3.0556.0.03", "Тумба ТВ «Блэквуд Лофт»", "living", [1600, 455, 575], 79, {}),
    ("0-04", "П3.0556.0.04", "Шкаф-витрина «Блэквуд Лофт»", "living", [700, 400, 1900], 79, {"note": "стекло бронза, с подсветкой"}),
    ("0-05", "П3.0556.0.05", "Тумба «Блэквуд Лофт»", "living", [1200, 400, 1274], 79, {}),
    ("0-07", "П3.0556.0.07", "Тумба «Блэквуд Лофт»", "living", [1773, 455, 780], 79, {}),
    ("4-06", "П3.0556.4.06", "Стол обеденный «Блэквуд Лофт»", "tables", [1402, 802, 750], 79, {"note": "металлические опоры"}),
    ("4-12", "П3.0556.4.12", "Стол обеденный раздвижной «Блэквуд Лофт»", "tables", [1302, 902, 770], 79,
     {"note": "раздвижной: L1302 / 1802 (построен сложенным; вставка 500 не показана)"}),
    ("1-11", "П3.0556.1.11", "Шкаф-купе «Блэквуд Лофт»", "bedroom", [2018, 670, 2161], 80, {}),
    ("1-12", "П3.0556.1.12", "Комод для шкафа-купе «Блэквуд Лофт»", "bedroom", [935, 557, 727], 80,
     {"note": "только для отделения шкафа-купе П3.0556.1.11"}),
    ("1-13", "П3.0556.1.13", "Полка для шкафа-купе «Блэквуд Лофт»", "bedroom", [935, 520, 16], 80,
     {"note": "только для отделения шкафа-купе П3.0556.1.11"}),
    ("1-14", "П3.0556.1.14", "Комод «Блэквуд Лофт»", "bedroom", [1200, 450, 905], 80, {}),
    ("1-16", "П3.0556.1.16", "Тумба прикроватная «Блэквуд Лофт»", "bedroom", [500, 400, 480], 80, {}),
    ("1-17", "П3.0556.1.17", "Тумба прикроватная «Блэквуд Лофт»", "bedroom", [500, 400, 635], 80, {"note": "с нишей"}),
    ("1-18", "П3.0556.1.18", "Комод «Блэквуд Лофт»", "bedroom", [800, 450, 1150], 80, {}),
    ("1-19", "П3.0556.1.19", "Комод «Блэквуд Лофт»", "bedroom", [1400, 450, 905], 80, {}),
    ("1-20", "П3.0556.1.20", "Кровать 1-08 «Блэквуд Лофт»", "bedroom", [950, 2120, 890], 80, {"note": "сп. место 2000×800"}),
    ("1-21", "П3.0556.1.21", "Кровать 1-09 с металлокаркасом «Блэквуд Лофт»", "bedroom", [1050, 2120, 890], 80, {"note": "сп. место 2000×900"}),
    ("1-22", "П3.0556.1.22", "Кровать 1-12 «Блэквуд Лофт»", "bedroom", [1350, 2120, 890], 80, {"note": "сп. место 2000×1200"}),
    ("1-23", "П3.0556.1.23", "Кровать 2-14 «Блэквуд Лофт»", "bedroom", [1550, 2120, 890], 80, {"note": "сп. место 2000×1400"}),
    ("1-24", "П3.0556.1.24", "Кровать 2-16 с металлокаркасом «Блэквуд Лофт»", "bedroom", [1750, 2120, 890], 80, {"note": "сп. место 2000×1600"}),
    ("1-25", "П3.0556.1.25", "Кровать 2-18 «Блэквуд Лофт»", "bedroom", [1950, 2120, 890], 80, {"note": "сп. место 2000×1800"}),
    ("1-26", "П3.0556.1.26", "Зеркало «Блэквуд Лофт»", "decor", [1068, 85, 801], 80, {"mount": "wall"}),
    ("1-27", "П3.0556.1.27", "Шкаф для одежды 2д «Блэквуд Лофт»", "bedroom", [954, 600, 2110], 80, {}),
    ("1-28", "П3.0556.1.28", "Шкаф для одежды 3д «Блэквуд Лофт»", "bedroom", [1404, 600, 2110], 80, {}),
    ("1-29", "П3.0556.1.29", "Шкаф для одежды 4д «Блэквуд Лофт»", "bedroom", [1854, 600, 2110], 80, {}),
    ("1-40", "П3.0556.1.40", "Шкаф-купе 2д «Блэквуд Лофт»", "bedroom", [1529, 650, 2292], 80, {"note": "без зеркала"}),
    ("1-41", "П3.0556.1.41", "Шкаф-купе 3д «Блэквуд Лофт»", "bedroom", [2027, 650, 2292], 80, {"note": "без зеркала"}),
    ("1-43", "П3.0556.1.43", "Шкаф-купе 3д «Блэквуд Лофт» с зеркалом", "bedroom", [2027, 650, 2292], 80, {"note": "с зеркалом"}),
    ("3-31", "П3.0556.3.31", "Шкаф 2д для прихожей «Блэквуд Лофт»", "hall", [704, 400, 1900], 79, {"is": "IS-P570-01-shkaf-1.pdf"}),
    ("3-32", "П3.0556.3.32", "Вешалка «Блэквуд Лофт»", "hall", [500, 256, 1780], 79, {"mount": "wall"}),
    ("3-33", "П3.0556.3.33", "Тумба «Блэквуд Лофт»", "hall", [504, 400, 480], 79,
     {"is": "IS-P570-03-tumba-1.pdf", "note": "с мягким сиденьем"}),
    ("3-34", "П3.0556.3.34", "Зеркало навесное «Блэквуд Лофт»", "hall", [900, 160, 750], 79,
     {"is": "IS-P570-04-zerkalo-navesnoe-1.pdf", "mount": "wall",
      "note": "каталог: H700; по инструкции щит 900×750 — построено по инструкции"}),
    ("3-35", "П3.0556.3.35", "Тумба для обуви «Блэквуд Лофт»", "hall", [904, 400, 1150], 79, {"is": "IS-P570-05-tumba-dlya-obuvi-1.pdf"}),
]


def write_catalog():
    models = []
    for tail, code, name, cat, size, page, extra in MODELS:
        m = {"id": f"{SLUG}-{tail}", "code": code, "name": name, "collection": SLUG, "category": cat, "size": size}
        if "is" in extra:
            m["is"] = extra["is"]
        m["page"] = page
        if "mount" in extra:
            m["mount"] = extra["mount"]
        note = extra.get("note")
        if "is" not in extra:
            note = (note + "; " if note else "") + "по каталогу и фото, без инструкции"
        if note:
            m["note"] = note
        models.append(m)
    frag = {
        "finishes": [
            {"id": f"{SLUG}-votan-cherny", "name": "Дуб Вотан / Черный", "body": VOTAN, "front": BLACK,
             "back": "door_enamel_whitey#f1f0ec",
             "roles": {"inner": "door_enamel_whitey#eeeeeb", "fabric": "velvet#5a544d"}, "swatch": "#9f836e"}],
        "profiles": {},
        "collections": [
            {"id": SLUG, "name": "Блэквуд Лофт", "brand": "Пинскдрев", "finishes": [f"{SLUG}-votan-cherny"], "metal": "black",
             "note": "Каталог «Корпусная мебель ч. II» 2025, PDF с. 75–80 (каталог 146–157); инструкции П570.01/03/04/05 "
                     "(прихожая 3.31/3.33/3.34/3.35). Корпус ЛДСП 25 «Дуб Вотан»: крышка и дно во всю ширину и глубину, "
                     "боковины между ними с отступом 2 мм; внутренние детали ЛДСП 16; фасады ЛДСП 16 вкладные, "
                     "заподлицо с боковинами, «Черный 660 WML» и дуб; двери шкафов из трёх щитов (дуб / чёрная полоса / "
                     "дуб); задние стенки ДВП белые в пазах; угловые металлические опоры 120 мм; ручки-скобы OZKM 5132 "
                     "чёрные; шкафы-купе с алюминиевыми профилями."}],
        "models": models,
    }
    with open(os.path.join(HERE, f"{SLUG}_catalog.json"), "w") as fh:
        json.dump(frag, fh, ensure_ascii=False, indent=1)


def main():
    write_cutlists()
    write_catalog()
    out = [m3_31(), m3_32(), m3_33(), m3_34(), m3_35(),
           m0_01(), m0_02(), m0_03(), m0_04(), m0_05(), m0_07(), m4_06(), m4_12(),
           m1_11(), m1_12(), m1_13(), m1_26(),
           chest(f"{SLUG}-1-14", 1200, 450, 905, 2, 3, door_cols=(1,), hinge="right", handle_off=True),
           chest(f"{SLUG}-1-16", 500, 400, 480, 1, 2),
           chest(f"{SLUG}-1-17", 500, 400, 635, 1, 2, niche=141),
           chest(f"{SLUG}-1-18", 800, 450, 1150, 1, 4),
           chest(f"{SLUG}-1-19", 1400, 450, 905, 2, 3),
           wardrobe(f"{SLUG}-1-27", 954, 2, None, ["left", "right"], ["r", "l"]),
           wardrobe(f"{SLUG}-1-28", 1404, 3, 1, ["left", "right", "right"], ["r", "l", "l"]),
           wardrobe(f"{SLUG}-1-29", 1854, 4, 1, ["left", "right", "left", "right"], ["r", "l", "r", "l"]),
           coupe(f"{SLUG}-1-40", 1529, 2), coupe(f"{SLUG}-1-41", 2027, 3), coupe(f"{SLUG}-1-43", 2027, 3, mirror_mid=True)]
    for tail, w in (("1-20", 800), ("1-21", 900), ("1-22", 1200), ("1-23", 1400), ("1-24", 1600), ("1-25", 1800)):
        out.append(bed(f"{SLUG}-{tail}", w))
    for p in out:
        print(os.path.relpath(p, os.path.join(HERE, "..", "..", "..")))


if __name__ == "__main__":
    main()
