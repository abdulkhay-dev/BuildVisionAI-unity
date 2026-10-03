"""XY-MCB-I deluxe smart peg board: champagne-gold aluminium board with a light wood top, 8x8 conical holes (some lit
violet), black glass control strip on the right, coloured pegs; behind it a 27" all-in-one monitor (thin black bezel,
silver chin, silver stand) showing the peg game (screen crop: a skewed photo, masked)."""
from k9lib import *
d = K("xy-mcb-i-deluxe", [680, 600, 520], {
    "alu": "metal#cbbd9f", "wood": "wood#dcb47e", "hole": "wood#b88c58", "hole2": "wood#70502c", "lit": "gloss#8d6bff",
    "glass": "gloss#0a0a0b", "black": "plastic#141517", "silver": "metal#d3d5d8", "uiblue": "plastic#1f67b3"})
CX = 340
# --- board
BX0, BX1, BZ0, BZ1, BH = 40, 640, 180, 595, 60
OUT = rpoly([(BX0, BZ0), (BX1, BZ0), (BX1, BZ1), (BX0, BZ1)], 45)
INS = rpoly([(BX0 + 10, BZ0 + 10), (BX1 - 10, BZ0 + 10), (BX1 - 10, BZ1 - 10), (BX0 + 10, BZ1 - 10)], 34)
# (review 2026-10-03) real cup holes: the gold body is a lower slab plus a rim ring; the wood insert is 16 mm thick
# with the holes cut through, over a darker wood floor (some floors lit violet)
d.slab("board", "top", OUT, [4, BH - 16], "alu", r=12)
d.slab("board-rim", "top", OUT + " " + INS, [20, BH - 2], "alu", r=8)
d.slab("board-foot", "top", rpoly([(BX0 + 15, BZ0 + 15), (BX1 - 15, BZ0 + 15), (BX1 - 15, BZ1 - 15), (BX0 + 15, BZ1 - 15)], 35),
       [0, 6], "black", r=2)
WR0, WR1 = 500, 470            # wood's right edge at the back / front (slanted boundary to the glass)
WOOD = rpoly([(BX0 + 10, BZ0 + 10), (WR0, BZ0 + 10), (WR1, BZ1 - 10), (BX0 + 10, BZ1 - 10)], 34)
d.slab("floor", "top", WOOD, [BH - 12, BH - 9], "hole", r=0.5)
d.slab("glass", "top", rpoly([(WR0, BZ0 + 10), (BX1 - 10, BZ0 + 10), (BX1 - 10, BZ1 - 10), (WR1, BZ1 - 10)], 34), [BH - 6, BH],
       "glass", r=1)
d.decal("logo", [WR0 + 30, BH + 0.6, BZ0 + 40], [20, 20], "top", "gloss#2a5fb0")
d.decal("logo-t", [WR0 + 80, BH + 0.6, BZ0 + 40], [60, 12], "top", "gloss#2a5fb0")
# 8x8 holes
lit = {(1, 3), (4, 3), (2, 6), (3, 6), (5, 5), (1, 5)}
outer, inner, litp = [], [], []
for r_ in range(8):
    for c in range(8):
        x, z = 82 + c * 50, 220 + r_ * 48
        if x > WR1 - 20 + (WR0 - WR1) * (1 - (z - BZ0) / (BZ1 - BZ0)):
            continue
        outer.append(circle(x, z, 16))
        (litp if (c, r_) in lit else inner).append(circle(x, z, 15))
d.slab("wood", "top", WOOD + " " + " ".join(outer), [BH - 10, BH], "wood", r=1)
d.slab("holes-lit", "top", " ".join(litp), [BH - 9.5, BH - 7], "lit", r=0.2)
# pegs (red, yellow, blue) standing in holes
for k, (c, r_, m) in enumerate([(0, 4, "gloss#e0352b"), (3, 1, "gloss#f2d43a"), (2, 5, "gloss#f2d43a"), (6, 3, "gloss#e0352b"),
                                (7, 2, "gloss#2f86d0")]):
    x, z = 82 + c * 50, 220 + r_ * 48
    d.cyl(f"peg-{k}", [x, BH - 15, z], [x, BH + 120, z], 25, m)
    d.decal(f"peg-top-{k}", [x, BH + 120.5, z], [10, 10], "top", "plastic#d8d8d8")
# right side: vents and the green power LED
d.box("vent", [BX1 - 1, 18, 470, BX1 + 0.6, 21, 520], "black", r=0.5, repeat=rep(5, [0, 6, 0]))
d.sphere("led", [BX1 - 2, 30, 545], 9, "gloss#36d06a")
# --- monitor: silver stand, black body tilted back, silver chin, the screen crop masked
MX = 340
d.box("stand-base", [MX - 150, 0, 15, MX + 150, 10, 175], "silver", r=8)
d.bar("stand-neck", [MX, 10, 110], [MX, 260, 70], [230, 12], "silver", r=4)
PR = rot("x", -8, [MX, 120, 130])
SW, SH, SB = 590, 332, 205               # picture area (inside the thin bezel): width, height, bottom y
x0, x1 = MX - SW / 2, MX + SW / 2
# (review 2026-10-03) the leaflet crop was skewed: it is now straightened (reference/<id>_screen.jpg and the albedo,
# 1280 x 720, the blue game area only) and laid over the whole picture area; thin black bezel, silver chin below
d.box("mon", [x0 - 14, SB - 52, 95, x1 + 14, SB + SH + 14, 128], "black", r=8, rot=PR)
d.box("mon-chin", [x0 - 14, SB - 52, 126, x1 + 14, SB - 12, 134], "silver", r=5, rot=PR)
d.box("mon-grille", [MX - 280, SB - 44, 133.6, MX + 280, SB - 20, 134.4], "plastic#c4c7cb", r=0.3, soft=True, rot=PR)
d.box("mon-bo", [x1 - 13, SB - 45, 133.8, x1 + 1, SB - 35, 134.6], "plastic#8e9297", r=0.3, soft=True, rot=PR)
d.screen("screen", [x0, SB, 127, x1, SB + SH, 130], "black", print="med_xy-mcb-i-deluxe_screen", bezel=0.2, r=1, rot=PR)
d.save()
