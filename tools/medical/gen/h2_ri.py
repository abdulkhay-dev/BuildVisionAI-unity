from h2lib import *
# XY-SL-RI children whirlpool tub (photo front-left): white glossy body with big vertical corner radii over a recessed
# plinth carrying a light-blue lettering band; left control deck with red/chrome buttons and a dial; U-shaped glass
# window in the front wall; lilac padded bars on the front and back rims; water inside; chrome jet on the right wall.
W, DP, H = 1305, 1010, 1010
RY, RT = 968, 42
d = D("xy-sl-ri", [W, DP, H], {
    "shell": "gloss#f7f8f9", "inner": "gloss#eef1f4", "line": "plastic#dfe3e8", "lilac": "leather#b2a8e0",
    "blue": "gloss#2f6fd0", "pale": "gloss#cfe0f6", "red": "gloss#d93a32", "water": "acrylic#b5dccf70"})
Y0 = 250                                          # bottom of the upper body (plinth below)
DX = 330                                          # control deck width (left end)
d.box("plinth", [45, 0, 45, W - 45, Y0 + 20, DP - 45], "shell", r=60)
d.slab("deck", "top", P(rr(0, 0, DX + 10, DP, [0, 0, 150, 150])), [Y0, RY + 2], "shell", r=30)
d.slab("end-r", "top", P(rr(W - 150, 0, W, DP, [150, 150, 0, 0])), [Y0, RY + 2], "shell", r=30)
d.box("back", [DX, Y0, 0, W - 140, RY + 2, 45], "shell", r=20)
WX0, WX1, WB, WR0, WR1 = 410, 1150, 600, 300, 70       # window: x range, bottom, lower-left / lower-right radius
front = (f"M {DX} {Y0} L {W - 140} {Y0} L {W - 140} {RY} L {WX1} {RY} L {WX1} {WB + WR1} Q {WX1} {WB} {WX1 - WR1} {WB} "
         f"L {WX0 + WR0} {WB} Q {WX0} {WB} {WX0} {WB + WR0} L {WX0} {RY} L {DX} {RY} Z")
d.slab("front", "front", front, [DP - 45, DP], "shell", r=18)
d.slab("glass", "front", P(rr(WX0 - 20, WB - 20, WX1 + 20, RY + 10, [WR1, 0, 0, WR0])), [DP - 34, DP - 26], "glass", r=2)
# basin + rim (front rim thin: the lilac bar sits on the glass), water
hole = rr(DX + 20, 60, W - 160, DP - 40, 50)
d.slab("basin-floor", "top", P(rr(DX, 40, W - 140, DP - 30, 40)), [Y0 + 40, Y0 + 70], "inner", r=4)
U = [(DX, 40), (W - 140, 40), (W - 140, DP - 46), (W - 160, DP - 46), (W - 160, 60), (DX + 20, 60), (DX + 20, DP - 46), (DX, DP - 46)]
d.slab("walls", "top", P(U), [Y0 + 60, RY], "inner", r=4)
d.slab("rim", "top", ring(rr(0, 0, W, DP, 150), hole), [RY, RY + RT], "shell", r=18)
d.slab("water", "top", P(offset(hole, 4)), [Y0 + 70, 884], "water", r=2, soft=True)
# lilac padded bars on the front and back rims
d.box("bar-front", [DX + 10, RY + RT - 10, DP - 72, W - 30, RY + RT + 42, DP - 8], "lilac", r=24)
d.box("bar-back", [DX - 60, RY + RT - 10, 8, 980, RY + RT + 42, 72], "lilac", r=24)
# deck controls: row along z of 3 red + 3 chrome buttons and a chrome dial with a blue ring
T = RY + RT
for i in range(3):
    d.lathe(f"btn-red{i}", [150, T - 2, 300 + i * 90], [[0, 0], [18, 0], [18, 12], [14, 16], [0, 16]], "red")
    d.lathe(f"btn-chr{i}", [150, T - 2, 570 + i * 90], [[0, 0], [22, 0], [22, 10], [16, 16], [0, 18]], "chrome")
d.lathe("dial-ring", [150, T - 2, 860], [[0, 0], [38, 0], [38, 8], [0, 8]], "blue")
d.lathe("dial", [150, T + 6, 860], [[0, 0], [28, 0], [28, 14], [20, 20], [0, 20]], "chrome")
d.lathe("jet", [W - 162, 860, 380], [[0, 0], [30, 0], [30, 8], [20, 12], [0, 12]], "chrome", axis="x",
        rot=rot("z", 180, [W - 162, 860, 380]))
# left end: logo near the front corner, seam and screws
logo_round(d, "logo", [0, 700, 330], 64, face="left")
text(d, "logo-t", "翔宇医疗", [-1.6, 684, 380], 34, "blue", face="left")
d.decal("logo-sub", [-1.6, 660, 465], [170, 8], "left", "pale", soft=True)
d.box("seam", [-1, Y0 + 20, DP - 120, 2, RY - 10, DP - 114], "line", r=1, soft=True)
d.lathe("screw", [-1, 300, DP - 117], [[0, 0], [5, 0], [4, 2], [0, 2]], "plastic#9aa0a8", axis="x", soft=True,
        repeat=rep(5, [0, 150, 0]))
# plinth lettering band on the front
d.slab("plate", "front", P(rr(380, 50, 1220, 200, 70)), [DP - 46, DP - 40], "pale", r=2)
text(d, "plate-text", "翔宇医疗设备有限责任公司", [410, 98, DP - 39.5], 54, "blue", stroke=9)
d.save()
