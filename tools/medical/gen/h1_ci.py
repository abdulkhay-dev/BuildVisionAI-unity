from h1lib import *
# XY-SL-CI butterfly (Hubbard) tub: figure-8 white tub (lobes at both ends, narrow waist), rounded rim with a seam under
# it, smooth vertical skirt; control box at the left end with the oval control panel, two buttons, arched panel line and
# logo on its end face; white slatted body support inside (leg plate + inclined backrest + armrest), 10 chrome jets.
d = D("xy-sl-ci", [2400, 1850, 950], {
    "shell": "gloss#f8f9fa", "inner": "gloss#f0f3f5", "seam": "plastic#e1e5e9", "insert": "plastic#f4f4f2",
    "slot": "plastic#8e959c", "blue": "gloss#2f7fd8", "grey": "plastic#b9c0c8"})
CZ = 925
def hw(t):
    base = max(0.0, 1 - abs(2 * t - 1) ** 3) ** (1 / 3)
    lobe = 1 - 0.33 * math.exp(-((t - 0.52) / 0.15) ** 2)
    return 925 * base * lobe * (0.90 + 0.10 * t)
outer = profile_outline(330, 2400, hw, CZ, n=90)
RY, RT = 850, 100
d.slab("skirt", "top", ring(offset(outer, -16), offset(outer, -70)), [0, RY + 2], "shell", r=24)
d.slab("seam", "top", ring(offset(outer, -10), offset(outer, -40)), [812, 830], "seam", r=6, soft=True)
hole = offset(outer, -140)
tub(d, "", None, hole, outer, RY, RT, 330, offset(outer, -80), rim_r=45)
# white slatted support: leg plate (left lobe) and seat pan just below the rim, inclined backrest rising to rim height
# in the right lobe, armrest bar at the back of the seat. Review 2026-10-02: raised from 520 to ~700 (photo: the plates
# sit just below the rim), slots longer and darker (they read as through-slots), seat pan added.
d.box("leg-plate", [560, 680, 700, 1120, 725, 1150], "insert", r=20)
d.box("leg-slot", [640, 724, 800, 664, 728, 1050], "slot", r=8, repeat=rep(5, [100, 0, 0]), soft=True)
d.box("seat-pan", [1110, 700, 700, 1300, 750, 1150], "insert", r=20)
d.box("seat-slot", [1160, 749, 820, 1182, 753, 1030], "slot", r=8, copies=[[70, 0, 0]], soft=True)
br = rot("z", 22, [1290, 730, CZ])
d.box("backrest", [1290, 705, 690, 1990, 760, 1160], "insert", r=30, rot=br)
for i in range(6):
    d.box(f"back-slot{i}", [1380 + 100 * i, 759, 790, 1402 + 100 * i, 763, 1060], "slot", r=8, rot=br, soft=True)
d.box("back-leg", [1700, 330, 760, 1740, 860, 1090], "insert", r=10)
d.box("leg-support", [700, 330, 760, 740, 685, 1090], "insert", r=10, copies=[[380, 0, 0]])
d.cyl("armrest", [1080, 830, 690], [1420, 870, 660], 70, "insert")
# jets on the inner walls
for i, t in enumerate((0.08, 0.16, 0.26, 0.33, 0.42, 0.58, 0.66, 0.74, 0.84, 0.92)):
    k = int(t * len(hole)) % len(hole)
    x, z = hole[k]
    d.sphere(f"jet{i}", [x, 640 - 60 * (i % 2), z], None, "chrome", radii=[26, 26, 26])
# control box at the left end
d.box("ctrl-box", [15, 0, 350, 470, 950, 1500], "shell", r=40)
d.add("panel", "screen", box=[30, 946, 782, 450, 956, 1068], r=60, face="top", bezel=0, mat="grey",
      print="med_xy-sl-ci_screen", rot=rot("y", -90, [240, 950, 925]))
d.lathe("btn", [240, 950, 560], [[0, 0], [30, 0], [30, 8], [20, 14], [0, 14]], "chrome", copies=[[0, 0, 730]])
d.lathe("btn-cap", [240, 960, 560], [[0, 0], [20, 0], [20, 6], [0, 6]], "blue", copies=[[0, 0, 730]], soft=True)
arch_o = "M 470 60 L 470 430 Q 470 700 925 700 Q 1380 700 1380 430 L 1380 60 Z"
arch_i = "M 484 60 L 484 430 Q 484 686 925 686 Q 1366 686 1366 430 L 1366 60 Z"
d.slab("arch", "side", arch_o + " " + arch_i, [8, 18], "seam", r=2, soft=True)
from p1lib import text
text(d, "logo-t", "翔宇", [14, 300, 610], 55, "blue", face="left", stroke=8)
d.lathe("logo", [14, 330, 560], [[0, 0], [32, 0], [32, 3], [0, 3]], "blue", axis="x", rot=rot("y", 180, [14, 330, 560]), soft=True)
d.save()
