from lib import *
from p2util import *
# old grey interferential cabinet on a black plinth: tilted membrane panel head, output strip, logo, drawer, door
d = D("xy-k-gr-bii", [620, 560, 1180], {"shell": "gloss#c8ccd2", "plinth": "plastic#2a2d33", "panel": "plastic#c6cacf",
      "strip": "plastic#dadcdf", "dark": "plastic#3d4248", "black": "gloss#141517", "red": "gloss#d8323f", "blue": "gloss#2f5fbf",
      "yellow": "gloss#e8c22a", "logo": "gloss#2f6fbf"})
X0, X1, Z0, Z1 = 60, 560, 40, 490
# plinth + castors
d.add("plinth", "slab", "plinth", plane="top", outline=rr(0, 0, 620, 560, 75), w=[138, 205], r=10)
d.add("plinth-lo", "slab", "plastic#1f2226", plane="top", outline=rr(40, 30, 580, 530, 60), w=[112, 142], r=8)
for i, (x, z) in enumerate(((60, 50), (560, 50), (60, 510), (560, 510))):
    d.add(f"castor{i}", "caster", "rubber#e8e9eb", at=[x - 17, 0, z], d=100)
    d.add(f"castor{i}b", "caster", "rubber#e8e9eb", at=[x + 17, 0, z], d=100)
# body and head
d.box("body", [X0, 195, Z0, X1, 900, Z1], "shell", r=30)
t = rot("x", -10, [310, 900, Z1 + 10])
d.add("head", "slab", "shell", plane="side", outline=f"M {Z0} 885 L {Z1 + 10} 885 L {Z1 + 10 - 48} 1170 L {Z0} 1170 Z", w=[X0 - 5, X1 + 5], r=34)
d.box("panel", [X0 + 15, 935, Z1 + 6, X1 - 15, 1140, Z1 + 14], "panel", r=10, rot=t)
zp = Z1 + 14.2
import math
def tc(cs): return [[c[0], c[1], c[2] - c[1] * math.tan(math.radians(10))] for c in cs]
d.box("p-title", [X0 + 18, 1105, zp - 1, X1 - 18, 1137, zp], "plastic#c3c7cc", soft=True, rot=t)
d.box("p-logo", [X0 + 30, 1112, zp, X0 + 110, 1130, zp + 0.5], "logo", soft=True, rot=t)
d.box("p-name", [X1 - 190, 1118, zp, X1 - 40, 1128, zp + 0.5], "dark", soft=True, rot=t)
d.box("p-mid", [309, 950, zp - 1, 311, 1100, zp], "plastic#9aa0a8", soft=True, rot=t)
d.box("p-win", [X0 + 30, 1068, zp, X0 + 62, 1090, zp + 0.5], "plastic#3a1416", soft=True, rot=t,
      copies=tc([[0, -32, 0], [0, -64, 0], [70, -32, 0], [70, -64, 0], [240, 0, 0], [240, -32, 0], [240, -64, 0], [310, -32, 0], [310, -64, 0]]))
d.box("p-led", [X0 + 75, 1042, zp, X0 + 135, 1048, zp + 0.5], "gloss#3cc060", soft=True, rot=t,
      copies=tc([[90, 0, 0], [240, 0, 0], [330, 0, 0], [0, -32, 0], [90, -32, 0], [240, -32, 0], [330, -32, 0]]))
d.box("p-strip", [X0 + 40, 978, zp, X0 + 150, 994, zp + 0.5], "dark", r=6, soft=True, rot=t, copies=tc([[110, 0, 0], [240, 0, 0], [350, 0, 0]]))
d.box("p-btn", [X0 + 30, 952, zp, X0 + 46, 964, zp + 0.5], "dark", soft=True, rot=t, repeat={"n": 6, "step": [34, 0, 0]},
      copies=tc([[240, 0, 0]]))
# output strip under the head
d.box("out-recess", [X0 + 20, 760, Z1 - 12, X1 - 20, 832, Z1 + 1], "plastic#9aa0a8", r=10)
d.box("out", [X0 + 24, 764, Z1 - 10, X1 - 24, 828, Z1 - 4], "strip", r=8)
xs = [(158, "yellow"), (196, "blue"), (234, "blue"), (272, "blue"), (348, "blue"), (386, "blue"), (424, "blue"), (462, "yellow")]
for i, (x, m) in enumerate(xs):
    d.cyl(f"knob{i}-skirt", [x, 796, Z1 - 4], [x, 796, Z1 + 4], 30, "chrome")
    d.cyl(f"knob{i}", [x, 796, Z1 + 4], [x, 796, Z1 + 16], 22, m)
d.cyl("socket", [X0 + 42, 812, Z1 - 4], [X0 + 42, 812, Z1 + 2], 14, "black", copies=[[0, -30, 0], [30, 0, 0], [30, -30, 0], [362, 0, 0], [362, -30, 0], [392, 0, 0], [392, -30, 0]])
d.box("warn", [X0 + 60, 775, Z1 - 4, X0 + 76, 790, Z1 - 3], "yellow", soft=True, copies=[[364, 0, 0]])
# logo, drawer, door, model plate
d.cyl("logo", [215, 640, Z1], [215, 640, Z1 + 1.5], 46, "logo", soft=True)
d.box("logo-x", [212, 622, Z1 + 1.5, 218, 658, Z1 + 2], "shell", soft=True)
d.box("logo-cn", [250, 640, Z1, 390, 664, Z1 + 1.5], "logo", soft=True)
d.box("logo-en", [250, 622, Z1, 390, 632, Z1 + 1.5], "logo", soft=True)
d.box("drawer", [X0 + 8, 425, Z1 - 4, X1 - 8, 592, Z1 + 6], "shell", r=12)
d.box("pull", [260, 555, Z1 + 1, 360, 588, Z1 + 7], "plastic#aeb3ba", r=10)
d.box("door", [X0 + 8, 205, Z1 - 4, X1 - 8, 418, Z1 + 4], "shell", r=12)
d.box("plate", [250, 330, Z1 + 4, 370, 348, Z1 + 5], "dark", soft=True)
d.box("plate-t", [255, 352, Z1 + 4, 365, 357, Z1 + 5], "plastic#6c7279", soft=True)
# right side: vents, rocker switch, handpiece holder
d.box("vent", [X1, 260, Z1 - 60, X1 + 1.5, 266, Z1 - 20], "dark", soft=True, repeat={"n": 9, "step": [0, 18, 0]})
d.box("rocker", [X1 + 3, 1080, Z1 - 70, X1 + 12, 1120, Z1 - 50], "gloss#2a9a4a", r=3)
d.box("holder", [X1 + 3, 1000, Z1 - 140, X1 + 50, 1050, Z1 - 60], "shell", r=14)
d.cyl("handpiece", [X1 + 40, 1040, Z1 - 150], [X1 + 40, 1040, Z1 + 40], 42, "plastic#d8dbe0", d2=48)
d.add("handpiece-cup", "lathe", "plastic#d8dbe0", at=[X1 + 40, 1040, Z1 + 40], axis="z", profile=[[0, 0], [24, 0], [30, 20], [28, 30], [0, 30]])
d.save()
