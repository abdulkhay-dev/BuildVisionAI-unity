"""Djio (П7.060.0.*, «Пинскдрев-Заславль»): a carcass of ЛДСП 16 (sides 405 / 409 deep) standing on a 25 mm base plate
(3 mm wider each side, flush with the fronts) on block feet 40 mm; a 25 mm top in «Кедр Орегон» overhanging 23 mm at
the sides and 17 mm at the front; fronts 19 mm overlay in front of the carcass between two pilasters 70 wide (two
milled grooves) fixed on the sides' front edges; frame doors (МДФ, border 72) glazed or with a sunk panel; drawers
without a separate front: the box's front wall is the facade; backs ХДФ nailed on the back.

z: backs 0–3, carcass 3–(3 + side depth), gap 2, fronts 19 → the base plate's front.
"""
from common import dump

B = 450
FEET, BASE, TOP = 40, 25, 25
Y0 = FEET + BASE          # the sides stand here
OX = 23                   # the carcass' left face (the top overhangs it)
GLASS = {"frame": 62, "rebate": 10, "t": 4, "tint": "clear"}
PANEL = {"type": "frame", "border": 72, "depth": 6, "r": 3}


class Case:
    def __init__(self, w, h, side_d):
        self.w, self.h, self.sd = w, h, side_d
        self.zc = 3 + side_d                     # the carcass' front edge
        self.zf0, self.zf1 = self.zc + 2, self.zc + 21
        self.yt = h - TOP                        # underside of the top
        self.parts, self.moves = [], []

    def add(self, *ps):
        self.parts += ps

    def shell(self, n_top, n_base, n_left, n_right):
        w = self.w
        self.add({"n": n_top, "mat": "top", "box": [0, self.yt, 0, w, self.h, B]},
                 {"n": n_base, "box": [OX - 3, FEET, 3, w - OX + 3, Y0, self.zf1]},
                 {"n": n_left, "box": [OX, Y0, 3, OX + 16, self.yt, self.zc]},
                 {"n": n_right, "box": [w - OX - 16, Y0, 3, w - OX, self.yt, self.zc]})

    def pilasters(self, n_left, n_right):
        for n, x0 in ((n_left, OX), (n_right, self.w - OX - 70)):
            self.add({"n": n, "kind": "front", "box": [x0, Y0, self.zc, x0 + 70, self.yt, self.zf1],
                      "face": {"type": "grooves", "w": 5, "depth": 3, "flute": "u",
                               "lines": [[x0 + 25, Y0, x0 + 25, self.yt], [x0 + 45, Y0, x0 + 45, self.yt]]}})

    def feet(self, extra_x=()):
        w, k = self.w, 0
        for x in [OX + 40, w - OX - 40]:
            for z in (40, self.zf1 - 40):
                k += 1
                self.add(self._foot(k, x, z))
        for x in extra_x:
            k += 1
            self.add(self._foot(k, x, self.zf1 - 40))

    def _foot(self, k, x, z):
        return {"id": f"N-{k}", "box": [x - 30, 0, z - 30, x + 30, FEET, z + 30], "covers": ["N"]}

    def front(self, n, x0, x1, y0, y1, pid=None, glass=False):
        p = {"n": n, "kind": "front", "box": [x0, y0, self.zf0, x1, y1, self.zf1]}
        if pid:
            p["id"] = pid
        if glass:
            p["glass"] = dict(GLASS)
        elif glass is False:
            p["face"] = dict(PANEL)
        self.add(p)
        return p.get("id", n)

    def knob(self, kid, x, y):
        self.add({"id": kid, "kind": "handle", "model": "knob", "at": [x, y], "d": 28, "t": 12, "standoff": 16,
                  "z": self.zf1, "covers": ["H"]})
        return kid

    def door(self, name, n, x0, x1, y0, y1, hinge, knob_at, pid=None, glass=False):
        fid = self.front(n, x0, x1, y0, y1, pid, glass)
        kid = self.knob(f"H-{name}", *knob_at)
        self.moves.append({"type": "door", "name": name, "parts": [fid, kid], "hinge": hinge, "angle": 105})

    def drawer(self, tag, ns, fx0, fx1, fy0, fh, bx0, bx1):
        """The box's front wall is the facade (ns: front, left, right, back, bottom); sides 400 deep, 162 high, 20 above
        the front's bottom; the bottom (ХДФ) nailed under the box."""
        nf, nl, nr, nb, nd = ns
        z1, z0 = self.zf0, self.zf0 - 400
        yb = fy0 + 20
        ids = [f"{nf}-{tag}", f"{nl}-{tag}", f"{nr}-{tag}", f"{nb}-{tag}", f"{nd}-{tag}"]
        self.add({"n": nf, "id": ids[0], "kind": "front", "box": [fx0, fy0, self.zf0, fx1, fy0 + fh, self.zf1]},
                 {"n": nl, "id": ids[1], "box": [bx0, yb, z0, bx0 + 16, yb + 162, z1]},
                 {"n": nr, "id": ids[2], "box": [bx1 - 16, yb, z0, bx1, yb + 162, z1]},
                 {"n": nb, "id": ids[3], "box": [bx0 + 16, yb, z0, bx1 - 16, yb + 162, z0 + 16]},
                 {"n": nd, "id": ids[4], "kind": "back", "box": [bx0 + 2, yb - 3.5, z1 - 405, bx1 - 2, yb, z1]})
        kid = self.knob(f"H-{tag}", (fx0 + fx1) / 2, fy0 + fh / 2)
        self.moves.append({"type": "drawer", "name": f"drawer_{tag}", "parts": ids + [kid], "travel": 330})

    def back(self, n, x0, x1, y0, y1, pid=None):
        p = {"n": n, "kind": "back", "box": [x0, y0, 0, x1, y1, 3]}
        if pid:
            p["id"] = pid
        self.add(p)

    def dump(self, did, size=None):
        return dump(did, size or [self.w, B, self.h], self.parts, self.moves)


# ------------------------------------------------------------------------------------------------------------ modules
def cabinet():
    """П7.060.0.11 Шкаф 650 × 450 × 2200: a glazed door over a panel door, one column of shelves."""
    c = Case(650, 2200, 409)
    c.shell("1", "4", "2", "3")
    c.pilasters("9", "10")
    x0, x1 = OX + 16, 650 - OX - 16
    c.add({"n": "6", "box": [x0, 566, 3, x1, 582, c.zc]},
          {"n": "14", "box": [x0, 1363, 3, x1, 1379, 407]})
    for k, y in enumerate((300, 955, 1724)):
        c.add({"n": "5", "id": f"5-{k + 1}", "box": [x0 + 1, y, 5, x1 - 1, y + 16, 409]})
    c.back("11", 25, 625, 42, 574)
    c.back("12", 25, 625, 574, 1371)
    c.back("13", 25, 625, 1371, 2194)
    dx0, dx1 = 94, 556
    c.door("door_bottom", "8", dx0, dx1, Y0 + 2, Y0 + 2 + 506, "left", (dx1 - 30, 366))
    c.door("door_top", "7", dx0, dx1, 576, 576 + 1598, "left", (dx1 - 30, 1133), glass=True)
    c.feet()
    return c.dump("djio-0-11")


def tv_unit():
    """П7.060.0.21 Тумба 1575 × 450 × 800: two glazed doors round a column of three drawers."""
    w = 1575
    c = Case(w, 800, 405)
    c.shell("1", "2", "3", "4")
    c.pilasters("16", "16")
    c.parts[-2]["id"], c.parts[-1]["id"] = "16-left", "16-right"
    xl, xr = OX + 16, w - OX - 16
    p5, p6 = xl + 510, xl + 510 + 16 + 444
    c.add({"n": "5", "box": [p5, Y0, 3, p5 + 16, c.yt, c.zc]},
          {"n": "6", "box": [p6, Y0, 3, p6 + 16, c.yt, c.zc]},
          {"n": "7", "id": "7-left", "box": [xl, c.yt - 16, 325, xl + 509, c.yt, 405]},
          {"n": "8", "box": [p5 + 16, c.yt - 16, 325, p6, c.yt, 405]},
          {"n": "7", "id": "7-right", "box": [p6 + 16, c.yt - 16, 325, p6 + 16 + 509, c.yt, 405]},
          {"n": "9", "box": [xl, 412, 3, p5, 428, 406]},
          {"n": "10", "box": [p6 + 16, 412, 3, xr, 428, 406]})
    c.back("18", 27, 557, 42, 773, "18-left")
    c.back("19", 557, 1016, 42, 773)
    c.back("18", 1017, 1547, 42, 773, "18-right")
    L, R = (94, 556), (w - 556, w - 94)
    c.door("door_left", "17", *L, Y0 + 2, c.yt - 2, "left", (L[1] - 30, 420), "17-left", glass=True)
    c.door("door_right", "17", *R, Y0 + 2, c.yt - 2, "right", (R[0] + 30, 420), "17-right", glass=True)
    for k, fy0 in enumerate((Y0 + 2, Y0 + 238, Y0 + 474)):
        c.drawer(str(k + 1), ("15", "11", "12", "13", "14"), 559, 1016, fy0, 234, 578, 997)
    c.feet(extra_x=[w / 2])
    return c.dump("djio-0-21")


def cabinet_4d():
    """П7.060.0.22 Тумба 1114 × 450 × 1200: two glazed doors over two panel doors, two columns."""
    w = 1114
    c = Case(w, 1200, 405)
    c.shell("1", "2", "3", "4")
    c.pilasters("10", "11")
    xl, xr = OX + 16, w - OX - 16
    p5 = xl + 510
    c.add({"n": "5", "box": [p5, Y0, 3, p5 + 16, c.yt, c.zc]})
    for side, (a, b) in (("left", (xl, p5)), ("right", (p5 + 16, xr))):
        c.add({"n": "12", "id": f"12-{side}", "box": [a, 566, 3, b, 582, c.zc]},
              {"n": "7", "id": f"7-{side}", "box": [a, c.yt - 16, 325, a + 509, c.yt, 405]},
              {"n": "6", "id": f"6-{side}-1", "box": [a + 1, 308, 5, b - 1, 324, 407]},
              {"n": "6", "id": f"6-{side}-2", "box": [a + 1, 870, 5, b - 1, 886, 407]})
    c.back("13", 27, 557, 42, 1173, "13-left")
    c.back("13", 558, 1088, 42, 1173, "13-right")
    L, R = (94, 556), (558, 1020)
    c.door("door_bottom_left", "9", *L, Y0 + 2, Y0 + 508, "left", (L[1] - 30, 493), "9-left")
    c.door("door_bottom_right", "9", *R, Y0 + 2, Y0 + 508, "right", (R[0] + 30, 493), "9-right")
    c.door("door_top_left", "8", *L, 576, 1174, "left", (L[1] - 30, 656), "8-left", glass=True)
    c.door("door_top_right", "8", *R, 576, 1174, "right", (R[0] + 30, 656), "8-right", glass=True)
    c.feet(extra_x=[w / 2])
    return c.dump("djio-0-22")


def chest():
    """П7.060.0.23 Тумба 800 × 450 × 1200: a drawer over two panel doors."""
    w = 800
    c = Case(w, 1200, 405)
    c.shell("1", "2", "3", "4")
    c.pilasters("13", "14")
    xl, xr = OX + 16, w - OX - 16
    ys = 930
    c.add({"n": "5", "box": [xl, ys, 3, xr, ys + 16, c.zc]},
          {"n": "19", "box": [75, ys + 16, 3, 91, c.yt, c.zc]},
          {"n": "20", "box": [709, ys + 16, 3, 725, c.yt, c.zc]},
          {"n": "16", "box": [91, c.yt - 16, 325, 708, c.yt, 405]},
          {"n": "7", "box": [xl, ys - 200, 3, xr, ys, 19]},
          {"n": "6", "id": "6-1", "box": [xl + 1, 350, 28, xr - 1, 366, 408]},
          {"n": "6", "id": "6-2", "box": [xl + 1, 640, 28, xr - 1, 656, 408]})
    c.back("17", 25, 775, 941, 1175)
    c.back("18", 26, 400, 42, 938, "18-left")
    c.back("18", 400, 774, 42, 938, "18-right")
    L, R = (94, 399), (401, 706)
    c.door("door_left", "15", *L, Y0 + 2, Y0 + 872, "left", (L[1] - 30, 600), "15-left")
    c.door("door_right", "15", *R, Y0 + 2, Y0 + 872, "right", (R[0] + 30, 600), "15-right")
    c.drawer("1", ("8", "9", "10", "11", "12"), 94, 706, 939, 234, 104, 696)
    c.feet()
    return c.dump("djio-0-23")


if __name__ == "__main__":
    print(cabinet())
    print(tv_unit())
    print(cabinet_4d())
    print(chest())
