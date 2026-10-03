"""xyrt-27 — two-castor walker for children, front-open. Frame: open grip end at the front (z=D, the side the
photo looks at), castors and cross bars at the back. H 520 instead of the printed 430 (photo: taller than wide)."""
from pd3_lib import *

W, Dp, H = 470, 430, 520
G = "plastic#16a394"
d = D("xyrt-27", [W, Dp, H], {"tube": G, "grip": "rubber#1c1d1f", "tip": "rubber#2a2b2d"})
T = 25
yT, yB = H - 21, 165
zc = 45                      # castor axis
zp = Dp - 150                # post just behind the grip
def zleg(y): return zc + (y - 125) / (yT - 125) * 78
for nm, x in (("l", 20), ("r", W - 20)):
    d.tube(f"top-{nm}", [[x, yT, Dp - 12], [x, yT, 125], [x, 112, zc]], T, "tube", bend=85)
    d.cyl(f"grip-{nm}", [x, yT, Dp - 140], [x, yT, Dp - 4], 42, "grip")
    d.sphere(f"gripend-{nm}", [x, yT, Dp - 4], 42, "grip", radii=[21, 21, 6])
    d.cyl(f"post-{nm}", [x, yB, zp], [x, yT, zp], T, "tube")
    d.tube(f"bot-{nm}", [[x, yB, zleg(yB)], [x, yB, Dp - 70], [x, 30, Dp - 26]], T, "tube", bend=110)
    d.cyl(f"tip-{nm}", [x, 0, Dp - 26], [x, 38, Dp - 26], 32, "tip")
    rigid_caster(d, f"c-{nm}", x, zc, 75, "plastic#f06a20", G, hub="rubber#1e1f22", hub_k=0.64)
    s = -1 if nm == "l" else 1
    d.sphere(f"bolt-{nm}", [x + s * 13, 370, zleg(370)], 9, "chrome", soft=True,
             copies=[[0, -155, zleg(215) - zleg(370)], [0, yB - 370, zp - zleg(370)]])
d.cyl("x-up", [20, 370, zleg(370)], [W - 20, 370, zleg(370)], T, "tube")
d.cyl("x-lo", [20, 215, zleg(215)], [W - 20, 215, zleg(215)], T, "tube")
d.box("label", [95, 362, zleg(370) + 11.5, 150, 378, zleg(370) + 13.5], "plastic#c9cdd2", r=1, soft=True)
d.save()
