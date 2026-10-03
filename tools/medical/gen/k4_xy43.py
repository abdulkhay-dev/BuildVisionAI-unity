from k4lib import *
d = K("xy-43", [540, 450, 740], {"white": "plastic#f0efe9", "ball": "gloss#1b1c1f", "cap": "rubber#1b1c1e", "stick": "gloss#e2782a"})
ZB, ZT, H = 392, 262, 740           # rail z at the bottom / top (leaning back), height
zr = lambda y: ZB + (ZT - ZB) * y / H
# --- U-shaped floor base (closed bend on the left), gusset plate at the right end, black feet
d.tube("base", [[505, 17, 70], [40, 17, 70], [40, 17, 395], [505, 17, 395]], 32, "white", bend=150)
# side plate with an arched top joining the runners' open ends and the right rail foot (photo: compact, rounded)
d.slab("gusset", "side", rpoly([(150, 0), (418, 0), (418, 125), (370, 160), (280, 160), (200, 120), (150, 50)], 30), [500, 508], "white", r=2)
d.box("foot", [20, 0, 50, 60, 6, 90], "cap", r=2, copies=[[0, 0, 325], [465, 0, 0], [465, 0, 325]])
# --- side rails leaning back, top bar with logo, black caps
for nm, x in (("l", 30), ("r", 510)):
    d.bar(f"rail-{nm}", [x, 0, ZB], [x, H - 8, ZT], [32, 32], "white", r=4)
    d.box(f"rail-cap-{nm}", [x - 17, H - 10, ZT - 17, x + 17, H, ZT + 17], "cap", r=3)
d.bar("top-bar", [30, H - 26, zr(H - 26)], [510, H - 26, zr(H - 26)], [32, 32], "white", r=4)
# oval logo on the top bar: white oval with a blue ring, blue "XY" mark with a red dot
zl = zr(H - 26) + 16
d.sphere("logo", [270, H - 26, zl], None, "gloss#3d5fb8", radii=[26, 12.5, 1.2], soft=True)
d.sphere("logo-in", [270, H - 26, zl + 0.4], None, "gloss#f7f7f7", radii=[23.5, 10.2, 1.2], soft=True)
text(d, "logo-t", "XY", [262, H - 30.5, zl + 1.8], 9, "gloss#3d5fb8", stroke=1.6)
d.sphere("logo-dot", [281, H - 26, zl + 1.4], None, "gloss#d83030", radii=[2.5, 2.5, 0.6], soft=True)
# --- black ball pegs on white pins up the front of each rail (~105 apart)
STEP = [0, 105, (ZT - ZB) * 105 / H]
for nm, x in (("l", 30), ("r", 510)):
    y0 = 160; zf = zr(y0) + 16
    d.cyl(f"pin-{nm}", [x, y0, zf - 4], [x, y0, zf + 32], 12, "white", repeat=rep(6, STEP))
    d.sphere(f"ball-{nm}", [x, y0, zf + 46], 36, "ball", repeat=rep(6, STEP))
y = 95; zf = zr(y) + 16
d.cyl("pin-extra", [510, y, zf - 4], [510, y, zf + 32], 12, "white")
d.sphere("ball-extra", [510, y, zf + 46], 36, "ball")
# --- orange wooden stick Ø30 × 920 resting on the second pegs from the top
ys = 160 + 4 * 105
d.cyl("stick", [-170, ys + 21, zr(ys) + 16 + 18], [750, ys + 21, zr(ys) + 16 + 18], 30, "stick")
d.save()
