"""sound-and-light-wall-panel: light-pink bear-ear wall panel with a white LED-dot equaliser display."""
import colorsys
from s2lib import *

W, H, T = 590, 900, 90
d = D("sound-and-light-wall-panel", [W, T, H], {
    "case": "plastic#e0b4d3", "dark": "plastic#cfa0bf", "grille": "plastic#b886a8"})
# measured on the photo (243 px over the ears = 590 mm): ears r 87 centred (87, 813), body 24..566 up to 880
panel(d, W, H, T, "case", inset=24, ear_c=(87, 813), ear_r=87, yt=880, grille="grille", grille_d=60,
      grille_off=(-29, 34), bumps=(29, 6, 143, 113), logo=(305, 851), logo_d=44,
      buttons=([223, 298, 372], 62, 33), case_dark="dark")
# black bezel and the light-grey display (darker at the top, as on the photo: 213 → 228 grey)
d.add("bezel", "slab", "black#141416", plane="front", box=[74, 118, T - 2, 516, 822, T + 5], radii=[16], r=3)
greys = ["dadbdb", "dddfde", "e1e2e2", "e4e5e5", "e7e8e8", "eaebeb"]
y_lo, y_hi = 135, 803
for i, g in enumerate(greys):                      # 6 bands from the top down, each a hair lower in z
    yb = y_hi - (y_hi - y_lo) * (i + 1) / len(greys) if i < len(greys) - 1 else y_lo
    d.box(f"display{i}", [90, yb, T + 3, 500, y_hi - (y_hi - y_lo) * i / len(greys), T + 6 - i * 0.05],
          "gloss#" + g, soft=i > 0)
F = T + 6
# LED dots (round, Ø 12): 24 columns on a 16.6 mm pitch. Bottom 7 rows full rainbow colour (left → right: blue,
# cyan, green, yellow, orange, red, magenta, violet); above them the column's colour darkened; the top 2-3 black.
heights = [8, 12, 15, 19, 15, 19, 14, 10, 17, 10, 14, 10, 21, 15, 8, 11, 8, 12, 11, 21, 15, 8, 11, 6]
x0, y0, p, s = 104, 150, 16.6, 12
for i, h in enumerate(heights):
    x = x0 + i * p + s / 2
    hue = (235 - i * 300 / 23) % 360 / 360
    r, g, b = colorsys.hsv_to_rgb(hue, 0.88, 0.95)
    col = "gloss#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))
    r2, g2, b2 = colorsys.hsv_to_rgb(hue, 0.75, 0.38)
    dim = "gloss#%02x%02x%02x" % (int(r2 * 255), int(g2 * 255), int(b2 * 255))
    yc = y0 + s / 2
    n_col = min(h, 7)
    n_blk = 0 if h <= 7 else (2 if h < 12 else 3)
    n_dim = max(0, h - n_col - n_blk)
    d.cyl(f"led{i}", [x, yc, F - 0.5], [x, yc, F + 0.8], s, col, sides=12, soft=True, repeat=rep(n_col, [0, p, 0]))
    if n_dim:
        d.cyl(f"led{i}-dim", [x, yc + n_col * p, F - 0.5], [x, yc + n_col * p, F + 0.8], s, dim, sides=12,
              soft=True, repeat=rep(n_dim, [0, p, 0]))
    if n_blk:
        y1 = yc + (n_col + n_dim) * p
        d.cyl(f"led{i}-blk", [x, y1, F - 0.5], [x, y1, F + 0.8], s, "black#121214", sides=12, soft=True,
              repeat=rep(n_blk, [0, p, 0]))
d.save()
