"""XYT-2 hydraulic step trainer: white square-tube frame, one black foam U handrail from the rear posts forward to
the column, a forward-leaning white column with a small LCD counter (facing the user), an A strut with a cross plate,
two black pedals on arms pivoting at the front with black hydraulic cylinders, a bowed white front foot.
The user stands on the pedals facing the column (front, z = depth)."""
import sys, os; sys.path.insert(0, os.path.dirname(__file__))
from k8lib import *

W, DP, H = 620, 800, 1140
d = D("xyt-2", [W, DP, H], {"frame": "plastic#efefeb", "foam": "rubber#1d1e20", "black": "plastic#1b1c1e", "chrome": "chrome",
                            "pedal": "rubber#222326", "blue": "gloss#2a62c8", "grey": "metal#a7abb0"})
CX = W / 2
# rear cross bar, rear posts, black caps
d.box("rear", [0, 0, 0, W, 50, 60], "frame", r=4)
d.box("rear-cap", [-1, 0, 0, 5, 50, 60], "black", r=2, copies=[[W - 4, 0, 0]])
for k, x in (("l", 50), ("r", W - 50)):
    d.box(f"post-{k}", [x - 25, 50, 5, x + 25, 830, 55], "frame", r=4)
# handrail: one black foam U from the rear posts, rising to the front, across behind the console
rail = [[50, 800, 30], [50, 985, 36], [50, 1055, 610], [CX, 1070, 705], [W - 50, 1055, 610], [W - 50, 985, 36],
        [W - 50, 800, 30]]
d.tube("rail", rail, 40, "foam", bend=110)
# floor beam, bowed front foot
d.box("beam", [CX - 28, 0, 55, CX + 28, 55, 700], "frame", r=4)
fo, fi = [], []
for i in range(13):
    t = i / 12
    x = 40 + (W - 80) * t
    z = 700 + 80 * math.sin(math.pi * t)
    fo.append((x, z + 28)); fi.append((x, z - 28))
foot = "M " + " L ".join(f"{x:.1f} {z:.1f}" for x, z in fo + fi[::-1]) + " Z"
d.slab("foot", "top", foot, [0, 40], "frame", r=6)
d.box("foot-cap", [28, 0, 690, 52, 42, 742], "black", r=4, copies=[[W - 80, 0, 0]])
# column leaning forward, A strut, cross plate with knobs, blue label
C0, C1 = [CX, 50, 600], [CX, H - 70, 745]
d.bar("column", C0, C1, [60, 60], "frame", r=5)
tilt = math.degrees(math.atan2(C1[2] - C0[2], C1[1] - C0[1]))
cz = lambda y: C0[2] + (C1[2] - C0[2]) * (y - C0[1]) / (C1[1] - C0[1])
d.bar("strut", [CX, 50, 330], [CX, 560, cz(560) - 20], [50, 50], "frame", r=4)
d.box("plate", [CX - 85, 540, cz(560) - 60, CX + 85, 575, cz(560) + 10], "frame", r=5)
for s in (-1, 1):
    star_knob(d, f"pknob{s}", [CX + s * 85, 557, cz(560) - 25], "x", s, "black", dd=40, l=30)
yl = 800
d.decal("label", [CX, yl, cz(yl) - 30.8], [22, 300], "back", "blue", rot=rot("x", tilt, [CX, yl, cz(yl) - 30.8]))
# LCD counter on the top, tilted toward the user
LC = [CX, H - 40, 745]
d.box("lcd", [CX - 55, H - 80, 715, CX + 55, H, 775], "black", r=10, rot=rot("x", 25, LC))
d.screen("lcd-screen", [CX - 42, H - 70, 712, CX + 42, H - 18, 716], "black", face="back", r=4, rot=rot("x", 25, LC))
d.decal("lcd-btn", [CX, H - 76, 713], [30, 6], "back", "gloss#c83a2a", rot=rot("x", 25, LC))
# pedals on arms pivoting at the front, hydraulic cylinders up to the cross plate
d.cyl("axle", [CX - 150, 110, 640], [CX + 150, 110, 640], 30, "chrome")
d.box("pivot", [CX - 40, 55, 610, CX + 40, 135, 670], "frame", r=6)
for k, x, yr in (("l", CX - 110, 70), ("r", CX + 110, 215)):
    d.bar(f"parm-{k}", [x, 110, 640], [x, yr, 210], [40, 40], "frame", r=4)
    yp = lambda z: 110 + (yr - 110) * (640 - z) / 430
    d.bar(f"pedal-{k}", [x, yp(560) + 38, 560], [x, yp(240) + 38, 240], [125, 36], "pedal", r=8)
    d.bar(f"ptread-{k}", [x, yp(545) + 58, 545], [x, yp(255) + 58, 255], [105, 5], "rubber#2e3033", r=2)
    star_knob(d, f"pedknob-{k}", [x + (-1 if k == "l" else 1) * 62, yp(400) + 30, 400], "x", -1 if k == "l" else 1, "black",
              dd=30, l=24)
    # photo: each cylinder stands on a white bracket at the FRONT end of its pedal (just behind the pivot), nearly
    # upright, its chrome rod up to the end of the cross plate under the column top
    sg = -1 if k == "l" else 1
    top = [CX + sg * 70, 545, cz(560) - 30]
    bz = 585
    bot = [x + sg * 8, yp(bz) + 30, bz]
    d.box(f"pbr-{k}", [x + sg * 22 - 7, yp(bz) - 8, bz - 45, x + sg * 22 + 7, yp(bz) + 48, bz + 40], "frame", r=4)
    d.cyl(f"pbolt-{k}", [x + sg * 29, yp(bz) + 30, bz], [x + sg * 34, yp(bz) + 30, bz], 12, "grey", copies=[[0, -24, 26]])
    mid = [bot[i] + (top[i] - bot[i]) * 0.62 for i in range(3)]
    d.cyl(f"cyl-{k}", bot, mid, 46, "black")
    d.cyl(f"rod-{k}", mid, top, 16, "chrome")
d.save()
