"""Helpers of batches kinesio-9 / kinesio-10 (shared by the k9_*.py generators only)."""
import math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from k4lib import *          # K, text, rpoly, circle, poly, lerp, rot, sec, rep, rotx

# ---- the Xiangyu hydraulic exerciser series (xy-dssz / xy-dsxb / xy-dsxz) ----
EX_MATS = {
    "frame": "plastic#f1e9d3",     # cream powder-coated tube
    "blue": "leather#a6c8e8",      # light-blue vinyl
    "pipe": "leather#e6e1dc",      # light piping band in the middle of every pad
    "cap": "rubber#1c1d20",        # black end caps / feet
    "foam": "rubber#202226",       # black foam grips
    "cyl": "black#1f2226",         # hydraulic cylinder body
    "dark": "plastic#2a2c30",      # brackets, hinge blocks
}
TUBE = 50


def mark(parts_from, d, **extra):
    """Add `extra` keys (e.g. rots) to every part added after index parts_from."""
    for p in d.d["parts"][parts_from:]:
        for k, v in extra.items():
            if k == "rots":
                p.setdefault("rots", []).extend(v)
            else:
                p[k] = v


def foot(d, id, x0, x1, z, y=32, dia=TUBE, cap=64, capl=58):
    """Floor cross tube along x with black end caps."""
    d.cyl(id, [x0 + 20, y, z], [x1 - 20, y, z], dia, "frame")
    d.lathe(id + "-c0", [x0, y, z], [[0, 0], [cap / 2 - 3, 0], [cap / 2, 6], [cap / 2, capl - 6], [cap / 2 - 4, capl], [0, capl]],
            "cap", axis="x")
    d.lathe(id + "-c1", [x1 - capl, y, z], [[0, 0], [cap / 2 - 4, 0], [cap / 2, 6], [cap / 2, capl - 6], [cap / 2 - 3, capl], [0, capl]],
            "cap", axis="x")


def zfoot(d, id, x, z0, z1, y=32, dia=TUBE, cap=64, capl=58):
    """Floor tube along z with black end caps."""
    d.cyl(id, [x, y, z0 + 20], [x, y, z1 - 20], dia, "frame")
    d.lathe(id + "-c0", [x, y, z0], [[0, 0], [cap / 2 - 3, 0], [cap / 2, 6], [cap / 2, capl - 6], [cap / 2 - 4, capl], [0, capl]],
            "cap", axis="z")
    d.lathe(id + "-c1", [x, y, z1 - capl], [[0, 0], [cap / 2 - 4, 0], [cap / 2, 6], [cap / 2, capl - 6], [cap / 2 - 3, capl], [0, capl]],
            "cap", axis="z")


def endcap(d, id, at, axis, dia=TUBE + 10, ln=50, flip=False):
    """A black cap on a tube end: `at` = the tube end, axis x/y/z; the cap extends +axis (or -axis if flip)."""
    a = list(at)
    i = "xyz".index(axis)
    if flip:
        a[i] -= ln
    d.lathe(id, a, [[0, 0], [dia / 2 - 3, 0], [dia / 2, 5], [dia / 2, ln - 5], [dia / 2 - 4, ln], [0, ln]], "cap", axis=axis)


def seat(d, id, cx, zb, zf, wb, wf, y0, layers=(24, 9, 34), r=55, outline=None):
    """Upholstered seat: blue base, light piping band, blue top (top-plane slabs). Returns the top height."""
    ol = outline or rpoly([(cx - wb / 2, zb), (cx + wb / 2, zb), (cx + wf / 2, zf), (cx - wf / 2, zf)], r)
    y = y0
    d.slab(id + "-lo", "top", ol, [y, y + layers[0]], "blue", r=9); y += layers[0]
    d.slab(id + "-pipe", "top", ol, [y - 1, y + layers[1] + 1], "pipe", r=3); y += layers[1]
    d.slab(id + "-hi", "top", ol, [y, y + layers[2]], "blue", r=14); y += layers[2]
    return y


def back(d, id, cx, y0, y1, wb, wt, zb, layers=(22, 9, 40), rt=70, rb=25, tilt=-8, outline=None):
    """Upholstered backrest standing on z = zb (its back face), the front facing +z, tilted back by `tilt` (deg about x
    at its bottom-back edge). Returns (front z, rot)."""
    ol = outline or rpoly([(cx - wb / 2, y0), (cx + wb / 2, y0), (cx + wt / 2, y1), (cx - wt / 2, y1)], 0)
    if not outline:
        # rounded top corners (rt), small bottom corners (rb)
        ol = (f"M {cx - wb / 2 + rb:.1f} {y0} L {cx + wb / 2 - rb:.1f} {y0} Q {cx + wb / 2:.1f} {y0} {cx + wb / 2:.1f} {y0 + rb} "
              f"L {cx + wt / 2:.1f} {y1 - rt:.1f} Q {cx + wt / 2:.1f} {y1} {cx + wt / 2 - rt:.1f} {y1} "
              f"L {cx - wt / 2 + rt:.1f} {y1} Q {cx - wt / 2:.1f} {y1} {cx - wt / 2:.1f} {y1 - rt:.1f} "
              f"L {cx - wb / 2:.1f} {y0 + rb} Q {cx - wb / 2:.1f} {y0} {cx - wb / 2 + rb:.1f} {y0} Z")
    R = rot("x", tilt, [cx, y0, zb])
    z = zb
    d.slab(id + "-b", "front", ol, [z, z + layers[0]], "blue", r=8, rot=R); z += layers[0]
    d.slab(id + "-pipe", "front", ol, [z - 1, z + layers[1] + 1], "pipe", r=3, rot=R); z += layers[1]
    d.slab(id + "-f", "front", ol, [z, z + layers[2]], "blue", r=14, rot=R); z += layers[2]
    return z, R


def logo(d, id, cx, y, z, h=26, R=None, mat="plastic#ffffff"):
    """Xiangyu logo on a front face: white round mark with a light-blue cross, then 翔宇医疗 in real stroke letters
    (the 医 / 疗 glyphs of t4lib) and a thin XIANGYU MEDICAL line under them; centred on cx (review 2026-10-03)."""
    import t4lib   # registers 医 / 疗 in p1lib's font (keeps lib's D methods)
    n0 = len(d.d["parts"])
    hc = h * 0.8
    tw = t4lib.text_len("翔宇医疗", hc, gap=0.12)
    w = h * 1.25 + tw
    x0 = cx - w / 2
    d.cyl(id + "-mark", [x0 + h * 0.5, y + h * 0.45, z - 0.5], [x0 + h * 0.5, y + h * 0.45, z + 0.7], h * 1.0, mat, sides=28, soft=True)
    d.decal(id + "-cross-v", [x0 + h * 0.5, y + h * 0.45, z + 0.9], [h * 0.2, h * 0.66], "front", "plastic#a6c8e8")
    d.decal(id + "-cross-h", [x0 + h * 0.5, y + h * 0.52, z + 0.9], [h * 0.66, h * 0.2], "front", "plastic#a6c8e8")
    t4lib.text(d, id + "-t", "翔宇医疗", [x0 + h * 1.25, y + h * 0.05, z + 0.6], hc, mat, stroke=max(1.4, hc * 0.12), gap=0.12)
    t4lib.text(d, id + "-en", "XIANGYU MEDICAL", [x0 + h * 1.27, y - h * 0.38, z + 0.6], hc * 0.3, mat, gap=0.3)
    if R:
        mark(n0, d, rots=[R])


def roller(d, id, a, b, dia=120, axis="x", cap=True):
    """Blue leather roller pad between a and b (along one axis) with gathered ends and a silver end cap."""
    d.cyl(id, a, b, dia, "blue", sides=28)
    if not cap:
        return
    i = "xyz".index(axis)
    for k, (p, sgn) in enumerate(((a, -1), (b, 1))):
        q = list(p); q[i] += sgn * 10
        d.cyl(f"{id}-g{k}", p, q, dia * 0.98, "blue", d2=dia * 0.72)
        q2 = list(q); q2[i] += sgn * 4
        d.cyl(f"{id}-e{k}", q, q2, dia * 0.5, "metal#c8cbcf")


def grip(d, id, a, b, dia=40):
    d.cyl(id, a, b, dia, "foam", sides=20)


def hydro(d, id, a, b, body=0.6, dia=46):
    """Hydraulic cylinder from a (body end) to b (rod end)."""
    m = lerp(a, b, body)
    d.cyl(id, a, m, dia, "cyl")
    d.cyl(id + "-rod", m, b, 16, "chrome")
    d.sphere(id + "-eye0", a, dia * 0.55, "cyl")
    d.sphere(id + "-eye1", b, 26, "cyl")


def crop_screen(d, id, mat_screen, print_, rect, z, crop_px, ui_px, frame_mat, frame_extra=40, r=1, outer=None, rot_=None):
    """Screen whose picture is a crop with margins: `rect` [x0, y0, x1, y1] = where the crop's UI area (ui_px
    [u0, v0, u1, v1] in crop pixels, v from the top) must land; crop_px = (w, h). The whole crop is laid on a
    screen box sized so the UI matches `rect`, and a frame of `frame_mat` (with a hole = rect) masks the margins,
    2 mm in front of the picture. z = the face plane (the screen box goes z-2..z)."""
    W, H = crop_px
    u0, v0, u1, v1 = ui_px
    x0, y0, x1, y1 = rect
    sx = (x1 - x0) / (u1 - u0); sy = (y1 - y0) / (v1 - v0)
    cx0 = x0 - u0 * sx; cx1 = cx0 + W * sx
    cy1 = y1 + v0 * sy; cy0 = cy1 - H * sy
    d.screen(id, [cx0, cy0, z - 2, cx1, cy1, z], mat_screen, print=print_, bezel=0.2, r=r, rot=rot_)
    e = frame_extra
    if outer:
        ox0, oy0, ox1, oy1 = outer
        outer = f"M {ox0:.1f} {oy0:.1f} H {ox1:.1f} V {oy1:.1f} H {ox0:.1f} Z"
    else:
        outer = f"M {min(cx0, x0) - e:.1f} {min(cy0, y0) - e:.1f} H {max(cx1, x1) + e:.1f} V {max(cy1, y1) + e:.1f} H {min(cx0, x0) - e:.1f} Z"
    inner = f"M {x0:.1f} {y0:.1f} V {y1:.1f} H {x1:.1f} V {y0:.1f} Z"
    d.slab(id + "-mask", "front", outer + " " + inner, [z + 2.2, z + 3.5], frame_mat, r=0.5, rot=rot_)
