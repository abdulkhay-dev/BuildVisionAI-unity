from pd1_lib import *
W, D_, H = 1800, 2100, 2000
d = K("square-combined-training-frame", [W, D_, H], {"pine": "wood#e2c8a2", "pine2": "wood#d8b88a", "knob": "gloss#2840b0",
      "grey": "metal#b9bcc0", "green": "gloss#2fa04a", "mat": "leather#7ccc3e", "strap": "fabric#f4f4f0"})
ZB, ZF = 300, 2100                     # frame from the back posts to the front posts (the climbing wall leans out behind)
P, HP = 80, 1880
# posts with round finials
for x in (0, W - P):
    for z in (ZB, ZF - P):
        d.box(f"post-{x}-{z}", [x, 0, z, x + P, HP, z + P], "pine", r=4)
        d.cyl(f"neck-{x}-{z}", [x + P / 2, HP, z + P / 2], [x + P / 2, HP + 40, z + P / 2], 40, "pine")
        d.sphere(f"fin-{x}-{z}", [x + P / 2, HP + 72, z + P / 2], 76, "pine")
# top beams; arched boards with 3 round holes on the front and the back; corner braces
for nm, z in (("f", ZF - 70), ("b", ZB + 10)):
    d.box("beam-" + nm, [P, 1700, z, W - P, 1800, z + 60], "pine", r=4)
    out = f"M {P} 1795 L {W - P} 1795 L {W - P} 1830 Q {W / 2} 1950 {P} 1830 Z"
    for hx in (W / 2 - 300, W / 2, W / 2 + 300):
        out += " " + circle(hx, 1845, 22)
    d.slab("arch-" + nm, "front", out, [z + 15, z + 45], "pine", r=3)
    d.slab("brace-" + nm, "front", poly([(P, 1700), (P + 150, 1700), (P, 1550)]), [z + 10, z + 50], "pine", r=3, mirror="x")
d.box("beam-s", [0, 1720, ZB + P, P, 1800, ZF - P], "pine", r=4, mirror="x")
# hanging beam across the middle with a row of blue knobs
ZM = (ZB + ZF) / 2
d.box("hang", [P, 1660, ZM - 40, W - P, 1740, ZM + 40], "pine2", r=4)
d.sphere("hook", [460, 1640, ZM], 42, "knob", repeat=rep(10, [98, 0, 0]))
# platform swing on white printed straps (a white tube frame round the platform), two foam cylinders on it
SX0, SX1, SZ0, SZ1 = 580, 1220, ZM - 200, ZM + 200
for i, x in enumerate((SX0 - 10, SX1 - 30)):
    d.box(f"strap{i}", [x, 450, ZM - 2, x + 40, 1660, ZM + 2], "strap", soft=True)
    # the printed lettering: small dark-grey blocks every ~75 mm on both faces (thin boxes: decals go pale)
    d.box(f"print{i}", [x + 13, 520, ZM + 2, x + 27, 548, ZM + 3], "plastic#7a7a7a", soft=True,
          repeat=rep(15, [0, 75, 0]), copies=[[0, 0, -5]])
    d.box(f"buckle{i}", [x - 3, 600, ZM - 6, x + 43, 640, ZM + 6], "metal#c8c8c8", r=3, soft=True)
d.tube("sw-frame", [[SX0 - 12, 458, SZ0 - 6], [SX1 + 12, 458, SZ0 - 6], [SX1 + 12, 458, SZ1 + 6], [SX0 - 12, 458, SZ1 + 6],
                    [SX0 - 12, 458, SZ0 - 6]], 18, "plastic#f0f0f0", bend=20)
d.box("sw-red", [SX0, 466, SZ0, SX1, 518, SZ1], "leather#e02424", r=12)
d.box("sw-yel", [SX0 + 3, 516, SZ0 + 3, SX1 - 3, 546, SZ1 - 3], "leather#f2c81e", r=8)
d.box("sw-grn", [SX0 + 5, 544, SZ0 + 5, SX1 - 5, 560, SZ1 - 5], "leather#2fa848", r=6)
d.cyl("sw-cyl-g", [830, 645, SZ0 + 20], [830, 645, SZ1 - 70], 172, "leather#9cd23e")
d.cyl("sw-cyl-r", [1010, 635, SZ0 + 50], [1000, 635, SZ1 + 5], 150, "leather#e8243a")
# back face, left half: ladder of grey / green rungs to a middle post
XM = 880
d.box("mid-post", [XM, 0, ZB, XM + P, 1700, ZB + P], "pine", r=4)
for i, y in enumerate((1320, 1140, 970, 790, 610, 430)):
    d.cyl(f"rung{i}", [P, y, ZB + 40], [XM, y, ZB + 40], 32, "grey" if i % 2 == 0 else "green")
# back face, right half: climbing wall panel leaning out behind the frame, coloured holds on its outer face
TL = rot("x", 10, [0, 1720, ZB])
d.box("wall", [XM + P, 0, ZB - 32, W - P, 1720, ZB], "pine2", r=4, rot=TL)
d.decal("plank", [XM + P + 76, 860, ZB - 32.6], [5, 1700], "back", "wood#b89060", repeat=rep(9, [76, 0, 0]), rot=TL)
d.decal("plank-in", [XM + P + 76, 860, ZB + 0.6], [5, 1700], "front", "wood#b89060", repeat=rep(9, [76, 0, 0]), rot=TL)
R_, Y_, G_, B_ = "#e02424", "#f2b81e", "#2fa040", "#2840b0"
_ph = [(325, 100, R_), (275, 145, Y_), (405, 165, G_), (465, 120, Y_), (345, 225, Y_), (465, 225, B_), (285, 265, R_),
       (415, 270, R_), (355, 335, G_), (478, 340, G_), (290, 390, B_), (430, 385, B_), (490, 455, B_), (360, 460, R_),
       (295, 518, G_), (430, 505, Y_), (495, 572, G_), (360, 590, Y_), (305, 650, B_), (440, 640, R_)]
holds = [(1720 - (px - 215) / 325 * 760, (790 - py) / 740 * 1720, c) for px, py, c in _ph]
for i, (x, y, c) in enumerate(holds):
    d.sphere(f"hold{i}", [x, y, ZB - 36], None, "gloss" + c, radii=[42, 36, 20], rot=TL)
# floor: two light-green mats, foam cylinders, a pile of cream boxes at the front right
d.box("mat", [P, 0, ZB + P, W / 2 - 4, 50, ZF - P], "mat", r=12)
d.box("mat2", [W / 2 + 4, 0, ZB + P, W - P, 50, ZF - P], "mat", r=12)
d.cyl("fl-cyl-g", [360, 160, ZF - 480], [360, 160, ZF - 110], 220, "leather#9cd23e")
d.cyl("fl-cyl-r", [640, 190, ZF - 130], [1120, 190, ZF - 640], 280, "leather#e8243a")
cartons = [([1130, 50, ZF - 210, 1700, 180, ZF - 80], -10),   # front, lying along x, left end further back
           ([1050, 50, ZF - 560, 1230, 210, ZF - 220], 0),    # left, lying along z (end towards the viewer)
           ([1250, 50, ZF - 560, 1720, 210, ZF - 400], 0),    # back bottom
           ([1240, 180, ZF - 360, 1700, 300, ZF - 230], -12), # middle, across the front one
           ([1140, 210, ZF - 560, 1660, 400, ZF - 420], 0)]   # back top
for i, (b, a) in enumerate(cartons):
    c = [(b[0] + b[3]) / 2, 0, (b[2] + b[5]) / 2]
    R = rot("y", a, c) if a else None
    d.box(f"carton{i}", b, "plastic#efe3c6", r=4, rot=R)
    L, Hh = b[3] - b[0], b[4] - b[1]
    n = 1 if L < 300 else 3
    d.box(f"lbl{i}", [b[0] + L / (2 * n) - 45, b[1] + Hh * 0.35, b[5], b[0] + L / (2 * n) + 45, b[1] + Hh * 0.65, b[5] + 0.8],
          "plastic#c49080", soft=True, rot=R, repeat=rep(n, [L / n, 0, 0]) if n > 1 else None)
    d.box(f"lblt{i}", [b[0] + L / (2 * n) - 45, b[4], c[2] - 20, b[0] + L / (2 * n) + 45, b[4] + 0.8, c[2] + 20],
          "plastic#c49080", soft=True, rot=R, repeat=rep(n, [L / n, 0, 0]) if n > 1 else None)
d.save()
