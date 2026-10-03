"""smart-sky-track (batch robot-1): ceiling rail BWS head. A section of the aluminium rail (along z) at the top,
the white motor head hanging under it (grey end frames with a dark grille, a white lower plate with a green LCD
strip; lettering and lines on the side), the grey webbing strap down to the white/grey spreader bar (across the
rail), the coiled cable to the white handheld remote, the emergency pull cord and the training vest below."""
from r_lib import *
from p1lib import text_len

W, DP, H = 560, 820, 1500
CX = W / 2
d = D("smart-sky-track", [W, DP, H], {
    "white": "gloss#f5f6f7", "frame": "plastic#8c8780", "rail": "metal#c9ccd0", "dark": "plastic#2e3033",
    "grille": "plastic#3b3d40", "lcd": "gloss#3d9a62", "blue": "gloss#3fa9e0", "line": "plastic#4a4d52",
    "text": "plastic#7d8288", "strap": "fabric#7b7670", "vest": "fabric#7a6f67", "yellow": "gloss#f2c618",
    "metal": "metal#b9bdc2", "btn": "plastic#e4e6e9"})
CZ = DP / 2
# --- rail section with the trolley slot underneath
d.box("rail", [CX - 80, 1410, 0, CX + 80, 1500, DP], "rail", r=6)
d.box("rail-slot", [CX - 22, 1408, 0, CX + 22, 1411, DP], "dark")
d.box("trolley", [CX - 30, 1395, CZ - 120, CX + 30, 1410, CZ + 120], "dark", r=4)
# --- head: grey core (end frames, bottom lip), white body over the middle, grilles + white plates + LCD on the ends
HX0, HX1, HY0, HY1 = CX - 210, CX + 210, 1120, 1400
d.box("head-core", [HX0, HY0, 10, HX1, HY1 - 30, DP - 10], "frame", r=70)
d.box("head-top", [HX0 + 20, HY1 - 40, 40, HX1 - 20, HY1 + 2, DP - 40], "white", r=30)
d.box("head-body", [HX0 - 2, HY0 + 30, 70, HX1 + 2, HY1, DP - 70], "white", r=34)
d.box("grille", [CX - 155, 1250, DP - 12, CX + 155, 1372, DP - 8], "grille", r=14, copies=[[0, 0, -(DP - 20)]])
d.box("grille-rib", [CX - 148, 1258, DP - 8, CX - 145, 1364, DP - 7], "dark", soft=True, repeat=rep(37, [8, 0, 0]))
d.box("grille-rib-b", [CX - 148, 1258, 7, CX - 145, 1364, 8], "dark", soft=True, repeat=rep(37, [8, 0, 0]))
d.box("end-plate", [CX - 165, 1132, DP - 16, CX + 165, 1246, DP - 6], "white", r=30, copies=[[0, 0, -(DP - 22)]])
d.box("lcd", [CX - 55, 1172, DP - 6, CX + 55, 1196, DP - 4.5], "lcd", r=3, copies=[[0, 0, -(DP - 10.5)]])
d.box("warn", [CX - 175, 1378, DP - 10, CX - 155, 1392, DP - 8.5], "yellow", r=1, soft=True)
# side lettering and lines (review 2026-10-03): photo 1 shows them on the side to the RIGHT of the labelled end, i.e.
# the +x face: "Dynamic Body Weight Support System" near the labelled (front) end, the grey line with blue end segments,
# "Sunnyou 翔宇" near the back end with a thin sub-line. text() reads mirrored from +x, so the strokes are mirrored in z.
XS = HX1 + 2.5
d.box("side-line", [XS, 1268, 160, XS + 1, 1272, DP - 160], "line", soft=True)
d.box("side-blue", [XS, 1268, 110, XS + 1, 1272, 200], "blue", soft=True, copies=[[0, 0, DP - 310]])
d.box("side-text", [XS, 1300, DP - 520, XS + 1, 1312, DP - 150], "text", soft=True)
n0 = len(d.d["parts"])
L = text_len("Sunnyou 翔宇", 30)
z0 = 110
text(d, "sunnyou", "Sunnyou 翔宇", [XS + 1, 1205, z0], 30, "line", along=(1, 0), stroke=4, face="right")
for p in d.d["parts"][n0:]:
    p["at"][2] = round(2 * (z0 + L / 2) - p["at"][2], 1)
    p["rot"]["deg"] = -p["rot"]["deg"]
    p["rot"]["about"] = list(p["at"])
d.box("sunnyou-sub", [XS, 1188, z0 + 30, XS + 1, 1193, z0 + L - 20], "text", soft=True)
d.box("strap-exit", [CX - 45, HY0 - 2, CZ - 20, CX + 45, HY0, CZ + 20], "dark", r=3)
# --- strap, buckle, connector, spreader bar (across the rail) with the grey frame and the C handle
SY = 680
d.strap("strap", [[CX, HY0, CZ], [CX, 860, CZ]], [50, 3], "strap")
d.box("buckle", [CX - 32, 770, CZ - 10, CX + 32, 870, CZ + 10], "metal", r=6)
d.box("buckle-plate", [CX - 26, 740, CZ - 14, CX + 26, 775, CZ + 14], "frame", r=5)
d.box("connector", [CX - 55, SY + 30, CZ - 32, CX + 55, SY + 70, CZ + 32], "white", r=14)
d.box("spreader", [CX - 190, SY - 30, CZ - 30, CX + 190, SY + 32, CZ + 30], "white", r=24)
d.box("spreader-seam", [CX - 190, SY - 2, CZ + 29, CX + 190, SY + 1, CZ + 31], "btn", soft=True)
d.sweep("spreader-frame", [[CX - 255, SY + 12, CZ], [CX - 255, SY - 22, CZ], [CX + 265, SY - 22, CZ], [CX + 265, SY + 18, CZ],
                           [CX + 205, SY + 18, CZ]], [22, 26], "frame", bend=20, r=6)
d.box("spreader-text", [CX - 120, SY + 8, CZ + 30, CX + 80, SY + 16, CZ + 31.5], "text", soft=True)
# --- remote on a coiled cable, hooked at the left end; emergency pull cord with its white handle
RX = CX - 220
d.coil("remote-cable", [CX - 120, HY0, CZ - 60], [RX, 790, CZ + 40], 34, 4, 26, "white")
d.box("remote", [RX - 34, 560, CZ + 32, RX + 34, 760, CZ + 56], "white", r=26)
d.box("remote-screen", [RX - 22, 690, CZ + 56, RX + 22, 735, CZ + 57.5], "dark", r=3)
d.lathe("remote-btn", [RX - 13, 665, CZ + 56], [[0, 0], [10, 0], [10, 3], [0, 4]], "btn", axis="z",
        copies=[[26, 0, 0], [0, -30, 0], [26, -30, 0], [0, -60, 0], [26, -60, 0], [0, -90, 0], [26, -90, 0]])
d.cyl("pull-cord", [CX + 150, HY0, CZ + 60], [CX + 150, 900, CZ + 60], 4, "white", soft=True)
d.cyl("pull-handle", [CX + 150, 780, CZ + 60], [CX + 150, 900, CZ + 60], 24, "white")
# --- training vest hanging from the spreader ends (grey-brown straps)
VZ, VT = CZ + 20, 420
for i, s in enumerate((-1, 1)):
    d.strap(f"vest-strap-{i}", [[CX + s * 240, SY - 22, CZ], [CX + s * 170, 560, VZ], [CX + s * 110, VT, VZ + 90]],
            [45, 3], "vest", bend=40, soft=True)
d.loft("vest", [sec(130, 300, 220, 95, CX, VZ), sec(300, 330, 240, 105, CX, VZ), sec(VT, 320, 230, 100, CX, VZ)],
       "vest", caps=False, soft=True)
d.strap("vest-leg", [[CX - 140, 140, VZ + 100], [CX - 20, 20, VZ + 110], [CX + 140, 140, VZ + 100]], [45, 3], "vest",
        bend=60, soft=True)
d.save()
