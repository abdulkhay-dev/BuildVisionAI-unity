from lib import *
from p2util import *
# white cabinet on a dark tube frame, drawer, side vent + hose port, dark deck with a big tilted tablet screen
d = D("xy-lrf-i", [480, 520, 1310], {"shell": "gloss#f5f6f7", "dark": "plastic#3a3f46", "black": "gloss#141517",
      "line": "plastic#2a2d31", "logo": "gloss#2f7fc8", "chrome": "chrome"})
X0, X1, Z0, Z1, YB, YT = 30, 450, 20, 500, 140, 1040
# base frame + castors
d.box("bar-x", [22, 114, 12, 458, 142, 50], "dark", r=6, copies=[[0, 0, 458]])
d.box("bar-z", [22, 114, 12, 60, 142, 508], "dark", r=6, copies=[[398, 0, 0]])
d.box("housing", [8, 112, 0, 62, 146, 54], "dark", r=10, copies=[[410, 0, 0], [0, 0, 466], [410, 0, 466]])
d.add("castor", "caster", "rubber#3d4147", at=[35, 0, 30], d=90, copies=[[410, 0, 0], [0, 0, 466], [410, 0, 466]])
# cabinet
d.box("cabinet", [X0, YB, Z0, X1, YT, Z1], "shell", r=16)
d.box("gap", [X1 - 1, YB + 6, Z1 - 9, X1 + 0.8, YT - 6, Z1 - 6], "plastic#8a9099", soft=True)
d.box("gap-top", [X0 + 4, YT - 1, Z1 - 9, X1 - 4, YT + 0.5, Z1 - 6], "plastic#8a9099", soft=True)
# front: logo and drawer
d.cyl("logo", [100, 650, Z1], [100, 650, Z1 + 1.5], 56, "logo", soft=True)
d.box("logo-x", [97, 628, Z1 + 1.5, 103, 672, Z1 + 2], "shell", soft=True)
d.box("logo-cn", [138, 648, Z1, 268, 676, Z1 + 1.5], "logo", soft=True)
d.box("logo-en", [138, 628, Z1, 268, 638, Z1 + 1.5], "logo", soft=True)
d.box("drawer-line", [52, 158, Z1, 402, 352, Z1 + 1], "line", r=10)
d.box("drawer", [56, 162, Z1, 398, 348, Z1 + 3], "shell", r=8)
d.box("notch", [190, 312, Z1 + 1, 262, 349, Z1 + 3.5], "line", r=6)
d.box("drawer-dot", [100, 175, Z1 + 3, 104, 179, Z1 + 3.5], "plastic#9aa0a8", soft=True, copies=[[250, 0, 0]])
# right side: hose port and slit vent
d.box("port", [X1 - 3, 845, 160, X1 + 5, 925, 355], "dark", r=34)
d.cyl("port-hole", [X1 + 5, 885, 190], [X1 + 6, 885, 190], 40, "plastic#22252a", soft=True)
d.cyl("coupling", [X1 + 18, 885, 225], [X1 + 18, 885, 310], 24, "chrome")
d.cyl("coupling-ring", [X1 + 18, 885, 250], [X1 + 18, 885, 262], 36, "chrome", copies=[[0, 0, 32]])
d.box("coupling-base", [X1 + 4, 872, 240, X1 + 14, 898, 300], "chrome", r=4)
d.box("vent-slit", [X1, 460, 118, X1 + 1.5, 494, 122], "plastic#5d636b", soft=True,
      repeat={"n": 34, "step": [0, 0, 8]}, copies=[[0, 44 * k, 0] for k in range(1, 7)])
# deck + tablet screen
d.box("deck", [X0 - 4, YT, Z0 - 4, X1 + 4, YT + 26, Z1 + 4], "dark", r=6)
d.box("deck-top", [X0 + 4, YT + 25, Z0 + 4, X1 - 4, YT + 27, Z1 - 4], "metal#8e9399", r=3)
d.box("side-switch", [X1 - 2, 920, Z0 + 4, X1 + 8, 975, Z0 + 18], "dark", r=3)
t = rot("x", -28, [240, YT + 22, Z1 - 20])
d.box("hinge", [170, YT + 18, Z1 - 120, 310, YT + 70, Z1 - 40], "dark", r=10)
d.add("screen", "screen", "black", box=[40, YT + 22, Z1 - 46, 440, YT + 302, Z1 - 20], r=22, face="front", bezel=3,
      print="med_xy-lrf-i_screen", rot=t)
d.box("screen-rim", [38, YT + 20, Z1 - 49, 442, YT + 304, Z1 - 30], "plastic#b9bec5", r=24, rot=t)
d.save()
