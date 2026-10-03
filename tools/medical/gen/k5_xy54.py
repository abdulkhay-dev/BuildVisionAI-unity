"""kinesio-5: xy-54 OT table — maple cabinet on castors with two doors (front, photo 2), a fold-down work tray
on the back (photo 1), fold-out side shelves (ring tree left, graded peg blocks right) and OT toys on top."""
from k5lib import *

# H: the photos give a worktop at ~860 (body ~1.35x taller than drawn first: photo 2 body height/width ~0.64 with the
# 1100 cabinet) and the bead-maze loops ~270 above it, so the whole model is ~1130 high (printed 940 is not the
# overall height of the dressed table); size covers the whole model
W, DD, H = 1890, 1030, 1130
d = D("xy-54", [W, DD, H], {"maple": "plastic#e3c58f", "maple2": "plastic#d9b77c", "top": "plastic#e8cc98",
                             "chrome": "chrome", "alu": "metal#c8ccd0", "wood": "plastic#c98a4a",
                             "red": "gloss#d8332b", "yel": "gloss#f2c018", "grn": "gloss#2c9a48",
                             "blu": "gloss#2c5fb8", "white": "plastic#f4f4f2", "steel": "metal#9ea4aa",
                             "dark": "plastic#2a2b2e", "knobB": "gloss#2b6fd0"})
X0, X1 = 395, 1495          # cabinet body
Z0, Z1 = 380, 1000          # back face (tray side) .. front face (doors)
YB, YT = 120, 835           # body bottom / top
# --- body, worktop, doors
d.box("body", [X0, YB, Z0, X1, YT, Z1], "maple", r=6)
d.box("worktop", [X0 - 15, YT - 10, Z0 - 15, X1 + 15, YT + 25, Z1 + 15], "top", r=5)
CXM = (X0 + X1) / 2
d.box("door-l", [X0 + 6, YB + 8, Z1, CXM - 2, YT - 8, Z1 + 4], "maple2", r=3)
d.box("door-r", [CXM + 2, YB + 8, Z1, X1 - 6, YT - 8, Z1 + 4], "maple2", r=3)
# bow-shaped light wooden pulls either side of the door gap, the lock under the right one
for k, (x, sg) in enumerate(((CXM - 30, -1), (CXM + 30, 1))):
    d.tube(f"pull{k}", [[x, 470, Z1 + 3], [x + sg * 6, 490, Z1 + 20], [x + sg * 6, 570, Z1 + 20], [x, 590, Z1 + 3]], 14,
           "plastic#e2b97a", bend=20)
d.lathe("lock", [CXM + 30, 420, Z1 + 4], [[0, 0], [10, 0], [10, 5], [0, 6]], "chrome", axis="z", soft=True)
# chrome corner trims and the back recess frame
for x in (X0 - 2, X1 - 10):
    for z in (Z0 - 2, Z1 - 10):
        d.box(f"trim{x}-{z}", [x, YB, z, x + 12, YT, z + 12], "alu", r=3)
d.tube("back-frame", [[X0 + 40, YB + 70, Z0 - 6], [X0 + 40, YT - 50, Z0 - 6], [X1 - 40, YT - 50, Z0 - 6],
                      [X1 - 40, YB + 70, Z0 - 6], [X0 + 40, YB + 70, Z0 - 6]], 16, "alu", bend=10)
d.box("back-panel", [X0 + 48, YB + 78, Z0 - 4, X1 - 48, YT - 58, Z0 + 1], "maple2", r=2)
for x in (X1 - 40, X1 - 120):
    d.sphere(f"blue-knob{x}", [x, YB + 70, Z0 - 18], 30, "knobB")
# side recess frames
for x, sgn in ((X0, -1), (X1, 1)):
    xx = x + sgn * 5
    d.tube(f"side-frame{x}", [[xx, YB + 60, Z0 + 40], [xx, YT - 40, Z0 + 40], [xx, YT - 40, Z1 - 40], [xx, YB + 60, Z1 - 40],
                              [xx, YB + 60, Z0 + 40]], 12, "alu", bend=8)
# castors
for x in (X0 + 70, X1 - 70):
    for z in (Z0 + 70, Z1 - 70):
        d.caster(f"castor{x}-{z}", [x, 0, z], 100, "rubber#7d8288")
# --- fold-down work tray on the back side, sloping slightly down outward
tr = rot("x", -8, [0, 305, Z0])
d.box("tray", [X0 - 60, 285, 20, X1 - 120, 305, Z0], "maple2", r=4, rot=tr)
d.box("tray-lip", [X0 - 60, 305, 20, X1 - 120, 325, 36], "maple2", r=4, rot=tr)
d.bar("tray-strut", [X1 - 160, 300, 60], [X1 - 160, 170, Z0 - 5], [14, 6], "alu", r=2)
d.bar("tray-strut2", [X0 - 20, 300, 60], [X0 + 20, 170, Z0 - 5], [14, 6], "alu", r=2)
# peg board with coloured shapes on the tray's left half, simulation tools on the right half
d.box("shape-board", [X0 - 40, 305, 50, X0 + 400, 328, 340], "maple", r=4, rot=tr)
cols = ["red", "yel", "grn", "blu", "red", "grn", "yel", "blu"]
for i in range(8):
    x = X0 + 10 + (i % 4) * 100
    z = 110 + (i // 4) * 130
    d.box(f"shape{i}", [x, 328, z, x + 50, 342, z + 50], cols[i], r=6 if i % 2 else 2, rot=tr)
    d.cyl(f"shape-peg{i}", [x + 25, 340, z + 25], [x + 25, 372, z + 25], 10, "chrome", rot=tr,
          soft=True)
tools = [("red", 90, 30), ("dark", 70, 18), ("red", 110, 22), ("yel", 60, 30), ("blu", 80, 20), ("grn", 70, 25)]
for i, (c, ln, wd) in enumerate(tools):
    x = X0 + 480 + (i % 3) * 140
    z = 90 + (i // 3) * 150
    d.box(f"tool{i}", [x, 306, z, x + ln, 322, z + wd], c, r=4, rot=tr)
# --- side shelves (fold-out) with chrome struts
SY = 400
for s, xa, xb, xw in (("l", 0, X0, X0), ("r", X1, W, X1)):
    d.box(f"shelf-{s}", [xa, SY - 25, 470, xb, SY, 930], "maple2", r=4)
    xs = xa + 60 if s == "l" else xb - 60
    d.bar(f"shelf-strut-{s}", [xs, SY - 25, 500], [xw, YB + 40, 520], [12, 6], "alu", r=2)
    d.bar(f"shelf-strut2-{s}", [xs, SY - 25, 900], [xw, YB + 40, 880], [12, 6], "alu", r=2)
# left shelf: ring tree (pole with pegs on a round base) and a tilted plate
d.lathe("tree-base", [190, SY, 700], [[0, 0], [110, 0], [110, 20], [100, 26], [0, 26]], "wood")
d.cyl("tree-pole", [190, SY + 26, 700], [190, SY + 420, 700], 40, "wood")
d.sphere("tree-top", [190, SY + 425, 700], 46, "wood")
for k in range(6):
    y = SY + 120 + k * 52
    a = (k % 2) * 2 - 1
    d.cyl(f"tree-peg{k}", [190, y, 700], [190 + a * 90, y + 25, 700 + (k % 3 - 1) * 40], 18, "wood")
d.box("tree-plate", [140, SY + 260, 760, 260, SY + 270, 860], "maple", r=3, rot=rot("x", -55, [200, SY + 265, 760]))
# right shelf: graded peg blocks in a clear tray
d.box("peg-tray", [X1 + 30, SY, 520, W - 20, SY + 30, 880], "acrylic#e8f0f480", r=4)
for k in range(8):
    x = X1 + 50 + k * 42
    h = 60 + k * 12
    d.box(f"pegblk{k}", [x, SY + 5, 560, x + 32, SY + h, 840], "wood", r=4)
    d.box(f"pegband{k}", [x - 1, SY + h * 0.55, 560, x + 33, SY + h * 0.55 + 8, 840], "grn", r=2, soft=True)
# --- toys on the worktop
TY = YT + 25
# pegboard panels at the back-left corner (one facing front, one facing left), white pegs
d.box("pegpanel-a", [X0 + 15, TY, Z0 + 10, X0 + 250, TY + 210, Z0 + 32], "maple", r=4)
d.box("pegpanel-b", [X0 + 10, TY, Z0 + 40, X0 + 32, TY + 210, Z0 + 260], "maple", r=4)
for i in range(15):
    x = X0 + 50 + (i % 5) * 40
    y = TY + 60 + (i // 5) * 50
    d.cyl(f"peg-a{i}", [x, y, Z0 + 32], [x, y, Z0 + 52], 12, "white", soft=True)
for i in range(12):
    z = Z0 + 80 + (i % 4) * 45
    y = TY + 60 + (i // 4) * 50
    d.cyl(f"peg-b{i}", [X0 + 32, y, z], [X0 + 50, y, z], 12, "white", soft=True)
# bead maze: wooden base with coloured wire loops and beads
BX0, BX1, BZ = X0 + 280, X0 + 580, Z0 + 40
d.box("maze-base", [BX0, TY, BZ, BX1, TY + 55, BZ + 150], "wood", r=6)
wires = [("blu", [[BX0 + 30, TY + 55, BZ + 40], [BX0 + 30, TY + 230, BZ + 40], [BX0 + 90, TY + 262, BZ + 50],
                   [BX0 + 140, TY + 150, BZ + 60], [BX0 + 210, TY + 262, BZ + 70], [BX0 + 270, TY + 200, BZ + 80],
                   [BX0 + 270, TY + 55, BZ + 80]]),
         ("red", [[BX0 + 50, TY + 55, BZ + 100], [BX0 + 60, TY + 200, BZ + 100], [BX0 + 120, TY + 215, BZ + 90],
                  [BX0 + 160, TY + 90, BZ + 80], [BX0 + 220, TY + 200, BZ + 70], [BX0 + 250, TY + 55, BZ + 60]]),
         ("grn", [[BX0 + 80, TY + 55, BZ + 120], [BX0 + 100, TY + 150, BZ + 120], [BX0 + 180, TY + 170, BZ + 110],
                  [BX0 + 200, TY + 55, BZ + 100]])]
for name, path in wires:
    d.tube(f"wire-{name}", path, 6, name, bend=40, soft=True)
beads = [(BX0 + 30, TY + 70, BZ + 40, "yel"), (BX0 + 30, TY + 95, BZ + 40, "red"), (BX0 + 30, TY + 120, BZ + 40, "blu"),
         (BX0 + 30, TY + 145, BZ + 40, "grn"), (BX0 + 270, TY + 70, BZ + 80, "red"), (BX0 + 270, TY + 95, BZ + 80, "yel"),
         (BX0 + 250, TY + 72, BZ + 60, "grn"), (BX0 + 200, TY + 70, BZ + 100, "blu"), (BX0 + 160, TY + 95, BZ + 80, "yel")]
for i, (x, y, z, c) in enumerate(beads):
    d.sphere(f"bead{i}", [x, y, z], 26, c)
# flat peg board with white pegs (front-left of the top)
d.box("pegboard", [X0 + 60, TY, Z0 + 330, X0 + 380, TY + 22, Z0 + 560], "wood", r=4)
for i in range(10):
    x = X0 + 100 + (i % 5) * 60
    z = Z0 + 380 + (i // 5) * 110
    d.cyl(f"pb-peg{i}", [x, TY + 22, z], [x, TY + 60, z], 14, "white", soft=True)
# white telephone (simulation tool)
d.box("phone", [X0 + 450, TY, Z0 + 330, X0 + 640, TY + 60, Z0 + 520], "white", r=22,
      rot=rot("x", 8, [0, TY, Z0 + 520]))
d.box("phone-keys", [X0 + 500, TY + 48, Z0 + 440, X0 + 590, TY + 52, Z0 + 505], "plastic#d9dbdf", r=6,
      rot=rot("x", 8, [0, TY, Z0 + 520]), soft=True)
d.cyl("phone-handset", [X0 + 470, TY + 78, Z0 + 370], [X0 + 620, TY + 78, Z0 + 370], 34, "white")
d.sphere("phone-ear", [X0 + 460, TY + 74, Z0 + 375], 58, "white")
d.sphere("phone-mouth", [X0 + 630, TY + 74, Z0 + 375], 58, "white")
# skittle board: 8 wooden pins with ball tops, coloured strings
SX0, SZ0 = X0 + 640, Z0 + 120
d.box("skittle-board", [SX0, TY, SZ0, SX0 + 340, TY + 25, SZ0 + 300], "wood", r=4)
for i in range(8):
    x = SX0 + 45 + (i % 4) * 80
    z = SZ0 + 70 + (i // 4) * 150
    d.cyl(f"pin{i}", [x, TY + 25, z], [x, TY + 150, z], 34, "wood")
    d.sphere(f"pin-top{i}", [x, TY + 158, z], 38, "wood")
for k, c in enumerate(("red", "grn", "yel")):
    d.tube(f"string{k}", [[SX0 + 20, TY + 30, SZ0 + 60 + k * 70], [SX0 + 180, TY + 30, SZ0 + 120 + k * 50],
                          [SX0 + 320, TY + 30, SZ0 + 80 + k * 60]], 8, c, bend=60, soft=True)
# steel rod block at the right-front
d.box("rod-block", [X1 - 180, TY, Z0 + 470, X1 - 40, TY + 40, Z1 - 30], "steel", r=4)
for i in range(6):
    d.cyl(f"rod{i}", [X1 - 160 + i * 22, TY + 40, Z0 + 520], [X1 - 160 + i * 22, TY + 110, Z0 + 520], 14, "steel",
          copies=[[0, 0, 50]])
# small tray of wooden cubes in front of the skittles (photo 2)
d.box("cube-tray", [SX0 + 20, TY, Z1 - 150, SX0 + 230, TY + 22, Z1 - 40], "wood", r=3)
for i in range(8):
    x = SX0 + 35 + (i % 4) * 48
    z = Z1 - 140 + (i // 4) * 50
    d.box(f"cube{i}", [x, TY + 22, z, x + 38, TY + 58, z + 38], "plastic#e0b27a", r=3)
# the fold-down tray hangs lower-middle on the back (photo 1: ~1/3 up the body) -> lift the tray group by DY
DY = 55
for p in d.d["parts"]:
    if p["id"].split("-")[0] in ("tray", "shape", "tool") or p["id"].startswith(("shape", "tool")):
        if "box" in p:
            p["box"][1] += DY; p["box"][4] += DY
        for k in ("from", "to"):
            if k in p:
                p[k][1] += DY
        if "rot" in p:
            p["rot"]["about"][1] += DY
# the struts keep their lower ends on the body
for p in d.d["parts"]:
    if p["id"].startswith("tray-strut"):
        p["to"][1] -= DY
d.save()
