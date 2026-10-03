"""visual-perceptual-trainer: 3 short white and 2 tall pink glowing tubes on round light bases, and a colour light cube."""
from s2lib import *

W, Dp, H = 1450, 650, 1420
d = D("visual-perceptual-trainer", [W, Dp, H], {
    "white": "acrylic#c4d4ffb8", "pink": "acrylic#f070c8b0", "disc": "acrylic#e6eeffa8"})
def tube(id, x, z, dia, h, mat, core="led"):
    d.cyl(id + "-disc", [x, 0, z], [x, 18, z], 300, "disc")
    d.cyl(id + "-glow", [x, 2, z], [x, 16, z], 220, "led", soft=True)
    d.cyl(id, [x, 18, z], [x, 18 + h, z], dia, mat, sides=40)
    d.cyl(id + "-core", [x, 30, z], [x, 18 + h - 25, z], dia * 0.8, core, soft=True)
    # the photo's bright white glow at the foot of each tube
    d.cyl(id + "-foot", [x, 18, z], [x, 120, z], dia + 1, "led", soft=True)
    d.cyl(id + "-rim", [x, 18 + h - 4, z], [x, 18 + h + 2, z], dia + 2, "acrylic#ffffffe0", soft=True)
# back row: two tall pink tubes; front row: three short white-blue tubes
for i, x in enumerate((300, 640)):
    # the photo makes the tall tubes ≈ 7.6 x their diameter (≈ 1400), the short ones ≈ 6.2 x (≈ 900)
    tube(f"tall{i}", x, 200, 180, H - 20, "pink", core="gloss#f7a6dc")
for i, x in enumerate((150, 470, 790)):
    tube(f"short{i}", x, 470, 150, 900, "white")
# light cube: a glowing core whose edges show between coloured face plates
x0, z0, s = 1040, 160, 400
d.box("cube", [x0, 0, z0, x0 + s, s, z0 + s], "led", r=6)
e = 9
d.box("cube-top", [x0 + e, s - 1, z0 + e, x0 + s - e, s + 1.5, z0 + s - e], "gloss#a8202c", r=2)
d.box("cube-front", [x0 + e, e, z0 + s - 1, x0 + s - e, s - e, z0 + s + 1.5], "gloss#2f6ee0", r=2)
d.box("cube-back", [x0 + e, e, z0 - 1.5, x0 + s - e, s - e, z0 + 1], "gloss#2f6ee0", r=2)
d.box("cube-right", [x0 + s - 1, e, z0 + e, x0 + s + 1.5, s - e, z0 + s - e], "gloss#c06ccc", r=2)
d.box("cube-left", [x0 - 1.5, e, z0 + e, x0 + 1, s - e, z0 + s - e], "gloss#c06ccc", r=2)
d.save()
