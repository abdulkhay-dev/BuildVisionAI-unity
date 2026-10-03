"""xyj-5 Wrist Extension Flexion Exerciser (wall). Photo front, 1.73 mm/px; W 520 = the wooden bar."""
from k7lib import *

d = D("xyj-5", [520, 260, 980], {
    "teal": "plastic#0a9486", "tealdk": "plastic#076a60", "chrome": "chrome", "black": "plastic#1b1d1f",
    "wood": "wood#d39a6c", "pink": "gloss#e7728f"})
CX = 242
rail_unit(d, CX, 980, 0, (617, 868), None, plate_w=196, plate_h=(52, 55), rail_gap=150, lever=(512, 796, 26))
# --- flat wooden handle bar through the friction hub
d.box("bar", [0, 742, 150, 520, 764, 192], "wood", r=6)
# --- friction hub: black body, chrome top clamp, red-pink front cap; small chrome knob with a pink cap at its right
d.box("hub", [216, 680, 120, 284, 776, 204], "black", r=8)
d.box("hub-clamp", [220, 772, 128, 280, 792, 196], "chrome", r=6)
d.box("hub-cap", [228, 698, 203, 274, 740, 210], "pink", r=6)
d.cyl("hub-axle", [206, 753, 171], [294, 753, 171], 30, "chrome")
d.box("knob-chrome", [288, 760, 150, 306, 790, 196], "chrome", r=5)
d.box("knob-cap", [289, 728, 160, 305, 762, 202], "pink", r=5)
d.save()
