#!/usr/bin/env python3
"""Shared machinery of the lift texture families (tools/lifts/textures/<family>.py): metals, floors, doors, walls,
panels.

Output per material M (Assets/House4696/External/Materials/M/): M_albedo.jpg (sRGB), M_normal.jpg (OpenGL: +G = up
the image), M_mask.png (R metallic, G AO, B 0, A smoothness). Entries go to tools/lifts/textures/entries/<family>.json
and are merged into external.json with tools/doors/textures/merge_entries.py (prefixes lift_ / liftfloor_ / liftdoor_ /
liftwall_ / liftpanel_).

Everything here works on arbitrary (h, w) images; the noise is the door kit's periodic Gaussian noise (FFT), so the
tiling metals tile for free and the fitted pictures simply do not care.
Needs numpy + Pillow only.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools" / "doors" / "textures"))
import make_finishes as mf          # noqa: E402  (colour maths, periodic noise)
import merge_entries                # noqa: E402

EXT = ROOT / "Assets" / "House4696" / "External"
REF = ROOT / "tools" / "lifts" / "reference"
ENTRIES = HERE / "entries"
SHEETS = HERE / "sheets"

srgb_to_linear, linear_to_srgb = mf.srgb_to_linear, mf.linear_to_srgb


# ------------------------------------------------------------------------------------------------ colour
def lin(h):
    """'#rrggbb' -> linear RGB (3,)."""
    return mf.hex_to_linear(h)


def hexof(v_lin):
    return mf.linear_to_hex(np.asarray(v_lin, dtype=np.float64))


def mean_hex(rgb8):
    """Mean colour of an sRGB uint8 image, averaged in linear light (what a texture filtered down shows)."""
    return hexof(srgb_to_linear(rgb8.reshape(-1, 3) / 255.0).mean(0))


def to8(a_lin):
    return np.round(linear_to_srgb(a_lin) * 255).astype(np.uint8)


def mix(a, b, t):
    t = np.asarray(t)[..., None] if np.ndim(t) else t
    return a * (1 - t) + b * t


def fit_mean(alb_lin, target_hex, mask=None):
    """Scales the albedo per channel so its mean (in linear light, over mask) equals target."""
    sel = alb_lin.reshape(-1, 3) if mask is None else alb_lin[mask > 0.5]
    k = lin(target_hex) / np.maximum(sel.mean(0), 1e-6)
    return np.clip(alb_lin * k, 0, 1)


# ------------------------------------------------------------------------------------------------ noise
def noise(rng, h, w, sx, sy=None):
    """Periodic unit noise (h, w): Gaussian correlation sx px along x (columns), sy px along y (rows)."""
    return mf.gauss_noise(rng, (h, w), sx, sx if sy is None else sy)


def fbm(rng, h, w, base_px, octaves=5, gain=0.55, aniso=1.0):
    """Fractal sum, coarsest sigma base_px (x) / base_px*aniso (y), unit std."""
    acc = np.zeros((h, w))
    a, s = 1.0, float(base_px)
    for _ in range(octaves):
        acc += a * noise(rng, h, w, max(s, 0.4), max(s * aniso, 0.4))
        a *= gain
        s /= 2.0
    acc -= acc.mean()
    return acc / max(acc.std(), 1e-9)


def blur(a, sig_x, sig_y=None):
    """Gaussian blur (periodic, FFT) of a 2D field."""
    sig_y = sig_x if sig_y is None else sig_y
    if sig_x <= 0 and sig_y <= 0:
        return a
    f = np.fft.rfft2(a)
    fy = np.fft.fftfreq(a.shape[0])[:, None]
    fx = np.fft.rfftfreq(a.shape[1])[None, :]
    f *= np.exp(-2 * np.pi ** 2 * ((fx * sig_x) ** 2 + (fy * sig_y) ** 2))
    return np.fft.irfft2(f, s=a.shape)


def blur_edge(a, sig):
    """Gaussian blur with mirrored borders (no wrap-around) for fitted pictures."""
    if sig <= 0:
        return a
    p = int(3 * sig) + 2
    if a.ndim == 2:
        b = np.pad(a, p, mode="reflect")
        return blur(b, sig)[p:-p, p:-p]
    return np.stack([blur_edge(a[..., c], sig) for c in range(a.shape[2])], -1)


def blur_edge_xy(a, sx, sy):
    """Anisotropic Gaussian blur with mirrored borders."""
    px, py = int(3 * sx) + 2, int(3 * sy) + 2
    b = np.pad(a, ((py, py), (px, px)), mode="reflect")
    return blur(b, sx, sy)[py:-py, px:-px]


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def contour_lines(n, width_px, soft=0.7):
    """Lines of constant width along the zero contour of a smooth field."""
    gy, gx = np.gradient(n)
    d = np.abs(n) / np.maximum(np.hypot(gx, gy), 1e-6)
    return np.clip((width_px / 2 + soft - d) / (2 * soft), 0.0, 1.0)


def sample(field, x, y):
    """Bilinear periodic sampling."""
    h, w = field.shape
    x0, y0 = np.floor(x).astype(np.int64), np.floor(y).astype(np.int64)
    tx, ty = x - x0, y - y0
    x0, y0 = x0 % w, y0 % h
    x1, y1 = (x0 + 1) % w, (y0 + 1) % h
    return ((field[y0, x0] * (1 - tx) + field[y0, x1] * tx) * (1 - ty) +
            (field[y1, x0] * (1 - tx) + field[y1, x1] * tx) * ty)


# ------------------------------------------------------------------------------------------------ stone
def worley(rng, x, y, cell):
    """F1, F2 distances (px) to a jittered grid of points (one per cell px square, periodic over the image when the
    image size is a multiple of cell) and the id of the nearest point."""
    h, w = x.shape
    gx, gy = max(1, int(round(w / cell))), max(1, int(round(h / cell)))
    cx, cy = w / gx, h / gy
    jx = rng.random((gy, gx))
    jy = rng.random((gy, gx))
    ix = np.floor(x / cx).astype(np.int64)
    iy = np.floor(y / cy).astype(np.int64)
    f1 = np.full(x.shape, 1e9)
    f2 = np.full(x.shape, 1e9)
    cid = np.zeros(x.shape, np.int64)
    for oy in (-1, 0, 1):
        for ox in (-1, 0, 1):
            kx, ky = ix + ox, iy + oy
            px_ = (kx + jx[ky % gy, kx % gx]) * cx
            py_ = (ky + jy[ky % gy, kx % gx]) * cy
            d = np.hypot(x - px_, y - py_)
            idn = (ky % gy) * gx + (kx % gx)
            closer = d < f1
            f2 = np.where(closer, f1, np.minimum(f2, d))
            cid = np.where(closer, idn, cid)
            f1 = np.where(closer, d, f1)
    return f1, f2, cid


def stone(rng, h, w, mm, spec):
    """Polished stone / printed stone film, linear RGB (h, w, 3).

    mm: millimetres per pixel. spec keys:
      base, base2   ground colours (hex), mixed by a domain-warped cloud (cloud_mm scale)
      veins: list of vein layers, each dict(color, alpha, width_mm, scale_mm, kind, ...):
        kind 'cells' breccia: borders of warped Worley cells of scale_mm (emperador, verde alpi); tone = per-cell
                     brightness spread of the clasts
        kind 'net'   smooth crack lines: zero contours of a warped 2-octave noise of scale_mm
        kind 'dir'   long drifting veins at angle deg (carrara, pink, calacatta): contours (levels) of an anisotropic
                     noise, length_mm along x scale_mm across, warped; soft_alpha / soft_width: the grey cloud
                     that follows the veins
        breakup (0..1) share of each vein hidden by a slow on/off noise
      speck: list of dict(color, share, size_mm) - granite / terrazzo chips (thresholded fine noise)
      fleck: (color, alpha, size_mm) - faint mottling
    """
    px = 1.0 / mm
    base, base2 = lin(spec["base"]), lin(spec.get("base2", spec["base"]))
    cl = fbm(rng, h, w, spec.get("cloud_mm", 120) * px, 5, 0.6)
    wx = fbm(rng, h, w, spec.get("cloud_mm", 120) * px * 1.5, 3) * spec.get("cloud_mm", 120) * px * 0.4
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    cl = smoothstep(-1.7, 1.7, sample(cl, xx + wx, yy + wx * 0.7))
    out = mix(base, base2, cl)
    for v in spec.get("veins", []):
        col = lin(v["color"])
        wpx = v["width_mm"] * px
        kind = v["kind"]
        if kind == "cells":
            # breccia: Worley cell borders (F2 - F1) of a warped jittered grid; cells get their own tone
            c = v["scale_mm"] * px
            wq = v.get("warp_mm", v["scale_mm"] * 0.25) * px
            dx = fbm(rng, h, w, c * 0.8, 4, 0.5) * wq
            dy = fbm(rng, h, w, c * 0.8, 4, 0.5) * wq
            f1, f2, cid = worley(rng, xx + dx, yy + dy, c)
            line = np.clip((wpx / 2 + 0.7 - (f2 - f1) / 2) / 1.4, 0, 1)
            if v.get("tone"):
                r = np.random.default_rng(int(rng.integers(1 << 30))).random(cid.max() + 1)
                out = out * (1 + v["tone"] * (r[cid] - 0.5))[..., None]
        elif kind == "net":
            sc = v["scale_mm"] * px
            n = fbm(rng, h, w, sc, v.get("oct", 2), v.get("gain", 0.4))
            wq = v.get("warp_mm", v["scale_mm"] * 0.5) * px
            dx = fbm(rng, h, w, sc * 1.3, 3) * wq
            dy = fbm(rng, h, w, sc * 1.3, 3) * wq
            n = sample(n, xx + dx, yy + dy) - v.get("level", 0.0)
            line = contour_lines(n, wpx)
        else:
            # 'dir': long veins drifting along `angle` (deg, image x towards y): contours of an anisotropic fbm
            # (long along the vein) in rotated coordinates, domain-warped
            ang = math.radians(v.get("angle", 30))
            L = v.get("length_mm", 400) * px
            sp = v["scale_mm"] * px
            n0 = fbm(rng, h, w, L, v.get("oct", 4), 0.55, aniso=sp / L)
            wq = v.get("warp_mm", 40) * px
            ws = v.get("warp_scale_mm", 150) * px
            dx = fbm(rng, h, w, ws, 4, 0.55) * wq
            dy = fbm(rng, h, w, ws, 4, 0.55) * wq
            ca, sa = math.cos(ang), math.sin(ang)
            xr = (xx + dx) * ca + (yy + dy) * sa
            yr = -(xx + dx) * sa + (yy + dy) * ca
            n = sample(n0, xr, yr)
            levels = v.get("levels", (0.0, 0.9, -0.9))
            dist = np.min(np.stack([np.abs(n - lev) for lev in levels]), 0)
            line = np.zeros_like(n)
            for lev in levels:
                line = np.maximum(line, contour_lines(n - lev, wpx, soft=0.8))
            if v.get("soft_alpha"):
                # the grey cloud that follows carrara veins
                halo = np.exp(-dist ** 2 / (2 * v.get("soft_width", 0.12) ** 2))
                line = np.maximum(line, halo * v["soft_alpha"])
        if v.get("breakup", 0) > 0:
            on = fbm(rng, h, w, v.get("breakup_mm", v["scale_mm"]) * px, 3)
            thr = np.quantile(on, v["breakup"])
            line = line * smoothstep(thr - 0.3, thr + 0.3, on)
        out = mix(out, col, np.clip(line * v["alpha"], 0, 1))
    for s in spec.get("speck", []):
        n = noise(rng, h, w, max(0.5, s["size_mm"] * px * 0.5))
        thr = np.quantile(n, 1 - s["share"])
        out = mix(out, lin(s["color"]), smoothstep(thr, thr + 0.25, n))
    if spec.get("fleck"):
        c, a, sz = spec["fleck"]
        n = fbm(rng, h, w, sz * px, 3)
        out = mix(out, lin(c), np.clip(n * 0.5, 0, 1) * a)
    return np.clip(out, 0, 1)


# ------------------------------------------------------------------------------------------------ wood (wood-look film)
def woodgrain(rng, h, w, mm_x, mm_y, light, dark, contrast=1.0, flitch=None, periodic=True):
    """Vertical-grain wood film (grain along image y), linear RGB. mm_x / mm_y: mm per px across / along the grain.
    Laminations: a 1D tone table across the grain, displaced by a slow warp (the grain wanders); fine streaks; pores.
    flitch: optional centre column (px) of a cathedral-free quarter-cut: the grain bends slightly around it."""
    pxx, pxy = 1 / mm_x, 1 / mm_y
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    warp = noise(rng, h, w, 40 * pxx, 600 * pxy) * 6 * pxx + noise(rng, h, w, 15 * pxx, 150 * pxy) * 1.5 * pxx
    if flitch is not None:
        warp += np.sin(yy / h * 2 * np.pi) * 3 * pxx
    x = xx + warp
    n_tab = 8 * w
    tab = np.zeros(n_tab)
    for sig_mm, amp in ((0.25, 0.35), (0.8, 0.5), (3.0, 0.6), (12, 0.6), (40, 0.4)):
        tab += amp * mf.noise_1d(rng, n_tab, sig_mm * pxx * 8)
    tab = (tab - tab.mean()) / tab.std()
    xi = (x * 8) % n_tab
    i0 = np.floor(xi).astype(np.int64)
    f = xi - i0
    tone = tab[i0] * (1 - f) + tab[(i0 + 1) % n_tab] * f
    streak = noise(rng, h, w, 0.5 * pxx, 80 * pxy)
    pores = noise(rng, h, w, 0.35 * pxx, 2.5 * pxy)
    pore = smoothstep(1.6, 2.4, pores)
    broad = noise(rng, h, w, 120 * pxx, 900 * pxy)
    t = np.clip(0.5 + 0.22 * contrast * tone + 0.06 * contrast * streak + 0.08 * broad, 0, 1)
    out = mix(lin(light), lin(dark), t)
    out = mix(out, lin(dark) * 0.7, pore * 0.35 * contrast)
    return np.clip(out, 0, 1), tone


# ------------------------------------------------------------------------------------------------ maps
def normal_from_height(hgt, tilt_deg=None, k=None, periodic=True):
    """OpenGL normal map (uint8) from a height field (any units). tilt_deg: rms tilt of the result; or k: slope scale."""
    if periodic:
        gx = (np.roll(hgt, -1, 1) - np.roll(hgt, 1, 1)) / 2
        gr = (np.roll(hgt, -1, 0) - np.roll(hgt, 1, 0)) / 2
    else:
        gr, gx = np.gradient(hgt)
    if k is None:
        slope = np.sqrt((gx ** 2 + gr ** 2).mean())
        k = math.tan(math.radians(tilt_deg)) / max(slope, 1e-9)
    n = np.stack([-gx * k, gr * k, np.ones_like(gx)], -1)       # +G = up = -row
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return np.round((n * 0.5 + 0.5) * 255).astype(np.uint8)


def flat_normal(h, w):
    n = np.zeros((h, w, 3), np.uint8)
    n[..., 0] = 128
    n[..., 1] = 128
    n[..., 2] = 255
    return n


def mask_map(metallic, smooth, ao=None):
    """RGBA uint8: R metallic, G AO, B 0, A smoothness (inputs 0..1, scalars or arrays of one shape)."""
    shp = next(np.shape(a) for a in (metallic, smooth, ao) if a is not None and np.ndim(a) == 2)
    m = np.zeros(shp + (4,), np.uint8)
    m[..., 0] = np.round(np.clip(np.broadcast_to(metallic, shp), 0, 1) * 255)
    m[..., 1] = 255 if ao is None else np.round(np.clip(np.broadcast_to(ao, shp), 0, 1) * 255)
    m[..., 3] = np.round(np.clip(np.broadcast_to(smooth, shp), 0, 1) * 255)
    return m


def resize(a, size, resample=Image.LANCZOS):
    """Resize an (h, w[, c]) float or uint8 array to size (w, h)."""
    if a.dtype == np.uint8:
        return np.asarray(Image.fromarray(a).resize(size, resample))
    if a.ndim == 2:
        return np.asarray(Image.fromarray(a.astype(np.float32), "F").resize(size, resample), dtype=np.float64)
    return np.stack([resize(a[..., c], size, resample) for c in range(a.shape[2])], -1)


def write_material(mid, albedo8, normal8, mask8):
    folder = EXT / "Materials" / mid
    folder.mkdir(parents=True, exist_ok=True)
    Image.fromarray(albedo8).save(folder / f"{mid}_albedo.jpg", quality=90, subsampling=0, optimize=True)
    Image.fromarray(normal8).save(folder / f"{mid}_normal.jpg", quality=92, subsampling=0, optimize=True)
    Image.fromarray(mask8, "RGBA").save(folder / f"{mid}_mask.png", optimize=True)


def read_albedo(mid):
    return np.asarray(Image.open(EXT / "Materials" / mid / f"{mid}_albedo.jpg").convert("RGB"))


def read_mask(mid):
    return np.asarray(Image.open(EXT / "Materials" / mid / f"{mid}_mask.png").convert("RGBA"))


def entry(mid, name, source, meters, size, neutral=False, mask_size=None):
    e = {"id": mid, "name": name, "category": "lift", "source": source, "neutral": neutral,
         "metersPerTile": [float(meters[0]), float(meters[1])], "maxSize": int(size), "folder": f"Materials/{mid}",
         "textures": {"albedo": f"{mid}_albedo.jpg", "normal": f"{mid}_normal.jpg", "mask": f"{mid}_mask.png"}}
    if mask_size:
        e["maskSize"] = int(mask_size)
    return e


def write_entries(family, entries, merge=True):
    """Replaces the family's entries by id (keeps those of materials not rebuilt this run) and merges them."""
    ENTRIES.mkdir(parents=True, exist_ok=True)
    path = ENTRIES / f"{family}.json"
    old = json.loads(path.read_text()) if path.exists() else []
    by = {e["id"]: e for e in old}
    for e in entries:
        by[e["id"]] = e
    order = [e["id"] for e in old] + [e["id"] for e in entries if e["id"] not in {o["id"] for o in old}]
    path.write_text(json.dumps([by[i] for i in order], ensure_ascii=False, indent=1))
    if merge:
        merge_entries.merge([str(path)])
    return path


# ------------------------------------------------------------------------------------------------ drawing
class Canvas:
    """Supersampled coverage masks: draw shapes in picture fractions (u right, v up from the bottom like the engine,
    or y down when flip=False) and get a (h, w) float mask with anti-aliased edges."""

    def __init__(self, w, h, ss=4):
        self.w, self.h, self.ss = w, h, ss

    def new(self):
        im = Image.new("L", (self.w * self.ss, self.h * self.ss), 0)
        return im, ImageDraw.Draw(im)

    def P(self, u, v):
        """Fraction (u from left, v from top) -> supersampled pixel."""
        return (u * self.w * self.ss, v * self.h * self.ss)

    def done(self, im):
        return np.asarray(im.resize((self.w, self.h), Image.BOX), dtype=np.float64) / 255.0


def poly_mask(cv, pts, fill=255):
    im, d = cv.new()
    d.polygon([cv.P(u, v) for u, v in pts], fill=fill)
    return cv.done(im)


def rect_mask(cv, u0, v0, u1, v1):
    return poly_mask(cv, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)])


def font(size, bold=False):
    for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
              "/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            continue
    return ImageFont.load_default()


def fit_h(im, h):
    return im.resize((max(1, round(im.width * h / im.height)), h), Image.LANCZOS)


def sheet(rows, out, title=""):
    """rows: list of (label, [PIL images]) -> one PNG, each row a strip of images of equal height with a label."""
    pad, lab_h = 8, 22
    fnt = font(15)
    widths = [sum(i.width for i in ims) + pad * (len(ims) + 1) for _, ims in rows]
    W = max(widths + [400])
    H = sum(max(i.height for i in ims) + lab_h + pad for _, ims in rows) + (30 if title else 0)
    s = Image.new("RGB", (W, H), (236, 236, 236))
    d = ImageDraw.Draw(s)
    y = 0
    if title:
        d.text((pad, 6), title, fill=(0, 0, 0), font=font(18, True))
        y = 30
    for label, ims in rows:
        d.text((pad, y + 3), label, fill=(20, 20, 20), font=fnt)
        x = pad
        for i in ims:
            s.paste(i.convert("RGB"), (x, y + lab_h))
            x += i.width + pad
        y += max(i.height for i in ims) + lab_h + pad
    out.parent.mkdir(parents=True, exist_ok=True)
    s.save(out, optimize=True)
    return out


def lit_preview(albedo8, mask8, env=(0.25, 0.85)):
    """A crude look of the material under a soft gradient environment: metallic parts show a vertical sky gradient
    sharpened by smoothness (mirror = strong contrast, satin = flat), dielectrics their albedo. For check sheets only."""
    a = srgb_to_linear(albedo8 / 255.0)
    met = mask8[..., 0:1] / 255.0
    sm = mask8[..., 3:4] / 255.0
    h, w = a.shape[:2]
    v = np.linspace(1, 0, h)[:, None, None]
    sharp = np.clip((sm - 0.4) / 0.6, 0, 1)
    band = 0.5 + 0.5 * np.tanh((v - 0.55) * (2 + 18 * sharp))       # bright upper reflection, dark lower
    envl = env[0] + (env[1] - env[0]) * (band * sharp + 0.62 * (1 - sharp))
    col = a * (met * envl * 1.15 + (1 - met) * 0.85)
    return Image.fromarray(to8(col))


# ------------------------------------------------------------------------------------------------ metre-space drawing
class MCanvas:
    """Supersampled coverage mask drawn in metres: x right, y UP from the bottom edge (the engine's v), over a
    picture of W x H metres at w x h px. Shapes are painted with value 255 (add) or 0 (erase); mask() -> (h, w) 0..1."""

    def __init__(self, W, H, w, h, ss=4):
        self.W, self.H, self.w, self.h, self.ss = W, H, w, h, ss
        self.im = Image.new("L", (w * ss, h * ss), 0)
        self.d = ImageDraw.Draw(self.im)

    def P(self, x, y):
        return (x / self.W * self.w * self.ss, (1 - y / self.H) * self.h * self.ss)

    def S(self, m):
        """metres -> supersampled px (x scale)."""
        return m / self.W * self.w * self.ss

    def poly(self, pts, v=255):
        self.d.polygon([self.P(x, y) for x, y in pts], fill=v)

    def rect(self, x0, y0, x1, y1, v=255):
        self.poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], v)

    def line(self, pts, width, v=255):
        pp = [self.P(x, y) for x, y in pts]
        wpx = max(1, int(round(self.S(width))))
        self.d.line(pp, fill=v, width=wpx, joint="curve")
        r = wpx / 2
        for p in (pp[0], pp[-1]):
            self.d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=v)

    def circle(self, cx, cy, r, v=255):
        (px, py), rr = self.P(cx, cy), self.S(r)
        ry = r / self.H * self.h * self.ss
        self.d.ellipse([px - rr, py - ry, px + rr, py + ry], fill=v)

    def ring(self, cx, cy, r, width, v=255):
        (px, py) = self.P(cx, cy)
        rr, ry = self.S(r + width / 2), (r + width / 2) / self.H * self.h * self.ss
        self.d.ellipse([px - rr, py - ry, px + rr, py + ry], outline=v, width=max(1, int(round(self.S(width)))))

    def arc_pts(self, cx, cy, r, a0, a1, n=96):
        return [(cx + r * math.cos(a), cy + r * math.sin(a)) for a in np.linspace(a0, a1, n)]

    def mask(self):
        return np.asarray(self.im.resize((self.w, self.h), Image.BOX), dtype=np.float64) / 255.0


def etched_metal(rng, w, h, mm_x, mm_y, base, etch, bg_smooth=0.95, hairline=None, etch_smooth=0.48,
                 etch_light=1.13, metallic=1.0, seam_u=None, extra_height=None):
    """A fitted picture of etched / mirror / hairline metal.
    base: hex or (h, w, 3) linear colour of the metal; etch: (h, w) 0..1 frosted (etched) areas;
    bg_smooth: smoothness of the un-etched metal (scalar or (h, w)); hairline: (h, w) 0..1 where the un-etched metal
    is brushed (vertical lines in albedo / normal); seam_u: list of u (0..1) where leaves / panels meet (dark line).
    Returns albedo8, normal8, mask8."""
    col = np.broadcast_to(lin(base) if isinstance(base, str) else base, (h, w, 3)).copy()
    hair = noise(rng, h, w, 0.5, 120 / mm_y) * 0.7 + noise(rng, h, w, 1.5, 400 / mm_y) * 0.5
    hair = hair / hair.std()
    spark = noise(rng, h, w, 0.6)
    hl = np.zeros((h, w)) if hairline is None else hairline
    a = col * (1 + 0.035 * (hl * hair)[..., None])
    a = a * (1 + (etch_light - 1) * etch + 0.04 * etch * spark)[..., None]
    sm = np.broadcast_to(bg_smooth, (h, w)) * (1 - etch) + etch_smooth * etch
    hgt = -1.0 * K_blur(etch) + 0.06 * hl * hair + 0.05 * etch * spark
    if extra_height is not None:
        hgt = hgt + extra_height
    ao = np.ones((h, w))
    if seam_u:
        xs = np.arange(w)[None, :] + 0.5
        for u in seam_u:
            d = np.abs(xs - u * w)
            sl = np.clip(1.2 - d, 0, 1) * np.ones((h, 1))
            a = a * (1 - 0.6 * sl)[..., None]
            ao = np.minimum(ao, 1 - 0.5 * sl)
            hgt = hgt - 2.0 * sl
    nrm = normal_from_height(hgt, k=0.35, periodic=False)
    msk = mask_map(metallic, sm, ao)
    return to8(np.clip(a, 0, 1)), nrm, msk


def K_blur(m):
    return blur_edge(m, 0.6)
