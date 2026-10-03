"""XY-JZJ-I smart posture mirror: tall graphite mirror panel with a portrait touch screen, black pedestal on an H base
with 4 twin castors; the back is black with a raised mount box and a chrome handle."""
from k9lib import *
d = K("xy-jzj-i", [900, 700, 2000], {
    "glass": "gloss#505357", "body": "plastic#1f2023", "base": "plastic#232427", "chrome": "chrome", "dot": "black#0c0c0d"})
CX = 450
PW, PB, PT = 610, 370, 2000           # panel width, bottom, top
Z0, Z1 = 318, 378                      # panel back / front
x0, x1 = CX - PW / 2, CX + PW / 2
# panel: black body, dark graphite mirror glass on the front
d.box("panel", [x0, PB, Z0, x1, PT, Z1 - 6], "body", r=8)
d.box("glass", [x0 + 1, PB + 1, Z1 - 8, x1 - 1, PT - 1, Z1], "glass", r=3)
# portrait screen: the crop (UI + a thin grey strip on its right) laid over the glass, the strip masked
SW, ST, SB = 510, PT - 148, PT - 148 - 1040
crop_screen(d, "screen", "dot", "med_xy-jzj-i_screen", [CX - SW / 2, SB, CX + SW / 2, ST], Z1 + 2, (413, 800), (15, 8, 410, 790),
            "glass", outer=[x0 + 1, PB + 1, x1 - 1, PT - 1])
d.decal("camera", [CX, PT - 70, Z1 + 6.2], [12, 12], "front", "dot")
d.decal("sensor", [CX, SB - 95, Z1 + 6.2], [10, 10], "front", "dot")
# back: raised mount box with a chrome handle (rear view of the leaflet)
d.box("mount", [CX - 172, PB, Z0 - 45, CX + 172, PB + 1110, Z0 + 2], "body", r=10)
d.box("mount-seam", [CX - 160, PB + 1000, Z0 - 47, CX + 160, PB + 1004, Z0 - 44], "plastic#34363a", r=1)
d.cyl("handle", [CX - 140, PB + 630, Z0 - 75], [CX + 140, PB + 630, Z0 - 75], 22, "chrome")
for nm, x in (("l", CX - 125), ("r", CX + 125)):
    d.cyl(f"handle-post-{nm}", [x, PB + 630, Z0 - 45], [x, PB + 630, Z0 - 78], 18, "chrome")
# base (photos, review 2026-10-03): a black pedestal block under the panel with concave flared flanks, and a
# pinwheel ("Z") base: a node block at the pedestal's front-left corner (castor under it) carries the long left arm
# running back-left to the left castor; a node at the back-right corner (castor under it) carries the long right arm
# running forward-right to the right castor
d.box("pedestal", [CX - 150, 125, 275, CX + 150, PB + 4, 425], "base", r=10)
for nm, x0_, x1_, z0_, z1_ in (("l", CX - 150, CX - 235, 380, 425), ("r", CX + 150, CX + 235, 275, 320)):
    d.slab(f"flare-{nm}", "front", f"M {x0_} {PB - 40} Q {x0_} 182 {x1_} 182 L {x0_} 182 Z", [z0_, z1_], "base", r=4)
FL, BR = (CX - 165, 500), (CX + 165, 200)
d.box("node-fl", [FL[0] - 45, 110, FL[1] - 85, FL[0] + 45, 185, FL[1] + 50], "base", r=8)
d.box("node-br", [BR[0] - 45, 110, BR[1] - 50, BR[0] + 45, 185, BR[1] + 85], "base", r=8)
d.bar("arm-l", [FL[0], 155, FL[1] - 20], [45, 155, 330], [70, 60], "base", r=8)
d.bar("arm-r", [BR[0], 155, BR[1] + 20], [855, 155, 390], [70, 60], "base", r=8)
d.box("arm-l-end", [10, 125, 295, 80, 185, 365], "base", r=8)
d.box("arm-r-end", [820, 125, 355, 890, 185, 425], "base", r=8)
for nm, (x, z) in (("fl", FL), ("br", BR), ("l", (45, 330)), ("r", (855, 390))):
    d.caster(f"castor-{nm}", [x, 0, z], 100, "rubber#8c9096")
d.save()
