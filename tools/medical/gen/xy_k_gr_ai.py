from lib import *
from p2util import *
# silver desktop interferential unit: deep rounded front frame, recessed tilted panel (picture), socket slot, side grips
d = D("xy-k-gr-ai", [420, 360, 232], {"shell": "plastic#dcdfe3", "bezel": "plastic#c8cdd5", "blue": "plastic#8fb6e0",
      "slot": "plastic#c9cdd3", "dark": "plastic#2c3036", "socket": "gloss#2f5fbf"})
d.cyl("foot", [40, 0, 40], [40, 9, 40], 22, "rubber#1c1d20", copies=[[340, 0, 0], [0, 0, 280], [340, 0, 280]])
d.box("body", [4, 8, 0, 416, 228, 242], "shell", r=14)
# filler between the body and the leaning frame
d.add("body-front", "slab", "shell", plane="side", outline="M 236 8 L 286 8 L 246 222 L 236 222 Z", w=[6, 414], r=10)
win, slot = rr(38, 92, 382, 214, 18), rr(45, 22, 375, 74, 14)
# the whole front frame leans back 10° about its bottom back edge (the photo: top flush with the body, bottom protruding, chin undercut)
T = rot("x", -10, [210, 8, 280])
d.add("bezel", "slab", "bezel", plane="front", outline=rr(0, 8, 420, 221, 40) + " " + win + " " + slot, w=[280, 360], r=16, rot=T)
d.add("lining", "slab", "blue", plane="front", outline=win + " " + rr(45, 99, 375, 207, 13), w=[318, 352], r=1, rot=T)
t = rot("x", -18, [210, 103.5, 326])
d.add("panel", "screen", "slot", box=[42, 103.5, 318, 378, 221.5, 326], r=10, face="front", bezel=4, print="med_xy-k-gr-ai_screen", rot=t)
d.box("panel-back", [40, 90, 290, 380, 216, 300], "slot", rot=T)
d.box("slot-back", [44, 20, 300, 376, 76, 330], "slot", r=4, rot=T)
d.box("company", [70, 52, 330, 210, 57, 331], "plastic#6c7279", soft=True, rot=T)
d.box("company2", [70, 42, 330, 230, 45, 331], "plastic#8a9099", soft=True, rot=T)
d.box("icon", [238, 40, 330, 252, 56, 331], "dark", soft=True, rot=T)
d.box("icon2", [262, 40, 330, 276, 56, 331], "gloss#e8c22a", soft=True, rot=T)
d.cyl("socket", [300, 50, 330], [300, 50, 336], 26, "socket", copies=[[44, 0, 0]], rot=T)
d.cyl("socket-in", [300, 50, 336], [300, 50, 337], 12, "dark", soft=True, copies=[[44, 0, 0]], rot=T)
d.box("grip", [2, 140, 190, 6, 182, 290], "dark", r=6, mirror="x")
d.save()
