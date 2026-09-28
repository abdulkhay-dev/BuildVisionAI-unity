#!/usr/bin/env python3
"""Door finish textures, wave 2: the oak-printing ЭкоШпон films (family eco-oak) and the Softwood films (softwood).

    python3 tools/doors/textures/eco_oak.py                          # every finish of both families
    python3 tools/doors/textures/eco_oak.py --family softwood        # one family
    python3 tools/doors/textures/eco_oak.py chalet-grande --compare  # only these (+ check sheet)
    python3 tools/doors/textures/eco_oak.py --no-write --compare     # check sheets only
    python3 tools/doors/textures/eco_oak.py --fit [ids]              # suggest `grain` / `tone` from the photos

Needs numpy and Pillow (+ the catalogue photos of tools/doors/.cache for --compare / --fit). Builds on wave 1's
tools/doors/textures/make_finishes.py (colour maths, noise, line drawing, the photo statistics and the check sheet)
and writes, per finish (M = material id):

    Assets/House4696/External/Materials/M/M_albedo.jpg  sRGB 2048x1024, grain along U (image x), tile 2.0 m x 1.0 m
    Assets/House4696/External/Materials/M/M_normal.jpg  tangent space, OpenGL, 1024x512
    Assets/House4696/External/Materials/M/M_mask.png    R metallic 0, G occlusion 255, B 0, A smoothness, 256x128
per family (F = eco-oak / softwood):
    tools/doors/textures/entries/F.json                 its external.json entries (merged with merge_entries.py)
    Assets/House4696/Resources/Doors/Finishes/F.json    the finishes (id, catalogue name, line, material, mean colour)
    tools/doors/.cache/finishes_F.png                   check sheet (with --compare)

Model. The films print sawn wood, so a pattern is built the way a veneer sheet is: boards (leaves) side by side
across the tile, each cut from its own log.
  * Board: the pith runs along the board (x) at c(x) with the cut at depth d(x) under it, so the growth-ring radius
    on the surface is R = sqrt((u - c)^2 + d^2) plus a wavy perturbation of the rings. Where the cut runs close to a
    ring (near the pith line) the rings open into cathedral arches (tips where d(x) = ring radius) and flames (the
    ring waviness); away from it they are straight rift lines. A board whose pith lies outside it is all rift.
    Every x-dependence is periodic over the 2 m tile and the boards partition the 1 m across it (wrapping), so the
    maps tile both ways.
  * Rings (per log): widths drawn around a median with a slow growth trend; each ring = earlywood (the pore band of
    the ring-porous oak / ash, the light spring wood of pine) + latewood (darker towards the ring's end; pine:
    a narrow dark band). Profiles are box-filtered over each pixel's footprint in R (exact coverage, no aliasing).
  * Pores: the earlywood band times short dashes along the fibre (x: vessels run along the stem, also where the
    rings turn into arches); ray flecks: short thin streaks along x; knots: the rings bend around a bump of R,
    a dark core with its own rings, a bark rim and radial checks; checks: along a ring line (R level set);
    broad tone: follows the rings (zones of growth) + board-to-board shade + long bands.
  * Concrete (Graphite Art): no boards - multi-scale clouds, lighter mottles, pits and fine sand.
A finish colours its pattern (linear RGB, relative to its catalogue mean): the ground tone in L* units (`grain` x
fine + `tone` x broad) runs towards the `dark` / `light` colours (their hue = the photos' a*, b* against L* slopes),
pores / rays / knots / checks are laid over in their own colours (limed films: light pores), and the base colour
is solved per channel so the texture's mean in linear light is exactly `color` (the mean of the photos' REFS crops).
The normal map embosses pores, checks, rays and knot rims; the mask carries the lacquer's smoothness (lower in pores).
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_finishes as mf                    # noqa: E402  (wave 1: colour, noise, lines, photo statistics, sheet)
import merge_entries                           # noqa: E402
from make_finishes import (ALBEDO, NORMAL, MASK, MM, TILE_M, EXT, CACHE, ROOT,   # noqa: E402
                           srgb_to_linear, linear_to_srgb, linear_to_lab, hex_to_linear, linear_to_hex,
                           gauss_noise, noise_1d, warp_rows, draw_lines, box_down)

SOURCE = "procedural:tools/doors/textures/eco_oak.py"
FINISH_DIR = ROOT / "Assets" / "House4696" / "Resources" / "Doors" / "Finishes"
ENTRY_DIR = HERE / "entries"

W_PX, H_PX = ALBEDO
PX = 1.0 / MM                                  # albedo pixels per mm
TILE_MM = (TILE_M[0] * 1000.0, TILE_M[1] * 1000.0)


# ------------------------------------------------------------------------------------------------ helpers
def lognormal(rng, med_sig, size=None):
    med, sig = med_sig
    return med * np.exp(sig * rng.standard_normal(size))


def periodic_1d(rng, n, corr):
    """Smooth periodic 1D noise of n samples, correlation `corr` samples, unit std."""
    return noise_1d(rng, n, max(1.0, corr))


def lut(table, pos):
    """Linear lookup of a uniformly sampled table at fractional positions (clamped)."""
    pos = np.clip(pos, 0.0, len(table) - 1.000001)
    i = pos.astype(np.int64)
    t = pos - i
    return table[i] * (1 - t) + table[i + 1] * t


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def periodic_dx(x, x0, period):
    return (x - x0 + period / 2) % period - period / 2


# ------------------------------------------------------------------------------------------------ growth rings
RING_STEP = 0.02                               # mm, sampling of the ring profiles (cumulative tables)


def ring_log(rng, r_max, spec):
    """Rings of one log from the pith outwards: cumulative (box-filter) tables of the earlywood indicator and the
    latewood density over R, sampled every RING_STEP mm."""
    med, sig = spec["ring"]
    n = int(r_max / med * 2.5) + 64
    trend = periodic_1d(rng, max(256, 2 * n), spec.get("trend", 6.0))[:n]
    q = spec.get("trend_share", 0.5)
    widths = med * np.exp(sig * (math.sqrt(1 - q) * rng.standard_normal(n) + math.sqrt(q) * trend))
    widths = np.clip(widths, 0.35 * med, 4.0 * med)
    edges = np.concatenate([[0.0], np.cumsum(widths)])
    ew = np.clip(lognormal(rng, spec["early"], n), 0.12, 0.6 * widths)
    r = (np.arange(int(edges[-1] / RING_STEP)) + 0.5) * RING_STEP
    k = np.clip(np.searchsorted(edges, r, side="right") - 1, 0, n - 1)
    s = r - edges[k]
    # rings differ: a prominent pore band here, a dark latewood there (strengths correlated over a few rings)
    vs = spec.get("vary", 0.35)
    es = np.clip(np.exp(vs * (0.6 * rng.standard_normal(n) + 0.8 * periodic_1d(rng, max(256, 2 * n), 2.5)[:n])),
                 0.25, 2.5)
    ls = np.clip(np.exp(vs * (0.6 * rng.standard_normal(n) + 0.8 * periodic_1d(rng, max(256, 2 * n), 2.5)[:n])),
                 0.25, 2.5)
    early = (s < ew[k]) * es[k]
    late = np.clip((s - ew[k]) / np.maximum(widths[k] - ew[k], 1e-6), 0.0, 1.0) ** spec.get("late_gamma", 1.6)
    late[s < ew[k]] = 0.0
    if spec.get("late_band"):                  # pine: a narrow dark latewood band at the ring's end, soft inner edge
        band = spec["late_band"]
        lw = np.minimum(band * widths[k], 0.7 * widths[k])
        late = smoothstep(widths[k] - lw * 1.6, widths[k] - lw * 0.4, s)
    late = late * ls[k]
    cum = lambda f: np.concatenate([[0.0], np.cumsum(f) * RING_STEP])
    return dict(early=cum(early), late=cum(late), rmax=r[-1])


def box_profile(cum, R, hR):
    """Mean of a ring profile over [R - hR, R + hR] (hR = the pixel's footprint in R) from its cumulative table."""
    a = lut(cum, (R + hR) / RING_STEP)
    b = lut(cum, (R - hR) / RING_STEP)
    return (a - b) / (2 * hR)


# ------------------------------------------------------------------------------------------------ wood structure
def knot_list(rng, p, bw):
    """Knots of one board: (x mm, u mm across from the board centre, diameter mm, kind)."""
    area = bw * TILE_MM[0] / 1e6
    out = []
    for kind, key in (("knot", "knots"), ("pin", "pins")):
        spec = p.get(key)
        if not spec:
            continue
        for _ in range(rng.poisson(spec["per_m2"] * area)):
            a = float(np.clip(lognormal(rng, spec["size"]), 1.5, spec.get("max", 40.0)))
            room = bw / 2 - 0.9 * a - 4.0
            if room <= 0:
                continue
            out.append((rng.uniform(0, TILE_MM[0]), rng.uniform(-room, room) * 0.85, a, kind))
    return out


def board_log(rng, p, bw):
    """Pith line c(x), cut depth d(x) (mm, over the tile's columns) of one board of width bw."""
    x_len = W_PX
    flat = rng.random() < p["flat_share"]
    if flat:
        c0 = rng.uniform(-p["pith_in"], p["pith_in"]) * bw
    else:                                      # rift / quarter: the pith outside the board
        c0 = (0.5 + rng.gamma(2.0, p.get("rift_out", 0.6))) * bw * rng.choice([-1.0, 1.0])
    c = c0 + p["pith_wander"] * bw * periodic_1d(rng, x_len, p["pith_len"] * PX)
    # cut depth: a zigzag along the board (long ramps - the cathedral tips come one after another - and turns with
    # small radii, so the rings close in pointed flames instead of round ovals), periodic over the tile
    dm = lognormal(rng, p["depth"])
    n_turn = 2 * int(rng.integers(p.get("turns", (1, 3))[0], p.get("turns", (1, 3))[1] + 1))
    seg = rng.dirichlet(np.full(n_turn, 3.0)) * (TILE_MM[0] - n_turn * 200.0) + 200.0     # ramps >= 200 mm
    xs = (np.cumsum(seg) + rng.uniform(0, TILE_MM[0])) % TILE_MM[0]
    xs.sort()
    hi = dm * (1 + p["depth_amp"] * rng.uniform(0.5, 1.0, n_turn))
    lo = dm * (1 - p["depth_amp"] * rng.uniform(0.5, 1.0, n_turn))
    vals = np.where(np.arange(n_turn) % 2 == 0, hi, lo)
    x_mm = (np.arange(x_len) + 0.5) * MM
    d = np.interp(x_mm, np.concatenate([xs - TILE_MM[0], xs, xs + TILE_MM[0]]), np.tile(vals, 3))
    d = _blur_periodic(d, p.get("turn_round", 25.0) * PX)
    d += p.get("depth_noise", 0.08) * dm * periodic_1d(rng, x_len, 120.0 * PX)
    slope = np.abs(np.gradient(d)) * PX                                         # mm of depth per mm along
    d = dm + (d - dm) * min(1.0, p.get("max_slope", 0.15) / max(1e-9, slope.max()))
    dmin = p.get("dmin", 4.0)
    d = dmin + np.logaddexp(0.0, (d - dmin) / 2.0) * 2.0                       # soft floor
    ecc = p.get("ecc", 0.15) * rng.uniform(-1, 1)
    return c, d, flat, ecc


def _blur_rows(a, sig):
    """Gaussian blur across the grain (along rows), periodic."""
    k = np.fft.rfftfreq(a.shape[0])[:, None]
    return np.fft.irfft(np.fft.rfft(a, axis=0) * np.exp(-2 * np.pi ** 2 * (k * sig) ** 2), n=a.shape[0], axis=0)


def _blur_periodic(a, sig):
    k = np.fft.rfftfreq(len(a))
    return np.fft.irfft(np.fft.rfft(a) * np.exp(-2 * np.pi ** 2 * (k * sig) ** 2), n=len(a))


def wood_structure(pid, seed=None):
    """The pattern's fields at albedo resolution (rows = across the grain, columns = along):
    early / late (ring profiles, ~0..1), zone (tone following the rings), board (per-board shade), pores / rays /
    knot / rim / check opacities, knot rings, broad and fibre tone (unit std)."""
    p = PATTERNS[pid]
    rng = np.random.default_rng(p["seed"] if seed is None else seed)
    w, h = W_PX, H_PX
    f = {k: np.zeros((h, w)) for k in ("early", "late", "zone", "board", "check", "halo")}
    x_mm = (np.arange(w) + 0.5) * MM
    # boards across the tile (wrapping around y)
    widths = []
    while sum(widths) < TILE_MM[1]:
        widths.append(float(np.clip(lognormal(rng, p["board"][:2]), *p["board"][2:])))
    widths = np.array(widths) * TILE_MM[1] / sum(widths)
    off = rng.uniform(0, TILE_MM[1])
    edges = (np.concatenate([[0.0], np.cumsum(widths)]) + off) * PX
    knots = []
    for i in range(len(widths)):
        y0, y1 = edges[i], edges[i + 1]
        rows = np.arange(int(math.floor(y0)), int(math.ceil(y1)))
        bw = widths[i]
        u = (rows + 0.5 - (y0 + y1) / 2) * MM
        c, d, flat, ecc = board_log(rng, p, bw)
        du = u[:, None] - c[None, :]
        R = np.sqrt(du * du + d[None, :] ** 2)
        R *= 1 + ecc * du / R                  # eccentric growth: rings wider on one side of the pith
        for amp, along, across in p["wave"]:
            R += amp * gauss_noise(rng, (len(rows), w), along * PX, across * PX)
        # knots: the rings bend around them (a bump of R, elongated along the grain)
        for xk, uk, a, kind in knot_list(rng, p, bw):
            if kind == "knot":
                dx = periodic_dx(x_mm[None, :], xk, TILE_MM[0]) / p["knots"].get("flow", 2.2)
                du = u[:, None] - uk
                sr = 0.75 * a
                R += p["knots"].get("bump", 2.5) * a * np.exp(-(dx * dx + du * du) / (2 * sr * sr))
            knots.append((xk * PX, (uk * PX + (y0 + y1) / 2) % h, a, kind))
        Rx = (np.roll(R, -1, 1) - np.roll(R, 1, 1)) / 2
        Ry = np.gradient(R, axis=0)
        hR = 0.5 * (np.abs(Rx) + np.abs(Ry)) + 0.03
        log = ring_log(rng, float(R.max()) + 10.0, p["rings"])
        early = box_profile(log["early"], R, hR)
        late = box_profile(log["late"], R, hR)
        zone_tab = periodic_1d(rng, int(log["rmax"] / 0.5) + 2, p["zone_len"] / 0.5)
        zone = lut(zone_tab, R / 0.5)
        shade = rng.standard_normal()
        check = np.zeros_like(R)
        cs = p.get("checks")
        if cs:
            gR = np.hypot(Rx, Ry) + 1e-6
            for _ in range(rng.poisson(cs["per_m2"] * bw * TILE_MM[0] / 1e6)):
                ln = float(np.clip(lognormal(rng, cs["length"]), 20.0, 0.9 * TILE_MM[0]))
                xs = rng.uniform(0, TILE_MM[0])
                j = int(np.clip(rng.normal(0.0, 0.25) * len(rows) + len(rows) / 2, 2, len(rows) - 3))
                r0 = R[j, int(xs * PX) % w]
                s = periodic_dx(x_mm, xs + ln / 2, TILE_MM[0]) / ln + 0.5          # 0..1 along the check
                on = (s > 0) & (s < 1)
                env = np.where(on, np.sin(np.pi * np.clip(s, 0, 1)) ** 0.7, 0.0)
                hw = lognormal(rng, cs["width"]) * PX / 2 * env * np.exp(0.35 * periodic_1d(rng, w, 12 * PX))
                wig = cs.get("wiggle", 0.8) * periodic_1d(rng, w, 18 * PX)
                dist = np.abs(R - r0 - wig[None, :]) / gR                           # px from the ring line
                side = np.sign(u[j] - c[int(xs * PX) % w])                         # one flank of an arch only
                keep = on[None, :] * (np.sign(u[:, None] - c[None, :]) == side) * smoothstep(0.2, 0.45, gR)
                check = np.maximum(check, np.clip(hw[None, :] + 0.5 - dist, 0.0, 1.0) * keep)
        # composite the board's rows (anti-aliased seam: coverage of each row by [y0, y1))
        cov = np.clip(np.minimum(rows + 1, y1) - np.maximum(rows, y0), 0.0, 1.0)[:, None]
        rr = rows % h                          # distinct within a board: plain fancy-index accumulation is safe
        for key, val in (("early", early), ("late", late), ("zone", zone), ("check", check)):
            f[key][rr] += cov * val
        f["board"][rr] += cov * shade
    # pores: the earlywood band (softened into the latewood) x a stipple of short dashes along the fibre
    ps = p["pores"]
    band = np.clip(f["early"], 0, None)
    band = 0.75 * band + 0.25 * _blur_rows(band, 0.8)
    dash = gauss_noise(rng, (h, w), ps["len"] * PX, ps["wid"] * PX)
    dash = smoothstep(ps["thr"] - 0.5, ps["thr"] + 0.5, dash)
    f["pores"] = np.clip(band * dash * ps["fill"] + np.clip(1 - band, 0, 1) * ps.get("late", 0.0) * dash, 0, 1)
    # ray flecks: short thin streaks along x; dark / light streaks of the print (fibre bundles, figure)
    disp = gauss_noise(rng, (h, w), 150 * PX, 25 * PX) * (0.8 * PX)
    env_table = noise_1d(rng, 1 << 16, 8.0 * PX)
    for key in ("rays", "sdark", "slight"):
        acc = np.zeros((h, w))
        if p.get(key):
            draw_lines(rng, acc, p[key], disp, env_table, PX)
        f[key] = 1 - np.exp(-acc)
    # knots: dark core with its own rings, bark rim, radial checks; a darker halo
    f["knot"], f["rim"], f["kring"] = np.zeros((h, w)), np.zeros((h, w)), np.zeros((h, w))
    for xk, yk, a, kind in knots:
        _draw_knot(rng, f, p, xk, yk, a, kind)
    # broad tone: long bands + clouds; fibre: fine streaks along x
    bands = gauss_noise(rng, (h, w), p["bands"][1] * PX, p["bands"][0] * PX)
    clouds = gauss_noise(rng, (h, w), p["clouds"][1] * PX, p["clouds"][0] * PX)
    f["fibre"] = gauss_noise(rng, (h, w), p["fibre"][1] * PX, p["fibre"][0] * PX)
    z = f["zone"] / max(1e-9, f["zone"].std())
    b = f["board"]
    wz, wb, wc = p["broad_mix"]
    broad = wz * z + wb * b + wc * clouds + math.sqrt(max(0.0, 1 - wz * wz - wb * wb - wc * wc)) * bands
    f["broad"] = broad / broad.std()
    # the latewood is fibrous, not a smooth gradient: modulate it with streaks along the fibre
    fl = p.get("late_fibre")
    if fl:
        f["late"] = f["late"] * np.clip(1 + fl[0] * gauss_noise(rng, (h, w), fl[2] * PX, fl[1] * PX), 0, None)
    f["relief"] = p["relief"]
    return f


def _draw_knot(rng, f, p, xk, yk, a, kind):
    """Adds a knot (centre xk, yk in px, diameter a mm) to the knot fields."""
    h, w = H_PX, W_PX
    ks = p["knots"] if kind == "knot" else p["pins"]
    asp = ks.get("aspect", 1.4) * math.exp(0.15 * rng.standard_normal())
    r_px = a * PX / 2
    ext = int(r_px * asp * 4 + 6)
    cols = (np.arange(int(xk) - ext, int(xk) + ext + 1)) % w
    rows = (np.arange(int(yk) - int(r_px * 4 + 6), int(yk) + int(r_px * 4 + 6) + 1)) % h
    X = periodic_dx(cols[None, :] + 0.5, xk, w) / asp
    Y = periodic_dx(rows[:, None] + 0.5, yk, h)
    rho = np.hypot(X, Y)
    th = np.arctan2(Y, X)
    ph = rng.uniform(0, 2 * np.pi, 3)
    edge = r_px * (1 + 0.10 * np.cos(2 * th + ph[0]) + 0.07 * np.cos(3 * th + ph[1]) + 0.05 * np.cos(5 * th + ph[2]))
    core = np.clip(edge - rho + 0.5, 0.0, 1.0)
    rim_w = max(0.7, ks.get("rim", 0.12) * r_px)
    rim = np.clip(1 - np.abs(rho - edge) / rim_w, 0.0, 1.0)
    kring = core * (0.5 + 0.5 * np.cos(2 * np.pi * rho / max(0.9, 0.12 * r_px * 2)))
    # radial checks of bigger knots
    if kind == "knot" and a > 9 and rng.random() < ks.get("cracked", 0.5):
        for _ in range(rng.integers(1, 4)):
            ang = rng.uniform(0, 2 * np.pi)
            dth = np.angle(np.exp(1j * (th - ang)))
            ln = rng.uniform(0.5, 1.1) * r_px
            wd = 0.5 + 0.8 * np.clip(1 - rho / ln, 0, 1)
            rim = np.maximum(rim, np.clip(wd - np.abs(dth) * rho, 0, 1) * (rho < ln))
    halo = np.exp(-(rho / (r_px * 2.2)) ** 2)
    ix = np.ix_(rows, cols)
    f["knot"][ix] = np.maximum(f["knot"][ix], core)
    f["rim"][ix] = np.maximum(f["rim"][ix], rim * ks.get("rim_alpha", 0.8))
    f["kring"][ix] = np.maximum(f["kring"][ix], kring)
    f["halo"][ix] = np.maximum(f["halo"][ix], halo * ks.get("halo", 0.6))


# ------------------------------------------------------------------------------------------------ patterns
# Lengths in mm. board = leaf width (median, log-sigma, min, max); flat_share = share of flat-sawn leaves (the pith
# line inside, within +-pith_in of the width; else it lies outside: rift); depth = cut depth under the pith line
# (median, log-sigma), depth_amp x depth = its swing along the tile: a zigzag of `turns` ramp pairs, corners rounded
# by turn_round, slope <= max_slope (0.15) - the cathedral tips; ecc = eccentric growth; wave = ring waviness octaves (amplitude, correlation along, across) - the flames; rings = ring width (median,
# log-sigma), earlywood width, latewood gamma (pine: late_band = dark band share); zone_len = correlation of the tone
# that follows the rings (in R); pores = dash length / width along the fibre, threshold, fill of the earlywood band,
# latewood share; rays = draw_lines spec; knots / pins = per m2, diameter, ring bump (x diameter) and its flow
# length along the grain, core aspect, rim; checks = per m2, length, width, wiggle across the rings; bands / clouds /
# fibre = (sigma across, sigma along); broad_mix = weights of zone, board shade, clouds in the broad tone (rest:
# bands); relief = what the embossing follows and the rms tilt.
PATTERNS = {
    "legno": dict(
        seed=5101,
        board=(170.0, 0.3, 100.0, 300.0), flat_share=0.65, pith_in=0.22, rift_out=0.6, pith_wander=0.12,
        pith_len=400.0, depth=(40.0, 0.4), depth_amp=0.6, turns=(1, 3), turn_round=25.0, dmin=4.0, ecc=0.15,
        wave=[(4.0, 260.0, 30.0), (1.5, 90.0, 12.0), (0.5, 35.0, 5.0)],
        rings=dict(ring=(2.8, 0.35), early=(0.7, 0.25), late_gamma=1.6, trend=6.0),
        late_fibre=(0.6, 0.5, 4.0),
        zone_len=6.0,
        pores=dict(len=0.8, wid=0.35, thr=0.0, fill=0.9, late=0.08),
        rays=dict(per_cm=1.2, width=(0.35, 0.3), length=(9.0, 0.6), alpha=(0.2, 0.6), fade=0.6, slope=0.0),
        knots=dict(per_m2=1.5, size=(12.0, 0.4), max=30.0, bump=2.5, flow=2.2, aspect=1.3, rim=0.12,
                   rim_alpha=0.8, halo=0.5, cracked=0.5),
        pins=dict(per_m2=4.0, size=(3.0, 0.3), max=6.0, aspect=1.2, rim=0.3, rim_alpha=0.5, halo=0.3),
        checks=dict(per_m2=2.0, length=(90.0, 0.7), width=(0.8, 0.4), wiggle=0.8),
        sdark=dict(per_cm=0.5, width=(0.5, 0.4), length=(120.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.4, width=(0.7, 0.4), length=(80.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        bands=(25.0, 700.0), clouds=(150.0, 500.0), fibre=(0.35, 5.0), broad_mix=(0.55, 0.45, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.25, late=0.2, tilt_deg=3.0),
    ),
    # CLASSICO class A (Royal Oak, Antique Oak): a clean crown-cut oak veneer - cathedrals, no knots or checks
    "classic": dict(
        seed=6201,
        board=(190.0, 0.25, 120.0, 300.0), flat_share=0.75, pith_in=0.2, rift_out=0.6, pith_wander=0.12,
        pith_len=400.0, depth=(45.0, 0.35), depth_amp=0.6, turns=(1, 3), turn_round=25.0, dmin=4.0, ecc=0.15,
        wave=[(4.0, 260.0, 30.0), (1.5, 90.0, 12.0), (0.5, 35.0, 5.0)],
        rings=dict(ring=(2.6, 0.3), early=(0.7, 0.25), late_gamma=1.6, trend=6.0),
        late_fibre=(0.6, 0.5, 4.0),
        zone_len=6.0,
        pores=dict(len=0.8, wid=0.35, thr=0.0, fill=0.9, late=0.06),
        rays=dict(per_cm=1.2, width=(0.3, 0.3), length=(8.0, 0.6), alpha=(0.2, 0.6), fade=0.6, slope=0.0),
        sdark=dict(per_cm=0.3, width=(0.5, 0.4), length=(120.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.3, width=(0.7, 0.4), length=(80.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        bands=(25.0, 700.0), clouds=(150.0, 500.0), fibre=(0.35, 5.0), broad_mix=(0.6, 0.35, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.25, late=0.2, tilt_deg=2.5),
    ),
    # Silver Ash: ash - wide rings, broad pore bands, bold cathedrals, no visible rays
    "ash": dict(
        seed=6301,
        board=(200.0, 0.25, 130.0, 320.0), flat_share=0.8, pith_in=0.2, rift_out=0.6, pith_wander=0.12,
        pith_len=400.0, depth=(50.0, 0.35), depth_amp=0.65, turns=(1, 3), turn_round=25.0, dmin=4.0, ecc=0.15,
        wave=[(5.0, 260.0, 30.0), (1.8, 90.0, 12.0), (0.5, 35.0, 5.0)],
        rings=dict(ring=(4.0, 0.3), early=(1.2, 0.25), late_gamma=1.4, trend=6.0),
        late_fibre=(0.6, 0.5, 4.0),
        zone_len=8.0,
        pores=dict(len=0.9, wid=0.4, thr=-0.2, fill=0.95, late=0.05),
        sdark=dict(per_cm=0.3, width=(0.5, 0.4), length=(120.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        bands=(25.0, 700.0), clouds=(150.0, 500.0), fibre=(0.35, 5.0), broad_mix=(0.6, 0.35, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.25, late=0.2, tilt_deg=2.5),
    ),
    # Virgin / Ivory: painted open-pore oak - the paint hides the tone, the pores show as fine dashes; stipple
    "painted": dict(
        seed=6401,
        board=(170.0, 0.3, 100.0, 300.0), flat_share=0.45, pith_in=0.22, rift_out=0.6, pith_wander=0.1,
        pith_len=400.0, depth=(40.0, 0.4), depth_amp=0.6, turns=(1, 3), turn_round=25.0, dmin=4.0, ecc=0.15,
        wave=[(4.0, 260.0, 30.0), (1.5, 90.0, 12.0), (0.5, 35.0, 5.0)],
        rings=dict(ring=(2.4, 0.3), early=(0.6, 0.25), late_gamma=1.6, trend=6.0),
        late_fibre=(0.6, 0.5, 4.0),
        zone_len=6.0,
        pores=dict(len=1.0, wid=0.35, thr=0.2, fill=0.9, late=0.15),
        rays=dict(per_cm=1.0, width=(0.3, 0.3), length=(6.0, 0.6), alpha=(0.2, 0.6), fade=0.6, slope=0.0),
        bands=(25.0, 700.0), clouds=(150.0, 500.0), fibre=(0.5, 1.2), broad_mix=(0.5, 0.3, 0.4),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.5, late=0.1, tilt_deg=2.5),
    ),
    # Original Oak: rustic oak - knots, long dark checks, strong zones
    "rustic": dict(
        seed=6501,
        board=(160.0, 0.3, 90.0, 280.0), flat_share=0.55, pith_in=0.22, rift_out=0.6, pith_wander=0.12,
        pith_len=400.0, depth=(40.0, 0.4), depth_amp=0.6, turns=(1, 3), turn_round=25.0, dmin=4.0, ecc=0.15,
        wave=[(4.0, 260.0, 30.0), (1.5, 90.0, 12.0), (0.6, 35.0, 5.0)],
        rings=dict(ring=(3.0, 0.35), early=(0.8, 0.25), late_gamma=1.5, trend=6.0, vary=0.45),
        late_fibre=(0.6, 0.5, 4.0),
        zone_len=5.0,
        pores=dict(len=0.8, wid=0.35, thr=0.0, fill=0.9, late=0.08),
        rays=dict(per_cm=1.5, width=(0.35, 0.3), length=(10.0, 0.6), alpha=(0.2, 0.7), fade=0.6, slope=0.0),
        knots=dict(per_m2=2.5, size=(13.0, 0.45), max=35.0, bump=2.5, flow=2.2, aspect=1.3, rim=0.12,
                   rim_alpha=0.85, halo=0.6, cracked=0.6),
        pins=dict(per_m2=6.0, size=(3.0, 0.3), max=6.0, aspect=1.2, rim=0.3, rim_alpha=0.5, halo=0.3),
        checks=dict(per_m2=16.0, length=(250.0, 0.6), width=(1.8, 0.5), wiggle=1.5),
        sdark=dict(per_cm=1.2, width=(0.6, 0.5), length=(180.0, 0.8), alpha=(0.3, 1.0), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.6, width=(0.8, 0.45), length=(100.0, 0.8), alpha=(0.2, 0.9), fade=0.8, slope=0.002),
        bands=(25.0, 700.0), clouds=(150.0, 500.0), fibre=(0.35, 5.0), broad_mix=(0.6, 0.4, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.3, late=0.25, tilt_deg=3.5),
    ),
    # Chalet: rustic limed oak - flames everywhere, lime in the pores, knots, checks
    "chalet": dict(
        seed=6601,
        board=(180.0, 0.3, 100.0, 300.0), flat_share=0.6, pith_in=0.22, rift_out=0.6, pith_wander=0.12,
        pith_len=400.0, depth=(45.0, 0.4), depth_amp=0.65, turns=(1, 3), turn_round=25.0, dmin=4.0, ecc=0.15,
        wave=[(5.0, 240.0, 28.0), (1.8, 80.0, 11.0), (0.6, 30.0, 5.0)],
        rings=dict(ring=(3.8, 0.35), early=(1.1, 0.3), late_gamma=1.5, trend=6.0, vary=0.5),
        late_fibre=(0.6, 0.5, 4.0),
        zone_len=5.0,
        pores=dict(len=1.0, wid=0.4, thr=-0.4, fill=1.0, late=0.08),
        rays=dict(per_cm=1.2, width=(0.35, 0.3), length=(9.0, 0.6), alpha=(0.2, 0.6), fade=0.6, slope=0.0),
        knots=dict(per_m2=1.2, size=(8.0, 0.4), max=18.0, bump=2.5, flow=2.2, aspect=1.3, rim=0.12,
                   rim_alpha=0.85, halo=0.6, cracked=0.6),
        pins=dict(per_m2=4.0, size=(2.5, 0.3), max=5.0, aspect=1.2, rim=0.3, rim_alpha=0.5, halo=0.3),
        checks=dict(per_m2=5.0, length=(120.0, 0.7), width=(1.0, 0.45), wiggle=1.0),
        sdark=dict(per_cm=0.5, width=(0.6, 0.45), length=(150.0, 0.8), alpha=(0.2, 0.9), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.5, width=(0.7, 0.45), length=(80.0, 0.8), alpha=(0.2, 0.9), fade=0.8, slope=0.002),
        bands=(25.0, 700.0), clouds=(150.0, 500.0), fibre=(0.35, 5.0), broad_mix=(0.6, 0.4, 0.35),
        relief=dict(pores=1.2, checks=2.5, rays=0.3, rim=0.8, fibre=0.3, late=0.25, tilt_deg=4.0),
    ),
    # Softwood films: pine - wide rings with a narrow dark latewood band, no pores, few knots
    "pine": dict(
        seed=7301,
        board=(160.0, 0.3, 100.0, 280.0), flat_share=0.6, pith_in=0.22, rift_out=0.6, pith_wander=0.12,
        pith_len=400.0, depth=(40.0, 0.4), depth_amp=0.6, turns=(1, 3), turn_round=30.0, dmin=4.0, ecc=0.15,
        wave=[(4.0, 260.0, 30.0), (1.2, 90.0, 12.0), (0.3, 35.0, 5.0)],
        rings=dict(ring=(4.0, 0.4), early=(1.0, 0.2), late_band=0.25, trend=6.0),
        late_fibre=(0.6, 0.5, 4.0),
        zone_len=8.0,
        pores=dict(len=1.0, wid=0.4, thr=0.3, fill=0.0, late=0.0),
        knots=dict(per_m2=0.4, size=(16.0, 0.35), max=30.0, bump=2.0, flow=2.0, aspect=1.2, rim=0.1,
                   rim_alpha=0.6, halo=0.5, cracked=0.0),
        sdark=dict(per_cm=0.3, width=(0.6, 0.4), length=(150.0, 0.8), alpha=(0.2, 0.7), fade=0.8, slope=0.002),
        bands=(25.0, 700.0), clouds=(150.0, 500.0), fibre=(0.35, 5.0), broad_mix=(0.6, 0.35, 0.35),
        relief=dict(pores=0.0, checks=2.5, rays=0.0, rim=0.5, fibre=0.4, late=0.6, tilt_deg=2.0),
    ),
    # Graphite Art: concrete - clouds = broad octaves (amplitude, sigma mm), grit = the fine ones (+ sand),
    # mottle (sigma, threshold, softness), pits (per m2, radius median mm, log-sigma)
    "concrete": dict(
        seed=6701, clouds=[(1.0, 260.0), (0.6, 90.0), (0.4, 35.0)], grit=[(1.0, 12.0), (0.7, 5.0), (0.4, 2.0)],
        mottle=(55.0, 0.7, 0.9),
        pits=(4000.0, 0.45, 0.5),
        relief=dict(pits=1.0, mottle=0.15, fibre=0.35, tilt_deg=2.5),
    ),
}


# ------------------------------------------------------------------------------------------------ concrete
def concrete_structure(pid, seed=None):
    """Graphite Art: cast-concrete print - multi-scale clouds, lighter trowelled mottles, pits and fine sand."""
    p = PATTERNS[pid]
    rng = np.random.default_rng(p["seed"] if seed is None else seed)
    h, w = H_PX, W_PX
    clouds = sum(a * gauss_noise(rng, (h, w), s * PX, s * PX) for a, s in p["clouds"])
    grit = sum(a * gauss_noise(rng, (h, w), s * PX, s * PX) for a, s in p["grit"])
    warp = gauss_noise(rng, (h, w), 200 * PX, 200 * PX) * (25 * PX)
    m = warp_rows(gauss_noise(rng, (h, w), p["mottle"][0] * PX, p["mottle"][0] * PX), warp)
    mottle = smoothstep(p["mottle"][1], p["mottle"][1] + p["mottle"][2], m)
    mottle *= smoothstep(-1.0, 1.5, gauss_noise(rng, (h, w), 15 * PX, 15 * PX))     # broken, streaky edges
    grit = grit / grit.std() + 0.5 * gauss_noise(rng, (h, w), 0.6, 0.6)          # + fine sand
    pits = np.zeros((h, w))
    area = TILE_MM[0] * TILE_MM[1] / 1e6
    for _ in range(rng.poisson(p["pits"][0] * area)):
        r = float(np.clip(lognormal(rng, p["pits"][1:]), 0.25, 3.0)) * PX
        xc, yc = rng.uniform(0, w), rng.uniform(0, h)
        e = int(r + 3)
        cols = np.arange(int(xc) - e, int(xc) + e + 1) % w
        rows = np.arange(int(yc) - e, int(yc) + e + 1) % h
        d = np.hypot(periodic_dx(cols[None, :] + 0.5, xc, w), periodic_dx(rows[:, None] + 0.5, yc, h))
        ix = np.ix_(rows, cols)
        pits[ix] = np.maximum(pits[ix], np.clip(r - d + 0.5, 0.0, 1.0))
    broad = clouds / clouds.std()
    return dict(broad=broad, fibre=grit / grit.std(), mottle=mottle, pits=pits, relief=p["relief"], kind="concrete")


# ------------------------------------------------------------------------------------------------ finishes
def shade(color, dL, slope):
    """The mean colour moved by dL in L* along the photos' a*, b* slopes (hex)."""
    lab = linear_to_lab(hex_to_linear(color))
    return lab_to_hex(np.array([lab[0] + dL, lab[1] + slope[0] * dL, lab[2] + slope[1] * dL]))


def lab_to_hex(lab):
    fy = (lab[0] + 16) / 116
    fx, fz = fy + lab[1] / 500, fy - lab[2] / 200
    d = 6 / 29
    inv = lambda t: t ** 3 if t > d else 3 * d * d * (t - 4 / 29)
    xyz = np.array([inv(fx), inv(fy), inv(fz)]) * mf._WHITE
    return linear_to_hex(np.linalg.solve(mf._M, xyz))


# family / id / catalogue name / material; pattern (+ seed = another print of the same kind); color = catalogue mean
# (sRGB hex, linear mean of the REFS crops); dark / light = the ground's full-strength dark / light colours (hue =
# photos' slopes of a*, b* against L*); grain = L* std of the ring (latewood) tone, tone = L* std of the broad tone,
# fibre = L* std of the fibre noise; pore / ray = opacity of the pores / ray flecks and their colours; knot / rim /
# check = colours of knot cores, knot rims and checks; halo = L* darkening around knots; smooth = lacquer smoothness.
def _F(family, fid, name, pattern, color, slope, dark_dL=25.0, light_dL=15.0, **kw):
    d = dict(family=family, id=fid, name=name, line="ЭкоШпон", material="door_" + fid.replace("-", "_"),
             pattern=pattern, color=color, dark=shade(color, -dark_dL, slope), light=shade(color, light_dL, slope))
    d.update(kw)
    return d


FINISHES = [
    _F("eco-oak", "royal-oak", "Royal Oak", "classic", "#eeeeee", (0.0, 0.0), dark_dL=18, light_dL=4,
       grain=1.42, tone=0.40, fibre=0.3, streak=0.3, pore=0.35, pore_col="#c9c9c9", ray=0.2, ray_col="#d8d8d8", smooth=0.40),
    _F("eco-oak", "antique-oak", "Antique Oak", "classic", "#361a12", (0.3, 0.6), dark_dL=8, light_dL=8, seed=6203,
       grain=1.94, tone=1.14, fibre=0.4, streak=0.3, pore=0.5, pore_col="#22100a", ray=0.3, ray_col="#2a130c", smooth=0.42),
    _F("eco-oak", "silver-ash", "Silver Ash", "ash", "#f3f3f3", (0.0, 0.0), dark_dL=25, light_dL=3,
       grain=2.09, tone=0.40, fibre=0.4, streak=0.3, pore=0.6, pore_col="#a9a9a9", smooth=0.40),
    _F("eco-oak", "ivory", "Ivory", "painted", "#eddecc", (0.0, 0.1), dark_dL=10, light_dL=4,
       grain=1.27, tone=0.10, fibre=0.25, pore=0.3, pore_col="#d2c1ad", ray=0.1, ray_col="#dccbb8", smooth=0.40),
    _F("eco-oak", "virgin", "Virgin", "painted", "#e3e3e3", (0.0, 0.0), dark_dL=10, light_dL=4,
       grain=1.26, tone=0.10, fibre=0.25, pore=0.35, pore_col="#c4c4c4", ray=0.1, ray_col="#d0d0d0", smooth=0.40),
    _F("eco-oak", "dark-oak", "Dark Oak", "legno", "#3f2e22", (-0.1, 0.2), dark_dL=10, light_dL=8, seed=5102,
       grain=2.10, tone=1.07, fibre=0.6, streak=0.4, pore=0.45, pore_col="#2a1c12", ray=0.3, ray_col="#2e2016", knot="#21160f",
       rim="#140c08", check="#120b07", halo=3.0, smooth=0.40),
    _F("eco-oak", "organic-oak", "Organic Oak", "legno", "#b9a07a", (-0.06, -0.05), dark_dL=22, light_dL=10,
       grain=2.04, tone=3.69, fibre=0.9, streak=0.5, pore=0.5, pore_col="#8a7050", ray=0.35, ray_col="#937a58", knot="#5c4632",
       rim="#3a2a1c", check="#3b2d20", halo=6.0, smooth=0.40),
    _F("eco-oak", "nordic-oak", "Nordic Oak", "legno", "#f5f1e6", (0.0, -0.06), dark_dL=14, light_dL=3,
       grain=1.34, tone=1.83, fibre=0.5, streak=0.4, pore=0.45, pore_col="#cdc6b4", ray=0.3, ray_col="#d9d3c3", knot="#b0a591",
       rim="#9a8f7c", check="#a09684", halo=4.0, smooth=0.40),
    _F("eco-oak", "original-oak", "Original Oak", "rustic", "#8d735b", (-0.07, 0.07), dark_dL=25, light_dL=15,
       grain=6.05, tone=2.39, fibre=1.2, streak=0.8, pore=0.55, pore_col="#5c4631", ray=0.45, ray_col="#6a5440", knot="#4a3524",
       rim="#2a1c12", check="#1e150e", halo=8.0, smooth=0.38),
    _F("eco-oak", "chalet-grande", "Chalet Grande", "chalet", "#764b40", (-0.19, -0.13), dark_dL=15, light_dL=10,
       grain=0.8, tone=4.8, fibre=0.9, streak=0.5, pore=0.5, pore_col="#d6b8ad", ray=0.3, ray_col="#9a6d61", knot="#3e241c",
       rim="#24130e", check="#2a1812", halo=6.0, smooth=0.34),
    _F("eco-oak", "chalet-grasse", "Chalet Grasse", "chalet", "#6b6a6d", (0.0, -0.03), dark_dL=15, light_dL=10,
       grain=0.8, tone=5.0, fibre=0.9, streak=0.5, pore=0.35, pore_col="#c8c7c9", ray=0.3, ray_col="#8a898c", knot="#353437",
       rim="#1f1e20", check="#232224", halo=6.0, smooth=0.34),
    _F("eco-oak", "chalet-provence", "Chalet Provence", "chalet", "#cecac0", (0.0, -0.02), dark_dL=15, light_dL=6,
       grain=1.19, tone=2.19, fibre=0.6, streak=0.4, pore=0.5, pore_col="#f0ede6", ray=0.25, ray_col="#bdb8ad", knot="#8f887b",
       rim="#6b655a", check="#77716a", halo=4.0, smooth=0.34),
    _F("eco-oak", "graphite-art", "Graphite Art", "concrete", "#585965", (0.02, -0.08), dark_dL=10, light_dL=10,
       tone=0.3, fibre=1.26, mottle=0.3, mottle_col="#6e707d", pit=0.8, pit_col="#3a3b44", smooth=0.30),
    _F("softwood", "cappuccino-softwood", "Cappuccino Softwood", "pine", "#e9ddd2", (-0.15, -0.15), dark_dL=10,
       light_dL=4, grain=1.29, tone=0.46, fibre=0.3, streak=0.3, smooth=0.40),
    _F("softwood", "white-softwood", "White Softwood", "pine", "#f7f7f7", (0.0, 0.0), dark_dL=8, light_dL=2,
       seed=7303, grain=1.03, tone=0.17, fibre=0.25, streak=0.3, smooth=0.40),
]
FAMILIES = ("eco-oak", "softwood")

# Flat, grain-vertical areas of the catalogue photos (tools/doors/.cache/photos): (file, (x0, y0, x1, y1)); the
# first one of each finish is shown on the check sheet. Boxes per render layout (the renders of one model share it).
_K12 = [(62, 52, 108, 148), (62, 240, 108, 288), (24, 40, 36, 170), (130, 40, 142, 300)]      # КЛАССИКО-12
_K13 = [(62, 240, 108, 288), (24, 40, 36, 170), (130, 40, 142, 300)]                           # КЛАССИКО-13 WC
_KST = [(24, 40, 36, 170), (130, 40, 142, 300)]                                                # КЛАССИКО stiles
_K32S = [(54, 56, 110, 200), (54, 249, 110, 300), (22, 40, 38, 170), (127, 40, 142, 300)]     # КЛАССИКО-32, 165 px
_K32T = [(62, 60, 112, 190), (62, 250, 112, 300), (25, 40, 39, 170), (132, 40, 144, 300)]     # 171 px wide renders
_K33S = [(54, 249, 110, 300), (22, 40, 38, 170), (127, 40, 142, 300)]
_K33T = [(62, 250, 112, 300), (25, 40, 39, 170), (132, 40, 144, 300)]
_K32B = [(125, 135, 260, 480), (130, 595, 255, 730), (52, 60, 92, 425), (52, 470, 92, 800), (300, 60, 338, 800)]
_K33B = [(130, 595, 255, 730), (52, 60, 92, 425), (52, 470, 92, 800), (300, 60, 338, 800)]
_L21 = [(122, 50, 134, 285), (13, 14, 29, 165)]                                                # ЛЕГНО-21/22/23/28
_L38B = [(32, 40, 72, 395), (32, 445, 72, 800), (302, 40, 338, 800), (228, 160, 295, 242), (78, 380, 148, 466),
         (228, 604, 295, 686)]                                                                 # ЛЕГНО-38/39, big
_L28B = [(32, 40, 72, 395), (32, 445, 72, 800), (302, 40, 338, 800)]                          # ЛЕГНО-28, big
_L38S = [(13, 12, 29, 165), (13, 185, 29, 326), (123, 40, 135, 300)]                           # ЛЕГНО-38/39, small


def _R(fname, boxes):
    return [(fname, b) for b in boxes]


def _legno(fid, ext="jpg", models=("p053_legno-21", "p054_legno-22", "p055_legno-23")):
    return [r for m in models for r in _R(f"{m}__{fid}.{ext}", _L21)]


REFS = {
    "royal-oak": _R("p041_klassiko-12__royal-oak.jpg", _K12) + _R("p042_klassiko-13-wc__royal-oak.jpg", _K13[1:]),
    "antique-oak": _R("p041_klassiko-12__antique-oak.jpg", _K12) + _R("p042_klassiko-13-wc__antique-oak.jpg", _K13[1:]),
    "silver-ash": _R("p041_klassiko-12__silver-ash.jpg", _K12) + _R("p042_klassiko-13-wc__silver-ash.jpg", _K13[1:])
    + _R("p041_klassiko-12__silver-ash-silver-rift.jpg", _K12[:1] + _K12[2:])
    + _R("p042_klassiko-13-wc__silver-ash-silver-rift.jpg", _K13[1:]),
    "ivory": _R("p041_klassiko-12__ivory.jpg", _K12) + _R("p042_klassiko-13-wc__ivory.jpg", _K13[1:])
    + [r for m in ("16", "17-3-mf", "32g-27", "33g-27-mf") for r in _R(f"p043_klassiko-{m}__ivory.jpg", _KST)],
    "virgin": _R("p057_legno-39__virgin.jpg", _L28B) + _R("p041_klassiko-12__virgin.jpg", _K12)
    + _R("p042_klassiko-13-wc__virgin.jpg", _K13[1:]) + _R("p043_klassiko-16__virgin.jpg", _KST) + _legno("virgin")
    + _R("p057_legno-38__virgin.jpg", _L38S),
    "dark-oak": _R("p044_klassiko-32__dark-oak.jpg", _K32S) + _R("p045_klassiko-33-wc__dark-oak.jpg", _K33S[1:])
    + _legno("dark-oak"),
    "organic-oak": _R("p045_klassiko-33-wc__organic-oak.jpg", _K33B) + _R("p044_klassiko-32__organic-oak.jpg", _K32T)
    + _legno("organic-oak"),
    "nordic-oak": _R("p044_klassiko-32__nordic-oak.jpg", _K32B) + _R("p045_klassiko-33-wc__nordic-oak.jpg", _K33T)
    + _legno("nordic-oak"),
    "original-oak": _R("p057_legno-38__original-oak.jpg", _L38B) + _R("p057_legno-39__original-oak.jpg", _L38S)
    + _legno("original-oak"),
    "chalet-grande": _R("p056_legno-28__chalet-grande.jpg", _L28B) + _R("p041_klassiko-12__chalet-grande.jpg", _K12)
    + _R("p042_klassiko-13-wc__chalet-grande.jpg", _K13) + _legno("chalet-grande"),
    "chalet-grasse": _R("p056_legno-28__chalet-grasse.jpg", _L28B) + _legno("chalet-grasse"),
    "chalet-provence": _R("p041_klassiko-12__chalet-provence.jpg", _K12)
    + _R("p042_klassiko-13-wc__chalet-provence.jpg", _K13) + _legno("chalet-provence")
    + _R("p056_legno-28__chalet-provence.jpg", _L21),
    "graphite-art": _legno("graphite-art"),
    "cappuccino-softwood": _R("p041_klassiko-12__cappuccino-softwood.jpg", _K12)
    + _R("p042_klassiko-13-wc__cappuccino-softwood.jpg", _K13[1:])
    + _R("p044_klassiko-32__cappuccino-softwood.jpg", _K32S) + _R("p045_klassiko-33-wc__cappuccino-softwood.jpg", _K33S[1:])
    + _legno("cappuccino-softwood") + _R("p056_legno-28__cappuccino-softwood.jpg", _L21),
    # (the КЛАССИКО-12 and ЛЕГНО-21 renders of White Softwood are PNGs without JPEG tables: not usable by as_photo)
    "white-softwood": _R("p042_klassiko-13-wc__white-softwood.jpg", _K13)
    + _legno("white-softwood", models=("p054_legno-22", "p055_legno-23", "p056_legno-28")),
}


# ------------------------------------------------------------------------------------------------ maps
def structure(fin, cache):
    """The pattern fields of a finish, shared by the finishes of the same pattern and seed."""
    key = (fin["pattern"], fin.get("seed"))
    if key not in cache:
        builder = concrete_structure if fin["pattern"] == "concrete" else wood_structure
        cache[key] = builder(*key)
    return cache[key]


def albedo_linear(fin, st):
    """Linear-RGB albedo (h, w, 3) of a finish; its mean is exactly the finish's colour."""
    col = hex_to_linear(fin["color"])
    ratio = lambda hx: hex_to_linear(hx) / col
    rd = np.clip(ratio(fin["dark"]), 0.03, 1.0)
    rl = np.clip(ratio(fin["light"]), 1.0, 30.0)
    Lc = linear_to_lab(col)[0]
    dLd = max(1e-3, Lc - linear_to_lab(col * rd)[0])
    dLl = max(1e-3, linear_to_lab(col * rl)[0] - Lc)
    t = fin.get("tone", 0.0) * st["broad"] + fin.get("fibre", 0.0) * st["fibre"]
    if st.get("kind") != "concrete":
        late = st["late"]
        t = t - fin.get("grain", 0.0) * (late - late.mean()) / max(1e-9, late.std()) - fin.get("halo", 0.0) * st["halo"]
    t = t[..., None]
    out = np.where(t < 0, np.exp(-t / dLd * np.log(rd)), np.exp(t / dLl * np.log(rl)))

    def over(o, alpha, hx, mod=None):
        a = np.clip(alpha, 0.0, 1.0)[..., None]
        c = ratio(hx) if mod is None else ratio(hx) * mod[..., None]
        return o * (1 - a) + a * c

    if st.get("kind") == "concrete":
        out = over(out, fin["mottle"] * st["mottle"], fin["mottle_col"])
        out = over(out, fin["pit"] * st["pits"], fin["pit_col"])
    else:
        if fin.get("pore"):
            out = over(out, fin["pore"] * st["pores"], fin["pore_col"])
        if fin.get("ray"):
            out = over(out, fin["ray"] * st["rays"], fin["ray_col"])
        if fin.get("streak"):
            out = over(out, fin["streak"] * st["sdark"], fin["dark"])
            out = over(out, fin["streak"] * st["slight"], fin["light"])
        if fin.get("knot"):
            out = over(out, st["knot"], fin["knot"], 0.8 + 0.4 * st["kring"])
            out = over(out, st["rim"], fin["rim"])
        if fin.get("check"):
            out = over(out, st["check"], fin["check"])
    base = col / out.reshape(-1, 3).mean(0, dtype=np.float64)
    for _ in range(4):                          # clipping at 1 (the white films) shifts the mean: re-solve
        a = np.clip(out * base, 0, 1)
        base *= col / a.reshape(-1, 3).mean(0, dtype=np.float64)
    return np.clip(out * base, 0, 1)


def normal_map(st):
    rel = st["relief"]
    if st.get("kind") == "concrete":
        hgt = -rel["pits"] * st["pits"] - rel["mottle"] * st["mottle"] + rel["fibre"] * 0.25 * st["fibre"]
    else:
        hgt = (-rel["pores"] * st["pores"] - rel["checks"] * st["check"] - rel["rays"] * st["rays"]
               - rel["rim"] * st["rim"] - rel["late"] * st["late"] + rel["fibre"] * 0.25 * st["fibre"])
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
    d = box_down(st["pits"] if st.get("kind") == "concrete" else st["pores"] + st.get("check", 0) * 2, f)
    d = (d - d.mean()) / max(1e-9, d.std())
    base = fin["smooth"] * 255
    sm = np.clip(base - 3.0 * d, base - 15, base + 8)
    m = np.zeros((MASK[1], MASK[0], 4), np.uint8)
    m[..., 1] = 255
    m[..., 3] = np.round(sm).astype(np.uint8)
    return m


# ------------------------------------------------------------------------------------------------ output
def albedo_path(fin):
    return EXT / "Materials" / fin["material"] / (fin["material"] + "_albedo.jpg")


def write_finish(fin, st, alb):
    mid = fin["material"]
    folder = EXT / "Materials" / mid
    folder.mkdir(parents=True, exist_ok=True)
    rgb = np.round(linear_to_srgb(alb) * 255).astype(np.uint8)
    Image.fromarray(rgb).save(folder / f"{mid}_albedo.jpg", quality=90, subsampling=0, optimize=True)
    Image.fromarray(normal_map(st)).save(folder / f"{mid}_normal.jpg", quality=92, subsampling=0, optimize=True)
    Image.fromarray(mask_map(fin, st)).save(folder / f"{mid}_mask.png", optimize=True)


def read_albedo(fin):
    return srgb_to_linear(np.asarray(Image.open(albedo_path(fin)).convert("RGB"), dtype=np.float64) / 255)


def manifest_entry(fin):
    mid = fin["material"]
    return {"id": mid, "name": f"{fin['name']} ({fin['line']})", "category": "door", "source": SOURCE,
            "neutral": False, "metersPerTile": list(TILE_M), "maxSize": ALBEDO[0], "folder": f"Materials/{mid}",
            "textures": {"albedo": f"{mid}_albedo.jpg", "normal": f"{mid}_normal.jpg", "mask": f"{mid}_mask.png"}}


def write_family(family, merge=True):
    """entries/<family>.json (+ merge into external.json) and Resources/Doors/Finishes/<family>.json."""
    fins = [f for f in FINISHES if f["family"] == family]
    ENTRY_DIR.mkdir(parents=True, exist_ok=True)
    entries = ENTRY_DIR / f"{family}.json"
    entries.write_text(json.dumps([manifest_entry(f) for f in fins], ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")
    rows = []
    for f in fins:
        mean = read_albedo(f).reshape(-1, 3).mean(0) if albedo_path(f).exists() else hex_to_linear(f["color"])
        rows.append({"id": f["id"], "name": f["name"], "line": f["line"], "material": f["material"],
                     "color": linear_to_hex(mean)})
    FINISH_DIR.mkdir(parents=True, exist_ok=True)
    (FINISH_DIR / f"{family}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n",
                                               encoding="utf-8")
    print("family", family, "->", entries.relative_to(ROOT), "+", (FINISH_DIR / f"{family}.json").relative_to(ROOT))
    if merge:
        merge_entries.merge([str(entries)])


# ------------------------------------------------------------------------------------------------ fitting
STATS = mf.STATS


def measure(fin, alb):
    mf.REFS.update(REFS)
    return mf.measure(fin, alb)


def fit(fin, st, rounds=2):
    """Suggests `grain` (concrete: `fibre`) and `tone` so that the texture, seen like its photos, has the photos' contrast statistics
    (sx, fine, band); wave 1's method (each statistic squared ~ linear in grain^2 and tone^2)."""
    f = dict(fin)
    fine = "fibre" if fin["pattern"] == "concrete" else "grain"      # concrete: no rings, the sand is the fine part
    for _ in range(rounds):
        c, t = max(0.3, f.get(fine, 1.0)), max(0.3, f["tone"])
        rows, got = [], []
        for pc, pt in [(c, t), (c * 1.4, t), (c, t * 1.6)]:
            g = dict(f, **{fine: pc}, tone=pt)
            r = measure(g, albedo_linear(g, st))
            rows.append([1.0, pc * pc, pt * pt])
            got.append([r["t" + k] ** 2 for k in STATS])
        coef = np.linalg.solve(np.array(rows), np.array(got))
        target = np.array([r["p" + k] ** 2 for k in STATS])
        m = coef[1:].T / target[:, None]
        want = (target - coef[0]) / target
        best = None
        for fix in (None, 0, 1):
            x = np.array([0.01, 0.01])
            if fix is None:
                x = np.linalg.lstsq(m, want, rcond=None)[0]
            else:
                o = 1 - fix
                x[o] = max(0.01, float(m[:, o] @ (want - m[:, fix] * 0.01)) / float(m[:, o] @ m[:, o]))
            if np.all(x >= 0.01 - 1e-9):
                err = float(np.sum((m @ x - want) ** 2))
                if best is None or err < best[0]:
                    best = (err, x)
        f[fine], f["tone"] = [round(float(math.sqrt(v)), 2) for v in best[1]]
    r = measure(f, albedo_linear(f, st))
    print("fit %-20s %s=%.2f, tone=%.2f   " % (f["id"], fine, f[fine], f["tone"]) +
          "  ".join("%s %.2f/%.2f" % (k, r["p" + k], r["t" + k]) for k in STATS) + "  dE %.2f" % r["de"])
    return f


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("finishes", nargs="*", help="finish ids (default: all of --family)")
    ap.add_argument("--family", choices=FAMILIES, help="only this family")
    ap.add_argument("--compare", action="store_true", help="write tools/doors/.cache/finishes_<family>.png")
    ap.add_argument("--no-write", action="store_true", help="do not write textures / entries / external.json")
    ap.add_argument("--no-merge", action="store_true", help="write entries/<family>.json but do not merge it")
    ap.add_argument("--fit", action="store_true", help="suggest grain / tone from the photos (needs the photos)")
    args = ap.parse_args()
    fins = [f for f in FINISHES if (not args.finishes or f["id"] in args.finishes)
            and (not args.family or f["family"] == args.family)]
    if args.finishes and len(fins) != len(args.finishes):
        sys.exit("unknown finish: " + ", ".join(set(args.finishes) - {f["id"] for f in fins}))
    if (args.compare or args.fit) and not (CACHE / "photos").is_dir():
        sys.exit("no catalogue photos in %s: run tools/doors/catalog_index.py first" % (CACHE / "photos"))
    mf.REFS.update(REFS)
    structures, albedos = {}, {}
    for fin in fins:
        st = structure(fin, structures)
        if args.fit:
            fit(fin, st)
            continue
        alb = albedo_linear(fin, st)
        if not args.no_write:
            write_finish(fin, st, alb)
            print("finish", fin["id"], "->", fin["material"])
            alb = read_albedo(fin)             # compare what Unity gets: the written JPEG
        if args.compare:
            albedos[fin["id"]] = alb.astype(np.float32)
    if args.fit:
        return
    families = [fam for fam in FAMILIES if any(f["family"] == fam for f in fins)]
    if not args.no_write:
        for fam in families:
            write_family(fam, merge=not args.no_merge)
    if args.compare:
        for fam in families:
            mf.compare([f for f in fins if f["family"] == fam], albedos, CACHE / f"finishes_{fam}.png")


if __name__ == "__main__":
    main()
