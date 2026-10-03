from k4lib import *
# size: the printed 70 x 49 x 54 cm repeats XY-44's figures; the set laid out as in the photo needs ~800 x 720 x 420
d = K("xy-45", [800, 720, 420], {"cream": "plastic#f1eadb", "edge": "gloss#d2722c", "wood": "wood#e6a457", "rod": "wood#d89048",
                                 "knob": "plastic#1d1e21", "brass": "metal#c9a248", "foot": "rubber#1b1c1e"})
def tablet(id, x0, z0, x1, z1, y0):
    d.box(id, [x0, y0, z0, x1, y0 + 16, z1], "edge", r=3)
    d.box(id + "-top", [x0 + 3, y0 + 15, z0 + 3, x1 - 3, y0 + 17, z1 - 3], "cream", r=1)
# --- ladder shelf: base board, two orange-wood uprights, 3 rods with clothes-pegs
tablet("shelf-base", 20, 20, 400, 165, 0)
d.box("upright", [45, 17, 55, 67, 420, 135], "wood", r=3, copies=[[288, 0, 0]])
for i, y in enumerate((150, 255, 360)):
    d.cyl(f"rod{i}", [67, y, 95], [333, y, 95], 18, "rod")
PEGS = {2: [(110, "acrylic#9fe3c6d0"), (175, "acrylic#a8e8cfd0"), (225, "acrylic#9fd8e6d0"), (295, "acrylic#f2a0b8d0")],
        1: [(100, "acrylic#f2a0b8d0"), (170, "acrylic#6f9fe8d0"), (235, "acrylic#6f9fe8d0"), (300, "acrylic#9fe3c6d0")],
        0: [(110, "acrylic#f4f4f4d0"), (200, "acrylic#f4f4f4d0"), (290, "acrylic#eef2f6d0")]}
ys = (150, 255, 360)
for r, pegs in PEGS.items():
    for j, (x, mat) in enumerate(pegs):
        y = ys[r]
        d.box(f"peg{r}{j}", [x - 7, y - 12, 96, x + 7, y + 42, 110], mat, r=3, rot=rot("x", 12, [x, y, 95]))
        d.box(f"pegb{r}{j}", [x - 7, y - 12, 80, x + 7, y + 42, 94], mat, r=3, rot=rot("x", -12, [x, y, 95]))
# --- knob tablet on small black feet, 4 rounded-triangle knobs on chrome stems (diamond)
d.box("kt-foot", [430, 0, 40, 450, 12, 60], "foot", r=3, copies=[[310, 0, 0], [0, 0, 260], [310, 0, 260]])
tablet("kt", 420, 30, 780, 330, 12)
for i, (x, z) in enumerate(((600, 85), (470, 185), (730, 185), (600, 280))):
    d.cyl(f"kt-stem{i}", [x, 29, z], [x, 72, z], 14, "chrome")
    d.slab(f"kt-knob{i}", "top", rpoly([(x, z - 42), (x + 40, z + 25), (x - 40, z + 25)], 14), [72, 96], "knob", r=6)
    d.decal(f"kt-dot{i}", [x, 96.5, z], [9, 9], "top", "plastic#d8d8d8")
# --- fittings tablet: tap, recessed handle, chain, hasp, bolt, switch plate, small fittings (places read off the photo)
X = 60                                    # the tablet sits front-centre/right in the photo
tablet("ft", 140 + X, 375, 640 + X, 700, 0)
d.box("ft-slot", [170 + X, 15, 600, 240 + X, 17.5, 640], "plastic#6a3a18", r=6)
d.box("ft-slot-in", [180 + X, 16, 608, 230 + X, 17.8, 632], "plastic#3a1e0c", r=4)
tx, tz = 340 + X, 430                     # chrome tap at the back, left of centre
d.cyl("tap-base", [tx, 17, tz], [tx, 30, tz], 46, "chrome")
d.cyl("tap-body", [tx, 30, tz], [tx, 85, tz], 28, "chrome")
d.cyl("tap-spout", [tx, 75, tz], [tx + 60, 70, tz], 16, "chrome")
d.cyl("tap-lever", [tx, 88, tz], [tx - 45, 102, tz], 10, "chrome")
d.sphere("tap-top", [tx, 88, tz], 30, "chrome")
d.tube("chain", [[x + X, 21, z] for x, z in ((265, 590), (295, 575), (325, 595), (355, 578), (385, 598), (405, 585))], 7, "brass", bend=15)
d.tube("chain-b", [[x + X, 23, z] for x, z in ((265, 582), (295, 597), (325, 577), (355, 596), (385, 576))], 6, "brass", bend=15)
d.box("hasp", [405 + X, 17, 512, 435 + X, 23, 535], "brass", r=2)
d.cyl("hasp-pin", [415 + X, 23, 524], [415 + X, 36, 524], 8, "brass")
d.box("bolt-plate", [475 + X, 17, 408, 535 + X, 20, 420], "chrome", r=2)
d.cyl("bolt", [462 + X, 26, 414], [548 + X, 26, 414], 7, "chrome")
d.sphere("bolt-end", [462 + X, 26, 414], 13, "chrome", copies=[[86, 0, 0]])
d.box("switch", [425 + X, 17, 585, 520 + X, 21, 650], "plastic#f6f6f4", r=3)
d.box("switch-key", [455 + X, 21, 600, 485 + X, 34, 625], "plastic#e8e8e6", r=5)
d.box("zip", [495 + X, 17, 470, 560 + X, 23, 498], "knob", r=2)
d.decal("zip-teeth", [527 + X, 23.5, 484], [56, 5], "top", "chrome")
d.box("blue", [548 + X, 17, 528, 592 + X, 26, 556], "gloss#2a62c8", r=3)
d.box("blue-b", [535 + X, 17, 532, 550 + X, 25, 552], "knob", r=2)
d.tube("hook", [[220 + X, 20, 470], [260 + X, 20, 470], [265 + X, 20, 485], [255 + X, 20, 492]], 6, "brass", bend=6)
d.tube("hook-b", [[205 + X, 20, 520], [245 + X, 20, 520]], 6, "brass")
d.box("lock", [318 + X, 17, 628, 345 + X, 30, 652], "brass", r=4)
d.save()
