"""Floor play items of batch pediatric-4: XYRT-67 balance footpath (4 rod mats), XYRT-44 octagonal soft ball pool."""
import random
from pd4lib import *


def xyrt67():
    d = D("xyrt-67", [1470, 1200, 30], {"cord": "plastic#7d8ea8"})
    cols = ["plastic#2f9e3e", "plastic#e0261f", "plastic#f6cf18", "plastic#1f4fbf"]   # front -> back
    n, pitch, dia = 48, 30.6, 26
    x0 = (1470 - (n - 1) * pitch) / 2
    for s, col in enumerate(cols):
        z1 = 1200 - 300 * s - 4
        z0 = z1 - 292
        d.cyl(f"rod{s}", [x0, 15, z0 + 13], [x0, 15, z1 - 13], dia, col, sides=14, repeat=rep(n, [pitch, 0, 0]))
        d.sphere(f"rod{s}-end", [x0, 15, z0 + 13], dia, col, sides=12, repeat=rep(n, [pitch, 0, 0]),
                 copies=[[0, 0, z1 - z0 - 26]])
        # the two cords threading the rods (seen as beads between them)
        for k, f in enumerate((0.27, 0.73)):
            z = z0 + (z1 - z0) * f
            d.cyl(f"cord{s}-{k}", [x0 - 45, 15, z], [x0 + (n - 1) * pitch + 8, 15, z], 11, "cord", sides=10)
    return d


def xyrt44():
    d = D("xyrt-44", [1500, 1500, 680], {"viny": "leather#3a90de", "pipe": "leather#1d3f9a", "floor": "leather#2a6cc8",
                                        "o": "gloss#f07a1e", "g": "gloss#3fae4a", "b": "gloss#2d5fd0", "r": "gloss#e2352a",
                                        "y": "gloss#f2c21c"})
    c, H, T = 750, 680, 100
    apo = 750                        # outer apothem (across flats 1500)
    side = 2 * apo * math.tan(math.radians(22.5))
    rnd_ = random.Random(44)
    for i in range(8):
        a = 90 + 45 * i                  # outward normal of the panel (90 = the front)
        # panel built facing the front (normal +z), then turned about the pool centre
        r = rot("y", -(a - 90), [c, 0, c])  # about y turns z towards x: normal +z -> angle a
        zf = c + apo
        d.box(f"panel{i}", [c - side / 2 + 6, 0, zf - T, c + side / 2 - 6, H, zf], "viny", r=14, puff=5, rot=r)
        # navy piping along the top edges
        d.tube(f"pipe{i}", [[c - side / 2 + 20, H - 3, zf - 3], [c + side / 2 - 20, H - 3, zf - 3]], 9, "pipe",
               soft=True, rot=r)
        d.tube(f"pipe{i}b", [[c - side / 2 + 50, H - 3, zf - T + 3], [c + side / 2 - 50, H - 3, zf - T + 3]], 9,
               "pipe", soft=True, rot=r)
    # the underwater print (photo): ~10 big fish per outer face (yellow with black bars, orange-red, magenta,
    # lime, violet), each a flat oval body + forked tail + dark eye; green / violet weed sprigs (stem + leaves);
    # clusters of white bubbles. Panels i and i+4 are parallel, so one turned part per mark type carries both.
    BALL = 520
    fish_cols = ["plastic#f5cf1e", "plastic#f5cf1e", "plastic#ee5a24", "plastic#d1309a", "plastic#a6d63a",
                 "plastic#8e4fc8", "plastic#f39a1c"]
    for g in range(4):
        marks = {}                     # (kind, colour, variant) -> list of world points
        a_g = 90 + 45 * g
        for i in (g, g + 4):
            a = 90 + 45 * i
            n = (math.cos(math.radians(a)), math.sin(math.radians(a)))
            t = (math.cos(math.radians(a - 90)), math.sin(math.radians(a - 90)))
            for face, dist, vmin in (("out", apo + 5, 70), ("in", apo - T - 5, BALL + 50)):
                def W(u, v): return (c + n[0] * dist + t[0] * u, v, c + n[1] * dist + t[1] * u)
                um = side / 2 - 140
                # fish on a jittered grid (the photo's fish are spread evenly, not clumped)
                rows = [v for v in range(vmin + 40, H - 50, 125)]
                for ri_, v0 in enumerate(rows):
                    for k in range(3):
                        u = -um + k * um + (45 if ri_ % 2 else -35) + rnd_.uniform(-25, 25)
                        if face == "out" and rnd_.random() < 0.15: continue
                        v = v0 + rnd_.uniform(-25, 25)
                        col = fish_cols[rnd_.randrange(len(fish_cols))]
                        sgn = rnd_.choice((-1, 1))          # +1 = swims right
                        marks.setdefault(("body", col, 0), []).append(W(u, v))
                        marks.setdefault(("tail", col, sgn), []).append(W(u - sgn * 52, v))
                        marks.setdefault(("eye", "plastic#1d1d24", 0), []).append(W(u + sgn * 28, v + 6))
                        if col == "plastic#f5cf1e":
                            marks.setdefault(("bar", "plastic#2a2328", 0), []).append(W(u - sgn * 4, v))
                        else:
                            marks.setdefault(("fin", "plastic#f5cf1e", 0), []).append(W(u - sgn * 6, v + 26))
                # weed sprigs
                for k in range(10 if face == "out" else 3):
                    u, v = rnd_.uniform(-um, um), rnd_.uniform(vmin + 20, H - 140)
                    wc = "plastic#3fa83a" if rnd_.random() < 0.75 else "plastic#9a4fd0"
                    marks.setdefault(("stem", wc, 0), []).append(W(u, v))
                    marks.setdefault(("leafL", wc, 0), []).append(W(u - 14, v + 10))
                    marks.setdefault(("leafR", wc, 0), []).append(W(u + 14, v + 30))
                # bubble clusters (3 dots of falling size, rising)
                for k in range(18 if face == "out" else 5):
                    u, v = rnd_.uniform(-side / 2 + 40, side / 2 - 40), rnd_.uniform(vmin - 20, H - 40)
                    for j, (du, dv) in enumerate(((0, 0), (12, 20), (2, 38))):
                        marks.setdefault(("dot", "plastic#ffffff", j), []).append(W(u + du, v + dv))
        for j, ((kind, col, var), pts) in enumerate(marks.items()):
            p0 = list(pts[0])
            cop = [[p[0] - p0[0], p[1] - p0[1], p[2] - p0[2]] for p in pts[1:]]
            ry = rot("y", -(a_g - 90), p0)
            if kind == "tail":
                # forked tail: a flat triangle behind the body, notched at the back
                x, y, z = p0
                tri = P([(x + var * 18, y), (x - var * 22, y + 26), (x - var * 10, y), (x - var * 22, y - 26)])
                d.slab(f"tail{g}-{j}", "front", tri, [z - 1.5, z + 1.5], col, soft=True, rot=ry, copies=cop)
                continue
            radii = {"body": [48, 28, 2.5], "eye": [6, 6, 3.5], "bar": [7, 26, 3.2], "fin": [16, 7, 2.2],
                     "stem": [4, 62, 2.4], "leafL": [4, 28, 2.6], "leafR": [4, 28, 2.6],
                     "dot": [[8, 8, 2], [6, 6, 2], [5, 5, 2]][var] if kind == "dot" else None}[kind]
            extra = {}
            if kind in ("leafL", "leafR"):
                extra["rots"] = [ry]
                ry = rot("z", 40 if kind == "leafL" else -40, p0)
            d.sphere(f"{kind}{g}-{j}", p0, None, col, radii=radii, sides=12 if kind == "body" else 8, soft=True,
                     rot=ry, copies=cop, **extra)
    # soft floor and the ball filling
    oct_in = [polar(c, c, (apo - T + 5) / math.cos(math.radians(22.5)), 22.5 + 45 * k) for k in range(8)]
    d.slab("floor", "top", P(oct_in), [0, 40], "floor", r=6)
    d.slab("fill", "top", P(oct_in), [40, BALL - 5], "o", r=4)
    # top layer of balls (hex grid inside the octagon), coloured mostly orange / green / blue
    ri = apo - T - 36
    pts = []
    step = 70
    for jz in range(-12, 13):
        for jx in range(-12, 13):
            x = jx * step + (step / 2 if jz % 2 else 0)
            z = jz * step * 0.866
            # inside the inner octagon (apothem ri)
            if all(abs(x * math.cos(math.radians(22.5 * 0 + 45 * k)) + z * math.sin(math.radians(45 * k))) <= ri
                   for k in range(4)):
                pts.append((c + x, c + z))
    groups = {"o": [], "g": [], "b": [], "r": [], "y": []}
    for p in pts:
        q = rnd_.random()
        key = "o" if q < 0.52 else "g" if q < 0.72 else "b" if q < 0.9 else "r" if q < 0.96 else "y"
        groups[key].append((p, BALL + rnd_.uniform(-6, 10)))
    for key, lst in groups.items():
        if not lst: continue
        (x0, z0), y0 = lst[0]
        d.sphere(f"balls-{key}", [x0, y0, z0], 70, key, sides=10, soft=True,
                 copies=[[p[0] - x0, y - y0, p[1] - z0] for p, y in lst[1:]])
    return d


def _rot_off(du, dv, a):
    """Offset (du along the panel, dv up) of a panel facing angle a, in design axes (copies are not turned)."""
    t = math.radians(a - 90)
    # rot y by -(a-90): about y turns z towards x; a vector along +x turns to (cos t, 0, -sin t)... (engine: +deg z->x)
    return [du * math.cos(t), dv, du * math.sin(t)]


if __name__ == "__main__":
    main({"xyrt-67": xyrt67, "xyrt-44": xyrt44})
