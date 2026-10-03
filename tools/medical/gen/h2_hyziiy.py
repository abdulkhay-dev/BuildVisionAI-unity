from h2lib import *
# HYZ-IIY perianal fumigation chair + console tower (photo: front, chair at the left, console at the right).
# Chair: white glossy base tub with a blue arch line and the round logo, lilac seat cushion with a round hole and a
# clear splash dome over its back half, thick white armrest blocks with sloping top pads and pockets, a tall reclined
# lilac backrest with quilting lines. Console: white tower, front view a "C" opening to the chair (head with a diagonal
# brace on top, column, rounded foot block at the bottom left), blue edge line, blue arch with the logo, control panel
# with a LCD and blue/orange keys and a green switch on the head.
W, DP, H = 1360, 800, 1250   # review: console measured ~540 wide in the photo (head 390 px at 1.47 mm/px)
d = D("hyz-iiy", [W, DP, H], {
    "shell": "gloss#f8f9fa", "lilac": "leather#cfcee8", "quilt": "plastic#b4b3d4", "blue": "gloss#4a5fc0",
    "dark": "black#2b2f35", "dome": "acrylic#e6edf890", "panel": "plastic#cfd3d8", "frame": "plastic#5b6168"})
# ---------------- chair (x 0..760)
CX = 380
d.loft("base", [sec(18, 560, 560, 110, CX, 482), sec(300, 610, 640, 130, CX, 442), sec(440, 640, 680, 140, CX, 422)], "shell")
d.slab("base-lip", "top", P(rr(CX - 335, 72, CX + 335, 772, 150)), [430, 470], "shell", r=16)
d.box("foot", [CX - 230, 0, 260, CX - 200, 20, 290], "dark", r=4, copies=[[430, 0, 0], [0, 0, 400], [430, 0, 400]])
# blue arch line and the round logo on the base front (z 762)
arch_o = "M 330 40 L 330 300 Q 330 380 410 380 Q 490 380 490 300 L 490 40 Z"
arch_i = "M 342 40 L 342 300 Q 342 368 410 368 Q 478 368 478 300 L 478 40 Z"
d.slab("arch", "front", arch_o + " " + arch_i, [760, 765], "blue", r=1)
d.lathe("logo", [410, 230, 762], [[0, 0], [52, 0], [52, 2], [0, 2]], "gloss#ffffff", axis="z", soft=True)
# photo: white disc in a blue ring with the blue mark
logo_round(d, "logo-m", [410, 230, 764], 92, blue="gloss#ffffff", white="gloss#2f4fb8")
d.slab("logo-m-ring", "front", ring(ell(410, 230, 50, 50), ell(410, 230, 43, 43)), [764, 767], "gloss#2f4fb8", r=0.5, soft=True)
# seat cushion with the hole, splash dome
d.box("seat", [CX - 260, 440, 270, CX + 260, 515, 760], "lilac", r=24, puff=8)
d.lathe("hole", [CX, 513, 560], [[0, 0], [85, 0], [85, 5], [0, 5]], "dark", soft=True)
d.lathe("hole-ring", [CX, 516, 560], [[62, 0], [92, 0], [92, 4], [62, 4]], "plastic#9da2b8", soft=True)
# clear splash hood over the BACK half of the hole (its front edge crosses the hole's middle), rising ~190 mm
d.sphere("dome", [CX, 515, 395], None, "dome", radii=[185, 195, 205])
# armrests: block + sloping top pad + pocket slot (left, right = shifted copy)
for nm, dx in (("l", 0), ("r", 580)):
    d.box(f"arm-{nm}", [dx, 420, 240, dx + 180, 740, 770], "shell", r=50)
    d.box(f"arm-pad-{nm}", [dx - 0, 690, 220, dx + 180, 790, 720], "shell", r=45, rot=rot("x", 15, [dx + 90, 740, 720]))
    ox = dx + 18 if nm == "l" else dx + 82          # outer half of the arm front (photo: pocket mouth low, outside)
    d.box(f"arm-pocket-{nm}", [ox - 6, 480, 764, ox + 86, 520, 771], "plastic#e4e7ea", r=12, soft=True)
    d.box(f"arm-slot-{nm}", [ox, 488, 769, ox + 80, 512, 776], "dark", r=10, soft=True)
d.cyl("arm-knob", [-12, 690, 700], [6, 690, 700], 26, "chrome")
# backrest, reclined 10 deg, with quilting lines
br = rot("x", -10, [CX, 480, 210])
d.box("back", [CX - 275, 470, 150, CX + 275, 1262, 265], "lilac", r=40, puff=10, rot=br)
q = dict(soft=True, rot=br)
d.box("q-top", [CX - 258, 1060, 270, CX + 258, 1066, 274], "quilt", r=2, **q)
d.box("q-sq-h", [CX - 120, 900, 270, CX + 120, 906, 274], "quilt", r=2, copies=[[0, -170, 0]], **q)
d.box("q-sq-v", [CX - 122, 730, 270, CX - 116, 906, 274], "quilt", r=2, copies=[[238, 0, 0]], **q)
for i, (a, b) in enumerate([((CX - 265, 1060), (CX - 120, 906)), ((CX + 265, 1060), (CX + 120, 906)),
                             ((CX - 120, 730), (CX - 240, 560)), ((CX + 120, 730), (CX + 240, 560))]):
    d.bar(f"q-diag{i}", [a[0], a[1], 272], [b[0], b[1], 272], [5, 4], "quilt", r=1, soft=True, rot=br)
# ---------------- console tower (x 820..1360, z 300..650)
Z0, Z1 = 300, 650
c = ("M 1360 0 L 1360 1050 Q 1360 1092 1310 1092 L 863 1092 Q 820 1092 820 1056 L 820 960 L 972 760 L 972 0 Z")
d.slab("tower", "front", c, [Z0, Z1], "shell", r=26)
d.box("tower-foot", [832, 0, Z0 + 20, 1002, 380, Z1 - 70], "shell", r=60)
d.tube("edge", [[827, 1080, Z1 + 1], [827, 962, Z1 + 1], [972, 770, Z1 + 1], [972, 10, Z1 + 1]], 12, "blue", bend=60, soft=True)
arch2_o = "M 1050 10 L 1050 600 Q 1050 700 1160 700 Q 1270 700 1270 600 L 1270 10 Z"
arch2_i = "M 1064 10 L 1064 600 Q 1064 686 1160 686 Q 1256 686 1256 600 L 1256 10 Z"
d.slab("arch2", "front", arch2_o + " " + arch2_i, [Z1 - 2, Z1 + 3], "blue", r=1)
logo_round(d, "logo2", [1160, 500, Z1 + 1], 115, blue="gloss#ffffff", white="gloss#2f4fb8")
d.slab("logo2-ring", "front", ring(ell(1160, 500, 61, 61), ell(1160, 500, 53, 53)), [Z1 + 1, Z1 + 4], "gloss#2f4fb8", r=0.5, soft=True)
d.slab("logo2-r", "front", ring(ell(1240, 560, 9, 9), ell(1240, 560, 6, 6)), [Z1, Z1 + 1.5], "gloss#2f4fb8", r=0.5, soft=True)
# control panel on the head (sloping a little to the front), LCD, keys, green rocker switch
pr = rot("x", 12, [1097, 1092, Z1 - 10])
d.slab("head-wedge", "side", f"M {Z0} 1080 L {Z0} {1092 + (Z1 - 10 - Z0) * 0.2126:.0f} L {Z1 - 10} 1092 L {Z1 - 10} 1080 Z", [822, 1358], "shell", r=10)
d.box("panel", [870, 1086, Z0 + 40, 1300, 1100, Z1 - 30], "frame", r=8, rot=pr)
d.box("panel-face", [888, 1098, Z0 + 55, 1282, 1103, Z1 - 45], "panel", r=4, rot=pr)
d.add("lcd", "screen", "frame", box=[1030, 1098, Z0 + 110, 1170, 1108, Z0 + 260], r=4, face="top", bezel=6, rot=pr)
d.box("key-b", [930, 1102, Z0 + 150, 972, 1110, Z0 + 175], "gloss#3f8fe0", r=3, copies=[[275, 0, 0], [275, 0, 50]], rot=pr)
d.box("key-o", [930, 1102, Z0 + 205, 972, 1110, Z0 + 230], "gloss#e86a2a", r=3, rot=pr)
text(d, "panel-t", "XIANGYU", [1050, 1104, Z0 + 92], 9, "plastic#6b7280", face="top", stroke=1.6)
d.box("switch", [1318, 1088, Z0 + 60, 1348, 1110, Z0 + 95], "gloss#2fa84a", r=4, rot=pr)
d.save()
