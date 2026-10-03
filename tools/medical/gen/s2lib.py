"""Helpers for the sensory-2 generators (on top of lib)."""
import math, random
from lib import *


def pts_path(pts):
    return "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in pts) + " Z"


def arc_pts(cx, cy, r, a0, a1, n=None):
    """Points on a circle from angle a0 to a1 (degrees, counter-clockwise when a1 > a0)."""
    n = n or max(4, int(abs(a1 - a0) / 6))
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cy + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def bear_outline(bx0, bx1, yt, rb, exl, exr, ey, re, y0=0):
    """Rounded rectangle body [bx0, bx1] x [y0, yt] united with two ear circles (centres exl / exr, ey, radius re)."""
    p = []
    p += arc_pts(bx0 + rb, y0 + rb, rb, 180, 270, 8)
    p += arc_pts(bx1 - rb, y0 + rb, rb, 270, 360, 8)
    # right side meets the right ear (lower intersection)
    dy = math.sqrt(max(re * re - (bx1 - exr) ** 2, 0))
    a_lo = math.degrees(math.atan2(-dy, bx1 - exr))
    dx = math.sqrt(max(re * re - (yt - ey) ** 2, 0))
    a_top_r = math.degrees(math.atan2(yt - ey, -dx))          # where the right ear meets the top edge (left side)
    p += arc_pts(exr, ey, re, a_lo, a_top_r)
    a_top_l = math.degrees(math.atan2(yt - ey, dx))            # where the left ear meets the top edge (right side)
    a_lo_l = 180 - a_lo                                        # left ear meets the left side
    p += arc_pts(exl, ey, re, a_top_l, a_lo_l)
    return pts_path(p)


def disc(d, id, x, y, z, dia, h, mat, **kw):
    """A flat disc on a front face: from z to z + h."""
    return d.cyl(id, [x, y, z], [x, y, z + h], dia, mat, **kw)


def ring(d, id, x, y, z, r0, r1, h, mat, **kw):
    """A raised ring on a front face (lathe along z)."""
    return d.lathe(id, [x, y, z], [[r0, 0], [r1, 0], [r1, h], [r0, h], [r0, 0]], mat, axis="z", **kw)


def panel(d, W, H, D, case, *, inset, ear_c, ear_r, yt, rb=40, grille=None, grille_d=57,
          bumps=None, bump_ring=50, logo=None, buttons=None, step=25, case_dark=None, grille_off=(-4, 12), logo_d=30):
    """The case of the bear-ear wall panel family.
    inset: body side inset from the outer edge (the ears stick out by it); ear_c (dx from the outer edge, y);
    bumps: (x0, y0, x1, y1) of the left bottom bump (the right one mirrored); logo: (cx, cy);
    buttons: (xs, y, dia)."""
    exl, exr, ey = ear_c[0], W - ear_c[0], ear_c[1]
    # main front shell: the outline extruded from the step to the front; a smaller back box behind it
    d.slab("case", "front", bear_outline(inset, W - inset, yt, rb, exl, exr, ey, ear_r), [step, D], case, r=14)
    d.add("case-back", "slab", case_dark or case, plane="front",
          box=[inset + 12, 12, 0, W - inset - 12, yt - 12, step + 2], radii=[rb], r=4)
    if grille:
        # dotted speaker grille: small dark dots on a 6.5 mm grid inside a circle
        gx, gy, rr = exl + grille_off[0], ey + grille_off[1], grille_d / 2
        offs = []
        n = int(rr // 6.5)
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                if (i * 6.5) ** 2 + (j * 6.5) ** 2 <= (rr - 2) ** 2 and (i, j) != (0, 0):
                    offs.append([i * 6.5, j * 6.5, 0])
        d.cyl("grille", [gx, gy, D - 1], [gx, gy, D + 0.8], 3.6, grille, soft=True, mirror="x", copies=offs)
    if bumps:
        x0, y0, x1, y1 = bumps
        d.add("bump", "slab", case, plane="front", box=[x0, y0, D - 1, x1, y1, D + 6], radii=[24], r=3, mirror="x")
        ring(d, "bump-ring", (x0 + x1) / 2, (y0 + y1) / 2, D + 6, bump_ring / 2 - 3, bump_ring / 2, 1.6,
             case_dark or case, soft=True, mirror="x")
    if logo:
        lx, ly = logo
        # green leaf mark: a yellow-green disc with a dark green leaf, then 3 green characters and a tiny line
        k_ = logo_d / 30
        disc(d, "logo-disc", lx - 45, ly + 2, D, logo_d, 1.2, "gloss#b9cf3a", soft=True)
        d.box("logo-leaf", [lx - 45 - 11 * k_, ly + 2 - 10 * k_, D + 1, lx - 45 + 11 * k_, ly + 2 + 4 * k_, D + 2.4],
              "gloss#1e8a3c", r=5 * k_, soft=True, rot=rot("z", 30, [lx - 45, ly, D]))
        # three dark-green characters drawn as strokes (glyph-like, not real letters)
        k = "gloss#1a5a30"
        d.box("logo-ch-h1", [lx - 24, ly + 12, D, lx - 6, ly + 15, D + 1.2], k, soft=True, repeat=rep(3, [23, 0, 0]))
        d.box("logo-ch-h2", [lx - 22, ly + 3, D, lx - 8, ly + 6, D + 1.2], k, soft=True, repeat=rep(3, [23, 0, 0]))
        d.box("logo-ch-h3", [lx - 25, ly - 5, D, lx - 5, ly - 2, D + 1.2], k, soft=True, repeat=rep(3, [23, 0, 0]))
        d.box("logo-ch-v", [lx - 16.5, ly - 5, D, lx - 13.5, ly + 17, D + 1.2], k, soft=True, repeat=rep(3, [23, 0, 0]))
        d.box("logo-en", [lx - 24, ly - 13, D, lx + 44, ly - 9, D + 1], "gloss#2a8a48", soft=True)
    if buttons:
        xs, by, bd = buttons
        cols = ["gloss#d4161c", "gloss#f2e010", "gloss#18a838"]
        for i, x in enumerate(xs):
            disc(d, f"btn{i}-rim", x, by, D, bd + 9, 3, "plastic#3a2a30")
            d.lathe(f"btn{i}", [x, by, D + 3], [[0, 0], [bd / 2, 0], [bd / 2, 3], [bd / 2 - 3, 6], [0, 7]],
                    cols[i], axis="z")


# ---- stroke lettering: p1lib.text() without p1lib's D-method patches (p1lib re-binds them with its own order)
_keep = {k: D.__dict__[k] for k in ("bar", "lathe", "sphere", "decal", "slab", "loft") if k in D.__dict__}
import p1lib as _p1
for _k, _v in _keep.items(): setattr(D, _k, _v)
for _k in ("screen", "caster"):
    if _k in D.__dict__ and _k not in _keep: delattr(D, _k)
text, text_len = _p1.text, _p1.text_len
