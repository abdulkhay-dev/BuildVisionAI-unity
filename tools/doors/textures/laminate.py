#!/usr/bin/env python3
"""Door finishes of the line "Ламинированные" (catalogue pp. 114-125): printed paper laminate - Italian and Milan
walnut, wenge and white prints; flat, slightly glossy.

    python3 tools/doors/textures/laminate.py [ids] [--compare] [--no-write] [--fit] [--slopes]

See tools/doors/textures/grain.py for the structures, the colour model and the outputs.
"""
import grain

FAMILY = "laminate"
LINE = "Ламинированные"
SOURCE = "procedural:tools/doors/textures/laminate.py"

# pattern (+ seed = another print of it); color = catalogue mean (sRGB, linear-light mean of the photos' crops);
# dark / light = full-strength line colours (hue from --slopes); comb / tone = L* std of lines / broad tone;
# smooth = the laminate's gloss (mask alpha / 255)
FINISHES = [
    dict(id="l-11-italoreh", material="door_l_11_italoreh", name="Л-11 ИталОрех", tag="ламинат",
         pattern="ital", color="#7b3620", dark="#5e2110", light="#9a4d31", comb=1.46, tone=2.58, smooth=0.52),
    dict(id="l-12-milanoreh", material="door_l_12_milanoreh", name="Л-12 МиланОрех", tag="ламинат",
         pattern="milan", color="#c98546", dark="#af6224", light="#dfa363", comb=1.48, tone=3.34, smooth=0.52),
    dict(id="l-13-wenge", material="door_l_13_wenge", name="Л-13 Венге", tag="ламинат",
         pattern="wenge", color="#3c2418", dark="#2b1609", light="#634432", comb=2.4, tone=1.0, smooth=0.52),
    dict(id="l-23-white", material="door_l_23_white", name="Л-23 Белый", tag="ламинат",
         pattern="paper", color="#d4d4d3", dark="#c9c8c9", light="#dcdcd9", comb=0.2, tone=0.3, smooth=0.55),
]

# flat areas of the catalogue photos (file, (x0, y0, x1, y1)); the first one is shown on the check sheet
REFS = {
    "l-11-italoreh": [
        ("p125_gost-l-11__italoreh.jpg", (30, 30, 340, 400)),
        ("p125_gost-l-11__italoreh.jpg", (110, 470, 340, 800)),
        ("p115_1g-l-11__italoreh.jpg", (30, 30, 140, 420)),
        ("p115_1g-l-11__italoreh.jpg", (228, 30, 340, 800)),
        ("p116_2s-l-11__italoreh.jpg", (30, 30, 125, 420)),
        ("p116_2s-l-11__italoreh.jpg", (250, 30, 340, 800)),
    ],
    "l-12-milanoreh": [
        ("p125_gost-l-12__milanoreh.jpg", (30, 30, 340, 400)),
        ("p125_gost-l-12__milanoreh.jpg", (110, 470, 340, 800)),
        ("p115_1g-l-12__milanoreh.jpg", (30, 30, 140, 420)),
        ("p115_1g-l-12__milanoreh.jpg", (228, 30, 340, 800)),
        ("p116_2s-l-12__milanoreh.jpg", (30, 30, 125, 420)),
        ("p116_2s-l-12__milanoreh.jpg", (250, 30, 340, 800)),
    ],
    "l-13-wenge": [
        ("p125_gost-l-13__venge.jpg", (12, 12, 140, 160)),
        ("p125_gost-l-13__venge.jpg", (40, 200, 140, 330)),
    ],
    "l-23-white": [
        ("p125_gost-l-23__belyy.jpg", (20, 20, 140, 160)),
        ("p125_gost-l-23__belyy.jpg", (40, 200, 140, 330)),
    ],
}

if __name__ == "__main__":
    grain.run(FAMILY, LINE, FINISHES, REFS, SOURCE)
