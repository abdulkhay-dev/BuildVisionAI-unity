from lib import *
from p2util import *
# portable desktop microwave unit: silver box with a framed panel, pole + 2-segment arm with dampers, white cup radiator
d = D("hyj-i", [420, 330, 720], {"shell": "plastic#c8ccd2", "bezel": "plastic#d6dade", "panel": "plastic#d9dce0",
      "blue": "gloss#3b8fd6", "dark": "plastic#3d4248", "chrome": "chrome", "black": "gloss#15171a", "cup": "gloss#f4f5f7"})
d.box("foot", [30, 0, 30, 60, 9, 60], "rubber#1c1d20", copies=[[330, 0, 0], [0, 0, 240], [330, 0, 240]])
d.box("body", [2, 8, 0, 418, 196, 300], "shell", r=24)
d.add("bezel", "slab", "bezel", plane="front", outline=rr(0, 8, 420, 200, 30) + " " + rr(36, 82, 384, 184, 16) + " " + rr(44, 24, 376, 66, 12),
      w=[290, 330], r=8)
d.add("blue-line", "slab", "blue", plane="front", outline=rr(29, 75, 391, 191, 20) + " " + rr(36, 82, 384, 184, 16), w=[328, 331], r=1)
d.box("panel", [34, 80, 300, 386, 186, 316], "panel", r=4)
d.box("strip", [42, 22, 300, 378, 68, 310], "plastic#b9bec5", r=4)
z = 316.2
d.box("strip-txt", [110, 40, 310, 310, 50, 311], "plastic#5d636b", soft=True)
d.box("strip-line", [52, 60, 310, 200, 62, 311], "plastic#8a9099", soft=True)
d.box("p-logo", [52, 165, z - 1, 74, 177, z], "blue", soft=True)
d.box("p-logo-t", [78, 167, z - 1, 112, 175, z], "blue", soft=True)
d.box("p-title", [150, 170, z - 1, 260, 177, z], "dark", soft=True)
d.box("p-led", [70, 138, z - 1, 122, 160, z], "gloss#141518", soft=True, copies=[[62, 0, 0]])
d.box("p-led-d", [75, 142, z - 0.5, 87, 156, z + 0.3], "gloss#e0303a", soft=True, copies=[[16, 0, 0], [32, 0, 0], [62, 0, 0], [78, 0, 0], [94, 0, 0]])
d.box("p-btn", [66, 100, z - 1, 88, 122, z + 1], "blue", soft=True, repeat={"n": 6, "step": [32, 0, 0]})
d.box("p-btn-t", [68, 90, z - 1, 86, 93, z], "plastic#7d838b", soft=True, repeat={"n": 6, "step": [32, 0, 0]})
d.cyl("p-lamp", [300, 152, z - 1], [300, 152, z + 0.5], 7, "gloss#d8323f", soft=True, copies=[[22, 0, 0]])
d.box("p-start", [334, 104, z - 1, 354, 120, z + 1], "blue", soft=True)
d.box("grip", [417, 120, 190, 421, 158, 268], "dark", r=3)
d.box("grip-s", [-1, 120, 190, 3, 158, 268], "dark", r=3)
d.cyl("rf-nut", [290, 192, 150], [290, 212, 150], 26, "chrome", sides=6)
d.cyl("rf-pin", [290, 212, 150], [290, 222, 150], 14, "chrome")
# pole on the right rear corner
P = [385, 0, 50]
d.cyl("pole-base", [P[0], 192, P[2]], [P[0], 236, P[2]], 56, "black")
d.cyl("pole", [P[0], 236, P[2]], [P[0], 492, P[2]], 25, "chrome")
d.cyl("damper-rod", [P[0] - 22, 222, P[2]], [P[0] - 22, 268, P[2]], 7, "chrome", copies=[[44, 0, 0]])
d.cyl("damper", [P[0] - 22, 266, P[2]], [P[0] - 22, 396, P[2]], 15, "black", copies=[[44, 0, 0]])
d.box("damper-foot", [P[0] - 32, 214, P[2] - 10, P[0] + 32, 224, P[2] + 10], "chrome", r=3)
d.box("clamp", [P[0] - 33, 394, P[2] - 16, P[0] + 33, 410, P[2] + 16], "black", r=5)
d.box("elbow", [P[0] - 18, 478, P[2] - 20, P[0] + 18, 518, P[2] + 20], "black", r=8)
E = [P[0], 505, P[2] + 5]; Tj = [300, 650, 125]
d.cyl("arm", E, Tj, 20, "chrome")
d.cyl("arm-damper", add(lerp(E, Tj, 0.12), [0, 14, 22]), add(lerp(E, Tj, 0.62), [0, 14, 22]), 15, "black")
d.cyl("arm-damper-rod", add(lerp(E, Tj, 0.62), [0, 14, 22]), add(lerp(E, Tj, 0.86), [0, 14, 22]), 7, "chrome")
d.box("joint", [Tj[0] - 18, Tj[1] - 20, Tj[2] - 20, Tj[0] + 18, Tj[1] + 20, Tj[2] + 20], "black", r=8)
d.cyl("joint-nut", [Tj[0] - 28, Tj[1] + 5, Tj[2]], [Tj[0] - 18, Tj[1] + 5, Tj[2]], 24, "chrome", sides=6)
# cup radiator: back end under the joint, open face down/forward-left
v = norm([-0.3, -0.88, 0.36])
C0 = add(Tj, [-80, 12, 10]); C1 = add(C0, mul(v, 140))
d.add("cup-bracket", "bar", "black", **{"from": Tj, "to": add(C0, [40, 0, 0])}, section=[22, 30], r=6)
d.cyl("cup-collar", sub(C0, mul(v, 16)), add(C0, mul(v, 20)), 96, "chrome")
d.cyl("cup-knurl", sub(C0, mul(v, 22)), sub(C0, mul(v, 16)), 70, "plastic#8a9099")
d.cyl("cup", add(C0, mul(v, 18)), C1, 125, "cup", sides=40)
d.cyl("cup-face", C1, add(C1, mul(v, 2)), 116, "plastic#e2e4e7")
d.save()
