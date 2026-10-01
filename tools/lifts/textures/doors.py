#!/usr/bin/env python3
"""Lift textures, family `doors`: the patterned landing doors of the GLZ / NBSL catalogue (p.23-24).

    python tools/lifts/textures/doors.py [--no-merge] [ids]          # ids like sl-7061

One fitted picture per door (metersPerTile [1, 1]): the hall-side face of the closed door, both leaves together,
u = left -> right as seen from the hall, v = bottom -> top; 440 x 1024 px for the ~0.9 x 2.1 m opening (the leaves
overlap the jambs by 25 mm, sampled with wrap: the outer 30 mm of every design is plain metal). The leaf joint is a
dark hairline at u = 0.5.

Etched mirror steel: the mask carries the look - mirror smoothness ~0.95, etched (frosted) areas 0.48 and a touch
lighter, metallic 1 everywhere; the etched areas are a hair recessed in the normal map. Colours (baked, not tinted):
stainless #d9d9d9, rose gold #d6a476, titanium gold #d2b262 (the reflectance colours of metals.md).
SL-8055 «цветной металл, бук»: a fitted beech picture (each leaf its own flitch) rather than the tiling
lift_woodmetal, so the two leaves read as two veneered panels like the catalogue photo.
"""
import argparse
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lift_kit as K                # noqa: E402

FAMILY = "doors"
SOURCE = "procedural:tools/lifts/textures/doors.py"
W_M, H_M = 0.9, 2.1
PW, PH = 440, 1024
MMX, MMY = W_M * 1000 / PW, H_M * 1000 / PH
STAINLESS, ROSE, TIGOLD = "#d9d9d9", "#d6a476", "#d2b262"


def canvas():
    return K.MCanvas(W_M, H_M, PW, PH, 4)


def mirror_x(pts):
    return [(W_M - x, y) for x, y in pts]


# ------------------------------------------------------------------------------------------------ designs
def d7061():
    """Mirror; round etched rosette over the joint in the upper third; two frosted stripes near the outer edges."""
    c = canvas()
    for x0, x1 in ((0.11, 0.18), (0.82, 0.89)):
        c.rect(x0 * W_M, 0, x1 * W_M, H_M)
    cx, cy, R = W_M / 2, H_M * (1 - 0.277), 0.233
    c.ring(cx, cy, R, 0.005)
    c.ring(cx, cy, R - 0.012, 0.003)
    c.circle(cx, cy, R - 0.03)
    # mirror drawing inside the frosted disk: six lobed petals, an eight-point star and a small centre
    for k in range(6):
        a = k * math.pi / 3 + math.pi / 2
        px, py = cx + 0.105 * math.cos(a), cy + 0.105 * math.sin(a)
        c.ring(px, py, 0.075, 0.006, v=0)
        c.ring(px, py, 0.052, 0.003, v=0)
    c.circle(cx, cy, 0.075, v=255)
    c.ring(cx, cy, 0.075, 0.005, v=0)
    star = []
    for k in range(16):
        a = k * math.pi / 8 + math.pi / 2
        r = 0.068 if k % 2 == 0 else 0.03
        star.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    c.poly(star, v=0)
    c.circle(cx, cy, 0.018, v=255)
    for k in range(8):
        a = k * math.pi / 4
        c.circle(cx + 0.045 * math.cos(a + math.pi / 8), cy + 0.045 * math.sin(a + math.pi / 8), 0.006, v=0)
    return STAINLESS, c.mask(), None


def d7105():
    """Rose-gold mirror; per leaf a thin etched frame whose inner sides join a square lattice medallion on the
    joint at mid-height (an 'H')."""
    c = canvas()
    lw = 0.007
    fx = lambda f: f * W_M
    fy = lambda f: H_M * (1 - f)                       # from top fraction
    top, bot = fy(0.035), fy(0.968)
    btop, bbot = fy(0.346), fy(0.585)
    left = [(fx(0.425), btop), (fx(0.425), top), (fx(0.055), top), (fx(0.055), bot), (fx(0.425), bot), (fx(0.425), bbot)]
    c.line(left, lw)
    c.line(mirror_x(left), lw)
    box = [(fx(0.236), btop), (fx(0.764), btop), (fx(0.764), bbot), (fx(0.236), bbot), (fx(0.236), btop)]
    c.line(box, lw)
    # inner lattice square with a solid etched border
    x0, x1, y0, y1 = fx(0.286), fx(0.717), fy(0.565), fy(0.365)
    c.rect(x0, y0, x1, y1)
    b = 0.012
    c.rect(x0 + b, y0 + b, x1 - b, y1 - b, v=0)
    # lattice: rings on a grid with diamond links (Chinese window fretwork), etched strokes
    n = 4
    px_ = (x1 - x0 - 2 * b) / n
    py_ = (y1 - y0 - 2 * b) / n
    for i in range(n + 1):
        for j in range(n + 1):
            gx, gy = x0 + b + i * px_, y0 + b + j * py_
            c.ring(gx, gy, px_ * 0.36, 0.005)
            if i < n and j < n:
                mx, my = gx + px_ / 2, gy + py_ / 2
                d = px_ * 0.2
                c.line([(mx - d, my), (mx, my + d), (mx + d, my), (mx, my - d), (mx - d, my)], 0.005)
    # keep the lattice inside its border
    inner = K.MCanvas(W_M, H_M, PW, PH, 4)
    inner.rect(x0 + b, y0 + b, x1 - b, y1 - b)
    outer = K.MCanvas(W_M, H_M, PW, PH, 4)
    outer.rect(x0, y0, x1, y1)
    m = c.mask()
    m_in, m_out = inner.mask(), outer.mask()
    border = np.clip(m_out - m_in, 0, 1)
    m = np.maximum(m * m_in, border) + m * (1 - m_out)
    return ROSE, np.clip(m, 0, 1), None


def d7014():
    """Mirror; 40 horizontal frosted stripes (half the 49.5 mm pitch) across both leaves, a mirror margin at the
    edges and at the joint."""
    c = canvas()
    pitch = 0.0236 * H_M
    y_top = H_M * (1 - 0.038)
    for k in range(40):
        y1 = y_top - k * pitch
        y0 = y1 - pitch * 0.5
        c.rect(0.10 * W_M, y0, 0.48 * W_M, y1)
        c.rect(0.52 * W_M, y0, 0.90 * W_M, y1)
    return STAINLESS, c.mask(), None


def spiral(cx, cy, r0, a0, turns, sense, shrink=0.55, n=60):
    pts = []
    for t in np.linspace(0, 1, n):
        a = a0 + sense * turns * 2 * math.pi * t
        r = r0 * (shrink ** (turns * t * 2))
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def leaf_shape(x, y, ang, length, width):
    pts = []
    for t in np.linspace(0, 1, 16):
        wv = width * math.sin(math.pi * t) ** 0.9 * (1 - 0.3 * t)
        pts.append((t * length, wv))
    pts += [(t, -wv) for t, wv in pts[::-1]]
    ca, sa = math.cos(ang), math.sin(ang)
    return [(x + px * ca - py * sa, y + px * sa + py * ca) for px, py in pts]


def scroll_band(c, x0, x1, y0, y1, rng):
    """Baroque scrollwork filling a vertical band: a sinuous stem with alternating volutes, acanthus leaves and buds."""
    xc, bw = (x0 + x1) / 2, x1 - x0
    period = bw * 1.05
    amp = bw * 0.16
    stem = [(xc + amp * math.sin(2 * math.pi * (y - y0) / period), y) for y in np.linspace(y0, y1, 400)]
    c.line(stem, 0.009)
    k = 0
    y = y0 + period * 0.25
    while y < y1 - period * 0.2:
        side = 1 if k % 2 == 0 else -1
        sx = xc + amp * math.sin(2 * math.pi * (y - y0) / period)
        # volute: an arm out to the side, curling back
        r0 = bw * 0.26
        ccx = sx + side * bw * 0.22
        ccy = y + bw * 0.05
        a0 = math.pi if side > 0 else 0.0
        sp = spiral(ccx, ccy, r0, a0, 1.35, -side, shrink=0.62)
        c.line([(sx, y)] + sp, 0.008)
        # thick curl end
        ex, ey = sp[-1]
        c.circle(ex, ey, 0.007)
        # acanthus leaves along the arm
        for t, sz in ((0.18, 1.0), (0.42, 0.8), (0.65, 0.6)):
            i = int(t * (len(sp) - 1))
            (ax, ay), (bx, by) = sp[i], sp[min(i + 2, len(sp) - 1)]
            ang = math.atan2(by - ay, bx - ax) + side * 0.9
            c.poly(leaf_shape(ax, ay, ang, 0.05 * sz, 0.016 * sz))
            c.poly(leaf_shape(ax, ay, ang - side * 1.6, 0.035 * sz, 0.011 * sz))
        # a bud and small curl on the other side of the stem
        o = -side
        bx_, by_ = sx + o * bw * 0.12, y + period * 0.18
        c.poly(leaf_shape(sx, y + period * 0.05, math.atan2(by_ - y - period * 0.05, bx_ - sx), 0.06, 0.016))
        sp2 = spiral(sx + o * bw * 0.3, y - period * 0.12, bw * 0.09, 0 if o > 0 else math.pi, 1.0, o, shrink=0.45, n=40)
        c.line(sp2, 0.004)
        c.circle(sp2[0][0], sp2[0][1], 0.006)
        y += period * 0.5
        k += 1
    # small berries to fill
    for _ in range(int((y1 - y0) / bw * 6)):
        bx = rng.uniform(x0 + 0.01, x1 - 0.01)
        by = rng.uniform(y0, y1)
        c.circle(bx, by, rng.uniform(0.003, 0.006))


def d7001():
    """Mirror; on each leaf a vertical band (~1/3 of the leaf) of etched baroque scrollwork, nearly full height.
    The band is the scroll drawn twice - as is and mirrored about the band axis half a period lower - which gives
    the dense, roughly symmetric tracery of the catalogue."""
    y0, y1 = H_M * (1 - 0.884), H_M * (1 - 0.077)
    bx0, bx1 = 0.125 * W_M, 0.35 * W_M
    bw = bx1 - bx0
    c = canvas()
    scroll_band(c, bx0, bx1, y0, y1, np.random.default_rng(7001))
    c2 = canvas()
    scroll_band(c2, bx0, bx1, y0 - bw * 0.26, y1 + bw * 0.26, np.random.default_rng(7002))
    m1 = c.mask()
    m2 = c2.mask()
    xa0, xa1 = int(round((bx0 - 0.02) / W_M * PW)), int(round((bx1 + 0.02) / W_M * PW))
    band = m1[:, xa0:xa1]
    band = np.maximum(band, m2[:, xa0:xa1][:, ::-1])
    clip = canvas()
    clip.rect(bx0 - 0.02, y0, bx1 + 0.02, y1)
    cm = clip.mask()[:, xa0:xa1]
    band = band * cm
    m = np.zeros((PH, PW))
    m[:, xa0:xa1] = band
    # right leaf: the same band mirrored, centred in 0.60 .. 0.82 of the width
    wb = xa1 - xa0
    xb0 = int(round(0.71 * PW - wb / 2))
    m[:, xb0:xb0 + wb] = np.maximum(m[:, xb0:xb0 + wb], band[:, ::-1])
    return STAINLESS, np.clip(m, 0, 1), None


def d7037():
    """Titanium gold (multi-process: mirror + etching): etched classical arch with fluted Ionic columns across both
    leaves, a keystone and a beaded archivolt, a thin inner arch, festoon loops along the top."""
    c = canvas()
    cx = W_M / 2
    cap_y0, cap_y1 = H_M * 0.73, H_M * 0.77           # capital
    col_c = 0.30
    half = 0.058
    for sx in (-1, 1):
        x = cx + sx * col_c
        # base / plinth
        c.rect(x - 0.075, 0.02, x + 0.075, 0.06)
        c.rect(x - 0.065, 0.06, x + 0.065, 0.08)
        # fluted shaft: five frosted strips with mirror gaps
        n = 5
        sw = 2 * half / n
        for i in range(n):
            a = x - half + i * sw
            c.rect(a + 0.003, 0.08, a + sw - 0.003, cap_y0)
        # Ionic capital: abacus + echinus + two volutes
        c.rect(x - 0.085, cap_y1 - 0.016, x + 0.085, cap_y1)
        c.poly([(x - 0.07, cap_y0), (x + 0.07, cap_y0), (x + 0.08, cap_y1 - 0.016), (x - 0.08, cap_y1 - 0.016)])
        for vx in (-1, 1):
            vcx, vcy = x + vx * 0.068, cap_y0 + 0.022
            c.circle(vcx, vcy, 0.024)
            c.line(spiral(vcx, vcy, 0.018, math.pi / 2, 1.5, vx, shrink=0.55, n=50), 0.004, v=0)
        c.rect(x - 0.06, cap_y0 - 0.012, x + 0.06, cap_y0 - 0.004)       # necking
    # archivolt: frosted band with a line of mirror beads and mirror edge lines
    ay = cap_y1
    r_out, r_in = col_c + 0.06, col_c - 0.045
    band = c.arc_pts(cx, ay, r_out, 0, math.pi) + c.arc_pts(cx, ay, r_in, math.pi, 0)
    c.poly(band)
    c.line(c.arc_pts(cx, ay, r_out - 0.008, 0, math.pi), 0.003, v=0)
    c.line(c.arc_pts(cx, ay, r_in + 0.008, 0, math.pi), 0.003, v=0)
    rm = (r_out + r_in) / 2
    for a in np.linspace(0.05, math.pi - 0.05, 19):
        c.circle(cx + rm * math.cos(a), ay + rm * math.sin(a), 0.0085, v=0)
    # keystone
    c.poly([(cx - 0.045, ay + r_in - 0.01), (cx + 0.045, ay + r_in - 0.01), (cx + 0.06, ay + r_out + 0.035),
            (cx - 0.06, ay + r_out + 0.035)])
    c.poly([(cx - 0.03, ay + r_in + 0.01), (cx + 0.03, ay + r_in + 0.01), (cx + 0.04, ay + r_out + 0.018),
            (cx - 0.04, ay + r_out + 0.018)], v=0)
    c.rect(cx - 0.025, ay + r_in + 0.02, cx + 0.025, ay + r_out + 0.01)
    # inner arch (thin line), closing at the bottom
    ri = 0.205
    inner = [(cx - ri, 0.1)] + c.arc_pts(cx, ay - 0.04, ri, math.pi, 0) + [(cx + ri, 0.1), (cx - ri, 0.1)]
    c.line(inner, 0.004)
    # festoon loops along the top edge
    for k in range(-2, 3):
        x = cx + k * 0.15
        loop = [(x - 0.03, H_M)] + c.arc_pts(x, H_M - 0.085, 0.03, math.pi, 2 * math.pi) + [(x + 0.03, H_M)]
        c.line(loop, 0.008)
        c.line([(x - 0.016, H_M)] + c.arc_pts(x, H_M - 0.085, 0.016, math.pi, 2 * math.pi) + [(x + 0.016, H_M)], 0.003)
    return TIGOLD, c.mask(), None


def d8055():
    """«Цветной метал, бук»: beech wood-look film, each leaf its own vertical flitch; satin, not metal."""
    rng = np.random.default_rng(8055)
    half = PW // 2
    leaves = []
    for k in range(2):
        a, tone = K.woodgrain(rng, PH, half, MMX, MMY, "#d8ad6d", "#a8773d", contrast=0.75)
        fl = K.noise(rng, PH, half, 0.6, 1.8 / MMY)
        a = K.mix(a, a * 0.75, K.smoothstep(2.3, 3.0, fl) * 0.5)
        # a lighter heart band down the middle of the right leaf, as in the photo
        xs = np.linspace(-1, 1, half)[None, :]
        a = a * (1 + (0.08 if k == 1 else 0.04) * np.exp(-(xs / 0.5) ** 2))[..., None]
        leaves.append((a, tone))
    alb = np.concatenate([leaves[0][0], leaves[1][0]], 1)
    alb = K.fit_mean(alb, "#c09455")
    tone = np.concatenate([leaves[0][1], leaves[1][1]], 1)
    hgt = 0.4 * tone
    xs = np.arange(PW)[None, :] + 0.5
    seam = np.clip(1.2 - np.abs(xs - PW / 2), 0, 1) * np.ones((PH, 1))
    alb = alb * (1 - 0.6 * seam)[..., None]
    nrm = K.normal_from_height(hgt - 3 * seam, k=0.25, periodic=False)
    msk = K.mask_map(0.0, 0.5 * np.ones((PH, PW)), 1 - 0.5 * seam)
    return K.to8(alb), nrm, msk


DOORS = {
    "sl-7061": ("SL-7061 дверь: зеркало, травление (розетка, полосы)", d7061),
    "sl-7105": ("SL-7105 дверь: розовое золото, зеркало, травление", d7105),
    "sl-7001": ("SL-7001 дверь: зеркало, травление (растительный орнамент)", d7001),
    "sl-7014": ("SL-7014 дверь: зеркало, травление (полосы)", d7014),
    "sl-7037": ("SL-7037 дверь: мультипроцесс титана (арка)", d7037),
    "sl-8055": ("SL-8055 дверь: цветной металл, бук", None),
}


def mid_of(did):
    return "liftdoor_" + did.replace("-", "_")


def build(did):
    if did == "sl-8055":
        return d8055()
    base, etch, _ = DOORS[did][1]()
    rng = np.random.default_rng(sum(map(ord, did)))
    hair = None
    if did == "sl-7037":
        # multi-process titanium: the field outside the arch is hairline-brushed, the arch opening mirror
        c = canvas()
        c.poly([(W_M / 2 - 0.25, 0.08)] + c.arc_pts(W_M / 2, H_M * 0.77, 0.25, math.pi, 0) + [(W_M / 2 + 0.25, 0.08)])
        inside = c.mask()
        hair = 1 - inside
        bg = 0.93 * inside + 0.62 * (1 - inside)
        return K.etched_metal(rng, PW, PH, MMX, MMY, base, etch, bg_smooth=bg, hairline=hair, seam_u=[0.5], etch_light=1.22)
    return K.etched_metal(rng, PW, PH, MMX, MMY, base, etch, bg_smooth=0.95, seam_u=[0.5], etch_light=1.22)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--no-merge", action="store_true")
    args = ap.parse_args(argv)
    ids = args.ids or list(DOORS)
    for did in ids:
        alb, nrm, msk = build(did)
        K.write_material(mid_of(did), alb, nrm, msk)
        print(mid_of(did), K.mean_hex(alb), alb.shape)
    entries = [K.entry(mid_of(d), DOORS[d][0], SOURCE, (1, 1), 1024, mask_size=1024) for d in DOORS]
    rows = []
    for did in DOORS:
        mid = mid_of(did)
        alb = K.read_albedo(mid)
        msk = K.read_mask(mid)
        ref = Image.open(K.REF / "doors" / f"{did}.jpg").convert("RGB").crop((110, 125, 475, 892))
        sm = Image.fromarray(msk[..., 3])
        ims = [K.fit_h(ref, 420), Image.fromarray(alb).resize((180, 420)), sm.resize((180, 420)),
               K.lit_preview(alb, msk).resize((180, 420)),
               Image.fromarray(alb).crop((PW // 2 - 110, 120, PW // 2 + 110, 420))]
        rows.append((f"{mid}: ref | albedo | smoothness | lit | 1:1", ims))
    rows = [(a[0] + "   ||   " + (b[0] if b else ""), a[1] + (b[1] if b else [])) for a, b in zip(rows[::2], rows[1::2] + [None])]
    K.sheet(rows, K.SHEETS / f"{FAMILY}.png", "Lift landing doors")
    K.write_entries(FAMILY, entries, merge=not args.no_merge)


if __name__ == "__main__":
    main()
