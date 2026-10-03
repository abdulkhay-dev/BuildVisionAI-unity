# XYRT-19 children safety chair: white tube frame (inverted U sides, front legs slanting forward) on 4 castors,
# grey seat, wrap-around backrest and headrest, push handles with black grips, wooden tray with a body cut-out,
# grey pommel block with a red strap under the tray, wooden footplate at the front
from pd2_lib import *

W, D, H = 530, 860, 1050
C = W / 2
d = Design("xyrt-19", [W, D, H], {"tube": "plastic#f2f2f0", "pad": "leather#8e8a86", "wood": "wood#dcb98a",
                                    "foam": "rubber#232426", "red": "fabric#c8324a", "knob": "plastic#1c1d1f",
                                    "wheel": "rubber#6e7c8c"})
XL, XR = 48, W - 48
ZFL, ZRL = 700, 235          # front / rear leg feet
YA = 655                     # arm height
for nm, x in (("l", XL), ("r", XR)):
    d.tube(f"side-{nm}", [[x, 78, ZFL], [x, YA, 615], [x, YA, ZRL], [x, 78, ZRL]], 26, "tube", bend=90)
    for y in (300, 400):
        zf = ZFL + (615 - ZFL) * (y - 78) / (YA - 78)
        d.cyl(f"rail-{nm}{y}", [x, y, zf], [x, y, ZRL], 22, "tube")
    d.add(f"castor-f{nm}", "caster", "wheel", at=[x, 0, ZFL + 8], d=80)
    d.add(f"castor-r{nm}", "caster", "wheel", at=[x, 0, ZRL - 8], d=80)
    # push handle post: white tube rising from the rear leg, leaning back
    d.tube(f"push-{nm}", [[x, 380, ZRL], [x, 905, 125]], 24, "tube")
# push bar across the back (a U over the two posts), black foam grip on the top, red clip at the headrest
d.tube("push-bar", [[XL, 900, 126], [XL, 950, 116], [XR, 950, 116], [XR, 900, 126]], 24, "tube", bend=45)
d.cyl("push-grip", [XL + 30, 950, 116], [XR - 30, 950, 116], 42, "foam")
d.box("push-clip", [C + 118, 930, 108, C + 140, 970, 128], "red", r=4)
for y in (300, 400):
    d.cyl(f"cross-b{y}", [XL, y, ZRL], [XR, y, ZRL], 22, "tube")
d.cyl("cross-f400", [XL, 400, 650], [XR, 400, 650], 22, "tube")
# seat cushion, wrap-around backrest, headrest
d.box("seat", [72, 405, 255, W - 72, 470, 640], "pad", r=22, puff=6)
back = (f"M 80 225 L {W - 80} 225 L {W - 80} 380 Q {W - 80} 395 {W - 100} 392 L {W - 118} 300 L 118 300 L 100 392 "
        f"Q 80 395 80 380 Z")
d.slab("back", "top", back, [440, 895], "pad", r=18)
d.box("head-post", [C - 18, 880, 228, C + 18, 925, 250], "tube", r=4)
d.box("headrest", [C - 115, 900, 225, C + 115, 1050, 292], "pad", r=26, puff=5)
# tray on the arms: body cut-out at the back, side flaps outside the arms
tray = (f"M 0 335 L {C - 95} 335 L {C - 95} 400 A 95 95 0 0 0 {C + 95} 400 L {C + 95} 335 L {W} 335 L {W} 800 "
        f"L 0 800 Z")
d.slab("tray", "top", tray, [YA + 13, YA + 33], "wood", r=4)
for nm, x0 in (("l", 14), ("r", W - 30)):
    d.box(f"tray-flap-{nm}", [x0, YA - 60, 420, x0 + 16, YA + 14, 640], "wood", r=3)
# pommel block under the tray front with a red strap, black knob below
d.box("pommel", [C - 42, 430, 650, C + 42, YA + 12, 725], "pad", r=16, puff=3)
d.box("pommel-strap", [C - 12, 440, 724, C + 12, YA, 728], "red", r=2, soft=True)
d.lathe("pommel-knob", [C, 395, 690], [[0, 0], [8, 0], [8, 12], [20, 14], [20, 30], [0, 34]], "knob",
        rot=rot("x", 180, [C, 412, 690]))
# footplate at the front on a tube bracket
d.tube("foot-bracket", [[XL, 300, 676], [XL, 175, 700], [XR, 175, 700], [XR, 300, 676]], 22, "tube", bend=40)
d.box("footplate", [40, 162, 640, W - 40, 182, 860], "wood", r=8)
d.lathe("foot-knob", [XR + 12, 200, 700], [[0, 0], [6, 0], [6, 10], [15, 12], [15, 26], [0, 28]], "knob", axis="x")
d.save()
