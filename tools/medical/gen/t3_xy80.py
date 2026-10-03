# XY-80 nesting stools, set of 5 stored nested (front edges aligned) - table-3 batch
from lib import *
d = D("xy-80", [550, 380, 610], {
  "ply": "wood#e3cfa6", "veneer": "wood#f2b46e", "leg": "plastic#9aa3ad", "foot": "rubber#1c1d20", "tag": "metal#c9ccd0"})
sizes = [(550, 380, 610), (500, 350, 510), (450, 320, 410), (400, 290, 310), (350, 250, 210)]
W, Dd = 550, 380
TH = 22   # plywood top
for i, (w, dp, h) in enumerate(sizes):
    x0 = (W - w) / 2; x1 = x0 + w; z1 = Dd; z0 = z1 - dp
    s = f"s{i+1}"
    d.box(s + "-top", [x0, h - TH, z0, x1, h - 3, z1], "ply", r=2)
    d.box(s + "-veneer", [x0, h - 3, z0, x1, h, z1], "veneer", r=1.5)
    # ply lines on the edge
    d.box(s + "-ply", [x0 - 0.5, h - 14, z0 - 0.5, x1 + 0.5, h - 12, z1 + 0.5], "veneer", soft=True)
    # front and back: an inverted U of grey tube along the width, bent at the top corners (photo)
    lx = x0 + 20; rx = x1 - 20; zf = z1 - 20; zb = z0 + 20; yt = h - TH - 12
    d.tube(s + "-leg", [[lx, 25, zf], [lx, yt, zf], [rx, yt, zf], [rx, 25, zf]], 25, "leg", bend=45,
           copies=[[0, 0, zb - zf]])
    d.cyl(s + "-foot", [lx, 0, zf], [lx, 32, zf], 30, "foot",
          copies=[[rx - lx, 0, 0], [0, 0, zb - zf], [rx - lx, 0, zb - zf]])
d.cyl("tag", [W - 45, 610, Dd - 40], [W - 45, 611.5, Dd - 40], 22, "tag", soft=True)
d.save()
