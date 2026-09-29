"""Skay (П6.112.0.*): top and bottom run the full width, the sides stand between them; the carcass (depth 420) stands on
metal tube legs 180 mm (опора «j»); every front is ЛДСП 16 inset flush in the carcass (z 404–420) with ~2.5 mm gaps;
partitions: the full-depth one (404, to the back) closes the drawer / niche column, the one between two doors starts in
front of the backs (388); backs ХДФ 3.5 in grooves (~6 mm) behind every section; drawer boxes on 350 runners with 14 mm
per side; gold knobs.
"""
from common import dump, drawer_box

D = 420
ZF0 = D - 16          # the fronts' back face: fronts are inset flush with the carcass
LEG = 180
Y0 = LEG + 16         # top face of the bottom
ZB0, ZB1 = 8, 11.5    # backs in grooves


def carcass(w, h_in, ns=("1", "2", "3", "4")):
    """Top and bottom w × 420 over and under the sides h_in × 420. ns: top, bottom, left side, right side."""
    y1 = Y0 + h_in
    return [{"n": ns[0], "box": [0, y1, 0, w, y1 + 16, D]},
            {"n": ns[1], "box": [0, LEG, 0, w, Y0, D]},
            {"n": ns[2], "box": [0, Y0, 0, 16, y1, D]},
            {"n": ns[3], "box": [w - 16, Y0, 0, w, y1, D]}]


def legs(xs_front, xs_back, zf=380, zb=40, d=22):
    out = []
    for k, (x, z) in enumerate([(x, zf) for x in xs_front] + [(x, zb) for x in xs_back]):
        out.append({"id": f"j-{k + 1}", "kind": "tube", "mat": "metal",
                    "box": [x - d / 2, 0, z - d / 2, x + d / 2, LEG, z + d / 2], "covers": ["j"]})
    return out


def knob(kid, x, y):
    return {"id": kid, "kind": "handle", "model": "knob", "at": [x, y], "d": 30, "t": 10, "standoff": 18, "z": D,
            "covers": ["k"]}


def front(n, x0, x1, y0, y1, pid=None):
    p = {"n": n, "kind": "front", "box": [x0, y0, ZF0, x1, y1, D]}
    if pid:
        p["id"] = pid
    return p


def back(n, x0, x1, y0, y1, pid=None):
    p = {"n": n, "kind": "back", "box": [x0, y0, ZB0, x1, y1, ZB1]}
    if pid:
        p["id"] = pid
    return p


def drawer(tag, nf, nb, fx0, fx1, fy0, fh, bx0, bx1, knob_down, moves):
    """A drawer: front fx0..fx1 × fy0..fy0+fh, box bx0..bx1 (200 high, 350 deep, 20 above the front's bottom)."""
    fid = f"{nf}-{tag}"
    box = drawer_box(tag, bx0, bx1, fy0 + 20, 200, ZF0 - 350, ZF0, n=nb)
    k = knob(f"k-{tag}", (fx0 + fx1) / 2, fy0 + fh - knob_down)
    moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": [fid] + [q["id"] for q in box] + [k["id"]], "travel": 300})
    return [front(nf, fx0, fx1, fy0, fy0 + fh, fid)] + box + [k]


def shelf(n, pid, x0, x1, y, depth=378):
    return {"n": n, "id": pid, "box": [x0, y, 20, x1, y + 16, 20 + depth]}


# ------------------------------------------------------------------------------------------------------------ modules
def low(w, h_in, did, ns, drawers):
    """0.02 / 0.03: two inset doors (left) and a drawer column (right) behind a full-depth partition.
    ns: numbers of the door partition, the column partition, the door shelves, doors, backs (left, right, column)."""
    n_p_doors, n_p_col, n_shelf, n_door, n_door1, n_b1, n_b2, n_b3 = ns
    p = carcass(w, h_in)
    y1 = Y0 + h_in
    xp1, xp2 = 503, 1006                   # the partition between the doors, the partition of the column
    p += [{"n": n_p_doors, "box": [xp1, Y0, 16, xp1 + 16, y1, ZF0]},
          {"n": n_p_col, "box": [xp2, Y0, 0, xp2 + 16, y1, ZF0]}]
    ym = (Y0 + y1) / 2 - 8
    p += [shelf(n_shelf, f"{n_shelf}-left", 17.5, 501.5, ym), shelf(n_shelf, f"{n_shelf}-right", 520.5, 1004.5, ym)]
    p += [back(n_b1, 10, 509, Y0 - 5, y1 + 5), back(n_b2, 513, 1012, Y0 - 5, y1 + 5), back(n_b3, 1016, w - 10, Y0 - 5, y1 + 5)]
    L, R = (19, 509.5), (512.5, 1003)
    yd0, yd1 = Y0 + 2, y1 - 2
    kd = 42 if h_in < 500 else 35
    p += [front(n_door, *L, yd0, yd1), knob("k-left", L[1] - 37.5, yd1 - kd),
          front(n_door1, *R, yd0, yd1), knob("k-right", R[0] + 37.5, yd1 - kd)]
    moves = [{"type": "door", "name": "door_left", "parts": [n_door, "k-left"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_right", "parts": [n_door1, "k-right"], "hinge": "right", "angle": 105}]
    p += drawers(moves)
    p += legs([40, 746, w - 40], [40, w - 40])
    return dump(did, [w, D, LEG + h_in + 32], p, moves)


def tv_unit():
    """П6.112.0.02 Тумба 1492 × 420 × 610: two doors, an open niche over one drawer."""
    def drawers(moves):
        fy0 = Y0 + 1.5
        return ([{"n": "7", "box": [1022, fy0 + 240 + 1, 16, 1476, fy0 + 240 + 17, ZF0]}] +
                drawer("1", "8.1", ("8.2", "8.3", "8.4", "8.5"), 1024, 1474, fy0, 240, 1035, 1463, 37, moves))
    return low(1492, 398, "skay-0-02", ("6", "5", "9", "10", "10.1", "11", "12", "13"), drawers)


def chest():
    """П6.112.0.03 Тумба 1492 × 420 × 942: two doors, three drawers."""
    def drawers(moves):
        out = []
        for k in range(3):
            fy0 = Y0 + 2.5 + k * 242.5
            out += drawer(str(k + 1), "8.1", ("8.2", "8.3", "8.4", "8.5"), 1024, 1474, fy0, 240, 1035, 1463, 35, moves)
        return out
    return low(1492, 730, "skay-0-03", ("5", "6", "7", "9", "9.1", "10", "11", "12"), drawers)


def cabinet():
    """П6.112.0.01 Шкаф 680 × 420 × 2020: an open shelf column and a door over two drawers."""
    w, h_in = 680, 1808
    y1 = Y0 + h_in
    ys = Y0 + 488                                           # the fixed shelf over the drawers
    p = carcass(w, h_in, ("3", "4", "1", "2"))
    p += [{"n": "5", "box": [17, ys, 0, w - 17, ys + 16, ZF0]},
          {"n": "6", "box": [244, ys + 16, 16, 260, y1, ZF0]}]
    g = (y1 - ys - 16 - 3 * 16) / 4
    for k in range(3):
        y = ys + 16 + g * (k + 1) + 16 * k
        p += [shelf("7", f"7-{k + 1}", 16, 244, y), shelf("8", f"8-{k + 1}", 263, 661, y)]
    p += [back("11", 10, 252, ys + 8, ys + 8 + 1316), back("12", 254, 666, ys + 8, ys + 8 + 1316),
          back("13", 10, 337, Y0 - 8, Y0 - 8 + 500, "13-left"), back("13", 339, 666, Y0 - 8, Y0 - 8 + 500, "13-right")]
    door = (248, 662, ys + 19, ys + 19 + 1298)
    p += [front("9", door[0], door[1], door[2], door[3]), knob("k-door", 273, (door[2] + door[3]) / 2)]
    moves = [{"type": "door", "name": "door", "parts": ["9", "k-door"], "hinge": "right", "angle": 105}]
    for k, fy0 in enumerate((Y0 + 2.5, Y0 + 245.5)):
        p += drawer(str(k + 1), "10.1", ("10.2", "10.3", "10.4", "10.5"), 19, w - 19, fy0, 240, 30, w - 30, 45, moves)
    p += legs([40, w - 40], [40, w - 40])
    return dump("skay-0-01", [w, D, LEG + h_in + 32], p, moves)


def cabinet_2d():
    """П6.112.0.07 Тумба 981 × 420 × 1492: two doors with shelves over one wide drawer."""
    w, h_in = 981.5, 1280
    y1 = Y0 + h_in
    ys = y1 - 1020 - 16                                     # the fixed shelf under the doors
    xp = w / 2 - 8
    p = carcass(w, h_in)
    p += [{"n": "5", "box": [17, ys, 0, w - 17, ys + 16, ZF0]},
          {"n": "6", "box": [xp, ys + 16, 16, xp + 16, y1, ZF0]}]
    g = (1020 - 32) / 3
    for k in range(2):
        y = ys + 16 + g * (k + 1) + 16 * k
        p += [shelf("7", f"7-{2 * k + 1}", 18, 481, y), shelf("7", f"7-{2 * k + 2}", 500.5, 963.5, y)]
    p += [back("10", 9.75, 487.75, ys + 10, ys + 10 + 1032), back("11", 493.75, 971.75, ys + 10, ys + 10 + 1032),
          back("12", 12.25, 969.25, Y0 - 6, Y0 - 6 + 256)]
    L, R = (18.8, 489.3), (492.2, 962.7)
    yd0, yd1 = ys + 18, y1 - 2
    ky = 963
    p += [front("8", *L, yd0, yd1, "8-left"), knob("k-left", L[1] - 36, ky),
          front("8", *R, yd0, yd1, "8-right"), knob("k-right", R[0] + 36, ky)]
    moves = [{"type": "door", "name": "door_left", "parts": ["8-left", "k-left"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_right", "parts": ["8-right", "k-right"], "hinge": "right", "angle": 105}]
    p += drawer("1", "9.1", ("9.2", "9.3", "9.4", "9.5"), 19, w - 19, Y0 + 2, 240, 30, w - 30, 50, moves)
    p += legs([40, w - 40], [40, w - 40])
    return dump("skay-0-07", [w, D, LEG + h_in + 32], p, moves)


if __name__ == "__main__":
    print(cabinet())
    print(tv_unit())
    print(chest())
    print(cabinet_2d())
