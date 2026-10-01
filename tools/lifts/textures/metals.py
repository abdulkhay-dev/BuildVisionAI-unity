#!/usr/bin/env python3
"""Lift textures, family `metals`: the tiling metals of the GLZ / NBSL cabins and doors.

    python tools/lifts/textures/metals.py [--no-merge] [ids]

  lift_brushed    hairline (No.4 / HL) stainless, grain vertical (along V); neutral, tinted by the engine
  lift_mirror     mirror (No.8) stainless, almost flat with a long sheet waviness; neutral, tinted
  lift_painted    powder-coated steel, orange peel; neutral, tinted by the paint colour
  lift_woodmetal  «цветной металл, бук» (SL-8055) wood-look film on steel, vertical grain; baked colour
  lift_checker    chequer (diamond / lentil tread) plate of the freight cars, brushed stainless

Writes the materials, entries/metals.json (+ merge), sheets/metals.png and the tint table of metals.md
(finish colours as seen in the catalogue -> the `tint` to multiply the neutral albedo with).
UV: metres (metersPerTile = tile); walls / doors get u horizontal, v = height, so the grain runs along image y.
"""
import argparse
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lift_kit as K                # noqa: E402

FAMILY = "metals"
SOURCE = "procedural:tools/lifts/textures/metals.py"
N = 1024

# neutral albedo means (sRGB): what the engine's tint multiplies
MEAN = {"lift_brushed": "#d8d8d8", "lift_mirror": "#e6e6e6", "lift_painted": "#e6e6e6"}

# finish colours: (what the catalogue shows, the metal's reflectance colour to aim at); see metals.md
FINISH_COLOURS = {
    "rose-gold": ("SL-7105 door: mean #be8b5d, bright #d6a476; SL-1109 hairline pylons #7b542b..#986d40 (dim cabin)", "#d6a476"),
    "titanium-gold": ("SL-7037 door: mean #b79d52, bright #ccb36b; SL-1095 walls bright #d8b356", "#d2b262"),
    "champagne-gold": ("no sample in the catalogue (only named in «материал стен на выбор»); typical champagne PVD", "#d5c29e"),
    "black-titanium": ("SL-1137 corner inserts / SL-2039BJ: near-black mirror, slightly warm", "#3b3633"),
    "smoky-grey": ("SL-1136 side walls: #4d3a1e mean, #654f31 bright (dark bronze-brown, dim render)", "#7a6650"),
}
# catalogue finishes (catalog.json "finishes") -> (colour key or hex, base material)
FINISH_TINTS = [
    ("rose-gold-mirror", "rose-gold", "lift_mirror"),
    ("rose-gold-etched", "rose-gold", "lift_mirror"),
    ("titanium-gold-mirror", "titanium-gold", "lift_mirror"),
    ("titanium-gold-etched", "titanium-gold", "lift_mirror"),
    ("titanium-gold-hairline", "titanium-gold", "lift_brushed"),
    ("black-titanium-mirror", "black-titanium", "lift_mirror"),
    ("black-titanium-hairline", "black-titanium", "lift_brushed"),
    ("champagne-gold", "champagne-gold", "lift_mirror"),
    ("(rose gold, hairline — no finish id yet)", "rose-gold", "lift_brushed"),
    ("(champagne, hairline — no finish id yet)", "champagne-gold", "lift_brushed"),
    ("smoky-grey-stainless", "smoky-grey", "lift_brushed"),
    ("painted-b505p", "#c1bfbf", "lift_painted"),
    ("painted-b531p", "#a7a6b0", "lift_painted"),
    ("painted-black", "#1a1a1a", "lift_painted"),
]


def tint_for(target_hex, base_mean_hex):
    """Tint t (sRGB hex) with lin(albedo_mean) * lin(t) = lin(target): URP multiplies _BaseColor in linear light."""
    t = K.lin(target_hex) / K.lin(base_mean_hex)
    clipped = bool((t > 1.0).any())
    return K.hexof(np.clip(t, 0, 1)), clipped


# ------------------------------------------------------------------------------------------------ builders
def brushed(rng):
    """1024 x 1024 over 0.5 x 1.0 m: 0.49 mm/px across, 0.98 mm/px along the grain (vertical)."""
    mmx, mmy = 500 / N, 1000 / N
    fine = K.noise(rng, N, N, 0.45, 220 / mmy)                      # single hairlines, long
    mid = K.noise(rng, N, N, 1.2, 600 / mmy)                        # bundles of strokes
    band = K.noise(rng, N, N, 18 / mmx, 1000 / mmy)                 # soft streaky bands
    pits = K.noise(rng, N, N, 0.5, 4.0)                             # broken strokes
    t = 0.55 * fine + 0.35 * mid + 0.25 * band + 0.12 * pits
    t = (t - t.mean()) / t.std()
    a = np.repeat(np.clip(1 + 0.045 * t, 0, 2)[..., None], 3, -1) * 0.7
    a = K.fit_mean(a, MEAN["lift_brushed"])
    hgt = 0.8 * fine + 0.5 * mid + 0.15 * pits
    nrm = K.normal_from_height(hgt, tilt_deg=2.2)
    sm = 0.575 + 0.02 * K.smoothstep(-2, 2, band) - 0.03 * K.smoothstep(1.2, 2.5, -fine)
    msk = K.mask_map(1.0, sm)
    return K.to8(a), nrm, msk, (0.5, 1.0)


def mirror(rng):
    """1024 x 1024 over 2 x 2 m: flat, the only life a long waviness (oil-canning) of the sheet in the normal."""
    px = N / 2000.0
    wav = K.noise(rng, N, N, 260 * px, 380 * px) + 0.35 * K.noise(rng, N, N, 90 * px, 140 * px)
    fine = K.noise(rng, N, N, 1.0, 1.0)
    a = np.ones((N, N, 3)) * (1 + 0.004 * wav[..., None] + 0.002 * fine[..., None])
    a = K.fit_mean(a, MEAN["lift_mirror"])
    nrm = K.normal_from_height(wav + 0.01 * fine, tilt_deg=0.7)
    msk = K.mask_map(1.0, 0.90 - 0.004 * K.smoothstep(1.5, 3, fine))   # 0.96 showed the probes' pixels on big flat portals
    return K.to8(a), nrm, msk, (2.0, 2.0)


def painted(rng):
    """1024 x 1024 over 0.5 x 0.5 m (0.49 mm/px): powder coat with orange peel and a faint mottle."""
    px = N / 500.0
    peel = K.noise(rng, N, N, 1.4 * px) + 0.5 * K.noise(rng, N, N, 0.6 * px)
    mott = K.noise(rng, N, N, 25 * px)
    a = np.ones((N, N, 3)) * (1 + 0.008 * mott[..., None] + 0.006 * peel[..., None])
    a = K.fit_mean(a, MEAN["lift_painted"])
    nrm = K.normal_from_height(peel, tilt_deg=1.6)
    msk = K.mask_map(0.1, 0.45 + 0.02 * K.smoothstep(-2, 2, peel))
    return K.to8(a), nrm, msk, (0.5, 0.5)


def woodmetal(rng):
    """1024 x 1024 over 0.5 x 1.0 m: beech wood-look film (SL-8055), vertical grain, satin."""
    mmx, mmy = 500 / N, 1000 / N
    a, tone = K.woodgrain(rng, N, N, mmx, mmy, "#d4a96c", "#a8783f", contrast=0.7)
    # beech: small dark ray flecks (1-3 mm long, along the grain)
    fl = K.noise(rng, N, N, 0.6, 1.8 / mmy)
    fleck = K.smoothstep(2.3, 3.0, fl)
    a = K.mix(a, a * 0.72, fleck * 0.6)
    a = K.fit_mean(a, "#c09455")
    hgt = 0.6 * tone - 1.5 * fleck + 0.3 * K.noise(rng, N, N, 0.5, 6)
    nrm = K.normal_from_height(hgt, tilt_deg=1.0)
    msk = K.mask_map(0.0, 0.5 - 0.08 * fleck)
    return K.to8(a), nrm, msk, (0.5, 1.0)


def checker(rng):
    """1024 x 1024 over 0.4 x 0.4 m (0.39 mm/px): lentil (diamond) tread plate, 7 x 7 staggered pairs of
    perpendicular lentils, 27 mm long, 7 mm wide, ~1.5 mm high, on a vertically brushed stainless ground."""
    mm = 400.0 / N
    reps = 7
    pitch = N / reps                                  # px between lentils of one orientation
    L, Wd = 27 / mm, 7 / mm
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float64)
    hgt = np.zeros((N, N))
    for ox, oy, ang in ((0.0, 0.0, 45.0), (0.5, 0.5, -45.0)):
        # local coords relative to the nearest lattice centre (periodic)
        cx = (xx / pitch - ox) % 1.0 - 0.5
        cy = (yy / pitch - oy) % 1.0 - 0.5
        dx, dy = cx * pitch, cy * pitch
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        a_ = dx * c + dy * s                          # along the lentil
        b_ = -dx * s + dy * c
        f = np.clip(1 - (2 * a_ / L) ** 2, 0, 1)
        bmax = Wd / 2 * f + 1e-6
        r = np.clip(1 - (b_ / bmax) ** 2, 0, 1)
        dome = np.sqrt(r) * f ** 0.35
        hgt = np.maximum(hgt, K.smoothstep(0.0, 0.35, dome) * (0.7 + 0.3 * dome))
    lent = (hgt > 0.02).astype(float)
    lent_s = K.blur(lent, 1.0)
    # brushed ground
    fine = K.noise(rng, N, N, 0.5, 150 / mm)
    band = K.noise(rng, N, N, 6 / mm, 400 / mm)
    wear = K.noise(rng, N, N, 3.0)
    g = 1 + 0.05 * (0.6 * fine + 0.4 * band)
    a = np.repeat((g * (1 + 0.11 * lent_s * (0.6 + 0.4 * wear)))[..., None], 3, -1)
    ao = 1 - 0.28 * np.clip(K.blur(lent, 5) - lent_s, 0, 1) * 2.5
    a = a * ao[..., None]
    a = K.fit_mean(a, "#bcbcbc")
    nrm = K.normal_from_height(K.blur(hgt, 0.7) * 4.0 + 0.02 * fine, k=1.5 / mm / 4.0)
    sm = 0.5 + 0.1 * lent_s - 0.02 * K.smoothstep(1, 2.5, wear)
    msk = K.mask_map(1.0, sm, ao)
    return K.to8(a), nrm, msk, (0.4, 0.4)


MATERIALS = {
    "lift_brushed": ("Лифт: нержавеющая сталь, шлифованная (hairline)", brushed, True),
    "lift_mirror": ("Лифт: нержавеющая сталь, зеркало", mirror, True),
    "lift_painted": ("Лифт: окрашенная сталь (порошковая)", painted, True),
    "lift_woodmetal": ("Лифт: цветной металл под бук (SL-8055)", woodmetal, False),
    "lift_checker": ("Лифт: рифлёный лист «чечевица» (нержавейка)", checker, False),
}


def write_notes(stats):
    rows = []
    for fid, key, base in FINISH_TINTS:
        if key.startswith("#"):
            seen, target = "catalog.json colour", key
        else:
            seen, target = FINISH_COLOURS[key]
        t, clipped = tint_for(target, MEAN[base])
        rows.append(f"| {fid} | {base} | {target} | **{t}**{' (clipped at 1)' if clipped else ''} |")
    seen_rows = "\n".join(f"| {k} | {v[0]} | {v[1]} |" for k, v in FINISH_COLOURS.items())
    stat_rows = "\n".join(f"| {k} | {v['size']} | {v['tile']} | {v['mean']} | {v['note']} |" for k, v in stats.items())
    text = f"""# Lift metals (family `metals`)

Generator: `tools/lifts/textures/metals.py` (numpy + Pillow; `lift_kit.py` shared). Check sheet: `sheets/metals.png`.

| id | px | metersPerTile | albedo mean (sRGB, linear-light average) | notes |
|---|---|---|---|---|
{stat_rows}

The three neutral metals (`lift_brushed`, `lift_mirror`, `lift_painted`) are grey with saturation 0 and are tinted by
the engine (`lift_brushed#rrggbb` multiplies `_BaseColor`, i.e. in **linear** light). Grain of the brushed metal runs
along V (vertical on walls and doors).

## Finish colours seen in the catalogue

The catalogue renders show reflections, not the metal itself, so the target is the bright end of the metal's own
hairline / mirror areas (the p90 of the door leaves, which reflect a light wall), i.e. the reflectance colour.

| colour | what the catalogue shows | target metal colour (sRGB) |
|---|---|---|
{seen_rows}

## Tints for catalog.json `finishes[].tint`

`tint = srgb( linear(target) / linear(albedo mean of the base material) )`, so that `lift_<base>#tint` shows the
target colour. (Writing the plain target colour as the tint instead would come out darker than the catalogue:
×0.69 in linear light on brushed, ×0.79 on mirror.)

| finish id | base material | target | tint to write |
|---|---|---|---|
{chr(10).join(rows)}

Notes
- smoky grey: the catalogue calls it «дымчато-серая», the render shows dark bronze-brown; the target keeps the render's
  hue but lifts it so it does not read as black under the app's lighting (#4a371c in catalog.json now would be a
  near-black metal).
- black titanium: near-black mirror; a metal this dark relies on reflections, so it will read as black glass-like.
- champagne: no swatch printed — a typical champagne PVD colour.
- painted-*: catalog colour / #e6e6e6 in linear light.
"""
    (HERE / "metals.md").write_text(text)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--no-merge", action="store_true")
    args = ap.parse_args(argv)
    ids = args.ids or list(MATERIALS)
    entries, rows, stats = [], [], {}
    for i, mid in enumerate(MATERIALS):
        name, fn, neutral = MATERIALS[mid]
        if mid in ids:
            rng = np.random.default_rng(4100 + i)
            alb, nrm, msk, tile = fn(rng)
            K.write_material(mid, alb, nrm, msk)
        alb = K.read_albedo(mid)
        msk = K.read_mask(mid)
        tile = {"lift_brushed": (0.5, 1.0), "lift_mirror": (2.0, 2.0), "lift_painted": (0.5, 0.5),
                "lift_woodmetal": (0.5, 1.0), "lift_checker": (0.4, 0.4)}[mid]
        entries.append(K.entry(mid, name, SOURCE, tile, N, neutral))
        sm = msk[..., 3].mean() / 255
        stats[mid] = {"size": f"{alb.shape[1]}x{alb.shape[0]}", "tile": f"{tile[0]} x {tile[1]} m",
                      "mean": K.mean_hex(alb), "note": f"metallic {msk[..., 0].mean() / 255:.2f}, smoothness {sm:.2f}"}
        # sheet: 1:1 crop (256 px), the tile scaled to 512 px tall, a tinted strip for neutral ones, lit preview
        crop = Image.fromarray(alb[:256, :256])
        nrm = Image.open(K.EXT / "Materials" / mid / f"{mid}_normal.jpg").convert("RGB")
        ims = [Image.fromarray(alb).resize((256, 256)), crop.resize((256, 256), Image.NEAREST), nrm.crop((0, 0, 256, 256)),
               K.lit_preview(alb[::4, ::4], msk[::4, ::4])]
        if neutral:
            for key in ("rose-gold", "titanium-gold", "champagne-gold", "black-titanium", "smoky-grey"):
                t, _ = tint_for(FINISH_COLOURS[key][1], MEAN[mid])
                lin = K.srgb_to_linear(alb[::4, ::4] / 255.0) * K.lin(t)
                ims.append(K.lit_preview(K.to8(lin), msk[::4, ::4]))
        rows.append((f"{mid} — {stats[mid]['mean']}  {stats[mid]['note']}  (tile | 1:1 crop | normal | lit | tinted: rose, Ti-gold, champagne, black Ti, smoky)", ims))
    ref = [Image.open(K.REF / "floors" / f).convert("RGB").resize((340, 256)) for f in ("checker-steel.jpg", "checker-stainless.jpg")]
    ref += [K.fit_h(Image.open(K.REF / "doors" / f).convert("RGB").crop((100, 100, 480, 900)), 256) for f in ("sl-8055.jpg", "sl-7105.jpg", "sl-7037.jpg", "plain-stainless.jpg")]
    rows.append(("references: checker steel / stainless, door SL-8055 beech, SL-7105 rose gold, SL-7037 titanium gold, plain stainless", ref))
    K.sheet(rows, K.SHEETS / f"{FAMILY}.png", "Lift metals")
    K.write_entries(FAMILY, entries, merge=not args.no_merge)
    write_notes(stats)
    for k, v in stats.items():
        print(k, v)


if __name__ == "__main__":
    main()
