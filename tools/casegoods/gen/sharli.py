"""Sharli (П6.116.0.*): the carcass hangs between four corner stiles 80 × 19 (full height, curved inner edge below the
carcass) standing on ФБ482 glides; the bottom and the fixed shelf are notched round the back stiles; backs (ХДФ) are
nailed across the backs of the stiles (9 mm on each); fronts МДФ 19 with vertical reeds between the front stiles; the
glazed doors are frameless glass under a fluted strip that hides its top 63 mm; top 16 in «Шарли керамика» with rounded
front corners.

z: back 0–3, back stiles 3–22, sides 22–388, front stiles and fronts 388–407 (= B 407).
"""
from common import dump, drawer_box

B = 407
ZB, ZS0, ZS1, ZF = 3, 22, 388, 407      # back face of the back stiles, the sides' depth, the front plane
LEG_W, LEG_T, GLIDE = 80, 19, 4
CB = 204                                 # underside of the carcass (sides and bottom)
FLUTE = {"type": "fluted", "dir": "y", "pitch": 32, "depth": 4, "flute": "reed", "gap": 3}


def top(w, h):
    r = 30
    return {"n": "2", "mat": "top", "box": [0, h - 16, 0, w, h, B], "shape": "path",
            "outline": f"M 0 0 L {w} 0 L {w} {B - r} Q {w} {B} {w - r} {B} L {r} {B} Q 0 {B} 0 {B - r} Z"}


def stile(n, x_outer, z0, h_top, side):
    """A corner stile: 80 wide, full height from the glide to under the top; below the carcass its inner edge rounds
    in (r ≈ 29) and tapers to 42 mm at the floor. side = +1 for a left stile (inner edge at larger x), -1 for a right."""
    s = side
    xo, xi = x_outer, x_outer + s * LEG_W
    x0, x1 = sorted([xo, xi])
    outline = (f"M {xo} {GLIDE} L {xo + s * 42} {GLIDE} L {xo + s * 57} 175 Q {xo + s * 57} {CB} {xi} {CB} "
               f"L {xi} {h_top} L {xo} {h_top} Z")
    return {"n": n, "box": [x0, GLIDE, z0, x1, h_top, z0 + LEG_T], "shape": "path", "outline": outline}


def stiles(w, h_top, ns):
    """ns: numbers of the front-left, front-right, back-left, back-right stiles."""
    fl, fr, bl, br = ns
    return [stile(fl, 5, ZS1, h_top, 1), stile(fr, w - 5, ZS1, h_top, -1),
            stile(bl, 5, ZB, h_top, 1), stile(br, w - 5, ZB, h_top, -1)]


def glide(gid, x, z):
    return {"id": gid, "kind": "tube", "mat": "black", "box": [x - 10, 0, z - 10, x + 10, GLIDE, z + 10], "covers": ["c"]}


def corner_glides(w):
    zs = [ZB + LEG_T / 2, ZS1 + LEG_T / 2]
    xs = [5 + 21, w - 5 - 21]
    return [glide(f"c-{i + 1}", x, z) for i, (x, z) in enumerate((x, z) for z in zs for x in xs)]


def cone_leg(k, x, z=200):
    """Опора «m»: a tapered turned leg under the bottom, on its own glide."""
    return [{"id": f"m-{k}", "kind": "rod", "mat": "body", "from": [x, CB, z], "to": [x, GLIDE, z], "d": 50, "d2": 34,
             "covers": ["m"]},
            glide(f"c-m{k}", x, z)]


def notched(n, w, y0, depth):
    """Bottom / fixed shelf between the sides (x 21 … w-21) from the back plane, notched round the back stiles."""
    x0, x1, z1 = 21, w - 21, ZB + depth
    xi0, xi1 = 5 + LEG_W, w - 5 - LEG_W
    outline = (f"M {xi0} {ZB} L {xi1} {ZB} L {xi1} {ZS0} L {x1} {ZS0} L {x1} {z1} L {x0} {z1} L {x0} {ZS0} "
               f"L {xi0} {ZS0} Z")
    return {"n": n, "box": [x0, y0, ZB, x1, y0 + 16, z1], "shape": "path", "outline": outline}


def sides(w, h_top):
    return [{"n": "1", "id": "1-left", "box": [5, CB, ZS0, 21, h_top, ZS1]},
            {"n": "1", "id": "1-right", "box": [w - 21, CB, ZS0, w - 5, h_top, ZS1]}]


def handle(hid, x, y):
    return {"id": hid, "kind": "handle", "model": "bar", "at": [x, y], "dir": "up", "d": 36, "band": 12, "t": 6,
            "standoff": 6, "z": ZF, "covers": ["k"]}


def front(n, x0, x1, y0, y1, pid=None):
    p = {"n": n, "kind": "front", "box": [x0, y0, ZS1, x1, y1, ZF], "face": FLUTE}
    if pid:
        p["id"] = pid
    return p


def glass_door(tag, n_strip, n_glass, x0, x1, y0, h_glass, y_top):
    """Frameless glass (4 mm) behind the front plane with a fluted strip 150 over its top 63 mm; they open together."""
    return [front(n_strip, x0, x1, y_top - 150, y_top),
            {"n": n_glass, "id": f"{n_glass}-{tag}", "kind": "glass", "box": [x0 + 1, y0, ZS1 - 4, x1 - 1, y0 + h_glass, ZS1]}]


# ------------------------------------------------------------------------------------------------------------ modules
def cabinet():
    """П6.116.0.01-01 Шкаф 614 × 407 × 2004: glass door over a fluted door, fixed shelf, glass shelves."""
    w, h = 614, 2004
    ht = h - 16
    p = [top(w, h)] + sides(w, ht) + stiles(w, ht, ("10", "11", "12", "13"))
    p += [notched("3", w, CB, 385.5), notched("4", w, 901, 380.5),
          {"n": "5", "box": [22, 543, 25, 592, 559, 375]},
          {"n": "6", "id": "6-1", "kind": "glass", "box": [22, 1272, 25, 592, 1278, 375]},
          {"n": "6", "id": "6-2", "kind": "glass", "box": [22, 1633, 25, 592, 1639, 375]},
          {"n": "8", "kind": "back", "box": [76, CB, 0, 538, CB + 705, ZB]},
          {"n": "9", "kind": "back", "box": [76, CB + 705, 0, 538, CB + 705 + 1077, ZB]}]
    x0, x1 = 87, 527
    p.append(front("7", x0, x1, 206, 961))
    p.append(handle("k-door", x1 - 46, 961 - 54))
    p += glass_door("1", "7.1", "7.2", x0, x1, 964, 935, ht - 2)
    p += corner_glides(w)
    moves = [{"type": "door", "name": "door", "parts": ["7", "k-door"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "glass_door", "parts": ["7.1", "7.2-1"], "hinge": "left", "angle": 105}]
    return dump("sharli-0-01-01", [w, B, h], p, moves)


def tv_unit():
    """П6.116.0.02 Тумба 1500 × 407 × 563: two fluted doors round two drawers, shelves, two turned legs in between."""
    w, h = 1500, 563
    ht = h - 16
    p = [top(w, h)] + sides(w, ht) + stiles(w, ht, ("9", "10", "11", "12"))
    p += [notched("3", w, CB, 385.5),
          {"n": "4", "box": [520, 220, ZB, 536, ht, ZB + 380]},
          {"n": "5", "box": [964, 220, ZB, 980, ht, ZB + 380]},
          {"n": "6", "id": "6-left", "box": [22, 375, 25, 519, 391, 375]},
          {"n": "6", "id": "6-right", "box": [981, 375, 25, 1478, 391, 375]},
          {"n": "13", "id": "13-left", "kind": "back", "box": [76, CB, 0, 526, CB + 345, ZB]},
          {"n": "14", "kind": "back", "box": [529, CB, 0, 971, CB + 345, ZB]},
          {"n": "13", "id": "13-right", "kind": "back", "box": [974, CB, 0, 1424, CB + 345, ZB]}]
    p.append(front("7", 87.5, 527.5, 206, 545, "7-left"))
    p.append(handle("k-left", 527.5 - 46, 380))
    p.append(front("7", 972.5, 1412.5, 206, 545, "7-right"))
    p.append(handle("k-right", 972.5 + 46, 380))
    moves = [{"type": "door", "name": "door_left", "parts": ["7-left", "k-left"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_right", "parts": ["7-right", "k-right"], "hinge": "right", "angle": 105}]
    for tag, y0 in (("top", 377), ("bottom", 206)):
        fid = f"8.1-{tag}"
        box = drawer_box(tag, 549.5, 950.5, y0 + 23, 124, ZS1 - 350, ZS1, n=("8.2", "8.3", "8.4", "8.5"))
        hid = f"k-{tag}"
        p += [front("8.1", 530, 970, y0, y0 + 168, fid)] + box + [handle(hid, 750, y0 + 84)]
        moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": [fid] + [q["id"] for q in box] + [hid],
                      "travel": 300})
    p += corner_glides(w) + cone_leg(1, 463) + cone_leg(2, 1037)
    return dump("sharli-0-02", [w, B, h], p, moves)


def cabinet_2d():
    """П6.116.0.03 Шкаф 2Д 1058 × 407 × 1504: two glass doors over two fluted doors, a partition below."""
    w, h = 1058, 1504
    ht = h - 16
    p = [top(w, h)] + sides(w, ht) + stiles(w, ht, ("11", "12", "13", "14"))
    p += [notched("3", w, CB, 385.5), notched("4", w, 822, 380.5),
          {"n": "15", "box": [521, 220, ZB, 537, 822, ZB + 380.5]},
          {"n": "5", "id": "5-left", "box": [22.5, 515, 25, 519.5, 531, 375]},
          {"n": "5", "id": "5-right", "box": [538.5, 515, 25, 1035.5, 531, 375]},
          {"n": "6", "kind": "glass", "box": [22, 1101, 25, 1036, 1107, 375]},
          {"n": "9", "id": "9-left", "kind": "back", "box": [76, CB, 0, 528, CB + 617, ZB]},
          {"n": "9", "id": "9-right", "kind": "back", "box": [530, CB, 0, 982, CB + 617, ZB]},
          {"n": "10", "kind": "back", "box": [76, CB + 617, 0, 982, CB + 617 + 665, ZB]}]
    L, R = (87.5, 527.5), (530.5, 970.5)
    p += [front("7", *L, 206, 873), handle("k-left", L[1] - 46, 873 - 54),
          front("8", *R, 206, 873), handle("k-right", R[0] + 46, 873 - 54)]
    p += glass_door("left", "7.1", "7.2", *L, 876, 523, ht - 2)
    p += glass_door("right", "8.1", "7.2", *R, 876, 523, ht - 2)
    p += corner_glides(w) + cone_leg(1, 529)
    moves = [{"type": "door", "name": "door_left", "parts": ["7", "k-left"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "door_right", "parts": ["8", "k-right"], "hinge": "right", "angle": 105},
             {"type": "door", "name": "glass_left", "parts": ["7.1", "7.2-left"], "hinge": "left", "angle": 105},
             {"type": "door", "name": "glass_right", "parts": ["8.1", "7.2-right"], "hinge": "right", "angle": 105}]
    return dump("sharli-0-03", [w, B, h], p, moves)


if __name__ == "__main__":
    print(cabinet())
    print(tv_unit())
    print(cabinet_2d())
