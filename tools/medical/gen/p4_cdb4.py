"""XY-K-CDB-IV shortwave therapy cabinet. Writes only xy-k-cdb-iv.json."""
from lib import *
from p4lib import *

d = D("xy-k-cdb-iv", [430, 330, 830], {"shell": "gloss#e9eaeb", "head": "gloss#f1f2f3", "trim": "plastic#3a3f46",
                                       "membrane": "plastic#aeb2b7", "black": "gloss#121315", "white": "plastic#f6f6f6"})
# base: plate with round foot lobes over small castors
d.box("plate", [25, 78, 15, 405, 104, 300], "shell", r=8)
d.cyl("lobe", [55, 78, 55], [55, 102, 55], 110, "shell", copies=[[320, 0, 0], [0, 0, 220], [320, 0, 220]])
d.add("castor", "caster", "rubber#8a9097", at=[55, 0, 55], d=55, copies=[[320, 0, 0], [0, 0, 220], [320, 0, 220]])
# body with dark corner trims
d.box("body", [25, 100, 15, 405, 645, 300], "shell", r=14)
d.box("trim", [22, 104, 268, 50, 640, 303], "trim", r=10, mirror="x")
d.cyl("logo-mark", [193, 540, 299], [193, 540, 302], 60, "black", soft=True)
d.decal("logo-cross", [193, 540, 302.5], [11, 38], "front", "white", soft=True, copies=[[0, 12, 0]])
d.decal("logo-bar", [193, 551, 302.5], [34, 8], "front", "white", soft=True)
d.decal("logo-cn", [237, 552, 300.5], [25, 28], "front", "black", soft=True, repeat=rep(4, [29, 0, 0]))
d.decal("logo-en", [281, 528, 300.5], [112, 6], "front", "black", soft=True)
d.box("drawer", [56, 115, 296, 374, 300, 304], "shell", r=6)
# thin dark grip slot along most of the drawer's top edge
d.slab("drawer-grip", "front", "M 105 298 L 325 298 L 312 289 Q 215 283 118 289 Z", [298, 306], "black", r=1)
# left side: vent dots and the green rocker switch
d.box("vent-dot", [22, 610, 70, 26, 614, 74], "plastic#9aa0a6", soft=True, repeat=rep(9, [0, 0, 18]),
      copies=[[0, -18 * k, 0] for k in range(1, 11)])
d.box("switch-frame", [20, 570, 248, 26, 614, 282], "trim", r=3)
d.box("switch", [18, 576, 253, 24, 608, 277], "gloss#2e9a4a", r=3)
# control head: front rolls over into a top sloping forward ~9 deg
# control head flush with the body (same width and depth), seam at 640; its front rolls over into the sloping top
d.slab("head", "side", "M 15 640 L 301 640 L 301 727 Q 301 777 253 782 L 35 822 Q 15 824 15 804 Z", [25, 405], "head", r=22)
t = rot("x", 9, [215, 822, 20])
y = 826.6
d.box("membrane", [42, 816, 34, 388, 826, 262], "membrane", r=6, rot=t)
d.decal("title", [170, y, 42], [150, 8], "top", "plastic#5d6268", soft=True, rot=t)
d.decal("front-band", [215, y, 236], [330, 44], "top", "plastic#3a3f46", soft=True, rot=t)
d.decal("band-text", [235, y + 0.3, 228], [210, 4], "top", "plastic#d9dce0", soft=True, rot=t, copies=[[0, 0, 12]])
d.decal("led", [82, y, 92], [40, 20], "top", "plastic#2b2e33", soft=True, rot=t)
d.decal("led2", [138, y, 86], [16, 14], "top", "plastic#2b2e33", soft=True, rot=t)
d.decal("led-bar", [252, y, 72], [8, 64], "top", "plastic#2b2e33", soft=True, rot=t)
d.cyl("btn", [78, 825, 132], [78, 832, 132], 20, "white", rot=t, copies=[[36, 0, 0], [72, 0, -10], [108, 0, -10]])
d.decal("btn-mark", [78, 832.5, 132], [8, 6], "top", "plastic#3a3f45", soft=True, rot=t, copies=[[36, 0, 0], [72, 0, -10], [108, 0, -10]])
d.cyl("round-key", [206, 825, 92], [206, 831, 92], 22, "white", rot=t)
d.box("key", [222, 825, 76, 232, 830, 86], "white", r=2, rot=t, copies=[[14, 0, 0], [0, 0, 16], [14, 0, 16]])
d.lathe("knob", [332, 825, 112], [[0, 0], [24, 0], [24, 4], [22, 26], [18, 30], [0, 30]], "black", sides=20, rot=t)
d.box("lever", [372, 825, 96, 384, 842, 112], "black", r=3, rot=t)
d.save()
