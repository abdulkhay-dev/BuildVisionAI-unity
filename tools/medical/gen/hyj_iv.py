from hyjcart import *
# two arms: left -> round drum far out to the left, right -> rectangular radiator leaning in over the cart
cx = 620
d = D("hyj-iv", [910, 500, 1650], dict(MATS))
cart(d, cx, logo="xiangyu")
HL = [cx - 245, 1020, 95]; JL = [cx - 400, 1395, 250]; RL = [cx - 465, 1515, 270]
arm(d, "arm-l", HL, JL, -1)
drum_radiator(d, "rad-l", RL, JL, yaw=-15)
HR = [cx + 245, 1020, 95]; JR = [cx + 20, 1405, 240]; RR = [cx - 20, 1550, 250]
arm(d, "arm-r", HR, JR, +1)
rect_radiator(d, "rad-r", RR, JR)
cable(d, "cable-l", [[RL[0] + 40, RL[1] + 90, RL[2] - 90], [RL[0] + 120, RL[1] + 110, RL[2] - 100], [JL[0] + 70, JL[1] - 60, JL[2] - 60],
                     [HL[0] - 40, HL[1] + 40, HL[2] + 120], [cx - 228, 840, 330], [cx - 238, 520, 370], [cx - 232, 560, 425], [cx - 214, 770, 405]])
cable(d, "cable-r", [[RR[0] + 150, RR[1] - 70, RR[2] - 40], [JR[0] + 120, JR[1] + 10, JR[2] - 60], [HR[0] + 40, HR[1] + 40, HR[2] + 120],
                     [cx + 228, 840, 330], [cx + 238, 470, 370], [cx + 232, 520, 425], [cx + 214, 770, 405]])
socket(d, "socket-l", cx, -1)
socket(d, "socket-r", cx, +1)
# right side: dark handle slot near the front, small grey holder box on the right rail at the rear
d.box("slot", [cx + 199, 640, 395, cx + 202, 750, 412], "dark", r=2, soft=True)
d.box("holder", [cx + 236, 800, 120, cx + 290, 852, 240], "rail", r=8)
d.box("holder-in", [cx + 246, 846, 130, cx + 280, 853, 230], "railtop", r=4)
d.save()
