"""XYGS-1 quadriceps board: a long base board, a blue padded inverted-V tent hinged at the back end, its long front
panel resting against a wooden heel stop; 4 blue pegs in the cream front section."""
import math
from k6lib import *

W, DEP, H = 200, 800, 310
d = D("xygs-1", [W, DEP, H], {"wood": "wood#e6b46a", "cream": "plastic#f2ede0", "pad": "leather#3762b2",
                              "under": "leather#33558f", "peg": "gloss#2b3f9c"})
T = 20
d.box("base", [0, 0, 0, W, T, DEP], "wood", r=3)
d.box("top-cream", [2, T, 470, W - 2, T + 1.2, DEP - 2], "cream", r=0.5)
# hinge (chrome piano hinge at the back end)
d.cyl("hinge", [8, T + 8, 28], [W - 8, T + 8, 28], 14, "chrome")
# back panel: from the hinge steeply up to the apex
APZ, APY = 110, H
L1 = math.hypot(APZ - 28, APY - T - 8)
a1 = math.degrees(math.atan2(APY - T - 8, APZ - 28))
d.box("panel-back", [0, T + 8, 28, W, T + 62, 28 + L1], "pad", r=14, puff=3, rot=rot("x", -a1, [W / 2, T + 8, 28]))
# front panel: from the heel stop up to the apex (top surface line)
FZ, FY = 470, T + 44
L2 = math.hypot(FZ - APZ, APY - FY) + 20
a2 = math.degrees(math.atan2(APY - FY, FZ - APZ))
d.box("panel-front", [0, FY - 58, FZ - L2, W, FY, FZ], "pad", r=14, puff=3, rot=rot("x", a2, [W / 2, FY, FZ]))
# heel stop block (wood, white top), blue pegs, a clear round level at the front corner
d.box("stop", [0, T, 472, W, T + 32, 530], "wood", r=3)
d.box("stop-top", [2, T + 32, 474, W - 2, T + 33.5, 528], "plastic#f6f6f2", r=1)
for z in (575, 630):
    d.cyl(f"peg-ring{z}", [55, T, z], [55, T + 1.8, z], 32, "plastic#dde3ea", copies=[[90, 0, 0]], soft=True)
    d.cyl(f"peg{z}", [55, T, z], [55, T + 3, z], 24, "peg", copies=[[90, 0, 0]])
# clear round level set into the front corner: white rim, pale glass face
d.sphere("level-rim", [160, T + 1, 765], 0, "plastic#f4f6f6", radii=[30, 3.5, 20], soft=True)
d.sphere("level", [160, T + 2, 765], 0, "acrylic#d6eef2cc", radii=[24, 3, 15], soft=True)
d.save()
