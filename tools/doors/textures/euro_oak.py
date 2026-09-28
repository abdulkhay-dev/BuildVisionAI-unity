#!/usr/bin/env python3
"""Door finishes "ЕвроШпон" (el'PORTA, series CLASSICO and LEGNO): a printed straight-grain oak film under acrylic
lacquer - Real Oak, Milk Oak, Brown Oak, Thermo Oak.

    python3 tools/doors/textures/euro_oak.py [ids] [--compare] [--no-write] [--fit] [--analyze]

The catalogue renders (pages 68-73) show rift oak: dense straight lines, no cathedrals or knots, slow broad bands.
The structure (finish_kit.oak_structure) is built as the wood is: growth rings ~2 mm wide (earlywood with its pore
dashes, a transition, a lighter latewood whose tone varies ring to ring and drifts along the grain), short slanted
light ray flecks, a few long darker / lighter streaks, broad bands with a flame-like wander; the print is embossed
at the pores. Milk Oak is the whitened colourway: light ground, grey pores.
"""
import finish_kit as kit

PATTERNS = {
    "eurooak": dict(
        seed=6101, warp=[(1.0, 420.0, 30.0), (0.2, 70.0, 5.0)],
        ring=(2.0, 0.45), ring_rho=0.6, early=(0.3, 0.07), trans=0.2,
        ring_tone=(-1.0, -0.3, 0.45), ring_var=0.35, drift=0.45, drift_len=110.0, hp=4.0,
        pores=dict(len=5.0, duty=0.55, alpha=0.75, late=0.12),
        rays=dict(per_cm=1.0, width=(0.6, 0.3), length=(5.0, 0.5), alpha=(0.15, 0.6), fade=0.3, slope=0.04),
        dark=dict(per_cm=0.25, width=(0.5, 0.4), length=(260.0, 0.8), alpha=(0.2, 0.8), fade=0.7, slope=0.002),
        light=dict(per_cm=0.3, width=(0.9, 0.4), length=(160.0, 0.8), alpha=(0.2, 0.8), fade=0.8, slope=0.002),
        fade_len=20.0, bands=(16.0, 900.0), cluster=(3.5, 160.0), cluster_share=0.45, band_warp=(3.0, 350.0, 40.0),
        fibre=(0.4, 3.0), fibre_share=0.15,
        relief=dict(pore=1.0, ring=0.2, fibre=0.25, tilt_deg=2.5),
    ),
}


def eurooak(scale=1.0, seed=None):
    return kit.oak_structure(PATTERNS["eurooak"], scale, seed)


# color: catalogue mean (sRGB, linear-light mean of the REFS); dark / light: full-strength streak colours (the ground
# tone goes towards them; hue from the photos' a*/b* slopes); pore / fleck: pore and ray colours at strength
# pore_k / fleck_k; comb / tone: L* std of the fine lines / broad bands (--fit); smooth: acrylic lacquer.
FINISHES = [
    dict(id="real-oak", material="door_real_oak", name="Real Oak", pattern="eurooak",
         color="#c59762", dark="#90632e", light="#e0b27d", pore="#855924", fleck="#e6b883",
         comb=0.60, tone=0.65, pore_k=0.4, fleck_k=0.5, smooth=0.42),
    dict(id="milk-oak", material="door_milk_oak", name="Milk Oak", pattern="eurooak",
         color="#e1e0e5", dark="#afaeb3", light="#efeef3", pore="#a4a4a9", fleck="#efeef3",
         comb=1.19, tone=0.53, pore_k=0.6, fleck_k=0.5, smooth=0.42),
    dict(id="brown-oak", material="door_brown_oak", name="Brown Oak", pattern="eurooak",
         color="#583724", dark="#41210e", light="#6e4c39", pore="#3c1c07", fleck="#704f3b",
         comb=2.53, tone=0.89, pore_k=0.6, fleck_k=0.5, smooth=0.42),
    dict(id="thermo-oak", material="door_thermo_oak", name="Thermo Oak", pattern="eurooak",
         color="#3c2720", dark="#2b160e", light="#4e3932", pore="#29140b", fleck="#4e3932",
         comb=2.30, tone=0.68, pore_k=0.6, fleck_k=0.5, smooth=0.42),
]

REFS = {
    "real-oak": [
        ("p069_klassiko-12__real-oak.jpg", (303, 60, 340, 790)),
        ("p069_klassiko-12__real-oak.jpg", (55, 60, 91, 420)),
        ("p069_klassiko-12__real-oak.jpg", (130, 135, 265, 480)),
        ("p069_klassiko-13__real-oak.jpg", (127, 25, 142, 330)),
    ],
    "milk-oak": [
        ("p069_klassiko-12__milk-oak.jpg", (127, 25, 142, 330)),
        ("p069_klassiko-13__milk-oak.jpg", (127, 25, 142, 330)),
        ("p073_legno-21__milk-oak.jpg", (123, 15, 139, 330)),
        ("p073_legno-38__milk-oak.jpg", (123, 15, 139, 330)),
        ("p069_klassiko-12__milk-oak.jpg", (48, 50, 112, 185)),
    ],
    "brown-oak": [
        ("p069_klassiko-12__brown-oak.jpg", (127, 25, 142, 330)),
        ("p069_klassiko-13__brown-oak.jpg", (127, 25, 142, 330)),
        ("p073_legno-21__brown-oak.jpg", (123, 15, 139, 330)),
        ("p073_legno-38__brown-oak.jpg", (123, 15, 139, 330)),
        ("p069_klassiko-12__brown-oak.jpg", (48, 50, 112, 185)),
    ],
    "thermo-oak": [
        ("p069_klassiko-12__thermo-oak.jpg", (127, 25, 142, 330)),
        ("p069_klassiko-13__thermo-oak.jpg", (127, 25, 142, 330)),
        ("p069_klassiko-12__thermo-oak.jpg", (48, 50, 112, 185)),
    ],
}

FAMILY = dict(id="euro-oak", line="ЕвроШпон", suffix="ЕвроШпон", module="euro_oak.py",
              patterns={"eurooak": eurooak}, finishes=FINISHES, refs=REFS)

if __name__ == "__main__":
    kit.main(FAMILY)
