from k4lib import *
d = K("xy-33", [1040, 840, 830], {"frame": "plastic#f1f1ee", "wood": "wood#dcae6c", "felt": "fabric#1f7a5a",
                                  "foot": "rubber#18191b", "cu": "metal#b8734a", "red": "gloss#d33a2c", "knob": "plastic#1c1d20"})
T = 17                                  # top tilt, front edge low (photo: the back edge stands ~250 above the frame)
P = [520, 545, 840]                     # tilt pivot (front edge underside, on the front legs' copper hinges)
TR = rot("x", T, P)
tn = math.tan(math.radians(T))
under = lambda z: P[1] + (P[2] - z) * tn - 4
LX, LZ = (110, 930), (130, 720)
# --- white square-tube frame: 4 legs, braces round all sides at two levels, black feet, copper hinge brackets
for i, x in enumerate(LX):
    for j, z in enumerate(LZ):
        top = 520                       # all four legs equal (photo); hinges on the front legs, black caps on the back ones
        d.box(f"leg{i}{j}", [x - 20, 30, z - 20, x + 20, top, z + 20], "frame", r=3)
        d.box(f"foot{i}{j}", [x - 22, 0, z - 22, x + 22, 32, z + 22], "foot", r=4)
        if j == 1:
            d.box(f"hinge{i}{j}", [x - 18, top, z - 18, x + 18, top + 25, z + 18], "cu", r=3)
        else:
            d.box(f"cap{i}{j}", [x - 21, top, z - 21, x + 21, top + 8, z + 21], "foot", r=3)
# centre prop under the raised back of the top (hidden from the front in the photo)
d.bar("prop", [520, 470, LZ[0]], [520, under(170) - 4, 170], [60, 20], "frame", r=3)
for k, y in (("lo", 215), ("hi", 455)):
    d.box(f"brace-f-{k}", [LX[0], y, LZ[1] - 15, LX[1], y + 34, LZ[1] + 15], "frame", r=3, copies=[[0, 0, LZ[0] - LZ[1]]])
    d.box(f"brace-s-{k}", [LX[0] - 15, y, LZ[0], LX[0] + 15, y + 34, LZ[1]], "frame", r=3, copies=[[LX[1] - LX[0], 0, 0]])
d.decal("bolt", [LX[0], 472, LZ[1] + 20.5], [8, 8], "front", "plastic#8a8d92", copies=[[0, -240, 0], [LX[1] - LX[0], 0, 0], [LX[1] - LX[0], -240, 0]])
# --- tilting top: light-wood border, green felt, accessories
d.box("under", [40, 545, 20, 1000, 557, 820], "wood", r=2, rot=TR)
d.box("rim-l", [0, 545, 0, 60, 587, 840], "wood", r=5, rot=TR, copies=[[980, 0, 0]])
d.box("rim-b", [55, 545, 0, 985, 587, 60], "wood", r=5, rot=TR, repeat={"n": 2, "step": [0, 0, 780], "local": True})
d.box("felt", [60, 545, 60, 980, 577, 780], "felt", r=1, rot=TR)
d.decal("tag", [300, 587.5, 30], [60, 16], "top", "gloss#2a4fae", rot=TR)
d.decal("tag2", [780, 587.5, 30], [40, 12], "top", "plastic#d9d9d9", rot=TR)
# plank with two upright dowels (front left)
d.box("plank", [230, 577, 600, 470, 597, 700], "wood", r=4, rot=TR)
d.cyl("dowel", [290, 595, 650], [290, 705, 650], 26, "wood", rot=TR, copies=[[120, 0, 0]])
# block with two black knobs (middle)
d.box("block", [470, 577, 420, 650, 613, 500], "wood", r=5, rot=TR)
d.lathe("knob", [515, 613, 460], [[0, 0], [8, 0], [8, 10], [18, 12], [18, 26], [0, 28]], "knob", rot=TR, copies=[[90, 0, 0]])
# rail with a roller along the right edge
d.box("rail", [850, 577, 130, 940, 601, 700], "wood", r=5, rot=TR)
# photo: a small stop at the back end, a slider block with a cross roller near the front end
d.box("rail-stop", [860, 601, 140, 930, 625, 185], "wood", r=5, rot=TR)
d.box("slider", [852, 601, 520, 938, 645, 640], "wood", r=6, rot=TR)
d.cyl("roller", [846, 660, 580], [944, 660, 580], 38, "wood", rot=TR)
# red tilt crank under the left edge at the back
d.cyl("crank-shaft", [92, 720, 140], [20, 720, 140], 16, "chrome")
d.box("crank-arm", [10, 660, 125, 28, 735, 155], "red", r=6)
d.cyl("crank-grip", [19, 670, 140], [-12, 670, 140], 26, "red")
d.save()
