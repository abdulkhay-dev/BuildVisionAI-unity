"""XY-DSXZ-01A leg press (hydraulic exerciser). Patient sits facing +z; in front a white footboard on a double tube
linkage pivoting on top of a cream U frame, black grips on both ends of the pivot, two cylinders under it."""
from k9lib import *
d = K("xy-dsxz-01a", [700, 1400, 1300], dict(EX_MATS, board="plastic#f2f1ec"))
CX = 350
# --- rear foot, main beam rising from the front frame up to the seat and on to the rear
foot(d, "foot-r", 110, 590, 95)
d.sweep("beam", [[CX, 40, 1290], [CX, 200, 800], [CX, 330, 420], [CX, 330, 250], [CX, 60, 120]], [70, 50], "frame",
        shape="oval", bend=160)
d.cyl("post", [CX, 250, 560], [CX, 425, 560], TUBE, "frame")
d.box("seat-plate", [CX - 90, 418, 300, CX + 90, 432, 620], "dark", r=4)
seat(d, "seat", CX, 270, 650, 330, 400, 432)
d.cyl("bumper", [CX - 40, 410, 600], [CX + 40, 410, 600], 30, "cap")
zf, BR = back(d, "back", CX, 540, 1300, 255, 285, 210, tilt=-8, rt=110)
logo(d, "logo", CX, 1130, zf, h=32, R=BR)
d.box("hinge", [CX - 50, 470, 205, CX + 50, 555, 290], "dark", r=10)
d.sweep("support", [[CX, 330, 330], [CX, 400, 200], [CX, 560, 175], rotx([CX, 1230, 175], -8, [CX, 540, 210])],
        [50, 35], "frame", shape="oval", bend=60)
# side handles at the seat: cream tubes out from under the seat, black grips pointing forward
for nm, s in (("l", -1), ("r", 1)):
    x = CX + s * 285
    d.tube(f"shandle-{nm}", [[CX + s * 60, 400, 330], [x, 430, 330], [x, 520, 360]], 30, "frame", bend=40)
    grip(d, f"sgrip-{nm}", [x, 516, 355], [x, 535, 520], dia=40)
# --- front frame: floor tube with two dark wheel rings, inverted U up to the pivot
FZ = 1290
d.cyl("ffoot", [CX - 170, 40, FZ], [CX + 170, 40, FZ], TUBE, "frame")
for nm, x in (("l", CX - 110), ("r", CX + 110)):
    d.cyl(f"fring-{nm}", [x - 22, 40, FZ], [x + 22, 40, FZ], 76, "rubber#3a3d42")
d.tube("fu", [[CX - 130, 40, FZ], [CX - 130, 400, FZ - 10], [CX + 130, 400, FZ - 10], [CX + 130, 40, FZ]], 44, "frame", bend=90)
d.cyl("fu-bar", [CX - 130, 200, FZ - 5], [CX + 130, 200, FZ - 5], 36, "frame")
PY, PZ = 445, FZ - 20
d.cyl("pivot", [CX - 140, PY, PZ], [CX + 140, PY, PZ], 70, "frame")
d.box("pivot-plate", [CX - 150, PY - 55, PZ - 30, CX + 150, PY + 10, PZ + 30], "frame", r=12)
d.cyl("pivot-axle", [CX - 160, PY, PZ], [CX + 160, PY, PZ], 30, "chrome")
for nm, s in (("l", -1), ("r", 1)):
    grip(d, f"pgrip-{nm}", [CX + s * 165, PY, PZ], [CX + s * 345, PY, PZ], dia=46)
# double-tube linkage up-back to the footboard
BZ, BY = 1000, 660
for nm, x in (("l", CX - 70), ("r", CX + 70)):
    d.cyl(f"link-{nm}", [x, PY, PZ], [x, BY, BZ + 25], 58, "frame")
d.box("bracket", [CX - 110, BY - 60, BZ + 10, CX + 110, BY + 40, BZ + 40], "frame", r=8)
d.box("board", [CX - 200, BY - 230, BZ - 5, CX + 200, BY + 230, BZ + 10], "board", r=6,
      rot=rot("x", -10, [CX, BY, BZ]))
# two hydraulic cylinders from the beam forward to the U cross bar
for nm, x in (("l", CX - 55), ("r", CX + 55)):
    hydro(d, f"hyd-{nm}", [x, 150, 830], [x, 200, FZ - 20], body=0.65, dia=44)
d.save()
