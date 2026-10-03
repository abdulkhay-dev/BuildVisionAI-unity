"""Helpers of batch kinesio-4 (shared by the k4_*.py generators only)."""
import math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import p1lib
from lib import D, rnd, rot, sec, rep

text = p1lib.text
# digits the shared font lacks (added here at import, for this batch's labels only)
p1lib._FONT.setdefault("1", (0.3, [[(0, 0.75), (0.3, 1), (0.3, 0)]]))
p1lib._FONT.setdefault("4", (0.56, [[(0.42, 0), (0.42, 1), (0, 0.32), (0.56, 0.32)]]))
p1lib._FONT.setdefault("2", (0.52, [[(0, 0.8), (0.14, 1), (0.4, 1), (0.52, 0.8), (0.52, 0.62), (0, 0), (0.52, 0)]]))
p1lib._FONT.setdefault("3", (0.52, [[(0, 0.86), (0.14, 1), (0.4, 1), (0.52, 0.84), (0.52, 0.64), (0.38, 0.52), (0.18, 0.52)], [(0.38, 0.52), (0.52, 0.4), (0.52, 0.16), (0.4, 0), (0.12, 0), (0, 0.14)]]))
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


def mesh(d, id, x0, x1, z0, z1, y, step, wire, mat, nx=None, nz=None):
    """A flat wire grid in the x-z plane at height y: wires along x (repeated along z) and along z (repeated along x)."""
    nz_ = nz or int(round((z1 - z0) / step)) + 1
    nx_ = nx or int(round((x1 - x0) / step)) + 1
    sz = (z1 - z0) / (nz_ - 1); sx = (x1 - x0) / (nx_ - 1)
    d.cyl(id + "-x", [x0, y, z0], [x1, y, z0], wire, mat, repeat={"n": nz_, "step": [0, 0, sz]})
    d.cyl(id + "-z", [x0, y + wire * 0.9, z0], [x0, y + wire * 0.9, z1], wire, mat, repeat={"n": nx_, "step": [sx, 0, 0]})


def vmesh(d, id, x0, x1, y0, y1, z, step, wire, mat):
    """A vertical wire grid in the x-y plane at depth z."""
    ny = int(round((y1 - y0) / step)) + 1; nx = int(round((x1 - x0) / step)) + 1
    sy = (y1 - y0) / (ny - 1); sx = (x1 - x0) / (nx - 1)
    d.cyl(id + "-h", [x0, y0, z], [x1, y0, z], wire, mat, repeat={"n": ny, "step": [0, sy, 0]})
    d.cyl(id + "-v", [x0, y0, z + wire * 0.9], [x0, y1, z + wire * 0.9], wire, mat, repeat={"n": nx, "step": [sx, 0, 0]})
