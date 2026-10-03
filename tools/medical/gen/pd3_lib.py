"""Helpers of batch pediatric-3 (on top of lib.py); used only by the pd3_*.py generators."""
import math
from lib import D, rot, sec, rep


def rigid_caster(d, id, x, z, wd, tyre, bracket, hub="plastic#9aa3ad", width=26, plate_h=None, hub_k=0.45, **kw):
    """Fixed walker castor: wheel (axis x) touching the floor at (x, z), hub, two side plates in `bracket` colour
    rising to a top plate at y = wd + 20. Returns the top y."""
    r = wd / 2
    top = wd + 22
    d.add(id + "-tyre", "wheel", tyre, at=[x, r, z], d=wd, d2=width, axis="x", **kw)
    d.add(id + "-hub", "wheel", hub, at=[x, r, z], d=wd * hub_k, d2=width + 6, axis="x", **kw)
    t = 4
    for s, nm in ((-1, "a"), (1, "b")):
        xo = x + s * (width / 2 + 5)
        d.add(id + "-pl" + nm, "box", bracket,
              box=[xo - t / 2, r - 14, z - r * 0.55, xo + t / 2, top, z + r * 0.55], r=1.5, **kw)
    d.add(id + "-top", "box", bracket, box=[x - width / 2 - 8, top - 6, z - r * 0.6, x + width / 2 + 8, top, z + r * 0.6], r=2, **kw)
    d.add(id + "-axle", "cyl", "chrome", **{"from": [x - width / 2 - 9, r, z], "to": [x + width / 2 + 9, r, z]}, d=9, **kw)
    return top


def along(a, b, t):
    return [a[i] + (b[i] - a[i]) * t for i in range(3)]


def unit(a, b):
    v = [b[i] - a[i] for i in range(3)]
    L = math.sqrt(sum(c * c for c in v))
    return [c / L for c in v], L


def stripes(d, id, a, b, dd, colours, band, start=0.0, **kw):
    """Coloured sleeve bands (cyl d=dd) along the segment a→b, repeating `colours`, each `band` mm long."""
    u, L = unit(a, b)
    n = len(colours)
    per = int((L - start) // (band * n)) + 1
    for k, c in enumerate(colours):
        s0 = start + k * band
        if s0 >= L: break
        m = int((L - s0) // (band * n)) + (1 if (L - s0) % (band * n) > band * 0.5 else 0)
        m = max(1, min(per, m))
        p0 = [a[i] + u[i] * s0 for i in range(3)]
        p1 = [a[i] + u[i] * (s0 + band) for i in range(3)]
        d.add(f"{id}-{k}", "cyl", c, **{"from": p0, "to": p1}, d=dd, sides=20,
              repeat={"n": m, "step": [u[i] * band * n for i in range(3)]}, **kw)
