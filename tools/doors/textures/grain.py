#!/usr/bin/env python3
"""Shared machinery of the door finish families laminate / pvc / enamel / solid (waves 2-5): printed wood decors with
crown-cut figure (cathedrals, eyes), straight-grain prints, glued pine lamellas and plain painted / white surfaces.

The family modules (tools/doors/textures/laminate.py, pvc.py, enamel.py, solid.py) hold the finishes, their colours
and the catalogue crops; this module builds the structures and writes everything:

    python3 tools/doors/textures/<family>.py                       # textures + entries + Finishes/<family>.json + merge
    python3 tools/doors/textures/<family>.py l-11-italoreh         # only these finishes (the family files stay whole)
    python3 tools/doors/textures/<family>.py --compare             # + tools/doors/.cache/finishes_<family>.png
    python3 tools/doors/textures/<family>.py --no-write --compare  # check sheet only
    python3 tools/doors/textures/<family>.py --fit                 # suggest comb / tone from the photos
    python3 tools/doors/textures/<family>.py --slopes              # hue of the photos' tone variation (dark / light)

Needs numpy and Pillow; the photos (tools/doors/.cache, see tools/doors/catalog_index.py) only for --compare / --fit /
--slopes. Deterministic (fixed seeds). Output per finish as wave 1's make_finishes.py (whose helpers it imports):
albedo 2048x1024 sRGB (grain along U = image x, U up the leaf), normal 1024x512 OpenGL, mask 256x128 (R metallic, G AO,
A smoothness); the tile is 2.0 m x 1.0 m and wraps both ways.

Structures (PATTERNS; lengths in mm):
  * flitch - the decor is a set of veneer flitches side by side across the tile (`width`, soft joins `blend`, or a
    glue line for lamellas). A crown-cut flitch is a plane through a tapered log with undulating rings: at a point
    (x along, u across from the pith line) the radius is R = sqrt(u^2 + h(x)^2) + taper*x + wobble, where h(x) is the
    plane's depth under the rings (dips make eyes) and the taper tips the cathedrals up the leaf (+U). A quarter flitch
    has R = u + wobble (straight lines). Rings are a random sequence of widths (`spacing`), periodic in R so that the
    tile wraps (taper*2000 mm is exactly one period); each ring has its own line strength and tone. A ring's line is
    a `profile` (soft latewood band, sharp conifer latewood, thin light line, earlywood pore band) summed from a few
    harmonics, each damped by the local line density (anti-aliased at the texture's own pixel size).
  * pores (dark) / streaks (light): short lines along the grain, as wave 1 draws them; knots (pine): small dark
    ellipses with the rings bent round them.
  * plain - paint and white films: a faint mottle and, in the normal map, the orange peel of sprayed enamel or the
    fine texture of a film.
Colour as wave 1 (make_finishes.albedo_linear): the ground follows `comb` x (ring lines, fibre) + `tone` x (flitch
tones, bands) in L* units towards the `dark` / `light` colours, pores and streaks at full strength are those colours,
and the mean in linear light is exactly `color` (the catalogue's). `dark` / `light` hues follow the photos' a*, b*
against L* (--slopes).
"""
import argparse
import io
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import make_finishes as mf
from make_finishes import (ALBEDO, MASK, MM, NORMAL, TILE_M, CACHE, EXT, ROOT, box_down, draw_lines, gauss_noise,
                           hex_to_linear, lab_stats, linear_to_hex, linear_to_lab, linear_to_srgb, noise_1d,
                           srgb_to_linear, warp_rows)

W, H = ALBEDO
L_MM = W * MM                       # tile length along the grain, mm (2000)
PHOTO_MM = mf.PHOTO_MM
AA_PX = 0.35                        # Gaussian footprint of a texel (px) that damps the ring lines' harmonics
FINISHES_DIR = ROOT / "Assets" / "House4696" / "Resources" / "Doors" / "Finishes"
ENTRIES_DIR = Path(__file__).resolve().parent / "entries"

# ------------------------------------------------------------------------------------------------ patterns
# flitch: width = (median, log-sigma) across; blend = soft join; glue = (darkness 0..1, width) of a glue line instead;
#   crown = share of crown-cut flitches (else quarter); pith = where the pith line lies across a flitch (fractions);
#   sweep = (amp, corr) wander of the pith line; h0 = depth range, hamp / hcorr = its variation along, hmin = floor;
#   taper = range (0 = no drift: eyes only); period = ring sequence period when the taper is 0 or quarter-cut;
#   spacing = ring width (mean, log-sigma); profile / K = line shape and harmonics; amp_sig = line strength per ring;
#   ring_tone = tone per ring (bands between lines); fade = (log-sigma, along, across) of line strength;
#   wobble = octaves (amp, along, across) of radial jitter; flitch_contrast = log-sigma of a flitch's line contrast;
#   flitch_tone = share of the flitches' own tones in the broad field, bands / cluster as wave 1;
#   pores / streaks = wave 1 line specs (dark / light); fibre = (across, along), fibre_share = its share of `fine`;
#   knots = (per m^2, size range, ring bend); relief = what the normal map embosses and its rms tilt.
# plain: mottle = (across, along) of the faint tone variation; peel = (sigma, share of a broader wave) of the orange
#   peel; relief tilt.
PATTERNS = {
    # Italian walnut print (ИталОрех): flame cathedrals up the leaf, flitches of clearly different tone
    "ital": dict(
        kind="flitch", seed=1101,
        width=(190.0, 0.3), blend=8.0, crown=0.8, pith=(0.25, 0.75), sweep=(10.0, 600.0),
        h0=(14.0, 45.0), hamp=14.0, hcorr=280.0, hmin=5.0, taper=(0.06, 0.09), period=300.0,
        spacing=(7.5, 0.4), profile="late", K=16, amp_sig=0.45, ring_tone=0.55,
        fade=(0.45, 70.0, 6.0), wobble=[(2.5, 350.0, 45.0), (0.7, 40.0, 5.0), (0.25, 10.0, 1.2)],
        flitch_contrast=0.25, flitch_tone=0.75, bands=(25.0, 700.0), cluster=(4.0, 160.0), cluster_share=0.4,
        pores=dict(per_cm=2.2, width=(0.35, 0.3), length=(14.0, 0.7), alpha=(0.15, 0.55), fade=0.7, slope=0.004),
        streaks=None, fade_len=12.0, fibre=(0.5, 12.0), fibre_share=0.35,
        relief=dict(ring=0.25, pores=1.0, fibre=0.35, tilt_deg=0.9),
    ),
    # Milan walnut print (МиланОрех): eyes and cathedrals in columns ~270 mm apart, flitches alike in tone
    "milan": dict(
        kind="flitch", seed=1201,
        width=(265.0, 0.2), blend=14.0, crown=1.0, pith=(0.3, 0.7), sweep=(12.0, 500.0),
        h0=(18.0, 45.0), hamp=24.0, hcorr=260.0, hmin=5.0, taper=(0.04, 0.06), period=300.0,
        spacing=(8.0, 0.4), profile="late", K=16, amp_sig=0.45, ring_tone=0.45,
        fade=(0.45, 70.0, 6.0), wobble=[(2.5, 350.0, 45.0), (0.7, 40.0, 5.0), (0.25, 10.0, 1.2)],
        flitch_contrast=0.2, flitch_tone=0.4, bands=(25.0, 700.0), cluster=(4.0, 160.0), cluster_share=0.4,
        pores=dict(per_cm=2.0, width=(0.35, 0.3), length=(14.0, 0.7), alpha=(0.12, 0.45), fade=0.7, slope=0.004),
        streaks=None, fade_len=12.0, fibre=(0.5, 12.0), fibre_share=0.35,
        relief=dict(ring=0.25, pores=1.0, fibre=0.35, tilt_deg=0.9),
    ),
    # wenge print (Венге): straight, dense grain - thin lighter lines on a dark ground, flitches of different tone
    "wenge": dict(
        kind="flitch", seed=1301,
        width=(150.0, 0.3), blend=6.0, crown=0.0, pith=(0.2, 0.8), sweep=(8.0, 600.0),
        h0=(60.0, 140.0), hamp=10.0, hcorr=400.0, hmin=5.0, taper=(0.05, 0.07), period=260.0,
        spacing=(2.6, 0.5), profile="light", K=12, amp_sig=0.7, ring_tone=0.25,
        fade=(0.6, 40.0, 3.0), wobble=[(2.5, 300.0, 40.0), (0.6, 40.0, 4.0), (0.2, 12.0, 1.0)],
        flitch_contrast=0.3, flitch_tone=0.7, bands=(20.0, 700.0), cluster=(3.0, 150.0), cluster_share=0.4,
        pores=dict(per_cm=3.0, width=(0.3, 0.3), length=(10.0, 0.7), alpha=(0.2, 0.6), fade=0.7, slope=0.003),
        streaks=None, fade_len=10.0, fibre=(0.4, 10.0), fibre_share=0.3,
        relief=dict(ring=0.2, pores=1.0, fibre=0.35, tilt_deg=0.9),
    ),
    # Shimo ash print (Шимо): ash-like streaks - long, straight to gently arched lines of the earlywood pores,
    # rings of clearly different tone, some broad arches
    "shimo": dict(
        kind="flitch", seed=1401,
        width=(170.0, 0.3), blend=8.0, crown=0.5, pith=(0.1, 0.9), sweep=(10.0, 500.0),
        h0=(40.0, 110.0), hamp=15.0, hcorr=300.0, hmin=6.0, taper=(0.05, 0.07), period=260.0,
        spacing=(4.5, 0.5), profile="pore", K=12, amp_sig=0.55, ring_tone=0.7,
        fade=(0.6, 60.0, 4.0), wobble=[(2.5, 300.0, 40.0), (0.6, 40.0, 4.0), (0.2, 12.0, 1.0)],
        flitch_contrast=0.3, flitch_tone=0.6, bands=(20.0, 600.0), cluster=(3.0, 140.0), cluster_share=0.4,
        pores=dict(per_cm=3.0, width=(0.35, 0.3), length=(10.0, 0.7), alpha=(0.15, 0.5), fade=0.7, slope=0.003),
        streaks=dict(per_cm=0.6, width=(0.8, 0.4), length=(60.0, 0.8), alpha=(0.2, 0.7), fade=0.8, slope=0.002),
        fade_len=12.0, fibre=(0.4, 10.0), fibre_share=0.3,
        relief=dict(ring=0.3, pores=1.0, fibre=0.35, tilt_deg=1.2),
    ),
    # unfinished solid pine, glued lamellas: sharp orange latewood, cathedrals in the flat-sawn lamellas, straight
    # lines in the rift ones, a few small sound knots; the raised latewood of sanded softwood in the relief
    "pine": dict(
        kind="flitch", seed=1501,
        width=(62.0, 0.25), glue=(0.22, 0.4), crown=0.6, pith=(-0.3, 1.3), sweep=(4.0, 500.0),
        h0=(25.0, 90.0), hamp=8.0, hcorr=250.0, hmin=4.0, taper=(0.05, 0.07), period=220.0,
        spacing=(5.5, 0.5), profile="sharp", K=16, amp_sig=0.35, ring_tone=0.15,
        fade=(0.4, 100.0, 8.0), wobble=[(1.5, 400.0, 40.0), (0.3, 80.0, 8.0)],
        flitch_contrast=0.3, flitch_tone=0.7, bands=(15.0, 500.0), cluster=(3.0, 150.0), cluster_share=0.3,
        pores=dict(per_cm=0.25, width=(0.3, 0.3), length=(8.0, 0.6), alpha=(0.1, 0.3), fade=0.6, slope=0.003),
        streaks=None, fade_len=10.0, fibre=(0.5, 15.0), fibre_share=0.2,
        knots=(1.5, (4.0, 12.0), 0.8),
        relief=dict(ring=-0.6, pores=0.5, fibre=0.5, tilt_deg=1.8),
    ),
    # plain white paper laminate: faint mottle, a trace of paper texture under the gloss
    "paper": dict(kind="plain", seed=2301, mottle=(1.2, 2.5), cloud=60.0, peel=(1.6, 0.3), relief=dict(tilt_deg=0.35)),
    # plain white PVC film: a fine even grain in the film
    "film": dict(kind="plain", seed=2401, mottle=(1.2, 2.5), cloud=60.0, peel=(1.3, 0.25), relief=dict(tilt_deg=0.6)),
    # sprayed enamel on MDF, satin: orange peel
    "enamel": dict(kind="plain", seed=2501, mottle=(1.5, 1.5), cloud=80.0, peel=(2.2, 0.35), relief=dict(tilt_deg=0.9)),
}


# ------------------------------------------------------------------------------------------------ small helpers
def lab_to_linear(lab):
    """CIE L*a*b* (D65) -> linear sRGB (inverse of make_finishes.linear_to_lab)."""
    lab = np.asarray(lab, dtype=np.float64)
    fy = (lab[..., 0] + 16) / 116
    fx = fy + lab[..., 1] / 500
    fz = fy - lab[..., 2] / 200
    d = 6 / 29
    inv = lambda f: np.where(f > d, f ** 3, 3 * d * d * (f - 4 / 29))
    xyz = np.stack([inv(fx), inv(fy), inv(fz)], -1) * mf._WHITE
    return xyz @ np.linalg.inv(mf._M).T


def lab_hex(L, a, b):
    return linear_to_hex(np.clip(lab_to_linear([L, a, b]), 0, 1))


def smooth01(t):
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3 - 2 * t)


def dper(a, axis):
    """Central difference on the torus (per pixel)."""
    return (np.roll(a, -1, axis) - np.roll(a, 1, axis)) / 2


def unit(a):
    a = a - a.mean()
    s = a.std()
    return a / s if s > 1e-12 else a


def _wrapd(a, c):
    d = (a - c) % 1.0
    return np.minimum(d, 1 - d)


# ------------------------------------------------------------------------------------------------ rings
def profile_coeffs(kind, k_max):
    """Fourier coefficients (k = 1..k_max) of a ring's tone across it: phase 0 = start of the ring (earlywood),
    1 = its end (latewood). Zero mean; dark < 0 < light."""
    phi = (np.arange(4096) + 0.5) / 4096
    if kind == "late":            # walnut: the ring darkens towards its end, a crisp edge to the next earlywood
        p = -0.75 * smooth01((phi - 0.3) / 0.62) ** 1.3 - 0.35 * np.exp(-0.5 * ((phi - 0.97) / 0.025) ** 2)
    elif kind == "soft":          # a soft darker latewood band
        p = -np.exp(-0.5 * (_wrapd(phi, 0.72) / 0.13) ** 2)
    elif kind == "sharp":         # conifer: a latewood band (last ~30 % of the ring), abrupt at the next ring
        p = -smooth01((phi - 0.6) / 0.16) * (0.8 + 0.2 * phi)
    elif kind == "light":         # a thin light band (wenge's parenchyma)
        p = np.exp(-0.5 * (_wrapd(phi, 0.5) / 0.09) ** 2)
    elif kind == "pore":          # ring-porous: dark earlywood pore band at the start of the ring (ash)
        p = -np.exp(-0.5 * (_wrapd(phi, 0.14) / 0.1) ** 2)
    else:
        raise ValueError(kind)
    c = np.fft.rfft(p) / len(p)
    return c[1:k_max + 1]


def eval_profile(coef, phase, sig):
    """Sum of the profile's harmonics at `phase` (0..1), each damped by a Gaussian of `sig` rings (the pixel's
    footprint in ring units) - the line pattern anti-aliased where the rings get dense."""
    out = np.zeros_like(phase)
    s2 = -2 * np.pi ** 2 * sig * sig
    for k, ck in enumerate(coef, 1):
        ang = 2 * np.pi * k * phase
        out += 2 * (ck.real * np.cos(ang) - ck.imag * np.sin(ang)) * np.exp(s2 * k * k)
    return out


class Rings:
    """Growth rings along the radius: random widths (log-normal), periodic with `period` mm."""

    def __init__(self, rng, period, mean, sig):
        n = max(3, int(round(period / mean)))
        w = np.exp(sig * rng.standard_normal(n))
        w *= period / w.sum()
        self.w, self.n, self.period = w, n, period
        self.edges = np.concatenate([[0.0], np.cumsum(w)])

    def index(self, R):
        """Ring number (int), phase in the ring (0..1) and the ring's width at radius R (mm)."""
        q = np.floor(R / self.period)
        r = R - q * self.period
        i = np.clip(np.searchsorted(self.edges, r, side="right") - 1, 0, self.n - 1)
        frac = np.clip((r - self.edges[i]) / self.w[i], 0.0, 1 - 1e-9)
        return q.astype(np.int64) * self.n + i, frac, self.w[i]


def per_ring(vals, idx, frac, lo, hi):
    """A per-ring value that changes smoothly from the previous ring's inside [lo, hi] of the phase."""
    n = len(vals)
    i = idx % n
    s = smooth01((frac - lo) / (hi - lo))
    return vals[(i - 1) % n] * (1 - s) + vals[i] * s


def flitch_layout(rng, med, sig):
    """Widths (mm) of the flitches across the 1000 mm tile and the row where the first one starts."""
    ws = []
    while sum(ws) < 1000.0:
        ws.append(med * math.exp(sig * rng.standard_normal()))
    if len(ws) > 1 and sum(ws) - 1000.0 > ws[-1] / 2:
        ws.pop()
    ws = np.array(ws) * (1000.0 / sum(ws))
    return ws, rng.uniform(0, H)


# ------------------------------------------------------------------------------------------------ structures
def flitch_structure(p, seed=None):
    """Fields of a flitch pattern at albedo resolution: fine (ring lines + fibre), broad (flitch tones + bands), both
    unit std; dark / light opacity (pores, knots / streaks); height (for the normal map)."""
    rng = np.random.default_rng(p["seed"] if seed is None else seed)
    px = 1.0 / MM
    xs = np.arange(W) * MM
    wob = np.zeros((H, W))
    for amp, along, across in p["wobble"]:
        wob += amp * gauss_noise(rng, (H, W), along * px, across * px)
    wob_x, wob_y = dper(wob, 1) / MM, dper(wob, 0) / MM
    fs, fa, fc = p["fade"]
    fade = np.exp(fs * gauss_noise(rng, (H, W), fa * px, fc * px))
    ws, start = flitch_layout(rng, *p["width"])
    edges = start + np.concatenate([[0.0], np.cumsum(ws)]) * px
    glue = p.get("glue")
    m = (0.0 if glue else p["blend"]) * px
    coef = profile_coeffs(p["profile"], p["K"])
    knots = []
    ring = np.zeros((H, W))
    ftone = np.zeros((H, 1))
    wsum = np.zeros((H, 1))
    gl = np.zeros((H, 1))
    for k in range(len(ws)):
        y0, y1 = edges[k], edges[k + 1]
        rows = np.arange(int(math.floor(y0 - m)) - 1, int(math.ceil(y1 + m)) + 2)
        if m > 0:
            wgt = smooth01((rows - (y0 - m / 2)) / m) * smooth01(((y1 + m / 2) - rows) / m)
        else:   # hard join: exact pixel coverage of the lamella
            wgt = np.clip(np.minimum(rows + 0.5, y1) - np.maximum(rows - 0.5, y0), 0.0, 1.0)
        keep = wgt > 0
        rows, wgt = rows[keep], wgt[keep]
        rr = rows % H
        crown = rng.uniform() < p["crown"]
        c0 = (y0 + rng.uniform(*p["pith"]) * (y1 - y0)) * MM
        sweep = p["sweep"][0] * noise_1d(rng, W, p["sweep"][1] * px)
        cp = dper(sweep, 0) / MM
        u = rows[:, None] * MM - (c0 + sweep)[None, :]
        tau = rng.uniform(*p["taper"]) if crown else 0.0
        kn = np.zeros((len(rows), W))
        if p.get("knots"):
            kn = knot_bend(rng, p["knots"], rows, y0, y1, knots)
        if crown:
            h0 = rng.uniform(*p["h0"])
            hraw = h0 + p["hamp"] * noise_1d(rng, W, p["hcorr"] * px)
            h = np.sqrt(hraw ** 2 + p["hmin"] ** 2)
            hp = dper(h, 0) / MM
            rho = np.sqrt(u * u + h[None, :] ** 2)
            R = rho + tau * xs[None, :] + wob[rr] + kn
            dRx = (h * hp)[None, :] / rho - u / rho * cp[None, :] + tau + wob_x[rr]
            dRy = u / rho + wob_y[rr]
            period = tau * L_MM if tau > 0 else p["period"]
        else:
            sgn = 1.0 if rng.uniform() < 0.5 else -1.0
            R = sgn * u + wob[rr] + kn + 1000.0
            dRx = -sgn * cp[None, :] + wob_x[rr]
            dRy = sgn + wob_y[rr]
            period = p["period"]
        if p.get("knots"):
            dRx = dRx + dper(kn, 1) / MM
            dRy = dRy + np.vstack([np.diff(kn, axis=0), np.zeros((1, W))]) / MM
        rings = Rings(rng, period, *p["spacing"])
        idx, frac, sw = rings.index(R)
        dens = np.sqrt(dRx ** 2 + dRy ** 2) / sw * MM                   # rings per pixel
        amp = np.clip(np.exp(p["amp_sig"] * rng.standard_normal(rings.n)), 0.15, 2.2)
        tone = rng.standard_normal(rings.n)
        a = per_ring(amp, idx, frac, 0.05, 0.45)
        e = per_ring(tone, idx, frac, 0.0, 1.0) if p["profile"] != "sharp" else per_ring(tone, idx, frac, 0.0, 0.3)
        line = eval_profile(coef, frac, dens * AA_PX)
        contrast = math.exp(p["flitch_contrast"] * rng.standard_normal())
        t = contrast * (a * fade[rr] * line + p["ring_tone"] * e)
        ring[rr] += wgt[:, None] * t
        wsum[rr] += wgt[:, None]
        ftone[rr] += wgt[:, None] * rng.standard_normal()
        if glue:                                                        # glue line on the lamella's lower edge
            gw = glue[1] * px
            gl[rr] += (np.clip(1 - np.abs(rows + 0.0 - y0) / max(gw, 0.5), 0, 1) * glue[0])[:, None]
    ring /= wsum
    ftone /= wsum
    # broad tone: the flitches' own tones, bands and clusters along the grain
    band = gauss_noise(rng, (H, W), p["bands"][1] * px, p["bands"][0] * px)
    clus = gauss_noise(rng, (H, W), p["cluster"][1] * px, p["cluster"][0] * px)
    cs = p["cluster_share"]
    broad = math.sqrt(1 - cs) * band + math.sqrt(cs) * clus
    ft = p["flitch_tone"]
    broad = math.sqrt(1 - ft) * unit(broad) + math.sqrt(ft) * unit(np.broadcast_to(ftone, (H, W)).copy())
    fibre = gauss_noise(rng, (H, W), p["fibre"][1] * px, p["fibre"][0] * px)
    fsh = p["fibre_share"]
    fine = math.sqrt(1 - fsh) * unit(ring) + math.sqrt(fsh) * fibre
    dark = np.zeros((H, W))
    light = np.zeros((H, W))
    env = noise_1d(rng, 1 << 18, p["fade_len"] * px)
    disp = wob * px
    if p.get("pores"):
        acc = np.zeros((H, W))
        draw_lines(rng, acc, p["pores"], disp, env, px)
        dark = 1 - np.exp(-acc)
    if p.get("streaks"):
        acc = np.zeros((H, W))
        draw_lines(rng, acc, p["streaks"], disp, env, px)
        light = 1 - np.exp(-acc)
    if knots:
        dark = 1 - (1 - dark) * (1 - knot_spots(knots))
    if glue:
        dark = 1 - (1 - dark) * (1 - np.broadcast_to(gl, (H, W)))
    rel = p["relief"]
    height = rel["ring"] * unit(ring) - rel["pores"] * dark + rel["fibre"] * fibre
    return dict(fine=unit(fine), broad=unit(broad), dark=dark, light=light, height=height,
                tilt=rel["tilt_deg"], ring=ring)


def knot_bend(rng, spec, rows, y0, y1, out):
    """Radial displacement (mm) of the rings round the knots of one lamella; the knots are appended to `out`."""
    per_m2, (smin, smax), bend = spec
    area = (y1 - y0) * MM * L_MM / 1e6
    n = rng.poisson(per_m2 * area)
    disp = np.zeros((len(rows), W))
    xs = np.arange(W)
    for _ in range(n):
        size = rng.uniform(smin, smax)                  # mm, across
        kx = rng.uniform(0, W)
        ky = rng.uniform(y0 + 0.2 * (y1 - y0), y1 - 0.2 * (y1 - y0))
        ax, ay = size * 1.6 / MM, size / MM / 2          # half-axes in px (elongated along the grain)
        dx = (xs[None, :] - kx + W / 2) % W - W / 2
        dy = rows[:, None] - ky
        r2 = (dx / (ax * 2.2)) ** 2 + (dy / (ay * 2.2)) ** 2
        disp += bend * size * np.exp(-r2)
        out.append((kx, ky, ax, ay, rng.uniform(0.55, 0.95)))
    return disp


def knot_spots(knots):
    """Opacity of the knots themselves: a dark ellipse with a darker rim."""
    acc = np.zeros((H, W))
    ys, xs = np.arange(H), np.arange(W)
    for kx, ky, ax, ay, a in knots:
        dx = (xs[None, :] - kx + W / 2) % W - W / 2
        dy = (ys[:, None] - ky + H / 2) % H - H / 2
        r = np.sqrt((dx / ax) ** 2 + (dy / ay) ** 2)
        body = smooth01((1.1 - r) / 0.25) * 0.55 + np.exp(-((r - 0.95) / 0.12) ** 2) * 0.45
        acc = 1 - (1 - acc) * (1 - np.clip(a * body, 0, 0.97))
    return acc


def plain_structure(p, seed=None):
    """Paint / white film: a faint mottle (fine and broad, unit std) and the surface relief."""
    rng = np.random.default_rng(p["seed"] if seed is None else seed)
    px = 1.0 / MM
    fine = gauss_noise(rng, (H, W), p["mottle"][1] * px, p["mottle"][0] * px)
    broad = gauss_noise(rng, (H, W), p["cloud"] * px, p["cloud"] * px)
    s, broad_share = p["peel"]
    pe = gauss_noise(rng, (H, W), s * px, s * px)
    pe2 = gauss_noise(rng, (H, W), 3 * s * px, 3 * s * px)
    height = math.sqrt(1 - broad_share) * pe + math.sqrt(broad_share) * pe2
    zero = np.zeros((H, W))
    return dict(fine=fine, broad=broad, dark=zero, light=zero, height=height, tilt=p["relief"]["tilt_deg"])


def structure(pattern, seed=None):
    p = PATTERNS[pattern]
    return (flitch_structure if p["kind"] == "flitch" else plain_structure)(p, seed)


def finish_structure(fin, cache):
    key = (fin["pattern"], fin.get("seed"))
    if key not in cache:
        cache[key] = structure(*key)
    return cache[key]


# ------------------------------------------------------------------------------------------------ maps
def albedo(fin, st):
    return mf.albedo_linear(fin, st)


def normal_map(st):
    f = W // NORMAL[0]
    hgt = box_down(st["height"], f)
    gx = dper(hgt, 1)
    gr = dper(hgt, 0)
    slope = np.sqrt(gx ** 2 + gr ** 2)
    k = math.tan(math.radians(st["tilt"])) / max(1e-9, np.sqrt((slope ** 2).mean()))
    n = np.stack([-gx * k, gr * k, np.ones_like(gx)], -1)            # OpenGL: +Y (green) = up = -row
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return np.round((n * 0.5 + 0.5) * 255).astype(np.uint8)


def mask_map(fin, st):
    """Smoothness `smooth`, a little lower in the pores (and where `smooth_var` says: pine's earlywood)."""
    f = W // MASK[0]
    d = box_down(st["dark"], f)
    sm = fin["smooth"] * 255 - 25.0 * d
    if fin.get("smooth_var") and "ring" in st:
        r = np.clip(box_down(unit(st["ring"]), f), -2.0, 2.0)
        sm = sm - fin["smooth_var"] * 255 * r        # latewood (ring < 0) a little smoother
    m = np.zeros((MASK[1], MASK[0], 4), np.uint8)
    m[..., 1] = 255
    m[..., 3] = np.round(np.clip(sm, 20, 240)).astype(np.uint8)
    return m


def write_finish(fin, st, alb):
    mid = fin["material"]
    folder = EXT / "Materials" / mid
    folder.mkdir(parents=True, exist_ok=True)
    rgb = np.round(linear_to_srgb(alb) * 255).astype(np.uint8)
    Image.fromarray(rgb).save(folder / f"{mid}_albedo.jpg", quality=90, subsampling=0, optimize=True)
    Image.fromarray(normal_map(st)).save(folder / f"{mid}_normal.jpg", quality=92, subsampling=0, optimize=True)
    Image.fromarray(mask_map(fin, st)).save(folder / f"{mid}_mask.png", optimize=True)


def manifest_entry(fin, source, line):
    mid = fin["material"]
    return {"id": mid, "name": "%s (%s)" % (fin["name"], fin.get("tag", line)), "category": "door", "source": source,
            "neutral": False, "metersPerTile": list(TILE_M), "maxSize": ALBEDO[0], "folder": f"Materials/{mid}",
            "textures": {"albedo": f"{mid}_albedo.jpg", "normal": f"{mid}_normal.jpg", "mask": f"{mid}_mask.png"}}


# ------------------------------------------------------------------------------------------------ photos, check sheet
def photo(fname):
    return Image.open(CACHE / "photos" / fname)


def photo_crop(fname, box):
    im = photo(fname)
    lin = srgb_to_linear(np.asarray(im.convert("RGB").crop(box), dtype=np.float64) / 255)
    return lin, im.height / PHOTO_MM


def upright(alb):
    """The tile as the leaf shows it: grain vertical, U (image x) up."""
    return np.rot90(alb)


def as_photo(alb, fname):
    """The texture the way a catalogue photo shows it (U up): downsized to the photo's scale (Lanczos in sRGB) and
    JPEG-compressed with the photo's own quantization tables (4:2:0)."""
    ref = photo(fname)
    scale = ref.height / PHOTO_MM
    v = upright(alb)
    size = (int(round(v.shape[1] * MM * scale)), int(round(v.shape[0] * MM * scale)))
    img = Image.fromarray(np.round(linear_to_srgb(v) * 255).astype(np.uint8)).resize(size, Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", qtables=ref.quantization, subsampling=2)
    return srgb_to_linear(np.asarray(Image.open(buf).convert("RGB"), dtype=np.float64) / 255)


STATS = ("sx", "fine", "band")


def measure(fin, alb, refs):
    """Photo vs texture: mean colour (linear) and L* contrast statistics over the finish's crops."""
    rng = np.random.default_rng(1)
    pm, wsum, ph, tx, shown = np.zeros(3), 0.0, [], [], {}
    for fname, box in refs:
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


def slopes(fin, refs):
    """a*, b* against L* inside the finish's crops (the hue of its dark / light variation) and the L* spread."""
    Ls, As, Bs = [], [], []
    for fname, box in refs:
        lin, _ = photo_crop(fname, box)
        lab = linear_to_lab(lin).reshape(-1, 3)
        Ls.append(lab[:, 0])
        As.append(lab[:, 1])
        Bs.append(lab[:, 2])
    L, A, B = (np.concatenate(v) for v in (Ls, As, Bs))
    Lc = L - L.mean()
    sa = float((Lc * (A - A.mean())).sum() / (Lc * Lc).sum())
    sb = float((Lc * (B - B.mean())).sum() / (Lc * Lc).sum())
    lo, hi = np.percentile(L, [2, 98])
    print("slopes %-18s L %.1f a %.1f b %.1f   da/dL %+.3f  db/dL %+.3f   L* 2%%..98%% %.1f..%.1f" % (
        fin["id"], L.mean(), A.mean(), B.mean(), sa, sb, lo, hi))
    return sa, sb


def fit(fin, st, refs, rounds=2):
    """comb / tone that give the texture, seen like its photos, the photos' contrast statistics (as wave 1)."""
    f = dict(fin)
    for _ in range(rounds):
        c, t = max(0.3, f["comb"]), max(0.3, f["tone"])
        rows, got = [], []
        for pc, pt in [(c, t), (c * 1.4, t), (c, t * 1.6)]:
            g = dict(f, comb=pc, tone=pt)
            r = measure(g, albedo(g, st), refs)
            rows.append([1.0, pc * pc, pt * pt])
            got.append([r["t" + k] ** 2 for k in STATS])
        coef = np.linalg.solve(np.array(rows), np.array(got))
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
    r = measure(f, albedo(f, st), refs)
    print("fit %-18s comb=%.2f, tone=%.2f   " % (f["id"], f["comb"], f["tone"]) +
          "  ".join("%s %.2f/%.2f" % (k, r["p" + k], r["t" + k]) for k in STATS) + "  dE %.2f" % r["de"])
    return f


def compare(family, fins, albedos, all_refs, out_path):
    """Prints the photo / texture table and draws the check sheet: per finish (a) a photo crop, (b) the texture seen
    the same way, both enlarged alike, (c) the texture at 1 px/mm - all with the leaf's up at the top."""
    report = [measure(fin, albedos[fin["id"]], all_refs[fin["id"]]) for fin in fins if all_refs.get(fin["id"])]
    head = ["finish", "photo", "L*", "a*", "b*", "texture", "L*", "a*", "b*", "dE76", "sx ph/tex", "fine ph/tex",
            "band ph/tex"]
    cells = [head] + [[r["id"], linear_to_hex(r["photo"]), *("%.1f" % v for v in r["plab"]), linear_to_hex(r["tex"]),
                       *("%.1f" % v for v in r["tlab"]), "%.2f" % r["de"]] +
                      ["%.2f / %.2f" % (r["p" + k], r["t" + k]) for k in STATS] for r in report]
    widths = [19, 8, 6, 6, 6, 8, 6, 6, 6, 6, 13, 13, 13]
    print("\n".join("".join(c.ljust(wd) if i in (0, 1, 5) else c.rjust(wd - 1) + " " for i, (c, wd) in
                             enumerate(zip(row, widths))) for row in cells))
    if out_path is None:
        return report
    to8 = lambda x: Image.fromarray(np.round(linear_to_srgb(x) * 255).astype(np.uint8))
    tiles = []
    for r in report:
        fname, box = all_refs[r["id"]][0]
        lin, scale = photo_crop(fname, box)
        z = 2 if scale > 0.3 else 4
        ch, cw = min(lin.shape[0], 640 // z), min(lin.shape[1], 240 // z)
        a = to8(lin[:ch, :cw]).resize((cw * z, ch * z), Image.NEAREST)
        sh = r["shown"][fname]
        b = to8(sh[40:40 + ch, 30:30 + cw]).resize((cw * z, ch * z), Image.NEAREST)
        c = to8(upright(albedos[r["id"]])[600:600 + 640, 300:300 + 260])
        tile = Image.new("RGB", (a.width + b.width + c.width + 24, max(a.height, c.height) + 36), "white")
        for img, x in ((a, 0), (b, a.width + 8), (c, a.width + b.width + 24)):
            tile.paste(img, (x, 36))
        d = ImageDraw.Draw(tile)
        d.text((2, 2), "%s   photo %s  texture %s   dE76 %.2f" % (
            r["id"], linear_to_hex(r["photo"]), linear_to_hex(r["tex"]), r["de"]), fill="black")
        d.text((2, 18), "(a) %s x%d  (b) texture seen the same way  (c) 1 px/mm   sx %.1f/%.1f  fine %.1f/%.1f" % (
            fname.split("__")[0], z, r["psx"], r["tsx"], r["pfine"], r["tfine"]), fill=(60, 60, 60))
        tiles.append(tile)
    cols = 2 if len(tiles) > 2 else 1
    per = math.ceil(len(tiles) / cols)
    groups = [tiles[i * per:(i + 1) * per] for i in range(cols)]
    colw = [max(t.width for t in g) for g in groups]
    top = 16 * (len(cells) + 2)
    sheet = Image.new("RGB", (max(sum(colw) + 30 * (cols - 1), 1000),
                              top + max(sum(t.height + 14 for t in g) for g in groups)), "white")
    d = ImageDraw.Draw(sheet)
    d.text((4, 4), "Door finishes (%s) vs catalogue photos: mean colour in linear light; L* contrast (sx across the "
                   "grain in 80 mm, fine = pixel to pixel, band = broad) of the texture downsized like the photo and "
                   "JPEG-compressed with its tables; leaf up = top" % family, fill="black")
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
def run(family, line, finishes, refs, source, argv=None):
    """Command line of a family module (see the module docstring)."""
    ap = argparse.ArgumentParser(description="door finishes: " + family)
    ap.add_argument("finishes", nargs="*", help="finish ids (default: all of the family)")
    ap.add_argument("--compare", action="store_true", help="write tools/doors/.cache/finishes_%s.png" % family)
    ap.add_argument("--no-write", action="store_true", help="do not write textures / json / external.json")
    ap.add_argument("--sheet", default=str(CACHE / ("finishes_%s.png" % family)))
    ap.add_argument("--fit", action="store_true", help="suggest comb / tone from the photos")
    ap.add_argument("--slopes", action="store_true", help="a*, b* against L* in the photos (dark / light hue)")
    args = ap.parse_args(argv)
    fins = [f for f in finishes if not args.finishes or f["id"] in args.finishes]
    if args.finishes and len(fins) != len(args.finishes):
        sys.exit("unknown finish: " + ", ".join(set(args.finishes) - {f["id"] for f in fins}))
    if (args.compare or args.fit or args.slopes) and not (CACHE / "photos").is_dir():
        sys.exit("no catalogue photos in %s: run tools/doors/catalog_index.py first" % (CACHE / "photos"))
    if args.slopes:
        for fin in fins:
            if refs.get(fin["id"]):
                slopes(fin, refs[fin["id"]])
        return
    structures, albedos, colors = {}, {}, {}
    for fin in fins:
        st = finish_structure(fin, structures)
        if args.fit:
            if refs.get(fin["id"]):
                fit(fin, st, refs[fin["id"]])
            continue
        alb = albedo(fin, st)
        if not args.no_write:
            write_finish(fin, st, alb)
            print("finish", fin["id"], "->", fin["material"])
            # compare what Unity gets: the written JPEG
            alb = srgb_to_linear(np.asarray(Image.open(EXT / "Materials" / fin["material"] /
                                                       (fin["material"] + "_albedo.jpg")), dtype=np.float64) / 255)
        colors[fin["id"]] = linear_to_hex(alb.reshape(-1, 3).mean(0, dtype=np.float64))
        if args.compare:
            albedos[fin["id"]] = alb.astype(np.float32)
    if args.fit:
        return
    if not args.no_write:
        write_family(family, line, finishes, colors, source)
    if args.compare:
        compare(family, [f for f in fins if f["id"] in albedos], albedos, refs, Path(args.sheet))


def write_family(family, line, finishes, colors, source):
    """entries/<family>.json (merged into external.json) and Resources/Doors/Finishes/<family>.json. Finishes not
    rebuilt in this run keep the colour of their written albedo."""
    for fin in finishes:
        if fin["id"] not in colors:
            path = EXT / "Materials" / fin["material"] / (fin["material"] + "_albedo.jpg")
            if path.exists():
                a = srgb_to_linear(np.asarray(Image.open(path), dtype=np.float64) / 255)
                colors[fin["id"]] = linear_to_hex(a.reshape(-1, 3).mean(0, dtype=np.float64))
    ENTRIES_DIR.mkdir(parents=True, exist_ok=True)
    entries = [manifest_entry(f, source, line) for f in finishes]
    epath = ENTRIES_DIR / (family + ".json")
    epath.write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    FINISHES_DIR.mkdir(parents=True, exist_ok=True)
    rows = [{"id": f["id"], "name": f["name"], "line": line, "material": f["material"],
             "color": colors.get(f["id"], f["color"])} for f in finishes]
    fpath = FINISHES_DIR / (family + ".json")
    fpath.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("entries", epath, "\nfinishes", fpath)
    import merge_entries
    merge_entries.merge([str(epath)])
