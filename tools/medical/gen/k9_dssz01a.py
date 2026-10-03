"""XY-DSSZ-01A shoulder press (hydraulic exerciser). Patient sits facing +z."""
from k9lib import *
d = K("xy-dssz-01a", [800, 900, 1350], dict(EX_MATS))
CX = 400
# --- floor: short front foot under the seat front, long rear foot behind
foot(d, "foot-f", 225, 575, 790)
foot(d, "foot-r", 105, 695, 95)
d.box("foot-r-pad", [215, 50, 82, 300, 60, 108], "cap", r=4, copies=[[285, 0, 0]])
d.cyl("post", [CX, 40, 785], [CX, 425, 760], TUBE, "frame")
# arch from under the seat down to the middle of the rear foot (one wide curved tube)
d.sweep("arch", [[CX, 420, 600], [CX, 400, 430], [CX, 230, 250], [CX, 60, 140]], [70, 50], "frame", shape="oval", bend=170)
d.box("seat-plate", [CX - 90, 418, 420, CX + 90, 432, 760], "dark", r=4)
d.cyl("bumper", [CX - 150, 412, 735], [CX - 120, 412, 735], 30, "cap")
yt = seat(d, "seat", CX, 400, 790, 330, 420, 432)
# --- backrest + its support behind
zf, BR = back(d, "back", CX, 525, 1325, 270, 295, 300, tilt=-9, rt=110)
logo(d, "logo", CX, 1120, zf, h=34, R=BR)
d.box("hinge", [CX - 55, 470, 300, CX + 55, 545, 380], "dark", r=10)
d.sweep("support", [[CX, 430, 420], [CX, 440, 280], [CX, 560, 255], rotx([CX, 1290, 255], -9, [CX, 525, 300])],
        [50, 35], "frame", shape="oval", bend=70)
# --- the press lever: a U frame pivoting behind the backrest top, front ends bent down into long black grips
yb = 1315
zp = 150   # pivot bracket z
d.box("pivot-bracket", [CX - 70, yb - 40, zp - 30, CX + 70, yb + 25, zp + 35], "frame", r=10)
d.cyl("pivot-axle", [CX - 85, yb - 10, zp], [CX + 85, yb - 10, zp], 22, "chrome")
for nm, x in (("l", 120), ("r", 680)):
    path = [[CX, yb, zp - 20], [x, yb, zp - 20], [x, yb, 380], [x, 1180, 520], [x, 820, 690]]
    d.tube(f"lever-{nm}", path, 38, "frame", bend=90)
    grip(d, f"grip-{nm}", lerp(path[3], path[4], 0.12), lerp(path[3], path[4], 1.03), dia=46)
# hydraulic cylinder hanging behind the backrest (far side), its body below
hydro(d, "hyd", [CX - 110, 880, 175], [CX - 110, 1290, 150], body=0.68)
d.box("hyd-lug", [CX - 125, 840, 160, CX - 95, 895, 225], "frame", r=6)
d.save()
