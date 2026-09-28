#!/usr/bin/env python3
"""Door finishes "Шпон файн-лайн" (BRAVO): reconstituted veneer with dead-straight fine lines.

    python3 tools/doors/textures/fine_line.py [ids] [--compare] [--no-write] [--fit] [--analyze]

Fine-line veneer is sliced from a glued block of dyed peeled veneer, so its figure is laminations only: layers
~0.5-1.5 mm thick whose tone alternates, dead straight (no warp), a tone that drifts only slowly along the grain,
rare darker glue lines and lighter streaks that run the whole length, and broad very long bands. Built with wave 1's
lamination model (make_finishes.structure) through tools/doors/textures/finish_kit.py; colours fitted to the
catalogue (pages 94-101: РОНДО, АФИНА, СОНАТА, ГРЕЦИЯ, ЛАГУНА, ЭКСКЛЮЗИВ, ЭТЮД ...).
"""
import numpy as np

import finish_kit as kit

PATTERNS = {
    # straight laminations; the RONDO photo (the only big one) shows dense fine lines, a few darker thin lines and
    # longer light streaks, with broad bands several cm wide
    "fineline": dict(
        seed=9101, warp=[(0.12, 1500.0, 80.0)], band_warp=(0.5, 1500.0, 120.0),
        comb=dict(thickness=(0.8, 0.55), rho=-0.45, drift=0.45, drift_len=260.0, hp=4.0, mod=(0.3, 25.0, 700.0)),
        dark=dict(per_cm=0.35, width=(0.45, 0.35), length=(700.0, 0.6), alpha=(0.25, 0.9), fade=0.5, slope=0.0),
        light=dict(per_cm=0.35, width=(0.8, 0.45), length=(450.0, 0.7), alpha=(0.25, 0.9), fade=0.6, slope=0.0),
        fade_len=90.0, bands=(14.0, 1600.0), cluster=(3.5, 420.0), cluster_share=0.45, fibre=(0.35, 5.0),
        fibre_share=0.12,
        relief=dict(comb=0.5, groove=0.8, fibre=0.35, tilt_deg=1.6),
    ),
}


PORES = dict(seed=9102, len=2.5, duty=0.06, alpha=0.8, depth=0.6)


def fineline(scale=1.0, seed=None):
    st = kit.wave1_structure("fine_line.fineline", PATTERNS["fineline"], scale, seed)
    # the peeled veneer's own pores: sparse short dashes along the lines (colour `pore`, default dark, x pore_k)
    rng = np.random.default_rng(PORES["seed"] if seed is None else seed + 1)
    px = scale / kit.MM
    st["pore"] = PORES["alpha"] * kit.dashes(rng, np.zeros((kit.ALBEDO[1], kit.ALBEDO[0])), px, PORES["len"],
                                             PORES["duty"])
    st["height"] = st["height"] - PORES["depth"] * st["pore"]
    st["rough"] = st["rough"] + st["pore"]
    return st


# color: catalogue mean (sRGB, linear-light mean of the REFS); dark / light: full-strength line colours (their hue
# follows the photos' a*/b* slopes); comb / tone: L* std of the fine lines / broad bands (--fit); smooth: lacquer.
FINISHES = [
    dict(id="f-01-oak", material="door_f_01_oak", name="Ф-01 Дуб", pattern="fineline",
         color="#d5a27d", dark="#b5815c", light="#ebb893", comb=2.34, tone=1.83, pore_k=0.35, smooth=0.40),
    dict(id="f-11-walnut", material="door_f_11_walnut", name="Ф-11 Орех", pattern="fineline",
         color="#8e5a32", dark="#6c3f1d", light="#a8764b", comb=1.90, tone=2.00, pore_k=0.35, smooth=0.40),
    dict(id="f-15-makore", material="door_f_15_makore", name="Ф-15 Макоре", pattern="fineline",
         color="#733224", dark="#52180e", light="#8c4636", comb=1.60, tone=2.00, pore_k=0.35, smooth=0.40),
    dict(id="f-17-chocolate", material="door_f_17_chocolate", name="Ф-17 Шоколад", pattern="fineline",
         color="#552e1a", dark="#3a1809", light="#6c4432", comb=2.20, tone=1.10, pore_k=0.35, smooth=0.40),
    dict(id="f-22-white-oak", material="door_f_22_white_oak", name="Ф-22 БелДуб", pattern="fineline",
         color="#ede4dc", dark="#d3c8bd", light="#faf6f1", comb=1.11, tone=0.42, pore_k=0.35, smooth=0.40),
    dict(id="f-27-wenge", material="door_f_27_wenge", name="Ф-27 Венге", pattern="fineline",
         color="#3f261b", dark="#26120a", light="#56403a", comb=1.38, tone=0.39, pore_k=0.35, smooth=0.40),
]

# Flat, vertical-grain areas of the catalogue photos (file, box[, "rot" = grain horizontal in the photo]); the first
# one of each finish is shown on the check sheet.
REFS = {
    "f-01-oak": [
        ("p095_rondo-f-01__dub.jpg", (303, 55, 339, 790)),
        ("p095_rondo-f-01__dub.jpg", (105, 60, 295, 780), "rot"),
        ("p095_rondo-f-01__dub.jpg", (32, 60, 92, 420)),
        ("p100_laguna-f-01__dub.jpg", (125, 20, 137, 330)),
        ("p100_eksklyuziv-f-01__dub.jpg", (108, 20, 137, 330)),
    ],
    "f-11-walnut": [
        ("p100_laguna-f-11__oreh.jpg", (125, 20, 137, 330)),
        ("p099_greciya-f-11__oreh.jpg", (125, 20, 138, 330)),
        ("p098_stil-f-11__oreh.jpg", (129, 55, 143, 330)),
        ("p097_karolina-f-11__oreh.jpg", (131, 50, 145, 330)),
    ],
    "f-15-makore": [
        ("p100_eksklyuziv-f-15__makore.jpg", (108, 20, 137, 330)),
        ("p099_greciya-f-15__makore.jpg", (125, 20, 138, 330)),
        ("p098_karolina-f-15__makore.jpg", (131, 50, 145, 330)),
    ],
    "f-17-chocolate": [
        ("p100_eksklyuziv-f-17__shokolad.jpg", (108, 20, 137, 330)),
        ("p100_laguna-f-17__shokolad.jpg", (125, 20, 137, 330)),
    ],
    "f-22-white-oak": [
        ("p095_rondo-f-22__beldub.jpg", (40, 20, 118, 330), "rot"),
        ("p095_rondo-f-22__beldub.jpg", (123, 20, 137, 330)),
        ("p099_stil-f-22__beldub.jpg", (129, 55, 143, 330)),
    ],
    "f-27-wenge": [
        ("p095_rondo-f-27__venge.jpg", (40, 20, 118, 330), "rot"),
        ("p095_rondo-f-27__venge.jpg", (123, 20, 137, 330)),
        ("p096_etyud-f-27-f-01__venge-dub.jpg", (118, 20, 138, 330)),
        ("p096_etyud-f-27-f-01__venge-dub.jpg", (12, 20, 34, 175)),
    ],
}

FAMILY = dict(id="fine-line", line="Шпон файн-лайн", suffix="шпон файн-лайн", module="fine_line.py",
              patterns={"fineline": fineline}, finishes=FINISHES, refs=REFS)

if __name__ == "__main__":
    kit.main(FAMILY)
