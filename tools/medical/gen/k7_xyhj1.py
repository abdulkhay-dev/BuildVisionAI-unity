"""xyhj-1 Anklebone Rectification Trainer: white tube base on castors, black diamond-plate footboard hinged at the
front (heels) and raised toward the post at the back, white post with a T handle and two black foam grips."""
from k7lib import *

d = D("xyhj-1", [470, 720, 1460], {
    "white": "plastic#eceeec", "black": "plastic#1a1b1d", "plate": "metal#26282a", "foam": "rubber#1c1d1f",
    "stud": "metal#4a4d50"})
BY = 72
# --- base: rounded tube loop, two inner rack bars with teeth, back plate for the post, castors
d.tube("loop", [[20, BY, 360], [20, BY, 700], [450, BY, 700], [450, BY, 20], [20, BY, 20], [20, BY, 360]], 30, "white", bend=70)
for nm, x in (("l", 150), ("r", 320)):
    d.box(f"rack-{nm}", [x - 16, BY - 8, 20, x + 16, BY + 8, 700], "white", r=3)
    d.box(f"tooth-{nm}", [x - 16, BY + 7, 360, x + 16, BY + 20, 372], "white", r=2, repeat={"n": 7, "step": [0, 0, 34]})
d.box("post-plate", [175, BY - 10, 10, 295, BY + 12, 90], "white", r=5)
for x in (30, 440):
    for z in (40, 680):
        d.caster(f"castor-{x}-{z}", [x, 0, z], 50, "rubber#1f2022")
# --- footboard: black diamond plate, hinged at the front (z 690) and raised 30° toward the back
P = [235, 88, 655]
tilt = rot("x", 30, P)
outline = ("M 45 655 L 45 270 Q 45 230 85 230 L 385 230 Q 425 230 425 270 L 425 655 Z")
d.slab("board", "top", outline, [P[1] - 14, P[1]], "plate", r=3, rot=tilt)
# diamond plate: rows of short raised dashes, alternately turned +45 / -45 degrees in the plate (herringbone)
for k in range(12):
    z = 256 + k * 34
    sg = 1 if k % 2 == 0 else -1
    x0 = 70 if k % 2 == 0 else 87
    c = [x0, P[1] + 0.6, z]
    d.decal(f"stud-{k}", c, [15, 5], "stud", face="top", soft=True, rot=rot("y", 45 * sg, c), rots=[tilt],
            repeat={"n": 10, "step": [24.04, 0, 24.04 * sg], "local": True})
d.cyl("heel-bar", [46, 92, 662], [424, 92, 662], 30, "foam")
d.cyl("hinge", [20, 80, 655], [450, 80, 655], 16, "white")
# white heel hoop over the board's front edge (photo: a raised U tube from the base sides across the front)
d.tube("heel-hoop", [[28, BY + 8, 590], [28, BY + 78, 676], [442, BY + 78, 676], [442, BY + 8, 590]], 26, "white", bend=34)
# prop struts from under the board's back half into the rack teeth
for nm, x in (("l", 150), ("r", 320)):
    d.cyl(f"strut-{nm}", [x, 262, 340], [x, BY + 16, 440], 12, "black")
d.cyl("strut-bar", [150, 262, 340], [320, 262, 340], 12, "black")
# --- white post at the back centre: lower tube, collar, upper tube with a black lock knob and a label; T handle
d.cyl("post-low", [235, BY, 40], [235, 950, 40], 38, "white")
d.cyl("post-collar", [235, 940, 40], [235, 975, 40], 46, "white")
d.cyl("post-up", [235, 970, 40], [235, 1432, 40], 32, "white")
d.lathe("lock-knob", [256, 1225, 40], [[0, 0], [7, 0], [7, 8], [15, 10], [15, 26], [0, 28]], "black", axis="x")
d.decal("label", [235, 1035, 59.2], [18, 26], "plastic#c9ccd0", face="front", soft=True)
d.cyl("t-bar", [12, 1440, 40], [458, 1440, 40], 28, "white")
d.sphere("t-joint", [235, 1440, 40], 40, "white")
d.cyl("grip-l", [10, 1440, 40], [160, 1440, 40], 42, "foam")
d.cyl("grip-r", [310, 1440, 40], [460, 1440, 40], 42, "foam")
d.save()
