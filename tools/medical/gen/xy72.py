from pfx_lib import *
d = D("xy-72", [2100, 1200, 1000], {
  "pad": "leather#8fb8e0", "frame": "plastic#f1f2f4", "cap": "plastic#9aa0a8", "act": "metal#a9aeb5",
  "bolt": "metal#8d939a", "emb": "plastic#c9cdd3"})
T = 540   # underside of the mattress = top of the top frame
F = 480   # bottom of the top frame
# --- mattress: foot section flat, head section raised 30 deg about the hinge
d.box("mat-foot", [712, T, 0, 2100, T + 90, 1200], "pad", r=30, puff=6)
hr = rot("z", -30, [706, T, 600])
d.box("mat-head", [0, T, 0, 700, T + 90, 1200], "pad", r=30, puff=6, rot=hr)
d.box("board-head", [20, T - 16, 40, 690, T, 1160], "frame", r=4, rot=hr)
# --- top frame (horizontal), rect tube 60 high
d.bar("top-rail", [20, F + 30, 60], [2080, F + 30, 60], [40, 60], "frame", r=6, copies=[[0, 0, 1080]])
d.bar("top-end", [40, F + 30, 60], [40, F + 30, 1140], [40, 60], "frame", r=6, copies=[[2020, 0, 0]])
d.bar("top-ladder", [170, F + 30, 60], [170, F + 30, 1140], [40, 40], "frame", r=6)
d.bar("top-hinge", [715, F + 30, 60], [715, F + 30, 1140], [40, 60], "frame", r=6)
d.bar("top-mid", [1300, F + 30, 60], [1300, F + 30, 1140], [40, 60], "frame", r=6)
d.cyl("head-strut", [300, F + 40, 600], [760, F + 10, 600], 30, "act")
# --- base frame
B0, B1 = 170, 230
d.bar("base-rail", [200, 200, 220], [1900, 200, 220], [60, 60], "frame", r=6, copies=[[0, 0, 760]])
d.bar("base-end", [230, 200, 190], [230, 200, 1010], [60, 60], "frame", r=6, copies=[[1640, 0, 0]])
d.bar("leg-arm", [110, 200, 220], [200, 200, 220], [60, 60], "frame", r=6,
      copies=[[0, 0, 760], [1790, 0, 0], [1790, 0, 760]])
d.box("leg", [70, 30, 185, 140, 240, 255], "frame", r=6, copies=[[0, 0, 760], [1890, 0, 0], [1890, 0, 760]])
d.box("leg-cap", [66, 12, 181, 144, 34, 259], "cap", r=5, copies=[[0, 0, 760], [1890, 0, 0], [1890, 0, 760]])
d.box("leg-top", [66, 236, 181, 144, 256, 259], "cap", r=4, copies=[[0, 0, 760], [1890, 0, 0], [1890, 0, 760]])
d.cyl("leg-link", [140, 120, 270], [320, 170, 270], 14, "chrome", copies=[[0, 0, 660]])
d.cyl("leg-link-f", [1960, 120, 270], [1780, 170, 270], 14, "chrome", copies=[[0, 0, 660]])
d.add("caster", "caster", "rubber#a3a8ae", at=[330, 0, 220], d=75, copies=[[0, 0, 760], [1440, 0, 0], [1440, 0, 760]])
d.box("caster-plate", [300, 100, 190, 360, 170, 250], "frame", r=6, copies=[[0, 0, 760], [1440, 0, 0], [1440, 0, 760]])
# --- lift: two lever plates per side, same orientation (vertical part toward the foot)
def lever(x0, xv, x1):
    return (f"M {x0} {B1} L {x1} {B1} L {x1} {F} L {xv} {F} "
            f"Q {xv} {B1 + 50} {x0} {B1 + 40} Z")
for nm, (x0, xv, x1) in (("xiangyu", (680, 1000, 1120)), ("medical", (1300, 1700, 1820))):
    d.slab("lever-" + nm, "front", lever(x0, xv, x1), [1012, 1024], "frame", r=3, copies=[[0, 0, -848]])
    d.cyl("bolt-top-" + nm, [x1 - 45, F - 30, 1022], [x1 - 45, F - 30, 1030], 26, "bolt", soft=True)
    d.cyl("bolt-bot-" + nm, [x1 - 45, B1 + 35, 1022], [x1 - 45, B1 + 35, 1030], 26, "bolt", soft=True)
    d.cyl("lever-tube-" + nm, [x1 - 45, B1 + 35, 176], [x1 - 45, B1 + 35, 1024], 40, "frame")
    d.bar("sub-rail-" + nm, [x0 + 250, F - 20, 180], [x1, F - 20, 180], [40, 40], "frame", r=5, copies=[[0, 0, 840]])
# letters (embossed white on white): rows of small shaded blocks
d.decal("txt-xiangyu", [790, 300, 1025], [16, 26], "front", "emb", soft=True, repeat=rep(8, [26, 0, 0]))
d.decal("txt-medical", [1430, 300, 1025], [18, 26], "front", "emb", soft=True, repeat=rep(7, [30, 0, 0]))
d.cyl("actuator", [1060, 420, 560], [1640, 330, 560], 50, "act")
d.cyl("actuator-rod", [1000, 430, 560], [1080, 418, 560], 26, "chrome")
d.bar("act-cross", [1000, 430, 180], [1000, 430, 1020], [40, 40], "frame", r=5)
# motor housing at the foot end, front
d.box("motor", [1830, 250, 820, 1990, 360, 980], "frame", r=22)
d.box("motor-end", [1990, 255, 830, 2010, 355, 970], "cap", r=8)
d.tube("motor-cable", [[1900, 360, 980], [1950, 420, 1060], [2000, 470, 1100]], 8, "plastic#3a3f45", bend=40, soft=True)
# foot switch bar across the foot end on two grey Z levers
d.tube("foot-lever", [[1870, 215, 300], [1960, 215, 300], [2010, 110, 300], [2060, 110, 300]], 22, "cap", bend=25,
       copies=[[0, 0, 600]])
d.cyl("foot-bar", [2060, 110, 280], [2060, 110, 920], 24, "chrome")
d.save()
