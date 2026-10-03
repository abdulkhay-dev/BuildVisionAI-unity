# XY-79 folding commode: aluminium frame with telescopic legs, grey armrests, U backrest with foam grip,
# white toilet seat with lid and bucket — other-1
from o_lib import *
W, DP, H = 560, 630, 800
d = D("xy-79", [W, DP, H], {
    "alu": "metal#c8ccd2", "inner": "metal#d8dbe0", "grey": "plastic#9a9fa6", "tip": "rubber#8d9298",
    "foam": "rubber#8a8f96", "white": "plastic#f3f3f0", "dot": "plastic#5c6168"})
AY = 690                       # armrest tube height
legs = [(24, 596), (W - 24, 596), (40, 40), (W - 40, 40)]
for i, (x, z) in enumerate(legs):
    d.cyl(f"leg-up{i}", [x, 250, z], [x, AY, z], 25, "alu")
    d.cyl(f"leg-in{i}", [x, 40, z], [x, 255, z], 20, "inner")
    d.cyl(f"clip{i}", [x, 245, z], [x, 265, z], 29, "grey")
    d.cyl(f"tip{i}", [x, 0, z], [x, 45, z], 30, "tip")
    d.cyl(f"hole{i}", [x, 80, z + (11 if z > 300 else -11)], [x, 80, z + (12 if z > 300 else -12)], 5, "dot",
          soft=True, repeat=rep(5, [0, 30, 0]))
# side frames: armrest tube rounding down into the front leg, grey pad with a curled front end
for i, x in enumerate((24, W - 24)):
    xr = 40 if i == 0 else W - 40
    d.tube(f"arm-tube{i}", [[xr, AY - 20, 40], [x, AY, 60], [x, AY, 560], [x, AY - 60, 596]], 25, "alu", bend=40)
    d.box(f"pad{i}", [x - 22, AY + 10, 150, x + 22, AY + 38, 560], "grey", r=12, puff=2)
    d.tube(f"pad-curl{i}", [[x, AY + 24, 550], [x, AY + 18, 600], [x, AY - 40, 612]], 40, "grey", bend=30)
    d.cyl(f"rail{i}", [x, 430, 40], [x, 430, 596], 22, "alu")
# no front bar: the photo shows the front open under the seat (the user sits there)
# rear crossbar and the U backrest with a grey foam grip
d.tube("rear-bar", [[40, 560, 40], [140, 575, 30], [W - 140, 575, 30], [W - 40, 560, 40]], 22, "alu", bend=40)
d.tube("back-u", [[140, 560, 30], [140, H - 18, 20], [W - 140, H - 18, 20], [W - 140, 560, 30]], 22, "alu", bend=45)
d.cyl("grip", [175, H - 18, 20], [W - 175, H - 18, 20], 38, "foam")
d.cyl("u-clip", [140, 700, 26], [140, 720, 26], 28, "grey", copies=[[W - 280, 0, 0]])
# white toilet seat with the closed lid, white bucket under it
SZ = 330
d.lathe("bucket", [W / 2, 230, SZ], [[0, 0], [125, 0], [150, 200], [154, 205], [0, 205]], "white")
d.loft("seat", [sec(440, 400, 440, 190, W / 2, SZ), sec(462, 400, 440, 190, W / 2, SZ)], "white")
d.loft("lid", [sec(462, 380, 420, 180, W / 2, SZ - 4), sec(478, 370, 410, 175, W / 2, SZ - 4)], "white")
d.box("hinge", [W / 2 - 110, 455, 90, W / 2 + 110, 478, 120], "white", r=8)
d.save()
