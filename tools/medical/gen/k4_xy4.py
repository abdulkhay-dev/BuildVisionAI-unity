from k4lib import *
d = K("xy-4", [610, 1180, 1120], {"white": "plastic#f2f1ec", "cap": "rubber#1b1c1e", "black": "plastic#1c1d20",
                                  "saddle": "leather#9b9fa4", "foam": "rubber#1f2023", "blue": "gloss#2a6fd0"})
CX = 305
CAP = [[0, 0], [31, 0], [34, 8], [34, 46], [28, 56], [0, 58]]
# --- floor tubes with black end caps
for nm, z in (("rear", 95), ("front", 1080)):
    d.cyl(f"foot-{nm}", [40, 34, z], [570, 34, z], 60, "white")
    d.lathe(f"cap-{nm}", [0, 34, z], CAP, "cap", axis="x")
    d.lathe(f"cap-{nm}-r", [610, 34, z], CAP, "cap", axis="x", rot=rot("y", 180, [610, 34, z]))
# --- column (front foot to the handlebar), sleeve clamp, diagonal tube (rear foot to the column)
d.box("col-foot", [270, 30, 1040, 340, 90, 1120], "white", r=6)
d.bar("column", [CX, 60, 1070], [CX, 1000, 965], [62, 62], "white", r=6)
d.bar("sleeve", [CX, 690, 1000], [CX, 770, 991], [80, 80], "white", r=8)
d.lathe("sleeve-knob", [CX, 730, 954], [[0, 0], [9, 0], [9, 12], [20, 15], [20, 30], [0, 33]], "black", axis="z",
        rot=rot("y", 180, [CX, 730, 954]))
d.bar("diagonal", [CX, 55, 110], [CX, 470, 1010], [60, 42], "white", r=6)
d.decal("label", [CX, 900, 952.5], [36, 110], "back", "gloss#3d7fd6")
# --- seat arm with open square end, strut, saddle
d.bar("seat-arm", [CX, 505, 985], [CX, 550, 270], [58, 58], "white", r=6)
d.decal("arm-hole", [CX, 550, 269.4], [44, 44], "back", "plastic#2a2b2e")
d.cyl("pivot", [262, 505, 985], [348, 505, 985], 34, "chrome")
d.cyl("strut", [CX, 800, 975], [CX, 548, 640], 30, "white")
d.box("saddle-post", [282, 548, 380, 328, 580, 520], "white", r=4)
# heart-shaped saddle (photo): two wide rear lobes with a notch in the middle of the back, a waist, rounded nose
# (top-plane outline in x, z)
def heart(m):
    c = CX
    return (f"M {c} {305 + m} C {c - 30} {282 + m} {c - 110 + m} {270 + m} {c - 132 + m} {300 + m} "
            f"C {c - 152 + m} {330} {c - 142 + m} {420} {c - 120 + m} {470} C {c - 95 + m} {540} {c - 55 + m} {640 - m} {c} {645 - m} "
            f"C {c + 55 - m} {640 - m} {c + 95 - m} {540} {c + 120 - m} {470} C {c + 142 - m} {420} {c + 152 - m} {330} {c + 132 - m} {300 + m} "
            f"C {c + 110 - m} {270 + m} {c + 30} {282 + m} {c} {305 + m} Z")
d.slab("saddle", "top", heart(0), [568, 638], "saddle", r=24)
# --- gas spring from the diagonal up to the seat arm, resistance block on top
d.cyl("spring", [252, 150, 300], [252, 420, 545], 42, "black")
d.cyl("spring-rod", [252, 420, 545], [252, 518, 640], 16, "chrome")
d.box("spring-block", [228, 400, 515, 276, 455, 575], "black", r=8)
d.cyl("spring-pin", [252, 518, 640], [CX, 522, 640], 14, "chrome")
d.cyl("spring-foot", [252, 150, 300], [CX, 150, 300], 14, "chrome")
# --- heart-shaped footrest loop round the column base, axle, black footrests with ratchet straps
d.tube("loop", [[CX, 505, 960], [CX + 70, 470, 1060], [CX + 70, 320, 1085], [CX + 70, 255, 1000], [CX + 70, 330, 910],
                [CX, 470, 935]], 28, "white", bend=55)
d.cyl("axle", [130, 275, 1000], [480, 275, 1000], 22, "chrome")
for nm, x0 in (("l", 55), ("r", 465)):
    d.box(f"footrest-{nm}", [x0, 258, 920, x0 + 90, 290, 1080], "black", r=10)
    d.strap(f"strap-{nm}", [[x0 + 10, 290, 990], [x0 + 45, 330, 1010], [x0 + 70, 250, 1050]], [24, 4], "black", bend=25)
    # long ratchet strap end hanging below the footrest (photo)
    xs = x0 + (75 if x0 > CX else 15)
    d.strap(f"strap-tail-{nm}", [[xs, 262, 1050], [xs, 210, 1066], [xs, 165, 1078]], [24, 4], "black", bend=30)
    d.decal(f"strap-teeth-{nm}", [xs + (12.5 if x0 > CX else -12.5), 215, 1064], [16, 80], "right" if x0 > CX else "left", "plastic#45474b",
            repeat=rep(1, [0, 0, 0]))
# --- handlebar (two C loops, tips turned inward), blue LCD counter
d.tube("handlebar", [[195, 1095, 905], [42, 1095, 925], [42, 990, 950], [568, 990, 950], [568, 1095, 925], [415, 1095, 905]],
       38, "foam", bend=75)
d.box("lcd", [262, 1008, 932, 348, 1108, 972], "blue", r=16, rot=rot("x", -10, [CX, 1005, 950]))
d.screen("lcd-screen", [274, 1040, 927, 336, 1094, 934], "black", face="back", bezel=3, rot=rot("x", -10, [CX, 1005, 950]))
d.decal("lcd-btn", [CX, 1022, 931.4], [16, 10], "back", "gloss#d62b25", rot=rot("x", -10, [CX, 1005, 950]))
d.save()
