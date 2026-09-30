#!/usr/bin/env python3
"""Casegoods decor textures, family dark_oaks_b: six rustic / sawn oak melamine films of the Pinskdrev catalogue.

    python tools/casegoods/textures/dark_oaks_b.py                   # textures + entries + merge + check sheet
    python tools/casegoods/textures/dark_oaks_b.py cg_dub_navarra    # only these (entries keep the others)
    python tools/casegoods/textures/dark_oaks_b.py --no-write        # check sheet only (nothing written in Assets)
    python tools/casegoods/textures/dark_oaks_b.py --no-merge        # write, but do not merge into external.json

Materials (id - catalogue decor - chosen swatch):
    cg_dub_stirling        «Дуб Стирлинг 374 SWN»   p. 93  (Гранде chart; Хольтен Лофт p. 134 prints darker)
    cg_dub_tryufelny       «Дуб Трюфельный»         p. 131 (Бритиш Бум «Каркас»; Плато p. 140 prints lighter)
    cg_dub_artizan_tryufel «Дуб Артизан Трюфель»    p. 30  (Ариста, МДФ 19)
    cg_dub_monastyrsky     «Дуб Монастырский 375»   no swatch: the front-on site photo of the Сорренто bedside
                                                    drawer (white-balanced on its «Бордо лайт» plinth) + p. 113
    cg_dub_navarra         «Дуб Наварра»            p. 74  (Деко)
    cg_dub_monterey        «Дуб Монтерей»           p. 64  (Мокко, left half of the swatch)

Builds on the door machinery (tools/doors/textures, not edited): eco_oak.wood_structure (sawn boards from logs:
growth rings, cathedrals, pores, rays, knots, checks, streaks) with this family's patterns registered in memory,
eco_oak.albedo_linear for the ground, knots and checks, finish_kit.straight_lines for the saw marks of the
Sonoma-truffle print. On top of eco_oak: streak layers in their own colours (the grey / pale streaks of the truffle
and smoky decors), saw marks across the grain, and a colour fit: the base colour is solved so that the texture,
seen like the catalogue swatch (downsized to the swatch's scale, trimmed sRGB mean as gen/catpage.py --swatch
measures it), has exactly the swatch's colour.

Output per material M (grain along U = image x, tile 2.0 m x 1.0 m, wraps both ways):
    Assets/House4696/External/Materials/M/M_albedo.jpg (2048x1024 sRGB), M_normal.jpg (1024x512 OpenGL),
    M_mask.png (256x128: R metallic 0, G AO 255, B 0, A smoothness)
    tools/casegoods/textures/entries/dark_oaks_b.json   merged with tools/doors/textures/merge_entries.py
    tools/casegoods/textures/sheets/dark_oaks_b.png     swatch | texture at the swatch's scale | photo | texture at
                                                        the photo's scale | 1 m of texture
Needs numpy + Pillow; PyMuPDF only for the check sheet (catalogue crops).
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
import make_finishes as mf                      # noqa: E402  colour maths, noise
import eco_oak as eo                            # noqa: E402  sawn-oak structure, albedo, normal, mask
import finish_kit as kit                        # noqa: E402  straight lines (saw marks)
import merge_entries                            # noqa: E402

FAMILY = "dark_oaks_b"
SOURCE = "procedural:tools/casegoods/textures/dark_oaks_b.py"
EXT = mf.EXT
ALBEDO, NORMAL, MASK, MM, TILE_M = mf.ALBEDO, mf.NORMAL, mf.MASK, mf.MM, mf.TILE_M
PX = 1.0 / MM
ENTRIES = HERE / "entries" / f"{FAMILY}.json"
SHEET = HERE / "sheets" / f"{FAMILY}.png"
PDF = ROOT / "tools" / "casegoods" / "reference" / "catalog_km2.pdf"
SITE = Path("/private/tmp/claude-501/-Users-abdulxay-Documents-works-ansormed-unity/"
            "56f20183-5ed3-4ca9-b3ff-990484386172/scratchpad/me/so_8C3A1962.jpg")
SWATCH_PX_MM = 0.6          # a catalogue swatch chip (~30 mm printed, 150 dpi) shows ~300 mm of the decor

hex_to_linear, linear_to_hex = mf.hex_to_linear, mf.linear_to_hex
linear_to_srgb, srgb_to_linear, linear_to_lab = mf.linear_to_srgb, mf.srgb_to_linear, mf.linear_to_lab


# ------------------------------------------------------------------------------------------------ patterns
# eco_oak pattern keys (see eco_oak.PATTERNS) + saw = cross-grain saw marks (pitch / width (median mm, log-sigma),
# jitter mm, share_on, strength range, patch (sigma along, across mm) and floor of the patches where they show).
def _base(**kw):
    p = dict(
        board=(170.0, 0.3, 100.0, 290.0), flat_share=0.55, pith_in=0.22, rift_out=0.6, pith_wander=0.12,
        pith_len=400.0, depth=(40.0, 0.4), depth_amp=0.6, turns=(1, 3), turn_round=25.0, dmin=4.0, ecc=0.15,
        wave=[(4.0, 260.0, 30.0), (1.5, 90.0, 12.0), (0.6, 35.0, 5.0)],
        rings=dict(ring=(3.0, 0.35), early=(0.8, 0.25), late_gamma=1.5, trend=6.0, vary=0.45),
        late_fibre=(0.6, 0.5, 4.0), zone_len=5.0,
        pores=dict(len=0.8, wid=0.35, thr=0.0, fill=0.9, late=0.08),
        rays=dict(per_cm=1.2, width=(0.35, 0.3), length=(9.0, 0.6), alpha=(0.2, 0.6), fade=0.6, slope=0.0),
        knots=dict(per_m2=1.5, size=(11.0, 0.45), max=30.0, bump=2.5, flow=2.2, aspect=1.3, rim=0.12,
                   rim_alpha=0.85, halo=0.6, cracked=0.6),
        pins=dict(per_m2=4.0, size=(3.0, 0.3), max=6.0, aspect=1.2, rim=0.3, rim_alpha=0.5, halo=0.3),
        checks=dict(per_m2=6.0, length=(150.0, 0.7), width=(1.0, 0.45), wiggle=1.0),
        sdark=dict(per_cm=0.8, width=(0.6, 0.5), length=(180.0, 0.8), alpha=(0.3, 1.0), fade=0.8, slope=0.002),
        slight=dict(per_cm=0.6, width=(0.8, 0.45), length=(110.0, 0.8), alpha=(0.2, 0.9), fade=0.8, slope=0.002),
        bands=(25.0, 700.0), clouds=(150.0, 500.0), fibre=(0.35, 5.0), broad_mix=(0.55, 0.45, 0.35),
        relief=dict(pores=1.0, checks=2.5, rays=0.3, rim=0.8, fibre=0.3, late=0.25, tilt_deg=3.5),
    )
    for k, v in kw.items():
        p[k] = dict(p[k], **v) if isinstance(v, dict) and isinstance(p.get(k), dict) else v
    return p


PATTERNS = {
    # Гранде 374 SWN: warm honey oak, strong cathedrals and straight lines, scattered dark knots, fine checks
    "cg_stirling": _base(
        seed=8101, board=(185.0, 0.3, 110.0, 300.0), flat_share=0.75, depth=(45.0, 0.4), depth_amp=0.65,
        rings=dict(ring=(3.2, 0.35), early=(0.9, 0.25)),
        knots=dict(per_m2=1.2, size=(10.0, 0.45)), pins=dict(per_m2=3.0),
        checks=dict(per_m2=7.0, length=(170.0, 0.7), width=(0.8, 0.4), wiggle=1.0),
        broad_mix=(0.6, 0.3, 0.35),
    ),
    # Sonoma-truffle: grey-brown, pale grey streaks, soft cathedrals, sawn cross-marks, few knots
    "cg_truffle": _base(
        seed=8201, board=(200.0, 0.3, 120.0, 320.0), flat_share=0.6, depth=(50.0, 0.4), depth_amp=0.6,
        rings=dict(ring=(3.4, 0.35), early=(0.9, 0.25)),
        knots=dict(per_m2=0.6, size=(10.0, 0.4)), pins=dict(per_m2=2.0),
        checks=dict(per_m2=2.0, length=(110.0, 0.7), width=(0.7, 0.4), wiggle=0.8),
        sdark=dict(per_cm=0.9, width=(0.5, 0.5), length=(220.0, 0.8), alpha=(0.3, 1.0)),
        slight=dict(per_cm=1.5, width=(2.0, 0.6), length=(200.0, 0.8), alpha=(0.2, 0.8)),
        saw=dict(pitch=(8.0, 0.6), width=(1.8, 0.4), jitter=14.0, share_on=0.35, strength=(0.1, 0.45),
                 patch=(220.0, 60.0), patch_thr=(0.4, 1.6), floor=0.0, seed=8202),
    ),
    # Артизан Трюфель: long straight fibres, plank striping, lengthwise cracks, small knots, hardly any cathedrals
    "cg_artizan": _base(
        seed=8301, board=(150.0, 0.35, 80.0, 260.0), flat_share=0.2, depth=(60.0, 0.4), depth_amp=0.4,
        rings=dict(ring=(2.2, 0.35), early=(0.6, 0.25)),
        knots=dict(per_m2=1.2, size=(8.0, 0.4), max=18.0), pins=dict(per_m2=5.0, size=(2.5, 0.3)),
        checks=dict(per_m2=12.0, length=(220.0, 0.6), width=(1.1, 0.45), wiggle=1.2),
        sdark=dict(per_cm=1.2, width=(0.6, 0.5), length=(220.0, 0.8), alpha=(0.3, 1.0)),
        slight=dict(per_cm=1.0, width=(1.4, 0.5), length=(180.0, 0.8), alpha=(0.2, 0.8)),
        broad_mix=(0.35, 0.65, 0.3),
    ),
    # Монастырский: dark smoky oak, long black cracks and knots, grey streaks, dense fine pore lines, contrast
    "cg_monastery": _base(
        seed=8401, board=(190.0, 0.3, 110.0, 300.0), flat_share=0.35, depth=(55.0, 0.4), depth_amp=0.55,
        rings=dict(ring=(2.4, 0.35), early=(0.7, 0.25)),
        pores=dict(len=2.5, wid=0.35, thr=-0.5, fill=1.0, late=0.5),
        knots=dict(per_m2=1.8, size=(13.0, 0.45), max=35.0, cracked=0.8), pins=dict(per_m2=4.0),
        checks=dict(per_m2=10.0, length=(330.0, 0.6), width=(1.6, 0.45), wiggle=1.6),
        sdark=dict(per_cm=1.0, width=(0.6, 0.5), length=(220.0, 0.8), alpha=(0.3, 1.0)),
        slight=dict(per_cm=1.1, width=(0.8, 0.5), length=(160.0, 0.8), alpha=(0.3, 1.0)),
    ),
    # Наварра: golden-honey rustic oak, open cathedrals, frequent dark knots, short dark lengthwise cracks
    "cg_navarra": _base(
        seed=8501, board=(210.0, 0.3, 130.0, 320.0), flat_share=0.7, depth=(55.0, 0.4), depth_amp=0.5,
        turns=(1, 2),
        rings=dict(ring=(4.0, 0.35), early=(1.0, 0.25)),
        knots=dict(per_m2=1.4, size=(12.0, 0.45), max=32.0), pins=dict(per_m2=4.0),
        checks=dict(per_m2=14.0, length=(110.0, 0.7), width=(1.3, 0.45), wiggle=1.2),
    ),
    # Монтерей: mid grey oak, straight fibres, soft cathedrals, grey streaks, a few swirls
    "cg_monterey": _base(
        seed=8601, board=(190.0, 0.3, 110.0, 300.0), flat_share=0.6, depth=(50.0, 0.4), depth_amp=0.6,
        turns=(1, 2),
        rings=dict(ring=(3.2, 0.35), early=(0.9, 0.25)),
        knots=dict(per_m2=0.8, size=(10.0, 0.4)), pins=dict(per_m2=2.5),
        checks=dict(per_m2=3.0, length=(120.0, 0.7), width=(0.8, 0.4), wiggle=0.8),
        slight=dict(per_cm=0.9, width=(0.9, 0.5), length=(140.0, 0.8), alpha=(0.3, 1.0)),
    ),
}
eo.PATTERNS.update(PATTERNS)                    # in memory only: eco_oak.py itself is not touched


def _F(mid, name, pattern, swatch, slope, dark_dL, light_dL, **kw):
    """A material: swatch = the catalogue colour to match (sRGB hex, as catpage --swatch reads it); dark / light =
    the ground's full-strength colours (L* offsets along the a*, b* slopes); the rest as eco_oak's finishes, plus
    sdark / slight (strength, colour) of the streak layers and saw (strength, light colour, dark colour)."""
    d = dict(id=mid, material=mid, name=name, pattern=pattern, swatch=swatch, color=swatch, slope=slope,
             dark=eo.shade(swatch, -dark_dL, slope), light=eo.shade(swatch, light_dL, slope))
    d.update(kw)
    return d


MATERIALS = [
    _F("cg_dub_stirling", "Дуб Стирлинг 374 SWN", "cg_stirling", "#8b6b4b", (0.1, 0.35), 22, 12,
       grain=5.5, tone=4.2, fibre=1.1, pore=0.45, pore_col=eo.shade("#8b6b4b", -18, (0.1, 0.35)), ray=0.3,
       ray_col=eo.shade("#8b6b4b", 6, (0.1, 0.35)), knot="#3e2a1a", rim="#24170e", check="#2a1c12", halo=6.0,
       sdark=(0.9, "#5a4533"), slight=(0.5, "#a28a6c"), smooth=0.30),
    _F("cg_dub_tryufelny", "Дуб Трюфельный", "cg_truffle", "#786657", (0.05, 0.25), 18, 16,
       grain=4.6, tone=4.4, fibre=1.0, pore=0.45, pore_col=eo.shade("#786657", -14, (0.05, 0.25)), ray=0.25,
       ray_col=eo.shade("#786657", 6, (0.05, 0.25)), knot="#3b2e25", rim="#241b15", check="#2c221b", halo=4.0,
       sdark=(0.9, "#4d3e33"), slight=(0.7, "#9c958c"), saw=(0.5, "#a19a92", "#5b4c40"), smooth=0.30),
    _F("cg_dub_artizan_tryufel", "Дуб Артизан Трюфель", "cg_artizan", "#6e5242", (0.1, 0.3), 16, 14,
       grain=3.2, tone=4.2, fibre=1.1, pore=0.4, pore_col=eo.shade("#6e5242", -12, (0.1, 0.3)), ray=0.2,
       ray_col=eo.shade("#6e5242", 5, (0.1, 0.3)), knot="#2e1f16", rim="#1b120c", check="#1f150f", halo=4.0,
       sdark=(0.8, "#3f2c21"), slight=(0.5, "#8a7a6e"), smooth=0.30),
    _F("cg_dub_monastyrsky", "Дуб Монастырский 375", "cg_monastery", "#655249", (0.05, 0.2), 16, 14,
       grain=3.6, tone=3.2, fibre=1.2, pore=0.7, pore_col="#857670", ray=0.2,
       ray_col=eo.shade("#655249", 6, (0.05, 0.2)), knot="#1d1511", rim="#0f0b09", check="#100c0a", halo=5.0,
       sdark=(0.9, "#3a2d26"), slight=(0.6, "#8c7f78"), smooth=0.30),
    _F("cg_dub_navarra", "Дуб Наварра", "cg_navarra", "#956b40", (0.15, 0.45), 20, 12,
       grain=3.0, tone=3.4, fibre=1.1, pore=0.45, pore_col=eo.shade("#956b40", -16, (0.15, 0.45)), ray=0.3,
       ray_col=eo.shade("#956b40", 6, (0.15, 0.45)), knot="#4a2e16", rim="#2b190b", check="#2e1c0f", halo=6.0,
       sdark=(0.7, "#6a4a2a"), slight=(0.4, "#b89166"), smooth=0.30),
    _F("cg_dub_monterey", "Дуб Монтерей", "cg_monterey", "#747474", (0.0, 0.0), 16, 14,
       grain=3.2, tone=3.0, fibre=1.0, pore=0.4, pore_col="#595959", ray=0.25, ray_col="#838383",
       knot="#3a3a3a", rim="#262626", check="#2d2d2d", halo=4.0,
       sdark=(0.5, "#505050"), slight=(0.6, "#9a9a9a"), smooth=0.30),
]

# check-sheet references: swatch (page, crop, rotate 90° so the grain runs along x), photo (page / file, crop,
# dpi or px per mm, rotate) - px_mm = the photo's approximate scale (for the texture shown the same way)
REFS = {
    "cg_dub_stirling": dict(swatch=(93, "0.764,0.86,0.815,0.9", True),
                            photo=dict(page=91, crop="0.237,0.71,0.345,0.895", dpi=200, px_mm=2.0, rot=True)),
    "cg_dub_tryufelny": dict(swatch=(131, "0.755,0.85,0.81,0.89", False),
                             photo=dict(page=131, crop="0.842,0.699,0.917,0.769", dpi=250, px_mm=0.35, rot=False)),
    "cg_dub_artizan_tryufel": dict(swatch=(30, "0.748,0.858,0.775,0.900", True),
                                   photo=dict(page=30, crop="0.1763,0.7606,0.206,0.7852", dpi=300, px_mm=0.57,
                                              rot=False)),
    "cg_dub_monastyrsky": dict(swatch=(113, "0.62,0.51,0.86,0.57", False),
                               photo=dict(file=str(SITE), box=(40, 830, 1360, 1370), px_mm=3.3, rot=False)),
    "cg_dub_navarra": dict(swatch=(74, "0.715,0.86,0.772,0.908", True),
                           photo=dict(page=74, crop="0.236,0.71,0.33,0.80", dpi=200, px_mm=1.2, rot=False)),
    "cg_dub_monterey": dict(swatch=(64, "0.65,0.865,0.672,0.905", False),
                            photo=dict(page=64, crop="0.5365,0.656,0.5434,0.823", dpi=300, px_mm=0.3, rot=True)),
}


# ------------------------------------------------------------------------------------------------ structure
def saw_marks(p, st):
    """Cross-grain saw marks of a sawn-board print: straight thin lines across the grain (constant x), broken, in
    patches. Returns (light, dark) opacity fields."""
    s = p["saw"]
    rng = np.random.default_rng(s["seed"])
    h, w = ALBEDO[1], ALBEDO[0]
    out = []
    for _ in range(2):
        out.append(kit.straight_lines(rng, s["pitch"], s["width"], PX, 1, s["jitter"], s["strength"],
                                      share_on=s["share_on"], soft=0.55, wander=0.3, wander_len=60.0))
    patch = kit.smoothstep(*s.get("patch_thr", (-0.6, 1.0)), mf.gauss_noise(rng, (h, w), s["patch"][0] * PX, s["patch"][1] * PX))
    patch = s["floor"] + (1 - s["floor"]) * patch
    return out[0] * patch, out[1] * patch


def structure(fin, cache):
    key = (fin["pattern"], fin.get("seed"))
    if key not in cache:
        st = eo.wood_structure(*key)
        p = PATTERNS[fin["pattern"]]
        if p.get("saw"):
            st["saw_light"], st["saw_dark"] = saw_marks(p, st)
        cache[key] = st
    return cache[key]


# ------------------------------------------------------------------------------------------------ maps
def _over(o, alpha, col_lin, mean):
    a = np.clip(alpha, 0.0, 1.0)[..., None]
    return o * (1 - a) + a * (col_lin / mean)


def albedo_linear(fin, st, color=None):
    """eco_oak's ground / pores / rays / knots / checks, then the streaks and saw marks in their own colours; the
    mean in linear light is `color` (default fin["color"])."""
    col = hex_to_linear(color or fin["color"])
    f = dict(fin, color=color or fin["color"], streak=0)
    out = eo.albedo_linear(f, st) / col                         # relative to the mean
    if fin.get("sdark"):
        out = _over(out, fin["sdark"][0] * st["sdark"], hex_to_linear(fin["sdark"][1]), col)
    if fin.get("slight"):
        out = _over(out, fin["slight"][0] * st["slight"], hex_to_linear(fin["slight"][1]), col)
    if fin.get("saw") and "saw_light" in st:
        k, cl, cd = fin["saw"]
        out = _over(out, k * st["saw_light"], hex_to_linear(cl), col)
        out = _over(out, k * st["saw_dark"], hex_to_linear(cd), col)
    base = col / out.reshape(-1, 3).mean(0, dtype=np.float64)
    for _ in range(4):
        a = np.clip(out * base, 0, 1)
        base *= col / a.reshape(-1, 3).mean(0, dtype=np.float64)
    return np.clip(out * base, 0, 1)


def normal_map(st):
    """eco_oak's relief (pores, checks, rays, knot rims, latewood, fibre) + the pressed-in saw marks."""
    rel = st["relief"]
    hgt = (-rel["pores"] * st["pores"] - rel["checks"] * st["check"] - rel["rays"] * st["rays"]
           - rel["rim"] * st["rim"] - rel["late"] * st["late"] + rel["fibre"] * 0.25 * st["fibre"])
    if "saw_light" in st:
        hgt = hgt - 0.5 * (st["saw_light"] + st["saw_dark"])
    hgt = mf.box_down(hgt, ALBEDO[0] // NORMAL[0])
    gx = (np.roll(hgt, -1, 1) - np.roll(hgt, 1, 1)) / 2
    gr = (np.roll(hgt, -1, 0) - np.roll(hgt, 1, 0)) / 2
    slope = np.sqrt(gx ** 2 + gr ** 2)
    k = math.tan(math.radians(rel["tilt_deg"])) / max(1e-9, np.sqrt((slope ** 2).mean()))
    n = np.stack([-gx * k, gr * k, np.ones_like(gx)], -1)       # OpenGL: +Y (green) = up = -row
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return np.round((n * 0.5 + 0.5) * 255).astype(np.uint8)


def to8(lin):
    return np.round(linear_to_srgb(np.clip(lin, 0, 1)) * 255).astype(np.uint8)


def trimmed_mean(rgb8):
    """gen/catpage.py's swatch statistic: mean of the middle 60 % by brightness (sRGB 0..255)."""
    im = np.asarray(rgb8, dtype=np.float64).reshape(-1, 3)
    order = np.argsort(im @ [0.299, 0.587, 0.114])
    k = len(order)
    return im[order[int(k * 0.2):max(int(k * 0.8), int(k * 0.2) + 1)]].mean(0)


def swatch_view(alb):
    """The texture as the catalogue swatch shows it: sRGB, box-downsized to SWATCH_PX_MM."""
    w, h = ALBEDO
    img = Image.fromarray(to8(alb))
    return img.resize((int(w * MM * SWATCH_PX_MM), int(h * MM * SWATCH_PX_MM)), Image.BOX)


def hex8(v):
    return "#" + "".join("%02x" % int(round(float(c))) for c in v)


def de76(hex_a, hex_b):
    return float(np.linalg.norm(linear_to_lab(hex_to_linear(hex_a)) - linear_to_lab(hex_to_linear(hex_b))))


def fit_color(fin, st, rounds=4):
    """Solves the linear mean so that the swatch view's trimmed mean is the swatch colour."""
    target = srgb_to_linear(np.array([int(fin["swatch"][i:i + 2], 16) for i in (1, 3, 5)]) / 255)
    color = fin["swatch"]
    for _ in range(rounds):
        alb = albedo_linear(fin, st, color)
        got = srgb_to_linear(trimmed_mean(swatch_view(alb)) / 255)
        color = linear_to_hex(np.clip(hex_to_linear(color) * target / got, 0, 1))
    return color, albedo_linear(fin, st, color)


def write_material(fin, st, alb):
    mid = fin["material"]
    folder = EXT / "Materials" / mid
    folder.mkdir(parents=True, exist_ok=True)
    Image.fromarray(to8(alb)).save(folder / f"{mid}_albedo.jpg", quality=90, subsampling=0, optimize=True)
    Image.fromarray(normal_map(st)).save(folder / f"{mid}_normal.jpg", quality=92, subsampling=0, optimize=True)
    Image.fromarray(eo.mask_map(fin, st)).save(folder / f"{mid}_mask.png", optimize=True)


def read_albedo(fin):
    path = EXT / "Materials" / fin["material"] / (fin["material"] + "_albedo.jpg")
    return srgb_to_linear(np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255)


def manifest_entry(fin):
    mid = fin["material"]
    return {"id": mid, "name": fin["name"], "category": "casegoods", "source": SOURCE, "neutral": False,
            "metersPerTile": list(TILE_M), "maxSize": ALBEDO[0], "folder": f"Materials/{mid}",
            "textures": {"albedo": f"{mid}_albedo.jpg", "normal": f"{mid}_normal.jpg", "mask": f"{mid}_mask.png"}}


def write_entries(merge=True):
    done = [f for f in MATERIALS if (EXT / "Materials" / f["material"] / (f["material"] + "_albedo.jpg")).exists()]
    ENTRIES.parent.mkdir(parents=True, exist_ok=True)
    ENTRIES.write_text(json.dumps([manifest_entry(f) for f in done], ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")
    print("entries", ENTRIES.relative_to(ROOT), len(done))
    if merge:
        merge_entries.merge([str(ENTRIES)])


# ------------------------------------------------------------------------------------------------ check sheet
def _page_crop(page, crop, dpi):
    import pymupdf                              # only the check sheet needs the catalogue
    doc = pymupdf.open(str(PDF))
    pg = doc[page - 1]
    r = pg.rect
    x0, y0, x1, y1 = (float(v) for v in crop.split(","))
    clip = pymupdf.Rect(r.x0 + x0 * r.width, r.y0 + y0 * r.height, r.x0 + x1 * r.width, r.y0 + y1 * r.height)
    pix = pg.get_pixmap(dpi=dpi, clip=clip)
    return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def _fit_h(img, hgt):
    return img.resize((max(1, round(img.width * hgt / img.height)), hgt), Image.LANCZOS)


def _tex_view(alb, px_mm, w_px, h_px, x0_mm=300.0, y0_mm=200.0):
    """w_px x h_px of the texture seen at px_mm (grain along x), box-filtered from the albedo."""
    w_mm, h_mm = w_px / px_mm, h_px / px_mm
    x0, y0 = int(x0_mm * PX), int(y0_mm * PX)
    cw, ch = max(2, int(w_mm * PX)), max(2, int(h_mm * PX))
    lin = np.take(np.take(alb, np.arange(y0, y0 + ch) % alb.shape[0], 0), np.arange(x0, x0 + cw) % alb.shape[1], 1)
    return Image.fromarray(to8(lin)).resize((w_px, h_px), Image.BOX if px_mm < PX else Image.LANCZOS)


PANEL = (380, 220)
FONT = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"


def _panel(img):
    """Fits img to the panel height, then centre-crops (or pads) it to the panel width."""
    w, h = PANEL
    img = _fit_h(img, h)
    if img.width >= w:
        x0 = (img.width - w) // 2
        return img.crop((x0, 0, x0 + w, h))
    out = Image.new("RGB", PANEL, "white")
    out.paste(img, ((w - img.width) // 2, 0))
    return out


def sheet(rows, out):
    """Per material: (a) swatch, (b) texture at the swatch's scale, (c) photo, (d) texture at the photo's scale,
    (e) 1.0 m x 0.55 m of texture. Grain along x everywhere (vertical-grain crops are turned)."""
    from PIL import ImageFont
    try:
        font = ImageFont.truetype(FONT, 14)
    except OSError:
        font = ImageFont.load_default()
    w, h = PANEL
    head = 40
    img = Image.new("RGB", (5 * w + 4 * 10, len(rows) * (h + head + 12)), "white")
    d = ImageDraw.Draw(img)
    for i, (fin, alb, info) in enumerate(rows):
        ref = REFS[fin["id"]]
        pg, crop, rot = ref["swatch"]
        sw = _page_crop(pg, crop, 150)
        if rot:
            sw = sw.transpose(Image.ROTATE_90)
        a = _panel(sw)
        z = h / sw.height                           # display zoom of the swatch
        b = _tex_view(alb, SWATCH_PX_MM * z, w, h, 150.0, 100.0)
        ph = ref["photo"]
        if "file" in ph:
            pim = Image.open(ph["file"]).convert("RGB").crop(ph["box"])
        else:
            pim = _page_crop(ph["page"], ph["crop"], ph["dpi"])
        if ph["rot"]:
            pim = pim.transpose(Image.ROTATE_90)
        zp = h / pim.height
        c = _panel(pim)
        dd = _tex_view(alb, ph["px_mm"] * zp, w, h, 900.0, 500.0)
        e = _tex_view(alb, w / 1000.0, w, h, 0.0, 0.0)
        y = i * (h + head + 12)
        for k, im in enumerate((a, b, c, dd, e)):
            img.paste(im, (k * (w + 10), y + head))
        d.text((2, y + 2), "%s  «%s»   swatch %s (p. %d)   texture at the swatch's scale %s  ΔE76 %.2f   "
               "linear mean %s" % (fin["id"], fin["name"], fin["swatch"], pg, info["view"], info["de"],
                                   info["mean"]), fill="black", font=font)
        d.text((2, y + 20), "(a) swatch   (b) texture at the swatch's scale   (c) photo   (d) texture at the "
               "photo's scale (~%.2f px/mm)   (e) 1.0 m" % (ph["px_mm"] * zp), fill=(80, 80, 80), font=font)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print("check sheet", out.relative_to(ROOT))


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--no-merge", action="store_true")
    ap.add_argument("--no-sheet", action="store_true")
    args = ap.parse_args()
    fins = [f for f in MATERIALS if not args.ids or f["id"] in args.ids]
    if args.ids and len(fins) != len(args.ids):
        sys.exit("unknown id: " + ", ".join(set(args.ids) - {f["id"] for f in fins}))
    cache, rows = {}, []
    for fin in fins:
        st = structure(fin, cache)
        color, alb = fit_color(fin, st)
        if not args.no_write:
            write_material(fin, st, alb)
            alb = read_albedo(fin)              # what Unity gets: the written JPEG
        view = hex8(trimmed_mean(swatch_view(alb)))
        info = dict(view=view, de=de76(view, fin["swatch"]), mean=linear_to_hex(alb.reshape(-1, 3).mean(0)),
                    base=color)
        print("%-24s swatch %s  view %s  dE76 %.2f  linear mean %s  (solved colour %s)" % (
            fin["id"], fin["swatch"], view, info["de"], info["mean"], color))
        rows.append((fin, alb.astype(np.float32), info))
    if not args.no_write:
        write_entries(merge=not args.no_merge)
    if not args.no_sheet:
        sheet(rows, SHEET if not args.ids else SHEET.with_name(f"{FAMILY}_{'_'.join(args.ids)}.png"))


if __name__ == "__main__":
    main()
