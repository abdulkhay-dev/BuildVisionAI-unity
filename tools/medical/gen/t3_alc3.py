# ALC-3 far-infrared massage bed with lumbar traction (table-3 batch). Head end = x small (pillow, U hand bar with
# armpit rolls), foot end = x max (stainless frame the traction straps run to).
from t3_alclib import *
L, Dp, Ht = 2040, 780, 680
d = D("alc-3", [2150, Dp, 1030], dict(MATS, mat="fabric#cddcf1", pillow="fabric#8fb3e6", belt="fabric#a9b2c0", beltb="fabric#5f73a6",
                                     legpad="fabric#7ea6e2", strapw="fabric#d9dee6", foam="rubber#141517",
                                     remote="plastic#f4f5f7", lcd="gloss#2f6fc8"))
body(d, 0, L, Dp, Ht, end_panel=False)
cz = Dp / 2
T = Ht + 3   # top of the mat
# ---- head end: pillow, black neck strap, U hand bar with two black armpit rolls
# photo: a flat envelope pillow propped up against the hand bar
d.box("pillow", [70, T, 150, 420, T + 70, 620], "pillow", r=14, puff=30, rot=rot("z", 14, [70, T, cz]))
d.strap("neck-strap", [[60, T + 4, 640], [520, T + 4, 640]], [36, 4], "fabric#202326", soft=True)
d.tube("hand-bar", [[95, T - 30, 70], [95, T + 10, 70], [430, 1000, 70], [430, 1000, Dp - 70], [95, T + 10, Dp - 70],
                    [95, T - 30, Dp - 70]], 32, "chr", bend=70)
d.box("bar-mount", [70, T - 6, 50, 130, T + 20, 95], "chr", r=5, copies=[[0, 0, Dp - 145]])
for nm, z in (("a", cz - 130), ("b", cz + 130)):
    d.cyl("roll-stem-" + nm, [430, 1000, z], [430, 950, z], 22, "chr")
    d.cyl("roll-" + nm, [430, 955, z], [430, 705, z], 110, "foam")
# ---- chest and pelvic traction harnesses lying open on the mat (grey with blue-grey stripes)
for nm, x0 in (("chest", 690), ("pelvis", 900)):
    d.box("belt-" + nm, [x0, T, 170, x0 + 170, T + 22, 640], "belt", r=8, puff=6)
    d.box("belt-" + nm + "-stripe", [x0 + 20, T + 10, 168, x0 + 40, T + 24, 642], "beltb", r=4, copies=[[110, 0, 0]])
    d.box("belt-" + nm + "-buckle", [x0 + 50, T + 20, 400, x0 + 120, T + 30, 470], "fabric#2b2f36", r=4)
# long traction straps from the pelvic harness to the foot frame
for nm, z in (("a", 290), ("b", 490)):
    d.strap("trac-" + nm, [[1070, T + 6, z], [1900, T + 8, z], [2070, 800, z + (1 if z < cz else -1) * 40]], [30, 3],
            "strapw", bend=60, soft=True)
# ---- blue padded leg pad with its straps
d.box("leg-pad", [1400, T, 200, 1830, T + 55, 640], "legpad", r=18, puff=8)
d.box("leg-pad-seam", [1540, T + 30, 198, 1548, T + 58, 642], "fabric#5f86c8", r=3, copies=[[140, 0, 0]])
d.strap("leg-strap", [[1450, T + 56, 140], [1450, T + 56, 700]], [40, 4], "strapw", soft=True, copies=[[300, 0, 0]])
# ---- white bat-handle remote with a blue panel and its cable
d.box("remote", [720, T, 620, 900, T + 32, 690], "remote", r=14)
d.add("remote-lcd", "screen", "lcd", box=[750, T + 30, 630, 840, T + 34, 680], r=4, face="top")
d.tube("remote-cable", [[720, T + 10, 655], [560, T + 4, 660], [300, T + 4, 600], [140, T + 4, 560]], 8,
       "plastic#1d1f22", bend=60, soft=True)
# ---- foot end stainless frame: two side tubes out of the end face, crossbars along the width
for nm, z in (("a", 120), ("b", Dp - 120)):
    d.tube("foot-side-" + nm, [[L - 40, 240, z], [2105, 240, z], [2125, 800, z]], 32, "chr", bend=50)
d.cyl("foot-top", [2125, 800, 120], [2125, 800, Dp - 120], 32, "chr")
d.cyl("foot-mid", [2117, 520, 120], [2117, 520, Dp - 120], 26, "chr")
d.bar("foot-tensioner", [2080, 260, cz], [2100, 500, cz], [30, 20], "gloss#a8463c", r=4)
d.save()
