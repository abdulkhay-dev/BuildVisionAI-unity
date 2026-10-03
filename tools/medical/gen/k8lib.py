"""Helpers of batch kinesio-8 (only the k8_*.py generators use this)."""
import math
from p1lib import *   # D (+ bar/lathe/sphere/decal/screen/slab/loft/caster), rot, sec, rep, text, rpoly


def caster(d, id, at, dd=75, mat="rubber#3a3d42", **kw):
    return d.add(id, "caster", mat, at=at, d=dd, **kw)


def ring_pts(c, rx, ry, plane="xy", n=20, a0=0.0):
    """closed ellipse polyline around c in a plane (xy: x/y, zy: z/y, xz: x/z)"""
    pts = []
    for k in range(n + 1):
        a = a0 + 2 * math.pi * k / n
        u, v = rx * math.cos(a), ry * math.sin(a)
        if plane == "xy": pts.append([c[0] + u, c[1] + v, c[2]])
        elif plane == "zy": pts.append([c[0], c[1] + v, c[2] + u])
        else: pts.append([c[0] + u, c[1], c[2] + v])
    return pts


def star_knob(d, id, at, axis, sign, mat="plastic#1d1f22", dd=40, l=32, **kw):
    """Black star/round clamp knob: a stem then a head, pointing along axis (x/y/z) in direction sign."""
    prof = [[0, 0], [6, 0], [6, l * 0.45], [dd / 2, l * 0.5], [dd / 2, l * 0.92], [dd / 2 - 5, l], [0, l]]
    if sign < 0:
        r = {"x": rot("y", 180, at), "y": rot("x", 180, at), "z": rot("y", 180, at)}[axis]
        return d.lathe(id, at, prof, mat, axis=axis, rot=r, **kw)
    return d.lathe(id, at, prof, mat, axis=axis, **kw)


def dumbbell(d, id, a, b, head, mat, grip=None, **kw):
    """Vinyl hex dumbbell from end a to end b (head = head diameter)."""
    L = math.dist(a, b)
    hl = head * 0.55
    u = [(b[i] - a[i]) / L for i in range(3)]
    p = lambda t: [a[i] + u[i] * t for i in range(3)]
    d.cyl(id + "-h1", a, p(hl), head, mat, sides=6, **kw)
    d.cyl(id + "-h2", p(L - hl), b, head, mat, sides=6, **kw)
    d.cyl(id + "-g", p(hl - 5), p(L - hl + 5), head * 0.42, grip or mat, **kw)


class G:
    """A group drawn in a local frame (u right, y up, w outward/front) placed at `o` facing `face` (+z, -z, +x, -x).
    Only right-angle turns, so boxes stay boxes."""
    def __init__(s, d, pre, o, face="+z"):
        s.d, s.pre, s.o, s.face = d, pre, o, face

    def p(s, q):
        u, y, w = q
        ox, oy, oz = s.o
        return {"+z": [ox + u, oy + y, oz + w], "-z": [ox - u, oy + y, oz - w],
                "-x": [ox - w, oy + y, oz + u], "+x": [ox + w, oy + y, oz - u]}[s.face]

    def bx(s, b):
        a, c = s.p(b[:3]), s.p(b[3:])
        return [min(a[0], c[0]), min(a[1], c[1]), min(a[2], c[2]), max(a[0], c[0]), max(a[1], c[1]), max(a[2], c[2])]

    def i(s, id): return f"{s.pre}{id}"
    def box(s, id, b, mat, **kw): return s.d.box(s.i(id), s.bx(b), mat, **kw)
    def cyl(s, id, a, b, dd, mat, **kw): return s.d.cyl(s.i(id), s.p(a), s.p(b), dd, mat, **kw)
    def bar(s, id, a, b, sc, mat, **kw): return s.d.bar(s.i(id), s.p(a), s.p(b), sc, mat, **kw)
    def tube(s, id, path, dd, mat, **kw): return s.d.tube(s.i(id), [s.p(q) for q in path], dd, mat, **kw)

    def top_outline(s, pts):
        """SVG path (top plane: x, z) of a closed polygon given in local (u, w)"""
        q = [s.p([u, 0, w]) for u, w in pts]
        return "M " + " L ".join(f"{a[0]:.1f} {a[2]:.1f}" for a in q) + " Z"


def dumbbell_round(d, id, a, L, head, axis, mat, grip=None, hl=None, **kw):
    """Vinyl dumbbell with rounded (lathed) heads, from point a along +axis (x/y/z) for length L; head = head diameter.
    The grip is a separate thinner part in `grip` colour when given."""
    R = head / 2.0
    hl = hl or head * 0.62
    g = head * 0.21
    prof = [[0, 0], [R * 0.62, 0], [R * 0.9, hl * 0.07], [R, hl * 0.25], [R, hl * 0.75], [R * 0.9, hl * 0.93],
            [R * 0.62, hl], [g, hl + 2], [g, L - hl - 2], [R * 0.62, L - hl], [R * 0.9, L - hl * 0.93],
            [R, L - hl * 0.75], [R, L - hl * 0.25], [R * 0.9, L - hl * 0.07], [R * 0.62, L], [0, L]]
    d.lathe(id, a, [[round(r, 1), round(h, 1)] for r, h in prof], mat, axis=axis, **kw)
