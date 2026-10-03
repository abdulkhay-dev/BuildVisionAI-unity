"""Helpers of batches pediatric-4 / pediatric-5 (children's rehab equipment). Millimetres.
Each pd4_*.py writes only its own devices' design files: `python3 pd4_x.py [id ...]` (no ids = all of the file)."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import D, rot, sec, rep
from h1lib import P, ring, arc, rr, ell


def polar(cx, cz, r, a):
    """Point at angle a (deg; 0 = +x, 90 = +z = the front) on a circle of radius r around (cx, cz)."""
    return (cx + r * math.cos(math.radians(a)), cz + r * math.sin(math.radians(a)))


def circ(cx, cz, r, n=48, a0=0.0):
    return [polar(cx, cz, r, a0 + 360.0 * k / n) for k in range(n)]


def sector(cx, cz, r0, r1, a0, a1, n=16):
    """Annulus sector outline points (top plane x/z): outer arc a0 -> a1, inner arc back."""
    out = [polar(cx, cz, r1, a0 + (a1 - a0) * k / n) for k in range(n + 1)]
    inn = [polar(cx, cz, r0, a1 - (a1 - a0) * k / n) for k in range(n + 1)]
    return out + inn


def poly(pts, y=None):
    """2D (x, z) points -> 3D path at height y, or 3D points unchanged."""
    return [[p[0], y, p[1]] for p in pts] if y is not None else [list(p) for p in pts]


def caster(d, id, x, z, dd=60, copies=None):
    return d.add(id, "caster", at=[x, 0, z], d=dd, copies=copies)


def wheel(d, id, at, dd, w, mat, axis="x", **kw):
    return d.add(id, "wheel", mat, at=at, d=dd, d2=w, axis=axis, **kw)


def screen(d, id, box, mat, **kw):
    return d.add(id, "screen", mat, box=box, **kw)


def corners(x0, z0, x1, z1):
    return [[x1 - x0, 0, 0], [0, 0, z1 - z0], [x1 - x0, 0, z1 - z0]]


def main(builders):
    """builders: {id: function() -> D}; build the ids given on the command line (all when none)."""
    ids = sys.argv[1:] or list(builders)
    for i in ids:
        builders[i]().save()
