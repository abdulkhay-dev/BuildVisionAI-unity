"""Helpers for the hydro-1 generators (tubs): plan outlines in the top plane (x, z) mm, tub shells with open basins."""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from lib import *


def P(pts):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def ring(outer, inner):
    """Outline with a hole: outer points + inner points (two subpaths)."""
    return P(outer) + " " + P(inner)


def arc(cx, cy, r, a0, a1, n=8, ry=None):
    ry = r if ry is None else ry
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)),
             cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def rr(x0, y0, x1, y1, r, n=None):
    """Rounded rectangle points; r = one radius or 4 [(x1,y0), (x1,y1), (x0,y1), (x0,y0)]."""
    if isinstance(r, (int, float)): r = [r] * 4
    a, b, c, d = [max(0.01, min(v, (x1 - x0) / 2 - 0.5, (y1 - y0) / 2 - 0.5)) for v in r]
    if n is None: n = max(4, min(24, int(max(a, b, c, d) / 15)))
    return (arc(x1 - a, y0 + a, a, -90, 0, n) + arc(x1 - b, y1 - b, b, 0, 90, n) +
            arc(x0 + c, y1 - c, c, 90, 180, n) + arc(x0 + d, y0 + d, d, 180, 270, n))


def ell(cx, cy, rx, ry, n=48):
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


def profile_outline(x0, x1, hw, cz, n=60, off=0.0):
    """Closed plan outline symmetric about z = cz with half width hw(t) (t 0..1 from x0 to x1), ends closed by the
    curve going to 0 width; off grows it outward (approx. offset)."""
    top, bot = [], []
    for k in range(n + 1):
        t = k / n
        # cosine spacing to resolve the round ends
        tt = 0.5 - 0.5 * math.cos(math.pi * t)
        x = x0 + (x1 - x0) * tt
        h = hw(tt)
        top.append((x, cz + h)); bot.append((x, cz - h))
    pts = top + list(reversed(bot[1:-1]))
    if off:
        pts = offset(pts, off)
    return pts


def offset(pts, d):
    """Move every vertex of a closed polygon outward by d along the averaged normal (smooth outlines only)."""
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    s = 1 if area > 0 else -1
    out = []
    for i in range(n):
        ax, ay = pts[i - 1]; bx, by = pts[i]; cx, cy = pts[(i + 1) % n]
        tx, ty = cx - ax, cy - ay
        l = math.hypot(tx, ty) or 1
        nx, ny = ty / l * s, -tx / l * s
        out.append((bx + nx * d, by + ny * d))
    return out


def tub(d, pre, body, hole, rim, rim_y, rim_t, floor_y, wall, mat="shell", inner="inner", rim_r=None,
        body_caps=False, water=None, water_mat="water"):
    """Open tub: body loft (or None when drawn elsewhere), inner walls + floor + domed rim ring, optional water."""
    if body:
        d.loft(pre + "body", body, mat, caps=body_caps)
    d.slab(pre + "walls", "top", ring(wall, hole), [floor_y, rim_y + 1], inner, r=4)
    d.slab(pre + "floor", "top", P(wall), [floor_y - 25, floor_y], inner, r=4)
    d.slab(pre + "rim", "top", ring(rim, hole), [rim_y, rim_y + rim_t], mat, r=rim_r if rim_r else rim_t * 0.45)
    if water is not None:
        d.slab(pre + "water", "top", P(offset(hole, 4)), [water - 4, water], water_mat, r=2, soft=True)


def valve(d, id, x, y, z, mat="chrome", disc=110, lever=90, ang=0, plate=True):
    """Chrome lever valve on a round plate on a flat rim: plate, body, lever (ang = lever heading deg about y)."""
    if plate:
        d.lathe(id + "-plate", [x, y, z], [[0, 0], [disc / 2, 0], [disc / 2, 4], [disc / 2 - 8, 9], [0, 9]], mat)
    d.lathe(id + "-body", [x, y, z], [[0, 0], [22, 0], [22, 30], [18, 45], [12, 52], [0, 52]], mat)
    a = math.radians(ang)
    d.cyl(id + "-lever", [x, y + 44, z], [x + lever * math.sin(a), y + 52, z + lever * math.cos(a)], 16, mat, d2=12)
