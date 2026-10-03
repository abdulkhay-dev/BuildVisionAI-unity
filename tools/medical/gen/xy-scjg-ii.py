# review 2026-10-02: 4-arm X base on the diagonals, flat wide column with a flared foot, "Sunnyou 翔宇" lettering,
# bigger drawer, taller head, tray reaching in front of the head with the grip pocket there, screen sized to the crop
from p1lib import *
d = D("xy-scjg-ii", [560, 560, 1150], {
  "shell": "plastic#f2f3f5", "grey": "plastic#b4b9c0", "lgrey": "plastic#dcdfe3", "black": "gloss#121314",
  "red": "gloss#d42020", "yellow": "gloss#f2c21a", "metal": "metal#b8bcc2", "vent": "plastic#9aa0a8"})
C = (280, 280)
# X base: four tapered flat arms on the diagonals, light-grey twin castors under the tips
pts = []
for k in range(4):
    a = math.radians(45 + 90 * k)
    ux, uz = math.cos(a), math.sin(a); vx, vz = -uz, ux
    root, tip, wr, wt = 70, 285, 62, 30
    pts += [(C[0] + ux * root - vx * wr, C[1] + uz * root - vz * wr),
            (C[0] + ux * tip - vx * wt, C[1] + uz * tip - vz * wt),
            (C[0] + ux * (tip + 26), C[1] + uz * (tip + 26)),
            (C[0] + ux * tip + vx * wt, C[1] + uz * tip + vz * wt),
            (C[0] + ux * root + vx * wr, C[1] + uz * root + vz * wr)]
d.slab("base", "top", rpoly(pts, 22), [118, 160], "shell", r=14)
for k in range(4):
    a = math.radians(45 + 90 * k)
    x, z = C[0] + 270 * math.cos(a), C[1] + 270 * math.sin(a)
    d.add(f"castor-{k}", "caster", "rubber#c9cdd2", at=[x, 0, z], d=75)
d.add("hub", "lathe", "shell", at=[C[0], 150, C[1]], profile=[[0, 0], [100, 0], [98, 12], [85, 28], [70, 40], [0, 42]])
# flat wide column with a flared foot, light groove at its front left
d.loft("column-foot", [sec(185, 225, 120, 50, 280, 228), sec(240, 196, 84, 26, 280, 228), sec(300, 190, 76, 22, 280, 228),
                       sec(905, 190, 76, 22, 280, 228)], "shell")
d.box("groove", [194, 300, 265, 199, 895, 266.6], "lgrey")
# "Sunnyou 翔宇" read downwards, tops to the right, with a row of small grey marks to its left
text(d, "logo", "Sunnyou 翔宇", [302, 588, 266], 34, "plastic#a9aeb5", along=(0, -1), stroke=5)
d.add("marks", "decal", "plastic#c4c8cd", at=[288, 548, 266], size=[7, 7], face="front", soft=True, repeat={"n": 7, "step": [0, -27, 0]})
# drawer box hung on the column: open-top grip crescent at the top front, badge
d.box("drawer", [108, 565, 170, 452, 780, 405], "shell", r=12)
d.slab("drawer-notch", "front", "M 200 781 L 360 781 Q 345 748 280 746 Q 215 748 200 781 Z", [396, 406.5], "plastic#8f959d", r=3)
d.add("badge", "decal", "grey", at=[280, 712, 405], size=[44, 9], face="front", soft=True)
d.add("badge-2", "decal", "grey", at=[280, 700, 405], size=[36, 5], face="front", soft=True)
# tray: reaches right of and in front of the head, grey grip pocket in front of the head's right half
d.box("tray", [35, 900, 95, 545, 935, 555], "shell", r=14)
d.box("pocket", [235, 933, 470, 520, 939, 532], "plastic#a3a9b1", r=26)
d.box("pocket-in", [245, 938.5, 478, 510, 939.6, 524], "plastic#c2c6cc", r=20, soft=True)
# head: white rounded box; the black glass front (screen crop sized over the front, its white rim blends)
d.box("head", [40, 935, 120, 440, 1145, 440], "shell", r=24)
d.add("panel", "screen", "shell", box=[46, 942, 438, 356, 1140, 446], r=4, face="front", bezel=0, print="med_xy-scjg-ii_screen")
# vent grille low on the left side
d.box("vent", [38, 960, 220, 41, 1000, 223], "vent", repeat={"n": 20, "step": [0, 0, 8]})
# E-stop on a yellow ring, warning triangle label, fibre port
d.add("estop-ring", "lathe", "yellow", at=[395, 1112, 440], axis="z", profile=[[0, 0], [21, 0], [21, 5], [0, 5]])
d.add("estop", "lathe", "red", at=[395, 1112, 445], axis="z", profile=[[0, 0], [10, 0], [10, 7], [17, 9], [17, 16], [11, 21], [0, 22]])
d.add("warn", "decal", "yellow", at=[398, 1068, 440], size=[22, 19], face="front", soft=True)
d.add("port", "lathe", "metal", at=[400, 1020, 440], axis="z", profile=[[0, 0], [25, 0], [25, 9], [16, 12], [0, 12]])
d.add("port-in", "lathe", "black", at=[400, 1020, 450], axis="z", profile=[[0, 0], [9, 0], [9, 10], [0, 10]])
# two black fibres looping down the right side and back up to the port; thin grey foot-switch cable on the left
d.tube("fibre", [[400, 1020, 458], [450, 1022, 488], [540, 990, 500], [556, 760, 485], [550, 420, 470], [522, 300, 458],
                 [496, 345, 450], [508, 640, 446], [520, 900, 452], [505, 1035, 462], [440, 1050, 458]], 6, "black", bend=60, soft=True)
d.tube("fibre-2", [[410, 1028, 458], [470, 1040, 480], [548, 1000, 492], [566, 760, 476], [562, 480, 466], [540, 400, 462]], 5, "black", bend=60, soft=True)
d.tube("cable", [[42, 898, 160], [30, 700, 165], [26, 200, 200], [60, 14, 300], [250, 6, 420], [300, 14, 470]], 4, "grey", bend=80, soft=True)
# foot switch on the floor in front
d.box("pedal", [292, 0, 432, 412, 32, 552], "shell", r=10)
d.box("pedal-top", [302, 30, 442, 402, 42, 540], "lgrey", r=8)
d.box("pedal-rib", [312, 41, 452, 392, 45, 458], "grey", r=2, repeat={"n": 7, "step": [0, 0, 12]})
d.save()
