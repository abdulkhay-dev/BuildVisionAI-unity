from h1lib import *
# XY-SL-CIX ozone bathtub: white tub with a thick flat rounded rim, the body below bulging and tapering to a rounded
# bottom on 4 short white legs, a crescent recess line on the front, a pale lilac wavy band on the front left, chrome
# valves + spout on the left (head) end, a black power box with a cable at the front bottom.
d = D("xy-sl-cix", [1960, 750, 850], {
    "shell": "gloss#f8f8f9", "inner": "gloss#eff2f4", "band": "gloss#d8c8d8", "seam": "plastic#e4e6ea",
    "dark": "black#1f2124"})
CX, CZ = 980, 375
S = [(130, 1700, 520, 150), (170, 1800, 610, 170), (250, 1870, 690, 175), (600, 1920, 730, 180), (770, 1920, 730, 180)]
d.loft("body", [sec(y, w, dd, r, CX, CZ) for y, w, dd, r in S], "shell", caps=False)
d.loft("bottom", [sec(118, 1660, 490, 140, CX, CZ), sec(132, 1702, 522, 150, CX, CZ)], "shell")
hole = rr(330, 100, 1870, 650, 150)
tub(d, "", None, hole, rr(0, 0, 1960, 750, 110), 760, 90, 400, rr(300, 80, 1880, 670, 150), rim_r=40)
d.slab("rim-seam", "top", ring(rr(18, 18, 1942, 732, 105), rr(300, 80, 1880, 670, 150)), [748, 762], "seam", r=4, soft=True)
def zf(y):  # front surface z at height y (flat part of the front)
    for (y0, _, d0, _), (y1, _, d1, _) in zip(S, S[1:]):
        if y0 <= y <= y1:
            return CZ + (d0 + (d1 - d0) * (y - y0) / (y1 - y0)) / 2
    return CZ + S[-1][2] / 2
# crescent recess line on the front (lower edge of the shallow recess)
pts = []
for k in range(15):
    t = k / 14
    x = 1860 - 1400 * t
    y = 745 - 370 * math.sin(math.pi / 2 * t) ** 0.8 + 40 * t ** 4
    pts.append([x, y, zf(y) + 3])
d.tube("recess", pts, 10, "seam", bend=150, soft=True)
# lilac wavy band wrapping the front-left corner (review 2026-10-02: it was a flat slab on the front only): horizontal
# slices of a thin strip that follows the body's rounded-corner section at each height, from s_l (on the end face) to
# s_r (on the front), arc length measured from the middle of the corner arc; both edges wave as in the photo.
def sect(y):
    for (y0, w0, d0, r0), (y1, w1, d1, r1) in zip(S, S[1:]):
        if y0 <= y <= y1:
            t = (y - y0) / (y1 - y0)
            return w0 + (w1 - w0) * t, d0 + (d1 - d0) * t, r0 + (r1 - r0) * t
    return S[-1][1:]
def perim(sv, w, dd, r, off):
    """Point on the section outline (offset outward by off) at arc length sv from the corner-arc middle (+ = front)."""
    cx, cz = CX - w / 2 + r, CZ + dd / 2 - r
    R = r + off
    half = math.pi / 4 * r
    if abs(sv) <= half:
        a = math.radians(135) - sv / r
        return (cx + R * math.cos(a), cz + R * math.sin(a))
    if sv > half:
        return (cx + (sv - half), CZ + dd / 2 + off)
    return (CX - w / 2 - off, cz - (-sv - half))
def wave(y, top, mid, bot):
    t = (y - 140) / (755 - 140)
    return bot + (mid - bot) * math.sin(math.pi * min(1, t / 0.6) / 2) if t < 0.6 else mid + (top - mid) * ((t - 0.6) / 0.4) ** 1.5
YS = [140 + 10 * k for k in range(12)] + [260 + 20 * k for k in range(25)] + [752]
for k, (y0, y1) in enumerate(zip(YS, YS[1:])):
    ym = (y0 + y1) / 2
    sa, sb = sect(y0), sect(y1)
    big = max(sa, sb, key=lambda v: v[0]); small = min(sa, sb, key=lambda v: v[0])
    sl, sr = wave(ym, -100, -170, -80), wave(ym, 330, 200, 240)
    n = 10
    outer = [perim(sl + (sr - sl) * i / n, *big, 2.5) for i in range(n + 1)]
    inner = [perim(sr - (sr - sl) * i / n, *small, -20) for i in range(n + 1)]
    d.slab(f"band{k}", "top", P(outer + inner), [y0, y1 + 0.5], "band", r=0, soft=True)
# short white legs
d.cyl("leg", [420, 0, 220], [420, 135, 220], 70, "shell", d2=90, copies=[[1200, 0, 0], [0, 0, 310], [1200, 0, 310]])
# black power box + cable at the front bottom
d.box("power", [700, 200, zf(245) - 30, 785, 290, zf(245) + 6], "dark", r=6)
d.tube("cable", [[730, 200, zf(200) - 10], [710, 60, zf(200) + 40], [630, 10, 820], [800, 10, 900], [910, 10, 780],
                 [770, 10, 740]], 12, "dark", bend=60, soft=True)
# left (head) end: valves and spout on the rim
T = 850
valve(d, "valve-b", 140, T - 4, 150, disc=110, lever=80, ang=60)
valve(d, "valve-f", 330, T - 4, 600, disc=110, lever=80, ang=120)
d.lathe("spout-base", [230, T - 4, 230], [[0, 0], [36, 0], [36, 10], [24, 20], [0, 20]], "chrome")
d.cyl("spout-col", [230, T + 10, 230], [230, T + 70, 230], 44, "chrome")
d.cyl("spout", [230, T + 60, 230], [470, T + 60, 230], 40, "chrome", d2=34)
d.save()
