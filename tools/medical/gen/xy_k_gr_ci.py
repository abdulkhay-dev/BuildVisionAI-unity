from lib import *
from p2util import *
# two-piece desktop interferential: white base with a blue arch socket recess, steel right side, tilted white panel slab, fork holder
d = D("xy-k-gr-ci", [550, 380, 520], {"shell": "gloss#f2f3f5", "blue": "gloss#2f5fb0", "black": "gloss#141517",
      "steel": "metal#b9bec5", "membrane": "plastic#c9cdd3"})
d.cyl("foot", [60, 0, 50], [60, 10, 50], 20, "rubber#1c1d20", copies=[[340, 0, 0], [0, 0, 270], [340, 0, 270]])
d.box("body", [32, 10, 22, 428, 248, 324], "shell", r=26)
front = ("M 30 10 L 108 10 L 108 55 Q 108 125 200 125 L 330 125 Q 418 125 418 55 L 418 10 L 430 10 L 430 222 "
         "Q 430 250 402 250 L 58 250 Q 30 250 30 222 Z")
d.add("front", "slab", "shell", plane="front", outline=front, w=[318, 350], r=10)
d.box("recess", [100, 10, 300, 424, 132, 326], "blue", r=4)
# socket plates: black outlines (blue inside) with 2 black sockets in chrome rings each
for k in range(3):
    x0 = 181 + k * 46
    d.add(f"plate{k}", "slab", "black", plane="front", outline=rr(x0, 20, x0 + 38, 106, 17) + " " + rr(x0 + 3, 23, x0 + 35, 103, 14), w=[325, 328], r=1)
d.cyl("sock", [200, 42, 326], [200, 42, 331], 22, "chrome", copies=[[0, 40, 0], [44, 0, 0], [44, 40, 0], [88, 0, 0], [88, 40, 0]])
d.cyl("sock-in", [200, 42, 331], [200, 42, 332], 15, "black", soft=True, copies=[[0, 40, 0], [44, 0, 0], [44, 40, 0], [88, 0, 0], [88, 40, 0]])
d.box("icon", [150, 80, 326, 166, 96, 327], "plastic#f2f3f5", soft=True)
d.box("warn", [330, 55, 326, 346, 70, 327], "gloss#e8c22a", soft=True)
# brushed-steel right side panel, rising behind to cover the support wedge
d.add("steel", "slab", "steel", plane="side", outline="M 26 14 L 346 14 L 346 252 Q 330 262 300 300 L 255 380 L 110 252 L 26 252 Z", w=[428, 434], r=2)
d.box("steel-logo", [434, 120, 230, 435, 200, 260], "plastic#2f4f8a", soft=True)
# blue support wedge and the tilted panel slab
d.add("wedge", "slab", "blue", plane="side", outline="M 110 244 L 332 244 L 250 410 Z", w=[60, 400], r=6)
t = rot("x", -25, [230, 240, 362])
d.box("slab", [10, 240, 336, 450, 552, 362], "shell", r=34, rot=t)
d.add("panel", "screen", "membrane", box=[38, 262, 358, 422, 532, 364], r=8, face="front", bezel=2, print="med_xy-k-gr-ci_screen", rot=t)
# vacuum-cup holder: a flat stainless fork plate (5 tines) rising out of the steel side at the rear, tines pointing up and out
import math
u = (math.cos(math.radians(35)), math.sin(math.radians(35))); n = (-u[1], u[0]); O = (430, 250)
P = lambda sx, tx: f"{O[0] + sx * u[0] + tx * n[0]:.1f} {O[1] + sx * u[1] + tx * n[1]:.1f}"
pts = [P(0, 0)]
for k, L in enumerate((105, 112, 120, 128, 135)):
    t0, t1 = k * 16.5, k * 16.5 + 10
    pts += [P(L, t0), P(L + 4, (t0 + t1) / 2), P(L, t1)]
    if k < 4:
        pts += [P(62, t1), P(62, t1 + 6.5)]
pts += [P(0, 76)]
d.add("fork", "slab", "steel", plane="front", outline="M " + " L ".join(pts) + " Z", w=[150, 153], r=1)
d.box("fork-root", [426, 236, 140, 446, 262, 163], "steel", r=3)
d.save()
