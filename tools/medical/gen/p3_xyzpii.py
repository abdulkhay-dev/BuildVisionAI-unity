"""XYZP-II computer-trolley medium frequency unit: mint-green and white workstation cart, pull-out keyboard shelf,
flat-panel monitor on the head. Only a small scene photo exists — proportions from it (cart next to a seated woman)."""
from p3lib import *

d = D("xyzp-ii", [640, 620, 1350], {
    "green": "gloss#6fd0b0", "shell": "gloss#f4f5f7", "dark": "plastic#1d1f22", "kbd": "plastic#25272b", "keys": "plastic#3d4046",
    "bezel": "gloss#111214", "ui": "gloss#f2f5f8", "ui-b": "gloss#5b9be0", "ui-g": "plastic#c9d2dc", "wheel": "rubber#2a2b2d",
    "stand": "gloss#18191b"})
ZB, ZF = 40, 470
# ---- plinth and castors
d.box("plinth", [50, 64, ZB, 510, 118, ZF + 10], "green", r=14)
d.add("castor", "caster", "wheel", at=[80, 0, ZB + 50], d=55, copies=[[400, 0, 0], [0, 0, 330], [400, 0, 330]])
# ---- lower cabinet: green side panels with a kinked front edge, white front, dark open compartment low on the left
side = rpoly([(ZB, 112), (ZF, 112), (ZF + 10, 330), (ZF - 10, 690), (ZB, 690)], [6, 6, 30, 10, 6])
d.slab("side-l", "side", side, [50, 102], "green", r=14)
d.slab("side-r", "side", side, [458, 510], "green", r=14)
d.box("core", [100, 112, ZB, 460, 690, ZF - 12], "shell", r=6)
d.box("front", [102, 112, ZF - 14, 458, 688, ZF - 4], "shell", r=6)
d.box("opening", [126, 120, ZF - 6, 290, 560, ZF - 2], "dark", r=6)
d.box("opening-in", [132, 124, ZF - 2.5, 284, 552, ZF - 1.5], "bezel", soft=True)
# ---- waist and the white keyboard shelf (pulled out forward, reaching right), keyboard and mouse
d.box("waist", [56, 688, ZB, 504, 792, ZF - 10], "green", r=12)
d.box("shelf", [40, 790, 190, 640, 826, ZF + 150], "shell", r=12)
d.box("kbd", [110, 826, ZF + 20, 470, 840, ZF + 140], "kbd", r=6)
d.box("keys", [120, 839, ZF + 30, 460, 841.5, ZF + 130], "keys", r=3, soft=True)
d.add("mouse", "loft", "dark", sections=[{"at": 826, "w": 60, "d": 95, "r": 28, "cx": 560, "cz": ZF + 70},
                                         {"at": 846, "w": 54, "d": 84, "r": 26, "cx": 560, "cz": ZF + 70}], dome="end", domeH=10)
d.box("back-col", [56, 745, ZB, 504, 846, ZB + 130], "green", r=10)
# ---- head: green block, wider at the top
head = rpoly([(ZB - 10, 836), (ZF - 10, 836), (ZF + 50, 1022), (ZF + 44, 1032), (ZB - 10, 1032)], [8, 10, 6, 6, 10])
d.slab("head", "side", head, [20, 540], "green", r=16)
# ---- monitor on a black stand
d.box("stand-base", [200, 1030, 160, 380, 1042, 320], "stand", r=10)
d.box("stand-neck", [270, 1040, 230, 310, 1130, 260], "stand", r=8)
d.add("monitor", "screen", "bezel", box=[40, 1080, 260, 540, 1350, 290], r=10, face="front", bezel=16)
d.decal("ui", [290, 1212, 291], [460, 236], "front", "ui", soft=True)
d.decal("ui-side", [76, 1180, 291.3], [26, 140], "front", "ui-b", soft=True)
d.decal("ui-btn", [165, 1120, 291.3], [26, 16], "front", "ui-b", soft=True, copies=[[225, 0, 0]])
d.decal("ui-row", [200, 1270, 291.3], [110, 8], "front", "ui-g", soft=True, copies=[[200, 0, 0], [0, -40, 0], [200, -40, 0], [0, -80, 0], [200, -80, 0]])
d.decal("ui-title", [290, 1316, 291.3], [120, 8], "front", "ui-g", soft=True)
d.save()
