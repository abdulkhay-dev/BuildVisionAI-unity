"""smell-perception-game-box: pink bear-ear wall panel with a raised inner panel, scent outlets and colour keys."""
from s2lib import *

W, H, T = 620, 900, 120
d = D("smell-perception-game-box", [W, T, H], {
    "case": "plastic#d286b8", "dark": "plastic#bd5e9a", "grille": "plastic#b06696"})
# measured on the photo (254 px over the ears = 620 mm, x = (px - 1) * 2.44): ears r 90 at (90, 810), body top 873
panel(d, W, H, T, "case", inset=27, ear_c=(90, 810), ear_r=90, yt=873, grille="grille", grille_d=58,
      grille_off=(-24, 29), bumps=(29, 6, 143, 113), logo=(316, 845), logo_d=40,
      buttons=([216, 293, 371], 65, 33), case_dark="dark")
F = T + 8   # front of the raised inner panel
# raised inner panel: two darker pink lines on the photo (the lip's outer edge at x 87 / 531, y 128 / 808 and the
# groove at x 101 / 516, y 141 / 796)
d.add("panel-edge", "slab", "dark", plane="front", box=[84, 125, T - 1, 534, 811, T + 2.5], radii=[20], r=1)
d.add("panel-lip", "slab", "case", plane="front", box=[88, 129, T - 1, 530, 807, T + 4], radii=[18], r=2)
d.add("panel-groove", "slab", "dark", plane="front", box=[97, 137, T + 3, 520, 800, T + 5], radii=[12], r=1)
d.add("panel", "slab", "case", plane="front", box=[103, 143, T + 4, 514, 794, F], radii=[10], r=3)
# column of 5 small dots: 4 dark red, the last dark blue
d.cyl("dot", [156, 658, F - 1], [156, 658, F + 2.5], 20, "gloss#7a1a22", copies=[[0, -97, 0], [0, -190, 0], [0, -290, 0]])
d.cyl("dot-b", [156, 275, F - 1], [156, 275, F + 2.5], 20, "gloss#1e2a78")
# vertical light strip: dark red edge, red / yellow / green stripes
d.box("strip", [222, 256, F - 1, 256, 675, F + 2], "gloss#7a1a22", r=1)
for i, c in enumerate(["gloss#b81820", "gloss#e8d40a", "gloss#159548"]):
    d.box(f"strip{i}", [224 + i * 10, 258, F + 1, 224 + (i + 1) * 10 - 0.6, 673, F + 3], c, soft=True)
# 4 square keys and 4 white scent outlets
ys = [650, 527, 405, 284]
for i, (y, c) in enumerate(zip(ys, ["gloss#8f1d26", "gloss#1e2a96", "gloss#c9a6da", "gloss#8fd6e8"])):
    d.box(f"key{i}", [310, y - 26.5, F - 1, 364, y + 26.5, F + 5], c, r=3)
    d.lathe(f"scent{i}", [448, y, F - 1], [[0, 0], [28, 0], [28, 3], [25, 5], [0, 5.5]], "gloss#f3f4f6", axis="z")
d.save()
