from hyjcart import *
# single arm from the right rear corner, round drum radiator up and to the right
cx = 280
d = D("hyj-ii-enhanced", [900, 500, 1650], dict(MATS))
cart(d, cx, logo="sunnyou")
H = [cx + 245, 1020, 95]; J = [cx + 420, 1385, 280]; R = [cx + 470, 1515, 290]
arm(d, "arm", H, J, +1)
drum_radiator(d, "rad", R, J, yaw=-10)
cable(d, "cable", [[R[0] - 60, R[1] + 60, R[2] - 100], [R[0] - 120, R[1] + 40, R[2] - 120], [J[0] - 50, J[1] - 40, J[2] - 60],
                   [H[0] + 40, H[1] + 40, H[2] + 120], [cx + 228, 840, 330], [cx + 238, 470, 370], [cx + 232, 520, 425], [cx + 214, 770, 405]])
socket(d, "socket", cx, +1)
d.save()
