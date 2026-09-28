"""SKINNY ART painted ornaments (decals) of the DveriMebel / el'PORTA / BRAVO 2020 catalogue, pp. 109-111 (Whitey
enamel): silver-grey scroll prints on the enamel panel fields and darker grey-brown prints on the satin glass of
Скинни-12 / -13 / -14 / -15.1 / -20 / -21 ART.

Drawn from the photos p109_skinni-12-art__whitey.jpg (the big one, ~0.39 px/mm), p110_skinni-13-art / -14-art /
-15-1-art / -20-art__whitey.jpg and p111_skinni-21-art__whitey.jpg (~0.16 px/mm), compared with the plain versions
(p109_skinni-12__whitey.jpg ...) to tell the ornament from the panel mouldings. The photos only give the layout, the
density and the darkness; the motifs are drawn as a decorator's scroll print that reads the same at that scale:

  * vine border (12 top / bottom, 13 glass / bottom): a wavy stem round the field twisted with a thin twin line,
    leaf pairs and spiral tendrils along it, a leaf and small volutes in the corners, a small palmette under the
    middle of the top and the bottom runs;
  * baroque frame (14 top, 15.1 glass): a crest of C-scrolls with a hanging palmette at the top, thin double side
    lines with a knot at mid height, a fleur-de-lis crest with S-scrolls at the bottom; 14 / 15.1 bottom: the crest;
    14 / 15.1 middle: a small rinceau band;
  * cartouche frame (20 top, 21 glass): moustache C-scroll crest with a heart of volutes, corner loops braided down
    the sides into thin side lines, a small fleur with a base line at the bottom; 20 / 21 oval: a horizontal scroll
    ornament; 20 / 21 bottom: curved diagonal swoosh stripes and a fleur under the arch.

Shared parts (the photos show the same print) are drawn by one function and registered for both ids.
"""
import math

import numpy as np

from art_wave3 import art, spline

# leaf bounds in the photos' pixels (measured on the panel mouldings; find_leaf starts the leaf inside the cornice)
SMALL_LEAF = (20.97, 23.35, 149.5, 339.95)     # p110 / p111 small photos
BIG_LEAF = (53.7, 54.1, 362.8, 818.7)           # p109 Скинни-12 ART

ENAMEL = "#e2e2e2"             # enamel-whitey (enamel.py) = the photos' field grey: what the enamel decals lie on
SILVER = dict(color="#a2a3a6", alpha=0.62, smooth=0.50, metallic=0.40)      # print on the enamel
GLASSP = dict(color="#8b8782", alpha=0.95, smooth=0.45, metallic=0.10)      # print on the satin glass


def paint(base, alpha):
    """A print's paint with its own opacity (matched to the darkness of its photo)."""
    return dict(base, alpha=alpha)


SILVER_14 = paint(SILVER, 0.55)       # Скинни-14 / -15.1 ART enamel parts: a lighter print on the photos
SILVER_13 = paint(SILVER, 0.45)       # Скинни-13 ART bottom panel: fainter than the same print on Скинни-12 ART
GLASS_15 = paint(GLASSP, 0.65)        # Скинни-15.1 ART glass: lighter than -13 / -21


# ------------------------------------------------------------------------------------------------ motif helpers
def _u(v):
    v = np.asarray(v, np.float64)
    return v / max(float(np.hypot(*v)), 1e-9)


def volute(p, d, r, turns=1.0, side=1, shrink=0.3, step=0.5):
    """Spiral leaving point p in direction d and curling to the left (side 1) or right (side -1): starting radius r,
    ending radius r * shrink after `turns` turns."""
    p = np.asarray(p, np.float64)
    d = _u(d)
    n = np.array([-d[1], d[0]])
    c = p + side * n * r
    a0 = math.atan2(p[1] - c[1], p[0] - c[0])
    sweep = side * turns * 2 * math.pi
    m = max(12, int(abs(sweep) * r / step))
    t = np.linspace(0, 1, m)
    rr = r * (1 - (1 - shrink) * t ** 0.9)
    ang = a0 + sweep * t
    return np.stack([c[0] + rr * np.cos(ang), c[1] + rr * np.sin(ang)], 1)


def scroll_pts(pts, end=None, start=None):
    """A smooth line through pts, ending (and / or starting) in a volute: end / start = (r, turns, side[, shrink])."""
    P = spline(pts, step=0.5)
    if end:
        r, turns, side = end[:3]
        V = volute(P[-1], P[-1] - P[-4], r, turns, side, *(end[3:4] or [0.3]))
        P = np.vstack([P, V[1:]])
    if start:
        r, turns, side = start[:3]
        V = volute(P[0], P[0] - P[3], r, turns, side, *(start[3:4] or [0.3]))
        P = np.vstack([V[::-1][:-1], P])
    return P


def scroll(L, pts, w, end=None, start=None, taper=(6, 6)):
    """A scroll stroke (w scalar or a width profile along it) ending / starting in a volute."""
    P = scroll_pts(pts, end, start)
    L.stroke(P, w, taper=taper)
    return P


def frond(L, pts, w, leaf_len, leaf_w, n, side=0, angle=40, taper=(3, 8), shrink=0.45):
    """An acanthus-like frond: a curved spine with n leaves along it (side 1 / -1 = left / right of the spine,
    0 = alternating), smaller towards the tip."""
    P = spline(pts, step=0.5)
    L.stroke(P, w, taper=taper)
    s = np.concatenate([[0], np.cumsum(np.hypot(*(P[1:] - P[:-1]).T))])
    for k in range(n):
        f = (k + 0.7) / (n + 0.4)
        i = int(np.searchsorted(s, f * s[-1]))
        i = min(max(i, 1), len(P) - 2)
        d = _u(P[i + 1] - P[i - 1])
        sd = side or (1 if k % 2 == 0 else -1)
        a = math.radians(angle) * sd
        dd = np.array([d[0] * math.cos(a) - d[1] * math.sin(a), d[0] * math.sin(a) + d[1] * math.cos(a)])
        g = 1 - (1 - shrink) * f
        L.leaf(P[i], P[i] + dd * leaf_len * g, leaf_w * g, 0.18 * sd, 0.4)
    return P


def sine_path(p0, p1, amp, halfwaves, phase=0.0, step=1.0):
    """Points from p0 to p1 displaced sideways by amp * sin(pi * halfwaves * t + phase)."""
    p0, p1 = np.asarray(p0, np.float64), np.asarray(p1, np.float64)
    d = p1 - p0
    L = float(np.hypot(*d))
    n = np.array([-d[1], d[0]]) / L
    t = np.linspace(0, 1, max(8, int(L / step)))
    off = amp * np.sin(math.pi * halfwaves * t + phase)
    return p0 + np.outer(t, d) + np.outer(off, n), t


def along(P):
    """Arc length, unit tangents and left normals of a polyline."""
    s = np.concatenate([[0], np.cumsum(np.hypot(*(P[1:] - P[:-1]).T))])
    T = np.gradient(P, axis=0)
    T /= np.maximum(np.hypot(*T.T), 1e-9)[:, None]
    return s, T, np.stack([-T[:, 1], T[:, 0]], 1)


def at_s(P, s, S):
    """Point, tangent angle (deg) at arc length S."""
    i = int(np.clip(np.searchsorted(s, S), 1, len(P) - 2))
    d = P[i + 1] - P[i - 1]
    return P[i], math.degrees(math.atan2(d[1], d[0]))


def tendril(L, w, r=5.0, reach=(13, 8), side=1, turns=1.3):
    """(local frame: stem along +x at the origin, +y = the side it grows to) a tendril leaving the stem and ending
    in a spiral curling back."""
    rx, ry = reach
    scroll(L, [[0, 0], [rx * 0.45, ry * 0.55 * side], [rx, ry * side]], (w, w * 0.8, w * 0.55, w * 0.35),
           end=(r, turns, side, 0.22), taper=(0, 4))


def leaf_pair(L, size=1.0, berry=True):
    """(local frame) a leaf forward-in, a leaf backward-in and a berry."""
    L.leaf([0.5, 0.3], [14 * size, 9 * size], 5.6 * size, 0.18, 0.38)
    L.leaf([-0.5, 0.3], [-12 * size, 8 * size], 5.0 * size, -0.18, 0.38)
    if berry:
        L.dot(1.0 * size, 7.5 * size, 1.7 * size)


# ------------------------------------------------------------------------------------------------ vine border
def vine_border(a, box, paint, w=2.4, inset=17.0, amp=7.0, period=190.0):
    """Скинни-12 / -13 ART: a twisted wavy stem round the field (the box) - one smooth line with a thin twin
    crossing it - leaf pairs and spiral tendrils along its inner side, a leaf and volutes in the corners, a small
    palmette under the middle of the top and the bottom runs."""
    L = a.layer(**paint)
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    xs = x0 + inset                          # side stem's mean line
    yt = y1 - inset                          # top run at the corners
    rc = 16.0                                # corner radius
    xc = xs + rc
    half = cx - xc
    xd = xc + 0.5 * half                     # the dip of the top run
    dip = min(22.0, 0.045 * half + 12)
    # quarter path: top centre -> dip -> corner -> down the side to the middle (a crest there: vertical tangent)
    top = [[cx, yt - 3], [cx - 0.15 * half, yt - 5], [xd + 0.25 * half, yt - dip + 5], [xd, yt - dip],
           [xd - 0.25 * half, yt - dip + 6], [xc + 0.12 * half, yt - 1.5], [xc, yt]]
    corner = [[xs + rc * (1 - math.sin(t)), yt - rc * (1 - math.cos(t))] for t in np.linspace(0.3, 1.27, 4)]
    ys0 = yt - rc
    run = ys0 - cy
    nh = max(0, int(round(run / (period / 2) - 0.5))) + 0.5
    side, _ = sine_path([xs, ys0 - 8], [xs, cy], amp, nh, step=8)
    ramp = np.clip((ys0 - 8 - side[:, 1]) / 60, 0, 1)          # ease the wave in below the corner
    side[:, 0] = xs + (side[:, 0] - xs) * ramp
    Q = spline(np.vstack([top, corner, [[xs, ys0 - 2]], side[1:]]), step=0.6)
    s, T, N = along(Q)
    S = s[-1]
    with a.mirror_x(cx), a.mirror_y(cy):
        L.stroke(Q, w)
        # the twin: crosses the stem at the top middle and the side middle, ~55 mm half waves
        k = max(2, int(round(S / 55)))
        off = 0.62 * amp * np.sin(math.pi * k * s / S)
        L.stroke(Q + N * off[:, None], w * 0.45)
        # motifs at the twin's crests (inside = left of the path), skipping the middle palmette and the corner
        sc = s[int(np.argmin(np.hypot(*(Q - [xs + rc * 0.3, yt - rc * 0.3]).T)))]     # corner arc length
        n = 0
        for j in range(k):
            Sj = (j + 0.5) / k * S
            if Sj < 38 or abs(Sj - sc) < 30:
                continue
            p, ang = at_s(Q, s, Sj)
            inside = off[int(np.searchsorted(s, Sj))] > 0
            with a.at(p[0], p[1], ang):
                if inside:
                    if n % 2 == 0:
                        leaf_pair(L)
                    else:
                        tendril(L, w * 0.8, 5.0, (13, 9), 1)
                        L.leaf([-1, 0.5], [-11, 7], 4.6, -0.18, 0.38)
                    n += 1
                else:
                    L.leaf([0, -0.5], [9, -7], 4.2, -0.15, 0.38)          # a small leaf outwards
        # corner: a leaf pointing into the corner and two volutes under it
        pc = np.array([xs + rc * 0.3, yt - rc * 0.3])
        with a.at(pc[0], pc[1], 135):
            L.leaf([0, 0], [15, 0], 6.0, 0.0, 0.35)
        for sg in (1, -1):
            with a.at(pc[0] + 1, pc[1] - 1, -45 + sg * 55):
                tendril(L, w * 0.7, 3.8, (10, 5), -sg, 1.2)
        # middle palmette under the top run's centre
        with a.at(cx, yt - 3, 0):
            L.leaf([0, -2], [0, -24], 7.0, 0.0, 0.3)
            L.dot(0, -28, 1.8)
            for sg in (1, -1):
                scroll(L, [[0, -3], [sg * 8, -7], [sg * 14, -15]], (w * 0.9, w * 0.7, w * 0.45),
                       end=(4.5, 1.2, 1 if sg > 0 else -1, 0.25), taper=(0, 3))
                L.leaf([sg * 2, -1], [sg * 16, 1], 4.5, sg * 0.2, 0.38)


@art("doorart_skinny_12_art_top", "decal", "Скинни-12 ART, верх (рамка-лоза)", (183.5, 795, 616.5, 1856),
     photos=[("p109_skinni-12-art__whitey.jpg", BIG_LEAF)], shape=("skinny-12-art", "doorart_skinny_12_art_top"), under=ENAMEL)
def skinny_12_top(a):
    vine_border(a, a.box, SILVER)


def vine_small(a, paint):
    vine_border(a, a.box, paint, period=170.0)


@art("doorart_skinny_12_art_bottom", "decal", "Скинни-12 ART, низ (рамка-лоза)", (183.5, 177, 616.5, 560),
     photos=[("p109_skinni-12-art__whitey.jpg", BIG_LEAF)], shape=("skinny-12-art", "doorart_skinny_12_art_bottom"), under=ENAMEL)
def skinny_12_bottom(a):
    vine_small(a, SILVER)


@art("doorart_skinny_13_art_glass", "decal", "Скинни-13 ART, стекло (рамка-лоза)", (147.5, 759, 652.5, 1892),
     photos=[("p110_skinni-13-art__whitey.jpg", SMALL_LEAF)], shape=("skinny-13-art", "doorart_skinny_13_art_glass"))
def skinny_13_glass(a):
    vine_border(a, a.box, GLASSP, w=2.8)


@art("doorart_skinny_13_art_bottom", "decal", "Скинни-13 ART, низ (рамка-лоза)", (183.5, 177, 616.5, 560),
     photos=[("p110_skinni-13-art__whitey.jpg", SMALL_LEAF), ("p109_skinni-12-art__whitey.jpg", BIG_LEAF)],
     shape=("skinny-13-art", "doorart_skinny_13_art_bottom"), under=ENAMEL)
def skinny_13_bottom(a):
    vine_small(a, SILVER_13)


# ------------------------------------------------------------------------------------------------ baroque frame
def crest_top(a, L, cx, yt, s=1.0, sy=1.0, w=2.6, hs=185.0):
    """The C-scroll crest hanging from the top (Скинни-14 / -15.1 ART): local origin at the top middle, the right
    half drawn and mirrored; hs = half the span (to the side lines), s / sy = scale."""
    with a.mirror_x(cx), a.at(cx, yt, 0, sx=s, sy=s * sy):
        # main arm: from the palmette's top out and up over a low arch, down into the corner volute
        scroll(L, [[1, -22], [22, -8], [60, 0], [100, -2], [136, -12], [162, -28], [hs - 10, -50]],
               (w * 0.9, w * 2.0, w * 2.6, w * 2.4, w * 2.0, w * 1.3, w * 0.8), end=(18, 1.2, -1, 0.22),
               taper=(4, 8))
        # a C-scroll hanging inside the arch, curling out
        scroll(L, [[104, -3], [102, -18], [94, -32], [82, -40]], (w * 1.4, w * 1.6, w * 1.0, w * 0.6),
               end=(10, 1.15, 1, 0.22), taper=(2, 5))
        L.leaf([100, -12], [126, -34], 8, 0.25, 0.4)
        # a sprig on the arch curling back to the middle, leaves over the arch
        scroll(L, [[62, 1], [52, 11], [38, 14]], (w * 1.1, w * 0.7, w * 0.5), end=(6.5, 1.15, 1, 0.22), taper=(0, 3))
        L.leaf([78, 1], [104, 14], 9, 0.25, 0.4)
        L.leaf([128, -9], [150, 6], 8, -0.1, 0.4)
        # the lyre: an inner scroll from under the palmette's top out and down, curling in
        scroll(L, [[4, -22], [26, -26], [42, -38], [46, -54]], (w * 0.8, w * 1.8, w * 1.5, w * 0.9),
               end=(10, 1.2, -1, 0.22), taper=(3, 5))
        L.leaf([44, -30], [66, -48], 8, -0.2, 0.4)
        # palmette hanging in the middle: a long middle leaf, side leaves curving out, a cross of beads, a ball
        L.leaf([0, -14], [0, -112], 16, 0.0, 0.3)
        L.leaf([2, -26], [24, -86], 11, 0.3, 0.45)
        L.leaf([1, -84], [0, -100], 6, 0.0, 0.5)
        L.diamond(9, -104, 6, 5)
        L.dot(0, -122, 3.8)
        L.leaf([0, -12], [0, 14], 11, 0.0, 0.5)                      # a bud on top
        # corner: leaves over the volute
        L.leaf([hs - 12, -38], [hs + 10, -8], 9, 0.2, 0.4)
        L.leaf([hs - 22, -30], [hs - 34, -2], 7.5, -0.2, 0.4)


def crest_bottom(a, L, cx, yb, s=1.0, w=2.6, hs=185.0):
    """The fleur-de-lis crest standing on the bottom (Скинни-14 / -15.1 ART): origin at the bottom middle."""
    with a.mirror_x(cx), a.at(cx, yb, 0, s=s):
        # fleur-de-lis: middle petal, side petals curling out and down, a band, a tail with a ball
        L.leaf([0, 86], [0, 194], 22, 0.0, 0.35)
        L.diamond(0, 200, 7, 9)
        scroll(L, [[3, 96], [12, 124], [28, 148], [48, 154]], (w * 2.4, w * 2.2, w * 1.3, w * 0.7),
               end=(10, 1.15, -1, 0.22), taper=(2, 5))
        L.rect(-19, 80, 19, 90)
        L.leaf([0, 82], [0, 38], 12, 0.0, 0.35)
        L.dot(0, 31, 3.2)
        # big S-scroll from under the band up and out, down into a big volute at the bottom corner
        scroll(L, [[8, 84], [36, 96], [70, 104], [110, 100], [140, 82], [156, 56]],
               (w * 0.9, w * 2.0, w * 2.6, w * 2.4, w * 1.6, w * 0.9), end=(19, 1.2, -1, 0.2), taper=(4, 8))
        # a C-scroll riding on it, curling down
        scroll(L, [[72, 104], [84, 122], [104, 132], [120, 128]], (w * 1.3, w * 1.5, w * 1.0, w * 0.6),
               end=(9, 1.15, -1, 0.22), taper=(2, 5))
        # a smaller scroll under it curling up
        scroll(L, [[12, 70], [44, 56], [78, 46], [102, 34]], (w * 0.8, w * 1.8, w * 1.4, w * 0.8),
               end=(12, 1.15, 1, 0.22), taper=(3, 5))
        # leaves
        L.leaf([118, 96], [140, 114], 9, 0.2, 0.4)
        L.leaf([50, 104], [58, 126], 8, -0.2, 0.4)
        L.leaf([56, 50], [62, 26], 8, 0.2, 0.4)
        L.leaf([30, 58], [24, 34], 7, -0.2, 0.4)
        L.leaf([134, 48], [124, 28], 7, 0.2, 0.4)
        # corner: the side line's end turning in and curling, leaves out
        scroll(L, [[hs, 170], [hs, 124], [hs - 3, 102], [hs - 12, 88]], (w * 1.0, w * 1.5, w * 1.2, w * 0.6),
               end=(12, 1.15, -1, 0.22), taper=(0, 5))
        L.leaf([hs - 1, 116], [hs + 16, 94], 8, -0.2, 0.4)
        L.leaf([hs - 1, 136], [hs + 14, 156], 7, 0.2, 0.4)


def side_knot(a, L, x, y, s=1.0, w=2.4):
    """A small knot on a side line: a bead, two C-scrolls back to back on each side, bars."""
    with a.mirror_y(y), a.mirror_x(x), a.at(x, y, 0, s=s):
        L.diamond(0, 0, 10, 18)
        scroll(L, [[1.5, 12], [8, 18], [16, 17]], (w * 1.3, w * 0.8), end=(6.5, 1.15, -1, 0.22), taper=(0, 3))
        L.leaf([0.5, 24], [10, 42], 7, 0.2, 0.4)
        L.rect(-7, 26, 7, 29.5)


def baroque_frame(a, paint, cx, xl, yt, yb, yk, w=2.6, sy=1.0, double=True, line=0.85):
    """Скинни-14 top / -15.1 glass: crest at the top, thin side lines with a knot, fleur crest at the bottom."""
    L = a.layer(**paint)
    hs = cx - xl
    s = hs / 185.0
    crest_top(a, L, cx, yt, s, sy, w)
    crest_bottom(a, L, cx, yb, s, w)
    y_top = yt - (50 + 18 + 12) * s * sy           # under the corner volute
    y_bot = yb + 170 * s
    with a.mirror_x(cx):
        for y0, y1 in ((yk + 40 * s, y_top), (y_bot, yk - 40 * s)):
            L.stroke([[xl, y0], [xl, y1]], w * line, taper=(3, 3))
            if double:
                L.stroke([[xl + 5.5 * s, y0 + 8], [xl + 5.5 * s, y1 - 8]], w * 0.35, taper=(6, 6))
        side_knot(a, L, xl, yk, s, w)


@art("doorart_skinny_15_1_art_glass", "decal", "Скинни-15.1 ART, стекло (барочная рамка)", (147.5, 944, 652.5, 1892),
     photos=[("p110_skinni-15-1-art__whitey.jpg", SMALL_LEAF)], shape=("skinny-15-1-art", "doorart_skinny_15_1_art_glass"))
def skinny_15_1_glass(a):
    baroque_frame(a, GLASS_15, 400.0, 214.0, 1822.0, 975.0, 1450.0)


@art("doorart_skinny_14_art_top", "decal", "Скинни-14 ART, верх (барочная рамка)", (183.5, 980, 616.5, 1856),
     photos=[("p110_skinni-14-art__whitey.jpg", SMALL_LEAF)], shape=("skinny-14-art", "doorart_skinny_14_art_top"), under=ENAMEL)
def skinny_14_top(a):
    baroque_frame(a, SILVER_14, 400.0, 208.0, 1838.0, 996.0, 1448.0, line=0.55)


def rinceau(a, L, cx, cy, half, amp=11.0, n=4, w=1.8):
    """A small horizontal rinceau band (Скинни-14 / -15.1 ART middle panel): from a middle palmette a wavy stem
    runs to each side, a spiral curls inside every hump, a leaf grows out of every crest, a volute ends it."""
    with a.mirror_x(cx), a.at(cx, cy):
        x0 = 9.0
        stem, _ = sine_path([x0, 0], [half, 0], amp, n, step=1.0)
        stem[:, 1] *= -1                                         # the first hump goes up
        stem = np.vstack([[[3, -3]], stem])
        scroll(L, stem[::3], (w * 1.2, w * 1.0, w * 0.8, w * 0.5), end=(5.0, 1.15, 1 if n % 2 == 0 else -1, 0.25),
               taper=(0, 5))
        step = (half - x0) / n
        for k in range(n):
            xk = x0 + (k + 0.5) * step
            sg = 1 if k % 2 == 0 else -1                        # the hump's side: +1 up, -1 down
            # a spiral inside the hump: from just past the crest down into it, curling back
            scroll(L, [[xk - 1, sg * amp], [xk + 5, sg * (amp - 2.5)], [xk + 8, sg * (amp - 8)]],
                   (w * 0.9, w * 0.65, w * 0.45), end=(4.4, 1.15, -sg, 0.25), taper=(0, 2))
            # a leaf out of the crest, backwards and outwards
            L.leaf([xk - 1, sg * (amp + 0.5)], [xk - 15, sg * (amp + 8)], 5.5, -0.2 * sg, 0.4)
        # middle palmette: a bud up, a drop down, two small volutes
        L.leaf([0, 1], [0, 20], 8, 0.0, 0.4)
        L.leaf([0, -1], [0, -15], 6.5, 0.0, 0.4)
        scroll(L, [[1, 3], [5, 9], [11, 11]], (w * 0.9, w * 0.6), end=(3.6, 1.1, -1, 0.25), taper=(0, 2))


@art("doorart_skinny_14_art_middle", "decal", "Скинни-14 ART, средняя филёнка (завиток)",
     (183.5, 717.5, 616.5, 767.5), photos=[("p110_skinni-14-art__whitey.jpg", SMALL_LEAF)],
     shape=("skinny-14-art", "doorart_skinny_14_art_middle"), under=ENAMEL)
def skinny_14_middle(a):
    rinceau(a, a.layer(**SILVER_14), 400.0, 742.5, 172.0)


@art("doorart_skinny_15_1_art_middle", "decal", "Скинни-15.1 ART, средняя филёнка (завиток)",
     (183.5, 717.5, 616.5, 767.5), photos=[("p110_skinni-15-1-art__whitey.jpg", SMALL_LEAF)],
     shape=("skinny-15-1-art", "doorart_skinny_15_1_art_middle"), under=ENAMEL)
def skinny_15_1_middle(a):
    rinceau(a, a.layer(**SILVER_14), 400.0, 742.5, 172.0)


def crest_panel(a, paint):
    """Скинни-14 / -15.1 ART bottom panel: the top crest along the top of the field, a leafy drop hanging from
    each corner volute."""
    L = a.layer(**paint)
    crest_top(a, L, 400.0, 481.0, 1.0, 1.0)
    with a.mirror_x(400.0), a.at(400.0 + 185.0, 481.0):
        frond(L, [[-4, -72], [-2, -86], [0, -104], [-4, -118]], 2.2, 13, 6, 3, side=0, angle=40)
        L.leaf([-4, -116], [-4, -134], 7, 0.0, 0.4)


@art("doorart_skinny_14_art_bottom", "decal", "Скинни-14 ART, низ (барочный гребень)", (183.5, 177, 616.5, 506),
     photos=[("p110_skinni-14-art__whitey.jpg", SMALL_LEAF)], shape=("skinny-14-art", "doorart_skinny_14_art_bottom"), under=ENAMEL)
def skinny_14_bottom(a):
    crest_panel(a, SILVER_14)


@art("doorart_skinny_15_1_art_bottom", "decal", "Скинни-15.1 ART, низ (барочный гребень)", (183.5, 177, 616.5, 506),
     photos=[("p110_skinni-15-1-art__whitey.jpg", SMALL_LEAF)], shape=("skinny-15-1-art", "doorart_skinny_15_1_art_bottom"),
     under=ENAMEL)
def skinny_15_1_bottom(a):
    crest_panel(a, SILVER_14)


# ------------------------------------------------------------------------------------------------ cartouche frame
def cartouche_frame(a, paint, cx, xl, yt, yb, w=2.6):
    """Скинни-20 top / -21 glass: a moustache C-scroll crest with a heart of volutes and a drop in the middle, its
    arms turning down into loops at the corners, a braid under each loop into a thin side line, a small fleur on a
    base line at the bottom and the side lines curling in at the bottom corners. yt = the crest's top, yb = the
    base line."""
    L = a.layer(**paint)
    hs = cx - xl
    with a.mirror_x(cx):
        with a.at(cx, yt):
            # the arm: centre -> low arch -> corner, down into the loop
            scroll(L, [[1, -26], [16, -10], [50, 0], [95, -2], [135, -10], [hs - 32, -18], [hs - 8, -30],
                        [hs + 5, -52], [hs + 8, -78], [hs + 3, -100], [hs - 7, -112]],
                   (w * 0.9, w * 2.0, w * 2.4, w * 2.1, w * 1.6, w * 1.2, w * 1.5, w * 1.6, w * 1.1, w * 0.7),
                   end=(10, 1.15, -1, 0.22), taper=(4, 8))
            # the heart and the drop
            scroll(L, [[2, -24], [22, -26], [40, -38], [46, -58], [40, -72]],
                   (w * 0.9, w * 2.2, w * 2.0, w * 1.4, w * 0.8), end=(12, 1.15, -1, 0.22), taper=(3, 5))
            L.leaf([30, -30], [52, -24], 7, 0.2, 0.4)
            L.leaf([0, -28], [0, -88], 13, 0.0, 0.3)
            L.dot(0, -95, 3.5)
            L.leaf([0, -24], [0, 6], 9, 0.0, 0.45)
            L.leaf([1, -20], [15, -3], 6, 0.2, 0.4)
            # sprigs on the arms
            L.leaf([48, 0.5], [72, 13], 8, 0.25, 0.4)
            scroll(L, [[100, -1], [92, 9], [80, 12]], (w * 1.0, w * 0.6), end=(5.5, 1.15, 1, 0.22), taper=(0, 3))
            L.leaf([136, -9], [152, 6], 7, -0.15, 0.4)
            L.leaf([hs - 20, -18], [hs - 6, -2], 7, -0.2, 0.4)
            # inside the loop: a small leaf
            L.leaf([hs - 3, -96], [hs - 8, -70], 6, 0.2, 0.4)
            # braid under the loop into the side line
            yb0, yb1 = -122, -236
            L.dot(hs - 1, yb0 + 2, 2.6)                                  # a bead under the loop
            for sg in (1, -1):
                pts = [[hs - 1, yb0], [hs + 7 * sg, yb0 - 18], [hs - 6 * sg, yb0 - 48], [hs + 5 * sg, yb0 - 80],
                       [hs, yb1]]
                L.stroke(spline(pts), (w * 0.7, w * 1.2, w * 1.2, w * 0.9), taper=(0, 0))
            for yy in (yb0 - 33, yb0 - 64):
                L.leaf([hs + 1, yy], [hs - 14, yy - 10], 5.5, 0.2, 0.4)
        # side line down to the bottom corner
        L.stroke([[xl, yt - 236], [xl, yb + 70]], w * 0.8)
        with a.at(cx, yb):
            # base line with a volute at its end
            scroll(L, [[0, 0], [60, -1], [120, 1], [hs - 40, 2]], (w * 1.0, w * 0.9, w * 0.7),
                   end=(6, 1.15, 1, 0.25), taper=(0, 4))
            # the fleur: a bud and a crown of two C-scrolls curling down
            L.leaf([0, 3], [0, 70], 16, 0.0, 0.35)
            L.dot(0, 78, 3.2)
            scroll(L, [[2, 8], [16, 26], [36, 38], [54, 32], [58, 18]], (w * 1.0, w * 2.0, w * 1.8, w * 1.1, w * 0.7),
                   end=(10, 1.15, -1, 0.22), taper=(2, 5))
            L.leaf([6, 2], [34, 6], 8, 0.2, 0.4)
            L.leaf([70, 1], [92, 12], 7, 0.2, 0.4)
            L.leaf([66, 30], [84, 44], 6, 0.2, 0.4)
            # the side line's end: an S bending in under the base line, a volute curling out
            scroll(L, [[hs, 72], [hs, 36], [hs - 6, 14], [hs - 12, -6], [hs - 8, -26]],
                   (w * 0.8, w * 1.3, w * 1.5, w * 1.0, w * 0.6), end=(8, 1.15, 1, 0.22), taper=(0, 4))
            L.leaf([hs, 44], [hs + 15, 30], 6.5, -0.2, 0.4)
            L.leaf([hs - 8, 10], [hs - 26, 20], 6, 0.2, 0.4)


@art("doorart_skinny_21_art_glass", "decal", "Скинни-21 ART, стекло (картуш)", (139.5, 988.5, 660.5, 1883),
     photos=[("p111_skinni-21-art__whitey.jpg", SMALL_LEAF)], shape=("skinny-21-art", "doorart_skinny_21_art_glass"))
def skinny_21_glass(a):
    cartouche_frame(a, GLASSP, 400.0, 205.0, 1826.0, 1108.0)


@art("doorart_skinny_20_art_top", "decal", "Скинни-20 ART, верх (картуш)", (175.5, 1043, 624.5, 1847),
     photos=[("p110_skinni-20-art__whitey.jpg", SMALL_LEAF)], shape=("skinny-20-art", "doorart_skinny_20_art_top"), under=ENAMEL)
def skinny_20_top(a):
    cartouche_frame(a, SILVER, 400.0, 198.0, 1824.0, 1114.0)


# ------------------------------------------------------------------------------------------------ oval and bottom
def oval_scroll(a, paint, cx=400.0, cy=752.0, w=2.2):
    """Скинни-20 / -21 ART oval: a horizontal scroll ornament - a lily and a drop in the middle, a C-scroll and a
    long S-scroll to each side, leaves."""
    L = a.layer(**paint)
    with a.mirror_x(cx), a.at(cx, cy, sx=0.88, sy=1.0):
        L.leaf([0, 4], [0, 36], 10, 0.0, 0.4)
        L.leaf([0, -4], [0, -26], 8, 0.0, 0.4)
        L.dot(0, -32, 2.6)
        L.dot(0, 41, 2.2)
        scroll(L, [[3, 3], [18, 14], [38, 21], [56, 16]], (w * 0.8, w * 1.6, w * 1.3, w * 0.7),
               end=(8, 1.15, -1, 0.22), taper=(3, 5))
        scroll(L, [[6, -3], [40, -10], [80, -7], [110, 3], [124, 15]], (w * 0.8, w * 1.8, w * 1.6, w * 1.0, w * 0.6),
               end=(9, 1.15, 1, 0.22), taper=(3, 5))
        L.leaf([70, -7], [90, -21], 7, -0.2, 0.4)
        L.leaf([100, -1], [124, -10], 7, -0.2, 0.4)
        L.leaf([62, 17], [82, 30], 7, 0.2, 0.4)
        L.leaf([118, 10], [146, 4], 7, -0.1, 0.4)
        scroll(L, [[132, 8], [140, 20], [152, 22]], (w * 0.8, w * 0.5), end=(4.5, 1.1, -1, 0.25), taper=(0, 3))
        L.leaf([4, 1], [20, 3], 5, 0.2, 0.4)


@art("doorart_skinny_20_art_oval", "decal", "Скинни-20 ART, овал (завиток)", (175.5, 655, 624.5, 837),
     photos=[("p110_skinni-20-art__whitey.jpg", SMALL_LEAF)], shape=("skinny-20-art", "doorart_skinny_20_art_oval"), under=ENAMEL)
def skinny_20_oval(a):
    oval_scroll(a, SILVER)


@art("doorart_skinny_21_art_oval", "decal", "Скинни-21 ART, овал (завиток)", (175.5, 655, 624.5, 837),
     photos=[("p111_skinni-21-art__whitey.jpg", SMALL_LEAF)], shape=("skinny-21-art", "doorart_skinny_21_art_oval"), under=ENAMEL)
def skinny_21_oval(a):
    oval_scroll(a, SILVER)


def _runs(P, keep):
    out, cur = [], []
    for p, k in zip(P, keep):
        if k:
            cur.append(p)
        elif cur:
            out.append(np.array(cur))
            cur = []
    if cur:
        out.append(np.array(cur))
    return [r for r in out if len(r) > 1 and float(np.hypot(*(r[-1] - r[0]))) > 15.0]     # no stubs


def swoosh_panel(a, paint, w=2.4):
    """Скинни-20 / -21 ART bottom panel: a thin frame line inside the arched field, curved diagonal stripes (each a
    line and a thin companion) rising to the right inside it, a fleur with moustache scrolls under the arch."""
    L = a.layer(**paint)
    cx = 400.0
    xl, xr, yb = 202.0, 598.0, 200.0

    def arch(x):                           # the flat field's top (the inner panel's arched edge - its moulding)
        return 445.5 + 0.000805 * (x - 400.0) ** 2 - 32.5

    def ytop(x):
        return arch(x) - 8.0

    # frame line
    xs = np.linspace(xl, xr, 80)
    L.stroke(np.vstack([[[xl, yb]], [[x, ytop(x)] for x in xs], [[xr, yb]], [[xl, yb]]]), w * 0.6)
    # stripes
    base = np.array([[0, 0], [30, 70], [62, 135], [100, 195], [145, 250], [195, 295]], np.float64)
    fx, fy, frx, fry = cx, 382.0, 80.0, 50.0             # the fleur's clearing
    for x0 in (100.0, 210.0, 320.0, 430.0, 540.0):
        for off, ww in ((0.0, w * 1.2), (-10.0, w * 0.75)):
            P = spline(base + [x0 + off, 150.0], step=0.6)
            keep = ((P[:, 0] > xl + 1.5) & (P[:, 0] < xr - 1.5) & (P[:, 1] > yb + 1.5)
                    & (P[:, 1] < np.array([ytop(x) for x in P[:, 0]]) - 1.5)
                    & (((P[:, 0] - fx) / frx) ** 2 + ((P[:, 1] - fy) / fry) ** 2 > 1))
            for R in _runs(P, keep):
                L.stroke(R, ww)
    # the fleur under the arch
    with a.mirror_x(cx), a.at(cx, 376.0):
        L.leaf([0, 0], [0, 30], 12, 0.0, 0.4)
        L.leaf([0, -4], [0, -30], 9, 0.0, 0.35)
        L.dot(0, -36, 2.6)
        scroll(L, [[2, 4], [20, 18], [44, 26], [60, 24]], (w * 0.9, w * 1.9, w * 1.4, w * 0.8),
               end=(8, 1.15, -1, 0.22), taper=(3, 5))
        L.leaf([3, 2], [22, -10], 7, -0.2, 0.4)
        L.leaf([30, 20], [40, 2], 6, 0.2, 0.4)


@art("doorart_skinny_20_art_bottom", "decal", "Скинни-20 ART, низ (диагональные полосы)", (175.5, 186, 624.5, 452),
     photos=[("p110_skinni-20-art__whitey.jpg", SMALL_LEAF)], shape=("skinny-20-art", "doorart_skinny_20_art_bottom"), under=ENAMEL)
def skinny_20_bottom(a):
    swoosh_panel(a, SILVER)


@art("doorart_skinny_21_art_bottom", "decal", "Скинни-21 ART, низ (диагональные полосы)", (175.5, 186, 624.5, 452),
     photos=[("p111_skinni-21-art__whitey.jpg", SMALL_LEAF)], shape=("skinny-21-art", "doorart_skinny_21_art_bottom"), under=ENAMEL)
def skinny_21_bottom(a):
    swoosh_panel(a, SILVER)
