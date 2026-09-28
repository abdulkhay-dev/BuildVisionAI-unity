#!/usr/bin/env python3
"""Shared machinery of the door finish families of waves 2+ (crosscut, euro_oak, veneer, fine_line, ...).

A family module (tools/doors/textures/<family>.py) declares a FAMILY dict and calls `finish_kit.main(FAMILY)`:

    FAMILY = dict(id="crosscut", line="ЭкоШпон", module="crosscut.py", suffix="ЭкоШпон",
                  patterns={"crosscut": builder}, finishes=[...], refs={...})

    python3 tools/doors/textures/<family>.py                    # textures + entries + Finishes/<family>.json + merge
    python3 tools/doors/textures/<family>.py --compare          # + tools/doors/.cache/finishes_<family>.png
    python3 tools/doors/textures/<family>.py --no-write --compare [ids]   # check sheet only
    python3 tools/doors/textures/<family>.py --fit [ids]        # suggest `comb` / `tone` from the photos
    python3 tools/doors/textures/<family>.py --analyze [ids]    # photo mean colour and streak hue slopes

It builds on wave 1's generator (make_finishes.py: colour maths, periodic noise, laminations, lines, photo
statistics) and adds what the other films and veneers need: sub-layered laminations (oak growth rings: earlywood,
transition, latewood), pore dashes, straight crosshatch lines and extra coloured line layers.

A pattern builder returns a structure dict (albedo resolution, all fields periodic on the 2.0 x 1.0 m tile):
    fine, broad        unit-std tone fields (fine lines, broad bands), coloured by `comb` / `tone` (L* units)
    <layer>            0..1 opacity of a coloured layer - dark, light, pore, fleck, xlight, xdark (LAYERS)
    height             relief (arbitrary units): embossing / open pores; normal map rms tilt = relief.tilt_deg
    rough              unit-std field that lowers smoothness where it is high (pores, embossing)
A finish colours it (albedo_linear) exactly like wave 1 - ground from `comb` x fine + `tone` x broad, towards the
`dark` / `light` colours - then every layer multiplies in its colour (fin[<layer>], default dark or light) at
strength fin[<layer>_k] (default 1); finally the base is solved per channel so the texture's mean in linear light is
exactly `color`.

Needs numpy + Pillow; the photos of tools/doors/.cache (catalog_index.py) only for --compare / --fit / --analyze.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import make_finishes as mf          # noqa: E402  (wave 1: colour, noise, laminations, photo statistics)
import merge_entries                # noqa: E402

ROOT = mf.ROOT
EXT = mf.EXT
CACHE = mf.CACHE
ALBEDO, NORMAL, MASK, MM, TILE_M = mf.ALBEDO, mf.NORMAL, mf.MASK, mf.MM, mf.TILE_M
FINISHES_DIR = ROOT / "Assets" / "House4696" / "Resources" / "Doors" / "Finishes"
ENTRIES_DIR = HERE / "entries"

# coloured layers over the ground: name -> the finish key of its default colour
LAYERS = {"dark": "dark", "light": "light", "pore": "dark", "fleck": "light", "xlight": "light", "xdark": "dark"}

hex_to_linear, linear_to_hex = mf.hex_to_linear, mf.linear_to_hex
linear_to_srgb, srgb_to_linear, linear_to_lab = mf.linear_to_srgb, mf.srgb_to_linear, mf.linear_to_lab
gauss_noise, noise_1d, warp_rows, highpass_across = mf.gauss_noise, mf.noise_1d, mf.warp_rows, mf.highpass_across


# ------------------------------------------------------------------------------------------------ building blocks
def warp(rng, octaves, px):
    """Cross-grain displacement (px) shared by the fields: octaves of (amplitude mm, correlation along, across mm)."""
    w, h = ALBEDO
    disp = np.zeros((h, w))
    for amp, along, across in octaves:
        if amp > 0:
            disp += gauss_noise(rng, (h, w), along * px, across * px) * (amp * px)
    return disp


def layer_edges(rng, thickness, px, rho=0.0):
    """Layer thicknesses (px) across one tile: log-normal (median mm, log-sigma), AR(1)-correlated log-thickness
    (rho > 0: neighbours alike, e.g. growth rings of a year group), scaled to exactly one tile."""
    h = ALBEDO[1]
    med, sig = thickness
    th, total, z = [], 0.0, rng.standard_normal()
    while total < h / px:
        z = rho * z + math.sqrt(1 - rho * rho) * rng.standard_normal()
        t = min(12.0, max(0.2, med * math.exp(sig * z)))
        th.append(t)
        total += t
    th = np.array(th) * (h / total)
    return th


def layered(th, tone, disp):
    """Box-filtered (exact pixel coverage) laminations across the grain: layer i of thickness th[i] px has the tone
    tone[i, x] (tone: (k, w) or (k,)); every row is displaced by disp (the layers follow the warp). Periodic."""
    w, h = ALBEDO
    tone = np.asarray(tone, dtype=np.float64)
    if tone.ndim == 1:
        tone = np.repeat(tone[:, None], w, 1)
    edges = np.concatenate([[0.0], np.cumsum(th)])
    cum = np.concatenate([np.zeros((1, w)), np.cumsum(tone * th[:, None], 0)], 0)
    rows = np.arange(h, dtype=np.float64)
    out = np.empty((h, w))
    for x in range(w):
        y = rows - disp[:, x]
        out[:, x] = (mf.periodic_integral(y + 0.5, cum[:, x], edges) -
                     mf.periodic_integral(y - 0.5, cum[:, x], edges))
    return out


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def dashes(rng, disp, px, along, duty, soft=0.35, across=0.35):
    """Dash field 0..1 following the grain: noise correlated `along` mm along the grain and ~`across` mm across,
    thresholded so that `duty` of it is on (pore tracks, broken lines)."""
    w, h = ALBEDO
    n = warp_rows(gauss_noise(rng, (h, w), along * px, max(0.3, across * px)), disp)
    thr = float(np.quantile(n, 1 - duty))
    return smoothstep(thr - soft, thr + soft, n)


def straight_lines(rng, pitch, width, px, axis, jitter_len, strength, share_on=0.7, soft=0.5,
                   wander=0.0, wander_len=40.0):
    """Straight thin lines of a crosshatch, drawn with exact coverage.
    axis=1: lines across the grain (constant x, image columns), their pattern along y; axis=0: along the grain.
    pitch / width: (median mm, log-sigma); each line's opacity comes and goes along it (noise correlated jitter_len
    mm, `share_on` of it visible, `soft` the edge of the threshold), times `strength` (0..1 per line, drawn from the
    given range). wander: max sideways drift (mm) along the line over wander_len mm. Returns (h, w) opacity."""
    w, h = ALBEDO
    span = w if axis == 1 else h            # positions along this axis
    length = h if axis == 1 else w          # the lines' own direction
    med, sig = pitch
    pos, total = [], 0.0
    while total < span / px:
        total += min(4 * med, max(0.4 * med, med * math.exp(sig * rng.standard_normal())))
        pos.append(total)
    pos = np.array(pos) * (span / total)
    n = len(pos)
    wmed, wsig = width
    widths = np.clip(wmed * np.exp(wsig * rng.standard_normal(n)), 0.25, 3.0) * px
    amp = rng.uniform(*strength, n)
    env = np.empty((n, length))
    for i in range(n):
        env[i] = noise_1d(rng, length, jitter_len * px)
    thr = np.quantile(env, 1 - share_on)
    env = smoothstep(thr - soft, thr + soft, env) * amp[:, None]
    shift = np.zeros((n, length))
    if wander > 0:
        for i in range(n):
            shift[i] = noise_1d(rng, length, wander_len * px) * (wander * px / 2.5)
    out = np.zeros((length, span))            # rows = along the line, cols = position of the line
    s = np.arange(length)
    for i in range(n):
        c = pos[i] + shift[i]
        hw = widths[i] / 2
        c0 = int(math.floor(c.min() - hw - 0.5))
        c1 = int(math.ceil(c.max() + hw + 0.5))
        cols = np.arange(c0, c1 + 1)[None, :]
        cov = np.clip(np.minimum(c[:, None] + hw, cols + 0.5) - np.maximum(c[:, None] - hw, cols - 0.5), 0.0, 1.0)
        a = np.clip(cov * env[i][:, None], 0.0, 0.97)
        idx = np.ix_(s, cols[0] % span)
        out[idx] = 1 - (1 - out[idx]) * (1 - a)
    return out if axis == 1 else out.T


def unit(a):
    a = a - a.mean()
    return a / max(1e-12, a.std())


def oak_structure(p, scale=1.0, seed=None):
    """Straight-grain (rift / quarter) oak, real veneer or its print. Lengths in mm; keys of p:
      warp          octaves (amplitude, along, across) of the cross-grain wander of everything
      ring          growth ring width (median, log-sigma), ring_rho = likeness of neighbouring rings
      early         earlywood share of a ring (mean, sd); its pores sit there, the transition follows (trans)
      ring_tone     tones of earlywood, transition, latewood; ring_var = ring-to-ring spread of the latewood tone;
                    drift / drift_len = share of each layer's tone that changes along the grain, over that length
      hp            the rings carry the fine lines only: variation across wider than ~hp mm is left to `broad`
      pores         dict(len, duty, alpha, late) - dashes along the earlywood (len mm, share on, opacity) and the
                    fainter share `late` of them in the latewood
      rays          wave-1 line spec of the ray flecks (short light dashes, slightly slanted); None = none
      dark / light  wave-1 line specs of long darker / lighter streaks; None = none
      bands, cluster, cluster_share, band_warp   broad tone (sigma across, along), flame-like extra wander
      fibre, fibre_share                         faint fibre noise (sigma across, along) in the fine tone
      relief        dict(pore, ring, fibre, tilt_deg): open / embossed pores, earlywood dip, fibre
    Returns the kit's structure fields (fine, broad, pore, fleck, dark, light, height, rough)."""
    rng = np.random.default_rng(p["seed"] if seed is None else seed)
    px = scale / MM
    w, h = ALBEDO
    disp = warp(rng, p["warp"], px)
    rings = layer_edges(rng, p["ring"], px, p.get("ring_rho", 0.0))
    n = len(rings)
    e = np.clip(p["early"][0] + p["early"][1] * rng.standard_normal(n), 0.12, 0.6)
    tr = np.clip(p.get("trans", 0.2) * (1 + 0.3 * rng.standard_normal(n)), 0.05, 0.4)
    lw = np.clip(1 - e - tr, 0.1, None)
    th = np.stack([rings * e, rings * tr, rings * lw], 1).reshape(-1)
    th *= h / th.sum()
    te, tt, tl = p["ring_tone"]
    var = p.get("ring_var", 0.4)
    ring_amp = np.exp(0.3 * rng.standard_normal(n))           # some rings are marked more strongly
    late = tl + var * rng.standard_normal(n)
    base = np.stack([te * ring_amp, tt * ring_amp, late], 1).reshape(-1)
    k = len(base)
    m = p.get("drift", 0.4)
    tone = base[:, None] + m * base.std() * gauss_noise(rng, (k, w), p["drift_len"] * px, 0.6)
    ringf = layered(th, tone, disp)
    ringf = highpass_across(ringf, p.get("hp", 4.0) * px)
    early = layered(th, np.stack([np.ones(n), np.zeros(n), np.zeros(n)], 1).reshape(-1), disp)
    pr = p["pores"]
    d1 = dashes(rng, disp, px, pr["len"], pr["duty"])
    d2 = dashes(rng, disp, px, pr["len"] * 0.6, pr["duty"] * 0.5)
    pore = np.clip(pr["alpha"] * (early * d1 + pr.get("late", 0.15) * (1 - early) * d2), 0, 1)
    env_table = noise_1d(rng, 1 << 18, p.get("fade_len", 20.0) * px)
    out = {}
    for key in ("rays", "dark", "light"):
        acc = np.zeros((h, w))
        if p.get(key):
            mf.draw_lines(rng, acc, p[key], disp, env_table, px)
        out[key] = 1 - np.exp(-acc)
    amp, along, across = p["band_warp"]
    bdisp = disp + gauss_noise(rng, (h, w), along * px, across * px) * (amp * px)
    bands = warp_rows(gauss_noise(rng, (h, w), p["bands"][1] * px, p["bands"][0] * px), bdisp)
    cluster = warp_rows(gauss_noise(rng, (h, w), p["cluster"][1] * px, p["cluster"][0] * px), bdisp)
    fibre = warp_rows(gauss_noise(rng, (h, w), p["fibre"][1] * px, p["fibre"][0] * px), disp)
    cs, fs = p["cluster_share"], p["fibre_share"]
    broad = unit(math.sqrt(1 - cs) * bands + math.sqrt(cs) * cluster)
    fine = unit(math.sqrt(1 - fs) * unit(ringf) + math.sqrt(fs) * fibre)
    rel = p["relief"]
    height = -rel["pore"] * pore - rel["ring"] * early + rel["fibre"] * 0.25 * fibre
    return dict(fine=fine, broad=broad, pore=pore, fleck=out["rays"], dark=out["dark"], light=out["light"],
                height=height, rough=pore, relief=rel, early=early)


def wave1_structure(name, params, scale=1.0, seed=None):
    """make_finishes.structure() of a wave-1-style pattern (the PATTERNS keys of make_finishes: warp, comb, dark,
    light, bands, cluster, fibre, relief), plus the relief / roughness fields of this kit (wave 1's embossing)."""
    mf.PATTERNS[name] = params                  # in memory only: make_finishes.py itself is not touched
    st = mf.structure(name, scale, seed)
    rel = st["relief"]
    st["height"] = -rel["comb"] * 0.25 * st["comb"] - rel["groove"] * st["dark"] + rel["fibre"] * 0.25 * st["fibre"]
    st["rough"] = st["dark"]
    return st


# ------------------------------------------------------------------------------------------------ maps
def albedo_linear(fin, st):
    """Linear-RGB albedo (h, w, 3): wave 1's ground (make_finishes.albedo_linear) + coloured layers, mean = color."""
    col = hex_to_linear(fin["color"])
    rd = np.clip(hex_to_linear(fin["dark"]) / col, 0.03, 1.0)
    rl = np.clip(hex_to_linear(fin["light"]) / col, 1.0, 30.0)
    Lc = linear_to_lab(col)[0]
    dLd = max(1e-3, Lc - linear_to_lab(col * rd)[0])
    dLl = max(1e-3, linear_to_lab(col * rl)[0] - Lc)
    t = (fin["comb"] * st["fine"] + fin["tone"] * st["broad"])[..., None]
    out = np.where(t < 0, np.exp(-t / dLd * np.log(rd)), np.exp(t / dLl * np.log(rl)))
    for name, key in LAYERS.items():
        if name not in st:
            continue
        k = fin.get(name + "_k", 1.0)
        if k <= 0:
            continue
        r = np.clip(hex_to_linear(fin.get(name, fin[key])) / col, 0.02, 30.0)
        a = np.clip(k * st[name], 0.0, 1.0)[..., None]
        out = out * (1 + a * (r - 1))
    base = col / out.reshape(-1, 3).mean(0, dtype=np.float64)
    for _ in range(4):                          # clipping at 1 (white films) shifts the mean: re-solve
        a = np.clip(out * base, 0, 1)
        base *= col / a.reshape(-1, 3).mean(0, dtype=np.float64)
    return np.clip(out * base, 0, 1)


def normal_map(fin, st):
    """OpenGL tangent-space normals of st["height"], rms tilt fin["tilt"] or relief.tilt_deg (degrees)."""
    hgt = mf.box_down(st["height"], ALBEDO[0] // NORMAL[0])
    gx = (np.roll(hgt, -1, 1) - np.roll(hgt, 1, 1)) / 2
    gr = (np.roll(hgt, -1, 0) - np.roll(hgt, 1, 0)) / 2
    slope = np.sqrt(gx ** 2 + gr ** 2)
    tilt = fin.get("tilt", st["relief"]["tilt_deg"])
    k = math.tan(math.radians(tilt)) / max(1e-9, np.sqrt((slope ** 2).mean()))
    n = np.stack([-gx * k, gr * k, np.ones_like(gx)], -1)          # +Y (green) = up = -row
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return np.round((n * 0.5 + 0.5) * 255).astype(np.uint8)


def mask_map(fin, st):
    """R metallic 0, G occlusion 255, B 0, A smoothness: fin["smooth"], lower where st["rough"] is high."""
    f = ALBEDO[0] // MASK[0]
    s0 = fin["smooth"] * 255
    if "rough" in st:
        d = unit(mf.box_down(st["rough"], f))
        sm = np.clip(s0 - fin.get("rough_k", 4.0) * d, s0 - 15, s0 + 10)
    else:
        sm = np.full((MASK[1], MASK[0]), s0)
    m = np.zeros((MASK[1], MASK[0], 4), np.uint8)
    m[..., 1] = 255
    m[..., 3] = np.round(np.clip(sm, 0, 255)).astype(np.uint8)
    return m


def write_finish(fin, st, alb):
    mid = fin["material"]
    folder = EXT / "Materials" / mid
    folder.mkdir(parents=True, exist_ok=True)
    rgb = np.round(linear_to_srgb(alb) * 255).astype(np.uint8)
    Image.fromarray(rgb).save(folder / f"{mid}_albedo.jpg", quality=90, subsampling=0, optimize=True)
    Image.fromarray(normal_map(fin, st)).save(folder / f"{mid}_normal.jpg", quality=92, subsampling=0, optimize=True)
    Image.fromarray(mask_map(fin, st)).save(folder / f"{mid}_mask.png", optimize=True)


def read_albedo(fin):
    path = EXT / "Materials" / fin["material"] / (fin["material"] + "_albedo.jpg")
    return srgb_to_linear(np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255)


def manifest_entry(family, fin):
    mid = fin["material"]
    return {"id": mid, "name": f"{fin['name']} ({family['suffix']})", "category": "door",
            "source": "procedural:tools/doors/textures/" + family["module"], "neutral": False,
            "metersPerTile": list(TILE_M), "maxSize": ALBEDO[0], "folder": f"Materials/{mid}",
            "textures": {"albedo": f"{mid}_albedo.jpg", "normal": f"{mid}_normal.jpg", "mask": f"{mid}_mask.png"}}


def write_family_files(family, fins, means):
    """entries/<family>.json (+ merge into external.json) and Resources/Doors/Finishes/<family>.json. Finishes not
    regenerated this run keep their previous entry (their colour is read back from the written albedo)."""
    ENTRIES_DIR.mkdir(parents=True, exist_ok=True)
    FINISHES_DIR.mkdir(parents=True, exist_ok=True)
    all_fins = family["finishes"]
    for fin in all_fins:
        if fin["id"] not in means and (EXT / "Materials" / fin["material"] / (fin["material"] + "_albedo.jpg")).exists():
            means[fin["id"]] = read_albedo(fin).reshape(-1, 3).mean(0)
    done = [f for f in all_fins if f["id"] in means]
    entries = ENTRIES_DIR / f"{family['id']}.json"
    entries.write_text(json.dumps([manifest_entry(family, f) for f in done], ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")
    merge_entries.merge([str(entries)])
    rows = [{"id": f["id"], "name": f["name"], "line": family["line"], "material": f["material"],
             "color": linear_to_hex(means[f["id"]])} for f in done]
    out = FINISHES_DIR / f"{family['id']}.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("entries", entries, "\nfinishes", out)


# ------------------------------------------------------------------------------------------------ photos
def ref_crop(ref):
    """(linear crop with the grain vertical, px per mm) of a REFS entry (file, box[, "rot"])."""
    lin, scale = mf.photo_crop(ref[0], ref[1])
    if len(ref) > 2 and ref[2] == "rot":
        lin = np.transpose(lin, (1, 0, 2))
    return lin, scale


def measure(refs, fin, alb, shown=None):
    """Photo vs texture statistics over the finish's REFS crops (texture: same-size crops at random places)."""
    rng = np.random.default_rng(1)
    pm, wsum, ph, tx = np.zeros(3), 0.0, [], []
    shown = {} if shown is None else shown
    for ref in refs[fin["id"]]:
        fname = ref[0]
        lin, scale = ref_crop(ref)
        if fname not in shown:
            shown[fname] = mf.as_photo(alb, fname)
        tex = shown[fname]
        ch, cw = lin.shape[:2]
        ts = []
        for _ in range(8):
            y0 = rng.integers(0, max(1, tex.shape[0] - ch))
            x0 = rng.integers(0, max(1, tex.shape[1] - cw))
            ts.append(mf.lab_stats(tex[y0:y0 + ch, x0:x0 + cw], scale))
        wgt = math.sqrt(ch * cw)
        ps = mf.lab_stats(lin, scale)
        pm += wgt * ps["mean"]
        wsum += wgt
        ph.append([ps[k] for k in mf.STATS])
        tx.append([np.mean([t[k] for t in ts]) for k in mf.STATS])
    pm /= wsum
    tm = alb.reshape(-1, 3).mean(0, dtype=np.float64)
    plab, tlab = linear_to_lab(pm), linear_to_lab(tm)
    ph, tx = np.mean(ph, 0), np.mean(tx, 0)
    out = dict(id=fin["id"], photo=pm, tex=tm, plab=plab, tlab=tlab, de=float(np.linalg.norm(plab - tlab)),
               shown=shown)
    for i, k in enumerate(mf.STATS):
        out["p" + k], out["t" + k] = float(ph[i]), float(tx[i])
    return out


def analyze(refs, fin):
    """Mean photo colour and the hue of its streaks: slopes of a*, b* against L* (fine detail, lighting removed)."""
    labs, pm, wsum = [], np.zeros(3), 0.0
    for ref in refs[fin["id"]]:
        lin, scale = ref_crop(ref)
        lab = linear_to_lab(lin)
        smooth = np.stack([mf.blur(lab[..., c], 12 * scale, 12 * scale) for c in range(3)], -1)
        labs.append((lab - smooth).reshape(-1, 3))
        wgt = math.sqrt(lin.shape[0] * lin.shape[1])
        pm += wgt * lin.reshape(-1, 3).mean(0)
        wsum += wgt
    pm /= wsum
    d = np.concatenate(labs)
    L = d[:, 0]
    sa = float((L * d[:, 1]).sum() / (L * L).sum())
    sb = float((L * d[:, 2]).sum() / (L * L).sum())
    lab = linear_to_lab(pm)

    def at(dl):
        target = lab + np.array([dl, sa * dl, sb * dl])
        return lab_to_hex(target)
    print("analyze %-18s photo %s  L*a*b* %.1f %.1f %.1f  slopes a*/L* %.3f b*/L* %.3f  std L* %.2f  "
          "dark(-12) %s light(+8) %s" % (fin["id"], linear_to_hex(pm), *lab, sa, sb, float(L.std()), at(-12), at(8)))


def lab_to_linear(lab):
    L, a, b = lab
    fy = (L + 16) / 116
    fx, fz = fy + a / 500, fy - b / 200
    d = 6 / 29
    finv = lambda f: f ** 3 if f > d else 3 * d * d * (f - 4 / 29)
    xyz = np.array([finv(fx), finv(fy), finv(fz)]) * mf._WHITE
    return np.linalg.solve(mf._M, xyz)


def lab_to_hex(lab):
    return linear_to_hex(np.clip(lab_to_linear(lab), 0, 1))


def fit(refs, fin, st, rounds=2):
    """Suggests `comb` and `tone` (as make_finishes.fit, over this family's REFS)."""
    f = dict(fin)
    for _ in range(rounds):
        c, t = max(0.3, f["comb"]), max(0.3, f["tone"])
        rows, got = [], []
        for pc, pt in [(c, t), (c * 1.4, t), (c, t * 1.6)]:
            g = dict(f, comb=pc, tone=pt)
            r = measure(refs, g, albedo_linear(g, st))
            rows.append([1.0, pc * pc, pt * pt])
            got.append([r["t" + k] ** 2 for k in mf.STATS])
        coef = np.linalg.solve(np.array(rows), np.array(got))
        target = np.array([r["p" + k] ** 2 for k in mf.STATS])
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
    r = measure(refs, f, albedo_linear(f, st))
    print("fit %-18s comb=%.2f, tone=%.2f   " % (f["id"], f["comb"], f["tone"]) +
          "  ".join("%s %.2f/%.2f" % (k, r["p" + k], r["t" + k]) for k in mf.STATS) + "  dE %.2f" % r["de"])
    return f


# ------------------------------------------------------------------------------------------------ check sheet
def compare(family, fins, albedos, out_path):
    """Prints the photo / texture table and draws the check sheet: per finish (a) the first REFS crop, (b) the
    texture as that photo would show it, (c) the texture 1:1 (1 px/mm), (d) 1:1 zoomed x3 (the pores / hatch)."""
    refs = family["refs"]
    report = [measure(refs, fin, albedos[fin["id"]]) for fin in fins if refs.get(fin["id"])]
    head = ["finish", "photo", "L*", "a*", "b*", "texture", "L*", "a*", "b*", "dE76", "sx ph/tex", "fine ph/tex",
            "band ph/tex"]
    cells = [head] + [[r["id"], linear_to_hex(r["photo"]), *("%.1f" % v for v in r["plab"]), linear_to_hex(r["tex"]),
                       *("%.1f" % v for v in r["tlab"]), "%.2f" % r["de"]] +
                      ["%.2f / %.2f" % (r["p" + k], r["t" + k]) for k in mf.STATS] for r in report]
    widths = [19, 8, 6, 6, 6, 8, 6, 6, 6, 6, 13, 13, 13]
    print("\n".join("".join(c.ljust(wd) if i in (0, 1, 5) else c.rjust(wd - 1) + " " for i, (c, wd) in
                             enumerate(zip(row, widths))) for row in cells))
    if out_path is None:
        return report
    to8 = lambda x: Image.fromarray(np.round(linear_to_srgb(x) * 255).astype(np.uint8))
    tiles = []
    for r in report:
        ref = refs[r["id"]][0]
        lin, scale = ref_crop(ref)
        z = 2 if scale > 0.3 else 4
        ch, cw = min(lin.shape[0], 600 // z), min(lin.shape[1], 220 // z)
        a = to8(lin[:ch, :cw]).resize((cw * z, ch * z), Image.NEAREST)
        b = to8(r["shown"][ref[0]][60:60 + ch, 40:40 + cw]).resize((cw * z, ch * z), Image.NEAREST)
        v = np.transpose(albedos[r["id"]], (1, 0, 2))
        c = to8(v[700:700 + 600, 300:300 + 240])
        dz = to8(v[1000:1000 + 200, 600:600 + 80]).resize((240, 600), Image.NEAREST)
        tile = Image.new("RGB", (a.width + b.width + c.width + dz.width + 40, max(a.height, c.height) + 36), "white")
        x = 0
        for img, gap in ((a, 8), (b, 16), (c, 16), (dz, 0)):
            tile.paste(img, (x, 36))
            x += img.width + gap
        d = ImageDraw.Draw(tile)
        d.text((2, 2), "%s   photo %s  texture %s   dE76 %.2f" % (
            r["id"], linear_to_hex(r["photo"]), linear_to_hex(r["tex"]), r["de"]), fill="black")
        d.text((2, 18), "(a) %s x%d  (b) texture seen the same way  (c) texture 1 px/mm  (d) x3   sx %.1f/%.1f  "
                        "fine %.1f/%.1f" % (ref[0].split("__")[0], z, r["psx"], r["tsx"], r["pfine"], r["tfine"]),
               fill=(60, 60, 60))
        tiles.append(tile)
    cols = 2 if len(tiles) > 2 else 1
    per = math.ceil(len(tiles) / cols)
    groups = [tiles[i * per:(i + 1) * per] for i in range(cols)]
    colw = [max(t.width for t in g) for g in groups if g]
    top = 16 * (len(cells) + 2)
    sheet = Image.new("RGB", (max(sum(colw) + 30 * (cols - 1), 1000),
                              top + max(sum(t.height + 14 for t in g) for g in groups if g)), "white")
    d = ImageDraw.Draw(sheet)
    d.text((4, 4), "%s finishes vs catalogue photos: mean colour in linear light; L* contrast (sx across the grain in "
                   "80 mm, fine = pixel to pixel, band = broad) of the texture downsized like the photo and "
                   "JPEG-compressed with its tables" % family["id"], fill="black")
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
def finish_structure(family, fin, cache):
    key = (fin["pattern"], fin.get("scale", 1.0), fin.get("seed"))
    if key not in cache:
        cache[key] = family["patterns"][fin["pattern"]](scale=key[1], seed=key[2])
    return cache[key]


def main(family, argv=None):
    ap = argparse.ArgumentParser(description="door finishes: " + family["id"])
    ap.add_argument("finishes", nargs="*", help="finish ids (default: all of the family)")
    ap.add_argument("--compare", action="store_true", help="write tools/doors/.cache/finishes_<family>.png")
    ap.add_argument("--no-write", action="store_true", help="do not write textures / entries / Finishes json")
    ap.add_argument("--sheet", default=str(CACHE / f"finishes_{family['id']}.png"))
    ap.add_argument("--fit", action="store_true", help="suggest comb / tone from the photos")
    ap.add_argument("--analyze", action="store_true", help="photo mean colour and streak hue slopes")
    args = ap.parse_args(argv)
    fins = [f for f in family["finishes"] if not args.finishes or f["id"] in args.finishes]
    if args.finishes and len(fins) != len(args.finishes):
        sys.exit("unknown finish: " + ", ".join(set(args.finishes) - {f["id"] for f in fins}))
    if (args.compare or args.fit or args.analyze) and not (CACHE / "photos").is_dir():
        sys.exit("no catalogue photos in %s: run tools/doors/catalog_index.py first" % (CACHE / "photos"))
    if args.analyze:
        for fin in fins:
            analyze(family["refs"], fin)
        return
    structures, albedos, means = {}, {}, {}
    for fin in fins:
        st = finish_structure(family, fin, structures)
        if args.fit:
            fit(family["refs"], fin, st)
            continue
        alb = albedo_linear(fin, st)
        if not args.no_write:
            write_finish(fin, st, alb)
            print("finish", fin["id"], "->", fin["material"])
            alb = read_albedo(fin)                      # compare what Unity gets: the written JPEG
        means[fin["id"]] = alb.reshape(-1, 3).mean(0, dtype=np.float64)
        if args.compare:
            albedos[fin["id"]] = alb.astype(np.float32)
    if args.fit:
        return
    if not args.no_write:
        write_family_files(family, fins, means)
    if args.compare:
        compare(family, fins, albedos, Path(args.sheet))
