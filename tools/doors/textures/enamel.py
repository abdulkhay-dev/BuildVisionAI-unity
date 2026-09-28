#!/usr/bin/env python3
"""Door finishes of the line "Окрашенные (эмаль)" (series SKINNY, catalogue pp. 108-111, swatches p. 108): MDF
sprayed with enamel - smooth, satin, a very fine orange peel; no grain.

    python3 tools/doors/textures/enamel.py [ids] [--compare] [--no-write] [--fit] [--slopes]

See tools/doors/textures/grain.py for the structures, the colour model and the outputs.
"""
import grain

FAMILY = "enamel"
LINE = "Окрашенные (эмаль)"
SOURCE = "procedural:tools/doors/textures/enamel.py"

# pattern "enamel" (plain): comb / tone = L* std of the faint mottle; smooth = satin enamel (mask alpha / 255)
FINISHES = [
    dict(id="enamel-whitey", material="door_enamel_whitey", name="Whitey", tag="эмаль SKINNY",
         pattern="enamel", color="#e2e2e2", dark="#dadada", light="#e8e8e8", comb=0.15, tone=0.25, smooth=0.47),
    dict(id="enamel-cream", material="door_enamel_cream", name="Cream", tag="эмаль SKINNY",
         pattern="enamel", seed=2502, color="#fbefdf", dark="#efe2d1", light="#fff6e8", comb=0.15, tone=0.25,
         smooth=0.47),
    dict(id="enamel-mocca", material="door_enamel_mocca", name="Mocca", tag="эмаль SKINNY",
         pattern="enamel", seed=2503, color="#7c6a60", dark="#705e54", light="#847369", comb=0.2, tone=0.3,
         smooth=0.47),
]

# flat areas of the catalogue photos; the first one is on the check sheet
REFS = {
    "enamel-whitey": [
        ("p109_skinni-10__whitey.jpg", (30, 40, 340, 400)),
        ("p109_skinni-10__whitey.jpg", (110, 450, 340, 800)),
        ("p109_skinni-12__whitey.jpg", (130, 30, 146, 300)),
        ("p110_skinni-14__whitey.jpg", (130, 30, 146, 300)),
    ],
    "enamel-cream": [
        ("p109_skinni-12__cream.jpg", (130, 30, 146, 300)),
        ("p109_skinni-13__cream.jpg", (130, 30, 146, 300)),
        ("p110_skinni-14__cream.jpg", (130, 30, 146, 300)),
        ("p110_skinni-20__cream.jpg", (130, 30, 146, 300)),
        ("p111_skinni-21__cream.jpg", (130, 30, 146, 300)),
        ("p110_skinni-15-1__cream.jpg", (130, 30, 146, 300)),
    ],
    "enamel-mocca": [
        ("p109_skinni-12__mocca.jpg", (130, 30, 146, 300)),
        ("p109_skinni-12__mocca.jpg", (24, 30, 38, 160)),
        ("p109_skinni-12__mocca.jpg", (24, 210, 38, 300)),
        ("p110_skinni-13__mocca.jpg", (130, 30, 146, 300)),
        ("p110_skinni-13__mocca.jpg", (24, 30, 38, 160)),
        ("p110_skinni-13__mocca.jpg", (24, 210, 38, 300)),
    ],
}

if __name__ == "__main__":
    grain.run(FAMILY, LINE, FINISHES, REFS, SOURCE)
