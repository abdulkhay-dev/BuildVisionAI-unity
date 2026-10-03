from pfx_lib import *
# table length along z: brushed "S" end cap at the back (z~0) with the monitor; the patient sits at the front end
d = D("xy-szgjk-ii", [850, 1050, 1330], {
  "shell": "gloss#f4f5f7", "panel": "plastic#dde0e4", "steel": "metal#c4c8ce", "end": "metal#b4b9c0",
  "black": "plastic#2b2e33", "red": "gloss#d42a26", "grey": "plastic#9aa0a6", "cam": "plastic#1f2124",
  "ui": "gloss#8fc4ec", "tile": "plastic#fbfcfd"})
TOP = 680   # measured on the photos (seated dummy, column/table ratios): the table is at ~680, not 800
# --- floor rails across the width, flat cross bar along the length, small castors
d.box("rail", [0, 14, 140, 850, 62, 260], "steel", r=14, copies=[[0, 0, 650]])
d.box("cross", [385, 22, 250, 465, 55, 800], "steel", r=10)
d.add("castor", "caster", at=[45, 0, 200], d=50, copies=[[760, 0, 0], [0, 0, 650], [760, 0, 650]])
# --- telescopic lifting columns (3 stages, widest at the bottom)
for i, z in enumerate((200, 850)):
    d.cyl(f"col1-{i}", [425, 70, z], [425, 300, z], 125, "steel")
    d.cyl(f"col2-{i}", [425, 300, z], [425, 440, z], 108, "steel")
    d.cyl(f"col3-{i}", [425, 440, z], [425, TOP - 190 if z < 300 else TOP - 95, z], 92, "steel")
    d.cyl(f"col-ring-{i}", [425, 295, z], [425, 308, z], 112, "end", copies=[[0, 140, 0]])
# --- table: white slab with big rounded corners at the patient end, S-end housing with a brushed end cap
d.slab("top", "top", "M 85 30 L 765 30 Q 800 30 800 65 L 800 900 Q 800 1030 670 1030 L 180 1030 Q 50 1030 50 900 "
       "L 50 65 Q 50 30 85 30 Z", [TOP - 100, TOP], "shell", r=35)
d.box("s-housing", [55, TOP - 190, 35, 795, TOP - 80, 330], "shell", r=24)
d.box("s-undercut", [130, TOP - 196, 250, 720, TOP - 186, 330], "plastic#4a4e55", soft=True)
d.slab("s-cap", "top", "M 44 24 L 806 24 L 806 115 L 796 115 L 796 36 L 54 36 L 54 115 L 44 115 Z",
       [TOP - 190, TOP + 2], "end", r=4)
d.decal("s-logo", [425, TOP - 95, 23.5], [62, 82], "back", "plastic#8a9099", soft=True)
# --- top: plinth at the S end, two inset work panels on the patient half
d.box("plinth", [70, TOP - 5, 40, 780, TOP + 50, 340], "shell", r=26)
d.box("panel-l", [90, TOP - 1, 390, 415, TOP + 2, 985], "panel", r=20)
d.box("panel-r", [435, TOP - 1, 390, 760, TOP + 2, 985], "panel", r=20)
d.decal("panel-screw", [425, TOP + 2.5, 975], [10, 10], "top", "plastic#8a9099", soft=True)
# --- edges: e-stop on the left; e-stop, three grey buttons and lettering on the right
d.lathe("e-stop-l", [50, TOP - 50, 330], [[0, 0], [22, 0], [22, 8], [18, 16], [0, 18]], "red", axis="x",
        rot=rot("y", 180, [50, TOP - 50, 330]))
d.lathe("e-stop-r", [800, TOP - 50, 330], [[0, 0], [22, 0], [22, 8], [18, 16], [0, 18]], "red", axis="x")
d.lathe("button-r", [800, TOP - 50, 410], [[0, 0], [16, 0], [16, 7], [0, 8]], "plastic#b7bcc3", axis="x",
        repeat=rep(3, [0, 0, 60]))
d.decal("sunnyou", [800.5, TOP - 50, 700], [150, 18], "right", "plastic#9aa0a6", soft=True)
# --- two-link arm: hub on the plinth, link 1 (white, black top band and end), elbow, flat link 2, grip, forearm pad
d.lathe("hub", [425, TOP + 50, 210], [[0, 0], [115, 0], [110, 30], [92, 62], [80, 70], [0, 70]], "shell")
d.lathe("hub-ring", [425, TOP + 50, 210], [[0, 0], [118, 0], [118, 8], [0, 8]], "grey")
L1 = rot("y", 20, [425, 0, 210])
d.box("link1", [370, TOP + 120, 150, 480, TOP + 225, 650], "shell", r=42, rot=L1)
d.box("link1-top", [372, TOP + 205, 152, 478, TOP + 236, 648], "black", r=15, rot=L1)
d.box("link1-end", [368, TOP + 118, 570, 482, TOP + 236, 662], "black", r=40, rot=L1)
d.cyl("elbow", [560, TOP + 125, 580], [560, TOP + 58, 580], 80, "shell")
d.bar("link2", [560, TOP + 50, 580], [400, TOP + 50, 780], [80, 22], "shell", r=10)
d.lathe("discs", [400, TOP + 2, 780], [[0, 0], [75, 0], [75, 12], [62, 14], [62, 30], [48, 34], [48, 62], [0, 62]], "steel")
d.cyl("grip", [400, TOP + 62, 780], [400, TOP + 225, 780], 36, "black")
d.lathe("grip-knob", [400, TOP + 225, 780], [[0, 0], [24, 0], [28, 10], [20, 24], [0, 26]], "black")
d.box("pad-bracket", [445, TOP + 40, 800, 505, TOP + 72, 950], "shell", r=10)
d.box("forearm-pad", [432, TOP + 70, 790, 520, TOP + 112, 990], "black", r=32)
# --- monitor (~27": 640 x 390 measured against the table length on photos 2 and 3), its bottom ~100 above the plinth,
# on a white pole at the S end; light-blue UI drawn with decals; camera boom on top
MB = TOP + 150
d.cyl("pole", [425, TOP + 50, 110], [425, MB + 10, 110], 40, "shell")
d.add("monitor", "screen", "shell", box=[105, MB, 85, 745, MB + 390, 135], r=14, face="front", bezel=22)
d.decal("ui", [425, MB + 195, 135.6], [596, 346], "front", "ui", soft=True)
d.decal("ui-tile", [215, MB + 115, 136.2], [80, 94], "front", "tile", soft=True, repeat=rep(5, [105, 0, 0]))
d.decal("ui-title", [275, MB + 270, 136.2], [210, 13], "front", "tile", soft=True)
d.decal("ui-hello", [230, MB + 305, 136.2], [120, 8], "front", "tile", soft=True)
d.box("side-box", [83, MB + 140, 92, 105, MB + 230, 128], "plastic#d3d6db", r=6)
d.lathe("cam-hub", [425, MB + 390, 108], [[0, 0], [46, 0], [46, 84], [0, 88]], "shell")
d.lathe("cam-hub-ring", [425, MB + 410, 108], [[47, 0], [47, 3], [0, 3], [0, 0]], "grey", repeat=rep(3, [0, 16, 0]))
d.bar("cam-boom", [425, MB + 455, 108], [790, MB + 455, 108], [32, 18], "steel", r=5)
d.box("camera", [760, MB + 428, 78, 842, MB + 485, 142], "cam", r=8)
d.decal("cam-lens", [801, MB + 456, 142.5], [44, 22], "front", "screen", soft=True)
d.save()
