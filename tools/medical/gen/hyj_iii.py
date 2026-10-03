from hyjcart import *
# single arm from the right rear corner, rectangular radiator overhanging ~285 right of the cart
cx = 280
d = D("hyj-iii", [940, 500, 1630], dict(MATS))
cart(d, cx, logo="sunnyou")
H = [cx + 245, 1020, 95]; J = [cx + 460, 1395, 300]; R = [cx + 425, 1540, 300]
arm(d, "arm", H, J, +1)
rect_radiator(d, "rad", R, J)
cable(d, "cable", [[R[0] + 150, R[1] - 70, R[2] - 40], [J[0] + 60, J[1] + 20, J[2] - 30], [H[0] + 40, H[1] + 40, H[2] + 120],
                   [cx + 228, 840, 330], [cx + 238, 470, 370], [cx + 232, 520, 425], [cx + 214, 770, 405]])
socket(d, "socket", cx, +1)
d.save()
