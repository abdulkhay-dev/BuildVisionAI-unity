# XY-K-SWY-II forced-air patient warmer: white box, black glass front with the printed UI, top arch handle, hose — other-1
import math
from o_lib import *

BW, BD = 370, 420          # body width / depth
X0 = 400                   # body left (the hose lies to the left of it)
FY = 28                    # feet height
TOP = FY + 378             # body top
PB = 120                   # bottom of the black panel
d = D("xy-k-swy-ii", [X0 + BW, 445, 482], {
    "shell": "plastic#eceef1", "glass": "gloss#18191d", "grey": "plastic#9a9fa6", "foot": "rubber#1b1c1e",
    "hose": "plastic#e3e5e8", "cuff": "plastic#f1f2f4"})
X1 = X0 + BW
cx = X0 + BW / 2
# body: side profile (z, y) — small top-front radius, big top-back, the front rolls under with a big radius
prof = rr4(0, FY, BD, TOP, 40, 90, 22, 70)   # corners: (z0,yb) (z1,yb) (z1,yt) (z0,yt)
d.slab("body", "side", prof, [X0, X1], "shell", r=14)
# black glass front panel = the printed screen (logo, titles, 10.5" UI, company line)
d.add("panel-back", "box", "glass", box=[X0 + 6, PB, BD - 4, X1 - 6, PB + 60, BD + 2], r=2)
screen(d, "panel", [X0 + 6, PB, BD - 2, X1 - 6, TOP - 6, BD + 3], "glass", r=40, face="front", print="med_xy-k-swy-ii_screen", bezel=0)
# the panel's top corners are rounded (photo 1/3, r ≈ 34): body-white corner fillers just in front of the picture
RC = 34
for k, (xc, sx) in enumerate(((X0 + 6, 1), (X1 - 6, -1))):
    yc = TOP - 6
    pts = [(xc, yc - RC - 1), (xc, yc + 1), (xc + sx * (RC + 1), yc + 1)]
    for i in range(9):
        a = math.pi / 2 * i / 8
        pts.append((xc + sx * (RC - RC * math.sin(a)), yc - RC + RC * math.cos(a)))
    d.slab(f"panel-corner{k}", "front", poly(pts), [BD + 3, BD + 4.5], "shell", soft=True)
# the picture is straightened to the frontal photo 3 (scratch/other-1-review/swy_screen.py): no mask needed
# carry handle (photo 2): a bridge along the depth whose legs flare into the top with big fillets; arch opening
# across x with grey inner faces; grey well in the top under it
T = TOP
arch = (f"M 70 {T - 10} L 70 {T - 2} Q 120 {T + 2} 122 {T + 40} Q 124 {T + 80} 165 {T + 80} L 285 {T + 80} "
        f"Q 326 {T + 80} 328 {T + 40} Q 330 {T + 2} 380 {T - 2} L 380 {T - 10} L 300 {T - 10} L 300 {T + 28} "
        f"Q 300 {T + 50} 278 {T + 50} L 172 {T + 50} Q 150 {T + 50} 150 {T + 28} L 150 {T - 10} Z")
HW = 58
d.slab("handle", "side", arch, [cx - HW, cx + HW], "shell", r=12)
band = (f"M 147 {T - 6} L 147 {T + 28} Q 147 {T + 53} 172 {T + 53} L 278 {T + 53} Q 303 {T + 53} 303 {T + 28} "
        f"L 303 {T - 6} L 297 {T - 6} L 297 {T + 28} Q 297 {T + 47} 278 {T + 47} L 172 {T + 47} Q 153 {T + 47} 153 {T + 28} "
        f"L 153 {T - 6} Z")
d.slab("handle-in", "side", band, [cx - HW + 9, cx + HW - 9], "grey", soft=True)
d.box("handle-well", [cx - HW + 9, TOP - 6, 150, cx + HW - 9, TOP + 1, 300], "grey", r=4)
# feet: black round feet with a dark grey disc
d.cyl("foot", [X0 + 46, FY, 44], [X0 + 46, 6, 44], 40, "foot", copies=[[BW - 92, 0, 0], [0, 0, BD - 88], [BW - 92, 0, BD - 88]])
d.cyl("foot-disc", [X0 + 46, 8, 44], [X0 + 46, 0, 44], 36, "plastic#6b625c", d2=46,
      copies=[[BW - 92, 0, 0], [0, 0, BD - 88], [BW - 92, 0, BD - 88]])
# air hose: white coupling on the left side at mid height, corrugated hose on the table to the front-left, cuff nozzle
HY, HZ = 215, 210
d.add("coupling", "lathe", "cuff", at=[X0 - 46, HY, HZ], axis="x",
      profile=[[0, 0], [40, 0], [44, 6], [44, 40], [48, 42], [48, 46], [0, 46]])
path = [[X0 - 46, HY, HZ], [X0 - 100, HY - 20, HZ + 15], [X0 - 200, 44, HZ + 90], [X0 - 280, 48, HZ + 140]]
d.tube("hose", path, 72, "hose", bend=110, rib=4, pitch=13)
ux, uz = -0.82, 0.57
a = [X0 - 280, 48, HZ + 140]
b = [a[0] + ux * 105, 48, a[2] + uz * 105]
d.cyl("nozzle", a, b, 84, "cuff")
d.cyl("nozzle-ring", lerp(a, b, 0.25), lerp(a, b, 0.42), 96, "cuff")
d.cyl("nozzle-end", b, [b[0] + ux * 3, 48, b[2] + uz * 3], 70, "plastic#55595f", soft=True)
d.save()
print("hose end", b)
