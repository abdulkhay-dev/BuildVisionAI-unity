"""Helpers for the hydro-2 generators (on top of h1lib)."""
from h1lib import *


def logo_round(d, id, at, dia, face="front", blue="gloss#2f6fd0", white="gloss#ffffff", soft=True):
    """Round Xiangyu mark: a blue disc with a white cross-ish 'T' (flat on a front/side face)."""
    x, y, z = at
    if face == "front":
        d.lathe(id, [x, y, z], [[0, 0], [dia / 2, 0], [dia / 2, 1.5], [0, 1.5]], blue, axis="z", soft=soft)
        d.decal(id + "-v", [x + dia * 0.05, y - dia * 0.05, z + 2.4], [dia * 0.16, dia * 0.6], "front", white, soft=True)
        d.decal(id + "-h", [x, y + dia * 0.15, z + 2.4], [dia * 0.62, dia * 0.14], "front", white, soft=True)
    elif face == "right":
        d.lathe(id, [x, y, z], [[0, 0], [dia / 2, 0], [dia / 2, 1.5], [0, 1.5]], blue, axis="x", soft=soft)
        d.decal(id + "-v", [x + 1.6, y - dia * 0.05, z], [dia * 0.16, dia * 0.6], "right", white, soft=True)
        d.decal(id + "-h", [x + 1.6, y + dia * 0.15, z], [dia * 0.62, dia * 0.14], "right", white, soft=True)
    elif face == "left":
        d.lathe(id, [x - 1.5, y, z], [[0, 0], [dia / 2, 0], [dia / 2, 1.5], [0, 1.5]], blue, axis="x", soft=soft)
        d.decal(id + "-v", [x - 1.6, y - dia * 0.05, z], [dia * 0.16, dia * 0.6], "left", white, soft=True)
        d.decal(id + "-h", [x - 1.6, y + dia * 0.15, z], [dia * 0.62, dia * 0.14], "left", white, soft=True)


def bar_handle(d, id, a, b, out, mat="chrome", dia=22, **kw):
    """Grab handle: a bar from a to b standing off by vector out (3 points squared U with bends)."""
    p0 = [a[0], a[1], a[2]]
    p1 = [a[0] + out[0], a[1] + out[1], a[2] + out[2]]
    p2 = [b[0] + out[0], b[1] + out[1], b[2] + out[2]]
    p3 = [b[0], b[1], b[2]]
    d.tube(id, [p0, p1, p2, p3], dia, mat, bend=min(30, max(abs(v) for v in out) * 0.6), **kw)


# ---- lettering (review 2026-10-02): real stroke letters from p1lib.text(), plus the glyphs the brand needs
_keep = {k: D.__dict__[k] for k in ("bar", "lathe", "sphere", "decal", "slab", "loft")}
import p1lib as _p1   # p1lib re-binds some D methods with its own argument order: put lib's back
for _k, _v in _keep.items(): setattr(D, _k, _v)
_p1._FONT.setdefault("医", (0.95, [[(0.92, 0.95), (0.05, 0.95), (0.05, 0.02), (0.95, 0.02)], [(0.36, 0.86), (0.26, 0.64)],
                                  [(0.3, 0.74), (0.78, 0.74)], [(0.18, 0.5), (0.85, 0.5)], [(0.52, 0.74), (0.5, 0.5), (0.24, 0.16)],
                                  [(0.54, 0.44), (0.84, 0.14)]]))
_p1._FONT.setdefault("疗", (0.95, [[(0.56, 1.0), (0.6, 0.9)], [(0.22, 0.88), (0.95, 0.88)], [(0.22, 0.88), (0.22, 0.4), (0.06, 0.02)],
                                  [(0.03, 0.72), (0.12, 0.62)], [(0.0, 0.46), (0.12, 0.38)], [(0.38, 0.7), (0.86, 0.7), (0.64, 0.54)],
                                  [(0.62, 0.56), (0.62, 0.04), (0.5, 0.1)]]))
_p1._FONT.setdefault("J", (0.6, [[(0.6, 1), (0.6, 0.2), (0.45, 0), (0.15, 0), (0, 0.2)]]))
_p1._FONT.setdefault("Z", (0.7, [[(0, 1), (0.7, 1), (0, 0), (0.7, 0)]]))
_CN = {
    "设": [[(0.08, 0.95), (0.16, 0.85)], [(0.02, 0.62), (0.18, 0.62), (0.18, 0.1), (0.28, 0.2)], [(0.5, 0.95), (0.5, 0.7), (0.4, 0.56)],
          [(0.5, 0.95), (0.78, 0.95), (0.78, 0.65), (0.92, 0.62)], [(0.42, 0.5), (0.85, 0.5), (0.45, 0.02)], [(0.52, 0.38), (0.95, 0.02)]],
    "备": [[(0.45, 1), (0.2, 0.7)], [(0.4, 0.88), (0.75, 0.88), (0.25, 0.55)], [(0.45, 0.75), (0.95, 0.55)],
          [(0.2, 0.48), (0.8, 0.48), (0.8, 0), (0.2, 0), (0.2, 0.48)], [(0.5, 0.48), (0.5, 0)], [(0.2, 0.24), (0.8, 0.24)]],
    "有": [[(0.02, 0.8), (0.95, 0.8)], [(0.5, 1.0), (0.12, 0.3)], [(0.3, 0.0), (0.3, 0.6), (0.85, 0.6), (0.85, 0.0), (0.75, 0.05)],
          [(0.3, 0.42), (0.85, 0.42)], [(0.3, 0.24), (0.85, 0.24)]],
    "限": [[(0.08, 0), (0.08, 0.95), (0.28, 0.95), (0.18, 0.7), (0.3, 0.5), (0.15, 0.4)],
          [(0.42, 0.02), (0.42, 0.92), (0.85, 0.92), (0.85, 0.5), (0.42, 0.5)], [(0.42, 0.7), (0.85, 0.7)], [(0.55, 0.5), (0.95, 0.02)],
          [(0.42, 0.1), (0.6, 0.25)]],
    "责": [[(0.1, 0.92), (0.9, 0.92)], [(0.2, 0.78), (0.8, 0.78)], [(0.05, 0.64), (0.95, 0.64)], [(0.5, 1), (0.5, 0.64)],
          [(0.25, 0.15), (0.25, 0.5), (0.75, 0.5), (0.75, 0.15)], [(0.5, 0.5), (0.5, 0.22)], [(0.4, 0.12), (0.15, 0)], [(0.6, 0.12), (0.85, 0)]],
    "任": [[(0.25, 1), (0.05, 0.55)], [(0.15, 0.75), (0.15, 0)], [(0.45, 0.85), (0.9, 0.95)], [(0.38, 0.5), (0.95, 0.5)],
          [(0.66, 0.9), (0.66, 0.02)], [(0.42, 0.02), (0.9, 0.02)]],
    "公": [[(0.38, 0.95), (0.08, 0.55)], [(0.6, 0.95), (0.92, 0.55)], [(0.45, 0.5), (0.15, 0.05), (0.85, 0.1)], [(0.68, 0.3), (0.9, 0.0)]],
    "司": [[(0.1, 0.92), (0.85, 0.92), (0.85, 0.0), (0.72, 0.05)], [(0.15, 0.68), (0.68, 0.68)],
          [(0.2, 0.5), (0.2, 0.12), (0.62, 0.12), (0.62, 0.5), (0.2, 0.5)]],
}
for _c, _s in _CN.items(): _p1._FONT.setdefault(_c, (0.95, _s))
text = _p1.text
text_len = _p1.text_len


def brand_cn(d, id, x, y, z, h, mat, mark=True, face="front"):
    """Round mark + '翔宇医疗' on a front face; (x, y) = the bottom-left of the mark's box."""
    if mark:
        logo_round(d, id + "-m", [x + h * 0.6, y + h * 0.5, z], h * 1.15, face=face)
        x += h * 1.4
    text(d, id + "-t", "翔宇医疗", [x, y, z + 1.6], h, mat, face=face)
