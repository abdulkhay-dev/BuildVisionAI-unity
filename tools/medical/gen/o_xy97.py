# XY-97 lifting wash basin: white ceramic vanity basin with a chrome mixer on a cream lifting carriage, cream back
# panel to the floor and a cream floor plate; drawn in the photo's (lowest) position — other-2
from o_lib import *
W, DP, H = 650, 560, 860
d = D("xy-97", [W, DP, H], {
    "cer": "gloss#f6f6f4", "cream": "plastic#efe8d6", "chrome": "chrome", "blk": "plastic#17181a", "dark": "plastic#6b6e72"})
TY = 650                     # basin deck top (lowest position)
CX, CZ = W / 2, 330          # bowl centre
RX, RZ = 225, 160
def ell(s, ccw=False):
    sw = 0 if ccw else 1
    rx, rz = RX * s, RZ * s
    return f"M {CX - rx} {CZ} A {rx} {rz} 0 1 {sw} {CX + rx} {CZ} A {rx} {rz} 0 1 {sw} {CX - rx} {CZ} Z"
# floor plate, fixed back panel, lifting carriage
d.box("plate", [70, 0, 0, 580, 12, 470], "cream", r=4)
d.box("back", [125, 12, 0, 545, 330, 26], "cream", r=3)
d.box("carriage", [95, 300, 0, 555, TY - 30, 190], "cream", r=6)
d.box("seam", [97, 330, 189, 553, 333, 191], "plastic#cfc6b0", soft=True)
d.box("screw", [110, 470, 189.5, 116, 476, 191.5], "dark", soft=True, copies=[[428, 0, 0], [0, -120, 0], [428, -120, 0]])
d.box("switch", [91, 575, 140, 96, 595, 168], "blk", soft=True)
# white ceramic basin: deck with ears and a bulging front, stepped oval bowl, drain bump under it
deck = ("M 0 0 L 650 0 L 650 330 Q 650 390 595 390 Q 560 390 545 420 C 500 540 400 560 325 560 "
        "C 250 560 150 540 105 420 Q 90 390 55 390 Q 0 390 0 330 Z")
d.slab("deck", "top", deck + " " + ell(1.0), [TY - 30, TY], "cer", r=10)
for i, (y0, y1, hole, outer) in enumerate(((595, 621, 0.92, 1.06), (565, 596, 0.8, 1.0), (538, 566, 0.62, 0.9))):
    d.slab(f"bowl{i}", "top", ell(outer) + " " + ell(hole), [y0, y1], "cer", r=8)
d.slab("bowl-floor", "top", ell(0.74), [518, 540], "cer", r=8)
# smooth outer skin of the bowl (open loft around the stepped inside)
d.loft("bowl-skin", [sec(519, 336, 240, 120, CX, CZ), sec(545, 405, 292, 146, CX, CZ), sec(575, 450, 324, 162, CX, CZ),
                     sec(605, 476, 342, 171, CX, CZ), sec(TY - 26, 482, 346, 173, CX, CZ)], "cer", caps=False)
d.cyl("drain", [CX, 540, CZ], [CX, 541.5, CZ], 40, "chrome", soft=True)
d.lathe("drain-bump", [CX, 488, CZ], [[0, 0], [16, 1], [28, 8], [36, 22], [38, 32], [0, 32]], "cer")
d.box("overflow", [CX - 8, 600, CZ - RZ * 0.93 - 1, CX + 8, 610, CZ - RZ * 0.93 + 1], "dark", soft=True)
# chrome 2-handle gooseneck mixer at the back
d.box("tap-plate", [CX - 75, TY, 45, CX + 75, TY + 14, 95], "chrome", r=6)
d.cyl("tap-body", [CX, TY + 10, 70], [CX, TY + 60, 70], 34, "chrome")
d.tube("spout", [[CX, TY + 55, 70], [CX, TY + 190, 85], [CX, TY + 200, 150], [CX, TY + 150, 175]], 22, "chrome", bend=55)
for i, x in enumerate((CX - 58, CX + 58)):
    d.cyl(f"valve{i}", [x, TY + 12, 70], [x, TY + 40, 70], 26, "chrome")
    d.box(f"lever{i}", [x - 10 + (-30 if i == 0 else 0), TY + 38, 62, x + 10 + (30 if i == 1 else 0), TY + 50, 78], "chrome", r=5)
# chrome angle valve low on the left
d.cyl("valve-pipe", [125, 40, 30], [125, 110, 30], 18, "chrome")
d.cyl("valve-out", [125, 60, 30], [80, 60, 60], 16, "chrome")
d.box("valve-lever", [70, 52, 55, 90, 68, 90], "chrome", r=4)
d.save()
