#!/usr/bin/env python3
"""Door finish textures: the wood-imitating films of the DveriMebel / el'PORTA catalogue (2020), made procedurally.

    python3 tools/doors/textures/make_finishes.py                       # every finish of FINISHES
    python3 tools/doors/textures/make_finishes.py golden-reef 3d-grey   # only these
    python3 tools/doors/textures/make_finishes.py --compare             # + tools/doors/.cache/finishes_compare.png
    python3 tools/doors/textures/make_finishes.py --no-write --compare  # check sheet only
    python3 tools/doors/textures/make_finishes.py --fit [ids]           # suggest `comb` / `tone` from the photos

Needs numpy and Pillow (the catalogue photos of tools/doors/.cache, see tools/doors/catalog_index.py, only for
--compare / --fit). Deterministic: all random draws come from the patterns' fixed seeds. Writes per finish (M =
material id):

    Assets/House4696/External/Materials/M/M_albedo.jpg  sRGB 2048x1024, grain along U (image x), tile 2.0 m x 1.0 m
    Assets/House4696/External/Materials/M/M_normal.jpg  tangent space, OpenGL (+Y = green = up), 1024x512
    Assets/House4696/External/Materials/M/M_mask.png    R metallic 0, G occlusion 255, B 0, A smoothness, 256x128
    Assets/House4696/External/external.json             its "door_*" material entries (all other entries untouched)

Model. A pattern (PATTERNS) builds the film's structure once; the finishes of a pattern are colourways of one
printed film and share it:
  * comb - laminations across the grain (fine-line films are printed from laminated veneer): layers ~1 mm thick
    whose tone alternates from layer to layer and drifts along the grain, drawn with exact pixel coverage (crisp);
  * dark / light lines on top - pores and light streaks with a width, a length with soft ends and an opacity that
    comes and goes along them;
  * bands and clusters - broad and medium tone variation, strongly elongated along the grain (no blotches);
  * one smooth cross-grain wander (warp) moves all of it; the broad tone wanders more (flame-like figure).
  Everything is built on the torus (FFT noise, lines drawn modulo the tile), so the maps tile in both directions.
A finish (FINISHES) colours it in linear RGB: the ground follows the tone (in L* units: `comb` x fine lines +
`tone` x bands), getting darker towards the `dark` colour and lighter towards the `light` colour, and the distinct
lines are the `dark` / `light` colours at full opacity - so streaks differ in hue as the film's do. The base colour
is then solved per channel so that the texture's mean (in linear light, i.e. seen from afar) is exactly `color`.
The normal map embosses the dark lines and the darker laminations (rms tilt `relief.tilt_deg`); the mask's
smoothness is the satin lacquer's (`smooth`), a little lower where the pores are dense.

Fitting (the numbers in FINISHES; --compare shows the result):
  * color - the mean of the REFS crops (flat areas: stiles, flat leaves) of the catalogue renders in linear light;
  * dark / light - their a*, b* follow the photos' slopes of a*, b* against L* inside those areas (the hue of the
    streaks); their lightness is how much the distinct lines stand out (chosen by eye);
  * comb / tone (--fit) - the texture is shown the way the photo shows it: downsized to the photo's scale
    (Lanczos in sRGB; ~0.4 px/mm for the big photos, ~0.16 for the small ones) and JPEG-compressed with the photo's
    own quantization tables; then comb and tone are least-squares fitted to the photos' L* contrast: `sx` (across the
    grain in 80 mm windows), `fine` (pixel to pixel) and `band` (wider than ~15 mm). The catalogue renders look
    sharpened (their contrast rises towards the pixel scale), so `fine` stays somewhat under the photos' value:
    the texture keeps a natural spectrum instead of copying the sharpening.
The albedo is written as 8-bit JPEG, which drops chroma offsets under ~0.5 level: near-neutral films (the greys)
lose their faint tint (dE76 < 1); the --compare table is measured on the written files.

To add a finish: a FINISHES row plus REFS crops of its photos, then --fit, paste comb / tone, --compare and look at
the sheet. A different film structure (oak, crosscut, softwood, ...) is a new PATTERNS entry.
"""
import argparse
import io
import json
import math
import sys
from pathlib import Path

try:
    import fcntl                     # the manifest lock (POSIX); without it the merge simply is not serialised
except ImportError:
    fcntl = None

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXT = ROOT / "Assets" / "House4696" / "External"
CACHE = ROOT / "tools" / "doors" / ".cache"
SOURCE = "procedural:tools/doors/textures/make_finishes.py"

TILE_M = (2.0, 1.0)            # along the grain (U, image x) x across (V, image y)
ALBEDO = (2048, 1024)          # ~1 px/mm
NORMAL = (1024, 512)
MASK = (256, 128)
MM = TILE_M[0] * 1000 / ALBEDO[0]   # mm per albedo pixel (square pixels: 2000/2048 = 1000/1024)

# ------------------------------------------------------------------------------------------------ structures
# Lengths in mm. warp = octaves (amplitude, correlation along, across) of the cross-grain wander shared by all
# fields; band_warp = extra wander of the broad tone only (flame-like figure).
# comb: the laminations the film is printed from - layer thickness (median, log-sigma), rho = likeness of neighbours,
#       drift = share of each layer's tone that changes along the grain, over drift_len.
# dark / light: distinct lines over it - per_cm = lines met in any 10 mm across, width / length = (median,
#       log-sigma), alpha = opacity range, fade = along-grain opacity modulation (0 steady .. 1 comes and goes over
#       fade_len), slope = max drift across per mm along.
# bands / cluster: broad and medium tone variation (sigma across, sigma along); fibre: faint fibre noise.
# relief: what the embossing follows (weights), rms tilt of the normals.
PATTERNS = {
    # ЭкоШпон Veralinga: dense fine combed lines, short light streaks, soft bands
    "veralinga": dict(
        seed=4211, warp=[(1.3, 260.0, 25.0), (0.2, 60.0, 6.0)], band_warp=(3.0, 300.0, 40.0),
        comb=dict(thickness=(0.9, 0.6), rho=-0.5, drift=0.7, drift_len=35.0, hp=3.5, mod=(0.35, 15.0, 250.0)),
        dark=dict(per_cm=0.8, width=(0.45, 0.4), length=(250.0, 0.9), alpha=(0.3, 1.0), fade=0.8, slope=0.003),
        light=dict(per_cm=0.5, width=(0.7, 0.45), length=(70.0, 0.8), alpha=(0.3, 1.0), fade=0.8, slope=0.003),
        fade_len=18.0, bands=(20.0, 900.0), cluster=(3.0, 110.0), cluster_share=0.5, fibre=(0.4, 3.0), fibre_share=0.14,
        relief=dict(comb=0.5, groove=1.0, fibre=0.2, tilt_deg=3.0),
    ),
    # 3D-Graf: finer, wavier lines with short dark pore dashes, deeper emboss
    "graf3d": dict(
        seed=7331, warp=[(1.5, 250.0, 30.0), (0.9, 45.0, 6.0)], band_warp=(3.0, 300.0, 35.0),
        comb=dict(thickness=(0.8, 0.6), rho=-0.45, drift=0.8, drift_len=22.0, hp=3.5, mod=(0.4, 12.0, 160.0)),
        dark=dict(per_cm=1.6, width=(0.45, 0.4), length=(45.0, 0.7), alpha=(0.3, 1.0), fade=0.5, slope=0.006),
        light=dict(per_cm=1.3, width=(0.6, 0.45), length=(130.0, 0.8), alpha=(0.3, 1.0), fade=0.8, slope=0.004),
        fade_len=20.0, bands=(16.0, 800.0), cluster=(2.5, 130.0), cluster_share=0.5, fibre=(0.4, 3.0), fibre_share=0.14,
        relief=dict(comb=0.6, groove=1.0, fibre=0.25, tilt_deg=4.0),
    ),
    # Golden Reef: teak-like - fine lines under broad flowing bands of orange and reddish brown
    "reef": dict(
        seed=1907, warp=[(1.5, 400.0, 50.0), (0.25, 60.0, 10.0)], band_warp=(9.0, 260.0, 45.0),
        comb=dict(thickness=(1.2, 0.65), rho=-0.3, drift=0.6, drift_len=120.0, hp=5.0, mod=(0.4, 20.0, 400.0)),
        dark=dict(per_cm=0.3, width=(1.0, 0.7), length=(450.0, 0.8), alpha=(0.25, 0.9), fade=0.5, slope=0.001),
        light=dict(per_cm=0.3, width=(1.2, 0.6), length=(350.0, 0.8), alpha=(0.25, 0.8), fade=0.5, slope=0.001),
        fade_len=80.0, bands=(13.0, 520.0), cluster=(4.0, 260.0), cluster_share=0.35, fibre=(0.4, 6.0),
        fibre_share=0.15,
        relief=dict(comb=0.5, groove=1.0, fibre=0.2, tilt_deg=2.5),
    ),
}

# ------------------------------------------------------------------------------------------------ finishes
# pattern / scale: the structure and its size (scale > 1 = every streak wider and longer; optional seed = another
# print of the same kind); color: catalogue mean (sRGB); dark / light: colour of a full-strength dark / light line
# on it; comb: L* std of the fine lines at 1 px/mm; tone: L* std of the bands and clusters; smooth: satin lacquer
# smoothness (mask alpha / 255).
FINISHES = [
    dict(id="cappuccino-veralinga", material="door_cappuccino_veralinga", name="Cappuccino Veralinga (ЭкоШпон)",
         pattern="veralinga", scale=1.0, color="#c6b9af", dark="#938379", light="#e1d5cd",
         comb=2.14, tone=1.71, smooth=0.40),
    dict(id="grey-veralinga", material="door_grey_veralinga", name="Grey Veralinga (ЭкоШпон)",
         pattern="veralinga", scale=1.0, color="#828182", dark="#434242", light="#b1b0b2",
         comb=5.21, tone=2.73, smooth=0.40),
    dict(id="wenge-veralinga", material="door_wenge_veralinga", name="Wenge Veralinga (ЭкоШпон)",
         pattern="veralinga", scale=1.0, color="#3a2c2b", dark="#221514", light="#504241",
         comb=2.15, tone=1.55, smooth=0.42),
    dict(id="bianco-veralinga", material="door_bianco_veralinga", name="Bianco Veralinga (ЭкоШпон)",
         pattern="veralinga", scale=1.0, color="#d8d8d3", dark="#b7b7b1", light="#e7e9e4",
         comb=1.26, tone=1.17, smooth=0.40),
    dict(id="snow-veralinga", material="door_snow_veralinga", name="Snow Veralinga (ЭкоШпон)",
         pattern="veralinga", scale=1.0, color="#ececec", dark="#d9d9d9", light="#f7f7f7",
         comb=0.93, tone=0.72, smooth=0.40),
    dict(id="anegri-veralinga", material="door_anegri_veralinga", name="Anegri Veralinga (ЭкоШпон)",
         pattern="veralinga", scale=1.0, color="#c39768", dark="#92683b", light="#ddb281",
         comb=2.59, tone=2.40, smooth=0.40),
    dict(id="golden-reef", material="door_golden_reef", name="Golden Reef (ЭкоШпон)",
         pattern="reef", scale=1.0, color="#ac7049", dark="#6b3b2f", light="#ca8952",
         comb=2.43, tone=3.68, smooth=0.40),
    dict(id="3d-cappuccino", material="door_3d_cappuccino", name="3D Cappuccino (3D-Graf)",
         pattern="graf3d", scale=1.0, color="#c3b6ac", dark="#908277", light="#e9dbd2",
         comb=3.85, tone=1.15, smooth=0.38),
    dict(id="3d-grey", material="door_3d_grey", name="3D Grey (3D-Graf)",
         pattern="graf3d", scale=1.0, color="#868586", dark="#4f4e4f", light="#afaeaf",
         comb=2.98, tone=1.75, smooth=0.38),
    dict(id="3d-wenge", material="door_3d_wenge", name="3D Wenge (3D-Graf)",
         pattern="graf3d", scale=1.0, color="#352016", dark="#211008", light="#493327",
         comb=2.38, tone=0.35, smooth=0.40),
]

# Flat, vertical-grain areas of the catalogue photos (tools/doors/.cache/photos, see tools/doors/catalog_index.py):
# (file, (x0, y0, x1, y1)). The first one of each finish is shown on the check sheet.
REFS = {
    "cappuccino-veralinga": [
        ("p019_porta-11-tmf__cappuccino-veralinga.jpg", (150, 40, 300, 790)),
        ("p020_porta-21__cappuccino-veralinga.jpg", (31, 30, 62, 395)),
        ("p020_porta-21__cappuccino-veralinga.jpg", (301, 30, 339, 790)),
        ("p022_porta-23-mf__cappuccino-veralinga.jpg", (31, 30, 70, 395)),
        ("p022_porta-23-mf__cappuccino-veralinga.jpg", (301, 30, 339, 790)),
        ("p023_porta-24-mf__cappuccino-veralinga.jpg", (85, 85, 150, 385)),
        ("p023_porta-24-mf__cappuccino-veralinga.jpg", (225, 85, 290, 760)),
        ("p024_porta-25-mf-alu__cappuccino-veralinga.jpg", (245, 85, 290, 760)),
        ("p147_porta-21__cappuccino-veralinga.jpg", (140, 30, 180, 790)),
    ],
    "grey-veralinga": [
        ("p037_trend-0__grey-veralinga.jpg", (35, 40, 339, 390)),
        ("p037_trend-0__grey-veralinga.jpg", (35, 450, 339, 795)),
        ("p025_porta-26__grey-veralinga.jpg", (31, 30, 70, 395)),
        ("p025_porta-26__grey-veralinga.jpg", (302, 30, 339, 790)),
        ("p026_porta-27-mf__grey-veralinga.jpg", (29, 30, 60, 395)),
    ],
    "wenge-veralinga": [
        ("p023_porta-24-mf__wenge-veralinga.jpg", (85, 85, 150, 385)),
        ("p023_porta-24-mf__wenge-veralinga.jpg", (225, 85, 290, 760)),
        ("p065_s-13-print__wenge-veralinga.jpg", (300, 60, 338, 790)),
        ("p149_porta-23__wenge-veralinga.jpg", (140, 30, 180, 790)),
        ("p131_porta-23-1p-03__wenge-veralinga.jpg", (300, 60, 338, 790)),
        ("p133_porta-21-1p-02-wc__wenge-veralinga.jpg", (300, 60, 338, 790)),
    ],
    "bianco-veralinga": [
        ("p149_porta-23__bianco-veralinga.jpg", (140, 30, 180, 790)),
        ("p130_porta-21-1p-03__bianco-veralinga.jpg", (300, 60, 338, 790)),
        ("p131_porta-23-1p-03__bianco-veralinga.jpg", (300, 60, 338, 790)),
        ("p133_porta-21-1p-02-wc__bianco-veralinga.jpg", (300, 60, 338, 790)),
        ("p134_porta-22-1p-02-wc__bianco-veralinga.jpg", (300, 60, 338, 790)),
    ],
    "snow-veralinga": [
        ("p037_trend-0__snow-veralinga.jpg", (18, 20, 135, 165)),
        ("p037_trend-0__snow-veralinga.jpg", (18, 190, 135, 330)),
        ("p020_porta-21__snow-veralinga.jpg", (13, 15, 28, 165)),
        ("p020_porta-21__snow-veralinga.jpg", (123, 15, 138, 330)),
        ("p022_porta-23-mf__snow-veralinga.jpg", (123, 15, 138, 330)),
        ("p021_porta-22-mf__snow-veralinga.jpg", (123, 15, 138, 330)),
    ],
    "anegri-veralinga": [
        ("p147_porta-21__anegri-veralinga.jpg", (140, 30, 180, 790)),
        ("p147_porta-21__anegri-veralinga.jpg", (30, 30, 70, 380)),
        ("p148_porta-22__anegri-veralinga.jpg", (140, 30, 180, 790)),
        ("p148_porta-22__anegri-veralinga.jpg", (30, 30, 70, 380)),
        ("p130_porta-21-1p-03__anegri-veralinga.jpg", (122, 15, 138, 330)),
        ("p133_porta-21-1p-02-wc__anegri-veralinga.jpg", (122, 15, 138, 330)),
    ],
    "golden-reef": [
        ("p041_klassiko-12__golden-reef.jpg", (62, 52, 108, 148)),
        ("p020_porta-21__golden-reef.jpg", (122, 14, 138, 330)),
        ("p020_porta-21__golden-reef.jpg", (13, 14, 29, 165)),
        ("p021_porta-22-mf__golden-reef.jpg", (122, 14, 138, 330)),
        ("p022_porta-23-mf__golden-reef.jpg", (122, 14, 138, 330)),
        ("p053_legno-21__golden-reef.jpg", (122, 14, 138, 330)),
        ("p055_legno-23__golden-reef.jpg", (122, 14, 138, 330)),
    ],
    "3d-cappuccino": [
        ("p014_gleys-1-sprig__3d-cappuccino.jpg", (150, 40, 338, 800)),
        ("p010_porta-23__3d-cappuccino.jpg", (31, 30, 70, 395)),
        ("p010_porta-23__3d-cappuccino.jpg", (302, 30, 339, 800)),
        ("p010_porta-25-alu__3d-cappuccino.jpg", (245, 85, 290, 780)),
    ],
    "3d-grey": [
        ("p011_trend-0__3d-grey.jpg", (35, 40, 339, 400)),
        ("p011_trend-0__3d-grey.jpg", (35, 460, 339, 810)),
        ("p011_porta-29__3d-grey.jpg", (302, 30, 339, 800)),
    ],
    "3d-wenge": [
        ("p014_gleys-1-sprig__3d-wenge.jpg", (150, 40, 338, 800)),
        ("p009_porta-21__3d-wenge.jpg", (31, 30, 70, 395)),
        ("p009_porta-21__3d-wenge.jpg", (302, 30, 339, 800)),
        ("p009_porta-22__3d-wenge.jpg", (302, 30, 339, 800)),
    ],
}
PHOTO_MM = 2080.0      # a catalogue photo's height covers the leaf (2000 mm) and the top of the frame
SX_WINDOW_MM = 80.0    # window of the cross-grain contrast statistic


# ------------------------------------------------------------------------------------------------ colour
_M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750], [0.0193339, 0.1191920, 0.9503041]])
_WHITE = np.array([0.95047, 1.0, 1.08883])


def srgb_to_linear(s):
    s = np.asarray(s, dtype=np.float64)
    return np.where(s <= 0.04045, s / 12.92, ((s + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(v):
    v = np.clip(np.asarray(v, dtype=np.float64), 0.0, 1.0)
    return np.where(v <= 0.0031308, 12.92 * v, 1.055 * v ** (1 / 2.4) - 0.055)


def linear_to_lab(rgb):
    xyz = np.asarray(rgb, dtype=np.float64) @ _M.T / _WHITE
    d = 6 / 29
    f = np.where(xyz > d ** 3, np.cbrt(xyz), xyz / (3 * d * d) + 4 / 29)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])], -1)


def hex_to_linear(h):
    h = h.lstrip("#")
    return srgb_to_linear(np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255.0)


def linear_to_hex(v):
    s = np.round(linear_to_srgb(v) * 255).astype(int)
    return "#%02x%02x%02x" % tuple(s)


# ------------------------------------------------------------------------------------------------ fields
def gauss_noise(rng, shape, sig_x, sig_y):
    """Periodic noise with a Gaussian correlation (sigmas in px along x = columns and y = rows), zero mean, unit std."""
    h, w = shape
    spec = np.fft.rfft2(rng.standard_normal(shape))
    fy = np.fft.fftfreq(h)[:, None]
    fx = np.fft.rfftfreq(w)[None, :]
    spec *= np.exp(-2 * np.pi ** 2 * ((fx * sig_x) ** 2 + (fy * sig_y) ** 2))
    n = np.fft.irfft2(spec, s=shape)
    n -= n.mean()
    return n / n.std()


def noise_1d(rng, n, sig):
    """Long 1D noise table (periodic), Gaussian correlation `sig` samples, unit std."""
    spec = np.fft.rfft(rng.standard_normal(n))
    spec *= np.exp(-2 * np.pi ** 2 * (np.fft.rfftfreq(n) * sig) ** 2)
    t = np.fft.irfft(spec, n=n)
    t -= t.mean()
    return t / t.std()


def warp_rows(field, disp):
    """field(x, y + disp(x, y)), linear along y, periodic."""
    h, w = field.shape
    y = np.arange(h)[:, None] + disp
    y0 = np.floor(y).astype(np.int64)
    t = y - y0
    cols = np.arange(w)[None, :]
    return field[y0 % h, cols] * (1 - t) + field[(y0 + 1) % h, cols] * t


def highpass_across(field, sig):
    """Removes the variation across the grain (rows) wider than ~sig px (Gaussian, periodic)."""
    h = field.shape[0]
    f = np.fft.rfft(field, axis=0)
    f *= 1 - np.exp(-2 * np.pi ** 2 * (np.fft.rfftfreq(h)[:, None] * sig) ** 2)
    return np.fft.irfft(f, n=h, axis=0)


def draw_lines(rng, acc, spec, disp, env_table, px):
    """Accumulates -log(1 - opacity) of thin lines along x into acc (rows = across, cols = along); px = pixels per mm
    of the pattern."""
    h, w = acc.shape
    width_med, width_sig = spec["width"]
    len_med, len_sig = spec["length"]
    mean_len = len_med * math.exp(len_sig ** 2 / 2) * px
    count = int(round(spec["per_cm"] * (h / px / 10.0) * w / min(mean_len, w)))
    ys = rng.uniform(0, h, count)
    widths = np.clip(width_med * np.exp(width_sig * rng.standard_normal(count)), 0.2, 6.0) * px
    lengths = np.clip(len_med * np.exp(len_sig * rng.standard_normal(count)), 8.0, 0.95 * w / px) * px
    x0s = rng.integers(0, w, count)
    alphas = rng.uniform(*spec["alpha"], count)
    slopes = rng.uniform(-spec["slope"], spec["slope"], count)
    offs = rng.integers(0, len(env_table), count)
    fade = spec["fade"]
    for y, wd, ln, x0, a, sl, off in zip(ys, widths, lengths, x0s, alphas, slopes, offs):
        n = max(4, int(ln))
        s = np.arange(n)
        xs = (x0 + s) % w
        # soft ends (raised cosine over ~20% of the length at each end) and fading along the line
        taper = np.minimum(1.0, np.minimum(s + 0.5, n - 0.5 - s) / max(2.0, 0.2 * n))
        taper = 0.5 - 0.5 * np.cos(np.pi * taper)
        e = env_table[(off + s) % len(env_table)]
        env = taper * np.clip(1.0 - fade * 0.5 + fade * 0.5 * e, 0.0, 1.0)
        yi = int(math.floor(y))
        t = y - yi
        yc = y + disp[yi % h, xs] * (1 - t) + disp[(yi + 1) % h, xs] * t + sl * (s - n / 2)
        hw = wd / 2
        r0 = int(math.floor(yc.min() - hw - 0.5))
        r1 = int(math.ceil(yc.max() + hw + 0.5))
        rows = np.arange(r0, r1 + 1)[:, None]
        cov = np.clip(np.minimum(yc + hw, rows + 0.5) - np.maximum(yc - hw, rows - 0.5), 0.0, 1.0)
        op = np.clip(a * env * cov, 0.0, 0.97)
        acc[np.ix_(rows[:, 0] % h, xs)] += -np.log1p(-op)


def periodic_integral(y, cum, edges):
    """Integral from 0 to y of a periodic piecewise-constant profile (cum = its integral at the edges)."""
    period = edges[-1]
    q = np.floor(y / period)
    return q * cum[-1] + np.interp(y - q * period, edges, cum)


def comb_field(rng, spec, disp, px):
    """Laminations across the grain (what a fine-line film is printed from): layers of random thickness, each with a
    tone that drifts along the grain, following the warp. Box-filtered per pixel (crisp edges); zero mean, unit std."""
    w, h = ALBEDO
    med, sig = spec["thickness"]
    th, total = [], 0.0
    while total < h / px:                                   # mm of the pattern across the tile
        t = min(8.0, max(0.25, med * math.exp(sig * rng.standard_normal())))
        th.append(t)
        total += t
    th = np.array(th) * (h / total)                        # px, exactly one tile across
    edges = np.concatenate([[0.0], np.cumsum(th)])
    k = len(th)
    rho = spec["rho"]
    g = rng.standard_normal(k)
    b = np.empty(k)
    b[0] = g[0]
    for i in range(1, k):
        b[i] = rho * b[i - 1] + math.sqrt(1 - rho * rho) * g[i]
    m = spec["drift"]
    tone = math.sqrt(1 - m * m) * b[:, None] + m * gauss_noise(rng, (k, w), spec["drift_len"] * px, 0.6)
    cum = np.concatenate([np.zeros((1, w)), np.cumsum(tone * th[:, None], 0)], 0)     # integral at the edges
    rows = np.arange(h, dtype=np.float64)
    out = np.empty((h, w))
    for x in range(w):
        y = rows - disp[:, x]                               # layer-space coordinate shown by each pixel
        out[:, x] = periodic_integral(y + 0.5, cum[:, x], edges) - periodic_integral(y - 0.5, cum[:, x], edges)
    # the laminations carry the fine lines only: their broad variation is left to the band / cluster fields
    out = highpass_across(out, spec["hp"] * px)
    # line contrast itself varies over the surface (patches where the lines are crisper or fainter)
    amount, sa, sl = spec["mod"]
    out *= np.clip(1 + amount * warp_rows(gauss_noise(rng, (h, w), sl * px, sa * px), disp), 0.2, None)
    return out / out.std()


def structure(pattern_id, scale=1.0, seed=None):
    """The pattern's fields at albedo resolution: dark / light line opacity, fine and broad tone (unit std).
    scale > 1 makes every feature of the pattern larger; seed replaces the pattern's own."""
    p = PATTERNS[pattern_id]
    rng = np.random.default_rng(p["seed"] if seed is None else seed)
    px = scale / MM                                         # albedo pixels per mm of the pattern
    w, h = ALBEDO
    disp = np.zeros((h, w))
    for amp, along, across in p["warp"]:
        disp += gauss_noise(rng, (h, w), along * px, across * px) * (amp * px)
    comb = comb_field(rng, p["comb"], disp, px)
    env_table = noise_1d(rng, 1 << 18, p["fade_len"] * px)
    acc_d = np.zeros((h, w))
    acc_l = np.zeros((h, w))
    draw_lines(rng, acc_d, p["dark"], disp, env_table, px)
    draw_lines(rng, acc_l, p["light"], disp, env_table, px)
    amp, along, across = p["band_warp"]                     # the broad tone wanders more: flame-like figure
    bdisp = disp + gauss_noise(rng, (h, w), along * px, across * px) * (amp * px)
    bands = warp_rows(gauss_noise(rng, (h, w), p["bands"][1] * px, p["bands"][0] * px), bdisp)
    cluster = warp_rows(gauss_noise(rng, (h, w), p["cluster"][1] * px, p["cluster"][0] * px), bdisp)
    fibre = gauss_noise(rng, (h, w), p["fibre"][1] * px, p["fibre"][0] * px)
    cs, fs = p["cluster_share"], p["fibre_share"]
    broad = math.sqrt(1 - cs) * bands + math.sqrt(cs) * cluster
    fine = math.sqrt(1 - fs) * comb + math.sqrt(fs) * fibre
    return dict(dark=1 - np.exp(-acc_d), light=1 - np.exp(-acc_l), fine=fine / fine.std(), broad=broad / broad.std(),
                comb=comb, fibre=fibre, relief=p["relief"])


def finish_structure(fin, cache):
    """structure() of a finish, shared by the finishes of the same pattern, scale and seed."""
    key = (fin["pattern"], fin.get("scale", 1.0), fin.get("seed"))
    if key not in cache:
        cache[key] = structure(*key)
    return cache[key]


# ------------------------------------------------------------------------------------------------ maps
def albedo_linear(fin, st):
    """Linear-RGB albedo (h, w, 3) of a finish."""
    col = hex_to_linear(fin["color"])
    rd = np.clip(hex_to_linear(fin["dark"]) / col, 0.03, 1.0)     # full-strength line colours relative to the mean
    rl = np.clip(hex_to_linear(fin["light"]) / col, 1.0, 30.0)
    Lc = linear_to_lab(col)[0]
    dLd = max(1e-3, Lc - linear_to_lab(col * rd)[0])
    dLl = max(1e-3, linear_to_lab(col * rl)[0] - Lc)
    # ground: tone in L* units, darker along the dark colour, lighter along the light colour
    t = (fin["comb"] * st["fine"] + fin["tone"] * st["broad"])[..., None]
    g = np.where(t < 0, np.exp(-t / dLd * np.log(rd)), np.exp(t / dLl * np.log(rl)))
    out = g * (1 - st["dark"][..., None] * (1 - rd)) * (1 + st["light"][..., None] * (rl - 1))
    base = col / out.reshape(-1, 3).mean(0, dtype=np.float64)
    for _ in range(3):                         # clipping at 1 (white films) shifts the mean: re-solve
        a = np.clip(out * base, 0, 1)
        base *= col / a.reshape(-1, 3).mean(0, dtype=np.float64)
    return np.clip(out * base, 0, 1)


def box_down(a, f):
    """Area average by an integer factor (periodic sizes are multiples)."""
    h, w = a.shape[:2]
    return a.reshape(h // f, f, w // f, f, *a.shape[2:]).mean((1, 3))


def normal_map(st):
    rel = st["relief"]
    # embossing: darker laminations and the dark lines are pressed in, faint fibre texture on top
    hgt = -rel["comb"] * 0.25 * st["comb"] - rel["groove"] * st["dark"] + rel["fibre"] * 0.25 * st["fibre"]
    f = ALBEDO[0] // NORMAL[0]
    hgt = box_down(hgt, f)
    gx = (np.roll(hgt, -1, 1) - np.roll(hgt, 1, 1)) / 2          # d/dx (U, right)
    gr = (np.roll(hgt, -1, 0) - np.roll(hgt, 1, 0)) / 2          # d/drow (down the image = -V)
    slope = np.sqrt(gx ** 2 + gr ** 2)
    k = math.tan(math.radians(rel["tilt_deg"])) / max(1e-9, np.sqrt((slope ** 2).mean()))
    n = np.stack([-gx * k, gr * k, np.ones_like(gx)], -1)          # OpenGL: +Y (green) = up = -row
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return np.round((n * 0.5 + 0.5) * 255).astype(np.uint8)


def mask_map(fin, st):
    f = ALBEDO[0] // MASK[0]
    d = box_down(st["dark"], f)
    d = (d - d.mean()) / max(1e-9, d.std())
    sm = np.clip(fin["smooth"] * 255 - 3.0 * d, 90, 115)
    m = np.zeros((MASK[1], MASK[0], 4), np.uint8)
    m[..., 1] = 255
    m[..., 3] = np.round(sm).astype(np.uint8)
    return m


def write_finish(fin, st, alb):
    mid = fin["material"]
    folder = EXT / "Materials" / mid
    folder.mkdir(parents=True, exist_ok=True)
    rgb = np.round(linear_to_srgb(alb) * 255).astype(np.uint8)
    Image.fromarray(rgb).save(folder / f"{mid}_albedo.jpg", quality=90, subsampling=0, optimize=True)
    Image.fromarray(normal_map(st)).save(folder / f"{mid}_normal.jpg", quality=92, subsampling=0, optimize=True)
    Image.fromarray(mask_map(fin, st)).save(folder / f"{mid}_mask.png", optimize=True)


def manifest_entry(fin):
    mid = fin["material"]
    return {"id": mid, "name": fin["name"], "category": "door", "source": SOURCE, "neutral": False,
            "metersPerTile": list(TILE_M), "maxSize": ALBEDO[0], "folder": f"Materials/{mid}",
            "textures": {"albedo": f"{mid}_albedo.jpg", "normal": f"{mid}_normal.jpg", "mask": f"{mid}_mask.png"}}


def update_manifest(fins):
    """Replaces (in place) or appends the finishes' entries of external.json; every other entry stays byte for byte.
    Takes the lock of tools/doors/textures/merge_entries.py, so concurrent writers do not lose each other's entries."""
    path = EXT / "external.json"
    lock_path = ROOT / ".cache" / "external.json.lock"          # outside Assets: Unity would import it
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_path, "w") as lock:
        if fcntl:
            fcntl.flock(lock, fcntl.LOCK_EX)
        manifest = json.loads(path.read_text(encoding="utf-8"))
        mats = manifest["materials"]
        index = {m["id"]: i for i, m in enumerate(mats)}
        for fin in fins:
            e = manifest_entry(fin)
            if e["id"] in index:
                mats[index[e["id"]]] = e
            else:
                index[e["id"]] = len(mats)
                mats.append(e)
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")


# ------------------------------------------------------------------------------------------------ check sheet
def blur(a, sy, sx):
    """Separable Gaussian blur (sigmas in px along rows / columns), edges reflected."""
    for axis, sig in ((0, sy), (1, sx)):
        if sig < 0.3:
            continue
        r = min(int(3 * sig + 0.5), a.shape[axis] - 1)
        k = np.exp(-0.5 * (np.arange(-r, r + 1) / sig) ** 2)
        pad = [(0, 0), (0, 0)]
        pad[axis] = (r, r)
        win = np.lib.stride_tricks.sliding_window_view(np.pad(a, pad, mode="reflect"), 2 * r + 1, axis=axis)
        a = win @ (k / k.sum())
    return a


def lab_stats(lin, px_per_mm):
    """Mean colour (linear) and L* contrast of a grain-vertical area: `sx` = across the grain in SX_WINDOW_MM windows,
    `fine` = its finest part (pixel to pixel), `band` = the broad variation (wider than ~15 mm, longer than ~60 mm)."""
    L = linear_to_lab(lin)[..., 0]
    h, w = L.shape
    win = max(3, min(w, int(round(SX_WINDOW_MM * px_per_mm))))
    sx = np.mean([L[:, x:x + win].std(1).mean() for x in range(0, w - win + 1, win)])
    fine = (L[:, 1:-1] - (L[:, :-2] + L[:, 1:-1] + L[:, 2:]) / 3).std()
    b = blur(L, 30 * px_per_mm, 6 * px_per_mm)
    yy, xx = np.mgrid[0:h, 0:w]
    plane = np.linalg.lstsq(np.stack([np.ones(h * w), yy.ravel(), xx.ravel()], 1), b.ravel(), rcond=None)[0]
    band = (b.ravel() - np.stack([np.ones(h * w), yy.ravel(), xx.ravel()], 1) @ plane).std()   # lighting removed
    return dict(mean=lin.reshape(-1, 3).mean(0, dtype=np.float64), sx=float(sx), fine=float(fine), band=float(band))


def photo(fname):
    return Image.open(CACHE / "photos" / fname)


def photo_crop(fname, box):
    im = photo(fname)
    lin = srgb_to_linear(np.asarray(im.convert("RGB").crop(box), dtype=np.float64) / 255)
    return lin, im.height / PHOTO_MM


def as_photo(alb, fname):
    """The texture the way a catalogue photo shows it: grain vertical, downsized to the photo's scale (Lanczos in sRGB,
    like an image editor's downsizing) and JPEG-compressed with the photo's own quantization tables (4:2:0)."""
    ref = photo(fname)
    scale = ref.height / PHOTO_MM
    v = np.transpose(alb, (1, 0, 2))                     # rows = along the grain, cols = across
    size = (int(round(v.shape[1] * MM * scale)), int(round(v.shape[0] * MM * scale)))
    img = Image.fromarray(np.round(linear_to_srgb(v) * 255).astype(np.uint8)).resize(size, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", qtables=ref.quantization, subsampling=2)
    return srgb_to_linear(np.asarray(Image.open(buf).convert("RGB"), dtype=np.float64) / 255)


STATS = ("sx", "fine", "band")


def measure(fin, alb):
    """Photo vs texture statistics over the finish's REFS crops (texture: same-size crops at random places)."""
    rng = np.random.default_rng(1)
    pm, wsum, ph, tx = np.zeros(3), 0.0, [], []
    shown = {}
    for fname, box in REFS[fin["id"]]:
        lin, scale = photo_crop(fname, box)
        if fname not in shown:
            shown[fname] = as_photo(alb, fname)
        tex = shown[fname]
        ch, cw = lin.shape[:2]
        ts = []
        for _ in range(8):
            y0 = rng.integers(0, max(1, tex.shape[0] - ch))
            x0 = rng.integers(0, max(1, tex.shape[1] - cw))
            ts.append(lab_stats(tex[y0:y0 + ch, x0:x0 + cw], scale))
        wgt = math.sqrt(ch * cw)
        ps = lab_stats(lin, scale)
        pm += wgt * ps["mean"]
        wsum += wgt
        ph.append([ps[k] for k in STATS])
        tx.append([np.mean([t[k] for t in ts]) for k in STATS])
    pm /= wsum
    tm = alb.reshape(-1, 3).mean(0, dtype=np.float64)
    plab, tlab = linear_to_lab(pm), linear_to_lab(tm)
    ph, tx = np.mean(ph, 0), np.mean(tx, 0)
    out = dict(id=fin["id"], photo=pm, tex=tm, plab=plab, tlab=tlab, de=float(np.linalg.norm(plab - tlab)), shown=shown)
    for i, k in enumerate(STATS):
        out["p" + k], out["t" + k] = float(ph[i]), float(tx[i])
    return out


def fit(fin, st, rounds=2):
    """Suggests `comb` and `tone` of a finish so that the texture, seen like its photos, has the photos' contrast
    statistics (STATS). Model: each statistic squared is linear in comb^2 and tone^2; least squares on relative
    errors with comb, tone >= 0.2."""
    f = dict(fin)
    for _ in range(rounds):
        c, t = max(0.3, f["comb"]), max(0.3, f["tone"])
        rows, got = [], []
        for pc, pt in [(c, t), (c * 1.4, t), (c, t * 1.6)]:
            g = dict(f, comb=pc, tone=pt)
            r = measure(g, albedo_linear(g, st))
            rows.append([1.0, pc * pc, pt * pt])
            got.append([r["t" + k] ** 2 for k in STATS])
        coef = np.linalg.solve(np.array(rows), np.array(got))          # 3 x len(STATS): const, comb^2, tone^2
        target = np.array([r["p" + k] ** 2 for k in STATS])
        m = coef[1:].T / target[:, None]
        want = (target - coef[0]) / target
        best = None
        for fix in (None, 0, 1):
            x = np.array([0.04, 0.04])
            if fix is None:
                x = np.linalg.lstsq(m, want, rcond=None)[0]
            else:
                o = 1 - fix
                x[o] = max(0.04, float(m[:, o] @ (want - m[:, fix] * 0.04)) / float(m[:, o] @ m[:, o]))
            if np.all(x >= 0.04 - 1e-9):
                err = float(np.sum((m @ x - want) ** 2))
                if best is None or err < best[0]:
                    best = (err, x)
        f["comb"], f["tone"] = [round(float(math.sqrt(v)), 2) for v in best[1]]
    r = measure(f, albedo_linear(f, st))
    print("fit %-21s comb=%.2f, tone=%.2f   " % (f["id"], f["comb"], f["tone"]) +
          "  ".join("%s %.2f/%.2f" % (k, r["p" + k], r["t" + k]) for k in STATS) + "  dE %.2f" % r["de"])
    return f


def compare(fins, albedos, out_path):
    """Prints the photo / texture table and draws the check sheet."""
    report = [measure(fin, albedos[fin["id"]]) for fin in fins if REFS.get(fin["id"])]
    head = ["finish", "photo", "L*", "a*", "b*", "texture", "L*", "a*", "b*", "dE76", "sx ph/tex", "fine ph/tex",
            "band ph/tex"]
    cells = [head] + [[r["id"], linear_to_hex(r["photo"]), *("%.1f" % v for v in r["plab"]), linear_to_hex(r["tex"]),
                       *("%.1f" % v for v in r["tlab"]), "%.2f" % r["de"]] +
                      ["%.2f / %.2f" % (r["p" + k], r["t" + k]) for k in STATS] for r in report]
    widths = [21, 8, 6, 6, 6, 8, 6, 6, 6, 6, 13, 13, 13]
    print("\n".join("".join(c.ljust(wd) if i in (0, 1, 5) else c.rjust(wd - 1) + " " for i, (c, wd) in
                             enumerate(zip(row, widths))) for row in cells))
    if out_path is None:
        return report
    # per finish: (a) photo crop, (b) the texture as that photo would show it, both enlarged alike, (c) 1:1 close-up
    to8 = lambda x: Image.fromarray(np.round(linear_to_srgb(x) * 255).astype(np.uint8))
    tiles = []
    for r in report:
        fname, box = REFS[r["id"]][0]
        lin, scale = photo_crop(fname, box)
        z = 2 if scale > 0.3 else 4
        ch, cw = min(lin.shape[0], 600 // z), min(lin.shape[1], 220 // z)
        a = to8(lin[:ch, :cw]).resize((cw * z, ch * z), Image.NEAREST)
        b = to8(r["shown"][fname][60:60 + ch, 40:40 + cw]).resize((cw * z, ch * z), Image.NEAREST)
        c = to8(np.transpose(albedos[r["id"]], (1, 0, 2))[700:700 + 600, 300:300 + 240])
        tile = Image.new("RGB", (a.width + b.width + c.width + 24, max(a.height, c.height) + 36), "white")
        for img, x in ((a, 0), (b, a.width + 8), (c, a.width + b.width + 24)):
            tile.paste(img, (x, 36))
        d = ImageDraw.Draw(tile)
        d.text((2, 2), "%s   photo %s  texture %s   dE76 %.2f" % (
            r["id"], linear_to_hex(r["photo"]), linear_to_hex(r["tex"]), r["de"]), fill="black")
        d.text((2, 18), "(a) %s x%d  (b) texture seen the same way  (c) texture 1 px/mm   "
                        "sx %.1f/%.1f  fine %.1f/%.1f" % (
            fname.split("__")[0], z, r["psx"], r["tsx"], r["pfine"], r["tfine"]), fill=(60, 60, 60))
        tiles.append(tile)
    cols = 2
    per = math.ceil(len(tiles) / cols)
    groups = [tiles[i * per:(i + 1) * per] for i in range(cols)]
    colw = [max(t.width for t in g) for g in groups]
    top = 16 * (len(cells) + 2)
    sheet = Image.new("RGB", (max(sum(colw) + 30 * (cols - 1), 1000),
                              top + max(sum(t.height + 14 for t in g) for g in groups)), "white")
    d = ImageDraw.Draw(sheet)
    d.text((4, 4), "Door finishes vs catalogue photos: mean colour in linear light; L* contrast (sx across the grain "
                   "in 80 mm, fine = pixel to pixel, band = broad) of the texture downsized like the photo and "
                   "JPEG-compressed with its tables", fill="black")
    for i, row in enumerate(cells):
        x = 4
        for c, wd in zip(row, widths):
            d.text((x, 22 + 16 * i), c, fill="black")
            x += wd * 7
    x = 0
    for g, cwid in zip(groups, colw):
        y = top
        for t in g:
            sheet.paste(t, (x, y))
            y += t.height + 14
        x += cwid + 30
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path)
    print("check sheet", out_path)
    return report


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("finishes", nargs="*", help="finish ids (default: all)")
    ap.add_argument("--compare", action="store_true", help="write tools/doors/.cache/finishes_compare.png")
    ap.add_argument("--no-write", action="store_true", help="do not write textures / external.json")
    ap.add_argument("--sheet", default=str(CACHE / "finishes_compare.png"))
    ap.add_argument("--fit", action="store_true", help="suggest comb / tone from the photos (needs the photos)")
    args = ap.parse_args()
    fins = [f for f in FINISHES if not args.finishes or f["id"] in args.finishes]
    if args.finishes and len(fins) != len(args.finishes):
        sys.exit("unknown finish: " + ", ".join(set(args.finishes) - {f["id"] for f in fins}))
    if (args.compare or args.fit) and not (CACHE / "photos").is_dir():
        sys.exit("no catalogue photos in %s: run tools/doors/catalog_index.py first" % (CACHE / "photos"))
    structures, albedos = {}, {}
    for fin in fins:
        st = finish_structure(fin, structures)
        if args.fit:
            fit(fin, st)
            continue
        alb = albedo_linear(fin, st)
        if not args.no_write:
            write_finish(fin, st, alb)
            print("finish", fin["id"], "->", fin["material"])
            # compare what Unity gets: the written JPEG
            alb = srgb_to_linear(np.asarray(Image.open(EXT / "Materials" / fin["material"] /
                                                       (fin["material"] + "_albedo.jpg")), dtype=np.float64) / 255)
        if args.compare:
            albedos[fin["id"]] = alb.astype(np.float32)
    if args.fit:
        return
    if not args.no_write:
        update_manifest(fins)
        print("manifest", EXT / "external.json")
    if args.compare:
        compare(fins, albedos, Path(args.sheet))


if __name__ == "__main__":
    main()
