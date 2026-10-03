"""Helpers of batch pediatric-1 (shared by the pd1_*.py generators only)."""
import math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import p1lib
from lib import D, rnd, rot, sec, rep

text = p1lib.text
# digits the shared font lacks (added at import for this batch's labels only; 1–4 as in k4lib)
_F = p1lib._FONT
_F.setdefault("1", (0.3, [[(0, 0.75), (0.3, 1), (0.3, 0)]]))
_F.setdefault("2", (0.52, [[(0, 0.8), (0.14, 1), (0.4, 1), (0.52, 0.8), (0.52, 0.62), (0, 0), (0.52, 0)]]))
_F.setdefault("3", (0.52, [[(0, 0.86), (0.14, 1), (0.4, 1), (0.52, 0.84), (0.52, 0.64), (0.38, 0.52), (0.18, 0.52)],
                           [(0.38, 0.52), (0.52, 0.4), (0.52, 0.16), (0.4, 0), (0.12, 0), (0, 0.14)]]))
_F.setdefault("4", (0.56, [[(0.42, 0), (0.42, 1), (0, 0.32), (0.56, 0.32)]]))
_F.setdefault("5", (0.52, [[(0.5, 1), (0.06, 1), (0.02, 0.56), (0.3, 0.6), (0.48, 0.48), (0.52, 0.24), (0.4, 0.02), (0.14, 0), (0, 0.12)]]))
_SIX = [(0.46, 0.94), (0.3, 1), (0.12, 0.94), (0, 0.66), (0, 0.2), (0.14, 0), (0.38, 0), (0.52, 0.16), (0.52, 0.38), (0.38, 0.56), (0.14, 0.56), (0, 0.4)]
_F.setdefault("6", (0.52, [_SIX]))
_F.setdefault("9", (0.52, [[(0.52 - x, 1 - y) for x, y in _SIX]]))
_F.setdefault("7", (0.5, [[(0, 1), (0.5, 1), (0.16, 0)]]))
_F.setdefault("0", (0.5, [[(0.14, 0), (0, 0.2), (0, 0.8), (0.14, 1), (0.36, 1), (0.5, 0.8), (0.5, 0.2), (0.36, 0), (0.14, 0)]]))
text_len = p1lib.text_len
rotx = p1lib.rotx
rpoly = p1lib.rpoly


class K(D):
    """lib.D with every part kind; decal(id, at, size, face, mat)."""
    def box(s, id, b, mat, r=None, **kw): return s.add(id, "box", mat, box=b, r=r, **kw)
    def cyl(s, id, a, b, d, mat, **kw): return s.add(id, "cyl", mat, **{"from": a, "to": b, "d": d}, **kw)
    def bar(s, id, a, b, sec_, mat, r=None, **kw): return s.add(id, "bar", mat, **{"from": a, "to": b}, section=sec_, r=r, **kw)
    def decal(s, id, at, size, face, mat=None, **kw):
        kw.setdefault("soft", True)
        return s.add(id, "decal", mat, at=at, size=size, face=face, **kw)
    def screen(s, id, b, mat, **kw): return s.add(id, "screen", mat, box=b, **kw)
    def caster(s, id, at, d=75, mat=None, **kw): return s.add(id, "caster", mat, at=at, d=d, **kw)
    def wheel(s, id, at, d, mat, **kw): return s.add(id, "wheel", mat, at=at, d=d, **kw)
    def lathe(s, id, at, prof, mat, axis=None, **kw): return s.add(id, "lathe", mat, at=at, profile=prof, axis=axis, **kw)
    def sphere(s, id, at, d, mat, **kw): return s.add(id, "sphere", mat, at=at, d=d, **kw)


def circle(a, b, r):
    """SVG circle centred at (a, b) of a slab plane."""
    return f"M {a - r:.1f} {b:.1f} A {r} {r} 0 1 0 {a + r:.1f} {b:.1f} A {r} {r} 0 1 0 {a - r:.1f} {b:.1f} Z"


def poly(pts):
    return "M " + " L ".join(f"{p[0]:.1f} {p[1]:.1f}" for p in pts) + " Z"


def arc_pts(cx, cy, r, a0, a1, n=12):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
            for k in range(n + 1)]


def lerp(a, b, t): return [a[i] + (b[i] - a[i]) * t for i in range(len(a))]


def yrot_deg(dx, dz):
    """rot about y (deg) that turns the +x axis of a part into the plan direction (dx, dz)."""
    return -math.degrees(math.atan2(dz, dx))


def plan_box(d, id, a, b, half_w, y0, y1, mat, r=None, ext=0.0, **kw):
    """A box lying along the plan segment a→b ([x, z]), half_w thick across, from y0 to y1 (turned about y)."""
    dx, dz = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dz) + 2 * ext
    mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    return d.box(id, [mx - L / 2, y0, mz - half_w, mx + L / 2, y1, mz + half_w], mat, r=r,
                 rot=rot("y", round(yrot_deg(dx, dz), 2), [mx, 0, mz]), **kw)


def strokes(d, id, polys, mat, w=4, z=0.0, extra=None):
    """Line drawing on a front face (x/y) at depth z: each polyline segment a thin decal turned about z.
    `extra` = an additional turn (rots entry) applied after, e.g. the tilt of the board the drawing is on."""
    n = 0
    for poly_ in polys:
        for a, b in zip(poly_, poly_[1:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            ln = math.hypot(b[0] - a[0], b[1] - a[1])
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            at = [mx, my, z]
            p = d.add(f"{id}-{n}", "decal", mat, at=at, size=[ln + w, w], face="front", soft=True,
                      rot={"axis": "z", "deg": round(ang, 1), "about": at})
            if extra: p["rots"] = [extra]
            n += 1
    return n


def ring(cx, cy, rx, ry=None, a0=0, a1=360, n=16):
    ry = ry or rx
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]
