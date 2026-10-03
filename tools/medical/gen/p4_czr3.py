"""XY-K-CZR-III magnetic vibration heat tower. Writes only xy-k-czr-iii.json."""
from lib import *
from p4lib import *

d = D("xy-k-czr-iii", [560, 560, 1450], {"shell": "plastic#d3d6da", "black": "gloss#1a1b1d", "base": "plastic#232427",
                                          "light": "plastic#e4e6e9", "dark": "plastic#3a3d42"})
# black plinth, castors with white housings
d.loft("plinth", [sec(140, 480, 480, 80, 280, 280), sec(262, 520, 520, 90, 280, 280), sec(280, 506, 506, 84, 280, 280)], "base")
# round lobes bulging out at the corners over the castors
C4 = [[420, 0, 0], [0, 0, 420], [420, 0, 420]]
d.lathe("plinth-lobe", [70, 140, 70], [[0, 0], [58, 0], [70, 110], [66, 140], [0, 140]], "base", sides=32, copies=C4)
d.add("castor", "caster", "rubber#8d939a", at=[70, 0, 70], d=100, copies=C4)
d.box("castor-cap", [45, 95, 45, 95, 145, 95], "light", r=12, copies=C4)
d.box("plinth-grille", [190, 150, 520, 370, 230, 528], "plastic#121314", r=6)
# tower: deeper lower part, sloped transition, slimmer upper part
d.loft("tower", [sec(270, 400, 440, 60, 280, 280), sec(700, 400, 440, 60, 280, 280), sec(800, 380, 330, 55, 280, 235),
                 sec(1150, 370, 330, 55, 280, 235)], "shell", dome="end", domeH=12)
d.decal("brand", [330, 650, 500.5], [140, 6], "front", "plastic#5a5f66", soft=True)
d.slab("door-groove", "front", rrect(215, 335, 472, 565, 40), [496, 501], "plastic#8f959c", r=1)
d.slab("door", "front", rrect(219, 339, 468, 561, 37), [496, 503], "shell", r=3)
d.box("door-pull", [300, 465, 501, 390, 512, 505], "plastic#eceef0", r=4)
d.box("door-pull-in", [306, 471, 503, 384, 506, 506], "plastic#9aa0a6", r=3)
d.box("vent", [78, 340, 380, 82, 344, 460], "plastic#6d7379", repeat=rep(11, [0, 16, 0]))
# control strip with 4 sockets
d.box("strip", [175, 865, 396, 385, 962, 410], "black", r=12)
d.cyl("socket", [216, 925, 408], [216, 925, 413], 22, "metal#c9ccd0", copies=[[42 * k, 0, 0] for k in range(1, 4)])
d.cyl("socket-in", [216, 925, 412], [216, 925, 415], 9, "gloss#b8322c", copies=[[42 * k, 0, 0] for k in range(1, 4)])
d.decal("socket-label", [216, 893, 410.5], [26, 5], "front", "plastic#c9ccd0", soft=True, copies=[[42 * k, 0, 0] for k in range(1, 4)])
d.box("led", [272, 975, 398, 288, 985, 404], "gloss#2e9a4a", r=2)
# applicator tray with end brackets and a black U grab handle
d.box("tray", [85, 1022, 390, 495, 1036, 515], "light", r=6)
d.box("tray-lip", [85, 1022, 505, 495, 1050, 515], "light", r=4)
d.slab("bracket", "side", "M 395 1000 L 520 1000 Q 530 1000 530 1012 L 530 1080 Q 530 1092 518 1092 L 470 1092 Q 450 1060 395 1050 Z",
       [80, 100], "light", r=5, mirror="x")
d.tube("handle", [[100, 1070, 500], [100, 1070, 548], [460, 1070, 548], [460, 1070, 500]], 30, "black", bend=40)
# hose hub on the left, the black hose arcing down into a white holster
d.cyl("hub", [92, 1195, 260], [58, 1195, 260], 215, "black", sides=40)
d.cyl("hub-face", [60, 1195, 260], [54, 1195, 260], 185, "dark", sides=40)
d.decal("hub-text", [53, 1225, 260], [90, 8], "left", "plastic#c9ccd0", soft=True)
d.box("holster", [42, 740, 390, 92, 900, 475], "light", r=14)
d.box("holster-mouth", [50, 895, 400, 84, 902, 465], "dark", r=8)
d.tube("hose", [[62, 1285, 300], [26, 1268, 425], [34, 1080, 455], [66, 900, 432]], 48, "black", bend=110)
# monitor: grey rounded housing tilted back, black bezel, touch screen
t = rot("x", -15, [340, 1090, 470])
d.box("head-block", [85, 1130, 110, 330, 1300, 390], "shell", r=45)
d.box("neck", [285, 1100, 330, 400, 1200, 420], "dark", r=12)
d.box("mon", [175, 1090, 418, 505, 1440, 475], "shell", r=60, rot=t)
d.box("mon-back", [180, 1095, 398, 500, 1435, 440], "black", r=58, rot=t)
# thick black bezel in the upper part of the housing (grey chin below), the 4:3 display inside it
d.slab("bezel", "front", rrect(232, 1185, 448, 1415, 30), [471, 478.5], "black", r=2.5, rot=t)
d.add("screen", "screen", "black", box=[250, 1228, 476, 430, 1366, 480], r=3, bezel=1, print="med_xy-k-czr-iii_screen", rot=t)
d.save()
