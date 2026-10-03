from lib import *
from p2util import *
# laser magnetic cart: dark splayed base, white rounded cabinet, chin ledge + knob, tilted 12" screen, coil paddle on a pole (left), C handle (right)
W = 750; cx = W / 2
d = D("xy-jgc-iii", [W, 650, 1610], {"shell": "plastic#f1f2f4", "dark": "plastic#3a3f46", "grey": "plastic#c9cdd2",
      "chrome": "chrome", "black": "gloss#15171a", "red": "gloss#d4202a", "purple": "gloss#9a3d8c", "white": "plastic#fafafa"})
X0, X1, Z0, Z1 = cx - 210, cx + 210, 45, 605
# base
d.box("skirt", [X0 - 4, 95, Z0 + 5, X1 + 4, 185, Z1 - 5], "dark", r=24)
for i, (sx, z0, z1) in enumerate(((-1, 120, 40), (1, 120, 40), (-1, 530, 610), (1, 530, 610))):
    d.add(f"leg{i}", "bar", "dark", **{"from": [cx + sx * 150, 125, z0], "to": [cx + sx * 300, 112, z1]}, section=[90, 42], r=16)
d.cyl("castor-cap", [cx - 300, 98, 40], [cx - 300, 132, 40], 66, "dark", copies=[[600, 0, 0], [0, 0, 570], [600, 0, 570]])
d.add("castor", "caster", "rubber#34373c", at=[cx - 300, 0, 50], d=100, copies=[[600, 0, 0], [0, 0, 570], [600, 0, 570]])
# cabinet, chin ledge, rear upper body
d.box("cabinet", [X0, 180, Z0, X1, 935, Z1], "shell", r=38)
d.box("seam", [X0 + 2, 718, Z1 - 1, X1 - 2, 721, Z1 + 1], "plastic#d2d5d9", soft=True)
d.add("chin", "slab", "shell", plane="top", outline=f"M {X0} {Z1 - 120} L {X1} {Z1 - 120} L {X1} {Z1 - 20} Q {X1} {Z1 + 50} {cx + 120} {Z1 + 50} L {cx - 120} {Z1 + 50} Q {X0} {Z1 + 50} {X0} {Z1 - 20} Z",
      w=[870, 935], r=24)
d.add("knob", "lathe", "metal#c9ccd0", at=[cx, 932, Z1 - 15], profile=[[0, 0], [36, 0], [36, 18], [32, 24], [0, 25]])
d.add("upper", "slab", "shell", plane="side", outline=f"M {Z0} 900 L 440 900 L 430 980 L 368 1240 Q 355 1278 315 1270 L 110 1150 Q {Z0} 1110 {Z0} 1060 Z", w=[X0, X1], r=40)
t = rot("x", -12, [cx, 930, 470])
d.box("screen-back", [X0 + 3, 925, 420, X1 - 3, 1285, 462], "shell", r=26, rot=t)
d.add("screen", "screen", "black", box=[X0 + 8, 935, 455, X1 - 8, 1278, 468], r=20, face="front", bezel=36,
      print="med_xy-jgc-iii_screen", rot=t)
d.box("screen-logo", [cx - 45, 1252, 468, cx + 45, 1262, 469.5], "plastic#c9cdd2", soft=True, rot=t)
# front details
d.box("stop-recess", [X0 + 30, 742, Z1 - 3, cx - 10, 802, Z1 + 1], "plastic#e2e4e7", r=12)
d.cyl("stop-base", [X0 + 70, 772, Z1], [X0 + 70, 772, Z1 + 8], 46, "plastic#b9bec5")
d.add("stop", "lathe", "red", at=[X0 + 70, 772, Z1 + 8], axis="z", profile=[[0, 0], [14, 0], [14, 6], [21, 8], [22, 16], [18, 20], [0, 21]])
d.cyl("key", [X0 + 135, 772, Z1], [X0 + 135, 772, Z1 + 8], 30, "chrome")
d.box("key-slot", [X0 + 133, 764, Z1 + 8, X0 + 137, 780, Z1 + 9], "black", soft=True)
d.box("brand", [X0 + 30, 662, Z1, X0 + 120, 676, Z1 + 1.5], "plastic#4d5259", soft=True)
d.box("brand-cn", [X0 + 126, 662, Z1, X0 + 156, 676, Z1 + 1.5], "plastic#4d5259", soft=True)
d.box("brand-sub", [X0 + 30, 648, Z1, X0 + 110, 651, Z1 + 1.5], "plastic#a6abb1", soft=True)
d.box("tile", [X0 + 70, 310, Z1 - 2, X0 + 160, 400, Z1 + 3], "purple", r=16)
d.add("icon", "tube", "white", path=[[X0 + 100, 380, Z1 + 3.5], [X0 + 92, 355, Z1 + 3.5], [X0 + 108, 330, Z1 + 3.5]], d=4, bend=20, soft=True,
      copies=[[30, 0, 0]])
d.box("icon-t", [X0 + 95, 318, Z1 + 3, X0 + 135, 322, Z1 + 4], "white", soft=True)
# side holders with chrome knobs (both sides)
d.box("holder", [X1 - 4, 615, 470, X1 + 48, 725, 598], "grey", r=18, mirror="x")
d.cyl("holder-knob", [X1 + 20, 672, 598], [X1 + 20, 672, 622], 46, "chrome", mirror="x")
d.cyl("holder-knob-f", [X1 + 20, 672, 622], [X1 + 20, 672, 626], 38, "plastic#d8dbe0", mirror="x")
# right side: C grab handle, door seam, speaker grille, vent panel
d.tube("handle", [[X1 - 5, 1005, 455], [X1 + 110, 1005, 455], [X1 + 110, 690, 455], [X1 + 40, 680, 455]], 34, "metal#c9ccd0", bend=70)
d.box("handle-foot", [X1 - 2, 980, 430, X1 + 16, 1030, 480], "grey", r=8)
d.box("door", [X1, 808, 300, X1 + 1, 812, 410], "plastic#c3c7cc", soft=True, copies=[[0, 150, 0]])
d.box("door-v", [X1, 808, 300, X1 + 1, 962, 304], "plastic#c3c7cc", soft=True, copies=[[0, 0, 106]])
d.cyl("speaker", [X1 - 1, 1090, 250], [X1 + 1.5, 1090, 250], 92, "plastic#b9bec5", soft=True)
d.cyl("speaker-in", [X1 + 1.5, 1090, 250], [X1 + 2, 1090, 250], 70, "plastic#9aa0a8", soft=True)
d.box("vent", [X1 - 1, 220, 80, X1 + 1.5, 560, 330], "plastic#8f959c", r=6, soft=True)
d.box("vent-line", [X1 + 1.5, 230, 90, X1 + 2, 232, 320], "plastic#6c7279", soft=True, repeat={"n": 34, "step": [0, 10, 0]})
# left: chrome pole, grey applicator handle tube with U-bend, clamp with black star knob, ferrule, paddle head
PX, HX, PZ = X0 - 40, X0 - 85, 470
d.cyl("pole", [PX, 690, PZ], [PX, 1330, PZ], 22, "chrome")
d.cyl("pole-cap", [PX, 1330, PZ], [PX, 1345, PZ], 28, "chrome")
d.tube("appl-tube", [[X0 - 10, 640, PZ + 20], [HX + 10, 585, PZ + 20], [HX, 700, PZ + 20], [HX, 1320, PZ + 20]], 40, "grey", bend=60)
d.box("clamp", [HX - 25, 975, PZ - 25, PX + 18, 1030, PZ + 45], "chrome", r=10)
d.cyl("star-shaft", [HX - 25, 1002, PZ + 10], [HX - 60, 1002, PZ + 10], 14, "chrome")
d.add("star", "lathe", "black", at=[HX - 60, 1002, PZ + 10], axis="x", sides=10,
      profile=[[0, 0], [34, 0], [34, 14], [12, 22], [0, 22]], rot=rot("z", 180, [HX - 60, 1002, PZ + 10]))
d.cyl("ferrule", [HX, 1300, PZ + 20], [HX, 1355, PZ + 20], 50, "chrome")
d.add("paddle-neck", "loft", "white", sections=[{"at": 1350, "w": 46, "d": 40, "r": 20, "cx": HX, "cz": PZ + 20}, {"at": 1405, "w": 80, "d": 42, "r": 20, "cx": HX, "cz": PZ + 20}])
d.add("paddle", "slab", "white", plane="front", outline=f"M {HX} 1385 A 72 108 0 0 1 {HX} 1601 A 72 108 0 0 1 {HX} 1385 Z", w=[PZ - 2, PZ + 42], r=16)
d.add("paddle-ring", "lathe", "grey", at=[HX, 1500, PZ + 42], axis="z", profile=[[50, 0], [55, 0], [55, 4], [50, 4]], caps=False)
d.add("paddle-dot", "sphere", "grey", at=[HX, 1500, PZ + 43], d=10)
d.save()
