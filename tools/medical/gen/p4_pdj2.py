"""XY-K-PDJ-II pelvic floor trainer on a pole trolley. Writes only xy-k-pdj-ii.json."""
import math
from lib import *
from p4lib import *

d = D("xy-k-pdj-ii", [520, 500, 1250], {"shell": "gloss#f5f6f7", "pink": "plastic#e9a8b6", "col": "plastic#e3e6ea",
                                        "grey": "plastic#9aa0a6", "dark": "plastic#3a3f45"})
cx, cz = 260, 250
ends = []
for k in range(5):
    a = math.radians(90 + 72 * k)
    ends.append((cx + 228 * math.cos(a), cz + 228 * math.sin(a)))
for k, (x, z) in enumerate(ends):
    # wide flat legs running out level, the end turned down into a socket over the castor
    ex, ez = cx + (x - cx) * 0.93, cz + (z - cz) * 0.93
    d.add(f"leg-{k}", "bar", "shell", **{"from": [cx, 118, cz], "to": [ex, 112, ez]}, section=[66, 30], r=12)
    d.cyl(f"leg-end-{k}", [x, 86, z], [x, 126, z], 46, "shell")
    d.add(f"castor-{k}", "caster", "rubber#eef0f2", at=[x, 0, z], d=75)
    # big pink hub caps on both faces of the white wheel
    d.cyl(f"castor-cap-{k}", [x - 13.5, 37.5, z - 22.5], [x + 13.5, 37.5, z - 22.5], 54, "pink", sides=24)
d.cyl("hub", [cx, 95, cz], [cx, 150, cz], 120, "shell")
d.box("collar", [cx - 48, 150, cz - 38, cx + 48, 166, cz + 38], "pink", r=10)
d.add("column", "bar", "col", **{"from": [cx, 150, cz], "to": [cx, 960, cz]}, section=[72, 50], r=18)
d.decal("column-label", [cx, 340, cz + 25.5], [26, 40], "front", "pink", soft=True)
# storage box: white with a thick pink lid, black slot handle
d.box("box", [80, 590, 120, 440, 740, 380], "shell", r=12)
d.box("box-lid", [78, 738, 118, 442, 762, 382], "pink", r=8)
d.slab("box-handle", "front", rrect(212, 650, 338, 688, 17), [376, 382], "black#141517", r=2)
d.slab("box-handle-in", "front", rrect(222, 658, 328, 680, 10), [380, 383], "plastic#d8dbdf", r=1)
d.decal("box-text", [260, 625, 380.5], [100, 4], "front", "plastic#c9ccd0", soft=True)
# tray: white body, pink top plate with a darker pink rim
d.box("tray", [35, 952, 85, 485, 990, 415], "shell", r=14)
d.box("tray-top", [43, 984, 93, 477, 994, 407], "plastic#de8fa1", r=10)
d.box("tray-top-in", [55, 990, 105, 465, 996, 395], "pink", r=8)
# tablet unit: a wedge (deep at the foot, thin at the top), white front frame, pink sides
P = poly([(236, 996), (318, 996), (252, 1250), (224, 1250)])
d.slab("unit", "side", P, [115, 405], "shell", r=12)
d.slab("unit-side", "side", P, [111, 118], "pink", r=3, copies=[[291, 0, 0]])
t = rot("x", -15, [260, 996, 318])
# copy offsets are applied after the turn (world space): a second row 70 mm lower along the tilted face
ROW2 = [0, -70 * math.cos(math.radians(15)), 70 * math.sin(math.radians(15))]
# display: white touch UI (no screen crop): light tiles with pink icons in 2 rows x 4, two blue header keys
d.box("screen", [133, 1062, 314, 387, 1236, 319.5], "gloss#f6f7f9", r=4, rot=t)
d.decal("ui-bar", [260, 1222, 319.8], [240, 10], "front", "plastic#e7f0fa", soft=True, rot=t)
d.decal("ui-key", [205, 1210, 319.9], [34, 9], "front", "gloss#4d8fd9", soft=True, copies=[[110, 0, 0]], rot=t)
d.decal("ui-logo", [260, 1223, 319.9], [24, 5], "front", "gloss#4d8fd9", soft=True, rot=t)
d.decal("ui-tile", [168, 1166, 319.8], [54, 62], "front", "plastic#eceef2", soft=True,
        repeat=rep(4, [61, 0, 0]), copies=[ROW2], rot=t)
d.decal("ui-icon", [168, 1174, 319.9], [24, 22], "front", "plastic#f2b3c0", soft=True,
        repeat=rep(4, [61, 0, 0]), copies=[ROW2], rot=t)
d.decal("ui-text", [168, 1150, 319.9], [26, 3], "front", "plastic#e59aab", soft=True,
        repeat=rep(4, [61, 0, 0]), copies=[ROW2], rot=t)
# lower control strip: white, 3 dark navy sockets in the middle, big pink knobs at the ends
d.box("strip", [117, 1000, 312, 403, 1054, 319], "plastic#f1f2f4", r=4, rot=t)
d.cyl("socket", [222, 1027, 318], [222, 1027, 323], 26, "plastic#3e4b63", copies=[[38, 0, 0], [76, 0, 0]], rot=t)
d.cyl("socket-in", [222, 1027, 322], [222, 1027, 325], 12, "plastic#8d96a3", copies=[[38, 0, 0], [76, 0, 0]], rot=t)
d.lathe("knob", [150, 1027, 318], [[0, 0], [21, 0], [21, 14], [18, 18], [0, 18]], "pink", axis="z", sides=24, copies=[[220, 0, 0]], rot=t)
d.decal("knob-mark", [150, 1038, 336.2], [2, 8], "front", "white", soft=True, copies=[[220, 0, 0]], rot=t)
# probe cradle on the tray's left front: pink fork holding a grey probe
d.box("cradle", [52, 992, 300, 150, 1006, 385], "pink", r=6)
d.box("cradle-fork", [56, 1004, 330, 70, 1040, 362], "pink", r=5, copies=[[60, 0, 0], [80, 0, 0]])
d.cyl("probe", [62, 1032, 346], [146, 1032, 346], 26, "plastic#7e848b")
d.save()
