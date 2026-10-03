"""xyhj-2 Anklebone Trainer (tilt standing board). Photo = front view, 2.08 mm/px horizontally
(x = 400 + (px - 242) * 2.08, along-board s = (845 - py) * 2.08). The board leans back 12°; the photo cannot show the
depth, so the rear legs and the foot platform's depth are drawn to the printed D 830."""
from k7lib import *

d = D("xyhj-2", [800, 830, 1770], {
    "pad": "leather#5772a7", "strap": "fabric#a68f55", "cream": "plastic#ddd4a8", "rail": "metal#6a6650",
    "chrome": "chrome", "black": "plastic#1a1b1d", "slat": "plastic#8d8a72", "rubber": "rubber#1c1d1f"})
YB, ZF = 120, 620                  # board bottom, front face z (before the tilt)
L = 1690
tilt = rot("x", -12, [400, YB, ZF])
# --- blue padded board: wide upper part, narrower lower part with a central slot (hole)
top = YB + L
# photo (scanned): 576 wide down to s ~380, a short taper, 462 wide below; slot ~118 wide from s 60 to ~735
board = (f"M 169 {YB + 40} L 169 {YB + 330} Q 169 {YB + 362} 112 {YB + 392} L 112 {top - 45} Q 112 {top} 157 {top} "
         f"L 643 {top} Q 688 {top} 688 {top - 45} L 688 {YB + 392} Q 631 {YB + 362} 631 {YB + 330} L 631 {YB + 40} "
         f"Q 631 {YB} 591 {YB} L 209 {YB} Q 169 {YB} 169 {YB + 40} Z "
         f"M 341 {YB + 60} L 341 {YB + 676} Q 341 {YB + 735} 400 {YB + 735} Q 459 {YB + 735} 459 {YB + 676} "
         f"L 459 {YB + 60} Z")
d.slab("board", "front", board, [ZF - 70, ZF], "pad", r=22, rot=tilt)
d.slab("board-back", "front", board, [ZF - 88, ZF - 68], "plastic#3a3d42", r=4, rot=tilt)
d.cyl("spine", [400, YB + 40, ZF - 100], [400, top - 200, ZF - 100], 34, "chrome", rot=tilt)
# --- tan webbing straps: chest (V-dip) and knee (two halves meeting in a V)
sc = YB + 873
d.strap("strap-chest", [[52, sc, ZF - 60], [112, sc, ZF + 6], [400, sc - 26, ZF + 12], [688, sc, ZF + 6], [748, sc, ZF - 60]],
        [110, 6], "strap", bend=40, roll=90, rot=tilt)
sk = YB + 140
d.strap("strap-knee-l", [[52, sk, ZF - 60], [190, sk, ZF + 6], [396, sk - 28, ZF + 12]], [100, 6], "strap", bend=40, roll=90, rot=tilt)
d.strap("strap-knee-r", [[404, sk - 28, ZF + 12], [610, sk, ZF + 6], [748, sk, ZF - 60]], [100, 6], "strap", bend=40, roll=90, rot=tilt)
# --- side frames (mirrored). Photo (front view, camera above): the black wheels show LOWER than the dark rails' feet,
#     so they stand in front of them: the dark rails (lock knob, ratchet block on top) are the adjustable rear props
#     down to the floor behind, the cream struts run down the board's sides to the front wheels; a short cream
#     cross bar near the floor joins strut and rail.
TP = lambda q: rotx(q, -12, [400, YB, ZF])
r_top = TP([45, 1200, ZF - 40])
d.bar("rail", r_top, [45, 14, 150], [26, 34], "rail", r=4, mirror="x")
d.box("rail-foot", [28, 0, 120, 62, 16, 182], "rubber", r=4, mirror="x")
km = [45 + (45 - 45), (r_top[1] + 14) / 2.0, (r_top[2] + 150) / 2.0]
d.lathe("rail-knob", [32, km[1], km[2]], [[0, 0], [7, 0], [7, 8], [17, 10], [17, 28], [0, 30]], "black", axis="x",
        rot=rot("y", 180, [32, km[1], km[2]]), mirror="x")
d.box("ratchet", [62, 1080, ZF - 72, 108, 1220, ZF - 22], "black", r=6, rot=tilt, mirror="x")
d.tube("hook", [[58, 1120, ZF - 40], [14, 1140, ZF - 30], [6, 1190, ZF - 10], [26, 1225, ZF + 10]], 20, "chrome",
       bend=22, rot=tilt, mirror="x")
s_top = TP([70, 1060, ZF - 50])
d.cyl("front-strut", s_top, [121, 70, 668], 30, "cream", mirror="x")
d.cyl("strut-cross", [121 - 0.06 * 100, 170, 655], [45, 170, 190], 22, "cream", mirror="x")
d.cyl("strut-cross2", [119, 130, 660], [45, 130, 196], 14, "metal#a9adb2", mirror="x")
d.add("front-wheel", "wheel", "rubber", at=[121, 32, 670], d=64, d2=30, axis="x", mirror="x")
d.cyl("wheel-fork", [121, 32, 670], [121, 78, 668], 16, "cream", mirror="x")
d.cyl("top-rod", [48, 1560, ZF - 90], [48, 1760, ZF - 90], 16, "chrome", rot=tilt, mirror="x")
d.box("top-bracket", [42, 1500, ZF - 110, 118, 1550, ZF - 70], "cream", r=6, rot=tilt, mirror="x")
d.sphere("top-knob", [34, 1572, ZF - 90], 34, "black", rot=tilt, mirror="x")
# --- slatted foot platform in front (photo: a step ~150 high: khaki slatted top with a front lip on a chrome stand
#     of two side legs, a bottom bar and a V brace)
d.box("foot-plate", [200, 136, 640, 600, 148, 830], "slat", r=4)
d.box("foot-slat", [204, 148, 646, 596, 156, 676], "slat", r=3, repeat={"n": 5, "step": [0, 0, 37]})
d.box("foot-lip", [200, 110, 812, 600, 162, 830], "slat", r=4)
d.box("foot-side", [200, 110, 640, 212, 150, 830], "slat", r=3, copies=[[388, 0, 0]])
d.bar("foot-leg", [216, 0, 800], [216, 136, 800], [16, 16], "chrome", r=3, copies=[[368, 0, 0], [0, 0, -140], [368, 0, -140]])
d.bar("foot-base", [208, 8, 800], [592, 8, 800], [20, 16], "chrome", r=3, copies=[[0, 0, -140]])
d.bar("foot-side-base", [216, 8, 660], [216, 8, 800], [16, 16], "chrome", r=3, copies=[[368, 0, 0]])
d.tube("foot-brace", [[224, 104, 806], [300, 20, 806], [500, 20, 806], [576, 104, 806]], 12, "chrome", bend=20)
d.save()
