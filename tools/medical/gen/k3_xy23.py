"""XY-23 exercise device (mini basketball stand), kinesio-3."""
from k3_lib import *

W, Dd, H = 600, 450, 1060
d = D("xy-23", [W, Dd, H], {"base": "plastic#c9cbca", "top": "plastic#eceeee", "post": "chrome",
                            "orange": "gloss#ea5a1c", "rope": "plastic#efefe9"})
# grey D-shaped floor base: flat back, rounded front, 45 thick
BD = 190
d.slab("base", "top", f"M 0 0 L {W} 0 L {W} {BD - 110} Q {W} {BD} {W - 150} {BD} L 150 {BD} Q 0 {BD} 0 {BD - 110} Z",
       [0, 45], "base", r=8)
d.decal("base-lbl", [W / 2, 25, BD + 0.5], [36, 16], "gloss#2f5fb8", face="front", soft=True)
d.decal("base-hole", [W / 2 - 200, 25, BD - 2], [8, 8], "plastic#55585c", face="front", soft=True, copies=[[400, 0, 0]])
# white flat top bar, same plan shape, thinner
d.slab("top", "top", f"M 0 0 L {W} 0 L {W} {BD - 120} Q {W} {BD - 20} {W - 150} {BD - 20} L 150 {BD - 20} Q 0 {BD - 20} 0 {BD - 120} Z",
       [H - 32, H], "top", r=6)
for k in range(3):
    d.cyl(f"screw{k}", [W / 2 - 200 + 200 * k, H, 60], [W / 2 - 200 + 200 * k, H + 3, 60], 12, "metal#9a9da2")
# two chrome uprights
XU = [152, 448]
ZU = 70
for k, x in enumerate(XU):
    d.cyl(f"post{k}", [x, 45, ZU], [x, H - 32, ZU], 26, "post")
# pulley under the top bar (black wheel in a fork) and the rope
d.box("pfork", [W / 2 - 22, H - 110, ZU - 16, W / 2 + 22, H - 32, ZU + 16], "chrome", r=4)
d.add("pwheel", "wheel", "plastic#1d1e20", at=[W / 2, H - 85, ZU + 2], d=70, d2=22, axis="x")
BY0, BY1 = 400, 662          # backboard
BZ0, BZ1 = ZU + 18, ZU + 46
d.cyl("rope-a", [W / 2 - 34, H - 85, ZU + 2], [W / 2 - 34, BY1, ZU + 2], 7, "rope", soft=True)
d.cyl("rope-b", [W / 2 + 34, H - 85, ZU + 2], [W / 2 + 34, 300, ZU + 2], 7, "rope", soft=True)
d.tube("rope-c", [[W / 2 + 34, 300, ZU + 2], [W / 2 + 60, 140, ZU + 20], [W / 2 + 90, 45, ZU + 40]], 7, "rope", bend=60, soft=True)
d.box("cleat", [W / 2 + 70, 45, ZU + 25, W / 2 + 110, 60, ZU + 55], "chrome", r=4)
# orange backboard sliding on the uprights (sleeves behind it)
d.box("board", [W / 2 - 168, BY0, BZ0, W / 2 + 168, BY1, BZ1], "orange", r=6)
for k, x in enumerate(XU):
    d.box(f"slv{k}", [x - 16, BY0 + 30, ZU - 20, x + 16, BY1 - 30, ZU + 20], "plastic#d65a1c", r=6)
# hoop: orange ring with the bracket, hooks
HY = BY0 + 32
R = 185
HC = [W / 2, HY, BZ1 + 20 + R]
d.tube("hoop", ring(HC[0], HY, HC[2], R, R, "xz", 32), 18, "orange")
d.box("hbr", [W / 2 - 60, HY - 70, BZ1, W / 2 + 60, HY + 10, BZ1 + 12], "orange", r=4)
d.bar("hbr2", [W / 2 - 40, HY - 60, BZ1 + 6], [W / 2 - 25, HY, BZ1 + 40], [10, 16], "orange", r=2, copies=[[50, 0, 0]])
for k in range(12):
    a = 2 * math.pi * k / 12
    d.box(f"hook{k}", [HC[0] + R * math.cos(a) - 6, HY - 22, HC[2] + R * math.sin(a) - 6,
                        HC[0] + R * math.cos(a) + 6, HY - 4, HC[2] + R * math.sin(a) + 6], "orange", r=2)
# (review) photo: thick cord, a looser and finer mesh that gathers to a narrow red bottom
net(d, "net", [HC[0], HY - 12, HC[2]], R - 8, 38, 330, n=12, rows=8, white=0.42, d_=9, pw=1.3, sag=0.5)
d.save()
