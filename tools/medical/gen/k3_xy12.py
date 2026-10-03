"""XY-12 pulley weight (wall pulley station), kinesio-3. Size D 500: the 200 frame + the two pedals lying in front."""
from k3_lib import *

d = D("xy-12", [630, 500, 1800], {"frame": "plastic#eef0f1"})
pulley_unit(d, "", [0, 0, 0], "+z", W=630, Dp=200, H=1800, ring_y=1300, stack_h=190, base_h=170, pedals=True)
d.save()
