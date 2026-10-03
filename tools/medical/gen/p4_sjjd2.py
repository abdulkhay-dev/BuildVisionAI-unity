"""XY-K-SJJD-II EMG biofeedback workstation cart. Writes only xy-k-sjjd-ii.json."""
from lib import *
from p4lib import *

d = D("xy-k-sjjd-ii", [620, 600, 1550], {"shell": "gloss#f4f5f7", "grey": "plastic#a9adb3", "deck": "plastic#a3a7ad",
                                          "tray": "plastic#8f949a", "dark": "plastic#3a3d42", "black": "gloss#111214"})
cx, cz = 300, 300
# base: grey shroud, 4 flat tapered legs, castors
d.loft("shroud", [sec(150, 300, 290, 70, cx, cz), sec(250, 350, 330, 80, cx, cz), sec(305, 345, 325, 78, cx, cz)], "grey")
for k, (x, z) in enumerate(((50, 60), (570, 60), (50, 540), (570, 540))):
    d.add(f"leg-{k}", "bar", "grey", **{"from": [cx + (x - cx) * 0.3, 200, cz + (z - cz) * 0.3], "to": [x, 140, z]}, section=[92, 46], r=14)
    d.add(f"castor-{k}", "caster", "rubber#7d838a", at=[x, 0, z + 20], d=100)
    d.cyl(f"castor-hub-{k}", [x - 17, 50, z - 10], [x + 17, 50, z - 10], 62, "plastic#d9dbde", sides=24)
# lower cabinet and printer
d.box("cabinet", [130, 290, 150, 470, 512, 450], "shell", r=30)
d.slab("cab-handle", "front", rrect(330, 420, 410, 446, 13), [447, 453], "black", r=2)
d.box("printer", [150, 510, 180, 440, 703, 425], "shell", r=10)
d.box("printer-mouth", [172, 690, 200, 418, 705, 400], "dark", r=8)
d.box("printer-panel", [380, 700, 380, 425, 706, 418], "plastic#c9ccd0", r=3)
d.box("shelf", [250, 512, 420, 470, 517, 545], "plastic#d3d6da", r=3)
# column (2 tubes) and the tray under the deck
d.cyl("column", [230, 505, 150], [230, 1000, 150], 42, "metal#cfd2d6", copies=[[50, 0, 0]])
d.box("column-cap", [205, 940, 128, 305, 1000, 175], "shell", r=10)
d.loft("tray", [sec(770, 400, 260, 30, 340, 300), sec(815, 460, 310, 36, 340, 300)], "tray")
d.box("tray-in", [130, 813, 160, 550, 817, 440], "plastic#7c8187", r=20)
d.box("tray-arm", [230, 800, 140, 280, 830, 200], "tray", r=6)
# deck: grey top, white curved underside, keyboard, mouse, connector knobs
d.loft("deck-under", [sec(960, 540, 330, 40, 310, 320), sec(1000, 600, 390, 34, 310, 320), sec(1034, 620, 400, 32, 310, 320)], "shell")
d.add("deck-top", "slab", "deck", plane="top", box=[0, 1030, 120, 620, 1056, 520], radii=[32], r=6)
d.box("keyboard", [120, 1055, 355, 420, 1066, 470], "plastic#f2f3f4", r=4)
d.decal("keys", [270, 1066.3, 412], [280, 90], "top", "plastic#dfe2e6", soft=True)
d.sphere("mouse", [475, 1062, 415], None, "plastic#f2f3f4", radii=[30, 14, 46])
# connector knobs on the deck's front rim: a light pair at the left, a dark pair left of the middle
d.cyl("knob", [45, 1043, 519], [45, 1043, 531], 18, "plastic#c9ccd0", copies=[[30, 0, 0]])
d.cyl("knob-d", [180, 1043, 519], [180, 1043, 531], 18, "plastic#5d6268", copies=[[30, 0, 0]])
d.cyl("knob-r", [525, 1055, 490], [525, 1064, 490], 18, "plastic#8fa8c8", copies=[[34, 0, 0]])
# VESA plate with a round hole, monitor
d.box("vesa", [220, 1052, 150, 290, 1250, 172], "plastic#9a9fa5", r=6)
d.cyl("vesa-hole", [255, 1115, 148], [255, 1115, 174], 34, "dark")
# thin monitor: silver-grey edges and back, black glass with a narrow border (screen crop perspective-corrected)
d.box("monitor-back", [0, 1232, 174, 510, 1550, 194], "metal#c4c7cb", r=6)
d.add("screen", "screen", "black", box=[2, 1234, 193, 508, 1548, 199], r=4, bezel=7, print="med_xy-k-sjjd-ii_screen")
d.save()
