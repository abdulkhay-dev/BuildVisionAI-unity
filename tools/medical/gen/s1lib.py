"""Helpers of batch sensory-1 (multi-sensory room). Millimetres; frame of Docs/medical-designs.md."""
import math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lib import D, rot, sec, rep
from sflib import poly_path, rrect_pts, round_poly, ellipse_pts, f


def path(pts, close=True):
    return poly_path(pts, close)


def circle_pts(cx, cy, r, n=28):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def ring_path(cx, cy, r0, r1, n=32):
    """Annulus outline (outer + inner subpath)."""
    o = circle_pts(cx, cy, r1, n)
    i = list(reversed(circle_pts(cx, cy, r0, n)))
    return path(o) + " " + path(i)


def _in_rr(x, y, x0, y0, x1, y1, r):
    if x < x0 or x > x1 or y < y0 or y > y1:
        return False
    cx = min(max(x, x0 + r), x1 - r); cy = min(max(y, y0 + r), y1 - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r + 1e-6


def union_outline(shapes, centre, n=240):
    """Outline of a union of rounded rects ('rr', x0, y0, x1, y1, r) and circles ('c', cx, cy, r), traced in polar
    steps from `centre` (the union must be star-shaped from there)."""
    def inside(x, y):
        for s in shapes:
            if s[0] == "rr" and _in_rr(x, y, *s[1:]):
                return True
            if s[0] == "c" and (x - s[1]) ** 2 + (y - s[2]) ** 2 <= s[3] ** 2:
                return True
        return False
    cx, cy = centre
    pts = []
    for k in range(n):
        a = 2 * math.pi * k / n
        dx, dy = math.cos(a), math.sin(a)
        lo, hi = 0.0, 3000.0
        # coarse march to the last inside point, then bisect
        t = 0.0; last = 0.0
        while t < hi:
            if inside(cx + dx * t, cy + dy * t):
                last = t
            t += 4.0
        lo, hi = last, last + 4.0
        for _ in range(12):
            m = (lo + hi) / 2
            if inside(cx + dx * m, cy + dy * m):
                lo = m
            else:
                hi = m
        pts.append((cx + dx * lo, cy + dy * lo))
    return pts


def disc(d, id, cx, cy, z, dia, mat, h=1.5, **kw):
    """A flat round disc on a front face at z (from z to z + h)."""
    return d.cyl(id, [cx, cy, z], [cx, cy, z + h], dia, mat, soft=True, **kw)


def strokes(d, id, polys, z, w, mat, soft=True):
    """Lines drawn on a front face (z) as rotated decal strokes: polys = list of [(x, y), ...]."""
    n = 0
    for poly in polys:
        for a, b in zip(poly, poly[1:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            ln = math.hypot(b[0] - a[0], b[1] - a[1])
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            at = [mx, my, z]
            d.decal(f"{id}-{n}", at, [ln + w * 0.9, w], "front", mat, soft=soft, rot=rot("z", round(ang, 1), at))
            n += 1
    return n


def bars(d, id, polys, z0, z1, w, mat):
    """Lines as thin proud boxes (dark marks on light faces): each segment a box turned about z."""
    n = 0
    for poly in polys:
        for a, b in zip(poly, poly[1:]):
            mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
            ln = math.hypot(b[0] - a[0], b[1] - a[1]) + w * 0.9
            ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
            d.box(f"{id}-{n}", [mx - ln / 2, my - w / 2, z0, mx + ln / 2, my + w / 2, z1], mat, soft=True,
                  rot=rot("z", round(ang, 1), [mx, my, z0]))
            n += 1
    return n


def tri_pts(cx, cy, s, direction):
    """Equilateral-ish triangle of size s pointing up/down/left/right."""
    h = s * 0.87
    if direction == "up":
        return [(cx - s / 2, cy - h / 3), (cx + s / 2, cy - h / 3), (cx, cy + 2 * h / 3)]
    if direction == "down":
        return [(cx + s / 2, cy + h / 3), (cx - s / 2, cy + h / 3), (cx, cy - 2 * h / 3)]
    if direction == "right":
        return [(cx - h / 3, cy - s / 2), (cx + 2 * h / 3, cy), (cx - h / 3, cy + s / 2)]
    return [(cx + h / 3, cy + s / 2), (cx - 2 * h / 3, cy), (cx + h / 3, cy - s / 2)]


def star_pts(cx, cy, R, r=None, rot_deg=90):
    r = r or R * 0.45
    pts = []
    for k in range(10):
        a = math.radians(rot_deg + 36 * k)
        rr = R if k % 2 == 0 else r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts


def front_slab(d, id, pts_or_path, z0, z1, mat, r=None, **kw):
    o = pts_or_path if isinstance(pts_or_path, str) else path(pts_or_path)
    return d.add(id, "slab", mat, plane="front", outline=o, w=[z0, z1], r=r, **kw)


def side_slab(d, id, pts, x0, x1, mat, r=None, **kw):
    """Profile in the side plane: points (z, y), extruded along x."""
    o = pts if isinstance(pts, str) else path(pts)
    return d.add(id, "slab", mat, plane="side", outline=o, w=[x0, x1], r=r, **kw)


def top_slab(d, id, pts, y0, y1, mat, r=None, **kw):
    """Outline in the top plane: points (x, z), extruded along y."""
    o = pts if isinstance(pts, str) else path(pts)
    return d.add(id, "slab", mat, plane="top", outline=o, w=[y0, y1], r=r, **kw)


# ---------------------------------------------------------------- the wall-panel family
def panel_case(d, W, H, Dp, ears, body, bumps, buttons, logo, grille_mat, case="case", btn_ring=None):
    """Common case of the sensory wall panels.
    ears: [(cx, cy, r)], body: (x0, y0, x1, y1, r), bumps: [(cx, cy, size)], buttons: [(cx, cy, dia, mat)],
    logo: (cx, cy)."""
    shapes = [("rr",) + tuple(body)] + [("c", cx, cy, r) for cx, cy, r in ears]
    pts = union_outline(shapes, ((body[0] + body[2]) / 2, (body[1] + body[3]) / 2))
    front_slab(d, "case", pts, 0, Dp, case, r=22)
    # speaker grilles in the ears: a dotted disc (slightly darker tone + dot rows)
    for i, (cx, cy, r) in enumerate(ears):
        gx = cx + (6 if cx < W / 2 else -6); gy = cy - 8
        # a round grille of small holes: rows of dots filling a circle of r 30
        for j in range(-3, 4):
            hc = math.sqrt(max(0.0, 30 ** 2 - (j * 8) ** 2))
            n = int(2 * hc / 8) + 1
            disc(d, f"grille{i}-{j + 3}", gx - (n - 1) * 4, gy + j * 8, Dp, 4.2, grille_mat, h=0.8,
                 repeat={"n": n, "step": [8, 0, 0]})
    # bottom-corner bumps: low raised rounded squares with a small ring
    for i, (cx, cy, s) in enumerate(bumps):
        front_slab(d, f"bump{i}", rrect_pts(cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2, s * 0.38), Dp - 2, Dp + 5, case, r=4)
        front_slab(d, f"bumpring{i}", ring_path(cx, cy, 20, 25), Dp + 5, Dp + 6, grille_mat, soft=True)
    # push buttons with darker rings
    for i, (cx, cy, dia, mat) in enumerate(buttons):
        ring = btn_ring or grille_mat
        d.cyl(f"btnring{i}", [cx, cy, Dp - 1], [cx, cy, Dp + 3], dia + 9, ring, soft=True)
        d.lathe(f"btn{i}", [cx, cy, Dp + 3], [[0, 0], [dia / 2, 0], [dia / 2, 5], [dia / 2 - 3, 8], [0, 9]], mat, axis="z", soft=True)
    # logo: leaf mark in a green square + green characters + a tiny text line
    lx, ly = logo
    front_slab(d, "logo-sq", rrect_pts(lx - 52, ly - 14, lx - 24, ly + 14, 11), Dp, Dp + 1.2, "gloss#1f9a3c", soft=True)
    strokes(d, "logo-leaf", [[(lx - 47, ly - 8), (lx - 42, ly + 4), (lx - 34, ly + 9), (lx - 28, ly + 9)],
                             [(lx - 46, ly - 9), (lx - 36, ly - 4), (lx - 29, ly + 2)]], Dp + 1.4, 4, "gloss#d8e83a")
    for k in range(3):
        x = lx - 16 + k * 22
        strokes(d, f"logo-c{k}", [[(x, ly + 12), (x + 16, ly + 12)], [(x + 8, ly + 14), (x + 8, ly - 2)],
                                  [(x, ly + 4), (x + 16, ly + 4)], [(x + 2, ly - 2), (x + 14, ly - 2)]],
                Dp + 0.6, 3, "gloss#1d5a32")
    d.decal("logo-en", [lx + 5, ly - 10, Dp + 0.6], [62, 3], "front", "gloss#1d5a32", soft=True)
