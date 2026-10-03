"""Helpers of batch kinesio-2 (only the k2_*.py generators use this)."""
import math
from pfx_lib import *


def sec(at, w, d, r, cx, cz): return {"at": at, "w": w, "d": d, "r": r, "cx": cx, "cz": cz}
def rep(n, step): return {"n": n, "step": step}


def scr(d, id, box, mat, **kw): return d.add(id, "screen", mat, box=box, **kw)
def caster(d, id, at, dd=75, mat="rubber", **kw): return d.add(id, "caster", mat, at=at, d=dd, **kw)
def wheel(d, id, at, dd, w, mat, axis="x", **kw): return d.add(id, "wheel", mat, at=at, d=dd, d2=w, axis=axis, **kw)


def star_knob(d, id, at, axis, sign, mat="plastic#1d1f22", dd=46, l=34, **kw):
    """Black star (lobed) clamp knob: a stem then a fluted head, pointing along axis (x/y/z) in direction sign."""
    prof = [[0, 0], [7, 0], [7, l * 0.45], [dd / 2, l * 0.5], [dd / 2, l * 0.92], [dd / 2 - 5, l], [0, l]]
    if sign < 0:
        prof = prof  # lathes grow along +axis; flip by rotating 180 deg
        r = {"x": rot("y", 180, at), "y": rot("x", 180, at), "z": rot("y", 180, at)}[axis]
        return d.lathe(id, at, prof, mat, axis=axis, rot=r, **kw)
    return d.lathe(id, at, prof, mat, axis=axis, **kw)


def xy_logo(d, id, at, h, face, blue="gloss#2f6fbf", text=True):
    """Xiangyu mark: a blue rounded square with a white cross, the blue 2-line name to its right (front/left/right faces)."""
    x, y, z = at
    d.decal(id + "-mark", at, [h, h], face, blue, soft=True)
    n = {"front": [0, 0, 0.6], "back": [0, 0, -0.6], "left": [-0.6, 0, 0], "right": [0.6, 0, 0], "top": [0, 0.6, 0]}[face]
    x, y, z = x + n[0], y + n[1], z + n[2]   # the white cross a hair in front of the blue square
    d.decal(id + "-bar", [x, y + h * 0.12, z], [h * 0.62, h * 0.14], face, "plastic#ffffff", soft=True)
    d.decal(id + "-stem", [x, y - h * 0.08, z], [h * 0.14, h * 0.55], face, "plastic#ffffff", soft=True)
    if text:
        off = h * 0.6 + h * 1.15
        if face == "front": p = [x + off, y, z]
        elif face == "back": p = [x - off, y, z]
        elif face == "left": p = [x, y, z - off]
        else: p = [x, y, z + off]
        d.decal(id + "-name", [p[0], y + h * 0.15, p[2]], [h * 2.1, h * 0.42], face, blue, soft=True)
        d.decal(id + "-sub", [p[0], y - h * 0.28, p[2]], [h * 2.1, h * 0.14], face, blue, soft=True)


def quad_hole_outline(x0, y0, x1, y1, quad):
    """SVG outline: rectangle (x0,y0)-(x1,y1) with a quad hole (list of 4 points) — mask around a skewed screen crop."""
    q = quad
    return (f"M {x0} {y0} L {x1} {y0} L {x1} {y1} L {x0} {y1} Z "
            f"M {q[0][0]:.1f} {q[0][1]:.1f} L {q[1][0]:.1f} {q[1][1]:.1f} L {q[2][0]:.1f} {q[2][1]:.1f} L {q[3][0]:.1f} {q[3][1]:.1f} Z")


def text_side(d, id, s, origin, h, mat, face="right", gap=0.28, stroke=None, ang=0.0):
    """Lettering on a side face read by a viewer standing at that side (p1lib.text draws the (z, y) plane un-mirrored,
    which reads backwards on the right face): origin = bottom-left of the first letter as seen; reads towards -z on
    the right face, +z on the left one; `ang` = baseline slope (deg, counter-clockwise as seen)."""
    from p1lib import _FONT
    st = stroke or max(1.5, h * 0.14)
    sz = -1 if face == "right" else 1
    ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    n, pen = 0, 0.0
    for c in s:
        if c not in _FONT:
            pen += 0.45; continue
        wch, polys = _FONT[c]
        for poly in polys:
            for a, b in zip(poly, poly[1:]):
                mu, mv = (pen + (a[0] + b[0]) / 2) * h, (a[1] + b[1]) / 2 * h
                du, dv = (b[0] - a[0]) * h, (b[1] - a[1]) * h
                MU, MV = mu * ca - mv * sa, mu * sa + mv * ca          # seen (right, up)
                DU, DV = du * ca - dv * sa, du * sa + dv * ca
                ln = math.hypot(du, dv)
                sang = math.degrees(math.atan2(DV, sz * DU))          # stroke angle in the (z, y) plane
                at = [origin[0], origin[1] + MV, origin[2] + sz * MU]
                d.add(f"{id}-{n}", "decal", mat, at=at, size=[ln + st, st], face=face, soft=True,
                      rot={"axis": "x", "deg": round(-sang, 1), "about": at})
                n += 1
        pen += wch + gap
    return n
