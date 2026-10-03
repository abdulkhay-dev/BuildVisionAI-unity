"""Helpers of batch kinesio-6 (only the k6_*.py generators use this)."""
import math
from pfx_lib import *


def caster(d, id, at, dd=75, mat="rubber#3a3d42", **kw): return d.add(id, "caster", mat, at=at, d=dd, **kw)


def star_knob(d, id, at, axis, sign, mat="plastic#1d1f22", dd=40, l=32, **kw):
    """Black star clamp knob: a stem then a lobed head, pointing along axis (x/y/z) in direction sign."""
    prof = [[0, 0], [6, 0], [6, l * 0.45], [dd / 2, l * 0.5], [dd / 2, l * 0.92], [dd / 2 - 5, l], [0, l]]
    if sign < 0:
        r = {"x": rot("y", 180, at), "y": rot("x", 180, at), "z": rot("y", 180, at)}[axis]
        return d.lathe(id, at, prof, mat, axis=axis, rot=r, **kw)
    return d.lathe(id, at, prof, mat, axis=axis, **kw)


def ball_knob(d, id, at, axis, sign, mat="plastic#1d1f22", dd=34, l=30, **kw):
    """Round black clamp knob on a short stem."""
    x, y, z = at
    v = {"x": (1, 0, 0), "y": (0, 1, 0), "z": (0, 0, 1)}[axis]
    tip = [x + v[0] * sign * l, y + v[1] * sign * l, z + v[2] * sign * l]
    d.cyl(id + "-stem", at, tip, 10, "chrome", **kw)
    return d.sphere(id, tip, dd, mat, **kw)


def post(d, id, x, z, y0, y1, out, white="plastic#f1f1ee", inner="chrome", knob="plastic#1d1f22", dd=32,
         din=25, frac=0.62, flange=True, knob_side="z"):
    """Telescopic handrail post: white outer tube from y0, chrome inner tube to y1, black star knob at the joint
    pointing outward (out = +1/-1 along knob_side), a small round foot flange."""
    yj = y0 + (y1 - y0) * frac
    d.cyl(id, [x, y0, z], [x, yj, z], dd, white)
    d.cyl(id + "-in", [x, yj - 20, z], [x, y1, z], din, inner)
    d.cyl(id + "-col", [x, yj - 6, z], [x, yj + 14, z], dd + 6, white)
    if knob_side == "z":
        star_knob(d, id + "-k", [x, yj, z + out * (dd / 2)], "z", out, knob)
    else:
        star_knob(d, id + "-k", [x + out * (dd / 2), yj, z], "x", out, knob)
    if flange:
        d.cyl(id + "-fl", [x, y0, z], [x, y0 + 5, z], dd + 34, white)


def rail_saddle(d, id, x, y, z, mat="chrome"):
    """Small saddle bracket under a handrail (top of a post)."""
    d.box(id, [x - 22, y - 28, z - 16, x + 22, y - 12, z + 16], mat, r=4)
