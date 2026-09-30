#!/usr/bin/env python3
"""Casegoods decor textures, wave 6: family `light_oaks` - the light / honey oak films of the Pinskdrev catalogue.

    python tools/casegoods/textures/light_oaks.py                      # every material: maps + entries + merge
    python tools/casegoods/textures/light_oaks.py cg_dub_sonoma        # only these
    python tools/casegoods/textures/light_oaks.py --sheet              # + tools/casegoods/textures/sheets/light_oaks.png
    python tools/casegoods/textures/light_oaks.py --no-write --sheet   # check sheet from the written maps only
    python tools/casegoods/textures/light_oaks.py --analyze            # swatch mean, L* contrast, a*/b* slopes

Builds on the door machinery (tools/doors/textures, not edited): eco_oak.wood_structure (sawn boards side by side,
growth rings opening into cathedrals near the pith line, pores in the earlywood, ray flecks, knots with rims and
radial checks, checks along the rings, broad tone), eco_oak.albedo_linear / normal_map / mask_map (colouring with the
mean solved to the target colour, embossed pores and checks, matt smoothness) and finish_kit.straight_lines (the
cross-grain saw marks of the Sonoma films). The patterns below are this family's own (injected into eco_oak.PATTERNS
in memory). Per material M it writes Assets/House4696/External/Materials/M/M_albedo.jpg (sRGB 2048x1024, 2.0 x 1.0 m,
grain along U, tileable), M_normal.jpg (OpenGL 1024x512), M_mask.png (256x128: R metallic 0, G AO 255, B 0,
A smoothness), then tools/casegoods/textures/entries/light_oaks.json, merged into external.json.

Colour: `color` is the chosen catalogue swatch's mean (tools/casegoods/gen/catpage.py --swatch, the trimmed mean of the
print); the texture's mean in linear light is solved to it, so the written JPEG lands within dE76 ~0.5 of it. The
swatch choice and the conflicts between collections are in tools/casegoods/textures/light_oaks.md.

The generator needs numpy + Pillow; --sheet / --analyze also need PyMuPDF (the catalogue PDF).
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DOORS = ROOT / "tools" / "doors" / "textures"
sys.path.insert(0, str(DOORS))
import eco_oak as eo                     # noqa: E402  (board / ring / knot model, colouring, normal and mask maps)
import finish_kit as fk                  # noqa: E402  (straight_lines: saw marks)
import make_finishes as mf               # noqa: E402  (colour maths, noise)
import merge_entries                     # noqa: E402

FAMILY = "light_oaks"
EXT = mf.EXT
ALBEDO, MM, TILE_M = mf.ALBEDO, mf.MM, mf.TILE_M
PX = 1.0 / MM
ENTRIES = HERE / "entries" / f"{FAMILY}.json"
SHEET = HERE / "sheets" / f"{FAMILY}.png"
SOURCE = "procedural:tools/casegoods/textures/light_oaks.py"
hex_to_linear, linear_to_hex, linear_to_lab = mf.hex_to_linear, mf.linear_to_hex, mf.linear_to_lab

# ------------------------------------------------------------------------------------------------ patterns
# Keys as eco_oak.PATTERNS (lengths in mm): board = leaf width (median, log-sigma, min, max); flat_share = share of
# flat-sawn leaves (cathedrals), the rest rift (straight lines); depth / depth_amp / turns = the cathedral arches;
# wave = ring waviness; rings = ring width, earlywood; pores; rays; knots / pins; checks (cracks along the rings);
# sdark / slight = long streaks; bands / clouds / fibre; broad_mix = weights of ring zones, board shade, clouds;
# relief. Extra keys of this family: saw = cross-grain saw marks (finish_kit.straight_lines spec + patch mask).
_BASE = dict(
    pith_in=0.22, rift_out=0.6, pith_wander=0.12, pith_len=400.0, depth=(40.0, 0.4), depth_amp=0.6, turns=(1, 3),
    turn_round=25.0, dmin=4.0, ecc=0.15, wave=[(4.0, 260.0, 30.0), (1.5, 90.0, 12.0), (0.5, 35.0, 5.0)],
    late_fibre=(0.6, 0.5, 4.0), zone_len=6.0, bands=(25.0, 700.0), clouds=(150.0, 500.0), fibre=(0.35, 5.0),
)


def _P(**kw):
    d = dict(_BASE)
    d.update(kw)
    return d


PATTERNS = {
    # Дуб Бордо лайт: bleached oak print - long straight fibres and fine pore lines, soft cathedrals, long thin dark
    # cracks along the grain (the Агата close-up p. 26), hardly any knots
    "lo_bordo": _P(
        seed=8101, board=(190.0, 0.3, 110.0, 320.0), flat_share=0.5, depth=(55.0, 0.35), depth_amp=0.55,
        rings=dict(ring=(2.4, 0.35), early=(0.7, 0.25), late_gamma=1.6, trend=6.0, vary=0.4),
        pores=dict(len=1.1, wid=0.3, thr=0.1, fill=0.9, late=0.10),
        rays=dict(per_cm=0.8, width=(0.3, 0.3), length=(8.0, 0.6), alpha=(0.1, 0.4), fade=0.6, slope=0.0),
        pins=dict(per_m2=1.0, size=(2.5, 0.3), max=5.0, aspect=1.3, rim=0.3, rim_alpha=0.4, halo=0.2),
        checks=dict(per_m2=10.0, length=(260.0, 0.6), width=(0.55, 0.35), wiggle=1.0),
        sdark=dict(per_cm=0.9, width=(0.45, 0.4), length=(200.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.5, width=(0.8, 0.45), length=(120.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        broad_mix=(0.5, 0.4, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.3, late=0.2, tilt_deg=3.0),
    ),
    # Дуб Сонома: sawn oak - straight pale fibres, darker grey-brown pore streaks, faint cathedrals, few small knots,
    # patches of short saw-cut marks across the grain
    "lo_sonoma": _P(
        seed=8201, board=(170.0, 0.3, 100.0, 300.0), flat_share=0.45, depth=(45.0, 0.4),
        rings=dict(ring=(2.8, 0.35), early=(0.8, 0.25), late_gamma=1.5, trend=6.0, vary=0.45),
        pores=dict(len=1.2, wid=0.35, thr=0.0, fill=0.9, late=0.12),
        rays=dict(per_cm=1.0, width=(0.3, 0.3), length=(8.0, 0.6), alpha=(0.1, 0.5), fade=0.6, slope=0.0),
        knots=dict(per_m2=0.5, size=(9.0, 0.35), max=18.0, bump=2.2, flow=2.2, aspect=1.4, rim=0.12,
                   rim_alpha=0.6, halo=0.4, cracked=0.3),
        pins=dict(per_m2=2.5, size=(2.5, 0.3), max=5.0, aspect=1.3, rim=0.3, rim_alpha=0.45, halo=0.25),
        checks=dict(per_m2=1.5, length=(90.0, 0.6), width=(0.6, 0.4), wiggle=0.8),
        sdark=dict(per_cm=1.4, width=(0.55, 0.45), length=(220.0, 0.8), alpha=(0.25, 0.9), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.9, width=(0.9, 0.45), length=(150.0, 0.8), alpha=(0.25, 0.9), fade=0.8, slope=0.002),
        broad_mix=(0.45, 0.45, 0.35),
        saw=dict(pitch=(22.0, 0.45), width=(0.9, 0.4), jitter_len=18.0, share_on=0.45, strength=(0.25, 0.8),
                 wander=1.5, patch=(260.0, 90.0), patch_share=0.4),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.3, late=0.2, tilt_deg=3.0),
    ),
    # Дуб Кантри золотой: golden rustic oak - open cathedrals, long straight fibres, small dark knots, short cracks
    "lo_kantri": _P(
        seed=8301, board=(180.0, 0.3, 100.0, 300.0), flat_share=0.6, depth=(45.0, 0.4), depth_amp=0.65, dmin=8.0,
        wave=[(5.0, 260.0, 30.0), (1.6, 90.0, 12.0), (0.6, 35.0, 5.0)],
        rings=dict(ring=(3.2, 0.35), early=(0.9, 0.25), late_gamma=1.5, trend=6.0, vary=0.45),
        pores=dict(len=0.9, wid=0.35, thr=0.0, fill=0.9, late=0.08),
        rays=dict(per_cm=1.2, width=(0.35, 0.3), length=(9.0, 0.6), alpha=(0.2, 0.6), fade=0.6, slope=0.0),
        knots=dict(per_m2=1.6, size=(11.0, 0.45), max=28.0, bump=2.5, flow=2.2, aspect=1.4, rim=0.12,
                   rim_alpha=0.85, halo=0.55, cracked=0.6),
        pins=dict(per_m2=4.0, size=(3.0, 0.3), max=6.0, aspect=1.3, rim=0.3, rim_alpha=0.55, halo=0.3),
        checks=dict(per_m2=7.0, length=(90.0, 0.6), width=(1.1, 0.45), wiggle=1.0),
        tails=dict(length=35.0, width=2.5, streak=20.0, gain=5.0),
        sdark=dict(per_cm=0.9, width=(0.55, 0.45), length=(180.0, 0.8), alpha=(0.25, 0.9), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.6, width=(0.8, 0.45), length=(100.0, 0.8), alpha=(0.2, 0.9), fade=0.8, slope=0.002),
        broad_mix=(0.55, 0.45, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.3, late=0.25, tilt_deg=3.5),
    ),
    # Дуб Онтарио / Дуб Артизан (artisan oak): straw ground, frequent small dark knots with cracks, short pore strokes,
    # mostly straight grain, hardly any cathedrals
    "lo_artisan": _P(
        seed=8401, board=(200.0, 0.3, 120.0, 320.0), flat_share=0.3, depth=(60.0, 0.4), depth_amp=0.5,
        rings=dict(ring=(3.0, 0.35), early=(0.8, 0.25), late_gamma=1.5, trend=6.0, vary=0.4),
        pores=dict(len=1.6, wid=0.4, thr=0.1, fill=0.9, late=0.12),
        rays=dict(per_cm=1.0, width=(0.35, 0.3), length=(10.0, 0.6), alpha=(0.15, 0.5), fade=0.6, slope=0.0),
        knots=dict(per_m2=8.0, size=(14.0, 0.5), max=34.0, bump=2.4, flow=2.6, aspect=1.9, rim=0.16,
                   rim_alpha=0.8, halo=0.8, cracked=1.0),
        tails=dict(length=45.0, width=3.0, streak=25.0, gain=6.0),
        pins=dict(per_m2=20.0, size=(3.0, 0.35), max=6.5, aspect=1.4, rim=0.35, rim_alpha=0.75, halo=0.35),
        checks=dict(per_m2=9.0, length=(70.0, 0.6), width=(1.1, 0.5), wiggle=0.8),
        sdark=dict(per_cm=0.7, width=(0.5, 0.45), length=(160.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.6, width=(0.8, 0.45), length=(100.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        broad_mix=(0.4, 0.45, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.3, late=0.2, tilt_deg=3.5),
    ),
    # Дуб Мадура: light greyish oak - long straight fibres, fine grey pore streaks, soft low-contrast cathedrals, pins
    "lo_madura": _P(
        seed=8501, board=(190.0, 0.3, 110.0, 320.0), flat_share=0.25, depth=(55.0, 0.35), depth_amp=0.55,
        rings=dict(ring=(2.2, 0.35), early=(0.6, 0.25), late_gamma=1.6, trend=6.0, vary=0.4),
        pores=dict(len=1.3, wid=0.3, thr=0.05, fill=0.9, late=0.12),
        rays=dict(per_cm=0.8, width=(0.3, 0.3), length=(8.0, 0.6), alpha=(0.1, 0.4), fade=0.6, slope=0.0),
        pins=dict(per_m2=2.5, size=(2.5, 0.3), max=5.0, aspect=1.3, rim=0.3, rim_alpha=0.45, halo=0.25),
        checks=dict(per_m2=1.0, length=(80.0, 0.6), width=(0.5, 0.35), wiggle=0.8),
        sdark=dict(per_cm=1.8, width=(0.45, 0.4), length=(240.0, 0.8), alpha=(0.25, 0.9), fade=0.8, slope=0.002),
        slight=dict(per_cm=1.0, width=(0.8, 0.45), length=(160.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        broad_mix=(0.45, 0.4, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.3, late=0.2, tilt_deg=3.0),
    ),
    # Дуб Ланцелот: warm rustic oak - rich plank figure, darker streaks, knots and cracks
    "lo_lancelot": _P(
        seed=8601, board=(170.0, 0.3, 100.0, 280.0), flat_share=0.65, depth=(40.0, 0.4), depth_amp=0.65,
        wave=[(5.0, 240.0, 28.0), (1.8, 80.0, 11.0), (0.6, 30.0, 5.0)],
        rings=dict(ring=(3.4, 0.35), early=(0.9, 0.25), late_gamma=1.5, trend=6.0, vary=0.5),
        pores=dict(len=0.9, wid=0.35, thr=0.0, fill=0.9, late=0.08),
        rays=dict(per_cm=1.2, width=(0.35, 0.3), length=(9.0, 0.6), alpha=(0.2, 0.6), fade=0.6, slope=0.0),
        knots=dict(per_m2=1.8, size=(12.0, 0.45), max=30.0, bump=2.5, flow=2.2, aspect=1.4, rim=0.12,
                   rim_alpha=0.85, halo=0.6, cracked=0.6),
        pins=dict(per_m2=4.0, size=(3.0, 0.3), max=6.0, aspect=1.3, rim=0.3, rim_alpha=0.55, halo=0.3),
        checks=dict(per_m2=8.0, length=(140.0, 0.6), width=(1.2, 0.5), wiggle=1.2),
        tails=dict(length=40.0, width=3.0, streak=20.0, gain=5.0),
        sdark=dict(per_cm=1.3, width=(0.6, 0.5), length=(200.0, 0.8), alpha=(0.3, 1.0), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.7, width=(0.8, 0.45), length=(110.0, 0.8), alpha=(0.2, 0.9), fade=0.8, slope=0.002),
        broad_mix=(0.6, 0.45, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.3, late=0.25, tilt_deg=3.5),
    ),
    # Дуб натуральный (массив): lacquered solid oak glued from ~70 mm staves - straight grain with ray flecks, each
    # stave its own shade, no knots
    "lo_staves": _P(
        seed=8701, board=(70.0, 0.12, 55.0, 88.0), flat_share=0.35, pith_in=0.2, rift_out=0.35,
        depth=(30.0, 0.4), depth_amp=0.5,
        rings=dict(ring=(2.6, 0.35), early=(0.8, 0.25), late_gamma=1.5, trend=6.0, vary=0.45),
        pores=dict(len=0.8, wid=0.35, thr=0.0, fill=0.9, late=0.08),
        rays=dict(per_cm=2.2, width=(0.45, 0.35), length=(10.0, 0.6), alpha=(0.25, 0.8), fade=0.6, slope=0.004),
        checks=dict(per_m2=0.5, length=(60.0, 0.5), width=(0.5, 0.3), wiggle=0.6),
        sdark=dict(per_cm=0.5, width=(0.5, 0.4), length=(140.0, 0.8), alpha=(0.2, 0.7), fade=0.8, slope=0.002),
        broad_mix=(0.35, 0.75, 0.25),
        relief=dict(pores=1.0, checks=2.0, rays=0.4, rim=0.5, fibre=0.25, late=0.2, tilt_deg=2.0),
    ),
    # Дуб Сахара: greige oak - straight planks, soft cathedrals, fine grey pores, a few small knots
    "lo_sahara": _P(
        seed=8801, board=(180.0, 0.3, 100.0, 300.0), flat_share=0.5, depth=(45.0, 0.4),
        rings=dict(ring=(2.6, 0.35), early=(0.7, 0.25), late_gamma=1.6, trend=6.0, vary=0.4),
        pores=dict(len=1.0, wid=0.35, thr=0.0, fill=0.9, late=0.10),
        rays=dict(per_cm=1.0, width=(0.3, 0.3), length=(8.0, 0.6), alpha=(0.15, 0.5), fade=0.6, slope=0.0),
        knots=dict(per_m2=0.7, size=(9.0, 0.4), max=20.0, bump=2.3, flow=2.2, aspect=1.4, rim=0.12,
                   rim_alpha=0.75, halo=0.45, cracked=0.4),
        pins=dict(per_m2=3.0, size=(2.5, 0.3), max=5.0, aspect=1.3, rim=0.3, rim_alpha=0.5, halo=0.25),
        checks=dict(per_m2=2.0, length=(110.0, 0.6), width=(0.7, 0.4), wiggle=0.9),
        sdark=dict(per_cm=1.1, width=(0.5, 0.45), length=(200.0, 0.8), alpha=(0.25, 0.9), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.7, width=(0.8, 0.45), length=(120.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        broad_mix=(0.5, 0.4, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.3, late=0.2, tilt_deg=3.0),
    ),
}


# ------------------------------------------------------------------------------------------------ materials
def _M(mid, name, pattern, color, slope, dark_dL, light_dL, swatch, photo, **kw):
    """A material: id, catalogue name, pattern (+ seed), color = the chosen swatch's mean (hex); dark / light = the
    ground's full-strength colours dL in L* from it along the swatch's a*/b* slopes; grain / tone / fibre = L* std of
    the ring, broad and fibre tone; pore / ray / streak / knot / rim / check / halo as eco_oak; saw = saw-mark opacity;
    smooth = matt SWN smoothness. swatch = (PDF page, crop, grain 'x'/'y' in the crop, mm the crop's width shows);
    photo = (PDF page, crop) of a catalogue photo of the decor on furniture (None: none)."""
    d = dict(id=mid, material=mid, name=name, pattern=pattern, color=color,
             dark=eo.shade(color, -dark_dL, slope), light=eo.shade(color, light_dL, slope), swatch=swatch,
             photo=photo, smooth=0.32)
    for key in ("pore", "ray", "knot", "rim", "check"):          # colours given as dL (negative = darker) -> hex
        v = kw.get(key + "_dL")
        if v is not None:
            kw.setdefault(key + "_col" if key in ("pore", "ray") else key, eo.shade(color, v, slope))
            kw.pop(key + "_dL")
    d.update(kw)
    return d


MATERIALS = [
    _M("cg_dub_bordo_layt", "Дуб Бордо лайт 380 SWN", "lo_bordo", "#e7e7e1", (0.0, 0.05), 16, 3,
       (27, "0.675,0.865,0.73,0.905", "x", 320), (26, "0.245,0.715,0.40,0.89"),
       grain=1.2, tone=0.8, fibre=0.35, streak=0.35, pore=0.45, pore_dL=-12, ray=0.15, ray_dL=-5,
       knot="#aeaba6", rim_dL=-35, check_dL=-45, halo=1.0),
    _M("cg_dub_sonoma", "Дуб Сонома 325", "lo_sonoma", "#caab92", (0.05, 0.15), 22, 8,
       (104, "0.725,0.86,0.775,0.9", "y", 320), (104, "0.045,0.13,0.125,0.31"),
       grain=2.4, tone=2.2, fibre=0.8, streak=0.55, pore=0.5, pore_dL=-20, ray=0.2, ray_dL=-10,
       knot_dL=-26, rim_dL=-45, check_dL=-50, halo=3.0, saw=0.7, saw_dL=-16),
    _M("cg_dub_kantri_zolotoy", "Дуб Кантри золотой 389 SWN", "lo_kantri", "#b39266", (0.05, 0.15), 24, 10,
       (33, "0.670,0.855,0.695,0.89", "x", 250), (33, "0.143,0.235,0.2,0.4"),
       grain=3.4, tone=3.8, fibre=1.0, streak=0.7, pore=0.5, pore_dL=-22, ray=0.3, ray_dL=-12,
       knot_dL=-28, rim_dL=-50, check_dL=-55, halo=5.0, tail=0.6, tail_dL=-24),
    _M("cg_dub_ontario", "Дуб Онтарио 385ТМ", "lo_artisan", "#a08357", (0.05, 0.12), 22, 10,
       (137, "0.60,0.86,0.655,0.90", "y", 300), (70, "0.09,0.42,0.21,0.61"),
       grain=2.8, tone=3.4, fibre=1.0, streak=0.55, pore=0.55, pore_dL=-20, ray=0.25, ray_dL=-10,
       knot_dL=-30, rim_dL=-44, check_dL=-50, halo=8.0, tail=0.8, tail_dL=-28),
    # Кен's «Дуб Онтарио»: the same artisan print as cg_dub_ontario, coloured to Кен's studio photo (site, П3.596.0.02,
    # the plain upper-left front, the flattest crop: #bca48c) - the light beige-grey of p. 70, not the honey Лари print
    _M("cg_dub_ontario_svetly", "Дуб Онтарио (Кен)", "lo_artisan", "#bca48c", (0.03, 0.12), 22, 9,
       None, (70, "0.09,0.42,0.21,0.61"),
       grain=2.6, tone=3.0, fibre=0.9, streak=0.5, pore=0.55, pore_dL=-18, ray=0.25, ray_dL=-9,
       knot_dL=-30, rim_dL=-44, check_dL=-50, halo=8.0, tail=0.8, tail_dL=-28),
    _M("cg_dub_madura", "Дуб Мадура", "lo_madura", "#beb1a1", (0.03, 0.12), 18, 7,
       (132, "0.815,0.855,0.87,0.905", "x", 320), (97, "0.40,0.755,0.44,0.79"),
       grain=2.2, tone=2.0, fibre=0.7, streak=0.55, pore=0.5, pore_dL=-16, ray=0.15, ray_dL=-8,
       knot_dL=-24, rim_dL=-40, check_dL=-42, halo=2.0),
    _M("cg_dub_artizan", "Дуб Артизан", "lo_artisan", "#a2825f", (0.05, 0.12), 22, 10,
       None, None, seed=8403,
       grain=2.8, tone=3.2, fibre=1.0, streak=0.55, pore=0.55, pore_dL=-20, ray=0.25, ray_dL=-10,
       knot_dL=-30, rim_dL=-44, check_dL=-50, halo=8.0, tail=0.8, tail_dL=-28),
    _M("cg_dub_lancelot", "Дуб Ланцелот", "lo_lancelot", "#997658", (0.08, 0.15), 24, 12,
       (134, "0.735,0.856,0.795,0.905", "x", 350), (134, "0.105,0.43,0.195,0.52"),
       grain=3.6, tone=3.4, fibre=1.1, streak=0.65, pore=0.5, pore_dL=-22, ray=0.3, ray_dL=-12,
       knot_dL=-26, rim_dL=-45, check_dL=-48, halo=6.0, tail=0.6, tail_dL=-24),
    _M("cg_dub_naturalny", "Дуб натуральный (массив)", "lo_staves", "#9a866a", (0.03, 0.12), 22, 12,
       (79, "0.748,0.858,0.808,0.900", "y", 320), None,
       grain=3.6, tone=4.4, fibre=1.2, streak=0.35, pore=0.55, pore_dL=-22, ray=0.5, ray_dL=10,
       check_dL=-40, smooth=0.45),
    _M("cg_dub_sahara", "Дуб Сахара", "lo_sahara", "#837b64", (0.0, 0.12), 20, 8,
       None, (43, "0.35,0.60,0.63,0.70"),
       grain=2.2, tone=2.0, fibre=0.8, streak=0.55, pore=0.45, pore_dL=-18, ray=0.2, ray_dL=-8,
       knot_dL=-24, rim_dL=-40, check_dL=-42, halo=3.0),
]


# ------------------------------------------------------------------------------------------------ maps
def structure(mat, cache):
    key = (mat["pattern"], mat.get("seed"))
    if key not in cache:
        eo.PATTERNS.update(PATTERNS)                         # in memory only: eco_oak.py itself is not touched
        st = eo.wood_structure(*key)
        p = PATTERNS[mat["pattern"]]
        if p.get("saw"):
            st["saw"] = saw_marks(p["saw"], (p["seed"] if key[1] is None else key[1]) + 17)
        if p.get("tails"):
            st["tail"] = knot_tails(st, p["tails"], (p["seed"] if key[1] is None else key[1]) + 29)
        if st["knot"].any():                                  # knot cores: mottled, not a flat stamp
            rng = np.random.default_rng(key[1] or p["seed"])
            mott = mf.gauss_noise(rng, st["knot"].shape, 2.5 * PX, 1.5 * PX)
            st["knot"] = st["knot"] * np.clip(0.78 + 0.22 * mott, 0.35, 1.0)
        cache[key] = st
    return cache[key]


def saw_marks(s, seed):
    """Short saw-cut marks across the grain (image columns), only in elongated patches (Sonoma films)."""
    rng = np.random.default_rng(seed)
    lines = fk.straight_lines(rng, s["pitch"], s["width"], PX, 1, s["jitter_len"], s["strength"],
                              share_on=s["share_on"], wander=s["wander"], wander_len=30.0)
    h, w = ALBEDO[1], ALBEDO[0]
    patch = mf.gauss_noise(rng, (h, w), s["patch"][0] * PX, s["patch"][1] * PX)
    thr = float(np.quantile(patch, 1 - s["patch_share"]))
    return lines * fk.smoothstep(thr - 0.4, thr + 0.6, patch)


def _blur_xy(a, sx, sy):
    """Periodic Gaussian blur, sigmas in px along x (columns) and y (rows)."""
    fy = np.fft.fftfreq(a.shape[0])[:, None]
    fx = np.fft.rfftfreq(a.shape[1])[None, :]
    return np.fft.irfft2(np.fft.rfft2(a) * np.exp(-2 * np.pi ** 2 * ((fx * sx) ** 2 + (fy * sy) ** 2)), s=a.shape)


def knot_tails(st, t, seed):
    """Dark streaks trailing the knots along the grain (the stained fibre flowing round a knot of artisan oak):
    the knot cores smeared along x, broken into fibre streaks."""
    rng = np.random.default_rng(seed)
    k = np.clip(t["gain"] * _blur_xy(st["knot"], t["length"] * PX, t["width"] * PX), 0, 1) ** t.get("gamma", 0.8)
    n = mf.gauss_noise(rng, st["knot"].shape, t["streak"] * PX, 0.5 * PX)
    return np.clip(k * fk.smoothstep(-0.3, 0.9, n), 0, 1)


def albedo_linear(mat, st):
    """eco_oak's colouring (mean = color) + this family's extra layers, mean re-solved."""
    out = eo.albedo_linear(mat, st)
    extra = [(k, f) for k, f in (("saw", "saw"), ("tail", "tail")) if mat.get(k) and f in st]
    for k, f in extra:
        col = hex_to_linear(mat["color"])
        r = np.clip(hex_to_linear(eo.shade(mat["color"], mat.get(k + "_dL", -14), (0, 0))) / col, 0.05, 1.0)
        a = np.clip(mat[k] * st[f], 0, 1)[..., None]
        out = out * (1 + a * (r - 1))
    if extra:
        col = hex_to_linear(mat["color"])
        base = col / out.reshape(-1, 3).mean(0, dtype=np.float64)
        for _ in range(4):
            out2 = np.clip(out * base, 0, 1)
            base *= col / out2.reshape(-1, 3).mean(0, dtype=np.float64)
        out = np.clip(out * base, 0, 1)
    return out


def relief_structure(mat, st):
    """Fields for the normal / mask maps: the saw marks are pressed in a little, like the pores."""
    pores = st["pores"]
    if "saw" in st and mat.get("saw"):
        pores = np.maximum(pores, 0.5 * mat["saw"] * st["saw"])
    if "tail" in st and mat.get("tail"):
        pores = np.maximum(pores, 0.6 * mat["tail"] * st["tail"])
    return dict(st, pores=pores)


def albedo_path(mat):
    return EXT / "Materials" / mat["material"] / (mat["material"] + "_albedo.jpg")


def write_material(mat, st, alb):
    mid = mat["material"]
    folder = EXT / "Materials" / mid
    folder.mkdir(parents=True, exist_ok=True)
    rgb = np.round(mf.linear_to_srgb(alb) * 255).astype(np.uint8)
    Image.fromarray(rgb).save(folder / f"{mid}_albedo.jpg", quality=90, subsampling=0, optimize=True)
    rs = relief_structure(mat, st)
    Image.fromarray(eo.normal_map(rs)).save(folder / f"{mid}_normal.jpg", quality=92, subsampling=0, optimize=True)
    Image.fromarray(eo.mask_map(mat, rs)).save(folder / f"{mid}_mask.png", optimize=True)


def read_albedo(mat):
    return mf.srgb_to_linear(np.asarray(Image.open(albedo_path(mat)).convert("RGB"), dtype=np.float64) / 255)


def entry(mat):
    mid = mat["material"]
    return {"id": mid, "name": mat["name"], "category": "casegoods", "source": SOURCE, "neutral": False,
            "metersPerTile": list(TILE_M), "maxSize": ALBEDO[0], "folder": f"Materials/{mid}",
            "textures": {"albedo": f"{mid}_albedo.jpg", "normal": f"{mid}_normal.jpg", "mask": f"{mid}_mask.png"}}


def write_entries(merge=True):
    done = [m for m in MATERIALS if albedo_path(m).exists()]
    ENTRIES.parent.mkdir(parents=True, exist_ok=True)
    ENTRIES.write_text(json.dumps([entry(m) for m in done], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("entries", ENTRIES.relative_to(ROOT), len(done))
    if merge:
        merge_entries.merge([str(ENTRIES)])


def de76(a_lin, b_lin):
    return float(np.linalg.norm(linear_to_lab(a_lin) - linear_to_lab(b_lin)))


# ------------------------------------------------------------------------------------------------ catalogue
def _pdf():
    import pymupdf                                            # only for --sheet / --analyze
    sys.path.insert(0, str(ROOT / "tools" / "casegoods" / "gen"))
    import catpage
    return catpage, pymupdf.open(catpage.PDF)


def cat_crop(cp, doc, page, crop, dpi=300):
    pg = doc[page - 1]
    return cp.render(pg, dpi, cp.frac_rect(pg, crop))


def lstats(img_srgb):
    """L* std of the detail (the swatch's print: 3 px blur removed as noise), a*/b* slopes against L*."""
    lab = linear_to_lab(mf.srgb_to_linear(np.asarray(img_srgb, dtype=np.float64) / 255))
    L = lab[..., 0]
    det = L - mf.blur(L, 25, 25)
    a = lab[..., 1] - mf.blur(lab[..., 1], 25, 25)
    b = lab[..., 2] - mf.blur(lab[..., 2], 25, 25)
    k = (det * det).sum() + 1e-9
    return float(L.std()), float(det.std()), float((det * a).sum() / k), float((det * b).sum() / k)


def tex_at(alb_lin, grain, mm_w, size):
    """A crop of the texture showing mm_w mm across, grain as in the reference ('x' along its width, 'y' along its
    height), resized to `size` (w, h) px like the print."""
    w, h = size
    mm_h = mm_w * h / w
    if grain == "x":
        cw, ch = int(mm_w * PX), int(mm_h * PX)
        v = alb_lin[300:300 + ch, 500:500 + cw]
    else:
        cw, ch = int(mm_h * PX), int(mm_w * PX)
        v = np.transpose(alb_lin[300:300 + ch, 500:500 + cw], (1, 0, 2))
    img = Image.fromarray(np.round(mf.linear_to_srgb(v) * 255).astype(np.uint8))
    return img.resize(size, Image.LANCZOS)


def analyze(mats, albs):
    cp, doc = _pdf()
    print("%-22s %-8s %-8s %5s  %-22s %-22s" % ("material", "swatch", "texture", "dE76", "swatch L*std/det a/L b/L",
                                                "texture L*std/det a/L b/L"))
    for m in mats:
        tex = albs[m["id"]]
        tmean = tex.reshape(-1, 3).mean(0)
        if not m["swatch"]:
            print("%-22s %-8s %-8s %5.2f  (no swatch)" % (m["id"], m["color"], linear_to_hex(tmean),
                                                          de76(tmean, hex_to_linear(m["color"]))))
            continue
        page, crop, grain, mm_w = m["swatch"]
        sw = cat_crop(cp, doc, page, crop)
        hx, _ = cp.swatch(doc[page - 1], crop)
        ts = tex_at(tex, grain, mm_w, sw.size).filter(ImageFilter.GaussianBlur(1.0))
        s1, s2 = lstats(sw), lstats(ts)
        print("%-22s %-8s %-8s %5.2f  %5.1f %4.1f %5.2f %5.2f   %5.1f %4.1f %5.2f %5.2f" % (
            m["id"], hx, linear_to_hex(tmean), de76(tmean, hex_to_linear(hx)), *s1, *s2))


def _font(size):
    for f in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial Unicode.ttf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def sheet(mats, albs, out):
    """Per material: swatch crop | catalogue photo crop | texture at the swatch's scale | 1 m x 1 m | the whole tile |
    30 cm at 1 px/mm (the pores, knots and cracks as the texture carries them)."""
    cp, doc = _pdf()
    f1, f2 = _font(15), _font(12)
    H = 300
    rows = []
    for m in mats:
        tex = albs[m["id"]]
        tmean = tex.reshape(-1, 3).mean(0)
        target = hex_to_linear(m["color"])
        cells = []
        if m["swatch"]:
            page, crop, grain, mm_w = m["swatch"]
            sw = cat_crop(cp, doc, page, crop)
            ts = tex_at(tex, grain, mm_w, sw.size)
            z = H / sw.height
            cells.append(("swatch p.%d" % page, sw.resize((int(sw.width * z), H), Image.NEAREST)))
        else:
            grain, mm_w = "x", 320
        if m["photo"]:
            ph = cat_crop(cp, doc, m["photo"][0], m["photo"][1], 200)
            z = H / ph.height
            if ph.width * z > 700:
                z = 700 / ph.width
            cells.append(("photo p.%d" % m["photo"][0], ph.resize((int(ph.width * z), int(ph.height * z)),
                                                                   Image.LANCZOS)))
        if m["swatch"]:
            cells.append(("texture at swatch scale (%d mm)" % mm_w,
                          ts.resize((int(ts.width * H / ts.height), H), Image.NEAREST)))
        else:
            ts = tex_at(tex, "x", 320, (320, 160))
            cells.append(("texture 320 mm (no swatch)", ts.resize((600, 300), Image.LANCZOS)))
        one = Image.fromarray(np.round(mf.linear_to_srgb(tex[0:1024, 0:1024]) * 255).astype(np.uint8))
        cells.append(("1 m x 1 m", one.resize((H, H), Image.LANCZOS)))
        wide = Image.fromarray(np.round(mf.linear_to_srgb(tex) * 255).astype(np.uint8)).resize((600, 300),
                                                                                             Image.LANCZOS)
        cells.append(("whole tile 2 x 1 m", wide))
        det = Image.fromarray(np.round(mf.linear_to_srgb(tex[600:900, 1200:1500]) * 255).astype(np.uint8))
        cells.append(("300 mm at 1 px/mm", det))
        W = sum(c.width + 12 for _, c in cells)
        row = Image.new("RGB", (W, H + 40), "white")
        d = ImageDraw.Draw(row)
        d.text((4, 2), "%s  «%s»   target %s   texture %s   dE76 %.2f" % (
            m["id"], m["name"], m["color"], linear_to_hex(tmean), de76(tmean, target)), fill="black", font=f1)
        x = 0
        for label, c in cells:
            row.paste(c, (x, 36))
            d.text((x + 2, 20), label, fill=(80, 80, 80), font=f2)
            x += c.width + 12
        rows.append(row)
    W = max(r.width for r in rows)
    img = Image.new("RGB", (W, sum(r.height + 10 for r in rows)), "white")
    y = 0
    for r in rows:
        img.paste(r, (0, y))
        y += r.height + 10
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print("sheet", out)


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--no-write", action="store_true", help="use the written albedos, write nothing but the sheet")
    ap.add_argument("--no-merge", action="store_true")
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--sheet-path", default=str(SHEET))
    ap.add_argument("--analyze", action="store_true")
    a = ap.parse_args()
    mats = [m for m in MATERIALS if not a.ids or m["id"] in a.ids]
    if a.ids and len(mats) != len(a.ids):
        sys.exit("unknown id: " + ", ".join(set(a.ids) - {m["id"] for m in mats}))
    cache, albs = {}, {}
    for m in mats:
        if a.no_write:
            albs[m["id"]] = read_albedo(m)
            continue
        st = structure(m, cache)
        alb = albedo_linear(m, st)
        write_material(m, st, alb)
        albs[m["id"]] = read_albedo(m)                         # what Unity gets: the written JPEG
        mean = albs[m["id"]].reshape(-1, 3).mean(0)
        print("%-22s -> %s  mean %s  dE76 %.2f" % (m["id"], albedo_path(m).relative_to(ROOT), linear_to_hex(mean),
                                                  de76(mean, hex_to_linear(m["color"]))))
    if not a.no_write:
        write_entries(merge=not a.no_merge)
    if a.analyze:
        analyze(mats, albs)
    if a.sheet:
        sheet(mats, albs, Path(a.sheet_path))


if __name__ == "__main__":
    main()
