# XY-78 electric lifting commode chair: white base + column with actuator, white seat ring, navy sling back,
# blue armrests, chrome front legs and footrests — other-1
from o_lib import *
W, DP, H = 790, 1040, 1190
d = D("xy-78", [W, DP, H], {
    "white": "plastic#f1f1ee", "chrome": "chrome", "blk": "plastic#1d1e21", "navy": "fabric#2a4f9e",
    "pad": "leather#4f78c4", "plate": "metal#b9bec4"})
# base: white rectangular steel frame on 4 castors
BY0, BY1 = 118, 160
for x in (60, W - 60):
    d.bar(f"rail{x}", [x, (BY0 + BY1) / 2, 50], [x, (BY0 + BY1) / 2, 910], [56, BY1 - BY0], "white", r=6)
for z in (50, 900):
    d.bar(f"cross{z}", [32, (BY0 + BY1) / 2, z], [W - 32, (BY0 + BY1) / 2, z], [56, BY1 - BY0], "white", r=6)
for x in (60, W - 60):
    for z in (80, 870):
        caster(d, f"castor{x}-{z}", [x, 0, z], 100, "plastic#8a8f96")
# lifting column at the rear right (viewer's left) with the black actuator and control boxes
CX, CZ = 92, 130
d.bar("column", [CX, BY1 - 5, CZ], [CX, 1010, CZ], [62, 62], "white", r=5)
d.box("col-cap", [CX - 33, 1005, CZ - 33, CX + 33, 1018, CZ + 33], "white", r=4)
d.box("col-foot", [CX - 50, BY1 - 2, CZ - 50, CX + 50, BY1 + 8, CZ + 50], "metal#c9ccd0", r=3)
d.cyl("act-body", [CX - 56, 310, CZ], [CX - 56, 610, CZ], 48, "blk")
d.cyl("act-rod", [CX - 56, 610, CZ], [CX - 56, 830, CZ], 24, "metal#9da2a8")
d.box("act-motor", [CX - 86, 250, CZ - 30, CX - 26, 320, CZ + 40], "blk", r=6)
d.box("ctrl-box", [CX - 88, 330, CZ + 40, CX - 30, 380, CZ + 150], "blk", r=6)
# black control box (photo: rounded pedal-like box) on the left base rail, in front of the column
d.loft("battery", [sec(BY1, 100, 150, 20, 70, 760), sec(BY1 + 45, 100, 150, 20, 70, 760), sec(BY1 + 62, 84, 120, 18, 70, 770)], "blk")
# seat carriage: white side arm from the column, white seat frame, white seat ring with the commode opening
SY = 520
d.bar("carriage", [CX, SY - 20, CZ], [CX, SY - 20, 760], [50, 40], "white", r=5)
d.bar("carriage-x", [CX, SY - 20, CZ + 120], [W - 140, SY - 20, CZ + 120], [44, 36], "white", r=5)
d.bar("seat-rail", [W - 140, SY - 20, CZ + 120], [W - 140, SY - 20, 760], [44, 36], "white", r=5)
d.bar("seat-front", [CX, SY - 20, 760], [W - 140, SY - 20, 760], [44, 36], "white", r=5)
seat = rr(150, 300, 650, 780, 40) + " " + f"M 400 470 A 80 105 0 1 0 400.1 470 Z"
d.slab("seat", "top", rr(150, 300, 650, 780, 40) + " " + "M 335 520 Q 335 450 400 450 Q 465 450 465 520 L 465 640 Q 465 700 400 700 Q 335 700 335 640 Z",
       [SY, SY + 34], "white", r=8)
# backrest: white tube frame with a rounded top, navy sling with a pocket
BZ = 300
d.tube("back-frame", [[190, SY + 10, BZ], [190, 1100, BZ - 15], [230, H - 15, BZ - 20], [570, H - 15, BZ - 20],
                      [610, 1100, BZ - 15], [610, SY + 10, BZ]], 26, "white", bend=60)
# sling hangs from the top bar down to ~240 above the seat; the pocket's top edge slants (photo)
d.slab("sling", "front", poly([(205, 790), (595, 790), (595, 960), (560, H - 30), (285, H - 30), (205, 1010)]), [BZ - 22, BZ - 12], "navy", r=3)
d.slab("pocket", "front", poly([(208, 790), (592, 790), (592, 975), (208, 940)]), [BZ - 12, BZ - 2], "navy", r=3)
# armrests: blue pads on white posts with chrome struts
for i, x in enumerate((205, 595)):
    # (photo: the pad pivots on the backrest frame and rests on one chrome strut from the seat side — no post)
    xa = x - 40 if i == 0 else x + 40
    d.box(f"arm{i}", [xa - 35, 722, 320, xa + 35, 760, 700], "pad", r=14, puff=3)
    d.cyl(f"arm-pivot{i}", [x - 13 if i == 0 else x + 13, 740, BZ - 8], [xa, 740, BZ - 8], 22, "white")
    d.box(f"arm-bracket{i}", [xa - 12, 726, BZ - 18, xa + 12, 752, 340], "white", r=5)
    d.cyl(f"arm-strut{i}", [xa, SY + 20, 400], [xa, 724, 540], 18, "chrome")
# chrome front legs bent down to the base front corners, black lock knobs
for i, x in enumerate((170, 630)):
    d.tube(f"leg{i}", [[x, SY - 20, 740], [x, SY - 60, 840], [x + (60 if i == 0 else -60) * 0 , BY1 + 10, 870]], 28, "chrome", bend=80)
    d.cyl(f"knob{i}", [x + (-1 if i == 0 else 1) * 14, 330, 860], [x + (-1 if i == 0 else 1) * 40, 330, 860], 26, "blk")
    # swing-away footrest hanger and footplate
    d.tube(f"hanger{i}", [[x, SY - 40, 800], [x, 260, 930], [x, 140, 990]], 22, "chrome", bend=60)
    xp0, xp1 = (x, x + 170) if i == 0 else (x - 170, x)
    d.box(f"footplate{i}", [xp0, 128, 900, xp1, 142, 1035], "plate", r=4)
# hand controller hanging from the backrest on its cable to the box on the base
d.box("pendant", [310, 700, BZ + 10, 352, 860, BZ + 34], "blk", r=10)
d.tube("pendant-cord", [[331, 700, BZ + 22], [335, 520, BZ + 80], [200, 300, 760], [90, 222, 760]], 7, "blk", bend=120, soft=True)
d.tube("cable", [[CX - 60, 330, CZ + 150], [60, 180, 400], [160, 20, 760], [110, 200, 760]], 7, "blk", bend=150, soft=True)
d.save()
