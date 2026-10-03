from k4lib import *
d = K("xy-40", [2000, 1150, 2100], {"frame": "metal#e2e4e6", "wire": "metal#cdd1d6", "rope": "plastic#9a9da1",
                                    "pad": "leather#79b2e8", "navy": "fabric#1c2a4a", "green": "gloss#22a447",
                                    "black": "plastic#1b1c1e", "strap": "fabric#6aa6e2"})
YR = 2075                                    # roof frame centre height
# --- back posts on a floor rail with castors
d.caster("castor", [60, 0, 45], 90, copies=[[1880, 0, 0]])
d.box("floor-rail", [0, 112, 10, 2000, 160, 80], "frame", r=3)
for x in (25, 1975):
    d.bar(f"post-{x}", [x, 112, 45], [x, 2100, 45], [50, 50], "frame", r=3)
# --- roof: frame, middle bars, wire mesh, label strip on the front edge
d.box("roof-back", [0, YR - 25, 20, 2000, YR + 25, 70], "frame", r=3)
d.box("roof-front", [0, YR - 25, 1100, 2000, YR + 25, 1150], "frame", r=3)
d.box("roof-side", [0, YR - 25, 70, 50, YR + 25, 1100], "frame", r=3, mirror="x")
d.box("roof-mid", [975, YR - 22, 70, 1025, YR + 22, 1100], "frame", r=3)
mesh(d, "roof", 50, 1950, 70, 1100, YR - 5, 100, 4, "wire")
d.decal("roof-label", [330, YR, 1150.6], [260, 26], "front", "plastic#2a2f3a")
# --- diagonal braces from the posts to the roof sides
for x in (25, 1975):
    d.bar(f"brace-{x}", [x, 1450, 45], [x, YR - 25, 650], [40, 30], "frame", r=3)
d.bar("brace-mid", [1000, 1700, 45], [1000, YR - 25, 420], [36, 30], "frame", r=3)
d.bar("cross-mid", [25, 1700, 45], [1975, 1700, 45], [36, 30], "frame", r=3)
# --- mesh back panel on the right half (upper part)
X0, X1, Y0, Y1 = 1040, 1950, 980, YR - 30
d.bar("back-net-bottom", [X0, Y0, 45], [1975, Y0, 45], [36, 30], "frame", r=3)
d.bar("back-net-side", [X0, Y0, 45], [X0, Y1, 45], [36, 30], "frame", r=3)
vmesh(d, "back-net", X0 + 20, X1, Y0 + 20, Y1, 50, 100, 4, "wire")
# --- treatment table on castors: white frame, legs, stretchers, screw feet
TZ0, TZ1 = 360, 1040
d.caster("t-castor", [95, 0, TZ0 + 30], 95, copies=[[1810, 0, 0], [0, 0, TZ1 - TZ0 - 60], [1810, 0, TZ1 - TZ0 - 60]])
for x in (95, 1905):
    for z in (TZ0 + 30, TZ1 - 30):
        d.bar(f"leg-{x}-{z}", [x, 120, z], [x, 520, z], [50, 50], "frame", r=3)
d.box("t-frame", [60, 495, TZ0, 1940, 540, TZ0 + 40], "frame", r=3, copies=[[0, 0, TZ1 - TZ0 - 40]])
d.box("t-frame-end", [60, 495, TZ0 + 40, 120, 540, TZ1 - 40], "frame", r=3, copies=[[1820, 0, 0]])
d.box("t-stretch", [95, 175, TZ0 + 10, 1905, 215, TZ0 + 50], "frame", r=3, copies=[[0, 0, TZ1 - TZ0 - 60]])
d.box("t-stretch-end", [75, 175, TZ0 + 30, 115, 215, TZ1 - 30], "frame", r=3, copies=[[1810, 0, 0]])
d.box("t-rail", [300, 455, TZ1 + 5, 1500, 478, TZ1 + 22], "frame", r=6)
for x in (150, 1850):
    d.cyl(f"screw-{x}", [x, 30, TZ1 + 20], [x, 260, TZ1 + 20], 18, "chrome")
    d.cyl(f"screw-foot-{x}", [x, 0, TZ1 + 20], [x, 30, TZ1 + 20], 50, "black")
    d.cyl(f"screw-knob-{x}", [x - 45, 260, TZ1 + 20], [x + 45, 260, TZ1 + 20], 22, "black")
    d.box(f"screw-bracket-{x}", [x - 20, 230, TZ1 - 30, x + 20, 280, TZ1 + 35], "frame", r=3)
# --- light-blue 3-section padded top, face slot in the right section
d.box("pad-a", [62, 540, TZ0 + 2, 700, 600, TZ1 - 2], "pad", r=20, puff=6)
d.box("pad-b", [706, 540, TZ0 + 2, 1300, 600, TZ1 - 2], "pad", r=20, puff=6)
d.slab("pad-c", "top", rpoly([(1306, TZ0 + 2), (1938, TZ0 + 2), (1938, TZ1 - 2), (1306, TZ1 - 2)], 20) + " " +
       rpoly([(1640, 640), (1860, 640), (1860, 740), (1640, 740)], 30), [540, 600], "pad", r=16)
# --- two wide straps across the table, hanging down the front edge
for x in (640, 1360):
    path = [[x, 601, TZ0 + 10], [x, 605, 700], [x, 602, TZ1 + 2], [x, 570, TZ1 + 16], [x, 420, TZ1 + 20]]
    d.strap(f"strap-edge-{x}", path, [150, 3], "navy", bend=25, soft=True)
    d.strap(f"strap-{x}", [[p[0], p[1] + 2, p[2] + (2 if i >= 3 else 0)] for i, p in enumerate(path)], [124, 3], "strap", bend=25, soft=True)
# --- pulleys, ropes, green D-handles, navy slings
for x, z in ((600, 640), (1000, 700), (1350, 760)):
    d.box(f"pulley-br-{x}", [x - 20, YR - 70, z - 8, x + 20, YR - 25, z + 8], "frame", r=3)
    d.wheel(f"pulley-{x}", [x, YR - 80, z], 70, "plastic#f2f2f0", d2=22)
def handle(id, x, z, ytop, yb):
    d.cyl(f"{id}-rope", [x, ytop, z], [x, yb + 95, z], 6, "rope", soft=True)
    d.tube(f"{id}-d", [[x, yb + 95, z], [x, yb + 60, z - 45], [x, yb, z - 45], [x, yb, z + 45], [x, yb + 60, z + 45], [x, yb + 95, z]],
           14, "green", bend=18)
    d.cyl(f"{id}-grip", [x, yb, z - 45], [x, yb, z + 45], 26, "green")
handle("h1", 565, 640, YR - 115, 1000)
handle("h2", 1035, 700, YR - 115, 780)
d.cyl("h2-rope-low", [1035, 780, 700], [1035, 605, 700], 6, "rope", soft=True)
d.cyl("rope-up", [635, YR - 115, 640], [635, 600, 640], 6, "rope", soft=True)
for x, z in ((1300, 760), (1500, 820)):
    d.cyl(f"sling-rope-{x}", [x, YR - 30, z], [x, 1420, z], 6, "rope", soft=True)
    d.tube(f"sling-hook-{x}", [[x, 1420, z], [x + 10, 1400, z], [x, 1385, z]], 5, "chrome", bend=5)
    d.loft(f"sling-{x}", [sec(1060, 70, 60, 28, x, z), sec(1110, 120, 90, 40, x, z), sec(1300, 115, 80, 36, x, z),
                         sec(1385, 70, 40, 18, x, z)], "navy", dome="start", domeH=30)
d.save()
