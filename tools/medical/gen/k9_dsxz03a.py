"""XY-DSXZ-03A leg extension / leg curl (hydraulic exerciser). Patient sits facing +z; at the seat front a pivot
hub with a pair of knee rollers, a C-curved lever down in front to a pair of ankle rollers, a cylinder between them."""
from k9lib import *
d = K("xy-dsxz-03a", [650, 1100, 1350], dict(EX_MATS))
CX = 325
foot(d, "foot-r", 85, 565, 95)
foot(d, "foot-f", 145, 505, 700)
d.sweep("spine", [[CX, 60, 140], [CX, 250, 230], [CX, 380, 380], [CX, 410, 560]], [60, 46], "frame", shape="oval", bend=150)
d.cyl("column", [CX, 40, 700], [CX, 450, 730], TUBE + 5, "frame")
d.box("seat-plate", [CX - 90, 418, 360, CX + 90, 432, 690], "dark", r=4)
seat(d, "seat", CX, 330, 690, 330, 400, 432)
zf, BR = back(d, "back", CX, 540, 1345, 255, 285, 240, tilt=-7, rt=110)
logo(d, "logo", CX, 1160, zf, h=32, R=BR)
d.box("hinge", [CX - 50, 470, 235, CX + 50, 555, 320], "dark", r=10)
d.sweep("support", [[CX, 400, 420], [CX, 420, 230], [CX, 560, 205], rotx([CX, 1250, 205], -7, [CX, 540, 240])],
        [50, 35], "frame", shape="oval", bend=60)
for nm, s in (("l", -1), ("r", 1)):
    x = CX + s * 285
    d.tube(f"shandle-{nm}", [[CX + s * 60, 410, 300], [x, 430, 300], [x, 520, 330]], 30, "frame", bend=40)
    grip(d, f"sgrip-{nm}", [x, 516, 325], [x, 530, 490], dia=40)
# pivot hub at the seat front with the knee roller pair
HY, HZ = 455, 750
d.box("hub", [CX - 45, HY - 50, HZ - 50, CX + 45, HY + 50, HZ + 50], "frame", r=20)
d.cyl("hub-axle", [CX - 250, HY, HZ], [CX + 250, HY, HZ], 30, "frame")
roller(d, "knee-l", [CX - 255, HY, HZ], [CX - 50, HY, HZ], dia=115)
roller(d, "knee-r", [CX + 50, HY, HZ], [CX + 255, HY, HZ], dia=115)
# C lever: forward from the hub, round and down to the ankle roller pair low in front
LY, LZ = 115, 900
d.sweep("lever", [[CX, HY, HZ], [CX, HY + 10, 930], [CX, 280, 1030], [CX, LY, LZ + 50], [CX, LY, LZ]], [55, 42], "frame",
        shape="oval", bend=120)
d.cyl("ankle-axle", [CX - 240, LY, LZ], [CX + 240, LY, LZ], 30, "frame")
roller(d, "ankle-l", [CX - 245, LY, LZ], [CX - 35, LY, LZ], dia=115)
roller(d, "ankle-r", [CX + 35, LY, LZ], [CX + 245, LY, LZ], dia=115)
# hydraulic cylinder from the column foot up to the lever
hydro(d, "hyd", [CX + 40, 150, 715], [CX + 40, 360, 975], body=0.6)
d.save()
