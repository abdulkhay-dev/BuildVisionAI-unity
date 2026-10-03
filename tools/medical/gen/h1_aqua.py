from h1lib import *
from p1lib import text, text_len
# Aquatic underwater treadmill: black-topped white plinth (long flat landing at the left where the optional ramp joins),
# glass tank set back from the plinth front in a stainless frame (door = left end with a blue logo band, D handle and
# latch at its front edge), glass back wall, stainless right end wall with 6 jets + a column of cone nozzles, rows of
# upward cone nozzles along the bottom, inner U rails, belt; a narrow tall white machine module on the right with a
# rounded hood, logo, touch panel, vertical blue XIANGYU MEDICAL stripe, camera on its left face, monitor on a stalk.
# Review 2026-10-02: layout from the photo (landing ~660, tank 1370 × 820 at the back, module 330 wide), right end
# wall with jets, front split 40/60, real lettering, nozzles pointing up.
d = D("aquatic-underwater-treadmill", [2400, 1100, 1960], {
    "white": "gloss#f5f6f7", "black": "black#2a2b2d", "steel": "metal#c9cdd2", "glass": "acrylic#a6d3ea80", "wall": "metal#d7dce0",
    "blue": "gloss#2f8fd8", "grey": "plastic#9aa1a9", "belt": "rubber#3d4146", "dark": "black#1f2124"})
PY = 150
d.box("plinth", [0, 0, 0, 2400, PY - 8, 1100], "white", r=10)
d.box("plinth-top", [4, PY - 12, 4, 2396, PY, 1096], "black", r=6)
TH = 40
TL = text_len("XIANGYU MEDICAL", TH, gap=0.9)
TX = 1350 - TL / 2
text(d, "plinth-text", "XIANGYU MEDICAL", [TX, 55, 1100.5], TH, "grey", gap=0.9, stroke=5)
d.decal("plinth-line", [TX - 400, 75, 1100.5], [650, 5], "front", "grey", soft=True)
d.decal("plinth-line2", [TX + TL + 330, 75, 1100.5], [500, 5], "front", "grey", soft=True)
d.decal("plinth-line-l", [1200, 70, -0.5], [2000, 5], "back", "grey", soft=True)
# tank frame
X0, X1, Z0, Z1, Y0, Y1 = 660, 2030, 40, 860, PY, PY + 1300
XP = X0 + 550  # front post: narrow left pane, wide right pane
S = [48, 48]
for i, (x, z) in enumerate(((X0, Z0), (X0, Z1), (X1, Z1), (X1, Z0), (XP, Z1), (XP, Z0))):
    d.bar(f"post{i}", [x, Y0, z], [x, Y1, z], S, "steel", r=8)
for i, (y) in enumerate((Y0 + 24, Y1)):
    d.bar(f"rail-f{i}", [X0, y, Z1], [X1, y, Z1], S, "steel", r=8)
    d.bar(f"rail-b{i}", [X0, y, Z0], [X1, y, Z0], S, "steel", r=8)
    d.bar(f"rail-l{i}", [X0, y, Z0], [X0, y, Z1], S, "steel", r=8)
    d.bar(f"rail-r{i}", [X1, y, Z0], [X1, y, Z1], S, "steel", r=8)
# glass panes: front, back, left end (door); stainless right end wall
d.box("pane-f", [X0 + 20, Y0 + 45, Z1 - 6, X1 - 20, Y1 - 20, Z1 + 6], "glass")
d.box("pane-b", [X0 + 20, Y0 + 45, Z0 - 6, X1 - 20, Y1 - 20, Z0 + 6], "glass")
d.box("pane-l", [X0 - 6, Y0 + 45, Z0 + 20, X0 + 6, Y1 - 20, Z1 - 20], "glass")
d.box("end-wall", [X1 - 14, Y0 + 40, Z0 + 20, X1 + 4, Y1 - 20, Z1 - 20], "wall")
d.box("band", [X0 - 10, 1120, Z0 + 25, X0 - 4, 1230, Z1 - 25], "blue", r=2)
d.lathe("band-disc", [X0 - 10, 1175, 260], [[0, 0], [35, 0], [35, 1.5], [0, 1.5]], "white", axis="x", rot=rot("y", 180, [X0 - 10, 1175, 260]), soft=True)
text(d, "band-logo", "翔宇", [X0 - 10.5, 1150, 310], 50, "white", face="left", stroke=7)
# door handle + latch at the front edge of the end face
d.tube("handle", [[X0 - 8, 900, Z1 - 70], [X0 - 60, 910, Z1 - 70], [X0 - 60, 1090, Z1 - 70], [X0 - 8, 1100, Z1 - 70]], 22, "chrome", bend=25)
d.box("latch", [X0 - 40, 820, Z1 - 40, X0 - 4, 930, Z1 + 20], "chrome", r=6)
d.box("latch2", [X0 - 30, 960, Z1 - 30, X0 - 4, 1010, Z1 + 10], "chrome", r=6)
# inside: belt, U rails, jets on the right end wall, cone nozzles
d.box("belt", [X0 + 70, Y0, 200, X1 - 70, Y0 + 50, 700], "belt", r=10)
d.box("belt-side", [X0 + 60, Y0, 180, X1 - 60, Y0 + 40, 205], "steel", r=6, copies=[[0, 0, 515]])
for nm, z in (("urail-b", 140), ("urail-f", 760)):
    d.tube(nm, [[X0 + 260, Y0, z], [X0 + 260, Y0 + 980, z], [X1 - 260, Y0 + 980, z], [X1 - 260, Y0, z]], 34, "chrome", bend=90)
for j, z in enumerate((380, 640)):
    for k, y in enumerate((620, 900, 1180)):
        d.sphere(f"jet{j}{k}", [X1 - 16, y, z], 80, "chrome", radii=[10, 40, 40])
        d.sphere(f"jet{j}{k}-c", [X1 - 24, y, z], 26, "dark")
d.lathe("nozzle-v", [X1 - 14, Y0 + 260, Z0 + 70], [[0, 0], [12, 0], [3, 40], [0, 40]], "white", axis="x",
        rot=rot("y", 180, [X1 - 14, Y0 + 260, Z0 + 70]), repeat=rep(8, [0, 120, 0]))
d.lathe("nozzle-f", [X0 + 520, Y0 + 50, Z1 - 40], [[0, 0], [12, 0], [3, 45], [0, 45]], "white", repeat=rep(11, [110, 0, 0]))
d.lathe("nozzle-b", [X0 + 520, Y0 + 50, Z0 + 40], [[0, 0], [12, 0], [3, 45], [0, 45]], "white", repeat=rep(11, [110, 0, 0]))
d.box("led", [X0 + 300, Y1 - 30, Z0 - 2, X0 + 650, Y1 - 15, Z0 + 10], "gloss#3a5be0", soft=True)
# machine module: narrow, tall, flush with the tank front
MX0, MX1 = 2040, 2370
d.box("module", [MX0, PY, Z0, MX1, 1480, Z1], "white", r=24)
d.loft("hood", [sec(1470, MX1 - MX0 + 10, Z1 - Z0 + 10, 60, (MX0 + MX1) / 2, (Z0 + Z1) / 2),
                sec(1530, MX1 - MX0 + 10, Z1 - Z0 + 10, 60, (MX0 + MX1) / 2, (Z0 + Z1) / 2)], "white", dome="end", domeH=30)
d.sphere("camera", [MX0 - 4, 1510, 470], 26, "dark")
d.box("stripe", [2260, PY + 10, Z1, 2330, 960, Z1 + 6], "blue", r=4)
SH = 46
text(d, "stripe-text", "XIANGYU MEDICAL", [2318, 960 - 30 - text_len("XIANGYU MEDICAL", SH, gap=0.5), Z1 + 6.5], SH, "white",
     along=(0, 1), gap=0.5, stroke=6)
d.lathe("logo-disc", [2120, 1365, Z1], [[0, 0], [28, 0], [28, 1.5], [0, 1.5]], "blue", axis="z", soft=True)
text(d, "logo", "翔宇", [2160, 1340, Z1 + 0.5], 48, "blue", stroke=6)
d.box("touch-frame", [2080, 1040, Z1 - 2, 2330, 1270, Z1 + 12], "grey", r=10)
d.add("touch", "screen", box=[2130, 1055, Z1 + 8, 2320, 1255, Z1 + 16], r=6, face="front", bezel=6, mat="grey")
d.lathe("stop", [2102, 1220, Z1 + 12], [[0, 0], [14, 0], [14, 10], [0, 12]], "gloss#d8262a", axis="z")
# monitor on a stalk
d.cyl("stalk", [2205, 1550, 520], [2205, 1700, 520], 46, "grey")
d.box("stalk-foot", [2150, 1550, 470, 2260, 1566, 570], "grey", r=8)
d.add("monitor", "screen", box=[2015, 1700, 500, 2395, 1955, 545], r=10, face="front", bezel=22, mat="plastic#c4c9cf")
d.save()
