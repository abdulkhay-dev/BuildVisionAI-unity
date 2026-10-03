# XYRT-17 wooden bed / balance bench: 12 lengthwise slats between full-height side aprons and end boards,
# 4 square legs with knee braces under the aprons, a small oval label on the front apron near the right end
from pd2_lib import *

W, D, H = 1500, 650, 430
d = Design("xyrt-17", [W, D, H], {"wood": "wood#e0aa52", "slat": "wood#e8bd6c", "label": "metal#d6d9dc"})
AH = 75                                    # apron height
# side aprons (front, back) and end boards, flush with the top
wbox(d, "apron-f", [0, H - AH, D - 28, W, H, D], "wood", r=4)
wbox(d, "apron-b", [0, H - AH, 0, W, H, 28], "wood", r=4)
d.box("end-l", [0, H - AH, 28, 30, H, D - 28], "wood", r=4)
d.box("end-r", [W - 30, H - AH, 28, W, H, D - 28], "wood", r=4)
# 12 slats along the length, slightly below the top of the frame
n, sw = 12, 36
gap = (D - 56 - n * sw) / (n + 1)
# (drawn along z and turned 90 deg so the wood grain runs along the slat)
zc = 28 + gap + sw / 2
d.box("slat", [W / 2 - sw / 2, H - 30, zc - (W - 60) / 2, W / 2 + sw / 2, H - 8, zc + (W - 60) / 2], "slat", r=3,
      rot=rot("y", 90, [W / 2, H, zc]), repeat=rep(n, [0, 0, sw + gap]))
d.box("bearer", [380, H - 54, 28, 420, H - 30, D - 28], "wood", r=2, copies=[[350, 0, 0], [700, 0, 0]])
# legs and knee braces (along the length, under the front/back aprons)
L = 55
for nm, x0, s in (("l", 0, 1), ("r", W - L, -1)):
    for zn, z0 in (("b", 0), ("f", D - L)):
        d.box(f"leg-{nm}{zn}", [x0, 0, z0, x0 + L, H - AH + 2, z0 + L], "wood", r=3)
        xi = x0 + L if s > 0 else x0
        tri = svg_poly([(xi, H - AH + 1), (xi + s * 70, H - AH + 1), (xi, H - AH - 70)])
        d.slab(f"knee-{nm}{zn}", "front", tri, [z0 + 8, z0 + L - 8], "wood", r=2)
# small oval label on the front apron near the right end (as in the photo)
d.slab("label", "front", svg_poly(ellipse_pts(W - 95, H - 38, 30, 14, n=28)), [D, D + 1.5], "label", r=0.5, soft=True)
d.save()
