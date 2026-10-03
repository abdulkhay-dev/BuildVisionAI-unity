# XYRT-13 free-standing ladder: dark-stained wood posts on long floor feet with braces, 8 lighter round rungs
from pd2_lib import *

W, D, H = 710, 530, 970
d = Design("xyrt-13", [W, D, H], {"wood": "wood#c4602a", "rung": "wood#dea050", "brace": "wood#c8904e",
                                    "label": "plastic#eef2ee"})
ZC = 175
for nm, xc in (("l", 50), ("r", W - 50)):
    # long floor foot with rounded ends
    d.box(f"foot-{nm}", [xc - 24, 0, 0, xc + 24, 48, D], "wood", r=10)
    # post with a chamfered top
    d.box(f"post-{nm}", [xc - 26, 46, ZC - 22, xc + 26, H - 6, ZC + 22], "wood", r=4)
    d.box(f"post-top-{nm}", [xc - 24, H - 10, ZC - 20, xc + 24, H, ZC + 20], "wood", r=8)
    # triangular braces in front of and behind the post
    tri = svg_poly([(ZC + 22, 48), (ZC + 112, 48), (ZC + 22, 168)])
    d.slab(f"brace-f-{nm}", "side", tri, [xc - 14, xc + 14], "brace", r=3)
    tri2 = svg_poly([(ZC - 22, 48), (ZC - 112, 48), (ZC - 22, 168)])
    d.slab(f"brace-b-{nm}", "side", tri2, [xc - 14, xc + 14], "brace", r=3)
# 8 round rungs
d.cyl("rung", [76, 158, ZC], [W - 76, 158, ZC], 24, "rung", repeat=rep(8, [0, 102, 0]))
d.box("label", [W / 2 - 16, 870, ZC + 12, W / 2 + 16, 884, ZC + 14], "label", r=2, soft=True)
d.save()
