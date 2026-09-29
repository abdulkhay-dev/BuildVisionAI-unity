"""«Марлен» (П3.594.1): all six modules by catalogue — p. 105 is the only spread (one interior photo, no module cut-outs,
no swatches: the colours come from the «Вена» chart on p. 115 and the «Акцент» chart on p. 132).

The construction read off the photo:
  * carcass ЛДСП 16 «Гикори Кингстон»: the sides run from the glides (12) to under the top, the top lies over them, the
    bottom between them just above the floor (its oak edge shows under the fronts), ХДФ back in grooves;
  * fronts ЛДСП 16 «Персидский жемчуг», inset between the sides / top / bottom, flush with the carcass edges, 2–3 mm gaps;
  * long bar handles in satin aluminium standing 32 mm off the fronts (outside the catalogue depth B, which is the
    carcass): 320 on drawers of the chest / desk / bedside, 272 on the wardrobe drawers, 336 upright on the doors;
  * the bed on round tapered oak legs, its headboard an oak board with an upholstered panel of six vertical channels.
"""
from common import dump, feet

T = 16
GL = 12            # glides
G = 2              # gaps round the inset fronts


def bar(pid, x, y, fz, length=320, dir="right"):
    return {"id": pid, "kind": "handle", "model": "bar", "at": [x, y], "dir": dir, "d": length, "band": 12, "t": 10,
            "standoff": 22, "z": fz}


def split(a0, a1, n, g=G):
    s = (a1 - a0 - (n + 1) * g) / n
    return [(round(a0 + g + i * (s + g), 1), round(a0 + g + i * (s + g) + s, 1)) for i in range(n)]


class Case:
    """Carcass w × b × h on glides; fronts inset flush with the carcass edges (face at z = b)."""

    def __init__(self, w, b, h):
        self.w, self.b, self.h = w, b, h
        self.fz, self.cz = b, b - T
        self.parts, self.moves = [], []

    def carcass(self, back=True):
        w, h, b = self.w, self.h, self.b
        self.parts += [{"id": "side-l", "box": [0, GL, 0, T, h - T, b]},
                       {"id": "side-r", "box": [w - T, GL, 0, w, h - T, b]},
                       {"id": "top", "box": [0, h - T, 0, w, h, b]},
                       {"id": "bottom", "box": [T, GL, 0, w - T, GL + T, b]}]
        if back:
            self.parts.append({"id": "back", "kind": "back", "box": [T - 5, GL + T - 5, 6, w - T + 5, h - T + 5, 9.5]})

    def glides(self, xs=None):
        xs = xs or [40, self.w - 40]
        self.parts += feet(xs, [40, self.b - 40], h=GL, d=24)

    def door(self, name, x0, y0, x1, y1, hinge, hx, hy, length=336, mat=None):
        f = {"id": name, "kind": "front", "box": [x0, y0, self.cz, x1, y1, self.fz]}
        h = bar(f"{name}-handle", hx, hy, self.fz, length, "up")
        self.parts += [f, h]
        self.moves.append({"type": "door", "name": name, "parts": [name, h["id"]], "hinge": hinge, "angle": 100})

    def drawer(self, name, x0, y0, x1, y1, wall0, wall1, handle_y, length=320, depth=None, box_h=None):
        cz = self.cz
        depth = depth or min(cz - 40, 450)
        bh = box_h or max(60, min(y1 - y0 - 55, 170))
        bx0, bx1 = wall0 + 13, wall1 - 13
        by0, z0 = y0 + 20, cz - depth
        box = [{"id": f"{name}-side-l", "box": [bx0, by0, z0, bx0 + T, by0 + bh, cz]},
               {"id": f"{name}-side-r", "box": [bx1 - T, by0, z0, bx1, by0 + bh, cz]},
               {"id": f"{name}-back", "box": [bx0 + T, by0, z0, bx1 - T, by0 + bh, z0 + T]},
               {"id": f"{name}-bottom", "kind": "back", "box": [bx0 + 11, by0 + 10, z0 + 4, bx1 - 11, by0 + 13.5, cz - 2]}]
        f = {"id": name, "kind": "front", "box": [x0, y0, cz, x1, y1, self.fz]}
        h = bar(f"{name}-handle", (x0 + x1) / 2, handle_y, self.fz, length)
        self.parts += [f] + box + [h]
        self.moves.append({"type": "drawer", "name": name, "parts": [name] + [q["id"] for q in box] + [h["id"]],
                           "travel": int(depth * 0.75)})

    def dump(self, did):
        return dump(did, [self.w, self.b, self.h], self.parts, self.moves)


def komod():
    """Комод 1.25, 1000×500×756: three equal drawers."""
    c = Case(1000, 500, 756)
    c.carcass()
    for i, (y0, y1) in enumerate(split(GL + T, c.h - T, 3)):
        c.drawer(f"drawer-{i + 1}", T + G, y0, c.w - T - G, y1, T, c.w - T, y1 - 50, box_h=150)
    c.glides([40, 500, 960])
    return c.dump("marlen-1-25")


def bedside():
    """Тумба прикроватная 1.21, 546×400×458: a drawer under an open niche; the shelf between them flush with the sides."""
    c = Case(546, 400, 458)
    c.carcass()
    sy = 230
    c.parts.append({"id": "shelf", "box": [T, sy, 0, c.w - T, sy + T, c.fz]})
    y0, y1 = GL + T + G, sy - G
    c.drawer("drawer", T + G, y0, c.w - T - G, y1, T, c.w - T, y1 - 70, box_h=120, depth=320)
    c.glides()
    return c.dump("marlen-1-21")


def desk():
    """Стол письменный 1.22, 1200×500×752: side panels 25 set in 20 under a 25 top, two drawers side by side under the
    top on a drawer shelf, a modesty panel at the back."""
    W, B, H = 1200, 500, 752
    S, TT, inset = 25, 25, 20
    c = Case(W, B, H)
    c.fz, c.cz = 480, 464                          # the sides and fronts 20 behind the top's front edge
    x0, x1 = inset + S, W - inset - S
    xm = W / 2
    sy = 577
    c.parts += [{"id": "top", "box": [0, H - TT, 0, W, H, B]},
                {"id": "side-l", "box": [inset, GL, 0, inset + S, H - TT, c.fz]},
                {"id": "side-r", "box": [W - inset - S, GL, 0, W - inset, H - TT, c.fz]},
                {"id": "drawer-shelf", "box": [x0, sy, 20, x1, sy + T, c.fz]},
                {"id": "partition", "box": [xm - T / 2, sy + T, 20, xm + T / 2, H - TT, c.cz]},
                {"id": "modesty", "box": [x0, 380, 20, x1, sy, 36]},
                {"id": "drawer-back", "box": [x0, sy + T, 20, xm - T / 2, H - TT, 36]},
                {"id": "drawer-back-r", "box": [xm + T / 2, sy + T, 20, x1, H - TT, 36]}]
    y0, y1 = sy + T + G, H - TT - G
    c.drawer("drawer-l", x0 + G, y0, xm - 1.5, y1, x0, xm - T / 2, (y0 + y1) / 2 + 15, depth=400, box_h=90)
    c.drawer("drawer-r", xm + 1.5, y0, x1 - G, y1, xm + T / 2, x1, (y0 + y1) / 2 + 15, depth=400, box_h=90)
    c.parts += feet([inset + S / 2, W - inset - S / 2], [40, c.fz - 40], h=GL, d=20)
    return c.dump("marlen-1-22")


def wardrobe_combined():
    """Шкаф комбинированный 1.23, 902×579×2292: two doors over two drawers; inside a partition, shelves on the left,
    a rail on the right, a hat shelf."""
    c = Case(902, 579, 2292)
    c.carcass()
    w = c.w
    d1 = (GL + T + G, 340)                         # the lower drawer 310, the upper 287, the doors 1641 (p. 105 photo)
    d2 = (343, 630)
    y_doors = (633, c.h - T - G)
    c.parts.append({"id": "over-drawers", "box": [T, 614, 9.5, w - T, 630, c.cz]})
    c.parts.append({"id": "partition", "box": [w / 2 - T / 2, 630, 9.5, w / 2 + T / 2, 1950, c.cz]})
    c.parts.append({"id": "hat", "box": [T, 1950, 9.5, w - T, 1966, c.cz]})
    for i, y in enumerate([1000, 1350, 1700]):
        c.parts.append({"id": f"shelf-{i + 1}", "box": [T + 1, y, 20, w / 2 - T / 2 - 1, y + T, c.cz - 4]})
    zc = (c.cz + 9.5) / 2
    c.parts.append({"id": "rail", "kind": "tube", "mat": "chrome", "box": [w / 2 + T / 2 + 4, 1870, zc - 10, w - T - 4, 1890, zc + 10]})
    (a0, a1), (b0, b1) = split(T, w - T, 2, 3)
    c.door("door-l", a0, y_doors[0], a1, y_doors[1], "left", a1 - 54, 1130)
    c.door("door-r", b0, y_doors[0], b1, y_doors[1], "right", b0 + 54, 1130)
    for i, (y0, y1) in enumerate((d1, d2)):
        c.drawer(f"drawer-{i + 1}", T + G, y0, w - T - G, y1, T, w - T, y1 - 55, length=272, box_h=180 if i == 0 else 160)
    c.glides([40, 451, 862])
    return c.dump("marlen-1-23")


def wardrobe_corner():
    """Шкаф угловой 1.24, 900×579×2292: a blind-corner unit — its left half stays behind the combined wardrobe standing
    at right angles against it (an oak blind panel), a pearl door on the free right half; hat shelf and rail inside."""
    c = Case(900, 579, 2292)
    c.carcass()
    w = c.w
    y0, y1 = GL + T + G, c.h - T - G
    c.parts.append({"id": "blind", "mat": "body", "box": [T + G, y0, c.cz, 449, y1, c.fz]})
    c.parts.append({"id": "hat", "box": [T, 1950, 9.5, w - T, 1966, c.cz]})
    for i, y in enumerate([500, 900, 1300]):
        c.parts.append({"id": f"shelf-{i + 1}", "box": [T + 1, y, 20, w - T - 1, y + T, c.cz - 4]})
    zc = (c.cz + 9.5) / 2
    c.parts.append({"id": "rail", "kind": "tube", "mat": "chrome", "box": [T + 4, 1870, zc - 10, w - T - 4, 1890, zc + 10]})
    c.door("door", 452, y0, w - T - G, y1, "left", w - T - G - 50, 1130)
    c.glides([40, 450, 860])
    return c.dump("marlen-1-24")


def oak_leg(pid, x, z, h=190, d=50, d2=34):
    return {"id": pid, "kind": "rod", "mat": "body", "from": [x, h, z], "to": [x, 0, z], "d": d, "d2": d2,
            "box": [x - d / 2, 0, z - d / 2, x + d / 2, h, z + d / 2]}


def bed():
    """Кровать 1.20, 1712×2143×1000, спальное место 2000×1600."""
    W, L, H = 1712, 2143, 1000
    LH, rail_top, hb, ft, R = 190, 420, 25, 25, 25
    p = [{"id": "headboard", "box": [0, LH, 0, W, H, hb]},
         {"id": "soft", "kind": "soft", "channels": 6, "box": [R, 540, hb, W - R, H - 15, hb + 80]},
         {"id": "rail-l", "box": [0, LH, hb, R, rail_top, L - ft]},
         {"id": "rail-r", "box": [W - R, LH, hb, W, rail_top, L - ft]},
         {"id": "foot", "box": [0, LH, L - ft, W, rail_top, L]},
         {"id": "cleat-l", "box": [R, 330, hb, R + 30, 360, L - ft]},
         {"id": "cleat-r", "box": [W - R - 30, 330, hb, W - R, 360, L - ft]},
         {"id": "beam", "box": [W / 2 - 20, 300, hb, W / 2 + 20, 360, L - ft]},
         {"id": "beam-leg-1", "kind": "tube", "mat": "black", "box": [W / 2 - 15, 0, 700, W / 2 + 15, 300, 730]},
         {"id": "beam-leg-2", "kind": "tube", "mat": "black", "box": [W / 2 - 15, 0, 1400, W / 2 + 15, 300, 1430]}]
    for i in range(24):
        z = hb + 110 + i * 82
        p.append({"id": f"slat-{i + 1}", "kind": "panel", "mat": "door_enamel_whitey#c9a877",
                  "box": [R + 30, 360, z, W - R - 30, 368, z + 53]})
    p.append({"id": "mattress", "kind": "mattress", "box": [56, 368, hb + 82, 1656, 568, hb + 2082]})
    for i, (x, z) in enumerate([(45, 25), (W - 45, 25), (45, L - 45), (W - 45, L - 45)]):
        p.append(oak_leg(f"leg-{i + 1}", x, z))
    return dump("marlen-1-20", [W, L, H], p, [])


if __name__ == "__main__":
    for f in (komod, bedside, desk, wardrobe_combined, wardrobe_corner, bed):
        print(f())
