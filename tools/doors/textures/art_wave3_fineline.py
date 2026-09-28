"""Fine-line veneer doors' art glass (СТ-Худ.) and Азалия's carved ornaments of the DveriMebel / el'PORTA / BRAVO
2020 catalogue, pp. 94-101: Рондо, Этюд, Афина, Селена, Азалия, Стиль, Лилия, Лагуна and Эксклюзив Ф-17 СТ-Худ.

Drawn from the photos p095_rondo-f-01__dub-st-hud.jpg (the big one, ~0.40 px/mm: the vine is traced from it),
p095_rondo-f-22 / -27, p096_etyud-f-27-f-01, p096_afina-f-01 / -11, p096_selena-f-01 / p097_selena-f-11,
p098_azaliya-f-01 / -11 (-st-hud and the plain ones for the carved panels), p098_stil-f-01 / p099_stil-f-22,
p099_liliya-f-01 / -11, p100_laguna-f-01 / -17 and p100_eksklyuziv-f-17__shokolad-st-hud.jpg (~0.16 px/mm). The
photos with a cornice and pilasters (Афина, Селена, Азалия, Стиль, Лилия) are given with the leaf's bounds in photo
pixels (measure.find_leaf takes the pilasters for the leaf). The small photos only give the layout, the density and
the darkness; the motifs are drawn as the glass decorator's print that reads the same at that scale:

  * Рондо: a double frame line and a vine climbing in S-curves, a palmette (a fan of five fronds from a collar) on
    every bend, a curl and a Greek-key tablet beside every bulge; dark grey lines on white satin;
  * Этюд: long dark grass blades crossing in lenses and X-es, three near-black three-leaf sprigs and three small
    outlined leaves;
  * Афина: a line following the pane's outline ~26 mm inside it, a cross of lines and a four-pointed star with a
    dark jewel at the crossing;
  * Селена: a stained-glass-like lattice of light grey lines (side lines, a pinched vase in the middle, cross bars),
    scroll garlands along the top and the bottom and a lily ornament in the middle;
  * Азалия: grey outlined scroll corners (top left, bottom right) on the arch, a moustache scroll on the medallion;
    the plain leaf's carved ornaments (and the glazed leaf's lower panel one) as painted relief shading;
  * Стиль: a frame line with scroll corners and a damask medallion (fleurs, C-scrolls, a cross) in light grey; the
    narrow pane: a horizontal lattice-and-scroll band;
  * Лилия: thin grey stems with outlined lily buds along the S-crescent, two buds in the tongue, a bud in the small
    piece;
  * Лагуна / Эксклюзив Ф-17: bronze satin with a brown print: hollow twisting stems, maple / vine leaves, tendrils and
    white rhinestone sparkles.
"""
import math

import numpy as np

from art_wave3 import (art, Art, SATIN, BRONZE, NONE, spline, spiral, scroll, arclen, design_rings,  # noqa: F401
                       leaf_ring)

B_CORNICE = (20.5, 17, 150.3, 341)          # leaf bounds (px) of the 171 x 341 photos with a cornice and pilasters


def _ph(name, bounds=B_CORNICE):
    return (name, bounds)


def _u(v):
    v = np.asarray(v, np.float64)
    return v / max(float(np.hypot(*v)), 1e-9)


def _rot(v, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])


def inset(ring, d, step=1.0, smooth=3):
    """The line d mm inside a closed ring (any orientation): the ring offset along its inward normals, the loops
    that concave corners make cut away (points closer than d to the ring dropped), lightly smoothed. d: a number or
    f(points Nx2) -> distances. -> Nx2 (open: close it for a stroke)."""
    R = np.asarray(ring, np.float64)
    R = np.vstack([R, R[:1]])
    seg = np.hypot(*(R[1:] - R[:-1]).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    n = max(16, int(s[-1] / step))
    u = np.linspace(0, s[-1], n, endpoint=False)
    P = np.stack([np.interp(u, s, R[:, 0]), np.interp(u, s, R[:, 1])], 1)
    area = 0.5 * np.sum(P[:, 0] * np.roll(P[:, 1], -1) - np.roll(P[:, 0], -1) * P[:, 1])
    T = np.roll(P, -1, 0) - np.roll(P, 1, 0)
    T /= np.maximum(np.hypot(*T.T), 1e-9)[:, None]
    N = np.stack([-T[:, 1], T[:, 0]], 1) * (1 if area > 0 else -1)      # inward (left of a ccw ring)
    dd = np.asarray(d(P) if callable(d) else np.full(len(P), float(d)), np.float64)
    Q = P + N * dd[:, None]
    # distance of every offset point to the ring (segments)
    A, Bv = R[:-1], R[1:]
    AB = Bv - A
    L2 = np.maximum((AB ** 2).sum(1), 1e-12)
    keep = np.ones(len(Q), bool)
    for i0 in range(0, len(Q), 512):
        q = Q[i0:i0 + 512, None, :]
        t = np.clip(((q - A[None]) * AB[None]).sum(2) / L2[None], 0, 1)
        D = np.hypot(*(q - (A[None] + t[..., None] * AB[None])).transpose(2, 0, 1))
        keep[i0:i0 + 512] = D.min(1) > dd[i0:i0 + 512] * 0.97
    Q = Q[keep]
    for _ in range(smooth):
        Q = (np.roll(Q, 1, 0) + 2 * Q + np.roll(Q, -1, 0)) / 4
    return Q


def closed(P):
    P = np.asarray(P, np.float64)
    return np.vstack([P, P[:1]])


# ================================================================================================ Рондо
RONDO_LINE = "#4d4946"         # the vine's dark grey line
RONDO_TAB = "#c6c2be"          # the Greek-key tablets' light grey band
ERASE = dict(color=SATIN["color"], alpha=SATIN["alpha"], smooth=SATIN["smooth"])   # paints the satin back

RONDO_COLLARS = [(372, 1645), (430, 1452), (372, 1262), (430, 1072), (372, 888), (430, 700), (372, 510)]


def leaf_mid(base, tip, bend, t0=0.0, t1=1.0, n=24):
    """Points of a leaf's (Layer.leaf) bowed midrib between the fractions t0 and t1 of its length."""
    b, t = np.asarray(base, np.float64), np.asarray(tip, np.float64)
    d = t - b
    L = float(np.hypot(*d))
    nrm = np.array([-d[1], d[0]]) / max(L, 1e-9)
    u = np.linspace(t0, t1, n)
    return b + np.outer(u, d) + np.outer(np.sin(np.pi * u) * bend * L, nrm)


def rondo_palmette(D, E, L, c, up, s, FR):
    """A palmette on the Рондо vine: a collar (a short tube on the stem) at c and five slender fronds fanning from
    the stem's upward direction `up` to the side s (+1 right, -1 left), the outermost curling down. D / E / L: dark,
    satin (hides the stem under the fronds) and line layers; FR: a (satin, line) layer pair per frond, back to
    front."""
    c = np.asarray(c, np.float64)
    u = _u(up)
    n = np.array([-u[1], u[0]])
    q = [c + n * 10 + u * 5, c - n * 10 + u * 5, c - n * 8.5 - u * 4, c + n * 8.5 - u * 4]
    base = c + u * 4
    ax = math.degrees(math.atan2(u[0], u[1])) * s       # the fan axis from the vertical, towards s
    for (FE, FL), (rel, ln, wd, bend) in zip(FR, ((-36, 104, 15, -0.10), (-13, 90, 16, 0.02), (9, 84, 16, 0.08), (31, 80, 15, 0.14),
                              (54, 76, 14, 0.30))):
        ang = max(ax + rel, 2 + (rel + 36) * 0.7)
        v = _rot(np.array([0.0, 1.0]), -s * ang)
        tip = base + v * ln
        b = base + v * 1
        FE.leaf(b, tip, wd, bend=bend * s, shape=0.55)
        FL.leaf_line(b, tip, wd, 1.45, bend=bend * s, shape=0.55)
        FL.stroke(leaf_mid(b, tip, bend * s, 0.04, 0.45), 0.9, taper=(0, 14))
    FE, FL = FR[-1]
    FE.fill(q)
    FL.stroke(closed(q), 1.6)
    FL.stroke([c + n * 9.2 + u * 0.5, c - n * 9.2 + u * 0.5], 1.2)


def ribbon(D, E, P, w=3.8, inner=1.3, taper=None):
    """A sandblasted 'double line': a dark line with a satin core."""
    D.stroke(P, w, taper=taper)
    E.stroke(P, inner, taper=taper)


def rondo_key(L, T, x0, y0, x1, y1):
    """A Greek-key tablet: a light grey band round it, a dark inner frame and a bar hooking into it."""
    T.rect(x0, y0, x1, y1, w=5.0)
    m = 6.5
    ix0, iy0, ix1, iy1 = x0 + m, y0 + m, x1 - m, y1 - m
    cx = (ix0 + ix1) / 2
    L.stroke([[cx, iy1], [ix0, iy1], [ix0, iy0], [ix1, iy0], [ix1, iy1 - 9]], 1.6)
    T.stroke([[cx, iy1 - 1], [cx, iy0 + 11]], 3.6)
    L.stroke([[cx, iy1], [cx, iy0 + 11]], 1.2)


@art("doorglass_rondo_do", "fit", "Рондо СТ-Худ. (лоза с пальметтами)", (294, 380, 506, 1794),
     photos=[("p095_rondo-f-01__dub-st-hud.jpg", (26.8, 26.7, 345.2, 817)),
             ("p095_rondo-f-27__venge-st-hud.jpg", (11, 11.6, 143.5, 342))],
     shape=("rondo-do", "doorglass_rondo_do"))
def rondo_do(a):
    """White satin; a double frame line ~36 mm inside the pane; a vine (a sandblasted double line) climbing in
    S-curves from the bottom of the frame to a palmette under its top: seven palmettes (a collar on the stem at every
    crossing, alternately left and right, fronds fanning round the stem), a curl inside every bulge of the stem and a
    Greek-key tablet beside it."""
    T = a.layer(RONDO_TAB)
    D = a.layer(RONDO_LINE)
    E = a.layer(**ERASE)
    L = a.layer(RONDO_LINE)
    FR = [(a.layer(**ERASE), a.layer(RONDO_LINE)) for _ in range(5)]
    for m in (0, 7):                                   # frame: two lines
        L.rect(331 + m, 420 + m, 471 - m, 1756 - m, w=2.0)
    pts = []                                           # the stem through the collars, bulging out between them
    C = RONDO_COLLARS
    for k, (x, y) in enumerate(C):
        pts.append([x, y])
        if k + 1 < len(C):
            h = y - C[k + 1][1]
            if x < 400:
                pts += [[354, y - 0.14 * h], [347, y - 0.34 * h], [355, y - 0.55 * h], [382, y - 0.76 * h],
                        [412, y - 0.91 * h]]
            else:
                pts += [[444, y - 0.14 * h], [448, y - 0.34 * h], [440, y - 0.55 * h], [416, y - 0.76 * h],
                        [388, y - 0.91 * h]]
    stem = spline(pts)
    ribbon(D, E, stem)
    # the stem's tail below the last palmette: down the left bulge into a curl
    P = scroll(D, [[372, 510], [356, 490], [348, 465], [351, 443]], (374, 452), 13, 200, 1.25, 3.6, cw=True,
               r_end=0.3, swell=0.0)
    E.stroke(P[:, :2], 1.1, taper=(0, 10))
    for k, (x, y) in enumerate(C):
        s = 1 if x < 400 else -1
        i = int(np.argmin(np.hypot(stem[:, 0] - x, stem[:, 1] - y)))
        up = stem[max(i - 4, 0)] - stem[min(i + 4, len(stem) - 1)]
        if k == 0:
            up = np.array([0.55, 1.0])
        h = y - (C[k + 1][1] if k + 1 < len(C) else 318)
        if k + 1 == len(C):
            rondo_key(L, T, 404, 432, 432, 498)
        elif s > 0:    # bulge on the left: curl inside it, tablet right of it
            P = scroll(D, [[348, y - 0.50 * h], [352, y - 0.40 * h], [362, y - 0.33 * h]], (380, y - 0.29 * h),
                       15, 190, 1.2, 3.6, cw=True, r_end=0.3, swell=0.1)
            E.stroke(P[:, :2], 1.1, taper=(0, 10))
            rondo_key(L, T, 404, y - 0.45 * h, 432, y - 0.08 * h)
        else:
            P = scroll(D, [[448, y - 0.50 * h], [446, y - 0.40 * h], [438, y - 0.33 * h]], (420, y - 0.29 * h),
                       15, -10, 1.2, 3.6, cw=False, r_end=0.3, swell=0.1)
            E.stroke(P[:, :2], 1.1, taper=(0, 10))
            rondo_key(L, T, 350, y - 0.43 * h, 378, y - 0.06 * h)
        rondo_palmette(D, E, L, (x, y), up, s, FR)


# ================================================================================================ Этюд
ETYUD_INK = "#2c2826"          # near-black print


def sprig3(F, E, base, axis, spread=30, ln=80, wd=22):
    """Three near-black leaves from one base fanning round `axis` (deg from the vertical, + = right), a hairline
    satin midrib in each."""
    b = np.asarray(base, np.float64)
    for k, (da, lk) in enumerate(((-spread, 0.84), (0, 1.0), (spread, 0.9))):
        v = _rot(np.array([0.0, 1.0]), -(axis + da))
        tip = b + v * ln * lk
        bend = -0.06 * np.sign(da) if da else 0.0
        F.leaf(b + v * 8, tip, wd * (0.9 if da else 1.0), bend=bend, shape=0.4)
        F.stroke([b, b + v * 12], 2.4)
        E.stroke(leaf_mid(b + v * 8, tip, bend, 0.15, 0.8), 1.0, taper=(8, 12))
    F.dot(b[0], b[1], 3.2)


@art("doorglass_etyud_do", "fit", "Этюд СТ-Худ. (травы и чёрные листья)", (294, 198, 506, 1786),
     photos=[("p096_etyud-f-27-f-01__venge-dub-st-hud.jpg", (11.2, 10.1, 139.4, 342))],
     shape=("etyud-do", "doorglass_etyud_do"))
def etyud_do(a):
    """White satin; four long near-black grass blades rising from tapered tips at the bottom, twisting round each
    other (an elongated lens in the upper middle, X-crossings below), three three-leaf sprigs (top middle, left, right
    low) and three small outlined leaves."""
    L = a.layer(ETYUD_INK)
    E = a.layer(**ERASE)
    L2 = a.layer(ETYUD_INK)
    E2 = a.layer(**ERASE)
    for pts, w, tp in (
        ([[401, 300], [380, 380], [354, 500], [337, 620], [340, 720], [362, 830], [390, 905], [382, 990],
          [372, 1100], [382, 1200], [400, 1262], [410, 1350], [412, 1450], [410, 1566]], 3.4, (140, 10)),
        ([[446, 418], [428, 500], [404, 600], [382, 700], [372, 800], [386, 895], [420, 960], [450, 1045],
          [455, 1130], [432, 1208], [402, 1262], [386, 1300], [378, 1334]], 3.2, (120, 6)),
        ([[384, 356], [364, 450], [350, 560], [358, 660], [382, 750], [410, 820], [424, 858]], 2.8, (110, 6)),
        ([[426, 676], [404, 760], [379, 850], [366, 935], [368, 1030], [386, 1150], [404, 1240], [417, 1320],
          [419, 1420], [415, 1532]], 2.6, (90, 90)),
    ):
        P = spline(pts)
        L.stroke(P, w * 2.2, taper=tp)                  # a double line: dark with a satin core
        E.stroke(P, w * 0.5, taper=(tp[0] * 1.3, tp[1] + 20))
    sprig3(L2, E2, (408, 1566), -2)
    sprig3(L2, E2, (378, 1334), -40)
    sprig3(L2, E2, (424, 858), 32)
    L = L2
    for b, t, w, bend in (((449, 1497), (477, 1548), 17, 0.08), ((392, 1263), (333, 1267), 16, -0.1),
                          ((440, 776), (472, 814), 16, 0.08)):
        L.leaf_line(b, t, w, 2.0, bend=bend)
        L.stroke(leaf_mid(b, t, bend, 0.1, 0.75), 1.0)


# ================================================================================================ Афина, Селена
FROST_LINE = "#a39b94"         # thin light grey line (sandblasted look) of Афина / Селена / Стиль
FROST_FILL = "#b3aca6"         # their filled ornaments


def pane_ring(design, ref):
    return design_rings(design, ref)[0]


def star4(L, F, c, rx, ry, pinch=0.35, w=2.2):
    """A four-pointed star with concave sides (outline) centred at c."""
    cx, cy = c
    pts = []
    for k in range(4):
        a0 = math.pi / 2 * k
        p0 = np.array([cx + rx * math.cos(a0), cy + ry * math.sin(a0)])
        a1 = a0 + math.pi / 2
        p1 = np.array([cx + rx * math.cos(a1), cy + ry * math.sin(a1)])
        m = (p0 + p1) / 2
        m = np.array([cx, cy]) + (m - [cx, cy]) * (1 - pinch)
        t = np.linspace(0, 1, 16)[:, None]
        pts.append((1 - t) ** 2 * p0 + 2 * (1 - t) * t * m + t ** 2 * p1)
    P = np.vstack(pts)
    F.fill(P)
    L.stroke(closed(P), w)


def jewel_dark(a, x, y, r):
    """A dark grey faceted glass jewel (Афина): a dark disc, a darker rim, a light glint."""
    a.layer("#3f3d3c").dot(x, y, r)
    a.layer("#6d6966").dot(x - r * 0.12, y + r * 0.1, r * 0.72)
    a.layer("#8f8a86").dot(x - r * 0.25, y + r * 0.25, r * 0.36)
    a.layer("#e8e4e0", smooth=0.9).dot(x - r * 0.38, y + r * 0.38, r * 0.16)


@art("doorglass_afina_do", "fit", "Афина СТ-Худ. (контур и звезда)", (130.6, 646.2, 669.4, 1902),
     photos=[_ph("p096_afina-f-01__dub-st-hud.jpg"), _ph("p096_afina-f-11__oreh-st-hud.jpg")],
     shape=("afina-do", "doorglass_afina_do"))
def afina_do(a):
    """White satin; a thin light grey line following the pane's outline 24 mm inside it (inside the bead), a
    vertical line on the pane's axis and a horizontal one at y 1240 from outline to outline, crossing in a
    four-pointed concave star (124 x 124 mm) with a dark grey jewel in its middle."""
    ring = pane_ring("afina-do", "doorglass_afina_do")
    L = a.layer(FROST_LINE)
    F = a.layer(**ERASE)
    L2 = a.layer(FROST_LINE)
    # 24 mm in at the sides, deeper under the arch (the photos' line runs ~30 mm lower there)
    I = inset(ring, lambda P: 24 + 30 * np.clip((P[:, 1] - 1640) / 220, 0, 1), smooth=6)
    L.stroke(closed(I), 2.4)
    cy = 1240.0
    top = float(I[np.abs(I[:, 0] - 400) < 3][:, 1].max())
    bot = float(I[np.abs(I[:, 0] - 400) < 3][:, 1].min())
    band = I[np.abs(I[:, 1] - cy) < 3][:, 0]
    L.stroke([[400, bot], [400, top]], 2.4)
    L.stroke([[band.min(), cy], [band.max(), cy]], 2.4)
    star4(L2, F, (400, cy), 64, 66, pinch=0.22, w=2.4)
    jewel_dark(a, 400, cy, 13)


SELENA_YC = 1311.0


@art("doorglass_selena_do", "fit", "Селена СТ-Худ. (решётка, гирлянды и лилия)", (128, 812, 672, 1888),
     photos=[_ph("p096_selena-f-01__dub-st-hud.jpg"), _ph("p097_selena-f-11__oreh-st-hud.jpg")],
     shape=("selena-do", "doorglass_selena_do"))
def selena_do(a):
    """White satin; a lattice of thin light grey lines: side lines 194 mm off the axis, a pinched vase in the middle
    (bowed in at the top and the bottom, pointed out at mid height), bars from the side lines to the vase at 1099,
    1311 and 1523; a garland of scrolls along the top and one along the bottom (a spiral in each corner, a pair of
    scrolls round a bud on the axis) and a lily in the middle (a bud, a spade leaf, two sweeping leaves, a drop and a
    pair of curls)."""
    L = a.layer("#9d958e")
    G = a.layer("#958d86")
    yc = SELENA_YC
    w = 3.0
    with a.mirror_x(400):
        with a.mirror_y(yc):
            L.stroke([[206, yc], [206, 1680]], w)                                         # side line
            L.stroke([[206, 1523], [289, 1523]], w)                                       # bars
            L.stroke([[206, yc], [241, yc]], w)
            L.curve([[300, 1712], [321, 1668], [327, 1612], [314, 1561], [290, 1523], [284, 1470], [287, 1420],
                     [296, 1386]], w)                                                     # the vase
            L.curve([[296, 1386], [266, 1348], [241, yc]], w)
            # garland: the corner spiral with its tail along the top ending in a small curl
            scroll(G, [[294, 1702], [284, 1714], [250, 1720], [218, 1716], [200, 1706]], (176, 1688), 23, 70,
                   1.4, 3.6, cw=False, r_end=0.22, swell=0.3)
            G.leaf((226, 1717), (258, 1737), 10, bend=0.25)
            G.leaf((200, 1706), (214, 1676), 9, bend=-0.2)
            scroll(G, [[300, 1712], [312, 1722], [328, 1721]], (332, 1706), 10, 100, 1.2, 3.0, cw=True, r_end=0.3)
            # the scroll pair on the axis
            scroll(G, [[400, 1700], [386, 1713], [366, 1719], [346, 1715]], (342, 1698), 15, 90, 1.3, 3.4,
                   cw=False, r_end=0.22, swell=0.3)
            G.leaf((394, 1708), (364, 1736), 10, bend=0.2)
    for yy, sg in ((1704, 1), (2 * yc - 1704, -1)):
        G.teardrop((400, yy - 6 * sg), (400, yy + 26 * sg), 12)
    # the lily (~170 x 210 mm): a bud over a pair of curls and a drop, two sweeping leaves in outline making a
    # "V", a spade petal between them and a pair of curls under it
    F = a.layer("#a39b94")
    E = a.layer(**ERASE)
    O = a.layer("#9d958e")
    F.teardrop((400, 1372), (400, 1410), 16)                                              # top bud
    F.teardrop((400, 1342), (400, 1318), 10)                                              # drop
    E.leaf((400, 1236), (400, 1312), 22, shape=0.62)                                      # middle petal
    O.leaf_line((400, 1236), (400, 1312), 22, 2.8, shape=0.62)
    O.stroke([[400, 1244], [400, 1290]], 1.8)
    with a.mirror_x(400):
        scroll(O, [[400, 1352], [390, 1350], [378, 1356]], (372, 1368), 10, -60, 1.25, 3.2, cw=False, r_end=0.3)
        for b, t, wd, bd in (((398, 1226), (322, 1334), 26, -0.16), ((398, 1232), (350, 1322), 16, -0.14)):
            E.leaf(b, t, wd, bend=bd, shape=0.45)                                         # the tulip leaves
            O.leaf_line(b, t, wd, 2.8, bend=bd, shape=0.45)
            O.stroke(leaf_mid(b, t, bd, 0.12, 0.7), 1.6, taper=(0, 10))
        scroll(O, [[400, 1224], [388, 1212], [370, 1208], [352, 1210]], (344, 1224), 13, -90, 1.3, 3.6,
               cw=True, r_end=0.22, swell=0.3)


# ================================================================================================ Азалия
# The ornaments are drawn as "bands": calligraphic scroll shapes (a centre line with a width along it) of which
# only the outline shows - grey on the glass, a carved groove on the panels. Coordinates are local (corner ornament:
# the corner at the origin, the arms along +x / +y, sized as on the plain leaf's upper panel, ~335 x 310 mm;
# medallion ornament: centred at the origin, ~300 x 60 mm) and placed with `place`.
def band(lead, w, spiral=None, start=0.22, end=0.3):
    """A band along the smooth line through `lead` (optionally ending in a spiral: (centre, r, a0, turns, cw)),
    widest (w) in its middle, pointed at the start (over the fraction `start`) and at the end (over `end`), or
    thinning to 0.3 w into the spiral's eye. -> (points Nx2, widths N)."""
    from art_wave3 import scroll_pts
    if spiral:
        c, r, a0, turns, cw = spiral
        P = scroll_pts(lead, c, r, a0, turns, cw, 0.28)
        sp_n = len(spiral_pts := spiral_raw(c, r, a0, turns, cw))
        n_lead = len(P) - sp_n
        Q = spline(np.vstack([P[:n_lead], P[n_lead:n_lead + 1]])) if n_lead >= 1 else P[:1]
        P = np.vstack([Q, P[n_lead + 1:]])
        s = arclen(P)
        u = s / s[-1]
        us = arclen(Q)[-1] / s[-1]
        W = w * (1 - 0.7 * np.clip((u - us) / max(1 - us, 1e-6), 0, 1) ** 0.8)
        del spiral_pts
    else:
        P = spline(lead)
        s = arclen(P)
        u = s / s[-1]
        W = w * np.sin(np.clip((1 - u) / end, 0, 1) * np.pi / 2) ** 0.7
    W = W * np.sin(np.clip(u / start, 0, 1) * np.pi / 2) ** 0.7
    return P, np.maximum(W, 0.6)


def spiral_raw(c, r, a0, turns, cw):
    a1 = a0 - 360 * turns if cw else a0 + 360 * turns
    return spiral(c[0], c[1], r, r * 0.28, a0, a1, step=max(0.6, r / 12))


def band_ring(P, W):
    """The outline (closed ring) of a band."""
    T = np.gradient(P, axis=0)
    T /= np.maximum(np.hypot(*T.T), 1e-9)[:, None]
    N = np.stack([-T[:, 1], T[:, 0]], 1)
    return np.vstack([P + N * W[:, None] / 2, (P - N * W[:, None] / 2)[::-1]])


def place(bands, x, y, sx=1.0, sy=1.0, s=1.0):
    """Bands moved to the leaf: local point p -> (x, y) + p * (sx s, sy s) (sx / sy = -1 mirror)."""
    k = np.array([sx * s, sy * s])
    return [(np.array([x, y]) + P * k, W * s) for P, W in bands]


def azaliya_corner():
    """The Азалия corner ornament (bottom-left orientation, ~336 x 315 mm): a volute at the top of the side arm
    with a thorn, an S-lobe with a thorn below it, a small curl, a "2"-shaped curl and two small ones in the corner,
    along the bottom a thorn, a hooked leaf, a C-wave and a rolled end."""
    B = []
    # side arm: the top volute (from its thorn tip, anticlockwise into the eye)
    B.append(band([[88, 244], [84, 266], [72, 290]], 20, ((40, 280), 33, 30, 1.2, False), start=0.3))
    # the S-lobe under it, bulging right to a corner, back left into the corner group
    B.append(band([[22, 244], [13, 212], [26, 192], [62, 182], [96, 166], [84, 140], [56, 122], [30, 100]], 19,
                  start=0.12, end=0.25))
    B.append(band([[30, 196], [16, 190], [4, 184]], 10, start=0.2, end=0.8))                 # its thorn
    B.append(band([[40, 206], [58, 200], [76, 188], [86, 172]], 9, start=0.3, end=0.4))     # a leaf in the lobe
    B.append(band([[74, 150], [58, 146], [48, 140]], 9, ((40, 132), 11, 60, 1.1, False)))   # small curl
    # the corner: a "2" (from the bottom stroke, up the diagonal, round anticlockwise over the top)
    B.append(band([[128, 10], [88, 5], [58, 12], [66, 30], [88, 42]], 20, ((100, 62), 22, -80, 1.1, False),
                  start=0.15))
    B.append(band([[112, 96], [96, 104], [80, 100]], 9, ((72, 90), 9, 90, 1.1, False)))
    B.append(band([[8, 110], [4, 80], [12, 62], [30, 60]], 13, ((24, 74), 12, -30, 1.1, False), start=0.2))
    B.append(band([[6, 52], [8, 20], [24, 8], [44, 14]], 13, ((34, 28), 11, -30, 1.1, False), start=0.2))
    # bottom arm: a thorn, a hooked leaf, a C-wave, the rolled end
    B.append(band([[132, 30], [142, 58], [152, 92]], 14, start=0.25, end=0.6))
    B.append(band([[160, 86], [176, 70], [190, 40], [206, 22], [232, 16]], 19, start=0.2, end=0.3))
    B.append(band([[212, 74], [242, 68], [254, 44], [242, 24], [222, 28]], 17, start=0.25, end=0.35))
    B.append(band([[236, 8], [268, 6], [296, 12], [318, 24]], 18, ((316, 42), 18, -60, 1.2, False),
                  start=0.2))
    B.append(band([[268, 30], [280, 52], [292, 60]], 8, start=0.3, end=0.5))
    return B


def azaliya_medallion():
    """The Азалия medallion ornament (~300 x 60 mm): a lozenge cross in the middle and on each side a long
    teardrop loop (thin at the middle, round at its far end) with a curl rolled inside its far end."""
    B = []
    for sx in (1, -1):
        m = np.array([sx, 1.0])
        B.append(band([p * m for p in ([8, -4], [50, -14], [100, -22], [134, -16], [146, 2], [136, 20],
                                       [104, 26], [60, 18], [22, 8], [8, 4])], 7, start=0.06, end=0.06))
        B.append(band([p * m for p in ([34, 2], [70, 4], [96, 0])], 7, ((110 * sx, 4), 11, -90 if sx > 0 else -90,
                                                                        1.2, sx < 0), start=0.25))
    B.append(band([[0, -32], [0, 0], [0, 32]], 10, start=0.5, end=0.5))
    B.append(band([[-20, 0], [0, 0], [20, 0]], 7, start=0.5, end=0.5))
    return B


def draw_outlined(a, bands, line, fill, w=2.4, layers=None):
    """Glass version: each band filled with `fill` and outlined with `line`, later bands over earlier ones."""
    if layers is None:
        layers = [(a.layer(**fill), a.layer(line)) for _ in bands]
    for (P, W), (F, L) in zip(bands, layers):
        R = band_ring(P, W)
        F.fill(R)
        L.stroke(closed(R), w)
    return layers


CARVE_SHADOW = dict(color="#1e1108", alpha=0.82, smooth=0.25)
CARVE_LIGHT = dict(color="#fff3e2", alpha=0.34, smooth=0.35)
CARVE_ERASE = dict(NONE)


def draw_carved(a, bands, w=4.0, layers=None):
    """Carved version (a decal): each band's outline as a routed groove lit from the upper left - a dark line (the
    groove's shaded upper-left wall) and a thin light line beside it on the lower right (its lit wall); inside a
    band the grooves of the bands under it are erased."""
    if layers is None:
        layers = [(a.layer(**CARVE_ERASE), a.layer(**CARVE_SHADOW), a.layer(**CARVE_LIGHT)) for _ in bands]
    for (P, W), (E, D, L) in zip(bands, layers):
        R = band_ring(P, W)
        E.fill(R)
        D.stroke(closed(R) + [-0.35 * w, 0.35 * w], w)
        L.stroke(closed(R) + [0.75 * w, -0.75 * w], w * 0.6)
    return layers


AZ_LINE = "#9f9790"
AZ_FILL = dict(color="#f7f2ec", alpha=0.92, smooth=0.4)


@art("doorglass_azaliya_do", "fit", "Азалия СТ-Худ. (угловые орнаменты)", (156, 917, 644, 1870),
     photos=[_ph("p098_azaliya-f-01__dub-st-hud.jpg"), _ph("p098_azaliya-f-11__oreh-st-hud.jpg")],
     shape=("azaliya-do", "doorglass_azaliya_do"))
def azaliya_do(a):
    """White satin arch; grey outlined scroll ornaments in the top left corner (~245 x 230 mm) and the bottom right
    one (the plain leaf's panel corners mirrored)."""
    C = azaliya_corner()
    lay = draw_outlined(a, place(C, 219, 1753, 1, -1, 0.73), AZ_LINE, AZ_FILL)
    draw_outlined(a, place(C, 590, 973, -1, 1, 0.73), AZ_LINE, AZ_FILL, layers=lay)


@art("doorglass_azaliya_do_2", "fit", "Азалия СТ-Худ., медальон", (165, 668, 635, 872),
     photos=[_ph("p098_azaliya-f-01__dub-st-hud.jpg"), _ph("p098_azaliya-f-11__oreh-st-hud.jpg")],
     shape=("azaliya-do", "doorglass_azaliya_do_2"))
def azaliya_do_2(a):
    """White satin ellipse; the grey outlined medallion ornament (~275 x 60 mm)."""
    draw_outlined(a, place(azaliya_medallion(), 400, 764, s=0.92), AZ_LINE, AZ_FILL)


@art("doorart_azaliya", "decal", "Азалия: резной орнамент филёнок", (0, 0, 800, 2000),
     photos=[_ph("p098_azaliya-f-01__dub.jpg"), _ph("p098_azaliya-f-15__makore.jpg")],
     shape=("azaliya", "doorart_azaliya"), under=["#d7a580", "#753122"])
def azaliya(a):
    """The plain Азалия's carved ornaments (painted relief shading, transparent elsewhere): the upper panel's top
    right and bottom left corners, the medallion's scroll and the lower panel's bottom left corner."""
    C = azaliya_corner()
    lay = draw_carved(a, place(C, 198, 962, 1, 1, 1.0))
    draw_carved(a, place(C, 596, 1775, -1, -1, 0.98), layers=lay)
    draw_carved(a, place(C, 196, 218, 1, 1, 1.02), layers=lay)
    draw_carved(a, place(azaliya_medallion(), 400, 765, s=1.05))


@art("doorart_azaliya_do", "decal", "Азалия СТ-Худ.: резной орнамент нижней филёнки", (100, 120, 700, 720),
     photos=[_ph("p098_azaliya-f-01__dub-st-hud.jpg"), _ph("p098_azaliya-f-11__oreh-st-hud.jpg")],
     shape=("azaliya-do", "doorart_azaliya_do"), under=["#d7a580", "#915d35"])
def azaliya_do_panel(a):
    """The glazed Азалия's lower panel: the same carved bottom left corner ornament as the plain leaf."""
    draw_carved(a, place(azaliya_corner(), 196, 218, 1, 1, 1.02))


# ================================================================================================ Стиль
STIL_C = (400.0, 1414.0)       # the medallion's centre = the pane's centre


def stil_corner(F, L):
    """A small scroll corner for Стиль's frame line (top left orientation, the frame corner at the origin)."""
    scroll(F, [[4, -6], [26, -4], [50, -8], [64, -18]], (56, -30), 11, 20, 1.25, 3.4, cw=True, r_end=0.25)
    scroll(F, [[6, -4], [4, -26], [8, -50], [18, -64]], (30, -56), 11, 250, 1.25, 3.4, cw=False, r_end=0.25)
    F.leaf((10, -10), (40, -40), 13, bend=0.15)
    F.leaf((22, -12), (46, -22), 8, bend=-0.2)
    F.leaf((12, -22), (20, -48), 8, bend=0.2)
    F.dot(78, -12, 3.5)
    F.dot(12, -78, 3.5)


def stil_medallion(F, L):
    """Стиль's damask medallion, the upper right quarter relative to its centre (drawn under mirror_x / mirror_y):
    the cross in the middle, one of the pair of C-scrolls (a lyre over the cross), a fern spray at the side, a tulip
    and the top fleur."""
    F.leaf((0, 0), (0, 70), 16, shape=0.5)                                     # the cross: vertical lozenge
    F.leaf((0, 0), (46, 0), 12, shape=0.45)                                    # horizontal arm
    F.dot(0, 0, 7)
    F.leaf((6, 6), (26, 30), 8, shape=0.5)                                     # diagonal leaflets
    scroll(F, [[3, 84], [10, 94], [30, 99], [52, 108], [62, 128]], (34, 132), 27, -10, 1.3, 6.0, cw=False,
           r_end=0.26, swell=0.2)                                              # a C-scroll of the lyre
    F.leaf((16, 150), (4, 168), 7, bend=0.2)
    # the fern spray at the side: a curved stem with leaflets pointing out
    stem = spline([[34, 10], [62, 18], [86, 34], [100, 58], [96, 80]])
    F.stroke(stem, 3.0, taper=(0, 12))
    scroll(F, [[97, 76], [92, 86]], (84, 84), 6, 0, 1.1, 2.6, cw=False, r_end=0.3)
    for t, ang, ln in ((0.3, 95, 20), (0.45, 5, 24), (0.62, 120, 18), (0.74, 15, 22), (0.88, 160, 14)):
        p = stem[int(t * (len(stem) - 1))]
        v = np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))])
        F.leaf(p, p + v * ln, 9, bend=0.15)
    F.leaf((96, 6), (118, 2), 10, bend=0.1)                                    # the spray's tip at mid height
    F.leaf((0, 164), (0, 200), 20, shape=0.6)                                  # tulip: middle petal
    F.leaf((4, 164), (20, 196), 11, bend=-0.25, shape=0.5)                     # side petal
    F.leaf((0, 204), (0, 222), 8)                                              # neck
    F.leaf((0, 218), (0, 272), 13, shape=0.3)                                  # the fleur: spike
    F.leaf((3, 222), (36, 244), 11, bend=0.3, shape=0.4)                       # its side leaves
    F.leaf((3, 220), (34, 214), 7, bend=-0.3)
    F.dot(42, 226, 3.5)


@art("doorglass_stil_do", "fit", "Стиль СТ-Худ. (рамка и дамасский медальон)", (197, 980.5, 603, 1847.5),
     photos=[_ph("p098_stil-f-01__dub-st-hud.jpg"), _ph("p099_stil-f-22__beldub-st-hud.jpg")],
     shape=("stil-do", "doorglass_stil_do"))
def stil_do(a):
    """White satin; a thin light grey frame line 25 mm inside the pane with a small scroll ornament in every corner,
    and a damask medallion (~230 x 570 mm) in the middle: a lozenge cross, a C-scroll pair, leafy sprays and a tulip
    and a fleur above and below."""
    L = a.layer(FROST_LINE)
    F = a.layer(FROST_FILL)
    x0, y0, x1, y1 = 222, 1005.5, 578, 1822.5
    L.rect(x0, y0, x1, y1, w=2.4)
    L.rect(x0 + 6, y0 + 6, x1 - 6, y1 - 6, w=1.2)
    cx, cy = STIL_C
    with a.mirror_x(cx), a.mirror_y(cy):
        with a.at(x0 + 6, y1 - 6, s=1.25):
            stil_corner(F, L)
        with a.at(cx, cy):
            stil_medallion(F, L)


@art("doorglass_stil_do_2", "fit", "Стиль СТ-Худ., узкое стекло (плетёнка и завитки)", (197, 721.5, 603, 778.5),
     photos=[_ph("p098_stil-f-01__dub-st-hud.jpg"), _ph("p099_stil-f-22__beldub-st-hud.jpg")],
     shape=("stil-do", "doorglass_stil_do_2"))
def stil_do_2(a):
    """White satin strip: a chain of interlaced lozenges in the middle, scroll tendrils running out from it to both
    ends with small curls and leaves."""
    L = a.layer(FROST_LINE)
    F = a.layer(FROST_FILL)
    cy = 750.0
    with a.mirror_x(400):
        for x in (400, 444):                                                    # the interlaced lozenges
            L.stroke(closed([[x - 30, cy], [x, cy + 16], [x + 30, cy], [x, cy - 16]]), 2.4)
        F.dot(422, cy, 3.2)
        # the tendril: a wave from the chain's tip to a curl near the end, a counter-curl and two leaves
        scroll(F, [[474, cy], [494, cy + 7], [516, cy + 6], [536, cy - 1]], (544, cy - 8), 8, 150, 1.25, 2.8,
               cw=True, r_end=0.3, swell=0.2)
        scroll(F, [[504, cy + 5], [516, cy - 4], [522, cy - 11]], (512, cy - 13), 6, 0, 1.1, 2.2, cw=False,
               r_end=0.35)
        F.leaf((488, cy + 5), (500, cy + 19), 7, bend=-0.25)
        F.leaf((528, cy + 3), (548, cy + 14), 7, bend=-0.2)
        F.dot(566, cy + 2, 2.6)
    F.dot(400, cy, 3.6)


# ================================================================================================ Лилия
LILY_LINE = "#6e7480"          # thin blue-grey line


def lily_bud(L, E, base, tip, width, w=2.0, sepal=1):
    """A slender lily bud in outline: a pointed bud, a line down its middle to two thirds and a sepal curving away
    from its base on the side `sepal` (+1 left of base->tip, -1 right, 0 none)."""
    b, t = np.asarray(base, np.float64), np.asarray(tip, np.float64)
    E.leaf(b, t, width, shape=0.38)
    L.leaf_line(b, t, width, w, shape=0.38)
    L.stroke(leaf_mid(b, t, 0.0, 0.1, 0.72), w * 0.8)
    if sepal:
        d = t - b
        n = np.array([-d[1], d[0]]) * sepal
        L.curve([b + d * 0.05, b + d * 0.35 + n * 0.25, b + d * 0.7 + n * 0.45], w * 0.9, taper=(0, 12))


def lily_stem(L, P, w=2.0, taper=(0, 60), E=None):
    """A stem: a line, or a hollow stem (two hairlines) when a satin layer E is given."""
    Q = spline(P)
    if E is None:
        L.stroke(Q, w, taper=taper)
    else:
        L.stroke(Q, w * 2.4, taper=taper)
        E.stroke(Q, w * 0.9, taper=(taper[0] * 1.2, taper[1] * 1.2))


def dashes(L, P, on=7.0, off=5.0, w=2.2):
    """A dashed line along the smooth line through P."""
    Q = spline(P, step=0.5)
    s = arclen(Q)
    t0 = 0.0
    while t0 < s[-1]:
        m = (s >= t0) & (s <= t0 + on)
        if m.sum() > 1:
            L.stroke(Q[m], w)
        t0 += on + off


@art("doorglass_liliya_do", "fit", "Лилия СТ-Худ. (стебли с бутонами лилий)", (125.9, 495.6, 452.6, 1917.4),
     photos=[_ph("p099_liliya-f-01__dub-st-hud.jpg"), _ph("p099_liliya-f-11__oreh-st-hud.jpg")],
     shape=("liliya-do", "doorglass_liliya_do"))
def liliya_do(a):
    """White satin S-crescent; two thin blue-grey hollow stems following it, three slender lily buds in outline
    (top, left at mid height, middle) and below the middle bud the stems turn into a pair of dashed lines running
    down into the crescent's tail."""
    E0 = a.layer(**ERASE)
    L0 = a.layer(LILY_LINE)
    E = a.layer(**ERASE)
    L = a.layer(LILY_LINE)
    lily_stem(L0, [[292, 1690], [280, 1600], [258, 1500], [238, 1400], [228, 1300], [232, 1200], [248, 1100],
                   [270, 1010], [300, 920], [332, 830]], 1.8, taper=(0, 40), E=E0)
    lily_stem(L0, [[206, 1336], [216, 1270], [222, 1190], [232, 1110], [252, 1040], [280, 960], [306, 890]], 1.6,
              taper=(0, 40), E=E0)
    lily_stem(L0, [[262, 1072], [268, 1010], [284, 950]], 1.5, taper=(0, 20), E=E0)
    lily_bud(L, E, (292, 1690), (304, 1770), 19, w=2.2, sepal=1)
    lily_bud(L, E, (206, 1336), (188, 1416), 21, w=2.2, sepal=-1)
    lily_bud(L, E, (262, 1072), (254, 1146), 18, w=2.2, sepal=-1)
    L.curve([[210, 1350], [192, 1370], [178, 1396]], 1.8, taper=(0, 10))            # a leaf line by the left bud
    for off in (0, 13):
        dashes(L, [[296 + off, 940], [322 + off, 860], [346 + off, 780], [368 + off, 700], [384 + off, 620],
                   [396 + off, 560]], 6.0, 4.5, 2.4)


@art("doorglass_liliya_do_2", "fit", "Лилия СТ-Худ., язычок (бутоны)", (187.1, 363.4, 377.6, 859.0),
     photos=[_ph("p099_liliya-f-01__dub-st-hud.jpg"), _ph("p099_liliya-f-11__oreh-st-hud.jpg")],
     shape=("liliya-do", "doorglass_liliya_do_2"))
def liliya_do_2(a):
    """White satin tongue; two lily buds in outline pointing up-left on long hollow stems sweeping down to its
    point."""
    E0 = a.layer(**ERASE)
    L0 = a.layer(LILY_LINE)
    E = a.layer(**ERASE)
    L = a.layer(LILY_LINE)
    lily_stem(L0, [[290, 672], [306, 632], [326, 582], [342, 530], [352, 490]], 1.7, taper=(0, 40), E=E0)
    lily_stem(L0, [[286, 610], [308, 572], [330, 526], [348, 480], [356, 456]], 1.6, taper=(0, 40), E=E0)
    lily_bud(L, E, (290, 672), (258, 726), 18, w=2.2, sepal=-1)
    lily_bud(L, E, (286, 610), (252, 660), 16, w=2.2, sepal=1)


@art("doorglass_liliya_do_3", "fit", "Лилия СТ-Худ., малое стекло", (124.7, 247.0, 293.6, 432.9),
     photos=[_ph("p099_liliya-f-01__dub-st-hud.jpg"), _ph("p099_liliya-f-11__oreh-st-hud.jpg")],
     shape=("liliya-do", "doorglass_liliya_do_3"))
def liliya_do_3(a):
    """Plain white satin: the photos show no drawing on the small bottom piece."""


# ================================================================================================ Лагуна, Эксклюзив Ф-17
VINE_LINE = "#78696a"          # the grey print of the hollow stems on bronze satin
VINE_LEAF = "#88726a"          # the leaves: a darker grey-brown
VINE_VEIN = dict(color="#b39485", alpha=0.9, smooth=0.4)        # a vein: the bronze glass showing through


def fan_leaves(F, V, c, angles, lengths, width, bend=0.08):
    """Pointed leaves radiating from c (angles in deg from the vertical, + = right), a light vein in each."""
    c = np.asarray(c, np.float64)
    for ang, ln in zip(angles, lengths):
        v = _rot(np.array([0.0, 1.0]), -ang)
        tip = c + v * ln
        b = c + v * ln * 0.08
        bd = bend * (1 if ang < 0 else -1)
        F.leaf(b, tip, width * (0.75 + 0.25 * ln / max(lengths)), bend=bd, shape=0.42)
        V.stroke(leaf_mid(b, tip, bd, 0.12, 0.8), 1.1, taper=(4, 12))


def vine_leaf(F, V, c, ang, size):
    """A vine / maple leaf pointing at ang (deg from the vertical, + = right): five pointed lobes, the veins light."""
    c = np.asarray(c, np.float64)
    for da, k, wk in ((0, 1.0, 0.5), (-42, 0.78, 0.45), (42, 0.78, 0.45), (-88, 0.5, 0.36), (88, 0.5, 0.36)):
        v = _rot(np.array([0.0, 1.0]), -(ang + da))
        tip = c + v * size * k
        F.leaf(c - v * size * 0.06, tip, size * wk, shape=0.4)
        V.stroke([c + v * size * 0.05, c + v * size * k * 0.75], 1.1, taper=(0, 8))
    F.dot(c[0], c[1], size * 0.16)


def hollow(L, E, P, w=4.4, core=1.6, taper=(0, 0)):
    """A hollow stem: a grey line with a glass-coloured core."""
    Q = spline(P)
    L.stroke(Q, w, taper=taper)
    E.stroke(Q, core, taper=(taper[0] * 1.3, taper[1] * 1.3))


def rhinestone(a, x, y, r=3.2):
    """A small clear rhinestone on the glass: a white faceted dot with a four-pointed glint."""
    a.layer("#8d7c74", smooth=0.9).dot(x, y, r * 1.15)
    a.layer("#ffffff", smooth=0.95, metallic=0.2).dot(x, y, r)
    G = a.layer("#ffffff", alpha=0.95, smooth=0.95)
    G.diamond(x, y, r * 0.9, r * 4.2)
    G.diamond(x, y, r * 4.2, r * 0.9)


@art("doorglass_laguna_do", "fit", "Лагуна СТ-Худ. (виноградная лоза)", (130.2, 599.0, 507.6, 1885.8), base=BRONZE,
     photos=[("p100_laguna-f-01__dub-st-hud.jpg", (10.5, 10.5, 140, 342)),
             ("p100_laguna-f-17__shokolad-st-hud.jpg", (10.5, 10.5, 140, 342))],
     shape=("laguna-do", "doorglass_laguna_do"))
def laguna_do(a):
    """Bronze satin; two hollow grey stems twisting round each other up the panel (a lens where they part), a fan
    of dark leaves at the top, single leaves and vine-leaf clusters along them, curling tendrils, a thin tendril with
    a ring on the right and two clear rhinestones."""
    L = a.layer(VINE_LINE)
    E = a.layer(color=BRONZE["color"], alpha=BRONZE["alpha"], smooth=BRONZE["smooth"])
    F = a.layer(VINE_LEAF)
    V = a.layer(**VINE_VEIN)
    hollow(L, E, [[268, 1690], [250, 1604], [258, 1544], [232, 1485], [202, 1426], [212, 1389], [268, 1359],
                  [304, 1337], [328, 1285], [318, 1233], [298, 1189], [246, 1115], [224, 1070], [222, 1011],
                  [209, 937], [196, 860], [190, 800]], 9.0, 3.2, taper=(0, 90))
    hollow(L, E, [[320, 1672], [292, 1619], [280, 1559], [272, 1485], [250, 1419], [266, 1367], [260, 1337],
                  [236, 1293], [248, 1248], [300, 1216], [305, 1189], [268, 1152], [240, 1120], [230, 1060]],
           8.0, 2.8, taper=(0, 60))
    hollow(L, E, [[268, 1690], [276, 1716], [290, 1730]], 7.0, 2.6)
    # tendrils
    L.curve([[266, 1690], [240, 1706], [214, 1708], [200, 1696]], 3.4, taper=(0, 20))
    scroll(L, [[246, 1115], [214, 1110], [196, 1120]], (190, 1136), 9, -80, 1.2, 3.4, cw=True, r_end=0.3)
    scroll(L, [[298, 1189], [322, 1176], [340, 1180]], (344, 1194), 9, -90, 1.2, 3.4, cw=False, r_end=0.3)
    L.curve([[338, 1330], [358, 1380], [368, 1440], [372, 1480], [364, 1500]], 3.0, taper=(0, 0))
    L.ellipse(360, 1525, 21, 15, w=3.4, rot=-15)
    L.curve([[356, 1540], [372, 1570], [376, 1596], [364, 1622], [350, 1630]], 3.0, taper=(0, 20))
    scroll(L, [[364, 1622], [352, 1640], [340, 1640]], (338, 1630), 7, 90, 1.2, 2.6, cw=False)
    # leaves
    fan_leaves(F, V, (292, 1724), (-66, -40, -16, 6, 28, 50, 72), (60, 80, 100, 108, 96, 80, 58), 28)
    fan_leaves(F, V, (300, 1632), (55,), (42,), 20)
    fan_leaves(F, V, (246, 1506), (-42,), (70,), 27)
    fan_leaves(F, V, (310, 1392), (8,), (82,), 28)
    vine_leaf(F, V, (374, 1300), 70, 54)
    vine_leaf(F, V, (200, 1192), -35, 52)
    fan_leaves(F, V, (220, 1122), (-60,), (34,), 17)
    fan_leaves(F, V, (256, 1080), (70,), (36,), 17)
    rhinestone(a, 388, 1496)
    rhinestone(a, 384, 1472, 2.6)


@art("doorglass_eksklyuziv_do_hud", "fit", "Эксклюзив Ф-17 СТ-Худ. (цветы на стебле)", (227.6, 723.1, 537.4, 1885.5),
     base=BRONZE, photos=[("p100_eksklyuziv-f-17__shokolad-st-hud.jpg", (10.5, 10.5, 140, 341))],
     shape=("eksklyuziv-do-hud", "doorglass_eksklyuziv_do_hud"))
def eksklyuziv_do_hud(a):
    """Bronze satin; a thin grey stem rising from the pane's lower point to two flowers (a fan of dark pointed
    leaves round a rhinestone), a loop curling under each flower, a leaf and a tendril on the stem."""
    L = a.layer(VINE_LINE)
    F = a.layer(VINE_LEAF)
    V = a.layer(**VINE_VEIN)
    L.curve([[252, 780], [290, 900], [326, 990], [352, 1080], [372, 1170], [394, 1260], [420, 1340], [430, 1400],
             [430, 1464]], 2.6, taper=(80, 0))
    L.curve([[430, 1400], [410, 1480], [396, 1560], [390, 1640], [388, 1688]], 2.4)
    for c, r, a0 in (((390, 1418), 36, 200), ((376, 1622), 30, 190)):
        scroll(L, [[c[0] + r * 1.4, c[1] + r * 0.2], [c[0] + r * 0.9, c[1] - r * 0.8], [c[0], c[1] - r * 1.05],
                   [c[0] - r * 0.9, c[1] - r * 0.6]], c, r * 0.8, a0, 1.1, 2.4, cw=True, r_end=0.3, swell=0.2)
    scroll(L, [[372, 1170], [350, 1188], [334, 1200]], (340, 1214), 10, 200, 1.2, 2.2, cw=True, r_end=0.3)
    fan_leaves(F, V, (432, 1330), (-4,), (56,), 18)
    fan_leaves(F, V, (430, 1476), (-52, -26, -4, 18, 42, 64), (40, 56, 72, 64, 52, 40), 19)
    fan_leaves(F, V, (388, 1692), (-54, -28, -6, 16, 40, 62), (44, 62, 80, 72, 58, 44), 20)
    rhinestone(a, 432, 1474)
    rhinestone(a, 388, 1690)


@art("doorglass_eksklyuziv_do_hud_2", "fit", "Эксклюзив Ф-17 СТ-Худ., среднее стекло (цветок)",
     (262.9, 456.0, 538.0, 1063.0), base=BRONZE,
     photos=[("p100_eksklyuziv-f-17__shokolad-st-hud.jpg", (10.5, 10.5, 140, 341))],
     shape=("eksklyuziv-do-hud", "doorglass_eksklyuziv_do_hud_2"))
def eksklyuziv_do_hud_2(a):
    """Bronze satin; a flower (a fan of dark leaves round a rhinestone) on a stem, sweeping arcs under it running
    down into the pane's lower point."""
    L = a.layer(VINE_LINE)
    F = a.layer(VINE_LEAF)
    V = a.layer(**VINE_VEIN)
    L.curve([[300, 520], [336, 600], [374, 680], [410, 750], [432, 800]], 2.4, taper=(60, 0))
    L.curve([[312, 560], [350, 660], [392, 730], [440, 772], [488, 784], [516, 770]], 2.2, taper=(50, 20))
    L.curve([[330, 740], [372, 772], [414, 790], [436, 806]], 2.0, taper=(20, 0))
    fan_leaves(F, V, (436, 806), (-58, -30, -6, 18, 44, 68), (34, 48, 62, 56, 46, 34), 18)
    rhinestone(a, 437, 806)


@art("doorglass_eksklyuziv_do_hud_3", "fit", "Эксклюзив Ф-17 СТ-Худ., малое стекло (бутон)",
     (295.7, 352.1, 546.1, 599.7), base=BRONZE,
     photos=[("p100_eksklyuziv-f-17__shokolad-st-hud.jpg", (10.5, 10.5, 140, 341))],
     shape=("eksklyuziv-do-hud", "doorglass_eksklyuziv_do_hud_3"))
def eksklyuziv_do_hud_3(a):
    """Bronze satin; a small bud of three dark leaves on a thin arc."""
    L = a.layer(VINE_LINE)
    F = a.layer(VINE_LEAF)
    V = a.layer(**VINE_VEIN)
    L.curve([[322, 410], [352, 446], [384, 474], [410, 492]], 2.4, taper=(40, 0))
    L.curve([[372, 468], [420, 500], [468, 528], [512, 566]], 2.0, taper=(30, 30))
    fan_leaves(F, V, (410, 492), (-36, -6, 24), (30, 42, 34), 16)
