#!/usr/bin/env python3
"""Door finishes "ЭкоШпон Crosscut" (el'PORTA, series PORTA Z): a wood-grain film with a crosshatch.

    python3 tools/doors/textures/crosscut.py [ids] [--compare] [--no-write] [--fit] [--analyze]

The catalogue (pages 30-33) calls it "антивандальный ЭкоШпон с продольно-поперечным тиснением": a printed long
grain (fine laminations, streaks, broad bands - wave 1's film model, make_finishes.structure) under a linen-like
crosshatch that is both printed and embossed. Measured on the renders (line spectra of the big photos, 0.39 px/mm,
and of the zoom insets of page 32, ~0.75 px/mm): thin straight lines across the grain about every 7-10 mm (light
ones on Wenge; light and dark ones on Cappuccino / Grey / Bianco), broken into dashes and stronger in long stripes
along the grain (the "plaid" of the photos), and a fainter set along the grain ~5-6 mm apart. Here:
  * base: wave 1's laminations + dark / light streaks + bands;
  * xlight / xdark: the hatch lines (finish_kit.straight_lines: exact pixel coverage, jittered pitch, opacity that
    comes and goes along each line), across the grain times a plaid field, plus the fainter set along the grain;
  * relief: the hatch is pressed in (grooves), the laminations a little.
"""
import numpy as np

import finish_kit as kit

PATTERNS = {
    "crosscut": dict(
        base=dict(
            seed=3053, warp=[(0.8, 300.0, 25.0), (0.15, 60.0, 6.0)], band_warp=(2.5, 400.0, 40.0),
            comb=dict(thickness=(0.9, 0.55), rho=-0.45, drift=0.6, drift_len=45.0, hp=3.5, mod=(0.35, 15.0, 300.0)),
            dark=dict(per_cm=0.7, width=(0.45, 0.4), length=(220.0, 0.9), alpha=(0.3, 1.0), fade=0.8,
                      slope=0.002),
            light=dict(per_cm=0.6, width=(0.7, 0.45), length=(120.0, 0.8), alpha=(0.3, 1.0), fade=0.8,
                       slope=0.002),
            fade_len=18.0, bands=(18.0, 1100.0), cluster=(3.5, 160.0), cluster_share=0.45, fibre=(0.4, 3.0),
            fibre_share=0.14,
            relief=dict(comb=0.5, groove=0.8, fibre=0.2, tilt_deg=3.0),
        ),
        hatch_seed=3054,
        # lines across the grain: pitch / width (median mm, log-sigma), opacity range, dash length (mm), visible
        # share, share of light lines; plaid = stripes along the grain where they are stronger
        across=dict(pitch=(4.0, 0.3), width=(1.1, 0.3), strength=(0.6, 1.0), jitter=12.0, share_on=0.85,
                    light=0.5, wander=0.25),
        plaid=dict(along=380.0, across=11.0, floor=0.6),
        along=dict(pitch=(5.5, 0.3), width=(0.8, 0.3), strength=(0.3, 0.9), jitter=40.0, share_on=0.6, light=0.5),
        along_k=0.6,
        emboss=dict(across=1.0, along=0.6, base=0.35, tilt_deg=5.0),
    ),
}


def crosscut(scale=1.0, seed=None):
    p = PATTERNS["crosscut"]
    st = kit.wave1_structure("crosscut.base", p["base"], scale, seed)
    rng = np.random.default_rng(p["hatch_seed"] if seed is None else seed + 1)
    px = scale / kit.MM
    w, h = kit.ALBEDO
    fields = {}
    for key, axis in (("across", 1), ("along", 0)):
        s = p[key]
        for tone, share in (("light", s["light"]), ("dark", 1 - s["light"])):
            if share <= 0:
                continue
            lo, hi = s["strength"]
            f = kit.straight_lines(rng, (s["pitch"][0] / share, s["pitch"][1]), s["width"], px, axis,
                                   s["jitter"], (lo, hi), share_on=s["share_on"], soft=0.55,
                                   wander=s.get("wander", 0.0), wander_len=60.0)
            fields[(key, tone)] = f
    pl = p["plaid"]
    plaid = kit.smoothstep(-0.9, 0.9, kit.gauss_noise(rng, (h, w), pl["along"] * px, pl["across"] * px))
    plaid = pl["floor"] + (1 - pl["floor"]) * plaid
    k = p["along_k"]
    union = lambda a, b: 1 - (1 - a) * (1 - b)
    st["xlight"] = union(fields[("across", "light")] * plaid, k * fields[("along", "light")])
    st["xdark"] = union(fields[("across", "dark")] * plaid, k * fields[("along", "dark")])
    e = p["emboss"]
    across = union(fields[("across", "light")], fields[("across", "dark")]) * plaid
    along = union(fields[("along", "light")], fields[("along", "dark")])
    st["height"] = -e["across"] * across - e["along"] * along + e["base"] * st["height"]
    st["relief"] = dict(st["relief"], tilt_deg=e["tilt_deg"])
    st["rough"] = across + along
    return st


# color: catalogue mean (sRGB, linear-light mean of the REFS); dark / light: full-strength streak colours;
# xlight / xdark: hatch line colours (default light / dark) at strength xlight_k / xdark_k; comb / tone: L* std of
# the fine lines / broad bands (--fit); smooth: the film's satin lacquer.
FINISHES = [
    dict(id="cappuccino-crosscut", material="door_cappuccino_crosscut", name="Cappuccino Crosscut",
         pattern="crosscut", color="#c5bab1", dark="#8b8077", light="#e1d6cd", comb=2.86, tone=1.13,
         xlight="#e1d6cd", xdark="#9f948b", xlight_k=1.0, xdark_k=1.0, smooth=0.36),
    dict(id="grey-crosscut", material="door_grey_crosscut", name="Grey Crosscut",
         pattern="crosscut", color="#8a8a8c", dark="#4f4f51", light="#b2b2b4", comb=4.45, tone=2.68,
         xlight="#afafb2", xdark="#626263", xlight_k=0.55, xdark_k=0.55, smooth=0.36),
    dict(id="wenge-crosscut", material="door_wenge_crosscut", name="Wenge Crosscut",
         pattern="crosscut", color="#3d2f2e", dark="#2a1c1b", light="#514342", comb=2.02, tone=0.83,
         xlight="#766766", xdark="#302221", xlight_k=1.0, xdark_k=0.4, smooth=0.38),
    dict(id="bianco-crosscut", material="door_bianco_crosscut", name="Bianco Crosscut",
         pattern="crosscut", color="#d4d5cf", dark="#aeaea8", light="#e5e6e0", comb=0.40, tone=0.81,
         xlight="#e2e3dd", xdark="#b9b9b3", xlight_k=0.5, xdark_k=0.6, smooth=0.36),
]

REFS = {
    "cappuccino-crosscut": [
        ("p031_porta-50__cappuccino-crosscut.jpg", (110, 40, 338, 790)),
        ("p033_porta-51-sa__cappuccino-crosscut.jpg", (160, 40, 350, 790)),
        ("p032_porta-50-a-6__cappuccino-crosscut.jpg", (20, 85, 140, 138)),
        ("p033_porta-51-wp__cappuccino-crosscut.jpg", (65, 15, 135, 330)),
    ],
    "grey-crosscut": [
        ("p031_porta-50__grey-crosscut.jpg", (110, 40, 338, 790)),
        ("p033_porta-51-s__grey-crosscut.jpg", (65, 15, 135, 330)),
        ("p033_porta-51-sa__grey-crosscut.jpg", (65, 15, 135, 330)),
    ],
    "wenge-crosscut": [
        ("p032_porta-50-a-6__wenge-crosscut.jpg", (130, 360, 365, 505)),
        ("p032_porta-50-a-6__wenge-crosscut.jpg", (40, 30, 365, 180)),
        ("p032_porta-50-a-6__wenge-crosscut.jpg", (40, 525, 365, 670)),
        ("p031_porta-50__wenge-crosscut.jpg", (45, 15, 135, 330)),
        ("p033_porta-51-sa__wenge-crosscut.jpg", (65, 15, 135, 330)),
    ],
    "bianco-crosscut": [
        ("p031_porta-50__bianco-crosscut.jpg", (45, 15, 135, 330)),
        ("p033_porta-51-sa__bianco-crosscut.jpg", (65, 15, 135, 330)),
        ("p033_porta-51-ww__bianco-crosscut.jpg", (65, 15, 135, 330)),
        ("p032_porta-50-a-6__bianco-crosscut.jpg", (20, 85, 140, 138)),
    ],
}

FAMILY = dict(id="crosscut", line="ЭкоШпон", suffix="ЭкоШпон", module="crosscut.py",
              patterns={"crosscut": crosscut}, finishes=FINISHES, refs=REFS)

if __name__ == "__main__":
    kit.main(FAMILY)
