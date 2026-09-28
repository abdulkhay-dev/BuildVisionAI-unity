#!/usr/bin/env python3
"""Door finish of the line "Массив" (catalogue pp. 104-105): unfinished solid pine of glued lamellas.

    python3 tools/doors/textures/solid.py [--compare] [--no-write] [--fit] [--slopes]

See tools/doors/textures/grain.py for the structures, the colour model and the outputs.
"""
import grain

FAMILY = "solid"
LINE = "Массив"
SOURCE = "procedural:tools/doors/textures/solid.py"

# pattern "pine": lamellas 45-90 mm wide; comb / tone = L* std of the rings / lamella tones; smooth = bare sanded wood
FINISHES = [
    dict(id="solid-pine", material="door_solid_pine", name="Без отделки", tag="массив сосны",
         pattern="pine", seed=1503, color="#dcc192", dark="#b89356", light="#f3daac", comb=2.4, tone=2.0, smooth=0.22,
         smooth_var=0.03),
]

# flat areas of the catalogue photos (stiles); the first one is on the check sheet
REFS = {
    "solid-pine": [
        ("p105_klasiko-13-wc__bez-otdelki.jpg", (55, 60, 95, 800)),
        ("p105_klasiko-13-wc__bez-otdelki.jpg", (305, 60, 345, 800)),
        ("p105_porta-21__bez-otdelki.jpg", (40, 40, 75, 800)),
        ("p105_porta-21__bez-otdelki.jpg", (300, 40, 335, 800)),
    ],
}

if __name__ == "__main__":
    grain.run(FAMILY, LINE, FINISHES, REFS, SOURCE)
