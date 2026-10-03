from lib import *
from p2util import *
import math
# slim white cart (2 drawers, white screen head) + the blue spine electrode board in an acrylic stand on its right
d = D("xy-k-zpjz-ii", [930, 570, 1260], {"shell": "plastic#f4f5f7", "dark": "plastic#4d5259", "line": "plastic#1f2226",
      "black": "gloss#141517", "deck": "plastic#c3c7cc", "board": "plastic#6cc0ea", "sil": "plastic#8a9099",
      "pad": "rubber#1c1d20", "acryl": "acrylic#e8f2f8a0"})
X0, X1, Z0, Z1, YB, YT = 20, 400, 20, 440, 130, 958
# H base, posts, castors
d.box("rail", [12, 104, 0, 48, 130, 460], "dark", r=12, copies=[[360, 0, 0]])
d.box("cross", [40, 106, 210, 380, 128, 250], "dark", r=10)
d.box("post", [16, 98, 6, 44, 132, 34], "dark", r=6, copies=[[360, 0, 0], [0, 0, 420], [360, 0, 420]])
d.add("castor", "caster", "rubber#e4e6e9", at=[30, 0, 28], d=75, copies=[[360, 0, 0], [0, 0, 420], [360, 0, 420]])
# cabinet, drawers, side logo
d.box("cabinet", [X0, YB, Z0, X1, YT, Z1], "shell", r=14)
for i, (y0, y1) in enumerate(((782, 905), (588, 774))):
    d.box(f"drawer{i}-line", [58, y0 - 3, Z1, 362, y1 + 3, Z1 + 1], "line", r=10)
    d.box(f"drawer{i}", [61, y0, Z1, 359, y1, Z1 + 3], "shell", r=8)
    d.box(f"drawer{i}-notch", [165, y1 - 34, Z1 + 1, 255, y1 + 1, Z1 + 3.5], "line", r=8)
d.box("mark-v", [X0 - 1.5, 640, 225, X0, 760, 250], "line", soft=True)
d.box("mark-h", [X0 - 1.5, 745, 190, X0, 775, 290], "line", soft=True)
d.box("mark-c", [X0 - 1.5, 650, 255, X0, 735, 275], "line", soft=True)
# deck, neck, screen head
d.box("deck", [X0 - 3, YT - 2, Z0 + 4, X1 + 3, YT + 48, Z1 - 4], "metal#b3b8be", r=8)
d.box("led", [X0 + 8, YT + 22, Z1 - 5, X0 + 20, YT + 40, Z1 - 3], "gloss#3cc060", soft=True)
d.box("neck", [165, YT + 44, 330, 255, YT + 70, 400], "dark", r=10)
t = rot("x", -12, [210, YT + 52, 420])
d.box("head", [20, YT + 52, 360, 400, YT + 320, 420], "shell", r=36, rot=t)
d.add("screen", "screen", "black", box=[60, YT + 140, 418, 360, YT + 300, 425], r=26, face="front", bezel=26, rot=t)
d.cyl("button", [210, YT + 100, 419], [210, YT + 100, 428], 42, "black", rot=t)
# accessory: blue spine board leaning back 25° in an acrylic stand
a = 25
tb = rot("x", -a, [670, 30, 485])
d.add("board", "slab", "board", plane="front", outline="M 430 30 L 910 30 L 910 640 Q 910 800 740 800 L 470 800 Q 430 800 430 760 Z",
      w=[470, 500], r=8, rot=tb)
d.add("mat", "slab", "sil", plane="front", outline="M 505 110 Q 590 128 670 112 Q 750 128 835 110 Q 860 110 860 134 L 848 406 Q 842 454 860 502 L 860 622 Q 860 654 820 660 "
      "Q 670 690 520 660 Q 480 654 480 622 L 480 502 Q 498 454 492 406 L 480 134 Q 480 110 505 110 Z", w=[499, 505], r=2, rot=tb)
# rib-like pads: a narrow spine column, two lateral columns each side sloping down-outward (more at the shoulders)
def para(x0, x1, y0, h, drop, side):
    """pad from the spine side (x1 for the left) outward, its outer end lower by drop"""
    if side < 0:
        return f"M {x0} {y0 - drop} L {x1} {y0} L {x1} {y0 + h} L {x0} {y0 + h - drop} Z"
    return f"M {x0} {y0} L {x1} {y0 - drop} L {x1} {y0 + h - drop} L {x0} {y0 + h} Z"
sub = []
for k in range(13):
    y0 = 136 + k * 38; h = 27; dr = 30 if k >= 10 else (8 if k < 3 else 14)
    sub.append(f"M 659 {y0} L 681 {y0} L 681 {y0 + h} L 659 {y0 + h} Z")
    sub.append(para(590, 650, y0, h, dr * 0.6, -1)); sub.append(para(510, 584, y0 - dr * 0.6 - 2, h, dr, -1))
    sub.append(para(690, 750, y0, h, dr * 0.6, 1)); sub.append(para(756, 830, y0 - dr * 0.6 - 2, h, dr, 1))
d.add("pads", "slab", "pad", plane="front", outline=" ".join(sub), w=[503, 509], r=3, rot=tb)
d.box("board-logo", [620, 728, 499, 720, 746, 501.5], "plastic#2f5f9a", soft=True, rot=tb)
d.tube("pad-cable", [[840, 150, 505], [870, 120, 520], [880, 60, 540]], 8, "pad", bend=40, soft=True, rot=tb)
d.box("stand-base", [425, 0, 300, 915, 14, 565], "acryl", r=4)
d.box("stand-lip", [425, 14, 540, 915, 70, 560], "acryl", r=4)
d.box("stand-back", [470, 30, 452, 870, 420, 468], "acryl", r=4, rot=tb)
d.save()
