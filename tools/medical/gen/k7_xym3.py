"""xym-3 Fingers Strength Exerciser: white H-frame table, light wood top, champagne U frame with 4 finger stations,
4 aqua weight bottles hanging under the top (the photo shows 4 stations, not 5)."""
from k7lib import *

d = D("xym-3", [800, 600, 1110], {
    "white": "plastic#f1f2ef", "top": "plastic#ecd5bd", "bronze": "metal#c9b48f", "black": "plastic#1a1b1d",
    "rod": "metal#a9adb2", "aqua": "acrylic#8fd3d6c8", "rubber": "rubber#1c1d1f"})
TY = 760          # underside of the table top
# --- white H stand: two side frames (foot tube + leg + top rail), low stretcher, under-top rail
for nm, x in (("l", 165), ("r", 635)):
    d.cyl(f"foot-{nm}", [x, 26, 40], [x, 26, 560], 40, "white")
    d.cyl(f"cap-{nm}", [x, 26, 14], [x, 26, 42], 44, "rubber", copies=[[0, 0, 544]])
    d.cyl(f"pad-{nm}", [x, 0, 28], [x, 8, 28], 36, "rubber", copies=[[0, 0, 544]])
    d.cyl(f"leg-{nm}", [x, 40, 300], [x, TY - 30, 300], 40, "white")
    d.bar(f"rail-{nm}", [x, TY - 15, 70], [x, TY - 15, 530], [36, 28], "white", r=6)
    d.cyl(f"leg-shoe-{nm}", [x, 26, 300], [x, 70, 300], 50, "white")
d.cyl("stretcher", [165, 180, 300], [635, 180, 300], 30, "white")
d.bar("under-rail", [165, TY - 18, 300], [635, TY - 18, 300], [30, 24], "white", r=5)
d.decal("stretcher-clip", [400, 180, 316], [30, 10], "black", face="front", soft=True)
# --- light wood table top
d.box("top", [0, TY, 0, 800, TY + 26, 600], "top", r=8)
# --- champagne inverted-U frame on the top near the back, 4 finger stations hanging from its top bar
FY = TY + 26
Z = 160
d.tube("u-frame", [[200, FY, Z], [200, 1085, Z], [600, 1085, Z], [600, FY, Z]], 26, "bronze", bend=55)
d.cyl("u-flange", [200, FY, Z], [200, FY + 8, Z], 48, "bronze", copies=[[400, 0, 0]])
for k, x in enumerate((290, 370, 450, 530)):
    d.box(f"clamp-{k}", [x - 16, 1068, Z - 18, x + 16, 1102, Z + 18], "black", r=5)
    d.lathe(f"clamp-knob-{k}", [x, 1085, Z + 18], [[0, 0], [6, 0], [6, 8], [11, 10], [11, 20], [0, 22]], "black", axis="z")
    d.cyl(f"rod-{k}", [x, 1068, Z], [x, FY + 64, Z + 30], 9, "rod")
    # black finger loop (photo: a low arch just above the top, hanging from the rod)
    d.tube(f"loop-{k}", [[x - 34, FY + 18, Z + 44], [x - 10, FY + 62, Z + 32], [x + 10, FY + 62, Z + 32],
                         [x + 34, FY + 18, Z + 44]], 14, "black", bend=16)
    # under the top: a chrome rod and a dark cord side by side, a chrome connector, an aqua weight bottle (neck up)
    d.cyl(f"cord-{k}", [x - 5, TY, Z + 10], [x - 5, 512, Z + 10], 7, "rod")
    d.cyl(f"cord2-{k}", [x + 5, TY, Z + 10], [x + 5, 512, Z + 10], 5, "plastic#3a3d42")
    d.cyl(f"conn-{k}", [x, 498, Z + 10], [x, 530, Z + 10], 16, "chrome")
    d.lathe(f"bottle-{k}", [x, 372, Z + 10], [[0, 0], [20, 0], [25, 6], [25, 96], [20, 110], [10, 116], [10, 124], [0, 124]], "aqua")
    d.cyl(f"bottle-cap-{k}", [x, 492, Z + 10], [x, 504, Z + 10], 24, "plastic#d9dde0")
d.save()
