from p1lib import *
d = D("xy-k-czld-ii", [700, 480, 200], {
  "lower": "plastic#e1e4e8", "upper": "gloss#eef0f2", "dark": "plastic#3a3f46", "groove": "plastic#4a4f56",
  "rib": "plastic#575d65", "line": "plastic#5b6168", "box": "metal#cdd1d6"})
CX, CZ = 350, 260
d.loft("lower", [sec(0, 670, 410, 140, CX, CZ), sec(12, 700, 440, 150, CX, CZ), sec(82, 700, 440, 150, CX, CZ),
                 sec(94, 676, 416, 142, CX, CZ)], "lower")
d.loft("groove", [sec(88, 652, 392, 136, CX, CZ), sec(110, 652, 392, 136, CX, CZ)], "groove")
d.loft("upper", [sec(104, 678, 418, 144, CX, CZ), sec(118, 700, 440, 150, CX, CZ), sec(160, 700, 440, 150, CX, CZ),
                 sec(178, 668, 408, 138, CX, CZ)], "upper")
d.loft("pad", [sec(170, 592, 332, 110, CX, CZ), sec(186, 588, 328, 108, CX, CZ)], "dark")
for i, (w, dd, r) in enumerate(((548, 292, 100), (494, 252, 90), (440, 212, 80), (386, 172, 70), (332, 134, 58), (278, 98, 46), (224, 64, 32), (170, 32, 16))):
    d.tube(f"ring-{i}", rr_path(CX, CZ, w, dd, r, 186), 6, "rib", soft=True)
for i, y in enumerate((30, 42)):
    d.tube(f"line-{i}", rr_path(CX, CZ, 701, 441, 150.5, y, 6), 3, "line", soft=True)
# ECG wave on the right half of the upper front: 4 tall beats, a gap with the "Sunnyou Body" print, 4 beats (review)
pts, x, Z = [[380, 141, 481]], 385, 481
for k in range(9):
    if k == 4:
        x += 70; pts.append([x, 141, Z]); continue
    pts += [[x, 141, Z], [x + 7, 141, Z], [x + 10, 128, Z], [x + 14, 168, Z], [x + 18, 120, Z], [x + 21, 141, Z]]
    x += 25
pts.append([x + 8, 141, Z])
d.tube("ecg", pts, 2.5, "line", soft=True)
d.decal("label", [522, 150, 480.8], [52, 5], "plastic#8a9099", soft=True)
# small silver control box at the rear with two buttons
d.box("ctrl", [50, 100, 0, 300, 205, 82], "box", r=18)
d.cyl("btn", [95, 203, 40], [95, 211, 40], 20, "plastic#9aa0a8", copies=[[160, 0, 0]])
d.save()
