#!/usr/bin/env python3
"""Casegoods decor textures, family dark_oaks_a: the mid / dark rustic oak films of Pinskdrev (SWN / SWA / WML
synchronised-pore melamine) - Дуб Каньон, Дуб Канзас 377, Дуб Нокс 392, Дуб Вотан 376, Дуб Саттер 369, Дуб Юкон 358.

    python3 tools/casegoods/textures/dark_oaks_a.py                 # every material: textures + entries + merge
    python3 tools/casegoods/textures/dark_oaks_a.py cg_dub_noks      # only these
    python3 tools/casegoods/textures/dark_oaks_a.py --no-write --sheet   # check sheet only (from the written maps)
    python3 tools/casegoods/textures/dark_oaks_a.py --sheet          # write + check sheet (needs PyMuPDF)
    python3 tools/casegoods/textures/dark_oaks_a.py --analyze        # swatch colour, L* detail and streak hue slopes

Writes per material M (tile 2.0 m x 1.0 m, grain along U = image x):
    Assets/House4696/External/Materials/M/M_albedo.jpg   sRGB 2048x1024, tileable
    Assets/House4696/External/Materials/M/M_normal.jpg   OpenGL 1024x512
    Assets/House4696/External/Materials/M/M_mask.png     R metallic 0, G AO 255, B 0, A smoothness, 256x128
and tools/casegoods/textures/entries/dark_oaks_a.json (merged into external.json with tools/doors/textures/
merge_entries.py), tools/casegoods/textures/sheets/dark_oaks_a.png (--sheet).

Model: the door wave's sawn-board oak (tools/doors/textures/eco_oak.py: boards across the tile, each with its own
log - growth rings opening into cathedrals where the cut runs near the pith, pores along the earlywood, rays, knots
with rims and radial checks, checks along the rings, dark / light streaks, broad zone / board / cloud tone), used
unchanged through its PATTERNS table (in memory), plus what these furniture films print on top:
  * plank joints - a thin dark line at some board edges and a few butt joints across a board (Нокс, Вотан, Канзас);
  * saw marks - bandsaw lines across the grain on some boards (Юкон, Вотан, Канзас: rough-sawn character);
  * grey wash - pale grey streaks and patches (Канзас, Юкон: weathered, limed look).
Colour: the mean in linear light is solved to the chosen catalogue swatch; the dark / light ends of the tone follow
the swatch's own a*, b* against L* slopes (--analyze). The generator needs only numpy + Pillow (PyMuPDF only for the
swatch / photo crops of --sheet / --analyze).
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
DOORS = ROOT / "tools" / "doors" / "textures"
GEN = ROOT / "tools" / "casegoods" / "gen"
for p in (DOORS,):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
import eco_oak as eco                 # noqa: E402  (sawn-board oak structure, colouring, knots, checks)
import finish_kit as fk               # noqa: E402  (straight lines of the saw marks, smoothstep)
import make_finishes as mf            # noqa: E402  (colour maths, noise)
import merge_entries                  # noqa: E402

FAMILY = "dark_oaks_a"
SOURCE = "procedural:tools/casegoods/textures/dark_oaks_a.py"
EXT = mf.EXT
ALBEDO, NORMAL, MASK, MM, TILE_M = mf.ALBEDO, mf.NORMAL, mf.MASK, mf.MM, mf.TILE_M
W_PX, H_PX = ALBEDO
PX = 1.0 / MM
ENTRIES = HERE / "entries" / f"{FAMILY}.json"
SHEET = HERE / "sheets" / f"{FAMILY}.png"
hex_to_linear, linear_to_hex, linear_to_lab = mf.hex_to_linear, mf.linear_to_hex, mf.linear_to_lab
linear_to_srgb, srgb_to_linear = mf.linear_to_srgb, mf.srgb_to_linear
gauss_noise, noise_1d = mf.gauss_noise, mf.noise_1d


# ------------------------------------------------------------------------------------------------ patterns
# eco_oak's pattern keys (see its PATTERNS comment) + this family's extras:
#   joints = dict(edge=share of board edges drawn, width mm, alpha, butt=butt joints per m of board, butt_alpha)
#   saw    = dict(boards=share of boards with saw marks, pitch (median mm, log-sigma), width, strength, share_on)
#   wash   = dict(sigma across, sigma along, threshold, softness) - pale grey patches following the grain
def _p(seed, **kw):
    base = dict(
        seed=seed,
        board=(170.0, 0.3, 100.0, 300.0), flat_share=0.5, pith_in=0.22, rift_out=0.6, pith_wander=0.12,
        pith_len=400.0, depth=(40.0, 0.4), depth_amp=0.6, turns=(1, 3), turn_round=25.0, dmin=4.0, ecc=0.15,
        wave=[(4.0, 260.0, 30.0), (1.5, 90.0, 12.0), (0.6, 35.0, 5.0)],
        rings=dict(ring=(3.0, 0.35), early=(0.8, 0.25), late_gamma=1.5, trend=6.0, vary=0.45),
        late_fibre=(0.6, 0.5, 4.0),
        zone_len=5.0,
        pores=dict(len=0.8, wid=0.35, thr=0.0, fill=0.9, late=0.08),
        rays=dict(per_cm=1.2, width=(0.35, 0.3), length=(9.0, 0.6), alpha=(0.2, 0.6), fade=0.6, slope=0.0),
        knots=dict(per_m2=1.5, size=(10.0, 0.45), max=30.0, bump=2.5, flow=2.6, aspect=2.0, rim=0.14,
                   rim_alpha=0.85, halo=0.6, cracked=0.8),
        pins=dict(per_m2=1.5, size=(3.0, 0.3), max=6.0, aspect=1.6, rim=0.3, rim_alpha=0.5, halo=0.3),
        checks=dict(per_m2=6.0, length=(120.0, 0.7), width=(1.0, 0.45), wiggle=1.0),
        sdark=dict(per_cm=0.9, width=(0.6, 0.5), length=(180.0, 0.8), alpha=(0.25, 0.9), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.5, width=(0.8, 0.45), length=(100.0, 0.8), alpha=(0.2, 0.9), fade=0.8, slope=0.002),
        bands=(25.0, 700.0), clouds=(150.0, 500.0), fibre=(0.35, 5.0), broad_mix=(0.55, 0.45, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.3, late=0.25, tilt_deg=3.5),
    )
    for k, v in kw.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            base[k] = dict(base[k], **v)
        else:
            base[k] = v
    return base


PATTERNS = {
    # Каньон: long straight planks, darker streaks, small knots and short cracks, faint cathedrals, calm
    "cg_kanon": _p(8101, board=(165.0, 0.3, 100.0, 260.0), flat_share=0.4, depth=(45.0, 0.4),
                   rings=dict(ring=(2.6, 0.35)),
                   knots=dict(per_m2=1.2, size=(12.0, 0.45), max=26.0), pins=dict(per_m2=2.0),
                   checks=dict(per_m2=7.0, length=(90.0, 0.6), width=(0.8, 0.4), wiggle=0.8),
                   sdark=dict(per_cm=1.1, alpha=(0.25, 0.9)), slight=dict(per_cm=0.6),
                   broad_mix=(0.5, 0.45, 0.35)),
    # Канзас 377: strong plank striping, pale grey streaks on dark brown, lengthwise cracks and knots
    "cg_kanzas": _p(8201, board=(150.0, 0.35, 80.0, 260.0), flat_share=0.35, depth=(40.0, 0.4),
                    rings=dict(ring=(2.8, 0.4), vary=0.5),
                    knots=dict(per_m2=1.8, size=(14.0, 0.45), max=34.0), pins=dict(per_m2=2.0),
                    checks=dict(per_m2=14.0, length=(200.0, 0.6), width=(1.3, 0.5), wiggle=1.4),
                    sdark=dict(per_cm=1.3, width=(0.7, 0.5), alpha=(0.3, 1.0)),
                    slight=dict(per_cm=0.7, width=(1.0, 0.5), length=(160.0, 0.8), alpha=(0.2, 0.8)),
                    broad_mix=(0.35, 0.7, 0.3),
                    joints=dict(edge=0.5, width=0.7, alpha=0.5, butt=0.0, butt_alpha=0.0),
                    saw=dict(boards=0.25, pitch=(13.0, 0.3), width=(3.5, 0.3), strength=(0.15, 0.5), share_on=0.45, blur=1.5),
                    wash=dict(sigma=(4.0, 160.0), thr=0.9, soft=0.7)),
    # Нокс 392: bold cathedrals, dark knots with cracks, plank joints
    "cg_noks": _p(8301, board=(180.0, 0.3, 110.0, 280.0), flat_share=0.75, depth=(45.0, 0.4), depth_amp=0.65,
                  wave=[(5.0, 240.0, 28.0), (1.8, 80.0, 11.0), (0.6, 30.0, 5.0)],
                  rings=dict(ring=(3.4, 0.35), vary=0.5),
                  knots=dict(per_m2=1.7, size=(18.0, 0.38), max=40.0, aspect=3.0, flow=3.4, bump=3.0, cracked=0.8, halo=0.45, rim=0.18), pins=dict(per_m2=0.0),
                  crack_knots=dict(share=0.7, length=(2.5, 6.0), width=(1.1, 0.4)),
                  pin_clusters=dict(mean=1.5, count=(3, 7), spread=(35.0, 8.0)),
                  checks=dict(per_m2=9.0, length=(140.0, 0.7), width=(1.2, 0.45), wiggle=1.2),
                  sdark=dict(per_cm=0.9), broad_mix=(0.6, 0.45, 0.3),
                  joints=dict(edge=0.6, width=0.7, alpha=0.5, butt=0.35, butt_alpha=0.35)),
    # Вотан 376: honey ground, frequent small dark knots with lengthwise cracks, saw-cut streaks, long planks
    "cg_votan": _p(8405, board=(160.0, 0.3, 90.0, 260.0), flat_share=0.35, depth=(40.0, 0.4),
                   rings=dict(ring=(2.8, 0.35)),
                   knots=dict(per_m2=2.2, size=(17.0, 0.38), max=40.0, aspect=3.0, flow=3.4, bump=3.0, cracked=0.8, halo=0.45, rim=0.18), pins=dict(per_m2=0.0),
                   crack_knots=dict(share=0.85, length=(2.5, 6.0), width=(1.2, 0.4)),
                   pin_clusters=dict(mean=2.0, count=(3, 7), spread=(35.0, 8.0)),
                   checks=dict(per_m2=24.0, length=(160.0, 0.6), width=(1.4, 0.5), wiggle=1.2),
                   sdark=dict(per_cm=1.2, width=(0.6, 0.5), alpha=(0.3, 1.0)),
                   slight=dict(per_cm=0.8, width=(0.9, 0.45)), broad_mix=(0.45, 0.55, 0.35),
                   joints=dict(edge=0.4, width=0.6, alpha=0.45, butt=0.2, butt_alpha=0.5),
                   saw=dict(boards=0.3, pitch=(12.0, 0.3), width=(3.5, 0.3), strength=(0.1, 0.4), share_on=0.4, blur=1.5)),
    # Саттер 369: reddish-brown rustic oak, dark knots, lengthwise cracks, grey-brown streaks, soft cathedrals
    "cg_satter": _p(8501, board=(175.0, 0.3, 110.0, 280.0), flat_share=0.55, depth=(45.0, 0.4),
                    rings=dict(ring=(3.0, 0.35)),
                    knots=dict(per_m2=1.5, size=(20.0, 0.38), max=40.0, aspect=3.0, flow=3.4, bump=3.0, cracked=0.8, halo=0.45, rim=0.18), pins=dict(per_m2=0.0),
                    crack_knots=dict(share=0.8, length=(2.5, 6.0), width=(1.3, 0.4)),
                    pin_clusters=dict(mean=1.0, count=(3, 6), spread=(30.0, 8.0)),
                    olive=dict(per_cm=0.6, width=(2.5, 0.5), length=(300.0, 0.7), alpha=(0.3, 0.9), fade=0.8, slope=0.002),
                    checks=dict(per_m2=20.0, length=(220.0, 0.6), width=(1.4, 0.5), wiggle=1.3),
                    sdark=dict(per_cm=1.8, width=(0.8, 0.5), alpha=(0.3, 1.0)),
                    slight=dict(per_cm=0.8, width=(0.9, 0.45)),
                    broad_mix=(0.55, 0.45, 0.35)),
    # Юкон 358: weathered grey rough-sawn planks, saw marks across the grain, open cracks, dark knots,
    # low-contrast cathedrals
    "cg_yukon": _p(8601, board=(160.0, 0.3, 100.0, 260.0), flat_share=0.45, depth=(45.0, 0.4),
                   rings=dict(ring=(3.2, 0.4), vary=0.5),
                   pores=dict(fill=0.7),
                   knots=dict(per_m2=1.6, size=(17.0, 0.38), max=40.0, aspect=3.0, flow=3.4, bump=3.0, cracked=0.8, halo=0.45, rim=0.18), pins=dict(per_m2=0.0),
                   crack_knots=dict(share=0.75, length=(2.5, 6.0), width=(1.4, 0.4)),
                   pin_clusters=dict(mean=1.2, count=(3, 6), spread=(35.0, 8.0)),
                   checks=dict(per_m2=16.0, length=(220.0, 0.6), width=(1.6, 0.5), wiggle=1.5),
                   sdark=dict(per_cm=1.4, width=(0.6, 0.5), alpha=(0.25, 1.0)),
                   slight=dict(per_cm=1.4, width=(1.0, 0.5), length=(160.0, 0.8), alpha=(0.3, 1.0)),
                   broad_mix=(0.35, 0.6, 0.4),
                   joints=dict(edge=0.35, width=0.6, alpha=0.4, butt=0.0, butt_alpha=0.0),
                   saw=dict(boards=0.6, pitch=(20.0, 0.3), width=(3.0, 0.3), strength=(0.8, 1.0), share_on=0.75, on=(0.3, 1.0), blur=3.5),
                   wash=dict(sigma=(5.0, 200.0), thr=0.6, soft=0.8),
                   relief=dict(tilt_deg=4.0)),
}
eco.PATTERNS.update(PATTERNS)          # in memory only: eco_oak.py itself is not touched


# ------------------------------------------------------------------------------------------------ extra fields
def board_edges(p):
    """The board edges (px, may exceed the tile height: wrap) eco_oak.wood_structure draws for pattern p - its rng
    draws the widths and the offset first, so the same seed gives the same boards."""
    rng = np.random.default_rng(p["seed"])
    widths = []
    while sum(widths) < eco.TILE_MM[1]:
        widths.append(float(np.clip(eco.lognormal(rng, p["board"][:2]), *p["board"][2:])))
    widths = np.array(widths) * eco.TILE_MM[1] / sum(widths)
    off = rng.uniform(0, eco.TILE_MM[1])
    return (np.concatenate([[0.0], np.cumsum(widths)]) + off) * PX


def extras(pid, st):
    """Adds this family's fields to the eco_oak structure: joint, saw, wash (0..1 opacities)."""
    p = PATTERNS[pid]
    rng = np.random.default_rng(p["seed"] + 77)
    h, w = H_PX, W_PX
    edges = board_edges(p)
    rows = np.arange(h)[:, None] + 0.5
    joint = np.zeros((h, w))
    saw = np.zeros((h, w))
    wash = np.zeros((h, w))
    js = p.get("joints")
    ss = p.get("saw")
    for i in range(len(edges) - 1):
        y0, y1 = edges[i], edges[i + 1]
        # rows of this board (periodic), their coverage
        dy = (rows - y0) % h
        inside = (dy < (y1 - y0)).astype(float)
        if js and rng.random() < js["edge"]:
            env = fk.smoothstep(-0.6, 0.4, noise_1d(rng, w, 120 * PX))[None, :]
            d = np.abs(mf_periodic(rows - y0, h))
            joint = np.maximum(joint, np.clip(js["width"] * PX / 2 + 0.5 - d, 0, 1) * js["alpha"] * env)
        if js and js.get("butt", 0) > 0:
            for _ in range(rng.poisson(js["butt"] * TILE_M[0])):
                x0 = rng.uniform(0, w)
                dx = np.abs(mf_periodic(np.arange(w)[None, :] + 0.5 - x0, w))
                line = np.clip(js["width"] * PX / 2 + 0.5 - dx, 0, 1)
                joint = np.maximum(joint, line * inside * js["butt_alpha"])
        if ss and rng.random() < ss["boards"]:
            lines = fk.straight_lines(rng, ss["pitch"], ss["width"], PX, axis=1, jitter_len=40.0,
                                      strength=ss["strength"], share_on=ss["share_on"], soft=0.6,
                                      wander=2.0, wander_len=60.0)
            # a board shows them over a part of its length only
            along = fk.smoothstep(*ss.get("on", (-0.3, 0.5)), noise_1d(rng, w, 250 * PX))[None, :]
            soft_in = np.clip(np.minimum(dy, (y1 - y0) - dy) / 3.0, 0, 1) * inside
            lines = mf.blur(lines, 0.0, ss.get("blur", 0.0) * PX) if ss.get("blur") else lines
            saw = np.maximum(saw, lines * along * soft_in)
    wsp = p.get("wash")
    if wsp:
        disp = gauss_noise(rng, (h, w), 150 * PX, 25 * PX) * (0.8 * PX)
        n = mf.warp_rows(gauss_noise(rng, (h, w), wsp["sigma"][1] * PX, wsp["sigma"][0] * PX), disp)
        n = 0.75 * n + 0.25 * gauss_noise(rng, (h, w), 40 * PX, 20 * PX)
        wash = fk.smoothstep(wsp["thr"] - wsp["soft"] / 2, wsp["thr"] + wsp["soft"] / 2, n / n.std())
    st["joint"], st["saw"], st["wash"] = joint, saw, wash
    knot_features(p, st)
    return st


def knot_centres(k):
    """Centres (px) and diameters (mm) of the knots in the core field k: peaks of the blurred field, size from the
    core area around each (elongated along x by the knots' aspect)."""
    f = 4
    kd = mf.box_down(k, f)
    b = mf.blur(kd, 2.0, 4.0)
    mx = b.copy()
    for dy in range(-4, 5):
        for dx in range(-10, 11):
            mx = np.maximum(mx, np.roll(np.roll(b, dy, 0), dx, 1))
    ys, xs = np.nonzero((b >= mx - 1e-12) & (b > 0.12))
    h, w = k.shape
    out = []
    for y, x in zip(ys, xs):
        yc, xc = (y + 0.5) * f, (x + 0.5) * f
        rr = np.arange(int(yc) - 40, int(yc) + 41) % h
        cc = np.arange(int(xc) - 90, int(xc) + 91) % w
        area = float(k[np.ix_(rr, cc)].sum()) * MM * MM
        out.append((xc, yc, math.sqrt(4 * area / math.pi)))
    return out


def knot_features(p, st):
    """Lengthwise cracks through the knots, clusters of pin knots, olive-grey streaks (patterns that ask for them);
    own rng, so the patterns without them stay as they were."""
    if not any(p.get(k) for k in ("crack_knots", "pin_clusters", "olive")):
        return
    rng = np.random.default_rng(p["seed"] + 99)
    h, w = H_PX, W_PX
    ck = p.get("crack_knots")
    if ck:
        asp = p["knots"].get("aspect", 1.3)
        knots = knot_centres(st["knot"])
        st["knot_list"] = knots
        for xc, yc, dia in knots:
            if dia < 6 or rng.random() > ck["share"]:
                continue
            L = dia * math.sqrt(asp) * rng.uniform(*ck["length"]) * PX    # px along the grain (knot length x factor)
            x0 = xc - L * rng.uniform(0.3, 0.7)
            n = int(L)
            cols = (np.floor(x0) + np.arange(n)).astype(int) % w
            sp = np.arange(n) / max(1, n - 1)
            wig = noise_1d(rng, max(64, n), 25 * PX)[:n] * (0.8 * PX) + rng.uniform(-0.08, 0.08) * dia / math.sqrt(asp) * PX
            yline = yc + wig
            hw = float(np.clip(ck["width"][0] * math.exp(ck["width"][1] * rng.standard_normal()), 0.5, 2.5)) \
                * PX / 2 * np.sin(np.pi * sp) ** 0.6 * np.exp(0.3 * noise_1d(rng, max(64, n), 10 * PX)[:n])
            r0 = int(math.floor(yline.min() - 4))
            r1 = int(math.ceil(yline.max() + 4))
            rows = np.arange(r0, r1 + 1)[:, None]
            cov = np.clip(hw[None, :] + 0.5 - np.abs(rows + 0.5 - yline[None, :]), 0, 1)
            ix = np.ix_(rows[:, 0] % h, cols)
            st["check"][ix] = np.maximum(st["check"][ix], cov)
    st["knot_big"] = st["knot"].copy()                 # the knots without the pin clusters
    pc = p.get("pin_clusters")
    if pc:
        for _ in range(rng.poisson(pc["mean"])):
            xc, yc = rng.uniform(0, w), rng.uniform(0, h)
            for _ in range(int(rng.integers(pc["count"][0], pc["count"][1] + 1))):
                xk = (xc + rng.normal(0, pc["spread"][0] * PX)) % w
                yk = (yc + rng.normal(0, pc["spread"][1] * PX)) % h
                a = float(np.clip(eco.lognormal(rng, (3.0, 0.3)), 1.8, 5.5))
                eco._draw_knot(rng, st, p, xk, yk, a, "pin")
    ol = p.get("olive")
    if ol:
        disp = gauss_noise(rng, (h, w), 150 * PX, 25 * PX) * (0.8 * PX)
        acc = np.zeros((h, w))
        mf.draw_lines(rng, acc, ol, disp, noise_1d(rng, 1 << 16, 8.0 * PX), PX)
        st["olive"] = np.clip(1 - np.exp(-acc) + 1.2 * st["halo"], 0, 1) * (1 - np.clip(st["knot"] + st["rim"], 0, 1))   # the knots stay dark


def mf_periodic(d, period):
    return (d + period / 2) % period - period / 2


# ------------------------------------------------------------------------------------------------ materials
def _M(mid, name, pattern, color, slope, swatch, photo, aliases, dark_dL=22.0, light_dL=14.0, **kw):
    """A material: colour = the chosen swatch's linear mean (sRGB hex); slope = its a*, b* per L* of the streaks;
    the layer colours are the mean shifted in L* along that slope (knot_dL, rim_dL, check_dL, pore_dL, ray_dL,
    joint_dL, saw_dL; wash_col = the grey of the wash)."""
    sh = lambda dl: eco.shade(color, dl, slope)
    d = dict(id=mid, name=name, material=mid, pattern=pattern, color=color, slope=slope, swatch=swatch,
             photo=photo, aliases=aliases, dark=sh(-dark_dL), light=sh(light_dL))
    for key, default in (("knot", -32), ("rim", -40), ("check", -42), ("pore", -12), ("ray", -6),
                         ("joint", -30), ("saw", -6)):
        d[key + "_col" if key in ("pore", "ray") else key] = sh(kw.pop(key + "_dL", default))
    d.update(kw)
    return d


# swatch / photo: (PDF page, crop fractions of the spread, rotate to grain-horizontal?)
MATERIALS = [
    _M("cg_dub_kanon", "Дуб Каньон", "cg_kanon", "#8c6d50", (-0.07, -0.09),
       (64, "0.265,0.865,0.31,0.905", False), (61, "0.345,0.73,0.405,0.9", True),
       ["«Дуб Каньон» Формат / Глобус p.64, Турин p.62-63, Оскар p.141, Плато p.140, Брауни p.114, Верес p.135,"
        " Юнона Лайт p.112, Каньон Лофт p.85"],
       dark_dL=20, light_dL=13, grain=3.2, tone=3.0, fibre=1.0, streak=0.6, pore=0.45, ray=0.35, halo=5.0,
       smooth=0.30),
    _M("cg_dub_kanzas", "Дуб Канзас 377 SWN", "cg_kanzas", "#7e6853", (-0.08, 0.02),
       (33, "0.757,0.850,0.784,0.895", False), (71, "0.135,0.45,0.2,0.53", False),
       ["«Дуб Канзас 377 SWN» Денвер p.33 / Ариста", "«ЛДСП ДУБ КАНЗАС» Форте Лофт p.71",
        "«Дуб Канзас 377ТМ» Лари p.137 / Мюнхен p.138"],
       dark_dL=22, light_dL=16, grain=3.6, tone=3.6, fibre=1.1, streak=0.7, pore=0.45, ray=0.3, halo=6.0,
       wash=0.35, wash_col="#9b9690", smooth=0.28),
    _M("cg_dub_noks", "Дуб Нокс 392 SWN", "cg_noks", "#7e5f40", (-0.10, -0.07),
       (14, "0.795,0.86,0.824,0.90", False), (14, "0.08,0.27,0.25,0.36", False),
       ["«Дуб Нокс 392 SWN» Рокси p.14 (каркас, столы)"],
       dark_dL=20, light_dL=12, grain=4.0, tone=3.2, fibre=1.0, streak=0.5, pore=0.5, ray=0.35, halo=7.0,
       knot_dL=-28, rim_dL=-46, smooth=0.30),
    _M("cg_dub_votan", "Дуб Вотан 376 WML", "cg_votan", "#9c7146", (-0.14, 0.03),
       (140, "0.716,0.852,0.77,0.895", False), (79, "0.12,0.18,0.155,0.33", True),
       ["«Дуб Вотан» Блэквуд Лофт p.79-80, Норд Лофт p.79 (ЛДСП), Плато p.140", "«Дуб Вотан 376 WML» Лайн p.69"],
       dark_dL=22, light_dL=13, grain=3.4, tone=3.4, fibre=1.0, streak=0.6, pore=0.45, ray=0.35, halo=7.0,
       knot_dL=-24, rim_dL=-46, smooth=0.28),
    _M("cg_dub_satter", "Дуб Саттер 369 SWA", "cg_satter", "#7f4e32", (-0.12, -0.11),
       (41, "0.715,0.86,0.73,0.90", False), (39, "0.82,0.72,0.868,0.89", False),
       ["«Дуб Саттер 369 SWA» Монако p.41 / p.42"],
       dark_dL=20, light_dL=12, grain=3.8, tone=3.4, fibre=1.0, streak=0.8, pore=0.45, ray=0.3, halo=6.0,
       knot_dL=-42, rim_dL=-56, olive=0.7, olive_col="#5a5040", smooth=0.30,
       # p.39 close-up: olive-brown / near-black knot cores with rings and radial checks, soft edge, lighter rim
       knot_style=dict(core="#3e3629", pith="#191512", check="#110f0c", rim="#8e6f55", rim_k=0.45, pin="#2f2a21",
                       ring_mm=1.6)),
    _M("cg_dub_yukon", "Дуб Юкон 358 SWN", "cg_yukon", "#8d8887", (-0.02, 0.0),
       (93, "0.69,0.86,0.74,0.9", True), (88, "0.79,0.30,0.86,0.40", True),
       ["«Дуб Юкон 358 SWN» Гранде p.93 (photos p.87-90)"],
       dark_dL=22, light_dL=16, grain=2.6, tone=3.4, fibre=1.3, streak=0.8, pore=0.35, ray=0.25, halo=5.0,
       wash=0.4, wash_col="#b9b6b3", knot_dL=-24, rim_dL=-38, saw_dL=-12, smooth=0.26),
]


# ------------------------------------------------------------------------------------------------ maps
def structure(mat, cache):
    key = mat["pattern"]
    if key not in cache:
        cache[key] = extras(key, eco.wood_structure(key))
    return cache[key]


def albedo_linear(mat, st):
    """eco_oak's albedo (ground, pores, rays, streaks, knots, checks) + joints, saw marks and the grey wash;
    the mean in linear light is solved to mat["color"] again at the end."""
    col = hex_to_linear(mat["color"])
    fin = dict(mat, pore_col=mat["pore_col"], ray_col=mat["ray_col"])
    if mat.get("knot_style"):
        fin["knot"] = None                                     # painted below (textured knots)
    out = eco.albedo_linear(fin, st) / col                     # relative to the mean
    ratio = lambda hx: hex_to_linear(hx) / col

    def over(o, alpha, hx):
        a = np.clip(alpha, 0.0, 1.0)[..., None]
        return o * (1 - a) + a * ratio(hx)

    if mat.get("wash"):
        a = mat["wash"] * st["wash"]
        out = out * (1 - a[..., None]) + a[..., None] * ratio(mat["wash_col"]) * np.sqrt(out)
    if mat.get("olive") and "olive" in st:
        out = over(out, mat["olive"] * st["olive"], mat["olive_col"])
    if st["saw"].any():
        out = out * (1 - np.clip(st["saw"], 0, 1)[..., None] * (1 - ratio(mat["saw"])))
    if st["joint"].any():
        out = over(out, st["joint"], mat["joint"])
    if mat.get("knot_style"):
        out = paint_knots(out, st, mat, ratio)
    base = col / out.reshape(-1, 3).mean(0, dtype=np.float64)
    for _ in range(4):
        a = np.clip(out * base, 0, 1)
        base *= col / a.reshape(-1, 3).mean(0, dtype=np.float64)
    return np.clip(out * base, 0, 1)


def paint_knots(out, st, mat, ratio):
    """Textured knots (relative albedo `out`): for each knot of st["knot_list"] an ellipse fitted to its core
    (second moments), an olive-brown core darkening to a near-black pith with growth rings, 2-4 radial checks, a
    soft edge and a lighter rim; the pin clusters as soft dark olive specks."""
    ks = mat["knot_style"]
    h, w = st["knot"].shape
    rng = np.random.default_rng(PATTERNS[mat["pattern"]]["seed"] + 123)
    pins = np.clip(st["knot"] - st["knot_big"], 0, 1)
    if pins.any():
        a = mf.blur(pins, 0.7, 0.7)[..., None]
        out = out * (1 - 0.85 * a) + 0.85 * a * ratio(ks["pin"])
    c_core, c_pith, c_chk, c_rim = (ratio(ks[k]) for k in ("core", "pith", "check", "rim"))
    for xc, yc, dia in st.get("knot_list", []):
        rr = np.arange(int(yc) - 70, int(yc) + 71)
        cc = np.arange(int(xc) - 170, int(xc) + 171)
        ix = np.ix_(rr % h, cc % w)
        k0 = st["knot_big"][ix]
        dy0 = (rr + 0.5 - yc)[:, None]
        dx0 = (cc + 0.5 - xc)[None, :]
        # ellipse of this knot only (a neighbour may share the window): moments within 1.5 x the last estimate
        mx = my = 0.0
        ax, ay = 0.9 * dia * PX, 0.35 * dia * PX
        for _ in range(3):
            sel = np.hypot((dx0 - mx) / ax, (dy0 - my) / ay) < 1.5
            k = k0 * sel
            m = k.sum()
            if m < 4:
                break
            my, mx = float((k * dy0).sum() / m), float((k * dx0).sum() / m)
            ax = 2 * math.sqrt(float((k * (dx0 - mx) ** 2).sum() / m)) + 0.5
            ay = 2 * math.sqrt(float((k * (dy0 - my) ** 2).sum() / m)) + 0.5
        if m < 4:
            continue
        dy, dx = dy0 - my, dx0 - mx
        u, v = dx / ax, dy / ay
        th = np.arctan2(v, u)
        ph = rng.uniform(0, 2 * np.pi, 3)
        rn = np.hypot(u, v) / (1 + 0.07 * np.cos(2 * th + ph[0]) + 0.05 * np.cos(3 * th + ph[1])
                               + 0.03 * np.cos(5 * th + ph[2]))
        core = fk.smoothstep(1.08, 0.72, rn)                                   # soft edge
        n_r = max(3.0, ay * MM / ks["ring_mm"])
        wob = sum(rng.uniform(0.03, 0.12) / j * np.cos(j * th + rng.uniform(0, 2 * np.pi)) for j in range(2, 9))
        wob = wob + 0.35 * gauss_noise(rng, rn.shape, 3.0, 3.0) * fk.smoothstep(0.1, 0.5, rn)
        rings = 0.5 + 0.5 * np.cos(2 * np.pi * (rn * n_r + wob))
        t = np.clip(0.15 + 0.6 * fk.smoothstep(0.0, 0.95, rn) + 0.22 * (rings - 0.5)
                    + 0.12 * gauss_noise(rng, rn.shape, 8.0, 8.0), 0, 1)[..., None]
        col = c_pith * (1 - t) + c_core * t                                     # pith dark, rings, olive outwards
        chk = np.zeros_like(rn)
        for _ in range(int(rng.integers(2, 5))):
            ang = rng.uniform(0, 2 * np.pi)
            reach = rng.uniform(0.55, 1.0)
            d = np.abs(np.angle(np.exp(1j * (th - ang)))) * np.hypot(u * ax, v * ay)   # px from the ray
            wd = 0.4 + 1.1 * np.clip(rn / reach, 0, 1)                               # widening outwards
            chk = np.maximum(chk, np.clip(wd - d, 0, 1) * fk.smoothstep(reach, reach * 0.8, rn)
                             * fk.smoothstep(0.05, 0.2, rn))
        band = np.exp(-((rn - 1.08) / 0.16) ** 2) * (1 - core)
        o = out[ix]
        o = o * (1 - ks["rim_k"] * band[..., None]) + ks["rim_k"] * band[..., None] * c_rim
        o = o * (1 - core[..., None]) + core[..., None] * col
        a = (0.9 * chk * core)[..., None]
        out[ix] = o * (1 - a) + a * c_chk
    return out


def normal_map(mat, st):
    rel = st["relief"]
    hgt = (-rel["pores"] * st["pores"] - rel["checks"] * st["check"] - rel["rays"] * st["rays"]
           - rel["rim"] * st["rim"] - rel["late"] * st["late"] + rel["fibre"] * 0.25 * st["fibre"]
           - 1.5 * st["joint"] - 0.6 * st["saw"])
    hgt = mf.box_down(hgt, ALBEDO[0] // NORMAL[0])
    gx = (np.roll(hgt, -1, 1) - np.roll(hgt, 1, 1)) / 2
    gr = (np.roll(hgt, -1, 0) - np.roll(hgt, 1, 0)) / 2
    slope = np.sqrt(gx ** 2 + gr ** 2)
    k = math.tan(math.radians(rel["tilt_deg"])) / max(1e-9, np.sqrt((slope ** 2).mean()))
    n = np.stack([-gx * k, gr * k, np.ones_like(gx)], -1)          # OpenGL: +Y (green) = up = -row
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return np.round((n * 0.5 + 0.5) * 255).astype(np.uint8)


def folder(mat):
    return EXT / "Materials" / mat["material"]


def write_material(mat, st, alb):
    mid = mat["material"]
    f = folder(mat)
    f.mkdir(parents=True, exist_ok=True)
    rgb = np.round(linear_to_srgb(alb) * 255).astype(np.uint8)
    Image.fromarray(rgb).save(f / f"{mid}_albedo.jpg", quality=90, subsampling=0, optimize=True)
    Image.fromarray(normal_map(mat, st)).save(f / f"{mid}_normal.jpg", quality=92, subsampling=0, optimize=True)
    Image.fromarray(eco.mask_map(mat, st)).save(f / f"{mid}_mask.png", optimize=True)


def read_albedo(mat):
    path = folder(mat) / f"{mat['material']}_albedo.jpg"
    return srgb_to_linear(np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255)


def entry(mat):
    mid = mat["material"]
    return {"id": mid, "name": mat["name"], "category": "casegoods", "source": SOURCE, "neutral": False,
            "metersPerTile": list(TILE_M), "maxSize": ALBEDO[0], "folder": f"Materials/{mid}",
            "textures": {"albedo": f"{mid}_albedo.jpg", "normal": f"{mid}_normal.jpg", "mask": f"{mid}_mask.png"}}


def write_entries(merge=True):
    done = [m for m in MATERIALS if (folder(m) / f"{m['material']}_albedo.jpg").exists()]
    ENTRIES.parent.mkdir(parents=True, exist_ok=True)
    ENTRIES.write_text(json.dumps([entry(m) for m in done], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("entries", ENTRIES.relative_to(ROOT), len(done))
    if merge:
        merge_entries.merge([str(ENTRIES)])


# ------------------------------------------------------------------------------------------------ swatches, sheet
def _catpage():
    if str(GEN) not in sys.path:
        sys.path.insert(0, str(GEN))
    import catpage                     # noqa: E402  (PyMuPDF)
    import pymupdf                     # noqa: E402
    return catpage, pymupdf.open(catpage.PDF)


def crop(doc, catpage, spec, dpi=300):
    pg, fr, rot = spec
    page = doc[pg - 1]
    im = catpage.render(page, dpi, catpage.frac_rect(page, fr))
    return im.transpose(Image.Transpose.ROTATE_90) if rot else im


def lin_mean(lin, trim=0.05):
    """Linear mean without the extreme `trim` shares by luminance (text specks, the crop's frame)."""
    a = lin.reshape(-1, 3)
    o = np.argsort(a @ [0.2126, 0.7152, 0.0722])
    k = len(o)
    return a[o[int(k * trim):max(int(k * (1 - trim)), int(k * trim) + 1)]].mean(0)


def detail(lin, sig):
    """L* std of the detail finer than ~sig px, and the a*, b* slopes against L* of that detail."""
    lab = linear_to_lab(lin)
    sm = np.stack([mf.blur(lab[..., c], sig, sig) for c in range(3)], -1)
    d = (lab - sm)[3:-3, 3:-3].reshape(-1, 3)
    L = d[:, 0]
    return float(L.std()), float((L * d[:, 1]).sum() / (L * L).sum()), float((L * d[:, 2]).sum() / (L * L).sum())


def de76(a, b):
    return float(np.linalg.norm(linear_to_lab(a) - linear_to_lab(b)))


SWATCH_MM = 400.0          # assumed width of the decor a catalogue swatch shows (knots ~15 mm = 1/25 of it)


def analyze(mats):
    catpage, doc = _catpage()
    for m in mats:
        lin = srgb_to_linear(np.asarray(crop(doc, catpage, m["swatch"]), dtype=np.float64) / 255)
        sd, sa, sb = detail(lin, 6)
        print("%-15s swatch p%d %s  %s  L* %.1f  detail std L* %.2f  slopes a*/L* %.2f b*/L* %.2f" % (
            m["id"], m["swatch"][0], m["swatch"][1], linear_to_hex(lin_mean(lin)), linear_to_lab(lin_mean(lin))[0],
            sd, sa, sb))


def texture_as_swatch(alb, sw_size, rot, x0=300, y0=200):
    """The texture over SWATCH_MM along the grain, resampled to the swatch's pixel size (grain horizontal)."""
    sw_w, sw_h = sw_size if not rot else (sw_size[1], sw_size[0])
    wmm = SWATCH_MM
    hmm = wmm * sw_h / sw_w
    reg = alb[y0:y0 + int(hmm * PX), x0:x0 + int(wmm * PX)]
    img = Image.fromarray(np.round(linear_to_srgb(reg) * 255).astype(np.uint8)).resize((sw_w, sw_h), Image.BOX)
    return img.transpose(Image.Transpose.ROTATE_90) if rot else img


def _font(size):
    from PIL import ImageFont
    for f in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial Unicode.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def sheet(mats, albs, out):
    catpage, doc = _catpage()
    f1, f2 = _font(15), _font(12)
    H = 230
    rows, table = [], []
    for m in mats:
        alb = albs[m["id"]]
        sw = crop(doc, catpage, m["swatch"])
        ph = crop(doc, catpage, m["photo"], 200)
        sw_lin = srgb_to_linear(np.asarray(sw, dtype=np.float64) / 255)
        tex_sw = texture_as_swatch(alb, sw.size, m["swatch"][2])
        tx_lin = srgb_to_linear(np.asarray(tex_sw, dtype=np.float64) / 255)
        s_mean, t_mean = lin_mean(sw_lin), alb.reshape(-1, 3).mean(0)
        de = de76(s_mean, t_mean)
        sd, td = detail(sw_lin, 6)[0], detail(tx_lin, 6)[0]
        table.append((m["id"], linear_to_hex(s_mean), linear_to_hex(t_mean), de, sd, td))
        z = lambda im: im.resize((max(1, round(im.width * H / im.height)), H), Image.LANCZOS)
        a, b, c = z(sw), z(ph), z(tex_sw)
        to8 = lambda x: Image.fromarray(np.round(linear_to_srgb(x) * 255).astype(np.uint8))
        d = to8(alb[100:100 + 512, 200:200 + 1024]).resize((2 * H, H), Image.LANCZOS)      # 1 m x 0.5 m
        tile = to8(alb).resize((2 * H, H), Image.BOX)
        rep = Image.new("RGB", (4 * H, 2 * H))
        for i in range(2):
            for j in range(2):
                rep.paste(tile, (i * 2 * H, j * H))
        rep = rep.resize((2 * H, H), Image.LANCZOS)                                         # 4 m x 2 m
        parts = [a, b, c, d, rep]
        row = Image.new("RGB", (sum(p.width for p in parts) + 12 * len(parts), H + 34), "white")
        x = 0
        for p in parts:
            row.paste(p, (x, 34))
            x += p.width + 12
        dr = ImageDraw.Draw(row)
        dr.text((2, 2), "%s  «%s»   swatch p%d %s   texture %s   dE76 %.2f   detail L* std swatch %.1f / texture %.1f"
                % (m["id"], m["name"], m["swatch"][0], linear_to_hex(s_mean), linear_to_hex(t_mean), de, sd, td),
                fill="black", font=f1)
        dr.text((2, 18), "(a) swatch p%d %s  (b) photo p%d  (c) texture as the swatch (%d mm wide)  (d) 1.0 x 0.5 m"
                "  (e) 2x2 tiles = 4 x 2 m" % (m["swatch"][0], m["swatch"][1], m["photo"][0], SWATCH_MM),
                fill=(70, 70, 70), font=f2)
        rows.append(row)
    W = max(r.width for r in rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (W, sum(r.height + 10 for r in rows)), "white")
    y = 0
    for r in rows:
        img.paste(r, (0, y))
        y += r.height + 10
    img.save(out)
    print("sheet", out.relative_to(ROOT))
    print("%-15s %-8s %-8s %6s %8s %8s" % ("id", "swatch", "texture", "dE76", "sw std", "tex std"))
    for t in table:
        print("%-15s %-8s %-8s %6.2f %8.2f %8.2f" % t)
    return table


# ------------------------------------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--no-write", action="store_true", help="do not generate: use the written maps")
    ap.add_argument("--no-merge", action="store_true")
    ap.add_argument("--sheet", action="store_true", help="write the check sheet (PyMuPDF)")
    ap.add_argument("--analyze", action="store_true", help="swatch colours / detail / slopes")
    a = ap.parse_args(argv)
    mats = [m for m in MATERIALS if not a.ids or m["id"] in a.ids]
    if a.ids and len(mats) != len(a.ids):
        sys.exit("unknown id: " + ", ".join(set(a.ids) - {m["id"] for m in mats}))
    if a.analyze:
        analyze(mats)
        return
    cache, albs = {}, {}
    for m in mats:
        if not a.no_write:
            st = structure(m, cache)
            write_material(m, st, albedo_linear(m, st))
            print("material", m["id"])
        albs[m["id"]] = read_albedo(m).astype(np.float32)
    if not a.no_write:
        write_entries(merge=not a.no_merge)
    if a.sheet:
        sheet(mats, albs, SHEET)


if __name__ == "__main__":
    main()
