"""Laminated doors' art glass (DveriMebel / el'PORTA / BRAVO 2020 catalogue, laminated series, pp. 117-121): the
printed / stained pictures on white satin glass of 3П, 3Х, 6П, 6Ф, 8П, 8Ф, 11Ф, 15Ф and 21Х-25Х.

Drawn from the Л-11 (ИталОрех) and Л-12 (МиланОрех) renders of each model. The photos are tiny (~0.19 px/mm) and
their leaf mapping includes some of the casing, so every position here was read off the photo resampled into the
design's pane (row by row: the photo's white pane span -> the design pane span, its height -> the pane's height) and
the motifs are drawn crisp at those places, in the photo's colours and density. Coordinates: leaf mm of the design
(x = 0 lock side, y up), the box = the art glass part's bounds in laminated-<model>.json.
"""
import math

import numpy as np

from art_wave3 import art, Art, SATIN, spline, arclen, design_rings  # noqa: F401

G = "doorglass_laminated_"
PAGES = {"3p": "p117_3p", "3h": "p117_3h", "6p": "p117_6p", "6f": "p118_6f", "8p": "p118_8p", "8f": "p118_8f",
         "11f": "p119_11f", "15f": "p120_15f", "21h": "p121_21h", "22h": "p121_22h", "23h": "p121_23h",
         "24h": "p121_24h", "25h": "p121_25h"}


# the leaf's bounds in the small photos' pixels (152 x 341; measured on 21Х's pane: find_leaf takes in the casing)
LEAF_PX = (13.1, 8.9, 139.5, 342.9)


def _ph(model):
    p = PAGES[model]
    return [(f"{p}-l-11__italoreh.jpg", LEAF_PX), (f"{p}-l-12__milanoreh.jpg", LEAF_PX)]


# ------------------------------------------------------------------------------------------------ pane helper
class Pane:
    """A design's glass ring: its span at a height, and widening of points about its centre line (the positions
    read off the resampled photos come out ~20 % narrower than the pane on the wavy panes)."""

    def __init__(self, design, ref, idx=0):
        self.ring = design_rings(design, ref)[idx]

    def edges(self, y):
        xs = []
        r = self.ring
        for (x0, y0), (x1, y1) in zip(r, np.roll(r, -1, 0)):
            if (y0 - y) * (y1 - y) <= 0 and y0 != y1:
                xs.append(x0 + (y - y0) / (y1 - y0) * (x1 - x0))
        return (min(xs), max(xs)) if xs else (np.nan, np.nan)

    def xc(self, y):
        a, b = self.edges(y)
        return (a + b) / 2

    def widen(self, pts, k):
        return [[self.xc(y) + (x - self.xc(y)) * k, y] for x, y in pts]

    def pt(self, x, y, k):
        return self.widen([[x, y]], k)[0]


# ------------------------------------------------------------------------------------------------ motif helpers
def _frame(base, tip, bend):
    b, t = np.asarray(base, np.float64), np.asarray(tip, np.float64)
    d = t - b
    n = float(np.hypot(*d))
    u = d / max(n, 1e-9)
    return b, d, n, np.array([-u[1], u[0]]), u


def _mid(base, tip, bend, s):
    b, d, n, nrm, _ = _frame(base, tip, bend)
    return b + np.outer(s, d) + np.outer(np.sin(np.pi * s) * bend * n, nrm)


def flame(L, base, tip, w, bend=0.0, cup=0.32, rb=0.62):
    """A drop / flame: round at the base, pointed at the tip (w = greatest width)."""
    s = np.linspace(0, 1, 60)
    mid = _mid(base, tip, bend, s)
    prof = np.where(s < cup, rb + (1 - rb) * np.sin(np.pi / 2 * s / cup),
                    np.cos(np.pi / 2 * (s - cup) / (1 - cup)) ** 0.85)
    L.stroke(np.column_stack([mid, np.maximum(w * prof, 0.35)]))


def vein(L, base, tip, w, bend=0.0, a=0.1, b=0.82):
    """The midrib of a leaf/flame drawn with the same bend, from a to b of its length, tapered."""
    s = np.linspace(a, b, 40)
    mid = _mid(base, tip, bend, s)
    L.stroke(mid, w, taper=(3, 0.45 * np.hypot(*(mid[-1] - mid[0]))))


def paisley(L, pts, w, tail=1.25):
    """A paisley / comma: round head at pts[0], its tail curling along the points and thinning to a point."""
    P = spline(pts)
    s = arclen(P)
    u = s / max(s[-1], 1e-9)
    W = np.maximum(w * np.clip(1 - u, 0, 1) ** tail, 0.45)
    L.stroke(np.column_stack([P, W]))


def ear(Lg, Ls, base, tip, w, n=7, awn=0.35):
    """A wheat ear from base to tip: pairs of grains along a thin axis, a top grain and a few awns."""
    b, d, L, nrm, u = _frame(base, tip, 0)
    Ls.stroke(np.array([b, b + d * 0.96]), max(w * 0.14, 0.8))
    g = L / (n + 1) * 1.55
    for i in range(n):
        t = 0.08 + 0.84 * i / max(n - 1, 1)
        k = 1.0 - 0.35 * t
        p = b + d * t
        for side in (-1, 1):
            q = p + nrm * side * w * 0.12
            Lg.leaf(q, q + u * g * 0.9 * k + nrm * side * w * 0.42 * k, w * 0.52 * k, shape=0.45)
    Lg.leaf(b + d * 0.86, b + d * 1.02, w * 0.5, shape=0.4)
    if awn:
        for side in (-1, 0, 1):
            p0 = b + d * (0.8 + 0.08 * abs(side))
            Ls.stroke(np.array([p0, p0 + u * L * awn + nrm * side * L * awn * 0.18]), 0.9, taper=(0, 6))


def feather(Lf, Ld, base, tip, w, bend=0.0, barbs=9):
    """A feather-like leaf: golden blade, darker shaft and slanted barbs."""
    Lf.leaf(base, tip, w, bend, shape=0.5)
    b, d, L, nrm, u = _frame(base, tip, bend)
    s = np.linspace(0.02, 0.97, 60)
    mid = _mid(base, tip, bend, s)
    Ld.stroke(mid, (1.6, 1.3, 0.5))
    for i in range(barbs):
        t = 0.14 + 0.7 * i / max(barbs - 1, 1)
        p = _mid(base, tip, bend, np.array([t]))[0]
        hw = w / 2 * (np.sin(np.pi / 2 * t / 0.5) if t < 0.5 else np.cos(np.pi / 2 * (t - 0.5) / 0.5)) ** 0.9
        for side in (-1, 1):
            q = p + nrm * side * hw * 0.85 + u * hw * 0.9
            Ld.stroke(np.array([p + nrm * side * 0.8, q]), 0.9, taper=(0, hw * 0.6))


def dots(L, x, y, r=4.0, n=3, rot=20.0):
    """A small cluster of dots (the pale blue-grey marks of 15Ф)."""
    for k in range(n):
        a = math.radians(rot + 360.0 * k / n)
        L.dot(x + r * 1.15 * math.cos(a), y + r * 1.15 * math.sin(a), r * (0.9 if k else 1.05))


def mark(L, x, y, length, w, rot):
    """A tiny leaf mark (6Ф)."""
    a = math.radians(rot)
    dx, dy = math.cos(a) * length / 2, math.sin(a) * length / 2
    L.leaf((x - dx, y - dy), (x + dx, y + dy), w, shape=0.5)


# ------------------------------------------------------------------------------------------------ 3П / 3Х
# the inverted tulip triangle (top edge 1811, tip 1255); centre line x ~ 390
@art(G + "3p", "fit", "3П (лилия)", (232.8, 1200, 546.3, 1811), photos=_ph("3p"), shape=("laminated-3p", G + "3p"))
def lam_3p(a):
    """One bright red lily near the top (6 pointed petals, dark red veins, orange stamens), a thin golden stem down
    the middle of the triangle with two small green leaves."""
    cx, cy = 393.0, 1703.0
    stem = a.layer("#c8a14f", 1.0, 0.55, 0.25)
    stem.curve([[390, 1672], [387, 1625], [381, 1588], [372, 1530], [366, 1478], [366, 1450], [369, 1432]], 2.6,
               taper=(0, 40))
    stem.curve([[381, 1590], [390, 1596]], 2.0)
    stem.curve([[367, 1480], [362, 1474]], 1.8)
    leaf = a.layer("#2d9a3b", 1.0, 0.5)
    leaf.leaf((383, 1590), (428, 1640), 17, bend=0.08, shape=0.45)
    leaf.leaf((364, 1470), (340, 1528), 14, bend=-0.10, shape=0.45)
    lv = a.layer("#1b6a28", 1.0, 0.5)
    vein(lv, (383, 1590), (428, 1640), 1.6, 0.08)
    vein(lv, (364, 1470), (340, 1528), 1.4, -0.10)
    # petals (base near the centre, tip, width, bend): broad, fleshy, slightly recurved
    petals = [((cx - 6, cy + 8), (334, 1785), 56, -0.10),      # upper left
              ((cx + 6, cy + 8), (448, 1787), 54, 0.10),       # upper right
              ((cx - 8, cy + 2), (268, 1727), 52, 0.12),       # left
              ((cx + 8, cy), (491, 1709), 52, -0.12),          # right
              ((cx + 6, cy - 6), (465, 1664), 46, 0.10),       # lower right
              ((cx - 4, cy - 8), (346, 1629), 52, 0.08)]       # lower left
    inner = []
    for ang, ln in ((91, 64), (148, 58), (-76, 52), (-158, 50), (30, 50)):
        t = math.radians(ang)
        inner.append(((cx, cy), (cx + ln * math.cos(t), cy + ln * math.sin(t)), 40, 0.0))
    red = a.layer("#e3161c", 1.0, 0.5)
    for b, t, w, bd in inner + petals:
        red.leaf(b, t, w, bd, shape=0.48)
    red.dot(cx, cy, 24)
    # darker throat, midribs and side veins
    dk = a.layer("#a10c13", 1.0, 0.5)
    for b, t, w, bd in inner:
        vein(dk, b, t, 2.2, bd, 0.3, 0.85)
    for b, t, w, bd in petals:
        dk.leaf(b, _mid(b, t, bd, np.array([0.38]))[0], w * 0.3, bd * 0.4, shape=0.3)
        vein(dk, b, t, 3.0, bd, 0.08, 0.84)
        B, D, Ln, N, U = _frame(b, t, bd)
        for side in (-1, 1):
            for f0, f1, k in ((0.2, 0.66, 0.22), (0.34, 0.8, 0.12)):
                p0 = _mid(b, t, bd, np.array([f0]))[0] + N * side * w * 0.05
                p1 = _mid(b, t, bd, np.array([f1]))[0] + N * side * w * k
                dk.curve([p0, (p0 + p1) / 2 + N * side * w * 0.08, p1], 1.4, taper=(2, 12))
    dk.dot(cx, cy, 10)
    # stamens: orange filaments to the upper right with dark anthers
    st = a.layer("#f2a324", 1.0, 0.55)
    ends = [(436, 1760), (451, 1747), (460, 1731), (428, 1771), (463, 1716)]
    for ex, ey in ends:
        st.curve([[cx + 4, cy + 4], [(cx + ex) / 2 + 2, (cy + ey) / 2 - 6], [ex, ey]], 1.7, taper=(0, 8))
    an = a.layer("#7a2a0a", 1.0, 0.5)
    for ex, ey in ends:
        an.ellipse(ex, ey, 4.2, 2.2, rot=35)


GREY_DAMASK = "#a19f9a"


def _damask_leaf(L, base, tip, w, bend=0.0):
    L.leaf(base, tip, w * 1.2, bend, shape=0.4)


def _scroll(L, cx, cy, r, a0, a1, w):
    """A C-scroll: spiral from radius r at a0 to r*0.35 at a1 (deg), with a round end."""
    w *= 1.3
    L.spiral(cx, cy, r, r * 0.35, a0, a1, w, taper=(4, 0))
    ang = math.radians(a1)
    L.dot(cx + r * 0.35 * math.cos(ang), cy + r * 0.35 * math.sin(ang), w * 0.9)


@art(G + "3x", "fit", "3Х (дамаск)", (232.8, 1200, 546.3, 1811), photos=_ph("3h"), shape=("laminated-3x", G + "3x"))
def lam_3x(a):
    """Light grey damask (lace-like baroque) printed on white satin, symmetric about the triangle's centre line: a
    lace edging under the top edge, a big palmette with scrolls filling the top, then a chain of smaller fleurons
    down the middle to ~1450."""
    cx = 390.0
    L = a.layer(GREY_DAMASK, 0.95, 0.45)
    Wc = a.layer(SATIN["color"], SATIN["alpha"], SATIN["smooth"])      # cut-outs (lace holes) in the grey
    with a.mirror_x(cx):
        # lace edging under the top edge: a thin rail with small scrolls and leaflets hanging from it
        L.curve([[cx, 1782], [cx + 60, 1780], [cx + 110, 1777], [cx + 142, 1774]], 2.0)
        for i, x in enumerate(np.arange(cx + 10, cx + 140, 16)):
            y = 1781 - (x - cx) * 0.05
            _scroll(L, x, y - 7, 5.5, 90, 400 if i % 2 else 380, 1.9)
            _damask_leaf(L, (x + 5, y - 9), (x + 11, y - 19), 6.0, 0.1)
        # central palmette: fan of outlined leaves from (cx, 1688) under a crown fleuron
        for ang, ln, wd in ((90, 64, 15), (66, 66, 14), (44, 60, 13), (24, 52, 12), (6, 40, 10)):
            t = math.radians(ang)
            b = (cx + 4 * math.cos(t), 1688 + 4 * math.sin(t))
            tp = (cx + ln * math.cos(t), 1688 + ln * math.sin(t))
            _damask_leaf(L, b, tp, wd, 0.08 if ang < 90 else 0)
            Wc.leaf(_mid(b, tp, 0.08 if ang < 90 else 0, np.array([0.3]))[0],
                    _mid(b, tp, 0.08 if ang < 90 else 0, np.array([0.85]))[0], wd * 0.38, 0.05)
        L.ellipse(cx, 1688, 18, 13)
        Wc.ellipse(cx, 1688, 9, 6)
        _damask_leaf(L, (cx, 1752), (cx + 16, 1770), 7, -0.2)
        L.dot(cx, 1760, 4)
        # acanthus branches sweeping out and up into the top corners, leaflets along them
        br1 = spline([[cx + 14, 1650], [cx + 50, 1660], [cx + 84, 1682], [cx + 108, 1714], [cx + 118, 1744],
                      [cx + 110, 1758], [cx + 98, 1752], [cx + 100, 1738]])
        L.stroke(br1, (4.2, 3.4, 2.0), taper=(6, 0))
        br2 = spline([[cx + 26, 1702], [cx + 48, 1716], [cx + 66, 1740], [cx + 70, 1760], [cx + 60, 1764],
                      [cx + 55, 1754]])
        L.stroke(br2, (3.4, 2.0), taper=(6, 0))
        br3 = spline([[cx + 14, 1612], [cx + 44, 1598], [cx + 72, 1604], [cx + 88, 1622], [cx + 84, 1638],
                      [cx + 72, 1634], [cx + 74, 1624]])
        L.stroke(br3, (3.6, 2.0), taper=(6, 0))
        for P, step, sz in ((br1, 11, 9.0), (br2, 10, 7.0), (br3, 11, 7.5)):
            sL = arclen(P)
            for j, d in enumerate(np.arange(10, sL[-1] - 16, step)):
                i = int(np.searchsorted(sL, d))
                p = P[i]
                tg = P[min(i + 3, len(P) - 1)] - P[max(i - 3, 0)]
                tg = tg / max(np.hypot(*tg), 1e-9)
                nr = np.array([-tg[1], tg[0]]) * (1 if j % 2 else -1)
                _damask_leaf(L, p, p + nr * sz + tg * sz * 0.5, sz * 0.5, 0.15)
        # C-scrolls and dots filling the spaces
        _scroll(L, cx + 64, 1628, 12, 30, 340, 2.4)
        _scroll(L, cx + 36, 1740, 9, 200, 510, 2.0)
        _scroll(L, cx + 92, 1662, 10, 200, 520, 2.0)
        _scroll(L, cx + 128, 1758, 7, 0, 300, 1.6)
        # sprigs hanging off the big branch (a short stalk, a leaf and a curl)
        for (bx, by), (tx, ty) in (((cx + 101, 1700), (cx + 124, 1690)), ((cx + 84, 1682), (cx + 100, 1656)),
                                   ((cx + 62, 1666), (cx + 70, 1646)), ((cx + 112, 1730), (cx + 136, 1728))):
            L.curve([[bx, by], [(bx + tx) / 2, (by + ty) / 2 + 3], [tx, ty]], 1.6)
            _damask_leaf(L, (tx, ty), (tx + (tx - bx) * 0.6, ty + (ty - by) * 0.6 - 4), 8, 0.15)
            _scroll(L, (bx + tx) / 2 + 2, (by + ty) / 2 - 6, 4.5, 60, 360, 1.4)
        for x, y, r in ((cx + 44, 1722, 2.8), (cx + 22, 1760, 2.4), (cx + 76, 1712, 2.4), (cx + 50, 1604, 2.2),
                        (cx + 80, 1640, 2.2), (cx + 118, 1716, 2.0), (cx + 60, 1770, 2.0), (cx + 88, 1766, 2.0)):
            L.dot(x, y, r)
        # the chain of fleurons down the middle
        L.curve([[cx, 1650], [cx, 1600], [cx, 1545], [cx, 1500], [cx, 1466]], 2.4, taper=(0, 10))
        for yc, wd, ht in ((1620, 46, 30), (1573, 40, 27), (1527, 32, 23), (1488, 23, 18)):
            L.diamond(cx, yc, 15 * wd / 46, ht * 0.95)
            Wc.diamond(cx, yc, 5 * wd / 46, ht * 0.4)
            _damask_leaf(L, (cx + 5, yc), (cx + wd, yc + ht * 0.2), ht * 0.42, 0.2)
            Wc.leaf((cx + wd * 0.3, yc + ht * 0.05), (cx + wd * 0.8, yc + ht * 0.17), ht * 0.14, 0.2)
            _damask_leaf(L, (cx + 3, yc + 4), (cx + wd * 0.55, yc + ht * 0.66), ht * 0.3, -0.1)
            _damask_leaf(L, (cx + 3, yc - 4), (cx + wd * 0.5, yc - ht * 0.58), ht * 0.26, 0.1)
            L.dot(cx + wd * 0.98, yc - ht * 0.3, 2.2)
            _scroll(L, cx + wd * 0.75, yc - ht * 0.72, 4.5, 90, 380, 1.4)
        L.dot(cx, 1456, 3.6)
        _damask_leaf(L, (cx, 1598), (cx, 1644), 11)
        Wc.leaf((cx, 1608), (cx, 1636), 4)


# ------------------------------------------------------------------------------------------------ 6П / 6Ф
# the tall wavy pane (x 131-350, y 178-1826); its centre wanders 216 (y 700) .. 263 (y 1350)
@art(G + "6p", "fit", "6П (красные лепестки)", (131.0, 177.5, 349.6, 1826.1), photos=_ph("6p"),
     shape=("laminated-6p", G + "6p"))
def lam_6p(a):
    """Thin golden-beige curling tendrils along the pane with red paisley petals on them: small ones spread up and
    down, two big ones at mid-height (~1000), a big tendril loop at the left above them, loops around some petals."""
    pn = Pane("laminated-6p", G + "6p")
    K = 1.3

    def Wd(pts):
        return pn.widen(pts, K)

    T = a.layer("#d0ae76", 1.0, 0.5, 0.15)
    w = 2.3
    # the main vine, top to bottom
    T.curve(Wd([[246, 1765], [238, 1700], [226, 1630], [214, 1560], [212, 1500], [228, 1440], [246, 1400],
                [262, 1340], [266, 1280], [255, 1220], [262, 1160], [278, 1110], [276, 1060], [268, 1010],
                [252, 960], [232, 900], [226, 840], [238, 780], [252, 720], [248, 660], [232, 610], [226, 560],
                [232, 490], [228, 430], [214, 380], [210, 320], [220, 260], [212, 212]]), w, taper=(20, 30))

    def spi(cx, cy, r0, r1, a0, a1, ww, taper):
        x, y = pn.pt(cx, cy, K)
        T.spiral(x, y, r0 * 1.12, r1 * 1.12, a0, a1, ww, taper=taper)

    # tendrils with curls (branch points on the vine)
    for pts in ([[214, 1560], [236, 1600], [250, 1632], [252, 1650]], [[212, 1500], [232, 1478], [250, 1468]],
                [[228, 1440], [214, 1420], [212, 1398]], [[276, 1060], [262, 1045]], [[252, 960], [220, 972],
                                                                                           [200, 968]],
                [[232, 610], [242, 628], [254, 640]], [[226, 560], [236, 575], [242, 590]],
                [[232, 490], [245, 510], [246, 522]], [[210, 320], [222, 335]], [[220, 260], [206, 248]],
                [[238, 1700], [252, 1716], [262, 1718]], [[262, 1340], [250, 1330], [240, 1334]],
                [[266, 1280], [280, 1300], [282, 1318]]):
        T.curve(Wd(pts), w * 0.8, taper=(0, 8))
    spi(232, 1216, 26, 30, 250, 575, w * 0.8, (10, 10))          # loop around petal 4
    spi(222, 1110, 56, 8, 20, 400, w * 0.9, (8, 20))              # the big loop at left
    spi(240, 797, 22, 26, 60, 370, w * 0.8, (10, 10))             # loop around petal 7
    spi(242, 642, 13, 4, 0, 330, w * 0.8, (0, 8))                 # small curls
    spi(236, 360, 18, 5, 180, 470, w * 0.8, (0, 8))
    R = a.layer("#df2a20", 1.0, 0.5)
    # (head, tail points..., head width)
    petals = [
        ([[242, 1668], [254, 1680], [258, 1698], [252, 1712]], 22),
        ([[256, 1606], [262, 1624], [258, 1640]], 20),
        ([[262, 1455], [256, 1474], [250, 1490]], 24),
        ([[226, 1388], [240, 1374], [256, 1372], [262, 1380]], 24),
        ([[276, 1318], [284, 1334], [282, 1348]], 18),
        ([[232, 1214], [236, 1193], [230, 1181]], 20),
        ([[250, 1050], [270, 1044], [282, 1030], [280, 1016], [272, 1014]], 36),
        ([[244, 972], [224, 966], [206, 970], [196, 982], [202, 990]], 36),
        ([[238, 797], [241, 777], [236, 768]], 20),
        ([[212, 552], [226, 570], [238, 582]], 24),
        ([[226, 340], [240, 350], [250, 366]], 22),
        ([[210, 245], [218, 262], [222, 276]], 18),
    ]
    petals = [(Wd(pts), wd) for pts, wd in petals]
    for pts, wd in petals:
        paisley(R, pts, wd)
    # each petal's tail tied to the vine by a short tendril
    vine = T.items[0]["stroke"][:, :2]
    for pts, wd in petals:
        head, tip = np.array(pts[0], np.float64), np.array(pts[-1], np.float64)
        dh, dt = np.hypot(*(vine - head).T), np.hypot(*(vine - tip).T)
        if dt.min() <= dh.min():
            i = int(np.argmin(dt))
            end = tip
        else:
            i = int(np.argmin(dh))
            u = (vine[i] - head) / max(dh[i], 1e-9)
            end = head + u * wd * 0.45
        dist = float(np.hypot(*(vine[i] - end)))
        if 3 < dist < 70:
            j = min(i + 12, len(vine) - 1)
            tg = vine[j] - vine[max(i - 12, 0)]
            tg = tg / max(np.hypot(*tg), 1e-9)
            m = (vine[i] + end) / 2 + tg * dist * 0.25
            T.curve([vine[i], m, end], w * 0.75)
    D = a.layer("#a3141c", 1.0, 0.5)
    for pts, wd in petals:
        (hx, hy), (tx, ty) = pts[0], pts[1]
        dx, dy = tx - hx, ty - hy
        n = math.hypot(dx, dy)
        ux, uy = dx / n, dy / n
        D.spiral(hx - ux * wd * 0.05, hy - uy * wd * 0.05, wd * 0.24, wd * 0.08,
                 math.degrees(math.atan2(uy, ux)) + 120, math.degrees(math.atan2(uy, ux)) + 420, 1.4)


SILVER = "#979ba0"


@art(G + "6f", "fit", "6Ф (серебристые линии)", (131.0, 177.5, 349.6, 1826.1), photos=_ph("6f"),
     shape=("laminated-6f", G + "6f"))
def lam_6f(a):
    """Two long thin silver-grey S-lines winding along the pane, meeting at mid-height, and four tiny grey leaf
    marks (top left, both sides at mid-height, bottom)."""
    pn = Pane("laminated-6f", G + "6f")
    K = 1.3
    L = a.layer(SILVER, 1.0, 0.55, 0.3)
    up = [[270, 1650], [274, 1590], [266, 1500], [240, 1425], [213, 1370], [199, 1300], [200, 1212], [211, 1130],
          [232, 1072], [258, 1040], [276, 1024], [284, 1030]]
    lo = [[196, 1036], [212, 1008], [236, 980], [258, 945], [276, 880], [283, 798], [275, 716], [254, 641],
          [229, 575], [212, 509], [208, 443], [219, 395], [236, 378]]
    L.curve(pn.widen(up, K), (1.4, 4.6, 5.4, 4.8, 1.8), taper=(30, 20))
    L.curve(pn.widen(lo, K), (1.6, 4.8, 5.4, 4.8, 1.8), taper=(20, 30))
    # hairline companions (the double-line look of the print)
    L.curve(pn.widen([[262, 1600], [259, 1520], [240, 1455], [218, 1405]], K), 1.3, taper=(20, 20))
    L.curve(pn.widen([[272, 862], [276, 790], [266, 712], [248, 655]], K), 1.3, taper=(20, 20))
    M = a.layer("#868b90", 1.0, 0.5, 0.2)
    for x, y, rot in ((219, 1621, 70), (174, 997, 60), (287, 1017, 115), (249, 374, 60)):
        mark(M, *pn.pt(x, y, K), 14, 7.5, rot)


# ------------------------------------------------------------------------------------------------ 8П / 8Ф
# two panes: upper (x 147-374, y 656-1880, pointed at the bottom), lower (x 117-358, y 182-1005)
ORANGE = "#f47a14"


@art(G + "8p", "fit", "8П (оранжевые листья)", (117.1, 182.0, 374.2, 1880.1), photos=_ph("8p"),
     shape=("laminated-8p", G + "8p"))
def lam_8p(a):
    """Bright orange flame-shaped leaves and buds on thin golden stems: a spray of two flames, two leaves and two
    berries in the upper pane, a small spray (flame, berry, leaf) in the lower one; pale thin grass lines below."""
    pale = a.layer("#dccfb6", 1.0, 0.5)
    for pts in ([[286, 1420], [272, 1300], [252, 1180], [236, 1060], [222, 960]],
                [[300, 1330], [292, 1200], [274, 1080], [252, 980], [232, 900]],
                [[250, 1230], [246, 1120], [236, 1010], [220, 920]],
                [[262, 740], [246, 640], [220, 530], [196, 430], [170, 330]],
                [[284, 700], [266, 590], [240, 480], [210, 380]]):
        pale.curve(pts, 1.6, taper=(30, 40))
    S = a.layer("#c9a04c", 1.0, 0.55, 0.25)
    S.curve([[282, 1752], [290, 1700], [296, 1640], [298, 1580], [294, 1520], [292, 1470], [284, 1410],
             [272, 1340], [262, 1280], [258, 1256]], 2.4)
    S.curve([[258, 1256], [252, 1200], [244, 1130], [236, 1060]], 2.0, taper=(0, 60))
    S.curve([[258, 1660], [274, 1640], [294, 1628]], 2.0)
    S.curve([[300, 1706], [296, 1690]], 1.8)
    S.curve([[298, 1470], [294, 1478]], 1.8)
    S.curve([[290, 1446], [291, 1462]], 1.8)
    S.curve([[283, 768], [280, 740], [272, 712], [262, 690], [248, 650], [234, 612], [220, 560], [206, 500]],
            2.2, taper=(0, 60))
    S.curve([[275, 726], [270, 715]], 1.8)
    S.curve([[225, 614], [234, 612]], 1.8)
    O = a.layer(ORANGE, 1.0, 0.5)
    parts = [((282, 1750), (278, 1844), 48, 0.04), ((258, 1658), (222, 1737), 28, -0.12),
             ((298, 1469), (220, 1537), 44, 0.10), ((258, 1254), (312, 1368), 42, -0.08),
             ((283, 767), (283, 846), 32, 0.05), ((225, 613), (234, 686), 28, -0.08)]
    for b, t, w, bd in parts:
        flame(O, b, t, w, bd)
    for x, y, r in ((300, 1708, 9), (292, 1442, 8.5), (276, 724, 10)):
        O.dot(x, y, r)
    D = a.layer("#d2530a", 1.0, 0.5)
    for b, t, w, bd in parts:
        vein(D, b, t, max(w * 0.1, 2.2), bd, 0.12, 0.8)
    H = a.layer("#fbb055", 1.0, 0.5)
    for b, t, w, bd in parts:
        B, Dd, Ln, N, U = _frame(b, t, bd)
        p = _mid(b, t, bd, np.linspace(0.2, 0.55, 12)) + N * w * 0.2
        H.stroke(p, w * 0.08, taper=(4, 8))


@art(G + "8f", "fit", "8Ф (колоски)", (117.1, 182.0, 374.2, 1880.1), photos=_ph("8f"),
     shape=("laminated-8f", G + "8f"))
def lam_8f(a):
    """Thin grey curved grass stems following the panes with golden-ochre wheat ears: two ears in the upper pane,
    one in the lower."""
    L = a.layer("#989b9f", 1.0, 0.55, 0.25)
    for pts, w in (([[218, 1800], [232, 1735], [241, 1654], [238, 1538], [233, 1423], [230, 1300], [232, 1190],
                     [228, 1080], [218, 980], [205, 890], [192, 820]], 3.4),
                   ([[252, 1764], [260, 1680], [262, 1600], [255, 1520], [246, 1440], [242, 1350], [241, 1250],
                     [242, 1150], [238, 1050], [228, 960]], 2.6),
                   ([[274, 1588], [262, 1540], [252, 1480], [248, 1400], [250, 1300], [252, 1200], [252, 1120]],
                    2.2),
                   ([[262, 1381], [258, 1320], [262, 1250], [266, 1170], [262, 1080], [250, 1000]], 2.2),
                   ([[322, 860], [300, 770], [276, 690], [252, 600], [228, 510], [205, 430], [180, 340],
                     [158, 270]], 3.0),
                   ([[233, 536], [226, 480], [212, 420], [192, 350], [172, 290]], 2.2),
                   ([[300, 840], [285, 760], [262, 680], [240, 600], [220, 520]], 1.8)):
        L.curve(pts, w * 1.25, taper=(40, 60))
    Gr = a.layer("#d09a2e", 1.0, 0.5, 0.1)
    Ax = a.layer("#b07a1e", 1.0, 0.5, 0.1)
    for b, t, w in (((274, 1586), (326, 1670), 21), ((262, 1379), (293, 1462), 20), ((233, 534), (263, 604), 19)):
        ear(Gr, Ax, b, t, w, n=6)


# ------------------------------------------------------------------------------------------------ 11Ф
@art(G + "11f", "fit", "11Ф (стебли с листьями)", (237.0, 180.1, 583.9, 1810.1), photos=_ph("11f"),
     shape=("laminated-11f", G + "11f"))
def lam_11f(a):
    """Two long wavy grey stems in the upper half (one from the top left, one joining it from the top right) with
    two small orange-gold leaves, and the same group turned 180 degrees in the lower half (the pane is point
    symmetric about its middle)."""
    S = a.layer("#9ca0a4", 1.0, 0.55, 0.25)
    Lo = a.layer("#8a4812", 1.0, 0.5)
    Lf = a.layer("#dd8a22", 1.0, 0.5, 0.1)
    Dk = a.layer("#9a5214", 1.0, 0.5)
    pn = Pane("laminated-11f", G + "11f")
    K = 1.2
    stem_a = [[308, 1748], [327, 1690], [333, 1621], [321, 1562], [297, 1496], [284, 1421], [292, 1362],
              [317, 1312], [350, 1262], [378, 1212], [391, 1154], [387, 1094]]
    stem_b = [[462, 1726], [430, 1688], [390, 1646], [356, 1604], [331, 1560], [312, 1520], [298, 1494]]
    leaves = [((366, 1700), (414, 1742), 16, 0.06), ((338, 1393), (398, 1424), 16, 0.06)]
    stem_a, stem_b = pn.widen(stem_a, K), pn.widen(stem_b, K)
    leaves = [(pn.pt(*b, K), pn.pt(*t, K), w, bd) for b, t, w, bd in leaves]
    for rot in (0, 180):
        with a.at(406, 997, rot):
            def loc(p):
                return [p[0] - 406, p[1] - 997]
            S.curve([loc(p) for p in stem_a], (1.6, 5.2, 5.4, 4.6, 1.4), taper=(25, 40))
            S.curve([loc(p) for p in stem_b], (1.4, 4.6, 3.8), taper=(30, 30))
            for b, t, w, bd in leaves:
                Lo.leaf(loc(b), loc(t), w, bd, shape=0.5)
                B, D, Ln, N, U = _frame(loc(b), loc(t), bd)
                Lf.leaf(np.add(loc(b), U * 3.5), np.subtract(loc(t), U * 3.5), w - 3.4, bd, shape=0.5)
                vein(Dk, loc(b), loc(t), 1.4, bd, 0.08, 0.9)


# ------------------------------------------------------------------------------------------------ 15Ф
# three panes: upper triangle (apex top-left, y 1088-1809), middle (apex at the handle side, y 843-1161), lower
# (apex bottom-left, y 217-915): the picture is symmetric about y ~ 1004
@art(G + "15f", "fit", "15Ф (золотые перья)", (132.7, 216.6, 327.9, 1809.1), photos=_ph("15f"),
     shape=("laminated-15f", G + "15f"))
def lam_15f(a):
    """Golden-ochre feather-like leaves with small pale blue-grey dots: two leaves in the upper pane, two in the
    middle one (a V from the apex) and two in the lower pane, the lower half a mirror of the upper."""
    F = a.layer("#cf962f", 1.0, 0.5, 0.15)
    D = a.layer("#92601a", 1.0, 0.5)
    B = a.layer("#a9b5c2", 1.0, 0.5)
    with a.mirror_y(1004):
        feather(F, D, (202, 1284), (160, 1388), 21, 0.06)
        feather(F, D, (229, 1214), (266, 1322), 21, -0.06)
        feather(F, D, (184, 1022), (272, 1082), 20, 0.05)
        dots(B, 231, 1390, 3.6)
    dots(B, 276, 1003, 3.6)


# ------------------------------------------------------------------------------------------------ 21Х-25Х
RECT = (271.2, 187.0, 534.0, 1812.3)
CX = 402.6


def _jewel_square(a, cx, cy, s):
    """A dark red square jewel in a gold frame (21Х)."""
    fr = a.layer("#c6a04a", 1.0, 0.7, 0.6)
    fr.rect(cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2)
    dk = a.layer("#4a0609", 1.0, 0.7)
    r = s / 2 - 5.5
    dk.rect(cx - r, cy - r, cx + r, cy + r)
    rd = a.layer("#8a1015", 1.0, 0.8)
    r2 = r - 3.5
    rd.fill([[cx - r2, cy - r2], [cx + r2, cy - r2], [cx + r2 - 3, cy + r2], [cx - r2, cy + r2]])
    hi = a.layer("#b3242a", 1.0, 0.85)
    hi.fill([[cx - r2 + 4, cy + r2 - 4], [cx + r2 - 6, cy + r2 - 4], [cx - r2 + 4, cy - r2 + 8]])


@art(G + "21x", "fit", "21Х (меандр)", RECT, photos=_ph("21h"), shape=("laminated-21x", G + "21x"))
def lam_21x(a):
    """A grey Greek-key (meander) band running vertically down the middle, and a small dark red square jewel in a
    gold frame above and below it."""
    L = a.layer("#a2a19d", 1.0, 0.5)
    W, lw = 58.0, 5.4
    x0, x1 = CX - W / 2, CX + W / 2
    top, bot, n = 1575.0, 433.0, 17
    P = (top - bot) / n
    ys = [top - k * P for k in range(n + 1)]
    path = [[x0, ys[0]]]
    for k in range(n):                                      # a serpentine: bar, side, bar, other side, ...
        xs = x1 if k % 2 == 0 else x0                       # the side joining bar k and bar k+1
        path += [[xs, ys[k]], [xs, ys[k + 1]], [x0 + x1 - xs, ys[k + 1]]]
    path = [p for i, p in enumerate(path) if i == 0 or p != path[i - 1]]
    L.stroke(np.array(path), lw)
    for k in range(n):
        xs = x1 if k % 2 == 0 else x0
        xo = x0 if xs == x1 else x1
        yb = ys[k + 1]
        L.stroke(np.array([[xo, yb], [xo, yb + 0.76 * P], [CX, yb + 0.76 * P], [CX, yb + 0.36 * P]]), lw)
    for cy in (1635.0, 369.0):
        _jewel_square(a, CX, cy, 54)


@art(G + "22x", "fit", "22Х (тюльпаны)", RECT, photos=_ph("22h"), shape=("laminated-22x", G + "22x"))
def lam_22x(a):
    """Three orange-red tulip buds (top, right of the upper third, left at mid-height) on long thin silver-grey
    intertwining stems, with a few outlined leaves."""
    S = a.layer("#a2a5a9", 1.0, 0.55, 0.3)
    stems = [
        [[387, 1621], [383, 1560], [379, 1480], [379, 1400], [386, 1320], [396, 1240], [405, 1150], [410, 1050],
         [405, 960], [397, 880], [392, 800], [396, 700], [410, 600], [420, 500], [419, 420], [408, 345],
         [398, 300]],
        [[429, 1371], [414, 1330], [393, 1290], [366, 1240], [346, 1178], [338, 1100], [341, 1030], [356, 960],
         [376, 900], [396, 830], [411, 760], [418, 690], [410, 620], [394, 560], [374, 500], [360, 430],
         [352, 380]],
        [[354, 879], [362, 840], [378, 790], [396, 742], [412, 700], [426, 640], [431, 560], [425, 480],
         [412, 400], [400, 330], [392, 280]],
        [[372, 1260], [360, 1180], [356, 1090], [364, 1000], [382, 920], [402, 850], [424, 760], [436, 660],
         [438, 580], [432, 500]],
    ]
    for i, pts in enumerate(stems):
        S.curve(pts, 3.4 if i < 3 else 2.4, taper=(0 if i < 3 else 40, 70))
    O = a.layer("#a2a5a9", 1.0, 0.55, 0.3)
    for b, t, w in (((372, 1566), (334, 1602), 17), ((432, 1300), (478, 1330), 17), ((346, 812), (298, 832), 17)):
        s_ = np.linspace(0, 1, 40)
        B, D, Ln, N, U = _frame(b, t, 0.1)
        mid = _mid(b, t, 0.1, s_)
        hw = w / 2 * np.sin(np.pi * s_) ** 0.9
        ring = np.vstack([mid + N * hw[:, None], (mid - N * hw[:, None])[::-1]])
        O.stroke(np.vstack([ring, ring[:1]]), 2.0)
        O.stroke(_mid(b, t, 0.1, np.linspace(0, 0.8, 20)), 1.3)
    T = a.layer("#cc4a1a", 1.0, 0.5)
    Tl = a.layer("#ec7a30", 1.0, 0.5)
    Dk = a.layer("#7e240e", 1.0, 0.5)
    tulips = [((387, 1620), [(-22, 84), (20, 104), (54, 60)]),
              ((429, 1371), [(10, 86), (46, 88), (74, 58)]),
              ((354, 879), [(-30, 98), (-60, 60), (16, 88)])]
    for (bx, by), tips in tulips:
        for dx, dy in tips:
            flame(T, (bx + dx * 0.08, by + dy * 0.08), (bx + dx, by + dy), 29, 0.0, cup=0.4, rb=0.7)
        for dx, dy in tips:
            b0, t0 = (bx + dx * 0.35, by + dy * 0.35), (bx + dx * 0.97, by + dy * 0.97)
            flame(Tl, b0, t0, 15, 0.0, cup=0.35, rb=0.6)
        for dx, dy in tips:
            vein(Dk, (bx + dx * 0.08, by + dy * 0.08), (bx + dx, by + dy), 2.8, 0.0, 0.02, 0.75)
        Dk.fill_curve([[bx - 13, by + 12], [bx, by - 2], [bx + 13, by + 12], [bx, by + 22]])


LEAD = "#6d706a"
BROWN = "#4c2518"
LIME = "#c4d13c"


def _jewel(a, cx, cy, hw, hh, lead=4.0):
    J = a.layer(LIME, 0.95, 0.85)
    J.diamond(cx, cy, 2 * hw, 2 * hh)
    Jd = a.layer("#9fae2a", 0.95, 0.85)
    Jd.fill([[cx, cy - hh * 0.8], [cx + hw * 0.8, cy], [cx, cy], [cx - hw * 0.4, cy - hh * 0.4]])
    Ld = a.layer(LEAD, 1.0, 0.6, 0.3)
    Ld.stroke(np.array([[cx, cy - hh], [cx + hw, cy], [cx, cy + hh], [cx - hw, cy], [cx, cy - hh]]), lead)


@art(G + "23x", "fit", "23Х (витраж)", RECT, photos=_ph("23h"), shape=("laminated-23x", G + "23x"))
def lam_23x(a):
    """Stained-glass look: grey-green lead lines (a frame, the vertical centre line, two horizontal lines above and
    two below the middle), lime-yellow diamond jewels on the crossings, dark brown scrolls with a tulip cup at the
    top and the bottom, and a medallion with a white four-petal flower in the middle."""
    Ld = a.layer(LEAD, 1.0, 0.6, 0.3)
    xl, xr, yt, yb = CX - 116.6, CX + 116.6, 1797.0, 203.0
    Ld.rect(xl, yb, xr, yt, w=5.0)
    Ld.stroke(np.array([[CX, yb], [CX, yt]]), 4.6)
    with a.mirror_y(1000.0):
        for y in (1487.0, 1175.0):
            Ld.stroke(np.array([[xl, y], [xr, y]]), 4.6)
    W = a.layer("#fbfaf7", 0.97, 0.5)
    B = a.layer(BROWN, 1.0, 0.6)
    L2 = a.layer(LEAD, 1.0, 0.6, 0.3)
    with a.mirror_y(1000.0):
        # --- top ornament: jewel in a lead diamond that ends in a tulip cup, two brown curls, jewel on the line
        cup = [[CX, 1680], [CX + 40, 1631], [CX + 44, 1600], [CX + 34, 1560], [CX + 14, 1532], [CX, 1514],
               [CX - 14, 1532], [CX - 34, 1560], [CX - 44, 1600], [CX - 40, 1631]]
        W.fill_curve(cup)
        with a.mirror_x(CX):
            B.fill_curve([[CX + 3, 1604], [CX + 18, 1600], [CX + 25, 1582], [CX + 20, 1558], [CX + 8, 1544],
                          [CX + 3, 1560]])
            # curl: ball at the outside, tail sweeping into the diamond's side vertex
            paisley(B, [[CX + 75, 1616], [CX + 70, 1604], [CX + 58, 1602], [CX + 48, 1616], [CX + 40, 1630]], 24,
                    tail=1.0)
        L2.curve(cup, 3.6, closed=True)
        with a.mirror_x(CX):
            L2.curve([[CX + 40, 1631], [CX + 22, 1606], [CX + 4, 1596]], 2.6)
            L2.curve([[CX + 44, 1600], [CX + 26, 1566], [CX + 6, 1548]], 2.2)
        L2.stroke(np.array([[CX, 1514], [CX, 1504]]), 4.0)
        # --- medallion (upper half): jewel on the line, big curls, a brown pointed drop over the flower
        frame = [[CX, 1158], [CX + 22, 1128], [CX + 40, 1092], [CX + 42, 1058], [CX + 34, 1034], [CX + 20, 1026],
                 [CX, 1030], [CX - 20, 1026], [CX - 34, 1034], [CX - 42, 1058], [CX - 40, 1092], [CX - 22, 1128]]
        W.fill_curve(frame)
        B.fill_curve([[CX, 1100], [CX + 14, 1080], [CX + 21, 1058], [CX + 16, 1042], [CX, 1036], [CX - 16, 1042],
                      [CX - 21, 1058], [CX - 14, 1080]])
        with a.mirror_x(CX):
            paisley(B, [[CX + 54, 1126], [CX + 48, 1142], [CX + 32, 1148], [CX + 16, 1138], [CX + 8, 1118]], 30,
                    tail=1.0)
        L2.curve(frame, 3.2, closed=True)
        with a.mirror_x(CX):
            L2.curve([[CX + 4, 1148], [CX + 20, 1112], [CX + 28, 1076], [CX + 26, 1048], [CX + 14, 1034]], 2.2)
    # the four-petal flower in the middle: white rings on a brown disc
    Bf = a.layer(BROWN, 1.0, 0.6)
    Bf.dot(CX, 1000, 33)
    Wf = a.layer("#fbfaf7", 0.97, 0.5)
    for dx, dy in ((0, 16), (0, -16), (16, 0), (-16, 0)):
        Wf.dot(CX + dx, 1000 + dy, 11.5)
    Bc = a.layer(BROWN, 1.0, 0.6)
    for dx, dy in ((0, 16), (0, -16), (16, 0), (-16, 0)):
        Bc.dot(CX + dx * 1.12, 1000 + dy * 1.12, 4.8)
    Bc.dot(CX, 1000, 6.5)
    Wc = a.layer("#fbfaf7", 0.97, 0.5)
    Wc.dot(CX, 1000, 3.2)
    L3 = a.layer(LEAD, 1.0, 0.6, 0.3)
    L3.ellipse(CX, 1000, 34.5, 34.5, w=2.8)
    with a.mirror_y(1000.0):
        _jewel(a, CX, 1630.0, 23, 29)
        _jewel(a, CX, 1484.0, 20, 21)
        _jewel(a, CX, 1180.0, 17, 19)


FILIGREE = "#737372"


def _fan(Lo, Li, calyx, dirs, lengths, width, bend=0.12):
    """A lily-like fan of lance petals from the calyx (outlined: dark petal, pale inside)."""
    cx, cy = calyx
    for ang, ln in zip(dirs, lengths):
        t = math.radians(ang)
        tip = (cx + ln * math.cos(t), cy + ln * math.sin(t))
        Lo.leaf((cx, cy), tip, width, bend, shape=0.55)
        base2 = (cx + 0.2 * ln * math.cos(t), cy + 0.2 * ln * math.sin(t))
        tip2 = (cx + 0.86 * ln * math.cos(t), cy + 0.86 * ln * math.sin(t))
        Li.leaf(base2, tip2, width * 0.52, bend, shape=0.55)


@art(G + "24x", "fit", "24Х (филигрань)", RECT, photos=_ph("24h"), shape=("laminated-24x", G + "24x"))
def lam_24x(a):
    """A dark grey filigree acanthus vine winding down the pane (period ~413 mm: a lily fan on the left crest, one on
    the right crest, curls in the bays), small beige rectangular medallions in the right bays, and two thin grey
    vertical lines near the sides."""
    Ln = a.layer("#8f8f8c", 1.0, 0.55, 0.2)
    for x in (320.0, 483.0):
        Ln.stroke(np.array([[x, 196], [x, 1803]]), 6.4)
    V = a.layer(FILIGREE, 1.0, 0.55, 0.2)
    Vi = a.layer("#d9d7d2", 0.95, 0.5)
    Vd = a.layer("#4f4f4e", 1.0, 0.55, 0.2)
    Pm = 413.0
    # the vine: x = 398 - 48 cos(2 pi (y - 1636) / P)  (left crests at 1636 - kP, right ones at 1429 - kP)
    ys = np.linspace(1700, 196, 700)
    xs = 398 - 48 * np.cos(2 * np.pi * (ys - 1636) / Pm)
    V.stroke(np.column_stack([xs, ys]), 4.4, taper=(40, 20))
    Md = a.layer("#d6ceb2", 1.0, 0.5)
    Mi = a.layer("#a9a88f", 1.0, 0.5)
    for k in range(4):
        dy = -k * Pm
        # left fan (opens up and to the right) and right fan (opens up and to the left)
        _fan(V, Vi, (371, 1690 + dy), (95, 72, 52, 34, 14, 128), (104, 88, 78, 70, 58, 48), 13)
        _fan(V, Vi, (437, 1474 + dy), (100, 122, 145, 165, 186, 60), (70, 84, 90, 88, 76, 46), 13, -0.12)
        for cx_, cy_ in ((371, 1690 + dy), (437, 1474 + dy)):
            Vd.ellipse(cx_, cy_, 13, 8, rot=-50 if cx_ < 400 else 50)
        # curls in the bays
        V.spiral(376, 1625 + dy, 22, 5, 180, 520, 3.0, taper=(0, 6))
        V.spiral(422, 1427 + dy, 22, 5, 0, -340, 3.0, taper=(0, 6))
        # little tendrils / leaf marks
        V.curve([[430, 1585 + dy], [418, 1578 + dy], [412, 1568 + dy]], 2.4, taper=(0, 6))
        V.leaf((408, 1548 + dy), (418, 1592 + dy), 6, 0.1)
        V.curve([[367, 1510 + dy], [360, 1520 + dy], [362, 1532 + dy]], 2.2, taper=(0, 6))
        # medallion and the thin arch around it
        V.curve([[390, 1690 + dy], [428, 1692 + dy], [448, 1672 + dy], [452, 1640 + dy], [446, 1612 + dy]], 2.0,
                taper=(0, 10))
        Md.rect(406, 1608 + dy, 437, 1671 + dy)
        Mi.rect(414, 1617 + dy, 429, 1662 + dy)
        Vd.rect(406, 1608 + dy, 437, 1671 + dy, w=1.6)


@art(G + "25x", "fit", "25Х (белые волны)", RECT, photos=_ph("25h"), shape=("laminated-25x", G + "25x"))
def lam_25x(a):
    """White-on-white: rows of short frosted wavy ribbons across the whole pane (brighter white print on the satin,
    with a faint shadow line under each), small gold-brown square jewels (a pair) near the top and the bottom and an
    amber leaf in the middle."""
    rng = np.random.default_rng(25)
    Bg = a.layer("#e6e3de", 0.86, 0.45)
    Bg.rect(*RECT)
    Wt = a.layer("#fefefd", 0.985, 0.5)
    xl, xr = 281.0, 524.0
    keep = [(CX, 1680, 30, 18), (CX, 352, 30, 18), (398, 1054, 28, 16)]
    y = 1802.0
    while y > 196:
        x = xl + rng.uniform(-60, 10)
        wd = rng.uniform(13.0, 15.0)
        while x < xr:
            ln = rng.uniform(70, 210)
            x1 = min(x + ln, xr + 30)
            if x1 - x > 16:
                xx = np.linspace(max(x, xl - 14), x1, 60)
                ph = rng.uniform(0, 2 * np.pi)
                yy = y + 2.4 * np.sin(2 * np.pi * xx / rng.uniform(70, 110) + ph)
                ok = np.ones(len(xx), bool)
                for kx, ky, hx, hy in keep:
                    ok &= ~((np.abs(xx - kx) < hx) & (np.abs(yy - ky) < hy))
                segs = np.split(np.arange(len(xx)), np.where(np.diff(ok.astype(int)) != 0)[0] + 1)
                for sg in segs:
                    if len(sg) > 3 and ok[sg[0]]:
                        Wt.stroke(np.column_stack([xx[sg], yy[sg]]), wd, taper=(3, 3))
            x = x1 + rng.uniform(5, 9)
        y -= rng.uniform(19.0, 21.0)
    J = a.layer("#5a3208", 1.0, 0.7, 0.3)
    Jg = a.layer("#e3a42a", 1.0, 0.85, 0.4)
    Jh = a.layer("#f7d27a", 1.0, 0.9, 0.4)
    for cy in (1680.0, 352.0):
        for dx in (-10.5, 10.5):
            J.rect(CX + dx - 9.5, cy - 9.5, CX + dx + 9.5, cy + 9.5)
            Jg.rect(CX + dx - 6.5, cy - 6.5, CX + dx + 6.5, cy + 6.5)
            Jh.dot(CX + dx - 2.5, cy + 2.5, 2.4)
    Am = a.layer("#b8621a", 1.0, 0.7, 0.2)
    Ad = a.layer("#5e2c0c", 1.0, 0.7, 0.2)
    Am.leaf((383, 1064), (414, 1043), 13, 0.08, shape=0.45)
    vein(Ad, (383, 1064), (414, 1043), 1.8, 0.08, 0.0, 0.9)
