# XYRT-21 children PT stool: blue round upholstered seat, black paddle lever, chrome gas lift with a blue label,
# polished 5-star base with arched arms, black twin-wheel castors (drawn at the top height 580)
import math
from pd2_lib import *

W, D, H = 450, 450, 580
C = W / 2
d = Design("xyrt-21", [W, D, H], {"seat": "leather#1f55b5", "blk": "plastic#1d1e21", "chr": "chrome",
                                    "caster": "plastic#1a1b1e", "label": "gloss#2f6fd0"})
# seat: thick round cushion with a well-rounded edge and a slightly domed top
d.lathe("seat", [C, 505, C], [[0, 0], [160, 0], [178, 8], [186, 26], [186, 50], [178, 66], [150, 75], [0, 80]], "seat",
        sides=56)
d.lathe("seat-plate", [C, 488, C], [[0, 0], [95, 0], [95, 18], [0, 18]], "blk")
# height lever: black paddle sticking out at the front left
d.cyl("lever-rod", [C - 40, 494, C + 30], [C - 110, 488, C + 110], 12, "blk")
d.box("lever", [C - 150, 462, C + 95, C - 95, 495, C + 150], "blk", r=8, rot=rot("y", -45, [C - 122, 478, C + 122]),
      rots=[rot("x", 35, [C - 110, 488, C + 110])])     # the paddle hangs down to the front
# gas lift: thin chrome piston, chrome collar, thick chrome cylinder with a small blue label
d.cyl("piston", [C, 400, C], [C, 490, C], 30, "chr")
d.lathe("collar", [C, 385, C], [[0, 0], [30, 0], [32, 6], [32, 18], [28, 22], [0, 22]], "blk")   # black ring on top of the cylinder
d.cyl("cylinder", [C, 140, C], [C, 390, C], 54, "chr")
d.box("cyl-label", [C - 16, 330, C + 26.5, C + 16, 370, C + 28], "label", r=2, soft=True)
d.lathe("hub", [C, 108, C], [[0, 0], [58, 0], [60, 12], [52, 40], [34, 54], [0, 54]], "chr")
# five arched chrome arms with black twin-wheel castors
R = 195
for k in range(5):
    a = math.radians(90 + 72 * k + 18)
    ux, uz = math.cos(a), math.sin(a)
    pts = [[C + r * ux, y, C + r * uz] for r, y in ((30, 140), (90, 148), (150, 128), (R, 100))]
    d.sweep(f"arm{k}", pts, [58, 26], "chr", shape="oval", bend=60)
    ex, ez = C + R * ux, C + R * uz
    d.lathe(f"armend{k}", [ex, 80, ez], [[0, 0], [20, 0], [20, 22], [0, 24]], "chr")
    d.cyl(f"cstem{k}", [ex, 58, ez], [ex, 84, ez], 16, "caster")
    cx, cz = ex + 8 * ux, ez + 8 * uz
    d.box(f"chood{k}", [cx - 8, 22, cz - 28, cx + 8, 64, cz + 12], "caster", r=7,
          rot=rot("y", -math.degrees(a) + 90, [cx, 40, cz]))
    d.add(f"cwheel{k}", "wheel", "caster", at=[cx - 16 * uz, 25, cz + 16 * ux], d=50, d2=16, axis="x",
          rot=rot("y", -math.degrees(a) + 90, [cx - 16 * uz, 25, cz + 16 * ux]), copies=[[32 * uz, 0, -32 * ux]])
d.save()
