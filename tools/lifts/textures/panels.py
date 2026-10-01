#!/usr/bin/env python3
"""Lift textures, family `panels`: car operating panels (COP) and landing call panels (LOP) of the GLZ / NBSL
catalogue (p.17-20, 38), as fitted pictures for the engine's panel boxes.

    python tools/lifts/textures/panels.py [--no-merge] [ids]          # ids like dc1000a, dl300

liftpanel_<id>, metersPerTile [1, 1]: the panel face front-on, from the catalogue's own front-view crop
(tools/lifts/reference/panels/<id>.jpg) cleaned up:
  - the page background around rounded corners is filled from the panel's edge (the box is rectangular);
  - multi-variant crops (DL300 / DL320 single + double, DL500A triangle / round / double) keep the first, single one;
  - the render's lighting (a top-to-bottom gradient over the steel, side shading) is divided out: a masked
    low-frequency blur of the steel's lightness is flattened to its median, so the engine's light does the shading;
  - the steel is set to the finish's colour level (stainless ~#c8c8c8, gold keeps its hue).
Mask: metallic 1 on the steel / gold and the button rims, 0 on the display glass, black glass, LED rings / digits and
printed marks; smoothness 0.6 hairline, 0.9 mirror finish and glass. Normal: a gentle relief from the lightness
(button rims, engraved marks), none on glass. Long side 512 px; the picture keeps the panel's own aspect (see
panels.md for each one's w:h) - the engine box should match it or the buttons turn oval.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lift_kit as K                # noqa: E402

FAMILY = "panels"
SOURCE = "catalogue crop, cleaned: tools/lifts/textures/panels.py"
LONG = 512

# panel id -> (finish, which blob of the crop: (row index, column index) of the variant to keep)
PANELS = {
    "dc1000a": ("stainless-hairline", (0, 0)),
    "dl300": ("stainless-hairline", (0, 0)),
    "dc1000c": ("stainless-hairline", (0, 0)),
    "dl320": ("stainless-hairline", (0, 0)),
    "dc2000a": ("stainless-hairline", (0, 0)),
    "dl400": ("stainless-hairline", (0, 0)),
    "dc2000b": ("titanium-gold-hairline", (0, 0)),
    "dl450": ("titanium-gold-hairline", (0, 0)),
    "dc5000a": ("black-glass", (0, 0)),
    "dl500a": ("black-glass", (0, 0)),
    "dc9000a": ("stainless-hairline", (0, 0)),
    "dl300b": ("stainless-hairline", (0, 0)),
    "dc1200a": ("stainless-hairline", (0, 0)),
    "dc4200a": ("stainless-hairline", (0, 0)),
    "dc1200b": ("stainless-mirror", (0, 0)),
    "dl100a": ("stainless-hairline", (0, 0)),
    "dl100a-double": ("stainless-hairline", (0, 0)),
    "dc1000a-freight": ("stainless-hairline", (0, 0)),
}


def hsv_parts(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    sat = np.where(mx > 1e-6, (mx - mn) / np.maximum(mx, 1e-6), 0)
    L = rgb @ np.array([0.299, 0.587, 0.114])
    return L, sat, mx


def runs(v, gap=3):
    """Index runs where v is True, merging gaps shorter than `gap`."""
    idx = np.flatnonzero(v)
    if len(idx) == 0:
        return []
    out, s, p = [], idx[0], idx[0]
    for i in idx[1:]:
        if i - p > gap:
            out.append((s, p + 1))
            s = i
        p = i
    out.append((s, p + 1))
    return [r for r in out if r[1] - r[0] > 8]


def pick_blob(rgb, which):
    L, sat, _ = hsv_parts(rgb)
    fg = ~((L > 0.92) & (sat < 0.08))
    rr = runs(fg.mean(1) > 0.02, gap=6)
    r0, r1 = rr[min(which[0], len(rr) - 1)]
    cc = runs(fg[r0:r1].mean(0) > 0.02, gap=6)
    c0, c1 = cc[min(which[1], len(cc) - 1)]
    sub = rgb[r0:r1, c0:c1]
    f = fg[r0:r1, c0:c1]
    # trim thin borders of background
    rows = np.flatnonzero(f.mean(1) > 0.3)
    cols = np.flatnonzero(f.mean(0) > 0.3)
    return sub[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1], f[rows[0]:rows[-1] + 1, cols[0]:cols[-1] + 1]


def fill_background(rgb, fg):
    """Replace page-background pixels (rounded corners, gaps) by the nearest panel pixel along the row, then the
    column (corners of a rounded top)."""
    out = rgb.copy()
    valid = fg.copy()
    h, w = valid.shape
    for y in range(h):
        v = np.flatnonzero(valid[y])
        if len(v) == 0 or len(v) == w:
            continue
        xs = np.arange(w)
        j = np.clip(np.searchsorted(v, xs), 0, len(v) - 1)
        jl = np.clip(j - 1, 0, len(v) - 1)
        near = np.where(np.abs(v[jl] - xs) < np.abs(v[j] - xs), v[jl], v[j])
        bad = ~valid[y]
        # sample a few px inside the edge (the edge itself is an anti-aliased rim)
        src = np.clip(near + np.sign(near - xs) * 3, 0, w - 1)
        out[y, bad] = out[y, src[bad]]
        valid[y] = valid[y] | (len(v) > w * 0.3)
    for x in range(w):
        v = np.flatnonzero(valid[:, x])
        if len(v) == 0 or len(v) == h:
            continue
        ys = np.arange(h)
        j = np.clip(np.searchsorted(v, ys), 0, len(v) - 1)
        jl = np.clip(j - 1, 0, len(v) - 1)
        near = np.where(np.abs(v[jl] - ys) < np.abs(v[j] - ys), v[jl], v[j])
        src = np.clip(near + np.sign(near - ys) * 3, 0, h - 1)
        bad = ~valid[:, x]
        out[bad, x] = out[src[bad], x]
    return out


def masked_blur(a, m, sx, sy):
    num = K.blur_edge_xy(a * m, sx, sy)
    den = K.blur_edge_xy(m, sx, sy)
    return num / np.maximum(den, 1e-3)


def build(pid):
    finish, which = PANELS[pid]
    src = np.asarray(Image.open(K.REF / "panels" / f"{pid}.jpg").convert("RGB"), dtype=np.float64) / 255.0
    rgb, fg = pick_blob(src, which)
    rgb = fill_background(rgb, fg)
    h0, w0 = rgb.shape[:2]
    s = LONG / max(h0, w0)
    size = (max(8, round(w0 * s)), max(8, round(h0 * s)))
    rgb = np.clip(K.resize(rgb, size), 0, 1)
    h, w = rgb.shape[:2]
    L, sat, mx = hsv_parts(rgb)
    hue_r = (rgb[..., 0] > rgb[..., 1] * 1.6) & (rgb[..., 0] > 0.35)          # red LED / digits
    hue_b = (rgb[..., 2] > rgb[..., 0] * 1.4) & (rgb[..., 2] > 0.3)           # blue display / ring
    hue_g = (rgb[..., 1] > rgb[..., 0] * 1.25) & (rgb[..., 1] > rgb[..., 2] * 1.1) & (sat > 0.3)
    gold = finish.startswith("titanium-gold")
    glass = finish == "black-glass"
    dark = L < (0.30 if not glass else 0.45)
    led = (hue_r | hue_b | hue_g) & (sat > 0.35)
    if gold:
        led = (hue_r | hue_b) & (sat > 0.45) & ~((rgb[..., 0] > rgb[..., 2] * 1.4) & (rgb[..., 1] > rgb[..., 2] * 1.2))
    # the display / glass field: large dark areas (opened so tiny printed marks stay metal-coloured but non-metal)
    dk = K.blur_edge(dark.astype(float), 3) > 0.5
    nonmetal = np.clip(K.blur_edge((dk | led).astype(float), 0.7), 0, 1)
    metal = 1 - nonmetal
    # flatten the render's lighting over the metal (and over the glass of black-glass panels)
    base_m = metal if not glass else nonmetal
    sx, sy = w * 0.25, h * 0.12
    field = masked_blur(L, base_m, sx, sy)
    ref_l = float(np.median(L[base_m > 0.5])) if (base_m > 0.5).any() else 0.7
    gain = np.clip(ref_l / np.maximum(field, 1e-3), 0.6, 1.6)
    if glass:
        target = 0.09
        gain = np.clip(target / np.maximum(field, 1e-3), 0.3, 1.5)
    gain = gain * base_m + 1 * (1 - base_m)
    rgb = np.clip(rgb * gain[..., None], 0, 1)
    # level of the steel: stainless at ~0.80 lightness, gold keeps its colour at ~0.72
    if not glass:
        Lm = float(np.median((rgb @ np.array([0.299, 0.587, 0.114]))[metal > 0.5]))
        tgt = 0.72 if gold else 0.80
        k = tgt / max(Lm, 1e-3)
        rgb = rgb * (1 + (k - 1) * metal)[..., None]
        if not gold:
            # neutral steel: pull the steel's slight colour cast to grey
            g = rgb.mean(-1, keepdims=True)
            rgb = rgb * (1 - 0.7 * metal[..., None]) + g * 0.7 * metal[..., None]
    rgb = np.clip(rgb, 0, 1)
    # maps
    Lf = rgb @ np.array([0.299, 0.587, 0.114])
    relief = K.blur_edge(Lf, 0.8) - K.blur_edge(Lf, 5)
    hgt = relief * metal
    nrm = K.normal_from_height(hgt, k=6.0, periodic=False)
    mirror = finish == "stainless-mirror"
    sm_metal = 0.88 if mirror else 0.6
    smooth = metal * sm_metal + nonmetal * 0.9
    met = metal
    if glass:                                   # black glass: all dielectric, glossy
        met = np.zeros_like(Lf)
        smooth = np.full_like(Lf, 0.92)
    msk = K.mask_map(met, smooth)
    alb8 = np.round(rgb * 255).astype(np.uint8)
    return alb8, nrm, msk


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--no-merge", action="store_true")
    args = ap.parse_args(argv)
    ids = args.ids or list(PANELS)
    cat = {p["id"]: p for p in json.loads((K.ROOT / "Assets/House4696/Resources/Lifts/catalog.json").read_text())["panels"]}
    for pid in ids:
        alb, nrm, msk = build(pid)
        K.write_material("liftpanel_" + pid.replace("-", "_"), alb, nrm, msk)
        print(pid, alb.shape[1], "x", alb.shape[0], f"w:h {alb.shape[1] / alb.shape[0]:.3f}")
    entries, rows, info = [], [], []
    for pid in PANELS:
        mid = "liftpanel_" + pid.replace("-", "_")
        alb, msk = K.read_albedo(mid), K.read_mask(mid)
        entries.append(K.entry(mid, f"Панель {cat[pid]['name']} ({cat[pid]['kind'].upper()})", SOURCE, (1, 1), LONG, mask_size=LONG))
        info.append((pid, cat[pid]["kind"], alb.shape[1], alb.shape[0]))
        ref = Image.open(K.REF / "panels" / f"{pid}.jpg").convert("RGB")
        def fit(im, bw=420, bh=420):
            k = min(bw / im.width, bh / im.height)
            return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
        ims = [fit(ref), fit(Image.fromarray(alb)), fit(Image.fromarray(msk[..., 0])),
               fit(Image.fromarray(msk[..., 3])), fit(K.lit_preview(alb, msk))]
        rows.append((f"{pid}", ims))
    # several panels per sheet row
    packed, cur = [], None
    for lab, ims in rows:
        if cur is None:
            cur = [lab, list(ims)]
        elif sum(i.width for i in cur[1]) + sum(i.width for i in ims) < 2400:
            cur[0] += " | " + lab
            cur[1] += ims
        else:
            packed.append(tuple(cur))
            cur = [lab, list(ims)]
    packed.append(tuple(cur))
    K.sheet(packed, K.SHEETS / f"{FAMILY}.png", "Lift panels: ref | albedo | metallic | smoothness | lit")
    K.write_entries(FAMILY, entries, merge=not args.no_merge)
    for i, k, w, h in info:
        print(f"| liftpanel_{i.replace('-', '_')} | {k} | {w} x {h} | {w / h:.3f} |")


if __name__ == "__main__":
    main()
