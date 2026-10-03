"""XYZP-IE medium frequency trolley: white cabinet on a blue H-base; a head with the screen let into its top and the
first light-blue socket panel; an upper block with the second socket panel; a tall door with the ECG-wave line and the
logo; a blue swoosh on the left side from the head's top down to the front edge; cable comb on the left.
Review 2026-10-02: proportions from the photo (front 380 wide, door ~1.7× its width, upper block ~0.4×), so H 1160;
sockets staggered with the lower row to the LEFT; light screen; swoosh only on the side; comb/holder/hook raised."""
from p3lib import *

d = D("xyzp-ie", [620, 560, 1160], {
    "shell": "gloss#f6f7f9", "blue": "gloss#2a6fc2", "seam": "plastic#a7adb4", "frame": "gloss#8fc0ec", "inner": "plastic#4f86cc",
    "sock": "plastic#b0b5ba", "sock-c": "plastic#7d838a", "sframe": "plastic#8d939a", "ui": "gloss#e3e7ec", "ui-ink": "plastic#a9b0b8",
    "wave": "gloss#2a6fc2", "wave2": "plastic#c9cdd2", "comb": "gloss#eef0f2", "hook": "plastic#8d939a", "wheel": "rubber#9aa0a7",
    "dark": "plastic#3a3f46"})
X0, X1, Z0, Z1 = 120, 500, 40, 500
YD, YU, YH, YT = 857, 1005, 1114, 1160          # door top, upper block top, head front top, head back top
# ---- blue H-base and castors
d.box("base-front", [0, 112, 470, 620, 162, 540], "blue", r=22)
d.box("base-rear", [20, 112, 20, 600, 162, 82], "blue", r=22)
d.box("plinth", [X0 + 10, 112, Z0, X1 - 10, 204, Z1 - 10], "blue", r=36)
d.add("castor", "caster", "wheel", at=[40, 0, 520], d=90, copies=[[540, 0, 0]])
d.add("castor-r", "caster", "wheel", at=[60, 0, 66], d=90, copies=[[500, 0, 0]])
# ---- cabinet: door section, upper block, head, dark seams between them
d.box("body", [X0, 200, Z0, X1, YD, Z1], "shell", r=18)
d.box("seam1", [X0 + 4, YD - 2, Z0 + 4, X1 - 4, YD + 6, Z1 - 4], "dark", r=6)
d.box("upper", [X0, YD + 4, Z0, X1, YU, Z1 + 4], "shell", r=16)
d.box("seam2", [X0 + 4, YU - 2, Z0 + 4, X1 - 4, YU + 6, Z1 - 2], "dark", r=6)
d.slab("head", "side", rpoly([(Z0 - 4, YU + 4), (Z1 + 6, YU + 4), (Z1 + 6, YH), (Z0 - 4, YT)], [8, 8, 26, 26]), [X0 - 6, X1 + 6], "shell", r=22)
ang = math.degrees(math.atan2(YT - YH, Z1 + 6 - Z0 + 4))
t = Tilt(YH, Z1 + 6, ang)
# screen (switched on, light UI) in a grey frame let into the top
t.box(d, "screen-frame", X0 + 26, 34, X1 - 26, 430, -2, 1, "sframe", r=12)
t.box(d, "screen", X0 + 40, 48, X1 - 40, 414, 0.5, 1.4, "ui", r=4)
t.box(d, "ui-bar", X0 + 60, 360, X1 - 120, 372, 1.2, 1.8, "ui-ink", soft=True)
t.box(d, "ui-bar2", X0 + 60, 330, X1 - 180, 338, 1.2, 1.8, "ui-ink", soft=True)
# ---- two light-blue socket panels: 4 sockets on top, 4 below shifted left (photo)
PAN = [(1020, 1098, Z1 + 6, X0 + 128, X0 + 348, [171, 214, 259, 305], [150, 195, 239, 284]),
       (916, 991, Z1 + 4, X0 + 134, X0 + 332, [177, 219, 262, 305], [152, 196, 239, 281])]
for i, (y0, y1, zf, xa, xb, top, bot) in enumerate(PAN):
    d.box(f"panel{i}", [xa, y0, zf - 4, xb, y1, zf + 2], "frame", r=12)
    d.box(f"panel{i}-in", [xa + 7, y0 + 7, zf - 2, xb - 7, y1 - 7, zf + 3], "inner", r=8)
    for row, xs in enumerate((top, bot)):
        yy = y0 + (y1 - y0) * (0.68 if row == 0 else 0.32)
        for k, x in enumerate(xs):
            d.cyl(f"sock{i}{row}{k}", [X0 + x, yy, zf + 2], [X0 + x, yy, zf + 10], 24, "sock-c")
            d.cyl(f"sockc{i}{row}{k}", [X0 + x, yy, zf + 8], [X0 + x, yy, zf + 13], 20, "sock")
# ---- door: seam outline, ECG wave line near its top, logo near the bottom
d.box("door-seam", [X0 + 12, 214, Z1 - 1, X1 - 12, YD - 8, Z1 + 0.6], "seam", r=10, soft=True)
d.box("door", [X0 + 14, 216, Z1 - 0.5, X1 - 14, YD - 10, Z1 + 1.2], "shell", r=9)
WY = 782
d.tube("wave-dash", [[X0 + 70, WY, Z1 + 2], [X0 + 100, WY, Z1 + 2]], 3, "wave2", soft=True)
d.tube("wave", [[X0 + 100, WY, Z1 + 2], [X0 + 118, WY, Z1 + 2], [X0 + 130, WY + 34, Z1 + 2], [X0 + 142, WY - 30, Z1 + 2],
                [X0 + 154, WY + 26, Z1 + 2], [X0 + 166, WY, Z1 + 2], [X1 - 16, WY + 6, Z1 + 2]], 4, "wave", soft=True)
d.tube("wave2", [[X0 + 166, WY - 7, Z1 + 2], [X1 - 16, WY - 1, Z1 + 2]], 3, "wave2", soft=True)
d.cyl("logo", [X0 + 200, 285, Z1 + 1], [X0 + 200, 285, Z1 + 2.5], 26, "blue", soft=True)
d.box("logo-t", [X0 + 219, 279, Z1 + 1, X0 + 290, 293, Z1 + 2.2], "blue", soft=True)
# ---- blue swoosh on the left side: from the head's top at the back, sweeping forward and down to the front edge
sw = ("M 500 204 L 476 204 L 474 720 Q 470 905 420 995 Q 340 1105 170 1146 L 250 1140 Q 400 1110 470 1015 "
      "Q 500 925 500 720 Z")
d.slab("swoosh", "side", sw, [X0 - 7, X0 + 2], "blue", r=1)
# ---- left side: box holder above a cable comb of 4 inverted-U loops; right side: small grey hook
d.box("comb-plate", [X0 - 10, 878, 350, X0, 902, 492], "comb", r=5)
for k in range(4):
    z = 368 + 36 * k
    d.tube(f"finger{k}", [[X0 - 6, 890, z], [X0 - 46, 890, z], [X0 - 46, 945, z], [X0 - 92, 945, z], [X0 - 92, 896, z]], 9, "comb", bend=14)
d.box("box-holder", [X0 - 76, 952, 370, X0, 996, 486], "comb", r=8)
d.box("box-holder-in", [X0 - 68, 992, 380, X0 - 8, 997, 476], "seam", soft=True)
d.box("hook", [X1, 905, 470, X1 + 14, 955, 486], "hook", r=4)
d.box("hook-tip", [X1 + 6, 943, 470, X1 + 14, 965, 486], "hook", r=3)
d.save()
