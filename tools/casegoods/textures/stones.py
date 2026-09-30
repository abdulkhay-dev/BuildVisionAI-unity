#!/usr/bin/env python3
"""Casegoods decor textures, family `stones`: the stone, concrete, metal-look and other non-wood films of the Pinskdrev
catalogue (plus the two textured blacks / whites that are not plain unis).

    python tools/casegoods/textures/stones.py [ids]                  # textures + entries/stones.json + merge
    python tools/casegoods/textures/stones.py --no-write --sheet [ids] # check sheet only (needs PyMuPDF)
    python tools/casegoods/textures/stones.py --sheet --photos DIR     # + sheets/stones.png (site photos cached in DIR)

Outputs per material M (Assets/House4696/External/Materials/M/): M_albedo.jpg (sRGB 2048x1024, tileable, metersPerTile
of the entry), M_normal.jpg (OpenGL, 1024x512), M_mask.png (R metallic 0, G AO 255, B 0, A smoothness; 256x128).

Colour: every decor is fitted to its catalogue swatch with the swatch's own statistic (tools/casegoods/gen/catpage.py
--swatch: the trimmed mean - middle 60 % by brightness - of the sRGB pixels at ~2 mm per pixel), so the texture
downsized to the swatch's print resolution gives the same number (dE76 <= 1.5, reported). Where no swatch exists the
target comes from the product photos (see stones.md).

The structures are procedural (numpy + Pillow only): periodic Gaussian noise (make_finishes.gauss_noise), domain-warped
clouds, crack-like vein polylines drawn with exact coverage on the torus, noise-contour veins, facet creases (Призма),
and wave 1's lamination model for the two woodgrain films (Черный 660 WML, Белая Ваниль). The colouring is the door
kit's (finish_kit.albedo_linear: ground from `comb` x fine + `tone` x broad towards `dark` / `light`, coloured layers
on top), then the base colour is re-solved against the swatch statistic.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools" / "doors" / "textures"))
import finish_kit as kit            # noqa: E402  (door machinery: colour, noise, laminations, maps)
import make_finishes as mf          # noqa: E402
import merge_entries                # noqa: E402

EXT = kit.EXT
W, H = kit.ALBEDO                   # 2048 x 1024
ENTRIES = HERE / "entries" / "stones.json"
SHEET = HERE / "sheets" / "stones.png"
SOURCE = "procedural:tools/casegoods/textures/stones.py"
SWATCH_MM_PER_PX = 2.0              # catpage renders a swatch at 150 dpi; a swatch chip shows ~400 mm in ~190 px

gauss_noise, unit, smoothstep = mf.gauss_noise, kit.unit, kit.smoothstep


# ------------------------------------------------------------------------------------------------ building blocks
def noise(rng, sx, sy=None):
    """Periodic unit noise over the tile, Gaussian correlation sx (along x = U) / sy px."""
    return gauss_noise(rng, (H, W), sx, sx if sy is None else sy)


def fbm(rng, octaves):
    """Sum of periodic noises: octaves = [(sigma_x px, sigma_y px, amplitude)], unit std."""
    return unit(sum(a * noise(rng, sx, sy) for sx, sy, a in octaves))


_YY, _XX = np.mgrid[0:H, 0:W].astype(np.float64)


def sample(field, x, y):
    """Bilinear periodic sampling of field at (x, y) px."""
    x0, y0 = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    tx, ty = x - x0, y - y0
    x0, y0 = x0 % W, y0 % H
    x1, y1 = (x0 + 1) % W, (y0 + 1) % H
    return ((field[y0, x0] * (1 - tx) + field[y0, x1] * tx) * (1 - ty) +
            (field[y1, x0] * (1 - tx) + field[y1, x1] * tx) * ty)


def warped(field, dx, dy):
    return sample(field, _XX + dx, _YY + dy)


def contour_lines(n, width_px, soft=0.7):
    """Lines along the zero contour of the smooth field n, of constant width (px): |n| / |grad n| is the distance."""
    gx = (np.roll(n, -1, 1) - np.roll(n, 1, 1)) / 2
    gy = (np.roll(n, -1, 0) - np.roll(n, 1, 0)) / 2
    d = np.abs(n) / np.maximum(np.hypot(gx, gy), 1e-6)
    return np.clip((width_px / 2 + soft - d) / (2 * soft), 0.0, 1.0)


def blur_periodic(a, sig):
    """Gaussian blur on the torus (FFT)."""
    if sig <= 0:
        return a
    f = np.fft.rfft2(a)
    fy = np.fft.fftfreq(a.shape[0])[:, None]
    fx = np.fft.rfftfreq(a.shape[1])[None, :]
    f *= np.exp(-2 * np.pi ** 2 * ((fx * sig) ** 2 + (fy * sig) ** 2))
    return np.fft.irfft2(f, s=a.shape)


def segment(out, p0, p1, w0, w1, a0, a1):
    """Draws a segment into `out` (max-composite, periodic), exact-ish coverage: widths w (px) and opacities a
    interpolated from p0 to p1."""
    (x0, y0), (x1, y1) = p0, p1
    r = max(w0, w1) / 2 + 1.5
    c0, c1 = int(math.floor(min(x0, x1) - r)), int(math.ceil(max(x0, x1) + r))
    r0, r1 = int(math.floor(min(y0, y1) - r)), int(math.ceil(max(y0, y1) + r))
    xs = np.arange(c0, c1 + 1, dtype=np.float64)[None, :]
    ys = np.arange(r0, r1 + 1, dtype=np.float64)[:, None]
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((xs - x0) * dx + (ys - y0) * dy) / L2, 0.0, 1.0)
    d = np.hypot(xs - (x0 + t * dx), ys - (y0 + t * dy))
    wid = w0 + (w1 - w0) * t
    a = a0 + (a1 - a0) * t
    cov = np.clip(wid / 2 + 0.5 - d, 0.0, 1.0) * np.minimum(1.0, wid)      # hairlines thinner than 1 px: fainter
    idx = np.ix_(np.arange(r0, r1 + 1) % H, np.arange(c0, c1 + 1) % W)
    out[idx] = np.maximum(out[idx], a * cov)


def vein_path(rng, start, theta, length_px, step_px, curl, kink):
    """A crack-like path: straight runs with slow bending (curl rad / step) and occasional kinks (probability per
    step, angle ~ N(0, 0.5 rad))."""
    n = max(3, int(length_px / step_px))
    pts = [np.array(start, float)]
    bend = 0.0
    for _ in range(n):
        bend = 0.85 * bend + curl * rng.standard_normal()
        theta += bend * 0.3
        if rng.random() < kink:
            theta += 0.5 * rng.standard_normal()
        pts.append(pts[-1] + step_px * np.array([math.cos(theta), math.sin(theta)]))
    return np.array(pts), theta


def draw_veins(rng, out, spec, px):
    """Vein network: spec = dict(count, length (median mm, log-sigma), width (median mm, log-sigma), alpha (lo, hi),
    angle (mean rad, spread rad or None = uniform), curl, kink, branch (children per vein), fade (0..1: opacity comes
    and goes along the vein), twin (share of veins with a parallel companion))."""
    for _ in range(spec["count"]):
        L = min(1800.0, spec["length"][0] * math.exp(spec["length"][1] * rng.standard_normal())) * px
        wmed = spec["width"][0] * math.exp(spec["width"][1] * rng.standard_normal()) * px
        amax = rng.uniform(*spec["alpha"])
        th = (rng.uniform(0, 2 * math.pi) if spec.get("angle") is None
              else spec["angle"][0] + spec["angle"][1] * rng.standard_normal())
        start = (rng.uniform(0, W), rng.uniform(0, H))
        _draw_one(rng, out, spec, px, start, th, L, wmed, amax, depth=0)


def _draw_one(rng, out, spec, px, start, th, L, wmed, amax, depth):
    step = max(3.0, spec.get("step", 6.0) * px)
    pts, _ = vein_path(rng, start, th, L, step, spec["curl"], spec["kink"])
    n = len(pts)
    s = np.arange(n) / (n - 1)
    taper = np.clip(np.minimum(s, 1 - s) / 0.12, 0, 1) ** 0.7
    env = mf.noise_1d(rng, max(64, n * 4), 6.0)[:n]
    fade = spec.get("fade", 0.5)
    alpha = amax * taper * np.clip(1 - fade + fade * (0.6 + 0.6 * env), 0.05, 1.0)
    wid = wmed * np.clip(0.55 + 0.45 * taper, 0.2, 1) * np.exp(0.35 * mf.noise_1d(rng, max(64, n * 4), 5.0)[:n])
    twin = rng.random() < spec.get("twin", 0.0)
    off = rng.uniform(1.5, 4.0) * px * (1 if rng.random() < 0.5 else -1)
    for i in range(n - 1):
        segment(out, pts[i], pts[i + 1], wid[i], wid[i + 1], alpha[i], alpha[i + 1])
        if twin:
            d = pts[i + 1] - pts[i]
            nrm = np.array([-d[1], d[0]]) / (np.hypot(*d) + 1e-9) * off
            segment(out, pts[i] + nrm, pts[i + 1] + nrm, wid[i] * 0.6, wid[i + 1] * 0.6, alpha[i] * 0.55,
                    alpha[i + 1] * 0.55)
    if depth < 2:
        for _ in range(rng.poisson(spec.get("branch", 0.0) / (depth + 1))):
            k = rng.integers(n // 5, max(n // 5 + 1, 4 * n // 5))
            d = pts[min(k + 1, n - 1)] - pts[k]
            base = math.atan2(d[1], d[0])
            ang = base + (1 if rng.random() < 0.5 else -1) * rng.uniform(0.25, 0.8)
            _draw_one(rng, out, spec, px, pts[k], ang, L * rng.uniform(0.2, 0.55), wid[k] * 0.65, alpha[k] * 0.8,
                      depth + 1)


def dots(rng, per_dm2, radius, alpha, px):
    """Sparse round specks / pores: per_dm2 per 100 x 100 mm, radius (median mm, log-sigma), alpha (lo, hi)."""
    ss = 2
    im = Image.new("L", (W * ss, H * ss), 0)
    d = ImageDraw.Draw(im)
    area_dm2 = (W / px / 100.0) * (H / px / 100.0)
    for _ in range(int(per_dm2 * area_dm2)):
        x, y = rng.uniform(0, W * ss), rng.uniform(0, H * ss)
        r = max(0.35, radius[0] * math.exp(radius[1] * rng.standard_normal()) * px * ss)
        a = int(255 * rng.uniform(*alpha))
        for ox in (-W * ss, 0, W * ss):
            for oy in (-H * ss, 0, H * ss):
                if -r <= x + ox <= W * ss + r and -r <= y + oy <= H * ss + r:
                    d.ellipse([x + ox - r, y + oy - r, x + ox + r, y + oy + r], fill=a)
    a = np.asarray(im, dtype=np.float64) / 255.0
    return a.reshape(H, ss, W, ss).mean((1, 3))


def smears(rng, count, length, width, alpha, blur_mm, px, angle=None):
    """Soft elongated marks (trowel / smear): short thick strokes, heavily blurred."""
    out = np.zeros((H, W))
    for _ in range(count):
        L = length[0] * math.exp(length[1] * rng.standard_normal()) * px
        th = rng.uniform(0, math.pi) if angle is None else angle[0] + angle[1] * rng.standard_normal()
        p0 = np.array([rng.uniform(0, W), rng.uniform(0, H)])
        p1 = p0 + L * np.array([math.cos(th), math.sin(th)])
        wd = width[0] * math.exp(width[1] * rng.standard_normal()) * px
        a = rng.uniform(*alpha)
        segment(out, p0, p1, wd, wd * rng.uniform(0.3, 1.0), a, a * rng.uniform(0.2, 1.0))
    return blur_periodic(out, blur_mm * px)


def creases(rng, spec, px):
    """Folded-facet relief (Призма): loose fans of long straight creases. Each crease is a tent (ridge or valley) of
    half-width `reach` mm whose height fades out towards the crease's ends, so the summed surface is piecewise
    planar with the creases as its edges. Returns (height, crease-line opacity)."""
    hgt = np.zeros((H, W))
    line = np.zeros((H, W))
    for _ in range(spec["fans"]):
        cx, cy = rng.uniform(0, W), rng.uniform(0, H)
        th0 = spec["angle"][0] + spec["angle"][1] * rng.standard_normal()
        for _ in range(rng.integers(*spec["per_fan"])):
            th = th0 + spec["spread"] * rng.standard_normal()
            L = min(1400.0, spec["length"][0] * math.exp(spec["length"][1] * rng.standard_normal())) * px
            reach = spec["reach"][0] * math.exp(spec["reach"][1] * rng.standard_normal()) * px
            # the window must stay smaller than the tile, or the wrapped indices repeat (stray seams)
            L = min(L, (H - 2 * reach - 8) / max(abs(math.sin(th)), 1e-3), (W - 2 * reach - 8) / max(abs(math.cos(th)), 1e-3))
            along = rng.uniform(-0.3, 0.3) * L
            p0 = np.array([cx, cy]) + rng.normal(0, spec["jitter"] * px, 2) + along * np.array([math.cos(th), math.sin(th)])
            u = np.array([math.cos(th), math.sin(th)])
            v = np.array([-u[1], u[0]])
            amp = (1 if rng.random() < 0.5 else -1) * rng.uniform(0.5, 1.0)
            # window: the crease's bounding box plus its reach
            ends = [p0 - u * L / 2, p0 + u * L / 2]
            r = reach + 2
            c0 = int(math.floor(min(e[0] for e in ends) - r)); c1 = int(math.ceil(max(e[0] for e in ends) + r))
            r0 = int(math.floor(min(e[1] for e in ends) - r)); r1 = int(math.ceil(max(e[1] for e in ends) + r))
            xs = np.arange(c0, c1 + 1, dtype=np.float64)[None, :] - p0[0]
            ys = np.arange(r0, r1 + 1, dtype=np.float64)[:, None] - p0[1]
            t = xs * u[0] + ys * u[1]                 # along the crease
            d = xs * v[0] + ys * v[1]                 # across
            env = np.clip(1 - (np.abs(t) / (L / 2)) ** 2, 0, 1)          # fades towards the ends
            tent = np.clip(1 - np.sqrt(d * d + 0.8) / reach, 0, 1)       # slightly rounded crest
            idx = np.ix_(np.arange(r0, r1 + 1) % H, np.arange(c0, c1 + 1) % W)
            hgt[idx] += amp * reach * tent * env
            wl = spec["line_w"] * px
            ln = np.clip(wl / 2 + 0.5 - np.abs(d), 0, 1) * np.minimum(1, wl) * env ** 0.5 * rng.uniform(0.3, 1.0)
            line[idx] = np.maximum(line[idx], ln)
    return hgt, line


# ------------------------------------------------------------------------------------------------ structures
# Every builder returns the kit's structure dict: fine / broad (unit std tone fields), coloured layers (dark, light,
# xdark, xlight, pore, fleck: 0..1), height (relief), rough (lowers smoothness), relief (tilt_deg).

def s_beton(tile):
    """Бетон Лайт: light cloudy concrete - large soft clouds, medium mottling, fine grain, sparse pores and a few
    darker trowel smears; the swatch shows faint greenish / yellowish patches."""
    px = W / (tile[0] * 1000)
    rng = np.random.default_rng(8181)
    broad = fbm(rng, [(260 * px, 260 * px, 1.0), (110 * px, 110 * px, 0.8), (45 * px, 45 * px, 0.55)])
    wx, wy = noise(rng, 90 * px) * 25 * px, noise(rng, 90 * px) * 25 * px
    broad = unit(warped(broad, wx, wy))
    fine = fbm(rng, [(9 * px, 9 * px, 0.8), (3 * px, 3 * px, 0.7), (0.8 * px, 0.8 * px, 0.6)])
    bx, by = noise(rng, 30 * px) * 14 * px, noise(rng, 30 * px) * 14 * px
    blot = warped(fbm(rng, [(35 * px, 22 * px, 1.0), (12 * px, 9 * px, 0.7), (4 * px, 4 * px, 0.3)]), wx + bx, wy + by)
    light = smoothstep(0.6, 2.2, blot) * 0.7                     # pale cement patches
    dark = np.clip(smears(rng, 30, (160, 0.5), (18, 0.5), (0.25, 0.6), 7, px) + 0.35 * smoothstep(1.2, 2.6, -blot), 0, 1)
    tint = smoothstep(0.3, 1.8, fbm(rng, [(180 * px, 180 * px, 1)]))  # a greener-grey cast in places
    pore = dots(rng, 35, (0.35, 0.45), (0.3, 0.8), px)
    height = -1.0 * pore + 0.12 * fine - 0.05 * dark
    return dict(fine=fine, broad=broad, light=light, dark=dark, xdark=tint, pore=pore, height=height,
                rough=pore + 0.3 * light, relief=dict(tilt_deg=1.6))


def s_kamen(tile):
    """Камень серый: dark grey concrete / stone - cloudy lighter and darker patches, fine specks, faint streaks."""
    px = W / (tile[0] * 1000)
    rng = np.random.default_rng(6919)
    wx, wy = noise(rng, 120 * px) * 30 * px, noise(rng, 120 * px) * 30 * px
    broad = unit(warped(fbm(rng, [(220 * px, 220 * px, 1.0), (80 * px, 80 * px, 0.8), (30 * px, 30 * px, 0.5)]), wx, wy))
    fine = fbm(rng, [(6 * px, 6 * px, 0.7), (2 * px, 2 * px, 0.8), (0.7 * px, 0.7 * px, 0.6),
                     (40 * px, 1.2 * px, 0.35)])                    # faint streaks along U
    blot = warped(fbm(rng, [(25 * px, 25 * px, 1.0), (9 * px, 9 * px, 0.6)]), wx, wy)
    light = smoothstep(0.9, 2.4, blot) * 0.5
    dark = smoothstep(1.0, 2.6, -blot) * 0.5
    fleck = dots(rng, 140, (0.3, 0.4), (0.3, 0.8), px)
    pore = dots(rng, 70, (0.3, 0.4), (0.4, 0.9), px)
    height = -0.8 * pore + 0.15 * fine
    return dict(fine=fine, broad=broad, light=light, dark=dark, fleck=fleck, pore=pore, height=height,
                rough=pore, relief=dict(tilt_deg=1.6))


def s_nero(tile):
    """Мрамор Неро Маркина: black marble - a large crack-like network of thin white veins (straight runs, kinks,
    branches, some doubled), faint grey ghost veins and hairlines, soft grey clouds in the black."""
    px = W / (tile[0] * 1000)
    rng = np.random.default_rng(8500)
    broad = unit(warped(fbm(rng, [(300 * px, 300 * px, 1.0), (90 * px, 90 * px, 0.6)]),
                        noise(rng, 150 * px) * 40 * px, noise(rng, 150 * px) * 40 * px))
    fine = fbm(rng, [(4 * px, 4 * px, 0.6), (1.2 * px, 1.2 * px, 0.8)])
    main = np.zeros((H, W))
    draw_veins(rng, main, dict(count=24, length=(700.0, 0.5), width=(1.3, 0.45), alpha=(0.45, 0.95), angle=None,
                               curl=0.012, kink=0.045, branch=0.5, fade=0.55, twin=0.35, step=6.0), px)
    main = blur_periodic(main, 0.5 * px)
    hair = np.zeros((H, W))
    draw_veins(rng, hair, dict(count=45, length=(300.0, 0.5), width=(0.45, 0.3), alpha=(0.2, 0.55), angle=None,
                               curl=0.015, kink=0.06, branch=0.4, fade=0.7, twin=0.0, step=5.0), px)
    ghost = np.zeros((H, W))
    draw_veins(rng, ghost, dict(count=14, length=(900.0, 0.4), width=(5.0, 0.4), alpha=(0.35, 0.8), angle=None,
                                curl=0.012, kink=0.03, branch=0.5, fade=0.6, step=8.0), px)
    ghost = blur_periodic(ghost, 4 * px)
    halo = np.clip(blur_periodic(main, 2.5 * px) * 2.0, 0, 1)
    xlight = np.clip(main + 0.55 * hair, 0, 1)
    height = 0.1 * fine - 0.15 * xlight
    return dict(fine=fine, broad=broad, xlight=xlight, light=np.clip(0.5 * halo + 0.6 * ghost, 0, 1),
                height=height, rough=xlight, relief=dict(tilt_deg=0.6))


def s_oniks(tile):
    """Оникс: grey-brown slate / onyx - mottled clouds (stretched a little along U), pale thin crack-like veins
    running mostly along U, darker smeared streaks and patches."""
    px = W / (tile[0] * 1000)
    rng = np.random.default_rng(8170)
    wx, wy = noise(rng, 200 * px, 120 * px) * 30 * px, noise(rng, 200 * px, 120 * px) * 20 * px
    broad = unit(warped(fbm(rng, [(520 * px, 300 * px, 0.8), (220 * px, 130 * px, 1.0), (90 * px, 50 * px, 0.45)]),
                        wx, wy))
    fine = fbm(rng, [(6 * px, 3 * px, 0.7), (2 * px, 1.2 * px, 0.7), (0.8 * px, 0.8 * px, 0.5)])
    veins = np.zeros((H, W))
    draw_veins(rng, veins, dict(count=55, length=(420.0, 0.6), width=(0.9, 0.5), alpha=(0.5, 1.0),
                                angle=(0.0, 0.45), curl=0.018, kink=0.05, branch=1.0, fade=0.7, twin=0.25, step=6.0), px)
    veins = blur_periodic(veins, 0.35 * px)
    streak = smears(rng, 70, (220, 0.6), (22, 0.6), (0.3, 0.8), 9, px, angle=(0.0, 0.3))
    patch = warped(fbm(rng, [(60 * px, 40 * px, 1.0), (20 * px, 14 * px, 0.5)]), wx, wy)
    dark = blur_periodic(np.clip(0.6 * streak + 0.4 * smoothstep(0.9, 2.3, patch), 0, 1), 6 * px)
    light = np.clip(smoothstep(0.8, 2.2, broad) * 0.2 + np.clip(blur_periodic(veins, 3 * px) * 1.3, 0, 0.45), 0, 1)
    height = 0.12 * fine - 0.1 * dark - 0.1 * veins
    return dict(fine=fine, broad=broad, xlight=veins, dark=dark, light=light, height=height,
                rough=dark, relief=dict(tilt_deg=1.0))


def s_bruklin(tile):
    """Металл Бруклин: dark anthracite-blue metal / concrete look - suede-like blotches, faint oxidised clouds, fine
    brushed streaks along U, matt."""
    px = W / (tile[0] * 1000)
    rng = np.random.default_rng(8080)
    wx, wy = noise(rng, 70 * px) * 18 * px, noise(rng, 70 * px) * 18 * px
    broad = unit(warped(fbm(rng, [(240 * px, 200 * px, 1.0), (70 * px, 60 * px, 0.8), (22 * px, 20 * px, 0.7)]), wx, wy))
    brush = fbm(rng, [(60 * px, 0.6 * px, 1.0), (20 * px, 0.4 * px, 0.6)])
    mottle = fbm(rng, [(9 * px, 8 * px, 1.0), (3.5 * px, 3.5 * px, 0.7), (1.2 * px, 1.2 * px, 0.5)])
    fine = unit(0.95 * mottle + 0.22 * brush)
    blot = fbm(rng, [(10 * px, 9 * px, 1.0), (4 * px, 4 * px, 0.5)])
    light = smoothstep(0.9, 2.4, blot) * 0.5
    dark = smoothstep(0.8, 2.3, -blot) * 0.6
    height = 0.12 * brush + 0.25 * mottle
    return dict(fine=fine, broad=broad, light=light, dark=dark, height=height, rough=light,
                relief=dict(tilt_deg=1.2))


def s_sharli(tile):
    """Шарли керамика: warm grey-brown ceramic / stone-look film - fine lengthwise streaks (as the tops' edges show),
    soft clouds, matt."""
    px = W / (tile[0] * 1000)
    rng = np.random.default_rng(1160)
    wy = noise(rng, 400 * px, 60 * px) * 6 * px
    broad = unit(sum(a * mf.warp_rows(noise(rng, sx, sy), wy) for sx, sy, a in
                     [(500 * px, 120 * px, 1.0), (180 * px, 35 * px, 0.7), (60 * px, 12 * px, 0.4)]))
    streak = unit(sum(a * mf.warp_rows(noise(rng, sx, sy), wy) for sx, sy, a in
                      [(120 * px, 1.6 * px, 1.0), (40 * px, 0.6 * px, 0.7), (300 * px, 4 * px, 0.6)]))
    cloud = fbm(rng, [(30 * px, 25 * px, 1.0), (8 * px, 7 * px, 0.6)])
    fine = unit(0.75 * streak + 0.45 * cloud + 0.35 * fbm(rng, [(1.0 * px, 1.0 * px, 1.0)]))
    acc = np.zeros((H, W))
    env = mf.noise_1d(rng, 1 << 18, 40 * px)
    mf.draw_lines(rng, acc, dict(per_cm=0.3, width=(0.6, 0.5), length=(260.0, 0.8), alpha=(0.2, 0.5), fade=0.8,
                                 slope=0.004), wy, env, px)
    dark = 1 - np.exp(-acc)
    acc = np.zeros((H, W))
    mf.draw_lines(rng, acc, dict(per_cm=0.35, width=(0.9, 0.5), length=(200.0, 0.8), alpha=(0.2, 0.55), fade=0.8,
                                 slope=0.004), wy, env, px)
    light = 1 - np.exp(-acc)
    height = 0.2 * fine - 0.3 * dark
    return dict(fine=fine, broad=broad, dark=dark, light=light, height=height, rough=dark,
                relief=dict(tilt_deg=1.2))


PAT_CHERNY = dict(      # «Черный 660 WML»: near-black brushed-wood film, dense straight pore lines (ash / pine-like)
    seed=6601, warp=[(0.6, 700.0, 40.0), (0.15, 90.0, 6.0)], band_warp=(1.5, 600.0, 50.0),
    comb=dict(thickness=(1.1, 0.6), rho=-0.4, drift=0.7, drift_len=45.0, hp=4.0, mod=(0.4, 20.0, 300.0)),
    dark=dict(per_cm=3.5, width=(0.55, 0.4), length=(110.0, 0.9), alpha=(0.5, 1.0), fade=0.6, slope=0.002),
    light=dict(per_cm=1.2, width=(0.7, 0.45), length=(160.0, 0.8), alpha=(0.3, 0.9), fade=0.8, slope=0.002),
    fade_len=15.0, bands=(18.0, 900.0), cluster=(4.0, 200.0), cluster_share=0.4, fibre=(0.4, 4.0), fibre_share=0.15,
    relief=dict(comb=0.5, groove=1.0, fibre=0.25, tilt_deg=4.0),
)

PAT_VANIL = dict(       # «Белая Ваниль»: creamy white with a faint fine painted-ash grain
    seed=1081, warp=[(1.2, 500.0, 40.0), (0.3, 80.0, 8.0)], band_warp=(3.0, 400.0, 45.0),
    comb=dict(thickness=(1.4, 0.65), rho=-0.3, drift=0.6, drift_len=60.0, hp=5.0, mod=(0.4, 25.0, 300.0)),
    dark=dict(per_cm=0.9, width=(0.45, 0.4), length=(110.0, 0.9), alpha=(0.3, 0.9), fade=0.8, slope=0.003),
    light=dict(per_cm=0.3, width=(0.8, 0.45), length=(120.0, 0.8), alpha=(0.2, 0.7), fade=0.8, slope=0.003),
    fade_len=18.0, bands=(20.0, 900.0), cluster=(4.0, 160.0), cluster_share=0.4, fibre=(0.4, 4.0), fibre_share=0.2,
    relief=dict(comb=0.4, groove=1.0, fibre=0.3, tilt_deg=2.2),
)


def s_wood(pattern_name, pattern):
    def build(tile):
        assert tuple(tile) == kit.TILE_M, "the lamination model is laid out for 2.0 x 1.0 m tiles"
        return kit.wave1_structure(pattern_name, pattern)
    return build


def s_prizma(tile):
    """Призма 870: cool light grey-white ground with a pressed facet relief - loose fans of long straight creases
    (100-600 mm) crossing at random angles, the crease lines themselves a little greyer."""
    px = W / (tile[0] * 1000)
    rng = np.random.default_rng(8700)
    _, line = creases(rng, dict(fans=70, per_fan=(4, 10), angle=(math.pi / 2, 0.55), spread=0.2,
                                length=(420.0, 0.5), reach=(35.0, 0.4), jitter=80.0, line_w=1.0), px)
    # the pressed relief: fewer, longer, straighter creases in fans, broad calm facets between them
    hgt, line2 = creases(rng, dict(fans=16, per_fan=(3, 6), angle=(math.pi / 2, 0.5), spread=0.13,
                                   length=(700.0, 0.35), reach=(90.0, 0.3), jitter=50.0, line_w=1.0), px)
    line = np.maximum(line, 0.6 * line2)
    broad = fbm(rng, [(300 * px, 300 * px, 1.0), (80 * px, 80 * px, 0.5)])
    fine = fbm(rng, [(1.5 * px, 1.5 * px, 1.0), (0.6 * px, 0.6 * px, 0.6)])
    gx = (np.roll(hgt, -1, 1) - np.roll(hgt, 1, 1)) / 2
    gy = (np.roll(hgt, -1, 0) - np.roll(hgt, 1, 0)) / 2
    shade = unit(-gx - gy)                               # the facets read faintly in the albedo too (lit top-left)
    return dict(fine=fine, broad=unit(0.3 * broad + 0.7 * shade), dark=line, height=hgt / max(1e-9, hgt.std()) +
                0.02 * fine - 0.05 * line, rough=line, relief=dict(tilt_deg=3.0))


def s_grafit(tile):
    """ХДФ графит текстурный: dark graphite hardboard back with a fine non-directional linen / stone emboss."""
    px = W / (tile[0] * 1000)
    rng = np.random.default_rng(3303)
    broad = fbm(rng, [(150 * px, 150 * px, 1.0), (40 * px, 40 * px, 0.6)])
    warpx = noise(rng, 8 * px) * 0.6 * px
    weft = warped(fbm(rng, [(6 * px, 0.35 * px, 1.0), (2 * px, 0.3 * px, 0.5)]), warpx, 0 * warpx)
    warp_ = warped(fbm(rng, [(0.35 * px, 6 * px, 1.0), (0.3 * px, 2 * px, 0.5)]), 0 * warpx, warpx)
    grain = fbm(rng, [(0.5 * px, 0.5 * px, 1.0), (1.5 * px, 1.5 * px, 0.6)])
    fine = unit(0.55 * weft + 0.55 * warp_ + 0.6 * grain)
    fleck = dots(rng, 400, (0.15, 0.4), (0.2, 0.6), px)
    height = fine
    return dict(fine=fine, broad=broad, fleck=fleck, height=height, rough=fine, relief=dict(tilt_deg=6.0))


# ------------------------------------------------------------------------------------------------ materials
# color: catalogue swatch target (catpage --swatch statistic, sRGB); dark / light (and xdark / xlight / fleck / pore):
# the colours of the full-strength layers; comb / tone: L* std of the fine / broad fields; smooth: mask alpha / 255.
# tile: metersPerTile (U, V). ref: the swatch (page, crop) or None; photo: check-sheet photo (see REF_PHOTOS).
MATERIALS = [
    dict(id="cg_beton_layt", name="Бетон Лайт 818ТМ", build=s_beton, tile=(2.0, 1.0),
         swatch=(137, "0.678,0.86,0.732,0.90"), target="#cdcac4",
         dark="#a9a7a1", light="#e2dfd8", xdark="#c4c8bf", xdark_k=0.5, pore="#7d7b77",
         comb=1.6, tone=2.6, smooth=0.22, tilt=1.6),
    dict(id="cg_mramor_nero_markina", name="Мрамор Неро Маркина 850ТМ", build=s_nero, tile=(2.0, 1.0),
         swatch=(137, "0.83,0.86,0.885,0.90"), target="#292929",
         dark="#1c1c1d", light="#434344", xlight="#c2c2c0", comb=0.9, tone=1.4, smooth=0.45, tilt=0.6),
    dict(id="cg_kamen_sery", name="Камень серый", build=s_kamen, tile=(2.0, 1.0),
         swatch=(69, "0.695,0.86,0.72,0.905"), target="#4a4a4a",
         dark="#3a3a3a", light="#5c5c5b", fleck="#6f6f6e", pore="#2c2c2c",
         comb=1.3, tone=2.2, smooth=0.22, tilt=1.6),
    dict(id="cg_sharli_keramika", name="Шарли керамика", build=s_sharli, tile=(2.0, 1.0),
         swatch=None, target="#68554e",
         dark="#54433d", light="#7d6a62", comb=1.3, tone=1.4, smooth=0.28, tilt=1.2),
    dict(id="cg_metall_bruklin", name="Металл Бруклин 808", build=s_bruklin, tile=(2.0, 1.0),
         swatch=(120, "0.715,0.865,0.738,0.90"), target="#4c4b51",
         dark="#39383e", light="#5d5c63", comb=1.5, tone=1.6, smooth=0.22, tilt=1.2),
    dict(id="cg_oniks", name="Оникс 817 TM", build=s_oniks, tile=(2.0, 1.0),
         swatch=(122, "0.749,0.865,0.772,0.90"), target="#726e65",
         dark="#4e4a44", light="#8f8b82", xlight="#bdb9af", dark_k=0.35, comb=1.1, tone=1.8, smooth=0.25, tilt=1.0),
    dict(id="cg_cherny_660", name="Черный 660 WML", build=s_wood("stones.cherny", PAT_CHERNY), tile=(2.0, 1.0),
         swatch=(79, "0.670,0.862,0.698,0.905"), target="#26252b",
         dark="#0e0d11", light="#403f48", comb=3.0, tone=0.9, smooth=0.28, tilt=4.0),
    dict(id="cg_prizma_870", name="Призма 870", build=s_prizma, tile=(2.0, 1.0),
         swatch=(118, "0.748,0.86,0.772,0.905"), target="#d5dce2",
         dark="#b9c0c7", light="#e3e8ec", dark_k=0.5, comb=0.35, tone=0.8, smooth=0.35, tilt=1.3),
    dict(id="cg_belaya_vanil", name="Белая Ваниль", build=s_wood("stones.vanil", PAT_VANIL), tile=(2.0, 1.0),
         swatch=(108, "0.80,0.87,0.845,0.905"), target="#e8e6e4",
         dark="#d8d4ce", light="#f1efed", dark_k=0.6, comb=0.45, tone=0.35, smooth=0.3, tilt=2.2),
    dict(id="cg_hdf_grafit", name="ХДФ графит текстурный", build=s_grafit, tile=(1.0, 0.5),
         swatch=None, target="#3a3b3d",
         dark="#2c2d2f", light="#4a4b4e", fleck="#56575a", comb=2.2, tone=0.9, smooth=0.2, tilt=6.0),
]

# check-sheet photo crops: ("pdf", page, "x0,y0,x1,y1") or ("site", url, (x0, y0, x1, y1) fractions)
REF_PHOTOS = {
    "cg_beton_layt": ("pdf", 137, "0.655,0.130,0.745,0.170"),
    "cg_mramor_nero_markina": ("pdf", 138, "0.795,0.855,0.868,0.905"),
    "cg_kamen_sery": ("pdf", 65, "0.400,0.510,0.485,0.640"),
    "cg_sharli_keramika": ("site", "П6.116.0.02_1.jpg", (0.10, 0.0, 0.90, 0.075)),
    "cg_metall_bruklin": ("site", "П3.0587.1.08_1.jpg", (0.08, 0.62, 0.45, 0.95)),
    "cg_oniks": ("pdf", 122, "0.340,0.720,0.405,0.890"),
    "cg_cherny_660": ("site", "П3.0556.3.33_2.jpg", (0.20, 0.32, 0.80, 0.52)),
    "cg_prizma_870": ("site", "П3.0592.1.05_1.jpg", (0.05, 0.48, 0.95, 0.90)),
    "cg_belaya_vanil": ("pdf", 108, "0.348,0.300,0.364,0.410"),
    "cg_hdf_grafit": ("pdf", 134, "0.150,0.520,0.200,0.600"),
}


# ------------------------------------------------------------------------------------------------ colour
def hex_to_srgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def srgb_to_hex(v):
    return "#%02x%02x%02x" % tuple(int(round(c)) for c in np.clip(v, 0, 255))


def lab_of_srgb(v):
    return mf.linear_to_lab(mf.srgb_to_linear(np.asarray(v, float) / 255.0))


def swatch_stat(rgb8, px_per_mm):
    """catpage.swatch's statistic of a texture: downsized to ~SWATCH_MM_PER_PX (box), trimmed sRGB mean (middle 60 %
    by brightness)."""
    f = max(1, int(round(SWATCH_MM_PER_PX * px_per_mm)))
    im = rgb8.astype(np.float64).reshape(H // f, f, W // f, f, 3).mean((1, 3)).reshape(-1, 3)
    lum = im @ [0.299, 0.587, 0.114]
    o = np.argsort(lum)
    k = len(o)
    return im[o[int(k * 0.2):int(k * 0.8)]].mean(0)


def to_rgb8(alb):
    return np.round(mf.linear_to_srgb(alb) * 255).astype(np.uint8)


def jpeg_roundtrip(rgb8):
    import io
    b = io.BytesIO()
    Image.fromarray(rgb8).save(b, "JPEG", quality=92, subsampling=0)
    return np.asarray(Image.open(io.BytesIO(b.getvalue())).convert("RGB"))


def fit_albedo(m, st):
    """albedo with the base re-solved so that swatch_stat == the target (sRGB), 5 rounds in linear light."""
    px = W / (m["tile"][0] * 1000)
    target = hex_to_srgb(m["target"])
    col_lin = mf.srgb_to_linear(target / 255)
    for _ in range(7):
        fin = dict(m, color=mf.linear_to_hex(np.clip(col_lin, 1e-4, 1)))
        alb = kit.albedo_linear(fin, st)
        got = swatch_stat(jpeg_roundtrip(to_rgb8(alb)), px)
        ratio = mf.srgb_to_linear(target / 255) / np.maximum(mf.srgb_to_linear(got / 255), 1e-5)
        col_lin = col_lin * ratio
        if np.abs(got - target).max() < 0.3:
            break
    return alb, fin


# ------------------------------------------------------------------------------------------------ write
def write(m, fin, st, alb):
    mid = m["id"]
    folder = EXT / "Materials" / mid
    folder.mkdir(parents=True, exist_ok=True)
    Image.fromarray(to_rgb8(alb)).save(folder / f"{mid}_albedo.jpg", quality=92, subsampling=0, optimize=True)
    Image.fromarray(kit.normal_map(fin, st)).save(folder / f"{mid}_normal.jpg", quality=92, subsampling=0, optimize=True)
    Image.fromarray(kit.mask_map(fin, st)).save(folder / f"{mid}_mask.png", optimize=True)


def entry(m):
    mid = m["id"]
    return {"id": mid, "name": m["name"], "category": "casegoods", "source": SOURCE, "neutral": False,
            "metersPerTile": list(m["tile"]), "maxSize": W, "folder": f"Materials/{mid}",
            "textures": {"albedo": f"{mid}_albedo.jpg", "normal": f"{mid}_normal.jpg", "mask": f"{mid}_mask.png"}}


def read_albedo(m):
    p = EXT / "Materials" / m["id"] / (m["id"] + "_albedo.jpg")
    return np.asarray(Image.open(p).convert("RGB")) if p.exists() else None


def report_row(m, rgb8):
    px = W / (m["tile"][0] * 1000)
    got = swatch_stat(rgb8, px)
    lin_mean = mf.srgb_to_linear(rgb8.reshape(-1, 3) / 255.0).mean(0)
    de = float(np.linalg.norm(lab_of_srgb(got) - lab_of_srgb(hex_to_srgb(m["target"]))))
    return dict(id=m["id"], target=m["target"], stat=srgb_to_hex(got), lin=mf.linear_to_hex(lin_mean), de=de)


# ------------------------------------------------------------------------------------------------ check sheet
def photo_crop(ref, photos):
    kind = ref[0]
    if kind == "pdf":
        sys.path.insert(0, str(ROOT / "tools" / "casegoods" / "gen"))
        import catpage
        import pymupdf
        doc = pymupdf.open(catpage.PDF)
        page = doc[ref[1] - 1]
        return catpage.render(page, 300, catpage.frac_rect(page, ref[2]))
    src = ref[1]
    name = src.rsplit("/", 1)[-1]
    path = Path(photos) / name if photos else None
    if src.startswith("http"):
        path = Path(photos) / name
        if not path.exists():
            import urllib.request
            req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
            path.write_bytes(urllib.request.urlopen(req, timeout=60).read())
    im = Image.open(path).convert("RGB")
    w, h = im.size
    x0, y0, x1, y1 = ref[2]
    return im.crop((int(w * x0), int(h * y0), int(w * x1), int(h * y1)))


def fit_h(im, hgt, max_w=None):
    w = max(1, int(im.width * hgt / im.height))
    if max_w and w > max_w:                  # very wide strips: keep their middle part
        cw = int(im.height * max_w / hgt)
        x0 = (im.width - cw) // 2
        im, w = im.crop((x0, 0, x0 + cw, im.height)), max_w
    return im.resize((w, hgt), Image.LANCZOS)


def font(size):
    from PIL import ImageFont
    for f in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def sheet(mats, rows, photos, out):
    import sys as _s
    _s.path.insert(0, str(ROOT / "tools" / "casegoods" / "gen"))
    import catpage
    import pymupdf
    doc = pymupdf.open(catpage.PDF)
    RH = 230
    tiles = []
    for m, r in zip(mats, rows):
        rgb8 = read_albedo(m)
        img = Image.fromarray(rgb8)
        px = W / (m["tile"][0] * 1000)
        cells = []
        if m["swatch"]:
            page = doc[m["swatch"][0] - 1]
            sw = catpage.render(page, 300, catpage.frac_rect(page, m["swatch"][1]))
            cells.append(("swatch p.%d %s" % (m["swatch"][0], m["target"]), fit_h(sw, RH, 3 * RH)))
            aspect = sw.width / sw.height
        else:
            cells.append(("no swatch (target %s)" % m["target"], Image.new("RGB", (RH, RH), m["target"])))
            aspect = 2.2
        try:
            cells.append(("photo", fit_h(photo_crop(REF_PHOTOS[m["id"]], photos), RH, 3 * RH)))
        except Exception as e:           # noqa: BLE001
            cells.append(("photo n/a: %s" % e, Image.new("RGB", (RH, RH), "white")))
        # texture at the swatch's scale: a chip of ~400 mm across (assumed), same aspect as the swatch
        cw = int(400 * px)
        ch = int(cw / aspect)
        cells.append(("texture 400 mm chip", fit_h(img.crop((300, 200, 300 + cw, 200 + ch)), RH)))
        # 1:1 region: 0.23 m x 0.23 m at full resolution (the pixel detail), and 1 m x 0.5 m
        c = int(230 * px)
        cells.append(("230 mm 1:1", img.crop((900, 400, 900 + c, 400 + c)).resize((RH, RH), Image.LANCZOS)))
        cells.append(("1.0 x 0.5 m", img.crop((0, 0, int(1000 * px), int(500 * px))).resize((2 * RH, RH), Image.LANCZOS)))
        # 2 x 2 tiles: seams and repetition
        t2 = Image.new("RGB", (2 * W, 2 * H))
        for ox in (0, W):
            for oy in (0, H):
                t2.paste(img, (ox, oy))
        cells.append(("2x2 tiles = %.1f x %.1f m" % (2 * m["tile"][0], 2 * m["tile"][1]), t2.resize((2 * RH, RH), Image.LANCZOS)))
        tw = sum(ci.width for _, ci in cells) + 10 * len(cells)
        tile = Image.new("RGB", (tw, RH + 34), "white")
        d = ImageDraw.Draw(tile)
        f1, f2 = font(13), font(11)
        d.text((2, 1), "%s  %s   swatch-stat %s  dE76 %.2f   linear mean %s   tile %s m" % (
            m["id"], m["name"], r["stat"], r["de"], r["lin"], m["tile"]), fill="black", font=f1)
        x = 0
        for lab, ci in cells:
            tile.paste(ci, (x, 32))
            d.text((x + 2, 18), lab, fill=(70, 70, 70), font=f2)
            x += ci.width + 10
        tiles.append(tile)
    sw_ = max(t.width for t in tiles)
    sh = Image.new("RGB", (sw_, sum(t.height + 12 for t in tiles)), "white")
    y = 0
    for t in tiles:
        sh.paste(t, (0, y))
        y += t.height + 12
    out.parent.mkdir(parents=True, exist_ok=True)
    sh.save(out)
    print("sheet", out, sh.size)


# ------------------------------------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--no-write", action="store_true", help="do not regenerate textures / entries")
    ap.add_argument("--sheet", action="store_true", help="write sheets/stones.png")
    ap.add_argument("--photos", default=None, help="directory of the site photos (downloaded there when missing)")
    ap.add_argument("--no-merge", action="store_true")
    a = ap.parse_args(argv)
    mats = [m for m in MATERIALS if not a.ids or m["id"] in a.ids]
    if a.ids and len(mats) != len(a.ids):
        sys.exit("unknown id: " + ", ".join(set(a.ids) - {m["id"] for m in MATERIALS}))
    if not a.no_write:
        for m in mats:
            st = m["build"](m["tile"])
            alb, fin = fit_albedo(m, st)
            write(m, fin, st, alb)
            print("wrote", m["id"])
    rows = []
    for m in mats:
        rgb8 = read_albedo(m)
        if rgb8 is None:
            continue
        r = report_row(m, rgb8)
        rows.append(r)
        print("%-24s target %s  texture(swatch stat) %s  dE76 %.2f  linear mean %s" % (
            r["id"], r["target"], r["stat"], r["de"], r["lin"]))
    if not a.no_write:
        done = [m for m in MATERIALS if read_albedo(m) is not None]
        ENTRIES.parent.mkdir(parents=True, exist_ok=True)
        ENTRIES.write_text(json.dumps([entry(m) for m in done], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("entries", ENTRIES)
        if not a.no_merge:
            merge_entries.merge([str(ENTRIES)])
    if a.sheet:
        sheet([m for m in mats if read_albedo(m) is not None], rows, a.photos, SHEET)


if __name__ == "__main__":
    main()
