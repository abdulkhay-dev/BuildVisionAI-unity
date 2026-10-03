"""Helpers of batch other-1 / other-2 (o_*.py generators) on top of lib.py."""
import math
from lib import D, rot, sec, rep
from t4lib import text, text_len, brand


def caster(d, id, at, dd=75, mat="rubber", **kw):
    return d.add(id, "caster", mat, at=at, d=dd, **kw)


def screen(d, id, box, mat, **kw):
    return d.add(id, "screen", mat, box=box, **kw)


def rr(x0, y0, x1, y1, r):
    """SVG rounded rectangle (absolute plane coords)."""
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    return (f"M {x0 + r} {y0} L {x1 - r} {y0} Q {x1} {y0} {x1} {y0 + r} L {x1} {y1 - r} Q {x1} {y1} {x1 - r} {y1} "
            f"L {x0 + r} {y1} Q {x0} {y1} {x0} {y1 - r} L {x0} {y0 + r} Q {x0} {y0} {x0 + r} {y0} Z")


def rr4(x0, y0, x1, y1, r00, r10, r11, r01):
    """SVG rectangle with its own radius per corner: (x0,y0), (x1,y0), (x1,y1), (x0,y1)."""
    return (f"M {x0 + r00} {y0} L {x1 - r10} {y0} Q {x1} {y0} {x1} {y0 + r10} L {x1} {y1 - r11} Q {x1} {y1} {x1 - r11} {y1} "
            f"L {x0 + r01} {y1} Q {x0} {y1} {x0} {y1 - r01} L {x0} {y0 + r00} Q {x0} {y0} {x0 + r00} {y0} Z")


def circle(cx, cy, r, ccw=False):
    s = 0 if ccw else 1
    return f"M {cx - r} {cy} A {r} {r} 0 1 {s} {cx + r} {cy} A {r} {r} 0 1 {s} {cx - r} {cy} Z"


def lerp(a, b, t):
    return [a[i] + (b[i] - a[i]) * t for i in range(len(a))]


def stadium(p0, p1, r, n=8):
    """SVG path of a stadium (rounded-end bar) of half-width r between plane points p0 and p1."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    pts = []
    a0 = math.atan2(ny, nx)
    for k in range(n + 1):  # cap around p1: from +n to -n via +u
        a = a0 - math.pi * k / n
        pts.append((p1[0] + r * math.cos(a), p1[1] + r * math.sin(a)))
    for k in range(n + 1):
        a = a0 + math.pi - math.pi * k / n
        pts.append((p0[0] + r * math.cos(a), p0[1] + r * math.sin(a)))
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def poly(pts):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


# extra glyphs for the stroke font (shared dict of p1lib)
from t4lib import _p1
_p1._FONT.setdefault("Z", (0.56, [[(0, 1), (0.56, 1), (0, 0), (0.56, 0)]]))
_p1._FONT.setdefault("2", (0.52, [[(0, 0.78), (0.12, 1), (0.4, 1), (0.52, 0.8), (0.5, 0.6), (0, 0), (0.52, 0)]]))
_p1._FONT.setdefault("0", (0.52, [[(0.12, 0), (0, 0.2), (0, 0.8), (0.12, 1), (0.4, 1), (0.52, 0.8), (0.52, 0.2), (0.4, 0), (0.12, 0)]]))
