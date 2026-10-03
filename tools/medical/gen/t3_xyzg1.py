# XYZG-1 electrical elbow traction chair (table-3 batch).
# Photo: chair faces front; patient's right side (x small) has a white upright frame with the elbow dial,
# a black forearm bar with blue cradles, red lever, teal weight plate, motor box and remote; the patient's left
# side (x large) has a white bracket from the backrest carrying a second elbow station that reaches out sideways.
import math
from lib import *
d = D("xyzg-1", [1230, 1010, 1170], {
  "frame": "plastic#f1f2f0", "pad": "leather#a9cdec", "cradle": "plastic#8ec0ec", "blk": "rubber#1b1c1f",
  "bar": "plastic#2a2c30", "red": "gloss#c8343a", "chr": "chrome", "plate": "plastic#2aa595", "grey": "plastic#b9bec5",
  "strap": "fabric#20262c", "brass": "metal#b89b52", "box": "plastic#2a64b8"})
# ---- base: two sled skis along z (black caps), cross tubes, seat posts
for nm, x in (("r", 130), ("l", 720)):
    d.cyl("ski-" + nm, [x, 40, 80], [x, 40, 900], 40, "frame")
    d.cyl("ski-cap-" + nm, [x, 40, 45], [x, 40, 82], 46, "blk", copies=[[0, 0, 853]])
d.bar("cross", [130, 45, 300], [720, 45, 300], [40, 40], "frame", r=4, copies=[[0, 0, 380]])
d.cyl("leveler", [330, 0, 300], [330, 25, 300], 50, "brass", copies=[[250, 0, 0], [0, 0, 380], [250, 0, 380]])
d.bar("seat-post", [330, 65, 300], [330, 470, 300], [45, 45], "frame", r=4, copies=[[250, 0, 0], [0, 0, 380], [250, 0, 380]])
d.bar("seat-rail", [270, 470, 300], [640, 470, 300], [40, 40], "frame", r=4, copies=[[0, 0, 380]])
# ---- seat and backrest (light blue PU), backrest with a white tube rim
d.box("seat", [230, 490, 250, 690, 560, 760], "pad", r=26, puff=4)
d.box("seat-board", [250, 470, 270, 670, 492, 740], "frame", r=4)
br = rot("x", -7, [460, 520, 230])
d.box("back", [240, 560, 205, 680, 1110, 265], "pad", r=24, puff=4, rot=br)
d.tube("back-rim", [[235, 500, 200], [235, 1130, 200], [685, 1130, 200], [685, 500, 200]], 28, "frame", bend=90, rot=br)
d.bar("back-strut", [460, 470, 230], [460, 600, 205], [50, 30], "frame", r=4)
# ---- right station (x small): white upright frame on the right ski
F = 130
d.bar("up-back", [F, 60, 380], [F, 960, 520], [45, 45], "frame", r=4)
d.bar("up-front", [F, 60, 840], [F, 980, 640], [45, 45], "frame", r=4)
d.bar("up-mid", [F, 400, 470], [F, 400, 780], [40, 40], "frame", r=4)
d.bar("up-top", [F, 975, 480], [F, 975, 700], [50, 50], "frame", r=4)
d.box("up-bracket", [60, 920, 520, 120, 990, 600], "grey", r=8)
d.bar("up-arm", [F, 975, 600], [300, 975, 600], [50, 50], "frame", r=4)
d.cyl("dial-r", [300, 975, 600], [330, 975, 600], 150, "blk")
d.cyl("dial-r-face", [330, 975, 600], [333, 975, 600], 130, "plastic#e8e8e8", soft=True)
d.cyl("dial-r-hub", [333, 975, 600], [345, 975, 600], 40, "blk", soft=True)
def cradle(id, a, b, w, h, mat="cradle"):
    """U foam cradle along a->b (mostly along z): a low base and two raised rounded side lips (photo)."""
    lo = h * 0.55; dy = (h - lo) / 2
    d.bar(id, [a[0], a[1] - dy, a[2]], [b[0], b[1] - dy, b[2]], [w, lo], mat, r=22)
    lw = w * 0.3; off = (w - lw) / 2
    d.bar(id + "-lip", [a[0] - off, a[1], a[2]], [b[0] - off, b[1], b[2]], [lw, h], mat, r=lw / 2 - 1,
          copies=[[2 * off, 0, 0]])
# black forearm bar from the dial forward, two blue cradles with black straps, red lever hanging down
d.cyl("fbar-r", [345, 975, 600], [400, 900, 1000], 45, "bar")
d.cyl("fbar-r-cap", [400, 900, 1000], [403, 896, 1010], 45, "blk")
cradle("cradle-r1", [340, 1040, 560], [355, 1035, 700], 140, 120)
d.bar("cradle-r1-strap", [340, 1048, 620], [345, 1048, 650], [146, 128], "strap", r=30)
cradle("cradle-r2", [372, 990, 780], [388, 965, 900], 130, 110)
d.bar("cradle-r2-strap", [378, 985, 820], [382, 980, 850], [134, 116], "plastic#8e96a3", r=30)
d.bar("lever-r", [330, 960, 640], [330, 640, 650], [40, 30], "red", r=6)
d.bar("lever-r-chr", [330, 640, 650], [330, 560, 650], [30, 22], "chr", r=4)
d.cyl("lever-r-knob", [330, 930, 668], [330, 930, 700], 34, "blk")
# teal weight plate on an axle out of the frame, motor box low, small blue control box, coiled remote
d.cyl("axle-r", [F, 600, 700], [8, 600, 700], 28, "frame")
d.lathe("plate-r", [112, 600, 700], [[16, 0], [86, 0], [95, 5], [95, 15], [86, 20], [16, 20]], "plate", axis="x",
        copies=[[-22, 0, 0], [-44, 0, 0]])
d.cyl("plate-r-hub", [46, 600, 700], [40, 600, 700], 50, "plastic#1f8577")
d.box("motor", [150, 120, 470, 290, 330, 690], "grey", r=12)
d.cyl("motor-can", [220, 230, 690], [220, 230, 760], 110, "grey")
d.box("ctrl", [95, 750, 700, 125, 840, 760], "box", r=6)
d.tube("remote-cord", [[100, 745, 730], [88, 560, 745], [80, 300, 760]], 7, "blk", bend=60, soft=True)
d.box("remote", [64, 110, 742, 96, 300, 778], "blk", r=12)
# ---- left station (x large): white bracket from the backrest out sideways, elbow dial, red/chrome forearm bar,
# two blue cradles, white/red post down with a teal plate
d.bar("brk-l", [690, 1010, 240], [930, 1010, 360], [50, 40], "frame", r=4)
d.bar("brk-l2", [690, 880, 240], [900, 1000, 350], [40, 30], "frame", r=4)
d.lathe("dial-l", [960, 1000, 380], [[0, 0], [80, 0], [80, 30], [0, 30]], "blk", axis="x")
d.cyl("fbar-l", [990, 1000, 380], [1200, 975, 1000], 40, "red")
d.cyl("fbar-l-chr", [1060, 992, 580], [1210, 974, 1005], 30, "chr")
cradle("cradle-l1", [960, 1060, 380], [1010, 1060, 540], 150, 120)
d.tube("cradle-l1-strap", [[960, 1000, 450], [960, 1130, 455], [1060, 1140, 470], [1060, 1000, 475]], 30, "strap", bend=40, soft=True)
cradle("cradle-l2", [1100, 1035, 700], [1140, 1030, 840], 130, 110)
d.bar("cradle-l2-strap", [1110, 1040, 755], [1120, 1040, 785], [136, 118], "plastic#8e96a3", r=30)
d.bar("post-l", [990, 990, 470], [990, 640, 470], [40, 40], "frame", r=4)
d.bar("post-l-red", [992, 960, 470], [992, 760, 470], [42, 30], "red", r=4)
d.cyl("plate-l", [960, 720, 470], [1015, 720, 470], 170, "plate")
d.cyl("lever-l-knob", [1010, 900, 470], [1040, 900, 470], 34, "blk")
d.save()
