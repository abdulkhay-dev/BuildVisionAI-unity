#!/usr/bin/env python3
"""Door finishes of the entrance steel doors (catalogue pp. 160-187, PDF pages 82-95): two families.

  entrance-metal  the powder-coated steel of the outer (and some inner) sides - "Антик" hammer-effect powder paint on
                  embossed ("декоративное тиснение") or smooth sheet: Антик Серебро, Антик Медь, Лунный камень, and
                  the browner Антик Медь of the Эконом series (УЛЬТРА ЛАЙТ / ПЛЮС / СТАР: other swatch, other photos)
  entrance-panel  the outer MDF panels: WINORIT design panels in PVC film (П-4 Золотой Дуб, П-25 Беленый Дуб,
                  П-26 Французский Дуб, П-28 Тёмная Вишня, Almond 28) and the plain matt "Эко Про" film Graphite Pro
The inner panels (Veralinga, Crosscut, EcoShpon oaks, П-34, Л-11) are other families' finishes.

    python3 tools/doors/textures/entrance.py                          # both families: textures, entries, Finishes
    python3 tools/doors/textures/entrance.py --family entrance-metal  # one family
    python3 tools/doors/textures/entrance.py moonstone --compare      # only these (+ check sheet of their family)
    python3 tools/doors/textures/entrance.py --no-write --compare     # check sheets only
    python3 tools/doors/textures/entrance.py --fit [ids]              # suggest the contrast (comb / grain, tone)
    python3 tools/doors/textures/entrance.py --analyze [ids]          # photo mean colour, hue of its variation

Needs numpy + Pillow; the catalogue photos only for --compare / --fit / --analyze: tools/doors/.cache/photos and
.cache/pdf (both written by tools/doors/catalog_index.py; the inner sides of the GROFF / Эконом doors are only in
pdf/). Output per finish (M = material id, as every door family): Assets/House4696/External/Materials/M/M_albedo.jpg
(sRGB 2048x1024, grain along U, tile 2.0 x 1.0 m, wraps both ways), M_normal.jpg (OpenGL 1024x512), M_mask.png
(256x128: R metallic, G occlusion 255, B 0, A smoothness); per family tools/doors/textures/entries/<family>.json
(merged into external.json), Assets/House4696/Resources/Doors/Finishes/<family>.json and, with --compare,
tools/doors/.cache/finishes_<family>.png.

Structures (PATTERNS; lengths in mm):
  * powder - "Антик" powder coat: a hammered / pebbled surface of irregular cells (periodic jittered-grid Voronoi,
    coordinates warped so the cells are not polygons), dark veins where the cells meet (the network breaks up and
    comes back), cell tops lighter than their rims, per-cell tone, light specks (metallic flakes gathered in small
    irregular clusters), a pixel-scale grain and sparse single flakes; faint broad mottle. Height = cell domes - veins + a fine peel; the mask is metallic
    (`metal`, higher on flakes, lower in the veins) with a satin smoothness. The catalogue renders read it as
    salt-and-pepper speckle (0.4 px/mm); the copper of GROFF / ДиМ is almost smooth there.
  * plain - the matt film Graphite Pro: grain.plain_structure (faint mottle + fine film texture).
  * flitch - printed crown-cut films (П-28 cherry, Almond 28): grain.flitch_structure (flitches, cathedrals, rings,
    pores) with these patterns' own parameters.
  * oak - printed oak films (П-4, П-26, П-25): eco_oak.wood_structure (boards, growth rings, pores, rays) with these
    patterns' own parameters (registered in eco_oak.PATTERNS in memory only).
Colour: the mean in linear light is exactly `color` (the photos' crops); powder / plain / flitch as finish_kit
(ground `comb` x fine + `tone` x broad in L* towards `dark` / `light`, layers dark = veins / pores and light = flakes
at dark_k / light_k), oak as eco_oak (`grain` x latewood + `tone` x broad, pores, rays, streaks).
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import make_finishes as mf          # noqa: E402  (wave 1: colour maths, noise, photo statistics)
import finish_kit as fk             # noqa: E402  (layered colouring, measure / compare sheet)
import grain                        # noqa: E402  (flitch prints, plain films, normal / mask of those)
import eco_oak                      # noqa: E402  (oak prints)
import merge_entries                # noqa: E402

EXT, CACHE, ROOT = mf.EXT, mf.CACHE, mf.ROOT
ALBEDO, NORMAL, MASK, MM = mf.ALBEDO, mf.NORMAL, mf.MASK, mf.MM
W, H = ALBEDO
PX = 1.0 / MM                                   # albedo pixels per mm
SOURCE = "procedural:tools/doors/textures/entrance.py"
FINISHES_DIR = ROOT / "Assets" / "House4696" / "Resources" / "Doors" / "Finishes"
ENTRIES_DIR = HERE / "entries"
FAMILIES = ("entrance-metal", "entrance-panel")

gauss_noise, unit, smoothstep = mf.gauss_noise, fk.unit, fk.smoothstep


# ------------------------------------------------------------------------------------------------ photos
def _photo(fname):
    """A catalogue image: tools/doors/.cache/photos (captioned photos), else .cache/pdf (every embedded image)."""
    for d in ("photos", "pdf"):
        p = CACHE / d / fname
        if p.exists():
            return Image.open(p)
    raise FileNotFoundError(fname)


mf.photo = _photo                   # in memory: make_finishes' photo_crop / as_photo also see .cache/pdf


# ------------------------------------------------------------------------------------------------ patterns
# powder: cell = mean cell size, jitter (0..1) of the cell centres, warp = (amplitude, correlation) of the coordinate
#   warp; vein = (width, correlation of its on/off, bias: > 0 more of the network visible); specks = (sigma of the
#   noise, share of the surface, threshold softness) of the flake clusters; flakes = share of pixels with a single
#   bright flake; mix = weights of per-cell tone, dome shading and pixel grain in the fine tone; mottle = (sigma of
#   the broad clouds, of the larger ones, share of the larger); relief = weights of domes, veins and a fine peel in the height, rms tilt of the normals (deg).
PATTERNS = {
    "antik": dict(
        kind="powder", seed=8101, cell=4.5, jitter=0.95, warp=(1.1, 5.0),
        vein=(1.2, 9.0, 0.5), specks=(0.5, 0.06, 0.35), flakes=0.02, mix=(0.4, 0.8, 0.35),
        mottle=(25.0, 120.0, 0.5),
        relief=dict(dome=1.0, vein=0.8, peel=0.35, tilt_deg=5.0),
    ),
    # Лунный камень: near-black with light flakes gathered in small clusters (the photos' light specks)
    "moon": dict(
        kind="powder", seed=8201, cell=4.0, jitter=0.95, warp=(1.0, 5.0),
        vein=(1.0, 9.0, 0.0), specks=(0.55, 0.1, 0.35), flakes=0.04, mix=(0.4, 0.6, 0.5),
        mottle=(25.0, 120.0, 0.5),
        relief=dict(dome=1.0, vein=0.6, peel=0.35, tilt_deg=4.5),
    ),
    # Эко Про film (Graphite Pro): a matt solid colour, a very faint mottle and film texture
    "ecopro": dict(kind="plain", seed=8301, mottle=(1.2, 2.5), cloud=70.0, peel=(1.2, 0.25),
                   relief=dict(tilt_deg=0.5)),
    # П-28 Тёмная Вишня: dense fine lines of a cherry print, flitches of different tone, some cathedrals and streaks
    "cherry": dict(
        kind="flitch", seed=8401,
        width=(200.0, 0.3), blend=10.0, crown=0.6, pith=(0.25, 0.75), sweep=(10.0, 600.0),
        h0=(20.0, 60.0), hamp=16.0, hcorr=300.0, hmin=5.0, taper=(0.05, 0.08), period=300.0,
        spacing=(4.5, 0.45), profile="late", K=16, amp_sig=0.5, ring_tone=0.5,
        fade=(0.5, 70.0, 5.0), wobble=[(2.5, 350.0, 45.0), (0.7, 40.0, 5.0), (0.25, 10.0, 1.2)],
        flitch_contrast=0.25, flitch_tone=0.6, bands=(25.0, 700.0), cluster=(4.0, 160.0), cluster_share=0.4,
        pores=dict(per_cm=2.4, width=(0.35, 0.3), length=(12.0, 0.7), alpha=(0.15, 0.55), fade=0.7, slope=0.004),
        streaks=dict(per_cm=0.3, width=(0.8, 0.4), length=(90.0, 0.8), alpha=(0.2, 0.6), fade=0.8, slope=0.002),
        fade_len=12.0, fibre=(0.5, 12.0), fibre_share=0.3,
        relief=dict(ring=0.25, pores=1.0, fibre=0.35, tilt_deg=1.4),
    ),
    # Almond 28: a walnut-like print - bold flame cathedrals up the leaf in wide flitches, dark streaks
    "almond": dict(
        kind="flitch", seed=8501,
        width=(240.0, 0.25), blend=12.0, crown=0.9, pith=(0.3, 0.7), sweep=(12.0, 500.0),
        h0=(15.0, 45.0), hamp=22.0, hcorr=260.0, hmin=5.0, taper=(0.045, 0.07), period=300.0,
        spacing=(6.5, 0.45), profile="late", K=16, amp_sig=0.5, ring_tone=0.5,
        fade=(0.45, 70.0, 6.0), wobble=[(2.5, 350.0, 45.0), (0.7, 40.0, 5.0), (0.25, 10.0, 1.2)],
        flitch_contrast=0.25, flitch_tone=0.55, bands=(25.0, 700.0), cluster=(4.0, 160.0), cluster_share=0.4,
        pores=dict(per_cm=2.2, width=(0.35, 0.3), length=(14.0, 0.7), alpha=(0.15, 0.55), fade=0.7, slope=0.004),
        streaks=None, fade_len=12.0, fibre=(0.5, 12.0), fibre_share=0.3,
        relief=dict(ring=0.25, pores=1.0, fibre=0.35, tilt_deg=1.4),
    ),
    # П-4 Золотой Дуб / П-26 Французский Дуб: crown-cut oak prints - cathedrals, fine straight lines, fine pores,
    # long darker streaks (П-26 more of them), no knots
    "oak-golden": dict(
        kind="oak", seed=8601,
        board=(180.0, 0.25, 110.0, 300.0), flat_share=0.45, pith_in=0.2, rift_out=0.6, pith_wander=0.12,
        pith_len=400.0, depth=(45.0, 0.35), depth_amp=0.6, turns=(1, 3), turn_round=25.0, dmin=4.0, ecc=0.15,
        wave=[(4.0, 260.0, 30.0), (1.5, 90.0, 12.0), (0.5, 35.0, 5.0)],
        rings=dict(ring=(2.4, 0.3), early=(0.6, 0.25), late_gamma=1.6, trend=6.0),
        late_fibre=(0.6, 0.5, 4.0),
        zone_len=6.0,
        pores=dict(len=0.8, wid=0.35, thr=0.1, fill=0.85, late=0.06),
        rays=dict(per_cm=0.8, width=(0.3, 0.3), length=(7.0, 0.6), alpha=(0.2, 0.5), fade=0.6, slope=0.0),
        sdark=dict(per_cm=0.4, width=(0.6, 0.4), length=(160.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.3, width=(0.8, 0.4), length=(100.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        bands=(25.0, 700.0), clouds=(150.0, 500.0), fibre=(0.35, 5.0), broad_mix=(0.55, 0.4, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.3, late=0.25, tilt_deg=2.0),
    ),
    "oak-french": dict(
        kind="oak", seed=8701,
        board=(170.0, 0.3, 100.0, 300.0), flat_share=0.7, pith_in=0.22, rift_out=0.6, pith_wander=0.12,
        pith_len=400.0, depth=(40.0, 0.4), depth_amp=0.65, turns=(1, 3), turn_round=25.0, dmin=4.0, ecc=0.15,
        wave=[(4.5, 260.0, 30.0), (1.6, 90.0, 12.0), (0.5, 35.0, 5.0)],
        rings=dict(ring=(2.8, 0.35), early=(0.7, 0.25), late_gamma=1.5, trend=6.0, vary=0.45),
        late_fibre=(0.6, 0.5, 4.0),
        zone_len=5.0,
        pores=dict(len=0.8, wid=0.35, thr=0.05, fill=0.9, late=0.08),
        rays=dict(per_cm=0.8, width=(0.3, 0.3), length=(7.0, 0.6), alpha=(0.2, 0.5), fade=0.6, slope=0.0),
        sdark=dict(per_cm=0.9, width=(0.6, 0.5), length=(180.0, 0.8), alpha=(0.3, 1.0), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.4, width=(0.8, 0.45), length=(100.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        bands=(25.0, 700.0), clouds=(150.0, 500.0), fibre=(0.35, 5.0), broad_mix=(0.6, 0.4, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.3, late=0.25, tilt_deg=2.0),
    ),
    # П-25 Беленый Дуб: white film with light grey-beige ash-like figure - wide rings, pore bands, bold cathedrals
    "oak-bleached": dict(
        kind="oak", seed=8801,
        board=(200.0, 0.25, 130.0, 320.0), flat_share=0.8, pith_in=0.2, rift_out=0.6, pith_wander=0.12,
        pith_len=400.0, depth=(50.0, 0.35), depth_amp=0.65, turns=(1, 3), turn_round=25.0, dmin=4.0, ecc=0.15,
        wave=[(5.0, 260.0, 30.0), (1.8, 90.0, 12.0), (0.5, 35.0, 5.0)],
        rings=dict(ring=(3.6, 0.3), early=(1.0, 0.25), late_gamma=1.4, trend=6.0),
        late_fibre=(0.6, 0.5, 4.0),
        zone_len=8.0,
        pores=dict(len=0.9, wid=0.4, thr=-0.2, fill=0.95, late=0.05),
        sdark=dict(per_cm=0.2, width=(0.5, 0.4), length=(120.0, 0.8), alpha=(0.2, 0.7), fade=0.8, slope=0.002),
        bands=(25.0, 700.0), clouds=(150.0, 500.0), fibre=(0.35, 5.0), broad_mix=(0.6, 0.35, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.3, late=0.2, tilt_deg=2.0),
    ),
}


# ------------------------------------------------------------------------------------------------ finishes
def _oak(color, slope, dark_dL, light_dL):
    """dark / light ground colours of an oak print: the mean moved by -dark_dL / +light_dL in L* along the photos'
    a*, b* slopes (eco_oak.shade)."""
    return dict(dark=eco_oak.shade(color, -dark_dL, slope), light=eco_oak.shade(color, light_dL, slope))


# family / id / catalogue name / line / tag (the library's label) / material / pattern (+ seed); color = mean of the
# REFS crops (sRGB, linear light); powder / plain / flitch: dark / light = full-strength vein (pore) and flake
# (streak) colours, their strength dark_k / light_k, comb / tone = L* std of the fine / broad tone (--fit);
# oak: as eco_oak (grain, tone, fibre, streak, pore + pore_col, ray + ray_col); smooth = mask alpha / 255;
# metal = mean metallic (powder coats: metallic flakes in a paint film).
FINISHES = [
    dict(family="entrance-metal", id="antik-silver", name="Антик Серебро", line="Металл", tag="порошковая окраска",
         pattern="antik", color="#575757", dark="#303031", light="#8c8c8e", comb=2.18, tone=0.63,
         dark_k=0.25, light_k=0.25, smooth=0.42, metal=0.5),
    dict(family="entrance-metal", id="antik-copper", name="Антик Медь", line="Металл", tag="порошковая окраска",
         pattern="antik", seed=8102, color="#693a34", dark="#4e1c18", light="#7a4e48", comb=0.95, tone=0.57,
         dark_k=0.08, light_k=0.06, smooth=0.42, metal=0.45),
    dict(family="entrance-metal", id="antik-copper-ekonom", name="Антик Медь (Эконом)", line="Металл",
         tag="порошковая окраска", pattern="antik", seed=8103, color="#49342d", dark="#2e1b13",
         light="#5b473f", comb=1.29, tone=0.62, dark_k=0.1, light_k=0.08, smooth=0.40, metal=0.45),
    dict(family="entrance-metal", id="moonstone", name="Лунный камень", line="Металл", tag="порошковая окраска",
         pattern="moon", color="#333237", dark="#1c1b1f", light="#6d6c74", comb=2.47, tone=0.7,
         dark_k=0.15, light_k=0.45, smooth=0.40, metal=0.45),
    dict(family="entrance-panel", id="winorit-p4", name="П-4 (Золотой Дуб)", line="WINORIT", tag="WINORIT",
         pattern="oak-golden", color="#8c5f23", **_oak("#8c5f23", (-0.2, 0.27), 18, 10),
         grain=2.38, tone=2.92, fibre=0.6, streak=0.4, pore=0.35, pore_col="#6a4415", ray=0.2, ray_col="#9c6f30",
         smooth=0.40),
    dict(family="entrance-panel", id="winorit-p25", name="П-25 (Беленый Дуб)", line="WINORIT", tag="WINORIT",
         pattern="oak-bleached", color="#e7e2da", **_oak("#e7e2da", (-0.05, 0.16), 16, 3),
         grain=1.98, tone=1.65, fibre=0.35, streak=0.3, pore=0.5, pore_col="#b5afa3", smooth=0.40),
    dict(family="entrance-panel", id="winorit-p26", name="П-26 (Французский Дуб)", line="WINORIT", tag="WINORIT",
         pattern="oak-french", color="#5c3b1a", **_oak("#5c3b1a", (0.06, 0.37), 14, 10),
         grain=5.38, tone=2.05, fibre=0.7, streak=0.6, pore=0.4, pore_col="#3f250c", ray=0.2, ray_col="#6a4824",
         smooth=0.40),
    dict(family="entrance-panel", id="winorit-p28", name="П-28 (Тёмная Вишня)", line="WINORIT", tag="WINORIT",
         pattern="cherry", color="#3a2a27", dark="#21120e", light="#4c3c38", comb=1.80, tone=3.75, smooth=0.40),
    dict(family="entrance-panel", id="almond-28", name="Almond 28", line="WINORIT", tag="WINORIT",
         pattern="almond", color="#422c27", dark="#27130d", light="#553e38", comb=2.21, tone=1.70, smooth=0.40),
    dict(family="entrance-panel", id="graphite-pro", name="Graphite Pro", line="Эко про", tag="Эко Про",
         pattern="ecopro", color="#434750", dark="#3e424b", light="#484c55", comb=0.19, tone=0.14, smooth=0.30),
]
for _f in FINISHES:
    _f["material"] = "door_" + _f["id"].replace("-", "_")


# ------------------------------------------------------------------------------------------------ catalogue crops
# Flat areas (file, (x0, y0, x1, y1)): photos/ = captioned outer sides, pdf/cat-<page>_<n> = the inner sides beside
# them. Boxes keep off the peephole, the lock and handle, the mouldings and the decorative strips; the first one of
# each finish is on the check sheet. Renders of one layout share the boxes.
_LINES_B = [(40, 135, 175, 300), (205, 135, 330, 300), (100, 335, 330, 505), (40, 535, 330, 700)]  # 4 strips, big
_LINES_S = [(14, 58, 70, 128), (88, 58, 142, 128), (40, 140, 142, 210), (14, 222, 142, 292)]      # the same, small
_PLAIN_B = [(80, 40, 175, 370), (205, 40, 330, 370), (110, 480, 330, 780)]                        # Эконом, big


def _R(fname, boxes):
    return [(fname, b) for b in boxes]


REFS = {
    "antik-silver": _R("p166_optim-termo-222__antik-serebro-cappuccino-veralinga-wp.jpg", [(175, 60, 330, 780)])
    + _R("p170_dim-universal-ep-22__antik-serebro-cappuccino-veralinga-wp.jpg", _LINES_B)
    + _R("p168_optim-termo-204__antik-serebro-cappuccino-veralinga.jpg",
         [(90, 60, 330, 290), (120, 300, 330, 480), (40, 490, 330, 780)])
    + _R("p182_optim-flesh__antik-serebro-wenge-veralinga-reflex.jpg", _LINES_B)
    + _R("p183_optim-prof__antik-serebro-cappuccino-veralinga-wp.jpg",
         [(140, 290, 330, 400), (140, 425, 330, 540), (140, 560, 330, 680)])
    + _R("p184_optim-nova__antik-serebro-p-34-shimo-svetlyy.jpg",
         [(40, 170, 170, 290), (200, 170, 330, 290), (120, 300, 330, 630)])
    + _R("p162_groff-t2-223__antik-serebro-cappuccino-veralinga-wp.jpg", _LINES_S),
    "antik-copper": _R("p162_groff-t2-223__antik-med-wenge-veralinga-bs.jpg", [(300, 60, 340, 780)] + _LINES_B)
    + _R("p171_dim-universal-ep-22__antik-med-wenge-veralinga-bs.jpg",
         [(40, 135, 180, 300), (215, 135, 340, 300), (100, 335, 340, 505), (40, 535, 340, 700)])
    + _R("p171_dim-universal-ep-29__antik-med-cappuccino-veralinga-wp.jpg", _LINES_S),
    "antik-copper-ekonom": _R("p187_ultra-plyus__antik-med.jpg", [(205, 40, 330, 780), (80, 40, 175, 370)])
    + _R("p186_ultra-layt__antik-med-l-11-italoreh.jpg", _PLAIN_B)
    + _R("cat-95_6.jpg", [(40, 40, 175, 370), (205, 40, 290, 370), (40, 480, 280, 780)])
    + _R("p186_ultra-star__antik-med.jpg", [(35, 20, 70, 300), (85, 20, 140, 75), (85, 95, 140, 300)])
    + _R("cat-95_3.jpg", [(15, 20, 70, 280), (85, 95, 118, 300)]),
    "moonstone": _R("p181_optim-tehno__lunnyy-kamen-cappuccino-veralinga-wp.jpg",
                    [(80, 135, 175, 300), (205, 135, 330, 300), (100, 335, 330, 505), (40, 535, 330, 700)])
    + _R("p180_optim-layn__lunnyy-kamen-cappuccino-crosscut.jpg",
         [(80, 135, 175, 300), (205, 135, 330, 300), (100, 335, 330, 505), (40, 535, 330, 700)])
    + _R("p170_dim-universal-ep-22__lunnyy-kamen-grey-veralinga-s.jpg", _LINES_S),
    "winorit-p28": _R("p163_groff-p3-301__p-28-temnaya-vishnya.jpg",
                      [(122, 240, 272, 440), (122, 590, 272, 700), (122, 140, 172, 205), (306, 60, 340, 220), (306, 290, 340, 720),
                       (36, 60, 78, 290), (36, 480, 78, 790)])
    + _R("cat-83_6.jpg", [(112, 240, 258, 440), (26, 60, 70, 780), (300, 60, 340, 290)])
    + _R("p164_groff-p3-302__p-28-temnaya-vishnya-p-25-belenyy-dub.jpg", [(15, 15, 38, 120), (15, 12, 145, 38)]),
    "winorit-p4": _R("p164_groff-p3-302__p-4-zolotoy-dub.jpg",
                     [(36, 110, 90, 290), (95, 35, 285, 85), (30, 740, 340, 800), (295, 110, 340, 230)])
    + _R("cat-84_4.jpg", [(95, 35, 285, 85), (36, 110, 85, 230), (290, 95, 335, 280)]),
    "winorit-p26": _R("p163_groff-p3-303__p-26-francuzskiy-dub-p-25-belenyy-dub.jpg",
                      [(130, 15, 143, 330), (15, 15, 28, 120), (15, 12, 148, 32)]),
    "winorit-p25": _R("cat-83_7.jpg", [(12, 15, 30, 330), (12, 12, 140, 30), (128, 15, 140, 120)])
    + _R("cat-84_1.jpg", [(14, 16, 138, 36), (120, 15, 140, 120)]),
    "almond-28": _R("p176_porta-s-51-p61__almond-28-bianco-veralinga-reflex.jpg",
                    [(302, 95, 342, 735), (32, 40, 86, 290), (32, 490, 86, 790), (32, 732, 340, 795)])
    + _R("p174_porta-s-4-p22__almond-28-cappuccino-veralinga-wp.jpg", [(40, 180, 140, 225), (30, 235, 140, 330)])
    + _R("p175_porta-s-9-p29__almond-28-cappuccino-veralinga-wp.jpg", [(30, 20, 85, 330)])
    + _R("p178_porta-s-55-55__almond-28.jpg", [(128, 20, 143, 330), (12, 292, 143, 330)]),
    "graphite-pro": _R("p177_porta-s-10-p50__graphite-pro-virgin.jpg",
                       [(200, 40, 330, 180), (200, 360, 330, 490), (40, 510, 180, 645)])
    + _R("p174_porta-s-4-l22__graphite-pro-nordic-oak-ww.jpg", [(40, 180, 140, 225)]),
}


# ------------------------------------------------------------------------------------------------ powder coat
def voronoi(rng, cell, jitter, dx, dy):
    """Periodic cells over the albedo grid: a jittered grid of nx x ny centres (spacing ~cell px) wrapping both ways;
    per pixel (displaced by dx, dy px) the distances to the nearest and second nearest centre and the nearest one's
    index."""
    nx, ny = max(2, round(W / cell)), max(2, round(H / cell))
    sx, sy = W / nx, H / ny
    ptx = (np.arange(nx)[None, :] + 0.5 + jitter * rng.uniform(-0.5, 0.5, (ny, nx))) * sx
    pty = (np.arange(ny)[:, None] + 0.5 + jitter * rng.uniform(-0.5, 0.5, (ny, nx))) * sy
    X = np.arange(W)[None, :] + dx
    Y = np.arange(H)[:, None] + dy
    ci = np.floor(X / sx).astype(np.int64)
    cj = np.floor(Y / sy).astype(np.int64)
    f1 = np.full((H, W), np.inf)
    f2 = np.full((H, W), np.inf)
    cid = np.zeros((H, W), np.int64)
    for dj in (-1, 0, 1):
        for di in (-1, 0, 1):
            i, j = ci + di, cj + dj
            ii, jj = i % nx, j % ny
            d = np.hypot(X - (ptx[jj, ii] + (i // nx) * W), Y - (pty[jj, ii] + (j // ny) * H))
            near = d < f1
            f2 = np.where(near, f1, np.minimum(f2, d))
            cid = np.where(near, jj * nx + ii, cid)
            f1 = np.where(near, d, f1)
    return f1, f2, cid, nx * ny


def powder_structure(p, seed=None):
    """Fields of an "Антик" powder coat (see the module docstring): fine / broad tone (unit std), dark = veins,
    light = specks and flakes (0..1), height, metal (0..1, where the flakes are)."""
    rng = np.random.default_rng(p["seed"] if seed is None else seed)
    amp, corr = p["warp"]
    dx = gauss_noise(rng, (H, W), corr * PX, corr * PX) * (amp * PX)
    dy = gauss_noise(rng, (H, W), corr * PX, corr * PX) * (amp * PX)
    f1, f2, cid, n = voronoi(rng, p["cell"] * PX, p["jitter"], dx, dy)
    vw, vcorr, vbias = p["vein"]
    vein = 1 - smoothstep(0.0, max(0.8, vw * PX), f2 - f1)
    vein *= smoothstep(-0.9, 0.9, gauss_noise(rng, (H, W), vcorr * PX, vcorr * PX) + vbias)   # the network breaks
    r = f1 / (0.5 * p["cell"] * PX)
    dome = np.clip(1 - r * r, -0.6, 1.0)                  # a pebble / hammer dent per cell: light top, darker rim
    ctone = rng.standard_normal(n)[cid]
    # specks: flakes gathered in irregular clusters (thresholded fine noise), each of its own brightness
    sig, share, soft = p["specks"]
    g = gauss_noise(rng, (H, W), sig * PX, sig * PX)
    thr = float(np.quantile(g, 1 - share))
    specks = smoothstep(thr - soft, thr + soft, g) * np.clip(0.75 + 0.25 * gauss_noise(rng, (H, W), 3.0, 3.0), 0, 1)
    flakes = smoothstep(1 - p["flakes"], 1 - 0.3 * p["flakes"], rng.uniform(0, 1, (H, W)))
    light = 1 - (1 - specks) * (1 - flakes)
    grain_px = gauss_noise(rng, (H, W), 0.45, 0.45)
    a, b, c = p["mix"]
    fine = unit(a * ctone + b * unit(dome) + c * grain_px)
    s1, s2, share2 = p["mottle"]
    broad = unit(math.sqrt(1 - share2) * gauss_noise(rng, (H, W), s1 * PX, s1 * PX) +
                 math.sqrt(share2) * gauss_noise(rng, (H, W), s2 * PX, s2 * PX))
    rel = p["relief"]
    peel = gauss_noise(rng, (H, W), 1.2 * PX, 1.2 * PX)
    height = rel["dome"] * unit(dome) - rel["vein"] * 2.0 * vein + rel["peel"] * peel
    metal = np.clip(0.5 + 0.5 * light - 0.6 * vein + 0.15 * dome, 0.0, 1.0)
    return dict(fine=fine, broad=broad, dark=vein, light=light, height=height, tilt=rel["tilt_deg"],
                metal=metal, relief=rel)


# ------------------------------------------------------------------------------------------------ structures, maps
def structure(fin, cache):
    """The pattern fields of a finish, shared by the finishes of the same pattern and seed."""
    key = (fin["pattern"], fin.get("seed"))
    if key not in cache:
        p = PATTERNS[fin["pattern"]]
        if p["kind"] == "powder":
            st = powder_structure(p, key[1])
        elif p["kind"] == "plain":
            st = grain.plain_structure(p, key[1])
        elif p["kind"] == "flitch":
            st = grain.flitch_structure(p, key[1])
        else:
            pid = "entrance:" + fin["pattern"]
            eco_oak.PATTERNS[pid] = p                   # in memory only: eco_oak.py itself is not touched
            st = eco_oak.wood_structure(pid, key[1])
        st["kind"] = p["kind"]
        cache[key] = st
    return cache[key]


def albedo_linear(fin, st):
    """Linear-RGB albedo; its mean is exactly the finish's colour."""
    if st["kind"] == "oak":
        return eco_oak.albedo_linear(fin, st)
    return fk.albedo_linear(fin, st)


def normal_map(fin, st):
    if st["kind"] == "oak":
        return eco_oak.normal_map(st)
    return grain.normal_map(st)


def mask_map(fin, st):
    """Powder coats: R metallic (fin["metal"], higher on the flakes, lower in the veins), A smoothness; the films as
    their structures' kits do (R 0)."""
    if st["kind"] == "oak":
        return eco_oak.mask_map(fin, st)
    if st["kind"] != "powder":
        return grain.mask_map(fin, st)
    f = W // MASK[0]
    md = unit(mf.box_down(st["metal"], f))
    vd = unit(mf.box_down(st["dark"], f))
    m = np.zeros((MASK[1], MASK[0], 4), np.uint8)
    m[..., 0] = np.round(np.clip(fin["metal"] * 255 + 10.0 * md, 0, 255)).astype(np.uint8)
    m[..., 1] = 255
    m[..., 3] = np.round(np.clip(fin["smooth"] * 255 - 5.0 * vd, 0, 255)).astype(np.uint8)
    return m


def albedo_path(fin):
    return EXT / "Materials" / fin["material"] / (fin["material"] + "_albedo.jpg")


def write_finish(fin, st, alb):
    mid = fin["material"]
    folder = EXT / "Materials" / mid
    folder.mkdir(parents=True, exist_ok=True)
    rgb = np.round(mf.linear_to_srgb(alb) * 255).astype(np.uint8)
    Image.fromarray(rgb).save(folder / f"{mid}_albedo.jpg", quality=90, subsampling=0, optimize=True)
    Image.fromarray(normal_map(fin, st)).save(folder / f"{mid}_normal.jpg", quality=92, subsampling=0, optimize=True)
    Image.fromarray(mask_map(fin, st)).save(folder / f"{mid}_mask.png", optimize=True)


def read_albedo(fin):
    return mf.srgb_to_linear(np.asarray(Image.open(albedo_path(fin)).convert("RGB"), dtype=np.float64) / 255)


def manifest_entry(fin):
    mid = fin["material"]
    return {"id": mid, "name": f"{fin['name']} ({fin['tag']})", "category": "door", "source": SOURCE,
            "neutral": False, "metersPerTile": list(mf.TILE_M), "maxSize": ALBEDO[0], "folder": f"Materials/{mid}",
            "textures": {"albedo": f"{mid}_albedo.jpg", "normal": f"{mid}_normal.jpg", "mask": f"{mid}_mask.png"}}


def write_family(family, means):
    """entries/<family>.json (merged into external.json) and Resources/Doors/Finishes/<family>.json; finishes not
    rebuilt in this run keep the colour of their written albedo."""
    fins = [f for f in FINISHES if f["family"] == family]
    for f in fins:
        if f["id"] not in means and albedo_path(f).exists():
            means[f["id"]] = read_albedo(f).reshape(-1, 3).mean(0)
    done = [f for f in fins if f["id"] in means]
    ENTRIES_DIR.mkdir(parents=True, exist_ok=True)
    FINISHES_DIR.mkdir(parents=True, exist_ok=True)
    entries = ENTRIES_DIR / f"{family}.json"
    entries.write_text(json.dumps([manifest_entry(f) for f in done], ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")
    merge_entries.merge([str(entries)])
    rows = [{"id": f["id"], "name": f["name"], "line": f["line"], "material": f["material"],
             "color": mf.linear_to_hex(means[f["id"]])} for f in done]
    out = FINISHES_DIR / f"{family}.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("entries", entries, "\nfinishes", out)


# ------------------------------------------------------------------------------------------------ fitting
def contrast_keys(fin):
    return ("grain", "tone") if PATTERNS[fin["pattern"]]["kind"] == "oak" else ("comb", "tone")


def fit(fin, st, rounds=2):
    """The fine / broad contrast that gives the texture, seen like its photos, the photos' L* statistics (the model
    and least squares of finish_kit.fit, with this module's colouring)."""
    ka, kb = contrast_keys(fin)
    f = dict(fin)
    for _ in range(rounds):
        c, t = max(0.2, f[ka]), max(0.2, f[kb])
        rows, got = [], []
        for pc, pt in [(c, t), (c * 1.4, t), (c, t * 1.6)]:
            g = dict(f, **{ka: pc, kb: pt})
            r = fk.measure(REFS, g, albedo_linear(g, st))
            rows.append([1.0, pc * pc, pt * pt])
            got.append([r["t" + k] ** 2 for k in mf.STATS])
        coef = np.linalg.solve(np.array(rows), np.array(got))
        target = np.array([r["p" + k] ** 2 for k in mf.STATS])
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
        f[ka], f[kb] = [round(float(math.sqrt(v)), 2) for v in best[1]]
    r = fk.measure(REFS, f, albedo_linear(f, st))
    print("fit %-20s %s=%.2f, %s=%.2f   " % (f["id"], ka, f[ka], kb, f[kb]) +
          "  ".join("%s %.2f/%.2f" % (k, r["p" + k], r["t" + k]) for k in mf.STATS) + "  dE %.2f" % r["de"])
    return f


# ------------------------------------------------------------------------------------------------ main
def main(argv=None):
    ap = argparse.ArgumentParser(description="entrance door finishes (entrance-metal, entrance-panel)")
    ap.add_argument("finishes", nargs="*", help="finish ids (default: all of the families)")
    ap.add_argument("--family", choices=FAMILIES, help="only this family")
    ap.add_argument("--compare", action="store_true", help="write tools/doors/.cache/finishes_<family>.png")
    ap.add_argument("--no-write", action="store_true", help="do not write textures / entries / Finishes json")
    ap.add_argument("--fit", action="store_true", help="suggest the fine / broad contrast from the photos")
    ap.add_argument("--analyze", action="store_true", help="photo mean colour and the hue of its variation")
    args = ap.parse_args(argv)
    fins = [f for f in FINISHES if (not args.finishes or f["id"] in args.finishes)
            and (not args.family or f["family"] == args.family)]
    if args.finishes and len(fins) != len(args.finishes):
        sys.exit("unknown finish (or not of --family): " + ", ".join(set(args.finishes) - {f["id"] for f in fins}))
    if (args.compare or args.fit or args.analyze) and not (CACHE / "photos").is_dir():
        sys.exit("no catalogue photos in %s: run tools/doors/catalog_index.py first" % (CACHE / "photos"))
    if args.analyze:
        for fin in fins:
            fk.analyze(REFS, fin)
        return
    structures, albedos, means = {}, {}, {}
    for fin in fins:
        st = structure(fin, structures)
        if args.fit:
            fit(fin, st)
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
    for family in FAMILIES:
        fam = [f for f in fins if f["family"] == family]
        if not fam:
            continue
        if not args.no_write:
            write_family(family, dict(means))
        if args.compare:
            fk.compare(dict(id=family, refs=REFS), fam, albedos, CACHE / f"finishes_{family}.png")


if __name__ == "__main__":
    main()
