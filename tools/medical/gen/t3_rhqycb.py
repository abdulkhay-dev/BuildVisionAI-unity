"""RH-QYC-B Rehamaster multifunctional traction table (table-3 batch). Head end at x = 0 with the traction unit
(LCD box on a cantilever arm down to the base), 4-section blue top on a white frame, trapezoid 'Rehamaster' shroud,
two leaning white lift columns, white base frame on 4 castors, black grab handles at the foot end, foot pedal."""
import math
from lib import *
from t3_alclib import FONT
FONT.update({
    "R": [[(0, 0), (0, 1), (0.75, 1), (1, 0.85), (1, 0.62), (0.75, 0.5), (0, 0.5)], [(0.45, 0.5), (1, 0)]],
    "E": [[(1, 1), (0, 1), (0, 0), (1, 0)], [(0, 0.52), (0.8, 0.52)]],
    "H": [[(0, 0), (0, 1)], [(1, 0), (1, 1)], [(0, 0.5), (1, 0.5)]],
    "M": [[(0, 0), (0, 1), (0.5, 0.45), (1, 1), (1, 0)]],
    "S": [[(1, 0.85), (0.8, 1), (0.2, 1), (0, 0.8), (0.2, 0.55), (0.8, 0.45), (1, 0.2), (0.8, 0), (0.2, 0), (0, 0.15)]],
    "T": [[(0, 1), (1, 1)], [(0.5, 1), (0.5, 0)]],
})
from t3_alclib import lettering
W, D_, H = 2032, 710, 1020
d = D("rh-qyc-b", [W, D_, H], {
    "pad": "leather#2fa3d6", "white": "plastic#f3f4f5", "frame": "plastic#e9ebee", "grey": "plastic#b9bec5",
    "black": "rubber#17181a", "blk": "plastic#1d1f22", "chrome": "chrome", "cast": "plastic#c9ccd0",
    "letter": "plastic#a7adb5", "pedal": "plastic#2a6fd0"})
cz = D_ / 2
T = 870          # top of the pads
# ---- 4-section blue top (the foot section split lengthwise), thin white/grey frame under it
for nm, (x0, x1) in (("head", (360, 1000)), ("lumbar", (1010, 1300)), ("thigh", (1310, 1560))):
    d.box("pad-" + nm, [x0, T - 62, 30, x1, T, D_ - 30], "pad", r=20, puff=3)
d.box("pad-foot-a", [1570, T - 62, 30, 1960, T, cz - 6], "pad", r=20, puff=3)
d.box("pad-foot-b", [1570, T - 62, cz + 6, 1960, T, D_ - 30], "pad", r=20, puff=3)
d.box("pad-board", [370, T - 76, 40, 1950, T - 60, D_ - 40], "grey", r=4)
d.bar("frame-rail", [350, 770, 50], [1960, 770, 50], [40, 50], "white", r=6, copies=[[0, 0, D_ - 100]])
d.bar("frame-end", [370, 770, 50], [370, 770, D_ - 50], [40, 50], "white", r=6, copies=[[1570, 0, 0]])
d.box("frame-plate", [520, 740, 70, 1880, 760, D_ - 70], "grey", r=3)
# controls on the front of the frame: handwheel, release levers, knob
d.add("handwheel", "wheel", "blk", at=[1320, 720, D_ - 18], d=110, d2=20, axis="z")
d.cyl("handwheel-hub", [1320, 720, D_ - 50], [1320, 720, D_ - 6], 26, "chrome")
d.box("lever", [1580, 690, D_ - 40, 1620, 790, D_ - 10], "blk", r=8, copies=[[60, 0, 0]])
d.cyl("knob", [1480, 690, D_ - 50], [1480, 690, D_ - 10], 40, "blk")
# ---- trapezoid shroud with the Rehamaster lettering
sh = "M 840 770 L 1650 770 L 1580 560 L 910 560 Z"
d.slab("shroud", "front", sh, [80, D_ - 80], "white", r=14)
# photo: "Rehamaster" in mixed case (capital R, lowercase rest): stroke glyphs, cap height = 1, x-height 0.6
LOW = {
    "R": (FONT["R"], 0.95),
    "e": ([[(0.05, 0.33), (0.7, 0.33), (0.7, 0.45), (0.55, 0.6), (0.2, 0.6), (0.05, 0.45), (0.05, 0.15), (0.2, 0),
            (0.6, 0), (0.7, 0.08)]], 0.8),
    "h": ([[(0, 0), (0, 1)], [(0, 0.42), (0.2, 0.6), (0.5, 0.6), (0.65, 0.45), (0.65, 0)]], 0.8),
    "a": ([[(0.1, 0.55), (0.25, 0.6), (0.5, 0.6), (0.65, 0.48), (0.65, 0)],
           [(0.65, 0.32), (0.2, 0.3), (0.03, 0.18), (0.1, 0.03), (0.3, 0), (0.5, 0.03), (0.65, 0.15)]], 0.8),
    "m": ([[(0, 0), (0, 0.6)], [(0, 0.45), (0.12, 0.6), (0.3, 0.6), (0.42, 0.45), (0.42, 0)],
           [(0.42, 0.45), (0.54, 0.6), (0.72, 0.6), (0.84, 0.45), (0.84, 0)]], 1.0),
    "s": ([[(0.62, 0.52), (0.5, 0.6), (0.15, 0.6), (0.03, 0.48), (0.12, 0.35), (0.5, 0.27), (0.63, 0.15), (0.52, 0),
            (0.15, 0), (0.02, 0.08)]], 0.75),
    "t": ([[(0.25, 0.95), (0.25, 0.1), (0.35, 0), (0.55, 0.02)], [(0.05, 0.6), (0.5, 0.6)]], 0.6),
    "r": ([[(0, 0), (0, 0.6)], [(0, 0.4), (0.15, 0.57), (0.35, 0.6), (0.5, 0.58)]], 0.6),
}
def script(text, cx, y0, z, hc=92, wu=76, stroke=13):
    tot = sum(LOW[c][1] for c in text) * wu
    x = cx - tot / 2; seen = {}
    for c in text:
        seen.setdefault(c, []).append(x); x += LOW[c][1] * wu
    for c, xs in seen.items():
        cp = [[xx - xs[0], 0, 0] for xx in xs[1:]] or None
        for k, line in enumerate(LOW[c][0]):
            w_ = 0.75 if c == "R" else 1.0
            d.tube(f"logo-{c}{'u' if c.isupper() else 'l'}{k}", [[xs[0] + u * wu * w_, y0 + v * hc, z] for u, v in line],
                   stroke, "letter", bend=3, soft=True, copies=cp)
script("Rehamaster", 1245, 610, D_ - 78)
d.cyl("shroud-bolt", [930, 590, D_ - 82], [930, 590, D_ - 76], 16, "blk", soft=True, copies=[[620, 0, 0]])
# ---- two white lift columns leaning outward, pivots, base frame on castors
d.bar("col-l", [960, 580, cz], [800, 170, cz], [420, 150], "white", r=24)
d.bar("col-r", [1530, 580, cz], [1690, 170, cz], [420, 150], "white", r=24)
d.cyl("pivot", [800, 190, 130], [800, 190, D_ - 130], 50, "grey", copies=[[890, 0, 0]])
d.bar("base-rail", [420, 120, cz], [1880, 120, cz], [90, 70], "white", r=10)
d.bar("base-end", [620, 110, 60], [620, 110, D_ - 60], [70, 60], "white", r=8, copies=[[1250, 0, 0]])
d.add("castor", "caster", "cast", at=[620, 0, 70], d=90, copies=[[1250, 0, 0], [0, 0, D_ - 140], [1250, 0, D_ - 140]])
# ---- head-end traction unit: white box with the LCD on its chamfered top, post with pulley, rope arm to the
# black cervical holder on the head pad; cantilever arm down to a motor box on the base
ub = "M 0 650 L 0 760 L 150 870 L 340 870 L 340 650 Z"
d.slab("unit", "front", ub, [180, 530], "white", r=18)
d.add("unit-lcd", "screen", "black", box=[0, 815, 205, 165, 821, 505], r=6, face="top", bezel=8,
      rot=rot("z", 36.3, [82, 815, cz]))
d.box("unit-post", [170, 870, cz - 30, 230, 1000, cz + 30], "white", r=10)
d.cyl("unit-pulley", [200, 985, cz - 32], [200, 985, cz + 32], 50, "grey")
d.cyl("rope-arm", [340, 800, cz], [700, 820, cz], 20, "chrome")
d.box("holder-plate", [460, T, cz - 120, 640, T + 10, cz + 120], "chrome", r=4)
d.box("holder-pad", [500, T + 10, cz - 110, 560, T + 120, cz - 50], "black", r=18, copies=[[0, 0, 160]])
d.tube("holder-strap", [[600, T + 10, cz - 120], [600, T + 150, cz - 110], [600, T + 150, cz + 110], [600, T + 10, cz + 120]],
       30, "black", bend=60)
d.bar("arm", [190, 660, cz], [370, 170, cz], [110, 140], "white", r=18)
d.box("motor-box", [330, 100, cz - 150, 520, 270, cz + 150], "white", r=14)
d.bar("motor-link", [520, 150, cz], [640, 130, cz], [70, 60], "white", r=8)
d.cyl("motor-knob", [450, 270, cz + 60], [450, 300, cz + 60], 40, "blk")
d.add("castor-head", "caster", "cast", at=[400, 0, cz + 110], d=75, copies=[[0, 0, -220]])
# leg holders on a chrome post off the arm
d.cyl("lh-post", [280, 400, cz], [280, 470, cz], 22, "chrome")
d.box("lh-pad", [235, 470, cz - 80, 330, 720, cz - 10], "black", r=24, copies=[[0, 0, 90]])
# ---- black curved grab handles at the foot end
for nm, z in (("a", 60), ("b", D_ - 60)):
    d.tube("grip-" + nm, [[1890, T - 40, z], [1930, T + 70, z], [1995, T + 85, z], [2018, T + 20, z]], 32, "black", bend=40)
    d.bar("grip-mount-" + nm, [1880, 790, z], [1890, T - 30, z], [30, 30], "chrome", r=4)
# ---- foot pedal on the floor with the coiled white cable
d.box("pedal", [760, 0, D_ - 210, 990, 55, D_ - 20], "white", r=14)
d.box("pedal-pad", [790, 50, D_ - 190, 865, 62, D_ - 40], "pedal", r=10, copies=[[100, 0, 0]])
d.coil("pedal-cord", [520, 120, cz + 130], [770, 30, D_ - 110], 18, 4, 26, "plastic#f4f4f4", soft=True)
d.save()
