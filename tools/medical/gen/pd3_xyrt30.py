"""xyrt-30 — fabric crawl tunnel with a patchwork print, Ø800 × 5200, along x on the floor.
The spiral wire pinches the fabric every ~270 mm: each segment between two wires is a puffy band. Every band is
made of 8 curved panels (sweeps along an arc with an oval section: thick in the middle, thin at the wires), so the
silhouette is scalloped as in the photo. The panels follow the photo's patchwork in diagonal runs: pale yellow,
white with flowers, grey-blue fine check (a plain grey-blue: the library check textures are far too dark and
can only be tinted darker), light blue."""
import math
from pd3_lib import *

W, Dp, H = 5200, 800, 800
d = D("xyrt-30", [W, Dp, H], {"yel": "fabric#efdc94", "flo": "fabric#f1f0ea", "chk": "fabric#c6cbd5",
                              "blu": "fabric#d2dbf0", "hem": "fabric#d9dce4",
                              "or": "fabric#e8743a", "gr": "fabric#86b46e", "rd": "fabric#d8473c"})
R = 400
cy = cz = 400
HEM = 26
NSEG = 19
P = (W - 2 * HEM) / NSEG          # band length (wire pitch)
TH = 30                           # band puff (oval section height)
rm = R - TH / 2                   # path radius: the oval's outer apex touches R
NCOL = 8
pattern = ["yel", "flo", "chk", "blu"]
for j in range(NCOL):
    a0, a1 = j * 360 / NCOL, (j + 1) * 360 / NCOL
    path = []
    for k in range(7):
        a = math.radians(a0 + (a1 - a0) * k / 6)
        path.append([0, cy + rm * math.cos(a), cz + rm * math.sin(a)])
    for m, mat in enumerate(pattern):
        i0 = (m - j) % 4                     # diagonal runs of the patchwork
        n = len(range(i0, NSEG, 4))
        if n == 0: continue
        x = HEM + P * (i0 + 0.5)
        d.sweep(f"pan-{j}-{mat}", [[x, p[1], p[2]] for p in path], [P, TH], mat, shape="oval",
                repeat={"n": n, "step": [4 * P, 0, 0]})
# the print's small coloured motifs (flowers, figures) on the light panels: little patches at the band apex
for j in range(NCOL):
    am = math.radians((j + 0.5) * 360 / NCOL)
    for m, (mat, off, w, h) in enumerate((("or", -40, 46, 40), ("gr", 30, 40, 52), ("rd", 10, 30, 28))):
        i0 = (j * 3 + m * 2) % 4
        n = len(range(i0, NSEG, 4))
        x = HEM + P * (i0 + 0.5) + off
        R2 = rot("x", math.degrees(am), [0, cy, cz])
        aa = math.radians((m - 1) * 9)
        d.box(f"mot-{j}-{m}", [x - w / 2, cy + R - 2.5, cz - h / 2 + 60 * math.sin(aa), x + w / 2, cy + R + 0.5,
                               cz + h / 2 + 60 * math.sin(aa)], mat, soft=True, rot=R2,
              repeat={"n": n, "step": [4 * P, 0, 0]})
# hems at the open ends (the wire's last turn)
for nm, x in (("l", 0), ("r", W - HEM)):
    d.lathe(f"hem-{nm}", [x, cy, cz], [[R - 30, 0], [R - 6, 0], [R, HEM / 2], [R - 6, HEM], [R - 30, HEM], [R - 30, 0]],
            "hem", axis="x", caps=False, sides=56)
d.save()
