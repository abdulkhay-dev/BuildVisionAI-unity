"""XY-DSSZ-03A biceps / triceps (hydraulic exerciser). Patient sits facing +z, the arm rest in front."""
from k9lib import *
d = K("xy-dssz-03a", [800, 900, 1150], dict(EX_MATS))
CX = 400
# --- base: short rear foot under the seat, long front foot under the column, joined through the column hub
foot(d, "foot-r", 230, 570, 120)
d.box("foot-f-pad", [140, 50, 798, 230, 60, 822], "cap", r=4, copies=[[430, 0, 0]])
foot(d, "foot-f", 40, 760, 810)
d.cyl("post", [CX, 40, 140], [CX, 425, 200], TUBE, "frame")
d.sweep("beam", [[CX, 380, 210], [CX, 330, 380], [CX, 300, 520]], [55, 45], "frame", shape="oval", bend=80)
for nm, s in (("l", -1), ("r", 1)):
    d.sweep(f"strut-{nm}", [[CX, 300, 530], [CX + s * 120, 200, 640], [CX + s * 230, 40, 800]], [50, 42], "frame",
            shape="oval", bend=120)
d.box("seat-plate", [CX - 100, 418, 150, CX + 100, 432, 420], "dark", r=4)
# wide trapezoid seat, wide edge at the back
seat(d, "seat", CX, 90, 470, 470, 300, 432, layers=(26, 10, 36), r=70)
# --- column with the adjustment collar, T top carrying the two arm-rest blocks
col0, col1 = [CX, 300, 530], [CX, 1000, 610]
d.cyl("column", col0, col1, 60, "frame")
d.cyl("collar", [CX, 420, 543], [CX, 520, 555], 82, "dark")
d.cyl("collar-knob", [CX, 470, 549], [CX + 70, 470, 549], 16, "chrome")
d.sphere("collar-knob-b", [CX + 75, 470, 549], 30, "cap")
d.cyl("t-bar", [CX - 300, 1000, 610], [CX + 300, 1000, 610], 40, "frame")
d.box("t-hub", [CX - 45, 960, 570, CX + 45, 1045, 650], "frame", r=14)
for nm, x0, x1 in (("l", CX - 300, CX - 50), ("r", CX + 50, CX + 300)):
    d.box(f"rest-{nm}", [x0, 935, 545, x1, 1070, 680], "blue", r=32)
    d.box(f"rest-pipe-{nm}", [x0 + 6, 944, 541, x1 - 6, 955, 684], "pipe", r=4)
    xe = x0 - 6 if x0 < CX else x1 + 6
    d.cyl(f"rest-cap-{nm}", [x0 if x0 < CX else x1, 1002, 612], [xe, 1002, 612], 70, "metal#c8cbcf")
logo(d, "logo", CX + 175, 1015, 680.5, h=24)   # on the front face of the patient's-left block (towards the camera)
# --- the lever: pivots on the T, handle bar above-behind towards the patient, roller pair below in front
d.bar("lever-up", [CX, 1000, 640], [CX, 1110, 760], [36, 30], "frame", r=6)
d.cyl("handle-bar", [CX - 290, 1115, 765], [CX + 290, 1115, 765], 34, "frame")
for nm, s in (("l", -1), ("r", 1)):
    grip(d, f"grip-{nm}", [CX + s * 120, 1115, 765], [CX + s * 300, 1115, 765], dia=42)
d.bar("lever-dn", [CX, 1000, 640], [CX, 850, 730], [36, 30], "frame", r=6)
d.cyl("roll-axle", [CX - 200, 850, 735], [CX + 200, 850, 735], 30, "frame")
roller(d, "roll-l", [CX - 210, 850, 735], [CX - 40, 850, 735], dia=100)
roller(d, "roll-r", [CX + 40, 850, 735], [CX + 210, 850, 735], dia=100)
# hydraulic cylinder in front of the column, from a lug low on the column to the lever
d.box("hyd-lug", [CX - 20, 560, 560, CX + 20, 610, 620], "frame", r=5)
hydro(d, "hyd", [CX, 590, 620], [CX, 930, 700], body=0.62)
d.save()
