from lib import *
from p2util import *
import math
# off-white TENS trolley: flared plinth, cabinet with blue drawers, tilted panel head, socket strip, side basket + handle
d = D("rh-jpsj-b", [650, 370, 1150], {"shell": "plastic#eef1ee", "cream": "plastic#e9e8dc", "blue": "plastic#9ccfe0",
      "blue2": "plastic#7fb8cc", "dark": "plastic#4d5259", "knob": "gloss#2f6fd0", "grey": "plastic#9aa0a8", "black": "gloss#141517"})
cx = 240
X0, X1, Z0, Z1 = cx - 200, cx + 200, 18, 352
# four white flared feet (flat arms from the body corners out to round caps over twin-wheel castors)
for i, (sx, zc, zt) in enumerate(((-1, 70, 28), (1, 70, 28), (-1, 300, 342), (1, 300, 342))):
    d.add(f"foot{i}", "bar", "shell", **{"from": [cx + sx * 140, 135, zc], "to": [cx + sx * 205, 132, zt]}, section=[88, 64], r=26)
    d.cyl(f"foot-cap{i}", [cx + sx * 205, 100, zt], [cx + sx * 205, 164, zt], 84, "shell")
    x = cx + sx * 205
    d.add(f"castor{i}", "caster", "rubber#2c2f33", at=[x - 13, 0, zt + 10], d=75)
    d.add(f"castor{i}b", "caster", "rubber#2c2f33", at=[x + 13, 0, zt + 10], d=75)
# cabinet
d.box("cabinet", [X0, 100, Z0, X1, 870, Z1], "shell", r=40)
# the big front door panel outline (rounded bottom corners) holding the drawers and the badge
d.add("door-line", "slab", "plastic#c3c8cc", plane="front", outline=rr(X0 + 14, 118, X1 - 14, 795, 60) + " " + rr(X0 + 17, 121, X1 - 17, 792, 57), w=[Z1 - 1, Z1 + 1], soft=True)
d.box("front-seam", [X0 + 18, 790, Z1 - 1, X1 - 18, 793, Z1 + 1], "plastic#c9cdd2", soft=True)
d.box("logo", [cx - 50, 700, Z1 - 2, cx + 50, 730, Z1 + 3], "plastic#e2e6e9", r=14)
d.box("logo-t", [cx - 36, 711, Z1 + 3, cx + 12, 717, Z1 + 3.5], "plastic#6c9fb8", soft=True)
d.box("logo-m", [cx + 16, 708, Z1 + 3, cx + 38, 722, Z1 + 3.5], "gloss#3aa080", soft=True)
for i, (y0, y1) in enumerate(((530, 668), (385, 526))):
    d.box(f"drawer{i}", [X0 + 22, y0, Z1 - 4, X1 - 22, y1, Z1 + 5], "blue", r=8)
    d.box(f"drawer{i}-pull", [cx - 40, y1 - 30, Z1 + 1, cx + 30, y1 - 4, Z1 + 6], "blue2", r=8)
# right side: marks, vent slits
d.box("mark", [X1, 345, 140, X1 + 1.5, 395, 143], "dark", soft=True, copies=[[0, 0, 70]])
d.box("vent", [X1, 205, 70, X1 + 1.5, 209, 150], "plastic#7d838b", soft=True, repeat={"n": 5, "step": [0, 12, 0]}, copies=[[0, 0, 110]])
# head
d.add("head", "slab", "shell", plane="side", outline=f"M {Z0 - 4} 862 L {Z1 + 22} 862 L {Z1 - 30} 1150 L {Z0 - 4} 1150 Z", w=[X0 - 32, X1 + 32], r=40)
ang = math.degrees(math.atan2(52, 288))
t = rot("x", -ang, [cx, 880, Z1 + 18])
def tc(cs): return [[c[0], c[1], c[2] - c[1] * math.tan(math.radians(ang))] for c in cs]
d.box("panel", [X0 + 15, 890, Z1 + 12, X1 - 15, 1125, Z1 + 20], "cream", r=10, rot=t)
zp = Z1 + 20.3
d.box("p-title", [X0 + 22, 1095, zp - 1, X1 - 22, 1118, zp], "dark", soft=True, rot=t)
d.box("p-win", [X0 + 30, 1010, zp - 1, X0 + 78, 1065, zp], "plastic#b9bec5", soft=True, rot=t, copies=tc([[292, 0, 0]]))
d.box("p-win-in", [X0 + 36, 1016, zp - 0.5, X0 + 72, 1059, zp + 0.3], "cream", soft=True, rot=t, copies=tc([[292, 0, 0]]))
d.box("p-led", [X0 + 120, 1050, zp - 1, X0 + 132, 1058, zp + 0.5], "gloss#e0503a", soft=True, rot=t,
      copies=tc([[0, -16, 0], [0, -32, 0], [130, 0, 0], [130, -16, 0], [130, -32, 0]]))
d.cyl("p-knob", [X0 + 150, 990, zp - 1], [X0 + 150, 990, zp + 14], 22, "grey", rot=t, copies=tc([[50, 0, 0], [110, 0, 0], [160, 0, 0]]))
d.box("p-strip", [X0 + 22, 915, zp - 1, X0 + 192, 955, zp + 4], "dark", r=18, rot=t, copies=tc([[178, 0, 0]]))
d.cyl("p-bknob", [X0 + 50, 935, zp + 3], [X0 + 50, 935, zp + 15], 22, "knob", rot=t,
      copies=tc([[55, 0, 0], [110, 0, 0], [178, 0, 0], [233, 0, 0], [288, 0, 0]]))
# socket strip
d.box("sockets", [X0 + 25, 818, Z1 - 4, X1 - 25, 852, Z1 + 12], "dark", r=16)
d.cyl("sock", [X0 + 52, 835, Z1 + 11], [X0 + 52, 835, Z1 + 14], 15, "knob", repeat={"n": 6, "step": [26, 0, 0]})
d.cyl("sock2", [X0 + 212, 835, Z1 + 11], [X0 + 212, 835, Z1 + 13], 17, "plastic#b9bec5", repeat={"n": 6, "step": [26, 0, 0]})
d.cyl("sock2-in", [X0 + 212, 835, Z1 + 13], [X0 + 212, 835, Z1 + 14], 9, "black", soft=True, repeat={"n": 6, "step": [26, 0, 0]})
# side basket and handle
bx = X1 + 100
zc, H0, H1 = 185, 870, 985
d.box("basket-bottom", [bx - 75, H0, zc - 95, bx + 75, H0 + 6, zc + 95], "blue", r=3)
d.box("basket-front", [bx - 93, H0, zc + 95, bx + 93, H1, zc + 101], "blue", r=3, rot=rot("x", 10, [bx, H0, zc + 95]))
d.box("basket-back", [bx - 93, H0, zc - 101, bx + 93, H1, zc - 95], "blue", r=3, rot=rot("x", -10, [bx, H0, zc - 95]))
d.box("basket-left", [bx - 81, H0, zc - 114, bx - 75, H1, zc + 114], "blue", r=3, rot=rot("z", 9, [bx - 75, H0, zc]))
d.box("basket-right", [bx + 75, H0, zc - 114, bx + 81, H1, zc + 114], "blue", r=3, rot=rot("z", -9, [bx + 75, H0, zc]))
d.box("basket-mount", [X1 - 2, 900, 130, X1 + 12, 980, 240], "grey", r=4)
d.tube("handle", [[X1 - 2, 745, 90], [X1 + 48, 745, 100], [X1 + 48, 745, 290], [X1 - 2, 745, 300]], 25, "grey", bend=30)
d.save()
