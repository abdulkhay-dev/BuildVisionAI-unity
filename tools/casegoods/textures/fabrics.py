#!/usr/bin/env python3
"""Upholstery of the casegoods catalogue (texture wave 6, family `fabrics`): neutral, tintable fabric materials.

    python3 tools/casegoods/textures/fabrics.py                  # all: textures + entries + merge + check sheet
    python3 tools/casegoods/textures/fabrics.py cgfab_velur      # only these (the sheet shows every written one)
    python3 tools/casegoods/textures/fabrics.py --sheet          # check sheet only (reads the written textures)
    python3 tools/casegoods/textures/fabrics.py --no-merge       # do not touch external.json

Materials (all NEUTRAL: the albedo is a light grey, saturation 0, its pattern only a variation of value; the finish
tints it with "id#rrggbb", which URP multiplies into _BaseColor):
    cgfab_velur_myaty  crushed velour (Стамбул, Сати, Парма): pile pressed flat in irregular patches - silvery ground,
                       greyer blotches and flecks elongated along V, swirl-like veins; 2.0 x 1.0 m, no repeat on a bed
    cgfab_velur        short-pile velour / suede-look (Акцент, Бритиш Бум, Деко, Верес, Юнона Лайт): faint curved
                       pile marks, soft mottle, fibre grain; 1.0 x 0.5 m
    cgfab_rogozhka     matting (рогожка) / linen-look: 2 x 2 basket weave of ~1 mm melange yarns with slubs (Марлен);
                       256 x 128 yarns = 0.25 x 0.125 m
    cgfab_ekokozha     smooth eco-leather, fine pebble grain ~1 mm, satin (Элиза); 0.25 x 0.125 m

Mean colour: the texture's mean in LINEAR light is solved to exactly MEAN (sRGB hex; eco-leather lighter so that the
light cream of Элиза stays reachable with a tint <= 1). A finish colour `target` is then reached with the tint
    tint_linear = target_linear / mean_linear      (per channel; printed by --sheet and in fabrics.md)
Per material (M = id): Assets/House4696/External/Materials/M/M_albedo.jpg (2048 x 1024 sRGB grey), M_normal.jpg
(OpenGL, 1024 x 512), M_mask.png (R 0, G AO 255, B 0, A smoothness; 256 x 128) - all tileable; entries
tools/casegoods/textures/entries/fabrics.json merged by tools/doors/textures/merge_entries.py; the check sheet
tools/casegoods/textures/sheets/fabrics.png (catalogue photo crops, the texture tinted to each crop's colour at the
crop's scale, 1 x 0.5 m tinted patches, a close-up), lit with a simple key light to show the normal / smoothness.

Built on the door texture machinery (tools/doors/textures/make_finishes.py: colour maths, periodic FFT noise,
box filters); the catalogue crops come from tools/casegoods/gen/catpage.py's renderer. numpy + Pillow (+ PyMuPDF for
the sheet's photo crops).
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools" / "doors" / "textures"))
sys.path.insert(0, str(ROOT / "tools" / "casegoods" / "gen"))
import make_finishes as mf          # noqa: E402
import merge_entries                # noqa: E402

EXT = ROOT / "Assets" / "House4696" / "External"
ALBEDO, NORMAL, MASK = (2048, 1024), (1024, 512), (256, 128)
ENTRIES = HERE / "entries" / "fabrics.json"
SHEET = HERE / "sheets" / "fabrics.png"
SOURCE = "procedural:tools/casegoods/textures/fabrics.py"

hex_to_linear, linear_to_hex, linear_to_srgb = mf.hex_to_linear, mf.linear_to_hex, mf.linear_to_srgb
unit = lambda a: (a - a.mean()) / max(1e-12, a.std())      # noqa: E731


# ------------------------------------------------------------------------------------------------ periodic helpers
def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def sample(f, X, Y):
    """f at the real coordinates (X, Y) (px), bilinear, wrapping (periodic)."""
    h, w = f.shape
    x0 = np.floor(X).astype(np.int64)
    y0 = np.floor(Y).astype(np.int64)
    tx, ty = X - x0, Y - y0
    x0 %= w
    y0 %= h
    x1, y1 = (x0 + 1) % w, (y0 + 1) % h
    return (f[y0, x0] * (1 - tx) + f[y0, x1] * tx) * (1 - ty) + (f[y1, x0] * (1 - tx) + f[y1, x1] * tx) * ty


class Field:
    """Periodic noise on the albedo grid of a tile; sizes in mm."""

    def __init__(self, seed, tile_m):
        self.rng = np.random.default_rng(seed)
        self.w, self.h = ALBEDO
        self.ppm = self.w / (tile_m[0] * 1000.0)            # px per mm (square pixels)
        assert abs(self.h / (tile_m[1] * 1000.0) - self.ppm) < 1e-9
        self.Y, self.X = np.mgrid[0:self.h, 0:self.w].astype(np.float64)

    def noise(self, sx, sy=None):
        """Unit-std periodic noise, Gaussian correlation sx (along U / x) x sy (along V / y) mm."""
        return mf.gauss_noise(self.rng, (self.h, self.w), sx * self.ppm, (sy if sy is not None else sx) * self.ppm)

    def warp(self, octaves):
        """Displacement (px) along x and y: octaves of (amplitude mm, sigma x mm, sigma y mm)."""
        dx = sum(self.noise(sx, sy) * a * self.ppm for a, sx, sy in octaves)
        dy = sum(self.noise(sx, sy) * a * self.ppm for a, sx, sy in octaves)
        return dx, dy


def grad(a):
    return (np.roll(a, -1, 1) - np.roll(a, 1, 1)) / 2, (np.roll(a, -1, 0) - np.roll(a, 1, 0)) / 2


# ------------------------------------------------------------------------------------------------ builders
# A builder returns (value, height, smooth) on the albedo grid: value = relative albedo (mean ~1), height in mm,
# smooth = smoothness 0..1.

def crushed_velour(m):
    """Crushed velour: the pile is pressed in long irregular creases, and each crease facet leans its pile another
    way - so the fabric reads as light and mid-tone facets with soft light / dark sides, not as spots. Model: a
    crumple height (ridged, domain-warped noise at 45 / 18 / 7 mm, stretched `aniso` x along V - the crush
    direction) lit from the side: the facet's slope towards the light gives its tone (tanh, so the sides stay
    soft); faint crease lines where the pile turns over; a small crinkle (3-6 mm) and the pile grain on top; a weak
    elongated tone drift (no round blots). The same facets carry the relief (normal) and a smoothness that follows
    the facet's lean (flattened pile glossier), so the highlight shifts across the creases even without a sheen."""
    f = Field(m["seed"], m["tile"])
    an = m.get("aniso", 2.4)
    dx, dy = f.warp([(26, 110, 110 * an), (8, 30, 30 * an)])
    X, Y = f.X + dx, f.Y + dy
    crumple = np.zeros_like(X)
    for sig, amp in ((45.0, 0.55), (18.0, 0.6), (7.0, 0.35)):
        crumple += amp * sig * np.abs(sample(f.noise(sig, sig * an), X, Y))
    gx, gy = grad(crumple)
    r = np.sqrt((gx ** 2 + gy ** 2).mean())
    L = (0.85, 0.53)                                                  # light across the creases (mostly along U)
    lean = (L[0] * gx + L[1] * gy) / r
    facet = np.tanh(0.9 * lean)                                       # soft light / dark sides of each crease
    crease = np.exp(-((gx ** 2 + gy ** 2) / r ** 2) / 0.04)           # the fold line itself (pile turns over)
    cr = np.zeros_like(X)
    for sig, amp in ((6.0, 1.0), (2.5, 0.45)):
        cr += amp * sig * np.abs(sample(f.noise(sig, sig * 1.3), X + 0.5 * dx, Y + 0.5 * dy))
    cx, cy = grad(cr)
    cg = np.sqrt((cx ** 2 + cy ** 2).mean())
    crink = np.tanh(1.2 * (L[0] * cx + L[1] * cy) / cg)
    drift = sample(f.noise(60, 60 * an), X, Y)                        # elongated tone drift, not spots
    patch = smoothstep(0.3, 1.6, drift)
    streak = np.tanh(1.2 * sample(f.noise(10, 10 * an * 1.6), X, Y))   # lighter / darker pile streaks along the creases
    v = (1 + m["streak_k"] * streak + m["facet_k"] * facet * (0.75 + 0.25 * smoothstep(-1, 1, f.noise(80, 80 * an)))
         + m["crinkle_k"] * crink - m["crease_k"] * crease - m["blot_k"] * patch
         + 0.025 * f.noise(0.7) + 0.02 * f.noise(0.35, 1.2))
    v = np.clip(v, 0.3, None)
    hgt = 0.14 * unit(crumple) + 0.035 * unit(cr) + 0.012 * f.noise(0.5, 1.0)
    smooth = m["smooth"] + m["sheen_k"] * facet + 0.03 * crink + 0.03 * streak - 0.04 * crease
    return v, hgt, smooth


def velour(m):
    """Short-pile velour / suede-look: a calm, fine fibre grain; faint curved pile marks (lighter / darker brushed
    streaks where the pile lies another way, 30-120 mm long) and a soft broad mottle. Matt, soft sheen."""
    f = Field(m["seed"], m["tile"])
    dx, dy = f.warp([(40, 160, 160), (10, 40, 40)])
    X, Y = f.X + dx, f.Y + dy
    # pile marks: elongated noise in two orientations, mixed by a smooth field -> the streaks change direction
    s1 = sample(f.noise(28, 3.5), X, Y)
    s2 = sample(f.noise(3.5, 28), X, Y)
    mix = smoothstep(-0.6, 0.6, f.noise(120))
    s = unit(s1 * mix + s2 * (1 - mix))
    marks = smoothstep(1.1, 2.2, s) - 0.7 * smoothstep(1.2, 2.3, -s)
    v = (1 + m["mark_k"] * marks + 0.022 * f.noise(45) + 0.012 * f.noise(12)
         + 0.03 * f.noise(0.3) + 0.015 * f.noise(1.0))
    hgt = 0.012 * f.noise(0.35) + 0.008 * f.noise(1.2) + 0.03 * f.noise(15) + 0.01 * marks
    smooth = m["smooth"] + 0.035 * marks + 0.01 * f.noise(30)
    return v, hgt, smooth


def matting(m):
    """Рогожка: a 2 x 2 basket weave (pairs of warp yarns along V over / under pairs of weft yarns along U) of ~1 mm
    melange yarns: two-ply twist striations, yarn-to-yarn tone, slubs (thicker, lighter stretches), a slight wobble.
    Height = the upper of the two yarn surfaces (cross-section ~0.35 mm, crossing lift +-0.12 mm); the crevices
    between yarns and groups are darker (shadowed)."""
    f = Field(m["seed"], m["tile"])
    w, h = ALBEDO
    nu, nv = m["yarns"]                                              # yarns per tile along U, V (multiples of 4)
    p = w / nu
    assert abs(h / nv - p) < 1e-9 and nu % 4 == 0 and nv % 4 == 0
    rng = f.rng
    wob = [f.noise(18, 18) * 0.10 * p, f.noise(18, 18) * 0.10 * p]
    X, Y = f.X + wob[0], f.Y + wob[1]
    i = np.floor(X / p).astype(np.int64)                             # warp yarn index (yarn runs along y)
    j = np.floor(Y / p).astype(np.int64)                             # weft yarn index (runs along x)
    tx = X / p - i - 0.5
    ty = Y / p - j - 0.5
    gi, gj = (i // 2) % 2, (j // 2) % 2
    # yarn thickness varies along the yarn (slubs): per yarn noise along its length
    ncol = mf.gauss_noise(rng, (h, nu), 14 * f.ppm, 0.01)             # rows = along y, one column per warp yarn
    nrow = mf.gauss_noise(rng, (nv, w), 0.01, 14 * f.ppm)             # one row per weft yarn, along x
    sw = ncol[f.Y.astype(np.int64), i % nu]
    sf = nrow[j % nv, f.X.astype(np.int64)]
    slw, slf = smoothstep(1.2, 2.2, sw), smoothstep(1.2, 2.2, sf)
    ww = np.clip(0.84 + 0.05 * sw + 0.10 * slw, 0.6, 1.0)             # yarn width share of its pitch
    wf = np.clip(0.84 + 0.05 * sf + 0.10 * slf, 0.6, 1.0)
    prof = lambda t, wd: np.clip(1 - (2 * np.abs(t) / wd) ** 2, 0, 1) ** 0.45    # noqa: E731
    # over / under along the yarn: smooth square wave of the crossing group
    u = Y / (2 * p)
    vv = X / (2 * p)
    Sw = np.tanh(2.5 * np.sin(np.pi * u))                            # +1 on even weft groups
    Sf = np.tanh(2.5 * np.sin(np.pi * vv))                           # +1 on even warp groups
    lw = np.where(gi == 0, 1.0, -1.0) * Sw
    lf = -np.where(gj == 0, 1.0, -1.0) * Sf
    # a pair of yarns touches: the outer edges of the pair are the deeper crevices
    pair_w = np.where(i % 2 == 0, 1.0, -1.0)
    pair_f = np.where(j % 2 == 0, 1.0, -1.0)
    pw_, pf_ = prof(tx, ww), prof(ty, wf)
    hw = 0.35 * pw_ + 0.12 * lw + 0.04 * slw - 0.03 * np.clip(pair_w * tx * 2, 0, 1)
    hf = 0.35 * pf_ + 0.12 * lf + 0.04 * slf - 0.03 * np.clip(pair_f * ty * 2, 0, 1)
    top_w = hw >= hf
    ptop = np.where(top_w, pw_, pf_)                                 # across the visible yarn: 1 crown, 0 flank
    ltop = np.where(top_w, lw, lf)                                   # along it: +1 over, dives towards -1
    hgt = np.maximum(hw, hf)
    # tones: yarn-to-yarn, two-ply twist striations (diagonal in the yarn's frame), slubs lighter
    # yarn tone drifts along each yarn (~30 mm): no whole-tile stripes that would repeat every tile
    tone_w = mf.gauss_noise(rng, (h, nu), 30 * f.ppm, 0.01)[f.Y.astype(np.int64), i % nu] * m["yarn_k"]
    tone_f = mf.gauss_noise(rng, (nv, w), 0.01, 30 * f.ppm)[j % nv, f.X.astype(np.int64)] * m["yarn_k"]
    tw = m["twist_mm"] * f.ppm
    ply_w = np.cos(2 * np.pi * (Y / tw + tx * 0.9 + rng.uniform(0, 1, nu)[i % nu]))
    ply_f = np.cos(2 * np.pi * (X / tw + ty * 0.9 + rng.uniform(0, 1, nv)[j % nv]))
    melw = m["ply_k"] * np.tanh(2 * ply_w) * (1 + 0.5 * mf.gauss_noise(rng, (h, nu), 6 * f.ppm, 0.01)[f.Y.astype(np.int64), i % nu])
    melf = m["ply_k"] * np.tanh(2 * ply_f) * (1 + 0.5 * mf.gauss_noise(rng, (nv, w), 0.01, 6 * f.ppm)[j % nv, f.X.astype(np.int64)])
    yarn = np.where(top_w, tone_w + melw + m["slub_k"] * slw + 0.02 * sw, tone_f + melf + m["slub_k"] * slf + 0.02 * sf)
    fuzz = 0.025 * f.noise(0.12)
    shade = (0.66 + 0.34 * ptop ** 0.7) * (0.86 + 0.14 * smoothstep(-1, 0.6, ltop))   # flanks, dives shadowed
    v = (1 + yarn + fuzz) * shade
    hgt = hgt + 0.01 * f.noise(0.15)
    smooth = m["smooth"] + 0.04 * smoothstep(0.2, 0.45, hgt) - 0.02
    return v, hgt, smooth


def voronoi(X, Y, cs, rng):
    """Periodic jittered-grid Voronoi on a grid of cs px cells (the grid must divide the tile): F1, F2 (px)."""
    h, w = X.shape
    gy, gx = ALBEDO[1] // cs, ALBEDO[0] // cs
    jx = rng.uniform(0.0, 1.0, (gy, gx)) * cs
    jy = rng.uniform(0.0, 1.0, (gy, gx)) * cs
    ci = np.floor(X / cs).astype(np.int64)
    cj = np.floor(Y / cs).astype(np.int64)
    F1 = np.full(X.shape, 1e9)
    F2 = np.full(X.shape, 1e9)
    for dj in (-1, 0, 1):
        for di in (-1, 0, 1):
            ni, nj = ci + di, cj + dj
            px = ni * cs + jx[nj % gy, ni % gx]
            py = nj * cs + jy[nj % gy, ni % gx]
            d = np.hypot(X - px, Y - py)
            F2 = np.where(d < F1, F1, np.minimum(F2, d))
            F1 = np.minimum(F1, d)
    return F1, F2


def eco_leather(m):
    """Smooth eco-leather (PU): a fine pebble grain (Voronoi cells ~1 mm, rounded tops, narrow valleys, a coarser
    ~4 mm grain faintly over it), soft broad undulation; the albedo barely varies (valleys a touch darker), the
    satin smoothness drops in the valleys."""
    f = Field(m["seed"], m["tile"])
    dx, dy = f.warp([(0.35, 3, 3), (1.0, 12, 12)])
    X, Y = f.X + dx, f.Y + dy
    cs = m["cell_px"]
    F1, F2 = voronoi(X, Y, cs, f.rng)
    edge = F2 - F1
    valley = 1 - smoothstep(0.0, 0.28 * cs, edge)
    dome = 1 - (F1 / cs) ** 2
    G1, G2 = voronoi(X + 7.3, Y + 3.1, cs * 4, f.rng)                # coarser grain (off the fine grid)
    cvalley = 1 - smoothstep(0.0, 0.2 * cs * 4, G2 - G1)
    # nothing broader than ~3 mm: on a 0.25 m tile a broad mottle would show the repeat across a headboard
    hgt = (0.022 * dome - 0.030 * valley - 0.018 * cvalley + 0.006 * f.noise(2.5) + 0.004 * f.noise(0.3))
    v = 1 - 0.035 * valley - 0.02 * cvalley + 0.008 * f.noise(2.5) + 0.006 * f.noise(0.25)
    smooth = m["smooth"] + 0.05 - 0.14 * valley - 0.08 * cvalley
    return v, hgt, smooth


# ------------------------------------------------------------------------------------------------ materials
# refs: (label, page, crop x0,y0,x1,y1 of the spread, dpi, px per mm of the fabric in that render, target hex)
MATERIALS = [
    dict(id="cgfab_velur_myaty", name="Велюр мятый", build=crushed_velour, tile=(2.0, 1.0), mean="#e0e0e0",
         seed=7, aniso=2.4, tilt=6.0, facet_k=0.19, streak_k=0.07, crinkle_k=0.045, crease_k=0.05, blot_k=0.06, smooth=0.33,
         sheen_k=0.08,
         refs=[("Стамбул p.106 headboard", 106, (0.503, 0.41, 0.581, 0.44), 300, 0.58, "#c6bdb6"),
               ("Стамбул p.106 footboard", 106, (0.322, 0.53, 0.372, 0.64), 300, 0.25, "#c6bdb6"),
               ("Сати p.22 headboard", 22, (0.66, 0.505, 0.80, 0.575), 300, 0.95, "#ab9a93"),
               ("Парма p.54 headboard", 54, (0.537, 0.416, 0.703, 0.449), 250, 0.79, "#cdbfa8")],
         targets=[("Стамбул", "#c6bdb6"), ("Сати", "#ab9a93"), ("Сати white", "#d6ccbf"), ("Парма", "#cdbfa8")]),
    dict(id="cgfab_velur", name="Велюр", build=velour, tile=(1.0, 0.5), mean="#e0e0e0",
         seed=11, mark_k=0.05, tilt=3.0, smooth=0.30,
         refs=[("Акцент 3.02 p.132", 132, (0.37, 0.528, 0.47, 0.56), 300, 1.1, "#b0a28c"),
               ("Юнона Лайт p.109", 109, (0.60, 0.465, 0.72, 0.50), 300, 0.86, "#846d5d"),
               ("Деко p.73", 73, (0.16, 0.435, 0.30, 0.47), 250, 1.0, "#16110e"),
               ("Верес 3.09 p.135", 135, (0.02, 0.572, 0.155, 0.61), 300, 1.0, "#4a3a33")],
         targets=[("Акцент", "#b0a28c"), ("Бритиш 1.34", "#9e958e"), ("Юнона Лайт", "#846d5d"),
                  ("Верес", "#4a3a33"), ("Деко", "#16110e")]),
    dict(id="cgfab_rogozhka", name="Рогожка", build=matting, tile=(0.25, 0.125), mean="#e0e0e0",
         seed=5, yarns=(256, 128), tilt=16, yarn_k=0.04, ply_k=0.08, twist_mm=1.4, slub_k=0.06, smooth=0.22,
         refs=[("Марлен p.105 headboard", 105, (0.703, 0.475, 0.879, 0.524), 300, 0.94, "#c9bcab"),
               ("Бритиш Бум 1.34 p.131", 131, (0.767, 0.385, 0.869, 0.405), 300, 0.37, "#9e958e")],
         targets=[("Марлен", "#c9bcab"), ("Бритиш 1.32", "#bfbbb2"), ("Бритиш 1.34", "#9e958e")]),
    dict(id="cgfab_ekokozha", name="Экокожа", build=eco_leather, tile=(0.25, 0.125), mean="#ececec",
         seed=3, cell_px=8, tilt=5, smooth=0.55,
         refs=[("Элиза p.108 headboard", 108, (0.44, 0.457, 0.56, 0.519), 300, 0.78, "#e7dcc4")],
         targets=[("Элиза", "#e7dcc4"), ("Юнона Лайт", "#846d5d"), ("Верес", "#4a3a33")]),
]
BY_ID = {m["id"]: m for m in MATERIALS}


# ------------------------------------------------------------------------------------------------ writing
def solve_albedo(v, mean_hex):
    """Grey linear albedo with the value pattern v whose linear mean is exactly the target (clipping re-solved)."""
    target = float(hex_to_linear(mean_hex)[0])
    k = target / v.mean()
    for _ in range(4):
        k *= target / np.clip(v * k, 0, 1).mean()
    return np.clip(v * k, 0, 1)


def normal_from_height(hgt, tile_m, tilt=None):
    """OpenGL tangent-space normal map (NORMAL res) of a height field in mm on the albedo grid; with `tilt` (deg)
    the relief is scaled so that the rms slope angle is that (the height's shape stays, its depth is set)."""
    f = ALBEDO[0] // NORMAL[0]
    hn = mf.box_down(hgt, f)
    mm_px = tile_m[0] * 1000.0 / NORMAL[0]
    gx, gr = grad(hn)
    gx, gr = gx / mm_px, gr / mm_px
    if tilt:
        k = math.tan(math.radians(tilt)) / np.sqrt((gx ** 2 + gr ** 2).mean())
        gx, gr = gx * k, gr * k
    n = np.stack([-gx, gr, np.ones_like(gx)], -1)                    # +Y (green) = up = -row
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    tilt = float(np.degrees(np.sqrt((np.arctan(np.hypot(gx, gr)) ** 2).mean())))
    return np.round((n * 0.5 + 0.5) * 255).astype(np.uint8), tilt


def mask_from_smooth(smooth):
    f = ALBEDO[0] // MASK[0]
    s = mf.box_down(np.clip(smooth, 0, 1), f)
    m = np.zeros((MASK[1], MASK[0], 4), np.uint8)
    m[..., 1] = 255
    m[..., 3] = np.round(s * 255).astype(np.uint8)
    return m


def build(m):
    v, hgt, smooth = m["build"](m)
    alb = solve_albedo(v, m["mean"])
    nrm, tilt = normal_from_height(hgt, m["tile"], m.get("tilt"))
    mask = mask_from_smooth(smooth)
    folder = EXT / "Materials" / m["id"]
    folder.mkdir(parents=True, exist_ok=True)
    g8 = np.round(linear_to_srgb(alb) * 255).astype(np.uint8)
    Image.fromarray(np.repeat(g8[..., None], 3, -1)).save(folder / f"{m['id']}_albedo.jpg", quality=92,
                                                          subsampling=0)
    Image.fromarray(nrm).save(folder / f"{m['id']}_normal.jpg", quality=94, subsampling=0)
    Image.fromarray(mask).save(folder / f"{m['id']}_mask.png", optimize=True)
    print(f"{m['id']}: normal rms tilt {tilt:.1f} deg, smoothness mean {mask[..., 3].mean() / 255:.3f}")


def entry(m):
    mid = m["id"]
    return {"id": mid, "name": m["name"], "category": "casegoods", "source": SOURCE, "neutral": True,
            "metersPerTile": list(m["tile"]), "maxSize": ALBEDO[0], "folder": f"Materials/{mid}",
            "textures": {"albedo": f"{mid}_albedo.jpg", "normal": f"{mid}_normal.jpg", "mask": f"{mid}_mask.png"}}


def written(m):
    return (EXT / "Materials" / m["id"] / f"{m['id']}_albedo.jpg").exists()


def load(m):
    folder = EXT / "Materials" / m["id"]
    alb = np.asarray(Image.open(folder / f"{m['id']}_albedo.jpg").convert("RGB"), dtype=np.float64) / 255
    nrm = np.asarray(Image.open(folder / f"{m['id']}_normal.jpg").convert("RGB"), dtype=np.float64) / 255 * 2 - 1
    mask = np.asarray(Image.open(folder / f"{m['id']}_mask.png"), dtype=np.float64)[..., 3] / 255
    return mf.srgb_to_linear(alb), nrm, mask


def stats(m):
    lin, _, mask = load(m)
    mean = lin.reshape(-1, 3).mean(0)
    s8 = np.round(linear_to_srgb(lin) * 255)
    sat = float((s8.max(-1) - s8.min(-1)).mean())
    return dict(mean_hex=linear_to_hex(mean), mean_lin=mean, srgb_mean=s8.reshape(-1, 3).mean(0),
                p5_95=np.percentile(s8[..., 1], [5, 95]), sat=sat, smooth=float(mask.mean()))


def tint_for(target_hex, mean_lin):
    t = hex_to_linear(target_hex) / mean_lin
    return linear_to_hex(t) if t.max() <= 1.0 else f"unreachable ({t.max():.3f} > 1)"


# ------------------------------------------------------------------------------------------------ check sheet
def lit(m, tint_hex, size_m, out_px, origin=(0.0, 0.0)):
    """The material tinted to tint_hex, size_m (w, h metres) of it from origin (m) tiled, resized to out_px wide,
    lit by a key light from the upper left (Lambert on the normal map + a Blinn-Phong highlight from smoothness)."""
    lin, nrm, mask = load(m)
    tw, th = m["tile"]
    col = hex_to_linear(tint_hex) / lin.reshape(-1, 3).mean(0) if tint_hex else np.ones(3)   # tint = target / mean
    # the patch on the albedo grid (tiled)
    ppm = ALBEDO[0] / (tw * 1000.0)
    W, H = int(round(size_m[0] * 1000 * ppm)), int(round(size_m[1] * 1000 * ppm))
    ox, oy = int(origin[0] * 1000 * ppm), int(origin[1] * 1000 * ppm)
    ys = (np.arange(H) + oy) % ALBEDO[1]
    xs = (np.arange(W) + ox) % ALBEDO[0]
    # like the GPU's mipmaps: box-filter the maps to about 2 texels per output pixel, then sample
    step = 1
    while W // (step * 2) >= out_px * 2:
        step *= 2
    ys, xs = ys[::step] // step, xs[::step] // step
    lin_m = mf.box_down(lin, step) if step > 1 else lin
    a = lin_m[np.ix_(ys, xs)] * col
    fy, fx = ALBEDO[1] // NORMAL[1], ALBEDO[0] // NORMAL[0]
    ns = max(1, step // fx)
    nrm_m = mf.box_down(nrm, ns) if ns > 1 else nrm
    nrm_m = nrm_m / np.linalg.norm(nrm_m, axis=-1, keepdims=True)
    n = nrm_m[np.ix_(ys * step // (fy * ns), xs * step // (fx * ns))]
    s = mask[np.ix_(ys * step // (ALBEDO[1] // MASK[1]), xs * step // (ALBEDO[0] // MASK[0]))]
    L = np.array([-0.45, 0.45, 0.77])
    L /= np.linalg.norm(L)
    V = np.array([0.0, 0.0, 1.0])
    Hh = (L + V) / np.linalg.norm(L + V)
    ndl = np.clip(n @ L, 0, 1) / L[2]
    ndh = np.clip(n @ Hh, 0, 1)
    rough = np.clip(1 - s, 0.05, 1) ** 2
    spec_pow = 2 / rough ** 2 - 2
    spec = 0.04 * (spec_pow + 8) / (8 * np.pi) * ndh ** spec_pow * ndl * L[2]
    c = a * (0.35 + 0.65 * ndl)[..., None] + spec[..., None] * 0.6
    img = Image.fromarray(np.round(linear_to_srgb(c) * 255).astype(np.uint8))
    return img.resize((out_px, max(1, int(round(out_px * size_m[1] / size_m[0])))), Image.LANCZOS)


def page_crop(page, box, dpi):
    import catpage
    import pymupdf
    doc = pymupdf.open(catpage.PDF)
    return catpage.render(doc[page - 1], dpi, catpage.frac_rect(doc[page - 1], ",".join(map(str, box))))


def font(size):
    for p in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial Unicode.ttf",
              "/System/Library/Fonts/Helvetica.ttc"):
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            pass
    return ImageFont.load_default()


def sheet(mats):
    F, Fs = font(22), font(15)
    RH = 230                     # height of a reference row
    rows = []
    for m in mats:
        if not written(m):
            continue
        st = stats(m)
        parts = []
        # references: photo crop | the texture tinted to that crop's colour at the crop's scale, same size
        for label, page, box, dpi, ppmm, hexc in m["refs"]:
            ref = page_crop(page, box, dpi)
            sc = RH / ref.height
            ref = ref.resize((max(1, int(ref.width * sc)), RH), Image.LANCZOS)
            ref = ref.crop((0, 0, min(ref.width, 560), RH))               # at most 600 px of it
            size_m = (ref.width / (ppmm * sc) / 1000, RH / (ppmm * sc) / 1000)
            tex = lit(m, hexc, size_m, ref.width)
            tex = tex.resize((ref.width, RH), Image.LANCZOS)
            parts.append((f"{label}  ({size_m[0]:.2f} m)", ref, tex))
        # 1 x 0.5 m patches tinted to the targets + a close-up of the neutral texture
        pw = 500
        patches = [(f"{n} {h}: 1.0 x 0.5 m", lit(m, h, (1.0, 0.5), pw)) for n, h in m["targets"]]
        close = [("neutral 1.0 x 0.5 m", lit(m, None, (1.0, 0.5), pw)),
                 ("neutral 0.25 x 0.125 m", lit(m, None, (0.25, 0.125), pw)),
                 ("neutral 0.06 x 0.03 m", lit(m, None, (0.06, 0.03), pw))]
        rows.append((m, st, parts, patches + close))
    W = 2600
    blocks = []
    for m, st, parts, patches in rows:
        per, lines, x = 0, 1, 10
        for _, ref, _ in parts:
            if x + ref.width * 2 + 10 > W:
                lines, x = lines + 1, 10
            x += ref.width * 2 + 22
        h1 = 40 + lines * (RH + 32)
        nper = W // (patches[0][1].width + 12)
        ph = patches[0][1].height
        h2 = ((len(patches) + nper - 1) // nper) * (ph + 30)
        im = Image.new("RGB", (W, h1 + h2 + 20), (250, 250, 248))
        d = ImageDraw.Draw(im)
        d.text((10, 8), f"{m['id']}  «{m['name']}»   tile {m['tile'][0]} x {m['tile'][1]} m   mean {st['mean_hex']} "
                        f"(linear {st['mean_lin'][0]:.4f})   sat {st['sat']:.2f}   smoothness {st['smooth']:.2f}   "
                        f"sRGB 5-95% {st['p5_95'][0]:.0f}-{st['p5_95'][1]:.0f}", fill=(20, 20, 20), font=F)
        x, y = 10, 40
        for label, ref, tex in parts:
            if x + ref.width * 2 + 10 > W:
                x, y = 10, y + RH + 32
            d.text((x, y), label, fill=(60, 60, 60), font=Fs)
            im.paste(ref, (x, y + 22))
            im.paste(tex, (x + ref.width + 2, y + 22))
            x += ref.width * 2 + 22
        y += RH + 32
        x = 10
        for label, p in patches:
            if x + p.width > W:
                x, y = 10, y + ph + 30
            d.text((x, y), label, fill=(60, 60, 60), font=Fs)
            im.paste(p, (x, y + 20))
            x += p.width + 12
        blocks.append(im)
    out = Image.new("RGB", (W, sum(b.height for b in blocks)), (255, 255, 255))
    y = 0
    for b in blocks:
        out.paste(b, (0, y))
        y += b.height
    SHEET.parent.mkdir(parents=True, exist_ok=True)
    out.save(SHEET, optimize=True)
    print("sheet", SHEET, out.size)
    for m, st, _, _ in rows:
        print(f"{m['id']}: mean {st['mean_hex']} (linear {st['mean_lin'][0]:.4f}, sRGB pixel mean "
              f"{st['srgb_mean'][0]:.1f}), sat {st['sat']:.2f}, smoothness {st['smooth']:.3f}; tints: " +
              ", ".join(f"{n} {h} -> {tint_for(h, st['mean_lin'])}" for n, h in m["targets"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--sheet", action="store_true", help="check sheet only")
    ap.add_argument("--no-merge", action="store_true")
    a = ap.parse_args()
    mats = [BY_ID[i] for i in a.ids] if a.ids else MATERIALS
    if not a.sheet:
        for m in mats:
            build(m)
        done = [m for m in MATERIALS if written(m)]
        ENTRIES.parent.mkdir(parents=True, exist_ok=True)
        ENTRIES.write_text(json.dumps([entry(m) for m in done], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        if not a.no_merge:
            merge_entries.merge([str(ENTRIES)])
    sheet([m for m in MATERIALS if (not a.ids or m["id"] in a.ids)])


if __name__ == "__main__":
    main()
