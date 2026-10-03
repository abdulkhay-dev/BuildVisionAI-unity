# XYRT-14 adjustable sanding board (OT table): white square-tube frame on black feet, tilting wooden top with a green
# felt surface hinged at the front (z = depth), sanding block with two round handles, clamp plate, end stop with rollers
from pd2_lib import *

W, D, H = 820, 620, 880     # printed H 730 = top flat; drawn tilted 18 deg as in the photo
d = Design("xyrt-14", [W, D, H], {"white": "plastic#f1f1ef", "foot": "rubber#18191b", "wood": "wood#e8b462",
                                    "wood2": "wood#efc888", "felt": "fabric#1d7a4e", "copper": "metal#c48f72",
                                    "red": "gloss#c8322e", "knob": "plastic#1c1d1f"})
LT = 600                                   # leg top
XS = (75, W - 115)                         # leg x0 (40 wide)
ZS = (60, D - 100)                         # leg z0
for i, x in enumerate(XS):
    for j, z in enumerate(ZS):
        d.box(f"leg{i}{j}", [x, 48, z, x + 40, LT, z + 40], "white", r=3)
        d.box(f"foot{i}{j}", [x - 3, 0, z - 3, x + 43, 52, z + 43], "foot", r=5)
# rails on all four sides at two levels
for k, y in enumerate((270, 505)):
    for j, z in enumerate(ZS):
        d.box(f"rail-x{k}{j}", [XS[0] + 40, y, z + 8, XS[1], y + 30, z + 32], "white", r=3)
    for i, x in enumerate(XS):
        d.box(f"rail-z{k}{i}", [x + 8, y, ZS[0] + 40, x + 32, y + 30, ZS[1]], "white", r=3)
# copper hinge plates at the front leg tops, side struts from the back legs to the raised top
for i, x in enumerate(XS):
    d.box(f"hinge{i}", [x + 4, LT - 30, ZS[1] + 38, x + 36, LT + 26, ZS[1] + 44], "copper", r=3)
    d.box(f"hinge-block{i}", [x, LT, ZS[1] - 10, x + 40, LT + 22, ZS[1] + 44], "white", r=3)
    d.bar(f"strut{i}", [x + 20, LT - 20, ZS[0] + 20], [x + 20, 783, ZS[0] + 40], [26, 8], "white", r=2)
# tilting top (built flat on the hinge line, then turned up at the back)
Y0 = LT + 22
T = rot("x", 18, [W / 2, Y0, D])
rim = (f"M 0 0 L {W} 0 L {W} {D} L 0 {D} Z "
       f"M 55 55 L {W - 55} 55 L {W - 55} {D - 55} L 55 {D - 55} Z")
d.slab("rim", "top", rim, [Y0, Y0 + 60], "wood", r=6, rot=T)
d.box("board", [50, Y0 + 2, 50, W - 50, Y0 + 40, D - 50], "wood2", r=2, rot=T)
d.box("felt", [55, Y0 + 40, 55, W - 55, Y0 + 44, D - 55], "felt", r=1, rot=T)
YS = Y0 + 44
# sanding block with two vertical round handles: front left, its front edge at the rim (measured on the photo)
d.box("sander", [85, YS, 468, 325, YS + 26, 558], "wood2", r=5, rot=T)
d.cyl("sander-handle", [140, YS + 24, 513], [140, YS + 120, 513], 30, "wood2", rot=T, copies=[[130, 0, 0]])
d.lathe("sander-knob", [140, YS + 118, 513], [[0, 0], [16, 0], [16, 6], [11, 14], [0, 16]], "wood2", rot=T, copies=[[130, 0, 0]])
# clamp plate with two black knobs: right of the sander, a little behind it
d.box("clamp", [378, YS, 380, 578, YS + 22, 458], "wood2", r=5, rot=T)
for x in (425, 530):
    d.lathe(f"clamp-knob-{x}", [x, YS + 22, 419], [[0, 0], [8, 0], [8, 10], [20, 12], [20, 30], [0, 32]], "knob", rot=T)
# end stop along the right edge with roller blocks at both ends
d.box("stop", [690, YS, 110, 745, YS + 40, 545], "wood2", r=6, rot=T)
d.cyl("stop-roll", [672, YS + 32, 140], [762, YS + 32, 140], 52, "wood2", rot=T)
d.cyl("stop-roll2", [672, YS + 32, 510], [762, YS + 32, 510], 52, "wood2", rot=T)
# red tilt lever on the left side under the raised back edge
d.tube("lever", [[0, Y0 + 10, 90], [-1, Y0 - 20, 90], [-1, Y0 - 20, 170], [0, Y0 + 10, 170]], 18, "red", bend=12, rot=T)
d.box("label", [80, Y0 + 60, 18, 140, Y0 + 61, 40], "plastic#6d7f9a", r=1, rot=T, soft=True)
d.save()
