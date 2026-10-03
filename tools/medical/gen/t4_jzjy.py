"""XY-JZJY-III spinal decompression traction system (table + console) — batch table-4. Writes only xy-jzjy-iii.
Length along x: the tilted leg section at the left (x = 0), the head end and the console at the right, as in the
photos; front z = D."""
import math
from t4lib import *

d = D("xy-jzjy-iii", [2800, 800, 1390], {
    "white": "plastic#f2f3f5", "lgrey": "plastic#c9cdd2", "grey": "plastic#8a8f96", "pad": "leather#5a5f66",
    "bell": "rubber#1e2023", "blue": "gloss#2f7fd0", "dark": "plastic#26292e", "chrome": "chrome",
    "copper": "metal#c08a5a", "roll": "leather#8c9096"})
DP = 800
# ---------------------------------------------------------------- table
d.box("plinth", [750, 20, 50, 1860, 150, 750], "white", r=50)
d.box("plinth-top", [770, 150, 70, 1840, 168, 730], "lgrey", r=30)
d.lathe("foot", [820, 0, 120], [[0, 0], [22, 0], [22, 22], [0, 22]], "copper", copies=corners(820, 120, 1790, 680))
tl = text_len("XIANGYU MEDICAL", 30, 0.3)
text(d, "plinth-txt", "XIANGYU MEDICAL", [1180 - tl / 2, 72, 750.6], 30, "blue", gap=0.3)
for k, sg in enumerate((-1, 1)):   # the little triangles at both ends of the lettering
    d.add(f"plinth-tri{k}", "slab", "blue", plane="front", soft=True, w=[750.2, 751.2],
          outline=poly_path([(1180 + sg * (tl / 2 + 14), 72), (1180 + sg * (tl / 2 + 40), 72), (1180 + sg * (tl / 2 + 40 if sg < 0 else tl / 2 + 14), 102)]))
d.cyl("plinth-hole", [1450, 70, 749], [1450, 70, 751], 10, "dark", soft=True)
d.cyl("lever", [1790, 160, 640], [1815, 260, 690], 16, "dark")
d.sphere("lever-k", [1815, 262, 690], 30, "dark")
d.box("bellows", [900, 165, 160, 1745, 450, 640], "bell", r=10)
d.box("bell-rib", [893, 175, 153, 1752, 185, 647], "bell", r=5, repeat=rep(10, [0, 28, 0]))
d.box("shroud", [870, 440, 120, 1760, 552, 680], "white", r=24)
d.decal("stripe", [1315, 540, 680.5], [880, 6], "front", "blue", soft=True, copies=[[0, -12, 0]])
brand(d, "shroud-logo", 990, 478, 680, 26, mat="blue", en=False)
d.box("frame", [540, 550, 60, 1980, 632, 740], "white", r=14)
d.decal("led", [1000, 594, 740.5], [700, 26], "front", "plastic#b6babf", soft=True)
d.decal("led-dots", [760, 596, 740.8], [140, 6], "front", "plastic#7a7f86", soft=True)
d.box("switch", [1560, 580, 738, 1580, 610, 745], "dark", r=2)
# (photo 2: the top is ~130 thick, its top at ~760)
top_pad(d, "pad-f", 580, 1835, 410, 760, 628, 760, "pad", cr=40, r=26)
top_pad(d, "pad-b", 580, 1835, 40, 390, 628, 760, "pad", cr=40, r=26)
# head piece: grey pad on a white plate, chrome latch
d.box("head-plate", [1845, 600, 120, 2000, 640, 680], "white", r=10)
top_pad(d, "head-pad", 1850, 2020, 140, 660, 636, 745, "pad", cr=30, r=22)
d.tube("latch", [[1905, 720, 662], [1905, 655, 678], [1955, 655, 678], [1955, 720, 662]], 14, "chrome", bend=12)
# ---------------------------------------------------------------- tilted leg section (photo 2: pad ~26 deg down to
# the foot end, a white side-plate housing under it rising into a block at the end that carries the black calf plate
# and the knee roll; a white beam from the housing to the shroud)
lr = rot("z", 26, [585, 700, 0])
d.box("beam", [470, 460, 300, 905, 535, 500], "white", r=10)
front_slab(d, "leg-house", [(10, 600), (10, 680), (40, 705), (82, 700), (88, 610), (185, 605), (185, 560), (585, 650), (610, 640), (490, 450), (85, 480)],
           140, 660, "white", r=18)
d.box("leg-tray", [105, 640, 90, 585, 700, 710], "white", r=16, rot=lr)
top_pad(d, "leg-pad", 115, 575, 100, 700, 690, 770, "pad", cr=35, r=20, rot=lr)
d.box("calf-block", [95, 600, 200, 180, 650, 600], "grey", r=12)
d.add("calf", "slab", "dark", plane="front", outline="M 120 585 L 165 585 Q 122 680 132 792 L 86 792 Q 76 680 120 585 Z",
      w=[200, 600], r=10)
d.cyl("knee-roll", [245, 742, 160], [245, 742, 640], 180, "roll")
d.cyl("knee-end", [245, 742, 150], [245, 742, 160], 82, "dark", copies=[[0, 0, 490]])
d.cyl("knee-dot", [245, 742, 146], [245, 742, 151], 16, "white", soft=True, copies=[[0, 0, 498]])
d.box("ear", [228, 600, 128, 262, 715, 145], "grey", r=12, copies=[[0, 0, 527]])
d.cyl("ear-screw", [245, 640, 124], [245, 640, 129], 14, "chrome", soft=True, copies=[[0, 0, 545]])
# ---------------------------------------------------------------- console (C profile, slanted column)
X0 = 1960
d.box("c-base", [X0, 70, 120, X0 + 800, 175, 680], "white", r=30)
d.box("c-base-top", [X0 + 30, 175, 140, X0 + 770, 190, 660], "lgrey", r=14)
castor(d, "c-castor", X0 + 70, 170, 75, corners(X0 + 70, 170, X0 + 730, 630))
col = [(X0, 190), (X0 + 170, 190), (X0 + 270, 900), (X0 + 100, 900)]
front_slab(d, "c-col", col, 120, 680, "white", r=20)
ang = math.atan2(710, 100)            # the column's front edge direction (leaning right going up)
ux, uy = math.cos(ang), math.sin(ang)
tl = text_len("XIANGYU MEDICAL", 30, 0.3)
text(d, "c-txt", "XIANGYU MEDICAL", [X0 + 150 - ux * tl / 2, 545 - uy * tl / 2, 680.6], 30, "blue", along=(ux, uy), gap=0.3)
d.box("c-desk", [X0 + 80, 930, 110, X0 + 820, 965, 690], "white", r=14)
d.box("c-desk-u", [X0 + 160, 895, 130, X0 + 790, 932, 670], "grey", r=10)
back = "M {a} 190 L {b} 190 Q {c} 260 {d} 520 Q {c} 800 {e} 895 L {f} 895 Z".format(
    a=X0 + 150, b=X0 + 720, c=X0 + 600, d=X0 + 570, e=X0 + 760, f=X0 + 250)
d.add("c-back", "slab", "grey", plane="front", outline=back, w=[130, 330], r=10)
d.box("c-bump", [X0 + 230, 230, 300, X0 + 560, 580, 380], "grey", r=50, puff=8)
# monitor on a thin stalk, mouse, joystick
# monitor turned ~40 deg towards the table (photo 2 shows it foreshortened), stalk at its right half
mr = rot("y", -40, [X0 + 450, 0, 395])
d.lathe("m-foot", [X0 + 470, 965, 380], [[0, 0], [70, 0], [70, 6], [0, 10]], "white")
d.tube("m-stalk", [[X0 + 470, 970, 380], [X0 + 470, 1010, 380], [X0 + 470, 1065, 390]], 14, "white", bend=20)
d.add("monitor", "screen", "white", box=[X0 + 200, 1065, 383, X0 + 700, 1390, 405], face="front", r=6, bezel=14,
      print="med_xy-jzjy-iii_screen", rot=mr)
d.sphere("mouse", [X0 + 700, 980, 560], None, "dark", radii=[40, 18, 60])
d.cyl("joy", [X0 + 600, 965, 590], [X0 + 600, 1010, 590], 14, "dark")
d.sphere("joy-k", [X0 + 600, 1012, 590], 26, "dark")
d.save()
