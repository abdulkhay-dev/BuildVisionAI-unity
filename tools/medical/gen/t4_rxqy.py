"""XY-K-RXQY-III spinal decompression traction table — batch table-4. Writes only xy-k-rxqy-iii.
Length along x (console + pole at the left as in the photo), front z = D."""
import random
from t4lib import *

d = D("xy-k-rxqy-iii", [2800, 700, 2050], {
    "white": "plastic#f2f3f5", "grey": "plastic#6b7078", "top": "plastic#a9adb3", "pad": "leather#4fa6dc",
    "chrome": "chrome", "steel": "metal#c9ccd0", "lite": "plastic#dcdfe3", "cable": "metal#8d9196",
    "dark": "plastic#3a3e44", "cyan": "gloss#36c6e8", "logo": "gloss#2f7fd0", "bow": "metal#d6d8db"})
W, DP = 2800, 700
# ---------------------------------------------------------------- console
cx0, cx1, cz0, cz1 = 300, 720, 75, 625
d.box("con", [cx0, 85, cz0, cx1, 742, cz1], "white", r=18)
d.box("con-grey", [cx0 + 65, 110, cz1 - 2, cx1 - 135, 715, cz1 + 2], "grey", r=4)   # offset left (photo 2)
d.box("con-top", [cx0 - 12, 738, cz0 - 12, cx1 + 12, 762, cz1 + 12], "top", r=12)
d.box("con-touch", [cx0 + 40, 762, cz0 + 250, cx0 + 260, 766, cz1 - 30], "plastic#e6f1f5", r=6)
d.decal("con-keys", [cx0 + 70, 766.5, cz0 + 290], [26, 14], "top", "cyan", soft=True, repeat=rep(6, [30, 0, 0]),
        copies=[[0, 0, 60], [0, 0, 120], [0, 0, 180]])
random.seed(4)
dots = []
for k in range(120):
    z = random.uniform(cz0 + 50, cz1 - 50)
    y = 110 + 600 * random.random() ** 1.6          # denser towards the bottom
    dots.append([0, round(y - 300), round(z - 350)])
d.decal("con-dots", [cx0 - 0.6, 300, 350], [10, 6], "left", "plastic#a3a7ae", soft=True, copies=dots)
d.decal("con-logo", [cx0 - 0.6, 690, cz0 + 70], [40, 40], "left", "logo", soft=True)
d.decal("con-logo-t", [cx0 - 0.6, 690, cz0 + 140], [80, 14], "left", "logo", soft=True)
castor(d, "con-castor", cx0 + 50, cz0 + 50, 80, corners(cx0 + 50, cz0 + 50, cx1 - 50, cz1 - 50))
d.cyl("con-btn", [cx1, 690, 470], [cx1 + 40, 690, 470], 26, "white", copies=[[0, 0, 60]])
d.cyl("con-btn-r", [cx1 + 40, 690, 470], [cx1 + 52, 690, 470], 20, "gloss#e2312b", copies=[[0, 0, 60]])
# pulley blocks on the console top
for nm, x in (("l", 410), ("r", 625)):
    d.box(f"tp-{nm}", [x - 22, 762, 430, x + 22, 800, 470], "white", r=6)
    d.add(f"tp-w-{nm}", "wheel", "white", at=[x, 812, 450], d=70, d2=30, axis="z")
# ---------------------------------------------------------------- pole, arm, cables
px, pz = 517, 350
d.cyl("pole", [px, 762, pz], [px, 1960, pz], 40, "chrome")
d.cyl("cap", [px, 1960, pz], [px, 2035, pz], 84, "white")
d.cyl("cap-led", [px, 1995, pz], [px, 2008, pz], 86, "cyan", soft=True)
d.cyl("cap-clamp", [px, 1880, pz], [px, 1930, pz], 52, "white", copies=[[0, -110, 0]])
d.cyl("arm", [px, 1990, pz], [20, 1990, pz], 36, "chrome")
d.box("arm-clamp", [150, 1965, pz - 24, 215, 2015, pz + 24], "white", r=8, copies=[[275, 0, 0]])
d.cyl("arm-end", [10, 1990, pz], [30, 1990, pz], 40, "white")
gus = "M 500 1968 L 180 1968 L 200 1940 L 500 1745 Z M 470 1945 L 260 1945 L 470 1810 Z"
d.add("gusset", "slab", "white", plane="front", outline=gus, w=[pz - 9, pz + 9], r=3)
d.cyl("gus-disc", [395, 1885, pz - 11], [395, 1885, pz + 11], 105, "white")
d.cyl("gus-disc-in", [395, 1885, pz + 11], [395, 1885, pz + 13], 70, "lite", soft=True)
d.box("end-brk", [45, 1890, pz - 16, 85, 1975, pz + 16], "white", r=6)
d.add("end-pulley", "wheel", "white", at=[65, 1895, pz], d=70, d2=34, axis="z")
# cervical hanger (cable, knob, white Y with hooks)
# (photo 2: the coat-hanger lies across the table — it looks narrow in the front elevation, wide in photo 1)
d.cyl("c-cable", [40, 1880, pz], [80, 1670, pz], 4, "cable", soft=True)
d.sphere("c-knob", [80, 1665, pz], 30, "chrome")
d.tube("c-hanger", [[80, 1655, pz], [84, 1595, pz], [88, 1490, pz - 125], [88, 1460, pz - 125], [86, 1475, pz - 105]], 9, "lite", bend=8)
d.tube("c-hanger-r", [[84, 1595, pz], [88, 1490, pz + 125], [88, 1460, pz + 125], [86, 1475, pz + 105]], 9, "lite", bend=8)
# diagonal cable to the middle clamp; lower clamp with the traction rod
d.cyl("d-cable", [80, 1870, pz], [400, 1285, pz], 4, "cable", soft=True)
d.cyl("m-clamp", [px, 1260, pz], [px, 1310, pz], 54, "white", copies=[[0, -275, 0]])
d.add("m-pulley", "wheel", "white", at=[430, 1285, pz], d=62, d2=30, axis="z")
d.box("m-arm", [430, 1272, pz - 12, px, 1298, pz + 12], "white", r=5, copies=[[90, -275, 0]])
d.add("l-pulley", "wheel", "white", at=[610, 1010, pz], d=62, d2=30, axis="z")
d.cyl("m-handle", [px + 25, 1285, pz], [px + 70, 1250, pz], 10, "chrome", copies=[[0, -275, 0]])
d.cyl("m-handle-t", [px + 70, 1240, pz - 20], [px + 70, 1240, pz + 20], 10, "chrome", copies=[[0, -275, 0]])
d.cyl("v-cable-l", [410, 845, 450], [415, 1260, pz], 4, "cable", soft=True)
d.cyl("v-cable-r", [625, 845, 450], [625, 985, pz], 4, "cable", soft=True)
d.cyl("rod-cable", [640, 1020, pz], [870, 990, pz], 4, "cable", soft=True)
d.cyl("rod", [870, 990, pz], [1080, 932, pz], 12, "chrome")
d.cyl("rod-spring", [880, 987, pz], [935, 972, pz], 24, "chrome")
d.tube("rod-fork", [[1070, 935, pz - 22], [1125, 920, pz - 22]], 8, "chrome", copies=[[0, 0, 44]])
d.cyl("rod-fork-x", [1070, 935, pz - 22], [1070, 935, pz + 22], 10, "chrome")
# ---------------------------------------------------------------- bed
# (photo 2: aluminium band 490–560, thick white boards, thin blue pads; long pad from 850, a bare frame end before it)
d.box("frame", [690, 545, 25, 2790, 565, 675], "white", r=8)
d.box("rail", [700, 485, 20, 2785, 560, 45], "steel", r=6, copies=[[0, 0, 635]])
d.box("frame-x", [700, 485, 45, 760, 545, 655], "steel", r=4, copies=[[2020, 0, 0]])
top_pad(d, "board1", 845, 2125, 30, 670, 562, 612, "white", cr=30, r=6)
top_pad(d, "pad1", 850, 2120, 35, 665, 608, 648, "pad", cr=30, r=10)
cham_pad(d, "board2", 2133, 2788, 30, 670, 562, 612, "white", cx=60, cz=60, cr=20, r=6)
cham_pad(d, "pad2", 2138, 2783, 35, 665, 608, 648, "pad", cx=55, cz=55, cr=20, r=10)
# wedge with a rounded top and logo
wedge = round_poly([(1265, 646), (1600, 646), (1478, 885), (1445, 902), (1405, 902), (1372, 885)], 30)
front_slab(d, "wedge", wedge, 150, 550, "pad", r=18)
d.decal("wedge-logo", [1432, 790, 550.6], [40, 30], "front", "plastic#1f5b8f", soft=True)
# leg cylinders hanging from the bow tubes, neck pillow
for nm, zc in (("f", 410), ("b", 290)):
    d.cyl(f"legcyl-{nm}", [2225, 646, zc], [2225, 840, zc], 110, "pad")
    zf = 650 if nm == "f" else 50
    d.tube(f"bow-{nm}", [[2765, 520, zf], [2795, 560, zf], [2795, 895, zf], [2360, 918, zf], [2262, 918, zc], [2227, 840, zc]],
           34, "bow", bend=70)
pil = [(2480, 646), (2780, 646), (2780, 715), (2750, 742), (2700, 736), (2620, 708), (2550, 718), (2510, 730), (2480, 718)]
front_slab(d, "pillow", pil, 190, 510, "pad", r=20)
d.decal("pillow-logo", [2535, 685, 510.6], [30, 24], "front", "plastic#1f5b8f", soft=True)
# heater box under the middle, black clamps under the frame
d.box("heater-brk", [1360, 455, 220, 1580, 485, 480], "lite", r=4)
d.box("heater", [1320, 340, 200, 1620, 455, 500], "grey", r=8)
d.box("clamp", [1000, 465, 300, 1040, 487, 400], "dark", r=4, copies=[[1520, 0, 0]])
# chrome twin-tube legs at both ends, foot tubes bending inwards, levelling feet
for nm, x, s in (("a", 730, 1), ("b", 2640, -1)):
    d.box(f"leg-plate-{nm}", [x - 50, 468, 300, x + 50, 485, 400], "steel", r=4)
    # (photos: twin vertical tubes; at the floor each bends inwards along the length to a levelling foot,
    #  one towards the front, one towards the back)
    d.tube(f"leg-{nm}", [[x, 470, 335], [x, 75, 335], [x + s * 70, 62, 520], [x + s * 190, 62, 560]], 36, "chrome", bend=60)
    d.tube(f"leg2-{nm}", [[x, 470, 375], [x, 75, 375], [x + s * 70, 62, 180], [x + s * 190, 62, 140]], 36, "chrome", bend=60)
    d.lathe(f"foot-{nm}", [x + s * 190, 0, 560], [[0, 0], [45, 0], [45, 12], [10, 18], [10, 60], [0, 60]], "chrome", copies=[[0, 0, -420]])
d.save()
