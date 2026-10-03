from p1lib import *
d = D("xy-fswt-ic", [640, 400, 330], {
  "shell": "plastic#e9ebee", "rim": "plastic#d4d7dc", "black": "gloss#111214", "white": "plastic#f5f6f7",
  "green": "gloss#5ec48a", "lgreen": "gloss#bfe8cf", "grey": "plastic#5d636b", "feet": "plastic#8f959c",
  "cone": "acrylic#38c2d8d0"})
# rounded shell: base lip at the front, front panel leaning back ~21 deg, big top radius
d.slab("body", "side", "M 0 32 L 0 268 Q 0 316 48 320 L 268 326 Q 306 327 318 296 L 394 92 Q 400 74 400 56 L 400 32 "
       "Q 400 16 384 16 L 16 16 Q 0 16 0 32 Z", [110, 580], "shell", r=30)
k = (394 - 318) / (296 - 92.0)
A = math.degrees(math.atan(k))
zf = lambda y: 394 - (y - 92) * k
Q = [345, 192, zf(192)]
d.screen("panel", [126, 92, Q[2] - 5, 564, 290, Q[2] + 3], "rim", r=44, face="front", bezel=1,
         print="med_xy-fswt-ic_screen", rot=rot("x", -A, Q))
# the crop is perspective-skewed: its top-right corner shows the white rim and the turquoise applicator, its left
# edge the white body; cover those with the black glass so the panel reads as one black rounded pane (review)
X0, X1, Y0, Y1 = 126 + 1, 564 - 1, 92 + 1, 290 - 1
def uv(u, v): return f"{X0 + u * (X1 - X0):.1f} {Y1 - v * (Y1 - Y0):.1f}"
R_EDGE = [(1.0, 0), (1.0, 1.0), (0.962, 1.0), (0.97, 0.9), (0.944, 0.8), (0.911, 0.7), (0.876, 0.6), (0.845, 0.5), (0.81, 0.4),
          (0.775, 0.3), (0.734, 0.2), (0.695, 0.15), (0.6, 0.12), (0.486, 0.1), (0.074, 0.05), (0, 0.045), (0, 0)]
L_EDGE = [(0, 0.2), (0.009, 0.3), (0.036, 0.4), (0.059, 0.5), (0.085, 0.6), (0.111, 0.7), (0.138, 0.8), (0.17, 0.9), (0.22, 0.97),
          (0.23, 1.0), (0, 1.0)]
mask_r = "M " + " L ".join(uv(u, v) for u, v in R_EDGE) + " Z"
mask_l = "M " + " L ".join(uv(u, v) for u, v in L_EDGE) + " Z"
d.slab("mask-r", "front", mask_r, [Q[2] + 4.7, Q[2] + 5.4], "black", r=0.3, rot=rot("x", -A, Q))
d.slab("mask-l", "front", mask_l, [Q[2] + 4.7, Q[2] + 5.4], "black", r=0.3, rot=rot("x", -A, Q))
for i, (x, z) in enumerate(((150, 60), (540, 60), (150, 345), (540, 345))):
    d.lathe(f"foot-{i}", [x, 0, z], [[0, 0], [30, 0], [16, 9], [13, 18], [0, 18]], "feet")
# left: bottle in a white holder, cable comb, white/green handgrip with a round head
d.box("holder", [52, 40, 255, 118, 205, 352], "white", r=12)
d.box("holder-tab", [58, 150, 352, 76, 175, 362], "white", r=4)
d.lathe("bottle", [86, 40, 300], [[0, 0], [33, 0], [35, 6], [35, 180], [30, 196], [14, 206], [10, 214], [6, 250], [2, 254], [0, 254]], "white")
d.box("comb-base", [60, 205, 228, 112, 214, 248], "white", r=3)
d.cyl("comb", [64, 210, 238], [64, 252, 238], 3, "grey", repeat={"n": 7, "step": [7, 0, 0]})
d.loft("hp-grip", [sec(40, 44, 70, 22, 28, 310), sec(130, 46, 78, 23, 24, 318), sec(210, 42, 70, 21, 30, 322)], "white")
d.loft("hp-green", [sec(50, 34, 24, 12, 24, 350), sec(130, 38, 26, 13, 20, 357), sec(205, 34, 24, 12, 26, 357)], "green")
d.cyl("hp-bumper", [6, 120, 318], [6, 200, 318], 26, "grey")
# round head on top of the grip, its light-green face looking front-left (review: was facing straight left)
HH = [34, 248, 318]
RH = rot("y", -40, HH)
d.lathe("hp-head", HH, [[0, 0], [44, 0], [46, 10], [46, 58], [40, 64], [0, 64]], "white", axis="z", rot=RH)
d.lathe("hp-face", [HH[0], HH[1], HH[2] + 63], [[0, 0], [36, 0], [36, 4], [0, 4]], "lgreen", axis="z", rot=RH)
d.lathe("hp-eye", [HH[0], HH[1], HH[2] + 66], [[0, 0], [12, 0], [12, 4], [0, 4]], "grey", axis="z", rot=RH)
# right: holder with the focused applicator (grey ring, turquoise cone), white handle, hose stub
d.box("r-holder", [575, 110, 175, 612, 205, 290], "white", r=12)
d.cyl("r-handle", [598, 120, 232], [606, 240, 232], 50, "white")
H = [606, 265, 232]
R = rot("z", 40, H)
d.lathe("ring", H, [[0, 0], [66, 0], [68, 10], [62, 24], [44, 26], [0, 26]], "grey", axis="x", rot=R)
d.lathe("cone", [H[0] + 22, H[1], H[2]], [[0, 0], [52, 0], [44, 24], [16, 58], [8, 62], [0, 62]], "cone", axis="x", rot=R)
d.cyl("stub", [612, 150, 232], [636, 150, 232], 18, "white")
d.box("r-comb-base", [566, 250, 150, 590, 258, 210], "white", r=3)
d.cyl("r-comb", [578, 255, 154], [578, 290, 154], 3, "grey", repeat={"n": 7, "step": [0, 0, 8]})
d.save()
