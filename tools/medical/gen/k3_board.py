"""XY-10 chest-and-back straightener and XY-11 with the wall pulley unit, kinesio-3."""
from k3_lib import *

d = D("xy-10", [720, 1280, 2100], {"frame": "plastic#eef0f1"})
straightener(d, "", 0, 0, top=1880, bottom_y=620, board_z=(690, 250), loop=True)
d.save()

d = D("xy-11", [720, 1280, 2100], {"frame": "plastic#eef0f1"})
pulley_unit(d, "pu-", [80, 0, 0], "+z", W=560, Dp=200, H=2060, ring_y=1450, stack_h=190, base_h=190, cuffs=True, cuff_y=560)
B, T, nrm, up = straightener(d, "", 0, 0, top=2000, bottom_y=640, board_z=(700, 245), loop=False)
# (review) the board's white rectangular handle loop rises out of its top and lies back over the tower cap as a
# flat tube frame, its back edge a little higher (photo: a white rectangle over the top of the tower)
xa, xb = 360 - 190, 360 + 190
tz, ty = T[0] - nrm[0] * 30, T[1] - nrm[1] * 30
d.tube("loop", [[xa, ty - 120, tz - 0], [xa, 2078, tz - 40], [xa, 2095, 10], [xb, 2095, 10], [xb, 2078, tz - 40], [xb, ty - 120, tz]],
       25, "frame", bend=40)
d.cyl("loop-x", [xa, 2078, tz - 40], [xb, 2078, tz - 40], 25, "frame")
d.cyl("loop-g", [xa, 2088, 120], [xb, 2088, 120], 22, "frame")
d.save()
