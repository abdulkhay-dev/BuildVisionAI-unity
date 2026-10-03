"""xyrt-36a — OT group desk: low birch table with four round cut-outs + the three children's chairs of the photo
(left and back chairs with box sides, right chair with curved side frames). Size covers the set."""
import math
from pd3_lib import *

W, Dp, H = 1660, 1230, 680
d = D("xyrt-36a", [W, Dp, H], {"top": "plastic#e4cb9f", "leg": "wood#ddbf8c", "frame": "wood#d8b07a",
                               "panel": "wood#c07a4a", "green": "leather#2f9a45", "knob": "rubber#141516"})
TX0, TX1, TZ0, TZ1, TH = 230, 1430, 230, 1230, 450
cxT, czT = (TX0 + TX1) / 2, (TZ0 + TZ1) / 2


def dip(t):
    return ((math.cos(math.pi * t) + 1) / 2) ** 0.55 if abs(t) < 1 else 0.0


def edge(p0, p1, c, hw, dd, inward, n=40):
    """points along a straight edge p0→p1 (2D) with a cut-out centred at c (param along the edge) going `inward`."""
    out = []
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    for k in range(n + 1):
        s = L * k / n
        t = (s - c) / hw
        dv = dd * dip(t)
        out.append((p0[0] + ux * s + inward[0] * dv, p0[1] + uy * s + inward[1] * dv))
    return out


r = 45
pts = []
# front edge (z = TZ1) from right to left, back edge left to right, etc. Corner radius by chamfer points
pts += edge((TX1 - r, TZ1), (TX0 + r, TZ1), (TX1 - TX0) / 2 - r, 270, 175, (0, -1))
pts += [(TX0 + r * (1 - math.sin(a)), TZ1 - r * (1 - math.cos(a))) for a in [math.pi / 8 * k for k in range(1, 4)]]
pts += edge((TX0, TZ1 - r), (TX0, TZ0 + r), (TZ1 - TZ0) / 2 - r, 230, 160, (1, 0))
pts += [(TX0 + r * (1 - math.cos(a)), TZ0 + r * (1 - math.sin(a))) for a in [math.pi / 8 * k for k in range(1, 4)]]
pts += edge((TX0 + r, TZ0), (TX1 - r, TZ0), (TX1 - TX0) / 2 - r, 240, 165, (0, 1))
pts += [(TX1 - r * (1 - math.sin(a)), TZ0 + r * (1 - math.cos(a))) for a in [math.pi / 8 * k for k in range(1, 4)]]
pts += edge((TX1, TZ0 + r), (TX1, TZ1 - r), (TZ1 - TZ0) / 2 - r, 230, 160, (-1, 0))
pts += [(TX1 - r * (1 - math.cos(a)), TZ1 - r * (1 - math.sin(a))) for a in [math.pi / 8 * k for k in range(1, 4)]]
outline = "M " + " L ".join(f"{x:.1f} {z:.1f}" for x, z in pts) + " Z"
d.slab("top", "top", outline, [TH - 28, TH], "top", r=6)
for k, (x, z) in enumerate([(TX0 + 120, TZ0 + 120), (TX1 - 120, TZ0 + 120), (TX0 + 120, TZ1 - 120), (TX1 - 120, TZ1 - 120)]):
    d.box(f"leg{k}", [x - 24, 0, z - 24, x + 24, TH - 28, z + 24], "leg", r=4)


def chair(id, cx, cz, deg, curved=False):
    R = rot("y", deg, [cx, 0, cz])
    w, dd, hb, ha, hs = 360, 380, 680, 440, 270
    x0, x1, z0, z1 = cx - w / 2, cx + w / 2, cz - dd / 2, cz + dd / 2
    def box(n, b, m, **kw): d.box(f"{id}-{n}", b, m, rot=R, **kw)
    # seat and back
    box("seat", [x0 + 30, hs - 40, z0 + 60, x1 - 30, hs + 25, z1 - 5], "green", r=14, puff=6)
    box("back", [x0 + 34, hs + 10, z0 + 30, x1 - 34, hb - 8, z0 + 80], "green", r=16, puff=5)
    box("backboard", [x0 + 40, hs - 40, z0 + 20, x1 - 40, hb - 20, z0 + 34], "panel", r=4)
    for s, xs in (("l", x0), ("r", x1 - 34)):
        if not curved:
            box(f"post-{s}", [xs, 0, z0 + 20, xs + 34, hb, z0 + 60], "frame", r=6)
            box(f"fpost-{s}", [xs, 0, z1 - 50, xs + 34, ha, z1 - 14], "frame", r=5)
            box(f"panel-{s}", [xs + 6, 40, z0 + 60, xs + 28, ha - 10, z1 - 50], "panel", r=3)
            box(f"rail-{s}", [xs, 0, z0 + 60, xs + 34, 45, z1 - 50], "frame", r=4)
            box(f"arm-{s}", [xs - 4, ha, z0 + 20, xs + 38, ha + 28, z1 + 10], "frame", r=10)
            # adjustment slots and star knobs on the outer face
            xo = xs if s == "l" else xs + 34
            sg = -1 if s == "l" else 1
            for k, zz in enumerate([cz - 60, cz + 70]):
                box(f"slot-{s}{k}", [xo + sg * 0.5 - 1.5, 150, zz - 7, xo + sg * 0.5 + 1.5, 330, zz + 7], "knob", soft=True)
                d.add(f"{id}-knob-{s}{k}", "cyl", "knob", **{"from": [xo, 260 - k * 40, zz], "to": [xo + sg * 22, 260 - k * 40, zz]},
                      d=34, rot=R, soft=True)
        else:
            # photo: straight rear post (up to the back top) and front leg (to the seat), a seat rail with an arched
            # underside between them, and a thin bent-wood arm strip sweeping from the post top down to the seat rail
            zb, zf = z0 + 20, z1 - 10
            box(f"post-{s}", [xs, 0, zb, xs + 34, hb, zb + 40], "frame", r=6)
            box(f"fleg-{s}", [xs, 0, zf - 40, xs + 34, hs - 20, zf], "frame", r=5)
            ol = (f"M {zb + 40} {hs - 22} L {zf - 40} {hs - 22} L {zf - 40} {hs - 105} "
                  f"Q {(zb + zf) / 2} {hs - 55} {zb + 40} {hs - 105} Z")
            d.slab(f"{id}-rail-{s}", "side", ol, [xs + 3, xs + 31], "frame", r=4, rot=R)
            xm = xs + 17
            d.sweep(f"{id}-arm-{s}", [[xm, hb - 4, zb + 20], [xm, hb - 170, zb + 55], [xm, hs + 110, zb + 115],
                                      [xm, hs - 24, zb + 175]], [32, 20], "frame", shape="rect", r=5, bend=150, rot=R)
    box("stretch", [x0 + 30, 60, z0 + 30, x1 - 30, 100, z0 + 60], "frame", r=4)


chair("cl", 190, czT, 90)           # left chair faces +x
chair("cb", cxT, 190, 0)            # back chair faces the front
chair("cr", W - 190, czT, -90, curved=True)
d.save()
