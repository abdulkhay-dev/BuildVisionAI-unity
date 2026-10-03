"""Intermittent pneumatic compression XY-IPC-IID (13" touch screen bedside unit). Writes only xy-ipc-iid.json.
Review 2026-10-02: in both photos the white body behind the screen is about as deep as the screen is wide (~320 mm)
with a STRAIGHT top slope down to a low (~100 mm) back and overhangs the tray at the back; the tray sticks out
~30 mm in front of the bezel. Size D 260 -> 380, H 230 -> 250 (estimate contradicted by the photos)."""
from p5lib import *

W, DP, H = 340, 380, 250
ZB = 322                              # front of the body (behind the bezel)
d = D("xy-ipc-iid", [W, DP, H], {"stand": "plastic#d9dbde", "ped": "plastic#9a9ea4", "body": "plastic#f4f5f6",
                                 "black": "gloss#0d0e10", "panel": "plastic#d3d6da", "dark": "plastic#2b2d31",
                                 "blue": "gloss#2f7fd8", "white": "gloss#f7f7f7", "slot": "plastic#5c6066"})
# light-grey stand tray (sticks out in front of the screen) with a raised rim, darker pedestal under the body
TZ0, TZ1 = 98, DP
d.slab("stand", "top", rrect(0, TZ0, W, TZ1, 30), [0, 18], "stand", r=5)
d.slab("rim", "top", rrect(0, TZ0, W, TZ1, 30) + " " + rrect(16, TZ0 + 16, W - 16, TZ1 - 16, 16), [17, 23], "stand", r=2)
d.box("pedestal", [50, 17, 130, W - 50, 41, 330], "ped", r=5)
# white body, side profile: tall behind the bezel, straight top slope down to a low rounded back, overhanging the tray
d.slab("body", "side", f"M 3 40 L {ZB - 4} 40 L {ZB - 34} 228 L 270 231 L 58 140 Q 3 122 3 80 Z", [18, W - 18], "body", r=22)
# black bezel with big corner radii, tilted back, the touch screen in it
tilt = rot("x", -9, [W / 2, 36, ZB + 26])
d.slab("bezel", "front", rrect(6, 36, W - 6, 252, 38), [ZB - 4, ZB + 26], "black", r=7, rot=tilt)
d.add("screen", "screen", "black", box=[30, 58, ZB + 26, W - 30, 230, ZB + 27], r=2, face="front", bezel=1,
      print="med_xy-ipc-iid_screen", rot=tilt)
# left side: long recessed grey panel (DC jack, icons, blue-ringed air connector, white knob), 3 rows of vent slots
XL = 18
d.box("lp", [XL - 2, 74, 62, XL + 3, 128, 240], "panel", r=9)
d.cyl("dc", [XL - 1, 104, 86], [XL - 4, 104, 86], 9, "dark")
d.decal("dc-txt", [XL - 2.2, 92, 86], [16, 4], "left", "dark", soft=True)
d.decal("icon1", [XL - 2.2, 102, 116], [7, 9], "left", "dark", soft=True)
d.decal("icon2", [XL - 2.2, 102, 138], [9, 9], "left", "blue", soft=True)
d.cyl("air-ring", [XL - 1, 101, 168], [XL - 9, 101, 168], 30, "blue")
d.cyl("air-in", [XL - 9, 101, 168], [XL - 11, 101, 168], 16, "white")
d.lathe("knob", [XL - 1, 101, 206], [[0, 0], [16, 0], [16, 13], [13, 17], [0, 17]], "white", axis="x",
        rot=rot("z", 180, [XL - 1, 101, 206]))
d.decal("knob-txt", [XL - 2.2, 101, 228], [5, 26], "left", "dark", soft=True)
d.box("vent-l", [XL - 1.5, 48, 82, XL + 2, 51, 140], "slot", r=1.2, repeat=rep(3, [0, 8, 0]), copies=[[0, 0, 70]])
# right side: recessed grey panel (2 icons, black 6-pin connector, dot speaker grille), 3 rows of vent slots
XR = W - 18
d.box("rp", [XR - 3, 78, 70, XR + 2, 130, 252], "panel", r=9)
d.decal("ricon1", [XR + 2.2, 112, 240], [6, 6], "right", "blue", soft=True)
d.decal("ricon2", [XR + 2.2, 98, 240], [6, 7], "right", "dark", soft=True)
d.box("conn", [XR + 1, 84, 150, XR + 5, 124, 230], "dark", r=3)
d.box("conn-in", [XR + 4, 89, 156, XR + 5.5, 119, 224], "plastic#4a4d52", r=2)
d.cyl("pin", [XR + 5, 112, 168], [XR + 7, 112, 168], 7, "metal#b9a77a", repeat=rep(3, [0, 0, 22]),
      copies=[[0, -17, 0]])
d.cyl("dot", [XR + 1.5, 116, 86], [XR + 3, 116, 86], 3, "slot", repeat=rep(11, [0, 0, 5.5]),
      copies=[[0, -5 * k, 0] for k in range(1, 5)])
d.box("vent-r", [XR - 2, 48, 82, XR + 1.5, 51, 182], "slot", r=1.2, repeat=rep(3, [0, 8, 0]), copies=[[0, 0, 108]])
d.save()
