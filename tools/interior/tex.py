"""Procedural images for the models' own textures (paintings, rugs, posters, screen pictures). numpy only; arrays are
H×W×3 floats 0..1 in sRGB, row 0 = top of the image."""
import math

import numpy as np


def rng(seed):
    return np.random.default_rng(seed)


def value_noise(h, w, cells, seed=0):
    """Smooth value noise with `cells` lattice cells across the width."""
    r = rng(seed)
    ch = max(2, int(round(cells * h / w)))
    g = r.random((ch + 2, cells + 2))
    ys = np.linspace(0, ch, h, endpoint=False)
    xs = np.linspace(0, cells, w, endpoint=False)
    y0, x0 = ys.astype(int), xs.astype(int)
    fy, fx = ys - y0, xs - x0
    fy, fx = fy * fy * (3 - 2 * fy), fx * fx * (3 - 2 * fx)
    a = g[y0][:, x0]
    b = g[y0][:, x0 + 1]
    c = g[y0 + 1][:, x0]
    d = g[y0 + 1][:, x0 + 1]
    top = a + (b - a) * fx[None, :]
    bot = c + (d - c) * fx[None, :]
    return top + (bot - top) * fy[:, None]


def fbm(h, w, cells=4, octaves=5, seed=0, gain=0.5):
    out = np.zeros((h, w))
    amp, total = 1.0, 0.0
    for o in range(octaves):
        out += amp * value_noise(h, w, cells * 2 ** o, seed + o * 17)
        total += amp
        amp *= gain
    return out / total


def hexc(s):
    s = s.lstrip("#")
    return np.array([int(s[i:i + 2], 16) / 255 for i in (0, 2, 4)])


def mix(a, b, t):
    t = np.clip(t, 0, 1)[..., None] if np.ndim(t) else t
    return a * (1 - t) + b * t


def grid(h, w):
    y, x = np.mgrid[0:h, 0:w]
    return x / w, y / h


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def canvas_grain(img, seed=3, amt=0.035):
    h, w = img.shape[:2]
    n = rng(seed).random((h, w))
    weave = (np.sin(np.arange(w) * 2.2)[None, :] * np.sin(np.arange(h) * 2.2)[:, None]) * 0.5
    return np.clip(img + ((n - 0.5) + weave * 0.4)[..., None] * amt, 0, 1)


# ---------------------------------------------------------------------- paintings
def abstract_painting(h=1024, w=768, seed=11, palette=("#f1ece3", "#1d1c1b", "#8b8d8f", "#c9a46a", "#d9d4cb")):
    """Large gestural abstract: pale ground, sweeping black and grey masses, a few gold streaks (living room)."""
    x, y = grid(h, w)
    cols = [hexc(p) for p in palette]
    img = np.ones((h, w, 3)) * cols[0]
    n = fbm(h, w, 3, 5, seed)
    n2 = fbm(h, w, 5, 4, seed + 5)
    # diagonal masses
    band = np.sin((x * 1.6 + y * 1.1) * math.pi + n * 4.5)
    dark = smooth(0.55, 0.75, band) * smooth(0.25, 0.5, n2)
    img = mix(img, cols[1], dark * 0.95)
    grey = smooth(0.35, 0.6, np.sin((x * 0.9 - y * 1.7) * math.pi + n2 * 5)) * (1 - dark)
    img = mix(img, cols[2], grey * 0.75)
    soft = smooth(0.45, 0.7, fbm(h, w, 2, 3, seed + 9))
    img = mix(img, cols[4], soft * 0.35 * (1 - dark))
    streak = np.exp(-((np.sin((x * 2.5 + y * 0.6) * math.pi + n * 3) - 0.92) ** 2) / 0.0015) * smooth(0.4, 0.6, n2)
    img = mix(img, cols[3], streak * 0.9)
    return canvas_grain(img)


def ink_painting(h=768, w=1024, seed=21):
    """Soft grey ink wash with a dark brush stroke (bedroom, over the bed)."""
    x, y = grid(h, w)
    img = np.ones((h, w, 3)) * hexc("#f2efea")
    n = fbm(h, w, 3, 5, seed)
    wash = smooth(0.45, 0.8, n) * smooth(0.0, 0.3, 1 - abs(y - 0.55) * 2)
    img = mix(img, hexc("#9a9895"), wash * 0.7)
    stroke = np.exp(-((y - 0.45 - 0.18 * np.sin(x * 5 + n * 3)) ** 2) / 0.004) * smooth(0.15, 0.3, x) * smooth(0.95, 0.8, x)
    img = mix(img, hexc("#1e1d1c"), stroke * 0.9)
    splash = smooth(0.72, 0.8, fbm(h, w, 8, 3, seed + 4)) * smooth(0.2, 0.0, abs(x - 0.6) - 0.2)
    img = mix(img, hexc("#3a3836"), splash * 0.6)
    return canvas_grain(img, seed)


def mountain_picture(h=720, w=1280, seed=31, sunset=False):
    """Alpine landscape (home cinema screen, TV): sky gradient, layered ridges with snow, forest line, lake."""
    x, y = grid(h, w)
    top, horizon = (hexc("#3f6fb0"), hexc("#bcd6ea")) if not sunset else (hexc("#4d5a8a"), hexc("#f2b57a"))
    img = mix(top, horizon, smooth(0.0, 0.62, y))
    clouds = smooth(0.55, 0.8, fbm(h, w, 4, 5, seed)) * smooth(0.55, 0.1, y)
    img = mix(img, np.ones(3), clouds * 0.7)
    layers = [(0.30, 0.28, "#6d7f99", seed + 1, 0.9), (0.40, 0.2, "#4a5a70", seed + 2, 0.7), (0.52, 0.12, "#2f4a3c", seed + 3, 0.0)]
    for base, amp, col, s, snow in layers:
        ridge = base + amp * (0.5 - np.abs(fbm(1, w, 3, 6, s)[0] - 0.5) * 2) * -1 + amp * 0.3
        mask = y > ridge[None, :]
        shade = fbm(h, w, 12, 4, s + 7)
        c = hexc(col)[None, None, :] * (0.8 + 0.4 * shade[..., None])
        if snow:
            sn = (y < ridge[None, :] + 0.06 * snow) & (shade > 0.45)
            c = np.where(sn[..., None], hexc("#e9eef4") * (0.85 + 0.2 * shade[..., None]), c)
        img = np.where(mask[..., None], c, img)
    trees = 0.62 - 0.03 * (fbm(1, w, 60, 2, seed + 9)[0] > 0.5) - 0.02 * np.abs(np.sin(np.arange(w) * 0.9))
    img = np.where((y > trees[None, :])[..., None], hexc("#1f3326") * (0.8 + 0.3 * fbm(h, w, 30, 2, seed)[..., None]), img)
    lake = y > 0.72
    refl = img[np.clip((2 * 0.72 - y) * h, 0, h - 1).astype(int), (x * w).astype(int)]
    water = mix(refl * 0.7, hexc("#2e5a78"), 0.35 + 0.1 * fbm(h, w, 40, 2, seed + 3))
    img = np.where(lake[..., None], water, img)
    return np.clip(img, 0, 1)


def rocket_poster(h=900, w=640, seed=41, variant=0):
    """Kids' space poster: navy ground, stars, a white-and-orange rocket with flame."""
    x, y = grid(h, w)
    bg = [hexc("#1c2c4a"), hexc("#23365a"), hexc("#1a2640")][variant % 3]
    img = mix(bg, hexc("#2f4f7a"), smooth(0.2, 1.0, y) * 0.5)
    r = rng(seed)
    for _ in range(90):
        sx, sy, s = r.random(), r.random(), r.random() * 0.004 + 0.001
        img = mix(img, np.ones(3), np.exp(-(((x - sx) * w / h) ** 2 + (y - sy) ** 2) / (s * s)))
    # planet
    px, py, pr = [(0.75, 0.2, 0.12), (0.2, 0.25, 0.1), (0.8, 0.75, 0.13)][variant % 3]
    d = np.sqrt(((x - px) * w / h) ** 2 + (y - py) ** 2)
    pc = [hexc("#e0894a"), hexc("#7fb0d8"), hexc("#d9c07a")][variant % 3]
    lit = 0.65 + 0.45 * smooth(pr * 1.6, 0, np.sqrt(((x - px + 0.04) * w / h) ** 2 + (y - py + 0.04) ** 2))
    img = mix(img, pc * lit[..., None], smooth(pr + 0.004, pr - 0.004, d))
    # rocket body (tilted)
    ang = [-0.35, 0.3, -0.15][variant % 3]
    cx, cy = 0.5, 0.52
    u = (x - cx) * w / h * math.cos(ang) - (y - cy) * math.sin(ang)
    v = (x - cx) * w / h * math.sin(ang) + (y - cy) * math.cos(ang)
    body_w = 0.075 * np.sqrt(np.clip(1 - ((v + 0.02) / 0.26) ** 2, 0, 1))
    body = (np.abs(u) < body_w) & (v > -0.26) & (v < 0.2)
    img = np.where(body[..., None], hexc("#eeeeea") * (0.85 + 0.15 * (u / 0.075 + 1) / 2)[..., None], img)
    nose = body & (v < -0.12)
    img = np.where(nose[..., None], hexc("#e0663a"), img)
    win = np.sqrt(u ** 2 + (v + 0.04) ** 2) < 0.03
    img = np.where(win[..., None], hexc("#4f86c6"), img)
    fins = (np.abs(u) < 0.12 - (v - 0.12) * 0.2) & (v > 0.1) & (v < 0.2) & (np.abs(u) > 0.05)
    img = np.where(fins[..., None], hexc("#d9552e"), img)
    flame = (np.abs(u) < 0.045 * (1 - (v - 0.2) / 0.16)) & (v > 0.2) & (v < 0.36)
    img = np.where(flame[..., None], mix(hexc("#ffd35a"), hexc("#ff7a2a"), smooth(0.2, 0.36, v)), img)
    return np.clip(img, 0, 1)


# ---------------------------------------------------------------------- rugs
def rug_abstract(h=1024, w=1400, seed=51, base="#cfcac1", dark="#6e6a66", light="#ecE8e1"):
    """Low-pile rug with a soft grey marbled pattern (living room, bedroom)."""
    n = fbm(h, w, 3, 6, seed)
    n2 = fbm(h, w, 6, 4, seed + 3)
    img = np.ones((h, w, 3)) * hexc(base)
    img = mix(img, hexc(dark), smooth(0.58, 0.8, n) * 0.45)
    img = mix(img, hexc(light), smooth(0.5, 0.7, n2) * 0.5)
    vein = np.exp(-((fbm(h, w, 4, 5, seed + 8) - 0.5) ** 2) / 0.0006)
    img = mix(img, hexc(dark), vein * 0.35)
    pile = rng(seed).random((h, w)) * 0.06 - 0.03
    x, y = grid(h, w)
    border = np.minimum(np.minimum(x, 1 - x) * w, np.minimum(y, 1 - y) * h)
    img = img * (0.92 + 0.08 * smooth(0, 12, border))[..., None]
    return np.clip(img + pile[..., None], 0, 1)


def rug_round_rings(h=1024, seed=61, cols=("#3d5a80", "#c9d3dc", "#2b3e5c", "#8fa4b8")):
    """Round rug in concentric blue rings (kids' room); square image, outside the circle doesn't show."""
    x, y = grid(h, h)
    d = np.sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2) * 2
    wob = fbm(h, h, 5, 3, seed) * 0.05
    band = ((d + wob) * 5).astype(int) % len(cols)
    img = np.stack([hexc(c) for c in cols])[band]
    pile = rng(seed).random((h, h)) * 0.06 - 0.03
    return np.clip(img + pile[..., None], 0, 1)


def rug_stripe(h=512, w=1400, seed=71, base="#d8d2c8", line="#9b948a"):
    """Runner/bath mat: plain with a thin border line."""
    x, y = grid(h, w)
    img = np.ones((h, w, 3)) * hexc(base)
    bx = np.minimum(x, 1 - x) * w
    by = np.minimum(y, 1 - y) * h
    b = np.minimum(bx, by)
    img = mix(img, hexc(line), ((b > 24) & (b < 34)).astype(float))
    pile = rng(seed).random((h, w)) * 0.06 - 0.03
    return np.clip(img + pile[..., None], 0, 1)


def book_spines(h=256, w=1024, seed=81, palette=("#e9e4da", "#2f2b28", "#8b6b4e", "#b9b1a4", "#44505c", "#6d4a3a", "#d6cfc2")):
    """Row of book spines (vertical stripes of random width/colour with a lighter band) — wraps a books block."""
    r = rng(seed)
    img = np.zeros((h, w, 3))
    x0 = 0
    while x0 < w:
        bw = int(r.integers(14, 40))
        c = hexc(palette[r.integers(len(palette))]) * (0.85 + 0.25 * r.random())
        img[:, x0:x0 + bw] = c
        band = int(r.integers(h // 8, h // 3))
        img[band:band + 6, x0 + 3:x0 + bw - 3] = np.clip(c * 1.4 + 0.1, 0, 1)
        img[:, x0:x0 + 1] *= 0.6
        x0 += bw
    return np.clip(img, 0, 1)
