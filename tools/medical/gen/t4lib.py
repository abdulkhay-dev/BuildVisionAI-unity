"""Helpers for batches table-4 / table-5 (traction tables, tilt tables, TMS couch/chair). Millimetres."""
import math
from lib import D, rot, sec, rep
from sflib import poly_path, rrect_pts, chamfer_pts, round_poly, stadium_pts, ellipse_pts, quad, f


def top_pad(d, id, x0, x1, z0, z1, y0, y1, mat, cr=40, r=10, **kw):
    """A flat rounded-rectangle slab (pads, trays, boards) lying in x/z from y0 to y1."""
    return d.add(id, "slab", mat, plane="top", outline=poly_path(rrect_pts(x0, z0, x1, z1, cr)), w=[y0, y1], r=r, **kw)


def cham_pad(d, id, x0, x1, z0, z1, y0, y1, mat, cx=60, cz=60, cr=15, r=8, **kw):
    return d.add(id, "slab", mat, plane="top", outline=poly_path(chamfer_pts(x0, z0, x1, z1, cx, cz, cr)), w=[y0, y1], r=r, **kw)


def side_slab(d, id, pts, x0, x1, mat, r=10, **kw):
    """A profile in the z/y plane (points (z, y)) extruded along x from x0 to x1."""
    return d.add(id, "slab", mat, plane="side", outline=poly_path(pts), w=[x0, x1], r=r, **kw)


def front_slab(d, id, pts, z0, z1, mat, r=10, **kw):
    """A profile in the x/y plane (points (x, y)) extruded along z from z0 to z1."""
    return d.add(id, "slab", mat, plane="front", outline=poly_path(pts), w=[z0, z1], r=r, **kw)


def castor(d, id, x, z, dd=75, copies=None):
    d.add(id, "caster", at=[x, 0, z], d=dd, copies=copies)


def corners(x0, z0, x1, z1):
    """copies for the 3 other corners of a rectangle given the first corner (x0, z0)."""
    return [[x1 - x0, 0, 0], [0, 0, z1 - z0], [x1 - x0, 0, z1 - z0]]


def arc_pts(cx, cy, r, a0, a1, n=8):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + r * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


# ---- lettering (review 2026-10-02): p1lib.text() without p1lib's D-method patches (its decal takes another order)
import lib as _lib
_saved = {k: getattr(_lib.D, k) for k in ("bar", "lathe", "sphere", "decal", "slab", "loft")}
import p1lib as _p1
for _k, _v in _saved.items():
    setattr(_lib.D, _k, _v)
_p1._FONT.setdefault("医", (0.92, [[(0.92, 0.95), (0.04, 0.95), (0.04, 0), (0.94, 0)], [(0.3, 0.86), (0.22, 0.66)],
                                   [(0.26, 0.74), (0.74, 0.74)], [(0.16, 0.46), (0.84, 0.46)],
                                   [(0.47, 0.74), (0.45, 0.46), (0.22, 0.14)], [(0.5, 0.42), (0.8, 0.14)]]))
_p1._FONT.setdefault("疗", (0.95, [[(0.52, 1), (0.52, 0.9)], [(0.2, 0.86), (0.95, 0.86)], [(0.2, 0.86), (0.2, 0.36), (0.04, 0.02)],
                                   [(0, 0.72), (0.1, 0.62)], [(0, 0.44), (0.1, 0.52)],
                                   [(0.38, 0.66), (0.86, 0.66), (0.62, 0.48)], [(0.62, 0.48), (0.62, 0), (0.5, 0.05)]]))
text = _p1.text
text_len = _p1.text_len


def brand(d, id, x, y, z, h, mat="logo", white="white", en=True, cn=True):
    """Xiangyu logo on a front face (z = the face): blue disc with the white cross, '翔宇医疗' of cap height h and
    'XIANGYU MEDICAL' under it. (x, y) = the bottom-left of the Chinese line; the disc stands left of it."""
    rd = h * 1.25
    cx, cy = x - rd * 0.62, y + h * 0.35
    d.cyl(id + "-disc", [cx, cy, z], [cx, cy, z + 1], rd, mat, soft=True)
    d.decal(id + "-v", [cx - rd * 0.05, cy - rd * 0.1, z + 1.3], [rd * 0.16, rd * 0.62], "front", white, soft=True)
    d.decal(id + "-h", [cx, cy + rd * 0.14, z + 1.3], [rd * 0.66, rd * 0.13], "front", white, soft=True)
    d.decal(id + "-k", [cx + rd * 0.2, cy - rd * 0.08, z + 1.3], [rd * 0.12, rd * 0.3], "front", white, soft=True)
    if cn:
        text(d, id + "-cn", "翔宇医疗", [x, y, z + 0.6], h, mat, stroke=max(2.0, h * 0.11), gap=0.12)
    if en:
        text(d, id + "-en", "XIANGYU MEDICAL", [x + h * 0.05, y - h * 0.62, z + 0.6], h * 0.36, mat, gap=0.3)


def tilt_parts(d, prefix, r):
    """Turn every part whose id starts with `prefix` by r after its own rot (a label laid on a sloping face)."""
    for p in d.d["parts"]:
        if p["id"].startswith(prefix):
            if "rot" in p:
                p.setdefault("rots", []).append(r)
            else:
                p["rot"] = r
