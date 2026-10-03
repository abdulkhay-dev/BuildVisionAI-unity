from h1lib import *
# XY-90 pool hoist: floor base plate with a turntable, beige actuator housing, a round pivot post and a square front post
# on the right; a double-bar boom to the mast; a stainless ladder carriage on the mast carrying a slatted tubular chair
# (facing -x) whose legs bend over into the arm rails (∩ per side), a lap bar, a ladder-like footrest frame in front.
# Review 2026-10-02: chair 470 wide with 10 slats along z, ∩ arm frames, lower frame at 230, bottom carriage arm under
# the chair, footrest on vertical D-frames with rungs, red pin along +x, round pivot post + square front post + pendant.
d = D("xy-90", [2000, 800, 1500], {
    "alu": "metal#c3c8cd", "steel": "metal#d5d8db", "tube": "chrome", "beige": "plastic#a69d8a", "dark": "black#222427",
    "rubber": "rubber#2a2a2a", "red": "gloss#d42a2a"})
CZ = 400
MX = 870  # mast
# --- right: base plate, turntable, posts, housing, actuator, control box, cables, U handle
d.box("plate", [1450, 0, 140, 1970, 12, 660], "steel", r=3)
d.lathe("bolt", [1490, 12, 180], [[0, 0], [14, 0], [14, 8], [0, 8]], "steel", copies=[[440, 0, 0], [0, 0, 440], [440, 0, 440]])
d.lathe("turntable", [1690, 12, CZ], [[0, 0], [195, 0], [195, 28], [185, 34], [0, 34]], "plastic#8f9398")
d.cyl("pivot", [1660, 500, CZ - 90], [1660, 1440, CZ - 90], 70, "alu")
d.bar("post", [1790, 40, CZ - 60], [1790, 1400, CZ - 60], [80, 80], "alu", r=5)
d.box("pendant", [1835, 1290, CZ - 70, 1860, 1400, CZ - 25], "dark", r=8)
d.bar("cross", [1660, 1225, CZ - 75], [1790, 1225, CZ - 75], [40, 50], "alu", r=4)
d.box("housing", [1560, 44, CZ - 160, 1760, 500, CZ + 30], "beige", r=10)
d.box("socket", [1600, 330, CZ + 28, 1640, 390, CZ + 36], "dark", r=3)
d.cyl("actuator", [1530, 200, CZ - 40], [1530, 1110, CZ - 50], 40, "dark")
d.cyl("act-rod", [1530, 1110, CZ - 50], [1530, 1140, CZ - 55], 22, "chrome")
d.box("motor", [1490, 44, CZ - 120, 1585, 220, CZ + 40], "dark", r=10)
d.box("ctrl", [1585, 60, CZ + 30, 1660, 140, CZ + 60], "dark", r=6)
d.tube("cable", [[1840, 1300, CZ - 40], [1830, 1100, CZ - 10], [1800, 800, CZ + 10], [1720, 480, CZ + 45],
                 [1640, 360, CZ + 40]], 14, "dark", bend=80, soft=True)
d.tube("cable2", [[1620, 360, CZ + 36], [1600, 250, CZ + 60], [1580, 120, CZ + 70]], 10, "dark", bend=40, soft=True)
d.tube("handle", [[1820, 1040, CZ - 130], [1985, 1040, CZ - 130], [1985, 1040, CZ + 90], [1820, 1040, CZ + 90]], 26, "tube", bend=80)
# --- boom: two rectangular bars from the mast to the front post
for i, y in enumerate((1330, 1140)):
    d.bar(f"boom{i}", [MX, y, CZ - 60], [1750, y, CZ - 60], [40, 90], "alu", r=6, roll=90)
d.lathe("boom-bolt", [MX + 30, 1330, CZ - 15], [[0, 0], [16, 0], [16, 12], [0, 12]], "dark", axis="z", copies=[[0, -190, 0], [850, 0, 0], [850, -190, 0]])
# --- mast (flat channel with holes) with the ladder carriage, clamp + red pin along +x, bottom arm under the chair
d.bar("mast", [MX, 200, CZ - 60], [MX, 1460, CZ - 60], [110, 60], "alu", r=6)
d.lathe("mast-hole", [MX, 300, CZ - 30], [[0, 0], [7, 0], [7, 2], [0, 2]], "dark", axis="z", repeat=rep(6, [0, 90, 0]))
d.box("panel", [MX - 180, 560, CZ - 190, MX - 60, 1380, CZ + 20], "alu", r=4)
for nm, x, z0, z1, top in (("ladder-a", MX - 190, CZ - 220, CZ + 40, 1500), ("ladder-b", MX - 150, CZ - 160, CZ - 20, 1420)):
    d.tube(nm, [[x, 520, z0], [x, top, z0], [x, top, z1], [x, 520, z1]], 24, "tube", bend=60)
d.cyl("rung", [MX - 190, 700, CZ - 220], [MX - 190, 700, CZ + 40], 20, "tube", repeat=rep(4, [0, 210, 0]))
d.lathe("clamp", [MX + 60, 950, CZ - 60], [[0, 0], [24, 0], [24, 60], [0, 60]], "chrome", axis="x")
d.cyl("pin", [MX + 120, 950, CZ - 60], [MX + 230, 950, CZ - 60], 12, "chrome")
d.cyl("pin-red", [MX + 230, 950, CZ - 60], [MX + 250, 950, CZ - 60], 26, "red")
d.box("bracket", [MX - 200, 560, CZ - 230, MX - 60, 630, CZ + 50], "alu", r=6)
d.box("bottom-arm", [380, 150, CZ - 50, MX + 40, 230, CZ + 50], "alu", r=8)
# --- chair: slatted seat facing -x, ∩ side frames (legs + arm rails), lower frame, lap bar
SX0, SX1, SZ0, SZ1, SY, AY = 330, 800, 150, 650, 600, 830
d.tube("seat-frame", [[SX0, SY, SZ0], [SX1, SY, SZ0], [SX1, SY, SZ1], [SX0, SY, SZ1], [SX0, SY, SZ0]], 26, "tube", bend=20)
d.cyl("slat", [SX0 + 23, SY + 8, SZ0], [SX0 + 23, SY + 8, SZ1], 22, "tube", repeat=rep(10, [47, 0, 0]))
for nm, z in (("side-b", SZ0), ("side-f", SZ1)):
    d.tube(nm, [[SX0, 45, z], [SX0, AY, z], [SX1, AY, z], [SX1, 45, z]], 26, "tube", bend=75)
for i, (x, z) in enumerate(((SX0, SZ0), (SX1, SZ0), (SX0, SZ1), (SX1, SZ1))):
    d.cyl(f"foot{i}", [x, 0, z], [x, 45, z], 34, "rubber")
d.tube("low-frame", [[SX0, 230, SZ0], [SX1, 230, SZ0], [SX1, 230, SZ1], [SX0, 230, SZ1], [SX0, 230, SZ0]], 22, "tube", bend=20)
d.cyl("lap-bar", [SX0 + 40, AY + 28, SZ0 - 40], [SX0 + 40, AY + 28, SZ1 + 40], 24, "tube")
d.box("lap-clamp", [SX0 + 15, AY - 10, SZ0 - 25, SX0 + 65, AY + 50, SZ0 + 25], "steel", r=6, copies=[[0, 0, SZ1 - SZ0]])
d.sphere("lap-knob", [SX0 + 40, AY + 28, SZ0 - 50], 34, "dark", copies=[[0, 0, SZ1 - SZ0 + 100]])
# footrest: two D-frames in front of the front legs with rungs, a slatted tray at the floor in front
FX = SX0 - 110
for nm, z in (("fr-a", SZ0), ("fr-b", SZ1)):
    d.tube(nm, [[SX0, SY - 30, z], [FX, SY - 80, z], [FX, 70, z]], 22, "tube", bend=70)
    d.cyl(nm + "-rung", [FX, 160, z], [SX0, 160, z], 20, "tube", repeat=rep(3, [0, 140, 0]))
FX0, FX1 = 10, FX
d.tube("fr-frame", [[FX1, 70, SZ0 + 20], [FX0, 70, SZ0 + 20], [FX0, 70, SZ1 - 20], [FX1, 70, SZ1 - 20]], 22, "tube", bend=20)
d.cyl("fr-slat", [FX0, 74, SZ0 + 100], [FX1, 74, SZ0 + 100], 18, "tube", repeat=rep(5, [0, 0, 75]))
d.cyl("fr-foot", [FX0 + 15, 0, SZ0 + 20], [FX0 + 15, 60, SZ0 + 20], 24, "rubber", copies=[[0, 0, SZ1 - SZ0 - 40]])
d.save()
