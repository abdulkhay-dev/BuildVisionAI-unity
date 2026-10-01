#!/usr/bin/env python3
"""Lift textures, family `floors`: the car floor layouts of the GLZ / NBSL catalogue (PVC patterns and marble).

    python tools/lifts/textures/floors.py [--no-merge] [ids]        # ids like sl-4006p

One fitted picture per floor (metersPerTile [1, 1]: UV 0..1 over the whole car floor): u = left -> right as seen
from the door, v = 0 at the door -> 1 at the back wall (image top = back wall). 1024 x 1024, flat top-down, borders as
fractions of the size so the layout survives stretching to car aspects 0.7 .. 1.5 (a medallion becomes an ellipse).
PVC ("p") films: printed stone, satin (smoothness 0.35), fine emboss in the normal. Marble ("d"): polished (0.8),
hairline joints between the inlay pieces.

Pictured floors (catalogue p.21) follow the swatch crops in tools/lifts/reference/floors/ (layout measured in
fractions, colours from the regions' medians); the 8 floors named only under cabin photos follow those photos (see
floors.md). The checker plates are NOT made here: a fitted picture would stretch the tread with the car size; the
engine falls back to the tiling lift_checker (metals.py) for them.
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

FAMILY = "floors"
SOURCE = "procedural:tools/lifts/textures/floors.py"
N = 1024
MM = 1.5                            # mm per px (a ~1.5 m car floor)

# ------------------------------------------------------------------------------------------------ stones
S = {
    # white marble with grey diagonal veins (4006p field)
    "carrara": dict(base="#dddce1", base2="#cfced4", cloud_mm=160, veins=[
        dict(kind="dir", color="#7c7b83", alpha=0.85, width_mm=1.4, scale_mm=70, length_mm=600, angle=-45,
             levels=(0.0, 1.3), warp_mm=45, warp_scale_mm=130, soft_alpha=0.65, soft_width=0.25,
             breakup=0.4, breakup_mm=130),
        dict(kind="dir", color="#9e9da5", alpha=0.65, width_mm=0.6, scale_mm=25, length_mm=400, angle=-50,
             levels=(0.3, -0.6), warp_mm=15, warp_scale_mm=80, soft_alpha=0.3, breakup=0.45, breakup_mm=80)]),
    # brown emperador (borders of 4006p / 4173p)
    "emperador": dict(base="#6c5034", base2="#7a5c3c", cloud_mm=60, veins=[
        dict(kind="cells", color="#b0916a", alpha=0.8, width_mm=0.7, scale_mm=50, warp_mm=14, tone=0.35),
        dict(kind="cells", color="#9a7c56", alpha=0.55, width_mm=0.45, scale_mm=16, warp_mm=5, tone=0.2, breakup=0.3),
        dict(kind="net", color="#4b3622", alpha=0.45, width_mm=2.0, scale_mm=60, warp_mm=30, breakup=0.4)]),
    # dark emperador (4182d field, 4021p bars, 4072d, 4039d)
    "emperador_dark": dict(base="#4f331d", base2="#62432a", cloud_mm=45, veins=[
        dict(kind="cells", color="#b89466", alpha=0.85, width_mm=0.7, scale_mm=38, warp_mm=10, tone=0.45),
        dict(kind="cells", color="#a58358", alpha=0.6, width_mm=0.45, scale_mm=12, warp_mm=4, tone=0.25, breakup=0.35),
        dict(kind="net", color="#2c1a0c", alpha=0.5, width_mm=2.5, scale_mm=45, warp_mm=25, breakup=0.4)]),
    # light yellow marble with tan veins (4021p)
    "giallo": dict(base="#ddd5ac", base2="#d3c895", cloud_mm=110, veins=[
        dict(kind="cells", color="#c4ab80", alpha=0.45, width_mm=0.6, scale_mm=70, warp_mm=25, tone=0.06, breakup=0.3),
        dict(kind="net", color="#e9e3c6", alpha=0.45, width_mm=2.0, scale_mm=60, warp_mm=40, breakup=0.4)]),
    # golden yellow marble with red-brown veins (4012p outer field, SL-1095 photo)
    "giallo_sun": dict(base="#ead190", base2="#dcbb69", cloud_mm=100, veins=[
        dict(kind="cells", color="#a8733c", alpha=0.7, width_mm=0.8, scale_mm=75, warp_mm=30, tone=0.08, breakup=0.3),
        dict(kind="cells", color="#c99b5a", alpha=0.45, width_mm=0.5, scale_mm=25, warp_mm=10, breakup=0.5)]),
    # white marble with golden veins (4012p centre)
    "calacatta_gold": dict(base="#f2ecdc", base2="#e9e0c9", cloud_mm=150, veins=[
        dict(kind="dir", color="#c09a55", alpha=0.75, width_mm=1.1, scale_mm=60, length_mm=500, angle=-20,
             warp_mm=40, warp_scale_mm=120, soft_alpha=0.3, soft_width=0.1, breakup=0.35, breakup_mm=120),
        dict(kind="dir", color="#b9b0a0", alpha=0.45, width_mm=0.6, scale_mm=30, length_mm=250, angle=-30,
             levels=(0.4,), warp_mm=30, warp_scale_mm=90, breakup=0.5, breakup_mm=70)]),
    # beige cream marble (4025p field)
    "crema_beige": dict(base="#e0d9c8", base2="#d7cebb", cloud_mm=120, veins=[
        dict(kind="cells", color="#c9bfa8", alpha=0.4, width_mm=0.6, scale_mm=80, warp_mm=30, tone=0.03, breakup=0.4),
        dict(kind="net", color="#ece6d8", alpha=0.4, width_mm=1.5, scale_mm=50, warp_mm=40, breakup=0.5)]),
    # dark green marble with light veins (verde alpi): 4025p, 4027p, 4028p, 4012p
    "verde": dict(base="#203429", base2="#33473a", cloud_mm=40, veins=[
        dict(kind="cells", color="#93ab9b", alpha=0.85, width_mm=0.8, scale_mm=34, warp_mm=10, tone=0.5),
        dict(kind="cells", color="#d2ded6", alpha=0.55, width_mm=0.45, scale_mm=11, warp_mm=4, tone=0.25, breakup=0.4),
        dict(kind="net", color="#0f1e16", alpha=0.45, width_mm=2.5, scale_mm=45, warp_mm=30, breakup=0.4)]),
    # near-black (4027p corner squares)
    "nero_plain": dict(base="#181c26", base2="#1f2430", cloud_mm=50, veins=[
        dict(kind="net", color="#343a48", alpha=0.35, width_mm=0.6, scale_mm=40, warp_mm=20, breakup=0.6)]),
    # pink-white marble with lilac streaks (4027p, 4028p field)
    "rosa": dict(base="#f5ede7", base2="#ece1db", cloud_mm=130, veins=[
        dict(kind="dir", color="#8c7581", alpha=0.75, width_mm=0.9, scale_mm=24, length_mm=220, angle=50,
             levels=(0.0, 1.0, -1.0), warp_mm=15, warp_scale_mm=70, soft_alpha=0.6, soft_width=0.25, breakup=0.4,
             breakup_mm=70),
        dict(kind="dir", color="#bba7ae", alpha=0.55, width_mm=0.5, scale_mm=12, length_mm=110, angle=45,
             levels=(0.0,), warp_mm=8, warp_scale_mm=40, soft_alpha=0.3, breakup=0.5, breakup_mm=40)]),
    # light beige sandstone-like (4034p field)
    "beige_fine": dict(base="#ebdccb", base2="#e2d1bc", cloud_mm=60, fleck=("#d6c2aa", 0.5, 4),
                       veins=[dict(kind="net", color="#f6ecdf", alpha=0.35, width_mm=1.0, scale_mm=25, warp_mm=15,
                                   breakup=0.5)]),
    "taupe": dict(base="#4b4337", base2="#554b3e", cloud_mm=40, fleck=("#3e372d", 0.4, 5), veins=[]),
    "gold_band": dict(base="#a9894f", base2="#b39459", cloud_mm=20, veins=[
        dict(kind="dir", color="#8c7040", alpha=0.4, width_mm=0.5, scale_mm=5, length_mm=200, angle=0,
             warp_mm=2, warp_scale_mm=60, breakup=0.3, breakup_mm=40)]),
    # white marble with very faint grey veins (4173p)
    "bianco": dict(base="#e8e9e4", base2="#e0e1dd", cloud_mm=150, veins=[
        dict(kind="dir", color="#c2c2c9", alpha=0.55, width_mm=0.7, scale_mm=50, length_mm=300, angle=-35,
             warp_mm=30, warp_scale_mm=100, soft_alpha=0.35, soft_width=0.15, breakup=0.5, breakup_mm=70)]),
    # black granite with reddish specks (4106d border)
    "granite_black": dict(base="#211f1e", base2="#2a2625", cloud_mm=30, veins=[], speck=[
        dict(color="#4d3f3c", share=0.22, size_mm=2.0), dict(color="#0e0d0c", share=0.25, size_mm=2.5),
        dict(color="#7a6560", share=0.05, size_mm=1.4), dict(color="#5a5654", share=0.06, size_mm=1.2)]),
    # peach cream mottled (4106d centre)
    "crema_peach": dict(base="#ebdfc2", base2="#e2cba6", cloud_mm=50, fleck=("#f2e6cf", 0.5, 8),
                        veins=[dict(kind="net", color="#d9c19c", alpha=0.35, width_mm=1.5, scale_mm=30, warp_mm=20,
                                    breakup=0.5)]),
    # grey-green cloudy onyx (4145d)
    "grigio_onice": dict(base="#c3c2ba", base2="#b3b1a7", cloud_mm=90, veins=[
        dict(kind="cells", color="#dcdcd5", alpha=0.55, width_mm=2.5, scale_mm=60, warp_mm=25, tone=0.06),
        dict(kind="cells", color="#e8e8e2", alpha=0.4, width_mm=0.7, scale_mm=22, warp_mm=8, breakup=0.4),
        dict(kind="net", color="#a6a49a", alpha=0.3, width_mm=1.2, scale_mm=50, warp_mm=40, breakup=0.5)]),
    # crema marfil (4157d, 4182d, 4072d, 4150d light parts)
    "marfil": dict(base="#fbf4e5", base2="#f2e7d2", cloud_mm=140, veins=[
        dict(kind="net", color="#e2d3ba", alpha=0.45, width_mm=0.6, scale_mm=80, warp_mm=60, breakup=0.45),
        dict(kind="cells", color="#eadcc5", alpha=0.35, width_mm=0.5, scale_mm=50, warp_mm=20, breakup=0.5)]),
    "marfil_warm": dict(base="#efe3cc", base2="#e5d5ba", cloud_mm=120, veins=[
        dict(kind="net", color="#d4c19f", alpha=0.45, width_mm=0.7, scale_mm=70, warp_mm=50, breakup=0.45),
        dict(kind="cells", color="#ddcdb0", alpha=0.35, width_mm=0.5, scale_mm=45, warp_mm=18, breakup=0.5)]),
    # light brown marble band (4157d)
    "emperador_light": dict(base="#bfa483", base2="#b2967a", cloud_mm=40, veins=[
        dict(kind="cells", color="#d8c6a8", alpha=0.6, width_mm=0.6, scale_mm=35, warp_mm=10, tone=0.15),
        dict(kind="net", color="#9b8061", alpha=0.4, width_mm=1.4, scale_mm=50, warp_mm=30, breakup=0.4)]),
    # nero marquina with white and gold veins (4150d band)
    "nero_marquina": dict(base="#1b1612", base2="#241d17", cloud_mm=40, veins=[
        dict(kind="dir", color="#e8e0d0", alpha=0.8, width_mm=0.6, scale_mm=25, length_mm=200, angle=20,
             levels=(0.0, 1.1), warp_mm=20, warp_scale_mm=60, breakup=0.4, breakup_mm=50),
        dict(kind="cells", color="#b8904a", alpha=0.7, width_mm=0.7, scale_mm=40, warp_mm=12, breakup=0.55)]),
    # grey marble with white veins (4082d border)
    "grigio": dict(base="#6b6c6b", base2="#58595a", cloud_mm=50, veins=[
        dict(kind="cells", color="#b9bab7", alpha=0.65, width_mm=0.7, scale_mm=35, warp_mm=10, tone=0.3),
        dict(kind="net", color="#3f403f", alpha=0.45, width_mm=2.0, scale_mm=60, warp_mm=40, breakup=0.4)]),
    "beige_plain": dict(base="#ddd1b8", base2="#d4c6ab", cloud_mm=120, veins=[
        dict(kind="net", color="#e8dfcb", alpha=0.35, width_mm=1.2, scale_mm=70, warp_mm=50, breakup=0.5)]),
    "bronze": dict(base="#8a6a40", base2="#94744a", cloud_mm=20, veins=[]),
    # white marble with soft grey-beige veins (4039d field)
    "bianco_warm": dict(base="#efebe4", base2="#e5ded3", cloud_mm=140, veins=[
        dict(kind="dir", color="#c4b7a5", alpha=0.6, width_mm=1.0, scale_mm=80, length_mm=300, angle=-60,
             warp_mm=60, warp_scale_mm=150, soft_alpha=0.35, soft_width=0.12, breakup=0.3, breakup_mm=120),
        dict(kind="cells", color="#d9d0c4", alpha=0.4, width_mm=0.6, scale_mm=60, warp_mm=20, breakup=0.5)]),
    "gold_marble": dict(base="#cdb27a", base2="#c0a066", cloud_mm=30, veins=[
        dict(kind="cells", color="#e2cea0", alpha=0.5, width_mm=0.5, scale_mm=20, warp_mm=6, tone=0.1, breakup=0.4)]),
    # grey terrazzo / granite chip PVC (4017p)
    "terrazzo_grey": dict(base="#b4b4ae", base2="#acaca6", cloud_mm=60, veins=[], speck=[
        dict(color="#e2e2dc", share=0.28, size_mm=4.0), dict(color="#7b7b78", share=0.22, size_mm=3.5),
        dict(color="#55565a", share=0.08, size_mm=2.5), dict(color="#c9c8c0", share=0.15, size_mm=5.0)]),
    "grigio_light": dict(base="#dcdcd8", base2="#d0d0cc", cloud_mm=140, veins=[
        dict(kind="net", color="#bdbdbd", alpha=0.45, width_mm=0.8, scale_mm=90, warp_mm=60, breakup=0.45)]),
}


# ------------------------------------------------------------------------------------------------ layout helpers
def R(u0, v0, u1, v1):
    return [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]


def frame(inset, width, mitre=False):
    """Four bars of a square frame (fractions; outer edge at `inset`). Mitred: trapezoids, else butt joints with the
    top / bottom bars running full length."""
    a, b = inset, inset + width
    A, B = 1 - inset, 1 - inset - width
    if mitre:
        return [[(a, a), (A, a), (B, b), (b, b)], [(A, a), (A, A), (B, B), (B, b)],
                [(A, A), (a, A), (b, B), (B, B)], [(a, A), (a, a), (b, b), (b, B)]]
    return [R(a, a, A, b), R(a, B, A, A), R(a, b, b, B), R(B, b, A, B)]


def diamond(cu, cv, hu, hv=None):
    hv = hu if hv is None else hv
    return [(cu, cv - hv), (cu + hu, cv), (cu, cv + hv), (cu - hu, cv)]


def ellipse(cu, cv, r, n=180):
    return [(cu + r * math.cos(t), cv + r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, n, endpoint=False)]


# A layout: list of (stone, polygons) painted in order; each polygon a separate piece (own veins, own joints).
# "holes": a piece may be ('stone', [poly], [hole polys]).
LAYOUTS = {
    "sl-4006p": dict(kind="pvc", pieces=[
        ("emperador", [R(0, 0, 1, 1)]),
        ("carrara", [R(0.085, 0.085, 0.915, 0.915)]),
        ("emperador", [diamond(0.5, 0.5, 0.215)])]),
    "sl-4021p": dict(kind="pvc", pieces=[
        ("giallo", [R(0, 0, 1, 1)])] + [
        ("emperador_dark", [R(0.11, v - 0.02, 0.885, v + 0.02), R(0.26, v - 0.04, 0.735, v + 0.04)])
        for v in (0.24, 0.5, 0.76)]),
    "sl-4025p": dict(kind="pvc", pieces=[
        ("crema_beige", [R(0, 0, 1, 1)]),
        ("verde", frame(0.115, 0.058)),
        ("verde", [R(0, 0, 0.115, 0.115), R(0.885, 0, 1, 0.115), R(0, 0.885, 0.115, 1), R(0.885, 0.885, 1, 1)])]),
    "sl-4027p": dict(kind="pvc", tiles=(2, 2, (0.17, 0.17, 0.83, 0.83)), pieces=[
        ("verde", frame(0.0, 0.17)),
        ("nero_plain", [R(0, 0, 0.17, 0.17), R(0.83, 0, 1, 0.17), R(0, 0.83, 0.17, 1), R(0.83, 0.83, 1, 1)]),
        ("rosa", [R(0.17, 0.17, 0.83, 0.83)]),
        ("verde", [diamond(0.5, 0.5, 0.17)])]),
    "sl-4034p": dict(kind="pvc", pieces=[
        ("beige_fine", [R(0, 0, 1, 1)]),
        ("taupe", [diamond(0.5, 0.5, 0.32)]),
        ("beige_fine", [R(0.355, 0.355, 0.645, 0.645)]),
        # pinwheel of four gold ribbons round the square, each running past the corner on one end
        ("gold_band", [R(0.295, 0.295, 0.76, 0.355), R(0.645, 0.295, 0.705, 0.76),
                       R(0.24, 0.645, 0.705, 0.705), R(0.295, 0.24, 0.355, 0.705)])]),
    "sl-4173p": dict(kind="pvc", tiles=(2, 2, (0.085, 0.085, 0.915, 0.915)), pieces=[
        ("emperador", [R(0, 0, 1, 1)]),
        ("bianco", [R(0.085, 0.085, 0.915, 0.915)])]),
    "sl-4106d": dict(kind="marble", pieces=[
        ("granite_black", frame(0.0, 0.09, mitre=True)),
        ("crema_peach", [R(0.09, 0.09, 0.91, 0.91)])]),
    "sl-4145d": dict(kind="marble", pieces=[("grigio_onice", [R(0, 0, 1, 1)])]),
    "sl-4157d": dict(kind="marble", pieces=[
        ("marfil", frame(0.0, 0.09, mitre=True)),
        ("emperador_light", frame(0.09, 0.08, mitre=True)),
        ("marfil", [R(0.17, 0.17, 0.83, 0.83)])]),
    "sl-4182d": dict(kind="marble", pieces=[
        ("marfil_warm", frame(0.0, 0.085, mitre=True)),
        ("emperador_dark", [R(0.085, 0.085, 0.915, 0.915)]),
        ("marfil_warm", [[(0.5, 0.085), (0.915, 0.5), (0.5, 0.915), (0.085, 0.5)]]),
        ("emperador_dark", [R(0.29, 0.29, 0.71, 0.71)])]),
    # --- not pictured in the floor list: from the cabin photos
    "sl-4028p": dict(kind="pvc", pieces=[      # SL-1036: pink-white field, green bands across, black crossings
        ("rosa", [R(0, 0, 1, 1)]),
        ("verde", [R(0, 0.13, 1, 0.2), R(0, 0.8, 1, 0.87), R(0.13, 0, 0.2, 1), R(0.8, 0, 0.87, 1)]),
        ("nero_plain", [R(0.13, 0.13, 0.2, 0.2), R(0.8, 0.13, 0.87, 0.2), R(0.13, 0.8, 0.2, 0.87), R(0.8, 0.8, 0.87, 0.87)])]),
    "sl-4017p": dict(kind="pvc", pieces=[("terrazzo_grey", [R(0, 0, 1, 1)])]),
    "sl-4012p": dict(kind="pvc", pieces=[      # SL-1095: golden field, green frame, white-gold centre
        ("giallo_sun", [R(0, 0, 1, 1)]),
        ("verde", frame(0.16, 0.045)),
        ("calacatta_gold", [R(0.205, 0.205, 0.795, 0.795)])]),
    "sl-4072d": dict(kind="marble", pieces=[   # SL-1109: emperador border, cream band, dark line, cream centre
        ("emperador_dark", frame(0.0, 0.075, mitre=True)),
        ("marfil_warm", frame(0.075, 0.075, mitre=True)),
        ("emperador_dark", frame(0.15, 0.012)),
        ("marfil_warm", [R(0.162, 0.162, 0.838, 0.838)])]),
    "sl-4150d": dict(kind="marble", pieces=[   # SL-1135: cream border, black marquina band, cream centre
        ("marfil_warm", frame(0.0, 0.07, mitre=True)),
        ("nero_marquina", frame(0.07, 0.045)),
        ("marfil", [R(0.115, 0.115, 0.885, 0.885)])]),
    "sl-4082d": dict(kind="marble", pieces=[   # SL-1136: grey marble border (mitred), bronze line, beige centre
        ("grigio", frame(0.0, 0.09, mitre=True)),
        ("bronze", frame(0.09, 0.008)),
        ("beige_plain", [R(0.098, 0.098, 0.902, 0.902)])]),
    "sl-4039d": dict(kind="marble", medallion=True, pieces=[   # SL-1137: white field, round medallion
        ("bianco_warm", [R(0, 0, 0.5, 0.5), R(0.5, 0, 1, 0.5), R(0, 0.5, 0.5, 1), R(0.5, 0.5, 1, 1)]),
        ("emperador_dark", [ellipse(0.5, 0.5, 0.30)]),
        ("gold_marble", [ellipse(0.5, 0.5, 0.245)]),
        ("marfil", [ellipse(0.5, 0.5, 0.232)])]),
    "sl-4036p": dict(kind="pvc", pieces=[      # SL-1130: floor hidden by the lower canopy -> plain light frame
        ("grigio_light", [R(0, 0, 1, 1)]),
        ("grigio", frame(0.07, 0.03)),
        ("bianco", [R(0.1, 0.1, 0.9, 0.9)])]),
}

NAMES = {
    "sl-4006p": "SL-4006P ПВХ: белый мрамор, коричневая рамка, ромб",
    "sl-4021p": "SL-4021P ПВХ: светло-жёлтый мрамор, три тёмные полосы",
    "sl-4025p": "SL-4025P ПВХ: бежевый мрамор, зелёная рамка",
    "sl-4027p": "SL-4027P ПВХ: розово-белый мрамор, зелёная рамка, ромб",
    "sl-4034p": "SL-4034P ПВХ: бежевый, плетёный квадрат-ромб",
    "sl-4173p": "SL-4173P ПВХ: белый мрамор в коричневой рамке",
    "sl-4106d": "SL-4106D мрамор: кремовый центр, чёрный гранит",
    "sl-4145d": "SL-4145D мрамор: серо-зелёный",
    "sl-4157d": "SL-4157D мрамор: крем, светло-коричневая рамка",
    "sl-4182d": "SL-4182D мрамор: эмперадор, ромб в квадрате",
    "sl-4028p": "SL-4028P ПВХ узор (по фото SL-1036)",
    "sl-4017p": "SL-4017P ПВХ: серая крошка (по фото SL-1072)",
    "sl-4012p": "SL-4012P ПВХ узор (по фото SL-1095)",
    "sl-4072d": "SL-4072D мрамор (по фото SL-1109)",
    "sl-4150d": "SL-4150D мрамор (по фото SL-1135)",
    "sl-4082d": "SL-4082D мрамор (по фото SL-1136)",
    "sl-4039d": "SL-4039D мрамор с медальоном (по фото SL-1137)",
    "sl-4036p": "SL-4036P ПВХ узор (условно, на фото SL-1130 не виден)",
}


def mid_of(fid):
    return "liftfloor_" + fid.replace("-", "_")


def medallion(cv, rng):
    """4039d: a four-petal rose inside the gold ring: emperador petals with gold outlines, gold leaves between."""
    petals, leaves, outl = [], [], []
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        # petal: teardrop from the centre outwards
        pts = []
        for t in np.linspace(0, 1, 40):
            r = 0.035 + 0.17 * t
            w = 0.075 * math.sin(math.pi * t) ** 0.8 + 0.02 * (1 - t)
            pts.append((r, w))
        poly = [(0.5 + r * math.cos(a) - w * math.sin(a), 0.5 + r * math.sin(a) + w * math.cos(a)) for r, w in pts]
        poly += [(0.5 + r * math.cos(a) + w * math.sin(a), 0.5 + r * math.sin(a) - w * math.cos(a)) for r, w in pts[::-1]]
        petals.append(poly)
        b = a + math.pi / 4
        leaves.append([(0.5 + 0.06 * math.cos(b), 0.5 + 0.06 * math.sin(b)),
                       (0.5 + 0.2 * math.cos(b - 0.12), 0.5 + 0.2 * math.sin(b - 0.12)),
                       (0.5 + 0.225 * math.cos(b), 0.5 + 0.225 * math.sin(b)),
                       (0.5 + 0.2 * math.cos(b + 0.12), 0.5 + 0.2 * math.sin(b + 0.12))])
    gold = K.stone(rng, N, N, MM, S["gold_marble"])
    pet = K.stone(rng, N, N, MM, S["emperador_dark"])
    m_leaf = sum(K.poly_mask(cv, p) for p in leaves).clip(0, 1)
    m_pet = sum(K.poly_mask(cv, p) for p in petals).clip(0, 1)
    # gold outline of the petals: dilate by blurring
    m_out = np.clip(K.blur_edge(m_pet, 3.0) * 2.2, 0, 1)
    m_core = K.poly_mask(cv, ellipse(0.5, 0.5, 0.04))
    return [(gold, m_leaf), (gold, m_out), (pet, m_pet), (gold, m_core)]


def build(fid):
    lay = LAYOUTS[fid]
    rng = np.random.default_rng(sum(map(ord, fid)) * 7919)
    cv = K.Canvas(N, N, 4)
    marble = lay["kind"] == "marble"
    out = np.zeros((N, N, 3))
    joints = np.zeros((N, N))
    cache = {}
    for stone_id, polys in lay["pieces"]:
        for i, poly in enumerate(polys):
            key = (stone_id, i if marble else 0)          # PVC: one printed film; marble: each piece its own slab
            if key not in cache:
                cache[key] = K.stone(rng, N, N, MM, S[stone_id])
            m = K.poly_mask(cv, poly)
            out = out * (1 - m[..., None]) + cache[key] * m[..., None]
            joints = np.maximum(joints, np.clip(m * (1 - m) * 4, 0, 1))
    if lay.get("medallion"):
        for tex, m in medallion(cv, rng):
            out = out * (1 - m[..., None]) + tex * m[..., None]
            joints = np.maximum(joints, np.clip(m * (1 - m) * 4, 0, 1) * 0.5)
    if lay.get("tiles"):
        nx, ny, (u0, v0, u1, v1) = lay["tiles"]
        t = np.zeros((N, N))
        for k in range(1, nx):
            x = (u0 + (u1 - u0) * k / nx) * N
            t = np.maximum(t, np.clip(1 - np.abs(np.arange(N)[None, :] - x) / 0.8, 0, 1) * np.ones((N, 1)))
        for k in range(1, ny):
            y = (v0 + (v1 - v0) * k / ny) * N
            t = np.maximum(t, np.clip(1 - np.abs(np.arange(N)[:, None] - y) / 0.8, 0, 1) * np.ones((1, N)))
        inside = K.poly_mask(cv, R(u0, v0, u1, v1))
        joints = np.maximum(joints, t * inside * 0.5)
    # joints: hairline darkening (marble: open joint; PVC: the printed line of the film)
    jk = 0.35 if marble else 0.18
    out = out * (1 - jk * joints[..., None])
    if marble:
        hgt = -joints * 1.0
        nrm = K.normal_from_height(K.blur_edge(hgt, 0.6), k=0.5, periodic=False)
        sm = 0.8 - 0.35 * joints
    else:
        emb = K.noise(rng, N, N, 0.9) + 0.6 * K.noise(rng, N, N, 3.0)
        hgt = 0.1 * emb - 0.4 * joints
        nrm = K.normal_from_height(hgt, tilt_deg=1.2, periodic=False)
        sm = 0.35 + 0.02 * K.smoothstep(-2, 2, emb)
    msk = K.mask_map(0.0, sm)
    return K.to8(out), nrm, msk


def check_sheet(ids):
    rows = []
    for fid in ids:
        mid = mid_of(fid)
        alb = Image.open(K.EXT / "Materials" / mid / f"{mid}_albedo.jpg")
        ims = [alb.resize((300, 300)), alb.resize((214, 300)), alb.resize((300, 210))]
        img = K.REF / "floors" / f"{fid}.jpg"
        if img.exists():
            ims.insert(0, Image.open(img).convert("RGB").resize((300, 300)))
        else:
            cab = {"sl-4028p": "sl-1036", "sl-4017p": "sl-1072", "sl-4012p": "sl-1095", "sl-4072d": "sl-1109",
                   "sl-4150d": "sl-1135", "sl-4082d": "sl-1136", "sl-4039d": "sl-1137", "sl-4036p": "sl-1130"}[fid]
            c = Image.open(K.REF / "cabins" / f"{cab}.jpg").convert("RGB")
            ims.insert(0, K.fit_h(c.crop((0, int(c.height * 0.62), c.width, c.height)), 300))
        rows.append((f"{mid} ({LAYOUTS[fid]['kind']}, mean {K.mean_hex(np.asarray(alb))}): ref | 1:1 | 0.7 | 1.4", ims))
    # two floors per sheet row
    return [(a[0] + "    ||    " + (b[0] if b else ""), a[1] + (b[1] if b else []))
            for a, b in zip(rows[::2], rows[1::2] + [None])]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*")
    ap.add_argument("--no-merge", action="store_true")
    args = ap.parse_args(argv)
    ids = args.ids or list(LAYOUTS)
    for fid in ids:
        alb, nrm, msk = build(fid)
        K.write_material(mid_of(fid), alb, nrm, msk)
        print(mid_of(fid), K.mean_hex(alb))
    entries = [K.entry(mid_of(f), NAMES[f], SOURCE, (1, 1), N) for f in LAYOUTS]
    half = (len(LAYOUTS) + 1) // 2
    allids = list(LAYOUTS)
    K.sheet(check_sheet(allids[:10]), K.SHEETS / "floors.png", "Lift floors (pictured, catalogue p.21)")
    K.sheet(check_sheet(allids[10:]), K.SHEETS / "floors_cabins.png", "Lift floors (from cabin photos)")
    K.write_entries(FAMILY, entries, merge=not args.no_merge)


if __name__ == "__main__":
    main()
