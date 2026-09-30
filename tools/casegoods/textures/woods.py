#!/usr/bin/env python3
"""Casegoods decor textures, family `woods`: the pines, hickory, cedar, birch, wenge prints of the Pinskdrev catalogue
and a neutral solid-wood texture for tinting (wave 6, see tools/casegoods/BRIEF-textures.md).

    python3 tools/casegoods/textures/woods.py                   # textures + entries/woods.json + merge + sheet
    python3 tools/casegoods/textures/woods.py cg_bereza cg_venge # only these (entries keep the others)
    python3 tools/casegoods/textures/woods.py --no-write         # check sheet only (textures kept in memory)
    python3 tools/casegoods/textures/woods.py --no-sheet         # no check sheet (needs no PyMuPDF)

Builds on the door machinery (tools/doors/textures, not edited):
  * eco_oak.wood_structure - sawn boards across the tile, each from its own log (pith line, cut depth -> cathedrals,
    growth rings box-filtered, knots bending the rings, checks along the rings, pores, streaks); the pine / hickory /
    cedar / birch patterns below are new PATTERNS entries of it (added in memory);
  * finish_kit.oak_structure - straight-grain laminations (rings with earlywood / transition / latewood, pore dashes,
    ray flecks, long streaks): wenge, the wenge hardboard, Брауни's black woodgrain and the neutral solid wood;
  * their albedo / normal / mask writers (mean colour solved exactly, OpenGL normals, R metal / G AO / A smooth).
Colour: the target is the catalogue swatch measured the way tools/casegoods/gen/catpage.py measures it (sRGB trimmed
mean, the middle 60 % by brightness); the texture is measured the same way (at the swatch's scale) and its base colour
is corrected until both agree (dE76 printed and written to woods.md). The generator needs numpy + Pillow; the check
sheet (swatch | photo | texture at the swatch's scale | 1 m x 0.5 m) renders the catalogue with PyMuPDF.

Output per material M: Assets/House4696/External/Materials/M/M_albedo.jpg (2048x1024, 2.0 x 1.0 m, grain along U),
M_normal.jpg (1024x512), M_mask.png (256x128); tools/casegoods/textures/entries/woods.json;
tools/casegoods/textures/sheets/woods.png.
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
sys.path.insert(0, str(DOORS))
import make_finishes as mf      # noqa: E402
import eco_oak as eo            # noqa: E402
import finish_kit as kit        # noqa: E402
import merge_entries            # noqa: E402

EXT = mf.EXT
ALBEDO, TILE_M, MM = mf.ALBEDO, mf.TILE_M, mf.MM
hex_to_linear, linear_to_hex, linear_to_lab = mf.hex_to_linear, mf.linear_to_hex, mf.linear_to_lab
linear_to_srgb, srgb_to_linear = mf.linear_to_srgb, mf.srgb_to_linear
PDF = ROOT / "tools" / "casegoods" / "reference" / "catalog_km2.pdf"
ENTRIES = HERE / "entries" / "woods.json"
SHEET = HERE / "sheets" / "woods.png"
SOURCE = "procedural:tools/casegoods/textures/woods.py"

# ------------------------------------------------------------------------------------------------ board patterns
# eco_oak.wood_structure keys (lengths mm): board = width (median, log-sigma, min, max); flat_share = share of
# flat-sawn boards (cathedrals), else rift (straight lines); depth / depth_amp / turns = the cut under the pith line
# (cathedral tips); wave = ring waviness octaves; rings = ring width, earlywood, latewood (pine: late_band);
# pores / rays / knots / pins / checks / sdark / slight; bands / clouds / fibre; broad_mix; relief.
_BASE = dict(pith_in=0.22, rift_out=0.6, pith_wander=0.12, pith_len=400.0, turns=(1, 3), turn_round=28.0, dmin=4.0,
             ecc=0.15, late_fibre=(0.6, 0.5, 4.0), bands=(25.0, 700.0), clouds=(150.0, 500.0), fibre=(0.35, 5.0))
BOARD = {
    # «Сосна Карелия»: white painted pine - fine straight fibres, a few soft arches, rare small knots, faint streaks
    "kareliya": dict(_BASE, seed=9101, rift_out=1.5, pith_wander=0.05,
        board=(150.0, 0.3, 90.0, 260.0), flat_share=0.15, depth=(60.0, 0.4), depth_amp=0.4,
        wave=[(2.0, 350.0, 30.0), (0.6, 90.0, 10.0), (0.2, 30.0, 4.0)],
        rings=dict(ring=(2.6, 0.45), early=(1.0, 0.25), late_band=0.22, trend=6.0),
        zone_len=8.0, pores=dict(len=1.0, wid=0.4, thr=0.3, fill=0.0, late=0.0),
        knots=dict(per_m2=0.35, size=(9.0, 0.35), max=18.0, bump=2.0, flow=2.0, aspect=1.2, rim=0.1,
                   rim_alpha=0.4, halo=0.4, cracked=0.0),
        sdark=dict(per_cm=0.8, width=(0.45, 0.4), length=(160.0, 0.8), alpha=(0.2, 0.7), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.4, width=(0.8, 0.4), length=(120.0, 0.8), alpha=(0.2, 0.7), fade=0.8, slope=0.002),
        broad_mix=(0.4, 0.35, 0.35), fibre=(0.3, 6.0),
        relief=dict(pores=0.0, checks=2.0, rays=0.0, rim=0.4, fibre=0.6, late=0.8, tilt_deg=2.5)),
    # «Сосна Рандерс 540 SWN»: white-washed pine, grey lines and streaks, small pale knots, synchronised pores
    "randers": dict(_BASE, seed=9201, rift_out=1.2, pith_wander=0.06,
        board=(160.0, 0.3, 100.0, 260.0), flat_share=0.2, depth=(55.0, 0.4), depth_amp=0.5,
        wave=[(2.5, 320.0, 30.0), (0.8, 90.0, 11.0), (0.3, 30.0, 4.0)],
        rings=dict(ring=(3.8, 0.45), early=(1.2, 0.25), late_band=0.25, trend=6.0),
        zone_len=8.0, pores=dict(len=1.2, wid=0.35, thr=0.6, fill=0.3, late=0.25),
        knots=dict(per_m2=0.7, size=(10.0, 0.4), max=22.0, bump=2.2, flow=2.0, aspect=1.25, rim=0.12,
                   rim_alpha=0.45, halo=0.5, cracked=0.2),
        sdark=dict(per_cm=1.0, width=(0.5, 0.4), length=(200.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.6, width=(0.9, 0.45), length=(150.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        broad_mix=(0.45, 0.35, 0.35), fibre=(0.3, 6.0),
        relief=dict(pores=0.6, checks=2.0, rays=0.0, rim=0.5, fibre=0.5, late=1.0, tilt_deg=3.5)),
    # «Сосна Джексон»: weathered brushed pine - wide rings with deep dark latewood, big knots, checks, grey patina
    "jackson": dict(_BASE, seed=9301,
        board=(180.0, 0.3, 110.0, 280.0), flat_share=0.45, depth=(60.0, 0.4), depth_amp=0.5, max_slope=0.09, dmin=14.0,
        wave=[(4.5, 240.0, 28.0), (1.6, 80.0, 10.0), (0.6, 25.0, 4.0)],
        rings=dict(ring=(2.7, 0.45), early=(0.9, 0.3), late_band=0.33, trend=6.0, vary=0.5),
        zone_len=5.0, pores=dict(len=1.5, wid=0.35, thr=0.3, fill=0.35, late=0.2),
        knots=dict(per_m2=1.6, size=(20.0, 0.45), max=45.0, bump=2.8, flow=2.2, aspect=1.35, rim=0.12,
                   rim_alpha=0.85, halo=0.7, cracked=0.7),
        pins=dict(per_m2=3.0, size=(4.0, 0.3), max=8.0, aspect=1.2, rim=0.3, rim_alpha=0.6, halo=0.3),
        checks=dict(per_m2=6.0, length=(150.0, 0.7), width=(1.0, 0.45), wiggle=1.2),
        sdark=dict(per_cm=1.2, width=(0.6, 0.5), length=(180.0, 0.8), alpha=(0.3, 1.0), fade=0.8, slope=0.002),
        slight=dict(per_cm=2.0, width=(1.2, 0.5), length=(140.0, 0.8), alpha=(0.3, 1.0), fade=0.8, slope=0.002),
        broad_mix=(0.5, 0.45, 0.45), clouds=(60.0, 300.0), fibre=(0.35, 4.0),
        relief=dict(pores=0.6, checks=2.5, rays=0.0, rim=0.8, fibre=0.5, late=1.4, tilt_deg=6.0)),
    # «Гикори Кингстон 579 SWN»: light hickory / rustic oak - long planks, soft cathedrals, small knots, short checks
    "gikori": dict(_BASE, seed=9401,
        board=(170.0, 0.3, 100.0, 280.0), flat_share=0.55, depth=(55.0, 0.4), depth_amp=0.5, max_slope=0.1, dmin=12.0,
        wave=[(4.0, 260.0, 30.0), (1.4, 90.0, 12.0), (0.5, 35.0, 5.0)],
        rings=dict(ring=(3.0, 0.4), early=(0.8, 0.25), late_gamma=1.6, trend=6.0, vary=0.4),
        zone_len=6.0, pores=dict(len=0.9, wid=0.35, thr=0.0, fill=0.9, late=0.08),
        rays=dict(per_cm=1.0, width=(0.35, 0.3), length=(8.0, 0.6), alpha=(0.2, 0.5), fade=0.6, slope=0.0),
        knots=dict(per_m2=1.2, size=(8.0, 0.45), max=20.0, bump=2.4, flow=2.2, aspect=1.3, rim=0.14,
                   rim_alpha=0.85, halo=0.6, cracked=0.5),
        pins=dict(per_m2=5.0, size=(2.8, 0.3), max=5.0, aspect=1.2, rim=0.3, rim_alpha=0.6, halo=0.3),
        checks=dict(per_m2=4.0, length=(110.0, 0.7), width=(0.9, 0.4), wiggle=0.9),
        sdark=dict(per_cm=0.8, width=(0.5, 0.45), length=(160.0, 0.8), alpha=(0.2, 0.9), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.5, width=(0.8, 0.45), length=(100.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        broad_mix=(0.55, 0.45, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.25, late=0.25, tilt_deg=3.0)),
    # «Кедр Орегон 537 SWN»: honey cedar / oak planks - open cathedrals, knots
    "kedr": dict(_BASE, seed=9501,
        board=(180.0, 0.3, 110.0, 300.0), flat_share=0.7, depth=(55.0, 0.4), depth_amp=0.5, max_slope=0.1, dmin=12.0,
        wave=[(4.5, 250.0, 30.0), (1.5, 85.0, 12.0), (0.5, 30.0, 5.0)],
        rings=dict(ring=(3.4, 0.4), early=(0.9, 0.25), late_gamma=1.5, trend=6.0, vary=0.45),
        zone_len=5.0, pores=dict(len=0.9, wid=0.35, thr=0.0, fill=0.9, late=0.08),
        rays=dict(per_cm=1.0, width=(0.35, 0.3), length=(8.0, 0.6), alpha=(0.2, 0.5), fade=0.6, slope=0.0),
        knots=dict(per_m2=1.5, size=(11.0, 0.45), max=28.0, bump=2.5, flow=2.2, aspect=1.3, rim=0.13,
                   rim_alpha=0.85, halo=0.6, cracked=0.5),
        pins=dict(per_m2=4.0, size=(3.0, 0.3), max=6.0, aspect=1.2, rim=0.3, rim_alpha=0.6, halo=0.3),
        checks=dict(per_m2=3.0, length=(100.0, 0.7), width=(0.9, 0.4), wiggle=0.9),
        sdark=dict(per_cm=0.8, width=(0.55, 0.45), length=(160.0, 0.8), alpha=(0.2, 0.9), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.5, width=(0.8, 0.45), length=(100.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        broad_mix=(0.6, 0.45, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.25, late=0.25, tilt_deg=3.0)),
    # «Береза 261 SM»: dark flamed crown-cut birch - wide flitches, arches everywhere, thin light ring lines, flecks
    "bereza": dict(_BASE, seed=9601,
        board=(260.0, 0.25, 180.0, 380.0), flat_share=0.95, pith_in=0.18, depth=(20.0, 0.5), depth_amp=0.7,
        turns=(4, 6), turn_round=18.0, max_slope=0.22,
        wave=[(6.0, 180.0, 30.0), (3.0, 60.0, 10.0), (1.0, 20.0, 4.0)],
        rings=dict(ring=(2.4, 0.4), early=(1.4, 0.2), late_band=0.32, trend=5.0, vary=0.5),
        zone_len=4.0, pores=dict(len=1.0, wid=0.4, thr=0.3, fill=0.0, late=0.0),
        rays=dict(per_cm=1.5, width=(0.4, 0.3), length=(3.0, 0.5), alpha=(0.2, 0.6), fade=0.5, slope=0.05),
        pins=dict(per_m2=3.0, size=(2.0, 0.3), max=4.0, aspect=1.1, rim=0.4, rim_alpha=0.5, halo=0.2),
        sdark=dict(per_cm=0.5, width=(0.6, 0.45), length=(120.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.003),
        broad_mix=(0.55, 0.5, 0.4), clouds=(90.0, 300.0), fibre=(0.3, 4.0),
        relief=dict(pores=0.0, checks=0.0, rays=0.2, rim=0.3, fibre=0.2, late=0.3, tilt_deg=1.2)),
}
for _k, _p in BOARD.items():
    eo.PATTERNS["cg_" + _k] = _p                 # in memory only: eco_oak.py itself is not touched

# ------------------------------------------------------------------------------------------------ straight patterns
# finish_kit.oak_structure keys: warp, ring (width median, log-sigma), early / trans shares, ring_tone of earlywood /
# transition / latewood, pores (dash length, duty, alpha), rays / dark / light (line specs), bands, cluster, fibre, relief
STRAIGHT = {
    # «Венге»: wenge - straight dark chocolate stripes, fine lighter parenchyma lines, long open pores
    "venge": dict(
        seed=9701, warp=[(1.6, 380.0, 40.0), (0.4, 70.0, 6.0)],
        ring=(2.2, 0.55), ring_rho=0.3, early=(0.35, 0.08), trans=0.15,
        ring_tone=(1.0, 0.2, -0.9), ring_var=0.6, drift=0.6, drift_len=60.0, hp=6.0,
        pores=dict(len=6.0, duty=0.5, alpha=0.9, late=0.2),
        rays=None,
        dark=dict(per_cm=0.6, width=(1.2, 0.5), length=(300.0, 0.8), alpha=(0.3, 0.9), fade=0.6, slope=0.001),
        light=dict(per_cm=1.4, width=(0.35, 0.35), length=(220.0, 0.9), alpha=(0.3, 1.0), fade=0.7, slope=0.001),
        fade_len=30.0, bands=(14.0, 900.0), cluster=(4.0, 200.0), cluster_share=0.5, band_warp=(4.0, 400.0, 45.0),
        fibre=(0.4, 3.0), fibre_share=0.2,
        relief=dict(pore=1.0, ring=0.3, fibre=0.3, tilt_deg=3.0)),
    # «Черный» of Брауни: near-black woodgrain board - dense fine straight lines, no figure
    "cherny": dict(
        seed=9801, warp=[(1.2, 450.0, 40.0), (0.25, 80.0, 6.0)],
        ring=(1.3, 0.5), ring_rho=0.2, early=(0.35, 0.08), trans=0.2,
        ring_tone=(1.0, 0.3, -0.8), ring_var=0.5, drift=0.7, drift_len=40.0, hp=3.0,
        pores=dict(len=4.0, duty=0.5, alpha=0.8, late=0.2),
        rays=None,
        dark=dict(per_cm=0.3, width=(0.8, 0.5), length=(260.0, 0.8), alpha=(0.2, 0.7), fade=0.7, slope=0.001),
        light=dict(per_cm=0.9, width=(0.35, 0.3), length=(160.0, 0.9), alpha=(0.2, 0.9), fade=0.8, slope=0.001),
        fade_len=25.0, bands=(18.0, 900.0), cluster=(4.0, 220.0), cluster_share=0.5, band_warp=(3.0, 400.0, 45.0),
        fibre=(0.35, 3.0), fibre_share=0.25,
        relief=dict(pore=1.0, ring=0.3, fibre=0.3, tilt_deg=2.5)),
    # neutral solid wood (beech / birch): fine straight grain, soft rings, small ray flecks, closed lacquered pores
    "massiv": dict(
        seed=9901, warp=[(1.5, 400.0, 40.0), (0.3, 80.0, 6.0)],
        ring=(3.0, 0.45), ring_rho=0.5, early=(0.5, 0.1), trans=0.25,
        ring_tone=(0.6, 0.1, -0.7), ring_var=0.4, drift=0.5, drift_len=80.0, hp=6.0,
        pores=dict(len=1.2, duty=0.25, alpha=0.4, late=0.3),
        rays=dict(per_cm=2.0, width=(0.4, 0.3), length=(1.6, 0.5), alpha=(0.2, 0.7), fade=0.3, slope=0.1),
        dark=dict(per_cm=0.25, width=(0.5, 0.4), length=(200.0, 0.8), alpha=(0.15, 0.6), fade=0.8, slope=0.002),
        light=None,
        fade_len=30.0, bands=(20.0, 900.0), cluster=(5.0, 250.0), cluster_share=0.4, band_warp=(3.0, 400.0, 45.0),
        fibre=(0.35, 3.0), fibre_share=0.3,
        relief=dict(pore=0.5, ring=0.3, fibre=0.4, tilt_deg=1.2)),
}


def tint_for(target, grey="#e0e0e0"):
    """The linear _BaseColor tint that makes cg_massiv (albedo mean `grey`) average `target`: target / grey (linear)."""
    return np.clip(hex_to_linear(target) / hex_to_linear(grey), 0, 1)


def lab_to_hex(L, a, b):
    return eo.lab_to_hex(np.array([L, a, b]))


def shade(color, dL, slope=(0.0, 0.0)):
    return eo.shade(color, dL, slope)


# ------------------------------------------------------------------------------------------------ materials
# kind "board" (eco_oak colouring: grain = L* std of the latewood (negative: light lines), tone = broad, fibre;
# pore / ray / streak / knot / rim / check colours; halo = L* darkening round knots) or "straight" (finish_kit
# colouring: comb = L* std of the rings, tone = broad; pore / fleck / dark / light layers). color = the swatch
# (catpage.py value, sRGB); `fit` corrects the base so that the texture measures the same (target stays `color`).
# swatch = (page, crop fractions, mm the crop shows across the grain... (width, height) mm, grain "x" / "y" in it);
# photo = (page, crop, grain) of a product photo / close-up for the sheet.
def _board(mid, name, pattern, color, slope, dark_dL, light_dL, **kw):
    d = dict(id=mid, name=name, kind="board", pattern="cg_" + pattern, color=color,
             dark=shade(color, -dark_dL, slope), light=shade(color, light_dL, slope))
    d.update(kw)
    return d


def _straight(mid, name, pattern, color, **kw):
    d = dict(id=mid, name=name, kind="straight", pattern=pattern, color=color)
    d.update(kw)
    return d


MATERIALS = [
    _board("cg_sosna_kareliya", "Сосна Карелия 528 SWA", "kareliya", "#e6e7e1", (0.0, -0.25), 9.0, 2.5,
           grain=1.1, tone=0.55, fibre=0.45, streak=0.35, knot="#c9c2ae", rim="#b3aa95", halo=1.5, smooth=0.36,
           swatch=(128, (0.715, 0.865, 0.772, 0.90), (260.0, 105.0), "y"),
           photo=(122, (0.233, 0.71, 0.33, 0.90), "y")),
    _board("cg_sosna_randers", "Сосна Рандерс 540 SWN", "randers", "#c7c8c3", (0.0, -0.15), 16.0, 5.0,
           grain=1.2, tone=0.9, fibre=0.6, streak=0.35, pore=0.35, pore_col="#a4a59f", knot="#9e9887",
           rim="#7c7667", halo=3.0, smooth=0.34,
           swatch=(122, (0.715, 0.865, 0.738, 0.90), (110.0, 95.0), "y"),
           photo=(122, (0.233, 0.71, 0.33, 0.90), "y")),
    _board("cg_sosna_jackson", "Сосна Джексон", "jackson", "#6e6a60", (0.0, -0.08), 22.0, 16.0,
           grain=6.5, tone=4.5, fibre=1.3, streak=0.8, pore=0.4, pore_col="#3b352c", knot="#3a3027",
           rim="#1f1914", check="#1c1712", halo=6.0, smooth=0.28,
           swatch=(96, (0.715, 0.86, 0.775, 0.905), (420.0, 185.0), "x"),
           photo=(95, (0.235, 0.71, 0.41, 0.90), "y")),
    _board("cg_gikori_kingston", "Гикори Кингстон 579 SWN", "gikori", "#a1876f", (0.05, 0.2), 20.0, 10.0,
           grain=3.4, tone=3.0, fibre=0.9, streak=0.5, pore=0.45, pore_col="#7a6049", ray=0.3, ray_col="#8e7560",
           knot="#5a4332", rim="#35261b", check="#3a2c20", halo=5.0, smooth=0.34,
           swatch=(115, (0.845, 0.86, 0.895, 0.905), (300.0, 160.0), "y"),
           photo=(11, (0.15, 0.73, 0.55, 0.84), "x")),
    _board("cg_kedr_oregon", "Кедр Орегон 537 SWN", "kedr", "#a47e5a", (0.15, 0.35), 22.0, 11.0,
           grain=4.0, tone=3.2, fibre=0.9, streak=0.5, pore=0.45, pore_col="#76553a", ray=0.3, ray_col="#8e6c4d",
           knot="#553a26", rim="#301f13", check="#34241a", halo=5.0, smooth=0.34,
           swatch=None, photo=(49, (0.33, 0.622, 0.43, 0.642), "x")),
    _board("cg_bereza", "Береза 261 SM", "bereza", "#4b3c3b", (0.05, 0.1), 7.0, 9.0,
           grain=-3.0, tone=2.8, fibre=0.7, streak=0.4, ray=0.15, ray_col="#5a4948", knot="#3a2c2b",
           rim="#2a1f1e", halo=1.0, smooth=0.55,
           swatch=(27, (0.755, 0.865, 0.81, 0.905), (330.0, 150.0), "x"),
           photo=(26, (0.73, 0.71, 0.905, 0.90), "y")),
    _straight("cg_venge", "Венге", "venge", "#2d211b", dark="#1b120d", light="#5a4638", pore="#140c08",
              fleck="#4a3a30", comb=3.0, tone=2.2, pore_k=0.6, dark_k=0.8, light_k=0.55, smooth=0.36,
              swatch=(140, (0.863, 0.852, 0.915, 0.895), (330.0, 160.0), "x"),
              photo=None),
    _straight("cg_dvp_venge", "ДВП ламинированная ВЕНГЕ", "venge", "#46382f", scale=0.75, seed=9711,
              dark="#2f231c", light="#6a5748", pore="#261a13", fleck="#5c4a3d", comb=2.2, tone=1.0, pore_k=0.35,
              dark_k=0.5, light_k=0.4, smooth=0.42, tilt=1.2,
              swatch=None, photo=None),
    _straight("cg_cherny_drevesny", "Черный (Брауни)", "cherny", "#1c1d18", dark="#111210", light="#3a3a33",
              pore="#0c0d0b", fleck="#30302a", comb=2.2, tone=1.0, pore_k=0.5, dark_k=0.6, light_k=0.5, smooth=0.34,
              swatch=(114, (0.826, 0.885, 0.851, 0.908), (160.0, 150.0), "y"),
              photo=(114, (0.09, 0.20, 0.19, 0.40), "y")),
    _straight("cg_massiv", "Массив (бук / береза, под тонировку)", "massiv", "#e0e0e0", dark="#b4b4b4",
              light="#ededed", pore="#a8a8a8", fleck="#c4c4c4", comb=2.2, tone=1.4, pore_k=0.45, fleck_k=0.5,
              dark_k=0.6, smooth=0.45, target="linear",
              swatch=None, photo=(74, (0.325, 0.71, 0.41, 0.90), "y"),
              tints=["#c1966a", "#7e6753", "#8b653e", "#b39a7c"]),
]

# ------------------------------------------------------------------------------------------------ build
def structure(m, cache):
    key = (m["kind"], m["pattern"], m.get("scale", 1.0), m.get("seed"))
    if key not in cache:
        if m["kind"] == "board":
            cache[key] = eo.wood_structure(m["pattern"], m.get("seed"))
        else:
            cache[key] = kit.oak_structure(STRAIGHT[m["pattern"]], m.get("scale", 1.0), m.get("seed"))
    return cache[key]


def albedo(m, st, color):
    f = dict(m, color=color)
    return eo.albedo_linear(f, st) if m["kind"] == "board" else kit.albedo_linear(f, st)


def trimmed_srgb(img):
    """catpage.swatch's statistic: sRGB mean of the middle 60 % of the pixels by brightness (0..255)."""
    im = np.asarray(img, dtype=np.float64).reshape(-1, 3)
    lum = im @ [0.299, 0.587, 0.114]
    order = np.argsort(lum)
    k = len(order)
    return im[order[int(k * 0.2):max(int(k * 0.8), int(k * 0.2) + 1)]].mean(0)


def to8(lin):
    return np.round(linear_to_srgb(lin) * 255).astype(np.uint8)


def at_scale(lin, mm_w, mm_h, px_w, px_h, grain):
    """A crop of mm_w x mm_h of the texture (grain along x as in the albedo, or turned to y), resized to px_w x px_h."""
    w, h = int(round(mm_w / MM)), int(round(mm_h / MM))
    if grain == "y":
        w, h = h, w                    # mm across the grain (image x of the swatch) = albedo rows
    crop = lin[200:200 + h, 300:300 + w]
    img = Image.fromarray(to8(crop))
    if grain == "y":
        img = img.transpose(Image.Transpose.ROTATE_90)
    return img.resize((px_w, px_h), Image.LANCZOS)


def measured(m, lin):
    """The texture measured like the swatch: sRGB trimmed mean of the texture at the swatch's scale (whole tile)."""
    if m.get("target") == "linear" or not m.get("swatch"):
        return 255 * linear_to_srgb(lin.reshape(-1, 3).mean(0))
    # the swatch crop at 150 dpi (catpage) shows mm_w across ~ px: the texture downsized by the same factor
    page, box, (mm_w, mm_h), grain = m["swatch"]
    px_w = (box[2] - box[0]) * 1658 / 72 * 150
    f = px_w / mm_w * MM                # swatch px per texture px (< 1)
    img = Image.fromarray(to8(lin)).resize((max(8, int(ALBEDO[0] * f)), max(8, int(ALBEDO[1] * f))), Image.LANCZOS)
    return trimmed_srgb(img)


def de76(a_srgb, b_srgb):
    la = linear_to_lab(srgb_to_linear(np.asarray(a_srgb) / 255))
    lb = linear_to_lab(srgb_to_linear(np.asarray(b_srgb) / 255))
    return float(np.linalg.norm(la - lb))


def fit_color(m, st):
    """Base colour whose texture measures like the swatch (a few fixed-point steps in linear light)."""
    target = hex_to_linear(m["color"])
    col = target.copy()
    for _ in range(4):
        lin = albedo(m, st, linear_to_hex(col))
        got = srgb_to_linear(measured(m, lin) / 255)
        col = np.clip(col * target / np.maximum(got, 1e-5), 0, 1)
    return linear_to_hex(col)


def write(m, st, lin):
    mid = m["id"]
    folder = EXT / "Materials" / mid
    folder.mkdir(parents=True, exist_ok=True)
    Image.fromarray(to8(lin)).save(folder / f"{mid}_albedo.jpg", quality=90, subsampling=0, optimize=True)
    if m["kind"] == "board":
        nrm, msk = eo.normal_map(st), eo.mask_map(m, st)
    else:
        nrm, msk = kit.normal_map(m, st), kit.mask_map(m, st)
    Image.fromarray(nrm).save(folder / f"{mid}_normal.jpg", quality=92, subsampling=0, optimize=True)
    Image.fromarray(msk).save(folder / f"{mid}_mask.png", optimize=True)
    return srgb_to_linear(np.asarray(Image.open(folder / f"{mid}_albedo.jpg").convert("RGB"), dtype=np.float64) / 255)


def entry(m):
    mid = m["id"]
    return {"id": mid, "name": m["name"], "category": "casegoods", "source": SOURCE, "neutral": False,
            "metersPerTile": list(TILE_M), "maxSize": ALBEDO[0], "folder": f"Materials/{mid}",
            "textures": {"albedo": f"{mid}_albedo.jpg", "normal": f"{mid}_normal.jpg", "mask": f"{mid}_mask.png"}}


def write_entries(merge=True):
    done = [m for m in MATERIALS if (EXT / "Materials" / m["id"] / f"{m['id']}_albedo.jpg").exists()]
    ENTRIES.parent.mkdir(parents=True, exist_ok=True)
    ENTRIES.write_text(json.dumps([entry(m) for m in done], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if merge:
        merge_entries.merge([str(ENTRIES)])
    print("entries", ENTRIES)


# ------------------------------------------------------------------------------------------------ check sheet
def render(page, box, dpi):
    import pymupdf                     # only the sheet needs the catalogue
    doc = pymupdf.open(str(PDF))
    pg = doc[page - 1]
    r = pg.rect
    clip = pymupdf.Rect(r.x0 + box[0] * r.width, r.y0 + box[1] * r.height, r.x0 + box[2] * r.width,
                        r.y0 + box[3] * r.height)
    pix = pg.get_pixmap(dpi=dpi, clip=clip)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def fit_h(img, h):
    return img.resize((max(1, round(img.width * h / img.height)), h), Image.LANCZOS)


def font(size):
    from PIL import ImageFont
    for f in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def cap(img, w):
    """Centre crop to at most w px wide."""
    if img.width <= w:
        return img
    x0 = (img.width - w) // 2
    return img.crop((x0, 0, x0 + w, img.height))


def sheet(rows, path):
    """Per material: swatch | texture at the swatch's scale | product photo / close-up | 1 m x 0.5 m | 1:1 (1 px/mm,
    220 x 240 mm) | (cg_massiv) the tints the finishes multiply it with."""
    H = 240
    f1, f2 = font(15), font(12)
    tiles = []
    for m, lin, res in rows:
        parts, labels = [], []
        if m.get("swatch"):
            page, box, (mm_w, mm_h), grain = m["swatch"]
            sw = cap(fit_h(render(page, box, 300), H), 420)
            parts.append(sw)
            labels.append("swatch p.%d (%s)" % (page, m["color"]))
            parts.append(at_scale(lin, mm_w * sw.width / fit_h(render(page, box, 300), H).width, mm_h, sw.width, H,
                                  grain))
            labels.append("texture, %d mm across" % mm_w)
        if m.get("photo"):
            page, box, grain = m["photo"]
            ph = render(page, box, 250)
            parts.append(cap(fit_h(ph, H), 420))
            labels.append("photo p.%d" % page)
        parts.append(at_scale(lin, 1000.0, 500.0, 480, H, "x"))
        labels.append("texture 1 m x 0.5 m")
        crop = lin[300:300 + H, 900:900 + 220]
        parts.append(Image.fromarray(to8(crop)))
        labels.append("1:1 (1 px/mm)")
        for t in m.get("tints", []):
            tl = np.clip(lin * tint_for(t), 0, 1)
            parts.append(at_scale(tl, 250.0, 120.0, 200, 96, "x"))
            labels.append("tint %s -> %s" % (linear_to_hex(tint_for(t)), t))
        width = sum(p.width + 10 for p in parts)
        tile = Image.new("RGB", (width, H + 46), "white")
        d = ImageDraw.Draw(tile)
        x = 0
        for p, lab in zip(parts, labels):
            tile.paste(p, (x, 44))
            d.text((x, 25), lab, fill=(70, 70, 70), font=f2)
            x += p.width + 10
        d.text((2, 3), "%s  «%s»   texture mean %s   measured like the swatch %s vs %s   dE76 %.2f" % (
            m["id"], m["name"], res["mean"], res["meas"], m["color"], res["de"]), fill="black", font=f1)
        tiles.append(tile)
    W = max(t.width for t in tiles)
    out = Image.new("RGB", (W, sum(t.height + 10 for t in tiles)), "white")
    y = 0
    for t in tiles:
        out.paste(t, (0, y))
        y += t.height + 10
    path.parent.mkdir(parents=True, exist_ok=True)
    out.save(path)
    print("sheet", path)


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--no-sheet", action="store_true")
    ap.add_argument("--no-merge", action="store_true")
    ap.add_argument("--sheet", default=str(SHEET))
    a = ap.parse_args()
    mats = [m for m in MATERIALS if not a.ids or m["id"] in a.ids]
    if a.ids and len(mats) != len(a.ids):
        sys.exit("unknown: " + ", ".join(set(a.ids) - {m["id"] for m in MATERIALS}))
    cache, rows = {}, []
    for m in mats:
        st = structure(m, cache)
        base = fit_color(m, st)
        lin = albedo(m, st, base)
        if not a.no_write:
            lin = write(m, st, lin)                        # measure what Unity gets: the written JPEG
        meas = measured(m, lin)
        res = dict(mean=linear_to_hex(lin.reshape(-1, 3).mean(0)), meas="#%02x%02x%02x" % tuple(np.round(meas).astype(int)),
                   de=de76(meas, [int(m["color"][i:i + 2], 16) for i in (1, 3, 5)]),
                   base=base)
        L = linear_to_lab(lin)[..., 0]
        print("%-20s base %s  mean %s  measured %s  swatch %s  dE76 %.2f  L*std %.2f" % (
            m["id"], base, res["mean"], res["meas"], m["color"], res["de"], float(L.std())))
        rows.append((m, lin, res))
    if not a.no_write:
        write_entries(merge=not a.no_merge)
    if not a.no_sheet:
        sheet(rows, Path(a.sheet))


if __name__ == "__main__":
    main()
