"""Helpers of batch pediatric-2 (only used by the pd2_*.py generators)."""
import math
from lib import *

YEL = "plastic#f2b416"      # yellow powder-coated steel tube of the kids' gym line
RED = "leather#d42a26"      # red foam sleeve
BLU = "leather#2a5db0"      # blue foam sleeve
BLK = "rubber#1c1c1e"       # black end caps / feet


def arc_xy(cx, cy, z, r, a0, a1, n=16, ry=None):
    """Arc in the x-y plane at depth z, angles in degrees (0 = +x, 90 = up)."""
    ry = ry or r
    return [[cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n)), z]
            for k in range(n + 1)]


def arc_xz(cx, cz, y, r, a0, a1, n=16, rz=None):
    """Arc in the x-z plane at height y (0 = +x, 90 = +z)."""
    rz = rz or r
    return [[cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), y, cz + rz * math.sin(math.radians(a0 + (a1 - a0) * k / n))]
            for k in range(n + 1)]


Design = D


def svg_poly(pts):
    return "M " + " L ".join(f"{a:.1f} {b:.1f}" for a, b in pts) + " Z"


def ellipse_pts(ca, cb, ra, rb, tilt=0.0, n=40):
    t = math.radians(tilt)
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        u, v = ra * math.cos(a), rb * math.sin(a)
        out.append((ca + u * math.cos(t) - v * math.sin(t), cb + u * math.sin(t) + v * math.cos(t)))
    return out


def capped_bar_x(d, id, x0, x1, y, z, dia, mat=YEL, cap=BLK, capl=45, capd=None):
    """Horizontal tube along x with black end caps (the floor bars of the kids' gym line)."""
    capd = capd or dia + 8
    d.cyl(id, [x0 + capl - 5, y, z], [x1 - capl + 5, y, z], dia, mat)
    d.add(id + "-cap", "lathe", cap, at=[x0, y, z], axis="x",
          profile=[[0, 0], [capd / 2 - 5, 0], [capd / 2, 5], [capd / 2, capl - 4], [capd / 2 - 3, capl], [0, capl]])
    d.add(id + "-cap2", "lathe", cap, at=[x1, y, z], axis="x",
          profile=[[0, 0], [capd / 2 - 5, 0], [capd / 2, 5], [capd / 2, capl - 4], [capd / 2 - 3, capl], [0, capl]],
          rot=rot("y", 180, [x1, y, z]))


def foam(d, id, a, b, dia, mat, **kw):
    """A foam sleeve: a cylinder with softly rounded ends (lathe along the segment would need a turn; cyl is enough)."""
    return d.cyl(id, a, b, dia, mat, **kw)


def spline(pts, n=6):
    """Catmull-Rom curve through the points (3D), n samples per segment, ends kept."""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            out.append([0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2 +
                               (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(3)])
    out.append(list(pts[-1]))
    return out


def wbox(d, id, b, mat, face="front", **kw):
    """A wooden box whose grain runs along x: the engine lays the grain along y on front faces and along z on top
    faces, so the box is drawn turned 90 deg (about z for a front-face board, about y for a top-face board)."""
    x0, y0, z0, x1, y1, z1 = b
    cx, cy, cz = (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2
    L, h, t = x1 - x0, y1 - y0, z1 - z0
    if face == "front":
        lb = [cx - h / 2, cy - L / 2, z0, cx + h / 2, cy + L / 2, z1]
        r = rot("z", 90, [cx, cy, cz])
    else:
        lb = [cx - t / 2, y0, cz - L / 2, cx + t / 2, y1, cz + L / 2]
        r = rot("y", 90, [cx, cy, cz])
    if "rot" in kw:   # an extra turn goes after the grain turn
        kw["rots"] = [kw.pop("rot")] + kw.get("rots", [])
    return d.box(id, lb, mat, rot=r, **kw)
